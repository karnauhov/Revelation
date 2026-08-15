"""Leakage-free bidirectional statistical candidates for Ukrainian stage 7.

The implementation is deliberately self-contained and candidate-only.  It
trains IBM Model 1 in both directions on parallel verses outside the evaluated
fold, intersects mutual-best *token-type* links, and expands tied occurrences
to one verse-local hyperedge.  Token order is used only for deterministic
serialization and never for scoring or tie breaking.

No pretrained model or third-party aligner is used.  This first-party Apache
2.0 implementation runs on the CPython standard library.  Raw probabilities
are uncalibrated features and can never accept an alignment by themselves.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import sqrt
from pathlib import Path
import json
import platform
import re
import sys
from typing import Any, Iterable, Iterator, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_candidates import (
    CandidateContext,
    _attach_target_spans,
    _base_candidate,
    _ordered_original_ids,
    _ordered_target_ids,
    _relation,
    _sha256_file,
    _strongs_for_originals,
    load_context,
    source_contracts_from_registry,
    validate_candidate,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    comparison_form,
    deterministic_fold,
    stable_json,
)


STATISTICAL_CONTRACT_VERSION = "ukrainian-stage-7-statistical-candidate-v1"
STATISTICAL_GENERATOR_ID = "ibm1-bidirectional-oof-v1"
IBM1_ALGORITHM_VERSION = "ibm-model-1-em-null-prior-v1"
SYMMETRIZATION_VERSION = "mutual-best-type-intersection-no-position-v1"
NULL_KEY = "__UK7_IBM1_NULL__"

_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True)
class StatisticalConfig:
    """Frozen reproducibility and fail-closed candidate thresholds."""

    folds: int = 5
    iterations: int = 5
    minimum_pair_training_verses: int = 2
    minimum_forward_probability: float = 0.05
    minimum_reverse_probability: float = 0.05
    null_alignment_weight: float = 0.20
    tie_tolerance: float = 1e-12
    probability_serialization_digits: int = 15

    def validate(self) -> None:
        if self.folds < 2:
            raise ValueError("Statistical alignment requires at least two folds")
        if self.iterations < 1:
            raise ValueError("IBM Model 1 requires at least one EM iteration")
        if self.minimum_pair_training_verses < 2:
            raise ValueError("Single-verse co-presence is forbidden statistical proof")
        if not 0.0 <= self.minimum_forward_probability <= 1.0:
            raise ValueError("Invalid forward probability threshold")
        if not 0.0 <= self.minimum_reverse_probability <= 1.0:
            raise ValueError("Invalid reverse probability threshold")
        if not 0.0 < self.null_alignment_weight <= 1.0:
            raise ValueError("Invalid NULL alignment weight")
        if not 0.0 <= self.tie_tolerance < 1.0:
            raise ValueError("Invalid numerical tie tolerance")
        if not 12 <= self.probability_serialization_digits <= 17:
            raise ValueError("Probability serialization precision is unsafe")


@dataclass(frozen=True, slots=True)
class StatisticalOriginalToken:
    stable_id: str
    lexical_key: str
    order: int
    source_id: str
    source_family: str


@dataclass(frozen=True, slots=True)
class StatisticalTargetToken:
    stable_id: str
    lexical_key: str
    order: int


@dataclass(frozen=True, slots=True)
class StatisticalVerse:
    target_ref: str
    originals: tuple[StatisticalOriginalToken, ...]
    targets: tuple[StatisticalTargetToken, ...]


@dataclass(frozen=True, slots=True)
class IBM1Model:
    """A conditional lexical table ``P(outcome | conditioning)``."""

    probabilities: Mapping[tuple[str, str], float]
    support_verses: Mapping[tuple[str, str], int]
    training_refs: tuple[str, ...]
    model_sha256: str
    direction: str

    def probability(self, conditioning: str, outcome: str) -> float:
        return self.probabilities.get((conditioning, outcome), 0.0)

    def support(self, conditioning: str, outcome: str) -> int:
        return self.support_verses.get((conditioning, outcome), 0)


@dataclass(frozen=True, slots=True)
class BidirectionalIBM1:
    forward: IBM1Model
    reverse: IBM1Model
    held_out_fold: int


@dataclass(frozen=True, slots=True)
class TypeLink:
    source_key: str
    target_key: str
    forward_probability: float
    reverse_probability: float
    training_verse_support: int


@dataclass(frozen=True, slots=True)
class TypeComponent:
    source_keys: tuple[str, ...]
    target_keys: tuple[str, ...]
    links: tuple[TypeLink, ...]


def _sha256_canonical_lines(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = sha256()
    for row in rows:
        digest.update(stable_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _hash_value(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _canonical_probability(value: float, digits: int) -> str:
    return format(value, f".{digits}g")


def _model_digest(
    probabilities: Mapping[tuple[str, str], float],
    *,
    direction: str,
    iterations: int,
    digits: int,
) -> str:
    return _sha256_canonical_lines(
        {
            "algorithm_version": IBM1_ALGORITHM_VERSION,
            "direction": direction,
            "iterations": iterations,
            "conditioning_key_sha256": _hash_value(conditioning),
            "outcome_key_sha256": _hash_value(outcome),
            "probability": _canonical_probability(probability, digits),
        }
        for (conditioning, outcome), probability in sorted(probabilities.items())
    )


def _canonical_verses(verses: Sequence[StatisticalVerse]) -> tuple[StatisticalVerse, ...]:
    ordered = tuple(sorted(verses, key=lambda item: item.target_ref))
    refs = [verse.target_ref for verse in ordered]
    if len(refs) != len(set(refs)):
        raise ValueError("Duplicate target_ref in statistical parallel corpus")
    for verse in ordered:
        original_ids = [token.stable_id for token in verse.originals]
        target_ids = [token.stable_id for token in verse.targets]
        if len(original_ids) != len(set(original_ids)):
            raise ValueError(f"Duplicate original token ID at {verse.target_ref}")
        if len(target_ids) != len(set(target_ids)):
            raise ValueError(f"Duplicate OH token ID at {verse.target_ref}")
        if any(not token.lexical_key for token in (*verse.originals, *verse.targets)):
            raise ValueError(f"Empty statistical lexical key at {verse.target_ref}")
    return ordered


def _sentence_pairs(
    verses: Sequence[StatisticalVerse],
    *,
    reverse: bool,
) -> tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...]:
    rows: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = []
    for verse in _canonical_verses(verses):
        source = tuple(token.lexical_key for token in verse.originals)
        target = tuple(token.lexical_key for token in verse.targets)
        if reverse:
            source, target = target, source
        rows.append((verse.target_ref, source, target))
    return tuple(rows)


def train_ibm1(
    verses: Sequence[StatisticalVerse],
    *,
    direction: str,
    config: StatisticalConfig,
) -> IBM1Model:
    """Train deterministic IBM Model 1 without any positional feature."""

    config.validate()
    if direction not in {"original_to_oh1988", "oh1988_to_original"}:
        raise ValueError("Unknown IBM Model 1 direction")
    pairs = _sentence_pairs(verses, reverse=direction == "oh1988_to_original")
    if not pairs:
        raise ValueError("Cannot train IBM Model 1 on an empty corpus")

    possible: dict[str, set[str]] = defaultdict(set)
    support: Counter[tuple[str, str]] = Counter()
    for _target_ref, conditioning_sentence, outcome_sentence in pairs:
        conditioning_types = set(conditioning_sentence)
        outcome_types = set(outcome_sentence)
        for conditioning in conditioning_types:
            possible[conditioning].update(outcome_types)
            for outcome in outcome_types:
                support[(conditioning, outcome)] += 1
        possible[NULL_KEY].update(outcome_types)
        for outcome in outcome_types:
            support[(NULL_KEY, outcome)] += 1

    probabilities: dict[tuple[str, str], float] = {}
    for conditioning, outcomes in sorted(possible.items()):
        if not outcomes:
            continue
        initial = 1.0 / len(outcomes)
        for outcome in sorted(outcomes):
            probabilities[(conditioning, outcome)] = initial

    for _iteration in range(config.iterations):
        expected: Counter[tuple[str, str]] = Counter()
        totals: Counter[str] = Counter()
        for _target_ref, conditioning_sentence, outcome_sentence in pairs:
            conditioning_with_null = (NULL_KEY, *conditioning_sentence)
            for outcome in outcome_sentence:
                weighted = [
                    probabilities.get((conditioning, outcome), 0.0)
                    * (
                        config.null_alignment_weight
                        if conditioning == NULL_KEY
                        else 1.0
                    )
                    for conditioning in conditioning_with_null
                ]
                denominator = sum(weighted)
                if denominator <= 0.0:
                    continue
                for conditioning, weight in zip(conditioning_with_null, weighted):
                    if weight <= 0.0:
                        continue
                    delta = weight / denominator
                    expected[(conditioning, outcome)] += delta
                    totals[conditioning] += delta
        updated: dict[tuple[str, str], float] = {}
        for key in sorted(probabilities):
            conditioning, _outcome = key
            total = totals[conditioning]
            updated[key] = expected[key] / total if total > 0.0 else 0.0
        probabilities = updated

    digest = _model_digest(
        probabilities,
        direction=direction,
        iterations=config.iterations,
        digits=config.probability_serialization_digits,
    )
    return IBM1Model(
        probabilities=probabilities,
        support_verses=dict(support),
        training_refs=tuple(target_ref for target_ref, _left, _right in pairs),
        model_sha256=digest,
        direction=direction,
    )


def train_bidirectional_ibm1(
    verses: Sequence[StatisticalVerse],
    *,
    held_out_fold: int,
    config: StatisticalConfig,
) -> BidirectionalIBM1:
    config.validate()
    ordered = _canonical_verses(verses)
    return BidirectionalIBM1(
        forward=train_ibm1(
            ordered,
            direction="original_to_oh1988",
            config=config,
        ),
        reverse=train_ibm1(
            ordered,
            direction="oh1988_to_original",
            config=config,
        ),
        held_out_fold=held_out_fold,
    )


def _best_nonnull_keys(
    conditioning_keys: Sequence[str],
    outcome: str,
    *,
    model: IBM1Model,
    null_weight: float,
    tolerance: float,
) -> tuple[str, ...]:
    unique = tuple(sorted(set(conditioning_keys)))
    scored = [(key, model.probability(key, outcome)) for key in unique]
    if not scored:
        return ()
    best = max(value for _key, value in scored)
    null_score = model.probability(NULL_KEY, outcome) * null_weight
    if best <= 0.0 or best <= null_score + tolerance:
        return ()
    return tuple(key for key, value in scored if best - value <= tolerance)


def _connected_type_components(links: Sequence[TypeLink]) -> tuple[TypeComponent, ...]:
    adjacency: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    link_by_pair = {(link.source_key, link.target_key): link for link in links}
    for source_key, target_key in sorted(link_by_pair):
        source_node = ("source", source_key)
        target_node = ("target", target_key)
        adjacency[source_node].add(target_node)
        adjacency[target_node].add(source_node)

    components: list[TypeComponent] = []
    seen: set[tuple[str, str]] = set()
    for start in sorted(adjacency):
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        source_keys: set[str] = set()
        target_keys: set[str] = set()
        while queue:
            side, key = queue.popleft()
            (source_keys if side == "source" else target_keys).add(key)
            for neighbor in sorted(adjacency[(side, key)]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        component_links = tuple(
            link_by_pair[(source_key, target_key)]
            for source_key in sorted(source_keys)
            for target_key in sorted(target_keys)
            if (source_key, target_key) in link_by_pair
        )
        components.append(
            TypeComponent(
                source_keys=tuple(sorted(source_keys)),
                target_keys=tuple(sorted(target_keys)),
                links=component_links,
            )
        )
    return tuple(
        sorted(components, key=lambda item: (item.source_keys, item.target_keys))
    )


def infer_mutual_best_type_components(
    verse: StatisticalVerse,
    *,
    model: BidirectionalIBM1,
    config: StatisticalConfig,
) -> tuple[tuple[TypeComponent, ...], dict[str, int]]:
    """Infer type components; held-out token positions never enter scoring."""

    config.validate()
    source_keys = tuple(token.lexical_key for token in verse.originals)
    target_keys = tuple(token.lexical_key for token in verse.targets)
    forward_best = {
        target_key: _best_nonnull_keys(
            source_keys,
            target_key,
            model=model.forward,
            null_weight=config.null_alignment_weight,
            tolerance=config.tie_tolerance,
        )
        for target_key in sorted(set(target_keys))
    }
    reverse_best = {
        source_key: _best_nonnull_keys(
            target_keys,
            source_key,
            model=model.reverse,
            null_weight=config.null_alignment_weight,
            tolerance=config.tie_tolerance,
        )
        for source_key in sorted(set(source_keys))
    }
    counters: Counter[str] = Counter()
    links: list[TypeLink] = []
    for source_key in sorted(set(source_keys)):
        for target_key in sorted(set(target_keys)):
            counters["evaluated_type_pairs"] += 1
            if (
                source_key not in forward_best[target_key]
                or target_key not in reverse_best[source_key]
            ):
                counters["skipped_not_bidirectional_mutual_best"] += 1
                continue
            forward_probability = model.forward.probability(source_key, target_key)
            reverse_probability = model.reverse.probability(target_key, source_key)
            support = min(
                model.forward.support(source_key, target_key),
                model.reverse.support(target_key, source_key),
            )
            if support < config.minimum_pair_training_verses:
                counters["skipped_insufficient_oof_training_verse_support"] += 1
                continue
            if (
                forward_probability < config.minimum_forward_probability
                or reverse_probability < config.minimum_reverse_probability
            ):
                counters["skipped_probability_floor"] += 1
                continue
            links.append(
                TypeLink(
                    source_key=source_key,
                    target_key=target_key,
                    forward_probability=forward_probability,
                    reverse_probability=reverse_probability,
                    training_verse_support=support,
                )
            )
    counters["mutual_best_type_links"] = len(links)
    components = _connected_type_components(links)
    counters["emitted_type_components"] = len(components)
    counters["target_types_with_null_or_no_statistical_link"] = sum(
        not forward_best[key] for key in forward_best
    )
    counters["source_types_with_null_or_no_statistical_link"] = sum(
        not reverse_best[key] for key in reverse_best
    )
    return components, dict(sorted(counters.items()))


def _candidate_from_component(
    verse: StatisticalVerse,
    component: TypeComponent,
    *,
    context: CandidateContext,
    model: BidirectionalIBM1,
    config: StatisticalConfig,
) -> dict[str, Any]:
    original_ids = _ordered_original_ids(
        (
            token.stable_id
            for token in verse.originals
            if token.lexical_key in component.source_keys
        ),
        context.originals_by_id,
    )
    target_ids = _ordered_target_ids(
        (
            token.stable_id
            for token in verse.targets
            if token.lexical_key in component.target_keys
        ),
        context.target_by_id,
    )
    link_evidence = [
        {
            "source_lexical_key_sha256": _hash_value(link.source_key),
            "target_lexical_key_sha256": _hash_value(link.target_key),
            "forward_probability": float(
                _canonical_probability(
                    link.forward_probability, config.probability_serialization_digits
                )
            ),
            "reverse_probability": float(
                _canonical_probability(
                    link.reverse_probability, config.probability_serialization_digits
                )
            ),
            "training_verse_support": link.training_verse_support,
        }
        for link in component.links
    ]
    geometric_scores = [
        sqrt(link.forward_probability * link.reverse_probability)
        for link in component.links
    ]
    training_refs_sha256 = _sha256_canonical_lines(
        {"target_ref": target_ref} for target_ref in model.forward.training_refs
    )
    source_ids = sorted(
        {
            token.source_id
            for token in verse.originals
            if token.stable_id in set(original_ids)
        }
    )
    row = _base_candidate(
        generator_id=STATISTICAL_GENERATOR_ID,
        target_ref=verse.target_ref,
        original_ids=original_ids,
        target_ids=target_ids,
        strongs=_strongs_for_originals(original_ids, context.originals_by_id),
        relation=_relation(len(original_ids), len(target_ids)),
        evidence_channels=("bidirectional_statistical",),
        evidence=(
            {
                "kind": "oof_bidirectional_ibm1_mutual_best_type_component",
                "algorithm_version": IBM1_ALGORITHM_VERSION,
                "symmetrization_version": SYMMETRIZATION_VERSION,
                "held_out_fold": model.held_out_fold,
                "held_out_target_ref": verse.target_ref,
                "held_out_target_ref_excluded_from_training": (
                    verse.target_ref not in model.forward.training_refs
                    and verse.target_ref not in model.reverse.training_refs
                ),
                "training_verse_count": len(model.forward.training_refs),
                "training_refs_sha256": training_refs_sha256,
                "forward_model_sha256": model.forward.model_sha256,
                "reverse_model_sha256": model.reverse.model_sha256,
                "type_links": link_evidence,
                "position_feature_used": False,
                "neighbor_feature_used": False,
                "heldout_verse_copresence_is_proof": False,
                "stable_order_used_for_serialization_only": True,
            },
        ),
        dependency_family_ids=(*source_ids, "stage6_synthesized_text"),
        identity_extra={
            "held_out_fold": model.held_out_fold,
            "source_key_sha256": sorted(_hash_value(value) for value in component.source_keys),
            "target_key_sha256": sorted(_hash_value(value) for value in component.target_keys),
            "forward_model_sha256": model.forward.model_sha256,
            "reverse_model_sha256": model.reverse.model_sha256,
        },
        score={
            "kind": "uncalibrated_conservative_component_geometric_mean",
            "raw": float(
                _canonical_probability(
                    min(geometric_scores), config.probability_serialization_digits
                )
            ),
            "calibrated": False,
        },
    )
    _attach_target_spans(row, context=context)
    row["statistical_contract_version"] = STATISTICAL_CONTRACT_VERSION
    row["independent_vote"] = True
    row["proof_limitations"].extend(
        [
            "statistical score is uncalibrated and cannot accept a link",
            "parallel-verse membership alone never emits a candidate",
            "repeated or tied occurrences remain one many-to-many component",
        ]
    )
    validate_candidate(row, context=context)
    if row["resolver_eligible"] is not False or row["auto_acceptance"] is not False:
        raise RuntimeError("Statistical candidate unexpectedly enabled acceptance")
    return row


def generate_oof_statistical_candidates(
    verses: Sequence[StatisticalVerse],
    *,
    context: CandidateContext,
    config: StatisticalConfig = StatisticalConfig(),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Generate deterministic out-of-fold candidate-only hyperedges."""

    config.validate()
    ordered = _canonical_verses(verses)
    rows: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    fold_records: list[dict[str, Any]] = []
    for fold in range(config.folds):
        held_out = tuple(
            verse
            for verse in ordered
            if deterministic_fold(verse.target_ref, config.folds) == fold
        )
        training = tuple(
            verse
            for verse in ordered
            if deterministic_fold(verse.target_ref, config.folds) != fold
        )
        if not held_out:
            fold_records.append(
                {
                    "fold": fold,
                    "status": "skipped_empty_held_out_fold",
                    "held_out_verse_count": 0,
                    "training_verse_count": len(training),
                }
            )
            totals["skipped_empty_held_out_folds"] += 1
            continue
        if not training:
            raise ValueError("Out-of-fold statistical training set is empty")
        model = train_bidirectional_ibm1(
            training,
            held_out_fold=fold,
            config=config,
        )
        fold_candidate_count = 0
        for verse in held_out:
            if verse.target_ref in model.forward.training_refs:
                raise RuntimeError("Held-out verse leaked into forward training")
            if verse.target_ref in model.reverse.training_refs:
                raise RuntimeError("Held-out verse leaked into reverse training")
            components, counters = infer_mutual_best_type_components(
                verse,
                model=model,
                config=config,
            )
            totals.update(counters)
            for component in components:
                rows.append(
                    _candidate_from_component(
                        verse,
                        component,
                        context=context,
                        model=model,
                        config=config,
                    )
                )
                fold_candidate_count += 1
        training_refs_sha256 = _sha256_canonical_lines(
            {"target_ref": target_ref} for target_ref in model.forward.training_refs
        )
        held_out_refs_sha256 = _sha256_canonical_lines(
            {"target_ref": verse.target_ref} for verse in held_out
        )
        fold_records.append(
            {
                "fold": fold,
                "status": "generated_candidate_only",
                "held_out_verse_count": len(held_out),
                "training_verse_count": len(training),
                "training_refs_sha256": training_refs_sha256,
                "held_out_refs_sha256": held_out_refs_sha256,
                "training_and_held_out_disjoint": True,
                "forward_model_sha256": model.forward.model_sha256,
                "reverse_model_sha256": model.reverse.model_sha256,
                "candidate_count": fold_candidate_count,
            }
        )
    rows.sort(key=lambda row: (str(row["target_ref"]), str(row["candidate_id"])))
    output_sha256 = _sha256_canonical_lines(rows)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "statistical_contract_version": STATISTICAL_CONTRACT_VERSION,
        "artifact": "bidirectional_statistical_candidate_generation",
        "generator_id": STATISTICAL_GENERATOR_ID,
        "status": "candidate_only_uncalibrated_no_auto_acceptance",
        "algorithm": {
            "name": "IBM Model 1 expectation-maximization, both directions",
            "version": IBM1_ALGORITHM_VERSION,
            "symmetrization": SYMMETRIZATION_VERSION,
            "position_feature_used": False,
            "neighbor_feature_used": False,
            "proportional_feature_used": False,
            "verse_bag_assignment_used": False,
            "parallel_verse_boundary_role": "training instance and held-out candidate domain only",
        },
        "configuration": asdict(config),
        "folds": fold_records,
        "output_sha256": output_sha256,
        "processed_count": len(ordered),
        "skipped_count": totals.get("skipped_empty_held_out_folds", 0),
        "error_count": 0,
        "counts": {
            **dict(sorted(totals.items())),
            "candidate_count": len(rows),
            "verse_count": len(ordered),
        },
        "serialization": "UTF-8 JSON/JSONL; sorted keys; compact separators; LF; target_ref then candidate_id",
    }
    return rows, manifest


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            yield row


def load_statistical_parallel_corpus(
    token_inventory_path: Path,
    original_universe_path: Path,
    *,
    context: CandidateContext | None = None,
) -> tuple[CandidateContext, tuple[StatisticalVerse, ...], dict[str, int]]:
    """Load exact current stable IDs while excluding unresolved readings."""

    candidate_context = context or load_context(
        token_inventory_path, original_universe_path
    )
    target_by_ref: dict[str, list[StatisticalTargetToken]] = defaultdict(list)
    for token in candidate_context.target_by_id.values():
        if not token.comparison:
            continue
        target_by_ref[token.target_ref].append(
            StatisticalTargetToken(token.token_id, token.comparison, token.order)
        )

    original_by_ref: dict[str, list[StatisticalOriginalToken]] = defaultdict(list)
    counters: Counter[str] = Counter()
    for row in _read_jsonl(original_universe_path):
        counters["original_rows_processed"] += 1
        stable_id = str(row["original_token_id"])
        token = candidate_context.originals_by_id.get(stable_id)
        if token is None:
            raise ValueError(f"Original row lacks candidate context token: {stable_id}")
        if not token.is_resolved_primary:
            counters["original_rows_skipped_unresolved_or_nonprimary"] += 1
            continue
        if token.target_ref is None or not token.strong_classic:
            counters["original_rows_skipped_no_target_or_classic_strong"] += 1
            continue
        surface = str(row.get("surface_normalized") or "")
        if not surface:
            surface = comparison_form(str(row.get("surface_raw") or ""))
        if not surface:
            counters["original_rows_skipped_empty_surface"] += 1
            continue
        family = token.source_family
        lexical_key = f"{family}:{surface}"
        original_by_ref[token.target_ref].append(
            StatisticalOriginalToken(
                stable_id=stable_id,
                lexical_key=lexical_key,
                order=token.order,
                source_id=str(row.get("source_id") or family),
                source_family=family,
            )
        )
        counters["original_rows_retained"] += 1

    refs = sorted(set(target_by_ref) | set(original_by_ref))
    verses = tuple(
        StatisticalVerse(
            target_ref=target_ref,
            originals=tuple(
                sorted(
                    original_by_ref.get(target_ref, ()),
                    key=lambda token: (token.order, token.stable_id),
                )
            ),
            targets=tuple(
                sorted(
                    target_by_ref.get(target_ref, ()),
                    key=lambda token: (token.order, token.stable_id),
                )
            ),
        )
        for target_ref in refs
    )
    counters["parallel_verse_count"] = len(verses)
    counters["target_token_count"] = sum(len(verse.targets) for verse in verses)
    return candidate_context, _canonical_verses(verses), dict(sorted(counters.items()))


def _runtime_record() -> dict[str, Any]:
    executable = Path(sys.executable).resolve()
    return {
        "tool": "CPython standard library",
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "license": "Python Software Foundation License Version 2 (PSF-2.0)",
        "license_url": "https://docs.python.org/3/license.html",
        "executable_sha256": _sha256_file(executable),
        "platform": platform.platform(),
        "thread_count": 1,
        "hash_randomization_dependency": False,
        "floating_point_contract": "IEEE-754 binary64; canonical .15g by default; runtime digest pinned",
    }


def build_statistical_generator_registry(
    *,
    input_sha256: Mapping[str, str],
    source_contracts: Mapping[str, Mapping[str, Any]],
    config: StatisticalConfig,
) -> dict[str, Any]:
    config.validate()
    for name, digest in input_sha256.items():
        if _SHA256_RE.fullmatch(str(digest)) is None:
            raise ValueError(f"Invalid statistical input digest: {name}")
    required_sources = (
        "stage6_synthesized_text",
        "step_tahot",
        "step_tagnt",
    )
    contracts = []
    for source_id in required_sources:
        contract = source_contracts.get(source_id)
        if contract is None:
            raise ValueError(f"Missing statistical source contract: {source_id}")
        if (
            not contract.get("version")
            or not contract.get("license")
            or _SHA256_RE.fullmatch(str(contract.get("sha256", ""))) is None
        ):
            raise ValueError(f"Incomplete statistical source contract: {source_id}")
        contracts.append(dict(contract))
    implementation = Path(__file__)
    registry = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "statistical_contract_version": STATISTICAL_CONTRACT_VERSION,
        "artifact": "bidirectional_statistical_generator_registry",
        "generator_id": STATISTICAL_GENERATOR_ID,
        "status": "candidate_only_no_auto_acceptance",
        "algorithm": {
            "name": "IBM Model 1 expectation-maximization",
            "version": IBM1_ALGORITHM_VERSION,
            "reference": "Brown et al., Computational Linguistics 19(2), 1993, doi:10.1162/coli.1993.19.2.263",
            "algorithm_license": "mathematical method; implementation license applies",
            "symmetrization_version": SYMMETRIZATION_VERSION,
        },
        "implementation": {
            "path": "scripts/bible_module/ukrainian_stage_7_statistical.py",
            "version": STATISTICAL_GENERATOR_ID,
            "sha256": _sha256_file(implementation),
            "license": "Apache-2.0 (project LICENSE)",
            "external_package": None,
            "pretrained_model": None,
        },
        "runtime": _runtime_record(),
        "configuration": asdict(config),
        "input_sha256": dict(sorted(input_sha256.items())),
        "source_contracts": contracts,
        "reproducibility": {
            "fold_assignment": "sha256(target_ref) first 64 bits modulo folds",
            "exclusion_unit": "entire target_ref held-out fold",
            "canonical_iteration": True,
            "single_process": True,
            "token_order_used_for_scoring": False,
            "candidate_calibration": False,
            "auto_acceptance": False,
            "resolver_eligible": False,
        },
        "processed_count": 1,
        "skipped_count": 0,
        "error_count": 0,
        "serialization": "UTF-8 JSON; sorted keys; compact separators; LF",
    }
    return registry


def generate_statistical_candidate_artifacts(
    *,
    token_inventory_path: Path,
    original_universe_path: Path,
    source_registry_path: Path,
    output_dir: Path,
    config: StatisticalConfig = StatisticalConfig(),
) -> dict[str, Any]:
    """Generate standalone deterministic artifacts from frozen input paths."""

    config.validate()
    paths = {
        "ukrainian_token_inventory": token_inventory_path,
        "original_token_universe": original_universe_path,
        "source_registry": source_registry_path,
    }
    input_sha256 = {
        name: _sha256_file(path) for name, path in sorted(paths.items())
    }
    source_contracts = source_contracts_from_registry(source_registry_path)
    context, verses, load_counts = load_statistical_parallel_corpus(
        token_inventory_path, original_universe_path
    )
    rows, manifest = generate_oof_statistical_candidates(
        verses, context=context, config=config
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "alignment_candidates.statistical.jsonl"
    output_path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    if _sha256_file(output_path) != manifest["output_sha256"]:
        raise RuntimeError("Statistical candidate artifact digest drift")
    registry = build_statistical_generator_registry(
        input_sha256=input_sha256,
        source_contracts=source_contracts,
        config=config,
    )
    registry_path = output_dir / "statistical_generator_registry.json"
    registry_path.write_text(
        stable_json(registry) + "\n", encoding="utf-8", newline="\n"
    )
    manifest = {
        **manifest,
        "input_sha256": input_sha256,
        "load_counts": load_counts,
        "output_files": {
            output_path.name: _sha256_file(output_path),
            registry_path.name: _sha256_file(registry_path),
        },
    }
    manifest_path = output_dir / "statistical_candidates.manifest.json"
    manifest_path.write_text(
        stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest

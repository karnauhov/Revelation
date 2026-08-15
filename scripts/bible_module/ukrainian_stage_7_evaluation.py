"""Streaming frozen-gold evaluation for Ukrainian stage-7 candidates.

This module is deliberately evaluation-only.  It compares complete candidate
hyperedges with complete, independently reviewed gold hyperedges by exact
stable-ID semantics.  It never performs threshold selection, calibration,
partial credit, verse-bag matching, candidate promotion, or Strong markup.

The rejected legacy experiment is evaluated through a narrower and explicit
baseline contract: a ``target token + Strong`` occurrence is checked only
against Strong numbers carried by the original token(s) linked to that target
by frozen gold.  A legacy occurrence matching more than one linked original is
reported as ambiguous and is not counted as correct.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
from typing import Any, Iterable, Iterator, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_candidates import LEGACY_GENERATOR_ID
from scripts.bible_module.ukrainian_stage_7_gold import (
    validated_finalized_gold_lock,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"
DEFAULT_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_20260801"

EVALUATION_VERSION = "ukrainian-stage-7-frozen-gold-candidate-evaluation-v2"
EVALUATION_FOLD_COUNT = 5
SEALED_EVALUATION_FOLD = 4
DETAILS_FILENAME = "candidate_gold_evaluation.jsonl"
MANIFEST_FILENAME = "candidate_gold_evaluation.manifest.json"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_CANDIDATE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._-]+$")
_NON_NULL_RELATIONS = frozenset(
    {"one_to_one", "one_to_many", "many_to_one", "many_to_many", "grouped_expression"}
)
_ORIGINAL_NULL_REASONS = frozenset(
    {
        "translation_omission",
        "grammatical_function_not_overt",
        "absorbed_by_grouped_expression",
        "repetition_not_rendered",
        "source_text_not_rendered",
    }
)
_TARGET_NULL_REASONS = frozenset({"translation_addition", "function_token"})

_OT_BOOKS = frozenset(
    {
        "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth",
        "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh",
        "Esth", "Job", "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam",
        "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic",
        "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    }
)
_NT_BOOKS = frozenset(
    {
        "Mat", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor",
        "Gal", "Eph", "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim",
        "Titus", "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John",
        "3John", "Jude", "Rev",
    }
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    return sha256(stable_json(value).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"JSONL row is not an object: {path.name}:{line_number}")
            yield row


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _parse_ref(target_ref: Any) -> tuple[str, str]:
    if not isinstance(target_ref, str):
        raise ValueError("target_ref is missing or not a string")
    parts = target_ref.split(".")
    if len(parts) != 3 or not parts[0] or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError(f"Non-canonical target_ref: {target_ref!r}")
    book = parts[0]
    if book not in _OT_BOOKS | _NT_BOOKS:
        raise ValueError(f"Unknown protestant-66 book in target_ref: {target_ref!r}")
    if int(parts[1]) < 1 or int(parts[2]) < 1:
        raise ValueError(f"Non-positive chapter/verse in target_ref: {target_ref!r}")
    testament = "OT" if book in _OT_BOOKS else "NT"
    return book, testament


def _validated_folds(values: Iterable[int], *, fold_count: int) -> frozenset[int]:
    folds = frozenset(values)
    if fold_count != EVALUATION_FOLD_COUNT:
        raise ValueError("Frozen evaluation requires the five-fold stage-7 contract")
    if not folds or any(isinstance(value, bool) or not isinstance(value, int) for value in folds):
        raise ValueError("At least one integer evaluation fold is required")
    if any(value < 0 or value >= fold_count for value in folds):
        raise ValueError("Evaluation fold is outside the frozen fold grid")
    if SEALED_EVALUATION_FOLD in folds and folds != {SEALED_EVALUATION_FOLD}:
        raise ValueError("Sealed evaluation fold must be evaluated in isolation")
    return folds


def _evaluation_fold(target_ref: str, fold_count: int) -> int:
    """Use the frozen stage-7 gold/ledger target-ref fold assignment."""

    return int(sha256(target_ref.encode("utf-8")).hexdigest()[:8], 16) % fold_count


def _load_target_grid(
    path: Path,
    *,
    fold_count: int,
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    refs: dict[str, str] = {}
    strata_by_ref: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        token_id = row.get("token_id")
        if not isinstance(token_id, str) or not token_id or token_id in refs:
            raise ValueError("Target inventory has a missing or duplicate stable ID")
        target_ref = row.get("target_ref")
        book, testament = _parse_ref(target_ref)
        target_ref = str(target_ref)
        fold_id = _evaluation_fold(target_ref, fold_count)
        if row.get("book") not in (None, book):
            raise ValueError("Target inventory book stratum disagrees with target_ref")
        if row.get("testament") not in (None, testament):
            raise ValueError("Target inventory testament stratum disagrees with target_ref")
        if row.get("fold_id") not in (None, fold_id):
            raise ValueError("Target inventory fold stratum disagrees with frozen assignment")
        strata = {
            "book": book,
            "testament": testament,
            "genre": str(row.get("genre", "unclassified")),
            "fold_id": fold_id,
        }
        previous = strata_by_ref.get(target_ref)
        if previous is not None and previous != strata:
            raise ValueError("Target inventory has inconsistent verse strata")
        strata_by_ref[target_ref] = strata
        refs[token_id] = str(target_ref)
    if not refs:
        raise ValueError("Target inventory is empty")
    return refs, strata_by_ref


def _load_original_grid(path: Path) -> tuple[dict[str, str], dict[str, tuple[str, ...]]]:
    refs: dict[str, str] = {}
    strongs: dict[str, tuple[str, ...]] = {}
    for row in _read_jsonl(path):
        token_id = row.get("original_token_id")
        if not isinstance(token_id, str) or not token_id or token_id in refs:
            raise ValueError("Original universe has a missing or duplicate stable ID")
        target_ref = row.get("target_ref")
        _parse_ref(target_ref)
        raw_strongs = row.get("strong_classic")
        if (
            not isinstance(raw_strongs, list)
            or any(not isinstance(value, str) or not value for value in raw_strongs)
            or raw_strongs != sorted(set(raw_strongs))
        ):
            raise ValueError("Original universe has a non-canonical Strong list")
        refs[token_id] = str(target_ref)
        strongs[token_id] = tuple(raw_strongs)
    if not refs:
        raise ValueError("Original universe is empty")
    return refs, strongs


def _canonical_ids(value: Any, *, label: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"{label} must be a duplicate-free stable-ID list")
    return tuple(sorted(value))


def _semantic_identity(
    *,
    target_ref: str,
    relation: Any,
    original_ids: tuple[str, ...],
    target_ids: tuple[str, ...],
    null_reason: Any,
) -> tuple[str, str, tuple[str, ...], tuple[str, ...], str | None]:
    if not isinstance(relation, str) or not relation:
        raise ValueError("Hyperedge relation is missing")
    if null_reason is not None and not isinstance(null_reason, str):
        raise ValueError("Hyperedge null_reason must be a string or null")
    if relation == "original_omitted":
        if (
            not original_ids
            or target_ids
            or null_reason not in _ORIGINAL_NULL_REASONS
        ):
            raise ValueError("Original omission cardinality/null semantics are invalid")
    elif relation == "translation_addition":
        if original_ids or not target_ids or null_reason not in _TARGET_NULL_REASONS:
            raise ValueError("Translation addition cardinality/null semantics are invalid")
    else:
        if relation not in _NON_NULL_RELATIONS:
            raise ValueError("Hyperedge relation is outside the frozen gold contract")
        if not original_ids or not target_ids or null_reason is not None:
            raise ValueError("Non-null hyperedge cardinality/null semantics are invalid")
        cardinality = (len(original_ids), len(target_ids))
        if relation == "one_to_one" and cardinality != (1, 1):
            raise ValueError("one_to_one candidate/gold cardinality is invalid")
        if relation == "one_to_many" and not (
            cardinality[0] == 1 and cardinality[1] >= 2
        ):
            raise ValueError("one_to_many candidate/gold cardinality is invalid")
        if relation == "many_to_one" and not (
            cardinality[0] >= 2 and cardinality[1] == 1
        ):
            raise ValueError("many_to_one candidate/gold cardinality is invalid")
        if relation == "many_to_many" and not (
            cardinality[0] >= 2 and cardinality[1] >= 2
        ):
            raise ValueError("many_to_many candidate/gold cardinality is invalid")
    return target_ref, relation, original_ids, target_ids, null_reason


def _identity_payload(identity: tuple[Any, ...]) -> dict[str, Any]:
    target_ref, relation, original_ids, target_ids, null_reason = identity
    return {
        "target_ref": target_ref,
        "relation": relation,
        "original_token_ids": list(original_ids),
        "target_token_ids": list(target_ids),
        "null_reason": null_reason,
    }


def _severity(values: Iterable[str]) -> str:
    ranks = {"unclassified": 0, "normal": 1, "high": 2, "critical": 3}
    unique = {value for value in values if value in ranks}
    return max(unique or {"unclassified"}, key=ranks.__getitem__)


class _GoldIndex:
    def __init__(self) -> None:
        self.edges: dict[tuple[Any, ...], dict[str, Any]] = {}
        self.edge_by_id: dict[str, tuple[Any, ...]] = {}
        self.original_to_edge: dict[str, tuple[Any, ...]] = {}
        self.target_to_edge: dict[str, tuple[Any, ...]] = {}
        self.refs: set[str] = set()
        self.edge_metadata: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"severities": set(), "phenomena": set(), "genres": set()}
        )


def _load_gold_index(
    annotations_path: Path,
    *,
    folds: frozenset[int],
    fold_count: int,
    original_ref_by_id: Mapping[str, str],
    target_ref_by_id: Mapping[str, str],
    target_strata_by_ref: Mapping[str, Mapping[str, Any]],
) -> _GoldIndex:
    index = _GoldIndex()
    pending_target_metadata: dict[str, dict[str, Any]] = {}
    seen_decision_ids: set[str] = set()
    seen_accounting_ids: set[str] = set()
    for row in _read_jsonl(annotations_path):
        target_ref = row.get("target_ref")
        _parse_ref(target_ref)
        target_ref = str(target_ref)
        if _evaluation_fold(target_ref, fold_count) not in folds:
            # The sealed fold is routed solely by target_ref.  No label, score,
            # token or stratum content from another fold is inspected here.
            continue
        record_type = row.get("record_type")
        if record_type == "hyperedge":
            edge_id = row.get("edge_id")
            if not isinstance(edge_id, str) or not edge_id or edge_id in index.edge_by_id:
                raise ValueError("Gold has a missing or duplicate hyperedge ID")
            originals = _canonical_ids(row.get("original_token_ids"), label="gold original IDs")
            targets = _canonical_ids(row.get("target_token_ids"), label="gold target IDs")
            identity = _semantic_identity(
                target_ref=target_ref,
                relation=row.get("relation"),
                original_ids=originals,
                target_ids=targets,
                null_reason=row.get("null_reason"),
            )
            if identity in index.edges:
                raise ValueError("Gold contains a duplicate semantic hyperedge")
            for token_id in originals:
                if original_ref_by_id.get(token_id) != target_ref:
                    raise ValueError("Gold contains a stale, dangling or cross-verse original ID")
                if token_id in index.original_to_edge:
                    raise ValueError("Gold original token is accounted by multiple hyperedges")
                index.original_to_edge[token_id] = identity
            for token_id in targets:
                if target_ref_by_id.get(token_id) != target_ref:
                    raise ValueError("Gold contains a stale, dangling or cross-verse target ID")
                if token_id in index.target_to_edge:
                    raise ValueError("Gold target token is accounted by multiple hyperedges")
                index.target_to_edge[token_id] = identity
            index.edge_by_id[edge_id] = identity
            index.edges[identity] = {
                "edge_id": edge_id,
                "fold_id": _evaluation_fold(target_ref, fold_count),
            }
            index.refs.add(target_ref)
        elif record_type == "original_decision":
            decision_id = row.get("decision_id")
            if not isinstance(decision_id, str) or not decision_id or decision_id in seen_decision_ids:
                raise ValueError("Gold has a missing or duplicate original decision ID")
            seen_decision_ids.add(decision_id)
            edge_id = row.get("edge_id")
            if isinstance(edge_id, str) and edge_id:
                metadata = index.edge_metadata[edge_id]
                metadata["severities"].add(str(row.get("severity", "unclassified")))
                metadata["phenomena"].update(str(value) for value in row.get("phenomena", ()))
                if row.get("genre"):
                    metadata["genres"].add(str(row["genre"]))
        elif record_type == "target_accounting":
            accounting_id = row.get("accounting_id")
            if not isinstance(accounting_id, str) or not accounting_id or accounting_id in seen_accounting_ids:
                raise ValueError("Gold has a missing or duplicate target accounting ID")
            seen_accounting_ids.add(accounting_id)
            token_id = row.get("target_token_id")
            if isinstance(token_id, str) and token_id:
                pending_target_metadata[token_id] = {
                    "severities": {str(row.get("severity", "unclassified"))},
                    "phenomena": {str(value) for value in row.get("phenomena", ())},
                    "genres": {str(row["genre"])} if row.get("genre") else set(),
                }
        else:
            raise ValueError("Frozen gold contains an unknown record type")
    if not index.edges:
        raise ValueError("Selected evaluation fold has no frozen gold hyperedges")
    for identity, value in index.edges.items():
        edge_id = str(value["edge_id"])
        metadata = index.edge_metadata[edge_id]
        for target_id in identity[3]:
            target_metadata = pending_target_metadata.get(target_id)
            if target_metadata is None:
                continue
            for key in ("severities", "phenomena", "genres"):
                metadata[key].update(target_metadata[key])
        target_strata = target_strata_by_ref.get(identity[0])
        if target_strata is None:
            raise ValueError("Gold target_ref is absent from the target inventory strata")
        metadata_genres = metadata["genres"]
        inventory_genre = str(target_strata["genre"])
        if metadata_genres and metadata_genres != {inventory_genre}:
            raise ValueError("Gold and target inventory genre strata disagree")
        value["strata"] = {
            "testament": target_strata["testament"],
            "book": target_strata["book"],
            "relation": identity[1],
            "severity": _severity(metadata["severities"]),
            "genre": inventory_genre,
            "phenomena": sorted(metadata["phenomena"]) or ["unclassified"],
        }
    return index


def _candidate_identity(
    row: Mapping[str, Any],
    *,
    target_ref: str,
    gold: _GoldIndex,
    original_ref_by_id: Mapping[str, str],
    original_strongs: Mapping[str, tuple[str, ...]],
    target_ref_by_id: Mapping[str, str],
) -> tuple[Any, ...]:
    originals = _canonical_ids(row.get("original_token_ids"), label="candidate original IDs")
    targets = _canonical_ids(row.get("target_token_ids"), label="candidate target IDs")
    for token_id in originals:
        if original_ref_by_id.get(token_id) != target_ref or token_id not in gold.original_to_edge:
            raise ValueError("Candidate contains a stale, unselected, dangling or cross-verse original ID")
    for token_id in targets:
        if target_ref_by_id.get(token_id) != target_ref or token_id not in gold.target_to_edge:
            raise ValueError("Candidate contains a stale, unaccounted, dangling or cross-verse target ID")
    raw_strongs = row.get("strong_classic")
    if (
        not isinstance(raw_strongs, list)
        or any(not isinstance(value, str) or not value for value in raw_strongs)
        or raw_strongs != sorted(set(raw_strongs))
    ):
        raise ValueError("Candidate Strong list is not canonical")
    expected_strongs = sorted(
        {strong for token_id in originals for strong in original_strongs[token_id]}
    )
    if raw_strongs != expected_strongs:
        raise ValueError("Candidate Strong list is stale or not derived from its original IDs")
    return _semantic_identity(
        target_ref=target_ref,
        relation=row.get("relation"),
        original_ids=originals,
        target_ids=targets,
        null_reason=row.get("null_reason"),
    )


def _candidate_contract(row: Mapping[str, Any]) -> tuple[str, str]:
    candidate_id = row.get("candidate_id")
    generator_id = row.get("generator_id")
    if not isinstance(candidate_id, str) or _CANDIDATE_ID_RE.fullmatch(candidate_id) is None:
        raise ValueError("Candidate ID is missing or malformed")
    if not isinstance(generator_id, str) or not generator_id:
        raise ValueError("Candidate generator ID is missing")
    if (
        row.get("candidate_only") is not True
        or row.get("calibrated") is not False
        or row.get("auto_acceptance") is not False
        or row.get("resolver_eligible") is not False
    ):
        raise ValueError("Evaluation input is not an uncalibrated candidate-only row")
    score = row.get("generator_score")
    if score is not None and (
        not isinstance(score, dict) or score.get("calibrated") is not False
    ):
        raise ValueError("Generator-specific raw score is not explicitly uncalibrated")
    return candidate_id, generator_id


def _metric_increment(
    metrics: dict[str, Any],
    *,
    fold_id: int,
    strata: Mapping[str, Any],
    matched: bool,
) -> None:
    metrics["candidate_count"] += 1
    metrics["exact_match_count"] += int(matched)
    metrics["nonmatch_count"] += int(not matched)
    fold = metrics["folds"][str(fold_id)]
    fold["candidate_count"] += 1
    fold["exact_match_count"] += int(matched)
    for field in ("testament", "book", "relation", "severity", "genre"):
        value = str(strata.get(field, "unclassified"))
        bucket = metrics["strata"][field][value]
        bucket["candidate_count"] += 1
        bucket["exact_match_count"] += int(matched)
    for phenomenon in strata.get("phenomena", ["unclassified"]):
        bucket = metrics["strata"]["phenomenon"][str(phenomenon)]
        bucket["candidate_count"] += 1
        bucket["exact_match_count"] += int(matched)


def _new_metrics() -> dict[str, Any]:
    return {
        "candidate_count": 0,
        "exact_match_count": 0,
        "nonmatch_count": 0,
        "raw_score_present_count": 0,
        "raw_score_missing_count": 0,
        "matched_gold_identities": set(),
        "folds": defaultdict(lambda: Counter(candidate_count=0, exact_match_count=0)),
        "strata": defaultdict(
            lambda: defaultdict(lambda: Counter(candidate_count=0, exact_match_count=0))
        ),
    }


def _precision(correct: int, support: int) -> float | None:
    return correct / support if support else None


def _finalize_metrics(metrics: Mapping[str, Any], *, gold_edge_count: int) -> dict[str, Any]:
    candidate_count = int(metrics["candidate_count"])
    exact = int(metrics["exact_match_count"])
    folds = {
        fold: {
            **dict(sorted(counter.items())),
            "exact_precision": _precision(counter["exact_match_count"], counter["candidate_count"]),
        }
        for fold, counter in sorted(metrics["folds"].items(), key=lambda item: int(item[0]))
    }
    strata: dict[str, Any] = {}
    for field, values in sorted(metrics["strata"].items()):
        strata[field] = {
            value: {
                **dict(sorted(counter.items())),
                "exact_precision": _precision(counter["exact_match_count"], counter["candidate_count"]),
            }
            for value, counter in sorted(values.items())
        }
    return {
        "candidate_count": candidate_count,
        "exact_match_count": exact,
        "nonmatch_count": int(metrics["nonmatch_count"]),
        "exact_precision": _precision(exact, candidate_count),
        "unique_gold_hyperedges_matched": len(metrics["matched_gold_identities"]),
        "gold_hyperedge_count": gold_edge_count,
        "exact_recall": _precision(len(metrics["matched_gold_identities"]), gold_edge_count),
        "raw_score_present_count": int(metrics["raw_score_present_count"]),
        "raw_score_missing_count": int(metrics["raw_score_missing_count"]),
        "fold_metrics": folds,
        "stratum_metrics": strata,
        "scores_calibrated": False,
        "threshold_tuning_performed": False,
        "automatic_promotion_performed": False,
    }


def _legacy_increment(
    metrics: Mapping[str, Any],
    *,
    fold_id: int,
    strata: Mapping[str, Any],
    status: str,
) -> None:
    metrics["totals"]["occurrence_count"] += 1
    metrics["totals"][status] += 1
    metrics["folds"][str(fold_id)]["occurrence_count"] += 1
    metrics["folds"][str(fold_id)][status] += 1
    for field in ("testament", "book", "relation", "severity", "genre"):
        value = str(strata.get(field, "unclassified"))
        metrics["strata"][field][value]["occurrence_count"] += 1
        metrics["strata"][field][value][status] += 1
    for phenomenon in strata.get("phenomena", ["unclassified"]):
        metrics["strata"]["phenomenon"][str(phenomenon)]["occurrence_count"] += 1
        metrics["strata"]["phenomenon"][str(phenomenon)][status] += 1


def _finalize_legacy_buckets(metrics: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    def finalize(values: Mapping[str, Counter[str]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for value, counter in sorted(values.items()):
            support = counter["occurrence_count"]
            determinate = counter["correct"] + counter["incorrect"]
            result[value] = {
                **dict(sorted(counter.items())),
                "strict_precision": _precision(counter["correct"], support),
                "determinate_precision": _precision(counter["correct"], determinate),
            }
        return result

    folds = finalize(metrics["folds"])
    strata = {
        field: finalize(values)
        for field, values in sorted(metrics["strata"].items())
    }
    return folds, strata


def _gold_strata_for_nonmatch(
    identity: tuple[Any, ...],
    *,
    gold: _GoldIndex,
    target_strata_by_ref: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    target_ref, relation, original_ids, target_ids, _null_reason = identity
    target_strata = target_strata_by_ref.get(target_ref)
    if target_strata is None:
        raise ValueError("Candidate target_ref lacks frozen target strata")
    overlapping = {
        gold.original_to_edge[token_id]
        for token_id in original_ids
        if token_id in gold.original_to_edge
    } | {
        gold.target_to_edge[token_id]
        for token_id in target_ids
        if token_id in gold.target_to_edge
    }
    overlap_strata = [gold.edges[value]["strata"] for value in overlapping]
    return {
        "testament": str(target_strata["testament"]),
        "book": str(target_strata["book"]),
        "relation": str(relation),
        "severity": _severity(
            str(value.get("severity", "unclassified")) for value in overlap_strata
        ),
        "genre": str(target_strata["genre"]),
        "phenomena": sorted(
            {
                str(phenomenon)
                for value in overlap_strata
                for phenomenon in value.get("phenomena", ())
            }
        )
        or ["unclassified"],
    }


def _legacy_occurrences(
    row: Mapping[str, Any],
    *,
    target_ref: str,
    gold: _GoldIndex,
    original_strongs: Mapping[str, tuple[str, ...]],
    target_ref_by_id: Mapping[str, str],
) -> Iterator[dict[str, Any]]:
    originals = _canonical_ids(row.get("original_token_ids"), label="legacy original IDs")
    targets = _canonical_ids(row.get("target_token_ids"), label="legacy target IDs")
    if originals or len(targets) != 1:
        raise ValueError("Legacy baseline requires no current original and exactly one target ID")
    target_id = targets[0]
    if target_ref_by_id.get(target_id) != target_ref or target_id not in gold.target_to_edge:
        raise ValueError("Legacy baseline contains a stale, dangling or cross-verse target ID")
    strongs = row.get("strong_classic")
    if (
        not isinstance(strongs, list)
        or not strongs
        or any(not isinstance(value, str) or not value for value in strongs)
        or strongs != sorted(set(strongs))
    ):
        raise ValueError("Legacy baseline Strong occurrences are not canonical")
    if row.get("vote_weight") != 0:
        raise ValueError("Legacy baseline must retain zero vote weight")
    score = row.get("generator_score")
    raw = score.get("raw") if isinstance(score, dict) else None
    if raw != 0 and raw != 0.0:
        raise ValueError("Legacy baseline raw score must remain zero")
    identity = gold.target_to_edge[target_id]
    linked_originals = identity[2]
    for strong in strongs:
        matching = sorted(
            token_id for token_id in linked_originals if strong in original_strongs[token_id]
        )
        status = "correct" if len(matching) == 1 else "ambiguous" if len(matching) > 1 else "incorrect"
        yield {
            "strong_classic": strong,
            "target_token_id": target_id,
            "linked_gold_original_token_ids": list(linked_originals),
            "matching_gold_original_token_ids": matching,
            "legacy_status": status,
            "candidate_only": True,
            "production_accepted": False,
        }


def evaluate_candidate_artifacts(
    *,
    gold_report_dir: Path,
    token_inventory_path: Path,
    original_universe_path: Path,
    candidate_inputs: Mapping[str, Path],
    output_dir: Path,
    evaluation_folds: Iterable[int],
    fold_count: int = EVALUATION_FOLD_COUNT,
) -> dict[str, Any]:
    """Stream candidate rows and evaluate an isolated frozen-gold fold scope."""

    folds = _validated_folds(evaluation_folds, fold_count=fold_count)
    if not candidate_inputs:
        raise ValueError("At least one candidate input is required")
    normalized_inputs: dict[str, Path] = {}
    for label, path in candidate_inputs.items():
        if not isinstance(label, str) or _LABEL_RE.fullmatch(label) is None:
            raise ValueError("Candidate input label is not stable/canonical")
        if label in normalized_inputs:
            raise ValueError("Duplicate candidate input label")
        if not path.is_file():
            raise ValueError(f"Candidate input is missing: {label}")
        normalized_inputs[label] = path
    if output_dir.exists():
        raise ValueError("Evaluation output directory already exists")

    lock = validated_finalized_gold_lock(gold_report_dir)
    if lock is None:
        raise ValueError("Frozen finalized gold lock is absent")
    annotations_path = gold_report_dir / "gold_alignment.annotations.jsonl"
    manifest_path = gold_report_dir / "gold_alignment.manifest.json"
    lock_path = gold_report_dir / "gold_alignment.finalized.lock.json"
    token_inventory_sha256 = _sha256_file(token_inventory_path)
    original_universe_sha256 = _sha256_file(original_universe_path)
    if lock.get("corpus_contract") == "ohienko_1988_production":
        locked_inputs = lock.get("input_sha256")
        if not isinstance(locked_inputs, Mapping):
            raise ValueError("Frozen production gold lacks immutable input locks")
        if (
            locked_inputs.get("ukrainian_token_inventory")
            != token_inventory_sha256
        ):
            raise ValueError("Target token inventory differs from frozen gold")
        if (
            locked_inputs.get("gold_selected_original_layer")
            != original_universe_sha256
        ):
            raise ValueError("Selected original layer differs from frozen gold")
        frozen_manifest = _read_json(manifest_path)
        if (
            frozen_manifest.get("output_sha256", {}).get(
                "gold_selected_original_layer.jsonl"
            )
            != original_universe_sha256
        ):
            raise ValueError(
                "Frozen gold manifest does not lock the selected original layer"
            )
    target_ref_by_id, target_strata_by_ref = _load_target_grid(
        token_inventory_path,
        fold_count=fold_count,
    )
    original_ref_by_id, original_strongs = _load_original_grid(original_universe_path)
    gold = _load_gold_index(
        annotations_path,
        folds=folds,
        fold_count=fold_count,
        original_ref_by_id=original_ref_by_id,
        target_ref_by_id=target_ref_by_id,
        target_strata_by_ref=target_strata_by_ref,
    )

    input_sha256 = {
        "frozen_gold_annotations": _sha256_file(annotations_path),
        "frozen_gold_manifest": _sha256_file(manifest_path),
        "frozen_gold_lock": _sha256_file(lock_path),
        "target_token_inventory": token_inventory_sha256,
        "selected_original_universe": original_universe_sha256,
        **{
            f"candidate_input.{label}": _sha256_file(path)
            for label, path in sorted(normalized_inputs.items())
        },
    }
    if any(_SHA256_RE.fullmatch(value) is None for value in input_sha256.values()):
        raise RuntimeError("Internal SHA-256 serialization failure")

    temp_dir = output_dir.with_name(output_dir.name + ".tmp-evaluation")
    if temp_dir.exists():
        raise ValueError("Stale evaluation temporary directory exists")
    temp_dir.mkdir(parents=True)
    details_path = temp_dir / DETAILS_FILENAME
    details_digest = sha256()
    metrics_by_generator: dict[str, dict[str, Any]] = defaultdict(_new_metrics)
    legacy_metrics: dict[str, Any] = {
        "totals": Counter(),
        "folds": defaultdict(Counter),
        "strata": defaultdict(lambda: defaultdict(Counter)),
    }
    seen_candidate_ids: set[str] = set()
    counters: Counter[str] = Counter()
    try:
        with details_path.open("w", encoding="utf-8", newline="\n") as details:
            for input_label, input_path in sorted(normalized_inputs.items()):
                before_sha = input_sha256[f"candidate_input.{input_label}"]
                for source_sequence, row in enumerate(_read_jsonl(input_path), 1):
                    counters["candidate_rows_read"] += 1
                    target_ref = row.get("target_ref")
                    _parse_ref(target_ref)
                    target_ref = str(target_ref)
                    fold_id = _evaluation_fold(target_ref, fold_count)
                    if fold_id not in folds:
                        counters["skipped_outside_requested_folds"] += 1
                        continue
                    if target_ref not in gold.refs:
                        counters["skipped_outside_frozen_gold_refs"] += 1
                        continue
                    candidate_id, generator_id = _candidate_contract(row)
                    if candidate_id in seen_candidate_ids:
                        raise ValueError("Duplicate candidate ID across evaluation inputs")
                    seen_candidate_ids.add(candidate_id)
                    raw_score = row.get("generator_score")
                    metrics = metrics_by_generator[generator_id]
                    metrics[
                        "raw_score_present_count" if raw_score is not None else "raw_score_missing_count"
                    ] += 1
                    base = {
                        "schema_version": SCHEMA_VERSION,
                        "contract_version": CONTRACT_VERSION,
                        "evaluation_version": EVALUATION_VERSION,
                        "record_type": "candidate_evaluation",
                        "input_channel": input_label,
                        "source_sequence": source_sequence,
                        "candidate_id": candidate_id,
                        "generator_id": generator_id,
                        "target_ref": target_ref,
                        "fold_id": fold_id,
                        "raw_generator_score": raw_score,
                        "raw_score_calibrated": False,
                        "candidate_only": True,
                        "resolver_eligible": False,
                        "automatic_promotion_performed": False,
                        "threshold_tuning_performed": False,
                    }
                    if generator_id == LEGACY_GENERATOR_ID:
                        occurrences = list(
                            _legacy_occurrences(
                                row,
                                target_ref=target_ref,
                                gold=gold,
                                original_strongs=original_strongs,
                                target_ref_by_id=target_ref_by_id,
                            )
                        )
                        for occurrence in occurrences:
                            legacy_identity = gold.target_to_edge[
                                occurrence["target_token_id"]
                            ]
                            _legacy_increment(
                                legacy_metrics,
                                fold_id=fold_id,
                                strata=gold.edges[legacy_identity]["strata"],
                                status=occurrence["legacy_status"],
                            )
                        metrics["candidate_count"] += 1
                        metrics["folds"][str(fold_id)]["candidate_count"] += 1
                        detail = {
                            **base,
                            "evaluation_kind": "legacy_target_token_plus_strong_via_gold_original_map",
                            "legacy_occurrences": occurrences,
                            "production_accepted": False,
                        }
                    else:
                        identity = _candidate_identity(
                            row,
                            target_ref=target_ref,
                            gold=gold,
                            original_ref_by_id=original_ref_by_id,
                            original_strongs=original_strongs,
                            target_ref_by_id=target_ref_by_id,
                        )
                        matched = identity in gold.edges
                        matched_gold = gold.edges.get(identity)
                        strata = (
                            matched_gold["strata"]
                            if matched_gold is not None
                            else _gold_strata_for_nonmatch(
                                identity,
                                gold=gold,
                                target_strata_by_ref=target_strata_by_ref,
                            )
                        )
                        _metric_increment(
                            metrics,
                            fold_id=fold_id,
                            strata=strata,
                            matched=matched,
                        )
                        if matched:
                            metrics["matched_gold_identities"].add(identity)
                        detail = {
                            **base,
                            "evaluation_kind": "exact_complete_hyperedge_semantics",
                            "candidate_semantic": _identity_payload(identity),
                            "candidate_semantic_sha256": _sha256_json(_identity_payload(identity)),
                            "exact_match": matched,
                            "matched_gold_edge_id": (
                                matched_gold["edge_id"] if matched_gold is not None else None
                            ),
                            "partial_credit": False,
                            "position_or_neighbor_matching": False,
                            "verse_bag_matching": False,
                            "production_accepted": False,
                        }
                    encoded = stable_json(detail) + "\n"
                    details.write(encoded)
                    details_digest.update(encoded.encode("utf-8"))
                    counters["evaluated_candidate_rows"] += 1
                if _sha256_file(input_path) != before_sha:
                    raise ValueError("Candidate input changed while it was being evaluated")

        finalized_metrics: dict[str, Any] = {}
        for generator_id, metrics in sorted(metrics_by_generator.items()):
            if generator_id == LEGACY_GENERATOR_ID:
                totals = legacy_metrics["totals"]
                occurrences = totals["occurrence_count"]
                determinate = totals["correct"] + totals["incorrect"]
                fold_metrics, stratum_metrics = _finalize_legacy_buckets(
                    legacy_metrics
                )
                finalized_metrics[generator_id] = {
                    "evaluation_kind": "legacy_target_token_plus_strong_via_gold_original_map",
                    "candidate_count": int(metrics["candidate_count"]),
                    "legacy_occurrence_count": int(occurrences),
                    "correct_occurrences": int(totals["correct"]),
                    "incorrect_occurrences": int(totals["incorrect"]),
                    "ambiguous_occurrences": int(totals["ambiguous"]),
                    "strict_precision": _precision(totals["correct"], occurrences),
                    "determinate_precision": _precision(totals["correct"], determinate),
                    "fold_metrics": fold_metrics,
                    "stratum_metrics": stratum_metrics,
                    "raw_score_present_count": int(metrics["raw_score_present_count"]),
                    "raw_score_missing_count": int(metrics["raw_score_missing_count"]),
                    "zero_vote_enforced": True,
                    "ambiguous_counted_as_correct": False,
                    "scores_calibrated": False,
                    "threshold_tuning_performed": False,
                    "automatic_promotion_performed": False,
                }
            else:
                finalized_metrics[generator_id] = {
                    "evaluation_kind": "exact_complete_hyperedge_semantics",
                    **_finalize_metrics(metrics, gold_edge_count=len(gold.edges)),
                }

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "evaluation_version": EVALUATION_VERSION,
            "artifact": "frozen_gold_candidate_channel_evaluation",
            "status": "complete_candidate_only_no_calibration_no_promotion",
            "evaluation_scope": (
                "sealed_fold_isolated" if folds == {SEALED_EVALUATION_FOLD} else "unsealed_folds_only"
            ),
            "fold_count": fold_count,
            "fold_assignment": "int(SHA256(target_ref)[0:8],16) modulo 5",
            "evaluation_folds": sorted(folds),
            "sealed_fold": SEALED_EVALUATION_FOLD,
            "sealed_fold_mixed_with_other_folds": False,
            "input_sha256": dict(sorted(input_sha256.items())),
            "output_sha256": {DETAILS_FILENAME: details_digest.hexdigest()},
            "candidate_inputs": [
                {"input_channel": label, "sha256": input_sha256[f"candidate_input.{label}"]}
                for label in sorted(normalized_inputs)
            ],
            "generator_metrics": finalized_metrics,
            "processed_count": int(counters["evaluated_candidate_rows"]),
            "skipped_count": int(
                counters["skipped_outside_requested_folds"]
                + counters["skipped_outside_frozen_gold_refs"]
            ),
            "error_count": 0,
            "counts": {
                **dict(sorted(counters.items())),
                "frozen_gold_hyperedges": len(gold.edges),
                "frozen_gold_refs": len(gold.refs),
                "candidate_generators_evaluated": len(finalized_metrics),
            },
            "candidate_only": True,
            "raw_scores_retained_uncalibrated": True,
            "exact_stable_id_semantic_match_only": True,
            "partial_credit": False,
            "verse_bag_or_position_matching": False,
            "threshold_tuning_performed": False,
            "automatic_promotion_performed": False,
            "serialization": (
                "UTF-8 JSON/JSONL; sorted keys; compact separators; LF; "
                "candidate input labels sorted, source JSONL order retained"
            ),
        }
        _write_json(temp_dir / MANIFEST_FILENAME, manifest)
        temp_dir.rename(output_dir)
        return manifest
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise


def _candidate_arg(value: str) -> tuple[str, Path]:
    label, separator, raw_path = value.partition("=")
    if not separator or _LABEL_RE.fullmatch(label) is None or not raw_path:
        raise argparse.ArgumentTypeError("candidate input must be LABEL=PATH")
    return label, Path(raw_path)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold-report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--token-inventory",
        type=Path,
        default=DEFAULT_WORK / "ukrainian_token_inventory.jsonl",
    )
    parser.add_argument(
        "--original-universe",
        type=Path,
        default=DEFAULT_WORK / "gold_selected_original_layer.jsonl",
    )
    parser.add_argument("--candidate", action="append", type=_candidate_arg, required=True)
    parser.add_argument("--fold", action="append", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    candidate_inputs: dict[str, Path] = {}
    for label, path in args.candidate:
        if label in candidate_inputs:
            raise ValueError("Duplicate --candidate label")
        candidate_inputs[label] = path
    result = evaluate_candidate_artifacts(
        gold_report_dir=args.gold_report_dir,
        token_inventory_path=args.token_inventory,
        original_universe_path=args.original_universe,
        candidate_inputs=candidate_inputs,
        output_dir=args.output_dir,
        evaluation_folds=args.fold,
    )
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

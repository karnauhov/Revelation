"""Deferral-aware frozen evaluation; no training, calibration or promotion.

The immutable eligibility mask is the first consumer of gold labels.  A whole
candidate hyperedge touching a deferred endpoint is excluded before gold
membership, metadata or any statistic is consulted.  Physical identities and
candidate contracts are validated first, so deferral cannot hide real errors.
The historical strict evaluator and its sealed outputs are unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Any, Iterable, Mapping, Sequence

from scripts.bible_module import ukrainian_stage_7_evaluation as strict
from scripts.bible_module.ukrainian_stage_7_candidates import LEGACY_GENERATOR_ID
from scripts.bible_module.ukrainian_stage_7_model import CONTRACT_VERSION, SCHEMA_VERSION, stable_json

EVALUATION_VERSION = "ukrainian-stage-7-deferral-aware-frozen-evaluation-v3"
PIPELINE_VERSION = "ukrainian-stage-7-fixed-evaluation-pipeline-v1"
DETAILS_FILENAME = "candidate_gold_evaluation.v3.jsonl"
MANIFEST_FILENAME = "candidate_gold_evaluation.v3.manifest.json"
ANNOTATIONS_FILENAME = "gold_alignment.annotations.v2.jsonl"
ELIGIBILITY_FILENAME = "gold_alignment.eligibility.v2.jsonl"
LOCK_FILENAME = "gold_alignment.finalized.v2.lock.json"
GOLD_MANIFEST_FILENAME = "gold_alignment.finalized.v2.manifest.json"


def _validated_gold(report_dir: Path) -> Mapping[str, Any]:
    from scripts.bible_module.ukrainian_stage_7_gold_v2 import validated_finalized_gold_lock_v2
    lock = validated_finalized_gold_lock_v2(report_dir)
    if lock is None:
        raise ValueError("Deferral-aware frozen finalized gold lock is absent")
    return lock


def _locked_path(lock: Mapping[str, Any], key: str, fallback: Path) -> Path:
    value = lock.get(key)
    if value is None:
        return fallback
    path = Path(value)
    return path if path.is_absolute() else strict.ROOT / path


def _file_spec(path: Path) -> dict[str, Any]:
    return {"sha256": strict._sha256_file(path), "bytes": path.stat().st_size}


def _consumer_specs() -> dict[str, Any]:
    # Pin the complete stage-7 producer/consumer/validator family, including
    # transitive comparison, provenance and correction validators.
    return {path.name: _file_spec(path) for path in sorted(Path(__file__).parent.glob("ukrainian_stage_7*.py"))}


def _validate_provenance(pipeline: Mapping[str, Any]) -> None:
    for value in pipeline.get("provenance_specs", {}).values():
        path = (strict.ROOT / value["path"]).resolve()
        if not path.is_relative_to(strict.ROOT) or _file_spec(path) != {key: value[key] for key in ("sha256", "bytes")}:
            raise ValueError("Frozen candidate provenance is stale or outside repository")


def _inputs(
    gold_report_dir: Path, token_inventory_path: Path,
    original_universe_path: Path, candidate_inputs: Mapping[str, Path],
) -> tuple[Mapping[str, Any], dict[str, Path], dict[str, Any]]:
    if not candidate_inputs or any(strict._LABEL_RE.fullmatch(label) is None for label in candidate_inputs):
        raise ValueError("At least one canonically labelled candidate input is required")
    lock = _validated_gold(gold_report_dir)
    paths = {
        "frozen_gold_annotations": _locked_path(lock, "annotations_path", gold_report_dir / ANNOTATIONS_FILENAME),
        "frozen_gold_eligibility": _locked_path(lock, "eligibility_path", gold_report_dir / ELIGIBILITY_FILENAME),
        "frozen_gold_lock": gold_report_dir / LOCK_FILENAME,
        "target_token_inventory": token_inventory_path,
        "selected_original_universe": original_universe_path,
        **{"candidate_input." + label: path for label, path in sorted(candidate_inputs.items())},
    }
    specs = {name: _file_spec(path) for name, path in sorted(paths.items())}
    locked_inputs = lock.get("input_sha256", {})
    for key, name in (("ukrainian_token_inventory", "target_token_inventory"),
                      ("gold_selected_original_layer", "selected_original_universe")):
        if locked_inputs.get(key) != specs[name]["sha256"]:
            raise ValueError("Physical target/original layer differs from frozen gold: " + key)
    output_hashes = lock.get("output_sha256", {})
    for name in ("frozen_gold_annotations", "frozen_gold_eligibility"):
        if output_hashes.get(paths[name].name) != specs[name]["sha256"]:
            raise ValueError("Frozen gold output digest differs: " + name)
    return lock, paths, specs


def freeze_evaluation_pipeline(
    *, gold_report_dir: Path, token_inventory_path: Path, original_universe_path: Path,
    candidate_inputs: Mapping[str, Path], output_path: Path,
    provenance_inputs: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Seal code and fixed candidate inputs before any sealed-fold scoring."""
    if output_path.exists():
        raise ValueError("Frozen pipeline output already exists")
    _lock, _paths, specs = _inputs(gold_report_dir, token_inventory_path, original_universe_path, candidate_inputs)
    provenance = {label: {"path": path.resolve().relative_to(strict.ROOT).as_posix(), **_file_spec(path)}
                  for label, path in sorted((provenance_inputs or {}).items())}
    pipeline = {
        "pipeline_version": PIPELINE_VERSION, "evaluation_version": EVALUATION_VERSION,
        "artifact": "fixed_deferral_aware_evaluation_pipeline", "input_specs": specs,
        "consumer_specs": _consumer_specs(), "candidate_channels": sorted(candidate_inputs),
        "provenance_specs": provenance,
        "supersedes": {"evaluation_contract": strict.EVALUATION_VERSION,
                       "strict_implementation": {"path": Path(strict.__file__).relative_to(strict.ROOT).as_posix(),
                                                 **_file_spec(Path(strict.__file__))},
                       "prior_completed_sealed_evaluation": None,
                       "historical_implementation_and_sealed_artifacts_preserved": True},
        "fold_count": 5, "sealed_fold": 4,
        "eligibility_policy": "exclude_whole_hyperedge_if_any_endpoint_deferred_before_membership_or_statistics",
        "precision_unit": "unique_complete_candidate_semantic_hyperedge",
        "recall_unit": "unique_eligible_gold_complete_semantic_hyperedge",
        "legacy_precision_unit": "unique_target_token_plus_strong_occurrence",
        "legacy_recall_unit": "eligible_target_token_original_token_strong_triple",
        "source_frequency_stratum_basis": "fixed_primary_source_universe; eligible_originals_only; separate_from_reviewed_phenomena",
        "training_performed": False, "threshold_tuning_performed": False,
        "calibration_performed": False, "automatic_promotion_performed": False,
        "implementation_role": "implementation_author_not_independent_checker",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    strict._write_json(output_path, pipeline)
    return pipeline


@dataclass(frozen=True)
class Eligibility:
    original: Mapping[str, bool]
    target: Mapping[str, bool]
    stable_key_by_node: Mapping[tuple[str, str], str]
    refs: frozenset[str]

    def deferred(self, originals: Iterable[str], targets: Iterable[str]) -> bool:
        return any(not self.original[token] for token in originals) or any(not self.target[token] for token in targets)

    def coverage(self) -> dict[str, Any]:
        def counts(values: Mapping[str, bool]) -> dict[str, Any]:
            eligible = sum(values.values())
            return {"full": len(values), "eligible_proven": eligible,
                    "deferred_excluded": len(values) - eligible,
                    "proven_coverage": strict._precision(eligible, len(values))}
        return {"original_link_null_decisions": counts(self.original),
                "target_accounting": counts(self.target), "selected_verse_count": len(self.refs),
                "targets_or_classifiers_inflate_original_decision_count": False}


class GoldIndex:
    """Original decisions are unique; declared target spans may overlap."""
    def __init__(self) -> None:
        self.edges: dict[tuple[Any, ...], dict[str, Any]] = {}
        self.edge_by_id: dict[str, tuple[Any, ...]] = {}
        self.original_to_edge: dict[str, tuple[Any, ...]] = {}
        self.target_to_edges: dict[str, set[tuple[Any, ...]]] = defaultdict(set)
        self.refs: set[str] = set()


def _load_eligibility(
    path: Path, *, folds: frozenset[int], original_refs: Mapping[str, str], target_refs: Mapping[str, str],
) -> Eligibility:
    originals: dict[str, bool] = {}
    targets: dict[str, bool] = {}
    keys: dict[tuple[str, str], str] = {}
    seen_keys: set[str] = set()
    refs: set[str] = set()
    for row in strict._read_jsonl(path):
        ref = row.get("target_ref")
        strict._parse_ref(ref)
        if strict._evaluation_fold(ref, 5) not in folds:
            continue
        is_original = "original_token_id" in row
        is_target = "target_token_id" in row
        if is_original == is_target or row.get("record_type") != "gold_eligibility":
            raise ValueError("Eligibility must identify exactly one physical node")
        side = "original" if is_original else "target"
        token = row.get(side + "_token_id")
        mapping = originals if is_original else targets
        physical_refs = original_refs if is_original else target_refs
        key = row.get("stable_key")
        eligible = row.get("eligible")
        if not isinstance(key, str) or not key.startswith(side + ":") or key in seen_keys:
            raise ValueError("Eligibility has a missing, duplicate or wrong-side stable key")
        if not isinstance(token, str) or token in mapping or physical_refs.get(token) != ref:
            raise ValueError("Eligibility has a duplicate, dangling or cross-verse physical ID")
        if not isinstance(eligible, bool):
            raise ValueError("Eligibility must be an explicit boolean")
        mapping[token] = eligible
        keys[(side, token)] = key
        seen_keys.add(key)
        refs.add(ref)
    if not refs:
        raise ValueError("Requested evaluation folds have no frozen eligibility nodes")
    return Eligibility(originals, targets, keys, frozenset(refs))


def _physical_ids(
    row: Mapping[str, Any], *, ref: str, original_refs: Mapping[str, str], target_refs: Mapping[str, str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    originals = strict._canonical_ids(row.get("original_token_ids"), label="original IDs")
    targets = strict._canonical_ids(row.get("target_token_ids"), label="target IDs")
    if any(original_refs.get(token) != ref for token in originals):
        raise ValueError("Stale, dangling or cross-verse original ID")
    if any(target_refs.get(token) != ref for token in targets):
        raise ValueError("Stale, dangling or cross-verse target ID")
    return originals, targets


def _source_frequency_classes(row: Mapping[str, Any]) -> set[str]:
    """Read fixed source metadata only after this gold node is eligible."""
    value = row.get("derived_source_strata")
    if value is None:
        return set()
    if (not isinstance(value, Mapping)
            or value.get("basis") != "frozen_primary_universe_classic_frequency"
            or value.get("source_frequency_is_strong_assignment") is not False
            or not isinstance(value.get("proof_sha256"), str)
            or strict._SHA256_RE.fullmatch(value["proof_sha256"]) is None):
        raise ValueError("Derived source-frequency metadata lacks its frozen evidence contract")
    classes = value.get("frequency_classes")
    if (not isinstance(classes, list) or any(not isinstance(item, str) or item not in {"frequent_lemma", "rare_lemma"} for item in classes)
            or len(classes) != len(set(classes))):
        raise ValueError("Derived source-frequency classes are invalid")
    return set(classes)


def _overlapping_edges(identity: tuple[Any, ...], gold: GoldIndex) -> set[tuple[Any, ...]]:
    return {gold.original_to_edge[token] for token in identity[2]} | {
        edge for token in identity[3] for edge in gold.target_to_edges[token]}


def _source_frequency_for_candidate(identity: tuple[Any, ...], gold: GoldIndex) -> list[str]:
    if identity in gold.edges:
        return gold.edges[identity]["strata"]["source_frequency_classes"]
    overlapping = _overlapping_edges(identity, gold)
    return sorted({item for edge in overlapping for item in gold.edges[edge]["strata"]["source_frequency_classes"]}) or ["unclassified"]


def _union_edge_strata(identities: Iterable[tuple[Any, ...]], gold: GoldIndex, *, relation: str | None = None) -> dict[str, Any]:
    values = [gold.edges[edge]["strata"] for edge in identities]
    if not values:
        raise ValueError("Gold overlap has no eligible declared hyperedge")
    relations = {value["relation"] for value in values}
    return {"book": values[0]["book"], "testament": values[0]["testament"], "genre": values[0]["genre"],
            "relation": relation or (next(iter(relations)) if len(relations) == 1 else "overlapping_target_groups"),
            "severity": strict._severity(value["severity"] for value in values),
            "phenomena": sorted({item for value in values for item in value["phenomena"]}),
            "source_frequency_classes": sorted({item for value in values for item in value["source_frequency_classes"]})}


def _load_gold_index(
    path: Path, *, folds: frozenset[int], eligibility: Eligibility,
    original_refs: Mapping[str, str], target_refs: Mapping[str, str], target_strata: Mapping[str, Any],
) -> GoldIndex:
    """Filter before metadata, then require exact reciprocal eligible accounting."""
    gold = GoldIndex()
    original_rows: dict[str, Mapping[str, Any]] = {}
    target_rows: dict[str, Mapping[str, Any]] = {}
    seen_labels: set[str] = set()
    deferred_seen: set[tuple[str, str]] = set()
    for row in strict._read_jsonl(path):
        ref = row.get("target_ref")
        strict._parse_ref(ref)
        if strict._evaluation_fold(ref, 5) not in folds:
            continue
        kind = row.get("record_type")
        if kind == "hyperedge":
            if row.get("status") != "reviewed_accepted":
                raise ValueError("Gold hyperedge lacks reviewed acceptance")
            originals, targets = _physical_ids(row, ref=ref, original_refs=original_refs, target_refs=target_refs)
            if any(token not in eligibility.original for token in originals) or any(token not in eligibility.target for token in targets):
                raise ValueError("Gold hyperedge node is absent from frozen eligibility")
            # No relation, severity, phenomenon or other deferred label is read.
            if eligibility.deferred(originals, targets):
                raise ValueError("Finalized gold hyperedge contains a deferred endpoint")
            identity = strict._semantic_identity(target_ref=ref, relation=row.get("relation"), original_ids=originals,
                                                 target_ids=targets, null_reason=row.get("null_reason"))
            edge_id = row.get("edge_id")
            if not isinstance(edge_id, str) or not edge_id or edge_id in gold.edge_by_id or identity in gold.edges:
                raise ValueError("Gold has a duplicate or missing hyperedge identity")
            for token in originals:
                if token in gold.original_to_edge:
                    raise ValueError("Duplicate original assignment across gold hyperedges")
                gold.original_to_edge[token] = identity
            for token in targets:
                gold.target_to_edges[token].add(identity)
            gold.edge_by_id[edge_id] = identity
            gold.edges[identity] = {"edge_id": edge_id, "fold_id": strict._evaluation_fold(ref, 5)}
        elif kind in {"original_decision", "target_accounting", "deferred_original_decision", "deferred_target_accounting"}:
            side = "original" if "original_decision" in kind else "target"
            token = row.get(side + "_token_id")
            node = (side, token)
            mapping = eligibility.original if side == "original" else eligibility.target
            physical = original_refs if side == "original" else target_refs
            key = eligibility.stable_key_by_node.get(node)
            id_field = "decision_id" if side == "original" else "accounting_id"
            if physical.get(token) != ref or token not in mapping or key is None:
                raise ValueError("Gold accounting node is stale, dangling or outside eligibility")
            actual_key = row.get("stable_key") if kind.startswith("deferred_") else side + ":" + str(row.get(id_field))
            if actual_key != key or key in seen_labels:
                raise ValueError("Gold accounting stable key differs or is duplicated")
            seen_labels.add(key)
            if not mapping[token]:
                if not kind.startswith("deferred_") or row.get("status") != "deferred_strong_unassigned":
                    raise ValueError("Deferred gold node carries an accepted label")
                assignment_fields = ("relation", "null_reason", "strong_classic", "target_status", "decision_status",
                                     "original_token_ids", "target_token_ids", "group_original_token_ids",
                                     "linked_original_token_ids", "edge_id")
                if any(field in row for field in assignment_fields) or row.get("strong_assignment") is not None:
                    raise ValueError("Deferred gold node leaks an unproved assignment")
                deferred_seen.add(node)
                continue
            if kind.startswith("deferred_") or row.get("status") != "reviewed_accepted":
                raise ValueError("Eligible gold node lacks reviewed acceptance")
            (original_rows if side == "original" else target_rows)[token] = row
        else:
            raise ValueError("Unknown deferral-aware gold record type")
    expected_originals = {token for token, eligible in eligibility.original.items() if eligible}
    expected_targets = {token for token, eligible in eligibility.target.items() if eligible}
    expected_deferred = {(side, token) for side, values in (("original", eligibility.original), ("target", eligibility.target))
                         for token, eligible in values.items() if not eligible}
    if set(original_rows) != expected_originals or set(gold.original_to_edge) != expected_originals:
        raise ValueError("Eligible original accounting is incomplete or duplicated")
    if set(target_rows) != expected_targets or set(gold.target_to_edges) != expected_targets or deferred_seen != expected_deferred:
        raise ValueError("Target/deferred accounting is incomplete or duplicated")
    for token, row in original_rows.items():
        identity = gold.original_to_edge[token]
        group = strict._canonical_ids(row.get("group_original_token_ids"), label="gold original decision group")
        targets = strict._canonical_ids(row.get("target_token_ids"), label="gold original decision targets")
        semantic = strict._semantic_identity(target_ref=row["target_ref"], relation=row.get("relation"),
                                            original_ids=group, target_ids=targets, null_reason=row.get("null_reason"))
        if semantic != identity or row.get("edge_id") != gold.edges[identity]["edge_id"]:
            raise ValueError("Original decision differs from reciprocal gold hyperedge")
    for token, row in target_rows.items():
        identities = gold.target_to_edges[token]
        linked = strict._canonical_ids(row.get("linked_original_token_ids"), label="gold linked original IDs")
        expected_linked = tuple(sorted({original for identity in identities for original in identity[2]}))
        if expected_linked:
            if any(not identity[2] for identity in identities):
                raise ValueError("Target is both an aligned span and a translation addition")
            expected_status = "aligned"
        else:
            if len(identities) != 1:
                raise ValueError("Target has conflicting translation-addition accounting")
            expected_status = next(iter(identities))[4]
        if linked != expected_linked or row.get("target_status") != expected_status:
            raise ValueError("Target accounting differs from reciprocal gold hyperedge")
    # Only proven eligible rows now contribute metadata or strata.
    for identity, value in gold.edges.items():
        rows = [original_rows[token] for token in identity[2]] + [target_rows[token] for token in identity[3]]
        strata = target_strata[identity[0]]
        value["strata"] = {"testament": strata["testament"], "book": strata["book"], "genre": strata["genre"],
                           "relation": identity[1], "severity": strict._severity(str(row.get("severity", "unclassified")) for row in rows),
                           "phenomena": sorted({str(item) for row in rows for item in row.get("phenomena", ())}) or ["unclassified"],
                           "source_frequency_classes": sorted({item for token in identity[2]
                               for item in _source_frequency_classes(original_rows[token])}) or ["unclassified"]}
    gold.refs = set(eligibility.refs)
    return gold


def _candidate_identity(
    row: Mapping[str, Any], *, ref: str, original_refs: Mapping[str, str], target_refs: Mapping[str, str],
    original_strongs: Mapping[str, tuple[str, ...]], legacy: bool,
) -> tuple[Any, ...]:
    originals, targets = _physical_ids(row, ref=ref, original_refs=original_refs, target_refs=target_refs)
    strongs = row.get("strong_classic")
    if not isinstance(strongs, list) or any(not isinstance(value, str) or not value for value in strongs) or strongs != sorted(set(strongs)):
        raise ValueError("Candidate Strong list is not canonical")
    if legacy:
        if originals or len(targets) != 1 or not strongs or row.get("relation") != "legacy_unproven_feature":
            raise ValueError("Legacy baseline requires one target and no current original")
        score = row.get("generator_score")
        if row.get("vote_weight") != 0 or not isinstance(score, dict) or score.get("raw") != 0:
            raise ValueError("Legacy baseline must retain zero vote/raw score")
        return ref, "legacy_unproven_feature", originals, targets, None
    expected = sorted({strong for token in originals for strong in original_strongs[token]})
    if strongs != expected:
        raise ValueError("Candidate Strong list is not derived from its original IDs")
    return strict._semantic_identity(target_ref=ref, relation=row.get("relation"), original_ids=originals,
                                     target_ids=targets, null_reason=row.get("null_reason"))


def _taxonomy(identity: tuple[Any, ...], gold: GoldIndex) -> str:
    if identity in gold.edges:
        return "exact_complete_hyperedge"
    overlaps = _overlapping_edges(identity, gold)
    if any(other[2:4] == identity[2:4] and other[1] == identity[1] for other in overlaps):
        return "wrong_null_reason"
    if any(other[2:4] == identity[2:4] for other in overlaps):
        return "wrong_relation"
    if len(overlaps) > 1:
        return "cross_gold_group_endpoints"
    return "incomplete_or_wrong_group_endpoints"


def _final_metrics(metrics: Mapping[str, Any], gold: GoldIndex) -> dict[str, Any]:
    predicted = metrics["identities"]
    tp = len(predicted & gold.edges.keys())
    fp = len(predicted) - tp
    fn = len(gold.edges) - tp
    gold_strata: dict[str, Counter[str]] = defaultdict(Counter)
    gold_folds: Counter[str] = Counter()
    for value in gold.edges.values():
        gold_folds[str(value["fold_id"])] += 1
        for field in ("testament", "book", "relation", "severity", "genre"):
            gold_strata[field][str(value["strata"][field])] += 1
        for phenomenon in value["strata"]["phenomena"]:
            gold_strata["phenomenon"][phenomenon] += 1
        for source_class in value["strata"]["source_frequency_classes"]:
            gold_strata["source_frequency"][source_class] += 1

    def bucket(predictions: Mapping[str, Any], support: int) -> dict[str, Any]:
        correct = int(predictions.get("exact_match_count", 0))
        candidate_count = int(predictions.get("candidate_count", 0))
        return {"candidate_count": candidate_count, "eligible_gold_support": support,
                "true_positive": correct, "false_positive": candidate_count - correct,
                "false_negative": support - correct, "precision_denominator_tp_plus_fp": candidate_count,
                "recall_denominator_tp_plus_fn": support, "exact_precision": strict._precision(correct, candidate_count),
                "exact_recall": strict._precision(correct, support)}

    strata = {field: {value: bucket(metrics["strata"]["strata"].get(field, {}).get(value, {}), gold_strata[field][value])
                      for value in sorted(set(gold_strata[field]) | set(metrics["strata"]["strata"].get(field, {})))}
              for field in sorted(set(gold_strata) | set(metrics["strata"]["strata"]))}
    fold_metrics = {fold: bucket(metrics["strata"]["folds"].get(fold, {}), gold_folds[fold])
                    for fold in sorted(set(gold_folds) | set(metrics["strata"]["folds"]))}
    return {"eligible_candidate_rows": metrics["rows"], "unique_candidate_hyperedges": len(predicted),
            "duplicate_semantic_prediction_rows": metrics["rows"] - len(predicted),
            "true_positive": tp, "false_positive": fp, "false_negative": fn,
            "precision_denominator_tp_plus_fp": tp + fp, "recall_denominator_tp_plus_fn": tp + fn,
            "exact_precision": strict._precision(tp, tp + fp), "exact_recall": strict._precision(tp, tp + fn),
            "row_exact_match_count": metrics["row_matches"], "row_precision_denominator": metrics["rows"],
            "row_exact_precision": strict._precision(metrics["row_matches"], metrics["rows"]),
            "error_taxonomy_unique_hyperedges": dict(sorted(metrics["taxonomy"].items())),
            "duplicate_prediction_taxonomy": "reported_separately_no_metric_inflation",
            "stratum_metrics": strata, "fold_metrics": fold_metrics,
            "threshold_tuning_performed": False, "training_performed": False, "automatic_promotion_performed": False}


def _validate_unsealed_predecessor(path: Path, pipeline_sha: str, specs: Mapping[str, Any], *,
                                  evaluation_parent: Path) -> dict[str, Any]:
    predecessor = strict._read_json(path)
    if (predecessor.get("evaluation_version") != EVALUATION_VERSION
            or predecessor.get("artifact") != "deferral_aware_frozen_gold_evaluation"
            or predecessor.get("status") != "complete_evaluation_only_no_training_tuning_or_promotion"
            or predecessor.get("evaluation_scope") != "unsealed_folds_only"
            or predecessor.get("evaluation_folds") != [0, 1, 2, 3]
            or predecessor.get("frozen_pipeline_sha256") != pipeline_sha
            or predecessor.get("input_specs") != specs
            or predecessor.get("error_count") != 0
            or predecessor.get("training_performed") is not False
            or predecessor.get("threshold_tuning_performed") is not False):
        raise ValueError("Unsealed predecessor is incomplete or does not match frozen pipeline")
    details = path.parent / DETAILS_FILENAME
    if not details.is_file() or predecessor.get("output_sha256", {}).get(DETAILS_FILENAME) != strict._sha256_file(details):
        raise ValueError("Unsealed predecessor details are absent or stale")
    evaluated = excluded = 0
    for row in strict._read_jsonl(details):
        if row.get("evaluation_version") != EVALUATION_VERSION or row.get("fold_id") not in (0, 1, 2, 3):
            raise ValueError("Unsealed predecessor details contain an invalid contract or sealed fold")
        if row.get("evaluation_status") == "evaluated":
            evaluated += 1
        elif row.get("evaluation_status") == "excluded_deferred_endpoint":
            excluded += 1
        else:
            raise ValueError("Unsealed predecessor detail has no completed evaluation status")
    if predecessor.get("processed_count") != evaluated or predecessor.get("counts", {}).get("excluded_deferred_candidate_rows", 0) != excluded:
        raise ValueError("Unsealed predecessor counts differ from its physical details")
    relative_path = path.resolve().relative_to(evaluation_parent.resolve()).as_posix()
    return {"manifest_path_relative_to_evaluation_parent": relative_path, **_file_spec(path)}


def evaluate_candidate_artifacts(
    *, gold_report_dir: Path, token_inventory_path: Path, original_universe_path: Path,
    candidate_inputs: Mapping[str, Path], output_dir: Path, evaluation_folds: Iterable[int],
    frozen_pipeline_path: Path, unsealed_manifest_path: Path | None = None,
) -> dict[str, Any]:
    folds = strict._validated_folds(evaluation_folds, fold_count=5)
    if output_dir.exists():
        raise ValueError("Evaluation output directory already exists")
    _lock, paths, specs = _inputs(gold_report_dir, token_inventory_path, original_universe_path, candidate_inputs)
    pipeline = strict._read_json(frozen_pipeline_path)
    if pipeline.get("pipeline_version") != PIPELINE_VERSION or pipeline.get("evaluation_version") != EVALUATION_VERSION:
        raise ValueError("Frozen pipeline contract differs")
    if pipeline.get("input_specs") != specs or pipeline.get("consumer_specs") != _consumer_specs():
        raise ValueError("Inputs or consumer code changed after pipeline freeze")
    if pipeline.get("candidate_channels") != sorted(candidate_inputs):
        raise ValueError("Candidate channels differ from frozen pipeline")
    _validate_provenance(pipeline)
    pipeline_sha = strict._sha256_file(frozen_pipeline_path)
    supersedes = None
    if folds == {4}:
        if unsealed_manifest_path is None:
            raise ValueError("Sealed evaluation requires completed unsealed evaluation of the same frozen pipeline")
        supersedes = _validate_unsealed_predecessor(unsealed_manifest_path, pipeline_sha, specs,
                                                   evaluation_parent=output_dir.parent)
    elif unsealed_manifest_path is not None:
        raise ValueError("Only sealed evaluation may name an unsealed predecessor")
    targets, strata = strict._load_target_grid(token_inventory_path, fold_count=5)
    originals, strongs = strict._load_original_grid(original_universe_path)
    eligibility = _load_eligibility(paths["frozen_gold_eligibility"], folds=folds, original_refs=originals, target_refs=targets)
    gold = _load_gold_index(paths["frozen_gold_annotations"], folds=folds, eligibility=eligibility,
                            original_refs=originals, target_refs=targets, target_strata=strata)
    temp = output_dir.with_name(output_dir.name + ".tmp-evaluation-v3")
    if temp.exists():
        raise ValueError("Stale evaluation temporary directory exists")
    temp.mkdir(parents=True)
    seen: set[str] = set()
    counters: Counter[str] = Counter()
    excluded: dict[str, Counter[str]] = defaultdict(Counter)
    metrics: dict[str, Any] = defaultdict(lambda: {"rows": 0, "row_matches": 0, "identities": set(),
                                                  "taxonomy": Counter(), "strata": strict._new_metrics()})
    legacy_originals = {target: sorted({original for edge in edges for original in edge[2]})
                        for target, edges in gold.target_to_edges.items()}
    legacy_strata = {target: _union_edge_strata(edges, gold) for target, edges in gold.target_to_edges.items()}
    legacy_units = {(target, original, strong) for target, original_ids in legacy_originals.items()
                    for original in original_ids for strong in strongs[original]}
    legacy_predictions: dict[tuple[str, str], str] = {}
    legacy_true: set[tuple[str, str, str]] = set()
    legacy_row_taxonomy: Counter[str] = Counter()
    legacy_buckets: dict[str, Any] = {"totals": Counter(), "folds": defaultdict(Counter),
                                       "strata": defaultdict(lambda: defaultdict(Counter))}
    # Gold-only legacy strata must retain their recall denominator even when
    # the fixed baseline predicts no occurrence in that stratum.
    for target, _original, _strong in legacy_units:
        values = legacy_strata[target]
        legacy_buckets["folds"][str(strict._evaluation_fold(targets[target], 5))]["occurrence_count"] += 0
        for field in ("testament", "book", "relation", "severity", "genre"):
            legacy_buckets["strata"][field][str(values[field])]["occurrence_count"] += 0
        for field, key in (("phenomenon", "phenomena"), ("source_frequency", "source_frequency_classes")):
            for value in values[key]:
                legacy_buckets["strata"][field][value]["occurrence_count"] += 0
    legacy_rows = 0
    try:
        with (temp / DETAILS_FILENAME).open("w", encoding="utf-8", newline="\n") as output:
            for label, path in sorted(candidate_inputs.items()):
                for sequence, row in enumerate(strict._read_jsonl(path), 1):
                    counters["candidate_rows_read"] += 1
                    ref = row.get("target_ref")
                    strict._parse_ref(ref)
                    fold = strict._evaluation_fold(ref, 5)
                    if fold not in folds:
                        counters["outside_requested_folds"] += 1
                        continue
                    candidate_id, generator = strict._candidate_contract(row)
                    if candidate_id in seen:
                        raise ValueError("Duplicate candidate ID across evaluation inputs")
                    seen.add(candidate_id)
                    legacy = generator == LEGACY_GENERATOR_ID
                    if not legacy:
                        metrics[generator]  # Preserve zero-support, fully excluded channels.
                    identity = _candidate_identity(row, ref=ref, original_refs=originals, target_refs=targets,
                                                   original_strongs=strongs, legacy=legacy)
                    if ref not in eligibility.refs:
                        counters["outside_frozen_gold_refs"] += 1
                        continue
                    if any(token not in eligibility.original for token in identity[2]) or any(token not in eligibility.target for token in identity[3]):
                        raise ValueError("Candidate node is outside frozen gold eligibility grid")
                    detail = {"evaluation_version": EVALUATION_VERSION, "candidate_id": candidate_id,
                              "generator_id": generator, "input_channel": label, "source_sequence": sequence,
                              "target_ref": ref, "fold_id": fold, "candidate_only": True, "production_accepted": False}
                    # THIS guard precedes all membership checks and gold-derived statistics.
                    if eligibility.deferred(identity[2], identity[3]):
                        excluded[generator]["candidate_rows"] += 1
                        excluded[generator]["legacy_strong_occurrences"] += len(row["strong_classic"]) if legacy else 0
                        counters["excluded_deferred_candidate_rows"] += 1
                        detail.update({"evaluation_status": "excluded_deferred_endpoint", "whole_hyperedge_excluded": True,
                                       "contributes_to_tp_fp_fn_or_support": False})
                    elif legacy:
                        legacy_rows += 1
                        target = identity[3][0]
                        linked_originals = legacy_originals[target]
                        occurrences = []
                        for strong in row["strong_classic"]:
                            matching = [token for token in linked_originals if strong in strongs[token]]
                            status = "correct" if len(matching) == 1 else "ambiguous" if matching else "incorrect"
                            legacy_row_taxonomy[status] += 1
                            strict._legacy_increment(legacy_buckets, fold_id=fold, strata=legacy_strata[target], status=status)
                            for source_class in legacy_strata[target]["source_frequency_classes"]:
                                source_bucket = legacy_buckets["strata"]["source_frequency"][source_class]
                                source_bucket["occurrence_count"] += 1
                                source_bucket[status] += 1
                            key = (target, strong)
                            duplicate = key in legacy_predictions
                            legacy_predictions[key] = status
                            if status == "correct":
                                legacy_true.add((target, matching[0], strong))
                            occurrences.append({"target_token_id": target, "strong_classic": strong, "status": status,
                                                "duplicate_semantic_prediction": duplicate})
                        detail.update({"evaluation_status": "evaluated", "legacy_occurrences": occurrences,
                                       "raw_generator_score": row.get("generator_score")})
                        counters["evaluated_candidate_rows"] += 1
                    else:
                        # Membership against the proven index is impossible before the guard above.
                        matched = identity in gold.edges
                        metric = metrics[generator]
                        metric["rows"] += 1
                        metric["row_matches"] += int(matched)
                        duplicate = identity in metric["identities"]
                        taxonomy = _taxonomy(identity, gold)
                        if not duplicate:
                            metric["identities"].add(identity)
                            metric["taxonomy"][taxonomy] += 1
                            values = gold.edges[identity]["strata"] if matched else _union_edge_strata(_overlapping_edges(identity, gold), gold, relation=str(identity[1]))
                            strict._metric_increment(metric["strata"], fold_id=fold, strata=values, matched=matched)
                            for source_class in _source_frequency_for_candidate(identity, gold):
                                source_bucket = metric["strata"]["strata"]["source_frequency"][source_class]
                                source_bucket["candidate_count"] += 1
                                source_bucket["exact_match_count"] += int(matched)
                        detail.update({"evaluation_status": "evaluated", "candidate_semantic": strict._identity_payload(identity),
                                       "exact_match": matched, "error_taxonomy": taxonomy,
                                       "duplicate_semantic_prediction": duplicate, "raw_generator_score": row.get("generator_score")})
                        counters["evaluated_candidate_rows"] += 1
                    output.write(stable_json(detail) + "\n")
            finalized = {generator: _final_metrics(value, gold) for generator, value in sorted(metrics.items())}
            if legacy_rows or LEGACY_GENERATOR_ID in excluded:
                counts = Counter(legacy_predictions.values())
                occurrence_rows = sum(legacy_row_taxonomy.values())
                legacy_fold_metrics, legacy_stratum_metrics = strict._finalize_legacy_buckets(legacy_buckets)

                def complete_legacy_bucket(bucket: dict[str, Any], units: set[tuple[str, str, str]]) -> None:
                    bucket["strict_precision_denominator"] = bucket["occurrence_count"]
                    bucket["eligible_gold_target_original_strong_support"] = len(units)
                    bucket["unique_true_positive"] = len(units & legacy_true)
                    bucket["unique_false_negative"] = len(units - legacy_true)
                    bucket["exact_recall"] = strict._precision(len(units & legacy_true), len(units))

                for fold, value in legacy_fold_metrics.items():
                    units = {unit for unit in legacy_units if strict._evaluation_fold(targets[unit[0]], 5) == int(fold)}
                    complete_legacy_bucket(value, units)
                for field, values in legacy_stratum_metrics.items():
                    for value, bucket in values.items():
                        def in_stratum(unit: tuple[str, str, str]) -> bool:
                            strata_value = legacy_strata[unit[0]]
                            if field == "phenomenon":
                                return value in strata_value["phenomena"]
                            if field == "source_frequency":
                                return value in strata_value["source_frequency_classes"]
                            return str(strata_value[field]) == value
                        complete_legacy_bucket(bucket, {unit for unit in legacy_units if in_stratum(unit)})
                tp = len(legacy_true)
                fp = counts["incorrect"] + counts["ambiguous"]
                fn = len(legacy_units - legacy_true)
                finalized[LEGACY_GENERATOR_ID] = {"evaluation_kind": "legacy_target_strong_unique_original_identification",
                    "eligible_candidate_rows": legacy_rows, "unique_occurrence_count": len(legacy_predictions),
                    "legacy_occurrence_count": occurrence_rows,
                    "duplicate_semantic_occurrence_rows": occurrence_rows - len(legacy_predictions),
                    "true_positive": tp, "false_positive": fp, "false_negative": fn,
                    "correct_occurrences": legacy_row_taxonomy["correct"], "incorrect_occurrences": legacy_row_taxonomy["incorrect"],
                    "ambiguous_occurrences": legacy_row_taxonomy["ambiguous"],
                    "unique_occurrence_error_taxonomy": dict(sorted(counts.items())),
                    "fold_metrics": legacy_fold_metrics, "stratum_metrics": legacy_stratum_metrics,
                    "precision_denominator_tp_plus_fp": tp + fp,
                    "recall_denominator_eligible_target_original_strong_triples": len(legacy_units),
                    "strict_precision": strict._precision(legacy_row_taxonomy["correct"], occurrence_rows),
                    "strict_row_precision_denominator": occurrence_rows,
                    "unique_exact_precision": strict._precision(tp, tp + fp), "exact_recall": strict._precision(tp, len(legacy_units)),
                    "omitted_originals_in_legacy_recall_denominator": False, "zero_vote_enforced": True,
                    "stratification": "union_of_all_eligible_declared_gold_groups_at_target",
                    "ambiguous_counted_as_correct": False, "training_performed": False, "threshold_tuning_performed": False}
        for name, path in paths.items():
            if _file_spec(path) != specs[name]:
                raise ValueError("Input changed during evaluation: " + name)
        if strict._sha256_file(frozen_pipeline_path) != pipeline_sha or pipeline["consumer_specs"] != _consumer_specs():
            raise ValueError("Frozen pipeline changed during evaluation")
        _validate_provenance(pipeline)
        manifest = {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION,
            "evaluation_version": EVALUATION_VERSION, "artifact": "deferral_aware_frozen_gold_evaluation",
            "status": "complete_evaluation_only_no_training_tuning_or_promotion", "evaluation_folds": sorted(folds),
            "evaluation_scope": "sealed_fold_isolated" if folds == {4} else "unsealed_folds_only",
            "fold_count": 5, "sealed_fold": 4, "sealed_fold_mixed_with_other_folds": False,
            "frozen_pipeline_sha256": pipeline_sha, "input_specs": specs, "unsealed_predecessor": supersedes,
            "supersedes": {**pipeline["supersedes"], "unsealed_evaluation": supersedes},
            "coverage": eligibility.coverage(), "eligible_gold_hyperedges": len(gold.edges),
            "generator_metrics": finalized, "excluded_from_all_metrics": {key: dict(sorted(value.items())) for key, value in sorted(excluded.items())},
            "counts": dict(sorted(counters.items())), "processed_count": counters["evaluated_candidate_rows"],
            "skipped_count": counters["outside_requested_folds"] + counters["outside_frozen_gold_refs"] + counters["excluded_deferred_candidate_rows"],
            "error_count": 0, "output_sha256": {DETAILS_FILENAME: strict._sha256_file(temp / DETAILS_FILENAME)},
            "eligibility_applied_before_membership_and_all_gold_statistics": True,
            "training_performed": False, "threshold_tuning_performed": False, "calibration_performed": False,
            "automatic_promotion_performed": False, "implementation_role": "implementation_author_not_independent_checker"}
        strict._write_json(temp / MANIFEST_FILENAME, manifest)
        temp.rename(output_dir)
        return manifest
    except Exception:
        if temp.exists():
            shutil.rmtree(temp)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold-report-dir", type=Path, default=strict.DEFAULT_REPORT)
    parser.add_argument("--token-inventory", type=Path, default=strict.DEFAULT_WORK / "ukrainian_token_inventory.jsonl")
    parser.add_argument("--original-universe", type=Path, default=strict.DEFAULT_WORK / "gold_selected_original_layer.jsonl")
    parser.add_argument("--candidate", type=strict._candidate_arg, action="append", required=True)
    parser.add_argument("--pipeline", type=Path, required=True)
    parser.add_argument("--freeze-pipeline", action="store_true")
    parser.add_argument("--fold", type=int, action="append")
    parser.add_argument("--unsealed-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    candidates = dict(args.candidate)
    if len(candidates) != len(args.candidate):
        raise ValueError("Duplicate candidate input label")
    common = dict(gold_report_dir=args.gold_report_dir, token_inventory_path=args.token_inventory,
                  original_universe_path=args.original_universe, candidate_inputs=candidates)
    if args.freeze_pipeline:
        result = freeze_evaluation_pipeline(**common, output_path=args.pipeline)
    else:
        if not args.fold or args.output_dir is None:
            parser.error("evaluation requires --fold and --output-dir")
        result = evaluate_candidate_artifacts(**common, frozen_pipeline_path=args.pipeline, output_dir=args.output_dir,
                                               evaluation_folds=args.fold, unsealed_manifest_path=args.unsealed_manifest)
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

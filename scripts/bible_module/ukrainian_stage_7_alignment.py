"""Pure constrained-hypergraph and calibration contracts for Ukrainian stage 7.

The candidate generators intentionally emit ``resolver_eligible=false``.  This
module accepts only a later, calibrated promotion layer and therefore cannot
turn raw bridge, legacy, frequency or positional features into Strong markup.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from typing import Any, Iterable, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_model import (
    candidate_is_evidence_backed,
    override_is_current,
    stable_json,
    validate_hyperedge,
    wilson_lower_bound,
)


ALIGNMENT_RESOLVER_VERSION = "ukrainian-stage-7-hypergraph-v1"
CALIBRATION_VERSION = "ukrainian-stage-7-wilson-crossfold-v1"
AUTO_LOWER_BOUND = 0.995
CALIBRATION_FOLDS = frozenset({0, 1, 2})
VALIDATION_FOLD = 3
SEALED_EVALUATION_FOLD = 4
AUTO_STRATUM_FIELDS = (
    "testament",
    "book",
    "genre",
    "anomaly_type",
    "evidence_class",
)


def _edge_id(edge: Mapping[str, Any]) -> str:
    value = edge.get("candidate_id") or edge.get("edge_id")
    if isinstance(value, str) and value:
        return value
    identity = {
        "target_ref": edge.get("target_ref"),
        "original_token_ids": list(edge.get("original_token_ids", ())),
        "target_token_ids": list(edge.get("target_token_ids", ())),
        "relation": edge.get("relation"),
        "evidence_channels": sorted(edge.get("evidence_channels", ())),
    }
    return "uk7edge:" + sha256(stable_json(identity).encode("utf-8")).hexdigest()


def _resolver_score(edge: Mapping[str, Any]) -> float:
    value = edge.get("calibrated_probability")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("Resolver edge requires a calibrated probability")
    score = float(value)
    if not 0.0 <= score <= 1.0:
        raise ValueError("Calibrated probability is outside [0,1]")
    return score


def rank_verse_hypergraph_solutions(
    candidates: Iterable[Mapping[str, Any]],
    *,
    target_ref: str,
    valid_original_ids: set[str],
    valid_target_token_ids: set[str],
    original_ref_by_id: Mapping[str, str],
    target_ref_by_id: Mapping[str, str],
    top_k: int = 5,
    beam_width: int = 512,
) -> dict[str, Any]:
    """Return deterministic non-overlapping top-k candidate decompositions.

    Word order never contributes to the score.  It is used only for canonical
    serialization outside this function.  Raw candidates remain rejected until
    an explicit calibration layer sets ``resolver_eligible=true`` and supplies
    a calibrated probability.
    """

    if not target_ref or top_k < 1 or beam_width < top_k:
        raise ValueError("Invalid hypergraph resolver configuration")
    accepted: list[dict[str, Any]] = []
    rejected = Counter()
    for raw in candidates:
        edge = dict(raw)
        if edge.get("target_ref") != target_ref:
            rejected["other_verse"] += 1
            continue
        if edge.get("resolver_eligible") is not True:
            rejected["not_resolver_eligible"] += 1
            continue
        if edge.get("textual_status") in {
            "unresolved",
            "unresolved_blocking",
            "alternative_unadjudicated",
        }:
            rejected["unresolved_textual_status"] += 1
            continue
        try:
            validate_hyperedge(
                edge,
                valid_original_ids=valid_original_ids,
                valid_target_token_ids=valid_target_token_ids,
                original_ref_by_id=original_ref_by_id,
                target_ref_by_id=target_ref_by_id,
            )
            score = _resolver_score(edge)
        except ValueError:
            rejected["invalid_edge"] += 1
            continue
        edge["resolved_edge_id"] = _edge_id(edge)
        edge["calibrated_probability"] = score
        accepted.append(edge)

    accepted.sort(
        key=lambda edge: (
            -float(edge["calibrated_probability"]),
            edge["resolved_edge_id"],
        )
    )
    # state = score, edge IDs, used original IDs, used target IDs
    states: list[tuple[float, tuple[str, ...], frozenset[str], frozenset[str]]] = [
        (0.0, (), frozenset(), frozenset())
    ]
    by_id = {edge["resolved_edge_id"]: edge for edge in accepted}
    for edge in accepted:
        edge_id = str(edge["resolved_edge_id"])
        originals = frozenset(str(value) for value in edge["original_token_ids"])
        targets = frozenset(str(value) for value in edge["target_token_ids"])
        expanded = list(states)
        for score, edge_ids, used_originals, used_targets in states:
            if originals & used_originals or targets & used_targets:
                continue
            expanded.append(
                (
                    score + float(edge["calibrated_probability"]),
                    tuple(sorted((*edge_ids, edge_id))),
                    used_originals | originals,
                    used_targets | targets,
                )
            )
        unique: dict[
            tuple[frozenset[str], frozenset[str], tuple[str, ...]],
            tuple[float, tuple[str, ...], frozenset[str], frozenset[str]],
        ] = {}
        for state in expanded:
            key = (state[2], state[3], state[1])
            previous = unique.get(key)
            if previous is None or state[0] > previous[0]:
                unique[key] = state
        states = sorted(unique.values(), key=lambda item: (-item[0], item[1]))[
            :beam_width
        ]

    nonempty = [state for state in states if state[1]]
    ranked = sorted(nonempty, key=lambda item: (-item[0], item[1]))[:top_k]
    solutions: list[dict[str, Any]] = []
    for rank, (score, edge_ids, originals, targets) in enumerate(ranked, 1):
        solutions.append(
            {
                "schema_version": 1,
                "resolver_version": ALIGNMENT_RESOLVER_VERSION,
                "target_ref": target_ref,
                "rank": rank,
                "score_sum": score,
                "edge_ids": list(edge_ids),
                "decomposition": [by_id[edge_id] for edge_id in edge_ids],
                "covered_original_token_ids": sorted(originals),
                "covered_target_token_ids": sorted(targets),
                "unaccounted_original_token_ids": sorted(
                    valid_original_ids - set(originals)
                ),
                "unaccounted_target_token_ids": sorted(
                    valid_target_token_ids - set(targets)
                ),
                "candidate_only": True,
                "production_accepted": False,
            }
        )
    return {
        "schema_version": 1,
        "resolver_version": ALIGNMENT_RESOLVER_VERSION,
        "target_ref": target_ref,
        "status": "candidate_solutions_only",
        "candidate_count": len(accepted),
        "rejected_counts": dict(sorted(rejected.items())),
        "solutions": solutions,
        "processed_count": len(accepted) + sum(rejected.values()),
        "skipped_count": sum(rejected.values()),
        "error_count": 0,
    }


def precision_metrics(correct: int, support: int) -> dict[str, Any]:
    if support < 0 or correct < 0 or correct > support:
        raise ValueError("Invalid precision counts")
    lower = wilson_lower_bound(correct, support)
    return {
        "correct": correct,
        "support": support,
        "precision": correct / support if support else None,
        "one_sided_wilson_lower_bound": lower if support else None,
        "auto_enabled": support > 0 and lower >= AUTO_LOWER_BOUND,
    }


def _evaluated_rows(
    decisions: Sequence[Mapping[str, Any]],
    *,
    threshold: float,
    allowed_folds: set[int],
) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for row in decisions:
        fold = row.get("fold_id")
        if fold == SEALED_EVALUATION_FOLD:
            raise ValueError("Sealed evaluation fold cannot be read during calibration")
        if fold not in allowed_folds:
            raise ValueError("Decision appears in the wrong calibration fold")
        if row.get("label_source") != "frozen_gold":
            raise ValueError("Calibration decision is not from frozen gold")
        score = row.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise ValueError("Calibration score is invalid")
        if float(score) >= threshold and row.get("eligible") is True:
            if row.get("correct") not in {True, False}:
                raise ValueError("Calibration correctness label is invalid")
            rows.append(row)
    return rows


def evaluate_threshold(
    decisions: Sequence[Mapping[str, Any]],
    *,
    threshold: float,
    allowed_folds: set[int],
    stratum_fields: Sequence[str] = (
        "testament",
        "book",
        "genre",
        "anomaly_type",
        "evidence_class",
    ),
) -> dict[str, Any]:
    selected = _evaluated_rows(
        decisions, threshold=threshold, allowed_folds=allowed_folds
    )
    overall = precision_metrics(
        sum(row["correct"] is True for row in selected), len(selected)
    )
    strata: dict[str, dict[str, dict[str, Any]]] = {}
    for field in stratum_fields:
        values: dict[str, list[Mapping[str, Any]]] = {}
        for row in selected:
            values.setdefault(str(row.get(field, "unclassified")), []).append(row)
        strata[field] = {
            value: precision_metrics(
                sum(row["correct"] is True for row in rows), len(rows)
            )
            for value, rows in sorted(values.items())
        }
    return {
        "schema_version": 1,
        "calibration_version": CALIBRATION_VERSION,
        "threshold": threshold,
        "folds": sorted(allowed_folds),
        "overall": overall,
        "strata": strata,
        "processed_count": len(decisions),
        "skipped_count": len(decisions) - len(selected),
        "error_count": 0,
    }


def calibrate_auto_class(
    calibration_decisions: Sequence[Mapping[str, Any]],
    validation_decisions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Choose maximum coverage without relaxing the 99.5% precision gate."""

    thresholds = sorted(
        {
            float(row["score"])
            for row in calibration_decisions
            if isinstance(row.get("score"), (int, float))
            and not isinstance(row.get("score"), bool)
        },
        reverse=True,
    )
    passing: list[dict[str, Any]] = []
    for threshold in thresholds:
        report = evaluate_threshold(
            calibration_decisions,
            threshold=threshold,
            allowed_folds=set(CALIBRATION_FOLDS),
        )
        if report["overall"]["auto_enabled"]:
            passing.append(report)
    if not passing:
        return {
            "schema_version": 1,
            "calibration_version": CALIBRATION_VERSION,
            "status": "blocked_no_threshold_meets_precision_gate",
            "minimum_lower_bound": AUTO_LOWER_BOUND,
            "sealed_fold_read": False,
            "processed_count": len(calibration_decisions),
            "skipped_count": len(calibration_decisions),
            "error_count": 0,
        }
    chosen = max(
        passing,
        key=lambda report: (
            report["overall"]["support"],
            report["threshold"],
        ),
    )
    validation = evaluate_threshold(
        validation_decisions,
        threshold=float(chosen["threshold"]),
        allowed_folds={VALIDATION_FOLD},
    )
    status = (
        "calibrated_validation_passed"
        if validation["overall"]["auto_enabled"]
        else "blocked_validation_precision_gate_failed"
    )
    disabled_strata = sorted(
        f"{field}:{value}"
        for field, values in validation["strata"].items()
        for value, metrics in values.items()
        if not metrics["auto_enabled"]
    )
    enabled_strata = sorted(
        f"{field}:{value}"
        for field, values in validation["strata"].items()
        for value, metrics in values.items()
        if metrics["auto_enabled"]
    )
    return {
        "schema_version": 1,
        "calibration_version": CALIBRATION_VERSION,
        "status": status,
        "minimum_lower_bound": AUTO_LOWER_BOUND,
        "threshold": chosen["threshold"],
        "calibration": chosen,
        "validation": validation,
        "disabled_auto_strata": disabled_strata,
        "enabled_auto_strata": enabled_strata,
        "sealed_fold_read": False,
        "coverage_tradeoff_forbidden": True,
        "processed_count": len(calibration_decisions) + len(validation_decisions),
        "skipped_count": chosen["skipped_count"] + validation["skipped_count"],
        "error_count": 0,
    }


def validate_complete_solution(
    edges: Sequence[Mapping[str, Any]],
    *,
    target_ref: str,
    expected_original_ids: set[str],
    expected_target_token_ids: set[str],
    original_ref_by_id: Mapping[str, str],
    target_ref_by_id: Mapping[str, str],
    acceptance_class: str,
    calibration: Mapping[str, Any] | None = None,
    overrides_by_id: Mapping[str, Mapping[str, Any]] | None = None,
    current_input_digests: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate exact final accounting; never infer missing null links."""

    if acceptance_class not in {"A_auto", "B_review"}:
        raise ValueError("C_unresolved cannot be accepted as a final solution")
    seen_originals: set[str] = set()
    seen_targets: set[str] = set()
    for edge in edges:
        validate_hyperedge(
            edge,
            valid_original_ids=expected_original_ids,
            valid_target_token_ids=expected_target_token_ids,
            original_ref_by_id=original_ref_by_id,
            target_ref_by_id=target_ref_by_id,
        )
        originals = set(str(value) for value in edge.get("original_token_ids", ()))
        targets = set(str(value) for value in edge.get("target_token_ids", ()))
        if originals & seen_originals or targets & seen_targets:
            raise ValueError("Final hypergraph solution contains overlapping edges")
        seen_originals.update(originals)
        seen_targets.update(targets)
        if edge.get("target_ref") != target_ref:
            raise ValueError("Final solution crosses a verse boundary")

    if seen_originals != expected_original_ids:
        raise ValueError("Final solution does not exactly account for original tokens")
    if seen_targets != expected_target_token_ids:
        raise ValueError("Final solution does not exactly account for Ukrainian tokens")

    if acceptance_class == "A_auto":
        if (
            calibration is None
            or calibration.get("status") != "calibrated_validation_passed"
            or calibration.get("validation", {})
            .get("overall", {})
            .get("one_sided_wilson_lower_bound", 0.0)
            < AUTO_LOWER_BOUND
        ):
            raise ValueError("A_auto lacks a passing frozen-gold calibration")
        if any(edge.get("auto_eligible") is not True for edge in edges):
            raise ValueError("A_auto solution contains a non-eligible edge")
        disabled_strata = set(calibration.get("disabled_auto_strata", ()))
        enabled_strata_value = calibration.get("enabled_auto_strata")
        if not isinstance(enabled_strata_value, list) or not enabled_strata_value:
            raise ValueError("A_auto calibration lacks explicit enabled strata")
        enabled_strata = set(str(value) for value in enabled_strata_value)
        for edge in edges:
            missing = [field for field in AUTO_STRATUM_FIELDS if not edge.get(field)]
            if missing:
                raise ValueError(
                    "A_auto edge lacks explicit calibration strata: "
                    + ", ".join(missing)
                )
            edge_strata = {
                f"{field}:{edge[field]}" for field in AUTO_STRATUM_FIELDS
            }
            blocked = sorted(edge_strata & disabled_strata)
            if blocked:
                raise ValueError(
                    "A_auto edge belongs to a disabled or underpowered stratum: "
                    + ", ".join(blocked)
                )
            unvalidated = sorted(edge_strata - enabled_strata)
            if unvalidated:
                raise ValueError(
                    "A_auto edge belongs to an unvalidated stratum: "
                    + ", ".join(unvalidated)
                )
    else:
        overrides = overrides_by_id or {}
        current = current_input_digests or {}
        for edge in edges:
            override_id = edge.get("manual_override_id")
            override = overrides.get(str(override_id))
            if override is None or not override_is_current(override, current):
                raise ValueError("B_review edge lacks a current manual override")

    return {
        "schema_version": 1,
        "resolver_version": ALIGNMENT_RESOLVER_VERSION,
        "target_ref": target_ref,
        "acceptance_class": acceptance_class,
        "edge_count": len(edges),
        "original_accounted": len(seen_originals),
        "target_accounted": len(seen_targets),
        "invalid_or_dangling": 0,
        "cross_verse": 0,
        "status": "complete_exact_accounting",
        "processed_count": len(edges),
        "skipped_count": 0,
        "error_count": 0,
    }

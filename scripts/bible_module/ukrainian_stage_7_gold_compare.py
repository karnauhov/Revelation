"""Deterministically compare two completed stage-7 blind gold reviews.

The comparison is intentionally post-review: it accepts only completed files
with valid digest sidecars, requires different reviewers for every stable ID,
and exposes substantive link/null disagreements for a separate adjudicator.
Different ``severity``/``phenomena`` metadata is counted separately and never
manufactures a false alignment disagreement.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold import (
    EXPECTED_STAGE6_COMMENT_SHA256,
    EXPECTED_STAGE6_TEXT_SHA256,
    GOLD_WORKFLOW_VERSION,
    _alignment_for_key,
    _evidence_ok,
    _merge_agreed_review_metadata,
    _read_json,
    _read_jsonl,
    _semantic_for_key,
    _sha256_file,
    _validate_final_grid,
    _validate_semantic_accounting,
    _write_json,
    _write_jsonl,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    sha256_text,
    stable_json,
)


COMPARISON_VERSION = "ukrainian-stage-7-gold-comparison-v1"
ADJUDICATION_SHARD_VERSION = "ukrainian-stage-7-adjudication-shard-v1"
CONSENSUS_CORRECTION_VERSION = "ukrainian-stage-7-consensus-correction-v1"
POST_CONSENSUS_QC_VERSION = (
    "ukrainian-stage-7-post-consensus-correction-content-qc-v1"
)
ADJUDICATION_QC_VERSION = "ukrainian-stage-7-adjudication-independent-qc-v1"
ALLOWED_INPUT_STATUSES = {
    "complete_compact_shard_expansion_ready_for_merge",
    "complete_shard_merge_ready_for_pass_ingestion",
    "complete_blind_review_pass",
}


def _key(row: Mapping[str, Any]) -> str:
    if row.get("record_type") == "original_decision":
        return "original:" + str(row.get("decision_id", ""))
    if row.get("record_type") == "target_accounting":
        return "target:" + str(row.get("accounting_id", ""))
    raise ValueError("Review contains an unknown decision record type")


def _validated_review(
    path: Path, *, expected_pass: int
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    sidecar_path = Path(str(path) + ".manifest.json")
    if not sidecar_path.is_file():
        raise ValueError("Completed review lacks its digest sidecar")
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("status") not in ALLOWED_INPUT_STATUSES
        or sidecar.get("output_sha256", {}).get(path.name) != _sha256_file(path)
    ):
        raise ValueError("Completed review differs from its digest sidecar")
    rows = list(_read_jsonl(path))
    metadata_rows = [
        row for row in rows if row.get("record_type") == "review_metadata"
    ]
    if len(metadata_rows) != 1:
        raise ValueError("Completed review requires exactly one metadata row")
    metadata = metadata_rows[0]
    if metadata.get("review_pass") != expected_pass:
        raise ValueError("Completed review pass number is invalid")
    values: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("record_type") == "review_metadata":
            continue
        stable_key = _key(row)
        if stable_key in values:
            raise ValueError("Completed review contains a duplicate stable ID")
        values[stable_key] = dict(row)
    return metadata, values


def compare_review_files(
    *, pass1_path: Path, pass2_path: Path, output_path: Path
) -> dict[str, Any]:
    """Write a post-blind comparison without resolving any disagreement."""

    metadata1, pass1 = _validated_review(pass1_path, expected_pass=1)
    metadata2, pass2 = _validated_review(pass2_path, expected_pass=2)
    if metadata1.get("input_sha256") != metadata2.get("input_sha256"):
        raise ValueError("Blind reviews are locked to different source inputs")
    if set(pass1) != set(pass2):
        raise ValueError("Blind reviews account for different stable IDs")
    same_reviewers: list[str] = []
    substantive: list[str] = []
    metadata_only: list[str] = []
    for stable_key in sorted(pass1):
        reviewer1 = str(
            pass1[stable_key].get("reviewer_id", metadata1.get("reviewer_id", ""))
        )
        reviewer2 = str(
            pass2[stable_key].get("reviewer_id", metadata2.get("reviewer_id", ""))
        )
        if not reviewer1 or not reviewer2:
            raise ValueError("Blind review decision lacks reviewer identity")
        if reviewer1 == reviewer2:
            same_reviewers.append(stable_key)
        if _alignment_for_key(pass1[stable_key]) != _alignment_for_key(
            pass2[stable_key]
        ):
            substantive.append(stable_key)
        elif _semantic_for_key(pass1[stable_key]) != _semantic_for_key(
            pass2[stable_key]
        ):
            metadata_only.append(stable_key)
    if same_reviewers:
        raise ValueError(
            "Blind comparison requires distinct reviewers: "
            + ", ".join(same_reviewers[:5])
        )

    rows: list[dict[str, Any]] = [
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "comparison_version": COMPARISON_VERSION,
            "record_type": "comparison_metadata",
            "status": (
                "complete_comparison_pending_adjudication"
                if substantive
                else "complete_alignment_agreement"
            ),
            "pass_1_sha256": _sha256_file(pass1_path),
            "pass_2_sha256": _sha256_file(pass2_path),
            "blind_review_independence_verified": True,
        }
    ]
    for stable_key in substantive:
        first = pass1[stable_key]
        second = pass2[stable_key]
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                "comparison_version": COMPARISON_VERSION,
                "record_type": "alignment_disagreement",
                "stable_key": stable_key,
                "target_ref": first["target_ref"],
                "pass_1": {
                    "reviewer_id": first.get(
                        "reviewer_id", metadata1.get("reviewer_id")
                    ),
                    "decision": _semantic_for_key(first),
                    "evidence": first["evidence"],
                    "rationale": first["rationale"],
                },
                "pass_2": {
                    "reviewer_id": second.get(
                        "reviewer_id", metadata2.get("reviewer_id")
                    ),
                    "decision": _semantic_for_key(second),
                    "evidence": second["evidence"],
                    "rationale": second["rationale"],
                },
                "adjudication_status": "unresolved",
            }
        )
    output_count, output_sha = _write_jsonl(output_path, rows)
    by_record_type = Counter(key.split(":", 1)[0] for key in substantive)
    by_book = Counter(str(pass1[key]["target_ref"]).split(".", 1)[0] for key in substantive)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "comparison_version": COMPARISON_VERSION,
        "artifact": "gold_review_pair_comparison",
        "status": rows[0]["status"],
        "serialization": "UTF-8 JSON; sorted keys, compact separators, LF",
        "input_sha256": {
            "review_pass_1": _sha256_file(pass1_path),
            "review_pass_1_manifest": _sha256_file(
                Path(str(pass1_path) + ".manifest.json")
            ),
            "review_pass_2": _sha256_file(pass2_path),
            "review_pass_2_manifest": _sha256_file(
                Path(str(pass2_path) + ".manifest.json")
            ),
        },
        "output_sha256": {output_path.name: output_sha},
        "processed_count": len(pass1),
        "skipped_count": 0,
        "error_count": 0,
        "counts": {
            "stable_decisions": len(pass1),
            "alignment_agreements": len(pass1) - len(substantive),
            "alignment_disagreements": len(substantive),
            "metadata_only_differences": len(metadata_only),
            "comparison_rows": output_count,
        },
        "alignment_disagreements_by_record_type": dict(sorted(by_record_type.items())),
        "alignment_disagreements_by_book": dict(sorted(by_book.items())),
        "acceptance_limits": [
            "This artifact compares two completed independent reviews and accepts no disputed decision.",
            "Every emitted alignment disagreement requires a distinct adjudicator before final gold.",
            "Metadata-only differences are conservatively merged during finalization and do not alter link/null semantics.",
        ],
    }
    _write_json(Path(str(output_path) + ".manifest.json"), manifest)
    return manifest


def validate_adjudication_shard(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
) -> dict[str, Any]:
    """Validate an exact post-comparison adjudication shard fail closed."""

    metadata1, pass1 = _validated_review(pass1_path, expected_pass=1)
    metadata2, pass2 = _validated_review(pass2_path, expected_pass=2)
    if metadata1.get("input_sha256") != metadata2.get("input_sha256"):
        raise ValueError("Blind adjudication inputs differ")
    if set(pass1) != set(pass2):
        raise ValueError("Blind adjudication passes account for different stable IDs")
    same_reviewers = [
        stable_key
        for stable_key in sorted(pass1)
        if str(
            pass1[stable_key].get(
                "reviewer_id", metadata1.get("reviewer_id", "")
            )
        )
        == str(
            pass2[stable_key].get(
                "reviewer_id", metadata2.get("reviewer_id", "")
            )
        )
    ]
    if same_reviewers:
        raise ValueError("Blind adjudication requires distinct reviewers")
    comparison_sidecar_path = Path(str(comparison_path) + ".manifest.json")
    comparison_sidecar = _read_json(comparison_sidecar_path)
    if (
        comparison_sidecar.get("comparison_version") != COMPARISON_VERSION
        or comparison_sidecar.get("input_sha256", {}).get("review_pass_1")
        != _sha256_file(pass1_path)
        or comparison_sidecar.get("input_sha256", {}).get("review_pass_2")
        != _sha256_file(pass2_path)
        or comparison_sidecar.get("input_sha256", {}).get(
            "review_pass_1_manifest"
        )
        != _sha256_file(Path(str(pass1_path) + ".manifest.json"))
        or comparison_sidecar.get("input_sha256", {}).get(
            "review_pass_2_manifest"
        )
        != _sha256_file(Path(str(pass2_path) + ".manifest.json"))
        or comparison_sidecar.get("output_sha256", {}).get(comparison_path.name)
        != _sha256_file(comparison_path)
    ):
        raise ValueError("Comparison differs from the completed blind reviews")
    comparison_rows = list(_read_jsonl(comparison_path))
    comparison_headers = [
        row
        for row in comparison_rows
        if row.get("record_type") == "comparison_metadata"
    ]
    if len(comparison_headers) != 1:
        raise ValueError("Comparison requires exactly one metadata row")
    comparison_header = comparison_headers[0]
    if (
        comparison_header.get("comparison_version") != COMPARISON_VERSION
        or comparison_header.get("pass_1_sha256") != _sha256_file(pass1_path)
        or comparison_header.get("pass_2_sha256") != _sha256_file(pass2_path)
        or comparison_header.get("blind_review_independence_verified") is not True
    ):
        raise ValueError("Comparison metadata or SHA locks differ")
    disagreement_rows = [
        row
        for row in comparison_rows
        if row.get("record_type") == "alignment_disagreement"
    ]
    disagreement_keys = {
        str(row.get("stable_key", ""))
        for row in disagreement_rows
    }
    if len(disagreement_keys) != len(comparison_rows) - 1:
        raise ValueError("Comparison contains duplicate or unknown records")
    expected_disagreements = {
        stable_key
        for stable_key in pass1
        if _alignment_for_key(pass1[stable_key])
        != _alignment_for_key(pass2[stable_key])
    }
    if disagreement_keys != expected_disagreements:
        raise ValueError("Comparison disagreement set is stale or incomplete")
    expected_status = (
        "complete_comparison_pending_adjudication"
        if expected_disagreements
        else "complete_alignment_agreement"
    )
    if comparison_header.get("status") != expected_status:
        raise ValueError("Comparison status differs from its disagreement set")
    for row in disagreement_rows:
        stable_key = str(row["stable_key"])
        first = pass1[stable_key]
        second = pass2[stable_key]
        reviewer1 = str(
            first.get("reviewer_id", metadata1.get("reviewer_id", ""))
        )
        reviewer2 = str(
            second.get("reviewer_id", metadata2.get("reviewer_id", ""))
        )
        if (
            row.get("target_ref") != first.get("target_ref")
            or row.get("pass_1", {}).get("reviewer_id") != reviewer1
            or row.get("pass_2", {}).get("reviewer_id") != reviewer2
            or row.get("pass_1", {}).get("decision")
            != _semantic_for_key(first)
            or row.get("pass_2", {}).get("decision")
            != _semantic_for_key(second)
            or row.get("adjudication_status") != "unresolved"
        ):
            raise ValueError("Comparison disagreement payload differs from blind reviews")

    rows = list(_read_jsonl(adjudication_path))
    headers = [
        row
        for row in rows
        if row.get("record_type") == "adjudication_shard_metadata"
    ]
    if len(headers) != 1:
        raise ValueError("Adjudication shard requires exactly one metadata row")
    header = headers[0]
    adjudicator = header.get("adjudicator_id")
    reviewer_ids = {
        str(row.get("reviewer_id", metadata1.get("reviewer_id", "")))
        for row in pass1.values()
    } | {
        str(row.get("reviewer_id", metadata2.get("reviewer_id", "")))
        for row in pass2.values()
    }
    if (
        header.get("status") != "complete_manual_adjudication_shard"
        or header.get("comparison_version") != COMPARISON_VERSION
        or not isinstance(adjudicator, str)
        or not adjudicator.strip()
        or adjudicator in reviewer_ids
        or header.get("comparison_sha256") != _sha256_file(comparison_path)
        or header.get("pass_1_sha256") != _sha256_file(pass1_path)
        or header.get("pass_2_sha256") != _sha256_file(pass2_path)
    ):
        raise ValueError("Adjudication metadata, independence or SHA locks differ")

    decisions: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("record_type") == "adjudication_shard_metadata":
            continue
        stable_key = _key(row)
        if stable_key not in disagreement_keys or stable_key in decisions:
            raise ValueError("Adjudication contains an agreed, unknown or duplicate ID")
        if not _evidence_ok(row.get("evidence")) or not str(
            row.get("rationale", "")
        ).strip():
            raise ValueError("Adjudication decision lacks evidence/rationale")
        decisions[stable_key] = dict(row)
    if set(decisions) != disagreement_keys:
        raise ValueError("Adjudication does not resolve every disagreement exactly once")

    final_values: dict[str, Mapping[str, Any]] = {
        stable_key: (
            decisions[stable_key]
            if stable_key in disagreement_keys
            else _merge_agreed_review_metadata(
                pass1[stable_key], pass2[stable_key]
            )
        )
        for stable_key in pass1
    }
    _validate_final_grid(final_values, pass1)
    originals = {
        key.removeprefix("original:"): value
        for key, value in final_values.items()
        if key.startswith("original:")
    }
    targets = {
        key.removeprefix("target:"): value
        for key, value in final_values.items()
        if key.startswith("target:")
    }
    _validate_semantic_accounting(originals, targets)

    if set(final_values) != set(pass1):
        raise ValueError("Adjudication changed the frozen stable-ID grid")
    sidecar_path = Path(str(adjudication_path) + ".manifest.json")
    if not sidecar_path.is_file():
        raise ValueError("Adjudication lacks its required digest sidecar")
    sidecar = _read_json(sidecar_path)
    adjudication_input_values = set(sidecar.get("input_sha256", {}).values())
    if (
        sidecar.get("status") != "complete_manual_adjudication_shard"
        or sidecar.get("output_sha256", {}).get(adjudication_path.name)
        != _sha256_file(adjudication_path)
        or not {
            _sha256_file(pass1_path),
            _sha256_file(pass2_path),
            _sha256_file(comparison_path),
        }
        <= adjudication_input_values
    ):
        raise ValueError("Adjudication differs from its required sidecar")
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "comparison_version": COMPARISON_VERSION,
        "adjudication_shard_version": ADJUDICATION_SHARD_VERSION,
        "status": "valid_complete_manual_adjudication_shard",
        "input_sha256": {
            "review_pass_1": _sha256_file(pass1_path),
            "review_pass_2": _sha256_file(pass2_path),
            "comparison": _sha256_file(comparison_path),
            "adjudication": _sha256_file(adjudication_path),
        },
        "output_sha256": {},
        "processed_count": len(decisions),
        "skipped_count": 0,
        "error_count": 0,
        "counts": {
            "alignment_disagreements": len(disagreement_keys),
            "adjudicated_decisions": len(decisions),
            "stable_decisions_after_overlay": len(final_values),
        },
        "adjudicator_id": adjudicator,
    }


def _validated_post_adjudication_values(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, Mapping[str, Any]],
    str,
]:
    """Return the already validated post-adjudication decision grid."""

    validate_adjudication_shard(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
    )
    metadata1, pass1 = _validated_review(pass1_path, expected_pass=1)
    metadata2, pass2 = _validated_review(pass2_path, expected_pass=2)
    disagreements = {
        stable_key
        for stable_key in pass1
        if _alignment_for_key(pass1[stable_key])
        != _alignment_for_key(pass2[stable_key])
    }
    adjudication_rows = list(_read_jsonl(adjudication_path))
    header = next(
        row
        for row in adjudication_rows
        if row.get("record_type") == "adjudication_shard_metadata"
    )
    decisions = {
        _key(row): dict(row)
        for row in adjudication_rows
        if row.get("record_type") != "adjudication_shard_metadata"
    }
    final_values: dict[str, Mapping[str, Any]] = {
        stable_key: (
            decisions[stable_key]
            if stable_key in disagreements
            else _merge_agreed_review_metadata(
                pass1[stable_key], pass2[stable_key]
            )
        )
        for stable_key in pass1
    }
    return (
        metadata1,
        metadata2,
        pass1,
        pass2,
        final_values,
        str(header["adjudicator_id"]),
    )


def _require_canonical_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    expected = "".join(stable_json(row) + "\n" for row in rows).encode("utf-8")
    if path.read_bytes() != expected:
        raise ValueError("Independent adjudication QC JSONL is not canonical UTF-8/LF")


def _require_canonical_json(path: Path, value: Mapping[str, Any]) -> None:
    expected = (stable_json(value) + "\n").encode("utf-8")
    if path.read_bytes() != expected:
        raise ValueError("Independent adjudication QC sidecar is not canonical UTF-8/LF")


def _qc_reviewer_id(row: Mapping[str, Any]) -> str:
    reviewer = row.get("reviewer_id") or row.get("audit_id")
    return str(reviewer or "").strip()


def _qc_semantics(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    try:
        return _semantic_for_key(value)
    except (KeyError, TypeError, ValueError):
        return None


def _selection_categories(
    final_values: Mapping[str, Mapping[str, Any]],
    pass1: Mapping[str, Mapping[str, Any]],
    pass2: Mapping[str, Mapping[str, Any]],
    *,
    semantic: bool,
) -> dict[str, str]:
    projection = _semantic_for_key if semantic else _alignment_for_key
    return {
        stable_key: (
            "pass_1"
            if projection(final_values[stable_key]) == projection(pass1[stable_key])
            else "pass_2"
            if projection(final_values[stable_key]) == projection(pass2[stable_key])
            else "new"
        )
        for stable_key in final_values
    }


def validate_adjudication_qc(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
    answer_free_template_path: Path,
    answer_free_template_manifest_path: Path,
    qc_path: Path,
    qc_manifest_sha256: str,
) -> dict[str, Any]:
    """Validate a complete independent post-adjudication content QC fail closed."""

    (
        metadata1,
        metadata2,
        pass1,
        pass2,
        final_values,
        adjudicator,
    ) = _validated_post_adjudication_values(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
    )
    adjudication_validation = validate_adjudication_shard(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
    )
    adjudication_rows = list(_read_jsonl(adjudication_path))
    adjudication = {
        _key(row): dict(row)
        for row in adjudication_rows
        if row.get("record_type") != "adjudication_shard_metadata"
    }
    if len(adjudication) != len(adjudication_rows) - 1:
        raise ValueError("Adjudication QC source contains duplicate or unknown records")

    template_manifest = _read_json(answer_free_template_manifest_path)
    if (
        template_manifest.get("status") != "prepared_answer_free_compact_review"
        or template_manifest.get("output_sha256", {}).get(
            answer_free_template_path.name
        )
        != _sha256_file(answer_free_template_path)
    ):
        raise ValueError("Answer-free QC template differs from its digest sidecar")
    template_rows = list(_read_jsonl(answer_free_template_path))
    templates: dict[str, dict[str, Any]] = {}
    template_original_count = 0
    template_target_count = 0
    for row in template_rows:
        target_ref = str(row.get("target_ref", ""))
        text = row.get("plain_text_nfc")
        comment = row.get("target_comment")
        if (
            not target_ref
            or target_ref in templates
            or not isinstance(text, str)
            or not isinstance(comment, str)
            or not isinstance(row.get("original_index"), list)
            or not isinstance(row.get("target_index"), list)
        ):
            raise ValueError("Answer-free QC template has invalid or duplicate verse data")
        templates[target_ref] = dict(row)
        template_original_count += len(row["original_index"])
        template_target_count += len(row["target_index"])
    if (
        template_manifest.get("processed_count") != len(template_rows)
        or template_original_count + template_target_count != len(final_values)
    ):
        raise ValueError("Answer-free QC template does not cover the final decision grid")
    final_refs = {str(row.get("target_ref", "")) for row in final_values.values()}
    if not final_refs <= set(templates):
        raise ValueError("Answer-free QC template omits a final-grid verse")

    sidecar_candidates = (
        Path(str(qc_path) + ".manifest.json"),
        qc_path.with_suffix(".manifest.json"),
    )
    existing_sidecars = [path for path in sidecar_candidates if path.is_file()]
    if len(existing_sidecars) != 1:
        raise ValueError("Independent adjudication QC lacks its required sidecar")
    sidecar_path = existing_sidecars[0]
    supplied_manifest_sha = str(qc_manifest_sha256).strip().lower()
    if (
        len(supplied_manifest_sha) != 64
        or any(
            character not in "0123456789abcdef"
            for character in supplied_manifest_sha
        )
        or _sha256_file(sidecar_path) != supplied_manifest_sha
    ):
        raise ValueError("Independent adjudication QC sidecar SHA-256 is stale")
    sidecar = _read_json(sidecar_path)
    _require_canonical_json(sidecar_path, sidecar)
    if sidecar.get("output_sha256") != {
        qc_path.name: _sha256_file(qc_path)
    }:
        raise ValueError("Independent adjudication QC differs from its digest sidecar")

    pass1_sidecar = Path(str(pass1_path) + ".manifest.json")
    pass2_sidecar = Path(str(pass2_path) + ".manifest.json")
    comparison_sidecar = Path(str(comparison_path) + ".manifest.json")
    adjudication_sidecar = Path(str(adjudication_path) + ".manifest.json")
    expected_input_sha256 = {
        "review_pass_1": _sha256_file(pass1_path),
        "review_pass_1_manifest": _sha256_file(pass1_sidecar),
        "review_pass_2": _sha256_file(pass2_path),
        "review_pass_2_manifest": _sha256_file(pass2_sidecar),
        "comparison": _sha256_file(comparison_path),
        "comparison_manifest": _sha256_file(comparison_sidecar),
        "adjudication": _sha256_file(adjudication_path),
        "adjudication_manifest": _sha256_file(adjudication_sidecar),
        "answer_free_template": _sha256_file(answer_free_template_path),
        "answer_free_template_manifest": _sha256_file(
            answer_free_template_manifest_path
        ),
    }
    sidecar_inputs = sidecar.get("input_sha256")
    if not isinstance(sidecar_inputs, dict) or any(
        sidecar_inputs.get(name) != digest
        for name, digest in expected_input_sha256.items()
    ):
        raise ValueError("Independent adjudication QC input SHA locks are stale")

    rows = list(_read_jsonl(qc_path))
    _require_canonical_jsonl(qc_path, rows)
    headers = [row for row in rows if row.get("record_type") == "qc_metadata"]
    if len(headers) != 1:
        raise ValueError("Independent adjudication QC requires exactly one metadata row")
    header = headers[0]
    results = [row for row in rows if row.get("record_type") != "qc_metadata"]
    if any(row.get("record_type") != "qc_adjudication_result" for row in results):
        raise ValueError("Independent adjudication QC contains an unknown record type")
    reviewer = _qc_reviewer_id(header)
    sidecar_reviewer = _qc_reviewer_id(sidecar)
    prior_reviewers = {
        str(metadata1.get("reviewer_id", "")),
        str(metadata2.get("reviewer_id", "")),
        adjudicator,
    }
    prior_reviewers.update(
        str(row.get("reviewer_id", "")) for row in pass1.values()
    )
    prior_reviewers.update(
        str(row.get("reviewer_id", "")) for row in pass2.values()
    )
    if (
        not reviewer
        or reviewer != sidecar_reviewer
        or reviewer in prior_reviewers
        or header.get("qc_version") != ADJUDICATION_QC_VERSION
        or header.get("overall_verdict") != "accepted"
        or header.get("shard_blocked") is not False
        or header.get("status") not in (None, "complete_qc_accepted")
        or sidecar.get("qc_version") != ADJUDICATION_QC_VERSION
        or sidecar.get("status") != "complete_qc_accepted"
        or sidecar.get("overall_verdict") != "accepted"
        or sidecar.get("shard_accepted") is not True
    ):
        raise ValueError("Independent adjudication QC status or reviewer independence differs")
    for field, expected in (
        ("schema_version", SCHEMA_VERSION),
        ("contract_version", CONTRACT_VERSION),
        ("gold_workflow_version", GOLD_WORKFLOW_VERSION),
        ("comparison_version", COMPARISON_VERSION),
        ("adjudication_shard_version", ADJUDICATION_SHARD_VERSION),
    ):
        if header.get(field, expected) != expected or sidecar.get(field) != expected:
            raise ValueError("Independent adjudication QC contract version differs")

    result_by_key: dict[str, dict[str, Any]] = {}
    for row in results:
        stable_key = str(row.get("stable_key", ""))
        if stable_key not in adjudication or stable_key in result_by_key:
            raise ValueError("Independent adjudication QC scope has an extra or duplicate ID")
        result_by_key[stable_key] = dict(row)
    if set(result_by_key) != set(adjudication):
        raise ValueError("Independent adjudication QC scope is missing an adjudication ID")

    alignment_selection = _selection_categories(
        adjudication, pass1, pass2, semantic=False
    )
    semantic_selection = _selection_categories(
        adjudication, pass1, pass2, semantic=True
    )
    header_selection_basis = header.get("selection_basis")
    sidecar_selection_basis = sidecar.get("selection_basis")
    if header_selection_basis is None and sidecar_selection_basis is None:
        selection_basis = "alignment"
        legacy_alignment_selection = True
    elif (
        header_selection_basis == sidecar_selection_basis
        and header_selection_basis in {"alignment", "semantic"}
    ):
        selection_basis = str(header_selection_basis)
        legacy_alignment_selection = False
    else:
        raise ValueError("Independent adjudication QC selection basis differs")
    selection = (
        semantic_selection if selection_basis == "semantic" else alignment_selection
    )
    alignment_selection_counts = dict(
        sorted(Counter(alignment_selection.values()).items())
    )
    semantic_selection_counts = dict(
        sorted(Counter(semantic_selection.values()).items())
    )
    if legacy_alignment_selection:
        unexpected_declarations = {
            "alignment_selection_counts",
            "semantic_selection_counts",
        }
        if unexpected_declarations.intersection(header) or (
            isinstance(sidecar.get("counts"), dict)
            and unexpected_declarations.intersection(sidecar["counts"])
        ):
            raise ValueError("Legacy adjudication QC mixes undeclared selection bases")
    elif (
        header.get("alignment_selection_counts") != alignment_selection_counts
        or header.get("semantic_selection_counts") != semantic_selection_counts
    ):
        raise ValueError("Independent adjudication QC selection counts differ")

    for stable_key, adjudicated in adjudication.items():
        row = result_by_key[stable_key]
        target_ref = str(adjudicated.get("target_ref", ""))
        template = templates.get(target_ref)
        evidence_ids = [
            str(item.get("evidence_id", ""))
            for item in adjudicated.get("evidence", [])
        ]
        if (
            template is None
            or row.get("schema_version") != SCHEMA_VERSION
            or row.get("qc_version") != ADJUDICATION_QC_VERSION
            or _qc_reviewer_id(row) != reviewer
            or row.get("verdict") != "accepted"
            or row.get("target_ref") != target_ref
            or row.get("adjudication_record_type") != adjudicated.get("record_type")
            or row.get("adjudication_severity") != adjudicated.get("severity")
            or row.get("selection_category") != selection[stable_key]
            or _qc_semantics(row.get("pass_1_semantics"))
            != _semantic_for_key(pass1[stable_key])
            or _qc_semantics(row.get("pass_2_semantics"))
            != _semantic_for_key(pass2[stable_key])
            or _qc_semantics(row.get("adjudication_semantics"))
            != _semantic_for_key(final_values[stable_key])
            or row.get("adjudication_evidence_ids") != evidence_ids
            or row.get("adjudication_rationale_sha256")
            != sha256_text(str(adjudicated.get("rationale", "")))
            or row.get("oh1988_exact_text") != template["plain_text_nfc"]
            or row.get("oh1988_exact_text_sha256")
            != sha256_text(template["plain_text_nfc"])
            or row.get("target_comment") != template["target_comment"]
            or row.get("target_comment_sha256")
            != sha256_text(template["target_comment"])
            or row.get("comparison_checked") is not True
            or row.get("pass_reviews_checked") is not True
            or row.get("target_comment_checked") is not True
            or not isinstance(row.get("source_evidence"), list)
            or not isinstance(row.get("target_evidence"), list)
            or not str(row.get("rationale", "")).strip()
        ):
            raise ValueError(
                "Independent adjudication QC semantic/evidence/text payload differs: "
                + stable_key
            )
        for optional_check in ("reciprocal_accounting_checked", "full_grid_checked"):
            if optional_check in row and row.get(optional_check) is not True:
                raise ValueError("Independent adjudication QC reciprocal check differs")

    expected_selection = dict(sorted(Counter(selection.values()).items()))
    expected_severity = dict(
        sorted(
            Counter(
                str(row.get("severity")) for row in adjudication.values()
            ).items()
        )
    )
    expected_record_types = dict(
        sorted(
            Counter(
                str(row.get("record_type")) for row in adjudication.values()
            ).items()
        )
    )
    affected_refs = {str(row.get("target_ref", "")) for row in adjudication.values()}
    high_keys = sorted(
        key for key, row in adjudication.items() if row.get("severity") == "high"
    )
    new_keys = sorted(key for key, category in selection.items() if category == "new")
    counts = sidecar.get("counts")
    verdict_counts = counts.get("verdict", {}) if isinstance(counts, dict) else {}
    if (
        not isinstance(counts, dict)
        or counts.get("adjudication_data_rows") != len(adjudication)
        or counts.get("audited_result_rows") != len(adjudication)
        or counts.get("affected_verses") != len(affected_refs)
        or counts.get("high_rows_checked") != len(high_keys)
        or counts.get("new_rows_checked") != len(new_keys)
        or counts.get("qc_jsonl_lines") != len(rows)
        or counts.get("record_type") != expected_record_types
        or counts.get("selection") != expected_selection
        or (
            not legacy_alignment_selection
            and counts.get("alignment_selection_counts")
            != alignment_selection_counts
        )
        or (
            not legacy_alignment_selection
            and counts.get("semantic_selection_counts")
            != semantic_selection_counts
        )
        or counts.get("severity") != expected_severity
        or counts.get("template_original_tokens") != template_original_count
        or counts.get("template_target_tokens") != template_target_count
        or counts.get("full_final_grid", len(final_values)) != len(final_values)
        or not isinstance(verdict_counts, dict)
        or verdict_counts.get("accepted") != len(adjudication)
        or verdict_counts.get("error", 0) != 0
        or verdict_counts.get("uncertain", 0) != 0
        or set(verdict_counts) - {"accepted", "error", "uncertain"}
        or sidecar.get("processed_count") != len(adjudication)
        or sidecar.get("skipped_count") != 0
        or sidecar.get("error_count") != 0
        or sidecar.get("uncertain_count") != 0
        or sidecar.get("error_stable_keys") != []
        or sidecar.get("uncertain_stable_keys") != []
        or sidecar.get("high_stable_keys") != high_keys
        or sidecar.get("new_stable_keys") != new_keys
        or sidecar.get("check_adjudication_result") != adjudication_validation
    ):
        raise ValueError("Independent adjudication QC counts or stable-key sets differ")
    critical_fields = (
        "critical_high_uncertain_stable_keys",
        "critical_high_unresolved_stable_keys",
    )
    if not any(field in sidecar for field in critical_fields) or any(
        sidecar.get(field, []) != [] for field in critical_fields
    ):
        raise ValueError("Independent adjudication QC leaves critical/high uncertainty")
    prohibited = sidecar.get("prohibited_signal_check")
    if not isinstance(prohibited, dict) or any(
        not (
            isinstance(prohibited.get(name), str)
            and (
                prohibited[name] == "not_used"
                or prohibited[name].startswith("not_used;")
            )
        )
        for name in (
            "candidates",
            "frequency_or_majority",
            "legacy",
            "neighbor",
            "position",
            "verse_bag",
        )
    ):
        raise ValueError("Independent adjudication QC used a prohibited signal")

    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "comparison_version": COMPARISON_VERSION,
        "adjudication_shard_version": ADJUDICATION_SHARD_VERSION,
        "qc_version": ADJUDICATION_QC_VERSION,
        "artifact": "gold_review_adjudication_independent_qc",
        "status": "valid_complete_independent_adjudication_qc_accepted",
        "input_sha256": expected_input_sha256,
        "output_sha256": {
            qc_path.name: _sha256_file(qc_path),
            sidecar_path.name: _sha256_file(sidecar_path),
        },
        "processed_count": len(results),
        "skipped_count": 0,
        "error_count": 0,
        "uncertain_count": 0,
        "counts": {
            "adjudication_rows": len(adjudication),
            "full_final_grid": len(final_values),
            "high_rows": len(high_keys),
            "new_rows": len(new_keys),
            "affected_verses": len(affected_refs),
            "alignment_selection_counts": alignment_selection_counts,
            "semantic_selection_counts": semantic_selection_counts,
        },
        "selection_basis": selection_basis,
        "legacy_alignment_selection": legacy_alignment_selection,
        "reviewer_id": reviewer,
    }


def _correction_scope_from_qc(
    qc_manifest: Mapping[str, Any],
    final_values: Mapping[str, Mapping[str, Any]],
) -> tuple[set[str], set[str], set[str]]:
    """Extract the exact correction scope without accepting proposal semantics."""

    proposals = qc_manifest.get("correction_proposals")
    if not isinstance(proposals, list) or not proposals:
        raise ValueError("Blocking QC manifest lacks correction proposals")
    expected: list[str] = []
    affected_refs: set[str] = set()
    revalidate_only: set[str] = set()
    for proposal in proposals:
        if (
            not isinstance(proposal, Mapping)
            or proposal.get("proposal_only_no_mutation_performed") is not True
            or proposal.get("required_workflow")
            != "separate_fail_closed_consensus_correction"
        ):
            raise ValueError("Blocking QC correction proposal contract is invalid")
        target_ref = proposal.get("target_ref")
        row_keys = proposal.get("rows_requiring_semantic_change")
        revalidate_keys = proposal.get("verse_local_rows_to_revalidate")
        unchanged_key = proposal.get("unchanged_reciprocal_row_to_revalidate")
        if (
            not isinstance(target_ref, str)
            or not target_ref
            or not isinstance(row_keys, list)
            or not row_keys
            or not isinstance(revalidate_keys, list)
            or not set(row_keys) <= set(revalidate_keys)
            or not isinstance(unchanged_key, str)
            or unchanged_key not in revalidate_keys
            or unchanged_key in row_keys
        ):
            raise ValueError("Blocking QC correction scope is incomplete")
        for stable_key in revalidate_keys:
            if (
                stable_key not in final_values
                or final_values[stable_key].get("target_ref") != target_ref
            ):
                raise ValueError("Blocking QC correction scope crosses the verse grid")
        expected.extend(str(value) for value in row_keys)
        revalidate_only.add(unchanged_key)
        affected_refs.add(target_ref)
    if len(expected) != len(set(expected)):
        raise ValueError("Blocking QC correction scope repeats a stable ID")
    expected_keys = set(expected)
    error_keys = set(qc_manifest.get("verdict_stable_keys", {}).get("error", []))
    if not error_keys or not error_keys <= expected_keys:
        raise ValueError("Blocking QC errors are absent from the correction scope")
    return expected_keys, affected_refs, revalidate_only


def validate_consensus_correction_shard(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
    blocking_qc_path: Path,
    correction_path: Path,
    require_sidecar: bool = True,
) -> dict[str, Any]:
    """Validate an independently reviewed post-adjudication correction."""

    (
        metadata1,
        metadata2,
        pass1,
        pass2,
        final_values,
        adjudicator,
    ) = _validated_post_adjudication_values(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
    )
    adjudication_sidecar_path = Path(str(adjudication_path) + ".manifest.json")
    qc_sidecar_path = Path(str(blocking_qc_path) + ".manifest.json")
    if not adjudication_sidecar_path.is_file() or not qc_sidecar_path.is_file():
        raise ValueError("Consensus correction requires adjudication and QC sidecars")
    qc_manifest = _read_json(qc_sidecar_path)
    if (
        qc_manifest.get("status") != "complete_qc_errors_found"
        or qc_manifest.get("overall_verdict") != "error"
        or qc_manifest.get("shard_blocked") is not True
        or qc_manifest.get("output_sha256", {}).get(blocking_qc_path.name)
        != _sha256_file(blocking_qc_path)
    ):
        raise ValueError("Consensus correction lacks a sealed blocking QC verdict")
    source_digests = {
        _sha256_file(pass1_path),
        _sha256_file(Path(str(pass1_path) + ".manifest.json")),
        _sha256_file(pass2_path),
        _sha256_file(Path(str(pass2_path) + ".manifest.json")),
        _sha256_file(comparison_path),
        _sha256_file(Path(str(comparison_path) + ".manifest.json")),
        _sha256_file(adjudication_path),
        _sha256_file(adjudication_sidecar_path),
    }
    if not source_digests <= set(qc_manifest.get("input_sha256", {}).values()):
        raise ValueError("Blocking QC is stale for the adjudicated review inputs")
    qc_rows = list(_read_jsonl(blocking_qc_path))
    qc_headers = [row for row in qc_rows if row.get("record_type") == "qc_metadata"]
    if len(qc_headers) != 1:
        raise ValueError("Blocking QC requires exactly one metadata row")
    qc_header = qc_headers[0]
    qc_error_keys = {
        str(row.get("stable_key", ""))
        for row in qc_rows
        if row.get("record_type") == "qc_adjudication_result"
        and row.get("verdict") == "error"
    }
    manifest_error_keys = set(
        qc_manifest.get("verdict_stable_keys", {}).get("error", [])
    )
    if (
        qc_header.get("status") != "complete_qc_errors_found"
        or qc_header.get("overall_verdict") != "error"
        or qc_header.get("shard_blocked") is not True
        or qc_header.get("reviewer_id") != qc_manifest.get("reviewer_id")
        or qc_header.get("input_sha256") != qc_manifest.get("input_sha256")
        or qc_error_keys != manifest_error_keys
    ):
        raise ValueError("Blocking QC payload and manifest disagree")
    expected_keys, affected_refs, revalidate_only = _correction_scope_from_qc(
        qc_manifest, final_values
    )

    rows = list(_read_jsonl(correction_path))
    headers = [
        row
        for row in rows
        if row.get("record_type") == "consensus_correction_metadata"
    ]
    if len(headers) != 1:
        raise ValueError("Consensus correction requires exactly one metadata row")
    header = headers[0]
    correction_reviewer = header.get("correction_reviewer_id")
    qc_reviewer = qc_manifest.get("reviewer_id")
    prior_reviewers = {
        str(row.get("reviewer_id", metadata1.get("reviewer_id", "")))
        for row in pass1.values()
    } | {
        str(row.get("reviewer_id", metadata2.get("reviewer_id", "")))
        for row in pass2.values()
    }
    prior_reviewers.update({adjudicator, str(qc_reviewer or "")})
    expected_locks = {
        "pass_1_sha256": _sha256_file(pass1_path),
        "pass_1_manifest_sha256": _sha256_file(
            Path(str(pass1_path) + ".manifest.json")
        ),
        "pass_2_sha256": _sha256_file(pass2_path),
        "pass_2_manifest_sha256": _sha256_file(
            Path(str(pass2_path) + ".manifest.json")
        ),
        "comparison_sha256": _sha256_file(comparison_path),
        "comparison_manifest_sha256": _sha256_file(
            Path(str(comparison_path) + ".manifest.json")
        ),
        "adjudication_sha256": _sha256_file(adjudication_path),
        "adjudication_manifest_sha256": _sha256_file(adjudication_sidecar_path),
        "blocking_qc_sha256": _sha256_file(blocking_qc_path),
        "blocking_qc_manifest_sha256": _sha256_file(qc_sidecar_path),
    }
    sorted_expected_keys = sorted(expected_keys)
    expected_keys_sha256 = sha256_text(stable_json(sorted_expected_keys))
    if (
        header.get("status")
        != "complete_manual_consensus_correction_pending_independent_qc"
        or header.get("correction_version") != CONSENSUS_CORRECTION_VERSION
        or header.get("comparison_version") != COMPARISON_VERSION
        or header.get("contract_version") != CONTRACT_VERSION
        or header.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or not isinstance(correction_reviewer, str)
        or not correction_reviewer.strip()
        or correction_reviewer in prior_reviewers
        or header.get("expected_changed_stable_keys") != sorted_expected_keys
        or header.get("expected_changed_stable_keys_sha256")
        != expected_keys_sha256
        or any(header.get(key) != value for key, value in expected_locks.items())
    ):
        raise ValueError("Consensus correction metadata, independence or SHA locks differ")

    decisions: dict[str, dict[str, Any]] = {}
    decision_order: list[str] = []
    for row in rows:
        if row.get("record_type") == "consensus_correction_metadata":
            continue
        stable_key = _key(row)
        if stable_key not in expected_keys or stable_key in decisions:
            raise ValueError("Consensus correction contains an unscoped or duplicate ID")
        if (
            row.get("schema_version") != SCHEMA_VERSION
            or row.get("contract_version") != CONTRACT_VERSION
            or row.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
            or row.get("reviewer_id") != correction_reviewer
            or not _evidence_ok(row.get("evidence"))
            or not str(row.get("rationale", "")).strip()
        ):
            raise ValueError("Consensus correction decision contract is invalid")
        expected_supersedes = sha256_text(
            stable_json(_alignment_for_key(final_values[stable_key]))
        )
        if row.get("supersedes_alignment_sha256") != expected_supersedes:
            raise ValueError("Consensus correction before-semantics lock differs")
        if _alignment_for_key(row) == _alignment_for_key(final_values[stable_key]):
            raise ValueError("Consensus correction row does not change its base decision")
        decisions[stable_key] = dict(row)
        decision_order.append(stable_key)
    if set(decisions) != expected_keys:
        raise ValueError("Consensus correction does not match the exact QC scope")
    if decision_order != sorted(decision_order):
        raise ValueError("Consensus correction rows are not in stable order")

    corrected_values = dict(final_values)
    corrected_values.update(decisions)
    _validate_final_grid(corrected_values, pass1)
    originals = {
        key.removeprefix("original:"): value
        for key, value in corrected_values.items()
        if key.startswith("original:")
    }
    targets = {
        key.removeprefix("target:"): value
        for key, value in corrected_values.items()
        if key.startswith("target:")
    }
    _validate_semantic_accounting(originals, targets)

    input_sha256 = {
        "review_pass_1": _sha256_file(pass1_path),
        "review_pass_1_manifest": _sha256_file(
            Path(str(pass1_path) + ".manifest.json")
        ),
        "review_pass_2": _sha256_file(pass2_path),
        "review_pass_2_manifest": _sha256_file(
            Path(str(pass2_path) + ".manifest.json")
        ),
        "comparison": _sha256_file(comparison_path),
        "comparison_manifest": _sha256_file(
            Path(str(comparison_path) + ".manifest.json")
        ),
        "adjudication": _sha256_file(adjudication_path),
        "adjudication_manifest": _sha256_file(adjudication_sidecar_path),
        "blocking_qc": _sha256_file(blocking_qc_path),
        "blocking_qc_manifest": _sha256_file(qc_sidecar_path),
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "comparison_version": COMPARISON_VERSION,
        "correction_version": CONSENSUS_CORRECTION_VERSION,
        "artifact": "gold_review_consensus_correction_shard",
        "status": (
            "valid_complete_manual_consensus_correction_pending_independent_qc"
        ),
        "serialization": "UTF-8 JSON; sorted keys, compact separators, LF",
        "input_sha256": input_sha256,
        "output_sha256": {correction_path.name: _sha256_file(correction_path)},
        "processed_count": len(decisions),
        "skipped_count": 0,
        "error_count": 0,
        "counts": {
            "correction_proposals": len(
                qc_manifest.get("correction_proposals", [])
            ),
            "corrected_original_decisions": sum(
                key.startswith("original:") for key in decisions
            ),
            "corrected_target_accounting": sum(
                key.startswith("target:") for key in decisions
            ),
            "affected_verses": len(affected_refs),
            "revalidated_unchanged_target_accounting": len(revalidate_only),
            "stable_decisions_after_correction": len(corrected_values),
        },
        "correction_reviewer_id": correction_reviewer,
    }
    if require_sidecar:
        sidecar_path = Path(str(correction_path) + ".manifest.json")
        if not sidecar_path.is_file():
            raise ValueError("Consensus correction lacks its digest sidecar")
        sidecar = _read_json(sidecar_path)
        if (
            sidecar.get("status")
            != "complete_manual_consensus_correction_pending_independent_qc"
            or sidecar.get("input_sha256") != input_sha256
            or sidecar.get("output_sha256") != result["output_sha256"]
            or sidecar.get("counts") != result["counts"]
            or sidecar.get("correction_reviewer_id") != correction_reviewer
            or sidecar.get("processed_count") != len(decisions)
            or sidecar.get("error_count") != 0
        ):
            raise ValueError("Consensus correction differs from its digest sidecar")
    return result


def seal_consensus_correction_shard(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
    blocking_qc_path: Path,
    correction_path: Path,
) -> dict[str, Any]:
    """Validate and write the deterministic correction digest sidecar."""

    result = validate_consensus_correction_shard(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
        blocking_qc_path=blocking_qc_path,
        correction_path=correction_path,
        require_sidecar=False,
    )
    sidecar = dict(result)
    sidecar["status"] = (
        "complete_manual_consensus_correction_pending_independent_qc"
    )
    sidecar_path = Path(str(correction_path) + ".manifest.json")
    if sidecar_path.is_file() and _read_json(sidecar_path) != sidecar:
        raise ValueError("Consensus correction sidecar already exists and differs")
    _write_json(sidecar_path, sidecar)
    return validate_consensus_correction_shard(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
        blocking_qc_path=blocking_qc_path,
        correction_path=correction_path,
    )


def validate_post_consensus_correction_qc(
    *,
    pass1_path: Path,
    pass2_path: Path,
    comparison_path: Path,
    adjudication_path: Path,
    blocking_qc_path: Path,
    correction_path: Path,
    final_qc_path: Path,
) -> dict[str, Any]:
    """Validate exact independent QC of an accepted consensus correction."""

    correction_result = validate_consensus_correction_shard(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
        blocking_qc_path=blocking_qc_path,
        correction_path=correction_path,
    )
    (
        metadata1,
        metadata2,
        pass1,
        pass2,
        final_values,
        adjudicator,
    ) = _validated_post_adjudication_values(
        pass1_path=pass1_path,
        pass2_path=pass2_path,
        comparison_path=comparison_path,
        adjudication_path=adjudication_path,
    )
    correction_rows = list(_read_jsonl(correction_path))
    correction_header = correction_rows[0]
    corrections = {
        _key(row): dict(row)
        for row in correction_rows
        if row.get("record_type") != "consensus_correction_metadata"
    }
    corrected_values = dict(final_values)
    corrected_values.update(corrections)
    _validate_final_grid(corrected_values, pass1)
    _validate_semantic_accounting(
        {
            key.removeprefix("original:"): value
            for key, value in corrected_values.items()
            if key.startswith("original:")
        },
        {
            key.removeprefix("target:"): value
            for key, value in corrected_values.items()
            if key.startswith("target:")
        },
    )

    adjudication_rows = list(_read_jsonl(adjudication_path))
    adjudication_keys_in_order = [
        _key(row)
        for row in adjudication_rows
        if row.get("record_type") != "adjudication_shard_metadata"
    ]
    correction_keys_in_order = [
        _key(row)
        for row in correction_rows
        if row.get("record_type") != "consensus_correction_metadata"
    ]
    blocking_qc_manifest = _read_json(
        Path(str(blocking_qc_path) + ".manifest.json")
    )
    _, _, revalidate_only = _correction_scope_from_qc(
        blocking_qc_manifest, final_values
    )
    revalidate_keys_in_order = sorted(revalidate_only)
    expected_by_record_type = {
        "qc_final_adjudication_result": adjudication_keys_in_order,
        "qc_final_consensus_correction_result": correction_keys_in_order,
        "qc_final_revalidate_only_result": revalidate_keys_in_order,
    }
    expected_unique_keys = set().union(
        *(set(keys) for keys in expected_by_record_type.values())
    )

    sidecar_path = Path(str(final_qc_path) + ".manifest.json")
    if not sidecar_path.is_file():
        raise ValueError("Post-consensus QC lacks its required digest sidecar")
    sidecar = _read_json(sidecar_path)
    rows = list(_read_jsonl(final_qc_path))
    headers = [row for row in rows if row.get("record_type") == "qc_metadata"]
    if len(headers) != 1:
        raise ValueError("Post-consensus QC requires exactly one metadata row")
    header = headers[0]
    observations = [row for row in rows if row.get("record_type") != "qc_metadata"]
    if len(observations) != len(rows) - 1:
        raise ValueError("Post-consensus QC contains an unknown metadata row")

    correction_reviewer = str(correction_header["correction_reviewer_id"])
    reviewer = header.get("reviewer_id")
    prior_reviewers = {
        str(row.get("reviewer_id", metadata1.get("reviewer_id", "")))
        for row in pass1.values()
    } | {
        str(row.get("reviewer_id", metadata2.get("reviewer_id", "")))
        for row in pass2.values()
    }
    prior_reviewers.update(
        {
            adjudicator,
            str(blocking_qc_manifest.get("reviewer_id", "")),
            correction_reviewer,
        }
    )
    if (
        not isinstance(reviewer, str)
        or not reviewer.strip()
        or reviewer in prior_reviewers
    ):
        raise ValueError("Post-consensus QC reviewer independence is invalid")

    source_locks = metadata1.get("input_sha256", {})
    if source_locks != metadata2.get("input_sha256", {}):
        raise ValueError("Post-consensus QC blind source locks differ")
    expected_input_sha256 = {
        "review_pass_1": _sha256_file(pass1_path),
        "review_pass_1_manifest": _sha256_file(
            Path(str(pass1_path) + ".manifest.json")
        ),
        "review_pass_2": _sha256_file(pass2_path),
        "review_pass_2_manifest": _sha256_file(
            Path(str(pass2_path) + ".manifest.json")
        ),
        "comparison": _sha256_file(comparison_path),
        "comparison_manifest": _sha256_file(
            Path(str(comparison_path) + ".manifest.json")
        ),
        "adjudication": _sha256_file(adjudication_path),
        "adjudication_manifest": _sha256_file(
            Path(str(adjudication_path) + ".manifest.json")
        ),
        "blocking_qc": _sha256_file(blocking_qc_path),
        "blocking_qc_manifest": _sha256_file(
            Path(str(blocking_qc_path) + ".manifest.json")
        ),
        "consensus_correction": _sha256_file(correction_path),
        "consensus_correction_manifest": _sha256_file(
            Path(str(correction_path) + ".manifest.json")
        ),
        "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
        "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
    }
    optional_source_locks = {
        "ukrainian_token_inventory": source_locks.get(
            "ukrainian_token_inventory"
        ),
        "original_token_universe": source_locks.get("original_token_universe"),
        "answer_free_compact_template": metadata2.get(
            "compact_template_sha256"
        ),
        "answer_free_compact_manifest": metadata2.get(
            "compact_manifest_sha256"
        ),
    }
    expected_input_sha256.update(
        {
            key: value
            for key, value in optional_source_locks.items()
            if value is not None
        }
    )
    if any(not value for value in expected_input_sha256.values()):
        raise ValueError("Post-consensus QC source locks are incomplete")
    if (
        header.get("input_sha256") != expected_input_sha256
        or sidecar.get("input_sha256") != expected_input_sha256
    ):
        raise ValueError("Post-consensus QC input SHA locks differ")

    expected_status = (
        "complete_independent_post_consensus_correction_qc_accepted"
    )
    structural_checks = header.get("structural_checks", {})
    if (
        header.get("schema_version") != SCHEMA_VERSION
        or header.get("contract_version") != CONTRACT_VERSION
        or header.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or header.get("comparison_version") != COMPARISON_VERSION
        or header.get("correction_version") != CONSENSUS_CORRECTION_VERSION
        or header.get("qc_version") != POST_CONSENSUS_QC_VERSION
        or header.get("status") != expected_status
        or header.get("overall_verdict") != "accepted"
        or header.get("shard_blocked") is not False
        or structural_checks.get("full_final_grid_semantic_accounting_valid")
        is not True
        or structural_checks.get("no_cross_verse_or_dangling_links") is not True
    ):
        raise ValueError("Post-consensus QC acceptance metadata is invalid")

    observed_by_record_type: dict[str, list[str]] = {
        key: [] for key in expected_by_record_type
    }
    for row in observations:
        record_type = str(row.get("record_type", ""))
        if record_type not in observed_by_record_type:
            raise ValueError("Post-consensus QC contains an unknown observation")
        stable_key = str(row.get("stable_key", ""))
        if stable_key not in corrected_values:
            raise ValueError("Post-consensus QC contains a dangling stable ID")
        if (
            row.get("schema_version") != SCHEMA_VERSION
            or row.get("contract_version") != CONTRACT_VERSION
            or row.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
            or row.get("comparison_version") != COMPARISON_VERSION
            or row.get("correction_version") != CONSENSUS_CORRECTION_VERSION
            or row.get("qc_version") != POST_CONSENSUS_QC_VERSION
            or row.get("reviewer_id") != reviewer
            or row.get("verdict") != "accepted"
            or row.get("target_ref")
            != corrected_values[stable_key].get("target_ref")
            or row.get("final_semantics")
            != _semantic_for_key(corrected_values[stable_key])
            or (
                record_type == "qc_final_adjudication_result"
                and row.get("correction_applied")
                != (stable_key in corrections)
            )
            or row.get("reciprocal_accounting_checked") is not True
            or not str(row.get("qc_rationale", "")).strip()
        ):
            raise ValueError("Post-consensus QC observation semantics differ")
        observed_by_record_type[record_type].append(stable_key)
    if observed_by_record_type != expected_by_record_type:
        raise ValueError("Post-consensus QC observation scope is incomplete")

    expected_counts = {
        "accepted_observations": len(observations),
        "adjudication_rows_rechecked": len(adjudication_keys_in_order),
        "correction_rows_checked": len(correction_keys_in_order),
        "error_observations": 0,
        "full_final_grid_original_decisions": sum(
            key.startswith("original:") for key in corrected_values
        ),
        "full_final_grid_stable_decisions": len(corrected_values),
        "full_final_grid_target_accounting": sum(
            key.startswith("target:") for key in corrected_values
        ),
        "observation_count": len(observations),
        "qc_jsonl_lines": len(rows),
        "revalidate_only_rows_checked": len(revalidate_keys_in_order),
        "uncertain_observations": 0,
        "unique_original_decisions_checked": sum(
            key.startswith("original:") for key in expected_unique_keys
        ),
        "unique_stable_keys_checked": len(expected_unique_keys),
        "unique_target_accounting_checked": sum(
            key.startswith("target:") for key in expected_unique_keys
        ),
    }
    counts = sidecar.get("counts", {})
    if any(counts.get(key) != value for key, value in expected_counts.items()):
        raise ValueError("Post-consensus QC counts differ from its exact scope")
    if (
        sidecar.get("schema_version") != SCHEMA_VERSION
        or sidecar.get("contract_version") != CONTRACT_VERSION
        or sidecar.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or sidecar.get("comparison_version") != COMPARISON_VERSION
        or sidecar.get("correction_version") != CONSENSUS_CORRECTION_VERSION
        or sidecar.get("qc_version") != POST_CONSENSUS_QC_VERSION
        or sidecar.get("status") != expected_status
        or sidecar.get("overall_verdict") != "accepted"
        or sidecar.get("shard_blocked") is not False
        or sidecar.get("reviewer_id") != reviewer
        or sidecar.get("processed_count") != len(observations)
        or sidecar.get("skipped_count") != 0
        or sidecar.get("error_count") != 0
        or sidecar.get("output_sha256", {}).get(final_qc_path.name)
        != _sha256_file(final_qc_path)
        or sidecar.get("adjudication_stable_keys")
        != sorted(adjudication_keys_in_order)
        or sidecar.get("corrected_stable_keys")
        != sorted(correction_keys_in_order)
        or sidecar.get("revalidated_unchanged_stable_keys")
        != revalidate_keys_in_order
        or sidecar.get("verdict_stable_keys")
        != {
            "accepted": sorted(expected_unique_keys),
            "error": [],
            "uncertain": [],
        }
    ):
        raise ValueError("Post-consensus QC differs from its digest sidecar")
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "comparison_version": COMPARISON_VERSION,
        "correction_version": CONSENSUS_CORRECTION_VERSION,
        "qc_version": POST_CONSENSUS_QC_VERSION,
        "artifact": "gold_review_post_consensus_correction_qc",
        "status": "valid_complete_independent_post_consensus_qc_accepted",
        "input_sha256": expected_input_sha256,
        "output_sha256": {final_qc_path.name: _sha256_file(final_qc_path)},
        "processed_count": len(observations),
        "skipped_count": 0,
        "error_count": 0,
        "counts": expected_counts,
        "reviewer_id": reviewer,
        "correction_status": correction_result["status"],
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--pass1", type=Path, required=True)
    compare.add_argument("--pass2", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check-adjudication")
    check.add_argument("--pass1", type=Path, required=True)
    check.add_argument("--pass2", type=Path, required=True)
    check.add_argument("--comparison", type=Path, required=True)
    check.add_argument("--adjudication", type=Path, required=True)
    adjudication_qc = commands.add_parser("check-adjudication-qc")
    adjudication_qc.add_argument("--pass1", type=Path, required=True)
    adjudication_qc.add_argument("--pass2", type=Path, required=True)
    adjudication_qc.add_argument("--comparison", type=Path, required=True)
    adjudication_qc.add_argument("--adjudication", type=Path, required=True)
    adjudication_qc.add_argument("--template", type=Path, required=True)
    adjudication_qc.add_argument("--template-manifest", type=Path, required=True)
    adjudication_qc.add_argument("--qc", type=Path, required=True)
    adjudication_qc.add_argument("--qc-manifest-sha256", required=True)
    for name in ("seal-correction", "check-correction"):
        correction = commands.add_parser(name)
        correction.add_argument("--pass1", type=Path, required=True)
        correction.add_argument("--pass2", type=Path, required=True)
        correction.add_argument("--comparison", type=Path, required=True)
        correction.add_argument("--adjudication", type=Path, required=True)
        correction.add_argument("--blocking-qc", type=Path, required=True)
        correction.add_argument("--correction", type=Path, required=True)
    final_qc = commands.add_parser("check-correction-qc")
    final_qc.add_argument("--pass1", type=Path, required=True)
    final_qc.add_argument("--pass2", type=Path, required=True)
    final_qc.add_argument("--comparison", type=Path, required=True)
    final_qc.add_argument("--adjudication", type=Path, required=True)
    final_qc.add_argument("--blocking-qc", type=Path, required=True)
    final_qc.add_argument("--correction", type=Path, required=True)
    final_qc.add_argument("--final-qc", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "compare":
        result = compare_review_files(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            output_path=args.output,
        )
    elif args.command == "check-adjudication":
        result = validate_adjudication_shard(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
        )
    elif args.command == "check-adjudication-qc":
        result = validate_adjudication_qc(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
            answer_free_template_path=args.template,
            answer_free_template_manifest_path=args.template_manifest,
            qc_path=args.qc,
            qc_manifest_sha256=args.qc_manifest_sha256,
        )
    elif args.command == "seal-correction":
        result = seal_consensus_correction_shard(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
            blocking_qc_path=args.blocking_qc,
            correction_path=args.correction,
        )
    elif args.command == "check-correction":
        result = validate_consensus_correction_shard(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
            blocking_qc_path=args.blocking_qc,
            correction_path=args.correction,
        )
    else:
        result = validate_post_consensus_correction_qc(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
            blocking_qc_path=args.blocking_qc,
            correction_path=args.correction,
            final_qc_path=args.final_qc,
        )
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

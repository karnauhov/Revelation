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
)


COMPARISON_VERSION = "ukrainian-stage-7-gold-comparison-v1"
ADJUDICATION_SHARD_VERSION = "ukrainian-stage-7-adjudication-shard-v1"
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
    comparison_sidecar_path = Path(str(comparison_path) + ".manifest.json")
    comparison_sidecar = _read_json(comparison_sidecar_path)
    if (
        comparison_sidecar.get("comparison_version") != COMPARISON_VERSION
        or comparison_sidecar.get("input_sha256", {}).get("review_pass_1")
        != _sha256_file(pass1_path)
        or comparison_sidecar.get("input_sha256", {}).get("review_pass_2")
        != _sha256_file(pass2_path)
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
    disagreement_keys = {
        str(row.get("stable_key", ""))
        for row in comparison_rows
        if row.get("record_type") == "alignment_disagreement"
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

    sidecar_path = Path(str(adjudication_path) + ".manifest.json")
    if sidecar_path.is_file():
        sidecar = _read_json(sidecar_path)
        if (
            sidecar.get("status") != "complete_manual_adjudication_shard"
            or sidecar.get("output_sha256", {}).get(adjudication_path.name)
            != _sha256_file(adjudication_path)
        ):
            raise ValueError("Adjudication differs from its supplied sidecar")
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "compare":
        result = compare_review_files(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            output_path=args.output,
        )
    else:
        result = validate_adjudication_shard(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            comparison_path=args.comparison,
            adjudication_path=args.adjudication,
        )
    from scripts.bible_module.ukrainian_stage_7_model import stable_json

    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""Audit a canonicalized external stage-7 blind-review batch.

Full submissions remain in the gitignored work tree.  This command writes only
stable IDs, digests, accounting totals, format-repair counts and quality-risk
metrics to the versioned report directory.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_external_gold import (
    EXTERNAL_FORMAT_CANONICALIZATION_VERSION,
    compact_quality_metrics,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


EXTERNAL_BATCH_AUDIT_VERSION = "ukrainian-stage-7-external-batch-audit-v1"
_PACKAGE_RE = re.compile(r"^uk7ext_gold_(.+)_pass1_(\d{3})$")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact is not an object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for ordinal, line in enumerate(stream, 1):
            if not line.strip():
                raise ValueError(f"Blank JSONL row {ordinal}: {path}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Non-object JSONL row {ordinal}: {path}")
            rows.append(value)
    return rows


def _aggregate_sha256(entries: Iterable[Mapping[str, Any]]) -> str:
    return sha256((stable_json(list(entries)) + "\n").encode("utf-8")).hexdigest()


def _counter_add(target: Counter[str], values: Mapping[str, Any]) -> None:
    for key, value in values.items():
        if not isinstance(value, int):
            raise ValueError(f"Counter value is not integer: {key}")
        target[key] += value


def audit_external_batch(
    *,
    package_root: Path,
    output_path: Path,
    first_ordinal: int,
    last_ordinal: int,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Batch audit output already exists: {output_path}")
    packages: dict[int, tuple[str, Path]] = {}
    for path in package_root.iterdir():
        if not path.is_dir():
            continue
        match = _PACKAGE_RE.fullmatch(path.name)
        if match is None:
            continue
        ordinal = int(match.group(2))
        if first_ordinal <= ordinal <= last_ordinal:
            if ordinal in packages:
                raise ValueError(f"Duplicate external package ordinal: {ordinal}")
            packages[ordinal] = (match.group(1), path)
    expected = list(range(first_ordinal, last_ordinal + 1))
    if sorted(packages) != expected:
        raise ValueError("External package ordinal range is incomplete")

    books: list[dict[str, Any]] = []
    aggregate_counts: Counter[str] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_severities: Counter[str] = Counter()
    aggregate_phenomena: Counter[str] = Counter()
    aggregate_repairs: Counter[str] = Counter()
    aggregate_sha_entries: list[dict[str, Any]] = []
    for ordinal in expected:
        book, package = packages[ordinal]
        suffix = f"{ordinal:03d}"
        task_path = package / "task_manifest.json"
        compact_manifest_path = package / "inputs" / "gold_compact_review.manifest.json"
        canonical_path = (
            package
            / "completed_external"
            / f"review_pass_1.shard_{suffix}.compact.normalized.external-v2.jsonl"
        )
        normalization_path = Path(
            str(canonical_path) + ".normalization.manifest.json"
        )
        expanded_path = (
            package
            / "completed_external"
            / f"review_pass_1.shard_{suffix}.raw.external-v1.canonical-v2.jsonl"
        )
        expanded_manifest_path = Path(str(expanded_path) + ".manifest.json")
        required = (
            task_path,
            compact_manifest_path,
            canonical_path,
            normalization_path,
            expanded_path,
            expanded_manifest_path,
        )
        if any(not path.is_file() for path in required):
            raise ValueError(f"External audited package is incomplete: {package.name}")

        task = _read_json(task_path)
        compact_manifest = _read_json(compact_manifest_path)
        normalization = _read_json(normalization_path)
        expanded_manifest = _read_json(expanded_manifest_path)
        canonical_sha = _sha256_file(canonical_path)
        expanded_sha = _sha256_file(expanded_path)
        if (
            task.get("review_pass") != 1
            or task.get("shard_id") != compact_manifest.get("shard_id")
            or compact_manifest.get("review_pass") != 1
            or compact_manifest.get("error_count") != 0
        ):
            raise ValueError(f"External task/compact identity mismatch: {book}")
        if (
            normalization.get("schema_version") != SCHEMA_VERSION
            or normalization.get("contract_version") != CONTRACT_VERSION
            or normalization.get("normalization_version")
            != EXTERNAL_FORMAT_CANONICALIZATION_VERSION
            or normalization.get("error_count") != 0
            or normalization.get("output_sha256") != {canonical_path.name: canonical_sha}
        ):
            raise ValueError(f"External canonicalization SHA chain differs: {book}")
        if (
            expanded_manifest.get("schema_version") != SCHEMA_VERSION
            or expanded_manifest.get("contract_version") != CONTRACT_VERSION
            or expanded_manifest.get("review_pass") != 1
            or expanded_manifest.get("shard_id") != task.get("shard_id")
            or expanded_manifest.get("error_count") != 0
            or expanded_manifest.get("output_sha256")
            != {expanded_path.name: expanded_sha}
            or expanded_manifest.get("input_sha256", {}).get(
                "manual_compact_submission"
            )
            != canonical_sha
        ):
            raise ValueError(f"Expanded external SHA chain differs: {book}")

        canonical_rows = _read_jsonl(canonical_path)
        expanded_rows = _read_jsonl(expanded_path)
        if any("\ufffd" in stable_json(row) for row in canonical_rows):
            raise ValueError(f"Replacement Unicode character found: {book}")
        quality = compact_quality_metrics(canonical_rows)
        metadata = [
            row for row in expanded_rows if row.get("record_type") == "review_metadata"
        ]
        originals = [
            row for row in expanded_rows if row.get("record_type") == "original_decision"
        ]
        targets = [
            row for row in expanded_rows if row.get("record_type") == "target_accounting"
        ]
        compact_counts = compact_manifest.get("counts", {})
        task_counts = task.get("counts", {})
        if (
            len(metadata) != 1
            or metadata[0].get("blind_to_other_pass") is not True
            or metadata[0].get("reviewer_id") != normalization.get("reviewer_id")
            or len(originals) != compact_counts.get("primary_original_decisions")
            or len(targets) != compact_counts.get("target_token_accounting_decisions")
            or len(originals) != task_counts.get("original_decisions")
            or len(targets) != task_counts.get("target_accounting_decisions")
            or quality["counts"].get("selected_verses", 0)
            != compact_counts.get("selected_verses")
        ):
            raise ValueError(f"External exact accounting differs: {book}")

        original_count = len(originals)
        target_count = len(targets)
        original_omitted = quality["counts"].get("original_omitted", 0)
        target_nulls = quality["counts"].get("target_nulls", 0)
        same_fraction = quality["one_to_one_same_local_index_fraction"]
        warnings: list[str] = []
        if same_fraction >= 0.5:
            warnings.append("elevated_same_local_index_signal_requires_position_bias_review")
        if target_count and target_nulls / target_count >= 0.15:
            warnings.append("elevated_target_null_rate_requires_independent_pass_review")
        if quality["severities"].get("critical", 0):
            warnings.append("critical_decisions_require_independent_double_review")
        repairs = normalization.get("format_repair_counts", {})
        _counter_add(aggregate_counts, quality["counts"])
        aggregate_counts["original_decisions"] += original_count
        aggregate_counts["target_accounting_decisions"] += target_count
        _counter_add(aggregate_relations, quality["relations"])
        _counter_add(aggregate_severities, quality["severities"])
        _counter_add(aggregate_phenomena, quality["phenomena"])
        _counter_add(aggregate_repairs, repairs)
        sha_entry = {
            "ordinal": ordinal,
            "book": book,
            "canonical_compact_sha256": canonical_sha,
            "expanded_raw_sha256": expanded_sha,
        }
        aggregate_sha_entries.append(sha_entry)
        books.append(
            {
                "ordinal": ordinal,
                "book": book,
                "shard_id": task["shard_id"],
                "reviewer_id": metadata[0]["reviewer_id"],
                "status": "merge_ready_pass_1_pending_independent_pass_2_and_adjudication",
                "input_sha256": normalization["input_sha256"],
                "output_sha256": {
                    "canonical_compact": canonical_sha,
                    "expanded_raw": expanded_sha,
                    "expanded_manifest": _sha256_file(expanded_manifest_path),
                    "normalization_manifest": _sha256_file(normalization_path),
                },
                "counts": {
                    "selected_verses": quality["counts"].get("selected_verses", 0),
                    "original_decisions": original_count,
                    "target_accounting_decisions": target_count,
                    "original_omitted": original_omitted,
                    "target_nulls": target_nulls,
                },
                "rates": {
                    "original_omitted_fraction": original_omitted / original_count,
                    "target_null_fraction": target_nulls / target_count,
                    "one_to_one_same_local_index_fraction": same_fraction,
                },
                "relations": quality["relations"],
                "severities": quality["severities"],
                "format_repair_counts": repairs,
                "risk_warnings": warnings,
                "position_only_ground_truth_status": "not_accepted_pending_pass2_comparison",
                "processed_count": original_count + target_count,
                "skipped_count": 0,
                "error_count": 0,
            }
        )

    one_to_one = aggregate_counts["one_to_one"]
    result = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "audit_version": EXTERNAL_BATCH_AUDIT_VERSION,
        "status": "merge_ready_external_pass_1_batch_pending_pass_2_and_adjudication",
        "scope": {"first_ordinal": first_ordinal, "last_ordinal": last_ordinal},
        "books": books,
        "aggregate": {
            "counts": dict(sorted(aggregate_counts.items())),
            "relations": dict(sorted(aggregate_relations.items())),
            "severities": dict(sorted(aggregate_severities.items())),
            "phenomena": dict(sorted(aggregate_phenomena.items())),
            "format_repair_counts": dict(sorted(aggregate_repairs.items())),
            "rates": {
                "original_omitted_fraction": (
                    aggregate_counts["original_omitted"]
                    / aggregate_counts["original_decisions"]
                ),
                "target_null_fraction": (
                    aggregate_counts["target_nulls"]
                    / aggregate_counts["target_accounting_decisions"]
                ),
                "one_to_one_same_local_index_fraction": (
                    aggregate_counts["one_to_one_same_local_index"] / one_to_one
                    if one_to_one
                    else 0.0
                ),
            },
        },
        "audited_output_aggregate_sha256": _aggregate_sha256(aggregate_sha_entries),
        "acceptance_limits": [
            "This batch is accepted only as pass 1, not finalized gold.",
            "Every book still requires an independent blind pass 2 and adjudication.",
            "No local-index, position, frequency or majority signal is accepted as ground truth.",
            "All high/critical decisions require the mandated independent review path.",
        ],
        "serialization": "UTF-8, source codepoints preserved, sorted keys, compact JSON, LF",
        "processed_count": len(books),
        "skipped_count": 0,
        "error_count": 0,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(stable_json(result) + "\n", encoding="utf-8", newline="\n")
    return result


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--first-ordinal", type=int, required=True)
    parser.add_argument("--last-ordinal", type=int, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = audit_external_batch(
        package_root=args.package_root,
        output_path=args.output,
        first_ordinal=args.first_ordinal,
        last_ordinal=args.last_ordinal,
    )
    print(stable_json({"status": result["status"], "processed": result["processed_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

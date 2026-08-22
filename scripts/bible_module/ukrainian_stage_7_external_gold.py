"""Fail-closed normalization for externally returned stage-7 gold wrappers.

Some external ChatGPT reviewers preserve the complete answer-free compact row
and place their answers in ``reviewer_answers`` instead of returning the narrow
submission schema accepted by :mod:`ukrainian_stage_7_gold_compact`.  This
module permits exactly that one mechanical wrapper shape.  It never infers,
repairs, merges, splits, or otherwise changes a reviewer decision.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold import (
    ALLOWED_NULL_REASONS,
    ALLOWED_RELATIONS,
    ALLOWED_SEVERITIES,
    ALLOWED_TARGET_STATUSES,
)
from scripts.bible_module.ukrainian_stage_7_gold_compact import (
    COMPACT_REVIEW_VERSION,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


EXTERNAL_WRAPPER_NORMALIZATION_VERSION = (
    "ukrainian-stage-7-external-wrapper-normalization-v1"
)
EXTERNAL_FORMAT_CANONICALIZATION_VERSION = (
    "ukrainian-stage-7-external-format-canonicalization-v1"
)
_SUBMISSION_FIELDS = (
    "schema_version",
    "contract_version",
    "compact_review_version",
    "record_type",
    "selection_id",
    "target_ref",
    "template_row_sha256",
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl_bytes(path: Path) -> tuple[list[bytes], list[dict[str, Any]]]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    if not raw_lines or any(not line.strip() for line in raw_lines):
        raise ValueError(f"JSONL must be nonempty and contain no blank rows: {path}")
    rows: list[dict[str, Any]] = []
    for ordinal, raw_line in enumerate(raw_lines, 1):
        try:
            value = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid UTF-8 JSONL row {ordinal}: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row {ordinal} is not an object: {path}")
        rows.append(value)
    return raw_lines, rows


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _answer_payload_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = [
        {
            "selection_id": row["selection_id"],
            "groups": row["groups"],
            "target_nulls": row["target_nulls"],
        }
        for row in rows
    ]
    return sha256((stable_json(payload) + "\n").encode("utf-8")).hexdigest()


def compact_quality_metrics(
    submission_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return deterministic, answer-only diagnostics for a compact submission."""

    counters: Counter[str] = Counter()
    relations: Counter[str] = Counter()
    severities: Counter[str] = Counter()
    phenomena: Counter[str] = Counter()
    for row in submission_rows:
        if row.get("record_type") == "compact_review_metadata":
            continue
        groups = row.get("groups")
        target_nulls = row.get("target_nulls")
        if not isinstance(groups, list) or not isinstance(target_nulls, list):
            raise ValueError("Compact quality row lacks group/null lists")
        counters["selected_verses"] += 1
        counters["target_nulls"] += len(target_nulls)
        for group in groups:
            if not isinstance(group, dict):
                raise ValueError("Compact quality group is not an object")
            relation = str(group.get("relation", ""))
            severity = str(group.get("severity", ""))
            relations[relation] += 1
            severities[severity] += 1
            counters["groups"] += 1
            if relation == "original_omitted":
                counters["original_omitted"] += 1
            if relation == "one_to_one":
                originals = group.get("original_indices")
                targets = group.get("target_indices")
                if (
                    isinstance(originals, list)
                    and len(originals) == 1
                    and isinstance(targets, list)
                    and len(targets) == 1
                ):
                    counters["one_to_one"] += 1
                    try:
                        same_index = int(str(originals[0])[1:]) == int(
                            str(targets[0])[1:]
                        )
                    except ValueError as exc:
                        raise ValueError("Compact local index is malformed") from exc
                    counters["one_to_one_same_local_index"] += int(same_index)
            for phenomenon in group.get("phenomena", []):
                phenomena[str(phenomenon)] += 1
        for target_null in target_nulls:
            if not isinstance(target_null, dict):
                raise ValueError("Compact quality target null is not an object")
            severities[str(target_null.get("severity", ""))] += 1
            for phenomenon in target_null.get("phenomena", []):
                phenomena[str(phenomenon)] += 1
    one_to_one = counters["one_to_one"]
    return {
        "counts": dict(sorted(counters.items())),
        "relations": dict(sorted(relations.items())),
        "severities": dict(sorted(severities.items())),
        "phenomena": dict(sorted(phenomena.items())),
        "one_to_one_same_local_index_fraction": (
            counters["one_to_one_same_local_index"] / one_to_one
            if one_to_one
            else 0.0
        ),
    }


def _canonical_relation(
    group: Mapping[str, Any], repairs: Counter[str]
) -> str:
    relation = group.get("relation")
    if relation in ALLOWED_RELATIONS:
        return str(relation)
    if relation not in {"aligned", "direct", "functional_replacement", "link", "linked"}:
        raise ValueError(f"Unsupported external relation alias: {relation!r}")
    originals = group.get("original_indices")
    targets = group.get("target_indices")
    if not isinstance(originals, list) or not isinstance(targets, list):
        raise ValueError("External relation alias lacks index lists")
    cardinality = (len(originals), len(targets))
    if cardinality == (1, 1):
        canonical = "one_to_one"
    elif cardinality[0] == 1 and cardinality[1] >= 2:
        canonical = "one_to_many"
    elif cardinality[0] >= 2 and cardinality[1] == 1:
        canonical = "many_to_one"
    elif cardinality[0] >= 2 and cardinality[1] >= 2:
        canonical = "many_to_many"
    else:
        raise ValueError(f"External relation alias has invalid cardinality: {cardinality}")
    repairs[f"relation:{relation}->{canonical}"] += 1
    return canonical


def _canonical_severity(value: Any, repairs: Counter[str]) -> str:
    if value in ALLOWED_SEVERITIES:
        return str(value)
    mapping = {"low": "normal", "medium": "high"}
    if value not in mapping:
        raise ValueError(f"Unsupported external severity alias: {value!r}")
    canonical = mapping[value]
    repairs[f"severity:{value}->{canonical}"] += 1
    return canonical


def _external_evidence(
    row: Mapping[str, Any],
    *,
    generated_id: str,
    repairs: Counter[str],
) -> list[dict[str, str]]:
    raw = row.get("evidence")
    if raw is None:
        raw = row.get("evidence_ids")
        if raw is not None:
            repairs["evidence_ids_promoted"] += 1
    values: list[Any] = []
    if isinstance(raw, list):
        values.extend(raw)
    elif isinstance(raw, dict):
        for key in sorted(raw):
            nested = raw[key]
            if not isinstance(nested, list):
                raise ValueError("External evidence map values must be lists")
            values.extend(nested)
        repairs["evidence_map_flattened"] += 1
    elif raw is not None:
        raise ValueError("External evidence must be a list or map")

    canonical: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for value in values:
        if isinstance(value, dict) and set(value) == {"kind", "evidence_id"}:
            kind = value.get("kind")
            evidence_id = value.get("evidence_id")
        elif isinstance(value, str):
            kind = "external_blind_review_reference"
            evidence_id = value
            repairs["evidence_string_wrapped"] += 1
        else:
            raise ValueError("External evidence entry cannot be canonicalized")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("External evidence kind is blank")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("External evidence ID is blank")
        pair = (kind, evidence_id)
        if pair not in seen:
            canonical.append({"kind": kind, "evidence_id": evidence_id})
            seen.add(pair)
    if not canonical:
        canonical.append(
            {
                "kind": "external_blind_review_decision",
                "evidence_id": generated_id,
            }
        )
        repairs["evidence_id_generated_from_stable_context"] += 1
    return canonical


def _canonical_group(
    group: Mapping[str, Any],
    *,
    reviewer_id: str,
    selection_id: str,
    ordinal: int,
    repairs: Counter[str],
) -> dict[str, Any]:
    originals = group.get("original_indices")
    targets = group.get("target_indices")
    if not isinstance(originals, list) or not isinstance(targets, list):
        raise ValueError("External group index lists are malformed")
    relation = _canonical_relation(group, repairs)
    null_reason = group.get("null_reason")
    if relation == "original_omitted":
        if null_reason not in ALLOWED_NULL_REASONS:
            null_reason = "translation_omission"
            repairs["missing_original_null_reason->translation_omission"] += 1
    elif null_reason is not None:
        null_reason = None
        repairs["non_null_group_null_reason_cleared"] += 1
    phenomena = group.get("phenomena")
    rationale = group.get("rationale")
    if not isinstance(phenomena, list) or not isinstance(rationale, str):
        raise ValueError("External group lacks phenomena/rationale")
    allowed_fields = {
        "original_indices",
        "target_indices",
        "relation",
        "null_reason",
        "severity",
        "phenomena",
        "evidence",
        "rationale",
    }
    repairs["unsupported_group_fields_dropped"] += len(set(group) - allowed_fields)
    return {
        "original_indices": originals,
        "target_indices": targets,
        "relation": relation,
        "null_reason": null_reason,
        "severity": _canonical_severity(group.get("severity"), repairs),
        "phenomena": phenomena,
        "evidence": _external_evidence(
            group,
            generated_id=(
                f"external:{reviewer_id}:{selection_id}:group:{ordinal:04d}"
            ),
            repairs=repairs,
        ),
        "rationale": rationale,
    }


def _canonical_target_null(
    row: Mapping[str, Any],
    *,
    reviewer_id: str,
    selection_id: str,
    ordinal: int,
    repairs: Counter[str],
) -> dict[str, Any]:
    target_index = row.get("target_index")
    if target_index is None and isinstance(row.get("target_indices"), list):
        indices = row["target_indices"]
        if len(indices) == 1:
            target_index = indices[0]
            repairs["target_indices_singularized"] += 1
    if not isinstance(target_index, str) or not target_index:
        raise ValueError("External target null lacks one target index")
    phenomena = row.get("phenomena")
    rationale = row.get("rationale")
    if not isinstance(phenomena, list) or not isinstance(rationale, str):
        raise ValueError("External target null lacks phenomena/rationale")
    status = row.get("target_status")
    if status not in ALLOWED_TARGET_STATUSES - {"aligned"}:
        if "addition" not in phenomena and row.get("null_reason") != "translation_addition":
            raise ValueError("External target null status cannot be derived safely")
        status = "translation_addition"
        repairs["target_status->translation_addition"] += 1
    allowed_fields = {
        "target_index",
        "target_status",
        "severity",
        "phenomena",
        "evidence",
        "rationale",
    }
    repairs["unsupported_target_null_fields_dropped"] += len(set(row) - allowed_fields)
    return {
        "target_index": target_index,
        "target_status": status,
        "severity": _canonical_severity(row.get("severity"), repairs),
        "phenomena": phenomena,
        "evidence": _external_evidence(
            row,
            generated_id=(
                f"external:{reviewer_id}:{selection_id}:target-null:{ordinal:04d}"
            ),
            repairs=repairs,
        ),
        "rationale": rationale,
    }


def normalize_external_compact_wrapper(
    *,
    template_path: Path,
    metadata_template_path: Path,
    external_path: Path,
    output_path: Path,
    canonicalize_format: bool = False,
) -> dict[str, Any]:
    """Normalize one exact wrapper shape without modifying answer payloads."""

    sidecar_path = Path(str(output_path) + ".normalization.manifest.json")
    if output_path.exists() or sidecar_path.exists():
        raise FileExistsError(
            f"External normalization output already exists; refusing overwrite: {output_path}"
        )

    template_lines, template_rows = _read_jsonl_bytes(template_path)
    metadata_lines, metadata_rows = _read_jsonl_bytes(metadata_template_path)
    external_lines, external_rows = _read_jsonl_bytes(external_path)
    if len(metadata_rows) != 1 or len(metadata_lines) != 1:
        raise ValueError("Metadata template must contain exactly one JSONL row")
    if external_lines[0] != metadata_lines[0]:
        raise ValueError("External wrapper metadata is not byte-exact")
    if len(external_rows) != len(template_rows) + 1:
        raise ValueError("External wrapper does not contain every template row exactly once")

    metadata = metadata_rows[0]
    reviewer_id = metadata.get("reviewer_id")
    shard_id = metadata.get("shard_id")
    if (
        metadata.get("record_type") != "compact_review_metadata"
        or metadata.get("schema_version") != SCHEMA_VERSION
        or metadata.get("contract_version") != CONTRACT_VERSION
        or metadata.get("compact_review_version") != COMPACT_REVIEW_VERSION
        or not isinstance(reviewer_id, str)
        or not reviewer_id.strip()
        or not isinstance(shard_id, str)
        or not shard_id.strip()
    ):
        raise ValueError("External wrapper metadata identity is invalid")

    normalized_rows: list[dict[str, Any]] = [dict(metadata)]
    normalized_answers: list[dict[str, Any]] = []
    repairs: Counter[str] = Counter()
    seen_selection_ids: set[str] = set()
    group_count = 0
    target_null_count = 0
    for ordinal, (template, external) in enumerate(
        zip(template_rows, external_rows[1:], strict=True), 1
    ):
        if template.get("record_type") != "compact_review_verse_template":
            raise ValueError(f"Template row {ordinal} has an invalid record type")
        if template.get("reviewer_answers") != {"groups": [], "target_nulls": []}:
            raise ValueError(f"Template row {ordinal} is not answer-free")
        if set(external) != set(template):
            raise ValueError(f"External wrapper row {ordinal} changed its field set")
        answers = external.get("reviewer_answers")
        if not isinstance(answers, dict) or set(answers) != {"groups", "target_nulls"}:
            raise ValueError(f"External wrapper row {ordinal} has malformed answers")
        groups = answers.get("groups")
        target_nulls = answers.get("target_nulls")
        if not isinstance(groups, list) or not isinstance(target_nulls, list):
            raise ValueError(f"External wrapper row {ordinal} answers are not lists")

        template_context = dict(template)
        template_context.pop("reviewer_answers")
        template_context["record_type"] = "compact_review_verse_submission"
        external_context = dict(external)
        external_context.pop("reviewer_answers")
        if external_context != template_context:
            raise ValueError(f"External wrapper row {ordinal} changed frozen context")

        selection_id = external.get("selection_id")
        if not isinstance(selection_id, str) or selection_id in seen_selection_ids:
            raise ValueError(f"External wrapper row {ordinal} has duplicate/invalid selection ID")
        seen_selection_ids.add(selection_id)
        normalized = {field: external[field] for field in _SUBMISSION_FIELDS}
        normalized["reviewer_id"] = reviewer_id
        if canonicalize_format:
            normalized["groups"] = [
                _canonical_group(
                    group,
                    reviewer_id=reviewer_id,
                    selection_id=selection_id,
                    ordinal=group_ordinal,
                    repairs=repairs,
                )
                for group_ordinal, group in enumerate(groups, 1)
                if isinstance(group, dict)
            ]
            if len(normalized["groups"]) != len(groups):
                raise ValueError(f"External wrapper row {ordinal} has a non-object group")
            normalized["target_nulls"] = [
                _canonical_target_null(
                    target_null,
                    reviewer_id=reviewer_id,
                    selection_id=selection_id,
                    ordinal=null_ordinal,
                    repairs=repairs,
                )
                for null_ordinal, target_null in enumerate(target_nulls, 1)
                if isinstance(target_null, dict)
            ]
            if len(normalized["target_nulls"]) != len(target_nulls):
                raise ValueError(
                    f"External wrapper row {ordinal} has a non-object target null"
                )
        else:
            normalized["groups"] = groups
            normalized["target_nulls"] = target_nulls
        normalized_rows.append(normalized)
        normalized_answers.append(normalized)
        group_count += len(normalized["groups"])
        target_null_count += len(normalized["target_nulls"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_path, normalized_rows)
    answer_sha = _answer_payload_sha256(normalized_answers)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "normalization_version": (
            EXTERNAL_FORMAT_CANONICALIZATION_VERSION
            if canonicalize_format
            else EXTERNAL_WRAPPER_NORMALIZATION_VERSION
        ),
        "status": (
            "canonicalized_external_answer_format_without_changing_link_indices"
            if canonicalize_format
            else "normalized_exact_external_wrapper_without_answer_changes"
        ),
        "review_pass": metadata.get("review_pass"),
        "reviewer_id": reviewer_id,
        "shard_id": shard_id,
        "input_sha256": {
            "compact_template": _sha256_file(template_path),
            "metadata_template": _sha256_file(metadata_template_path),
            "external_wrapper": _sha256_file(external_path),
        },
        "output_sha256": {output_path.name: _sha256_file(output_path)},
        "answer_payload_sha256": answer_sha,
        "counts": {
            "metadata_rows": 1,
            "verse_submission_rows": len(template_rows),
            "groups": group_count,
            "target_nulls": target_null_count,
            "source_context_rows_exact": len(template_rows),
        },
        "normalization_rules": [
            "require_byte_exact_metadata_template",
            "require_exact_template_context_except_record_type",
            (
                "canonicalize_declared_format_aliases_and_preserve_link_indices"
                if canonicalize_format
                else "promote_reviewer_answers_groups_and_target_nulls_verbatim"
            ),
            "inject_reviewer_id_from_exact_metadata",
            "do_not_change_original_or_target_link_indices",
        ],
        "format_repair_counts": dict(sorted(repairs.items())),
        "serialization": "UTF-8, source codepoints preserved, sorted keys, compact JSON, LF",
        "processed_count": len(normalized_rows),
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(sidecar_path, manifest)
    return manifest


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--metadata-template", type=Path, required=True)
    parser.add_argument("--external", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--canonicalize-format",
        action="store_true",
        help="canonicalize known external schema aliases without changing link indices",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = normalize_external_compact_wrapper(
        template_path=args.template,
        metadata_template_path=args.metadata_template,
        external_path=args.external,
        output_path=args.output,
        canonicalize_format=args.canonicalize_format,
    )
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

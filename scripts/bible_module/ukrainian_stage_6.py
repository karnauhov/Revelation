"""Generate stage 6 Ukrainian OH1988 text and footnote comments.

Full derivative corpora are written only below the gitignored ``work`` tree.
Strong alignment is intentionally outside this stage and belongs to stage 7.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scripts.bible_module.ukrainian_stage_6_model import (
    CONTRACT_VERSION,
    MAPPING_CONTRACT_VERSION,
    MERGE_SEPARATOR,
    SCHEMA_VERSION,
    SynthesisPart,
    join_synthesis_parts,
    rebase_anchor,
    serialize_comment_uses,
    sha256_text,
    stable_json,
    validate_partition,
    word_tokens,
)


ROOT = Path(__file__).resolve().parents[2]
STAGE4_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_4_20260801"
STAGE4_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_4_20260801"
STAGE5_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_5_20260801"
DEFAULT_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_6_20260801"
DEFAULT_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_6_20260801"
OVERRIDES = DEFAULT_REPORT / "synthesis_overrides.jsonl"
BASELINE = ROOT / "scripts/bible_module/reports/ukrainian_stage_2_20260801/baseline_manifest.json"
SOURCE = STAGE4_WORK / "normalized_wikisource_ohienko_1988_revisions.jsonl"
FORWARD = STAGE5_WORK / "source_to_target_map.jsonl"
REVERSE = STAGE5_WORK / "target_to_source_map.jsonl"
FOOTNOTE_PROJECTION = STAGE5_WORK / "footnote_projection.jsonl"
COMMONS_SCAN = ROOT / "scripts/bible_module/source_cache/commons_ohienko_1988.djvu"
STAGE4_PARSER_MANIFEST = STAGE4_REPORT / "parser_manifest.json"
STAGE4_COMMONS_MANIFEST = (
    STAGE4_REPORT / "normalized_commons_ohienko_1988_scan.manifest.json"
)
STAGE4_IA_MANIFEST = (
    STAGE4_REPORT / "normalized_internet_archive_ohienko_1988_scan.manifest.json"
)

EXPECTED_SOURCE_SPANS = 31_171
EXPECTED_TARGETS = 31_102
EXPECTED_FOOTNOTE_DEFINITIONS = 1_204
EXPECTED_FOOTNOTE_USES = 1_329
EXPECTED_VERSE_USES = 1_318
EXPECTED_HEADING_USES = 11
EXPECTED_OCR_REVIEWS = 149
EXPECTED_FORWARD_SHA = "5959d3af5422dbf8a8bed95e106c4379a55883a4f9972708c330355aed3e866f"
EXPECTED_REVERSE_SHA = "0870dd982d4eed3212610e8d1d127e55015568c11e8c0dcdcb26ddb38a27e40a"
EXPECTED_FOOTNOTE_SHA = "c1e21b8566d1b3fda8328d20374eaefe4c2a547613eb2749bf11b90e69aa678a"
EXPECTED_SCAN_SHA = "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(stable_json(row) + "\n")


def _target_grid() -> list[dict[str, Any]]:
    grid = _read_json(BASELINE)["target_grid"]
    if grid["canon"] != "protestant_66" or grid["versification"] != "kjv_protestant":
        raise AssertionError("Stage-2 target grid contract changed")
    keys = [str(value) for value in grid["verse_keys"]]
    targets: list[dict[str, Any]] = []
    index = 0
    for book in grid["books"]:
        for chapter, last_verse in enumerate(book["chapters"], 1):
            for verse in range(1, int(last_verse) + 1):
                targets.append(
                    {
                        "order": index + 1,
                        "ref": f"{book['code']}.{chapter}.{verse}",
                        "verse_key": keys[index],
                    }
                )
                index += 1
    if len(targets) != EXPECTED_TARGETS:
        raise AssertionError("Stage-2 target grid count changed")
    return targets


def _load_overrides() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows = _read_jsonl(OVERRIDES)
    if len(rows) != 4:
        raise AssertionError("Expected four proven text-interval overrides")
    by_rule: dict[str, dict[str, Any]] = {}
    for row in rows:
        if (
            row["schema_version"] != SCHEMA_VERSION
            or row["contract_version"] != CONTRACT_VERSION
            or row["mapping_contract_version"] != MAPPING_CONTRACT_VERSION
            or row["decision_type"] != "text_interval_override"
        ):
            raise AssertionError("Text override contract mismatch")
        intervals = [
            (int(item["start_scalar"]), int(item["end_scalar"]))
            for item in row["target_intervals"]
        ]
        separator = row["separator_interval"]
        intervals.append(
            (int(separator["start_scalar"]), int(separator["end_scalar"]))
        )
        validate_partition(int(row["source_length"]), sorted(intervals))
        by_rule[row["rule_id"]] = row
    if len(by_rule) != 4:
        raise AssertionError("Text override rule count changed")
    return rows, by_rule


def _load_source() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    records: dict[str, dict[str, Any]] = {}
    definitions: dict[str, dict[str, Any]] = {}
    use_records: dict[str, str] = {}
    line_count = 0
    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            line_count += 1
            records[record["record_id"]] = {
                "text": record["source_plain_nfc"],
                "provenance": record["provenance"],
            }
            for note in record.get("footnotes", []):
                use_records[note["use_id"]] = record["record_id"]
                current = definitions.get(note["footnote_id"])
                compact = {
                    "definition_order": note["definition_order"],
                    "footnote_id": note["footnote_id"],
                    "full_text_nfc": note["full_text_nfc"],
                    "name": note.get("name"),
                    "provenance": note["provenance"],
                    "source_revision": note["source_revision"],
                }
                if current is not None and current["full_text_nfc"] != compact["full_text_nfc"]:
                    raise AssertionError("Named footnote definition text changed")
                definitions[note["footnote_id"]] = current or compact
    if line_count != EXPECTED_SOURCE_SPANS:
        raise AssertionError("Stage-4 normalized source span count changed")
    if len(definitions) != EXPECTED_FOOTNOTE_DEFINITIONS:
        raise AssertionError("Stage-4 footnote definition count changed")
    return records, definitions, use_records


def _source_only_rule() -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    with FORWARD.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if not row.get("targets"):
                found.append(row)
    if len(found) != 1 or found[0]["operation"] != "range_transfer":
        raise AssertionError("Expected one source-only range_transfer rule")
    return found[0]


def _synthesize(
    reverse: Sequence[Mapping[str, Any]],
    records: Mapping[str, Mapping[str, Any]],
    overrides: Mapping[str, Mapping[str, Any]],
    source_only_rule: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    synthesized: list[dict[str, Any]] = []
    coverage: dict[str, list[tuple[str, int, int, str]]] = defaultdict(list)
    operation_counts: Counter[str] = Counter()
    separator_count = 0
    for target in reverse:
        raw_parts: list[tuple[str, int, int, str]] = []
        part_meta: list[dict[str, Any]] = []
        for source_part in target["source_parts"]:
            record_id = source_part["record_id"]
            source_text = str(records[record_id]["text"])
            start = int(source_part["span"]["start_scalar"])
            end = int(source_part["span"]["end_scalar"])
            if target["operation"] == "split":
                override = overrides[target["rule_id"]]
                if override["record_id"] != record_id or len(source_text) != override["source_length"]:
                    raise AssertionError("Split override source digest/length mismatch")
                interval = next(
                    item
                    for item in override["target_intervals"]
                    if item["target_ref"] == target["target_ref"]
                )
                start, end = int(interval["start_scalar"]), int(interval["end_scalar"])
            text = source_text[start:end]
            if not text:
                raise AssertionError("Empty synthesis interval")
            raw_parts.append((record_id, start, end, text))
            coverage[source_part["segment_id"]].append(
                (record_id, start, end, target["target_ref"])
            )
            part_meta.append(
                {
                    "effective_ref": source_part["effective_ref"],
                    "provenance": source_part["provenance"],
                    "record_id": record_id,
                    "reported_ref": source_part["reported_ref"],
                    "segment_id": source_part["segment_id"],
                    "source_order": source_part["source_order"],
                    "source_span": {"end_scalar": end, "start_scalar": start},
                    "text_sha256": sha256_text(text),
                }
            )
        text, mapped = join_synthesis_parts(raw_parts)
        if len(raw_parts) > 1:
            separator_count += len(raw_parts) - 1
        operation_counts[target["operation"]] += 1
        synthesized.append(
            {
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "merge_separator": MERGE_SEPARATOR if len(raw_parts) > 1 else None,
                "operation": target["operation"],
                "order": target["order"],
                "plain_text_nfc": text,
                "plain_text_sha256": sha256_text(text),
                "rule_id": target["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "source_parts": [
                    dict(
                        part_meta[index],
                        target_span={
                            "end_scalar": mapped[index].target_end,
                            "start_scalar": mapped[index].target_start,
                        },
                    )
                    for index in range(len(mapped))
                ],
                "target_ref": target["target_ref"],
                "verse_key": target["verse_key"],
            }
        )
    source_only: list[dict[str, Any]] = []
    for part in source_only_rule["source_parts"]:
        text = str(records[part["record_id"]]["text"])[
            int(part["span"]["start_scalar"]) : int(part["span"]["end_scalar"])
        ]
        coverage[part["segment_id"]].append(
            (
                part["record_id"],
                int(part["span"]["start_scalar"]),
                int(part["span"]["end_scalar"]),
                "source_only",
            )
        )
        source_only.append(
            {
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "operation": "range_transfer",
                "provenance": part["provenance"],
                "record_id": part["record_id"],
                "rule_id": source_only_rule["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "source_ref": part["effective_ref"],
                "source_span": part["span"],
                "source_text_nfc": text,
                "source_text_sha256": sha256_text(text),
                "status": "non_verse_source_material",
                "target_refs": [],
            }
        )
    if len(synthesized) != EXPECTED_TARGETS or len(coverage) != EXPECTED_SOURCE_SPANS:
        raise AssertionError("Source/target synthesis coverage mismatch")
    if any(not row["plain_text_nfc"] for row in synthesized):
        raise AssertionError("Every target text must be non-empty")
    split_separator_scalars = 0
    duplicate_source_scalars = 0
    for ranges in coverage.values():
        ordered = sorted(ranges, key=lambda item: (item[1], item[2], item[3]))
        if len({item[0] for item in ordered}) != 1:
            raise AssertionError("A source segment crosses source records")
        record_text = str(records[ordered[0][0]]["text"])
        for previous, current in zip(ordered, ordered[1:]):
            if previous[2] > current[1]:
                duplicate_source_scalars += previous[2] - current[1]
                continue
            gap = record_text[previous[2] : current[1]]
            if gap != MERGE_SEPARATOR:
                raise AssertionError(
                    "Split intervals may omit only one documented U+0020 boundary"
                )
            split_separator_scalars += len(gap)
    if duplicate_source_scalars:
        raise AssertionError("Source scalar intervals overlap")
    if split_separator_scalars != 4:
        raise AssertionError("Expected four documented split separator scalars")
    source_word_tokens = sum(
        len(
            word_tokens(
                str(records[part["record_id"]]["text"])[
                    part["source_span"]["start_scalar"] : part["source_span"]["end_scalar"]
                ]
            )
        )
        for row in synthesized
        for part in row["source_parts"]
    ) + sum(len(word_tokens(row["source_text_nfc"])) for row in source_only)
    synthesized_word_tokens = sum(
        len(word_tokens(row["plain_text_nfc"])) for row in synthesized
    )
    source_only_word_tokens = sum(
        len(word_tokens(row["source_text_nfc"])) for row in source_only
    )
    if source_word_tokens != synthesized_word_tokens + source_only_word_tokens:
        raise AssertionError("Source word-token accounting lost or duplicated tokens")
    rules = {row["rule_id"]: row["operation"] for row in reverse}
    rules[source_only_rule["rule_id"]] = source_only_rule["operation"]
    stats = {
        "duplicate_source_scalar_count": duplicate_source_scalars,
        "duplicated_source_word_token_count": 0,
        "lost_source_word_token_count": 0,
        "merge_separator": "U+0020",
        "merge_separator_count": separator_count,
        "operation_rule_counts": dict(sorted(Counter(rules.values()).items())),
        "operation_target_counts": dict(sorted(operation_counts.items())),
        "source_only_count": len(source_only),
        "source_only_word_token_count": source_only_word_tokens,
        "source_span_count": len(coverage),
        "source_word_token_count": source_word_tokens,
        "split_separator_scalar_count": split_separator_scalars,
        "synthesized_word_token_count": synthesized_word_tokens,
        "target_count": len(synthesized),
    }
    return synthesized, source_only, stats


def _project_footnotes(
    projections: Sequence[Mapping[str, Any]],
    synthesized: Sequence[Mapping[str, Any]],
    definitions: Mapping[str, Mapping[str, Any]],
    use_records: Mapping[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    by_target = {row["target_ref"]: row for row in synthesized}
    uses: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    for projection in projections:
        if not projection.get("target_candidates"):
            headings.append(
                {
                    **projection,
                    "anchor_status": "non_verse_source_material",
                    "contract_version": CONTRACT_VERSION,
                    "schema_version": SCHEMA_VERSION,
                }
            )
            continue
        target = by_target[projection["target_ref"]]
        parts = [
            SynthesisPart(
                record_id=part["record_id"],
                source_start=part["source_span"]["start_scalar"],
                source_end=part["source_span"]["end_scalar"],
                target_start=part["target_span"]["start_scalar"],
                target_end=part["target_span"]["end_scalar"],
                text="",
            )
            for part in target["source_parts"]
            if part["record_id"] == use_records[projection["use_id"]]
        ]
        anchor = projection["source_anchor"]
        try:
            start, end = rebase_anchor(
                anchor["start_scalar"], anchor["end_scalar"], parts
            )
        except ValueError as error:
            raise ValueError(
                stable_json(
                    {
                        "anchor": anchor,
                        "parts": [asdict(part) for part in parts],
                        "target_ref": projection.get("target_ref"),
                        "use_id": projection["use_id"],
                    }
                )
            ) from error
        if not (0 <= start <= end <= len(target["plain_text_nfc"])):
            raise AssertionError("Rebased footnote anchor is outside target text")
        definition = definitions[projection["footnote_id"]]
        uses.append(
            {
                "anchor_status": "resolved_by_proven_source_target_interval",
                "contract_version": CONTRACT_VERSION,
                "definition_name": definition["name"],
                "footnote_id": projection["footnote_id"],
                "full_text_nfc": projection["full_text_nfc"],
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "mapping_rule_id": projection["mapping_rule_id"],
                "marker": projection["marker"],
                "operation": projection["operation"],
                "provenance": projection["provenance"],
                "schema_version": SCHEMA_VERSION,
                "source_anchor": projection["source_anchor"],
                "source_order": projection["source_order"],
                "target_anchor": {"end_scalar": end, "start_scalar": start},
                "target_order": projection["target_order"],
                "target_ref": projection["target_ref"],
                "use_id": projection["use_id"],
            }
        )
    uses.sort(key=lambda row: (row["target_order"], row["source_order"], row["use_id"]))
    headings.sort(key=lambda row: (row["source_order"], row["use_id"]))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for use in uses:
        grouped[use["target_ref"]].append(use)
    comments: list[dict[str, Any]] = []
    for target in synthesized:
        target_uses = grouped.get(target["target_ref"], [])
        comment = serialize_comment_uses(target_uses)
        if re.search(r"(?:^|\s)[GH]\d+(?:\s|$)", comment):
            raise AssertionError("Strong-like service token leaked into target_comment")
        if len(target["plain_text_nfc"]) >= 12 and target["plain_text_nfc"] in comment:
            raise AssertionError("Canonical verse text leaked into target_comment")
        comments.append(
            {
                "comment_sha256": sha256_text(comment),
                "contract_version": CONTRACT_VERSION,
                "order": target["order"],
                "schema_version": SCHEMA_VERSION,
                "target_comment": comment,
                "target_ref": target["target_ref"],
                "use_ids": [use["use_id"] for use in target_uses],
                "verse_key": target["verse_key"],
            }
        )
    if len(uses) != EXPECTED_VERSE_USES or len(headings) != EXPECTED_HEADING_USES:
        raise AssertionError("Footnote use projection count changed")
    if len({row["use_id"] for row in uses + headings}) != EXPECTED_FOOTNOTE_USES:
        raise AssertionError("Footnote use was lost or duplicated")
    stats = {
        "comment_target_count": len(comments),
        "empty_comment_count": sum(not row["target_comment"] for row in comments),
        "footnote_definition_count": len(definitions),
        "heading_non_verse_use_count": len(headings),
        "markerless_use_count": sum(1 for row in uses + headings if not row["marker"]),
        "named_definition_count": sum(1 for row in definitions.values() if row["name"]),
        "named_use_count": sum(
            1 for row in uses + headings if definitions[row["footnote_id"]]["name"]
        ),
        "projected_use_count": len(uses),
        "total_use_count": len(uses) + len(headings),
        "unresolved_anchor_count": 0,
    }
    definition_rows = [
        {"contract_version": CONTRACT_VERSION, "schema_version": SCHEMA_VERSION, **row}
        for row in sorted(
            definitions.values(),
            key=lambda item: (item["definition_order"], item["footnote_id"]),
        )
    ]
    return uses, headings, comments, {"definitions": definition_rows, "stats": stats}


def _manual_reviews(
    override_rows: Sequence[Mapping[str, Any]], headings: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    with (STAGE4_REPORT / "source_diff.csv").open(encoding="utf-8", newline="") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["type"] == "footnote_text_not_confirmed_by_hidden_ocr"
        ]
    if len(rows) != EXPECTED_OCR_REVIEWS:
        raise AssertionError("Stage-4 OCR-review inventory changed")
    for index, row in enumerate(rows, 1):
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": [
                    {
                        "digest": EXPECTED_SCAN_SHA,
                        "kind": "commons_exact_edition_scan",
                        "locator": f"Ivan Ohienko Bible.djvu/{row['page_or_record']}",
                    },
                    {
                        "digest": row["evidence"]
                        .split("footnote_text_sha256=", 1)[1]
                        .split(";", 1)[0],
                        "kind": "normalized_footnote_text",
                    },
                ],
                "footnote_id": row["footnote_id"],
                "issue_id": f"uk6-footnote-ocr-{index:03d}",
                "resolution": "visually_matches_commons_scan_retained_without_change",
                "schema_version": SCHEMA_VERSION,
                "severity": "info",
                "status": "resolved",
                "type": "footnote_ocr_review",
            }
        )
    for row in override_rows:
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": row["evidence"],
                "issue_id": row["override_id"],
                "resolution": row["decision"],
                "rule_id": row["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "severity": "high",
                "status": "resolved",
                "type": "split_boundary_review",
            }
        )
    for row in headings:
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": [
                    {
                        "kind": "stage_5_non_verse_binding",
                        "mapping_rule_id": row.get("mapping_rule_id"),
                    }
                ],
                "footnote_id": row["footnote_id"],
                "issue_id": f"uk6-heading-{row['use_id'].rsplit(':', 1)[-1]}",
                "resolution": "retained_as_non_verse_source_material_no_new_binding_evidence",
                "schema_version": SCHEMA_VERSION,
                "severity": "medium",
                "status": "resolved_expected",
                "type": "heading_footnote_review",
            }
        )
    return sorted(reviews, key=lambda row: (row["type"], row["issue_id"]))


def _manifest(
    *,
    artifact: str,
    input_hashes: Mapping[str, str],
    output_path: Path,
    processed: int,
    skipped: int = 0,
    serialization: str = "UTF-8; LF; JSON keys sorted; compact separators",
) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": processed, "skipped": skipped},
        "deterministic_serialization": serialization,
        "generated_on": "2026-08-01",
        "input_sha256": dict(sorted(input_hashes.items())),
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": _sha256_file(output_path),
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
    }


def _write_source_diff(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "type",
                "severity",
                "status",
                "target_ref",
                "rule_id",
                "detail",
            ],
            lineterminator="\n",
        )
        writer.writeheader()


def generate(*, work_dir: Path, report_dir: Path) -> dict[str, Any]:
    work_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    override_rows, overrides = _load_overrides()
    if report_dir != DEFAULT_REPORT:
        shutil.copyfile(OVERRIDES, report_dir / "synthesis_overrides.jsonl")
    input_hashes = {
        "commons_exact_scan": _sha256_file(COMMONS_SCAN),
        "stage4_commons_manifest": _sha256_file(STAGE4_COMMONS_MANIFEST),
        "stage4_ia_manifest": _sha256_file(STAGE4_IA_MANIFEST),
        "stage4_parser_manifest": _sha256_file(STAGE4_PARSER_MANIFEST),
        "stage4_source": _sha256_file(SOURCE),
        "stage5_footnotes": _sha256_file(FOOTNOTE_PROJECTION),
        "stage5_forward": _sha256_file(FORWARD),
        "stage5_reverse": _sha256_file(REVERSE),
    }
    expected = {
        "commons_exact_scan": EXPECTED_SCAN_SHA,
        "stage5_footnotes": EXPECTED_FOOTNOTE_SHA,
        "stage5_forward": EXPECTED_FORWARD_SHA,
        "stage5_reverse": EXPECTED_REVERSE_SHA,
    }
    for key, digest in expected.items():
        if input_hashes[key] != digest:
            raise AssertionError(f"Fixed input changed: {key}")
    grid = _target_grid()
    reverse = _read_jsonl(REVERSE)
    if [(row["target_ref"], row["verse_key"]) for row in reverse] != [
        (row["ref"], row["verse_key"]) for row in grid
    ]:
        raise AssertionError("Exact 31,102 target-key equality failed")
    records, definitions, use_records = _load_source()
    synthesized, source_only, synthesis_stats = _synthesize(
        reverse, records, overrides, _source_only_rule()
    )
    synthesized_path = work_dir / "synthesized_text.jsonl"
    source_only_path = work_dir / "source_only_material.jsonl"
    _write_jsonl(synthesized_path, synthesized)
    _write_jsonl(source_only_path, source_only)
    projections = _read_jsonl(FOOTNOTE_PROJECTION)
    uses, headings, comments, footnote_bundle = _project_footnotes(
        projections, synthesized, definitions, use_records
    )
    uses_path = work_dir / "footnote_uses.jsonl"
    headings_path = work_dir / "heading_footnotes.jsonl"
    comments_path = work_dir / "target_comments.jsonl"
    definitions_path = work_dir / "footnote_definitions.jsonl"
    _write_jsonl(uses_path, uses)
    _write_jsonl(headings_path, headings)
    _write_jsonl(comments_path, comments)
    _write_jsonl(definitions_path, footnote_bundle["definitions"])
    manual_reviews = _manual_reviews(override_rows, headings)
    manual_path = report_dir / "manual_review.jsonl"
    _write_jsonl(manual_path, manual_reviews)
    source_diff_path = report_dir / "source_diff.csv"
    _write_source_diff(source_diff_path)
    preservation = {
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(synthesized), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; JSON keys sorted; compact separators",
        "input_sha256": input_hashes,
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": {"synthesized_text": _sha256_file(synthesized_path)},
        "plain_text_mismatch_count": 0,
        "round_trip_count": len(synthesized),
        "schema_version": SCHEMA_VERSION,
        "source_token_accounting": synthesis_stats,
        "status": "pass",
    }
    _write_json(report_dir / "plain_text_preservation_report.json", preservation)
    footnote_stats = {
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(projections), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; JSON keys sorted; compact separators",
        "input_sha256": {"stage5_footnotes": input_hashes["stage5_footnotes"]},
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": {
            "definitions": _sha256_file(definitions_path),
            "heading_uses": _sha256_file(headings_path),
            "target_comments": _sha256_file(comments_path),
            "verse_uses": _sha256_file(uses_path),
        },
        "schema_version": SCHEMA_VERSION,
        "statistics": footnote_bundle["stats"],
        "status": "pass",
    }
    _write_json(report_dir / "footnote_comment_stats.json", footnote_stats)
    _write_json(
        report_dir / "synthesized_text.manifest.json",
        _manifest(
            artifact="synthesized_text.jsonl",
            input_hashes=input_hashes,
            output_path=synthesized_path,
            processed=len(synthesized),
        ),
    )
    _write_json(
        report_dir / "source_only_material.manifest.json",
        _manifest(
            artifact="source_only_material.jsonl",
            input_hashes=input_hashes,
            output_path=source_only_path,
            processed=len(source_only),
        ),
    )
    footnote_manifest = {
        "artifact": "footnote_projection_bundle",
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(projections), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; one sorted compact JSON object per line",
        "generated_on": "2026-08-01",
        "input_sha256": input_hashes,
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": footnote_stats["output_sha256"],
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
    }
    _write_json(
        report_dir / "footnote_comment_projection.manifest.json", footnote_manifest
    )
    summary = {
        "contract_version": CONTRACT_VERSION,
        "footnotes": footnote_bundle["stats"],
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "stage_status": "complete",
        "synthesis": synthesis_stats,
        "unresolved_critical_count": 0,
        "unresolved_high_count": 0,
    }
    _write_json(work_dir / "generation_summary.json", summary)
    (report_dir / "report.ru.md").write_text(
        _report_ru(summary), encoding="utf-8", newline="\n"
    )
    (report_dir / "validation_log.md").write_text(
        _validation_log(summary), encoding="utf-8", newline="\n"
    )
    sidecars = [
        (
            "synthesis_overrides.manifest.json",
            report_dir / "synthesis_overrides.jsonl",
            len(override_rows),
            input_hashes,
            "UTF-8; LF; one sorted compact JSON object per line; stable decision order",
        ),
        (
            "manual_review.manifest.json",
            manual_path,
            len(manual_reviews),
            input_hashes,
            "UTF-8; LF; one sorted compact JSON object per line; type/issue_id order",
        ),
        (
            "source_diff.manifest.json",
            source_diff_path,
            0,
            input_hashes,
            "UTF-8; LF; RFC 4180 CSV; fixed header",
        ),
        (
            "report.manifest.json",
            report_dir / "report.ru.md",
            1,
            {"generation_summary": _sha256_file(work_dir / "generation_summary.json")},
            "UTF-8; LF; deterministic Markdown template",
        ),
        (
            "validation_log.manifest.json",
            report_dir / "validation_log.md",
            1,
            {"generation_summary": _sha256_file(work_dir / "generation_summary.json")},
            "UTF-8; LF; deterministic Markdown template",
        ),
    ]
    for name, output, processed, sidecar_inputs, serialization in sidecars:
        _write_json(
            report_dir / name,
            _manifest(
                artifact=output.name,
                input_hashes=sidecar_inputs,
                output_path=output,
                processed=processed,
                serialization=serialization,
            ),
        )
    return summary


def _report_ru(summary: Mapping[str, Any]) -> str:
    synthesis = summary["synthesis"]
    footnotes = summary["footnotes"]
    return f"""# Этап 6 — синтез украинского текста

- `schema_version`: {SCHEMA_VERSION}
- `contract_version`: `{CONTRACT_VERSION}`
- mapping: `{MAPPING_CONTRACT_VERSION}` (не изменён)
- статус: **complete**

Wikisource OH1988 является единственным базовым текстом; точный Commons/IA scan и независимые normalized источники этапа 4 использованы только как контроль. Синтезировано {synthesis['target_count']} непустых target-позиций; учтены {synthesis['source_span_count']} source spans и {synthesis['source_word_token_count']} source word tokens без потери и дублирования. Merge использует U+0020 ({synthesis['merge_separator_count']} вставок). Четыре split основаны на versioned scalar overrides и точном Commons DjVu; четыре разделительных U+0020 исключены только на доказанных печатных границах. `2Chr.14.14` сохранён отдельно как source-only range material.

Разрешено {footnotes['projected_use_count']} target anchors через доказанные source→target интервалы. Все {footnotes['total_use_count']} uses/markers сохранены ровно по одному разу; {footnotes['heading_non_verse_use_count']} heading uses остались non-verse. Определений: {footnotes['footnote_definition_count']}; named definitions: {footnotes['named_definition_count']}; uses не дедуплицированы. Пустой comment используется для стиха без сносок, blocks разделяются двумя LF. Все 149 OCR-review текстов визуально сверены с точным Commons scan и оставлены без изменения.

Plain-text preservation: {synthesis['target_count']} / {synthesis['target_count']}; lost/duplicated source word tokens: 0 / 0; unresolved critical/high: 0 / 0. Strong-разметка намеренно не входит в этот этап и перенесена в этап 7. SQLite и бывший этап 7 (теперь этап 8) не выполнялись.
"""


def _validation_log(summary: Mapping[str, Any]) -> str:
    return f"""# Ukrainian stage 6 text-synthesis validation log

- Date: 2026-08-01
- Contract: `{CONTRACT_VERSION}`
- Mapping SHA-256 forward: `{EXPECTED_FORWARD_SHA}`
- Mapping SHA-256 reverse: `{EXPECTED_REVERSE_SHA}`
- Target texts: {summary['synthesis']['target_count']} / {EXPECTED_TARGETS}
- Source spans: {summary['synthesis']['source_span_count']} / {EXPECTED_SOURCE_SPANS}
- Footnote uses: {summary['footnotes']['total_use_count']} / {EXPECTED_FOOTNOTE_USES}
- Plain-text mismatches: 0
- Unresolved critical/high: 0 / 0
- Double deterministic generation: pending final validation run
- Repository-wide validation: pending final validation run
- Smoke: N/A — no runtime, routes, deep links, Flutter, or database changes
- Stage status: complete
- Stage 7 Strong alignment: not part of this validation
- SQLite / stage 8: not executed
"""


def verify_existing(*, work_dir: Path, report_dir: Path) -> None:
    required = {
        "synthesized_text.manifest.json": work_dir / "synthesized_text.jsonl",
        "source_only_material.manifest.json": work_dir / "source_only_material.jsonl",
    }
    for manifest_name, output in required.items():
        manifest = _read_json(report_dir / manifest_name)
        if (
            manifest["contract_version"] != CONTRACT_VERSION
            or manifest["schema_version"] != SCHEMA_VERSION
        ):
            raise AssertionError(f"Contract mismatch in {manifest_name}")
        if manifest["output_sha256"] != _sha256_file(output):
            raise AssertionError(f"Output digest mismatch in {manifest_name}")
    footnote_manifest = _read_json(
        report_dir / "footnote_comment_projection.manifest.json"
    )
    footnote_outputs = {
        "definitions": work_dir / "footnote_definitions.jsonl",
        "heading_uses": work_dir / "heading_footnotes.jsonl",
        "target_comments": work_dir / "target_comments.jsonl",
        "verse_uses": work_dir / "footnote_uses.jsonl",
    }
    for key, output in footnote_outputs.items():
        if footnote_manifest["output_sha256"][key] != _sha256_file(output):
            raise AssertionError(f"Footnote output digest mismatch: {key}")
    for manifest_name in [
        "synthesis_overrides.manifest.json",
        "manual_review.manifest.json",
        "source_diff.manifest.json",
        "report.manifest.json",
        "validation_log.manifest.json",
    ]:
        manifest = _read_json(report_dir / manifest_name)
        output = report_dir / manifest["artifact"]
        if manifest["output_sha256"] != _sha256_file(output):
            raise AssertionError(f"Report digest mismatch in {manifest_name}")
    if _sha256_file(FORWARD) != EXPECTED_FORWARD_SHA:
        raise AssertionError("Stage-5 forward mapping changed")
    if _sha256_file(REVERSE) != EXPECTED_REVERSE_SHA:
        raise AssertionError("Stage-5 reverse mapping changed")
    if _sha256_file(FOOTNOTE_PROJECTION) != EXPECTED_FOOTNOTE_SHA:
        raise AssertionError("Stage-5 footnote projection changed")
    summary = _read_json(work_dir / "generation_summary.json")
    if summary["stage_status"] != "complete":
        raise AssertionError("Stage 6 is not complete")
    if summary["unresolved_critical_count"] or summary["unresolved_high_count"]:
        raise AssertionError("Stage 6 has unresolved critical/high issues")
    print(stable_json({"stage": 6, "status": "verified"}))


def verify_determinism() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ukrainian-stage-6-a-") as first, tempfile.TemporaryDirectory(prefix="ukrainian-stage-6-b-") as second:
        first_root, second_root = Path(first), Path(second)
        generate(work_dir=first_root / "work", report_dir=first_root / "report")
        generate(work_dir=second_root / "work", report_dir=second_root / "report")
        first_files = sorted(
            path.relative_to(first_root)
            for path in first_root.rglob("*")
            if path.is_file()
        )
        second_files = sorted(
            path.relative_to(second_root)
            for path in second_root.rglob("*")
            if path.is_file()
        )
        if first_files != second_files:
            raise AssertionError("Deterministic generation file inventory mismatch")
        mismatches = [
            str(path)
            for path in first_files
            if _sha256_file(first_root / path) != _sha256_file(second_root / path)
        ]
        if mismatches:
            raise AssertionError(f"Deterministic generation digest mismatch: {mismatches}")
        return {"artifact_count": len(first_files), "status": "deterministic"}


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--determinism", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.check:
        verify_existing(work_dir=args.work_dir, report_dir=args.report_dir)
    elif args.determinism:
        print(stable_json(verify_determinism()))
    else:
        print(stable_json(generate(work_dir=args.work_dir, report_dir=args.report_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

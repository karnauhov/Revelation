"""Reparse pinned OH1988 pages and prepare the corrected text-only release.

Historical stage-4/5/6 and Strong research inputs remain sealed. This pipeline
uses the same versification and proven split boundaries with fresh source IDs,
and audits every page and every effective source span before sealing output.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import re
import tempfile

from . import build_ohienko_1988 as builder
from . import ukrainian_stage_5 as mapping
from . import ukrainian_stage_6 as synthesis
from .ukrainian_stage_4 import load_contexts
from .ukrainian_stage_4_model import write_jsonl
from .ukrainian_stage_4_parsers import parse_wikisource_bundle
from .ukrainian_stage_5_model import (
    assert_forward_reverse_consistency, assert_unique_target_keys,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORK = ROOT / "scripts/bible_module/work/oh1988_text_repair"
DEFAULT_REPORT = ROOT / "scripts/bible_module/reports/oh1988_text_repair"
RESTORED_REFS = {"Deut.34.8", "Rev.1.3"}
ARTIFACTS = tuple(builder.INPUT_DIGESTS)


def source_texts(source):
    return {
        part.effective_ref: source.record_by_id[part.record_id]["source_plain_nfc"][
            part.span.start:part.span.end
        ] for part in source.segments
    }


def classify_change(ref: str, before: str, after: str) -> str:
    if "".join(before.split()) == "".join(after.split()):
        return "page_word_separator"
    if ref in RESTORED_REFS and after.startswith(before + " "):
        return "restored_page_continuation"
    if ref == "Rev.22.21" and before.startswith(after + " ") and re.fullmatch(
        r"(?:400px\|center\|сторінка=\d+)+", before[len(after) + 1:]
    ):
        return "noncanonical_image_carrier_removed"
    raise ValueError(f"Unexpected source change: {ref}")


def rebase_splits(rules, records, legacy_records, overrides):
    """Reuse a reviewed interval only when its entire source text is identical."""
    by_targets = {
        tuple(item["target_ref"] for item in row["target_intervals"]): row
        for row in overrides
    }
    result = {}
    for rule in rules:
        if rule["operation"] != "split":
            continue
        old = by_targets[tuple(item["ref"] for item in rule["targets"])]
        part, = rule["source_parts"]
        text = records[part["record_id"]]["text"]
        if text != legacy_records[old["record_id"]]["text"]:
            raise ValueError("Reviewed split source changed; new evidence required")
        row = copy.deepcopy(old)
        row.update(record_id=part["record_id"], rule_id=rule["rule_id"])
        row["rebase_evidence"] = {
            "previous_record_id": old["record_id"], "previous_rule_id": old["rule_id"],
            "identical_source_text_sha256": synthesis.sha256_text(text),
        }
        result[rule["rule_id"]] = row
    if len(result) != len(overrides):
        raise ValueError("Not all reviewed split boundaries were retained")
    return result


def generate(work: Path, report: Path):
    work.mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    old_manifest = json.loads((mapping.STAGE4_REPORT /
        "normalized_wikisource_ohienko_1988_revisions.manifest.json").read_text(encoding="utf-8"))
    if builder.sha256_file(mapping.SOURCE_PATH) != old_manifest["normalized_artifact"]["sha256"]:
        raise ValueError("Historical source seal changed")
    context = next(c for c in load_contexts()[0]
                   if c.source_id == "wikisource_ohienko_1988_revisions")
    parsed = parse_wikisource_bundle(context)
    if parsed.errors or parsed.counters["books"] != 66 or len(parsed.records) != 31_180:
        raise ValueError("Corrected parser corpus accounting changed")
    pages = parsed.format_details["page_audit"]
    if [row["page"] for row in pages] != list(range(1, 1539)):
        raise ValueError("Page coverage is incomplete or duplicated")
    source_path = work / "normalized_source.jsonl"
    source_path.write_bytes(write_jsonl(parsed.records)[0])
    legacy = mapping.load_source()
    source = mapping.load_source(source_path, repair_legacy_context=False)
    before, after = source_texts(legacy), source_texts(source)
    if before.keys() != after.keys():
        raise ValueError("Effective source verse inventory changed")
    changes = [
        {"source_ref": ref, "before": text, "after": after[ref],
         "kind": classify_change(ref, text, after[ref])}
        for ref, text in before.items() if text != after[ref]
    ]
    if {r["source_ref"] for r in changes if r["kind"] == "restored_page_continuation"} != RESTORED_REFS:
        raise ValueError("Expected missing continuations were not recovered")
    targets, baseline = mapping.load_targets()
    if builder.sha256_file(mapping.BASELINE_PATH) != builder.BASELINE_SHA256:
        raise ValueError("Target baseline seal changed")
    edges, evidence, _ = mapping.select_tvtms_relations(
        sections=mapping.parse_tvtms_sections(), targets=targets, source=source,
    )
    rules, reverse, _ = mapping.build_rules(
        targets=targets, source=source, edges_by_target_ref=edges,
        target_evidence=evidence, baseline_sha256=builder.BASELINE_SHA256,
        source_sha256=builder.sha256_file(source_path),
        tvtms_sha256=builder.sha256_file(mapping.TVTMS_PATH),
    )
    assert_forward_reverse_consistency(rules, reverse)
    assert_unique_target_keys(reverse)
    records, definitions, use_records = synthesis._load_source(source_path, expected_spans=31_180)
    legacy_records = synthesis._load_source()[0]
    splits = rebase_splits(rules, records, legacy_records, synthesis._load_overrides()[0])
    source_only, = [r for r in rules if not r["targets"]]
    texts, extra, stats = synthesis._synthesize(reverse, records, splits, source_only)
    projections, projection_stats, anomalies = mapping.project_footnotes(
        source=source, rules=rules, targets=targets,
    )
    uses, headings, comments, notes = synthesis._project_footnotes(
        projections, texts, definitions, use_records,
    )
    old_comments = builder.read_jsonl(synthesis.DEFAULT_WORK / "target_comments.jsonl")
    if [(r["target_ref"], r["target_comment"]) for r in old_comments] != [
        (r["target_ref"], r["target_comment"]) for r in comments
    ]:
        raise ValueError("Printed footnote text or verse binding changed")
    rows, database_stats = builder.validate_rows(texts, comments, uses, builder.target_grid(baseline))
    outputs = {
        "synthesized_text.jsonl": texts, "target_comments.jsonl": comments,
        "footnote_uses.jsonl": uses, "heading_footnotes.jsonl": headings,
        "source_only_material.jsonl": extra, "footnote_definitions.jsonl": notes["definitions"],
        "source_to_target_map.jsonl": rules, "target_to_source_map.jsonl": reverse,
        "footnote_projection.jsonl": projections, "synthesis_overrides.jsonl": list(splits.values()),
    }
    for name, data in outputs.items():
        synthesis._write_jsonl(work / name, data)
    old_texts = builder.read_jsonl(synthesis.DEFAULT_WORK / "synthesized_text.jsonl")
    target_changes = [
        {"target_ref": new["target_ref"], "verse_key": new["verse_key"],
         "kind": classify_change(new["target_ref"], old["plain_text_nfc"], new["plain_text_nfc"]),
         "before": old["plain_text_nfc"], "after": new["plain_text_nfc"]}
        for old, new in zip(old_texts, texts, strict=True)
        if old["plain_text_nfc"] != new["plain_text_nfc"]
    ]
    audit = {
        "status": "PASS", "contract": "oh1988-ordered-pages-v2",
        "source_bundle_sha256": context.expected_sha256,
        "historical_source_sha256": builder.sha256_file(mapping.SOURCE_PATH),
        "normalized_source_sha256": builder.sha256_file(source_path),
        "parser_sha256": builder.sha256_file(ROOT / "scripts/bible_module/ukrainian_stage_4_parsers.py"),
        "target_baseline_sha256": builder.BASELINE_SHA256,
        "tvtms_sha256": builder.sha256_file(mapping.TVTMS_PATH),
        "page_coverage": parsed.format_details, "source_changes": changes,
        "source_change_counts": dict(Counter(r["kind"] for r in changes)),
        "target_changes": target_changes,
        "target_change_counts": dict(Counter(r["kind"] for r in target_changes)),
        "effective_source_spans": len(after), "source_span_set_equal": True,
        "footnote_comments_unchanged": True, "footnotes": notes["stats"],
        "synthesis": stats, "database_statistics": database_stats,
        "strong_links": 0,
        "output_sha256": {name: builder.sha256_file(work / name) for name in outputs},
    }
    synthesis._write_json(report / "source_audit.json", audit)
    synthesis._write_json(report / "inputs.manifest.json", {
        "contract": audit["contract"], "source_bundle_sha256": context.expected_sha256,
        "source_audit_sha256": builder.sha256_file(report / "source_audit.json"),
        "output_sha256": audit["output_sha256"],
    })
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="oh1988-reparse-") as temporary:
            root = Path(temporary)
            audit = generate(root / "work", root / "report")
            expected = json.loads((args.report_dir / "source_audit.json").read_text(encoding="utf-8"))
            if audit != expected:
                raise ValueError("Full source reparse differs from sealed audit")
            for name, digest in audit["output_sha256"].items():
                if builder.sha256_file(args.work_dir / name) != digest:
                    raise ValueError(f"Sealed corrected artifact changed: {name}")
    else:
        audit = generate(args.work_dir, args.report_dir)
    print(json.dumps({"status": audit["status"], "changes": audit["target_change_counts"],
                      "source_spans": audit["effective_source_spans"]}))


if __name__ == "__main__":
    main()

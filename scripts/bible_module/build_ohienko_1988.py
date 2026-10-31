"""Build a staging OH1988 text module from the sealed, page-audited text corpus.

Strong research is deliberately not an input. Metadata is supplied explicitly so
the text-only attribution can be reviewed before a candidate is distributed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from typing import Any

from .ukrainian_stage_2_contract import (
    DEFAULT_BASELINE_PATH,
    MODULE_CODE,
    MODULE_FILENAME,
    MODULE_ID,
    MODULE_LANGUAGE,
    MODULE_TITLE,
    PROJECT_ROOT,
    schema_snapshot,
)
from .ukrainian_stage_6_model import (
    CONTRACT_VERSION,
    MAPPING_CONTRACT_VERSION,
    serialize_comment_uses,
    sha256_text,
    stable_json,
    word_tokens,
)

DEFAULT_WORK = PROJECT_ROOT / "scripts/bible_module/work/oh1988_text_repair"
BUILD_CONTRACT = "oh1988-text-module-v2"
BASELINE_SHA256 = "3c5fd1c4cbe8fa10d19f5c9301c778c165fb690b7fb374745cbb1c03948081c1"
INPUT_DIGESTS = {
    "synthesized_text.jsonl": "b634fef17d963997666fafd1653ff7acf47a55fef01465c9d9e66df357da6ebf",
    "target_comments.jsonl": "5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4",
    "footnote_uses.jsonl": "0b5579a18114f3a933272d547f4a5fdbc48430e09afb4134599f7324fb758056",
    "heading_footnotes.jsonl": "e5d31c484efb13f1ea9ee60cd8e342fc406d4ff1b37ae226dd76124b906f06aa",
    "source_only_material.jsonl": "a9674ef8a43410a30a86782f1cc82923f41c2c599858f9252c6134fac30cf40f",
    "footnote_definitions.jsonl": "8bf67f0dfb6ede4bac591afc6b879c82924f0c34e3c5ab27cf673d095b4fc514"
}
INFO_FIELDS = (
    "code", "module_id", "title", "description", "language", "canon",
    "versification", "license", "source_summary",
)
STRONG_PATTERN = re.compile(r"(?<!\w)[GH]\d+(?!\w)", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def target_grid(baseline: Mapping[str, Any]) -> list[tuple[str, str]]:
    grid = baseline["target_grid"]
    refs = [
        f"{book['code']}.{chapter}.{verse}"
        for book in grid["books"]
        for chapter, count in enumerate(book["chapters"], 1)
        for verse in range(1, int(count) + 1)
    ]
    keys = grid["verse_keys"]
    if len(refs) != len(keys) or len(set(keys)) != len(keys):
        raise ValueError("Invalid baseline grid")
    return list(zip(keys, refs, strict=True))


def validate_rows(
    texts: Sequence[Mapping[str, Any]],
    comments: Sequence[Mapping[str, Any]],
    uses: Sequence[Mapping[str, Any]],
    grid: Sequence[tuple[str, str]],
) -> tuple[list[tuple[str, str, str]], dict[str, Any]]:
    """Require exact ordered text/comment identity and footnote binding."""
    if len(texts) != len(grid) or len(comments) != len(grid):
        raise ValueError("Missing or extra text/comment rows")
    by_ref: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    seen_uses: set[str] = set()
    for use in uses:
        uid = use["use_id"]
        if not isinstance(uid, str) or not uid or uid in seen_uses:
            raise ValueError("Duplicate or invalid footnote use")
        seen_uses.add(uid)
        if (
            use.get("contract_version") != CONTRACT_VERSION
            or use.get("mapping_contract_version") != MAPPING_CONTRACT_VERSION
            or use.get("anchor_status") != "resolved_by_proven_source_target_interval"
        ):
            raise ValueError("Unproved footnote binding")
        by_ref[use["target_ref"]].append(use)
    result = []
    chapters: dict[str, Counter[str]] = defaultdict(Counter)
    operations: Counter[str] = Counter()
    consumed: set[str] = set()
    for order, ((key, ref), text_row, comment_row) in enumerate(
        zip(grid, texts, comments, strict=True), 1
    ):
        for row in (text_row, comment_row):
            if (
                (row.get("verse_key"), row.get("target_ref"), row.get("order"))
                != (key, ref, order)
                or row.get("contract_version") != CONTRACT_VERSION
                or row.get("schema_version") != 1
            ):
                raise ValueError(f"Incorrect row identity/order: {ref}")
        if (
            text_row.get("mapping_contract_version") != MAPPING_CONTRACT_VERSION
            or not text_row.get("rule_id")
            or text_row.get("operation") not in {"1:1", "merge", "split", "range_transfer"}
        ):
            raise ValueError(f"Missing mapping rule: {ref}")
        text = text_row.get("plain_text_nfc")
        comment = comment_row.get("target_comment")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Empty verse: {ref}")
        if not isinstance(comment, str):
            raise ValueError(f"Missing/NULL comment: {ref}")
        if sha256_text(text) != text_row.get("plain_text_sha256"):
            raise ValueError(f"Text digest mismatch: {ref}")
        if sha256_text(comment) != comment_row.get("comment_sha256"):
            raise ValueError(f"Comment digest mismatch: {ref}")
        if STRONG_PATTERN.search(text) or STRONG_PATTERN.search(comment):
            raise ValueError(f"Strong marker in text-only module: {ref}")
        verse_uses = by_ref.get(ref, [])
        if [u["use_id"] for u in verse_uses] != comment_row.get("use_ids"):
            raise ValueError(f"Lost or rebound footnote: {ref}")
        for use in verse_uses:
            anchor = use.get("target_anchor") or {}
            start, end = anchor.get("start_scalar"), anchor.get("end_scalar")
            if (
                use.get("target_order") != order
                or use.get("mapping_rule_id") != text_row["rule_id"]
                or not isinstance(start, int) or not isinstance(end, int)
                or not 0 <= start <= end <= len(text)
            ):
                raise ValueError(f"Invalid footnote anchor: {ref}")
            consumed.add(use["use_id"])
        if serialize_comment_uses(verse_uses) != comment:
            raise ValueError(f"Comment differs from printed uses: {ref}")
        result.append((key, text, comment))
        chapter = ref.rsplit(".", 1)[0]
        chapters[chapter].update({
            "verses": 1, "words": len(word_tokens(text)), "strong_markers": 0,
            "footnote_uses": len(verse_uses), "nonempty_comments": int(bool(comment)),
            "empty_texts": 0,
        })
        operations[text_row["operation"]] += 1
    if consumed != seen_uses:
        raise ValueError("Footnotes outside the target grid")
    books: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    for chapter, counts in chapters.items():
        books[chapter.split(".")[0]].update(counts)
        totals.update(counts)
    return result, {
        "books": {k: dict(v) for k, v in books.items()},
        "chapters": {k: dict(v) for k, v in chapters.items()},
        "totals": dict(totals),
        "projection_operations": dict(operations),
        "warnings": [],
    }


def load_inputs(work: Path, baseline_path: Path = DEFAULT_BASELINE_PATH):
    for name, expected in INPUT_DIGESTS.items():
        if sha256_file(work / name) != expected:
            raise ValueError(f"Sealed input changed: {name}")
    if sha256_file(baseline_path) != BASELINE_SHA256:
        raise ValueError("Sealed stage-2 baseline changed")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    grid = target_grid(baseline)
    if len(grid) != 31102 or len(baseline["target_grid"]["books"]) != 66:
        raise ValueError("Production baseline count changed")
    rows, stats = validate_rows(
        read_jsonl(work / "synthesized_text.jsonl"),
        read_jsonl(work / "target_comments.jsonl"),
        read_jsonl(work / "footnote_uses.jsonl"), grid,
    )
    headings = read_jsonl(work / "heading_footnotes.jsonl")
    extra = read_jsonl(work / "source_only_material.jsonl")
    if len(headings) != 11 or len(extra) != 1 or stats["totals"]["footnote_uses"] != 1318:
        raise ValueError("Non-verse source material count changed")
    stats["retained_non_verse_material"] = {
        "heading_footnote_uses": len(headings), "source_only_ranges": len(extra),
        "disposition": "preserved in sealed stage-6 sidecars; not attached to a neighbouring verse",
    }
    return baseline, rows, stats


def validate_info(info: Mapping[str, Any]) -> None:
    if set(info) != set(INFO_FIELDS) or any(
        not isinstance(info[k], str) or not info[k].strip() for k in INFO_FIELDS
    ):
        raise ValueError("Info must contain exactly nine nonempty text fields")
    expected = {
        "code": MODULE_CODE, "module_id": MODULE_ID, "title": MODULE_TITLE,
        "language": MODULE_LANGUAGE, "canon": "protestant_66",
        "versification": "kjv_protestant",
    }
    if any(info[k] != v for k, v in expected.items()):
        raise ValueError("Module identity differs from the approved edition")


def validate_metadata(data_version: int, built_at: str) -> None:
    if isinstance(data_version, bool) or not isinstance(data_version, int) or data_version < 1:
        raise ValueError("data_version must be a positive integer")
    date = datetime.fromisoformat(built_at.replace("Z", "+00:00"))
    if date.tzinfo is None or date.utcoffset().total_seconds() != 0:
        raise ValueError("Build date must be UTC with an explicit timezone")


def audit_database(
    path: Path, rows: Sequence[tuple[str, str, str]],
    info: Mapping[str, str], schema: Mapping[str, Any],
    data_version: int, built_at: str,
) -> dict[str, Any]:
    """Read every installed value back without allowing SQLite writes."""
    before = sha256_file(path)
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        if schema_snapshot(connection) != schema:
            raise ValueError("SQLite schema differs from the stage-2 contract")
        if connection.execute("PRAGMA user_version").fetchone()[0] != 4:
            raise ValueError("PRAGMA user_version differs")
        metadata = dict(connection.execute("SELECT key,value FROM db_metadata"))
        if metadata != {"schema_version": "4", "data_version": str(data_version), "date": built_at}:
            raise ValueError("SQLite metadata differs")
        actual_info = connection.execute("SELECT * FROM info").fetchall()
        if actual_info != [tuple(info[k] for k in INFO_FIELDS)]:
            raise ValueError("SQLite info differs")
        actual = connection.execute("SELECT verse_key,text,comment FROM verses ORDER BY verse_key").fetchall()
        if actual != list(rows):
            raise ValueError("SQLite text/comment/key differs from sealed inputs")
    finally:
        connection.close()
    if sha256_file(path) != before:
        raise ValueError("Read-only audit changed the database")
    semantic = {
        "schema": schema, "info": dict(info), "verses": actual,
        "metadata": {"schema_version": "4", "data_version": str(data_version)},
    }
    return {
        "integrity_check": "ok", "schema_version": 4,
        "verified_verses": len(actual), "verified_comments": len(actual),
        "sha256": before, "bytes": path.stat().st_size,
        "semantic_sha256_without_build_date": sha256_text(stable_json(semantic)),
    }


def build_database(
    target: Path, rows: Sequence[tuple[str, str, str]], info: Mapping[str, str],
    schema: Mapping[str, Any], *, data_version: int, built_at: str,
    replace: bool = False,
) -> dict[str, Any]:
    validate_info(info)
    validate_metadata(data_version, built_at)
    if target.is_symlink() or (target.exists() and not replace):
        raise FileExistsError(f"Refusing to replace {target}; use --replace explicitly")
    if not rows or any(
        not isinstance(k, str) or len(k) != 3 or not isinstance(t, str)
        or not t.strip() or not isinstance(c, str)
        or STRONG_PATTERN.search(t) or STRONG_PATTERN.search(c)
        for k, t, c in rows
    ) or [r[0] for r in rows] != sorted({r[0] for r in rows}):
        raise ValueError("Invalid, unordered, duplicate, empty or Strong-bearing rows")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".oh1988-", dir=target.parent) as temporary:
        staging = Path(temporary) / MODULE_FILENAME
        connection = sqlite3.connect(staging)
        try:
            for table in schema["tables"].values():
                connection.execute(table["sql"])
            connection.execute("PRAGMA user_version=4")
            connection.executemany("INSERT INTO db_metadata VALUES (?,?)", [
                ("schema_version", "4"), ("data_version", str(data_version)), ("date", built_at),
            ])
            connection.execute("INSERT INTO info VALUES (?,?,?,?,?,?,?,?,?)", tuple(info[k] for k in INFO_FIELDS))
            connection.executemany("INSERT INTO verses VALUES (?,?,?)", rows)
            connection.commit()
        finally:
            connection.close()
        audit = audit_database(staging, rows, info, schema, data_version, built_at)
        backup = None
        if target.exists():
            # A unique sibling survives replacement; never overwrite an earlier backup.
            fd, name = tempfile.mkstemp(prefix=target.name + ".backup-", suffix=".sqlite", dir=target.parent)
            os.close(fd)
            backup = Path(name)
            shutil.copy2(target, backup)
            if sha256_file(backup) != sha256_file(target):
                raise ValueError("Backup verification failed")
        os.replace(staging, target)
    return {**audit, "path": str(target), "backup_path": str(backup) if backup else None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--info", type=Path, required=True, help="Explicit reviewed/draft text-only info JSON")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--data-version", type=int, default=2)
    parser.add_argument("--built-at", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    protected = {args.info.resolve(), DEFAULT_BASELINE_PATH.resolve()}
    protected.update((args.work_dir / name).resolve() for name in INPUT_DIGESTS)
    if (
        args.output.resolve() in protected or args.report.resolve() in protected
        or args.output.resolve() == args.report.resolve()
    ):
        raise ValueError("Output/report paths must not overwrite inputs or each other")
    baseline, rows, stats = load_inputs(args.work_dir)
    info = json.loads(args.info.read_text(encoding="utf-8"))
    result = build_database(
        args.output, rows, info, baseline["schema_contracts"]["ukrainian_v4"]["schema"],
        data_version=args.data_version, built_at=args.built_at, replace=args.replace,
    )
    report = {
        "contract": BUILD_CONTRACT, "status": "staging_candidate_validated",
        "built_at": args.built_at, "data_version": args.data_version,
        "input_sha256": INPUT_DIGESTS,
        "baseline_sha256": sha256_file(DEFAULT_BASELINE_PATH),
        "info_sha256": sha256_file(args.info), "database": result, "statistics": stats,
        "strong_research_inputs": 0, "production_strong_links": 0,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "database": result, "totals": stats["totals"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

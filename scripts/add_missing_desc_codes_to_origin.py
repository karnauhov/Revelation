#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
add_missing_desc_codes_to_origin.py

1) Reads G/H codes from revelation_en.greek_descs.desc.
2) Checks the same id in revelation.greek_words.origin.
3) If code is missing in origin, appends it to origin (without removing existing data).
4) For each changed id prints origin BEFORE and AFTER.
5) Prints summary stats.
"""

import os
import re
import sqlite3
import sys
from typing import Dict, List, Optional, Set

DESC_DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"
ORIGIN_DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation.sqlite"

DESC_TABLE = "greek_descs"
DESC_COLUMN = "desc"

ORIGIN_TABLE = "greek_words"
ORIGIN_COLUMN = "origin"

CODE_RE = re.compile(r"\b([GH]\d+)\b")


def extract_codes(text: Optional[str]) -> List[str]:
    """Extract G/H codes preserving first-seen order and removing duplicates."""
    if text is None:
        return []

    seen: Set[str] = set()
    ordered: List[str] = []

    for match in CODE_RE.finditer(str(text)):
        code = match.group(1)
        if code not in seen:
            seen.add(code)
            ordered.append(code)
    return ordered


def build_updated_origin(origin_value: Optional[str], missing_codes: List[str]) -> str:
    """Append missing codes to origin preserving existing content."""
    to_add = ",".join(missing_codes)
    if origin_value is None:
        return to_add

    original = str(origin_value)
    if not original.strip():
        return to_add

    base = original.rstrip()
    if base.endswith(","):
        return f"{base}{to_add}"
    return f"{base},{to_add}"


def load_origin_by_id(conn: sqlite3.Connection) -> Dict[int, Optional[str]]:
    """Load raw origin text by id from revelation.sqlite."""
    cur = conn.cursor()
    cur.execute(f"SELECT id, {ORIGIN_COLUMN} FROM {ORIGIN_TABLE}")

    by_id: Dict[int, Optional[str]] = {}
    for row_id, origin in cur.fetchall():
        by_id[row_id] = origin
    return by_id


def fmt_origin(value: Optional[str]) -> str:
    if value is None:
        return "<NULL>"
    return value


def main() -> int:
    if not os.path.isfile(DESC_DB_PATH):
        print(f"DB not found: {DESC_DB_PATH}", file=sys.stderr)
        return 1
    if not os.path.isfile(ORIGIN_DB_PATH):
        print(f"DB not found: {ORIGIN_DB_PATH}", file=sys.stderr)
        return 1

    try:
        desc_conn = sqlite3.connect(DESC_DB_PATH)
        origin_conn = sqlite3.connect(ORIGIN_DB_PATH)
    except Exception as exc:
        print(f"Failed to open database: {exc}", file=sys.stderr)
        return 1

    try:
        origin_by_id = load_origin_by_id(origin_conn)
    except Exception as exc:
        print(f"Failed to read {ORIGIN_TABLE}.{ORIGIN_COLUMN}: {exc}", file=sys.stderr)
        desc_conn.close()
        origin_conn.close()
        return 1

    try:
        cur = desc_conn.cursor()
        cur.execute(f"SELECT id, {DESC_COLUMN} FROM {DESC_TABLE}")
        desc_rows = cur.fetchall()
    except Exception as exc:
        print(f"Failed to read {DESC_TABLE}.{DESC_COLUMN}: {exc}", file=sys.stderr)
        desc_conn.close()
        origin_conn.close()
        return 1

    total_rows = len(desc_rows)
    ids_with_codes_in_desc = 0
    ids_updated = 0
    ids_without_changes = 0
    ids_missing_in_origin_table = 0
    total_added_codes = 0

    write_cur = origin_conn.cursor()
    print("Changes in origin by id:")

    for row_id, desc in desc_rows:
        desc_codes = extract_codes(desc)
        if not desc_codes:
            continue

        ids_with_codes_in_desc += 1
        if row_id not in origin_by_id:
            ids_missing_in_origin_table += 1
            continue

        origin_before = origin_by_id[row_id]
        origin_codes = set(extract_codes(origin_before))
        missing_codes = [code for code in desc_codes if code not in origin_codes]

        if not missing_codes:
            ids_without_changes += 1
            continue

        origin_after = build_updated_origin(origin_before, missing_codes)

        try:
            write_cur.execute(
                f"UPDATE {ORIGIN_TABLE} SET {ORIGIN_COLUMN} = ? WHERE id = ?",
                (origin_after, row_id),
            )
        except Exception as exc:
            print(f"Update failed for id={row_id}: {exc}", file=sys.stderr)
            continue

        if write_cur.rowcount == 0:
            ids_missing_in_origin_table += 1
            continue

        ids_updated += 1
        total_added_codes += len(missing_codes)
        origin_by_id[row_id] = origin_after

        print(f"ID {row_id}")
        print(f"  before: {fmt_origin(origin_before)}")
        print(f"  after:  {origin_after}")
        print(f"  added:  {', '.join(missing_codes)}")

    try:
        origin_conn.commit()
    except Exception as exc:
        print(f"Commit failed: {exc}", file=sys.stderr)
        desc_conn.close()
        origin_conn.close()
        return 1

    print()
    print("=== Summary ===")
    print(f"Rows in {DESC_TABLE}: {total_rows}")
    print(f"IDs with at least one G/H code in {DESC_COLUMN}: {ids_with_codes_in_desc}")
    print(f"IDs updated in {ORIGIN_TABLE}.{ORIGIN_COLUMN}: {ids_updated}")
    print(f"IDs without changes needed: {ids_without_changes}")
    print(f"IDs missing in {ORIGIN_TABLE}: {ids_missing_in_origin_table}")
    print(f"Total codes appended: {total_added_codes}")

    desc_conn.close()
    origin_conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

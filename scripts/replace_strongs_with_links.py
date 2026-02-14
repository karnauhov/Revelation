#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
replace_strongs_with_links.py

Update greek_descs.desc in revelation_en.sqlite.

For each G<number> / H<number> sequence:
- replace it with markdown link:
    [G<number>](strong:G<number>) or [H<number>](strong:H<number>)
- if token is H and number starts with 0, remove only the first leading zero
  in the inserted value
- if token is immediately followed by optional spaces/tabs and (...) then
  remove that (...) part too (including the brackets)

The script prints each exact replacement:
    ID, removed substring, inserted substring

A timestamped DB backup is created before updates.
"""

import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime

DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"
TABLE_NAME = "greek_descs"
DESC_COLUMN = '"desc"'
TOKEN_RE = re.compile(r"\b([GH])(\d+)\b", flags=re.IGNORECASE | re.UNICODE)
STRONG_PREFIX = "strong:"


def backup_db(db_path: str) -> str:
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f"DB not found: {db_path}")

    base_dir, file_name = os.path.split(db_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_name}.bak_{timestamp}"
    backup_path = os.path.join(base_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    return backup_path


def normalize_token(prefix_raw: str, digits_raw: str):
    prefix = prefix_raw.upper()
    digits = digits_raw

    # For H-numbers remove only the first leading zero, if present.
    if prefix == "H" and len(digits) > 1 and digits.startswith("0"):
        digits = digits[1:]

    return prefix, digits


def should_skip_match(text: str, start_pos: int) -> bool:
    # Skip already-converted label: [G123]
    if start_pos > 0 and text[start_pos - 1] == "[":
        return True

    # Skip already-converted target: (strong:G123)
    pref_len = len(STRONG_PREFIX)
    if start_pos >= pref_len and text[start_pos - pref_len:start_pos].lower() == STRONG_PREFIX:
        return True

    return False


def find_optional_round_brackets_end(text: str, token_end_pos: int) -> int:
    """
    Return end position for removal:
    - token_end_pos if no immediate optional '(...)' tail
    - position just after matching ')' if found
    """
    idx = token_end_pos
    text_len = len(text)

    # Remove only spaces/tabs before '(' to avoid crossing line boundaries.
    while idx < text_len and text[idx] in (" ", "\t"):
        idx += 1

    if idx >= text_len or text[idx] != "(":
        return token_end_pos

    # Balanced scan for round brackets.
    depth = 1
    idx += 1
    while idx < text_len:
        ch = text[idx]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return idx + 1
        idx += 1

    # No closing bracket -> do not remove tail.
    return token_end_pos


def replace_in_text(row_id: int, desc_text):
    text = "" if desc_text is None else str(desc_text)
    result_parts = []
    cursor = 0
    replacements = []
    count_g = 0
    count_h = 0

    for match in TOKEN_RE.finditer(text):
        start_pos, end_pos = match.span()

        # If a previous replacement consumed this position, ignore.
        if start_pos < cursor:
            continue

        if should_skip_match(text, start_pos):
            continue

        prefix_raw, digits_raw = match.group(1), match.group(2)
        prefix, digits = normalize_token(prefix_raw, digits_raw)

        remove_end = find_optional_round_brackets_end(text, end_pos)
        old_substring = text[start_pos:remove_end]
        new_substring = f"[{prefix}{digits}](strong:{prefix}{digits})"

        result_parts.append(text[cursor:start_pos])
        result_parts.append(new_substring)
        cursor = remove_end

        if prefix == "G":
            count_g += 1
        else:
            count_h += 1

        replacements.append((row_id, old_substring, new_substring))

    if not replacements:
        return text, replacements, count_g, count_h

    result_parts.append(text[cursor:])
    new_text = "".join(result_parts)
    return new_text, replacements, count_g, count_h


def main():
    if not os.path.isfile(DB_PATH):
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        return

    try:
        backup_path = backup_db(DB_PATH)
        print(f"Backup created: {backup_path}")
    except Exception as exc:
        print(f"Backup failed: {exc}", file=sys.stderr)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT id, {DESC_COLUMN} FROM {TABLE_NAME}")
    except Exception as exc:
        print(f"Query failed for {TABLE_NAME}: {exc}", file=sys.stderr)
        conn.close()
        return

    rows = cur.fetchall()
    total_rows = len(rows)
    print(f"Rows found: {total_rows}. Start processing...")

    total_g = 0
    total_h = 0
    total_replacements = 0
    rows_changed = 0

    for row_id, desc_text in rows:
        new_text, replacements, cnt_g, cnt_h = replace_in_text(row_id, desc_text)

        if not replacements:
            continue

        rows_changed += 1
        total_g += cnt_g
        total_h += cnt_h
        total_replacements += len(replacements)

        for rid, old_sub, new_sub in replacements:
            print(f"ID {rid} | removed=<<<{old_sub}>>> | inserted=<<<{new_sub}>>>")

        try:
            cur.execute(
                f"UPDATE {TABLE_NAME} SET {DESC_COLUMN} = ? WHERE id = ?",
                (new_text, row_id),
            )
        except Exception as exc:
            print(f"Update failed for id={row_id}: {exc}", file=sys.stderr)
            try:
                conn.rollback()
            except Exception:
                pass
            conn.close()
            return

    try:
        conn.commit()
    except Exception as exc:
        print(f"Commit failed: {exc}", file=sys.stderr)
        try:
            conn.rollback()
        except Exception:
            pass
        conn.close()
        return

    print("\n--- Summary ---")
    print(f"Rows scanned: {total_rows}")
    print(f"Rows changed: {rows_changed}")
    print(f"Total replacements: {total_replacements}")
    print(f"G sequences replaced: {total_g}")
    print(f"H sequences replaced: {total_h}")

    conn.close()

    return {
        "rows_scanned": total_rows,
        "rows_changed": rows_changed,
        "total_replacements": total_replacements,
        "total_g": total_g,
        "total_h": total_h,
    }


if __name__ == "__main__":
    main()

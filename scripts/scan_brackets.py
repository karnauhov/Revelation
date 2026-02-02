#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
scan_unmatched_closing_marked.py

Scans a fixed SQLite database file and table (greek_descs.desc).
For each row counts total parentheses characters '(' + ')'.
If the total is odd, prints one-line record:

    id<TAB>index<TAB>full_desc_with_markers

index is the 0-based position of the first closing parenthesis ')'
that has no matching '(' before it (first unmatched closing).
full_desc_with_markers is the whole (sanitized) description where
we insert "@@" before and after that unmatched ')' so you can visually check.
If no unmatched closing exists, index is empty and no markers are inserted.

No CLI parameters — paths and table/column names are fixed.
"""

import sqlite3
from pathlib import Path
import sys
import re

# Fixed DB path and table/column names
DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"
TABLE = "greek_descs"
COL = "desc"
ID_COL = "id"

# Fetch batch size
BATCH_SIZE = 1000

def sanitize_one_line(s: str) -> str:
    """
    Replace newlines and tabs with spaces and collapse consecutive whitespace
    so output remains single-line and compact.
    """
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    # collapse multiple spaces into single
    s = re.sub(r" {2,}", " ", s)
    return s.strip()

def find_first_unmatched_closing(text: str):
    """
    Scan text left-to-right and return the index (0-based) of the first closing parenthesis ')'
    for which there was no unmatched opening '(' before it. If none, return None.

    Algorithm:
    - Maintain open_count: increment on '('.
    - On ')' if open_count > 0 -> decrement (matched), else -> this is an unmatched closing -> return index.
    """
    if text is None:
        return None
    open_count = 0
    for idx, ch in enumerate(text):
        if ch == "(":
            open_count += 1
        elif ch == ")":
            if open_count > 0:
                open_count -= 1
            else:
                return idx
    return None

def main():
    db_file = Path(DB_PATH)
    if not db_file.exists():
        print(f"Database file not found: {DB_PATH}", file=sys.stderr)
        sys.exit(2)

    # Open connection and defensively decode bytes
    conn = sqlite3.connect(str(db_file))
    conn.text_factory = lambda b: b.decode(errors="replace")
    cur = conn.cursor()

    table_q = f'"{TABLE}"'
    col_q = f'"{COL}"'
    id_q = f'"{ID_COL}"'

    try:
        cur.execute(f"SELECT {id_q}, {col_q} FROM {table_q}")
    except sqlite3.Error as e:
        print(f"SQLite error while querying: {e}", file=sys.stderr)
        conn.close()
        sys.exit(3)

    total_found = 0

    # Iterate in batches
    while True:
        rows = cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        for row in rows:
            row_id, desc = row

            if desc is None:
                continue

            # Sanitize to single-line form first (we compute index on sanitized string)
            desc_s = sanitize_one_line(desc)

            # Count total parentheses characters (only '(' and ')')
            total_paren = desc_s.count("(") + desc_s.count(")")

            if total_paren % 2 == 1:
                # find first unmatched closing ')' on sanitized text
                idx_unmatched = find_first_unmatched_closing(desc_s)
                if idx_unmatched is not None:
                    # Insert markers before and after the unmatched ')'
                    # Keep index reported as the original index in sanitized string (0-based)
                    # Construct modified description with markers
                    marked = desc_s[:idx_unmatched] + "@@" + desc_s[idx_unmatched] + "@@" + desc_s[idx_unmatched+1:]
                    index_field = str(idx_unmatched)
                else:
                    # No unmatched closing found (oddness from extra '(')
                    marked = desc_s
                    index_field = ""

                # Print single-line record: id<TAB>index<TAB>marked_desc
                # No additional separators, one record per line.
                print(f"{row_id}\t{index_field}\t{marked}")
                total_found += 1

    conn.close()

    # Print total count as a final line
    print(f"Найдено {total_found} строк(а) с нечётным числом круглых скобок.")

if __name__ == "__main__":
    main()

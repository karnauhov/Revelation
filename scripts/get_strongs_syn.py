#!/usr/bin/env python3
# coding: utf-8

import sqlite3
import re
import os
import sys

# Path to source and destination DB files
SRC_DB = r'C:\Users\karna\Downloads\Revelation\revelation_ru.sqlite'
DST_DB = r'C:\Users\karna\Downloads\Revelation\revelation.sqlite'

def fail(msg):
    print(msg)
    sys.exit(1)

def main(src_db_path, dst_db_path):
    # Basic checks for files
    if not os.path.isfile(src_db_path):
        fail(f"ERROR: source database not found at: {src_db_path}")
    if not os.path.isfile(dst_db_path):
        fail(f"ERROR: destination database not found at: {dst_db_path}")

    # Regex patterns
    # find "*син.*" marker and capture after it up to first dot or semicolon (non-greedy)
    pattern_syn = re.compile(r'\*син\.\*\s*(.*?)(?:[.;]|$)', re.IGNORECASE | re.DOTALL)
    # capture anything inside square brackets [ ... ]
    pattern_bracket_any = re.compile(r'\[\s*([^\]]+?)\s*\]')

    # Connect to source DB to inspect columns and read data
    src_conn = sqlite3.connect(src_db_path)
    try:
        src_cur = src_conn.cursor()
        src_cur.execute("PRAGMA table_info(greek_descs)")
        cols_info = src_cur.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
        col_names = [c[1] for c in cols_info]

        # find index of column named 'desc'
        desc_idx = None
        for i, n in enumerate(col_names):
            if n.lower() == 'desc':
                desc_idx = i
                break

        # determine neighbor column name to use as id (prefer left neighbor)
        neighbor_col_name = None
        if desc_idx is not None:
            if desc_idx - 1 >= 0:
                neighbor_col_name = col_names[desc_idx - 1]
            elif desc_idx + 1 < len(col_names):
                neighbor_col_name = col_names[desc_idx + 1]

        # fallback: if neighbor not found, try to use column named 'id'
        if neighbor_col_name is None:
            for n in col_names:
                if n.lower() == 'id':
                    neighbor_col_name = n
                    break

        if neighbor_col_name:
            select_query = f'SELECT rowid, "{neighbor_col_name}", "desc" FROM greek_descs'
        else:
            select_query = 'SELECT rowid, "desc" FROM greek_descs'

        # Prepare destination DB
        dst_conn = sqlite3.connect(dst_db_path)
        try:
            dst_cur = dst_conn.cursor()

            # Check that table greek_words exists and has column 'synonyms'
            dst_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='greek_words'")
            if not dst_cur.fetchone():
                fail("ERROR: destination table 'greek_words' does not exist in destination DB.")

            dst_cur.execute("PRAGMA table_info(greek_words)")
            dst_cols = [c[1] for c in dst_cur.fetchall()]
            if 'synonyms' not in dst_cols:
                fail("ERROR: destination table 'greek_words' has no column 'synonyms'.")

            # Start transaction
            updated_rows = 0
            skipped_no_id = 0
            skipped_not_found = 0
            total_tokens_inserted = 0
            invalid_tokens_report = []  # list of tuples (src_rowid, neighbor_value, raw_invalid_token)
            extracted_fragments_map = {}  # rowid -> list of original extracted fragments

            # Iterate source rows
            for row in src_cur.execute(select_query):
                if neighbor_col_name:
                    rowid, neighbor_value, desc = row
                else:
                    rowid, desc = row
                    neighbor_value = None

                if not desc:
                    continue

                # decode bytes if necessary
                if isinstance(desc, (bytes, bytearray)):
                    try:
                        desc = desc.decode('utf-8')
                    except Exception:
                        desc = desc.decode('utf-8', errors='replace')

                syn_matches = pattern_syn.findall(desc)
                if not syn_matches:
                    continue

                # Save original extracted fragments (trimmed)
                fragments_raw = [frag.strip() for frag in syn_matches if frag and frag.strip()]
                extracted_fragments_map[rowid] = fragments_raw.copy()

                # Determine neighbor_id (int) early so we can exclude self-references
                if neighbor_value is None:
                    print(f"[row {rowid}] WARNING: no neighbor/id column found in source; skipping update for this row.")
                    skipped_no_id += 1
                    continue

                # decode neighbor_value if bytes
                if isinstance(neighbor_value, (bytes, bytearray)):
                    try:
                        neighbor_value = neighbor_value.decode('utf-8')
                    except Exception:
                        neighbor_value = neighbor_value.decode('utf-8', errors='replace')

                # Try to coerce neighbor_value to integer id for matching destination table
                neighbor_id = None
                if isinstance(neighbor_value, int):
                    neighbor_id = neighbor_value
                else:
                    s = str(neighbor_value).strip()
                    if s.isdigit():
                        neighbor_id = int(s)
                    else:
                        print(f"[row {rowid}] WARNING: neighbor id value is not an integer ({s}); skipping update.")
                        skipped_no_id += 1
                        continue

                # Collect bracket tokens from all syn_matches for this row
                tokens_numeric = []
                for frag in syn_matches:
                    for raw in pattern_bracket_any.findall(frag):
                        raw_token = raw.strip()
                        if not raw_token:
                            continue
                        # Normalize if starts with G/g
                        if raw_token[0].lower() == 'g':
                            after_g = raw_token[1:].strip()
                            if after_g.isdigit():
                                tokens_numeric.append(after_g)
                            else:
                                invalid_tokens_report.append((rowid, neighbor_value, raw_token))
                        else:
                            # if token itself is digits, accept it
                            if raw_token.isdigit():
                                tokens_numeric.append(raw_token)
                            else:
                                invalid_tokens_report.append((rowid, neighbor_value, raw_token))

                # Remove tokens that are equal to neighbor_id (self-synonyms)
                tokens_filtered = []
                for t in tokens_numeric:
                    try:
                        if t.isdigit() and int(t) == neighbor_id:
                            # skip self-reference
                            continue
                    except Exception:
                        pass
                    tokens_filtered.append(t)

                # Remove duplicates while preserving order
                seen = set()
                tokens_unique = []
                for t in tokens_filtered:
                    if t not in seen:
                        seen.add(t)
                        tokens_unique.append(t)

                # Prepare synonyms string (comma-separated numbers, no spaces)
                if tokens_unique:
                    synonyms_value = ",".join(tokens_unique)
                else:
                    synonyms_value = ""  # empty string if nothing valid (or only self-references)

                # Check destination row exists
                dst_cur.execute("SELECT COUNT(1) FROM greek_words WHERE id = ?", (neighbor_id,))
                found = dst_cur.fetchone()[0]
                if not found:
                    print(f"[row {rowid}] WARNING: destination row with id={neighbor_id} not found in greek_words; skipping.")
                    skipped_not_found += 1
                    continue

                # Perform update
                dst_cur.execute("UPDATE greek_words SET synonyms = ? WHERE id = ?", (synonyms_value, neighbor_id))
                updated_rows += 1
                total_tokens_inserted += len(tokens_unique)

                # Print per-row summary including original extracted fragments
                # (fragments joined with " | " to preserve separation if multiple)
                fragments_display = " | ".join(fragments_raw) if fragments_raw else "(no fragment captured)"
                if tokens_unique:
                    print(f"[row {rowid}] id={neighbor_id} -> synonyms={synonyms_value} ; fragments: {fragments_display}")
                else:
                    print(f"[row {rowid}] id={neighbor_id} -> synonyms=(empty) ; fragments: {fragments_display}")

            # Commit transaction if any updates
            dst_conn.commit()

            # Print summary (English messages inside script)
            print()
            print(f"Done. Updated rows: {updated_rows}.")
            print(f"Skipped rows (no valid neighbor/id): {skipped_no_id}.")
            print(f"Skipped rows (destination id not found): {skipped_not_found}.")
            print(f"Total numeric tokens written to destination (unique count): {total_tokens_inserted}.")
            if invalid_tokens_report:
                print()
                print("Invalid tokens encountered (not written to destination). Examples (src_rowid, neighbor_value, raw_token):")
                for example in invalid_tokens_report[:50]:
                    print(example)
                if len(invalid_tokens_report) > 50:
                    print(f"... and {len(invalid_tokens_report) - 50} more invalid entries.")

            # Additionally, print a consolidated section with all extracted fragments (rowid -> fragments)
            if extracted_fragments_map:
                print()
                print("Extracted fragments per processed row (rowid -> fragments):")
                for rid, frags in extracted_fragments_map.items():
                    print(f"[row {rid}] {' | '.join(frags) if frags else '(no fragment)'}")

        finally:
            dst_conn.close()
    finally:
        src_conn.close()


if __name__ == '__main__':
    main(SRC_DB, DST_DB)

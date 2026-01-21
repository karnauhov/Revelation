#!/usr/bin/env python3
# encoding: utf-8

"""
Fetch pages https://biblehub.com/greek/{n}.htm for n in 1..100,
extract lines like "ἀγαπᾷ — 12 Occ." and convert each to the format:
    "ἀγαπᾷ: [], 12"
Join all lines for a page with newline, and write to SQLite DB.

IMPORTANT: only the 'usage' column is updated for existing rows.
Other columns are left intact.
"""

import requests
from bs4 import BeautifulSoup
import html
import unicodedata
import re
import sqlite3
import os
import sys
from typing import List

# === Configuration ===
BASE_URL = "https://biblehub.com/greek/{n}.htm"
START = 101
END = 5624
DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation.sqlite"
TIMEOUT = 20  # seconds for HTTP requests

# Regex to match lines like: "<word> — 12 Occ."
LINE_RE = re.compile(r'^(?P<word>.+?)\s*[-—–]\s*(?P<count>\d+)\s*Occ\.$', flags=re.UNICODE)

def fetch_page_text(url: str) -> str:
    """Fetch URL and return normalized visible text."""
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    encoding = resp.apparent_encoding or 'utf-8'
    text = resp.content.decode(encoding, errors='replace')
    soup = BeautifulSoup(text, 'html.parser')
    visible = soup.get_text(separator="\n")
    visible = html.unescape(visible)
    visible = unicodedata.normalize('NFC', visible)
    return visible

def extract_usage_lines(visible_text: str) -> List[str]:
    """
    From visible text, find all lines matching the LINE_RE.
    Return list of cleaned strings in the format: 'word: [], count'
    """
    lines = [ln.strip() for ln in visible_text.splitlines() if ln.strip()]
    results = []
    for ln in lines:
        m = LINE_RE.match(ln)
        if m:
            word = m.group('word').strip()
            count = m.group('count').strip()
            formatted = f"{word}: [], {count}"
            results.append(formatted)
    return results

def ensure_db_and_table(conn: sqlite3.Connection):
    """Create table if not exists with appropriate schema (keeps other columns untouched)."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS greek_words (
        id INTEGER PRIMARY KEY,
        usage TEXT
        -- other columns may exist and will be preserved on UPDATE
    )
    """)
    conn.commit()

def write_usage_to_db_preserve(conn: sqlite3.Connection, row_id: int, usage_text: str):
    """
    Safely write only the 'usage' column for given id.
    - If a row with id exists -> UPDATE only the usage column (other columns preserved).
    - If no row -> INSERT new row with id and usage (other columns will be NULL/default).
    """
    cur = conn.cursor()
    try:
        # Check existence
        cur.execute("SELECT 1 FROM greek_words WHERE id = ?", (row_id,))
        exists = cur.fetchone() is not None
        if exists:
            cur.execute("UPDATE greek_words SET usage = ? WHERE id = ?", (usage_text, row_id))
        else:
            cur.execute("INSERT INTO greek_words (id, usage) VALUES (?, ?)", (row_id, usage_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def main():
    # Ensure DB directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.isdir(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception as e:
            print(f"[FATAL] Cannot create DB directory '{db_dir}': {e}", file=sys.stderr)
            return

    # Connect to DB
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"[FATAL] Cannot open SQLite DB at '{DB_PATH}': {e}", file=sys.stderr)
        return

    try:
        ensure_db_and_table(conn)
    except Exception as e:
        print(f"[FATAL] Cannot ensure table exists: {e}", file=sys.stderr)
        conn.close()
        return

    # Loop pages
    for n in range(START, END + 1):
        url = BASE_URL.format(n=n)
        try:
            visible = fetch_page_text(url)
            usage_lines = extract_usage_lines(visible)
            if not usage_lines:
                usage_text = ""
                print(f"[INFO] Page {n}: no matching lines found. Writing empty usage.")
            else:
                usage_text = "\n".join(usage_lines)
                print(f"[WRITE] id={n} ->")
                print(usage_text)
            row_id = int(n)
            write_usage_to_db_preserve(conn, row_id, usage_text)
        except requests.HTTPError as he:
            print(f"[ERROR] HTTP error for page {n} ({url}): {he}")
        except requests.RequestException as rexc:
            print(f"[ERROR] Network error for page {n} ({url}): {rexc}")
        except sqlite3.Error as db_e:
            print(f"[ERROR] SQLite error while processing page {n}: {db_e}")
        except Exception as exc:
            print(f"[ERROR] Unexpected error for page {n}: {exc}")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import grouped records from JSON files into greek_descs table."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_uk.sqlite"
DEFAULT_IN_DIR = r"C:\Users\karna\Downloads\Revelation\ukr"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import records from JSON files into greek_descs table "
            "(columns: id, desc) using upsert by id."
        )
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--in-dir",
        default=DEFAULT_IN_DIR,
        help=f"Directory with JSON files (default: {DEFAULT_IN_DIR})",
    )
    parser.add_argument(
        "--glob",
        default="*.json",
        help="File mask for JSON files (default: *.json)",
    )
    return parser.parse_args()


def _normalize_id(value: object, source: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ValueError(f"Invalid id in {source}: {value!r}")


def _normalize_desc(value: object, source: str) -> str:
    if isinstance(value, str):
        return value
    raise ValueError(f"Invalid desc in {source}: expected string, got {type(value).__name__}")


def read_records(in_dir: Path, glob_pattern: str) -> tuple[list[tuple[int, str]], int, int, int]:
    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")

    files = sorted(in_dir.glob(glob_pattern))
    if not files:
        raise FileNotFoundError(f"No JSON files found in {in_dir} by pattern {glob_pattern!r}")

    by_id: dict[int, str] = {}
    total_objects = 0
    duplicate_ids = 0

    for file_path in files:
        with file_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)

        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {file_path}")

        for index, item in enumerate(payload, start=1):
            total_objects += 1
            source = f"{file_path}#{index}"

            if not isinstance(item, dict):
                raise ValueError(f"Expected object in {source}")
            if "id" not in item or "desc" not in item:
                raise ValueError(f"Missing required keys in {source}: expected id and desc")

            record_id = _normalize_id(item["id"], source)
            record_desc = _normalize_desc(item["desc"], source)

            if record_id in by_id:
                duplicate_ids += 1
            by_id[record_id] = record_desc

    records = sorted(by_id.items(), key=lambda x: x[0])
    return records, len(files), total_objects, duplicate_ids


def upsert_records(conn: sqlite3.Connection, records: list[tuple[int, str]]) -> tuple[int, int, int]:
    before_count = conn.execute('SELECT COUNT(*) FROM greek_descs').fetchone()[0]

    conn.executemany(
        '''
        INSERT INTO greek_descs (id, "desc")
        VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET
            "desc" = excluded."desc"
        ''',
        records,
    )

    after_count = conn.execute('SELECT COUNT(*) FROM greek_descs').fetchone()[0]
    inserted = after_count - before_count
    updated_existing = len(records) - inserted
    return inserted, updated_existing, after_count


def main() -> None:
    args = parse_args()
    db_path = Path(args.db)
    in_dir = Path(args.in_dir)

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    records, files_count, total_objects, duplicate_ids = read_records(in_dir, args.glob)

    with sqlite3.connect(str(db_path)) as conn:
        inserted, updated_existing, final_table_count = upsert_records(conn, records)
        conn.commit()

    print(f"FILES_PROCESSED={files_count}")
    print(f"OBJECTS_READ={total_objects}")
    print(f"UNIQUE_OBJECTS_BY_ID={len(records)}")
    print(f"DUPLICATE_IDS_OVERRIDDEN={duplicate_ids}")
    print(f"INSERTED={inserted}")
    print(f"UPDATED_EXISTING={updated_existing}")
    print(f"TABLE_ROWS_AFTER={final_table_count}")


if __name__ == "__main__":
    main()

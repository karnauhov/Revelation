from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

DB_METADATA_TABLE_NAME = "db_metadata"
DB_METADATA_SCHEMA_VERSION_KEY = "schema_version"
DB_METADATA_DATA_VERSION_KEY = "data_version"
DB_METADATA_DATE_KEY = "date"


def build_web_db_manifest_version_token(
    *,
    schema_version: int,
    data_version: int,
    date_iso: str,
    file_size_bytes: int | None = None,
) -> str:
    parts = [
        f"schema:{schema_version}",
        f"data:{data_version}",
        f"date:{date_iso}",
    ]
    if file_size_bytes is not None:
        parts.append(f"size:{file_size_bytes}")
    return f"manifest:{'|'.join(parts)}"


def read_web_db_manifest_entry(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"Файл БД не найден: {db_path}")

    connection = sqlite3.connect(str(db_path))
    try:
        metadata_values = _read_db_metadata_values(connection)
        schema_version = _read_schema_version(connection, metadata_values)
    finally:
        connection.close()

    data_version = _parse_required_int(
        metadata_values.get(DB_METADATA_DATA_VERSION_KEY),
        db_path=db_path,
        key=DB_METADATA_DATA_VERSION_KEY,
    )
    date_iso = _parse_required_text(
        metadata_values.get(DB_METADATA_DATE_KEY),
        db_path=db_path,
        key=DB_METADATA_DATE_KEY,
    )

    file_size_bytes = int(db_path.stat().st_size)
    return {
        "versionToken": build_web_db_manifest_version_token(
            schema_version=schema_version,
            data_version=data_version,
            date_iso=date_iso,
            file_size_bytes=file_size_bytes,
        ),
        "schemaVersion": schema_version,
        "dataVersion": data_version,
        "date": date_iso,
        "fileSizeBytes": file_size_bytes,
    }


def build_web_db_manifest_payload_from_paths(
    db_paths: Iterable[Path],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    for db_path in sorted((Path(path) for path in db_paths), key=lambda path: path.name):
        entries[db_path.name] = read_web_db_manifest_entry(db_path)

    return {
        "version": 1,
        "generatedAt": generated_at or _now_iso(),
        "databases": entries,
    }


def write_web_db_manifest(
    manifest_path: Path,
    *,
    db_paths: Iterable[Path],
    generated_at: str | None = None,
) -> Path:
    payload = build_web_db_manifest_payload_from_paths(
        db_paths,
        generated_at=generated_at,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def _read_schema_version(
    connection: sqlite3.Connection,
    metadata_values: dict[str, str],
) -> int:
    schema_value = metadata_values.get(DB_METADATA_SCHEMA_VERSION_KEY)
    if schema_value is not None:
        return _parse_required_int(
            schema_value,
            db_path=None,
            key=DB_METADATA_SCHEMA_VERSION_KEY,
        )

    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0] or 0)
    if user_version > 0:
        return user_version

    raise ValueError("В БД отсутствует schema_version и PRAGMA user_version.")


def _read_db_metadata_values(connection: sqlite3.Connection) -> dict[str, str]:
    if not _table_exists(connection, DB_METADATA_TABLE_NAME):
        return {}

    rows = connection.execute(
        f"""
        SELECT key, value
        FROM {DB_METADATA_TABLE_NAME}
        WHERE key IN (?, ?, ?)
        """,
        (
            DB_METADATA_SCHEMA_VERSION_KEY,
            DB_METADATA_DATA_VERSION_KEY,
            DB_METADATA_DATE_KEY,
        ),
    ).fetchall()
    return {str(key): str(value) for key, value in rows}


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _parse_required_int(
    value: str | None,
    *,
    db_path: Path | None,
    key: str,
) -> int:
    if value is None or not str(value).strip().isdigit():
        raise ValueError(_format_missing_metadata_message(db_path=db_path, key=key))
    return int(str(value).strip())


def _parse_required_text(
    value: str | None,
    *,
    db_path: Path | None,
    key: str,
) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(_format_missing_metadata_message(db_path=db_path, key=key))
    return text


def _format_missing_metadata_message(*, db_path: Path | None, key: str) -> str:
    target_name = db_path.name if db_path is not None else "БД"
    return f"В {target_name} отсутствует корректное значение db_metadata.{key}."

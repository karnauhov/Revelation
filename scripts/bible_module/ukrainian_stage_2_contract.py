from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
from pathlib import Path
from typing import Any

from .ukrainian_strong import strong_contract_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGE_2_REPORT_DIR = (
    PROJECT_ROOT
    / "scripts"
    / "bible_module"
    / "reports"
    / "ukrainian_stage_2_20260801"
)
DEFAULT_REFERENCE_DB_PATH = PROJECT_ROOT / "web" / "db" / "bible_kjv.sqlite"
DEFAULT_LEGACY_LXX_TR_DB_PATH = (
    PROJECT_ROOT / "web" / "db" / "bible_lxx_tr.sqlite"
)
DEFAULT_VERSE_MAP_PATH = (
    PROJECT_ROOT / "assets" / "data" / "bible_verse_map.json"
)
DEFAULT_BASELINE_PATH = STAGE_2_REPORT_DIR / "baseline_manifest.json"
DEFAULT_IDENTIFIERS_PATH = STAGE_2_REPORT_DIR / "final_identifiers.csv"

STAGE_2_GENERATED_ON = "2026-08-01"
LEGACY_APPLICATION_SCHEMA_VERSION = 3
UKRAINIAN_APPLICATION_SCHEMA_VERSION = 4
TARGET_BOOKS_COUNT = 66
TARGET_CHAPTERS_COUNT = 1189
TARGET_VERSES_COUNT = 31_102
TARGET_VERSE_KEYS_COUNT = 31_102

MODULE_FILENAME = "bible_ohienko_1988.sqlite"
MODULE_ID = "ohienko_1988"
MODULE_CODE = "OH1988"
MODULE_LANGUAGE = "uk"
MODULE_TITLE = "Біблія Огієнка (ювілейне видання 1988 року)"
TRANSLATION_TITLE = (
    "Біблія або Книги Святого Письма Старого і Нового Заповіту, "
    "переклад Івана Огієнка"
)
EDITION = "ювілейне видання 1988 року"
CANON = "protestant_66"
TARGET_VERSIFICATION = "kjv_protestant"
DERIVATIVE_LICENSE = (
    "Creative Commons Attribution-ShareAlike 4.0 International"
)
DERIVATIVE_LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

INFO_DESCRIPTION = (
    "Біблія або Книги Святого Письма Старого і Нового Заповіту, "
    "переклад Івана Огієнка; ювілейне видання 1988 року. Повний "
    "66-книжний Старий і Новий Завіти. Посилання модуля подано в "
    "цільовій KJV/протестантській версифікації Revelation; вони можуть "
    "відрізнятися від нумерації друкованого видання, а відповідність "
    "збережено у відтворюваній карті проєкції."
)
INFO_LICENSE = (
    "Текст і друковані виноски ювілейного видання перекладу Івана "
    "Огієнка 1988 року та похідний текстовий/Strong-модуль ліцензовано "
    "за Creative Commons "
    "Attribution-ShareAlike 4.0 International (CC BY-SA 4.0): "
    "https://creativecommons.org/licenses/by-sa/4.0/. Автор перекладу: "
    "Іван Огієнко. Дозвіл на видання до 1991 року надано Українським "
    "Біблійним Товариством; Wikimedia VRT ticket 2013112610015211. "
    "Зміни: технічна нормалізація, токенізація, явна реверсифікація, "
    "структурування друкованих виносок і додавання Strong. Пізніші "
    "редакції й правки УБТ після 1990 року не включено. Атрибуція не "
    "означає схвалення модуля УБТ, Wikimedia або Wikisource."
)
INFO_SOURCE_SUMMARY_TEMPLATE = (
    "Базовий текст і друковані виноски: закріплені ревізії Українських "
    "Вікіджерел для "
    "точного ювілейного видання 1988 року "
    "({wikisource_revision_lock}), звірені зі сканом Wikimedia Commons "
    "SHA-256 {commons_scan_sha256} та залежним контрольним сканом "
    "Internet Archive SHA-256 "
    "39d34d366554a2c798e180d0fce05a4ca11fc8c10901c174848e37f30468cee8. "
    "Strong створено як похідне послівне вирівнювання: STEPBible "
    "TAHOT/TAGNT commit b9dcc831a98e0fd6f3c7e122be9ff68377c310c0 — "
    "основний Hebrew OT/Greek NT ланцюжок; Open Scriptures Hebrew Bible "
    "v.2.2 commit 6a5db284c715c18b239422e57bb89684e6a19f00 — "
    "залежна OT-перевірка; Tanach.us UXLC 2.5 (27.6), April 2026 — "
    "незалежний OT-контроль поверхні й меж; unfoldingWord UGNT v0.34 "
    "commit fc95b2b8aad08bb65ab54628ab685413a1139e97 — незалежний "
    "NT Strong-контроль; CrossWire KJV 3.1 commit "
    "d490be7e34762deb2c76cb2c1306d4808e27890d — лише додатковий "
    "classic-Strong аудит. Жоден контрольний текст не замінює український "
    "текст видання 1988 року."
)
INFO_SOURCE_SUMMARY_PLACEHOLDERS = (
    "commons_scan_sha256",
    "wikisource_revision_lock",
)

FINAL_IDENTIFIERS: dict[str, object] = {
    "filename": MODULE_FILENAME,
    "module_id": MODULE_ID,
    "code": MODULE_CODE,
    "language": MODULE_LANGUAGE,
    "title": MODULE_TITLE,
    "translation": TRANSLATION_TITLE,
    "edition": EDITION,
    "canon": CANON,
    "target_versification": TARGET_VERSIFICATION,
    "schema_version": UKRAINIAN_APPLICATION_SCHEMA_VERSION,
    "target_books": TARGET_BOOKS_COUNT,
    "target_chapters": TARGET_CHAPTERS_COUNT,
    "target_verses": TARGET_VERSES_COUNT,
    "target_verse_keys": TARGET_VERSE_KEYS_COUNT,
}

_IDENTIFIER_RATIONALES = {
    "filename": "Имя следует из точного перевода и года, а не из общего языка.",
    "module_id": "Стабильный lowercase ID точного издания.",
    "code": "Короткий уникальный пользовательский код точного издания.",
    "language": "BCP 47/ISO 639-1 код украинского языка.",
    "title": "Краткое отображаемое название с годом точной редакции.",
    "translation": "Полное название утверждённого перевода.",
    "edition": "Утверждённое владельцем точное юбилейное издание.",
    "canon": "Полный протестантский канон из 66 книг.",
    "target_versification": "Зафиксированная KJV/протестантская сетка приложения.",
    "schema_version": (
        "Целевая прикладная схема украинского модуля с отдельным comment; "
        "legacy KJV/LXX_TR остаются на версии 3."
    ),
    "target_books": "Количество книг целевого эталона.",
    "target_chapters": "Количество глав целевого эталона.",
    "target_verses": "Количество стиховых позиций целевого эталона.",
    "target_verse_keys": "Количество уникальных упорядоченных ключей.",
}


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_lines(values: list[str]) -> str:
    payload = "".join(f"{value}\n" for value in values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _base36(number: int) -> str:
    if number <= 0:
        raise ValueError(f"base36 requires a positive integer, got {number}")
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    value = number
    characters: list[str] = []
    while value:
        value, remainder = divmod(value, 36)
        characters.append(alphabet[remainder])
    return "".join(reversed(characters))


def _schema_snapshot(connection: sqlite3.Connection) -> dict[str, object]:
    tables: dict[str, object] = {}
    rows = connection.execute(
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()
    for table_name, table_sql in rows:
        columns = [
            {
                "cid": int(row[0]),
                "name": str(row[1]),
                "type": str(row[2]),
                "not_null": bool(row[3]),
                "default": row[4],
                "primary_key_position": int(row[5]),
            }
            for row in connection.execute(
                f'PRAGMA table_info("{str(table_name)}")'
            ).fetchall()
        ]
        tables[str(table_name)] = {
            "sql": str(table_sql),
            "columns": columns,
        }
    snapshot = {"tables": tables}
    snapshot["fingerprint_sha256"] = _canonical_json_sha256(snapshot)
    return snapshot


def schema_snapshot(connection: sqlite3.Connection) -> dict[str, object]:
    """Return the deterministic application-schema snapshot used by tests."""

    return _schema_snapshot(connection)


def build_ukrainian_schema_contract() -> dict[str, object]:
    """Build the exact schema-only contract for the future Ukrainian DB."""

    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            "PRAGMA user_version = 4;\n\n"
            "CREATE TABLE db_metadata (\n"
            "  key TEXT PRIMARY KEY,\n"
            "  value TEXT NOT NULL\n"
            ") WITHOUT ROWID;\n\n"
            "CREATE TABLE info (\n"
            "  code TEXT PRIMARY KEY,\n"
            "  module_id TEXT NOT NULL UNIQUE,\n"
            "  title TEXT NOT NULL,\n"
            "  description TEXT NOT NULL,\n"
            "  language TEXT NOT NULL,\n"
            "  canon TEXT NOT NULL,\n"
            "  versification TEXT NOT NULL,\n"
            "  license TEXT NOT NULL,\n"
            "  source_summary TEXT NOT NULL,\n"
            "  CHECK (length(trim(code)) > 0),\n"
            "  CHECK (length(trim(module_id)) > 0)\n"
            ") WITHOUT ROWID;\n\n"
            "CREATE TABLE verses (\n"
            "  verse_key TEXT NOT NULL PRIMARY KEY CHECK(length(verse_key) = 3),\n"
            "  text TEXT NOT NULL DEFAULT '',\n"
            "  comment TEXT NOT NULL DEFAULT ''\n"
            ") WITHOUT ROWID;\n\n"
            "INSERT INTO db_metadata(key, value)\n"
            "VALUES ('schema_version', '4');\n"
        )
        pragma_user_version = int(
            connection.execute("PRAGMA user_version").fetchone()[0]
        )
        metadata_schema_version = str(
            connection.execute(
                "SELECT value FROM db_metadata WHERE key = 'schema_version'"
            ).fetchone()[0]
        )
        schema = _schema_snapshot(connection)
    finally:
        connection.close()

    return {
        "profile_id": "ukrainian_module_v4",
        "schema_version": UKRAINIAN_APPLICATION_SCHEMA_VERSION,
        "pragma_user_version": pragma_user_version,
        "db_metadata_schema_version": metadata_schema_version,
        "comment_column_supported": True,
        "schema": schema,
    }


def validate_schema_contracts(
    *,
    legacy_kjv: dict[str, object],
    legacy_lxx_tr: dict[str, object],
    ukrainian_target: dict[str, object],
) -> None:
    """Fail closed if legacy v3 and Ukrainian v4 schema profiles are mixed."""

    for module_name, legacy in (
        ("KJV", legacy_kjv),
        ("LXX_TR", legacy_lxx_tr),
    ):
        if legacy.get("pragma_user_version") != LEGACY_APPLICATION_SCHEMA_VERSION:
            raise ValueError(f"Legacy {module_name} PRAGMA user_version changed")
        metadata = legacy.get("db_metadata")
        if not isinstance(metadata, dict) or metadata.get("schema_version") != str(
            LEGACY_APPLICATION_SCHEMA_VERSION
        ):
            raise ValueError(
                f"Legacy {module_name} db_metadata.schema_version changed"
            )
        schema = legacy.get("schema")
        if not isinstance(schema, dict):
            raise ValueError(f"Legacy {module_name} schema is invalid")
        tables = schema.get("tables")
        verses = tables.get("verses") if isinstance(tables, dict) else None
        columns = verses.get("columns") if isinstance(verses, dict) else None
        if not isinstance(columns, list):
            raise ValueError(f"Legacy {module_name} verses schema is invalid")
        if [column.get("name") for column in columns] != ["verse_key", "text"]:
            raise ValueError(
                f"Legacy {module_name} must remain schema version 3 without comment"
            )

    if legacy_kjv.get("schema") != legacy_lxx_tr.get("schema"):
        raise ValueError("Legacy KJV/LXX_TR application schemas diverged")

    if ukrainian_target.get("schema_version") != UKRAINIAN_APPLICATION_SCHEMA_VERSION:
        raise ValueError("Ukrainian target schema_version must be 4")
    if (
        ukrainian_target.get("pragma_user_version")
        != UKRAINIAN_APPLICATION_SCHEMA_VERSION
    ):
        raise ValueError("Ukrainian target PRAGMA user_version must be 4")
    if ukrainian_target.get("db_metadata_schema_version") != str(
        UKRAINIAN_APPLICATION_SCHEMA_VERSION
    ):
        raise ValueError("Ukrainian target db_metadata.schema_version must be '4'")
    if ukrainian_target.get("comment_column_supported") is not True:
        raise ValueError("Ukrainian target must support verse comments")

    target_schema = ukrainian_target.get("schema")
    if not isinstance(target_schema, dict):
        raise ValueError("Ukrainian target schema is invalid")
    target_tables = target_schema.get("tables")
    target_verses = (
        target_tables.get("verses") if isinstance(target_tables, dict) else None
    )
    target_columns = (
        target_verses.get("columns") if isinstance(target_verses, dict) else None
    )
    if not isinstance(target_columns, list):
        raise ValueError("Ukrainian target verses schema is invalid")
    expected_columns = [
        {
            "cid": 0,
            "name": "verse_key",
            "type": "TEXT",
            "not_null": True,
            "default": None,
            "primary_key_position": 1,
        },
        {
            "cid": 1,
            "name": "text",
            "type": "TEXT",
            "not_null": True,
            "default": "''",
            "primary_key_position": 0,
        },
        {
            "cid": 2,
            "name": "comment",
            "type": "TEXT",
            "not_null": True,
            "default": "''",
            "primary_key_position": 0,
        },
    ]
    if target_columns != expected_columns:
        raise ValueError(
            "Ukrainian verses columns must be exactly "
            "verse_key, text, comment TEXT NOT NULL DEFAULT ''"
        )
    expected_verses_sql = (
        "CREATE TABLE verses (\n"
        "  verse_key TEXT NOT NULL PRIMARY KEY CHECK(length(verse_key) = 3),\n"
        "  text TEXT NOT NULL DEFAULT '',\n"
        "  comment TEXT NOT NULL DEFAULT ''\n"
        ") WITHOUT ROWID"
    )
    if target_verses.get("sql") != expected_verses_sql:
        raise ValueError("Ukrainian verses SQL contract changed")


def _read_reference_database(path: Path) -> dict[str, object]:
    resolved_path = path.resolve()
    connection = sqlite3.connect(
        f"{resolved_path.as_uri()}?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only=ON")
        integrity_check = str(
            connection.execute("PRAGMA integrity_check").fetchone()[0]
        )
        user_version = int(
            connection.execute("PRAGMA user_version").fetchone()[0]
        )
        metadata = {
            str(row["key"]): str(row["value"])
            for row in connection.execute(
                "SELECT key, value FROM db_metadata ORDER BY key"
            )
        }
        info_row = connection.execute(
            """
            SELECT code,
                   module_id,
                   title,
                   description,
                   language,
                   canon,
                   versification,
                   license,
                   source_summary
            FROM info
            """
        ).fetchall()
        if len(info_row) != 1:
            raise ValueError("Bible module info table must contain one row")
        verse_keys = [
            str(row[0])
            for row in connection.execute(
                "SELECT verse_key FROM verses ORDER BY verse_key"
            )
        ]
        nonempty_verses = int(
            connection.execute(
                "SELECT COUNT(*) FROM verses WHERE length(trim(text)) > 0"
            ).fetchone()[0]
        )
        schema = _schema_snapshot(connection)
    finally:
        connection.close()

    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "filename": path.name,
        "bytes": resolved_path.stat().st_size,
        "sha256": _sha256_path(resolved_path),
        "integrity_check": integrity_check,
        "pragma_user_version": user_version,
        "db_metadata": metadata,
        "info": dict(info_row[0]),
        "schema": schema,
        "verse_rows": len(verse_keys),
        "nonempty_verse_rows": nonempty_verses,
        "verse_keys": verse_keys,
    }


def _read_target_grid(verse_map_path: Path) -> dict[str, object]:
    payload = json.loads(verse_map_path.read_text(encoding="utf-8"))
    books = payload.get("books")
    if not isinstance(books, list):
        raise ValueError("Bible verse map must contain a books array")

    references: list[str] = []
    chapters_count = 0
    normalized_books: list[dict[str, object]] = []
    for raw_book in books:
        if not isinstance(raw_book, dict):
            raise ValueError("Bible verse map book must be an object")
        book_id = int(raw_book["id"])
        code = str(raw_book["code"])
        chapters = [int(value) for value in raw_book["chapters"]]
        chapters_count += len(chapters)
        normalized_books.append(
            {"id": book_id, "code": code, "chapters": chapters}
        )
        for chapter, verse_count in enumerate(chapters, start=1):
            for verse in range(1, verse_count + 1):
                references.append(f"{code}.{chapter}.{verse}")

    verse_keys = [
        _base36(ordinal).rjust(3, "0")
        for ordinal in range(1, len(references) + 1)
    ]
    pairs = [
        f"{verse_key}\t{reference}"
        for verse_key, reference in zip(verse_keys, references, strict=True)
    ]
    return {
        "verse_map_path": verse_map_path.relative_to(PROJECT_ROOT).as_posix(),
        "verse_map_sha256": _sha256_path(verse_map_path),
        "verse_map_schema_version": int(payload["schema_version"]),
        "canon": str(payload["canon"]),
        "versification": str(payload["versification"]),
        "books_count": len(normalized_books),
        "chapters_count": chapters_count,
        "verses_count": len(references),
        "verse_keys_count": len(verse_keys),
        "verse_key_format": payload["verse_key_format"],
        "books": normalized_books,
        "verse_keys": verse_keys,
        "verse_key_sequence_sha256": _sha256_lines(verse_keys),
        "canonical_reference_sequence_sha256": _sha256_lines(references),
        "verse_key_reference_pair_sequence_sha256": _sha256_lines(pairs),
    }


def _validate_baseline_inputs(
    reference_database: dict[str, object],
    legacy_lxx_tr_database: dict[str, object],
    target_grid: dict[str, object],
    ukrainian_schema_contract: dict[str, object],
) -> None:
    if reference_database["integrity_check"] != "ok":
        raise ValueError("Reference KJV database integrity_check failed")
    if legacy_lxx_tr_database["integrity_check"] != "ok":
        raise ValueError("Legacy LXX_TR database integrity_check failed")
    if (
        reference_database["pragma_user_version"]
        != LEGACY_APPLICATION_SCHEMA_VERSION
    ):
        raise ValueError("Reference KJV PRAGMA user_version changed")
    metadata = reference_database["db_metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("Reference KJV db_metadata is invalid")
    if metadata.get("schema_version") != str(LEGACY_APPLICATION_SCHEMA_VERSION):
        raise ValueError("Reference KJV db_metadata.schema_version changed")
    info = reference_database["info"]
    if not isinstance(info, dict):
        raise ValueError("Reference KJV info row is invalid")
    if info.get("canon") != CANON:
        raise ValueError("Reference KJV canon changed")
    if info.get("versification") != TARGET_VERSIFICATION:
        raise ValueError("Reference KJV versification changed")
    if target_grid["canon"] != CANON:
        raise ValueError("Application verse map canon changed")
    if target_grid["versification"] != TARGET_VERSIFICATION:
        raise ValueError("Application verse map versification changed")

    expected_counts = (
        TARGET_BOOKS_COUNT,
        TARGET_CHAPTERS_COUNT,
        TARGET_VERSES_COUNT,
        TARGET_VERSE_KEYS_COUNT,
    )
    actual_counts = (
        target_grid["books_count"],
        target_grid["chapters_count"],
        target_grid["verses_count"],
        target_grid["verse_keys_count"],
    )
    if actual_counts != expected_counts:
        raise ValueError(
            f"Application target-grid counts changed: {actual_counts}"
        )
    if reference_database["verse_rows"] != TARGET_VERSES_COUNT:
        raise ValueError("Reference KJV verse row count changed")
    if reference_database["nonempty_verse_rows"] != TARGET_VERSES_COUNT:
        raise ValueError("Reference KJV contains empty verse rows")
    if reference_database["verse_keys"] != target_grid["verse_keys"]:
        raise ValueError(
            "Reference KJV verse_key sequence differs from the application map"
        )
    if legacy_lxx_tr_database["verse_rows"] != TARGET_VERSES_COUNT:
        raise ValueError("Legacy LXX_TR verse row count changed")
    if legacy_lxx_tr_database["verse_keys"] != target_grid["verse_keys"]:
        raise ValueError(
            "Legacy LXX_TR verse_key sequence differs from the application map"
        )
    lxx_info = legacy_lxx_tr_database["info"]
    if not isinstance(lxx_info, dict):
        raise ValueError("Legacy LXX_TR info row is invalid")
    if lxx_info.get("canon") != CANON:
        raise ValueError("Legacy LXX_TR canon changed")
    if lxx_info.get("versification") != TARGET_VERSIFICATION:
        raise ValueError("Legacy LXX_TR versification changed")
    validate_schema_contracts(
        legacy_kjv=reference_database,
        legacy_lxx_tr=legacy_lxx_tr_database,
        ukrainian_target=ukrainian_schema_contract,
    )


def build_baseline_manifest(
    *,
    reference_db_path: Path = DEFAULT_REFERENCE_DB_PATH,
    legacy_lxx_tr_db_path: Path = DEFAULT_LEGACY_LXX_TR_DB_PATH,
    verse_map_path: Path = DEFAULT_VERSE_MAP_PATH,
    generated_on: str = STAGE_2_GENERATED_ON,
) -> dict[str, object]:
    reference_database = _read_reference_database(reference_db_path)
    legacy_lxx_tr_database = _read_reference_database(legacy_lxx_tr_db_path)
    target_grid = _read_target_grid(verse_map_path)
    ukrainian_schema_contract = build_ukrainian_schema_contract()
    _validate_baseline_inputs(
        reference_database,
        legacy_lxx_tr_database,
        target_grid,
        ukrainian_schema_contract,
    )
    reference_database.pop("verse_keys")
    legacy_lxx_tr_database.pop("verse_keys")

    return {
        "schema_version": 1,
        "stage": 2,
        "status": "stage_2_complete_target_locked",
        "generated_on": generated_on,
        "selection": {
            "translation": TRANSLATION_TITLE,
            "edition": EDITION,
            "scope": (
                "Полный 66-книжный Ветхий и Новый Заветы; точный текст "
                "юбилейного издания 1988 года."
            ),
            "license": DERIVATIVE_LICENSE,
            "license_url": DERIVATIVE_LICENSE_URL,
            "restriction": (
                "Запрещено смешивать текст с редакциями и правками УБТ "
                "после 1990 года."
            ),
        },
        "final_module": {
            **FINAL_IDENTIFIERS,
            "info_description": INFO_DESCRIPTION,
            "info_license": INFO_LICENSE,
            "info_source_summary_template": INFO_SOURCE_SUMMARY_TEMPLATE,
            "info_source_summary_placeholders": list(
                INFO_SOURCE_SUMMARY_PLACEHOLDERS
            ),
        },
        "schema_contracts": {
            "legacy_v3": {
                "profile_id": "legacy_modules_v3",
                "schema_version": LEGACY_APPLICATION_SCHEMA_VERSION,
                "pragma_user_version": LEGACY_APPLICATION_SCHEMA_VERSION,
                "db_metadata_schema_version": str(
                    LEGACY_APPLICATION_SCHEMA_VERSION
                ),
                "comment_column_supported": False,
                "shared_schema": reference_database["schema"],
                "databases": {
                    "kjv": {
                        "filename": reference_database["filename"],
                        "sha256": reference_database["sha256"],
                        "bytes": reference_database["bytes"],
                        "info_code": reference_database["info"]["code"],
                        "module_id": reference_database["info"]["module_id"],
                        "verse_rows": reference_database["verse_rows"],
                    },
                    "lxx_tr": {
                        "filename": legacy_lxx_tr_database["filename"],
                        "sha256": legacy_lxx_tr_database["sha256"],
                        "bytes": legacy_lxx_tr_database["bytes"],
                        "info_code": legacy_lxx_tr_database["info"]["code"],
                        "module_id": legacy_lxx_tr_database["info"]["module_id"],
                        "verse_rows": legacy_lxx_tr_database["verse_rows"],
                    },
                },
            },
            "ukrainian_v4": ukrainian_schema_contract,
        },
        "target_fit_decision": {
            "result": "kjv_protestant_approved",
            "basis": (
                "The approved edition and target share the same ordered "
                "66-book canon. Source segmentation remains explicit in the "
                "intermediate model; 1:1, merge, split, and contiguous range "
                "rules preserve ordered canonical plain text, while paratext "
                "is retained with an explicit disposition."
            ),
            "losslessness_invariant": (
                "Every accepted source Unicode scalar and every resolved "
                "Strong relation is consumed exactly once by a target segment "
                "or by a versioned outside-grid paratext record."
            ),
            "stage_5_gate": (
                "The exhaustive source-to-target map must prove the invariant "
                "for every record; failure reopens stage 2 and blocks building."
            ),
        },
        "reference_database": reference_database,
        "legacy_lxx_tr_database": legacy_lxx_tr_database,
        "target_grid": target_grid,
        "strong_contract": strong_contract_manifest(),
    }


def render_baseline_manifest(manifest: dict[str, object]) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def render_final_identifiers_csv() -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("field", "value", "rationale"))
    for field, value in FINAL_IDENTIFIERS.items():
        writer.writerow((field, value, _IDENTIFIER_RATIONALES[field]))
    return output.getvalue()


def write_stage_2_evidence(
    *,
    reference_db_path: Path = DEFAULT_REFERENCE_DB_PATH,
    legacy_lxx_tr_db_path: Path = DEFAULT_LEGACY_LXX_TR_DB_PATH,
    verse_map_path: Path = DEFAULT_VERSE_MAP_PATH,
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    identifiers_path: Path = DEFAULT_IDENTIFIERS_PATH,
    generated_on: str = STAGE_2_GENERATED_ON,
) -> dict[str, object]:
    manifest = build_baseline_manifest(
        reference_db_path=reference_db_path,
        legacy_lxx_tr_db_path=legacy_lxx_tr_db_path,
        verse_map_path=verse_map_path,
        generated_on=generated_on,
    )
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(
        render_baseline_manifest(manifest),
        encoding="utf-8",
        newline="\n",
    )
    identifiers_path.write_text(
        render_final_identifiers_csv(),
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def load_baseline_manifest(
    path: Path = DEFAULT_BASELINE_PATH,
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Stage-2 baseline manifest must be a JSON object")
    return value

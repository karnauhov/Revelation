from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .canon import CANON_NAME
from .fetch_sources import load_manifest, verify_source_manifest
from .lxx import (
    CROSSWIRE_LXX_SOURCE_ID,
    CROSSWIRE_LXX_SOURCE_TEXT_ID,
    LxxImportResult,
    build_lxx_import_result_from_zip,
)
from .schema import (
    BIBLE_MODULE_DATA_VERSION_INITIAL,
    BIBLE_MODULE_SCHEMA_VERSION,
    assert_no_form_occurrence_tables,
    create_bible_module_schema,
    now_utc_iso,
    table_names,
)
from .sources import DEFAULT_SOURCE_LOCK_PATH
from .tagnt import (
    TAGNT_SOURCE_ID,
    TAGNT_SOURCE_TEXT_ID,
    TagntModuleVerse,
    build_na28_module_verses,
    iter_na28_tagnt_tokens,
)

MODULE_ID = "na28_lxx"
MODULE_CODE = "NA28_LXX"
DEFAULT_TARGET_PATH = (
    Path.home() / "Documents" / "revelation" / "db" / "bible_na28_lxx.sqlite"
)

TAGNT_LOCKED_SOURCE_IDS = ("step_tagnt_mat_jhn", "step_tagnt_act_rev")
SUPPORTING_LOCKED_SOURCE_IDS = (
    "step_tbesg",
    "step_tflsj_0_5624",
    "step_tflsj_extra",
    "step_tegmc",
)
REQUIRED_LOCKED_SOURCE_IDS = (
    *TAGNT_LOCKED_SOURCE_IDS,
    *SUPPORTING_LOCKED_SOURCE_IDS,
    CROSSWIRE_LXX_SOURCE_ID,
)

INSERT_MODULE_VERSE_SQL = """
INSERT INTO module_verses(
  module_verse_id,
  source_text_id,
  native_ref,
  book_id,
  chapter,
  verse,
  subverse,
  text_plain,
  text_display,
  tokens_count,
  sort_key
)
VALUES(
  :module_verse_id,
  :source_text_id,
  :native_ref,
  :book_id,
  :chapter,
  :verse,
  :subverse,
  :text_plain,
  :text_display,
  :tokens_count,
  :sort_key
)
"""

INSERT_MODULE_VERSE_LINK_SQL = """
INSERT INTO module_verse_links(
  module_verse_id,
  canonical_verse_id,
  link_kind,
  note
)
VALUES(
  :module_verse_id,
  :canonical_verse_id,
  :link_kind,
  :note
)
"""

INSERT_TOKEN_SQL = """
INSERT INTO tokens(
  token_id,
  module_verse_id,
  source_text_id,
  token_order,
  source_ref,
  text_type,
  surface,
  surface_normalized,
  surface_search,
  transliteration,
  lemma,
  morphology,
  gloss,
  raw_json
)
VALUES(
  :token_id,
  :module_verse_id,
  :source_text_id,
  :token_order,
  :source_ref,
  :text_type,
  :surface,
  :surface_normalized,
  :surface_search,
  :transliteration,
  :lemma,
  :morphology,
  :gloss,
  :raw_json
)
"""

INSERT_TOKEN_STRONG_SQL = """
INSERT INTO token_strongs(
  token_id,
  strong,
  raw_strong,
  role,
  segment_order,
  segment_surface,
  is_primary
)
VALUES(
  :token_id,
  :strong,
  :raw_strong,
  :role,
  :segment_order,
  :segment_surface,
  :is_primary
)
"""


@dataclass(frozen=True)
class BibleModuleBuildReport:
    target_path: Path
    backup_path: Path | None
    module_verses_count: int
    tokens_count: int
    token_strongs_count: int
    import_warnings_count: int
    built_at: str


def build_na28_lxx_module(
    *,
    target_path: Path = DEFAULT_TARGET_PATH,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    data_version: int = BIBLE_MODULE_DATA_VERSION_INITIAL,
    built_at: str | None = None,
) -> BibleModuleBuildReport:
    manifest = _load_verified_manifest(manifest_path)
    source_entries = _source_entries_by_id(manifest)
    source_paths = _source_paths_by_id(manifest, manifest_path)

    tagnt_paths = [source_paths[source_id] for source_id in TAGNT_LOCKED_SOURCE_IDS]
    nt_verses = build_na28_module_verses(iter_na28_tagnt_tokens(tagnt_paths))
    lxx_result = build_lxx_import_result_from_zip(source_paths[CROSSWIRE_LXX_SOURCE_ID])
    return build_na28_lxx_module_from_imports(
        target_path=target_path,
        source_entries=source_entries,
        nt_verses=nt_verses,
        lxx_result=lxx_result,
        data_version=data_version,
        built_at=built_at,
    )


def build_na28_lxx_module_from_imports(
    *,
    target_path: Path,
    source_entries: Mapping[str, Mapping[str, object]],
    nt_verses: Sequence[TagntModuleVerse],
    lxx_result: LxxImportResult,
    data_version: int = BIBLE_MODULE_DATA_VERSION_INITIAL,
    built_at: str | None = None,
) -> BibleModuleBuildReport:
    _require_locked_entries(source_entries)
    timestamp = _filesystem_timestamp(built_at or now_utc_iso())
    target_path = target_path.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = _new_temp_db_path(target_path)
    backup_path: Path | None = None
    actual_built_at = built_at or now_utc_iso()

    try:
        counts = _write_database(
            db_path=temp_path,
            source_entries=source_entries,
            nt_verses=nt_verses,
            lxx_result=lxx_result,
            data_version=data_version,
            built_at=actual_built_at,
        )
        validate_na28_lxx_database(temp_path, require_spot_checks=True)

        if target_path.exists():
            backup_path = target_path.with_name(f"{target_path.name}.{timestamp}.bak")
            shutil.copy2(target_path, backup_path)
        temp_path.replace(target_path)
        validate_na28_lxx_database(target_path, require_spot_checks=True)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return BibleModuleBuildReport(
        target_path=target_path,
        backup_path=backup_path,
        module_verses_count=counts["module_verses"],
        tokens_count=counts["tokens"],
        token_strongs_count=counts["token_strongs"],
        import_warnings_count=counts["import_warnings"],
        built_at=actual_built_at,
    )


def validate_na28_lxx_database(
    db_path: Path,
    *,
    require_spot_checks: bool,
) -> None:
    connection = sqlite3.connect(str(db_path))
    try:
        assert_no_form_occurrence_tables(table_names(connection))
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if user_version != BIBLE_MODULE_SCHEMA_VERSION:
            raise ValueError(
                f"Unexpected bible module user_version: {user_version}"
            )
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise ValueError(f"Bible module foreign key errors: {foreign_key_errors}")
        metadata = dict(connection.execute("SELECT key, value FROM db_metadata"))
        if metadata.get("schema_version") != str(BIBLE_MODULE_SCHEMA_VERSION):
            raise ValueError("Bible module db_metadata.schema_version mismatch")
        books_count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if int(books_count) != 66:
            raise ValueError(f"Bible module must contain 66 books, got {books_count}")
        padded_strongs_count = connection.execute(
            "SELECT COUNT(*) FROM token_strongs WHERE strong GLOB '[GH]0[0-9]*'"
        ).fetchone()[0]
        if int(padded_strongs_count) != 0:
            raise ValueError("Bible module contains padded normalized Strong keys")

        if require_spot_checks:
            _require_strong_occurrence(connection, canonical_ref="Gen.1.1", strong="G746")
            _require_strong_occurrence(connection, canonical_ref="Mat.1.1", strong="G976")
    finally:
        connection.close()


def _write_database(
    *,
    db_path: Path,
    source_entries: Mapping[str, Mapping[str, object]],
    nt_verses: Sequence[TagntModuleVerse],
    lxx_result: LxxImportResult,
    data_version: int,
    built_at: str,
) -> dict[str, int]:
    if db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN")
        create_bible_module_schema(
            connection,
            include_token_tables=True,
            seed_canon=True,
            data_version=data_version,
            date_iso=built_at,
        )
        _insert_module_metadata(
            connection,
            data_version=data_version,
            built_at=built_at,
        )
        _insert_module_sources(connection, source_entries, lxx_result)
        _insert_source_texts(connection)
        counts = _insert_module_verses_and_tokens(
            connection,
            lxx_result=lxx_result,
            nt_verses=nt_verses,
        )
        _insert_import_warnings(connection, lxx_result)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    counts["import_warnings"] = len(lxx_result.warnings)
    return counts


def _insert_module_metadata(
    connection: sqlite3.Connection,
    *,
    data_version: int,
    built_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bible_modules(
          module_id,
          code,
          title,
          language,
          module_kind,
          canon,
          versification,
          license,
          source_summary,
          schema_version,
          data_version,
          built_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            MODULE_ID,
            MODULE_CODE,
            "NA28/LXX Greek Bible Module",
            "grc",
            "original_language",
            CANON_NAME,
            "protestant_66_canonical_refs_with_lxx_native_refs",
            "STEPBible CC BY 4.0; CrossWire LXX free non-commercial distribution",
            "OT: CrossWire LXX Greek; NT: STEPBible TAGNT NA28 profile.",
            BIBLE_MODULE_SCHEMA_VERSION,
            data_version,
            built_at,
        ),
    )


def _insert_module_sources(
    connection: sqlite3.Connection,
    source_entries: Mapping[str, Mapping[str, object]],
    lxx_result: LxxImportResult,
) -> None:
    rows = [_tagnt_combined_source_row(source_entries)]
    rows.extend(_locked_source_row(source_entries[source_id]) for source_id in TAGNT_LOCKED_SOURCE_IDS)
    rows.append(_crosswire_source_row(source_entries[CROSSWIRE_LXX_SOURCE_ID], lxx_result))
    rows.extend(_locked_source_row(source_entries[source_id]) for source_id in SUPPORTING_LOCKED_SOURCE_IDS)
    connection.executemany(
        """
        INSERT INTO module_sources(
          source_id,
          module_id,
          title,
          source_url,
          source_version,
          license,
          checksum_sha256,
          import_notes
        )
        VALUES(
          :source_id,
          :module_id,
          :title,
          :source_url,
          :source_version,
          :license,
          :checksum_sha256,
          :import_notes
        )
        """,
        rows,
    )


def _insert_source_texts(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO source_texts(
          source_text_id,
          module_id,
          source_id,
          code,
          scope,
          language,
          priority
        )
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                CROSSWIRE_LXX_SOURCE_TEXT_ID,
                MODULE_ID,
                CROSSWIRE_LXX_SOURCE_ID,
                "LXX_OT",
                "OT",
                "grc",
                1,
            ),
            (
                TAGNT_SOURCE_TEXT_ID,
                MODULE_ID,
                TAGNT_SOURCE_ID,
                "TAGNT_NA28_NT",
                "NT",
                "grc",
                2,
            ),
        ],
    )


def _insert_module_verses_and_tokens(
    connection: sqlite3.Connection,
    *,
    lxx_result: LxxImportResult,
    nt_verses: Sequence[TagntModuleVerse],
) -> dict[str, int]:
    module_verse_id = 0
    token_id = 0
    token_strongs_count = 0

    for verse in (*lxx_result.module_verses, *nt_verses):
        module_verse_id += 1
        connection.execute(
            INSERT_MODULE_VERSE_SQL,
            verse.as_module_verse_row(module_verse_id=module_verse_id),
        )
        connection.execute(
            INSERT_MODULE_VERSE_LINK_SQL,
            verse.as_module_verse_link_row(module_verse_id=module_verse_id),
        )
        for token in verse.tokens:
            token_id += 1
            connection.execute(
                INSERT_TOKEN_SQL,
                token.as_token_row(
                    module_verse_id=module_verse_id,
                    token_id=token_id,
                ),
            )
            strong_rows = token.token_strong_rows(token_id=token_id)
            if strong_rows:
                connection.executemany(INSERT_TOKEN_STRONG_SQL, strong_rows)
            token_strongs_count += len(strong_rows)

    return {
        "module_verses": module_verse_id,
        "tokens": token_id,
        "token_strongs": token_strongs_count,
    }


def _insert_import_warnings(
    connection: sqlite3.Connection,
    lxx_result: LxxImportResult,
) -> None:
    rows = [
        warning.as_import_warning_row(warning_id=index)
        for index, warning in enumerate(lxx_result.warnings, start=1)
    ]
    if not rows:
        return
    connection.executemany(
        """
        INSERT INTO import_warnings(
          warning_id,
          source_id,
          severity,
          code,
          source_ref,
          message,
          raw_json
        )
        VALUES(
          :warning_id,
          :source_id,
          :severity,
          :code,
          :source_ref,
          :message,
          :raw_json
        )
        """,
        rows,
    )


def _require_strong_occurrence(
    connection: sqlite3.Connection,
    *,
    canonical_ref: str,
    strong: str,
) -> None:
    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM token_strongs ts
        JOIN tokens t ON t.token_id = ts.token_id
        JOIN module_verse_links link ON link.module_verse_id = t.module_verse_id
        JOIN canonical_verses verse ON verse.canonical_verse_id = link.canonical_verse_id
        WHERE verse.canonical_ref = ?
          AND ts.strong = ?
        """,
        (canonical_ref, strong),
    ).fetchone()[0]
    if int(count) <= 0:
        raise ValueError(f"Missing expected Strong {strong} in {canonical_ref}")


def _tagnt_combined_source_row(
    source_entries: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    entries = [source_entries[source_id] for source_id in TAGNT_LOCKED_SOURCE_IDS]
    checksum = _combined_sha256(str(entry["sha256"]) for entry in entries)
    return {
        "source_id": TAGNT_SOURCE_ID,
        "module_id": MODULE_ID,
        "title": "TAGNT - Translators Amalgamated Greek NT (NA28 profile)",
        "source_url": "; ".join(str(entry["source_page_url"]) for entry in entries),
        "source_version": str(entries[0]["version"]),
        "license": str(entries[0]["license"]),
        "checksum_sha256": checksum,
        "import_notes": "Combined locked TAGNT source chunks: "
        + ", ".join(str(entry["source_id"]) for entry in entries),
    }


def _crosswire_source_row(
    entry: Mapping[str, object],
    lxx_result: LxxImportResult,
) -> dict[str, object]:
    metadata = lxx_result.metadata
    source_version = metadata.exact_version if metadata is not None else str(entry["version"])
    license_name = (
        metadata.distribution_license
        if metadata is not None and metadata.distribution_license
        else str(entry["license"])
    )
    notes = str(entry.get("notes") or "")
    if metadata is not None:
        notes = (
            f"{notes} CrossWire module={metadata.module_name}; "
            f"Versification={metadata.versification}; "
            f"BlockType={metadata.block_type}; CompressType={metadata.compress_type}."
        ).strip()
    return {
        "source_id": CROSSWIRE_LXX_SOURCE_ID,
        "module_id": MODULE_ID,
        "title": str(entry["title"]),
        "source_url": str(entry["source_page_url"]),
        "source_version": source_version,
        "license": license_name,
        "checksum_sha256": str(entry["sha256"]),
        "import_notes": notes,
    }


def _locked_source_row(entry: Mapping[str, object]) -> dict[str, object]:
    return {
        "source_id": str(entry["source_id"]),
        "module_id": MODULE_ID,
        "title": str(entry["title"]),
        "source_url": str(entry["source_page_url"]),
        "source_version": str(entry["version"]),
        "license": str(entry["license"]),
        "checksum_sha256": str(entry["sha256"]),
        "import_notes": str(entry.get("notes") or ""),
    }


def _load_verified_manifest(manifest_path: Path) -> Mapping[str, object]:
    errors = verify_source_manifest(manifest_path=manifest_path)
    if errors:
        details = "\n".join(errors)
        raise ValueError(f"Cannot build NA28_LXX from invalid source manifest:\n{details}")
    manifest = load_manifest(manifest_path)
    if manifest is None:
        raise ValueError(f"Missing source manifest: {manifest_path}")
    return manifest


def _source_entries_by_id(
    manifest: Mapping[str, object],
) -> dict[str, Mapping[str, object]]:
    entries = manifest.get("sources")
    if not isinstance(entries, list):
        raise ValueError("Invalid source manifest: sources must be a list")
    by_id: dict[str, Mapping[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("Invalid source manifest entry")
        source_id = entry.get("source_id")
        if not isinstance(source_id, str):
            raise ValueError("Invalid source manifest entry without source_id")
        by_id[source_id] = entry
    _require_locked_entries(by_id)
    return by_id


def _source_paths_by_id(
    manifest: Mapping[str, object],
    manifest_path: Path,
) -> dict[str, Path]:
    entries = _source_entries_by_id(manifest)
    source_paths: dict[str, Path] = {}
    for source_id, entry in entries.items():
        local_path = entry.get("local_path")
        if not isinstance(local_path, str):
            raise ValueError(f"{source_id}: missing local_path")
        path = Path(local_path)
        source_paths[source_id] = path if path.is_absolute() else manifest_path.parent / path
    return source_paths


def _require_locked_entries(source_entries: Mapping[str, Mapping[str, object]]) -> None:
    missing = [source_id for source_id in REQUIRED_LOCKED_SOURCE_IDS if source_id not in source_entries]
    if missing:
        raise ValueError(f"Missing locked source entries: {', '.join(missing)}")


def _combined_sha256(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(str(value).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _new_temp_db_path(target_path: Path) -> Path:
    temp_file = tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(target_path.parent),
        prefix=f".{target_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_file.name)
    temp_file.close()
    temp_path.unlink(missing_ok=True)
    return temp_path


def _filesystem_timestamp(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the NA28_LXX Bible module SQLite database from locked sources.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET_PATH,
        help="Output bible_na28_lxx.sqlite path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_LOCK_PATH,
        help="Locked source_manifest.lock.json path.",
    )
    parser.add_argument(
        "--data-version",
        type=int,
        default=BIBLE_MODULE_DATA_VERSION_INITIAL,
        help="db_metadata.data_version and bible_modules.data_version value.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_na28_lxx_module(
        target_path=args.target,
        manifest_path=args.manifest,
        data_version=args.data_version,
    )
    print(json.dumps(_report_json(report), ensure_ascii=False, indent=2))
    return 0


def _report_json(report: BibleModuleBuildReport) -> dict[str, object]:
    return {
        "target_path": str(report.target_path),
        "backup_path": str(report.backup_path) if report.backup_path else None,
        "module_verses_count": report.module_verses_count,
        "tokens_count": report.tokens_count,
        "token_strongs_count": report.token_strongs_count,
        "import_warnings_count": report.import_warnings_count,
        "built_at": report.built_at,
    }


if __name__ == "__main__":
    raise SystemExit(main())

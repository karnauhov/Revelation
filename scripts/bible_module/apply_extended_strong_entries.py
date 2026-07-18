from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .fetch_sources import load_manifest, verify_source_manifest
from .lexicon import LexiconEntry, iter_step_lexicon_entries
from .schema import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    now_utc_iso,
)
from .sources import DEFAULT_SOURCE_LOCK_PATH
from .tagnt import normalize_strong

DEFAULT_COMMON_DB_PATH = Path.home() / "Documents" / "revelation" / "db" / "revelation.sqlite"
DEFAULT_BIBLE_MODULE_PATH = (
    Path.home() / "Documents" / "revelation" / "db" / "bible_na28_lxx.sqlite"
)

CLASSIC_GREEK_STRONG_MAX = 5624
EXPECTED_ATTESTED_EXTENDED_COUNT = 88
EXPECTED_PRIMARY_ATTESTED_EXTENDED_COUNT = 78
UNUSED_EXTENDED_SENTINEL = "G21502"

LEXICON_SOURCE_IDS = (
    "step_tbesg",
    "step_tflsj_0_5624",
    "step_tflsj_extra",
)
BASE_LEXICON_SOURCE_ID = "step_tbesg"
FULL_EXTRA_LEXICON_SOURCE_ID = "step_tflsj_extra"

INSERT_GREEK_WORD_SQL = """
INSERT INTO greek_words(id, word, category, synonyms, origin, usage)
VALUES(:id, :word, :category, :synonyms, :origin, :usage)
"""


@dataclass(frozen=True)
class ExtendedStrongRow:
    strong: str
    id: int
    word: str
    category: str
    synonyms: str
    origin: str
    usage: str
    tbesg_gloss: str
    tbesg_definition: str
    tflsj_extra_definition: str

    def insert_parameters(self) -> dict[str, object]:
        return {
            "id": self.id,
            "word": self.word,
            "category": self.category,
            "synonyms": self.synonyms,
            "origin": self.origin,
            "usage": self.usage,
        }


@dataclass(frozen=True)
class ExtendedStrongApplyReport:
    common_db_path: Path
    bible_module_path: Path
    backup_path: Path | None
    attested_extended_count: int
    primary_attested_extended_count: int
    inserted_count: int
    skipped_existing_count: int
    data_version_before: str
    data_version_after: str
    applied_at: str

    def as_json(self) -> dict[str, object]:
        return {
            "common_db_path": str(self.common_db_path),
            "bible_module_path": str(self.bible_module_path),
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "attested_extended_count": self.attested_extended_count,
            "primary_attested_extended_count": self.primary_attested_extended_count,
            "inserted_count": self.inserted_count,
            "skipped_existing_count": self.skipped_existing_count,
            "data_version_before": self.data_version_before,
            "data_version_after": self.data_version_after,
            "applied_at": self.applied_at,
        }


def apply_extended_strong_entries(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    bible_module_path: Path = DEFAULT_BIBLE_MODULE_PATH,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    source_paths: Mapping[str, Path] | None = None,
    expected_attested_count: int = EXPECTED_ATTESTED_EXTENDED_COUNT,
    expected_primary_count: int = EXPECTED_PRIMARY_ATTESTED_EXTENDED_COUNT,
    applied_at: str | None = None,
    data_version: int | None = None,
) -> ExtendedStrongApplyReport:
    common_db_path = common_db_path.resolve()
    bible_module_path = bible_module_path.resolve()
    applied_at = applied_at or now_utc_iso()

    lexicon_index = load_lexicon_index(
        manifest_path=manifest_path,
        source_paths=source_paths,
    )
    rows = build_attested_extended_strong_rows(
        bible_module_path=bible_module_path,
        lexicon_index=lexicon_index,
        expected_attested_count=expected_attested_count,
        expected_primary_count=expected_primary_count,
    )

    if not common_db_path.exists():
        raise FileNotFoundError(f"Common dictionary DB not found: {common_db_path}")

    backup_path: Path | None = None
    connection = sqlite3.connect(str(common_db_path))
    try:
        connection.row_factory = sqlite3.Row
        _validate_common_dictionary_schema(connection)
        existing_rows = _fetch_existing_greek_words(connection)
        _assert_classic_rows_are_in_scope(existing_rows)

        rows_to_insert = [
            row for row in rows if row.id not in existing_rows and row.id > CLASSIC_GREEK_STRONG_MAX
        ]
        skipped_existing_count = len(rows) - len(rows_to_insert)

        metadata_before = _read_db_metadata(connection)
        data_version_before = metadata_before.get(DB_METADATA_DATA_VERSION_KEY, "0")
        data_version_after = str(
            data_version if data_version is not None else int(data_version_before) + 1
        )

        if rows_to_insert:
            backup_path = _backup_db(common_db_path, applied_at)
            try:
                with connection:
                    connection.executemany(
                        INSERT_GREEK_WORD_SQL,
                        [row.insert_parameters() for row in rows_to_insert],
                    )
                    _set_db_metadata(
                        connection,
                        data_version=data_version_after,
                        date_iso=applied_at,
                    )
            except Exception:
                connection.close()
                if backup_path is not None and backup_path.exists():
                    shutil.copy2(backup_path, common_db_path)
                raise
        else:
            data_version_after = data_version_before
    finally:
        connection.close()

    return ExtendedStrongApplyReport(
        common_db_path=common_db_path,
        bible_module_path=bible_module_path,
        backup_path=backup_path,
        attested_extended_count=len(rows),
        primary_attested_extended_count=_count_primary_extended_strongs(bible_module_path),
        inserted_count=len(rows_to_insert),
        skipped_existing_count=skipped_existing_count,
        data_version_before=data_version_before,
        data_version_after=data_version_after,
        applied_at=applied_at,
    )


def load_lexicon_index(
    *,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    source_paths: Mapping[str, Path] | None = None,
) -> dict[str, dict[str, LexiconEntry]]:
    resolved_paths = (
        {source_id: Path(path) for source_id, path in source_paths.items()}
        if source_paths is not None
        else _source_paths_from_manifest(manifest_path)
    )

    missing = [source_id for source_id in LEXICON_SOURCE_IDS if source_id not in resolved_paths]
    if missing:
        raise ValueError(f"Missing lexicon source paths: {', '.join(missing)}")

    index: dict[str, dict[str, LexiconEntry]] = {
        source_id: {} for source_id in LEXICON_SOURCE_IDS
    }
    for source_id in LEXICON_SOURCE_IDS:
        for entry in iter_step_lexicon_entries(resolved_paths[source_id], source_id=source_id):
            index[source_id].setdefault(entry.strong, entry)

    return index


def build_attested_extended_strong_rows(
    *,
    bible_module_path: Path,
    lexicon_index: Mapping[str, Mapping[str, LexiconEntry]],
    expected_attested_count: int = EXPECTED_ATTESTED_EXTENDED_COUNT,
    expected_primary_count: int = EXPECTED_PRIMARY_ATTESTED_EXTENDED_COUNT,
) -> tuple[ExtendedStrongRow, ...]:
    attested = read_attested_extended_strongs(bible_module_path)
    primary_attested = read_attested_extended_strongs(
        bible_module_path,
        primary_only=True,
    )
    if len(attested) != expected_attested_count:
        raise ValueError(
            f"Expected {expected_attested_count} attested extended Strong keys, "
            f"found {len(attested)}"
        )
    if len(primary_attested) != expected_primary_count:
        raise ValueError(
            f"Expected {expected_primary_count} primary attested extended Strong keys, "
            f"found {len(primary_attested)}"
        )
    if UNUSED_EXTENDED_SENTINEL in attested:
        raise ValueError(f"Unused extended sentinel {UNUSED_EXTENDED_SENTINEL} is attested")

    base_index = lexicon_index.get(BASE_LEXICON_SOURCE_ID, {})
    extra_index = lexicon_index.get(FULL_EXTRA_LEXICON_SOURCE_ID, {})

    missing = [strong for strong in attested if strong not in base_index]
    if missing:
        raise ValueError(f"Missing TBESG entries: {', '.join(missing)}")

    rows: list[ExtendedStrongRow] = []
    for strong in attested:
        base = base_index[strong]
        extra = extra_index.get(strong)
        rows.append(
            ExtendedStrongRow(
                strong=strong,
                id=_strong_number(strong),
                word=base.greek.strip(),
                category=_category_from_morphology(base.morphology, base.dstrong),
                synonyms="",
                origin=_origin_from_lexicon_entry(base),
                usage="",
                tbesg_gloss=base.gloss.strip(),
                tbesg_definition=base.definition.strip(),
                tflsj_extra_definition=extra.definition.strip() if extra else "",
            )
        )

    return tuple(rows)


def read_attested_extended_strongs(
    bible_module_path: Path,
    *,
    primary_only: bool = False,
) -> tuple[str, ...]:
    if not bible_module_path.exists():
        raise FileNotFoundError(f"Bible module DB not found: {bible_module_path}")
    condition = "AND is_primary = 1" if primary_only else ""
    connection = sqlite3.connect(str(bible_module_path))
    try:
        rows = connection.execute(
            f"""
            SELECT DISTINCT strong
            FROM token_strongs
            WHERE strong LIKE 'G%'
              AND CAST(substr(strong, 2) AS INTEGER) > ?
              {condition}
            ORDER BY CAST(substr(strong, 2) AS INTEGER), strong
            """,
            (CLASSIC_GREEK_STRONG_MAX,),
        ).fetchall()
    finally:
        connection.close()

    strongs = tuple(str(row[0]) for row in rows)
    for strong in strongs:
        if normalize_strong(strong) != strong:
            raise ValueError(f"Attested Strong is not normalized: {strong}")
    return strongs


def _source_paths_from_manifest(manifest_path: Path) -> dict[str, Path]:
    errors = verify_source_manifest(manifest_path=manifest_path)
    if errors:
        details = "\n".join(errors)
        raise ValueError(f"Cannot read lexicons from invalid source manifest:\n{details}")
    manifest = load_manifest(manifest_path)
    if manifest is None:
        raise FileNotFoundError(f"Missing source manifest: {manifest_path}")

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise ValueError("Invalid source manifest: sources must be a list")

    paths: dict[str, Path] = {}
    for entry in sources:
        if not isinstance(entry, Mapping):
            continue
        source_id = entry.get("source_id")
        local_path = entry.get("local_path")
        if isinstance(source_id, str) and isinstance(local_path, str):
            path = Path(local_path)
            paths[source_id] = path if path.is_absolute() else manifest_path.parent / path
    return paths


def _validate_common_dictionary_schema(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(greek_words)").fetchall()
    }
    required = {"id", "word", "category", "synonyms", "origin", "usage"}
    missing = required - columns
    if missing:
        raise ValueError(f"Common DB greek_words is missing columns: {', '.join(sorted(missing))}")

    metadata_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(db_metadata)").fetchall()
    }
    if {"key", "value"} - metadata_columns:
        raise ValueError("Common DB db_metadata table is missing key/value columns")


def _fetch_existing_greek_words(connection: sqlite3.Connection) -> dict[int, dict[str, str]]:
    rows = connection.execute(
        "SELECT id, word, category, synonyms, origin, usage FROM greek_words"
    ).fetchall()
    return {
        int(row["id"]): {
            "word": str(row["word"]),
            "category": str(row["category"]),
            "synonyms": str(row["synonyms"]),
            "origin": str(row["origin"]),
            "usage": str(row["usage"]),
        }
        for row in rows
    }


def _assert_classic_rows_are_in_scope(existing_rows: Mapping[int, object]) -> None:
    missing_classic = [
        strong_id
        for strong_id in range(1, CLASSIC_GREEK_STRONG_MAX + 1)
        if strong_id not in existing_rows
    ]
    if missing_classic:
        preview = ", ".join(str(value) for value in missing_classic[:10])
        raise ValueError(f"Common DB is missing classic Greek Strong rows: {preview}")


def _read_db_metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return {
        str(row["key"]): str(row["value"])
        for row in connection.execute("SELECT key, value FROM db_metadata")
    }


def _set_db_metadata(
    connection: sqlite3.Connection,
    *,
    data_version: str,
    date_iso: str,
) -> None:
    connection.executemany(
        """
        INSERT INTO db_metadata(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (
            (DB_METADATA_DATA_VERSION_KEY, data_version),
            (DB_METADATA_DATE_KEY, date_iso),
        ),
    )


def _backup_db(db_path: Path, timestamp: str) -> Path:
    backup_path = db_path.with_name(f"{db_path.name}.{_filesystem_timestamp(timestamp)}.bak")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _filesystem_timestamp(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


def _category_from_morphology(morphology: str, dstrong: str) -> str:
    if "Name of" in dstrong:
        return "@properNoun, @indeclinable"

    value = morphology.strip()
    if not value:
        return ""

    categories: list[str] = []
    for part in re.split(r"\s*/\s*", value):
        categories.extend(_category_tokens_from_morphology_part(part))
    return ", ".join(dict.fromkeys(categories))


def _category_tokens_from_morphology_part(part: str) -> list[str]:
    tokens: list[str] = []
    if ":" in part:
        _language, detail = part.split(":", maxsplit=1)
    else:
        detail = part

    components = [component for component in detail.split("-") if component]
    if not components:
        return tokens

    word_type = components[0]
    extras = set(components[1:])

    if word_type == "N" and "P" in extras:
        tokens.extend(["@properNoun", "@indeclinable"])
    elif word_type == "N":
        tokens.append("@noun")
    elif word_type == "V":
        tokens.append("@verb")
    elif word_type == "A":
        tokens.append("@adj")
    elif word_type == "ADV":
        tokens.append("@adv")
    elif word_type == "CONJ":
        tokens.append("@conj")
    elif word_type == "INJ":
        tokens.append("@interj")
    elif word_type == "PREP":
        tokens.append("@prep")
    elif word_type == "PRT":
        tokens.append("@particle")
    elif word_type == "T":
        tokens.append("@artDef")

    if "@properNoun" not in tokens:
        if "M" in extras:
            tokens.append("@masc")
        if "F" in extras:
            tokens.append("@fem")
        if "N" in extras:
            tokens.append("@neut")

    return tokens


def _origin_from_lexicon_entry(entry: LexiconEntry) -> str:
    related: list[str] = []
    for raw in re.findall(r"[GH]0*\d+[A-Za-z]?", f"{entry.dstrong} {entry.ustrong}"):
        normalized = normalize_strong(raw)
        if normalized != entry.strong and normalized not in related:
            related.append(normalized)
    return ",".join(related)


def _strong_number(strong: str) -> int:
    normalized = normalize_strong(strong)
    if not normalized.startswith("G"):
        raise ValueError(f"Expected Greek Strong key: {strong}")
    return int(normalized[1:])


def _count_primary_extended_strongs(bible_module_path: Path) -> int:
    return len(read_attested_extended_strongs(bible_module_path, primary_only=True))


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Insert NA28_LXX-attested extended Greek Strong rows into revelation.sqlite.",
    )
    parser.add_argument(
        "--common-db",
        type=Path,
        default=DEFAULT_COMMON_DB_PATH,
        help="Path to common revelation.sqlite.",
    )
    parser.add_argument(
        "--bible-module",
        type=Path,
        default=DEFAULT_BIBLE_MODULE_PATH,
        help="Path to bible_na28_lxx.sqlite.",
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
        default=None,
        help="Optional db_metadata.data_version override. Defaults to current + 1.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    report = apply_extended_strong_entries(
        common_db_path=args.common_db,
        bible_module_path=args.bible_module,
        manifest_path=args.manifest,
        data_version=args.data_version,
    )
    print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

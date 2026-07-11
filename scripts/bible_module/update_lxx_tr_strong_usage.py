from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .schema import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    now_utc_iso,
)
from .strong_numbers import (
    CLASSIC_GREEK_STRONG_MAX,
    classic_greek_strong_or_none,
    is_classic_greek_strong,
    strong_number,
)
from .tagnt import normalize_strong

DEFAULT_DB_DIR = Path.home() / "Documents" / "revelation" / "db"
DEFAULT_COMMON_DB_PATH = DEFAULT_DB_DIR / "revelation.sqlite"
DEFAULT_LXX_TR_DB_PATH = DEFAULT_DB_DIR / "bible_lxx_tr.sqlite"

_STRONG_TOKEN_PATTERN = re.compile(r"\bG[1-9][0-9]*\b")
_USAGE_REF_PATTERN = re.compile(r"^(?P<verse_key>[0-9A-Z]{3})(?:x(?P<count>[1-9][0-9]*))?$")


@dataclass(frozen=True)
class LxxTrStrongCleanupReport:
    bible_module_path: Path
    backup_path: Path | None
    updated_verse_count: int
    replacement_counts: Mapping[str, int]
    removed_counts: Mapping[str, int]
    classic_token_count: int
    data_version_before: str
    data_version_after: str

    def as_json(self) -> dict[str, object]:
        return {
            "bible_module_path": str(self.bible_module_path),
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "updated_verse_count": self.updated_verse_count,
            "replacement_counts": dict(self.replacement_counts),
            "removed_counts": dict(self.removed_counts),
            "classic_token_count": self.classic_token_count,
            "data_version_before": self.data_version_before,
            "data_version_after": self.data_version_after,
        }


@dataclass(frozen=True)
class StrongUsageApplyReport:
    common_db_path: Path
    bible_module_path: Path
    lxx_cleanup: LxxTrStrongCleanupReport | None
    backup_path: Path | None
    source_token_count: int
    generated_usage_token_count: int
    database_usage_token_count: int
    nonempty_usage_rows: int
    changed_usage_rows: int
    greek_words_rows: int
    data_version_before: str
    data_version_after: str
    applied_at: str

    def as_json(self) -> dict[str, object]:
        return {
            "common_db_path": str(self.common_db_path),
            "bible_module_path": str(self.bible_module_path),
            "lxx_cleanup": self.lxx_cleanup.as_json() if self.lxx_cleanup else None,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "source_token_count": self.source_token_count,
            "generated_usage_token_count": self.generated_usage_token_count,
            "database_usage_token_count": self.database_usage_token_count,
            "nonempty_usage_rows": self.nonempty_usage_rows,
            "changed_usage_rows": self.changed_usage_rows,
            "greek_words_rows": self.greek_words_rows,
            "data_version_before": self.data_version_before,
            "data_version_after": self.data_version_after,
            "applied_at": self.applied_at,
        }


StrongUsageById = dict[int, dict[str, Counter[str]]]


def apply_lxx_tr_strong_usage(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    bible_module_path: Path = DEFAULT_LXX_TR_DB_PATH,
    clean_lxx_tr_strongs: bool = True,
    applied_at: str | None = None,
    data_version: int | None = None,
) -> StrongUsageApplyReport:
    common_db_path = common_db_path.resolve()
    bible_module_path = bible_module_path.resolve()
    applied_at = applied_at or now_utc_iso()

    lxx_cleanup = (
        replace_lxx_tr_extended_strongs(
            bible_module_path=bible_module_path,
            applied_at=applied_at,
        )
        if clean_lxx_tr_strongs
        else None
    )

    usage_by_id, source_token_count = collect_lxx_tr_strong_usage(
        bible_module_path,
    )
    formatted_usage = {
        strong_id: format_strong_usage(surface_counts)
        for strong_id, surface_counts in usage_by_id.items()
    }
    generated_usage_token_count = count_usage_occurrences(
        formatted_usage.values(),
    )
    if generated_usage_token_count != source_token_count:
        raise ValueError(
            "Generated usage count mismatch: "
            f"{generated_usage_token_count} != {source_token_count}"
        )

    if not common_db_path.exists():
        raise FileNotFoundError(f"Common dictionary DB not found: {common_db_path}")

    backup_path: Path | None = None
    connection = sqlite3.connect(str(common_db_path))
    try:
        connection.row_factory = sqlite3.Row
        _validate_common_dictionary(connection)
        existing_usage = _fetch_existing_usage(connection)
        data_version_before = _read_data_version(connection)
        rows_to_update = [
            (formatted_usage.get(strong_id, ""), strong_id)
            for strong_id in range(1, CLASSIC_GREEK_STRONG_MAX + 1)
        ]
        changed_usage_rows = sum(
            1
            for usage, strong_id in rows_to_update
            if existing_usage.get(strong_id, "") != usage
        )
        should_update_common_db = changed_usage_rows > 0 or data_version is not None
        data_version_after = str(
            data_version
            if data_version is not None
            else (
                int(data_version_before) + 1
                if should_update_common_db
                else int(data_version_before)
            )
        )

        if should_update_common_db:
            backup_path = _backup_db(common_db_path, applied_at)
            try:
                with connection:
                    connection.executemany(
                        "UPDATE greek_words SET usage = ? WHERE id = ?",
                        rows_to_update,
                    )
                    _set_metadata(
                        connection,
                        data_version=data_version_after,
                        date_iso=applied_at,
                    )
            except Exception:
                connection.close()
                if backup_path.exists():
                    shutil.copy2(backup_path, common_db_path)
                raise
    finally:
        connection.close()

    database_usage_token_count = count_database_usage(common_db_path)
    if database_usage_token_count != source_token_count:
        raise ValueError(
            "Database usage count mismatch: "
            f"{database_usage_token_count} != {source_token_count}"
        )

    return StrongUsageApplyReport(
        common_db_path=common_db_path,
        bible_module_path=bible_module_path,
        lxx_cleanup=lxx_cleanup,
        backup_path=backup_path,
        source_token_count=source_token_count,
        generated_usage_token_count=generated_usage_token_count,
        database_usage_token_count=database_usage_token_count,
        nonempty_usage_rows=sum(1 for value in formatted_usage.values() if value),
        changed_usage_rows=changed_usage_rows,
        greek_words_rows=_count_greek_words(common_db_path),
        data_version_before=data_version_before,
        data_version_after=data_version_after,
        applied_at=applied_at,
    )


def replace_lxx_tr_extended_strongs(
    *,
    bible_module_path: Path,
    applied_at: str | None = None,
) -> LxxTrStrongCleanupReport:
    bible_module_path = bible_module_path.resolve()
    applied_at = applied_at or now_utc_iso()
    if not bible_module_path.exists():
        raise FileNotFoundError(f"LXX/TR DB not found: {bible_module_path}")

    rows_to_update: list[tuple[str, str]] = []
    replacement_counts: Counter[str] = Counter()
    removed_counts: Counter[str] = Counter()

    connection = sqlite3.connect(str(bible_module_path))
    try:
        connection.row_factory = sqlite3.Row
        _validate_lxx_tr_schema(connection)
        data_version_before = _read_data_version(connection)
        for row in connection.execute(
            "SELECT verse_key, text FROM verses ORDER BY verse_key",
        ):
            verse_key = str(row["verse_key"])
            text = str(row["text"])
            next_text = _replace_extended_strongs_in_text(
                text,
                replacement_counts=replacement_counts,
                removed_counts=removed_counts,
            )
            if next_text != text:
                rows_to_update.append((next_text, verse_key))

        backup_path: Path | None = None
        data_version_after = data_version_before
        if rows_to_update:
            data_version_after = str(int(data_version_before) + 1)
            backup_path = _backup_db(bible_module_path, applied_at)
            try:
                with connection:
                    connection.executemany(
                        "UPDATE verses SET text = ? WHERE verse_key = ?",
                        rows_to_update,
                    )
                    _set_metadata(
                        connection,
                        data_version=data_version_after,
                        date_iso=applied_at,
                    )
            except Exception:
                connection.close()
                if backup_path.exists():
                    shutil.copy2(backup_path, bible_module_path)
                raise
    finally:
        connection.close()

    usage_by_id, classic_token_count = collect_lxx_tr_strong_usage(bible_module_path)
    del usage_by_id
    return LxxTrStrongCleanupReport(
        bible_module_path=bible_module_path,
        backup_path=backup_path,
        updated_verse_count=len(rows_to_update),
        replacement_counts=dict(sorted(replacement_counts.items())),
        removed_counts=dict(sorted(removed_counts.items())),
        classic_token_count=classic_token_count,
        data_version_before=data_version_before,
        data_version_after=data_version_after,
    )


def collect_lxx_tr_strong_usage(
    bible_module_path: Path,
) -> tuple[StrongUsageById, int]:
    bible_module_path = bible_module_path.resolve()
    if not bible_module_path.exists():
        raise FileNotFoundError(f"LXX/TR DB not found: {bible_module_path}")

    usage_by_id: StrongUsageById = defaultdict(lambda: defaultdict(Counter))
    source_token_count = 0
    out_of_scope: Counter[str] = Counter()
    connection = sqlite3.connect(str(bible_module_path))
    try:
        connection.row_factory = sqlite3.Row
        _validate_lxx_tr_schema(connection)
        for row in connection.execute("SELECT verse_key, text FROM verses ORDER BY verse_key"):
            verse_key = str(row["verse_key"])
            text = str(row["text"])
            previous_surface: str | None = None
            for part in text.split():
                if _STRONG_TOKEN_PATTERN.fullmatch(part):
                    normalized = normalize_strong(part)
                    if not is_classic_greek_strong(normalized):
                        out_of_scope[normalized] += 1
                    elif previous_surface:
                        strong_id = strong_number(normalized)
                        usage_by_id[strong_id][previous_surface][verse_key] += 1
                        source_token_count += 1
                    previous_surface = None
                    continue
                previous_surface = part
    finally:
        connection.close()

    if out_of_scope:
        details = ", ".join(
            f"{strong}={count}" for strong, count in sorted(out_of_scope.items())
        )
        raise ValueError(f"LXX/TR contains out-of-scope Greek Strong tags: {details}")

    return {
        strong_id: dict(surface_counts)
        for strong_id, surface_counts in usage_by_id.items()
    }, source_token_count


def format_strong_usage(surface_counts: Mapping[str, Counter[str]]) -> str:
    lines: list[str] = []
    for surface in sorted(surface_counts, key=lambda value: (value.casefold(), value)):
        verse_counts = surface_counts[surface]
        total = sum(verse_counts.values())
        refs = ";".join(
            f"{verse_key}x{count}" if count > 1 else verse_key
            for verse_key, count in sorted(verse_counts.items())
        )
        lines.append(f"{surface}: [{refs}], {total}")
    return "\n".join(lines)


def count_usage_occurrences(values: Sequence[str] | Mapping[object, str]) -> int:
    if isinstance(values, Mapping):
        iterable = values.values()
    else:
        iterable = values

    total = 0
    for usage in iterable:
        for line in usage.splitlines():
            total += count_usage_line_occurrences(line)
    return total


def count_usage_line_occurrences(line: str) -> int:
    stripped = line.strip()
    if not stripped:
        return 0
    open_index = stripped.rfind("[")
    close_index = stripped.rfind("]")
    if open_index == -1 or close_index == -1 or close_index < open_index:
        raise ValueError(f"Usage line is missing bracketed verse keys: {line}")

    refs_text = stripped[open_index + 1 : close_index].strip()
    refs_total = 0
    if refs_text:
        for raw_ref in refs_text.split(";"):
            ref = raw_ref.strip()
            match = _USAGE_REF_PATTERN.fullmatch(ref)
            if match is None:
                raise ValueError(f"Invalid usage verse key token: {ref}")
            refs_total += int(match.group("count") or "1")

    suffix = stripped[close_index + 1 :].strip()
    if suffix.startswith(","):
        line_total = int(suffix[1:].strip())
        if line_total != refs_total:
            raise ValueError(
                f"Usage line total mismatch: {line_total} != {refs_total}: {line}"
            )
    return refs_total


def count_database_usage(common_db_path: Path) -> int:
    connection = sqlite3.connect(str(common_db_path))
    try:
        rows = connection.execute("SELECT usage FROM greek_words").fetchall()
    finally:
        connection.close()
    return count_usage_occurrences([str(row[0]) for row in rows])


def _replace_extended_strongs_in_text(
    text: str,
    *,
    replacement_counts: Counter[str],
    removed_counts: Counter[str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        token = normalize_strong(match.group(0))
        replacement = classic_greek_strong_or_none(token)
        if replacement is None:
            removed_counts[token] += 1
            return ""
        if replacement != token:
            replacement_counts[f"{token}->{replacement}"] += 1
        return replacement

    next_text = _STRONG_TOKEN_PATTERN.sub(replace, text)
    return re.sub(r"\s+", " ", next_text).strip()


def _validate_lxx_tr_schema(connection: sqlite3.Connection) -> None:
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(verses)")]
    if columns != ["verse_key", "text"]:
        raise ValueError(f"Unexpected LXX/TR verses schema: {columns}")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise ValueError(f"LXX/TR integrity_check failed: {integrity}")


def _validate_common_dictionary(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(greek_words)")
    }
    required = {"id", "word", "category", "synonyms", "origin", "usage"}
    missing = required - columns
    if missing:
        raise ValueError(f"Common DB greek_words missing columns: {sorted(missing)}")

    ids = [
        int(row["id"])
        for row in connection.execute("SELECT id FROM greek_words ORDER BY id")
    ]
    expected = list(range(1, CLASSIC_GREEK_STRONG_MAX + 1))
    if ids != expected:
        missing_ids = sorted(set(expected) - set(ids))
        extra_ids = sorted(set(ids) - set(expected))
        raise ValueError(
            "Common DB must contain exactly classic Greek Strong rows "
            f"G1..G{CLASSIC_GREEK_STRONG_MAX}; "
            f"missing={missing_ids[:10]}, extra={extra_ids[:10]}"
        )

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise ValueError(f"Common DB integrity_check failed: {integrity}")


def _fetch_existing_usage(connection: sqlite3.Connection) -> dict[int, str]:
    return {
        int(row["id"]): str(row["usage"] or "")
        for row in connection.execute("SELECT id, usage FROM greek_words")
    }


def _read_data_version(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT value FROM db_metadata WHERE key = ?",
        (DB_METADATA_DATA_VERSION_KEY,),
    ).fetchone()
    if row is None or not str(row["value"]).strip().isdigit():
        return "0"
    return str(row["value"]).strip()


def _set_metadata(
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


def _count_greek_words(common_db_path: Path) -> int:
    connection = sqlite3.connect(str(common_db_path))
    try:
        return int(connection.execute("SELECT COUNT(*) FROM greek_words").fetchone()[0])
    finally:
        connection.close()


def _backup_db(db_path: Path, timestamp: str) -> Path:
    backup_path = db_path.with_name(f"{db_path.name}.{_filesystem_timestamp(timestamp)}.bak")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _filesystem_timestamp(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replace LXX/TR extended Greek Strong tags with classic equivalents "
            "and rebuild revelation.sqlite greek_words.usage."
        ),
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
        default=DEFAULT_LXX_TR_DB_PATH,
        help="Path to bible_lxx_tr.sqlite.",
    )
    parser.add_argument(
        "--skip-lxx-cleanup",
        action="store_true",
        help="Do not replace extended Strong tags in bible_lxx_tr.sqlite first.",
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
    report = apply_lxx_tr_strong_usage(
        common_db_path=args.common_db,
        bible_module_path=args.bible_module,
        clean_lxx_tr_strongs=not args.skip_lxx_cleanup,
        data_version=args.data_version,
    )
    print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

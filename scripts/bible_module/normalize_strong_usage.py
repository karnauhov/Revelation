from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

try:
    from .schema import (
        DB_METADATA_DATA_VERSION_KEY,
        DB_METADATA_DATE_KEY,
        now_utc_iso,
    )
except ImportError:  # pragma: no cover - supports direct script execution.
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.bible_module.schema import (  # type: ignore[no-redef]
        DB_METADATA_DATA_VERSION_KEY,
        DB_METADATA_DATE_KEY,
        now_utc_iso,
    )


DEFAULT_COMMON_DB_PATH = Path.home() / "Documents" / "revelation" / "db" / "revelation.sqlite"
DEFAULT_WEB_DB_PATH = (
    Path(__file__).resolve().parents[2] / "web" / "db" / "revelation.sqlite"
)

_USAGE_REF_PATTERN = re.compile(
    r"^(?P<verse_key>[0-9A-Z]{3})(?:x(?P<count>[1-9][0-9]*))?$"
)
_USAGE_TOTAL_PATTERN = re.compile(r"^,\s*(?P<count>[0-9]+)$")


class UsageNormalizationError(ValueError):
    """Raised when a usage row cannot be normalized without guessing."""


class UsageMergeConflict(UsageNormalizationError):
    """Raised when the same verse has incompatible occurrence counts."""


@dataclass(frozen=True)
class ParsedUsageVariant:
    surface: str
    refs: Mapping[str, int]
    line_number: int

    @property
    def occurrences(self) -> int:
        return sum(self.refs.values())


@dataclass(frozen=True)
class VariantCountChange:
    strong_id: int
    surface: str
    before_occurrences: int
    after_occurrences: int
    removed_occurrences: int
    duplicate_reference_count: int

    def as_json(self) -> dict[str, object]:
        return {
            "strong_id": self.strong_id,
            "surface": self.surface,
            "before_occurrences": self.before_occurrences,
            "after_occurrences": self.after_occurrences,
            "removed_occurrences": self.removed_occurrences,
            "duplicate_reference_count": self.duplicate_reference_count,
        }


@dataclass(frozen=True)
class UsageNormalizationResult:
    usage: str
    before_variants: int
    after_variants: int
    before_occurrences: int
    after_occurrences: int
    merge_groups: int
    merge_operations: int
    duplicate_reference_count: int
    duplicate_reference_occurrences: int
    count_changes: tuple[VariantCountChange, ...]


@dataclass(frozen=True)
class StrongUsageNormalizationReport:
    common_db_path: Path
    web_db_path: Path | None
    backup_path: Path | None
    applied_at: str
    dry_run: bool
    vacuumed: bool
    greek_words_rows: int
    changed_usage_rows: int
    rows_with_merges: int
    rows_with_count_changes: int
    before_variants: int
    after_variants: int
    merge_groups: int
    merge_operations: int
    duplicate_reference_count: int
    duplicate_reference_occurrences: int
    before_occurrences: int
    after_occurrences: int
    occurrence_difference: int
    data_version_before: str
    data_version_after: str
    count_changes: tuple[VariantCountChange, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "common_db_path": str(self.common_db_path),
            "web_db_path": str(self.web_db_path) if self.web_db_path else None,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "applied_at": self.applied_at,
            "dry_run": self.dry_run,
            "vacuumed": self.vacuumed,
            "greek_words_rows": self.greek_words_rows,
            "changed_usage_rows": self.changed_usage_rows,
            "rows_with_merges": self.rows_with_merges,
            "rows_with_count_changes": self.rows_with_count_changes,
            "before_variants": self.before_variants,
            "after_variants": self.after_variants,
            "variant_difference": self.before_variants - self.after_variants,
            "merge_groups": self.merge_groups,
            "merge_operations": self.merge_operations,
            "duplicate_reference_count": self.duplicate_reference_count,
            "duplicate_reference_occurrences": self.duplicate_reference_occurrences,
            "before_occurrences": self.before_occurrences,
            "after_occurrences": self.after_occurrences,
            "occurrence_difference": self.occurrence_difference,
            "data_version_before": self.data_version_before,
            "data_version_after": self.data_version_after,
            "count_changes": [change.as_json() for change in self.count_changes],
        }


def parse_usage_line(
    line: str,
    *,
    strong_id: int,
    line_number: int,
) -> ParsedUsageVariant:
    stripped = line.strip()
    colon_index = stripped.find(":")
    open_index = stripped.rfind("[")
    close_index = stripped.rfind("]")
    if (
        not stripped
        or colon_index <= 0
        or open_index <= colon_index
        or close_index < open_index
    ):
        raise UsageNormalizationError(
            f"Strong G{strong_id}, usage line {line_number} has invalid format: {line!r}"
        )

    surface = unicodedata.normalize("NFC", stripped[:colon_index].strip())
    if not surface:
        raise UsageNormalizationError(
            f"Strong G{strong_id}, usage line {line_number} has an empty form"
        )

    refs_text = stripped[open_index + 1 : close_index].strip()
    if not refs_text:
        raise UsageNormalizationError(
            f"Strong G{strong_id}, usage line {line_number} has no verse references"
        )

    total_match = _USAGE_TOTAL_PATTERN.fullmatch(stripped[close_index + 1 :].strip())
    if total_match is None:
        raise UsageNormalizationError(
            f"Strong G{strong_id}, usage line {line_number} has an invalid total: {line!r}"
        )
    declared_total = int(total_match.group("count"))

    refs: Counter[str] = Counter()
    for raw_ref in refs_text.split(";"):
        ref = raw_ref.strip()
        match = _USAGE_REF_PATTERN.fullmatch(ref)
        if match is None:
            raise UsageNormalizationError(
                f"Strong G{strong_id}, usage line {line_number} has an invalid "
                f"verse reference: {ref!r}"
            )
        refs[match.group("verse_key")] += int(match.group("count") or "1")

    actual_total = sum(refs.values())
    if declared_total != actual_total:
        raise UsageNormalizationError(
            f"Strong G{strong_id}, usage line {line_number} total mismatch: "
            f"declared {declared_total}, calculated {actual_total}"
        )

    return ParsedUsageVariant(
        surface=surface,
        refs=dict(refs),
        line_number=line_number,
    )


def _format_usage_variant(surface: str, refs: Mapping[str, int]) -> str:
    ordered_refs = ";".join(
        f"{verse_key}x{count}" if count > 1 else verse_key
        for verse_key, count in sorted(refs.items())
    )
    return f"{surface}: [{ordered_refs}], {sum(refs.values())}"


def normalize_usage_text(
    usage: str,
    *,
    strong_id: int,
) -> UsageNormalizationResult:
    groups: defaultdict[str, list[ParsedUsageVariant]] = defaultdict(list)
    before_variants = 0
    before_occurrences = 0

    for line_number, line in enumerate(usage.splitlines(), 1):
        if not line.strip():
            continue
        parsed = parse_usage_line(
            line,
            strong_id=strong_id,
            line_number=line_number,
        )
        groups[parsed.surface].append(parsed)
        before_variants += 1
        before_occurrences += parsed.occurrences

    output_lines: list[str] = []
    count_changes: list[VariantCountChange] = []
    after_occurrences = 0
    merge_groups = 0
    merge_operations = 0
    duplicate_reference_count = 0
    duplicate_reference_occurrences = 0

    for surface, variants in groups.items():
        if len(variants) > 1:
            merge_groups += 1
            merge_operations += len(variants) - 1

        merged_refs: dict[str, int] = {}
        source_by_ref: dict[str, ParsedUsageVariant] = {}
        before_group_occurrences = sum(variant.occurrences for variant in variants)
        group_duplicate_reference_count = 0
        group_duplicate_reference_occurrences = 0

        for variant in variants:
            for verse_key, count in variant.refs.items():
                previous_count = merged_refs.get(verse_key)
                if previous_count is None:
                    merged_refs[verse_key] = count
                    source_by_ref[verse_key] = variant
                    continue
                if previous_count != count:
                    previous_variant = source_by_ref[verse_key]
                    raise UsageMergeConflict(
                        f"Strong G{strong_id}, normalized form {surface!r} has "
                        f"conflicting counts for verse {verse_key}: "
                        f"{previous_count} on line {previous_variant.line_number} "
                        f"and {count} on line {variant.line_number}"
                    )
                group_duplicate_reference_count += 1
                group_duplicate_reference_occurrences += count

        group_after_occurrences = sum(merged_refs.values())
        if before_group_occurrences != (
            group_after_occurrences + group_duplicate_reference_occurrences
        ):
            raise UsageNormalizationError(
                f"Strong G{strong_id}, normalized form {surface!r} failed "
                "the occurrence conservation check"
            )

        if group_duplicate_reference_occurrences:
            count_changes.append(
                VariantCountChange(
                    strong_id=strong_id,
                    surface=surface,
                    before_occurrences=before_group_occurrences,
                    after_occurrences=group_after_occurrences,
                    removed_occurrences=group_duplicate_reference_occurrences,
                    duplicate_reference_count=group_duplicate_reference_count,
                )
            )

        after_occurrences += group_after_occurrences
        duplicate_reference_count += group_duplicate_reference_count
        duplicate_reference_occurrences += group_duplicate_reference_occurrences
        output_lines.append(_format_usage_variant(surface, merged_refs))

    output_lines.sort(key=lambda line: (line.split(":", 1)[0].casefold(), line))
    normalized_usage = "\n".join(output_lines)
    after_variants = len(output_lines)

    if before_occurrences != after_occurrences + duplicate_reference_occurrences:
        raise UsageNormalizationError(
            f"Strong G{strong_id} failed the database-wide occurrence conservation check"
        )
    if duplicate_reference_occurrences == 0 and before_occurrences != after_occurrences:
        raise UsageNormalizationError(
            f"Strong G{strong_id} changed occurrence sum without duplicate references"
        )

    # Parse the generated text once more. This verifies that every emitted line,
    # reference, xN count, and total is valid and that emitted references are unique.
    roundtrip_occurrences = 0
    roundtrip_variants = 0
    for line_number, line in enumerate(normalized_usage.splitlines(), 1):
        parsed = parse_usage_line(
            line,
            strong_id=strong_id,
            line_number=line_number,
        )
        if len(parsed.refs) != len(set(parsed.refs)):
            raise UsageNormalizationError(
                f"Strong G{strong_id} emitted duplicate verse references"
            )
        roundtrip_occurrences += parsed.occurrences
        roundtrip_variants += 1
    if roundtrip_occurrences != after_occurrences or roundtrip_variants != after_variants:
        raise UsageNormalizationError(
            f"Strong G{strong_id} failed the normalized usage roundtrip check"
        )

    return UsageNormalizationResult(
        usage=normalized_usage,
        before_variants=before_variants,
        after_variants=after_variants,
        before_occurrences=before_occurrences,
        after_occurrences=after_occurrences,
        merge_groups=merge_groups,
        merge_operations=merge_operations,
        duplicate_reference_count=duplicate_reference_count,
        duplicate_reference_occurrences=duplicate_reference_occurrences,
        count_changes=tuple(count_changes),
    )


def _validate_common_dictionary(connection: sqlite3.Connection) -> None:
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    required_tables = {"db_metadata", "greek_words"}
    missing_tables = required_tables - tables
    if missing_tables:
        raise UsageNormalizationError(
            f"Common dictionary is missing tables: {sorted(missing_tables)}"
        )

    columns = {
        str(row[1]) for row in connection.execute("PRAGMA table_info(greek_words)")
    }
    required_columns = {"id", "usage"}
    missing_columns = required_columns - columns
    if missing_columns:
        raise UsageNormalizationError(
            f"greek_words is missing columns: {sorted(missing_columns)}"
        )

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise UsageNormalizationError(f"Common dictionary integrity_check failed: {integrity}")

    ids = [
        int(row[0])
        for row in connection.execute("SELECT id FROM greek_words ORDER BY id")
    ]
    if any(strong_id <= 0 for strong_id in ids) or ids != sorted(set(ids)):
        raise UsageNormalizationError("greek_words ids must be positive and unique")


def _read_data_version(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT value FROM db_metadata WHERE key = ?",
        (DB_METADATA_DATA_VERSION_KEY,),
    ).fetchone()
    if row is None or not str(row[0]).strip().isdigit():
        return "0"
    return str(row[0]).strip()


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


def _backup_db(db_path: Path, timestamp: str) -> Path:
    filesystem_timestamp = "".join(
        character if character.isalnum() else "-" for character in timestamp
    )
    backup_path = db_path.with_name(f"{db_path.name}.{filesystem_timestamp}.bak")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _vacuum_db(db_path: Path) -> None:
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute("VACUUM")
    finally:
        connection.close()


def _aggregate_results(
    results: Sequence[UsageNormalizationResult],
) -> dict[str, object]:
    count_changes = tuple(
        change for result in results for change in result.count_changes
    )
    return {
        "before_variants": sum(result.before_variants for result in results),
        "after_variants": sum(result.after_variants for result in results),
        "before_occurrences": sum(result.before_occurrences for result in results),
        "after_occurrences": sum(result.after_occurrences for result in results),
        "merge_groups": sum(result.merge_groups for result in results),
        "merge_operations": sum(result.merge_operations for result in results),
        "duplicate_reference_count": sum(
            result.duplicate_reference_count for result in results
        ),
        "duplicate_reference_occurrences": sum(
            result.duplicate_reference_occurrences for result in results
        ),
        "rows_with_merges": sum(result.merge_groups > 0 for result in results),
        "rows_with_count_changes": sum(bool(result.count_changes) for result in results),
        "count_changes": count_changes,
    }


def apply_strong_usage_normalization(
    *,
    common_db_path: Path = DEFAULT_COMMON_DB_PATH,
    web_db_path: Path | None = None,
    dry_run: bool = False,
    vacuum: bool = False,
    applied_at: str | None = None,
) -> StrongUsageNormalizationReport:
    common_db_path = common_db_path.resolve()
    web_db_path = web_db_path.resolve() if web_db_path else None
    applied_at = applied_at or now_utc_iso()
    if not common_db_path.exists():
        raise FileNotFoundError(f"Common dictionary DB not found: {common_db_path}")
    if web_db_path and web_db_path == common_db_path:
        raise ValueError("Web DB path must differ from the common DB path")

    connection = sqlite3.connect(str(common_db_path))
    backup_path: Path | None = None
    try:
        connection.row_factory = sqlite3.Row
        _validate_common_dictionary(connection)
        data_version_before = _read_data_version(connection)
        rows = list(
            connection.execute("SELECT id, usage FROM greek_words ORDER BY id")
        )

        updates: list[tuple[str, int]] = []
        results: list[UsageNormalizationResult] = []
        for row in rows:
            strong_id = int(row["id"])
            current_usage = str(row["usage"] or "")
            result = normalize_usage_text(current_usage, strong_id=strong_id)
            results.append(result)
            if result.usage != current_usage:
                updates.append((result.usage, strong_id))

        aggregates = _aggregate_results(results)
        changed_usage_rows = len(updates)
        should_update = not dry_run and bool(updates)
        data_version_after = (
            str(int(data_version_before) + 1)
            if should_update
            else data_version_before
        )

        if should_update:
            backup_path = _backup_db(common_db_path, applied_at)
            try:
                with connection:
                    connection.executemany(
                        "UPDATE greek_words SET usage = ? WHERE id = ?",
                        updates,
                    )
                    _set_metadata(
                        connection,
                        data_version=data_version_after,
                        date_iso=applied_at,
                    )
            except Exception:
                connection.close()
                shutil.copy2(backup_path, common_db_path)
                raise
    finally:
        connection.close()

    vacuumed = False
    if vacuum and not dry_run and should_update:
        try:
            _vacuum_db(common_db_path)
            vacuumed = True
        except Exception:
            if backup_path:
                shutil.copy2(backup_path, common_db_path)
            raise

    # Re-open and verify the persisted result before copying it to web/db.
    verification_connection = sqlite3.connect(str(common_db_path))
    try:
        verification_connection.row_factory = sqlite3.Row
        _validate_common_dictionary(verification_connection)
        persisted_rows = list(
            verification_connection.execute(
                "SELECT id, usage FROM greek_words ORDER BY id"
            )
        )
        if not dry_run:
            for row, result in zip(persisted_rows, results, strict=True):
                if str(row["usage"] or "") != result.usage:
                    raise UsageNormalizationError(
                        f"Persisted usage verification failed for Strong G{row['id']}"
                    )
    finally:
        verification_connection.close()

    copied_web_db: Path | None = None
    if web_db_path and not dry_run:
        web_db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(common_db_path, web_db_path)
        copied_web_db = web_db_path

    return StrongUsageNormalizationReport(
        common_db_path=common_db_path,
        web_db_path=copied_web_db,
        backup_path=backup_path,
        applied_at=applied_at,
        dry_run=dry_run,
        vacuumed=vacuumed,
        greek_words_rows=len(rows),
        changed_usage_rows=changed_usage_rows,
        rows_with_merges=int(aggregates["rows_with_merges"]),
        rows_with_count_changes=int(aggregates["rows_with_count_changes"]),
        before_variants=int(aggregates["before_variants"]),
        after_variants=int(aggregates["after_variants"]),
        merge_groups=int(aggregates["merge_groups"]),
        merge_operations=int(aggregates["merge_operations"]),
        duplicate_reference_count=int(aggregates["duplicate_reference_count"]),
        duplicate_reference_occurrences=int(
            aggregates["duplicate_reference_occurrences"]
        ),
        before_occurrences=int(aggregates["before_occurrences"]),
        after_occurrences=int(aggregates["after_occurrences"]),
        occurrence_difference=int(aggregates["before_occurrences"])
        - int(aggregates["after_occurrences"]),
        data_version_before=data_version_before,
        data_version_after=data_version_after,
        count_changes=aggregates["count_changes"],  # type: ignore[arg-type]
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize Unicode NFC forms in greek_words.usage, merge duplicate "
            "forms and references, validate occurrence conservation, and sort output."
        )
    )
    parser.add_argument(
        "--common-db",
        type=Path,
        default=DEFAULT_COMMON_DB_PATH,
        help="Path to the common revelation.sqlite database.",
    )
    parser.add_argument(
        "--web-db",
        type=Path,
        default=None,
        help="Optional destination to replace after successful validation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and print the report without changing or copying any database.",
    )
    parser.add_argument(
        "--vacuum",
        action="store_true",
        help="Run SQLite VACUUM after the update and before copying the web database.",
    )
    parser.add_argument(
        "--applied-at",
        default=None,
        help="Optional UTC timestamp for metadata and backup naming.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    report = apply_strong_usage_normalization(
        common_db_path=args.common_db,
        web_db_path=args.web_db,
        dry_run=args.dry_run,
        vacuum=args.vacuum,
        applied_at=args.applied_at,
    )
    print(json.dumps(report.as_json(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

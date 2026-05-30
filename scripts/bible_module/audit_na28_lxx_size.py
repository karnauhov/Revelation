from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from .build_na28_lxx import DEFAULT_TARGET_PATH


@dataclass(frozen=True)
class ColumnAudit:
    name: str
    declared_type: str
    not_null: bool
    primary_key_position: int
    default_value: str | None
    text_bytes: int | None
    text_average_bytes: float | None
    text_max_bytes: int | None


@dataclass(frozen=True)
class TableAudit:
    name: str
    row_count: int
    text_bytes: int
    isolated_size_bytes: int | None
    columns: tuple[ColumnAudit, ...]


@dataclass(frozen=True)
class IndexAudit:
    name: str
    table_name: str
    unique: bool
    origin: str
    partial: bool
    columns: tuple[str, ...]
    is_explicit: bool
    isolated_size_bytes: int | None


@dataclass(frozen=True)
class ScenarioAudit:
    name: str
    size_bytes: int | None
    saved_bytes: int | None
    error: str | None


@dataclass(frozen=True)
class BibleModuleSizeAudit:
    db_path: str
    file_size_bytes: int
    page_size: int
    page_count: int
    freelist_count: int
    user_version: int
    tables: tuple[TableAudit, ...]
    indexes: tuple[IndexAudit, ...]
    scenarios: tuple[ScenarioAudit, ...]


def audit_bible_module_size(
    db_path: Path,
    *,
    include_deep_estimates: bool = False,
    include_scenarios: bool = False,
) -> BibleModuleSizeAudit:
    db_path = db_path.resolve()
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        table_names = _table_names(connection)
        table_sizes = (
            _estimate_isolated_table_sizes(db_path, table_names)
            if include_deep_estimates
            else {}
        )
        explicit_index_sizes = (
            _estimate_explicit_index_sizes(db_path, table_names)
            if include_deep_estimates
            else {}
        )
        tables = tuple(
            _audit_table(
                connection,
                table_name,
                isolated_size_bytes=table_sizes.get(table_name),
            )
            for table_name in table_names
        )
        indexes = tuple(
            _audit_index(
                connection,
                table_name,
                index_row,
                isolated_size_bytes=explicit_index_sizes.get(str(index_row["name"])),
            )
            for table_name in table_names
            for index_row in connection.execute(
                f"PRAGMA index_list({_quote_identifier(table_name)})"
            )
        )
        scenarios = _estimate_scenarios(db_path) if include_scenarios else tuple()
        return BibleModuleSizeAudit(
            db_path=str(db_path),
            file_size_bytes=db_path.stat().st_size,
            page_size=int(connection.execute("PRAGMA page_size").fetchone()[0]),
            page_count=int(connection.execute("PRAGMA page_count").fetchone()[0]),
            freelist_count=int(connection.execute("PRAGMA freelist_count").fetchone()[0]),
            user_version=int(connection.execute("PRAGMA user_version").fetchone()[0]),
            tables=tables,
            indexes=indexes,
            scenarios=scenarios,
        )
    finally:
        connection.close()


def render_markdown_report(audit: BibleModuleSizeAudit) -> str:
    lines = [
        "# NA28_LXX Bible Module Size Audit",
        "",
        f"- DB: `{audit.db_path}`",
        f"- File size: {_format_bytes(audit.file_size_bytes)}",
        f"- Page size: {audit.page_size}",
        f"- Page count: {audit.page_count}",
        f"- Free pages: {audit.freelist_count}",
        f"- SQLite user_version: {audit.user_version}",
        "",
        "## Tables",
        "",
        "| Table | Rows | Text payload | Isolated size |",
        "| --- | ---: | ---: | ---: |",
    ]
    for table in sorted(audit.tables, key=lambda item: item.text_bytes, reverse=True):
        lines.append(
            "| "
            + " | ".join(
                [
                    table.name,
                    str(table.row_count),
                    _format_bytes(table.text_bytes),
                    _format_optional_bytes(table.isolated_size_bytes),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Indexes",
            "",
            "| Index | Table | Kind | Columns | Isolated size |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for index in sorted(audit.indexes, key=lambda item: (item.table_name, item.name)):
        kind = "explicit" if index.is_explicit else f"auto/{index.origin}"
        lines.append(
            "| "
            + " | ".join(
                [
                    index.name,
                    index.table_name,
                    kind,
                    ", ".join(index.columns),
                    _format_optional_bytes(index.isolated_size_bytes),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Large Text Columns",
            "",
            "| Table | Column | Total | Avg | Max |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    text_columns = [
        (table.name, column)
        for table in audit.tables
        for column in table.columns
        if column.text_bytes is not None and column.text_bytes > 0
    ]
    for table_name, column in sorted(
        text_columns,
        key=lambda item: item[1].text_bytes or 0,
        reverse=True,
    ):
        lines.append(
            "| "
            + " | ".join(
                [
                    table_name,
                    column.name,
                    _format_bytes(column.text_bytes or 0),
                    f"{column.text_average_bytes or 0:.2f}",
                    str(column.text_max_bytes or 0),
                ]
            )
            + " |"
        )

    if audit.scenarios:
        lines.extend(
            [
                "",
                "## Temporary Pruning Scenarios",
                "",
                "| Scenario | Size | Saved | Error |",
                "| --- | ---: | ---: | --- |",
            ]
        )
        for scenario in audit.scenarios:
            lines.append(
                "| "
                + " | ".join(
                    [
                        scenario.name,
                        _format_optional_bytes(scenario.size_bytes),
                        _format_optional_bytes(scenario.saved_bytes),
                        scenario.error or "",
                    ]
                )
                + " |"
            )

    return "\n".join(lines) + "\n"


def audit_to_json(audit: BibleModuleSizeAudit) -> str:
    return json.dumps(asdict(audit), ensure_ascii=False, indent=2)


def _table_names(connection: sqlite3.Connection) -> tuple[str, ...]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return tuple(str(row["name"]) for row in rows)


def _audit_table(
    connection: sqlite3.Connection,
    table_name: str,
    *,
    isolated_size_bytes: int | None,
) -> TableAudit:
    row_count = int(
        connection.execute(
            f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}"
        ).fetchone()[0]
    )
    columns = tuple(
        _audit_column(connection, table_name, row)
        for row in _table_info(connection, table_name)
    )
    return TableAudit(
        name=table_name,
        row_count=row_count,
        text_bytes=sum(column.text_bytes or 0 for column in columns),
        isolated_size_bytes=isolated_size_bytes,
        columns=columns,
    )


def _audit_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_row: sqlite3.Row,
) -> ColumnAudit:
    name = str(column_row["name"])
    declared_type = str(column_row["type"])
    text_stats: tuple[int, float, int] | None = None
    if "TEXT" in declared_type.upper():
        quoted_table = _quote_identifier(table_name)
        quoted_column = _quote_identifier(name)
        row = connection.execute(
            f"""
            SELECT
              COALESCE(SUM(LENGTH({quoted_column})), 0),
              COALESCE(AVG(LENGTH({quoted_column})), 0),
              COALESCE(MAX(LENGTH({quoted_column})), 0)
            FROM {quoted_table}
            """
        ).fetchone()
        text_stats = (int(row[0]), float(row[1]), int(row[2]))

    return ColumnAudit(
        name=name,
        declared_type=declared_type,
        not_null=bool(column_row["notnull"]),
        primary_key_position=int(column_row["pk"]),
        default_value=(
            None
            if column_row["dflt_value"] is None
            else str(column_row["dflt_value"])
        ),
        text_bytes=None if text_stats is None else text_stats[0],
        text_average_bytes=None if text_stats is None else text_stats[1],
        text_max_bytes=None if text_stats is None else text_stats[2],
    )


def _table_info(
    connection: sqlite3.Connection,
    table_name: str,
) -> tuple[sqlite3.Row, ...]:
    return tuple(
        connection.execute(f"PRAGMA table_info({_quote_identifier(table_name)})")
    )


def _audit_index(
    connection: sqlite3.Connection,
    table_name: str,
    index_row: sqlite3.Row,
    *,
    isolated_size_bytes: int | None,
) -> IndexAudit:
    name = str(index_row["name"])
    column_rows = connection.execute(
        f"PRAGMA index_info({_quote_identifier(name)})"
    ).fetchall()
    return IndexAudit(
        name=name,
        table_name=table_name,
        unique=bool(index_row["unique"]),
        origin=str(index_row["origin"]),
        partial=bool(index_row["partial"]),
        columns=tuple(str(row["name"]) for row in column_rows),
        is_explicit=str(index_row["origin"]) == "c",
        isolated_size_bytes=isolated_size_bytes,
    )


def _estimate_isolated_table_sizes(
    db_path: Path,
    table_names: Sequence[str],
) -> dict[str, int]:
    return {
        table_name: _estimate_single_table_size(db_path, table_name)
        for table_name in table_names
    }


def _estimate_single_table_size(db_path: Path, table_name: str) -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "table.sqlite"
        connection = sqlite3.connect(str(temp_path))
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("ATTACH DATABASE ? AS src", (str(db_path),))
            create_sql = connection.execute(
                """
                SELECT sql
                FROM src.sqlite_master
                WHERE type = 'table'
                  AND name = ?
                """,
                (table_name,),
            ).fetchone()["sql"]
            connection.execute(str(create_sql))
            connection.execute(
                f"""
                INSERT INTO {_quote_identifier(table_name)}
                SELECT *
                FROM src.{_quote_identifier(table_name)}
                """
            )
            connection.commit()
            connection.execute("VACUUM")
        finally:
            connection.close()
        return temp_path.stat().st_size


def _estimate_explicit_index_sizes(
    db_path: Path,
    table_names: Sequence[str],
) -> dict[str, int]:
    sizes: dict[str, int] = {}
    source = sqlite3.connect(str(db_path))
    source.row_factory = sqlite3.Row
    try:
        for table_name in table_names:
            rows = source.execute(
                """
                SELECT name, sql
                FROM sqlite_master
                WHERE type = 'index'
                  AND tbl_name = ?
                  AND sql IS NOT NULL
                ORDER BY name
                """,
                (table_name,),
            ).fetchall()
            if not rows:
                continue
            table_only_size = _estimate_single_table_size(db_path, table_name)
            for row in rows:
                sizes[str(row["name"])] = _estimate_single_index_size(
                    db_path,
                    table_name,
                    str(row["sql"]),
                    table_only_size,
                )
    finally:
        source.close()
    return sizes


def _estimate_single_index_size(
    db_path: Path,
    table_name: str,
    index_sql: str,
    table_only_size: int,
) -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "index.sqlite"
        connection = sqlite3.connect(str(temp_path))
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("ATTACH DATABASE ? AS src", (str(db_path),))
            create_sql = connection.execute(
                """
                SELECT sql
                FROM src.sqlite_master
                WHERE type = 'table'
                  AND name = ?
                """,
                (table_name,),
            ).fetchone()["sql"]
            connection.execute(str(create_sql))
            connection.execute(
                f"""
                INSERT INTO {_quote_identifier(table_name)}
                SELECT *
                FROM src.{_quote_identifier(table_name)}
                """
            )
            connection.execute(index_sql)
            connection.commit()
            connection.execute("VACUUM")
        finally:
            connection.close()
        return max(0, temp_path.stat().st_size - table_only_size)


def _estimate_scenarios(db_path: Path) -> tuple[ScenarioAudit, ...]:
    scenarios: Mapping[str, Callable[[sqlite3.Connection], None]] = {
        "drop_import_warnings": _drop_import_warnings,
        "drop_token_raw_json": _drop_token_raw_json,
        "drop_token_and_warning_raw_json": _drop_token_and_warning_raw_json,
        "drop_tokens_token_strongs_import_warnings": (
            _drop_tokens_token_strongs_import_warnings
        ),
        "usage_source_compact_for_phase12": _make_usage_source_compact,
        "runtime_minimum_no_tokens_warnings_or_text_display": (
            _make_runtime_minimum_no_tokens_warnings_or_text_display
        ),
    }
    return tuple(
        _estimate_scenario(db_path, name, action)
        for name, action in scenarios.items()
    )


def _estimate_scenario(
    db_path: Path,
    name: str,
    action: Callable[[sqlite3.Connection], None],
) -> ScenarioAudit:
    source_size = db_path.stat().st_size
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / f"{name}.sqlite"
        shutil.copy2(db_path, temp_path)
        connection = sqlite3.connect(str(temp_path))
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            action(connection)
            connection.commit()
            connection.execute("VACUUM")
            connection.execute("ANALYZE")
        except Exception as error:  # pragma: no cover - depends on sqlite build.
            connection.rollback()
            return ScenarioAudit(
                name=name,
                size_bytes=None,
                saved_bytes=None,
                error=str(error),
            )
        finally:
            connection.close()
        size = temp_path.stat().st_size
        return ScenarioAudit(
            name=name,
            size_bytes=size,
            saved_bytes=source_size - size,
            error=None,
        )


def _drop_import_warnings(connection: sqlite3.Connection) -> None:
    connection.execute("DROP TABLE IF EXISTS import_warnings")


def _drop_token_raw_json(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE tokens DROP COLUMN raw_json")


def _drop_token_and_warning_raw_json(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE tokens DROP COLUMN raw_json")
    connection.execute("ALTER TABLE import_warnings DROP COLUMN raw_json")


def _drop_tokens_token_strongs_import_warnings(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP TABLE IF EXISTS token_strongs;
        DROP TABLE IF EXISTS tokens;
        DROP TABLE IF EXISTS import_warnings;
        """
    )


def _make_usage_source_compact(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP INDEX IF EXISTS idx_tokens_module_verse_token_order;
        DROP INDEX IF EXISTS idx_token_strongs_strong;
        DROP INDEX IF EXISTS idx_token_strongs_token_id;

        ALTER TABLE tokens RENAME TO tokens_full;
        CREATE TABLE tokens (
          token_id INTEGER PRIMARY KEY,
          module_verse_id INTEGER NOT NULL,
          token_order INTEGER NOT NULL,
          surface TEXT NOT NULL,
          surface_normalized TEXT NOT NULL,
          surface_search TEXT NOT NULL
        );
        INSERT INTO tokens(
          token_id,
          module_verse_id,
          token_order,
          surface,
          surface_normalized,
          surface_search
        )
        SELECT
          token_id,
          module_verse_id,
          token_order,
          surface,
          surface_normalized,
          surface_search
        FROM tokens_full;
        DROP TABLE tokens_full;

        ALTER TABLE token_strongs RENAME TO token_strongs_full;
        CREATE TABLE token_strongs (
          token_strong_id INTEGER PRIMARY KEY,
          token_id INTEGER NOT NULL,
          strong TEXT NOT NULL,
          raw_strong TEXT NOT NULL,
          role TEXT NOT NULL,
          is_primary INTEGER NOT NULL
        );
        INSERT INTO token_strongs(
          token_strong_id,
          token_id,
          strong,
          raw_strong,
          role,
          is_primary
        )
        SELECT
          token_strong_id,
          token_id,
          strong,
          raw_strong,
          role,
          is_primary
        FROM token_strongs_full;
        DROP TABLE token_strongs_full;

        DROP TABLE IF EXISTS import_warnings;

        CREATE INDEX idx_tokens_module_verse_token_order
          ON tokens(module_verse_id, token_order);
        CREATE INDEX idx_token_strongs_strong
          ON token_strongs(strong);
        CREATE INDEX idx_token_strongs_token_id
          ON token_strongs(token_id);
        """
    )


def _make_runtime_minimum_no_tokens_warnings_or_text_display(
    connection: sqlite3.Connection,
) -> None:
    _drop_tokens_token_strongs_import_warnings(connection)
    connection.executescript(
        """
        ALTER TABLE module_verses RENAME TO module_verses_full;
        CREATE TABLE module_verses (
          module_verse_id INTEGER PRIMARY KEY,
          source_text_id TEXT NOT NULL,
          native_ref TEXT NOT NULL,
          book_id INTEGER NOT NULL,
          chapter INTEGER NOT NULL,
          verse INTEGER NOT NULL,
          subverse TEXT NOT NULL DEFAULT '',
          text_plain TEXT NOT NULL,
          tokens_count INTEGER NOT NULL,
          sort_key INTEGER NOT NULL,
          UNIQUE (source_text_id, native_ref)
        );
        INSERT INTO module_verses(
          module_verse_id,
          source_text_id,
          native_ref,
          book_id,
          chapter,
          verse,
          subverse,
          text_plain,
          tokens_count,
          sort_key
        )
        SELECT
          module_verse_id,
          source_text_id,
          native_ref,
          book_id,
          chapter,
          verse,
          subverse,
          text_plain,
          tokens_count,
          sort_key
        FROM module_verses_full;
        DROP TABLE module_verses_full;
        CREATE INDEX idx_module_verses_source_text_sort_key
          ON module_verses(source_text_id, sort_key);
        """
    )


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _format_bytes(value: int) -> str:
    mib = value / (1024 * 1024)
    return f"{value} ({mib:.2f} MiB)"


def _format_optional_bytes(value: int | None) -> str:
    return "" if value is None else _format_bytes(value)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit NA28_LXX Bible module SQLite size and pruning options.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_TARGET_PATH,
        help="Bible module SQLite file to audit.",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Estimate isolated table and explicit index sizes using temporary copies.",
    )
    parser.add_argument(
        "--scenarios",
        action="store_true",
        help="Estimate temporary pruning scenarios using copies of the DB.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    audit = audit_bible_module_size(
        args.db,
        include_deep_estimates=args.deep,
        include_scenarios=args.scenarios,
    )
    if args.format == "markdown":
        print(render_markdown_report(audit), end="")
    else:
        print(audit_to_json(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

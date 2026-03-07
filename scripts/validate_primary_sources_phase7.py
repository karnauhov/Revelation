#!/usr/bin/env python3
"""Validate Primary Sources migration state for Phase 7."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


EXPECTED_SOURCE_COUNT = 19
EXPECTED_GROUP_COUNTS = {
    "full": 3,
    "significant": 4,
    "fragment": 12,
}
EXPECTED_PAGE_COUNT = 232
EXPECTED_WORD_COUNT = 156
EXPECTED_RECTANGLE_COUNT = 172
EXPECTED_VERSE_COUNT = 8
EXPECTED_FALSE_CAN_SHOW_IMAGES = 6
EXPECTED_ZERO_PAGE_SOURCES = {"U025", "U052"}
EXPECTED_OVERLAY_SOURCES = {"U001", "U002", "U004"}
EXPECTED_LOCALES = ("en", "es", "uk", "ru")


@dataclass
class ValidationCheck:
    key: str
    ok: bool
    details: str


def get_windows_documents_dir() -> Path | None:
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "Personal")
        if isinstance(value, str) and value.strip():
            return Path(os.path.expandvars(value.strip()))
    except Exception:
        pass

    one_drive = os.environ.get("OneDrive")
    if one_drive:
        return Path(one_drive) / "Documents"
    return None


def get_documents_dir() -> Path:
    system = platform.system()
    home = Path.home()
    if system == "Windows":
        docs = get_windows_documents_dir()
        if docs is not None:
            return docs
        profile = os.environ.get("USERPROFILE")
        return Path(profile) / "Documents" if profile else home / "Documents"
    if system == "Linux":
        try:
            result = subprocess.run(
                ["xdg-user-dir", "DOCUMENTS"],
                capture_output=True,
                text=True,
                check=False,
            )
            value = result.stdout.strip()
            if result.returncode == 0 and value:
                return Path(value)
        except OSError:
            pass
    return home / "Documents"


def default_db_dir() -> Path:
    return get_documents_dir() / "revelation" / "db"


def fetch_scalar(connection: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    row = connection.execute(sql, params).fetchone()
    return int(row[0] or 0) if row is not None else 0


def load_json_list(raw: str) -> list[object]:
    payload = json.loads(raw or "[]")
    if not isinstance(payload, list):
        raise ValueError("JSON value is not a list.")
    return payload


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def code_contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except OSError:
        return False


def validate_common_counts(common_connection: sqlite3.Connection) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []

    source_count = fetch_scalar(common_connection, "SELECT COUNT(*) FROM primary_sources")
    checks.append(
        ValidationCheck(
            key="source_count",
            ok=source_count == EXPECTED_SOURCE_COUNT,
            details=f"expected={EXPECTED_SOURCE_COUNT}, actual={source_count}",
        )
    )

    actual_group_counts = {
        row[0]: int(row[1] or 0)
        for row in common_connection.execute(
            "SELECT group_kind, COUNT(*) FROM primary_sources GROUP BY group_kind"
        ).fetchall()
    }
    checks.append(
        ValidationCheck(
            key="group_counts",
            ok=actual_group_counts == EXPECTED_GROUP_COUNTS,
            details=f"expected={EXPECTED_GROUP_COUNTS}, actual={actual_group_counts}",
        )
    )

    page_count = fetch_scalar(common_connection, "SELECT COUNT(*) FROM primary_source_pages")
    checks.append(
        ValidationCheck(
            key="page_count",
            ok=page_count == EXPECTED_PAGE_COUNT,
            details=f"expected={EXPECTED_PAGE_COUNT}, actual={page_count}",
        )
    )

    word_count = fetch_scalar(common_connection, "SELECT COUNT(*) FROM primary_source_words")
    checks.append(
        ValidationCheck(
            key="word_count",
            ok=word_count == EXPECTED_WORD_COUNT,
            details=f"expected={EXPECTED_WORD_COUNT}, actual={word_count}",
        )
    )

    rectangle_total = 0
    rectangle_errors: list[str] = []
    for source_id, page_name, word_index, rectangles_json in common_connection.execute(
        """
        SELECT source_id, page_name, word_index, rectangles_json
        FROM primary_source_words
        ORDER BY source_id, page_name, word_index
        """
    ).fetchall():
        try:
            rectangles = load_json_list(rectangles_json or "[]")
        except Exception as exc:
            rectangle_errors.append(
                f"{source_id}/{page_name}/word#{word_index}: rectangles_json parse error ({exc})"
            )
            continue
        rectangle_total += len(rectangles)
    checks.append(
        ValidationCheck(
            key="rectangle_count",
            ok=rectangle_total == EXPECTED_RECTANGLE_COUNT and not rectangle_errors,
            details=(
                f"expected={EXPECTED_RECTANGLE_COUNT}, actual={rectangle_total}"
                if not rectangle_errors
                else f"expected={EXPECTED_RECTANGLE_COUNT}, actual={rectangle_total}, errors={rectangle_errors[:3]}"
            ),
        )
    )

    verse_count = fetch_scalar(common_connection, "SELECT COUNT(*) FROM primary_source_verses")
    checks.append(
        ValidationCheck(
            key="verse_count",
            ok=verse_count == EXPECTED_VERSE_COUNT,
            details=f"expected={EXPECTED_VERSE_COUNT}, actual={verse_count}",
        )
    )
    return checks


def validate_preview_resources(common_connection: sqlite3.Connection) -> ValidationCheck:
    missing = [
        row[0]
        for row in common_connection.execute(
            """
            SELECT ps.id
            FROM primary_sources ps
            LEFT JOIN common_resources cr ON cr.key = ps.preview_resource_key
            WHERE cr.key IS NULL
            ORDER BY ps.id
            """
        ).fetchall()
    ]
    preview_count = fetch_scalar(
        common_connection,
        "SELECT COUNT(*) FROM common_resources WHERE key LIKE 'primary_sources/previews/%'",
    )
    return ValidationCheck(
        key="preview_resources",
        ok=not missing and preview_count == EXPECTED_SOURCE_COUNT,
        details=f"preview_count={preview_count}, missing={missing}",
    )


def validate_overlay_integrity(common_connection: sqlite3.Connection) -> ValidationCheck:
    sources_with_words = {
        row[0]
        for row in common_connection.execute(
            "SELECT DISTINCT source_id FROM primary_source_words ORDER BY source_id"
        ).fetchall()
    }
    sources_with_verses = {
        row[0]
        for row in common_connection.execute(
            "SELECT DISTINCT source_id FROM primary_source_verses ORDER BY source_id"
        ).fetchall()
    }
    issues: list[str] = []

    page_words: dict[tuple[str, str], set[int]] = {}
    for source_id, page_name, word_index in common_connection.execute(
        "SELECT source_id, page_name, word_index FROM primary_source_words"
    ).fetchall():
        page_words.setdefault((source_id, page_name), set()).add(int(word_index))

    for source_id, page_name, verse_index, word_indexes_json, contours_json in common_connection.execute(
        """
        SELECT source_id, page_name, verse_index, word_indexes_json, contours_json
        FROM primary_source_verses
        ORDER BY source_id, page_name, verse_index
        """
    ).fetchall():
        try:
            word_indexes = [int(value) for value in load_json_list(word_indexes_json or "[]")]
            contours = load_json_list(contours_json or "[]")
        except Exception as exc:
            issues.append(f"{source_id}/{page_name}/verse#{verse_index}: parse error ({exc})")
            continue
        known_words = page_words.get((source_id, page_name), set())
        missing_words = [value for value in word_indexes if value not in known_words]
        if missing_words:
            issues.append(
                f"{source_id}/{page_name}/verse#{verse_index}: missing word indexes {missing_words}"
            )
        if not contours:
            issues.append(f"{source_id}/{page_name}/verse#{verse_index}: empty contours")

    ok = (
        sources_with_words == EXPECTED_OVERLAY_SOURCES
        and sources_with_verses == EXPECTED_OVERLAY_SOURCES
        and not issues
    )
    details = (
        f"sources_with_words={sorted(sources_with_words)}, "
        f"sources_with_verses={sorted(sources_with_verses)}, "
        f"issues={issues[:5]}"
    )
    return ValidationCheck(key="overlay_navigation", ok=ok, details=details)


def validate_can_show_images(common_connection: sqlite3.Connection) -> ValidationCheck:
    false_count = fetch_scalar(
        common_connection,
        "SELECT COUNT(*) FROM primary_sources WHERE can_show_images = 0",
    )
    false_ids = [
        row[0]
        for row in common_connection.execute(
            "SELECT id FROM primary_sources WHERE can_show_images = 0 ORDER BY id"
        ).fetchall()
    ]
    root = project_root()
    runtime_guards_ok = all(
        [
            code_contains(
                root / "lib" / "repositories" / "primary_sources_db_repository.dart",
                "permissionsReceived: sourceRow.canShowImages",
            ),
            code_contains(
                root / "lib" / "viewmodels" / "primary_source_view_model.dart",
                "if (primarySource.pages.isNotEmpty && primarySource.permissionsReceived)",
            ),
            code_contains(
                root / "lib" / "screens" / "primary_source" / "primary_source_toolbar.dart",
                "primarySource.pages.isEmpty || !primarySource.permissionsReceived",
            ),
        ]
    )
    return ValidationCheck(
        key="can_show_images_runtime",
        ok=false_count == EXPECTED_FALSE_CAN_SHOW_IMAGES and runtime_guards_ok,
        details=(
            f"false_count={false_count}, false_ids={false_ids}, "
            f"runtime_guards_ok={runtime_guards_ok}"
        ),
    )


def validate_zero_page_sources(common_connection: sqlite3.Connection) -> ValidationCheck:
    zero_page_sources = {
        row[0]
        for row in common_connection.execute(
            """
            SELECT ps.id
            FROM primary_sources ps
            LEFT JOIN primary_source_pages pp ON pp.source_id = ps.id
            GROUP BY ps.id
            HAVING COUNT(pp.page_name) = 0
            ORDER BY ps.id
            """
        ).fetchall()
    }
    root = project_root()
    runtime_guards_ok = all(
        [
            code_contains(
                root / "lib" / "services" / "primary_source_reference_resolver.dart",
                "if (pages.isEmpty) {",
            ),
            code_contains(
                root / "lib" / "screens" / "primary_source" / "primary_source_screen.dart",
                "widget.primarySource.pages.isNotEmpty",
            ),
            code_contains(
                root / "lib" / "screens" / "primary_source" / "primary_source_toolbar.dart",
                "primarySource.pages.isEmpty || !primarySource.permissionsReceived",
            ),
        ]
    )
    return ValidationCheck(
        key="zero_page_sources",
        ok=zero_page_sources == EXPECTED_ZERO_PAGE_SOURCES and runtime_guards_ok,
        details=(
            f"expected={sorted(EXPECTED_ZERO_PAGE_SOURCES)}, actual={sorted(zero_page_sources)}, "
            f"runtime_guards_ok={runtime_guards_ok}"
        ),
    )


def validate_localized_metadata(db_dir: Path, common_connection: sqlite3.Connection) -> ValidationCheck:
    source_ids = {
        row[0]
        for row in common_connection.execute("SELECT id FROM primary_sources ORDER BY id").fetchall()
    }
    locale_issues: list[str] = []
    for lang in EXPECTED_LOCALES:
        localized_path = db_dir / f"revelation_{lang}.sqlite"
        if not localized_path.exists():
            locale_issues.append(f"{lang}: missing DB file")
            continue
        with sqlite3.connect(localized_path) as localized_connection:
            localized_connection.row_factory = sqlite3.Row
            localized_source_ids = {
                row[0]
                for row in localized_connection.execute(
                    "SELECT source_id FROM primary_source_texts ORDER BY source_id"
                ).fetchall()
            }
            if localized_source_ids != source_ids:
                locale_issues.append(
                    f"{lang}: source_id mismatch missing={sorted(source_ids - localized_source_ids)} "
                    f"extra={sorted(localized_source_ids - source_ids)}"
                )
            empty_counts = localized_connection.execute(
                """
                SELECT
                  SUM(CASE WHEN trim(title_markup) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(date_label) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(content_label) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(material_text) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(text_style_text) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(found_text) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(classification_text) = '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN trim(current_location_text) = '' THEN 1 ELSE 0 END)
                FROM primary_source_texts
                """
            ).fetchone()
            if any(int(value or 0) > 0 for value in empty_counts):
                locale_issues.append(f"{lang}: empty localized fields counts={tuple(int(v or 0) for v in empty_counts)}")
            text_count = fetch_scalar(
                localized_connection,
                "SELECT COUNT(*) FROM primary_source_texts",
            )
            if text_count != EXPECTED_SOURCE_COUNT:
                locale_issues.append(f"{lang}: text_count={text_count}")
    return ValidationCheck(
        key="localized_metadata",
        ok=not locale_issues,
        details="all locales complete" if not locale_issues else "; ".join(locale_issues),
    )


def run_validation(db_dir: Path) -> list[ValidationCheck]:
    common_path = db_dir / "revelation.sqlite"
    if not common_path.exists():
        raise FileNotFoundError(f"Common DB not found: {common_path}")

    with sqlite3.connect(common_path) as common_connection:
        common_connection.row_factory = sqlite3.Row
        checks: list[ValidationCheck] = []
        checks.extend(validate_common_counts(common_connection))
        checks.append(validate_preview_resources(common_connection))
        checks.append(validate_overlay_integrity(common_connection))
        checks.append(validate_can_show_images(common_connection))
        checks.append(validate_zero_page_sources(common_connection))
        checks.append(validate_localized_metadata(db_dir, common_connection))
        return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Primary Sources migration state for Phase 7.")
    parser.add_argument("--db-dir", type=Path, default=default_db_dir(), help="Path to folder with revelation SQLite files.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks = run_validation(args.db_dir)
    report = {
        "db_dir": str(args.db_dir),
        "all_ok": all(check.ok for check in checks),
        "checks": [asdict(check) for check in checks],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for check in checks:
            prefix = "OK" if check.ok else "FAIL"
            print(f"[{prefix}] {check.key}: {check.details}")
        print()
        print(f"Overall: {'OK' if report['all_ok'] else 'FAIL'}")
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

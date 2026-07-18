from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.normalize_strong_usage import (
    UsageMergeConflict,
    apply_strong_usage_normalization,
    normalize_usage_text,
)


class NormalizeStrongUsageTests(unittest.TestCase):
    def test_nfc_merges_forms_sorts_forms_and_references(self) -> None:
        result = normalize_usage_text(
            "β: [003;001x2], 3\n"
            "α: [00B;002], 2\n"
            "α: [004], 1\n",
            strong_id=602,
        )

        self.assertEqual(
            result.usage,
            "α: [002;004;00B], 3\nβ: [001x2;003], 3",
        )
        self.assertEqual(result.before_variants, 3)
        self.assertEqual(result.after_variants, 2)
        self.assertEqual(result.before_occurrences, 6)
        self.assertEqual(result.after_occurrences, 6)
        self.assertEqual(result.merge_groups, 1)
        self.assertEqual(result.merge_operations, 1)
        self.assertEqual(result.duplicate_reference_occurrences, 0)
        self.assertFalse(result.count_changes)

    def test_exact_duplicate_reference_is_removed_and_count_is_reported(self) -> None:
        result = normalize_usage_text(
            "ἀποκαλύψει: [001x2;003], 3\n"
            "ἀποκαлύψει: [001x2;002], 3\n".replace("л", "λ"),
            strong_id=602,
        )

        self.assertEqual(result.usage, "ἀποκαλύψει: [001x2;002;003], 4")
        self.assertEqual(result.before_occurrences, 6)
        self.assertEqual(result.after_occurrences, 4)
        self.assertEqual(result.duplicate_reference_count, 1)
        self.assertEqual(result.duplicate_reference_occurrences, 2)
        self.assertEqual(len(result.count_changes), 1)
        change = result.count_changes[0]
        self.assertEqual(change.before_occurrences, 6)
        self.assertEqual(change.after_occurrences, 4)
        self.assertEqual(change.removed_occurrences, 2)

    def test_conflicting_reference_counts_abort_without_guessing(self) -> None:
        with self.assertRaises(UsageMergeConflict):
            normalize_usage_text(
                "ἀποκαλύψει: [001x2], 2\n"
                "ἀποκαλύψει: [001x3], 3",
                strong_id=602,
            )

    def test_apply_is_transactional_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "revelation.sqlite"
            _create_fixture(db_path)

            report = apply_strong_usage_normalization(
                common_db_path=db_path,
                vacuum=True,
                applied_at="2026-07-18T10:00:00Z",
            )
            self.assertEqual(report.changed_usage_rows, 1)
            self.assertTrue(report.vacuumed)
            self.assertEqual(report.data_version_before, "4")
            self.assertEqual(report.data_version_after, "5")
            self.assertIsNotNone(report.backup_path)

            connection = sqlite3.connect(db_path)
            try:
                self.assertEqual(
                    connection.execute(
                        "SELECT usage FROM greek_words WHERE id = 602"
                    ).fetchone()[0],
                    "ἀποκαλύψει: [001x2;002;003], 4",
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'data_version'"
                    ).fetchone()[0],
                    "5",
                )
            finally:
                connection.close()

            second_report = apply_strong_usage_normalization(common_db_path=db_path)
            self.assertEqual(second_report.changed_usage_rows, 0)
            self.assertIsNone(second_report.backup_path)
            self.assertEqual(second_report.data_version_before, "5")
            self.assertEqual(second_report.data_version_after, "5")


def _create_fixture(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
            [
                ("schema_version", "4"),
                ("data_version", "4"),
                ("date", "2026-07-17T00:00:00Z"),
            ],
        )
        connection.execute(
            """
            CREATE TABLE greek_words (
              id INTEGER PRIMARY KEY NOT NULL,
              word TEXT NOT NULL DEFAULT '',
              category TEXT NOT NULL DEFAULT '',
              synonyms TEXT NOT NULL DEFAULT '',
              origin TEXT NOT NULL DEFAULT '',
              usage TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.executemany(
            "INSERT INTO greek_words(id, word, usage) VALUES(?, ?, ?)",
            [
                (
                    602,
                    "ἀποκάλυψις",
                    "ἀποκαλύψει: [001x2;003], 3\n"
                    "ἀποκαлύψει: [001x2;002], 3".replace("л", "λ"),
                ),
                (603, "word", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()

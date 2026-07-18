from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.update_lxx_tr_strong_usage import (
    apply_lxx_tr_strong_usage,
    count_usage_line_occurrences,
)


class UpdateLxxTrStrongUsageTests(unittest.TestCase):
    def test_replaces_extended_tags_and_rebuilds_common_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lxx_db_path = root / "bible_lxx_tr.sqlite"
            common_db_path = root / "revelation.sqlite"
            _create_lxx_tr_fixture(
                lxx_db_path,
                {
                    "001": (
                        "alpha G6031 beta G6053 know G6063 aware G6083 "
                        "boast G6094 plain G25 repeat G25 repeat G25"
                    ),
                    "002": "alpha G6031",
                },
            )
            _create_common_dictionary_fixture(common_db_path)

            report = apply_lxx_tr_strong_usage(
                common_db_path=common_db_path,
                bible_module_path=lxx_db_path,
                applied_at="2026-07-11T10:00:00Z",
            )

            self.assertEqual(report.source_token_count, 9)
            self.assertEqual(report.generated_usage_token_count, 9)
            self.assertEqual(report.database_usage_token_count, 9)
            self.assertEqual(report.greek_words_rows, 5624)
            self.assertEqual(report.data_version_before, "4")
            self.assertEqual(report.data_version_after, "5")
            self.assertIsNotNone(report.backup_path)
            self.assertIsNotNone(report.lxx_cleanup)
            assert report.lxx_cleanup is not None
            self.assertEqual(report.lxx_cleanup.data_version_before, "13")
            self.assertEqual(report.lxx_cleanup.data_version_after, "14")
            self.assertEqual(
                dict(report.lxx_cleanup.replacement_counts),
                {
                    "G6031->G1650": 2,
                    "G6053->G2737": 1,
                    "G6063->G1492": 1,
                    "G6083->G4894": 1,
                    "G6094->G3166": 1,
                },
            )

            connection = sqlite3.connect(lxx_db_path)
            try:
                text = connection.execute(
                    "SELECT text FROM verses WHERE verse_key = '001'"
                ).fetchone()[0]
                self.assertNotIn("G6031", text)
                self.assertNotIn("G6063", text)
                self.assertIn("alpha G1650", text)
                self.assertIn("beta G2737", text)
                self.assertIn("boast G3166", text)
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'data_version'"
                    ).fetchone()[0],
                    "14",
                )
            finally:
                connection.close()

            connection = sqlite3.connect(common_db_path)
            try:
                usage_25 = connection.execute(
                    "SELECT usage FROM greek_words WHERE id = 25"
                ).fetchone()[0]
                usage_1650 = connection.execute(
                    "SELECT usage FROM greek_words WHERE id = 1650"
                ).fetchone()[0]
                usage_1492 = connection.execute(
                    "SELECT usage FROM greek_words WHERE id = 1492"
                ).fetchone()[0]
                self.assertEqual(usage_25, "plain: [001], 1\nrepeat: [001x2], 2")
                self.assertEqual(usage_1650, "alpha: [001;002], 2")
                self.assertEqual(usage_1492, "know: [001], 1")
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'data_version'"
                    ).fetchone()[0],
                    "5",
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM greek_words").fetchone()[0],
                    5624,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM greek_words WHERE id > 5624"
                    ).fetchone()[0],
                    0,
                )
            finally:
                connection.close()

    def test_rejects_unmapped_extended_tags_when_cleanup_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lxx_db_path = root / "bible_lxx_tr.sqlite"
            common_db_path = root / "revelation.sqlite"
            _create_lxx_tr_fixture(lxx_db_path, {"001": "word G7000"})
            _create_common_dictionary_fixture(common_db_path)

            with self.assertRaisesRegex(ValueError, "out-of-scope"):
                apply_lxx_tr_strong_usage(
                    common_db_path=common_db_path,
                    bible_module_path=lxx_db_path,
                    clean_lxx_tr_strongs=False,
                    applied_at="2026-07-11T10:00:00Z",
                )

    def test_usage_line_count_validation_rejects_stale_totals(self) -> None:
        with self.assertRaisesRegex(ValueError, "total mismatch"):
            count_usage_line_occurrences("word: [001;002x2], 2")


def _create_lxx_tr_fixture(path: Path, verses: dict[str, str]) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
            [
                ("schema_version", "3"),
                ("data_version", "13"),
                ("date", "2026-07-10T00:00:00Z"),
            ],
        )
        connection.execute(
            """
            CREATE TABLE verses (
              verse_key TEXT PRIMARY KEY,
              text TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.executemany(
            "INSERT INTO verses(verse_key, text) VALUES(?, ?)",
            sorted(verses.items()),
        )
        connection.commit()
    finally:
        connection.close()


def _create_common_dictionary_fixture(path: Path) -> None:
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
                ("date", "2026-07-11T00:00:00Z"),
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
            """
            INSERT INTO greek_words(id, word, category, synonyms, origin, usage)
            VALUES(?, ?, '', '', '', 'legacy')
            """,
            [(strong_id, f"word-{strong_id}") for strong_id in range(1, 5625)],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()

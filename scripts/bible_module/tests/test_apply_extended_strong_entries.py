from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.apply_extended_strong_entries import (
    CLASSIC_GREEK_STRONG_MAX,
    apply_extended_strong_entries,
)


def lexicon_text(*data_lines: str) -> str:
    return "\n".join(
        [
            "metadata before table",
            "eStrong\tdStrong\tuStrong\tGreek\tTransliteration\tMorph\tGloss\tDefinition",
            *data_lines,
        ]
    )


class ApplyExtendedStrongEntriesTests(unittest.TestCase):
    def test_inserts_only_attested_extended_rows_and_updates_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_paths = _write_lexicon_sources(root)
            bible_module_path = root / "bible_na28_lxx.sqlite"
            common_db_path = root / "revelation.sqlite"
            _create_bible_module_fixture(bible_module_path)
            _create_common_dictionary_fixture(common_db_path)

            report = apply_extended_strong_entries(
                common_db_path=common_db_path,
                bible_module_path=bible_module_path,
                source_paths=source_paths,
                expected_attested_count=2,
                expected_primary_count=1,
                applied_at="2026-05-23T12:00:00Z",
            )

            self.assertTrue(report.backup_path is not None and report.backup_path.exists())
            self.assertEqual(report.attested_extended_count, 2)
            self.assertEqual(report.primary_attested_extended_count, 1)
            self.assertEqual(report.inserted_count, 2)
            self.assertEqual(report.skipped_existing_count, 0)
            self.assertEqual(report.data_version_before, "6")
            self.assertEqual(report.data_version_after, "7")

            connection = sqlite3.connect(common_db_path)
            try:
                connection.row_factory = sqlite3.Row
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'data_version'"
                    ).fetchone()["value"],
                    "7",
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'date'"
                    ).fetchone()["value"],
                    "2026-05-23T12:00:00Z",
                )
                g6000 = connection.execute(
                    "SELECT * FROM greek_words WHERE id = 6000"
                ).fetchone()
                g20833 = connection.execute(
                    "SELECT * FROM greek_words WHERE id = 20833"
                ).fetchone()
                self.assertEqual(g6000["word"], "ἀγγέλλω")
                self.assertEqual(g6000["category"], "@verb")
                self.assertEqual(g6000["origin"], "")
                self.assertEqual(g6000["usage"], "")
                self.assertEqual(g20833["word"], "ὁμείρομαι")
                self.assertEqual(g20833["category"], "@verb")

                self.assertIsNone(
                    connection.execute(
                        "SELECT id FROM greek_words WHERE id = 21502"
                    ).fetchone()
                )
            finally:
                connection.close()

    def test_preserves_existing_classic_rows_and_stores_numeric_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_paths = _write_lexicon_sources(root)
            bible_module_path = root / "bible_na28_lxx.sqlite"
            common_db_path = root / "revelation.sqlite"
            _create_bible_module_fixture(bible_module_path)
            _create_common_dictionary_fixture(common_db_path)

            apply_extended_strong_entries(
                common_db_path=common_db_path,
                bible_module_path=bible_module_path,
                source_paths=source_paths,
                expected_attested_count=2,
                expected_primary_count=1,
                applied_at="2026-05-23T12:00:00Z",
            )

            connection = sqlite3.connect(common_db_path)
            try:
                connection.row_factory = sqlite3.Row
                classic = connection.execute(
                    "SELECT word, category, synonyms, origin, usage FROM greek_words WHERE id = 25"
                ).fetchone()
                self.assertEqual(dict(classic), _classic_row_25())
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM greek_words WHERE id = 6000"
                    ).fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM greek_words WHERE id > 5624"
                    ).fetchone()[0],
                        2,
                )
            finally:
                connection.close()


def _write_lexicon_sources(root: Path) -> dict[str, Path]:
    source_paths = {
        "step_tbesg": root / "step_tbesg.txt",
        "step_tflsj_0_5624": root / "step_tflsj_0_5624.txt",
        "step_tflsj_extra": root / "step_tflsj_extra.txt",
    }
    source_paths["step_tbesg"].write_text(
        lexicon_text(
            "G0025\tG0025 =\tG0025\tἀγαπάω\tagapaō\tG:V\tto love\tclassic definition",
            "G06000\tG6000 =\tG6000\tἀγγέλλω\taggellō\tG:V\tto report\tbrief definition",
            "G20833\tG20833 =\tG20833\tὁμείρομαι\thomeiromai\tG:V\tyearn for\tbrief definition",
            "G21502\tG21502 =\tG21502\tΗνια\tHenia\tG:N-PRI\tHeneia\tunused definition",
        ),
        encoding="utf-8",
    )
    source_paths["step_tflsj_0_5624"].write_text(
        lexicon_text(
            "G0025\tG0025 =\tG0025\tἀγαπάω\tagapaō\tG:V\tto love\tfull classic definition",
        ),
        encoding="utf-8",
    )
    source_paths["step_tflsj_extra"].write_text(
        lexicon_text(
            "G6000\tG6000 =\tG6000\tἀγγέλλω\taggellō\tG:V\tto report\tfull extra definition",
            "G20833\tG20833 =\tG20833\tὁμείρομαι\thomeiromai\tG:V\tyearn for\tfull extra definition",
            "G21502\tG21502 =\tG21502\tΗνια\tHenia\tG:N-PRI\tHeneia\tunused full definition",
        ),
        encoding="utf-8",
    )
    return source_paths


def _create_bible_module_fixture(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE token_strongs (
              token_strong_id INTEGER PRIMARY KEY,
              token_id INTEGER NOT NULL,
              strong TEXT NOT NULL,
              raw_strong TEXT NOT NULL,
              role TEXT NOT NULL,
              segment_order INTEGER NOT NULL,
              segment_surface TEXT NOT NULL,
              is_primary INTEGER NOT NULL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO token_strongs(
              token_id,
              strong,
              raw_strong,
              role,
              segment_order,
              segment_surface,
              is_primary
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, "G6000", "G06000", "primary", 1, "surface", 1),
                (2, "G20833", "G20833", "alt", 1, "surface", 0),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _create_common_dictionary_fixture(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.executemany(
            "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
            [
                ("schema_version", "4"),
                ("data_version", "6"),
                ("date", "2026-05-23T00:00:00Z"),
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
        rows = [
            (
                strong_id,
                "classic-25" if strong_id == 25 else f"classic-{strong_id}",
                "@verb" if strong_id == 25 else "",
                "5368" if strong_id == 25 else "",
                "G5368,H5689" if strong_id == 25 else "",
                "legacy usage" if strong_id == 25 else "",
            )
            for strong_id in range(1, CLASSIC_GREEK_STRONG_MAX + 1)
        ]
        connection.executemany(
            """
            INSERT INTO greek_words(id, word, category, synonyms, origin, usage)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
    finally:
        connection.close()


def _classic_row_25() -> dict[str, str]:
    return {
        "word": "classic-25",
        "category": "@verb",
        "synonyms": "5368",
        "origin": "G5368,H5689",
        "usage": "legacy usage",
    }


if __name__ == "__main__":
    unittest.main()

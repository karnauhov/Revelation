from __future__ import annotations

import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.apply_extended_strong_descriptions import (
    LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS,
    SUPPORTED_LOCALES,
    apply_extended_strong_descriptions,
    build_source_description_inputs,
    validate_localized_extended_descriptions,
)


DESCRIPTIONS = {
    6000: {
        "en": "to announce or report",
        "es": "anunciar o comunicar",
        "ru": "возвещать или сообщать",
        "uk": "сповіщати або повідомляти",
    },
    20833: {
        "en": "to desire or yearn for",
        "es": "desear intensamente o anhelar",
        "ru": "сильно желать или тосковать",
        "uk": "сильно бажати або тужити",
    },
}


def lexicon_text(*data_lines: str) -> str:
    return "\n".join(
        [
            "metadata before table",
            "eStrong\tdStrong\tuStrong\tGreek\tTransliteration\tMorph\tGloss\tDefinition",
            *data_lines,
        ]
    )


class ApplyExtendedStrongDescriptionsTests(unittest.TestCase):
    def test_translation_map_covers_all_attested_extended_entries(self) -> None:
        self.assertEqual(len(LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS), 88)
        self.assertNotIn(21502, LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS)
        cyrillic = re.compile(r"[\u0400-\u04FF]")
        for strong_id, localized in LOCALIZED_EXTENDED_STRONG_DESCRIPTIONS.items():
            with self.subTest(strong_id=strong_id):
                self.assertEqual(set(localized), set(SUPPORTED_LOCALES))
                for locale in SUPPORTED_LOCALES:
                    self.assertTrue(localized[locale].strip())
                self.assertIsNone(cyrillic.search(localized["en"]))
                self.assertIsNone(cyrillic.search(localized["es"]))
                self.assertRegex(localized["ru"], cyrillic)
                self.assertRegex(localized["uk"], cyrillic)
                self.assertNotEqual(localized["es"], localized["en"])
                self.assertNotEqual(localized["ru"], localized["en"])
                self.assertNotEqual(localized["uk"], localized["en"])

    def test_builds_source_description_inputs_from_attested_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_paths = _write_lexicon_sources(root)
            bible_module_path = root / "bible_na28_lxx.sqlite"
            common_db_path = root / "revelation.sqlite"
            _create_bible_module_fixture(bible_module_path)
            _create_common_dictionary_fixture(common_db_path)

            inputs = build_source_description_inputs(
                common_db_path=common_db_path,
                bible_module_path=bible_module_path,
                source_paths=source_paths,
                descriptions=DESCRIPTIONS,
                expected_count=2,
                expected_primary_count=1,
            )

            self.assertEqual([row.id for row in inputs], [6000, 20833])
            self.assertEqual(inputs[0].source_gloss, "to report")
            self.assertEqual(inputs[0].translation_batch_range, (6000, 6003))
            self.assertEqual(inputs[1].translation_batch_range, (20833, 20833))

    def test_applies_translations_to_all_localized_dbs_and_updates_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            common_db_path = root / "revelation.sqlite"
            localized_db_paths = {
                locale: root / f"revelation_{locale}.sqlite"
                for locale in SUPPORTED_LOCALES
            }
            _create_common_dictionary_fixture(common_db_path)
            for locale, path in localized_db_paths.items():
                _create_localized_dictionary_fixture(path, data_version=10 + len(locale))

            report = apply_extended_strong_descriptions(
                common_db_path=common_db_path,
                localized_db_paths=localized_db_paths,
                descriptions=DESCRIPTIONS,
                expected_count=2,
                applied_at="2026-05-23T12:00:00Z",
            )

            self.assertEqual(report.expected_count, 2)
            self.assertEqual(len(report.locale_reports), 4)
            for locale_report in report.locale_reports:
                self.assertEqual(locale_report.changed_count, 2)
                self.assertEqual(locale_report.existing_extended_count_before, 0)
                self.assertEqual(locale_report.extended_count_after, 2)
                self.assertTrue(
                    locale_report.backup_path is not None
                    and locale_report.backup_path.exists()
                )

            for locale, path in localized_db_paths.items():
                connection = sqlite3.connect(path)
                try:
                    connection.row_factory = sqlite3.Row
                    self.assertEqual(
                        connection.execute(
                            "SELECT desc FROM greek_descs WHERE id = 6000"
                        ).fetchone()["desc"],
                        DESCRIPTIONS[6000][locale],
                    )
                    self.assertEqual(
                        connection.execute(
                            "SELECT value FROM db_metadata WHERE key = 'date'"
                        ).fetchone()["value"],
                        "2026-05-23T12:00:00Z",
                    )
                finally:
                    connection.close()

            common_connection = sqlite3.connect(common_db_path)
            try:
                self.assertEqual(
                    common_connection.execute(
                        "SELECT value FROM db_metadata WHERE key = 'date'"
                    ).fetchone()[0],
                    "2026-05-23T00:00:00Z",
                )
            finally:
                common_connection.close()

    def test_validation_rejects_missing_localized_descriptions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            common_db_path = root / "revelation.sqlite"
            localized_db_paths = {
                locale: root / f"revelation_{locale}.sqlite"
                for locale in SUPPORTED_LOCALES
            }
            _create_common_dictionary_fixture(common_db_path)
            for locale, path in localized_db_paths.items():
                _create_localized_dictionary_fixture(path)
                _insert_localized_descriptions(
                    path,
                    locale,
                    skip_id=20833 if locale == "uk" else None,
                )

            with self.assertRaisesRegex(ValueError, "revelation_uk.sqlite"):
                validate_localized_extended_descriptions(
                    common_db_path=common_db_path,
                    localized_db_paths=localized_db_paths,
                    descriptions=DESCRIPTIONS,
                    expected_count=2,
                )

    def test_validation_rejects_untranslated_non_english_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            common_db_path = root / "revelation.sqlite"
            localized_db_paths = {
                locale: root / f"revelation_{locale}.sqlite"
                for locale in SUPPORTED_LOCALES
            }
            _create_common_dictionary_fixture(common_db_path)
            for path in localized_db_paths.values():
                _create_localized_dictionary_fixture(path)

            bad_descriptions = {
                **DESCRIPTIONS,
                6000: {
                    **DESCRIPTIONS[6000],
                    "es": "to announce or report",
                },
            }

            with self.assertRaisesRegex(ValueError, "Spanish description appears"):
                validate_localized_extended_descriptions(
                    common_db_path=common_db_path,
                    localized_db_paths=localized_db_paths,
                    descriptions=bad_descriptions,
                    expected_count=2,
                )


def _write_lexicon_sources(root: Path) -> dict[str, Path]:
    source_paths = {
        "step_tbesg": root / "step_tbesg.txt",
        "step_tflsj_0_5624": root / "step_tflsj_0_5624.txt",
        "step_tflsj_extra": root / "step_tflsj_extra.txt",
    }
    source_paths["step_tbesg"].write_text(
        lexicon_text(
            "G06000\tG6000 =\tG6000\tἀγγέλλω\taggellō\tG:V\tto report\tbrief definition",
            "G20833\tG20833 =\tG20833\tὁμείρομαι\thomeiromai\tG:V\tyearn for\tbrief definition",
        ),
        encoding="utf-8",
    )
    source_paths["step_tflsj_0_5624"].write_text(lexicon_text(), encoding="utf-8")
    source_paths["step_tflsj_extra"].write_text(
        lexicon_text(
            "G6000\tG6000 =\tG6000\tἀγγέλλω\taggellō\tG:V\tto report\tfull extra definition",
            "G20833\tG20833 =\tG20833\tὁμείρομαι\thomeiromai\tG:V\tyearn for\tfull extra definition",
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
        connection.executemany(
            """
            INSERT INTO greek_words(id, word, category, synonyms, origin, usage)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            [
                (6000, "ἀγγέλλω", "@verb", "", "", ""),
                (20833, "ὁμείρομαι", "@verb", "", "", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _create_localized_dictionary_fixture(path: Path, *, data_version: int = 10) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.executemany(
            "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
            [
                ("schema_version", "6"),
                ("data_version", str(data_version)),
                ("date", "2026-05-23T00:00:00Z"),
            ],
        )
        connection.execute(
            """
            CREATE TABLE greek_descs (
              id INTEGER PRIMARY KEY NOT NULL,
              desc TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def _insert_localized_descriptions(path: Path, locale: str, *, skip_id: int | None = None) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.executemany(
            "INSERT INTO greek_descs(id, desc) VALUES(?, ?)",
            [
                (strong_id, localized[locale])
                for strong_id, localized in DESCRIPTIONS.items()
                if strong_id != skip_id
            ],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()

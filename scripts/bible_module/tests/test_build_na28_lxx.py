from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.build_na28_lxx import (
    MODULE_CODE,
    MODULE_ID,
    build_na28_lxx_module_from_imports,
    validate_na28_lxx_database,
)
from scripts.bible_module.lxx import LxxSourceVerse, build_lxx_import_result
from scripts.bible_module.schema import (
    BIBLE_MODULE_SCHEMA_VERSION,
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    DB_METADATA_SCHEMA_VERSION_KEY,
    read_db_metadata,
)
from scripts.bible_module.tagnt import build_na28_module_verses, parse_tagnt_row


def tagnt_line(*fields: str) -> str:
    return "\t".join(fields)


def _mat_1_1_tagnt_row() -> str:
    return tagnt_line(
        "Mat.1.1#01=NKO",
        "Biblos (Biblos)",
        "[The] book",
        "G0976=N-NSF",
        "biblos=book",
        "NA28+NA27",
        "",
        "",
        "Libro",
        "book",
        "#01",
        "G0976",
        "",
    )


def _gen_1_1_lxx_result():
    return build_lxx_import_result(
        [
            LxxSourceVerse(
                source_book_code="Gen",
                chapter=1,
                verse=1,
                entry_index=1,
                block_index=1,
                raw_osis=(
                    '<w lemma="strong:G0746" morph="packard:N1-DSF" '
                    'xlit="betacode:A)RXH=|">arche</w>'
                ),
            )
        ]
    )


class Na28LxxBuilderTests(unittest.TestCase):
    def test_fixture_build_creates_physical_module_with_tokens_and_spot_checks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bible_na28_lxx.sqlite"
            report = _build_fixture(target_path)

            self.assertEqual(report.target_path, target_path.resolve())
            self.assertIsNone(report.backup_path)
            self.assertEqual(report.module_verses_count, 2)
            self.assertEqual(report.tokens_count, 2)
            self.assertEqual(report.token_strongs_count, 2)
            self.assertEqual(report.import_warnings_count, 0)
            validate_na28_lxx_database(target_path, require_spot_checks=True)

            connection = sqlite3.connect(target_path)
            try:
                self.assertEqual(
                    int(connection.execute("PRAGMA user_version").fetchone()[0]),
                    BIBLE_MODULE_SCHEMA_VERSION,
                )
                metadata = read_db_metadata(connection)
                self.assertEqual(
                    metadata[DB_METADATA_SCHEMA_VERSION_KEY],
                    str(BIBLE_MODULE_SCHEMA_VERSION),
                )
                self.assertEqual(metadata[DB_METADATA_DATA_VERSION_KEY], "1")
                self.assertEqual(metadata[DB_METADATA_DATE_KEY], "2026-05-23T00:00:00Z")

                module = connection.execute(
                    "SELECT module_id, code, module_kind FROM bible_modules"
                ).fetchone()
                self.assertEqual(tuple(module), (MODULE_ID, MODULE_CODE, "original_language"))
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                    66,
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM source_texts").fetchone()[0],
                    2,
                )
                stored_strongs = connection.execute(
                    """
                    SELECT strong, raw_strong
                    FROM token_strongs
                    ORDER BY token_strong_id
                    """
                ).fetchall()
                self.assertEqual(stored_strongs, [("G746", "G0746"), ("G976", "G0976")])
            finally:
                connection.close()

    def test_existing_target_is_backed_up_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bible_na28_lxx.sqlite"
            target_path.write_bytes(b"old database")

            report = _build_fixture(target_path)

            self.assertIsNotNone(report.backup_path)
            assert report.backup_path is not None
            self.assertTrue(report.backup_path.exists())
            self.assertEqual(report.backup_path.read_bytes(), b"old database")
            validate_na28_lxx_database(target_path, require_spot_checks=True)

    def test_builder_requires_locked_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bible_na28_lxx.sqlite"
            with self.assertRaisesRegex(ValueError, "Missing locked source entries"):
                build_na28_lxx_module_from_imports(
                    target_path=target_path,
                    source_entries={},
                    nt_verses=(),
                    lxx_result=_gen_1_1_lxx_result(),
                    built_at="2026-05-23T00:00:00Z",
                )


def _build_fixture(target_path: Path):
    token = parse_tagnt_row(_mat_1_1_tagnt_row())
    assert token is not None
    nt_verses = build_na28_module_verses([token])
    return build_na28_lxx_module_from_imports(
        target_path=target_path,
        source_entries=_fake_source_entries(),
        nt_verses=nt_verses,
        lxx_result=_gen_1_1_lxx_result(),
        built_at="2026-05-23T00:00:00Z",
    )


def _fake_source_entries() -> dict[str, dict[str, object]]:
    source_ids = [
        "step_tagnt_mat_jhn",
        "step_tagnt_act_rev",
        "step_tbesg",
        "step_tflsj_0_5624",
        "step_tflsj_extra",
        "step_tegmc",
        "crosswire_lxx",
    ]
    return {
        source_id: {
            "source_id": source_id,
            "title": f"{source_id} title",
            "version": "fixture",
            "source_page_url": f"https://example.com/{source_id}",
            "license": "test-only",
            "sha256": f"{index:064x}"[-64:],
            "notes": "fixture source",
        }
        for index, source_id in enumerate(source_ids, start=1)
    }


if __name__ == "__main__":
    unittest.main()

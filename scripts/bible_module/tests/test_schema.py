from __future__ import annotations

import sqlite3
import unittest

from scripts.bible_module.canon import get_canonical_verse
from scripts.bible_module.schema import (
    BIBLE_MODULE_SCHEMA_VERSION,
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    DB_METADATA_SCHEMA_VERSION_KEY,
    FORBIDDEN_FORM_OCCURRENCE_TABLES,
    TOKEN_INDEXES,
    TOKEN_TABLES,
    assert_no_form_occurrence_tables,
    create_bible_module_schema,
    expected_index_names,
    expected_table_names,
    index_names,
    insert_minimal_module_fixture,
    read_db_metadata,
    table_names,
)


class BibleModuleSchemaTests(unittest.TestCase):
    def test_full_schema_creates_tables_indexes_metadata_and_canon_seed(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            create_bible_module_schema(
                connection,
                include_token_tables=True,
                date_iso="2026-05-23T00:00:00Z",
            )

            self.assertEqual(
                int(connection.execute("PRAGMA user_version").fetchone()[0]),
                BIBLE_MODULE_SCHEMA_VERSION,
            )
            self.assertTrue(set(expected_table_names()).issubset(table_names(connection)))
            self.assertTrue(set(expected_index_names()).issubset(index_names(connection)))
            self.assertFalse(set(FORBIDDEN_FORM_OCCURRENCE_TABLES) & table_names(connection))

            metadata = read_db_metadata(connection)
            self.assertEqual(
                metadata[DB_METADATA_SCHEMA_VERSION_KEY],
                str(BIBLE_MODULE_SCHEMA_VERSION),
            )
            self.assertEqual(metadata[DB_METADATA_DATA_VERSION_KEY], "1")
            self.assertEqual(metadata[DB_METADATA_DATE_KEY], "2026-05-23T00:00:00Z")

            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                66,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM canonical_verses").fetchone()[0],
                31_102,
            )

            mat = connection.execute(
                """
                SELECT canonical_ref, osis_ref
                FROM canonical_verses
                WHERE canonical_verse_id = ?
                """,
                (get_canonical_verse("Mat", 1, 1).canonical_verse_id,),
            ).fetchone()
            self.assertEqual(tuple(mat), ("Mat.1.1", "Matt.1.1"))
        finally:
            connection.close()

    def test_translation_schema_keeps_token_tables_optional(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            create_bible_module_schema(
                connection,
                include_token_tables=False,
                date_iso="2026-05-23T00:00:00Z",
            )

            names = table_names(connection)
            self.assertTrue(set(expected_table_names(include_token_tables=False)).issubset(names))
            self.assertFalse(set(TOKEN_TABLES) & names)
            self.assertFalse(set(TOKEN_INDEXES) & index_names(connection))
            self.assertTrue(
                set(expected_index_names(include_token_tables=False)).issubset(
                    index_names(connection)
                )
            )

            insert_minimal_module_fixture(connection, module_kind="translation")
            gen_1_1 = get_canonical_verse("Gen", 1, 1)
            connection.execute(
                """
                INSERT INTO module_verses(
                  module_verse_id,
                  source_text_id,
                  native_ref,
                  book_id,
                  chapter,
                  verse,
                  text_plain,
                  text_display,
                  tokens_count,
                  sort_key
                )
                VALUES(1, 'fixture_text', 'Gen.1.1', ?, 1, 1, 'In the beginning', 'In the beginning', 0, ?)
                """,
                (gen_1_1.book_id, gen_1_1.sort_key),
            )
            connection.execute(
                """
                INSERT INTO module_verse_links(module_verse_id, canonical_verse_id, link_kind)
                VALUES(1, ?, 'exact')
                """,
                (gen_1_1.canonical_verse_id,),
            )

            linked_ref = connection.execute(
                """
                SELECT c.canonical_ref
                FROM module_verse_links l
                JOIN canonical_verses c ON c.canonical_verse_id = l.canonical_verse_id
                WHERE l.module_verse_id = 1
                """
            ).fetchone()[0]
            self.assertEqual(linked_ref, "Gen.1.1")
        finally:
            connection.close()

    def test_full_schema_accepts_tokens_and_rejects_padded_strong_keys(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            create_bible_module_schema(
                connection,
                include_token_tables=True,
                date_iso="2026-05-23T00:00:00Z",
            )
            insert_minimal_module_fixture(
                connection,
                module_kind="original_language",
                code="NA28_LXX",
            )
            gen_1_1 = get_canonical_verse("Gen", 1, 1)
            connection.execute(
                """
                INSERT INTO module_verses(
                  module_verse_id,
                  source_text_id,
                  native_ref,
                  book_id,
                  chapter,
                  verse,
                  text_plain,
                  text_display,
                  tokens_count,
                  sort_key
                )
                VALUES(1, 'fixture_text', 'Gen.1.1', ?, 1, 1, 'text', 'text', 1, ?)
                """,
                (gen_1_1.book_id, gen_1_1.sort_key),
            )
            connection.execute(
                """
                INSERT INTO tokens(
                  token_id,
                  module_verse_id,
                  source_text_id,
                  token_order,
                  source_ref,
                  text_type,
                  surface,
                  surface_normalized,
                  surface_search,
                  transliteration,
                  lemma,
                  morphology,
                  gloss,
                  raw_json
                )
                VALUES(1, 1, 'fixture_text', 1, 'Gen.1.1!1', 'word', 'arche', 'arche', 'arche', '', '', '', '', '{}')
                """
            )
            connection.execute(
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
                VALUES(1, 'G746', 'G0746', 'primary', 0, 'arche', 1)
                """
            )

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
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
                    VALUES(1, 'G0746', 'G0746', 'primary', 1, 'arche', 1)
                    """
                )
        finally:
            connection.close()

    def test_form_occurrence_tables_are_forbidden_in_bible_modules(self) -> None:
        with self.assertRaisesRegex(ValueError, "form tables"):
            assert_no_form_occurrence_tables(["books", "word_forms"])


if __name__ == "__main__":
    unittest.main()


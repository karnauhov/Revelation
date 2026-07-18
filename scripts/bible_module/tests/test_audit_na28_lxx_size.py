from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.audit_na28_lxx_size import (
    audit_bible_module_size,
    render_markdown_report,
)
from scripts.bible_module.schema import create_bible_module_schema


class Na28LxxSizeAuditTests(unittest.TestCase):
    def test_audit_reports_tables_columns_indexes_and_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "bible_fixture.sqlite"
            _create_fixture_database(db_path)

            audit = audit_bible_module_size(
                db_path,
                include_deep_estimates=True,
                include_scenarios=True,
            )

            table_by_name = {table.name: table for table in audit.tables}
            self.assertIn("tokens", table_by_name)
            self.assertEqual(table_by_name["tokens"].row_count, 1)
            self.assertGreater(table_by_name["tokens"].text_bytes, 0)
            self.assertIsNotNone(table_by_name["tokens"].isolated_size_bytes)

            token_columns = {
                column.name: column for column in table_by_name["tokens"].columns
            }
            self.assertEqual(token_columns["raw_json"].text_bytes, len('{"source":1}'))

            index_names = {index.name for index in audit.indexes}
            self.assertIn("idx_token_strongs_strong", index_names)

            scenario_by_name = {scenario.name: scenario for scenario in audit.scenarios}
            self.assertIsNone(
                scenario_by_name["drop_tokens_token_strongs_import_warnings"].error
            )
            self.assertLess(
                scenario_by_name[
                    "drop_tokens_token_strongs_import_warnings"
                ].size_bytes,
                audit.file_size_bytes,
            )

            markdown = render_markdown_report(audit)
            self.assertIn("## Tables", markdown)
            self.assertIn("tokens", markdown)
            self.assertIn("Temporary Pruning Scenarios", markdown)


def _create_fixture_database(db_path: Path) -> None:
    connection = sqlite3.connect(db_path)
    try:
        create_bible_module_schema(
            connection,
            include_token_tables=True,
            date_iso="2026-05-23T00:00:00Z",
        )
        connection.execute(
            """
            INSERT INTO bible_modules(
              module_id,
              code,
              title,
              language,
              module_kind,
              canon,
              versification,
              license,
              source_summary,
              schema_version,
              data_version,
              built_at
            )
            VALUES(
              'na28_lxx',
              'NA28_LXX',
              'Fixture',
              'grc',
              'original_language',
              'protestant_66',
              'fixture',
              'test',
              'fixture',
              1,
              1,
              '2026-05-23T00:00:00Z'
            )
            """
        )
        connection.execute(
            """
            INSERT INTO module_sources(
              source_id,
              module_id,
              title,
              source_url,
              source_version,
              license,
              checksum_sha256,
              import_notes
            )
            VALUES(
              'source',
              'na28_lxx',
              'Source',
              'https://example.com',
              'fixture',
              'test',
              ?,
              'notes'
            )
            """,
            ("0" * 64,),
        )
        connection.execute(
            """
            INSERT INTO source_texts(
              source_text_id,
              module_id,
              source_id,
              code,
              scope,
              language,
              priority
            )
            VALUES('source_text', 'na28_lxx', 'source', 'FIX', 'NT', 'grc', 1)
            """
        )
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
            VALUES(
              1,
              'source_text',
              'Mat.1.1',
              40,
              1,
              1,
              'Biblos',
              'Biblos',
              1,
              40001001
            )
            """
        )
        connection.execute(
            """
            INSERT INTO module_verse_links(
              module_verse_id,
              canonical_verse_id,
              link_kind
            )
            VALUES(1, 40001001, 'exact')
            """
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
            VALUES(
              1,
              1,
              'source_text',
              1,
              'Mat.1.1#01=NKO',
              'NKO',
              'Biblos',
              'Biblos',
              'biblos',
              'Biblos',
              'biblos',
              'N-NSF',
              'book',
              '{"source":1}'
            )
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
            VALUES(1, 'G976', 'G0976', 'primary', 0, 'Biblos', 1)
            """
        )
        connection.execute(
            """
            INSERT INTO import_warnings(
              source_id,
              severity,
              code,
              source_ref,
              message,
              raw_json
            )
            VALUES('source', 'warning', 'fixture', 'Mat.1.1', 'message', '{}')
            """
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()

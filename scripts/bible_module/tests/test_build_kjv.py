from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.build_kjv import (
    KJV_SCHEMA_VERSION,
    create_kjv_schema,
    extract_kjv_verse_texts,
    validate_kjv_database,
    validate_kjv_source_texts,
    verse_key_for,
)
from scripts.bible_module.canon import get_canonical_verse


class KjvBuilderTests(unittest.TestCase):
    def test_usfx_parser_flattens_kjv_text_without_notes_or_strongs(self) -> None:
        texts = extract_kjv_verse_texts(
            """
            <usfx>
              <book id="GEN">
                <c id="1" />
                <p style="p">
                  <v id="2" bcv="GEN.1.2" />And the
                  <w s="H0776">earth</w>
                  <w s="H1961">was</w> without
                  <w s="H8414">form</w>, and
                  <w s="H0922">void</w>; and
                  <w s="H2822">darkness</w>
                  <add>was</add> upon the face of the deep.
                  <f caller="+"><fr>1.2</fr><ft>note to omit</ft></f>
                  <ve />
                </p>
              </book>
              <book id="PSA">
                <c id="23" />
                <d style="d">A <w s="H4210">Psalm</w> of David.</d>
                <q style="q1">
                  <v id="1" bcv="PSA.23.1" />The
                  <nd><w s="H3068">LORD</w></nd>
                  <add>is</add> my shepherd; I shall not want.
                  <ve />
                </q>
              </book>
              <book id="JHN">
                <c id="3" />
                <p style="p">
                  <v id="16" bcv="JHN.3.16" />
                  <wj>¶
                    <w s="G1063">For</w> God so loved the world.
                  </wj>
                  <ve />
                </p>
              </book>
              <book id="2CH">
                <c id="14" />
                <p style="p">
                  <v id="1" bcv="2CH.14.1" />So Abijah slept with his fathers.
                  <ve />
                  <v id="15" bcv="2CH.14.15" />They smote also the tents of cattle.
                  <ve />
                </p>
              </book>
            </usfx>
            """
        )

        self.assertEqual(
            texts["Gen.1.2"],
            "And the earth was without form, and void; and darkness was upon "
            "the face of the deep.",
        )
        self.assertEqual(
            texts["Ps.23.1"],
            "A Psalm of David. The LORD is my shepherd; I shall not want.",
        )
        self.assertEqual(texts["John.3.16"], "¶ For God so loved the world.")
        self.assertEqual(
            texts["2Chr.13.23"],
            "So Abijah slept with his fathers.",
        )
        self.assertEqual(
            texts["2Chr.14.14"],
            "They smote also the tents of cattle.",
        )

    def test_source_validation_rejects_partial_or_empty_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical verse map"):
            validate_kjv_source_texts({"Gen.1.1": ""})

    def test_kjv_schema_uses_same_compact_bible_module_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "bible_kjv.sqlite"
            connection = sqlite3.connect(db_path)
            try:
                create_kjv_schema(
                    connection,
                    data_version=1,
                    date_iso="2026-07-04T00:00:00Z",
                )
                connection.commit()

                self.assertEqual(
                    int(connection.execute("PRAGMA user_version").fetchone()[0]),
                    KJV_SCHEMA_VERSION,
                )
                self.assertEqual(
                    {
                        row[0]
                        for row in connection.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table'"
                        )
                    },
                    {"db_metadata", "info", "verses"},
                )
                self.assertEqual(
                    [
                        row[1]
                        for row in connection.execute("PRAGMA table_info(info)")
                    ],
                    [
                        "code",
                        "module_id",
                        "title",
                        "description",
                        "language",
                        "canon",
                        "versification",
                        "license",
                        "source_summary",
                    ],
                )
                self.assertEqual(
                    connection.execute("SELECT code, module_id FROM info").fetchone(),
                    ("KJV", "kjv"),
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0],
                    31102,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT verse_key FROM verses ORDER BY verse_key LIMIT 1"
                    ).fetchone()[0],
                    verse_key_for(get_canonical_verse("Gen", 1, 1)),
                )
            finally:
                connection.close()

            with self.assertRaisesRegex(ValueError, "empty"):
                validate_kjv_database(db_path)


if __name__ == "__main__":
    unittest.main()

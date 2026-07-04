from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.build_kjv import (
    KJV_SCHEMA_VERSION,
    create_kjv_schema,
    extract_kjv_verse_texts,
    plain_kjv_text,
    validate_kjv_database,
    validate_kjv_source_texts,
    verse_key_for,
)
from scripts.bible_module.canon import get_canonical_verse


class KjvBuilderTests(unittest.TestCase):
    def test_usfx_parser_flattens_kjv_text_with_strongs(self) -> None:
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
                  <wj>&#182;
                    <w s="G1063">For</w> God so loved the world.
                  </wj>
                  <ve />
                </p>
              </book>
              <book id="MAT">
                <c id="11" />
                <p style="p">
                  <v id="6" bcv="MAT.11.6" />
                  <w s="G3739">who</w><w s="G1437">soever</w>
                  <w s="G4624">shall</w>
                  <w s="G3361">not</w>
                  <w s="G4624">be offended</w>.
                  <ve />
                </p>
              </book>
              <book id="MRK">
                <c id="4" />
                <p style="p">
                  <v id="24" bcv="MRK.4.24" />
                  <w s="G4369">shall more be give</w>n.
                  <ve />
                </p>
              </book>
              <book id="ACT">
                <c id="1" />
                <p style="p">
                  <v id="12" bcv="ACT.1.12" />a sabbath
                  <w s="G4521">day</w>&#8217;<w s="G2192">s</w>
                  <w s="G3598">journey</w>.
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
            "And the earth H776 was H1961 without form, H8414 and void; "
            "H922 and darkness H2822 was upon the face of the deep.",
        )
        self.assertEqual(
            plain_kjv_text(texts["Gen.1.2"]),
            "And the earth was without form, and void; and darkness was upon "
            "the face of the deep.",
        )
        self.assertEqual(
            texts["Ps.23.1"],
            "A Psalm H4210 of David. The LORD H3068 is my shepherd; I shall "
            "not want.",
        )
        self.assertEqual(
            plain_kjv_text(texts["Ps.23.1"]),
            "A Psalm of David. The LORD is my shepherd; I shall not want.",
        )
        self.assertEqual(
            texts["John.3.16"],
            "For G1063 God so loved the world.",
        )
        self.assertEqual(
            plain_kjv_text(texts["John.3.16"]),
            "For God so loved the world.",
        )
        self.assertEqual(
            texts["Matt.11.6"],
            "whosoever G3739 G1437 shall G4624 not G3361 be offended. G4624",
        )
        self.assertEqual(
            plain_kjv_text(texts["Matt.11.6"]),
            "whosoever shall not be offended.",
        )
        self.assertEqual(
            texts["Mark.4.24"],
            "shall more be given. G4369",
        )
        self.assertEqual(
            plain_kjv_text(texts["Mark.4.24"]),
            "shall more be given.",
        )
        self.assertEqual(
            texts["Acts.1.12"],
            "a sabbath day\u2019s G4521 G2192 journey. G3598",
        )
        self.assertEqual(
            plain_kjv_text(texts["Acts.1.12"]),
            "a sabbath day\u2019s journey.",
        )
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

from __future__ import annotations

import json
import sqlite3
import unittest

from scripts.bible_module.schema import (
    create_bible_module_schema,
    insert_minimal_module_fixture,
)
from scripts.bible_module.tagnt import (
    TAGNT_SOURCE_TEXT_ID,
    build_na28_module_verses,
    normalize_strong,
    parse_tagnt_row,
    parse_tagnt_reference,
    surface_search_text,
)


def tagnt_line(*fields: str) -> str:
    return "\t".join(fields)


MATTHEW_1_1_ROWS = [
    tagnt_line(
        "Mat.1.1#01=NKO",
        "Βίβλος (Biblos)",
        "[The] book",
        "G0976=N-NSF",
        "βίβλος=book",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "Libro",
        "book",
        "#01",
        "G0976",
        "",
    ),
    tagnt_line(
        "Mat.1.1#02=NKO",
        "γενέσεως (geneseōs)",
        "of [the] genealogy",
        "G1078=N-GSF",
        "γένεσις=origin",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "de origen",
        "origin",
        "#02",
        "G1078",
        "",
    ),
    tagnt_line(
        "Mat.1.1#03=NKO",
        "Ἰησοῦ (Iēsou)",
        "of Jesus",
        "G2424G=N-GSM-P",
        "Ἰησοῦς=Jesus/Joshua",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "de Jesús",
        "Jesus»Jesus|Jesus@Mat.1.1",
        "#03",
        "G2424",
        "",
    ),
    tagnt_line(
        "Mat.1.1#04=NKO",
        "Χριστοῦ (Christou)",
        "Christ",
        "G5547=N-GSM-T",
        "Χριστός=Christ",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "Ungido",
        "Christ»Christ|Jesus@Mat.1.1",
        "#04",
        "G5547",
        "",
    ),
    tagnt_line(
        "Mat.1.1#05=NKO",
        "υἱοῦ (huiou)",
        "son",
        "G5207=N-GSM",
        "υἱός=son",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "hijo",
        "son",
        "#05",
        "G5207_A",
        "",
    ),
    tagnt_line(
        "Mat.1.1#06=NKO",
        "Δαυὶδ (Dauid)",
        "of David",
        "G1138=N-GSM-P",
        "Δαυείδ, Δαυίδ, Δαβίδ=David",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "Tyn+WH: Δαυεὶδ ; +TR: Δαβὶδ ;",
        "de David",
        "David»David|David@Rut.4.17",
        "#06",
        "G1138",
        "",
    ),
    tagnt_line(
        "Mat.1.1#07=NKO",
        "υἱοῦ (huiou)",
        "son",
        "G5207=N-GSM",
        "υἱός=son",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "",
        "hijo",
        "son",
        "#07",
        "G5207_B",
        "",
    ),
    tagnt_line(
        "Mat.1.1#08=NKO",
        "Ἀβραάμ. (Abraam)",
        "of Abraham.",
        "G0011=N-GSM-P",
        "Ἀβραάμ=Abraham",
        "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
        "",
        "Tyn: Ἁβραάμ ;",
        "de Abrahán",
        "Abraham»Abraham|Abraham@Gen.11.26",
        "#08",
        "G0011",
        "",
    ),
]


class TagntImportTests(unittest.TestCase):
    def test_headers_and_non_data_rows_are_skipped(self) -> None:
        self.assertIsNone(parse_tagnt_row("#_Significant variant\t\t"))
        self.assertIsNone(
            parse_tagnt_row(
                "Word & Type\tGreek\tEnglish translation\tdStrongs = Grammar"
            )
        )

    def test_parse_reference_parts(self) -> None:
        reference = parse_tagnt_reference("Mat.1.1#01=NKO")

        self.assertEqual(reference.source_book_code, "Mat")
        self.assertEqual(reference.canonical_book_code, "Mat")
        self.assertEqual(reference.chapter, 1)
        self.assertEqual(reference.verse, 1)
        self.assertEqual(reference.token_order, 1)
        self.assertEqual(reference.text_type, "NKO")
        self.assertEqual(reference.canonical_verse.canonical_ref, "Mat.1.1")

    def test_normalize_strong_keys_without_leading_zeroes(self) -> None:
        self.assertEqual(normalize_strong("G0001"), "G1")
        self.assertEqual(normalize_strong("G0011"), "G11")
        self.assertEqual(normalize_strong("G0976"), "G976")
        self.assertEqual(normalize_strong("G2424G"), "G2424")
        self.assertEqual(normalize_strong("G5207_A"), "G5207")

    def test_matthew_1_1_token_import_and_verse_build(self) -> None:
        tokens = [parse_tagnt_row(row) for row in MATTHEW_1_1_ROWS]
        self.assertTrue(all(token is not None for token in tokens))
        parsed_tokens = [token for token in tokens if token is not None]

        self.assertEqual(len(parsed_tokens), 8)
        self.assertTrue(all(token.is_na28 for token in parsed_tokens))

        first_token = parsed_tokens[0]
        self.assertEqual(first_token.surface, "Βίβλος")
        self.assertEqual(first_token.surface_search, "Βίβλος")
        self.assertEqual(first_token.transliteration, "Biblos")
        self.assertEqual(first_token.lemma, "βίβλος")
        self.assertEqual(first_token.gloss, "book")
        self.assertEqual(first_token.morphology, "N-NSF")
        self.assertEqual(first_token.strong_segments[0].strong, "G976")
        self.assertEqual(first_token.strong_segments[0].raw_strong, "G0976")

        jesus_token = parsed_tokens[2]
        self.assertEqual(jesus_token.strong_segments[0].strong, "G2424")
        self.assertEqual(jesus_token.strong_segments[0].raw_strong, "G2424G")

        abraham_token = parsed_tokens[-1]
        self.assertEqual(abraham_token.surface, "Ἀβραάμ.")
        self.assertEqual(abraham_token.surface_search, "Ἀβραάμ")
        self.assertEqual(abraham_token.strong_segments[0].strong, "G11")
        self.assertEqual(abraham_token.strong_segments[0].raw_strong, "G0011")

        raw_payload = json.loads(abraham_token.raw_json)
        self.assertEqual(raw_payload["source_ref"], "Mat.1.1#08=NKO")
        self.assertIn("columns", raw_payload)

        verses = build_na28_module_verses(parsed_tokens)
        self.assertEqual(len(verses), 1)
        self.assertEqual(verses[0].canonical_ref, "Mat.1.1")
        self.assertEqual(
            verses[0].text_plain,
            "Βίβλος γενέσεως Ἰησοῦ Χριστοῦ υἱοῦ Δαυὶδ υἱοῦ Ἀβραάμ.",
        )
        self.assertEqual(verses[0].tokens_count, 8)

    def test_tr_byz_only_extra_tokens_do_not_enter_na28_text(self) -> None:
        rows = [
            tagnt_line(
                "Mat.1.25#09=NKO",
                "υἱόν (huion)",
                "a son",
                "G5207=N-ASM",
                "υἱός=son",
                "NA28+NA27+Tyn+SBL+WH+Treg+TR+Byz",
                "",
                "",
                "a hijo",
                "son",
                "#09",
                "G5207",
                "",
            ),
            tagnt_line(
                "Mat.1.25#10=K",
                "αὐτῆς (autēs)",
                "of her",
                "G0846=P-GSF",
                "αὐτός=he/she/it/self",
                "TR+Byz",
                "",
                "",
                "de ella",
                "of her",
                "#10«09:G5207",
                "G0846_b",
                "G3778",
            ),
            tagnt_line(
                "Mat.1.25#12=K",
                "πρωτότοκον, (prōtotokon)",
                "firstborn,",
                "G4416=A-ASM-S",
                "πρωτότοκος=firstborn",
                "TR+Byz",
                "",
                "",
                "primogénito",
                "firstborn",
                "#12",
                "G4416",
                "",
            ),
        ]
        parsed_tokens = [token for row in rows if (token := parse_tagnt_row(row))]

        self.assertEqual([token.is_na28 for token in parsed_tokens], [True, False, False])

        verses = build_na28_module_verses(parsed_tokens)
        self.assertEqual(len(verses), 1)
        self.assertEqual(verses[0].text_plain, "υἱόν")
        self.assertNotIn("πρωτότοκον", verses[0].text_plain)
        self.assertNotIn("αὐτῆς", verses[0].text_plain)

    def test_meaning_spelling_variants_are_preserved_without_replacing_na28_token(
        self,
    ) -> None:
        row = tagnt_line(
            "Mat.1.10#10=N(k)O",
            "Ἀμώς· (Amōs)",
            "Amos;",
            "G0301H=N-ASM-P",
            "Ἀμώς=Amos",
            "NA28+NA27+Tyn+SBL+WH+Treg",
            "Ἀμών (t=Amōn) Amon - G0300=N-ASM-P in: TR+Byz",
            "TR+Byz: Ἀμών ;",
            "Amós",
            "Amos»Amos|Amon@2Ki.21.18",
            "#10",
            "G0301_A",
            "G0300",
        )
        token = parse_tagnt_row(row)
        self.assertIsNotNone(token)
        assert token is not None

        self.assertTrue(token.is_na28)
        self.assertEqual(token.surface, "Ἀμώς·")
        self.assertEqual(token.surface_search, "Ἀμώς")
        self.assertEqual(token.morphology, "N-ASM-P")
        self.assertEqual(token.strong_segments[0].role, "primary")
        self.assertEqual(token.strong_segments[0].strong, "G301")
        self.assertEqual(token.strong_segments[0].raw_strong, "G0301H")
        self.assertEqual(token.strong_segments[1].role, "alt")
        self.assertEqual(token.strong_segments[1].strong, "G300")
        self.assertIn("G0300", token.meaning_variants)
        self.assertIn("Ἀμών", token.spelling_variants)

        raw_payload = json.loads(token.raw_json)
        self.assertIn("G0300", raw_payload["meaning_variants"])
        self.assertIn("TR+Byz", raw_payload["spelling_variants"])

    def test_token_rows_fit_phase_three_schema(self) -> None:
        token = parse_tagnt_row(MATTHEW_1_1_ROWS[2])
        self.assertIsNotNone(token)
        assert token is not None
        verse = build_na28_module_verses([token])[0]

        connection = sqlite3.connect(":memory:")
        try:
            create_bible_module_schema(
                connection,
                include_token_tables=True,
                date_iso="2026-05-23T00:00:00Z",
            )
            insert_minimal_module_fixture(
                connection,
                code="NA28_LXX",
                module_kind="original_language",
                source_text_id=TAGNT_SOURCE_TEXT_ID,
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
                  subverse,
                  text_plain,
                  text_display,
                  tokens_count,
                  sort_key
                )
                VALUES(
                  :module_verse_id,
                  :source_text_id,
                  :native_ref,
                  :book_id,
                  :chapter,
                  :verse,
                  :subverse,
                  :text_plain,
                  :text_display,
                  :tokens_count,
                  :sort_key
                )
                """,
                verse.as_module_verse_row(module_verse_id=1),
            )
            connection.execute(
                """
                INSERT INTO module_verse_links(
                  module_verse_id,
                  canonical_verse_id,
                  link_kind,
                  note
                )
                VALUES(
                  :module_verse_id,
                  :canonical_verse_id,
                  :link_kind,
                  :note
                )
                """,
                verse.as_module_verse_link_row(module_verse_id=1),
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
                  :token_id,
                  :module_verse_id,
                  :source_text_id,
                  :token_order,
                  :source_ref,
                  :text_type,
                  :surface,
                  :surface_normalized,
                  :surface_search,
                  :transliteration,
                  :lemma,
                  :morphology,
                  :gloss,
                  :raw_json
                )
                """,
                token.as_token_row(module_verse_id=1, token_id=1),
            )
            for strong_row in token.token_strong_rows(token_id=1):
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
                    VALUES(
                      :token_id,
                      :strong,
                      :raw_strong,
                      :role,
                      :segment_order,
                      :segment_surface,
                      :is_primary
                    )
                    """,
                    strong_row,
                )

            stored = connection.execute(
                """
                SELECT strong, raw_strong
                FROM token_strongs
                WHERE token_id = 1
                """
            ).fetchone()
            self.assertEqual(tuple(stored), ("G2424", "G2424G"))
        finally:
            connection.close()

    def test_surface_search_strips_display_punctuation(self) -> None:
        self.assertEqual(surface_search_text("[[Πάντα,"), "Πάντα")


if __name__ == "__main__":
    unittest.main()

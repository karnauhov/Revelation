from __future__ import annotations

import unittest

from scripts.bible_module.canon import (
    BOOKS_BY_CODE,
    CANONICAL_BOOKS,
    CANON_POLICY,
    LXX_BOOK_MAPPINGS,
    assert_lxx_source_ref_allowed,
    canonical_verse_id_for,
    canonical_verse_rows,
    canonical_verses,
    get_canonical_verse,
    lxx_book_id_for_source_book,
    lxx_canonical_code_for_source_book,
    parse_canonical_ref,
)
from scripts.bible_module.guards import ImportGuardError


class BibleCanonTests(unittest.TestCase):
    def test_canonical_books_are_exactly_66_with_stable_ids(self) -> None:
        self.assertEqual(len(CANONICAL_BOOKS), 66)
        self.assertEqual([book.book_id for book in CANONICAL_BOOKS], list(range(1, 67)))
        self.assertEqual(sum(1 for book in CANONICAL_BOOKS if book.testament == "OT"), 39)
        self.assertEqual(sum(1 for book in CANONICAL_BOOKS if book.testament == "NT"), 27)
        self.assertEqual(CANONICAL_BOOKS[0].canonical_code, "Gen")
        self.assertEqual(CANONICAL_BOOKS[-1].canonical_code, "Rev")

    def test_canonical_verse_table_is_module_independent_and_complete(self) -> None:
        verses = canonical_verses()
        rows = canonical_verse_rows()

        self.assertEqual(len(verses), 31_102)
        self.assertEqual(len(rows), 31_102)
        self.assertEqual(verses[0].canonical_ref, "Gen.1.1")
        self.assertEqual(verses[-1].canonical_ref, "Rev.22.21")
        self.assertEqual(verses[0].osis_ref, "Gen.1.1")
        self.assertEqual(verses[-1].osis_ref, "Rev.22.21")

    def test_canonical_refs_and_ids_are_stable(self) -> None:
        gen_1_1 = get_canonical_verse("Gen", 1, 1)
        mat_1_1 = get_canonical_verse("Mat", 1, 1)
        rev_22_21 = get_canonical_verse("Rev", 22, 21)

        self.assertEqual(gen_1_1.canonical_verse_id, canonical_verse_id_for(1, 1, 1))
        self.assertEqual(gen_1_1.canonical_ref, "Gen.1.1")
        self.assertEqual(mat_1_1.canonical_ref, "Mat.1.1")
        self.assertEqual(mat_1_1.osis_ref, "Matt.1.1")
        self.assertEqual(rev_22_21.canonical_ref, "Rev.22.21")
        self.assertEqual(parse_canonical_ref("Rev.22.21"), rev_22_21)

    def test_rejects_out_of_range_canonical_refs(self) -> None:
        with self.assertRaises(KeyError):
            get_canonical_verse("Ps", 151, 1)
        with self.assertRaises(KeyError):
            get_canonical_verse("Ps", 3, 0)
        with self.assertRaises(KeyError):
            parse_canonical_ref("Rev.22.22")

    def test_phase_two_reference_storage_policy_is_explicit(self) -> None:
        self.assertIn("native_ref", CANON_POLICY.source_native_ref_storage)
        self.assertIn("osis_ref", CANON_POLICY.osis_ref_storage)
        self.assertIn("Protestant/English Psalm numbering", CANON_POLICY.psalm_numbering)
        self.assertIn("Greek additions are excluded", CANON_POLICY.esther)
        self.assertIn("Susanna", CANON_POLICY.daniel)

    def test_lxx_kingdoms_and_paraleipomenon_mapping_rules(self) -> None:
        expected = {
            "1 Kingdoms": "1Sam",
            "2 Kingdoms": "2Sam",
            "3 Kingdoms": "1Kgs",
            "4 Kingdoms": "2Kgs",
            "1 Paraleipomenon": "1Chr",
            "2 Paraleipomenon": "2Chr",
        }

        self.assertTrue(
            expected.items()
            <= {
                (mapping.source_name, mapping.canonical_code)
                for mapping in LXX_BOOK_MAPPINGS
            }
        )
        for source_name, canonical_code in expected.items():
            with self.subTest(source_name=source_name):
                self.assertEqual(
                    lxx_canonical_code_for_source_book(source_name),
                    canonical_code,
                )
                self.assertEqual(
                    lxx_book_id_for_source_book(source_name),
                    BOOKS_BY_CODE[canonical_code].book_id,
                )

    def test_lxx_canonical_aliases_resolve_to_66_book_codes(self) -> None:
        for source_name in ("Genesis", "Psalms", "Daniel", "Matthew", "Rev"):
            with self.subTest(source_name=source_name):
                canonical_code = lxx_canonical_code_for_source_book(source_name)
                self.assertIn(canonical_code, BOOKS_BY_CODE)

    def test_non_canonical_lxx_books_and_ranges_are_rejected(self) -> None:
        for source_book in (
            "Tobit",
            "Tob",
            "Judith",
            "Jdt",
            "Wisdom of Solomon",
            "Sirach",
            "Baruch",
            "EpJer",
            "1Esd",
            "2 Esdras",
            "1 Maccabees",
            "2Macc",
            "Odes",
            "PrMan",
            "Prayer of Manasseh",
            "Ps151",
            "Susanna",
            "Bel and the Dragon",
            "PrAzar",
            "Prayer of Azariah",
            "AddEsth",
            "Greek Esther Additions",
        ):
            with self.subTest(source_book=source_book):
                with self.assertRaises(ImportGuardError):
                    lxx_canonical_code_for_source_book(source_book)

        for source_book, chapter, verse in (
            ("Psalms", 151, 1),
            ("Esther", 11, 1),
            ("Daniel", 13, 1),
            ("Daniel", 14, 1),
        ):
            with self.subTest(source_book=source_book, chapter=chapter, verse=verse):
                with self.assertRaises(ImportGuardError):
                    assert_lxx_source_ref_allowed(source_book, chapter=chapter, verse=verse)

    def test_canonical_lxx_refs_are_allowed(self) -> None:
        assert_lxx_source_ref_allowed("Genesis", chapter=1, verse=1)
        assert_lxx_source_ref_allowed("1 Kingdoms", chapter=1, verse=1)
        assert_lxx_source_ref_allowed("Esther", chapter=10, verse=3)
        assert_lxx_source_ref_allowed("Daniel", chapter=12, verse=13)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.content_tool.bible_map import BibleCatalog
from scripts.content_tool.mixins.bibles import bible_project_root


class BibleCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        project_root = Path(__file__).resolve().parents[3]
        cls.catalog = BibleCatalog.load(project_root)

    def test_catalog_matches_application_canon(self) -> None:
        self.assertEqual(len(self.catalog.books), 66)
        self.assertEqual(self.catalog.total_verses, 31102)
        self.assertEqual(self.catalog.books[0].code, "Gen")
        self.assertEqual(self.catalog.books[-1].code, "Rev")

    def test_content_tool_project_root_contains_canonical_map(self) -> None:
        map_path = bible_project_root() / "assets" / "data" / "bible_verse_map.json"
        self.assertTrue(map_path.is_file(), map_path)

    def test_book_lookup_accepts_the_label_used_by_the_combobox(self) -> None:
        book = self.catalog.books[0]
        self.assertEqual(self.catalog.book_for_value(book.display_label()), book)

    def test_key_and_reference_mapping_matches_app_format(self) -> None:
        self.assertEqual(self.catalog.key_for(book_id=1, chapter=1, verse=1), "001")
        self.assertEqual(self.catalog.key_for(book_id=66, chapter=22, verse=21), "NZY")
        reference = self.catalog.reference_for_key("NZY")
        self.assertIsNotNone(reference)
        assert reference is not None
        self.assertEqual((reference[0].id, reference[1], reference[2]), (66, 22, 21))

    def test_reference_parser_accepts_application_book_codes_and_names(self) -> None:
        for value in ("Gen 1:1", "Genesis 1:1", "Откровение 22:21", "Rev 22:21"):
            reference = self.catalog.parse_reference(value)
            self.assertIsNotNone(reference, value)

    def test_chapter_keys_are_in_canonical_order(self) -> None:
        keys = self.catalog.verse_keys_for_chapter(book_id=19, chapter=1)
        self.assertEqual(len(keys), 6)
        self.assertEqual(keys, tuple(self.catalog.key_for(book_id=19, chapter=1, verse=index) for index in range(1, 7)))


if __name__ == "__main__":
    unittest.main()

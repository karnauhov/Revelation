from __future__ import annotations

import unittest

from scripts.bible_module.guards import (
    ImportGuardError,
    assert_canonical_import_book,
    assert_no_forbidden_books,
    assert_source_allowed,
)


class BibleImportGuardTests(unittest.TestCase):
    def test_rejects_known_apocryphal_books(self) -> None:
        for book in (
            "Tob",
            "Judith",
            "Wisdom of Solomon",
            "Psalm 151",
            "Odes",
            "1 Maccabees",
            "2 Esdras",
        ):
            with self.subTest(book=book):
                with self.assertRaises(ImportGuardError):
                    assert_canonical_import_book(book)

    def test_allows_canonical_book_names(self) -> None:
        assert_no_forbidden_books(["Genesis", "1 Kingdoms", "Matthew", "Revelation"])

    def test_rejects_rvr1960_without_explicit_permission(self) -> None:
        with self.assertRaisesRegex(ImportGuardError, "RVR1960"):
            assert_source_allowed("RVR1960")

    def test_allows_rvr1960_with_explicit_permission(self) -> None:
        assert_source_allowed("RVR1960", explicit_rvr1960_permission=True)


if __name__ == "__main__":
    unittest.main()

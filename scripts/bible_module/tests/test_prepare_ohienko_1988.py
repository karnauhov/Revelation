from __future__ import annotations

import unittest

from scripts.bible_module.prepare_ohienko_1988 import classify_change, rebase_splits


class SourceCorrectionTests(unittest.TestCase):
    def test_only_page_separators_and_verified_missing_continuations_are_accepted(self):
        self.assertEqual(classify_change("Gen.1.1", "дваслова", "два слова"), "page_word_separator")
        for ref in ("Deut.34.8", "Rev.1.3"):
            self.assertEqual(classify_change(ref, "Початок", "Початок продовження"),
                             "restored_page_continuation")
        for ref, before, after in [
            ("Gen.1.1", "Початок", "Початок продовження"),
            ("Rev.1.3", "Слова", "Інші слова"),
            ("Rev.1.3", "Увесь текст", "Увесь"),
            ("Rev.22.21", "Кінець. біблійні слова", "Кінець."),
        ]:
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                classify_change(ref, before, after)

    def test_only_image_carriers_can_be_removed_from_final_verse(self):
        self.assertEqual(classify_change("Rev.22.21", "Кінець. 400px|center|сторінка=1529", "Кінець."),
                         "noncanonical_image_carrier_removed")

    def test_reviewed_split_rebases_ids_without_changing_intervals(self):
        rule = {"operation": "split", "rule_id": "new-rule",
                "targets": [{"ref": "Ps.13.5"}, {"ref": "Ps.13.6"}],
                "source_parts": [{"record_id": "new-source"}]}
        override = {"record_id": "old-source", "rule_id": "old-rule",
                    "target_intervals": [{"target_ref": "Ps.13.5", "start_scalar": 0, "end_scalar": 1},
                                         {"target_ref": "Ps.13.6", "start_scalar": 2, "end_scalar": 3}]}
        old = {"old-source": {"text": "а б"}}
        new = {"new-source": {"text": "а б"}}
        result = rebase_splits([rule], new, old, [override])["new-rule"]
        self.assertEqual(result["record_id"], "new-source")
        self.assertEqual(result["target_intervals"], override["target_intervals"])
        self.assertEqual(override["record_id"], "old-source")
        with self.assertRaisesRegex(ValueError, "split source changed"):
            rebase_splits([rule], {"new-source": {"text": "а в"}}, old, [override])
        with self.assertRaisesRegex(ValueError, "Not all"):
            rebase_splits([], new, old, [override])


if __name__ == "__main__":
    unittest.main()

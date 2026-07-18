from __future__ import annotations

import sqlite3
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.bible_module.audit_kjv_tr_strongs import (
    BibleModule,
    StrongFilter,
    StrongVerseScore,
    build_match_distribution,
    build_match_ranges,
    compare_new_testaments,
    format_report,
    read_module,
    read_strong_filter,
    strong_counter,
)


class AuditKjvTrStrongsTests(unittest.TestCase):
    def test_match_distribution_keeps_exact_zero_and_hundred_separate(self) -> None:
        scores = (
            _score("100", matched=20, total=20),
            _score("95", matched=19, total=20),
            _score("90", matched=18, total=20),
            _score("5", matched=1, total=20),
            _score("between_zero_and_five", matched=1, total=30),
            _score("0", matched=0, total=20),
        )

        distribution = build_match_distribution(scores)

        self.assertEqual(
            [(bucket.label, bucket.verses_count) for bucket in distribution],
            [
                ("100%", 1),
                ("95–<100%", 1),
                ("90–<95%", 1),
                ("85–<90%", 0),
                ("80–<85%", 0),
                ("75–<80%", 0),
                ("70–<75%", 0),
                ("65–<70%", 0),
                ("60–<65%", 0),
                ("55–<60%", 0),
                ("50–<55%", 0),
                ("45–<50%", 0),
                ("40–<45%", 0),
                ("35–<40%", 0),
                ("30–<35%", 0),
                ("25–<30%", 0),
                ("20–<25%", 0),
                ("15–<20%", 0),
                ("10–<15%", 0),
                ("5–<10%", 1),
                ("0–<5%", 1),
                ("0%", 1),
            ],
        )

    def test_match_ranges_use_exact_fraction_boundaries(self) -> None:
        scores = (
            _score("zero", matched=0, total=20),
            _score("below_half", matched=1, total=3),
            _score("half", matched=10, total=20),
            _score("two_thirds", matched=2, total=3),
            _score("three_quarters", matched=3, total=4),
            _score("four_fifths", matched=4, total=5),
        )

        ranges = build_match_ranges(scores)

        self.assertEqual(
            [(match_range.label, len(match_range.verse_scores)) for match_range in ranges],
            [
                ("<50%", 2),
                ("50%–<66,(6)%", 1),
                ("66,(6)%–<75%", 1),
                ("75%–<80%", 1),
            ],
        )

    def test_strong_counter_normalizes_order_and_preserves_multiplicity(self) -> None:
        self.assertEqual(
            strong_counter("word G002 word H0007 word G2a"),
            Counter({"G2": 2, "H7": 1}),
        )

    def test_strong_counter_excludes_configured_weak_numbers(self) -> None:
        self.assertEqual(
            strong_counter(
                "article G3588 word G25 word G3588",
                excluded_strongs=frozenset({"G3588"}),
            ),
            Counter({"G25": 1}),
        )

    def test_compare_ignores_order_but_reports_count_difference(self) -> None:
        kjv = BibleModule(
            Path("kjv.sqlite"),
            {
                "001": "one G2 two G1 G1",
                "002": "one G5 G7",
            },
        )
        lxx_tr = BibleModule(
            Path("lxx.sqlite"),
            {
                "001": "one G1 two G2 G1",
                "002": "one G5 G6 G6",
            },
        )

        comparison = compare_new_testaments(
            kjv,
            lxx_tr,
            nt_keys=("001", "002"),
            refs_by_key={"001": "Mat.1.1", "002": "Mat.1.2"},
            excluded_strongs=frozenset({"G3588"}),
        )

        self.assertEqual(comparison.compared_verses_count, 2)
        self.assertEqual(comparison.mismatched_verses_count, 1)
        mismatch = comparison.mismatches[0]
        self.assertEqual(mismatch.verse_ref, "Mat.1.2")
        self.assertEqual(mismatch.kjv_only, Counter({"G7": 1}))
        self.assertEqual(mismatch.tr_only, Counter({"G6": 2}))
        self.assertEqual(mismatch.matched_count, 1)
        self.assertEqual(mismatch.tr_total_count, 3)
        self.assertEqual(mismatch.tr_unmatched_count, 2)
        self.assertEqual(mismatch.kjv_extra_count, 1)
        self.assertAlmostEqual(mismatch.tr_match_ratio, 1 / 3)
        self.assertAlmostEqual(mismatch.tr_mismatch_ratio, 2 / 3)
        self.assertEqual(mismatch.different_occurrences_count, 3)
        self.assertEqual(comparison.matched_count, 4)
        self.assertEqual(comparison.tr_total_count, 6)
        self.assertEqual(comparison.tr_unmatched_count, 2)
        self.assertEqual(comparison.kjv_extra_count, 1)

        self.assertEqual(comparison.chapter_scores[0].label, "Mat.1")
        self.assertEqual(comparison.book_scores[0].label, "Mat")
        self.assertEqual(comparison.max_chapter_tr_mismatch[0].label, "Mat.1")
        self.assertEqual(comparison.max_book_tr_mismatch[0].label, "Mat")

    def test_read_module_and_report_list_empty_verses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "module.sqlite"
            connection = sqlite3.connect(path)
            try:
                connection.execute(
                    "CREATE TABLE verses(verse_key TEXT PRIMARY KEY, text TEXT NOT NULL)"
                )
                connection.executemany(
                    "INSERT INTO verses(verse_key, text) VALUES(?, ?)",
                    [("001", "text G1"), ("002", "   ")],
                )
                connection.commit()
            finally:
                connection.close()

            module = read_module(path)
            self.assertEqual(module.empty_keys, ("002",))
            comparison = compare_new_testaments(
                module,
                module,
                nt_keys=("001",),
                refs_by_key={"001": "Mat.1.1", "002": "Mat.1.2"},
            )
            report = format_report(
                module,
                module,
                refs_by_key={"001": "Mat.1.1", "002": "Mat.1.2"},
                comparison=comparison,
                strong_filter=StrongFilter(
                    source_path=Path("filter.json"),
                    groups={"article": ("G3588",)},
                ),
            )

            self.assertIn("Пустых стихов: 1 (50.00%)", report)
            self.assertIn("Mat.1.2 [002]", report)
            self.assertIn("Несовпадающих стихов: 0 из 1 (0.00%)", report)
            self.assertIn(
                "Mat.1.1 [001]: TR=1; совпало=1; не совпало по TR=0; "
                "лишних KJV=0; совпадение=100.00%",
                report,
            )
            self.assertIn("Максимум по главам — несовпадение относительно TR", report)

    def test_reads_asset_groups_and_excludes_negative_categories(self) -> None:
        strong_filter = read_strong_filter()

        self.assertEqual(len(strong_filter.excluded_strongs), 77)
        self.assertIn("G3588", strong_filter.excluded_strongs)
        self.assertNotIn("G3361", strong_filter.excluded_strongs)
        self.assertNotIn("G3756", strong_filter.excluded_strongs)

def _score(label: str, *, matched: int, total: int) -> StrongVerseScore:
    return StrongVerseScore(
        verse_key=label,
        verse_ref=f"Mat.1.{label}",
        kjv_counts=Counter({f"G{index}": 1 for index in range(1, matched + 1)}),
        tr_counts=Counter({f"G{index}": 1 for index in range(1, total + 1)}),
    )


if __name__ == "__main__":
    unittest.main()


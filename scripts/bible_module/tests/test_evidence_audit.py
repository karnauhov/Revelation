from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.evidence_audit import (
    _GUTENBERG_BOOK_TITLES,
    _neighbor_index_check,
    alt_aware_metrics,
    audit_compact_index,
    metrics_for_sequences,
    parse_osis_verses,
    parse_project_gutenberg_kjv,
)


class EvidenceAuditTests(unittest.TestCase):
    def test_metrics_include_multiset_and_ordered_views(self) -> None:
        metrics = metrics_for_sequences(
            ("G1", "G2", "G1"),
            ("G2", "G1", "G3"),
        )

        self.assertEqual(metrics.matched, 2)
        self.assertEqual(metrics.tr_only_count, 1)
        self.assertEqual(metrics.kjv_only_count, 1)
        self.assertAlmostEqual(metrics.tr_recall, 2 / 3)
        self.assertAlmostEqual(metrics.kjv_precision, 2 / 3)
        self.assertAlmostEqual(metrics.f1, 2 / 3)
        self.assertAlmostEqual(metrics.multiset_jaccard, 1 / 2)
        self.assertEqual(metrics.ordered_matched, 2)

    def test_alt_aware_metrics_match_each_tr_token_at_most_once(self) -> None:
        metrics = alt_aware_metrics(
            ("G5213", "G5213", "G25"),
            (
                frozenset({"G4771", "G5213"}),
                frozenset({"G25"}),
            ),
        )

        self.assertEqual(metrics.matched, 2)
        self.assertAlmostEqual(metrics.tr_recall, 1.0)
        self.assertAlmostEqual(metrics.kjv_precision, 2 / 3)

    def test_osis_parser_normalizes_matthew_alias_and_strong_keys(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">
  <osisText>
    <verse osisID="Matt.1.1" sID="Matt.1.1"/>
    <w lemma="strong:G0976">The book</w>.
    <verse eID="Matt.1.1"/>
  </osisText>
</osis>
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.xml"
            path.write_text(xml, encoding="utf-8")
            verses = parse_osis_verses(path)

        self.assertEqual(tuple(verses), ("Mat.1.1",))
        self.assertEqual(verses["Mat.1.1"].text, "The book.")
        self.assertEqual(verses["Mat.1.1"].strong_sequence, ("G976",))

    def test_index_audit_uses_query_only_and_detects_exact_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "module.sqlite"
            connection = sqlite3.connect(path)
            try:
                connection.execute(
                    "CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT)"
                )
                connection.executemany(
                    "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
                    [
                        ("schema_version", "3"),
                        ("data_version", "1"),
                        ("date", "2026-07-25T00:00:00Z"),
                    ],
                )
                connection.execute(
                    "CREATE TABLE verses(verse_key TEXT PRIMARY KEY, text TEXT)"
                )
                connection.executemany(
                    "INSERT INTO verses(verse_key, text) VALUES(?, ?)",
                    [("001", "one"), ("002", "two")],
                )
                connection.commit()
            finally:
                connection.close()

            result = audit_compact_index(
                path,
                {"001": "Mat.1.1", "002": "Mat.1.2"},
            )

        self.assertEqual(result.query_only, 1)
        self.assertEqual(result.integrity_check, "ok")
        self.assertEqual(result.verse_rows, 2)
        self.assertTrue(result.keys_are_exact_base36_sequence)
        self.assertEqual(result.duplicate_keys, ())
        self.assertEqual(result.missing_keys, ())
        self.assertEqual(result.extra_keys, ())

    def test_gutenberg_parser_handles_inline_and_end_of_line_markers(self) -> None:
        lines = [
            "*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE ***",
            "The Old Testament of the King James Version of the Bible",
            *_GUTENBERG_BOOK_TITLES,
            "The Old Testament of the King James Version of the Bible",
        ]
        for index, title in enumerate(_GUTENBERG_BOOK_TITLES):
            if index == 39:
                lines.append("The New Testament of the King James Bible")
            lines.append(title)
            lines.append(
                "1:1 first 1:2"
                if index == 0
                else "1:1 only"
            )
            if index == 0:
                lines.append("second")
        lines.append("*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE ***")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gutenberg.txt"
            path.write_text("\n".join(lines), encoding="utf-8")
            verses = parse_project_gutenberg_kjv(path)

        self.assertEqual(len(verses), 67)
        self.assertEqual(verses["Gen.1.1"], "first")
        self.assertEqual(verses["Gen.1.2"], "second")
        self.assertEqual(verses["Rev.1.1"], "only")

    def test_neighbor_check_keeps_confirmed_same_reference_unshifted(self) -> None:
        result = _neighbor_index_check(
            verse_ref="Mat.1.2",
            local_kjv_text="current text",
            local_tr_text="α G1 β G2",
            kjv_usfx_texts={
                "Mat.1.1": "previous text",
                "Mat.1.2": "current text",
                "Mat.1.3": "next text",
            },
            scrivener={
                "Mat.1.1": "g d",
                "Mat.1.2": "a b",
                "Mat.1.3": "e z",
            },
            same_ref_text_checks=_same_ref_checks(True),
        )

        self.assertFalse(result["probable_shift"])
        self.assertEqual(
            result["same_ref_tr_scrivener_sequence_ratio"],
            1.0,
        )

    def test_neighbor_check_flags_text_matching_previous_reference(self) -> None:
        result = _neighbor_index_check(
            verse_ref="Mat.1.2",
            local_kjv_text="previous text",
            local_tr_text="α G1 β G2",
            kjv_usfx_texts={
                "Mat.1.1": "previous text",
                "Mat.1.2": "current text",
                "Mat.1.3": "next text",
            },
            scrivener={
                "Mat.1.1": "g d",
                "Mat.1.2": "a b",
                "Mat.1.3": "e z",
            },
            same_ref_text_checks=_same_ref_checks(False),
        )

        self.assertTrue(result["probable_shift"])
        self.assertTrue(
            result["neighbors"]["previous"]["kjv_locked_normalized_match"]
        )

def _same_ref_checks(value: bool) -> dict[str, bool]:
    return {
        "module_vs_locked_usfx_strict": value,
        "module_vs_crosswire_3_1_normalized": value,
        "module_vs_open_bibles_normalized": value,
        "module_vs_project_gutenberg_normalized": value,
    }


if __name__ == "__main__":
    unittest.main()

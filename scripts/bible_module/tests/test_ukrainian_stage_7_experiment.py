from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.bible_module.ukrainian_stage_7_experiment_model import (
    CONTRACT_VERSION,
    SynthesisPart,
    join_synthesis_parts,
    lexical_score,
    maximum_weight_assignment,
    multiset_metrics,
    rebase_anchor,
    render_strong_markup,
    serialize_comment_uses,
    strip_strong_markup,
    validate_partition,
    validate_strong,
    word_tokens,
)
from scripts.bible_module.ukrainian_stage_7_experiment import (
    _control_strongs,
    _sequence_severity,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7_experiment"
    / "synthesis_alignment_cases.json"
)
REPORT = (
    ROOT / "scripts/bible_module/reports/ukrainian_stage_7_experiment_20260801"
)


class SynthesisContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = cls.fixture["cases"]

    def test_fixture_is_cc0(self) -> None:
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def test_one_to_one_synthesis(self) -> None:
        case = self.cases["one_to_one"]
        text, parts = join_synthesis_parts([tuple(case)])
        self.assertEqual(text, "Слово світле")
        self.assertEqual((parts[0].target_start, parts[0].target_end), (0, 12))

    def test_merge_order_and_separator(self) -> None:
        text, parts = join_synthesis_parts(
            [tuple(part) for part in self.cases["merge"]]
        )
        self.assertEqual(text, "Перша частина")
        self.assertEqual(parts[1].target_start, 6)

    def test_existing_whitespace_is_not_duplicated(self) -> None:
        text, _ = join_synthesis_parts(
            [("a", 0, 6, "Перша "), ("b", 0, 7, "частина")]
        )
        self.assertEqual(text, "Перша частина")

    def test_split_exact_partition_with_separator_interval(self) -> None:
        validate_partition(13, [tuple(pair) for pair in self.cases["split_intervals"]])

    def test_split_boundary_ambiguity_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_partition(13, [(0, 6), (7, 13)])
        with self.assertRaises(ValueError):
            validate_partition(13, [(0, 8), (7, 13)])

    def test_source_only_range_is_not_joined_to_target(self) -> None:
        source_only = self.cases["range_source_only"]
        target, _ = join_synthesis_parts([("target", 0, 5, "Вірш")])
        self.assertNotIn(source_only, target)


class StrongContractTest(unittest.TestCase):
    def test_ot_and_nt_classic_ranges(self) -> None:
        self.assertTrue(validate_strong("H1254"))
        self.assertTrue(validate_strong("G3056"))
        self.assertFalse(validate_strong("H9003"))
        self.assertFalse(validate_strong("G5625"))
        self.assertFalse(validate_strong("G2424G"))

    def test_reordered_omitted_and_repeated_words(self) -> None:
        plain = "Другий перший доданий"
        tokens = word_tokens(plain)
        marked = render_strong_markup(
            plain,
            tokens,
            {1: ["H2"], 2: ["H1", "H1"]},
        )
        self.assertIn("Другий H2", marked)
        self.assertIn("перший H1 H1", marked)
        self.assertNotRegex(marked, r"доданий H")
        self.assertEqual(strip_strong_markup(marked), plain)

    def test_multiple_strong_on_one_surface_token(self) -> None:
        plain = "Складений вислів."
        marked = render_strong_markup(
            plain, word_tokens(plain), {1: ["G1", "G2", "G3"]}
        )
        self.assertEqual(strip_strong_markup(marked), plain)
        self.assertIn("Складений G1 G2 G3", marked)

    def test_plain_text_round_trip_property(self) -> None:
        samples = [
            "Слово.",
            "Апострофʼи та дефіс-слово!",
            "Число 12, повтор повтор.",
            "Рядок — з пунктуацією?",
        ]
        for plain in samples:
            tokens = word_tokens(plain)
            mapping = {
                token.order: [f"G{token.order}"]
                for token in tokens
                if token.order <= 4
            }
            self.assertEqual(
                strip_strong_markup(render_strong_markup(plain, tokens, mapping)),
                plain,
            )

    def test_lexical_evidence_can_override_position(self) -> None:
        lexical = lexical_score(
            joint=20,
            strong_frequency=22,
            word_frequency=25,
            verse_count=100,
            source_position=0.1,
            target_position=0.9,
        )
        positional = lexical_score(
            joint=1,
            strong_frequency=22,
            word_frequency=25,
            verse_count=100,
            source_position=0.1,
            target_position=0.1,
        )
        self.assertGreater(lexical, positional)

    def test_control_raw_values_are_preserved_during_normalization(self) -> None:
        tahot = _control_strongs("tahot", {"strong_raw": ["H0430G", "H9003"]})
        self.assertEqual(
            tahot,
            [
                {
                    "final": "H430",
                    "normalization": "extended_base_sense_comparison_only",
                    "raw": "H0430G",
                }
            ],
        )
        ugnt = _control_strongs("ugnt", {"strong_raw": ["G09760"]})
        self.assertEqual(ugnt[0]["final"], "G976")
        self.assertEqual(ugnt[0]["raw"], "G09760")
        tagnt = _control_strongs(
            "tagnt",
            {
                "extra": {"fields": {"alternative_strongs": "G3778"}},
                "strong": [
                    {"normalized": "G846", "raw": "G0846", "status": "classic"},
                    {"normalized": "G3778", "raw": "G3778", "status": "classic"},
                ],
            },
        )
        self.assertEqual([item["final"] for item in tagnt], ["G846"])

    def test_ordered_control_metrics_and_severity(self) -> None:
        metrics = multiset_metrics(["G1", "G2", "G3"], ["G3", "G2", "G1"])
        self.assertEqual(metrics["f1"], 1.0)
        self.assertAlmostEqual(metrics["ordered_f1"], 1 / 3, places=6)
        self.assertEqual(_sequence_severity(metrics), "low")

    def test_global_assignment_supports_reordering_and_unique_capacity(self) -> None:
        # The maximum requires a crossed (reordered) assignment.
        self.assertEqual(
            maximum_weight_assignment([[1.0, 9.0], [8.0, 2.0]]),
            [1, 0],
        )
        with self.assertRaises(ValueError):
            maximum_weight_assignment([[1.0], [2.0]])


class FootnoteContractTest(unittest.TestCase):
    def test_anchor_rebases_through_exact_merge_part(self) -> None:
        parts = [
            SynthesisPart("a", 0, 5, 0, 5, "Перша"),
            SynthesisPart("b", 0, 7, 6, 13, "частина"),
        ]
        self.assertEqual(rebase_anchor(2, 4, parts[:1]), (2, 4))
        self.assertEqual(rebase_anchor(1, 1, parts[1:]), (7, 7))

    def test_no_automatic_nearest_binding(self) -> None:
        parts = [SynthesisPart("a", 0, 5, 0, 5, "Перша")]
        with self.assertRaises(ValueError):
            rebase_anchor(6, 6, parts)

    def test_comment_order_named_reuse_and_markerless_use(self) -> None:
        uses = [
            {
                "footnote_id": "named",
                "full_text_nfc": "Повторне визначення",
                "marker": None,
                "source_order": 3,
                "use_id": "u3",
            },
            {
                "footnote_id": "named",
                "full_text_nfc": "Повторне визначення",
                "marker": "1",
                "source_order": 1,
                "use_id": "u1",
            },
            {
                "footnote_id": "other",
                "full_text_nfc": "Інший текст",
                "marker": "2",
                "source_order": 2,
                "use_id": "u2",
            },
        ]
        self.assertEqual(
            serialize_comment_uses(uses),
            "1 Повторне визначення\n\n2 Інший текст\n\nПовторне визначення",
        )


class FullArtifactInvariantTest(unittest.TestCase):
    def test_reports_preserve_experimental_contract(self) -> None:
        if not (REPORT / "synthesized_text.manifest.json").exists():
            self.skipTest("Stage-6 reports are generated only in the stage workspace")
        for name in [
            "synthesized_text.manifest.json",
            "strong_alignment.manifest.json",
            "footnote_comment_projection.manifest.json",
        ]:
            value = json.loads((REPORT / name).read_text(encoding="utf-8"))
            self.assertEqual(value["contract_version"], CONTRACT_VERSION)
            self.assertEqual(value["counts"]["error"], 0)

    def test_exact_31102_target_key_equality_evidence(self) -> None:
        baseline = json.loads(
            (
                ROOT
                / "scripts/bible_module/reports/ukrainian_stage_2_20260801/baseline_manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(baseline["target_grid"]["verses_count"], 31_102)
        manifest = json.loads(
            (
                ROOT
                / "scripts/bible_module/reports/ukrainian_stage_5_20260801/target_to_source_map.manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["processed_count"], 31_102)
        reverse_path = (
            ROOT
            / "scripts/bible_module/work/ukrainian_stage_5_20260801/target_to_source_map.jsonl"
        )
        if reverse_path.exists():
            expected = []
            keys = baseline["target_grid"]["verse_keys"]
            key_index = 0
            for book in baseline["target_grid"]["books"]:
                for chapter, last_verse in enumerate(book["chapters"], 1):
                    for verse in range(1, int(last_verse) + 1):
                        expected.append(
                            (f"{book['code']}.{chapter}.{verse}", str(keys[key_index]))
                        )
                        key_index += 1
            with reverse_path.open(encoding="utf-8") as handle:
                actual = [
                    (row["target_ref"], row["verse_key"])
                    for row in (json.loads(line) for line in handle)
                ]
            self.assertEqual(actual, expected)

    def test_heading_footnotes_remain_non_verse(self) -> None:
        if not (REPORT / "footnote_comment_stats.json").exists():
            self.skipTest("Stage-6 reports are generated only in the stage workspace")
        value = json.loads(
            (REPORT / "footnote_comment_stats.json").read_text(encoding="utf-8")
        )
        self.assertEqual(value["statistics"]["heading_non_verse_use_count"], 11)
        self.assertEqual(value["statistics"]["unresolved_anchor_count"], 0)

    def test_full_coverage_and_independent_control_audits(self) -> None:
        value = json.loads(
            (REPORT / "strong_coverage_report.json").read_text(encoding="utf-8")
        )
        stats = value["statistics"]
        self.assertEqual(stats["no_primary_control_target_count"], 0)
        self.assertEqual(sum(stats["control_target_counts"].values()), 31_102)
        self.assertEqual(
            sum(stats["uxlc_surface_triage_before_resolution"].values()), 23_145
        )
        self.assertEqual(stats["invalid_strong_count"], 0)
        self.assertEqual(stats["unresolved_high_count"], 1)
        self.assertEqual(value["status"], "incomplete_manual_review_required")
        self.assertGreater(stats["manual_review_required_strong_count"], 0)
        self.assertEqual(
            stats["manual_review_required_strong_count"],
            stats["alignment_confidence"]["low"],
        )
        self.assertGreater(stats["manual_review_required_target_count"], 0)
        self.assertEqual(len(stats["book_coverage"]), 66)
        self.assertEqual(len(stats["chapter_coverage"]), 1_189)
        self.assertEqual(
            stats["aligned_surface_token_count"]
            + stats["unaligned_surface_token_count"],
            stats["surface_token_count"],
        )
        control_manifest = json.loads(
            (REPORT / "strong_control_audit.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        unaligned_manifest = json.loads(
            (REPORT / "unaligned_surface_tokens.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(control_manifest["counts"]["processed"], 31_102)
        self.assertEqual(
            unaligned_manifest["counts"]["processed"],
            stats["unaligned_surface_token_count"],
        )

    def test_rule_counts_and_source_only_material(self) -> None:
        value = json.loads(
            (REPORT / "plain_text_preservation_report.json").read_text(
                encoding="utf-8"
            )
        )
        stats = value["source_token_accounting"]
        self.assertEqual(
            stats["operation_rule_counts"],
            {"1:1": 31_026, "merge": 68, "range_transfer": 1, "split": 4},
        )
        self.assertEqual(stats["source_only_count"], 1)
        self.assertEqual(stats["source_span_count"], 31_171)
        self.assertEqual(stats["split_separator_scalar_count"], 4)
        self.assertEqual(stats["duplicate_source_scalar_count"], 0)
        self.assertEqual(stats["lost_source_word_token_count"], 0)
        self.assertEqual(stats["duplicated_source_word_token_count"], 0)

    def test_manual_and_source_diff_expose_strong_binding_gate(self) -> None:
        with (REPORT / "manual_review.jsonl").open(encoding="utf-8") as handle:
            reviews = [json.loads(line) for line in handle]
        self.assertEqual(len(reviews), 177)
        unresolved = [
            row
            for row in reviews
            if row["severity"] in {"critical", "high"}
            and not row["status"].startswith("resolved")
        ]
        self.assertEqual(
            [row["issue_id"] for row in unresolved],
            ["uk6-strong-binding-aggregate"],
        )
        self.assertEqual(
            len(
                [
                    row
                    for row in reviews
                    if row["type"] == "strong_surface_binding_audit_sample"
                ]
            ),
            4,
        )
        import csv

        with (REPORT / "source_diff.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows)
        unresolved_diffs = [
            row
            for row in rows
            if row["severity"] in {"critical", "high"}
            and not row["status"].startswith("resolved")
        ]
        self.assertEqual(len(unresolved_diffs), 1)
        self.assertEqual(
            unresolved_diffs[0]["type"], "strong_surface_binding_ambiguity"
        )


if __name__ == "__main__":
    unittest.main()

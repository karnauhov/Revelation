from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.bible_module.ukrainian_stage_6_model import (
    CONTRACT_VERSION,
    SynthesisPart,
    join_synthesis_parts,
    rebase_anchor,
    serialize_comment_uses,
    validate_partition,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_6"
    / "synthesis_cases.json"
)
REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_6_20260801"


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
        validate_partition(
            13, [tuple(pair) for pair in self.cases["split_intervals"]]
        )

    def test_split_boundary_ambiguity_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_partition(13, [(0, 6), (7, 13)])
        with self.assertRaises(ValueError):
            validate_partition(13, [(0, 8), (7, 13)])

    def test_source_only_range_is_not_joined_to_target(self) -> None:
        source_only = self.cases["range_source_only"]
        target, _ = join_synthesis_parts([("target", 0, 5, "Вірш")])
        self.assertNotIn(source_only, target)


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
    def test_reports_use_text_synthesis_contract(self) -> None:
        for name in [
            "synthesized_text.manifest.json",
            "source_only_material.manifest.json",
            "footnote_comment_projection.manifest.json",
        ]:
            value = json.loads((REPORT / name).read_text(encoding="utf-8"))
            self.assertEqual(value["contract_version"], CONTRACT_VERSION)
            self.assertEqual(value["counts"]["error"], 0)
            self.assertEqual(value["status"], "complete")

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
        self.assertEqual(
            stats["operation_target_counts"],
            {"1:1": 31_026, "merge": 68, "split": 8},
        )
        self.assertEqual(stats["source_only_count"], 1)
        self.assertEqual(stats["source_span_count"], 31_171)
        self.assertEqual(stats["split_separator_scalar_count"], 4)
        self.assertEqual(stats["duplicate_source_scalar_count"], 0)
        self.assertEqual(stats["lost_source_word_token_count"], 0)
        self.assertEqual(stats["duplicated_source_word_token_count"], 0)
        self.assertEqual(
            stats["source_word_token_count"],
            stats["synthesized_word_token_count"]
            + stats["source_only_word_token_count"],
        )

    def test_footnote_projection_and_heading_non_verse_cases(self) -> None:
        value = json.loads(
            (REPORT / "footnote_comment_stats.json").read_text(encoding="utf-8")
        )
        stats = value["statistics"]
        self.assertEqual(stats["footnote_definition_count"], 1_204)
        self.assertEqual(stats["projected_use_count"], 1_318)
        self.assertEqual(stats["heading_non_verse_use_count"], 11)
        self.assertEqual(stats["total_use_count"], 1_329)
        self.assertEqual(stats["unresolved_anchor_count"], 0)
        self.assertEqual(stats["comment_target_count"], 31_102)

    def test_manual_review_is_resolved(self) -> None:
        with (REPORT / "manual_review.jsonl").open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        self.assertEqual(len(rows), 164)
        self.assertFalse(
            [
                row
                for row in rows
                if row["severity"] in {"critical", "high"}
                and not row["status"].startswith("resolved")
            ]
        )

    def test_stage_status_is_complete_without_strong_artifacts(self) -> None:
        report = (REPORT / "report.ru.md").read_text(encoding="utf-8")
        self.assertIn("статус: **complete**", report)
        self.assertIn("Strong-разметка намеренно не входит", report)
        self.assertFalse((REPORT / "strong_alignment.manifest.json").exists())
        self.assertFalse((REPORT / "strong_coverage_report.json").exists())


if __name__ == "__main__":
    unittest.main()

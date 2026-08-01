from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest

from scripts.bible_module.ukrainian_stage_5_model import (
    MAPPING_CONTRACT_VERSION,
    ScalarSpan,
    assert_forward_reverse_consistency,
    assert_no_forbidden_stage_6_fields,
    assert_unique_target_keys,
    project_footnote_use,
    sha256_lines,
    sort_projected_uses,
    stable_json,
    stable_rule_id,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_5"
    / "mapping_cases.json"
)
REPORT = (
    ROOT
    / "scripts"
    / "bible_module"
    / "reports"
    / "ukrainian_stage_5_20260801"
)


def _use(
    use_id: str,
    *,
    anchor_start: int | None,
    anchor_end: int | None = None,
    footnote_id: str = "footnote:1",
    marker: str | None = "1",
    source_order: int = 1,
) -> dict[str, object]:
    row: dict[str, object] = {
        "footnote_id": footnote_id,
        "full_text_nfc": "Synthetic footnote.",
        "printed_marker": marker,
        "provenance": {"fixture": "CC0-1.0"},
        "source_order": source_order,
        "use_id": use_id,
    }
    if anchor_start is not None:
        row["anchor_start_scalar"] = anchor_start
        row["anchor_end_scalar"] = (
            anchor_start if anchor_end is None else anchor_end
        )
    return row


def _interval(start: int, end: int, target: str) -> dict[str, object]:
    return {
        "source_span": {"start_scalar": start, "end_scalar": end},
        "target_ref": target,
    }


class FixtureContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in cls.fixture["cases"]}

    def test_fixture_is_cc0_and_covers_required_structures(self) -> None:
        self.assertEqual(self.fixture["license"], "CC0-1.0")
        self.assertTrue(
            {
                "one_to_one",
                "source_only",
                "target_only",
                "merge",
                "split",
                "range_transfer",
                "verse_zero_superscription",
                "subverse",
                "chapter_boundary",
                "book_boundary",
                "neighbor_better",
            }.issubset(self.cases)
        )

    def test_operation_cardinalities(self) -> None:
        expected = {
            "one_to_one": "1:1",
            "source_only": "range_transfer",
            "target_only": "range_transfer",
            "merge": "merge",
            "split": "split",
            "range_transfer": "range_transfer",
        }
        for case_id, operation in expected.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(self.cases[case_id]["operation"], operation)

    def test_neighbor_better_requires_manual_review(self) -> None:
        case = self.cases["neighbor_better"]
        self.assertNotEqual(case["source"][0], case["target"][0])
        self.assertTrue(case["manual_review"])


class MappingModelTest(unittest.TestCase):
    def test_scalar_span_rejects_split_boundary(self) -> None:
        self.assertTrue(ScalarSpan(0, 5).contains_anchor(1, 2))
        self.assertFalse(ScalarSpan(0, 5).contains_anchor(5, 5))

    def test_rule_id_and_serialization_are_stable(self) -> None:
        parts = [
            {
                "record_id": "record:1",
                "segment_id": "segment:1",
                "span": {"start_scalar": 0, "end_scalar": 3},
            }
        ]
        first = stable_rule_id(
            operation="1:1", source_parts=parts, target_refs=["Fix.1.1"]
        )
        second = stable_rule_id(
            operation="1:1", source_parts=parts, target_refs=["Fix.1.1"]
        )
        self.assertEqual(first, second)
        self.assertEqual(stable_json({"b": 2, "a": 1}), '{"a":1,"b":2}')

    def test_repeated_generation_has_same_sha256(self) -> None:
        rows = [{"rule_id": "a", "value": 1}, {"rule_id": "b", "value": 2}]
        self.assertEqual(sha256_lines(rows), sha256_lines([dict(row) for row in rows]))

    def test_forward_reverse_consistency_and_unique_keys(self) -> None:
        source_part = {"segment_id": "segment:1"}
        forward = [
            {
                "rule_id": "rule:1",
                "source_parts": [source_part],
                "targets": [{"verse_key": "001"}],
            }
        ]
        reverse = [
            {
                "rule_id": "rule:1",
                "source_parts": [source_part],
                "verse_key": "001",
            }
        ]
        assert_forward_reverse_consistency(forward, reverse)
        assert_unique_target_keys(reverse)

    def test_duplicate_target_key_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            assert_unique_target_keys([{"verse_key": "001"}, {"verse_key": "001"}])

    def test_stage_6_fields_are_rejected(self) -> None:
        assert_no_forbidden_stage_6_fields({"mapping": "only"})
        for field in ["target_comment", "strong_alignment", "strong_number"]:
            with self.subTest(field=field), self.assertRaises(AssertionError):
                assert_no_forbidden_stage_6_fields({field: "forbidden"})


class FootnoteProjectionTest(unittest.TestCase):
    def test_one_to_one_preserves_identity_marker_and_pending_anchor(self) -> None:
        row = project_footnote_use(
            use=_use("use:1", anchor_start=2, marker="7"),
            rule_id="rule:1",
            operation="1:1",
            intervals=[_interval(0, 10, "Fix.1.1")],
            target_order={"Fix.1.1": 1},
        )
        self.assertEqual(row["status"], "projected")
        self.assertEqual(row["target_ref"], "Fix.1.1")
        self.assertEqual(row["marker"], "7")
        self.assertEqual(row["anchor_status"], "target_anchor_pending")
        self.assertIsNone(row["target_anchor"])

    def test_merge_keeps_distinct_uses_in_source_order(self) -> None:
        intervals = [_interval(0, 10, "Fix.1.1")]
        rows = [
            project_footnote_use(
                use=_use("use:2", anchor_start=3, source_order=2),
                rule_id="rule:merge",
                operation="merge",
                intervals=intervals,
                target_order={"Fix.1.1": 1},
            ),
            project_footnote_use(
                use=_use("use:1", anchor_start=2, source_order=1),
                rule_id="rule:merge",
                operation="merge",
                intervals=intervals,
                target_order={"Fix.1.1": 1},
            ),
        ]
        ordered = sort_projected_uses(rows)
        self.assertEqual([row["use_id"] for row in ordered], ["use:1", "use:2"])
        self.assertEqual(len({row["use_id"] for row in ordered}), 2)

    def test_anchor_aware_split_projects_exactly_one_target(self) -> None:
        row = project_footnote_use(
            use=_use("use:split", anchor_start=2),
            rule_id="rule:split",
            operation="split",
            intervals=[
                _interval(0, 5, "Fix.1.1"),
                _interval(5, 10, "Fix.1.2"),
            ],
            target_order={"Fix.1.1": 1, "Fix.1.2": 2},
        )
        self.assertEqual(row["status"], "projected")
        self.assertEqual(row["target_ref"], "Fix.1.1")

    def test_split_boundary_is_not_bound_to_nearest_verse(self) -> None:
        row = project_footnote_use(
            use=_use("use:boundary", anchor_start=5),
            rule_id="rule:split",
            operation="split",
            intervals=[
                _interval(0, 5, "Fix.1.1"),
                _interval(5, 10, "Fix.1.2"),
            ],
            target_order={"Fix.1.1": 1, "Fix.1.2": 2},
        )
        self.assertEqual(row["status"], "explicit_anomaly")
        self.assertIsNone(row["target_ref"])
        self.assertEqual(row["target_candidates"], ["Fix.1.1", "Fix.1.2"])

    def test_range_transfer_unique_and_ambiguous_anchors(self) -> None:
        intervals = [
            _interval(0, 5, "Fix.1.1"),
            _interval(5, 10, "Fix.1.2"),
        ]
        unique = project_footnote_use(
            use=_use("use:unique", anchor_start=7),
            rule_id="rule:range",
            operation="range_transfer",
            intervals=intervals,
            target_order={"Fix.1.1": 1, "Fix.1.2": 2},
        )
        ambiguous = project_footnote_use(
            use=_use("use:ambiguous", anchor_start=4, anchor_end=6),
            rule_id="rule:range",
            operation="range_transfer",
            intervals=intervals,
            target_order={"Fix.1.1": 1, "Fix.1.2": 2},
        )
        self.assertEqual(unique["target_ref"], "Fix.1.2")
        self.assertEqual(ambiguous["status"], "explicit_anomaly")
        self.assertEqual(
            ambiguous["target_candidates"], ["Fix.1.1", "Fix.1.2"]
        )

    def test_markerless_fixture_is_preserved_not_invented(self) -> None:
        row = project_footnote_use(
            use=_use("use:markerless", anchor_start=2, marker=None),
            rule_id="rule:1",
            operation="1:1",
            intervals=[_interval(0, 10, "Fix.1.1")],
            target_order={"Fix.1.1": 1},
        )
        self.assertIsNone(row["marker"])

    def test_named_definition_reuse_does_not_merge_use_ids(self) -> None:
        rows = [
            project_footnote_use(
                use=_use(
                    f"use:{index}",
                    anchor_start=index,
                    footnote_id="named:shared",
                    source_order=index,
                ),
                rule_id="rule:1",
                operation="1:1",
                intervals=[_interval(0, 10, "Fix.1.1")],
                target_order={"Fix.1.1": 1},
            )
            for index in [1, 2]
        ]
        self.assertEqual({row["footnote_id"] for row in rows}, {"named:shared"})
        self.assertEqual(len({row["use_id"] for row in rows}), 2)

    def test_heading_footnote_has_no_automatic_target(self) -> None:
        heading = {
            "status": "explicit_anomaly",
            "reason": "non_verse_source_material_missing_source_verse_binding",
            "target_candidates": [],
        }
        self.assertEqual(heading["status"], "explicit_anomaly")
        self.assertEqual(heading["target_candidates"], [])


class ProductionReportInvariantTest(unittest.TestCase):
    def test_exact_target_and_source_coverage(self) -> None:
        coverage = json.loads(
            (REPORT / "coverage_report.json").read_text(encoding="utf-8")
        )
        self.assertTrue(coverage["target_key_exact_baseline_equality"])
        self.assertEqual(coverage["target_position_count"], 31_102)
        self.assertEqual(coverage["source_record_mapped_count"], 31_160)
        self.assertEqual(coverage["duplicate_target_key_count"], 0)
        self.assertEqual(coverage["unexplained_empty_target_count"], 0)
        self.assertTrue(coverage["forward_reverse_consistent"])

    def test_all_footnotes_and_markers_are_accounted_once(self) -> None:
        stats = json.loads(
            (REPORT / "footnote_projection_stats.json").read_text(encoding="utf-8")
        )
        self.assertEqual(stats["use_count"], 1_329)
        self.assertEqual(stats["marker_count"], 1_329)
        self.assertEqual(stats["unique_use_id_count"], 1_329)
        self.assertEqual(stats["heading_non_verse_count"], 11)
        self.assertFalse(stats["target_comment_created"])

    def test_preservation_and_no_nearest_binding(self) -> None:
        report = json.loads(
            (REPORT / "preservation_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["unaccounted_token_count"], 0)
        self.assertFalse(report["canonical_source_scalar_material_duplicated"])
        self.assertFalse(report["nearest_verse_binding_used"])

    def test_mapping_manifests_are_versioned_and_deterministic(self) -> None:
        for name in ["source_to_target_map", "target_to_source_map"]:
            with self.subTest(name=name):
                manifest = json.loads(
                    (REPORT / f"{name}.manifest.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    manifest["mapping_contract_version"], MAPPING_CONTRACT_VERSION
                )
                self.assertEqual(manifest["error_count"], 0)
                self.assertEqual(manifest["skipped_count"], 0)
                self.assertRegex(manifest["output_sha256"], r"^[0-9a-f]{64}$")

    def test_every_nonstandard_rule_has_review_and_evidence(self) -> None:
        with (REPORT / "mapping_rules.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            mapping_rows = list(csv.DictReader(handle))
        with (REPORT / "source_diff.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            nonstandard_rows = list(csv.DictReader(handle))
        reviewed_rule_ids = {
            row["rule_id"]
            for line in (REPORT / "manual_review.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if (row := json.loads(line))["kind"] == "mapping_rule"
        }
        self.assertEqual(len(mapping_rows), 31_099)
        self.assertEqual(len(nonstandard_rows), 3_369)
        self.assertEqual(
            sum(row["operation"] != "1:1" for row in mapping_rows), 73
        )
        for row in nonstandard_rows:
            with self.subTest(rule_id=row["rule_id"]):
                self.assertIn(row["rule_id"], reviewed_rule_ids)
        for row in mapping_rows:
            if row["manual_review_status"] == "reviewed":
                self.assertRegex(row["evidence_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()

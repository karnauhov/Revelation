"""CC0 synthetic regression checks for the deferral-aware trust boundary."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.bible_module import ukrainian_stage_7_gold_v2 as gold


def example_grid():
    grid = {}
    for number in (1, 2):
        ref = "Gen.1." + str(number)
        original, target = "o" + str(number), "t" + str(number)
        common = {"target_ref": ref, "severity": "normal", "phenomena": ["reorder"],
                  "reviewer_id": "blind1", "evidence": [{"evidence_id": "cc0"}], "rationale": "CC0 fixture"}
        grid["original:" + original] = {**common, "record_type": "original_decision", "decision_id": original,
            "original_token_id": "raw:" + original, "group_original_token_ids": ["raw:" + original],
            "target_token_ids": ["raw:" + target], "relation": "one_to_one", "null_reason": None}
        grid["target:" + target] = {**common, "record_type": "target_accounting", "accounting_id": target,
            "target_token_id": "raw:" + target, "linked_original_token_ids": ["raw:" + original],
            "target_status": "aligned", "target_span": {"start_scalar": 0, "end_scalar": 1,
                "start_byte": 0, "end_byte": 1, "surface_sha256": "a" * 64}}
    return grid


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.grid = example_grid()
        self.excluded = {"original:o2": "issue2", "target:t2": "issue2"}

    def test_mask_exact_once_and_original_only_threshold_denominator(self):
        mask = gold.build_eligibility(self.grid, self.excluded)
        counts = gold.coverage(mask, self.grid)
        self.assertEqual((counts["full_labels"], counts["eligible_labels"], counts["deferred_labels"]), (4, 2, 2))
        self.assertEqual((counts["full_original_decisions"], counts["eligible_original_decisions"]), (2, 1))
        self.assertEqual((counts["full_verses"], counts["proven_verses"]), (2, 1))
        self.assertEqual(len({r["stable_key"] for r in mask}), 4)

    def test_coverage_dimensions_show_full_proven_and_excluded_verses(self):
        mask = gold.build_eligibility(self.grid, self.excluded)
        counts = gold.coverage(mask, self.grid)
        for dimension, label in (("book", "Gen"), ("testament", "OT"), ("stratum", "reorder")):
            actual = counts["by"][dimension][label]
            self.assertEqual(actual["full_verses"], 2)
            self.assertEqual(actual["proven_verses"], 1)
            self.assertEqual(actual["deferred_only_verses"], 1)

    def test_target_or_deferred_only_verse_cannot_satisfy_proven_verse_minimum(self):
        mask = gold.build_eligibility(self.grid, self.excluded)
        targets = [r for r in mask if r["stable_key"].startswith("target:")]
        self.assertEqual(gold.coverage(targets, self.grid)["proven_verses"], 0)
        deferred = [r for r in mask if not r["eligible"]]
        self.assertEqual(gold.coverage(deferred, self.grid)["proven_verses"], 0)

    def test_reciprocal_component_cannot_be_partially_excluded(self):
        with self.assertRaisesRegex(ValueError, "closure"):
            gold.build_eligibility(self.grid, {"original:o2": "issue2"})

    def test_transitive_shared_target_and_many_to_many_exclusion_closure(self):
        grid = copy.deepcopy(self.grid)
        for row in grid.values():
            row["target_ref"] = "Gen.1.1"
        grid["original:o2"]["target_token_ids"] = ["raw:t1", "raw:t2"]
        grid["original:o2"]["relation"] = "one_to_many"
        grid["target:t1"]["linked_original_token_ids"] = ["raw:o1", "raw:o2"]
        partial = {"original:o1": "issue", "target:t1": "issue"}
        with self.assertRaisesRegex(ValueError, "closure"):
            gold.build_eligibility(grid, partial)
        complete = {key: "issue" for key in grid}
        self.assertTrue(all(not r["eligible"] for r in gold.build_eligibility(grid, complete)))
        for key in ("original:o1", "original:o2"):
            grid[key].update(relation="many_to_many", group_original_token_ids=["raw:o1", "raw:o2"],
                             target_token_ids=["raw:t1", "raw:t2"])
        grid["target:t2"]["linked_original_token_ids"] = ["raw:o1", "raw:o2"]
        with self.assertRaisesRegex(ValueError, "closure"):
            gold.build_eligibility(grid, partial)
        self.assertEqual(len(gold.build_eligibility(grid, complete)), 4)

    def test_unknown_and_cross_verse_declared_edges_fail_before_masking(self):
        for ref, target in (("Gen.1.1", "unknown"), ("Gen.1.2", "raw:t1")):
            invalid = copy.deepcopy(self.grid)
            invalid["original:o1"].update(target_ref=ref, target_token_ids=[target])
            with self.subTest(ref=ref, target=target), self.assertRaises(ValueError):
                gold.build_eligibility(invalid, {})

    def test_unknown_stable_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            gold.build_eligibility(self.grid, {"original:missing": "issue2"})

    def test_duplicate_physical_node_rejected(self):
        grid = copy.deepcopy(self.grid)
        grid["original:o3"] = {**grid["original:o1"], "decision_id": "o3"}
        with self.assertRaisesRegex(ValueError, "Duplicate physical"):
            gold.build_eligibility(grid, {})

    def test_deferred_nodes_present_without_false_nulls_or_edges(self):
        first = copy.deepcopy(self.grid)
        second = {k: dict(v, reviewer_id="blind2") for k, v in self.grid.items()}
        before = copy.deepcopy(self.grid)
        values = gold.make_annotations(self.grid, first, second, self.excluded,
                                       adjudicator="third", adjudicated_keys=set())
        self.assertEqual(self.grid, before)
        deferred = [r for r in values if r.get("status") == "deferred_strong_unassigned"]
        self.assertEqual(len(deferred), 2)
        for row in deferred:
            self.assertIsNone(row["strong_assignment"])
            self.assertFalse({"relation", "null_reason", "target_status", "target_token_ids"} & row.keys())
            self.assertFalse(row["include_in_training"])
            self.assertFalse(row["include_in_scoring"])
        edges = [r for r in values if r["record_type"] == "hyperedge"]
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["target_ref"], "Gen.1.1")

    def test_serialization_is_deterministic_under_grid_insertion_order(self):
        left = gold.build_eligibility(self.grid, self.excluded)
        right = gold.build_eligibility(dict(reversed(list(self.grid.items()))), self.excluded)
        self.assertEqual(gold._jsonl_bytes(left), gold._jsonl_bytes(right))

    def test_frozen_panel_fold_and_original_roster_cannot_drift(self):
        from hashlib import sha256
        panel = [{"target_ref": "Gen.1." + str(n), "fold_id": int(sha256(("Gen.1." + str(n)).encode()).hexdigest()[:8], 16) % 5,
                  "original_token_ids": ["raw:o" + str(n)], "strata": {"genre": "prose", "mapping_operation": "1:1"}}
                 for n in (1, 2)]
        mask = gold.build_eligibility(self.grid, self.excluded)
        counts = gold.coverage(mask, self.grid, panel)
        self.assertEqual(counts["by"]["selection_stratum"]["genre:prose"]["proven_verses"], 1)
        for invalid in (panel[:1], [dict(panel[0], fold_id=(panel[0]["fold_id"] + 1) % 5), panel[1]],
                        [dict(panel[0], original_token_ids=[]), panel[1]]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                gold.coverage(mask, self.grid, invalid)

    def test_corrected_agreement_retains_actual_correction_provenance(self):
        provenance = {"original:o1": {"correction_reviewer_id": "corrector", "correction_sha256": "c" * 64,
                                      "final_qc_sha256": "d" * 64, "originally_agreed": True}}
        second = {k: dict(v, reviewer_id="blind2") for k, v in self.grid.items()}
        values = gold.make_annotations(self.grid, self.grid, second, self.excluded,
            adjudicator="third", adjudicated_keys=set(), correction_provenance=provenance)
        original = next(r for r in values if r.get("decision_id") == "o1")
        self.assertEqual(original["correction_provenance"], provenance["original:o1"])
        self.assertTrue(original["review"]["correction_applied"])
        self.assertTrue(original["review"]["agreement"])
        self.assertEqual(original["rationale"]["correction"], "CC0 fixture")


class PhysicalLockTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.file = self.root / "proof.json"
        self.file.write_bytes(b"sealed\n")
        self.spec = gold.file_spec(self.file, self.root)

    def test_exact_lock_and_changed_missing_dependency(self):
        gold.PhysicalLocks(self.root).check(self.spec)
        self.file.write_bytes(b"tamper\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            gold.PhysicalLocks(self.root).check(self.spec)
        self.file.unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            gold.PhysicalLocks(self.root).check(self.spec)

    def test_path_escape_and_bool_bytes_are_rejected(self):
        for invalid in ({**self.spec, "path": "../proof.json"}, {**self.spec, "bytes": True},
                        {**self.spec, "sha256": "bad"}, {**self.spec, "bytes": -1}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                gold.PhysicalLocks(self.root).check(invalid)

    def test_absent_finalized_lock_is_not_finalized(self):
        self.assertIsNone(gold.validated_finalized_gold_lock_v2(self.root, root=self.root))

    def test_live_dependency_validation_cannot_be_disabled(self):
        with self.assertRaisesRegex(ValueError, "cannot be disabled"):
            gold.validated_finalized_gold_lock_v2(self.root, root=self.root, revalidate_inputs=False)

    def test_immutable_writer_rejects_replacement(self):
        with self.assertRaisesRegex(ValueError, "Refusing"):
            gold.emit_immutable(self.file, b"different")
        gold.emit_immutable(self.file, self.file.read_bytes())

    def test_new_cli_keeps_strict_check_final_dispatch_separate(self):
        strict = gold.strict
        with patch.object(strict, "validated_finalized_gold_lock", return_value={"strict": True}) as old:
            with patch.object(gold, "validated_finalized_gold_lock_v2", side_effect=AssertionError("new branch called")):
                self.assertEqual(strict.main(["check-final", "--report-dir", str(self.root)]), 0)
        old.assert_called_once_with(self.root)
        with patch.object(gold, "validated_finalized_gold_lock_v2", return_value={"completed": True}) as new:
            with patch.object(strict, "validated_finalized_gold_lock", side_effect=AssertionError("strict branch called")):
                self.assertEqual(strict.main(["check-final-completed", "--report-dir", str(self.root)]), 0)
        new.assert_called_once_with(self.root)


class FrozenCorpusContractTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.packet = self.root / "packet.manifest.json"
        source = {name: "a" * 64 for name in gold.strict.PRODUCTION_PACKET_INPUT_KEYS}
        source.update(stage6_text=gold.strict.EXPECTED_STAGE6_TEXT_SHA256,
                      stage6_comments=gold.strict.EXPECTED_STAGE6_COMMENT_SHA256)
        self.manifest = {"artifact": "gold_reviewer_packets", "status": "prepared_unanswered_blind_packets",
            "corpus_contract": "ohienko_1988_production", "schema_version": gold.SCHEMA_VERSION,
            "contract_version": gold.CONTRACT_VERSION, "gold_workflow_version": gold.strict.GOLD_WORKFLOW_VERSION,
            "input_sha256": source, "output_sha256": {"review_pass_1.packet.jsonl": "b" * 64}}
        self.registry = {"corpus_contract": "ohienko_1988_production", "inputs": {
            **{name: {"sha256": digest} for name, digest in source.items()},
            "frozen_packet": {"sha256": "b" * 64}, "reviewer_packets_manifest": {"path": "packet.manifest.json"}}}
        self.checks = unittest.mock.Mock()
        self.checks.check.return_value = self.packet

    def check(self):
        self.packet.write_bytes(gold.canonical_bytes(self.manifest))
        return gold._validate_packet_contract(self.registry, self.checks)

    def test_production_packet_and_each_source_alias_are_bound(self):
        self.assertEqual(self.check()["corpus_contract"], "ohienko_1988_production")

    def test_relabeling_production_as_fixture_cannot_weaken_minima(self):
        self.registry["corpus_contract"] = "CC0_fixture"
        with self.assertRaisesRegex(ValueError, "corpus contract"):
            self.check()

    def test_rehashed_source_alias_substitution_is_rejected(self):
        self.registry["inputs"]["gold_selected_original_layer"]["sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "source input alias"):
            self.check()

    def test_packet_payload_must_match_its_original_manifest(self):
        self.registry["inputs"]["frozen_packet"]["sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "payload differs"):
            self.check()

    def test_documented_fixture_alias_requires_actual_fixture_packet(self):
        self.registry["corpus_contract"] = "CC0_fixture"
        self.manifest["corpus_contract"] = "cc0_fixture"
        self.assertEqual(self.check()["corpus_contract"], "cc0_fixture")


class SourceFrequencyProofTests(unittest.TestCase):
    def setUp(self):
        self.grid = example_grid()
        self.mask = gold.build_eligibility(self.grid, {"original:o2": "issue2", "target:t2": "issue2"})
        self.annotations = gold.make_annotations(self.grid, self.grid, self.grid,
            {"original:o2": "issue2", "target:t2": "issue2"}, adjudicator=None, adjudicated_keys=set())
        self.universe = [{"original_token_id": "primary:" + str(i), "reading_status": "primary_mt",
                          "strong_classic": ["H1"]} for i in range(1000)]
        self.universe += [{"original_token_id": "rare:1", "reading_status": "primary_mt", "strong_classic": ["H2"]},
                          {"original_token_id": "alternative", "reading_status": "alternative", "strong_classic": ["H1"]},
                          {"original_token_id": "unresolved", "reading_status": "primary_unresolved", "strong_classic": ["H1"]}]
        self.selected = [{"original_token_id": "raw:o1", "target_ref": "Gen.1.1", "strong_classic": ["H1"]},
                         {"original_token_id": "raw:o2", "target_ref": "Gen.1.2", "strong_classic": ["H2"]}]

    def test_exact_source_counts_and_eligible_original_evidence(self):
        before = copy.deepcopy(self.grid)
        proof = gold.add_source_frequency_proof(self.mask, self.annotations, self.universe, self.selected)
        frequent = proof["by_band"]["frequent_1000_plus"]
        self.assertEqual(frequent["eligible_original_decisions"], 1)
        self.assertEqual(frequent["proven_verses"], 1)
        original = next(r for r in self.annotations if r["record_type"] == "original_decision")
        self.assertEqual(original["derived_source_strata"]["frequency_classes"], ["frequent_lemma"])
        self.assertEqual(original["derived_source_strata"]["frequency_evidence"][0]["primary_universe_frequency"], 1000)
        self.assertEqual(original["phenomena"], ["reorder"])
        self.assertEqual(self.grid, before)

    def test_deferred_rare_original_never_proves_an_eligible_rare_stratum(self):
        proof = gold.add_source_frequency_proof(self.mask, self.annotations, self.universe, self.selected)
        rare = proof["by_band"]["rare_1_to_5"]
        self.assertEqual(rare.get("eligible_original_decisions", 0), 0)
        self.assertEqual(rare["proven_verses"], 0)
        self.assertEqual(rare["deferred_only_verses"], 1)
        for row in self.annotations:
            if row["record_type"].startswith("deferred_"):
                self.assertNotIn("derived_source_strata", row)
                self.assertIsNone(row["strong_assignment"])

    def test_missing_selected_node_and_duplicate_universe_id_are_rejected(self):
        for universe, selected in ((self.universe, self.selected[:1]),
                                    (self.universe + [self.universe[0]], self.selected)):
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                gold.add_source_frequency_proof(self.mask, self.annotations, universe, selected)


if __name__ == "__main__":
    unittest.main()

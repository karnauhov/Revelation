"""Fail-closed completion boundaries without weakening the strict QC branch."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.ukrainian_stage_7_completion import (
    build_projection, canonical_bytes, emit_immutable, locked_file, sha256_file,
)


class CompletionContractTests(unittest.TestCase):
    def setUp(self):
        # One unresolved reciprocal grouped edge and one proven isolated edge.
        self.grid = {
            "original:o1": {"target_ref": "Mat.1.1", "original_token_id": "o1", "group_original_token_ids": ["o1", "o2"], "target_token_ids": ["t1"], "null_reason": None, "relation": "many_to_one"},
            "original:o2": {"target_ref": "Mat.1.1", "original_token_id": "o2", "group_original_token_ids": ["o1", "o2"], "target_token_ids": ["t1"], "null_reason": None, "relation": "many_to_one"},
            "target:t1": {"target_ref": "Mat.1.1", "target_token_id": "t1", "linked_original_token_ids": ["o1", "o2"], "target_status": "aligned"},
            "original:o3": {"target_ref": "Mat.1.1", "original_token_id": "o3", "group_original_token_ids": ["o3"], "target_token_ids": ["t2"], "null_reason": None, "relation": "one_to_one"},
            "target:t2": {"target_ref": "Mat.1.1", "target_token_id": "t2", "linked_original_token_ids": ["o3"], "target_status": "aligned"},
        }
        self.observations = [{"stable_key": k, "final_decision": copy.deepcopy(v), "reviewer_id": "qc", "verdict": "uncertain" if k == "original:o1" else "accepted", "rationale": "Occurrence inspected", "reciprocal_accounting_checked": True} for k, v in self.grid.items()]
        self.issues = [{"issue_id": "issue1", "target_ref": "Mat.1.1", "affected_stable_keys": ["original:o1", "original:o2", "target:t1"], "status": "deferred_strong_unassigned", "strong_assignment": None, "new_Strong_assigned": False, "leave_without_Strong": True, "missing_proof": "Ambiguous original lemma", "input_digests": {"source": "digest"}, "attempted_alternatives": ["apparatus inspected"], "evidence_files": ["source"], "module_code": "OH1988", "edition": "ohienko_1988", "follow_up": "optional", "qc_verdict": "uncertain"}]

    def project(self):
        return build_projection(self.grid, self.observations, self.issues, reviewer_id="qc", author_ids={"writer", "researcher"})

    def test_group_dependency_is_excluded_without_relabelling_verdict(self):
        frozen = copy.deepcopy(self.grid)
        rows, counts = self.project()
        by_key = {r["stable_key"]: r for r in rows}
        self.assertEqual(counts["deferred_decision_labels"], 3)
        self.assertEqual(counts["effective_proven_decision_labels"], 2)
        self.assertEqual(counts["excluded_reciprocal_edges"], 1)
        self.assertEqual(by_key["original:o2"]["content_verdict"], "accepted")
        for key in self.issues[0]["affected_stable_keys"]:
            row = by_key[key]
            self.assertFalse(row["include_in_training"])
            self.assertFalse(row["include_in_scoring"])
            self.assertFalse(row["include_in_strong_export"])
            self.assertIsNone(row["strong_assignment"])
            self.assertEqual(row["assigned_strongs"], [])
            self.assertFalse(row["null_omission_asserted_by_overlay"])
            self.assertNotIn("null_reason", row["effective_decision"])
            self.assertNotIn("relation", row["effective_decision"])
            self.assertNotIn("target_status", row["effective_decision"])
        self.assertEqual(by_key["original:o3"]["effective_decision"], frozen["original:o3"])
        self.assertEqual(self.grid, frozen)

    def test_negative_content_and_inventory_boundaries(self):
        mutations = {
            "missing_qc": lambda: self.observations.pop(),
            "duplicate_qc": lambda: self.observations.append(copy.deepcopy(self.observations[0])),
            "changed_frozen_semantics": lambda: self.observations[0]["final_decision"].update(null_reason="original_omitted"),
            "missing_accounting": lambda: self.observations[0].update(reciprocal_accounting_checked=False),
            "author_as_qc": lambda: self.observations[0].update(reviewer_id="writer"),
            "unregistered_uncertainty": lambda: self.observations[-1].update(verdict="uncertain"),
            "incomplete_group_exclusion": lambda: self.issues[0]["affected_stable_keys"].pop(),
            "overbroad_exclusion": lambda: self.issues[0]["affected_stable_keys"].append("original:o3"),
            "missing_research": lambda: self.issues[0].update(attempted_alternatives=[]),
            "missing_proof": lambda: self.issues[0].update(missing_proof=""),
            "invented_strong": lambda: self.issues[0].update(strong_assignment="G1"),
            "uncertain_relabelled_accepted": lambda: self.issues[0].update(qc_verdict="accepted"),
            "duplicate_issue": lambda: self.issues.append(copy.deepcopy(self.issues[0])),
            "cross_verse": lambda: self.grid["target:t1"].update(target_ref="Mat.1.2"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                self.setUp()
                mutate()
                with self.assertRaises(ValueError):
                    self.project()

    def test_definite_error_can_be_unassigned_without_hiding_verdict(self):
        self.observations[0]["verdict"] = "error"
        self.issues[0]["qc_verdict"] = "error"
        rows, counts = self.project()
        self.assertEqual(counts["content_errors"], 1)
        self.assertEqual(rows[0]["content_verdict"], "error")
        self.assertEqual(rows[0]["assignment_status"], "deferred_strong_unassigned")

    def test_proven_grid_requires_no_deferrals(self):
        for row in self.observations:
            row["verdict"] = "accepted"
        self.issues = []
        _, counts = self.project()
        self.assertEqual(counts["deferred_decision_labels"], 0)
        self.assertEqual(counts["effective_proven_decision_labels"], 5)

    def test_actual_reviewer_authorship_rejected(self):
        with self.assertRaisesRegex(ValueError, "authored"):
            build_projection(self.grid, self.observations, self.issues, reviewer_id="writer", author_ids={"writer"})

    def test_stale_byte_sha_and_outside_locks_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence.json"
            path.write_bytes(canonical_bytes({"verse": "Mat.1.1"}))
            spec = {"path": "evidence.json", "sha256": sha256_file(path), "bytes": path.stat().st_size}
            self.assertEqual(locked_file(spec, root), path.resolve())
            for replacement in ({"bytes": 0}, {"sha256": "0" * 64}, {"path": "../outside"}):
                with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                    locked_file(spec | replacement, root)
            with self.assertRaises(ValueError):
                locked_file({"path": "evidence.json", "sha256": ""}, root)

    def test_sealed_artifact_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sealed.json"
            emit_immutable(path, b"sealed\n")
            emit_immutable(path, b"sealed\n")
            with self.assertRaises(ValueError):
                emit_immutable(path, b"changed\n")


if __name__ == "__main__":
    unittest.main()

"""Regression tests for the scoped Stage-7 blind-review provenance repair."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.bible_module.ukrainian_stage_7_model import stable_json
from scripts.bible_module.ukrainian_stage_7_provenance import (
    _canonical_rows,
    _without_provenance,
    prove_expanded_semantics,
    repair_compact_rows,
)


class ProvenanceRepairTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "record_type": "compact_review_metadata",
                "review_pass": 2,
                "reviewer_id": "codex-blind-test-pass2-20260912-independent",
            },
            {
                "record_type": "compact_review_verse_submission",
                "target_ref": "Test.1.1",
                "groups": [
                    {
                        "original_indices": ["o001"],
                        "target_indices": ["t001"],
                        "relation": "one_to_one",
                        "rationale": "Independent blind Mat pass 2 at Test.1.1; local token match",
                        "evidence": [{"evidence_id": "uk7:mat:p2:ABC:g001", "kind": "manual_verse_local_original_target"}],
                    }
                ],
                "target_nulls": [
                    {
                        "target_index": "t002",
                        "target_status": "function_token",
                        "rationale": "Independent blind Mat pass 2 at Test.1.1; no source token",
                        "evidence": [{"evidence_id": "uk7:mat:p2:ABC:t002", "kind": "manual_verse_local_target_null"}],
                    }
                ],
            },
        ]
        self.scope = {"Test": ("001", "a" * 64, 1, 2)}

    def test_changes_only_provenance_and_keeps_original_immutable(self) -> None:
        original = copy.deepcopy(self.rows)
        with patch.dict("scripts.bible_module.ukrainian_stage_7_provenance.FROZEN_COMPACT", self.scope):
            repaired, count = repair_compact_rows(self.rows, "Test")
        self.assertEqual(count, 2)
        self.assertEqual(self.rows, original)
        self.assertEqual(_without_provenance(repaired), _without_provenance(original))
        self.assertEqual(repaired[1]["groups"][0]["evidence"][0]["evidence_id"], "uk7:test:p2:ABC:g001")
        self.assertEqual(repaired[1]["target_nulls"][0]["evidence"][0]["evidence_id"], "uk7:test:p2:ABC:t002")
        self.assertIn("blind Test pass 2 at Test.1.1", repaired[1]["groups"][0]["rationale"])

    def test_rejects_foreign_verse_and_unexpected_label(self) -> None:
        with patch.dict("scripts.bible_module.ukrainian_stage_7_provenance.FROZEN_COMPACT", self.scope):
            wrong_ref = copy.deepcopy(self.rows)
            wrong_ref[1]["target_ref"] = "Other.1.1"
            with self.assertRaisesRegex(ValueError, "foreign verse"):
                repair_compact_rows(wrong_ref, "Test")
            wrong_label = copy.deepcopy(self.rows)
            wrong_label[1]["groups"][0]["rationale"] = "guess"
            with self.assertRaisesRegex(ValueError, "exact known template defect"):
                repair_compact_rows(wrong_label, "Test")

    def test_rejects_duplicate_repaired_evidence_id(self) -> None:
        with patch.dict("scripts.bible_module.ukrainian_stage_7_provenance.FROZEN_COMPACT", self.scope):
            duplicate = copy.deepcopy(self.rows)
            duplicate[1]["target_nulls"][0]["evidence"][0]["evidence_id"] = "uk7:mat:p2:ABC:g001"
            with self.assertRaisesRegex(ValueError, "collide"):
                repair_compact_rows(duplicate, "Test")

    def test_requires_canonical_lf_jsonl(self) -> None:
        payload = ("\n".join(stable_json(row) for row in self.rows) + "\n").encode("utf-8")
        self.assertEqual(_canonical_rows(payload), self.rows)
        with self.assertRaisesRegex(ValueError, "LF-terminated"):
            _canonical_rows(payload.replace(b"\n", b"\r\n"))
        with self.assertRaisesRegex(ValueError, "not canonical"):
            _canonical_rows(b'{"z":1,"a":2}\n')

    def test_expanded_proof_rejects_a_changed_alignment(self) -> None:
        old = [
            {"record_type": "review_metadata", "review_pass": 2},
            {"record_type": "original_decision", "target_ref": "Test.1.1", "decision_id": "d1", "relation": "one_to_one", "target_token_ids": ["t1"], "rationale": "old", "evidence": [{"evidence_id": "uk7:mat:p2:x"}]},
        ]
        new = copy.deepcopy(old)
        new[1]["rationale"] = "repaired"
        new[1]["evidence"][0]["evidence_id"] = "uk7:test:p2:x"
        with tempfile.TemporaryDirectory() as folder, patch.dict(
            "scripts.bible_module.ukrainian_stage_7_provenance.FROZEN_COMPACT", self.scope
        ), patch.dict(
            "scripts.bible_module.ukrainian_stage_7_provenance.FROZEN_EXPANDED_DECISIONS", {"Test": 1}
        ):
            old_path = Path(folder) / "old.jsonl"
            new_path = Path(folder) / "new.jsonl"
            old_path.write_bytes(("\n".join(stable_json(row) for row in old) + "\n").encode("utf-8"))
            new_path.write_bytes(("\n".join(stable_json(row) for row in new) + "\n").encode("utf-8"))
            proof = prove_expanded_semantics(old_path, new_path, "Test")
            self.assertEqual(proof["semantic_decisions_changed"], 0)
            self.assertEqual(proof["stable_decisions"], 1)
            new[1]["target_token_ids"] = ["t2"]
            new_path.write_bytes(("\n".join(stable_json(row) for row in new) + "\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "semantic decisions changed"):
                prove_expanded_semantics(old_path, new_path, "Test")


if __name__ == "__main__":
    unittest.main()

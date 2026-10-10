"""Regression checks for applying sealed corrections in completion v2."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.bible_module import ukrainian_stage_7_completion_v2 as completion


class CorrectedCompletionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.chain = {name: self.root / name for name in
                      ("pass1", "pass2", "comparison", "adjudication")}
        self.base = {"original:o": {"record_type": "original_decision", "decision_id": "o",
                                  "original_token_id": "o", "target_ref": "Acts.13.29",
                                  "target_token_ids": ["t1", "t2"],
                                  "group_original_token_ids": ["o"]}}
        self.values = ({}, {}, {"o": {}}, {}, self.base, "adjudicator")

    def corrected_chain(self):
        for name in ("consensus_correction", "blocking_qc"):
            self.chain[name] = self.root / name
            self.chain[name + "_manifest"] = Path(str(self.chain[name]) + ".manifest.json")
        correction = dict(self.base["original:o"], target_token_ids=["t1"])
        self.chain["consensus_correction"].write_bytes(
            completion.canonical_bytes({"record_type": "consensus_correction_metadata"})
            + completion.canonical_bytes(correction))
        return correction

    def test_uncorrected_chain_preserves_the_full_base_grid(self):
        with patch.object(completion, "_validated_post_adjudication_values", return_value=self.values):
            actual = completion.validated_completion_grid(self.chain)
        self.assertEqual(actual[4], self.base)

    def test_validated_correction_replaces_only_the_scoped_decision(self):
        expected = self.corrected_chain()
        before = copy.deepcopy(self.base)
        with (patch.object(completion, "_validated_post_adjudication_values", return_value=self.values),
              patch.object(completion, "validate_consensus_correction_shard") as strict,
              patch.object(completion, "_validate_final_grid") as grid_check,
              patch.object(completion, "_validate_semantic_accounting") as accounting):
            result = completion.validated_completion_grid(self.chain)
        self.assertEqual(result[4]["original:o"], expected)
        self.assertEqual(self.base, before)
        strict.assert_called_once_with(
            **{name + "_path": self.chain[name] for name in ("pass1", "pass2", "comparison", "adjudication")},
            blocking_qc_path=self.chain["blocking_qc"], correction_path=self.chain["consensus_correction"])
        grid_check.assert_called_once_with(result[4], self.values[2])
        accounting.assert_called_once()

    def test_strict_correction_rejection_cannot_be_bypassed(self):
        self.corrected_chain()
        with (patch.object(completion, "_validated_post_adjudication_values", return_value=self.values),
              patch.object(completion, "validate_consensus_correction_shard", side_effect=ValueError("stale correction")),
              self.assertRaisesRegex(ValueError, "stale correction")):
            completion.validated_completion_grid(self.chain)

    def test_incomplete_correction_chain_is_rejected_before_work_reads(self):
        self.corrected_chain()
        for name in ("consensus_correction", "consensus_correction_manifest", "blocking_qc", "blocking_qc_manifest"):
            incomplete = dict(self.chain)
            incomplete.pop(name)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Incomplete"):
                completion.validated_completion_grid(incomplete)

    def test_redirected_correction_sidecar_is_rejected(self):
        self.corrected_chain()
        self.chain["consensus_correction_manifest"] = self.root / "different.manifest.json"
        with (patch.object(completion, "_validated_post_adjudication_values", return_value=self.values),
              self.assertRaisesRegex(ValueError, "sidecar")):
            completion.validated_completion_grid(self.chain)

    def test_v1_config_is_not_silently_upgraded(self):
        config = self.root / "config.json"
        config.write_bytes(completion.canonical_bytes({"completion_version": "ukrainian-stage-7-registered-deferral-completion-v1"}))
        with self.assertRaisesRegex(ValueError, "version"):
            completion.validate_config(config, self.root)

    def test_correction_header_and_decision_authors_are_both_guarded(self):
        rows = [{"record_type": "consensus_correction_metadata", "correction_reviewer_id": "corrector"},
                {"record_type": "original_decision", "reviewer_id": "corrector"}]
        self.assertEqual(completion.correction_authors(rows), {"corrector"})
        rows.append({"record_type": "target_accounting", "reviewer_id": "other"})
        self.assertEqual(completion.correction_authors(rows), {"corrector", "other"})
        with self.assertRaisesRegex(ValueError, "identity"):
            completion.correction_authors([{"record_type": "consensus_correction_metadata"}])

    def test_registry_snapshot_requires_exact_unique_roster_status_and_count(self):
        issue = {"issue_id": "oh1988:strongs-issue:v1:Acts.2.38:uncertain",
                 "status": "deferred_strong_unassigned", "affected_stable_keys": ["original:o", "target:t"]}
        marker = "<!-- strongs-issue-registry: OH1988 -->\n"
        row = "| `oh1988:strongs-issue:v1:Acts.2.38:uncertain` | Acts.2.38 | words | candidates | `deferred_strong_unassigned` | 2 | QC |\n"
        completion.validate_registry_snapshot(marker + row, [issue])
        for text in (row, marker, marker + row + row,
                     marker + row.replace(" | 2 |", " | 1 |"),
                     marker + row.replace("deferred_strong_unassigned", "accepted")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                completion.validate_registry_snapshot(text, [issue])


if __name__ == "__main__":
    unittest.main()

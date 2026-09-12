"""Fail-closed tests for blocked independent-QC provenance SHA rebasing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.ukrainian_stage_7_model import stable_json
from scripts.bible_module.ukrainian_stage_7_qc_rebase import (
    _require_blocked_qc_complete,
    _sha,
)


class BlockedQcRebaseTest(unittest.TestCase):
    def _case(self, folder: str) -> tuple[list[dict], dict, Path]:
        adjudication = Path(folder) / "adjudication.jsonl"
        adjudication.write_bytes(
            (stable_json({"record_type": "adjudication_shard_metadata"}) + "\n"
             + stable_json({"record_type": "original_decision", "decision_id": "d1"}) + "\n").encode("utf-8")
        )
        rows = [
            {"record_type": "qc_metadata", "overall_verdict": "uncertain", "shard_blocked": True},
            {"record_type": "qc_adjudication_result", "stable_key": "original:d1"},
        ]
        sidecar = {
            "shard_blocked": True,
            "overall_verdict": "uncertain",
            "error_count": 0,
            "input_sha256": {"adjudication": _sha(adjudication)},
            "counts": {
                "audited_result_rows": 1,
                "pass_agreed_decisions_checked": 1,
                "full_final_grid": 2,
                "full_grid_verdict": {"accepted": 1, "uncertain": 1, "error": 0},
            },
        }
        return rows, sidecar, adjudication

    def test_complete_blocked_qc_is_proof_ready_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            rows, sidecar, adjudication = self._case(folder)
            _require_blocked_qc_complete(rows, sidecar, adjudication, "Mark")

    def test_missing_or_duplicate_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            rows, sidecar, adjudication = self._case(folder)
            with self.assertRaisesRegex(ValueError, "no canonical header/results"):
                _require_blocked_qc_complete(rows[:1], sidecar, adjudication, "Mark")
            with self.assertRaisesRegex(ValueError, "scope differs"):
                _require_blocked_qc_complete([rows[0], rows[1], rows[1]], sidecar, adjudication, "Mark")

    def test_unblocked_or_incomplete_qc_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            rows, sidecar, adjudication = self._case(folder)
            rows[0]["shard_blocked"] = False
            with self.assertRaisesRegex(ValueError, "blocking verdict"):
                _require_blocked_qc_complete(rows, sidecar, adjudication, "Luke")
            rows[0]["shard_blocked"] = True
            sidecar["counts"]["pass_agreed_decisions_checked"] = 0
            with self.assertRaisesRegex(ValueError, "full-grid accounting"):
                _require_blocked_qc_complete(rows, sidecar, adjudication, "Luke")

    def test_stale_adjudication_sha_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            rows, sidecar, adjudication = self._case(folder)
            sidecar["input_sha256"]["adjudication"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "refers to another adjudication"):
                _require_blocked_qc_complete(rows, sidecar, adjudication, "Mark")


if __name__ == "__main__":
    unittest.main()

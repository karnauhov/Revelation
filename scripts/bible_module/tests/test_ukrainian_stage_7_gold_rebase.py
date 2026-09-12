"""Fail-closed regression tests for metadata-only adjudication SHA rebasing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.bible_module.ukrainian_stage_7_gold_rebase import (
    _canonical_object,
    _comparison_keys,
    _write_identical_or_new,
)
from scripts.bible_module.ukrainian_stage_7_model import stable_json


class AdjudicationRebaseTest(unittest.TestCase):
    def test_canonical_sidecar_required(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_bytes((stable_json({"a": 1, "b": 2}) + "\n").encode("utf-8"))
            self.assertEqual(_canonical_object(path), {"a": 1, "b": 2})
            path.write_bytes(b'{"b":2,"a":1}\n')
            with self.assertRaisesRegex(ValueError, "not canonical"):
                _canonical_object(path)

    def test_disagreement_ids_must_be_unique(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "comparison.jsonl"
            header = {"record_type": "comparison_metadata"}
            row = {"record_type": "alignment_disagreement", "stable_key": "original:d1"}
            path.write_bytes((stable_json(header) + "\n" + stable_json(row) + "\n").encode("utf-8"))
            self.assertEqual(_comparison_keys(path), {"original:d1"})
            path.write_bytes((stable_json(header) + "\n" + stable_json(row) + "\n" + stable_json(row) + "\n").encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "scope is invalid"):
                _comparison_keys(path)

    def test_existing_output_cannot_be_overwritten_with_different_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "rebase.jsonl"
            _write_identical_or_new(path, b"a\n")
            _write_identical_or_new(path, b"a\n")
            with self.assertRaisesRegex(ValueError, "refusing overwrite"):
                _write_identical_or_new(path, b"b\n")
            self.assertEqual(path.read_bytes(), b"a\n")


if __name__ == "__main__":
    unittest.main()

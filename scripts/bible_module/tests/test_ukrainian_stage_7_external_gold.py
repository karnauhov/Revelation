from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_external_gold import (
    EXTERNAL_FORMAT_CANONICALIZATION_VERSION,
    EXTERNAL_WRAPPER_NORMALIZATION_VERSION,
    compact_quality_metrics,
    normalize_external_compact_wrapper,
)
from scripts.bible_module.ukrainian_stage_7_gold_compact import (
    COMPACT_REVIEW_VERSION,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "external_wrapper_normalization_cases.json"
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class ExternalGoldWrapperNormalizationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _bundle(self, root: Path) -> tuple[Path, Path, Path, dict[str, object]]:
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "compact_review_version": COMPACT_REVIEW_VERSION,
            "record_type": "compact_review_metadata",
            "review_pass": 1,
            "reviewer_id": "cc0-external-reviewer-v1",
            "shard_id": "gold7:p1:shard:999:CC0-CC0",
        }
        template = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "compact_review_version": COMPACT_REVIEW_VERSION,
            "record_type": "compact_review_verse_template",
            "selection_id": "cc0:external:selection:1",
            "target_ref": "CC0.1.1",
            "template_row_sha256": "a" * 64,
            "book": "CC0",
            "plain_text_nfc": self.fixture["plain_text"],
            "original_index": [{"index": "o001", "display": {"surface_raw": "abc"}}],
            "target_index": [{"index": "t001", "surface": "Вигадане"}],
            "reviewer_answers": {"groups": [], "target_nulls": []},
        }
        external = deepcopy(template)
        external["record_type"] = "compact_review_verse_submission"
        external["reviewer_answers"] = {
            "groups": [self.fixture["group"]],
            "target_nulls": [self.fixture["target_null"]],
        }
        metadata_path = root / "metadata.jsonl"
        template_path = root / "template.jsonl"
        external_path = root / "external.jsonl"
        _write_jsonl(metadata_path, [metadata])
        _write_jsonl(template_path, [template])
        _write_jsonl(external_path, [metadata, external])
        return template_path, metadata_path, external_path, external

    def test_normalizes_exact_wrapper_without_changing_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, source_row = self._bundle(root)
            output = root / "normalized.jsonl"
            result = normalize_external_compact_wrapper(
                template_path=template,
                metadata_template_path=metadata,
                external_path=external,
                output_path=output,
            )
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(result["normalization_version"], EXTERNAL_WRAPPER_NORMALIZATION_VERSION)
            self.assertEqual(result["error_count"], 0)
            self.assertEqual(rows[1]["groups"], source_row["reviewer_answers"]["groups"])
            self.assertEqual(rows[1]["target_nulls"], source_row["reviewer_answers"]["target_nulls"])
            self.assertEqual(rows[1]["reviewer_id"], rows[0]["reviewer_id"])
            self.assertNotIn("plain_text_nfc", rows[1])
            self.assertEqual(
                result["output_sha256"][output.name], sha256(output.read_bytes()).hexdigest()
            )
            self.assertTrue(Path(str(output) + ".normalization.manifest.json").is_file())

    def test_rejects_changed_frozen_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, _ = self._bundle(root)
            rows = [json.loads(line) for line in external.read_text(encoding="utf-8").splitlines()]
            rows[1]["plain_text_nfc"] = "Змінено"
            _write_jsonl(external, rows)
            with self.assertRaisesRegex(ValueError, "changed frozen context"):
                normalize_external_compact_wrapper(
                    template_path=template,
                    metadata_template_path=metadata,
                    external_path=external,
                    output_path=root / "normalized.jsonl",
                )

    def test_canonicalizes_known_format_aliases_without_changing_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, _ = self._bundle(root)
            rows = [json.loads(line) for line in external.read_text(encoding="utf-8").splitlines()]
            group = rows[1]["reviewer_answers"]["groups"][0]
            group.pop("null_reason")
            group.pop("evidence")
            group["evidence_ids"] = ["o001", "t001"]
            group["relation"] = "linked"
            group["severity"] = "medium"
            target_null = rows[1]["reviewer_answers"]["target_nulls"][0]
            target_null.pop("target_status")
            target_null.pop("evidence")
            target_null["evidence_ids"] = ["t002"]
            target_null["severity"] = "low"
            _write_jsonl(external, rows)
            output = root / "canonical.jsonl"

            result = normalize_external_compact_wrapper(
                template_path=template,
                metadata_template_path=metadata,
                external_path=external,
                output_path=output,
                canonicalize_format=True,
            )
            canonical = [
                json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()
            ][1]
            canonical_group = canonical["groups"][0]
            canonical_null = canonical["target_nulls"][0]
            self.assertEqual(
                result["normalization_version"],
                EXTERNAL_FORMAT_CANONICALIZATION_VERSION,
            )
            self.assertEqual(canonical_group["original_indices"], ["o001"])
            self.assertEqual(canonical_group["target_indices"], ["t001"])
            self.assertEqual(canonical_group["relation"], "one_to_one")
            self.assertEqual(canonical_group["severity"], "high")
            self.assertEqual(canonical_group["null_reason"], None)
            self.assertEqual(
                [item["evidence_id"] for item in canonical_group["evidence"]],
                ["o001", "t001"],
            )
            self.assertEqual(canonical_null["target_status"], "translation_addition")
            self.assertEqual(canonical_null["severity"], "normal")
            self.assertNotIn("evidence_ids", canonical_group)
            self.assertGreater(result["format_repair_counts"]["evidence_ids_promoted"], 0)

    def test_rejects_nonexact_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, _ = self._bundle(root)
            rows = [json.loads(line) for line in external.read_text(encoding="utf-8").splitlines()]
            rows[0]["reviewer_id"] = "different-reviewer"
            _write_jsonl(external, rows)
            with self.assertRaisesRegex(ValueError, "metadata is not byte-exact"):
                normalize_external_compact_wrapper(
                    template_path=template,
                    metadata_template_path=metadata,
                    external_path=external,
                    output_path=root / "normalized.jsonl",
                )

    def test_rejects_malformed_answer_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, _ = self._bundle(root)
            rows = [json.loads(line) for line in external.read_text(encoding="utf-8").splitlines()]
            rows[1]["reviewer_answers"]["confidence"] = 1.0
            _write_jsonl(external, rows)
            with self.assertRaisesRegex(ValueError, "malformed answers"):
                normalize_external_compact_wrapper(
                    template_path=template,
                    metadata_template_path=metadata,
                    external_path=external,
                    output_path=root / "normalized.jsonl",
                )

    def test_refuses_to_overwrite_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template, metadata, external, _ = self._bundle(root)
            output = root / "normalized.jsonl"
            output.write_text("existing\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                normalize_external_compact_wrapper(
                    template_path=template,
                    metadata_template_path=metadata,
                    external_path=external,
                    output_path=output,
                )

    def test_quality_metrics_measure_position_signal_without_accepting_it(self) -> None:
        rows = [
            {
                "record_type": "compact_review_verse_submission",
                "groups": [
                    {
                        "original_indices": ["o001"],
                        "target_indices": ["t001"],
                        "relation": "one_to_one",
                        "severity": "normal",
                        "phenomena": ["named_entity"],
                    },
                    {
                        "original_indices": ["o002"],
                        "target_indices": ["t004"],
                        "relation": "one_to_one",
                        "severity": "high",
                        "phenomena": ["reorder"],
                    },
                    {
                        "original_indices": ["o003"],
                        "target_indices": [],
                        "relation": "original_omitted",
                        "severity": "critical",
                        "phenomena": ["omission"],
                    },
                ],
                "target_nulls": [
                    {"severity": "normal", "phenomena": ["addition"]}
                ],
            }
        ]
        metrics = compact_quality_metrics(rows)
        self.assertEqual(metrics["counts"]["one_to_one"], 2)
        self.assertEqual(metrics["counts"]["one_to_one_same_local_index"], 1)
        self.assertEqual(metrics["one_to_one_same_local_index_fraction"], 0.5)
        self.assertEqual(metrics["relations"]["original_omitted"], 1)
        self.assertEqual(metrics["severities"]["normal"], 2)


if __name__ == "__main__":
    unittest.main()

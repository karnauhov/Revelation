from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.bible_module import ukrainian_stage_7 as stage7
from scripts.bible_module.ukrainian_stage_7 import (
    _legacy_negative_annotations_for_overrides,
    _validate_finalized_gold_current_inputs,
)
from scripts.bible_module.ukrainian_stage_7_gold import (
    EXPECTED_STAGE6_COMMENT_SHA256,
    EXPECTED_STAGE6_TEXT_SHA256,
    finalize_gold,
    ingest_review_pass,
    prepare_reviewer_packets,
    validated_finalized_gold_lock,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    exact_word_tokens,
    sha256_text,
    stable_json,
)


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "gold_workflow_cases.json"
)


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class GoldWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _prepare(self, root: Path) -> tuple[Path, Path, Path]:
        text = self.fixture["plain_text"]
        tokens = exact_word_tokens(text)
        target_rows = [
            {
                "token_id": f"cc0:uk:{token.order}",
                "order": token.order,
                "surface": token.surface,
                "comparison": token.comparison,
                "start_scalar": token.start_scalar,
                "end_scalar": token.end_scalar,
                "start_byte": token.start_byte,
                "end_byte": token.end_byte,
            }
            for token in tokens
        ]
        original_rows = [
            {
                "original_token_id": row["original_token_id"],
                "order": index,
                "surface_normalized": f"source-{index}",
                "strong_classic": [f"H{index}"],
                "reading_status": "primary_mt",
            }
            for index, row in enumerate(self.fixture["originals"], 1)
        ]
        panel = {
            "schema_version": 1,
            "contract_version": CONTRACT_VERSION,
            "selection_id": "gold7:cc0-verse",
            "target_ref": "Gen.1.1",
            "verse_key": "cc0-verse",
            "book": "Gen",
            "testament": "OT",
            "plain_text_sha256": sha256_text(text),
            "comment_sha256": sha256_text(""),
            "original_token_ids": [row["original_token_id"] for row in original_rows],
            "projected_decision_count": len(original_rows),
            "strata": {
                "testament": "OT",
                "genre": "torah_prose_law",
                "mapping_operation": "merge",
                "textual_fingerprint_locus": True,
                "original_frequency_bands": ["rare_1_to_5", "frequent_1000_plus"],
            },
        }
        workbench = {
            "schema_version": 1,
            "contract_version": CONTRACT_VERSION,
            "selection_id": panel["selection_id"],
            "target_ref": panel["target_ref"],
            "plain_text_nfc": text,
            "target_comment": "",
            "target_tokens": target_rows,
            "original_tokens": original_rows,
            "strata": panel["strata"],
        }
        panel_path = root / "panel.jsonl"
        workbench_path = root / "workbench.jsonl"
        _write_jsonl(panel_path, [panel])
        _write_jsonl(workbench_path, [workbench])
        packet_dir = root / "packets"
        prepare_reviewer_packets(
            panel_path=panel_path,
            workbench_path=workbench_path,
            output_dir=packet_dir,
            minimum_verses=1,
            minimum_decisions=1,
            require_full_canon=False,
            _allow_cc0_fixture_without_immutable_corpus=True,
        )
        return (
            packet_dir / "review_pass_1.packet.jsonl",
            packet_dir / "review_pass_2.packet.jsonl",
            packet_dir / "gold_reviewer_packets.manifest.json",
        )

    def _submission(
        self,
        packet_path: Path,
        manifest_path: Path,
        *,
        reviewer: str,
        review_pass: int,
        severity_override: str | None = None,
    ) -> list[dict[str, object]]:
        packet = json.loads(packet_path.read_text(encoding="utf-8").splitlines()[0])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        target_id_by_order = {
            row["order"]: row["token_id"] for row in packet["target_tokens"]
        }
        decision_id_by_original = {
            row["original_token_id"]: row["decision_id"]
            for row in packet["original_decision_requests"]
        }
        rows: list[dict[str, object]] = [
            {
                "record_type": "review_metadata",
                "review_pass": review_pass,
                "reviewer_id": reviewer,
                "blind_to_other_pass": True,
                "packet_sha256": _sha(packet_path),
                "packet_manifest_sha256": _sha(manifest_path),
                "input_sha256": manifest["input_sha256"],
            }
        ]
        for index, item in enumerate(self.fixture["originals"]):
            original_id = item["original_token_id"]
            rows.append(
                {
                    "record_type": "original_decision",
                    "decision_status": "decided",
                    "decision_id": decision_id_by_original[original_id],
                    "original_token_id": original_id,
                    "target_ref": "Gen.1.1",
                    "relation": item["relation"],
                    "group_original_token_ids": item["group_original_token_ids"],
                    "target_token_ids": [target_id_by_order[value] for value in item["target_orders"]],
                    "null_reason": item.get("null_reason"),
                    "severity": severity_override if index == 0 and severity_override else ("high" if index == 0 else "normal"),
                    "phenomena": self.fixture["phenomena"] if index == 0 else [],
                    "evidence": [{"kind": "manual_token_context", "evidence_id": f"cc0:{reviewer}:o:{index}"}],
                    "rationale": "CC0 synthetic reviewer rationale.",
                }
            )
        accounting_id_by_target = {
            row["target_token_id"]: row["accounting_id"]
            for row in packet["target_accounting_requests"]
        }
        for index, item in enumerate(self.fixture["target_accounting"]):
            target_id = target_id_by_order[item["target_order"]]
            rows.append(
                {
                    "record_type": "target_accounting",
                    "decision_status": "decided",
                    "accounting_id": accounting_id_by_target[target_id],
                    "target_token_id": target_id,
                    "target_ref": "Gen.1.1",
                    "target_status": item["status"],
                    "linked_original_token_ids": item["linked_original_token_ids"],
                    "severity": "normal",
                    "phenomena": ["addition"] if item["status"] != "aligned" else [],
                    "evidence": [{"kind": "manual_target_context", "evidence_id": f"cc0:{reviewer}:t:{index}"}],
                    "rationale": "CC0 synthetic target accounting rationale.",
                }
            )
        return rows

    def test_prepare_is_deterministic_answer_free_and_exactly_accounted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            p1, _, manifest1 = self._prepare(first)
            p2, _, manifest2 = self._prepare(second)
            self.assertEqual(_sha(p1), _sha(p2))
            self.assertEqual(_sha(manifest1), _sha(manifest2))
            packet = json.loads(p1.read_text(encoding="utf-8").splitlines()[0])
            self.assertTrue(packet["blind_to_other_pass"])
            self.assertEqual(packet["answer_template"]["relation"], None)
            self.assertEqual(len(packet["original_decision_requests"]), 7)
            self.assertEqual(len(packet["target_accounting_requests"]), 7)

    def test_ingestion_rejects_missing_decision_and_cross_verse_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pass1_packet, _, manifest = self._prepare(root)
            rows = self._submission(pass1_packet, manifest, reviewer="reviewer-a", review_pass=1)
            missing = root / "missing.jsonl"
            _write_jsonl(missing, rows[:-1])
            with self.assertRaisesRegex(ValueError, "exactly once for every target"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=pass1_packet,
                    packet_manifest_path=manifest,
                    submission_path=missing,
                    output_path=root / "out.jsonl",
                )
            rows[1]["target_ref"] = "Gen.1.2"
            crossing = root / "crossing.jsonl"
            _write_jsonl(crossing, rows)
            with self.assertRaisesRegex(ValueError, "crosses a verse"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=pass1_packet,
                    packet_manifest_path=manifest,
                    submission_path=crossing,
                    output_path=root / "out.jsonl",
                )
            rows = self._submission(pass1_packet, manifest, reviewer="reviewer-a", review_pass=1)
            rows[0]["input_sha256"] = dict(rows[0]["input_sha256"])
            rows[0]["input_sha256"]["stage6_text"] = "0" * 64
            stale = root / "stale-lock.jsonl"
            _write_jsonl(stale, rows)
            with self.assertRaisesRegex(ValueError, "source input SHA locks differ"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=pass1_packet,
                    packet_manifest_path=manifest,
                    submission_path=stale,
                    output_path=root / "out.jsonl",
                )

    def test_ingestion_rejects_invalid_null_and_many_to_many_cardinality(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pass1_packet, _, manifest = self._prepare(root)
            rows = self._submission(pass1_packet, manifest, reviewer="reviewer-a", review_pass=1)
            omission = next(row for row in rows if row.get("relation") == "original_omitted")
            omission["null_reason"] = "unknown_reason"
            invalid_null = root / "invalid-null.jsonl"
            _write_jsonl(invalid_null, rows)
            with self.assertRaisesRegex(ValueError, "allowed reason"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=pass1_packet,
                    packet_manifest_path=manifest,
                    submission_path=invalid_null,
                    output_path=root / "out.jsonl",
                )
            rows = self._submission(pass1_packet, manifest, reviewer="reviewer-a", review_pass=1)
            many = next(row for row in rows if row.get("relation") == "many_to_many")
            many["target_token_ids"] = many["target_token_ids"][:1]
            invalid_many = root / "invalid-many.jsonl"
            _write_jsonl(invalid_many, rows)
            with self.assertRaisesRegex(ValueError, "many_to_many cardinality"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=pass1_packet,
                    packet_manifest_path=manifest,
                    submission_path=invalid_many,
                    output_path=root / "out.jsonl",
                )

    def test_finalize_requires_distinct_reviewers_and_adjudication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest = self._prepare(root)
            raw1 = root / "raw1.jsonl"
            raw2 = root / "raw2.jsonl"
            _write_jsonl(raw1, self._submission(packet1, manifest, reviewer="same", review_pass=1))
            _write_jsonl(raw2, self._submission(packet2, manifest, reviewer="same", review_pass=2))
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(review_pass=1, packet_path=packet1, packet_manifest_path=manifest, submission_path=raw1, output_path=pass1)
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            with self.assertRaisesRegex(ValueError, "distinct reviewers"):
                finalize_gold(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    packet_manifest_path=manifest,
                    report_dir=root / "report",
                    minimum_verses=1,
                    minimum_decisions=1,
                )

            _write_jsonl(raw2, self._submission(packet2, manifest, reviewer="reviewer-b", review_pass=2, severity_override="normal"))
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            with self.assertRaisesRegex(ValueError, "require explicit adjudication"):
                finalize_gold(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    packet_manifest_path=manifest,
                    report_dir=root / "report",
                    minimum_verses=1,
                    minimum_decisions=1,
                )

    def test_finalize_rejects_a_pass_changed_after_ingestion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest = self._prepare(root)
            raw1 = root / "raw1.jsonl"
            raw2 = root / "raw2.jsonl"
            _write_jsonl(raw1, self._submission(packet1, manifest, reviewer="reviewer-a", review_pass=1))
            _write_jsonl(raw2, self._submission(packet2, manifest, reviewer="reviewer-b", review_pass=2))
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(review_pass=1, packet_path=packet1, packet_manifest_path=manifest, submission_path=raw1, output_path=pass1)
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            pass1.write_text(pass1.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from its digest sidecar"):
                finalize_gold(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    packet_manifest_path=manifest,
                    report_dir=root / "report",
                    minimum_verses=1,
                    minimum_decisions=1,
                )

    def test_adjudicated_finalize_writes_and_verifies_protection_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest = self._prepare(root)
            raw1 = root / "raw1.jsonl"
            raw2 = root / "raw2.jsonl"
            _write_jsonl(raw1, self._submission(packet1, manifest, reviewer="reviewer-a", review_pass=1))
            _write_jsonl(raw2, self._submission(packet2, manifest, reviewer="reviewer-b", review_pass=2, severity_override="normal"))
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(review_pass=1, packet_path=packet1, packet_manifest_path=manifest, submission_path=raw1, output_path=pass1)
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            first_decision = next(
                row
                for row in json.loads("[" + ",".join(pass1.read_text(encoding="utf-8").splitlines()) + "]")
                if row.get("original_token_id") == "cc0:orig:1"
            )
            adjudication = root / "adjudication.jsonl"
            adjudicated = dict(first_decision)
            adjudicated["severity"] = "normal"
            adjudicated["evidence"] = [{"kind": "manual_adjudication", "evidence_id": "cc0:adjudication:1"}]
            adjudicated["rationale"] = "CC0 synthetic adjudication rationale."
            _write_jsonl(
                adjudication,
                [
                    {
                        "record_type": "adjudication_metadata",
                        "adjudicator_id": "adjudicator-c",
                        "pass_1_sha256": _sha(pass1),
                        "pass_2_sha256": _sha(pass2),
                        "packet_manifest_sha256": _sha(manifest),
                    },
                    adjudicated,
                ],
            )
            report = root / "report"
            result = finalize_gold(
                pass1_path=pass1,
                pass2_path=pass2,
                packet_manifest_path=manifest,
                report_dir=report,
                adjudication_path=adjudication,
                minimum_verses=1,
                minimum_decisions=1,
            )
            second_report = root / "report-second"
            finalize_gold(
                pass1_path=pass1,
                pass2_path=pass2,
                packet_manifest_path=manifest,
                report_dir=second_report,
                adjudication_path=adjudication,
                minimum_verses=1,
                minimum_decisions=1,
            )
            self.assertEqual(result["status"], "finalized_reviewed_gold")
            self.assertEqual(result["counts"]["accepted_assignment_or_null_decisions"], 7)
            self.assertEqual(result["counts"]["target_token_accounting_decisions"], 7)
            self.assertEqual(result["counts"]["unresolved_critical_high"], 0)
            self.assertIsNotNone(validated_finalized_gold_lock(report))
            annotations = report / "gold_alignment.annotations.jsonl"
            self.assertEqual(
                _sha(annotations),
                _sha(second_report / "gold_alignment.annotations.jsonl"),
            )
            self.assertEqual(
                _sha(report / "gold_alignment.manifest.json"),
                _sha(second_report / "gold_alignment.manifest.json"),
            )
            final_rows = [
                json.loads(line)
                for line in annotations.read_text(encoding="utf-8").splitlines()
            ]
            target_rows = [
                row for row in final_rows if row["record_type"] == "target_accounting"
            ]
            self.assertEqual(len(target_rows), 7)
            self.assertTrue(
                all(
                    {"start_scalar", "end_scalar", "start_byte", "end_byte", "surface_sha256"}
                    <= set(row["target_span"])
                    for row in target_rows
                )
            )
            annotations.write_text(annotations.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed after review"):
                validated_finalized_gold_lock(report)

    def test_prepare_manifest_uses_exact_immutable_stage6_locks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, manifest_path = self._prepare(Path(directory))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["input_sha256"]["stage6_text"], EXPECTED_STAGE6_TEXT_SHA256)
            self.assertEqual(manifest["input_sha256"]["stage6_comments"], EXPECTED_STAGE6_COMMENT_SHA256)

    def test_production_finalize_requires_exact_v2_input_lock_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest_path = self._prepare(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["corpus_contract"] = "ohienko_1988_production"
            manifest_path.write_text(
                stable_json(manifest) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "exact immutable input lock set"):
                finalize_gold(
                    pass1_path=packet1,
                    pass2_path=packet2,
                    packet_manifest_path=manifest_path,
                    report_dir=root / "report",
                    minimum_verses=1,
                    minimum_decisions=1,
                )


class GoldMainIntegrationGuardTest(unittest.TestCase):
    def test_current_inputs_are_an_exact_required_subset_of_review_locks(self) -> None:
        current = {"stage6_text": "a" * 64, "gold_selection_panel": "b" * 64}
        lock = {
            "input_sha256": {
                **current,
                "review_pass_1": "c" * 64,
                "review_pass_2": "d" * 64,
                "adjudication": "e" * 64,
            }
        }
        _validate_finalized_gold_current_inputs(lock, current)
        with self.assertRaisesRegex(RuntimeError, "gold_selection_panel"):
            _validate_finalized_gold_current_inputs(
                lock, {**current, "gold_selection_panel": "f" * 64}
            )
        with self.assertRaisesRegex(RuntimeError, "stage6_comments"):
            _validate_finalized_gold_current_inputs(
                lock, {**current, "stage6_comments": "0" * 64}
            )

    def test_legacy_overrides_use_separate_negative_rows_not_final_hyperedges(self) -> None:
        negative = {
            "record_type": "negative_edge",
            "annotation_id": "gold7-negative-cc0",
            "original": {"legacy_source_token_id": "cc0:legacy:1"},
        }
        gold = {
            "legacy_negative_annotations": [negative],
            "legacy_negative_annotation_count": 1,
            "annotations_path": "finalized-gold-with-hyperedges.jsonl",
        }
        self.assertEqual(_legacy_negative_annotations_for_overrides(gold), [negative])
        with self.assertRaisesRegex(RuntimeError, "schema drifted"):
            _legacy_negative_annotations_for_overrides(
                {
                    "legacy_negative_annotations": [
                        {"record_type": "hyperedge", "edge_id": "cc0:edge:1"}
                    ],
                    "legacy_negative_annotation_count": 1,
                }
            )

    def test_verify_existing_delegates_to_finalized_lock_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report"
            report.mkdir()
            report.joinpath("source_registry.json").write_text(
                stable_json(stage7._seal_payload({"sources": []})) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with (
                patch.object(stage7, "_stage6_rows", return_value=([], {})),
                patch.object(stage7, "REQUIRED_REPORTS", ()),
                patch.object(stage7, "_source_registry", return_value={"sources": []}),
                patch.object(
                    stage7,
                    "validated_finalized_gold_lock",
                    side_effect=ValueError("tampered finalized gold"),
                ),
            ):
                with self.assertRaisesRegex(ValueError, "tampered finalized gold"):
                    stage7.verify_existing(
                        work_dir=Path(directory) / "work",
                        report_dir=report,
                    )


if __name__ == "__main__":
    unittest.main()

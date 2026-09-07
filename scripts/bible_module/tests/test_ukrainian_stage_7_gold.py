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
    _semantic_for_key,
    finalize_gold,
    ingest_review_pass,
    prepare_reviewer_packets,
    validated_finalized_gold_lock,
)
from scripts.bible_module.ukrainian_stage_7_gold_compare import (
    compare_review_files,
    main as gold_compare_main,
    seal_consensus_correction_shard,
    validate_adjudication_qc,
    validate_adjudication_shard,
    validate_consensus_correction_shard,
    validate_post_consensus_correction_qc,
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

    @staticmethod
    def _change_first_link_to_null(rows: list[dict[str, object]]) -> None:
        original = next(
            row for row in rows if row.get("original_token_id") == "cc0:orig:1"
        )
        original.update(
            {
                "relation": "original_omitted",
                "target_token_ids": [],
                "null_reason": "translation_omission",
            }
        )
        target = next(
            row
            for row in rows
            if row.get("record_type") == "target_accounting"
            and row.get("linked_original_token_ids") == ["cc0:orig:1"]
        )
        target.update(
            {
                "target_status": "translation_addition",
                "linked_original_token_ids": [],
            }
        )

    def _adjudication_qc_fixture(
        self, root: Path, *, schema_variant: str = "josh"
    ) -> dict[str, object]:
        root.mkdir(parents=True, exist_ok=True)
        packet1, packet2, packet_manifest = self._prepare(root)
        raw1 = root / "raw1.jsonl"
        raw2 = root / "raw2.jsonl"
        rows1 = self._submission(
            packet1, packet_manifest, reviewer="reviewer-a", review_pass=1
        )
        rows2 = self._submission(
            packet2, packet_manifest, reviewer="reviewer-b", review_pass=2
        )
        self._change_first_link_to_null(rows2)
        _write_jsonl(raw1, rows1)
        _write_jsonl(raw2, rows2)
        pass1 = root / "pass1.jsonl"
        pass2 = root / "pass2.jsonl"
        ingest_review_pass(
            review_pass=1,
            packet_path=packet1,
            packet_manifest_path=packet_manifest,
            submission_path=raw1,
            output_path=pass1,
        )
        ingest_review_pass(
            review_pass=2,
            packet_path=packet2,
            packet_manifest_path=packet_manifest,
            submission_path=raw2,
            output_path=pass2,
        )
        comparison = root / "comparison.jsonl"
        compare_review_files(
            pass1_path=pass1,
            pass2_path=pass2,
            output_path=comparison,
        )
        pass1_rows = [
            json.loads(line)
            for line in pass1.read_text(encoding="utf-8").splitlines()
        ]
        pass2_rows = [
            json.loads(line)
            for line in pass2.read_text(encoding="utf-8").splitlines()
        ]
        pass1_values = {
            (
                "original:" + str(row["decision_id"])
                if row.get("record_type") == "original_decision"
                else "target:" + str(row["accounting_id"])
            ): row
            for row in pass1_rows
            if row.get("record_type") != "review_metadata"
        }
        pass2_values = {
            (
                "original:" + str(row["decision_id"])
                if row.get("record_type") == "original_decision"
                else "target:" + str(row["accounting_id"])
            ): row
            for row in pass2_rows
            if row.get("record_type") != "review_metadata"
        }
        adjudicated = [
            dict(row)
            for row in pass1_values.values()
            if row.get("original_token_id") == "cc0:orig:1"
            or (
                row.get("record_type") == "target_accounting"
                and row.get("linked_original_token_ids") == ["cc0:orig:1"]
            )
        ]
        for index, row in enumerate(adjudicated, 1):
            row["reviewer_id"] = "adjudicator-c"
            if schema_variant == "semantic":
                row["phenomena"] = sorted(
                    set(row.get("phenomena", [])) | {"manual_adjudication"}
                )
            row["evidence"] = [
                {
                    "kind": "manual_adjudication",
                    "evidence_id": f"cc0:adjudication:{index}",
                }
            ]
            row["rationale"] = "Independent CC0 adjudication rationale."
        adjudication = root / "adjudication.jsonl"
        _write_jsonl(
            adjudication,
            [
                {
                    "record_type": "adjudication_shard_metadata",
                    "status": "complete_manual_adjudication_shard",
                    "adjudicator_id": "adjudicator-c",
                    "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
                    "comparison_sha256": _sha(comparison),
                    "pass_1_sha256": _sha(pass1),
                    "pass_2_sha256": _sha(pass2),
                },
                *adjudicated,
            ],
        )
        adjudication_manifest = Path(str(adjudication) + ".manifest.json")
        adjudication_manifest.write_text(
            stable_json(
                {
                    "status": "complete_manual_adjudication_shard",
                    "input_sha256": {
                        "review_pass_1": _sha(pass1),
                        "review_pass_2": _sha(pass2),
                        "comparison": _sha(comparison),
                    },
                    "output_sha256": {adjudication.name: _sha(adjudication)},
                }
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        adjudication_check = validate_adjudication_shard(
            pass1_path=pass1,
            pass2_path=pass2,
            comparison_path=comparison,
            adjudication_path=adjudication,
        )

        packet = json.loads(packet1.read_text(encoding="utf-8").splitlines()[0])
        template = root / "template.jsonl"
        _write_jsonl(
            template,
            [
                {
                    "target_ref": packet["target_ref"],
                    "plain_text_nfc": packet["plain_text_nfc"],
                    "target_comment": packet["target_comment"],
                    "original_index": [
                        {"decision_id": row["decision_id"]}
                        for row in packet["original_decision_requests"]
                    ],
                    "target_index": [
                        {"accounting_id": row["accounting_id"]}
                        for row in packet["target_accounting_requests"]
                    ],
                }
            ],
        )
        template_manifest = root / "template.manifest.json"
        template_manifest.write_text(
            stable_json(
                {
                    "status": "prepared_answer_free_compact_review",
                    "processed_count": 1,
                    "output_sha256": {template.name: _sha(template)},
                }
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        qc_reviewer = "qc-reviewer-d"
        adjudication_values = {
            (
                "original:" + str(row["decision_id"])
                if row["record_type"] == "original_decision"
                else "target:" + str(row["accounting_id"])
            ): row
            for row in adjudicated
        }
        qc_header: dict[str, object] = {
            "schema_version": 1,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": "ukrainian-stage-7-gold-workflow-v2",
            "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
            "adjudication_shard_version": (
                "ukrainian-stage-7-adjudication-shard-v1"
            ),
            "qc_version": "ukrainian-stage-7-adjudication-independent-qc-v1",
            "record_type": "qc_metadata",
            "artifact": "independent_adjudication_content_qc",
            "audit_id": qc_reviewer,
            "overall_verdict": "accepted",
            "shard_blocked": False,
        }
        if schema_variant != "lev":
            qc_header["status"] = "complete_qc_accepted"
            qc_header["reviewer_id"] = qc_reviewer
        if schema_variant == "semantic":
            qc_header["selection_basis"] = "semantic"
            qc_header["alignment_selection_counts"] = {"pass_1": 2}
            qc_header["semantic_selection_counts"] = {"new": 2}
        qc_results: list[dict[str, object]] = []
        for stable_key in sorted(adjudication_values):
            final = adjudication_values[stable_key]
            result: dict[str, object] = {
                "schema_version": 1,
                "qc_version": (
                    "ukrainian-stage-7-adjudication-independent-qc-v1"
                ),
                "record_type": "qc_adjudication_result",
                "audit_id": qc_reviewer,
                "stable_key": stable_key,
                "target_ref": final["target_ref"],
                "adjudication_record_type": final["record_type"],
                "adjudication_severity": final["severity"],
                "selection_category": (
                    "new" if schema_variant == "semantic" else "pass_1"
                ),
                "pass_1_semantics": _semantic_for_key(
                    pass1_values[stable_key]
                ),
                "pass_2_semantics": _semantic_for_key(
                    pass2_values[stable_key]
                ),
                "adjudication_semantics": _semantic_for_key(final),
                "adjudication_evidence_ids": [
                    item["evidence_id"] for item in final["evidence"]
                ],
                "adjudication_rationale_sha256": sha256_text(
                    str(final["rationale"])
                ),
                "source_evidence": [],
                "target_evidence": [],
                "oh1988_exact_text": packet["plain_text_nfc"],
                "oh1988_exact_text_sha256": sha256_text(
                    packet["plain_text_nfc"]
                ),
                "target_comment": packet["target_comment"],
                "target_comment_sha256": sha256_text(
                    packet["target_comment"]
                ),
                "comparison_checked": True,
                "pass_reviews_checked": True,
                "target_comment_checked": True,
                "content_dimensions_checked": [
                    "exact_oh1988_comment",
                    "exact_oh1988_surface",
                    "reciprocal_accounting",
                ],
                "manual_scopes": ["all_adjudication_decisions"],
                "rationale": "Independent CC0 QC rationale.",
                "verdict": "accepted",
            }
            if schema_variant == "num":
                result["reviewer_id"] = qc_reviewer
                result["reciprocal_accounting_checked"] = True
            elif schema_variant == "josh":
                result["full_grid_checked"] = True
                result["reciprocal_accounting_checked"] = True
            qc_results.append(result)
        qc = root / "qc.jsonl"
        _write_jsonl(qc, [qc_header, *qc_results])
        high_keys = sorted(
            stable_key
            for stable_key, row in adjudication_values.items()
            if row["severity"] == "high"
        )
        input_sha256 = {
            "review_pass_1": _sha(pass1),
            "review_pass_1_manifest": _sha(
                Path(str(pass1) + ".manifest.json")
            ),
            "review_pass_2": _sha(pass2),
            "review_pass_2_manifest": _sha(
                Path(str(pass2) + ".manifest.json")
            ),
            "comparison": _sha(comparison),
            "comparison_manifest": _sha(
                Path(str(comparison) + ".manifest.json")
            ),
            "adjudication": _sha(adjudication),
            "adjudication_manifest": _sha(adjudication_manifest),
            "answer_free_template": _sha(template),
            "answer_free_template_manifest": _sha(template_manifest),
        }
        selected_counts = (
            {"new": 2} if schema_variant == "semantic" else {"pass_1": 2}
        )
        new_keys = (
            sorted(adjudication_values) if schema_variant == "semantic" else []
        )
        verdict_counts = {"accepted": 2}
        if schema_variant == "num":
            verdict_counts.update({"error": 0, "uncertain": 0})
        counts: dict[str, object] = {
            "adjudication_data_rows": 2,
            "affected_verses": 1,
            "audited_result_rows": 2,
            "high_rows_checked": 1,
            "new_rows_checked": len(new_keys),
            "qc_jsonl_lines": 3,
            "record_type": {
                "original_decision": 1,
                "target_accounting": 1,
            },
            "selection": selected_counts,
            "severity": {"high": 1, "normal": 1},
            "template_original_tokens": 7,
            "template_target_tokens": 7,
            "verdict": verdict_counts,
        }
        if schema_variant != "lev":
            counts["full_final_grid"] = 14
        if schema_variant == "semantic":
            counts["alignment_selection_counts"] = {"pass_1": 2}
            counts["semantic_selection_counts"] = {"new": 2}
        qc_manifest: dict[str, object] = {
            "schema_version": 1,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": "ukrainian-stage-7-gold-workflow-v2",
            "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
            "adjudication_shard_version": (
                "ukrainian-stage-7-adjudication-shard-v1"
            ),
            "qc_version": "ukrainian-stage-7-adjudication-independent-qc-v1",
            "artifact": "independent_adjudication_content_qc_manifest",
            "audit_id": qc_reviewer,
            "status": "complete_qc_accepted",
            "overall_verdict": "accepted",
            "shard_accepted": True,
            "processed_count": 2,
            "skipped_count": 0,
            "error_count": 0,
            "uncertain_count": 0,
            "error_stable_keys": [],
            "uncertain_stable_keys": [],
            "high_stable_keys": high_keys,
            "new_stable_keys": new_keys,
            "input_sha256": input_sha256,
            "output_sha256": {qc.name: _sha(qc)},
            "counts": counts,
            "check_adjudication_result": adjudication_check,
            "prohibited_signal_check": {
                "candidates": "not_used",
                "frequency_or_majority": "not_used",
                "legacy": "not_used",
                "neighbor": "not_used",
                "position": (
                    "not_used; stable IDs only"
                    if schema_variant == "num"
                    else "not_used"
                ),
                "verse_bag": "not_used",
            },
            "reviewer_independence": {
                "pass_1_reviewer_id": "reviewer-a",
                "pass_2_reviewer_id": "reviewer-b",
                "adjudicator_id": "adjudicator-c",
            },
        }
        if schema_variant == "num":
            qc_manifest["reviewer_id"] = qc_reviewer
            qc_manifest["critical_high_unresolved_stable_keys"] = []
        else:
            qc_manifest["critical_high_uncertain_stable_keys"] = []
            if schema_variant == "josh":
                qc_manifest["reviewer_id"] = qc_reviewer
        if schema_variant == "semantic":
            qc_manifest["reviewer_id"] = qc_reviewer
            qc_manifest["selection_basis"] = "semantic"
        qc_manifest_path = qc.with_suffix(".manifest.json")
        qc_manifest_path.write_text(
            stable_json(qc_manifest) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return {
            "pass1": pass1,
            "pass2": pass2,
            "comparison": comparison,
            "adjudication": adjudication,
            "template": template,
            "template_manifest": template_manifest,
            "qc": qc,
            "qc_manifest": qc_manifest_path,
            "qc_manifest_sha256": _sha(qc_manifest_path),
            "agreed_stable_key": next(
                stable_key
                for stable_key in sorted(pass1_values)
                if stable_key not in adjudication_values
            ),
        }

    @staticmethod
    def _resign_adjudication_qc(fixture: dict[str, object]) -> str:
        qc = fixture["qc"]
        qc_manifest_path = fixture["qc_manifest"]
        assert isinstance(qc, Path)
        assert isinstance(qc_manifest_path, Path)
        manifest = json.loads(qc_manifest_path.read_text(encoding="utf-8"))
        manifest["output_sha256"] = {qc.name: _sha(qc)}
        qc_manifest_path.write_text(
            stable_json(manifest) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return _sha(qc_manifest_path)

    @staticmethod
    def _validate_adjudication_qc_fixture(
        fixture: dict[str, object], *, manifest_sha256: str | None = None
    ) -> dict[str, object]:
        paths = {
            name: fixture[name]
            for name in (
                "pass1",
                "pass2",
                "comparison",
                "adjudication",
                "template",
                "template_manifest",
                "qc",
            )
        }
        assert all(isinstance(path, Path) for path in paths.values())
        digest = manifest_sha256 or fixture["qc_manifest_sha256"]
        assert isinstance(digest, str)
        return validate_adjudication_qc(
            pass1_path=paths["pass1"],
            pass2_path=paths["pass2"],
            comparison_path=paths["comparison"],
            adjudication_path=paths["adjudication"],
            answer_free_template_path=paths["template"],
            answer_free_template_manifest_path=paths["template_manifest"],
            qc_path=paths["qc"],
            qc_manifest_sha256=digest,
        )

    def test_adjudication_qc_accepts_lev_num_and_josh_schema_variants(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for variant in ("lev", "num", "josh", "semantic"):
                with self.subTest(variant=variant):
                    variant_root = root / variant
                    variant_root.mkdir()
                    fixture = self._adjudication_qc_fixture(
                        variant_root, schema_variant=variant
                    )
                    result = self._validate_adjudication_qc_fixture(fixture)
                    self.assertEqual(
                        result["status"],
                        "valid_complete_independent_adjudication_qc_accepted",
                    )
                    self.assertEqual(result["processed_count"], 2)
                    self.assertEqual(result["counts"]["full_final_grid"], 14)
                    self.assertEqual(
                        result["selection_basis"],
                        "semantic" if variant == "semantic" else "alignment",
                    )

            fixture = self._adjudication_qc_fixture(
                root / "cli", schema_variant="josh"
            )
            cli_args = [
                "check-adjudication-qc",
                "--pass1",
                str(fixture["pass1"]),
                "--pass2",
                str(fixture["pass2"]),
                "--comparison",
                str(fixture["comparison"]),
                "--adjudication",
                str(fixture["adjudication"]),
                "--template",
                str(fixture["template"]),
                "--template-manifest",
                str(fixture["template_manifest"]),
                "--qc",
                str(fixture["qc"]),
                "--qc-manifest-sha256",
                str(fixture["qc_manifest_sha256"]),
            ]
            with patch("builtins.print") as print_mock:
                self.assertEqual(gold_compare_main(cli_args), 0)
            self.assertIn(
                "valid_complete_independent_adjudication_qc_accepted",
                print_mock.call_args.args[0],
            )

    def test_adjudication_qc_rejects_stale_hashes_and_noncanonical_files(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._adjudication_qc_fixture(Path(directory))
            qc = fixture["qc"]
            manifest_path = fixture["qc_manifest"]
            assert isinstance(qc, Path)
            assert isinstance(manifest_path, Path)
            original_qc = qc.read_bytes()
            original_manifest = manifest_path.read_bytes()
            original_manifest_sha = _sha(manifest_path)

            with self.assertRaisesRegex(ValueError, "sidecar SHA-256 is stale"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256="0" * 64
                )

            qc.write_bytes(original_qc + b"\n")
            with self.assertRaisesRegex(ValueError, "differs from its digest sidecar"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=original_manifest_sha
                )

            qc.write_bytes(original_qc)
            manifest = json.loads(original_manifest)
            manifest["input_sha256"]["comparison"] = "0" * 64
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "input SHA locks are stale"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=_sha(manifest_path)
                )

            manifest_path.write_bytes(original_manifest + b" ")
            with self.assertRaisesRegex(ValueError, "sidecar SHA-256 is stale"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=original_manifest_sha
                )

            manifest_path.write_bytes(original_manifest)
            rows = [
                json.loads(line)
                for line in qc.read_text(encoding="utf-8").splitlines()
            ]
            qc.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            resigned_sha = self._resign_adjudication_qc(fixture)
            with self.assertRaisesRegex(ValueError, "not canonical UTF-8/LF"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=resigned_sha
                )

    def test_adjudication_qc_rejects_reviewer_scope_semantic_and_counts_tamper(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._adjudication_qc_fixture(Path(directory))
            qc = fixture["qc"]
            manifest_path = fixture["qc_manifest"]
            assert isinstance(qc, Path)
            assert isinstance(manifest_path, Path)
            original_qc = qc.read_bytes()
            original_manifest = manifest_path.read_bytes()

            def reset() -> None:
                qc.write_bytes(original_qc)
                manifest_path.write_bytes(original_manifest)

            def qc_rows() -> list[dict[str, object]]:
                return [
                    json.loads(line)
                    for line in qc.read_text(encoding="utf-8").splitlines()
                ]

            rows = qc_rows()
            for row in rows:
                row["audit_id"] = "adjudicator-c"
                if "reviewer_id" in row:
                    row["reviewer_id"] = "adjudicator-c"
            _write_jsonl(qc, rows)
            manifest = json.loads(original_manifest)
            manifest["audit_id"] = "adjudicator-c"
            manifest["reviewer_id"] = "adjudicator-c"
            manifest["output_sha256"] = {qc.name: _sha(qc)}
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "reviewer independence"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=_sha(manifest_path)
                )

            reset()
            rows = qc_rows()
            _write_jsonl(qc, rows[:-1])
            with self.assertRaisesRegex(ValueError, "scope is missing"):
                self._validate_adjudication_qc_fixture(
                    fixture,
                    manifest_sha256=self._resign_adjudication_qc(fixture),
                )

            reset()
            rows = qc_rows()
            extra = dict(rows[1])
            extra["stable_key"] = fixture["agreed_stable_key"]
            _write_jsonl(qc, [*rows, extra])
            with self.assertRaisesRegex(ValueError, "scope has an extra"):
                self._validate_adjudication_qc_fixture(
                    fixture,
                    manifest_sha256=self._resign_adjudication_qc(fixture),
                )

            for field, value in (
                ("adjudication_semantics", {"record_type": "invalid"}),
                ("adjudication_evidence_ids", ["cc0:tampered"]),
                ("target_ref", "Exod.1.1"),
                ("oh1988_exact_text_sha256", "0" * 64),
            ):
                with self.subTest(field=field):
                    reset()
                    rows = qc_rows()
                    rows[1][field] = value
                    _write_jsonl(qc, rows)
                    with self.assertRaisesRegex(
                        ValueError, "semantic/evidence/text payload differs"
                    ):
                        self._validate_adjudication_qc_fixture(
                            fixture,
                            manifest_sha256=self._resign_adjudication_qc(
                                fixture
                            ),
                        )

            reset()
            manifest = json.loads(original_manifest)
            manifest["processed_count"] = 1
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "counts or stable-key sets"):
                self._validate_adjudication_qc_fixture(
                    fixture, manifest_sha256=_sha(manifest_path)
                )

            semantic_fixture = self._adjudication_qc_fixture(
                Path(directory) / "semantic", schema_variant="semantic"
            )
            semantic_qc = semantic_fixture["qc"]
            semantic_manifest_path = semantic_fixture["qc_manifest"]
            assert isinstance(semantic_qc, Path)
            assert isinstance(semantic_manifest_path, Path)
            semantic_rows = [
                json.loads(line)
                for line in semantic_qc.read_text(encoding="utf-8").splitlines()
            ]
            semantic_rows[1]["selection_category"] = "pass_1"
            _write_jsonl(semantic_qc, semantic_rows)
            with self.assertRaisesRegex(ValueError, "semantic/evidence/text payload"):
                self._validate_adjudication_qc_fixture(
                    semantic_fixture,
                    manifest_sha256=self._resign_adjudication_qc(
                        semantic_fixture
                    ),
                )

            semantic_fixture = self._adjudication_qc_fixture(
                Path(directory) / "mixed-basis", schema_variant="semantic"
            )
            semantic_manifest_path = semantic_fixture["qc_manifest"]
            assert isinstance(semantic_manifest_path, Path)
            semantic_manifest = json.loads(
                semantic_manifest_path.read_text(encoding="utf-8")
            )
            semantic_manifest["selection_basis"] = "alignment"
            semantic_manifest_path.write_text(
                stable_json(semantic_manifest) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "selection basis differs"):
                self._validate_adjudication_qc_fixture(
                    semantic_fixture,
                    manifest_sha256=_sha(semantic_manifest_path),
                )

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

    def test_finalize_requires_distinct_reviewers_and_alignment_adjudication(self) -> None:
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

            rows2 = self._submission(
                packet2,
                manifest,
                reviewer="reviewer-b",
                review_pass=2,
                severity_override="normal",
            )
            next(
                row
                for row in rows2
                if row.get("original_token_id") == "cc0:orig:1"
            )["phenomena"] = []
            _write_jsonl(raw2, rows2)
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            result = finalize_gold(
                pass1_path=pass1,
                pass2_path=pass2,
                packet_manifest_path=manifest,
                report_dir=root / "metadata-consensus",
                minimum_verses=1,
                minimum_decisions=1,
            )
            self.assertEqual(result["counts"]["review_disagreements"], 0)
            self.assertEqual(
                result["counts"]["review_metadata_differences_merged"], 1
            )
            accepted = [
                row
                for row in json.loads(
                    "["
                    + ",".join(
                        (root / "metadata-consensus" / "gold_alignment.annotations.jsonl")
                        .read_text(encoding="utf-8")
                        .splitlines()
                    )
                    + "]"
                )
                if row.get("original_token_id") == "cc0:orig:1"
            ][0]
            self.assertEqual(accepted["severity"], "high")
            self.assertEqual(accepted["phenomena"], sorted(self.fixture["phenomena"]))

            self._change_first_link_to_null(rows2)
            _write_jsonl(raw2, rows2)
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=manifest,
                submission_path=raw2,
                output_path=pass2,
            )
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
            rows2 = self._submission(
                packet2,
                manifest,
                reviewer="reviewer-b",
                review_pass=2,
                severity_override="normal",
            )
            self._change_first_link_to_null(rows2)
            _write_jsonl(raw2, rows2)
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(review_pass=1, packet_path=packet1, packet_manifest_path=manifest, submission_path=raw1, output_path=pass1)
            ingest_review_pass(review_pass=2, packet_path=packet2, packet_manifest_path=manifest, submission_path=raw2, output_path=pass2)
            first_decision = next(
                row
                for row in json.loads("[" + ",".join(pass1.read_text(encoding="utf-8").splitlines()) + "]")
                if row.get("original_token_id") == "cc0:orig:1"
            )
            first_target = next(
                row
                for row in json.loads(
                    "[" + ",".join(pass1.read_text(encoding="utf-8").splitlines()) + "]"
                )
                if row.get("record_type") == "target_accounting"
                and row.get("linked_original_token_ids") == ["cc0:orig:1"]
            )
            adjudication = root / "adjudication.jsonl"
            adjudicated = dict(first_decision)
            adjudicated["evidence"] = [{"kind": "manual_adjudication", "evidence_id": "cc0:adjudication:1"}]
            adjudicated["rationale"] = "CC0 synthetic adjudication rationale."
            adjudicated_target = dict(first_target)
            adjudicated_target["evidence"] = [
                {
                    "kind": "manual_adjudication",
                    "evidence_id": "cc0:adjudication:2",
                }
            ]
            adjudicated_target["rationale"] = (
                "CC0 synthetic target-accounting adjudication rationale."
            )
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
                    adjudicated_target,
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
                    {
                        "start_scalar",
                        "end_scalar",
                        "start_byte",
                        "end_byte",
                        "surface_sha256",
                    }
                    <= set(row["target_span"])
                    for row in target_rows
                )
            )
            annotations.write_text(
                annotations.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "changed after review"):
                validated_finalized_gold_lock(report)

    def test_pair_comparison_and_shard_adjudication_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest = self._prepare(root)
            raw1 = root / "raw1.jsonl"
            raw2 = root / "raw2.jsonl"
            rows1 = self._submission(
                packet1, manifest, reviewer="reviewer-a", review_pass=1
            )
            rows2 = self._submission(
                packet2,
                manifest,
                reviewer="reviewer-b",
                review_pass=2,
                severity_override="normal",
            )
            _write_jsonl(raw1, rows1)
            _write_jsonl(raw2, rows2)
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(
                review_pass=1,
                packet_path=packet1,
                packet_manifest_path=manifest,
                submission_path=raw1,
                output_path=pass1,
            )
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=manifest,
                submission_path=raw2,
                output_path=pass2,
            )
            metadata_only = root / "metadata-only.jsonl"
            metadata_result = compare_review_files(
                pass1_path=pass1,
                pass2_path=pass2,
                output_path=metadata_only,
            )
            self.assertEqual(metadata_result["counts"]["alignment_disagreements"], 0)
            self.assertEqual(metadata_result["counts"]["metadata_only_differences"], 1)

            self._change_first_link_to_null(rows2)
            _write_jsonl(raw2, rows2)
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=manifest,
                submission_path=raw2,
                output_path=pass2,
            )
            comparison = root / "comparison.jsonl"
            comparison_result = compare_review_files(
                pass1_path=pass1,
                pass2_path=pass2,
                output_path=comparison,
            )
            self.assertEqual(comparison_result["counts"]["alignment_disagreements"], 2)
            normalized1 = [
                json.loads(line)
                for line in pass1.read_text(encoding="utf-8").splitlines()
            ]
            decisions = [
                dict(row)
                for row in normalized1
                if row.get("original_token_id") == "cc0:orig:1"
                or (
                    row.get("record_type") == "target_accounting"
                    and row.get("linked_original_token_ids") == ["cc0:orig:1"]
                )
            ]
            for index, row in enumerate(decisions, 1):
                row["evidence"] = [
                    {
                        "kind": "manual_adjudication",
                        "evidence_id": f"cc0:adjudication:{index}",
                    }
                ]
                row["rationale"] = "Independent CC0 adjudication rationale."
            adjudication = root / "adjudication-shard.jsonl"
            header = {
                "record_type": "adjudication_shard_metadata",
                "status": "complete_manual_adjudication_shard",
                "adjudicator_id": "adjudicator-c",
                "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
                "comparison_sha256": _sha(comparison),
                "pass_1_sha256": _sha(pass1),
                "pass_2_sha256": _sha(pass2),
            }
            _write_jsonl(adjudication, [header, *decisions])
            Path(str(adjudication) + ".manifest.json").write_text(
                stable_json(
                    {
                        "status": "complete_manual_adjudication_shard",
                        "input_sha256": {
                            "review_pass_1": _sha(pass1),
                            "review_pass_2": _sha(pass2),
                            "comparison": _sha(comparison),
                        },
                        "output_sha256": {
                            adjudication.name: _sha(adjudication)
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            checked = validate_adjudication_shard(
                pass1_path=pass1,
                pass2_path=pass2,
                comparison_path=comparison,
                adjudication_path=adjudication,
            )
            self.assertEqual(checked["processed_count"], 2)
            original_comparison_text = comparison.read_text(encoding="utf-8")
            comparison_rows = [
                json.loads(line) for line in original_comparison_text.splitlines()
            ]
            comparison_rows[1]["pass_1"]["decision"]["relation"] = (
                "original_omitted"
            )
            _write_jsonl(comparison, comparison_rows)
            comparison_sidecar_path = Path(str(comparison) + ".manifest.json")
            comparison_sidecar = json.loads(
                comparison_sidecar_path.read_text(encoding="utf-8")
            )
            comparison_sidecar["output_sha256"][comparison.name] = _sha(
                comparison
            )
            comparison_sidecar_path.write_text(
                stable_json(comparison_sidecar) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "payload differs"):
                validate_adjudication_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                )
            comparison.write_text(
                original_comparison_text,
                encoding="utf-8",
                newline="\n",
            )
            comparison_sidecar["output_sha256"][comparison.name] = _sha(
                comparison
            )
            comparison_sidecar_path.write_text(
                stable_json(comparison_sidecar) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            agreed = next(
                row
                for row in normalized1
                if row.get("original_token_id") == "cc0:orig:2"
            )
            _write_jsonl(adjudication, [header, *decisions, agreed])
            with self.assertRaisesRegex(ValueError, "agreed, unknown or duplicate"):
                validate_adjudication_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                )

    def test_consensus_correction_is_exact_independent_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, manifest = self._prepare(root)
            raw1 = root / "raw1.jsonl"
            raw2 = root / "raw2.jsonl"
            rows1 = self._submission(
                packet1, manifest, reviewer="reviewer-a", review_pass=1
            )
            rows2 = self._submission(
                packet2, manifest, reviewer="reviewer-b", review_pass=2
            )
            self._change_first_link_to_null(rows2)
            _write_jsonl(raw1, rows1)
            _write_jsonl(raw2, rows2)
            pass1 = root / "pass1.jsonl"
            pass2 = root / "pass2.jsonl"
            ingest_review_pass(
                review_pass=1,
                packet_path=packet1,
                packet_manifest_path=manifest,
                submission_path=raw1,
                output_path=pass1,
            )
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=manifest,
                submission_path=raw2,
                output_path=pass2,
            )
            comparison = root / "comparison.jsonl"
            compare_review_files(
                pass1_path=pass1,
                pass2_path=pass2,
                output_path=comparison,
            )
            normalized1 = [
                json.loads(line)
                for line in pass1.read_text(encoding="utf-8").splitlines()
            ]
            adjudicated = [
                dict(row)
                for row in normalized1
                if row.get("original_token_id") == "cc0:orig:1"
                or (
                    row.get("record_type") == "target_accounting"
                    and row.get("linked_original_token_ids") == ["cc0:orig:1"]
                )
            ]
            for index, row in enumerate(adjudicated, 1):
                row["reviewer_id"] = "adjudicator-c"
                row["evidence"] = [
                    {
                        "kind": "manual_adjudication",
                        "evidence_id": f"cc0:adjudication:{index}",
                    }
                ]
                row["rationale"] = "Independent CC0 adjudication rationale."
            adjudication = root / "adjudication.jsonl"
            adjudication_header = {
                "record_type": "adjudication_shard_metadata",
                "status": "complete_manual_adjudication_shard",
                "adjudicator_id": "adjudicator-c",
                "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
                "comparison_sha256": _sha(comparison),
                "pass_1_sha256": _sha(pass1),
                "pass_2_sha256": _sha(pass2),
            }
            _write_jsonl(adjudication, [adjudication_header, *adjudicated])
            adjudication_sidecar = Path(str(adjudication) + ".manifest.json")
            adjudication_sidecar.write_text(
                stable_json(
                    {
                        "status": "complete_manual_adjudication_shard",
                        "input_sha256": {
                            "review_pass_1": _sha(pass1),
                            "review_pass_2": _sha(pass2),
                            "comparison": _sha(comparison),
                        },
                        "output_sha256": {adjudication.name: _sha(adjudication)},
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )

            agreed_original = next(
                dict(row)
                for row in normalized1
                if row.get("original_token_id") == "cc0:orig:7"
            )
            agreed_target = next(
                dict(row)
                for row in normalized1
                if row.get("record_type") == "target_accounting"
                and row.get("target_token_id") == "cc0:uk:7"
            )
            original_key = "original:" + str(agreed_original["decision_id"])
            target_key = "target:" + str(agreed_target["accounting_id"])
            unchanged_target = next(
                row
                for row in normalized1
                if row.get("record_type") == "target_accounting"
                and row.get("target_token_id") == "cc0:uk:2"
            )
            unchanged_target_key = (
                "target:" + str(unchanged_target["accounting_id"])
            )
            qc_input_sha256 = {
                "review_pass_1": _sha(pass1),
                "review_pass_1_manifest": _sha(
                    Path(str(pass1) + ".manifest.json")
                ),
                "review_pass_2": _sha(pass2),
                "review_pass_2_manifest": _sha(
                    Path(str(pass2) + ".manifest.json")
                ),
                "comparison": _sha(comparison),
                "comparison_manifest": _sha(
                    Path(str(comparison) + ".manifest.json")
                ),
                "adjudication": _sha(adjudication),
                "adjudication_manifest": _sha(adjudication_sidecar),
            }
            blocking_qc = root / "blocking-qc.jsonl"
            _write_jsonl(
                blocking_qc,
                [
                    {
                        "record_type": "qc_metadata",
                        "status": "complete_qc_errors_found",
                        "overall_verdict": "error",
                        "shard_blocked": True,
                        "reviewer_id": "qc-reviewer-d",
                        "input_sha256": qc_input_sha256,
                    },
                    {
                        "record_type": "qc_adjudication_result",
                        "stable_key": target_key,
                        "verdict": "error",
                    },
                ],
            )
            qc_manifest = {
                "status": "complete_qc_errors_found",
                "overall_verdict": "error",
                "shard_blocked": True,
                "reviewer_id": "qc-reviewer-d",
                "input_sha256": qc_input_sha256,
                "output_sha256": {blocking_qc.name: _sha(blocking_qc)},
                "correction_proposals": [
                    {
                        "proposal_only_no_mutation_performed": True,
                        "required_workflow": (
                            "separate_fail_closed_consensus_correction"
                        ),
                        "target_ref": "Gen.1.1",
                        "rows_requiring_semantic_change": [
                            original_key,
                            target_key,
                        ],
                        "verse_local_rows_to_revalidate": [
                            original_key,
                            target_key,
                            unchanged_target_key,
                        ],
                        "unchanged_reciprocal_row_to_revalidate": (
                            unchanged_target_key
                        ),
                    }
                ],
                "verdict_stable_keys": {"error": [target_key]},
            }
            qc_sidecar = Path(str(blocking_qc) + ".manifest.json")
            qc_sidecar.write_text(
                stable_json(qc_manifest) + "\n",
                encoding="utf-8",
                newline="\n",
            )

            corrected_original = dict(agreed_original)
            corrected_original.update(
                {
                    "relation": "one_to_one",
                    "target_token_ids": ["cc0:uk:7"],
                    "null_reason": None,
                }
            )
            corrected_target = dict(agreed_target)
            corrected_target.update(
                {
                    "target_status": "aligned",
                    "linked_original_token_ids": ["cc0:orig:7"],
                }
            )
            for index, row in enumerate(
                (corrected_original, corrected_target), 1
            ):
                row["schema_version"] = 1
                row["contract_version"] = CONTRACT_VERSION
                row["gold_workflow_version"] = (
                    "ukrainian-stage-7-gold-workflow-v2"
                )
                row["reviewer_id"] = "correction-reviewer-e"
                row["evidence"] = [
                    {
                        "kind": "manual_consensus_correction",
                        "evidence_id": f"cc0:correction:{index}",
                    }
                ]
                row["rationale"] = "Independent CC0 correction rationale."
                base = agreed_original if index == 1 else agreed_target
                if base["record_type"] == "original_decision":
                    base_alignment = {
                        "record_type": "original_decision",
                        "decision_status": base["decision_status"],
                        "decision_id": base["decision_id"],
                        "original_token_id": base["original_token_id"],
                        "target_ref": base["target_ref"],
                        "relation": base["relation"],
                        "group_original_token_ids": base[
                            "group_original_token_ids"
                        ],
                        "target_token_ids": base["target_token_ids"],
                        "null_reason": base["null_reason"],
                    }
                else:
                    base_alignment = {
                        "record_type": "target_accounting",
                        "decision_status": base["decision_status"],
                        "accounting_id": base["accounting_id"],
                        "target_token_id": base["target_token_id"],
                        "target_ref": base["target_ref"],
                        "target_status": base["target_status"],
                        "linked_original_token_ids": base[
                            "linked_original_token_ids"
                        ],
                    }
                row["supersedes_alignment_sha256"] = sha256_text(
                    stable_json(base_alignment)
                )
            expected_keys = sorted([original_key, target_key])
            correction_header = {
                "schema_version": 1,
                "contract_version": CONTRACT_VERSION,
                "gold_workflow_version": "ukrainian-stage-7-gold-workflow-v2",
                "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
                "correction_version": "ukrainian-stage-7-consensus-correction-v1",
                "record_type": "consensus_correction_metadata",
                "status": (
                    "complete_manual_consensus_correction_pending_independent_qc"
                ),
                "correction_reviewer_id": "correction-reviewer-e",
                "pass_1_sha256": _sha(pass1),
                "pass_1_manifest_sha256": _sha(
                    Path(str(pass1) + ".manifest.json")
                ),
                "pass_2_sha256": _sha(pass2),
                "pass_2_manifest_sha256": _sha(
                    Path(str(pass2) + ".manifest.json")
                ),
                "comparison_sha256": _sha(comparison),
                "comparison_manifest_sha256": _sha(
                    Path(str(comparison) + ".manifest.json")
                ),
                "adjudication_sha256": _sha(adjudication),
                "adjudication_manifest_sha256": _sha(adjudication_sidecar),
                "blocking_qc_sha256": _sha(blocking_qc),
                "blocking_qc_manifest_sha256": _sha(qc_sidecar),
                "expected_changed_stable_keys": expected_keys,
                "expected_changed_stable_keys_sha256": sha256_text(
                    stable_json(expected_keys)
                ),
            }
            correction = root / "correction.jsonl"
            good_rows = [correction_header, corrected_original, corrected_target]
            _write_jsonl(correction, good_rows)
            sealed = seal_consensus_correction_shard(
                pass1_path=pass1,
                pass2_path=pass2,
                comparison_path=comparison,
                adjudication_path=adjudication,
                blocking_qc_path=blocking_qc,
                correction_path=correction,
            )
            self.assertEqual(
                sealed["status"],
                "valid_complete_manual_consensus_correction_pending_independent_qc",
            )
            self.assertEqual(sealed["processed_count"], 2)
            self.assertEqual(sealed["counts"]["stable_decisions_after_correction"], 14)
            correction_sidecar = Path(str(correction) + ".manifest.json")
            first_sidecar_bytes = correction_sidecar.read_bytes()
            resealed = seal_consensus_correction_shard(
                pass1_path=pass1,
                pass2_path=pass2,
                comparison_path=comparison,
                adjudication_path=adjudication,
                blocking_qc_path=blocking_qc,
                correction_path=correction,
            )
            self.assertEqual(resealed, sealed)
            self.assertEqual(correction_sidecar.read_bytes(), first_sidecar_bytes)

            base_values = {
                (
                    "original:" + str(row["decision_id"])
                    if row.get("record_type") == "original_decision"
                    else "target:" + str(row["accounting_id"])
                ): dict(row)
                for row in normalized1
                if row.get("record_type") != "review_metadata"
            }
            for row in adjudicated:
                stable_key = (
                    "original:" + str(row["decision_id"])
                    if row["record_type"] == "original_decision"
                    else "target:" + str(row["accounting_id"])
                )
                base_values[stable_key] = row
            base_values[original_key] = corrected_original
            base_values[target_key] = corrected_target
            adjudication_keys = [
                (
                    "original:" + str(row["decision_id"])
                    if row["record_type"] == "original_decision"
                    else "target:" + str(row["accounting_id"])
                )
                for row in adjudicated
            ]
            correction_keys = [original_key, target_key]
            final_qc_reviewer = "final-qc-reviewer-f"
            qc_version = (
                "ukrainian-stage-7-post-consensus-correction-content-qc-v1"
            )
            pass1_metadata = normalized1[0]
            pass2_metadata = json.loads(
                pass2.read_text(encoding="utf-8").splitlines()[0]
            )
            final_qc_inputs = {
                "review_pass_1": _sha(pass1),
                "review_pass_1_manifest": _sha(
                    Path(str(pass1) + ".manifest.json")
                ),
                "review_pass_2": _sha(pass2),
                "review_pass_2_manifest": _sha(
                    Path(str(pass2) + ".manifest.json")
                ),
                "comparison": _sha(comparison),
                "comparison_manifest": _sha(
                    Path(str(comparison) + ".manifest.json")
                ),
                "adjudication": _sha(adjudication),
                "adjudication_manifest": _sha(adjudication_sidecar),
                "blocking_qc": _sha(blocking_qc),
                "blocking_qc_manifest": _sha(qc_sidecar),
                "consensus_correction": _sha(correction),
                "consensus_correction_manifest": _sha(correction_sidecar),
                "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
            }
            for qc_key, source_key in (
                ("ukrainian_token_inventory", "ukrainian_token_inventory"),
                ("original_token_universe", "original_token_universe"),
            ):
                if source_key in pass1_metadata["input_sha256"]:
                    final_qc_inputs[qc_key] = pass1_metadata["input_sha256"][
                        source_key
                    ]
            for qc_key, metadata_key in (
                ("answer_free_compact_template", "compact_template_sha256"),
                ("answer_free_compact_manifest", "compact_manifest_sha256"),
            ):
                if metadata_key in pass2_metadata:
                    final_qc_inputs[qc_key] = pass2_metadata[metadata_key]
            final_qc_header = {
                "schema_version": 1,
                "contract_version": CONTRACT_VERSION,
                "gold_workflow_version": "ukrainian-stage-7-gold-workflow-v2",
                "comparison_version": "ukrainian-stage-7-gold-comparison-v1",
                "correction_version": "ukrainian-stage-7-consensus-correction-v1",
                "qc_version": qc_version,
                "record_type": "qc_metadata",
                "status": (
                    "complete_independent_post_consensus_correction_qc_accepted"
                ),
                "overall_verdict": "accepted",
                "shard_blocked": False,
                "reviewer_id": final_qc_reviewer,
                "input_sha256": final_qc_inputs,
                "structural_checks": {
                    "full_final_grid_semantic_accounting_valid": True,
                    "no_cross_verse_or_dangling_links": True,
                },
            }

            def qc_observation(
                record_type: str, stable_key: str
            ) -> dict[str, object]:
                row: dict[str, object] = {
                    "schema_version": 1,
                    "contract_version": CONTRACT_VERSION,
                    "gold_workflow_version": (
                        "ukrainian-stage-7-gold-workflow-v2"
                    ),
                    "comparison_version": (
                        "ukrainian-stage-7-gold-comparison-v1"
                    ),
                    "correction_version": (
                        "ukrainian-stage-7-consensus-correction-v1"
                    ),
                    "qc_version": qc_version,
                    "record_type": record_type,
                    "stable_key": stable_key,
                    "target_ref": base_values[stable_key]["target_ref"],
                    "final_semantics": _semantic_for_key(
                        base_values[stable_key]
                    ),
                    "reciprocal_accounting_checked": True,
                    "qc_rationale": "Independent CC0 final QC rationale.",
                    "reviewer_id": final_qc_reviewer,
                    "verdict": "accepted",
                }
                if record_type == "qc_final_adjudication_result":
                    row["correction_applied"] = stable_key in correction_keys
                return row

            final_qc_observations = [
                *[
                    qc_observation("qc_final_adjudication_result", key)
                    for key in adjudication_keys
                ],
                *[
                    qc_observation(
                        "qc_final_consensus_correction_result", key
                    )
                    for key in correction_keys
                ],
                qc_observation(
                    "qc_final_revalidate_only_result", unchanged_target_key
                ),
            ]
            unique_qc_keys = {
                *adjudication_keys,
                *correction_keys,
                unchanged_target_key,
            }
            final_qc_counts = {
                "accepted_observations": len(final_qc_observations),
                "adjudication_rows_rechecked": len(adjudication_keys),
                "correction_rows_checked": len(correction_keys),
                "error_observations": 0,
                "full_final_grid_original_decisions": sum(
                    key.startswith("original:") for key in base_values
                ),
                "full_final_grid_stable_decisions": len(base_values),
                "full_final_grid_target_accounting": sum(
                    key.startswith("target:") for key in base_values
                ),
                "observation_count": len(final_qc_observations),
                "qc_jsonl_lines": len(final_qc_observations) + 1,
                "revalidate_only_rows_checked": 1,
                "uncertain_observations": 0,
                "unique_original_decisions_checked": sum(
                    key.startswith("original:") for key in unique_qc_keys
                ),
                "unique_stable_keys_checked": len(unique_qc_keys),
                "unique_target_accounting_checked": sum(
                    key.startswith("target:") for key in unique_qc_keys
                ),
            }
            final_qc = root / "final-qc.jsonl"
            _write_jsonl(
                final_qc, [final_qc_header, *final_qc_observations]
            )
            final_qc_sidecar = Path(str(final_qc) + ".manifest.json")
            final_qc_manifest = {
                **{
                    key: value
                    for key, value in final_qc_header.items()
                    if key != "record_type"
                },
                "processed_count": len(final_qc_observations),
                "skipped_count": 0,
                "error_count": 0,
                "counts": final_qc_counts,
                "output_sha256": {final_qc.name: _sha(final_qc)},
                "adjudication_stable_keys": sorted(adjudication_keys),
                "corrected_stable_keys": sorted(correction_keys),
                "revalidated_unchanged_stable_keys": [unchanged_target_key],
                "verdict_stable_keys": {
                    "accepted": sorted(unique_qc_keys),
                    "error": [],
                    "uncertain": [],
                },
            }
            final_qc_sidecar.write_text(
                stable_json(final_qc_manifest) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            accepted_qc = validate_post_consensus_correction_qc(
                pass1_path=pass1,
                pass2_path=pass2,
                comparison_path=comparison,
                adjudication_path=adjudication,
                blocking_qc_path=blocking_qc,
                correction_path=correction,
                final_qc_path=final_qc,
            )
            self.assertEqual(accepted_qc["processed_count"], 5)
            self.assertEqual(accepted_qc["error_count"], 0)

            tampered_observations = json.loads(
                json.dumps(final_qc_observations)
            )
            tampered_observations[0]["final_semantics"]["relation"] = (
                "original_omitted"
            )
            _write_jsonl(
                final_qc, [final_qc_header, *tampered_observations]
            )
            with self.assertRaisesRegex(ValueError, "semantics differ"):
                validate_post_consensus_correction_qc(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    final_qc_path=final_qc,
                )

            colliding_header = dict(final_qc_header)
            colliding_header["reviewer_id"] = "reviewer-a"
            _write_jsonl(
                final_qc, [colliding_header, *final_qc_observations]
            )
            with self.assertRaisesRegex(ValueError, "independence"):
                validate_post_consensus_correction_qc(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    final_qc_path=final_qc,
                )

            _write_jsonl(correction, [correction_header, corrected_original])
            with self.assertRaisesRegex(ValueError, "exact QC scope"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )
            unchanged_original = dict(corrected_original)
            unchanged_original.update(
                {
                    "relation": agreed_original["relation"],
                    "target_token_ids": agreed_original["target_token_ids"],
                    "null_reason": agreed_original["null_reason"],
                }
            )
            _write_jsonl(
                correction,
                [correction_header, unchanged_original, corrected_target],
            )
            with self.assertRaisesRegex(ValueError, "does not change"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )
            dangling_target = dict(corrected_target)
            dangling_target["linked_original_token_ids"] = ["cc0:orig:6"]
            _write_jsonl(
                correction,
                [correction_header, corrected_original, dangling_target],
            )
            with self.assertRaisesRegex(ValueError, "accounting disagrees"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )
            stale_header = dict(correction_header)
            stale_header["blocking_qc_sha256"] = "0" * 64
            _write_jsonl(
                correction,
                [stale_header, corrected_original, corrected_target],
            )
            with self.assertRaisesRegex(ValueError, "SHA locks differ"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )
            extra = dict(corrected_original)
            extra["decision_id"] = "gold7:original:unscoped"
            _write_jsonl(
                correction,
                [correction_header, corrected_original, corrected_target, extra],
            )
            with self.assertRaisesRegex(ValueError, "unscoped or duplicate"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )
            colliding_header = dict(correction_header)
            colliding_header["correction_reviewer_id"] = "reviewer-a"
            colliding_original = dict(corrected_original)
            colliding_target = dict(corrected_target)
            colliding_original["reviewer_id"] = "reviewer-a"
            colliding_target["reviewer_id"] = "reviewer-a"
            _write_jsonl(
                correction,
                [colliding_header, colliding_original, colliding_target],
            )
            with self.assertRaisesRegex(ValueError, "independence"):
                validate_consensus_correction_shard(
                    pass1_path=pass1,
                    pass2_path=pass2,
                    comparison_path=comparison,
                    adjudication_path=adjudication,
                    blocking_qc_path=blocking_qc,
                    correction_path=correction,
                    require_sidecar=False,
                )

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

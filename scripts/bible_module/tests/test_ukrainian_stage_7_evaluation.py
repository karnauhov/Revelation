from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_evaluation import (
    DETAILS_FILENAME,
    MANIFEST_FILENAME,
    evaluate_candidate_artifacts,
)
from scripts.bible_module.ukrainian_stage_7_gold import (
    GOLD_WORKFLOW_VERSION,
    PRODUCTION_PACKET_INPUT_KEYS,
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
    / "evaluation_cases.json"
)


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class FrozenGoldCandidateEvaluationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _inputs(
        self,
        root: Path,
        *,
        candidates: list[dict[str, object]] | None = None,
        production_lock: bool = False,
    ) -> tuple[Path, Path, Path, Path]:
        token_inventory = root / "target.jsonl"
        original_universe = root / "original.jsonl"
        candidate_path = root / "candidates.jsonl"
        _write_jsonl(token_inventory, self.fixture["target_tokens"])
        _write_jsonl(original_universe, self.fixture["original_tokens"])
        _write_jsonl(
            candidate_path,
            candidates if candidates is not None else self.fixture["candidates"],
        )

        gold_rows: list[dict[str, object]] = []
        target_accounted: set[str] = set()
        for edge in self.fixture["gold_hyperedges"]:
            gold_rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                    "record_type": "hyperedge",
                    "status": "reviewed_accepted",
                    **edge,
                }
            )
            for original_id in edge["original_token_ids"]:
                gold_rows.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "contract_version": CONTRACT_VERSION,
                        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                        "record_type": "original_decision",
                        "decision_id": "cc0:decision:" + original_id,
                        "original_token_id": original_id,
                        "edge_id": edge["edge_id"],
                        "target_ref": edge["target_ref"],
                        "severity": edge["severity"],
                        "phenomena": edge["phenomena"],
                        "status": "reviewed_accepted",
                    }
                )
            for target_id in edge["target_token_ids"]:
                if target_id in target_accounted:
                    continue
                target_accounted.add(target_id)
                gold_rows.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "contract_version": CONTRACT_VERSION,
                        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                        "record_type": "target_accounting",
                        "accounting_id": "cc0:accounting:" + target_id,
                        "target_token_id": target_id,
                        "target_ref": edge["target_ref"],
                        "target_status": (
                            "aligned"
                            if edge["original_token_ids"]
                            else edge["null_reason"]
                        ),
                        "severity": edge["severity"],
                        "phenomena": edge["phenomena"],
                        "status": "reviewed_accepted",
                    }
                )

        gold_report = root / "gold-report"
        gold_report.mkdir()
        annotations = gold_report / "gold_alignment.annotations.jsonl"
        manifest_path = gold_report / "gold_alignment.manifest.json"
        _write_jsonl(annotations, gold_rows)
        lock_inputs = (
            {
                **{key: "a" * 64 for key in PRODUCTION_PACKET_INPUT_KEYS},
                "ukrainian_token_inventory": _sha(token_inventory),
                "gold_selected_original_layer": _sha(original_universe),
            }
            if production_lock
            else {}
        )
        corpus_contract = (
            "ohienko_1988_production" if production_lock else "cc0_fixture"
        )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "corpus_contract": corpus_contract,
            "artifact": "gold_alignment",
            "status": "finalized_reviewed_gold",
            "input_sha256": lock_inputs,
            "output_sha256": {
                annotations.name: _sha(annotations),
                "gold_selected_original_layer.jsonl": _sha(original_universe),
            },
            "processed_count": len(gold_rows),
            "skipped_count": 0,
            "error_count": 0,
        }
        _write_json(manifest_path, manifest)
        lock = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "corpus_contract": corpus_contract,
            "status": "finalized_reviewed_gold",
            "artifact_sha256": _sha(annotations),
            "manifest_sha256": _sha(manifest_path),
            "input_sha256": lock_inputs,
            "processed_count": len(gold_rows),
            "skipped_count": 0,
            "error_count": 0,
        }
        _write_json(gold_report / "gold_alignment.finalized.lock.json", lock)
        return gold_report, token_inventory, original_universe, candidate_path

    def _evaluate(
        self,
        root: Path,
        *,
        output_name: str,
        folds: set[int],
        candidates: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        gold, target, original, candidate = self._inputs(
            root, candidates=candidates
        )
        return evaluate_candidate_artifacts(
            gold_report_dir=gold,
            token_inventory_path=target,
            original_universe_path=original,
            candidate_inputs={"cc0": candidate},
            output_dir=root / output_name,
            evaluation_folds=folds,
        )

    def test_exact_many_to_many_nonexact_partial_and_null_edges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._evaluate(root, output_name="out", folds={4})
            metrics = manifest["generator_metrics"]["cc0-generator-v1"]
            self.assertEqual(metrics["candidate_count"], 4)
            self.assertEqual(metrics["exact_match_count"], 3)
            self.assertEqual(metrics["nonmatch_count"], 1)
            self.assertEqual(metrics["exact_precision"], 0.75)
            self.assertTrue(manifest["candidate_only"])
            self.assertFalse(manifest["threshold_tuning_performed"])
            self.assertFalse(manifest["automatic_promotion_performed"])
            rows = [
                json.loads(line)
                for line in (root / "out" / DETAILS_FILENAME)
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            by_id = {row["candidate_id"]: row for row in rows}
            self.assertTrue(by_id["cc0:candidate:exact-many"]["exact_match"])
            self.assertFalse(by_id["cc0:candidate:partial-many"]["exact_match"])
            self.assertTrue(by_id["cc0:candidate:exact-omitted"]["exact_match"])
            self.assertTrue(by_id["cc0:candidate:exact-addition"]["exact_match"])
            self.assertEqual(
                metrics["stratum_metrics"]["genre"]["torah_prose_law"][
                    "candidate_count"
                ],
                4,
            )
            self.assertEqual(
                metrics["stratum_metrics"]["severity"]["high"][
                    "candidate_count"
                ],
                2,
            )
            self.assertEqual(
                metrics["stratum_metrics"]["phenomenon"]["compound"][
                    "candidate_count"
                ],
                2,
            )
            self.assertEqual(
                by_id["cc0:candidate:exact-many"]["raw_generator_score"],
                {"calibrated": False, "name": "fixture-many", "value": 0.91},
            )
            self.assertTrue(all(row["candidate_only"] for row in rows))

    def test_legacy_correct_incorrect_and_ambiguous_are_separate_zero_vote(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._evaluate(root, output_name="out", folds={4})
            metrics = manifest["generator_metrics"]["legacy-zero-vote-v1"]
            self.assertEqual(metrics["correct_occurrences"], 1)
            self.assertEqual(metrics["incorrect_occurrences"], 1)
            self.assertEqual(metrics["ambiguous_occurrences"], 1)
            self.assertEqual(metrics["strict_precision"], 1 / 3)
            self.assertTrue(metrics["zero_vote_enforced"])
            self.assertFalse(metrics["ambiguous_counted_as_correct"])
            self.assertEqual(metrics["fold_metrics"]["4"]["occurrence_count"], 3)
            self.assertEqual(
                metrics["stratum_metrics"]["testament"]["OT"]["occurrence_count"],
                3,
            )
            rows = [
                json.loads(line)
                for line in (root / "out" / DETAILS_FILENAME)
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            legacy = {
                row["candidate_id"]: row["legacy_occurrences"][0]["legacy_status"]
                for row in rows
                if row["generator_id"] == "legacy-zero-vote-v1"
            }
            self.assertEqual(
                legacy,
                {
                    "cc0:candidate:legacy-ambiguous": "ambiguous",
                    "cc0:candidate:legacy-correct": "correct",
                    "cc0:candidate:legacy-incorrect": "incorrect",
                },
            )

    def test_sealed_fold_is_isolated_and_unsealed_run_reads_only_its_fold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gold, target, original, candidate = self._inputs(root)
            with self.assertRaisesRegex(ValueError, "isolation"):
                evaluate_candidate_artifacts(
                    gold_report_dir=gold,
                    token_inventory_path=target,
                    original_universe_path=original,
                    candidate_inputs={"cc0": candidate},
                    output_dir=root / "mixed",
                    evaluation_folds={3, 4},
                )
            manifest = evaluate_candidate_artifacts(
                gold_report_dir=gold,
                token_inventory_path=target,
                original_universe_path=original,
                candidate_inputs={"cc0": candidate},
                output_dir=root / "unsealed",
                evaluation_folds={3},
            )
            self.assertEqual(manifest["evaluation_scope"], "unsealed_folds_only")
            self.assertEqual(manifest["evaluation_folds"], [3])
            self.assertEqual(manifest["processed_count"], 1)
            details = (root / "unsealed" / DETAILS_FILENAME).read_text(
                encoding="utf-8"
            )
            self.assertIn("cc0:candidate:unsealed", details)
            self.assertNotIn("cc0:candidate:exact-many", details)

    def test_stale_ids_and_duplicate_candidates_fail_closed_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = [dict(row) for row in self.fixture["candidates"]]
            duplicate.insert(1, dict(duplicate[0]))
            gold, target, original, candidate = self._inputs(
                root, candidates=duplicate
            )
            with self.assertRaisesRegex(ValueError, "Duplicate candidate ID"):
                evaluate_candidate_artifacts(
                    gold_report_dir=gold,
                    token_inventory_path=target,
                    original_universe_path=original,
                    candidate_inputs={"cc0": candidate},
                    output_dir=root / "duplicate-out",
                    evaluation_folds={4},
                )
            self.assertFalse((root / "duplicate-out").exists())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stale = [dict(row) for row in self.fixture["candidates"]]
            stale[0] = {
                **stale[0],
                "original_token_ids": ["cc0:orig:missing"],
                "strong_classic": ["H1"],
            }
            gold, target, original, candidate = self._inputs(root, candidates=stale)
            with self.assertRaisesRegex(ValueError, "stale"):
                evaluate_candidate_artifacts(
                    gold_report_dir=gold,
                    token_inventory_path=target,
                    original_universe_path=original,
                    candidate_inputs={"cc0": candidate},
                    output_dir=root / "stale-out",
                    evaluation_folds={4},
                )
            self.assertFalse((root / "stale-out").exists())

    def test_output_is_byte_deterministic_across_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory_a, tempfile.TemporaryDirectory() as directory_b:
            root_a = Path(directory_a)
            root_b = Path(directory_b)
            self._evaluate(root_a, output_name="out", folds={4})
            self._evaluate(root_b, output_name="out", folds={4})
            for filename in (DETAILS_FILENAME, MANIFEST_FILENAME):
                self.assertEqual(
                    (root_a / "out" / filename).read_bytes(),
                    (root_b / "out" / filename).read_bytes(),
                )

    def test_production_gold_rejects_stale_selected_or_target_layer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gold, target, original, candidate = self._inputs(
                root, production_lock=True
            )
            original.write_text(
                original.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                ValueError, "Selected original layer differs from frozen gold"
            ):
                evaluate_candidate_artifacts(
                    gold_report_dir=gold,
                    token_inventory_path=target,
                    original_universe_path=original,
                    candidate_inputs={"cc0": candidate},
                    output_dir=root / "stale-original",
                    evaluation_folds={4},
                )
            self.assertFalse((root / "stale-original").exists())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gold, target, original, candidate = self._inputs(
                root, production_lock=True
            )
            target.write_text(
                target.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                ValueError, "Target token inventory differs from frozen gold"
            ):
                evaluate_candidate_artifacts(
                    gold_report_dir=gold,
                    token_inventory_path=target,
                    original_universe_path=original,
                    candidate_inputs={"cc0": candidate},
                    output_dir=root / "stale-target",
                    evaluation_folds={4},
                )
            self.assertFalse((root / "stale-target").exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

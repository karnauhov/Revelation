"""CC0 regression coverage for the deferral-aware evaluation consumer."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.bible_module import ukrainian_stage_7_evaluation_v2 as evaluation
from scripts.bible_module.ukrainian_stage_7_model import stable_json

FIXTURE = Path(__file__).parent / "fixtures/ukrainian_stage_7/evaluation_cases.json"


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(stable_json(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


class DeferralAwareEvaluationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    @contextmanager
    def inputs(self, *, candidates=None, deferred=True, mutate_gold=None, mutate_mask=None):
        """Gold's own lock validator has separate tests; exercise its consumer."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report"
            report.mkdir()
            target, original, candidate = root / "target.jsonl", root / "original.jsonl", root / "candidates.jsonl"
            write_rows(target, self.fixture["target_tokens"])
            write_rows(original, self.fixture["original_tokens"])
            write_rows(candidate, deepcopy(self.fixture["candidates"] if candidates is None else candidates))
            rows, mask = [], []
            for edge in self.fixture["gold_hyperedges"]:
                is_deferred = deferred and edge["edge_id"] == "cc0:gold:sealed:many"
                if not is_deferred:
                    rows.append({"record_type": "hyperedge", "status": "reviewed_accepted", **edge})
                for side, tokens in (("original", edge["original_token_ids"]), ("target", edge["target_token_ids"])):
                    for token in tokens:
                        id_field = "decision_id" if side == "original" else "accounting_id"
                        identity = "cc0:" + id_field + ":" + token
                        key = side + ":" + identity
                        mask.append({"record_type": "gold_eligibility", "stable_key": key,
                                     side + "_token_id": token, "target_ref": edge["target_ref"],
                                     "eligible": not is_deferred, "issue_ids": ["cc0:issue:one"] if is_deferred else [],
                                     "frozen_decision_sha256": "a" * 64})
                        if is_deferred:
                            rows.append({"record_type": "deferred_original_decision" if side == "original" else "deferred_target_accounting",
                                         "stable_key": key, side + "_token_id": token, "target_ref": edge["target_ref"],
                                         "status": "deferred_strong_unassigned", "strong_assignment": None})
                        elif side == "original":
                            rows.append({"record_type": "original_decision", "status": "reviewed_accepted", id_field: identity,
                                         "original_token_id": token, "target_ref": edge["target_ref"],
                                         "edge_id": edge["edge_id"], "relation": edge["relation"],
                                         "group_original_token_ids": edge["original_token_ids"], "target_token_ids": edge["target_token_ids"],
                                         "null_reason": edge["null_reason"], "severity": edge["severity"], "phenomena": edge["phenomena"]})
                        else:
                            rows.append({"record_type": "target_accounting", "status": "reviewed_accepted", id_field: identity,
                                         "target_token_id": token, "target_ref": edge["target_ref"],
                                         "target_status": "aligned" if edge["original_token_ids"] else edge["null_reason"],
                                         "linked_original_token_ids": edge["original_token_ids"],
                                         "severity": edge["severity"], "phenomena": edge["phenomena"]})
            if mutate_gold:
                mutate_gold(rows)
            if mutate_mask:
                mutate_mask(mask)
            annotation = report / evaluation.ANNOTATIONS_FILENAME
            eligibility = report / evaluation.ELIGIBILITY_FILENAME
            write_rows(annotation, rows)
            write_rows(eligibility, mask)
            lock = {"input_sha256": {"ukrainian_token_inventory": evaluation.strict._sha256_file(target),
                                     "gold_selected_original_layer": evaluation.strict._sha256_file(original)},
                    "output_sha256": {annotation.name: evaluation.strict._sha256_file(annotation),
                                      eligibility.name: evaluation.strict._sha256_file(eligibility)}}
            evaluation.strict._write_json(report / evaluation.LOCK_FILENAME, lock)
            common = dict(gold_report_dir=report, token_inventory_path=target, original_universe_path=original,
                          candidate_inputs={"cc0": candidate})
            with patch.object(evaluation, "_validated_gold", return_value=lock):
                pipeline = root / "pipeline.json"
                evaluation.freeze_evaluation_pipeline(**common, output_path=pipeline)
                yield root, common, pipeline

    def evaluate(self, root, common, pipeline, *, folds=(0, 1, 2, 3), name="unsealed", predecessor=None):
        return evaluation.evaluate_candidate_artifacts(**common, frozen_pipeline_path=pipeline,
            output_dir=root / name, evaluation_folds=folds, unsealed_manifest_path=predecessor)

    def sealed(self, root, common, pipeline):
        self.evaluate(root, common, pipeline)
        return self.evaluate(root, common, pipeline, folds=(4,), name="sealed",
                             predecessor=root / "unsealed" / evaluation.MANIFEST_FILENAME)

    def overlap_gold(self, rows):
        """Two declared source groups legitimately share the target span."""
        edge = next(row for row in rows if row["record_type"] == "hyperedge" and row["edge_id"] == "cc0:gold:sealed:many")
        rows.remove(edge)
        for number, original in enumerate(edge["original_token_ids"], 1):
            edge_id = "cc0:gold:overlap:" + str(number)
            rows.append({**edge, "edge_id": edge_id, "relation": "one_to_many", "original_token_ids": [original]})
            row = next(row for row in rows if row["record_type"] == "original_decision" and row["original_token_id"] == original)
            row.update(edge_id=edge_id, relation="one_to_many", group_original_token_ids=[original],
                       derived_source_strata={"frequency_classes": ["frequent_lemma" if number == 1 else "rare_lemma"],
                           "frequency_evidence": [], "proof_sha256": "a" * 64,
                           "basis": "frozen_primary_universe_classic_frequency", "source_frequency_is_strong_assignment": False})

    def test_whole_mixed_hyperedge_excluded_and_does_not_affect_denominators(self):
        mixed = deepcopy(self.fixture["candidates"][0])
        mixed.update(candidate_id="cc0:mixed", relation="one_to_many",
                     original_token_ids=["cc0:orig:sealed:3"],
                     target_token_ids=["cc0:uk:sealed:2", "cc0:uk:sealed:3"], strong_classic=["H2"])
        with self.inputs(candidates=self.fixture["candidates"] + [mixed]) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            metric = result["generator_metrics"]["cc0-generator-v1"]
            self.assertEqual((metric["true_positive"], metric["false_positive"], metric["false_negative"]), (2, 0, 1))
            self.assertEqual(metric["precision_denominator_tp_plus_fp"], 2)
            self.assertEqual(metric["recall_denominator_tp_plus_fn"], 3)
            self.assertEqual(result["excluded_from_all_metrics"]["cc0-generator-v1"]["candidate_rows"], 3)
            self.assertEqual(result["coverage"]["original_link_null_decisions"],
                             {"full": 4, "eligible_proven": 2, "deferred_excluded": 2, "proven_coverage": .5})
            rows = [json.loads(line) for line in (root / "sealed" / evaluation.DETAILS_FILENAME).read_text(encoding="utf-8").splitlines()]
            detail = next(row for row in rows if row["candidate_id"] == "cc0:mixed")
            self.assertFalse(detail["contributes_to_tp_fp_fn_or_support"])
            self.assertNotIn("exact_match", detail)
            self.assertNotIn("raw_generator_score", detail)

    def test_deferred_label_metadata_cannot_leak_into_statistics(self):
        def inject(rows):
            for row in rows:
                if row["record_type"].startswith("deferred_"):
                    row.update(severity="critical", phenomena=["DEFERRED_LABEL_LEAK"])
        with self.inputs(mutate_gold=inject) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            serialized = stable_json(result)
            self.assertNotIn("DEFERRED_LABEL_LEAK", serialized)
            self.assertNotIn("critical", serialized)
            legacy = result["generator_metrics"]["legacy-zero-vote-v1"]
            self.assertEqual(legacy["unique_occurrence_count"], 2)
            self.assertEqual(legacy["ambiguous_occurrences"], 0)
            self.assertEqual(result["excluded_from_all_metrics"]["legacy-zero-vote-v1"]["legacy_strong_occurrences"], 1)

    def test_derived_fixed_source_frequency_is_separate_and_masked_before_statistics(self):
        def source_metadata(rows):
            for row in rows:
                if row["record_type"] == "original_decision" and row["original_token_id"] == "cc0:orig:sealed:4":
                    row["derived_source_strata"] = {"frequency_classes": ["frequent_lemma"],
                        "frequency_evidence": [{"strong_classic": "H4", "primary_universe_frequency": 1200,
                                                "frequency_band": "frequent_1000_plus"}],
                        "proof_sha256": "a" * 64, "basis": "frozen_primary_universe_classic_frequency",
                        "source_frequency_is_strong_assignment": False}
                elif row["record_type"].startswith("deferred_"):
                    # Poison proves that even parsing derived classes happens
                    # after the consumer has applied frozen eligibility.
                    row["derived_source_strata"] = "DEFERRED_SOURCE_FREQUENCY_LEAK"
        with self.inputs(mutate_gold=source_metadata) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            metric = result["generator_metrics"]["cc0-generator-v1"]
            bucket = metric["stratum_metrics"]["source_frequency"]["frequent_lemma"]
            self.assertEqual((bucket["true_positive"], bucket["eligible_gold_support"]), (1, 1))
            # The fixture already has one reviewed frequent label on a
            # different edge; derived frequency must not relabel this edge.
            reviewed = metric["stratum_metrics"]["phenomenon"]["frequent_lemma"]
            self.assertEqual((reviewed["candidate_count"], reviewed["eligible_gold_support"]), (0, 1))
            self.assertNotIn("DEFERRED_SOURCE_FREQUENCY_LEAK", stable_json(result))

    def test_legacy_gold_only_source_frequency_stratum_retains_false_negatives(self):
        def source_metadata(rows):
            for row in rows:
                if row["record_type"] == "original_decision" and row["original_token_id"] == "cc0:orig:sealed:3":
                    row["derived_source_strata"] = {"frequency_classes": ["rare_lemma"],
                        "frequency_evidence": [{"strong_classic": "H2", "primary_universe_frequency": 3,
                                                "frequency_band": "rare_1_to_5"}],
                        "proof_sha256": "a" * 64, "basis": "frozen_primary_universe_classic_frequency",
                        "source_frequency_is_strong_assignment": False}
        candidates = [row for row in self.fixture["candidates"] if row["candidate_id"] != "cc0:candidate:legacy-correct"]
        with self.inputs(candidates=candidates, mutate_gold=source_metadata) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            legacy = result["generator_metrics"]["legacy-zero-vote-v1"]
            bucket = legacy["stratum_metrics"]["source_frequency"]["rare_lemma"]
            self.assertEqual(bucket["occurrence_count"], 0)
            self.assertEqual(bucket["eligible_gold_target_original_strong_support"], 1)
            self.assertEqual((bucket["unique_true_positive"], bucket["unique_false_negative"]), (0, 1))

    def test_declared_overlapping_targets_preserve_separate_exact_edges_and_legacy_union(self):
        candidates = deepcopy(self.fixture["candidates"])
        for number in (1, 2):
            candidate = deepcopy(candidates[0])
            candidate.update(candidate_id="cc0:exact-overlap:" + str(number), relation="one_to_many",
                             original_token_ids=["cc0:orig:sealed:" + str(number)])
            candidates.append(candidate)
        with self.inputs(candidates=candidates, deferred=False, mutate_gold=self.overlap_gold) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            self.assertEqual(result["eligible_gold_hyperedges"], 5)
            metric = result["generator_metrics"]["cc0-generator-v1"]
            self.assertEqual((metric["true_positive"], metric["false_positive"], metric["false_negative"]), (4, 2, 1))
            frequency = metric["stratum_metrics"]["source_frequency"]
            self.assertEqual((frequency["frequent_lemma"]["true_positive"], frequency["frequent_lemma"]["eligible_gold_support"]), (1, 1))
            self.assertEqual((frequency["rare_lemma"]["true_positive"], frequency["rare_lemma"]["eligible_gold_support"]), (1, 1))
            legacy = result["generator_metrics"]["legacy-zero-vote-v1"]
            self.assertEqual((legacy["true_positive"], legacy["false_positive"], legacy["false_negative"]), (1, 2, 4))
            self.assertEqual(legacy["ambiguous_occurrences"], 1)
            self.assertEqual(legacy["recall_denominator_eligible_target_original_strong_triples"], 5)

    def test_overlap_reciprocal_missing_extra_or_deferred_member_is_rejected(self):
        for linked in (["cc0:orig:sealed:1"], ["cc0:orig:sealed:1", "cc0:orig:sealed:2", "cc0:orig:sealed:3"]):
            def incomplete_union(rows):
                self.overlap_gold(rows)
                next(row for row in rows if row["record_type"] == "target_accounting" and row["target_token_id"] == "cc0:uk:sealed:1")["linked_original_token_ids"] = linked
            with self.subTest(linked=linked):
                with self.inputs(deferred=False, mutate_gold=incomplete_union) as (root, common, pipeline):
                    with self.assertRaisesRegex(ValueError, "reciprocal"):
                        self.sealed(root, common, pipeline)
        def partial_deferral(mask):
            next(row for row in mask if row.get("original_token_id") == "cc0:orig:sealed:1")["eligible"] = False
        with self.inputs(deferred=False, mutate_gold=self.overlap_gold, mutate_mask=partial_deferral) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "deferred endpoint|accepted label"):
                self.sealed(root, common, pipeline)

    def test_illegal_id_in_mixed_deferred_edge_is_still_rejected(self):
        candidate = deepcopy(self.fixture["candidates"][0])
        candidate["original_token_ids"] = ["cc0:orig:sealed:1", "cc0:orig:missing"]
        with self.inputs(candidates=[candidate]) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "Stale, dangling"):
                self.sealed(root, common, pipeline)
            self.assertFalse((root / "sealed").exists())
            self.assertFalse((root / "sealed.tmp-evaluation-v3").exists())

    def test_cross_verse_id_and_duplicate_endpoint_fail_before_deferral(self):
        for original_ids, expected in ((["cc0:orig:sealed:1", "cc0:orig:unsealed:1"], "cross-verse"),
                                       (["cc0:orig:sealed:1", "cc0:orig:sealed:1"], "duplicate-free")):
            with self.subTest(original_ids=original_ids):
                candidate = deepcopy(self.fixture["candidates"][0])
                candidate["original_token_ids"] = original_ids
                with self.inputs(candidates=[candidate]) as (root, common, pipeline):
                    with self.assertRaisesRegex(ValueError, expected):
                        self.sealed(root, common, pipeline)

    def test_duplicate_candidate_id_is_not_hidden_by_exclusion(self):
        with self.inputs(candidates=[self.fixture["candidates"][0]] * 2) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "Duplicate candidate ID"):
                self.sealed(root, common, pipeline)

    def test_duplicate_semantic_predictions_are_reported_without_inflation(self):
        repeated = deepcopy(self.fixture["candidates"][2])
        repeated["candidate_id"] = "cc0:repeated"
        with self.inputs(candidates=self.fixture["candidates"] + [repeated]) as (root, common, pipeline):
            result = self.sealed(root, common, pipeline)
            metric = result["generator_metrics"]["cc0-generator-v1"]
            self.assertEqual(metric["eligible_candidate_rows"], 3)
            self.assertEqual(metric["unique_candidate_hyperedges"], 2)
            self.assertEqual(metric["duplicate_semantic_prediction_rows"], 1)
            self.assertEqual(metric["true_positive"], 2)

    def test_gold_missing_or_mismatched_reciprocal_accounting_fails(self):
        mutations = [
            lambda rows: rows.remove(next(row for row in rows if row["record_type"] == "original_decision" and row["target_ref"] == "Gen.1.3")),
            lambda rows: rows.remove(next(row for row in rows if row["record_type"] == "target_accounting" and row["target_ref"] == "Gen.1.3")),
            lambda rows: next(row for row in rows if row["record_type"] == "original_decision" and row["target_ref"] == "Gen.1.3").update(edge_id="cc0:wrong-edge"),
            lambda rows: next(row for row in rows if row["record_type"] == "target_accounting" and row["target_ref"] == "Gen.1.3" and row["target_status"] == "aligned").update(linked_original_token_ids=[]),
            lambda rows: next(row for row in rows if row["record_type"] == "hyperedge" and row["target_ref"] == "Gen.1.3").update(status="deferred_strong_unassigned"),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with self.inputs(mutate_gold=mutation) as (root, common, pipeline):
                    with self.assertRaises(ValueError):
                        self.sealed(root, common, pipeline)

    def test_gold_mixed_deferred_hyperedge_is_rejected_not_partially_scored(self):
        def inject(rows):
            rows.append({"record_type": "hyperedge", "status": "reviewed_accepted", **self.fixture["gold_hyperedges"][0]})
        with self.inputs(mutate_gold=inject) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "deferred endpoint"):
                self.sealed(root, common, pipeline)

    def test_deferred_assignment_and_duplicate_mask_are_rejected(self):
        def leak(rows):
            next(row for row in rows if row["record_type"].startswith("deferred_")).update(relation="one_to_one")
        with self.inputs(mutate_gold=leak) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "unproved assignment"):
                self.sealed(root, common, pipeline)
        for field in ("original_token_ids", "target_token_ids", "group_original_token_ids", "linked_original_token_ids", "edge_id"):
            with self.subTest(field=field):
                def leak_topology(rows):
                    next(row for row in rows if row["record_type"].startswith("deferred_")).update({field: []})
                with self.inputs(mutate_gold=leak_topology) as (root, common, pipeline):
                    with self.assertRaisesRegex(ValueError, "unproved assignment"):
                        self.sealed(root, common, pipeline)
        with self.inputs(mutate_mask=lambda rows: rows.append(rows[0])) as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "duplicate"):
                self.sealed(root, common, pipeline)

    def test_sealed_requires_frozen_matching_unsealed_predecessor(self):
        with self.inputs() as (root, common, pipeline):
            with self.assertRaisesRegex(ValueError, "completed unsealed"):
                self.evaluate(root, common, pipeline, folds=(4,), name="sealed")
            with self.assertRaisesRegex(ValueError, "isolation"):
                self.evaluate(root, common, pipeline, folds=(3, 4), name="mixed")
            self.evaluate(root, common, pipeline)
            candidate = common["candidate_inputs"]["cc0"]
            candidate.write_text(candidate.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed after pipeline freeze"):
                self.evaluate(root, common, pipeline, folds=(4,), name="changed",
                              predecessor=root / "unsealed" / evaluation.MANIFEST_FILENAME)

    def test_forged_or_missing_unsealed_details_cannot_unlock_sealed_fold(self):
        with self.inputs() as (root, common, pipeline):
            self.evaluate(root, common, pipeline)
            predecessor = root / "unsealed" / evaluation.MANIFEST_FILENAME
            original = json.loads(predecessor.read_text(encoding="utf-8"))
            forged = {key: original[key] for key in ("evaluation_folds", "frozen_pipeline_sha256", "input_specs")}
            evaluation.strict._write_json(predecessor, forged)
            with self.assertRaisesRegex(ValueError, "incomplete"):
                self.evaluate(root, common, pipeline, folds=(4,), name="forged", predecessor=predecessor)
            evaluation.strict._write_json(predecessor, original)
            (predecessor.parent / evaluation.DETAILS_FILENAME).unlink()
            with self.assertRaisesRegex(ValueError, "absent or stale"):
                self.evaluate(root, common, pipeline, folds=(4,), name="missing-details", predecessor=predecessor)

    def test_artifacts_are_byte_deterministic(self):
        outputs = []
        for _ in range(2):
            with self.inputs() as (root, common, pipeline):
                self.sealed(root, common, pipeline)
                outputs.append(tuple((root / "sealed" / name).read_bytes() for name in
                                     (evaluation.DETAILS_FILENAME, evaluation.MANIFEST_FILENAME)))
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from scripts.bible_module.ukrainian_stage_7_alignment import (
    AUTO_LOWER_BOUND,
    calibrate_auto_class,
    rank_verse_hypergraph_solutions,
    validate_complete_solution,
)


def _edge(
    edge_id: str,
    originals: list[str],
    targets: list[str],
    probability: float,
    relation: str = "one_to_one",
) -> dict[str, object]:
    return {
        "edge_id": edge_id,
        "target_ref": "Gen.1.1",
        "relation": relation,
        "original_token_ids": originals,
        "target_token_ids": targets,
        "evidence_channels": ["lexical_morphological"],
        "resolver_eligible": True,
        "calibrated_probability": probability,
        "textual_status": "resolved",
        "testament": "OT",
        "book": "Gen",
        "genre": "torah_prose_law",
        "anomaly_type": "ordinary",
        "evidence_class": "lexical_morphological",
    }


def _gold_row(fold: int, *, score: float = 0.9, correct: bool = True) -> dict[str, object]:
    return {
        "fold_id": fold,
        "label_source": "frozen_gold",
        "score": score,
        "eligible": True,
        "correct": correct,
        "testament": "OT",
        "book": "Gen",
        "genre": "torah_prose_law",
        "anomaly_type": "ordinary",
        "evidence_class": "lexical_morphological",
    }


class Stage7HypergraphResolverTest(unittest.TestCase):
    def test_ranker_keeps_top_k_nonoverlapping_decompositions(self) -> None:
        candidates = [
            _edge("edge:a", ["o1"], ["u1"], 0.9),
            _edge("edge:b", ["o2"], ["u2"], 0.8),
            _edge("edge:c", ["o1", "o2"], ["u1"], 0.95, "many_to_one"),
            {
                **_edge("edge:raw", ["o1"], ["u2"], 1.0),
                "resolver_eligible": False,
            },
        ]
        result = rank_verse_hypergraph_solutions(
            candidates,
            target_ref="Gen.1.1",
            valid_original_ids={"o1", "o2"},
            valid_target_token_ids={"u1", "u2"},
            original_ref_by_id={"o1": "Gen.1.1", "o2": "Gen.1.1"},
            target_ref_by_id={"u1": "Gen.1.1", "u2": "Gen.1.1"},
            top_k=2,
        )
        self.assertEqual(result["candidate_count"], 3)
        self.assertEqual(result["rejected_counts"], {"not_resolver_eligible": 1})
        self.assertEqual(result["solutions"][0]["edge_ids"], ["edge:a", "edge:b"])
        self.assertAlmostEqual(result["solutions"][0]["score_sum"], 1.7)
        self.assertFalse(result["solutions"][0]["production_accepted"])

    def test_ranker_rejects_cross_verse_and_single_translation_only(self) -> None:
        invalid = {
            **_edge("edge:bridge", ["o1"], ["u1"], 0.9),
            "evidence_channels": ["manual_bridge_russyn"],
        }
        result = rank_verse_hypergraph_solutions(
            [invalid],
            target_ref="Gen.1.1",
            valid_original_ids={"o1"},
            valid_target_token_ids={"u1"},
            original_ref_by_id={"o1": "Gen.1.1"},
            target_ref_by_id={"u1": "Gen.1.1"},
        )
        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(result["rejected_counts"], {"invalid_edge": 1})

    def test_wilson_calibration_uses_only_declared_unsealed_folds(self) -> None:
        calibration = [_gold_row(index % 3) for index in range(539)]
        validation = [_gold_row(3) for _ in range(539)]
        report = calibrate_auto_class(calibration, validation)
        self.assertEqual(report["status"], "calibrated_validation_passed")
        self.assertGreaterEqual(
            report["validation"]["overall"]["one_sided_wilson_lower_bound"],
            AUTO_LOWER_BOUND,
        )
        self.assertFalse(report["sealed_fold_read"])
        self.assertTrue(
            {
                "testament:OT",
                "book:Gen",
                "genre:torah_prose_law",
                "anomaly_type:ordinary",
                "evidence_class:lexical_morphological",
            }
            <= set(report["enabled_auto_strata"])
        )
        blocked = calibrate_auto_class(calibration[:538], validation)
        self.assertEqual(
            blocked["status"], "blocked_no_threshold_meets_precision_gate"
        )
        with self.assertRaisesRegex(ValueError, "Sealed"):
            calibrate_auto_class([_gold_row(4)], validation)

    def test_final_solution_requires_exact_accounting_and_a_gate(self) -> None:
        edges = [
            {
                **_edge("edge:a", ["o1"], ["u1"], 0.999),
                "evidence_channels": ["gold_annotation"],
                "auto_eligible": True,
                "testament": "OT",
                "book": "Gen",
                "genre": "torah_prose_law",
                "anomaly_type": "translation_addition",
                "evidence_class": "gold_annotation",
            },
            {
                "edge_id": "edge:addition",
                "target_ref": "Gen.1.1",
                "relation": "translation_addition",
                "original_token_ids": [],
                "target_token_ids": ["u2"],
                "evidence_channels": ["gold_annotation"],
                "auto_eligible": True,
                "testament": "OT",
                "book": "Gen",
                "genre": "torah_prose_law",
                "anomaly_type": "translation_addition",
                "evidence_class": "gold_annotation",
            },
        ]
        calibration = {
            "status": "calibrated_validation_passed",
            "validation": {
                "overall": {"one_sided_wilson_lower_bound": AUTO_LOWER_BOUND}
            },
            "disabled_auto_strata": [],
            "enabled_auto_strata": [
                "testament:OT",
                "book:Gen",
                "genre:torah_prose_law",
                "anomaly_type:translation_addition",
                "evidence_class:gold_annotation",
            ],
        }
        result = validate_complete_solution(
            edges,
            target_ref="Gen.1.1",
            expected_original_ids={"o1"},
            expected_target_token_ids={"u1", "u2"},
            original_ref_by_id={"o1": "Gen.1.1"},
            target_ref_by_id={"u1": "Gen.1.1", "u2": "Gen.1.1"},
            acceptance_class="A_auto",
            calibration=calibration,
        )
        self.assertEqual(result["status"], "complete_exact_accounting")
        disabled = {
            **calibration,
            "disabled_auto_strata": ["book:Gen"],
        }
        with self.assertRaisesRegex(ValueError, "disabled or underpowered"):
            validate_complete_solution(
                edges,
                target_ref="Gen.1.1",
                expected_original_ids={"o1"},
                expected_target_token_ids={"u1", "u2"},
                original_ref_by_id={"o1": "Gen.1.1"},
                target_ref_by_id={"u1": "Gen.1.1", "u2": "Gen.1.1"},
                acceptance_class="A_auto",
                calibration=disabled,
            )
        with self.assertRaisesRegex(ValueError, "exactly account"):
            validate_complete_solution(
                edges[:1],
                target_ref="Gen.1.1",
                expected_original_ids={"o1"},
                expected_target_token_ids={"u1", "u2"},
                original_ref_by_id={"o1": "Gen.1.1"},
                target_ref_by_id={"u1": "Gen.1.1", "u2": "Gen.1.1"},
                acceptance_class="A_auto",
                calibration=calibration,
            )

    def test_b_review_rejects_a_stale_override(self) -> None:
        edge = {
            **_edge("edge:b", ["o1"], ["u1"], 0.5),
            "evidence_channels": ["manual_oh1988_review"],
            "manual_override_id": "override:1",
        }
        digest = "a" * 64
        with self.assertRaisesRegex(ValueError, "current manual override"):
            validate_complete_solution(
                [edge],
                target_ref="Gen.1.1",
                expected_original_ids={"o1"},
                expected_target_token_ids={"u1"},
                original_ref_by_id={"o1": "Gen.1.1"},
                target_ref_by_id={"u1": "Gen.1.1"},
                acceptance_class="B_review",
                overrides_by_id={
                    "override:1": {
                        "stale": False,
                        "input_digests": {"stage6_text": digest},
                    }
                },
                current_input_digests={"stage6_text": "b" * 64},
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_model import stable_json
from scripts.bible_module.ukrainian_stage_7_textual_render import (
    production_post_candidate_textual_expectations,
    validate_post_candidate_textual_render_contract,
    validate_post_candidate_textual_render_paths,
)


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "textual_render_contract_cases.json"
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class PostCandidateTextualRenderContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _validate(
        self,
        *,
        selected: list[dict[str, object]] | None = None,
        gold: list[dict[str, object]] | None = None,
        expectations: dict[str, dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return validate_post_candidate_textual_render_contract(
            selected_original_rows=(
                selected
                if selected is not None
                else deepcopy(self.fixture["selected_original_layer"])
            ),
            finalized_gold_rows=(
                gold if gold is not None else deepcopy(self.fixture["finalized_gold"])
            ),
            expectations=(
                expectations
                if expectations is not None
                else deepcopy(self.fixture["expectations"])
            ),
        )

    def test_five_shapes_emit_only_the_two_reviewed_markers(self) -> None:
        report = self._validate()
        self.assertEqual(report["processed_count"], 5)
        self.assertEqual(report["error_count"], 0)
        self.assertEqual(
            report["counts"],
            {
                "textual_loci": 5,
                "textual_alternative_members": 10,
                "no_render_loci": 3,
                "strong_marker_occurrences": 2,
            },
        )
        markers = report["markers"]
        self.assertEqual(
            [(row["target_ref"], row["strong_classic"]) for row in markers],
            [("1Cor.14.34", "G2010"), ("Acts.2.38", "G1909")],
        )
        no_render_refs = {"Mark.1.2", "Mark.16.9", "Rev.22.19"}
        self.assertFalse(
            no_render_refs
            & {str(row["target_ref"]) for row in report["markers"]}
        )
        ledger = report["textual_alternative_member_accounting"]
        self.assertEqual(len(ledger), 5)
        self.assertEqual(
            len(
                {
                    member
                    for row in ledger
                    for member in row["member_original_token_ids"]
                }
            ),
            10,
        )
        self.assertTrue(
            all(
                row["member_status"] == "accounted_as_textual_alternatives"
                for row in ledger
            )
        )

    def test_path_adapter_preserves_the_pure_result(self) -> None:
        expected = self._validate()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selected = root / "selected.jsonl"
            gold = root / "gold.jsonl"
            _write_jsonl(selected, self.fixture["selected_original_layer"])
            _write_jsonl(gold, self.fixture["finalized_gold"])
            actual = validate_post_candidate_textual_render_paths(
                selected_original_layer_path=selected,
                finalized_gold_annotations_path=gold,
                expectations=self.fixture["expectations"],
            )
        self.assertEqual(actual, expected)

    def test_no_render_acts_and_corinth_strong_contracts_fail_closed(self) -> None:
        mutations: list[tuple[str, list[dict[str, object]]]] = []
        selected = deepcopy(self.fixture["selected_original_layer"])
        selected[0]["strong_classic"] = ["G2531"]
        selected[0]["rendered_strong"] = ["G2531"]
        mutations.append(("no-render leaked Strong", selected))

        selected = deepcopy(self.fixture["selected_original_layer"])
        acts = next(row for row in selected if row["target_ref"] == "Acts.2.38")
        acts["strong_classic"] = ["G1909", "G1722"]
        acts["rendered_strong"] = ["G1909", "G1722"]
        mutations.append(("Acts alternative leaked", selected))

        selected = deepcopy(self.fixture["selected_original_layer"])
        cor = next(row for row in selected if row["target_ref"] == "1Cor.14.34")
        cor["strong_classic"] = ["G2010", "G2010"]
        cor["rendered_strong"] = ["G2010", "G2010"]
        mutations.append(("Corinth duplicate Strong", selected))

        for label, mutated in mutations:
            with self.subTest(label=label), self.assertRaises(ValueError):
                self._validate(selected=mutated)

    def test_member_loss_duplication_and_independent_promotion_fail_closed(self) -> None:
        selected = deepcopy(self.fixture["selected_original_layer"])
        selected[0]["manual_textual_member_ids"] = [
            "cc0:member:mark-1-2:c01"
        ]
        with self.assertRaisesRegex(ValueError, "lost|stale"):
            self._validate(selected=selected)

        selected = deepcopy(self.fixture["selected_original_layer"])
        selected.append(
            {
                "schema_version": 1,
                "contract_version": "ukrainian-stage-7-evidence-alignment-v1",
                "original_token_id": "cc0:member:mark-1-2:c06",
                "target_ref": "Mark.1.2",
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicated beside"):
            self._validate(selected=selected)

        gold = deepcopy(self.fixture["finalized_gold"])
        gold[0]["original_token_ids"] = ["cc0:member:mark-1-2:c06"]
        with self.assertRaisesRegex(ValueError, "stale or dangling original"):
            self._validate(gold=gold)

    def test_exact_span_and_ref_drift_fail_closed(self) -> None:
        selected = deepcopy(self.fixture["selected_original_layer"])
        selected[0]["reviewed_target_span"]["end_scalar"] = 4
        with self.assertRaisesRegex(ValueError, "span drift"):
            self._validate(selected=selected)

        gold = deepcopy(self.fixture["finalized_gold"])
        accounting = next(
            row
            for row in gold
            if row["record_type"] == "target_accounting"
            and row["target_ref"] == "Acts.2.38"
        )
        accounting["target_span"]["surface_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "span drift"):
            self._validate(gold=gold)

        gold = deepcopy(self.fixture["finalized_gold"])
        gold[0]["target_ref"] = "Mark.1.3"
        with self.assertRaisesRegex(ValueError, "crosses a verse"):
            self._validate(gold=gold)

    def test_stale_and_dangling_stable_ids_fail_closed(self) -> None:
        selected = deepcopy(self.fixture["selected_original_layer"])
        selected[0]["original_token_id"] = "cc0:overlay:stale"
        with self.assertRaisesRegex(ValueError, "Stale textual overlay ID"):
            self._validate(selected=selected)

        gold = deepcopy(self.fixture["finalized_gold"])
        gold[0]["target_token_ids"] = ["cc0:target:dangling"]
        with self.assertRaisesRegex(ValueError, "dangling target"):
            self._validate(gold=gold)

        gold = deepcopy(self.fixture["finalized_gold"])
        accounting = next(
            row
            for row in gold
            if row["record_type"] == "target_accounting"
            and row["target_ref"] == "Rev.22.19"
        )
        accounting["target_ref"] = "Rev.22.18"
        with self.assertRaisesRegex(ValueError, "crosses a verse"):
            self._validate(gold=gold)

    def test_production_expectations_lock_exact_five_ids_and_spans(self) -> None:
        expectations = production_post_candidate_textual_expectations()
        self.assertEqual(
            set(expectations),
            {"Mark.1.2", "Mark.16.9", "Acts.2.38", "1Cor.14.34", "Rev.22.19"},
        )
        self.assertEqual(
            expectations["Acts.2.38"]["target_span"],
            {
                "token_id": "uk7:KTO:014:69:70",
                "surface": "у",
                "start_scalar": 69,
                "end_scalar": 70,
                "start_byte": 124,
                "end_byte": 126,
            },
        )
        self.assertEqual(expectations["Acts.2.38"]["rendered_strong"], ["G1909"])
        self.assertEqual(
            expectations["1Cor.14.34"]["rendered_strong"], ["G2010"]
        )
        self.assertEqual(
            sum(not value["rendered_strong"] for value in expectations.values()),
            3,
        )


if __name__ == "__main__":
    unittest.main()

"""CC0 tests for leakage-free bidirectional stage-7 statistical candidates."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_candidates import (
    CandidateContext,
    OriginalToken,
    TargetToken,
    stable_json,
)
from scripts.bible_module.ukrainian_stage_7_model import deterministic_fold
from scripts.bible_module.ukrainian_stage_7_statistical import (
    IBM1_ALGORITHM_VERSION,
    STATISTICAL_CONTRACT_VERSION,
    STATISTICAL_GENERATOR_ID,
    SYMMETRIZATION_VERSION,
    StatisticalConfig,
    StatisticalOriginalToken,
    StatisticalTargetToken,
    StatisticalVerse,
    build_statistical_generator_registry,
    generate_oof_statistical_candidates,
    generate_statistical_candidate_artifacts,
    infer_mutual_best_type_components,
    train_bidirectional_ibm1,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "statistical_alignment_cases.json"
)


def _sha(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class StatisticalCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        if cls.fixture["license"] != "CC0-1.0":
            raise AssertionError("Statistical alignment fixture must remain CC0")
        cls.config = StatisticalConfig(
            folds=int(cls.fixture["folds"]),
            iterations=6,
            minimum_pair_training_verses=2,
        )
        cls.context, cls.verses, cls.target_rows, cls.original_rows = (
            cls._materialize_fixture()
        )

    @classmethod
    def _materialize_fixture(
        cls,
    ) -> tuple[
        CandidateContext,
        tuple[StatisticalVerse, ...],
        list[dict[str, object]],
        list[dict[str, object]],
    ]:
        targets_by_id: dict[str, TargetToken] = {}
        originals_by_id: dict[str, OriginalToken] = {}
        target_rows: list[dict[str, object]] = []
        original_rows: list[dict[str, object]] = []
        verses: list[StatisticalVerse] = []
        for verse_spec in cls.fixture["verses"]:
            target_ref = verse_spec["target_ref"]
            actual_fold = deterministic_fold(target_ref, cls.config.folds)
            if actual_fold != verse_spec["expected_fold"]:
                raise AssertionError(
                    f"Fixture fold drift for {target_ref}: {actual_fold}"
                )
            original_tokens: list[StatisticalOriginalToken] = []
            for order, (label, lexical_key, family, strong) in enumerate(
                verse_spec["originals"], 1
            ):
                token_id = f"cc0:orig:{target_ref}:{order}:{label}"
                source_id = (
                    "step_tahot_fixture"
                    if family == "TAHOT"
                    else "step_tagnt_fixture"
                )
                original_tokens.append(
                    StatisticalOriginalToken(
                        stable_id=token_id,
                        lexical_key=lexical_key,
                        order=order,
                        source_id=source_id,
                        source_family=family,
                    )
                )
                originals_by_id[token_id] = OriginalToken(
                    token_id=token_id,
                    target_ref=target_ref,
                    order=order,
                    source_family=family,
                    reading_status=(
                        "primary_mt"
                        if family == "TAHOT"
                        else "primary_shared_critical"
                    ),
                    morphology="fixture",
                    transliteration="fixture",
                    strong_classic=(strong,),
                )
                original_rows.append(
                    {
                        "original_token_id": token_id,
                        "target_ref": target_ref,
                        "order": order,
                        "source_id": source_id,
                        "source_family": family,
                        "reading_status": (
                            "primary_mt"
                            if family == "TAHOT"
                            else "primary_shared_critical"
                        ),
                        "surface_normalized": lexical_key.split(":", 1)[1],
                        "morphology_raw": "fixture",
                        "transliteration_raw": "fixture",
                        "strong_classic": [strong],
                    }
                )
            target_tokens: list[StatisticalTargetToken] = []
            scalar_cursor = 0
            byte_cursor = 0
            for order, (label, lexical_key) in enumerate(verse_spec["targets"], 1):
                token_id = f"uk7:{target_ref}:{order:03d}:{label}"
                surface = label
                end_scalar = scalar_cursor + len(surface)
                end_byte = byte_cursor + len(surface.encode("utf-8"))
                target = TargetToken(
                    token_id=token_id,
                    verse_key=f"cc0-{target_ref}",
                    target_ref=target_ref,
                    order=order,
                    comparison=lexical_key,
                    surface=surface,
                    start_scalar=scalar_cursor,
                    end_scalar=end_scalar,
                    start_byte=byte_cursor,
                    end_byte=end_byte,
                    plain_text_sha256="a" * 64,
                )
                targets_by_id[token_id] = target
                target_tokens.append(
                    StatisticalTargetToken(token_id, lexical_key, order)
                )
                target_rows.append(
                    {
                        "token_id": token_id,
                        "verse_key": target.verse_key,
                        "target_ref": target_ref,
                        "order": order,
                        "comparison": lexical_key,
                        "surface": surface,
                        "start_scalar": scalar_cursor,
                        "end_scalar": end_scalar,
                        "start_byte": byte_cursor,
                        "end_byte": end_byte,
                        "plain_text_sha256": "a" * 64,
                    }
                )
                scalar_cursor = end_scalar + 1
                byte_cursor = end_byte + 1
            verses.append(
                StatisticalVerse(
                    target_ref=target_ref,
                    originals=tuple(original_tokens),
                    targets=tuple(target_tokens),
                )
            )
        context = CandidateContext(
            target_by_id=targets_by_id,
            target_by_ref_comparison={},
            target_by_verse_order={
                (token.verse_key, token.order): token
                for token in targets_by_id.values()
            },
            originals_by_id=originals_by_id,
            proper_originals=(),
            greek_originals_by_ref={},
        )
        return context, tuple(verses), target_rows, original_rows

    def _generate(self) -> tuple[list[dict[str, object]], dict[str, object]]:
        return generate_oof_statistical_candidates(
            self.verses,
            context=self.context,
            config=self.config,
        )

    def test_oof_candidates_are_fail_closed_and_exclude_evaluated_verse(self) -> None:
        rows, manifest = self._generate()
        self.assertGreater(len(rows), 10)
        self.assertEqual(manifest["output_sha256"], _sha("".join(
            stable_json(row) + "\n" for row in rows
        )))
        for row in rows:
            self.assertEqual(row["generator_id"], STATISTICAL_GENERATOR_ID)
            self.assertFalse(row["auto_acceptance"])
            self.assertFalse(row["resolver_eligible"])
            self.assertFalse(row["calibrated"])
            self.assertEqual(row["evidence_channels"], ["bidirectional_statistical"])
            evidence = row["evidence"][0]
            self.assertTrue(evidence["held_out_target_ref_excluded_from_training"])
            self.assertFalse(evidence["position_feature_used"])
            self.assertFalse(evidence["neighbor_feature_used"])
            self.assertFalse(evidence["heldout_verse_copresence_is_proof"])
        self.assertEqual(manifest["error_count"], 0)
        self.assertEqual(
            manifest["algorithm"]["symmetrization"], SYMMETRIZATION_VERSION
        )

    def test_unseen_heldout_pair_is_not_a_verse_bag_candidate(self) -> None:
        rows, manifest = self._generate()
        self.assertFalse(any(row["target_ref"] == "Tst.1.14" for row in rows))
        self.assertFalse(manifest["algorithm"]["verse_bag_assignment_used"])
        self.assertGreater(
            manifest["counts"]["target_types_with_null_or_no_statistical_link"],
            0,
        )

    def test_reorder_does_not_change_type_links(self) -> None:
        training = tuple(
            verse
            for verse in self.verses
            if len(verse.originals) == len(verse.targets) == 1
            and verse.target_ref != "Tst.1.14"
        )
        model = train_bidirectional_ibm1(
            training, held_out_fold=99, config=self.config
        )
        base = next(verse for verse in self.verses if verse.target_ref == "Tst.1.12")
        reordered = StatisticalVerse(
            target_ref="Tst.reordered",
            originals=tuple(reversed(base.originals)),
            targets=tuple(reversed(base.targets)),
        )
        left, _ = infer_mutual_best_type_components(
            base, model=model, config=self.config
        )
        right, _ = infer_mutual_best_type_components(
            reordered, model=model, config=self.config
        )
        left_pairs = {
            (link.source_key, link.target_key)
            for component in left
            for link in component.links
        }
        right_pairs = {
            (link.source_key, link.target_key)
            for component in right
            for link in component.links
        }
        self.assertEqual(left_pairs, right_pairs)
        self.assertEqual(
            left_pairs,
            {("TAHOT:אדם", "адам"), ("TAHOT:אור", "світло")},
        )

    def test_repetition_and_compound_expand_without_nearest_tie_break(self) -> None:
        rows, _ = self._generate()
        repeated = next(row for row in rows if row["target_ref"] == "Tst.1.16")
        self.assertEqual(repeated["relation"], "many_to_many")
        self.assertEqual(len(repeated["original_token_ids"]), 2)
        self.assertEqual(len(repeated["target_token_ids"]), 2)
        compound = next(row for row in rows if row["target_ref"] == "Tst.1.17")
        self.assertEqual(compound["relation"], "many_to_one")
        self.assertEqual(compound["strong_classic"], ["G932", "G935"])
        for row in (repeated, compound):
            self.assertEqual(row["prohibited_assignment_methods_used"], [])
            self.assertTrue(
                row["evidence"][0]["stable_order_used_for_serialization_only"]
            )

    def test_distinct_exact_type_ties_remain_one_many_to_many_component(self) -> None:
        training = tuple(
            StatisticalVerse(
                target_ref=f"Tie.1.{index}",
                originals=(
                    StatisticalOriginalToken(
                        f"tie:o:{index}:1", "source:x", 1, "cc0", "TAHOT"
                    ),
                    StatisticalOriginalToken(
                        f"tie:o:{index}:2", "source:y", 2, "cc0", "TAHOT"
                    ),
                ),
                targets=(
                    StatisticalTargetToken(f"tie:t:{index}:1", "target:u", 1),
                    StatisticalTargetToken(f"tie:t:{index}:2", "target:v", 2),
                ),
            )
            for index in range(1, 4)
        )
        model = train_bidirectional_ibm1(
            training, held_out_fold=99, config=self.config
        )
        components, _ = infer_mutual_best_type_components(
            training[0], model=model, config=self.config
        )
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].source_keys, ("source:x", "source:y"))
        self.assertEqual(components[0].target_keys, ("target:u", "target:v"))
        self.assertEqual(len(components[0].links), 4)

    def test_training_and_generation_are_byte_deterministic(self) -> None:
        left_rows, left_manifest = self._generate()
        right_rows, right_manifest = self._generate()
        self.assertEqual(
            "".join(stable_json(row) + "\n" for row in left_rows),
            "".join(stable_json(row) + "\n" for row in right_rows),
        )
        self.assertEqual(left_manifest, right_manifest)
        self.assertTrue(
            all(
                fold.get("training_and_held_out_disjoint") is True
                for fold in left_manifest["folds"]
            )
        )

    def test_registry_locks_algorithm_runtime_license_digest_and_config(self) -> None:
        digest = "b" * 64
        source_contracts = {
            source_id: {
                "source_id": source_id,
                "version": "fixture-v1",
                "sha256": digest,
                "license": "CC0-1.0",
                "usage_status": "fixture",
            }
            for source_id in (
                "stage6_synthesized_text",
                "step_tahot",
                "step_tagnt",
            )
        }
        registry = build_statistical_generator_registry(
            input_sha256={"fixture": digest},
            source_contracts=source_contracts,
            config=self.config,
        )
        self.assertEqual(registry["generator_id"], STATISTICAL_GENERATOR_ID)
        self.assertEqual(
            registry["statistical_contract_version"], STATISTICAL_CONTRACT_VERSION
        )
        self.assertEqual(registry["algorithm"]["version"], IBM1_ALGORITHM_VERSION)
        self.assertEqual(registry["implementation"]["license"], "Apache-2.0 (project LICENSE)")
        self.assertRegex(registry["implementation"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(registry["runtime"]["executable_sha256"], r"^[0-9a-f]{64}$")
        self.assertIsNone(registry["implementation"]["pretrained_model"])
        self.assertFalse(registry["reproducibility"]["token_order_used_for_scoring"])
        self.assertFalse(registry["reproducibility"]["auto_acceptance"])

    def test_invalid_config_cannot_reduce_support_to_one_verse(self) -> None:
        with self.assertRaisesRegex(ValueError, "Single-verse"):
            StatisticalConfig(minimum_pair_training_verses=1).validate()

    def test_standalone_artifact_api_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            targets = root / "targets.jsonl"
            originals = root / "originals.jsonl"
            registry = root / "source_registry.json"
            _write_jsonl(targets, self.target_rows)
            _write_jsonl(originals, self.original_rows)
            digest = "c" * 64
            registry.write_text(
                stable_json(
                    {
                        "sources": [
                            {
                                "source_id": source_id,
                                "version": "fixture-v1",
                                "sha256": digest,
                                "license": "CC0-1.0",
                                "usage_status": "fixture",
                            }
                            for source_id in (
                                "stage6_synthesized_text",
                                "step_tahot_fixture",
                                "step_tagnt_fixture",
                            )
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            manifests = [
                generate_statistical_candidate_artifacts(
                    token_inventory_path=targets,
                    original_universe_path=originals,
                    source_registry_path=registry,
                    output_dir=root / name,
                    config=self.config,
                )
                for name in ("left", "right")
            ]
            self.assertEqual(
                manifests[0]["output_sha256"], manifests[1]["output_sha256"]
            )
            self.assertEqual(
                (root / "left" / "alignment_candidates.statistical.jsonl").read_bytes(),
                (root / "right" / "alignment_candidates.statistical.jsonl").read_bytes(),
            )
            self.assertGreater(manifests[0]["counts"]["candidate_count"], 10)


if __name__ == "__main__":
    unittest.main()

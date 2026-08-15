"""CC0 tests for the fail-closed stage-7 contextual candidate channel."""

from __future__ import annotations

import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.bible_module.ukrainian_stage_7_contextual import (
    ALIGN_LAYER,
    CONTEXTUAL_GENERATOR_ID,
    MODEL_FILES,
    MODEL_ID,
    MODEL_LICENSE,
    MODEL_REVISION,
    MODEL_SNAPSHOT_CONTRACT_SHA256,
    MUTUAL_SOFTMAX_THRESHOLD,
    RUNTIME_PACKAGE_CONTRACTS,
    RUNTIME_ENVIRONMENT_LOCKS,
    ContextualObservation,
    ContextualRuntimeUnavailable,
    ContextualWordLink,
    ModelInputTooLong,
    _distribution_record,
    build_contextual_generator_registry,
    generate_contextual_artifacts,
    generate_contextual_candidates,
    load_original_surfaces,
    preflight_contextual_sequences,
    validate_contextual_candidate,
    validate_contextual_generator_registry,
    validate_model_snapshot,
)
from scripts.bible_module.ukrainian_stage_7_candidates import load_context
from scripts.bible_module.ukrainian_stage_7_model import stable_json


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "contextual_alignment_cases.json"
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class FixtureEncoder:
    def __init__(
        self,
        observations: dict[str, object],
        *,
        wrong_revision: bool = False,
        too_long_ref: str | None = None,
    ) -> None:
        self.observations = observations
        self.wrong_revision = wrong_revision
        self.too_long_ref = too_long_ref

    def runtime_registry(self) -> None:
        return None

    def wordpiece_counts(
        self,
        *,
        original_words: list[str],
        target_words: list[str],
    ) -> tuple[int, int]:
        return len(original_words), len(target_words)

    def align(
        self,
        *,
        target_ref: str,
        original_words: list[str],
        target_words: list[str],
    ) -> ContextualObservation:
        if target_ref == self.too_long_ref:
            raise ModelInputTooLong("fixture refuses truncation")
        if not original_words or not target_words:
            raise AssertionError("Fixture encoder requires exact nonempty word sequences")
        raw = self.observations[target_ref]
        if not isinstance(raw, dict):
            raise AssertionError("Malformed fixture observation")
        links = tuple(ContextualWordLink(**value) for value in raw["links"])
        return ContextualObservation(
            target_ref=target_ref,
            model_id=MODEL_ID,
            model_revision="wrong" if self.wrong_revision else MODEL_REVISION,
            model_snapshot_contract_sha256=MODEL_SNAPSHOT_CONTRACT_SHA256,
            align_layer=ALIGN_LAYER,
            threshold=MUTUAL_SOFTMAX_THRESHOLD,
            original_wordpiece_count=int(raw["original_wordpiece_count"]),
            target_wordpiece_count=int(raw["target_wordpiece_count"]),
            original_sequence_sha256=sha256(
                stable_json(original_words).encode("utf-8")
            ).hexdigest(),
            target_sequence_sha256=sha256(
                stable_json(target_words).encode("utf-8")
            ).hexdigest(),
            links=links,
        )


class ContextualCandidateFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        if cls.fixture["license"] != "CC0-1.0":
            raise AssertionError("Contextual fixture must remain CC0")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.target_path = self.root / "target.jsonl"
        self.original_path = self.root / "original.jsonl"
        _write_jsonl(self.target_path, self.fixture["target_tokens"])
        _write_jsonl(self.original_path, self.fixture["original_tokens"])
        self.context = load_context(self.target_path, self.original_path)
        self.surfaces = load_original_surfaces(
            self.original_path, context=self.context
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _rows(self) -> tuple[list[dict[str, object]], dict[str, int]]:
        iterator, counters = generate_contextual_candidates(
            context=self.context,
            original_surfaces=self.surfaces,
            encoder=FixtureEncoder(self.fixture["observations"]),
        )
        return list(iterator), dict(counters)

    def test_model_and_runtime_artifacts_have_exact_compatible_contracts(self) -> None:
        self.assertEqual(MODEL_LICENSE, "BSD-3-Clause")
        self.assertRegex(MODEL_REVISION, r"^[0-9a-f]{40}$")
        self.assertRegex(MODEL_SNAPSHOT_CONTRACT_SHA256, r"^[0-9a-f]{64}$")
        self.assertEqual(
            MODEL_FILES["pytorch_model.bin"],
            {
                "size": 1_086_292_375,
                "sha256": "9f9d19adbab07c9f5ec2d74fe5701a66c123919feb35d05fce29969b6a85adb9",
            },
        )
        self.assertEqual(
            {name: item["license"] for name, item in RUNTIME_PACKAGE_CONTRACTS.items()},
            {
                "torch": "BSD-3-Clause",
                "transformers": "Apache-2.0",
                "huggingface-hub": "Apache-2.0",
                "tokenizers": "Apache-2.0",
                "safetensors": "Apache-2.0",
            },
        )
        for contract in RUNTIME_PACKAGE_CONTRACTS.values():
            self.assertRegex(contract["artifact_sha256"], r"^[0-9a-f]{64}$")

    def test_snapshot_validation_is_raw_byte_exact_and_fail_closed(self) -> None:
        path = self.root / "model"
        path.mkdir()
        payload = b"fixture model bytes\n"
        model_file = path / "tiny.bin"
        model_file.write_bytes(payload)
        contract = {
            "tiny.bin": {"size": len(payload), "sha256": sha256(payload).hexdigest()}
        }
        result = validate_model_snapshot(path, file_contract=contract)
        self.assertEqual(result["processed_count"], 1)
        model_file.write_bytes(payload + b"tamper")
        with self.assertRaisesRegex(ContextualRuntimeUnavailable, "changed"):
            validate_model_snapshot(path, file_contract=contract)
        model_file.unlink()
        with self.assertRaisesRegex(ContextualRuntimeUnavailable, "incomplete"):
            validate_model_snapshot(path, file_contract=contract)

    def test_installed_distribution_record_verifies_actual_file_bytes(self) -> None:
        package = self.root / "fixture.py"
        bytecode = self.root / "__pycache__" / "fixture.cpython-312.pyc"
        console = self.root / "bin" / "fixture.exe"
        metadata_path = self.root / "fixture.dist-info" / "METADATA"
        record_path = self.root / "fixture.dist-info" / "RECORD"
        metadata_path.parent.mkdir()
        console.parent.mkdir()
        package.write_bytes(b"fixture package\n")
        console.write_bytes(b"fixture console launcher\n")
        metadata_path.write_bytes(b"Name: fixture\nVersion: 1.0\n")

        def record_hash(path: Path) -> str:
            value = sha256(path.read_bytes()).digest()
            return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

        record_text = (
            f"../../bin/fixture.exe,sha256={record_hash(console)},{console.stat().st_size}\n"
            "__pycache__/fixture.cpython-312.pyc,,\n"
            f"fixture.py,sha256={record_hash(package)},{package.stat().st_size}\n"
            f"fixture.dist-info/METADATA,sha256={record_hash(metadata_path)},{metadata_path.stat().st_size}\n"
            "fixture.dist-info/RECORD,,\n"
        )
        record_path.write_text(record_text, encoding="utf-8", newline="\n")

        class Distribution:
            version = "1.0"

            def read_text(self, name: str) -> str | None:
                if name == "RECORD":
                    return record_path.read_text(encoding="utf-8")
                if name == "METADATA":
                    return metadata_path.read_text(encoding="utf-8")
                return None

            def locate_file(self, value: str) -> Path:
                return self_root / value

        self_root = self.root
        lock = {
            "version": "1.0",
            "record": sha256(record_text.encode("utf-8")).hexdigest(),
            "metadata": sha256(metadata_path.read_bytes()).hexdigest(),
            "license": "CC0-1.0",
        }
        with mock.patch.dict(
            RUNTIME_ENVIRONMENT_LOCKS, {"fixture": lock}, clear=False
        ), mock.patch(
            "scripts.bible_module.ukrainian_stage_7_contextual.metadata.distribution",
            return_value=Distribution(),
        ):
            result = _distribution_record("fixture")
            self.assertRegex(result["installed_tree_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(result["installed_file_count"], 4)
            self.assertEqual(result["record_hashed_file_count"], 3)
            self.assertEqual(result["ignored_unhashed_bytecode_cache_count"], 1)
            self.assertFalse(bytecode.exists())
            package.write_bytes(b"tampered package\n")
            with self.assertRaisesRegex(
                ContextualRuntimeUnavailable, "(?:size|installed file) drift"
            ):
                _distribution_record("fixture")

    def test_only_resolved_primary_original_surfaces_enter_model_input(self) -> None:
        self.assertEqual(
            set(self.surfaces),
            {
                "orig:light",
                "orig:shine",
                "orig:name-a",
                "orig:name-b",
                "orig:second-verse",
            },
        )
        self.assertNotIn("orig:unresolved", self.surfaces)

    def test_empty_original_surface_is_explicitly_accounted(self) -> None:
        rows = list(self.fixture["original_tokens"])
        rows.append(
            {
                "original_token_id": "orig:explicit-null",
                "target_ref": "Gen.1.2",
                "order": 2,
                "source_family": "TAHOT",
                "reading_status": "primary_fingerprint_selected_controlled",
                "morphology_raw": "",
                "transliteration_raw": "",
                "strong_classic": [],
                "surface_raw": "",
            }
        )
        _write_jsonl(self.original_path, rows)
        context = load_context(self.target_path, self.original_path)
        counters: Counter[str] = Counter()
        surfaces = load_original_surfaces(
            self.original_path,
            context=context,
            counters=counters,
        )
        self.assertNotIn("orig:explicit-null", surfaces)
        self.assertEqual(counters["original_rows_skipped_empty_surface"], 1)

    def test_exact_ref_grid_and_preflight_are_fail_closed(self) -> None:
        counts = preflight_contextual_sequences(
            context=self.context,
            original_surfaces=self.surfaces,
            encoder=FixtureEncoder(self.fixture["observations"]),
            expected_target_ref_count=2,
        )
        self.assertEqual(counts["validated_target_refs"], 2)
        self.assertEqual(counts["preflight_verses"], 2)
        with self.assertRaisesRegex(ValueError, "target-ref count drift"):
            preflight_contextual_sequences(
                context=self.context,
                original_surfaces=self.surfaces,
                encoder=FixtureEncoder(self.fixture["observations"]),
                expected_target_ref_count=3,
            )
        missing = dict(self.surfaces)
        missing.pop("orig:second-verse")
        with self.assertRaisesRegex(ValueError, "ref grids differ"):
            generate_contextual_candidates(
                context=self.context,
                original_surfaces=missing,
                encoder=FixtureEncoder(self.fixture["observations"]),
            )

        class OverlongFixtureEncoder(FixtureEncoder):
            def wordpiece_counts(
                self,
                *,
                original_words: list[str],
                target_words: list[str],
            ) -> tuple[int, int]:
                raise ModelInputTooLong("fixture refuses truncation")

        with self.assertRaisesRegex(ModelInputTooLong, "refuses truncation"):
            preflight_contextual_sequences(
                context=self.context,
                original_surfaces=self.surfaces,
                encoder=OverlongFixtureEncoder(self.fixture["observations"]),
                expected_target_ref_count=2,
            )

    def test_nonlexical_target_mark_is_accounted_but_not_model_input(self) -> None:
        target_rows = list(self.fixture["target_tokens"])
        target_rows.append(
            {
                "token_id": "uk7:CTX1:005:20:21",
                "verse_key": "CTX1",
                "target_ref": "Gen.1.1",
                "order": 5,
                "comparison": "",
                "surface": "\u0301",
                "start_scalar": 20,
                "end_scalar": 21,
                "start_byte": 39,
                "end_byte": 41,
                "plain_text_sha256": "a" * 64,
            }
        )
        _write_jsonl(self.target_path, target_rows)
        context = load_context(self.target_path, self.original_path)
        iterator, counters = generate_contextual_candidates(
            context=context,
            original_surfaces=self.surfaces,
            encoder=FixtureEncoder(self.fixture["observations"]),
        )
        self.assertEqual(len(list(iterator)), 3)
        self.assertEqual(counters["target_tokens_skipped_nonlexical"], 1)

    def test_mutual_links_form_nonpositional_one_and_many_to_many_candidates(self) -> None:
        rows, counters = self._rows()
        self.assertEqual(len(rows), 3)
        self.assertEqual(counters["observed_subword_links"], 7)
        self.assertEqual(counters["mutual_non_unknown_subword_links"], 5)
        self.assertEqual(counters["verses_without_mutual_links"], 1)
        many = next(row for row in rows if row["relation"] == "many_to_many")
        self.assertEqual(
            many["original_token_ids"], ["orig:name-a", "orig:name-b"]
        )
        self.assertEqual(
            many["target_token_ids"],
            ["uk7:CTX1:003:11:15", "uk7:CTX1:004:16:20"],
        )
        self.assertEqual(many["strong_classic"], ["H8034"])
        self.assertFalse(many["position_features_used"])
        self.assertFalse(many["translation_bridge_used"])
        self.assertFalse(many["verse_bag_transfer_used"])
        self.assertFalse(many["single_translation_proof"])
        self.assertFalse(many["resolver_eligible"])
        self.assertFalse(many["auto_acceptance"])
        self.assertEqual(many["prohibited_assignment_methods_used"], [])
        self.assertEqual(
            many["evidence"][0]["sequence_order_use"],
            "transformer_context_only",
        )
        for row in rows:
            validate_contextual_candidate(row, context=self.context)
            self.assertEqual(row["generator_id"], CONTEXTUAL_GENERATOR_ID)

    def test_strict_bidirectional_threshold_and_unknown_are_not_evidence(self) -> None:
        rows, _ = self._rows()
        serialized = stable_json(rows)
        self.assertNotIn('"target_to_source_probability":0.001', serialized)
        self.assertNotIn("[UNK]", serialized)
        self.assertFalse(
            any(
                row["original_token_ids"] == ["orig:shine"]
                and row["target_token_ids"] == ["uk7:CTX1:001:0:6"]
                for row in rows
            )
        )

    def test_model_contract_drift_blocks_all_candidates(self) -> None:
        iterator, _ = generate_contextual_candidates(
            context=self.context,
            original_surfaces=self.surfaces,
            encoder=FixtureEncoder(
                self.fixture["observations"], wrong_revision=True
            ),
            only_target_refs={"Gen.1.1"},
        )
        with self.assertRaisesRegex(ValueError, "pinned model contract"):
            list(iterator)

    def test_overlong_verse_is_skipped_without_truncation(self) -> None:
        iterator, counters = generate_contextual_candidates(
            context=self.context,
            original_surfaces=self.surfaces,
            encoder=FixtureEncoder(
                self.fixture["observations"], too_long_ref="Gen.1.2"
            ),
            only_target_refs={"Gen.1.2"},
        )
        self.assertEqual(list(iterator), [])
        self.assertEqual(counters["processed_verses"], 1)
        self.assertEqual(counters["skipped_model_input_too_long"], 1)

    def test_validator_rejects_positional_or_resolver_escalation(self) -> None:
        rows, _ = self._rows()
        positional = json.loads(stable_json(rows[0]))
        positional["position_features_used"] = True
        with self.assertRaisesRegex(ValueError, "positional"):
            validate_contextual_candidate(positional, context=self.context)
        resolver = json.loads(stable_json(rows[0]))
        resolver["resolver_eligible"] = True
        with self.assertRaisesRegex(ValueError, "cannot enable"):
            validate_contextual_candidate(resolver, context=self.context)

    def test_generation_is_deterministic(self) -> None:
        left, _ = self._rows()
        right, _ = self._rows()
        self.assertEqual(
            "".join(stable_json(row) + "\n" for row in left),
            "".join(stable_json(row) + "\n" for row in right),
        )

    def test_artifact_bundle_is_path_independent_and_non_overwriting(self) -> None:
        source_registry = self.root / "source_registry.json"
        runtime_report = self.root / "runtime-report.json"
        source_registry.write_text("{}\n", encoding="utf-8", newline="\n")
        runtime_report.write_text("{}\n", encoding="utf-8", newline="\n")
        left = self.root / "left"
        right = self.root / "right"
        progress = self.root / "left.progress.json"

        def encoder(*_args: object, **_kwargs: object) -> FixtureEncoder:
            return FixtureEncoder(self.fixture["observations"])

        with mock.patch(
            "scripts.bible_module.ukrainian_stage_7_contextual.AwesomeAlignLocalEncoder",
            side_effect=encoder,
        ):
            left_manifest = generate_contextual_artifacts(
                token_inventory_path=self.target_path,
                original_universe_path=self.original_path,
                source_registry_path=source_registry,
                model_snapshot_dir=self.root / "model",
                runtime_install_report_path=runtime_report,
                runtime_packages_dir=self.root / "runtime",
                output_dir=left,
                expected_target_ref_count=2,
                progress_path=progress,
            )
            right_manifest = generate_contextual_artifacts(
                token_inventory_path=self.target_path,
                original_universe_path=self.original_path,
                source_registry_path=source_registry,
                model_snapshot_dir=self.root / "model",
                runtime_install_report_path=runtime_report,
                runtime_packages_dir=self.root / "runtime",
                output_dir=right,
                expected_target_ref_count=2,
            )
            with self.assertRaises(FileExistsError):
                generate_contextual_artifacts(
                    token_inventory_path=self.target_path,
                    original_universe_path=self.original_path,
                    source_registry_path=source_registry,
                    model_snapshot_dir=self.root / "model",
                    runtime_install_report_path=runtime_report,
                    runtime_packages_dir=self.root / "runtime",
                    output_dir=left,
                    expected_target_ref_count=2,
                )
        self.assertEqual(left_manifest, right_manifest)
        self.assertEqual(
            (left / "alignment_candidates.contextual.jsonl").read_bytes(),
            (right / "alignment_candidates.contextual.jsonl").read_bytes(),
        )
        self.assertEqual(
            (left / "alignment_candidates.contextual.manifest.json").read_bytes(),
            (right / "alignment_candidates.contextual.manifest.json").read_bytes(),
        )
        self.assertEqual(left_manifest["output"], "alignment_candidates.contextual.jsonl")
        self.assertIn("source_registry", left_manifest["input_sha256"])
        progress_value = json.loads(progress.read_text(encoding="utf-8"))
        self.assertEqual(progress_value["status"], "complete")
        self.assertEqual(progress_value["processed_target_refs"], 2)
        self.assertEqual(progress_value["requested_target_refs"], 2)

    def test_registry_is_digest_locked_and_never_resolver_eligible(self) -> None:
        registry = build_contextual_generator_registry(runtime_registry=None)
        validate_contextual_generator_registry(registry)
        self.assertEqual(registry["model"]["license"], "BSD-3-Clause")
        self.assertEqual(registry["model"]["revision"], MODEL_REVISION)
        self.assertFalse(registry["resolver_eligible"])
        self.assertFalse(registry["auto_acceptance"])
        self.assertEqual(registry["skipped_count"], 1)
        invalid = json.loads(stable_json(registry))
        invalid["model"]["license"] = "unknown"
        with self.assertRaisesRegex(ValueError, "provenance drift"):
            validate_contextual_generator_registry(invalid)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.bible_module import ukrainian_stage_7 as stage7
from scripts.bible_module.ukrainian_stage_7 import (
    EXPECTED_STAGE6_COMMENT_SHA256,
    EXPECTED_STAGE6_MANIFEST_SHA256,
    EXPECTED_STAGE6_TEXT_SHA256,
    EXPECTED_TARGET_COUNT,
    MAPPING_CONTRACT,
    _acts_15_34_external_evidence,
    _decode_bcvwp,
    decode_ugnt_strong,
    _lexeme_inventory,
    _load_bridge_bundle,
    _plain_preservation,
    resolve_original_target_ref,
    _sha256_file,
    _source_to_original,
    _stage6_rows,
    _tahot_reading_status,
    _tagnt_reading_status,
    parse_tahot_surface_alternative,
    parse_tagnt_textual_alternative,
    parse_raw_reference,
    ukrainian_morphology_candidates,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    candidate_is_evidence_backed,
    comparison_form,
    deterministic_fold,
    exact_word_tokens,
    normalize_strong,
    normalized_edit_similarity,
    override_is_current,
    render_strong_markup,
    sha256_text,
    sha256_lines,
    stable_json,
    strip_strong_markup,
    validate_classic_strong,
    validate_exact_partition,
    validate_hyperedge,
    wilson_lower_bound,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "alignment_contract_cases.json"
)
REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class FixtureContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_is_cc0_and_contains_no_production_text(self) -> None:
        self.assertEqual(self.fixture["license"], "CC0-1.0")
        self.assertEqual(self.fixture["schema_version"], 1)
        fixture_text = FIXTURE.read_text(encoding="utf-8")
        self.assertNotIn("ohienko_1988", fixture_text.casefold())
        self.assertNotIn("plain_text_nfc", fixture_text)


class ArtifactInventoryContractTest(unittest.TestCase):
    def test_mutable_handoff_is_not_normative_inventory_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report"
            work = root / "work"
            report.mkdir()
            work.mkdir()
            (report / "HANDOFF.ru.md").write_text(
                "mutable checkpoint\n", encoding="utf-8", newline="\n"
            )
            (report / "evidence.json").write_text(
                "{}\n", encoding="utf-8", newline="\n"
            )
            (work / "corpus.jsonl").write_text(
                "{}\n", encoding="utf-8", newline="\n"
            )
            stage7._write_artifact_inventory(report, work)
            inventory = json.loads(
                (report / "artifact_inventory.manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            paths = {
                (entry["root"], entry["path"]) for entry in inventory["entries"]
            }
            self.assertNotIn(("report", "HANDOFF.ru.md"), paths)
            self.assertIn(("report", "evidence.json"), paths)
            self.assertIn(("work", "corpus.jsonl"), paths)


class CandidateIntegrationContractTest(unittest.TestCase):
    def test_registry_index_embeds_three_independent_locked_registries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specs = (
                (
                    "first_party",
                    "candidate_generator_registry.json",
                    "alignment_candidates.first_party.manifest.json",
                ),
                (
                    "statistical",
                    "statistical_generator_registry.json",
                    "statistical_candidates.manifest.json",
                ),
                (
                    "contextual",
                    "contextual_generator_registry.json",
                    "alignment_candidates.contextual.manifest.json",
                ),
            )
            directories: dict[str, Path] = {}
            for index, (channel, registry_name, manifest_name) in enumerate(specs):
                target = root / channel
                target.mkdir()
                directories[channel] = target
                (target / registry_name).write_text(
                    stable_json({"channel": channel, "ordinal": index}) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                (target / manifest_name).write_text(
                    stable_json({"artifact": channel}) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            source_registry_sha256 = "a" * 64
            payload = stage7._candidate_registry_index(
                source_registry_sha256=source_registry_sha256,
                first_party_dir=directories["first_party"],
                statistical_dir=directories["statistical"],
                contextual_dir=directories["contextual"],
            )
            stage7._validate_candidate_registry_index(
                payload,
                source_registry_sha256=source_registry_sha256,
                first_party_dir=directories["first_party"],
                statistical_dir=directories["statistical"],
                contextual_dir=directories["contextual"],
            )
            self.assertEqual(payload["processed_count"], 3)
            self.assertEqual(
                [row["channel"] for row in payload["generators"]],
                [
                    "first_party",
                    "bidirectional_statistical",
                    "multilingual_contextual",
                ],
            )
            (directories["statistical"] / "statistical_generator_registry.json").write_text(
                stable_json({"tampered": True}) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(RuntimeError, "provenance drifted"):
                stage7._validate_candidate_registry_index(
                    payload,
                    source_registry_sha256=source_registry_sha256,
                    first_party_dir=directories["first_party"],
                    statistical_dir=directories["statistical"],
                    contextual_dir=directories["contextual"],
                )

    def test_candidate_output_inventory_is_exact_and_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "candidate.jsonl"
            path.write_text("{}\n", encoding="utf-8", newline="\n")
            digest = _sha256_file(path)
            stage7._require_candidate_output_files(
                root,
                {path.name: digest},
                {path.name},
                channel="fixture",
            )
            with self.assertRaisesRegex(RuntimeError, "inventory drifted"):
                stage7._require_candidate_output_files(
                    root,
                    {path.name: digest},
                    {path.name, "missing.json"},
                    channel="fixture",
                )
            with self.assertRaisesRegex(RuntimeError, "digest mismatch"):
                stage7._require_candidate_output_files(
                    root,
                    {path.name: "b" * 64},
                    {path.name},
                    channel="fixture",
                )

    def test_statistical_bundle_requires_complete_disjoint_folds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "alignment_candidates.statistical.jsonl"
            registry_path = root / "statistical_generator_registry.json"
            candidate.write_text("{}\n", encoding="utf-8", newline="\n")
            inputs = {
                "original_token_universe": "a" * 64,
                "source_registry": "b" * 64,
                "ukrainian_token_inventory": "c" * 64,
            }
            registry = {
                "statistical_contract_version": stage7.STATISTICAL_CONTRACT_VERSION,
                "generator_id": stage7.STATISTICAL_GENERATOR_ID,
                "input_sha256": inputs,
                "error_count": 0,
                "reproducibility": {
                    "auto_acceptance": False,
                    "resolver_eligible": False,
                    "token_order_used_for_scoring": False,
                },
            }
            registry_path.write_text(
                stable_json(registry) + "\n", encoding="utf-8", newline="\n"
            )
            folds = [
                {
                    "fold": fold,
                    "held_out_verse_count": 1,
                    "candidate_count": 1,
                    "training_and_held_out_disjoint": True,
                }
                for fold in range(5)
            ]
            manifest = {
                "statistical_contract_version": stage7.STATISTICAL_CONTRACT_VERSION,
                "generator_id": stage7.STATISTICAL_GENERATOR_ID,
                "status": "candidate_only_uncalibrated_no_auto_acceptance",
                "input_sha256": inputs,
                "output_sha256": _sha256_file(candidate),
                "output_files": {
                    candidate.name: _sha256_file(candidate),
                    registry_path.name: _sha256_file(registry_path),
                },
                "processed_count": 5,
                "skipped_count": 0,
                "error_count": 0,
                "counts": {"verse_count": 5, "candidate_count": 5},
                "folds": folds,
            }
            manifest_path = root / "statistical_candidates.manifest.json"
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            stage7._validate_statistical_candidate_bundle(
                root, expected_inputs=inputs, expected_target_refs=5
            )
            manifest["folds"][0]["training_and_held_out_disjoint"] = False
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(RuntimeError, "incomplete or unsafe"):
                stage7._validate_statistical_candidate_bundle(
                    root, expected_inputs=inputs, expected_target_refs=5
                )

    def test_contextual_bundle_requires_full_preflight_and_explicit_null_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "alignment_candidates.contextual.jsonl"
            registry_path = root / "contextual_generator_registry.json"
            candidate.write_text("{}\n", encoding="utf-8", newline="\n")
            registry_path.write_text(
                stable_json({"generator_id": stage7.CONTEXTUAL_GENERATOR_ID}) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            inputs = {
                "token_inventory": "a" * 64,
                "original_token_universe": "b" * 64,
                "source_registry": "c" * 64,
                "model_snapshot_contract": "d" * 64,
                "runtime_install_report": "e" * 64,
            }
            manifest = {
                "contextual_contract_version": stage7.CONTEXTUAL_CONTRACT_VERSION,
                "status": "complete_candidate_only_no_auto_acceptance",
                "input_sha256": inputs,
                "output_sha256": _sha256_file(candidate),
                "output_files": {
                    candidate.name: _sha256_file(candidate),
                    registry_path.name: _sha256_file(registry_path),
                },
                "output_count": 1,
                "processed_count": 1,
                "skipped_count": 17,
                "error_count": 0,
                "counts": {
                    "preflight.validated_target_refs": 1,
                    "preflight.preflight_verses": 1,
                    "skipped_model_input_too_long": 0,
                    "surface.original_rows_skipped_empty_surface": 0,
                    "target_tokens_skipped_nonlexical": 3,
                },
                "calibrated": False,
                "auto_acceptance": False,
                "resolver_eligible": False,
            }
            manifest_path = root / "alignment_candidates.contextual.manifest.json"
            manifest_path.write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with mock.patch.object(stage7, "validate_contextual_generator_registry"):
                stage7._validate_contextual_candidate_bundle(
                    root, expected_inputs=inputs, expected_target_refs=1
                )
                manifest["counts"]["preflight.preflight_verses"] = 0
                manifest_path.write_text(
                    stable_json(manifest) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                with self.assertRaisesRegex(RuntimeError, "incomplete or unsafe"):
                    stage7._validate_contextual_candidate_bundle(
                        root, expected_inputs=inputs, expected_target_refs=1
                    )


class ExactTokenContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_exact_surface_scalar_and_utf8_byte_offsets(self) -> None:
        case = self.fixture["tokenization"]
        tokens = exact_word_tokens(case["text"])
        self.assertEqual(
            [
                {
                    "comparison": token.comparison,
                    "end_byte": token.end_byte,
                    "end_scalar": token.end_scalar,
                    "order": token.order,
                    "start_byte": token.start_byte,
                    "start_scalar": token.start_scalar,
                    "surface": token.surface,
                }
                for token in tokens
            ],
            case["tokens"],
        )
        validate_exact_partition(case["text"], tokens)

    def test_ukrainian_morphology_candidates_are_conservative_zero_vote_data(self) -> None:
        conjunction = ukrainian_morphology_candidates("І")
        self.assertEqual(conjunction[0]["lemma"], "і")
        self.assertEqual(conjunction[0]["pos"], "CCONJ")
        infinitive = ukrainian_morphology_candidates("любити")
        self.assertEqual(infinitive[0]["pos"], "VERB")
        proper = ukrainian_morphology_candidates("Давид")
        self.assertEqual(proper[0]["pos"], "PROPN")
        fallback = ukrainian_morphology_candidates("давнього")
        self.assertEqual(fallback[0]["pos"], "X")
        self.assertIsNone(fallback[0]["lemma"])
        self.assertIsNone(fallback[0]["confidence"])
        self.assertLess(fallback[0]["heuristic_score"], 0.2)
        self.assertEqual(fallback[0]["score_kind"], "uncalibrated_rule")
        self.assertEqual(ukrainian_morphology_candidates("́"), [])

    def test_comparison_normalization_never_mutates_surface(self) -> None:
        text = self.fixture["tokenization"]["text"]
        tokens = exact_word_tokens(text)
        self.assertEqual(tokens[-1].surface, "ім’я́")
        self.assertEqual(tokens[-1].comparison, "ім'я")
        self.assertEqual(tokens[2].surface, "пів‑слова")
        self.assertEqual(tokens[2].comparison, "пів-слова")
        self.assertEqual(tokens[0].comparison, "їжак")
        self.assertEqual(tokens[3].comparison, "й")
        self.assertEqual(text[tokens[-1].start_scalar : tokens[-1].end_scalar], "ім’я́")

    def test_historic_or_unusual_spelling_is_not_corrected(self) -> None:
        plain = "Словоѣ слова"
        tokens = exact_word_tokens(plain)
        self.assertEqual([token.surface for token in tokens], ["Словоѣ", "слова"])
        self.assertEqual(plain[tokens[0].start_scalar : tokens[0].end_scalar], "Словоѣ")

    def test_partition_rejects_surface_order_and_byte_drift(self) -> None:
        text = self.fixture["tokenization"]["text"]
        tokens = exact_word_tokens(text)
        with self.assertRaisesRegex(ValueError, "Scalar token round-trip"):
            validate_exact_partition(text, [replace(tokens[0], surface="інше"), *tokens[1:]])
        with self.assertRaisesRegex(ValueError, "Non-contiguous token order"):
            validate_exact_partition(text, [tokens[0], replace(tokens[1], order=3), *tokens[2:]])
        with self.assertRaises(ValueError):
            validate_exact_partition(text, [replace(tokens[0], start_byte=1), *tokens[1:]])

    def test_partition_rejects_overlapping_and_empty_tokens(self) -> None:
        text = "один два"
        tokens = exact_word_tokens(text)
        overlapping = [
            replace(
                tokens[0],
                surface=text,
                end_scalar=len(text),
                end_byte=len(text.encode("utf-8")),
            ),
            tokens[1],
        ]
        with self.assertRaises(ValueError):
            validate_exact_partition(text, overlapping)
        empty = replace(
            tokens[0],
            surface="",
            end_scalar=tokens[0].start_scalar,
            end_byte=tokens[0].start_byte,
        )
        with self.assertRaises(ValueError):
            validate_exact_partition(text, [empty, tokens[1]])

    def test_token_id_suffix_is_stable_and_offset_based(self) -> None:
        token = exact_word_tokens("Один два")[1]
        self.assertEqual(token.token_id_suffix, "002:5:8")


class StrongMarkupContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_raw_and_classic_strong_are_kept_separate(self) -> None:
        self.assertEqual(
            normalize_strong("H0430A"),
            {
                "raw": "H0430A",
                "classic": "H430",
                "status": "classic_with_source_suffix",
                "source_suffix": "A",
            },
        )
        self.assertEqual(normalize_strong("A01234")["classic"], "H1234")
        self.assertEqual(
            normalize_strong("A01234")["status"], "classic_aramaic_source"
        )
        self.assertEqual(normalize_strong("G03056N")["classic"], "G3056")

    def test_classic_ranges_and_nonclassic_codes_fail_closed(self) -> None:
        for value in ("H1", "H8674", "G1", "G5624"):
            with self.subTest(value=value):
                self.assertTrue(validate_classic_strong(value))
        for value in ("H0", "H8675", "G0", "G5625", "H0001", "G1A", "X1", ""):
            with self.subTest(value=value):
                self.assertFalse(validate_classic_strong(value))
        self.assertEqual(normalize_strong("G5625")["status"], "out_of_classic_range")
        self.assertEqual(normalize_strong("not-a-code")["status"], "nonclassic_source_code")

    def test_ugnt_terminal_zero_decoding_is_explicit_and_fail_closed(self) -> None:
        self.assertEqual(decode_ugnt_strong("G09760")["classic"], "G976")
        self.assertEqual(decode_ugnt_strong("G00110")["classic"], "G11")
        self.assertEqual(decode_ugnt_strong("G08460")["classic"], "G846")
        for raw in ("G41775", "G99237"):
            with self.subTest(raw=raw):
                decoded = decode_ugnt_strong(raw)
                self.assertIsNone(decoded["classic"])
                self.assertEqual(
                    decoded["status"], "extended_nonzero_unresolved"
                )

    def test_multiple_strong_round_trip_and_duplicate_suppression(self) -> None:
        for case in self.fixture["markup"]:
            with self.subTest(plain=case["plain"]):
                tokens = exact_word_tokens(case["plain"])
                mapping = {
                    int(order): markers
                    for order, markers in case["strong_by_token"].items()
                }
                marked = render_strong_markup(case["plain"], tokens, mapping)
                self.assertEqual(strip_strong_markup(marked), case["plain"])
        first = self.fixture["markup"][0]
        marked = render_strong_markup(
            first["plain"],
            exact_word_tokens(first["plain"]),
            {1: ["H1", "H2", "H2"], 2: ["H3"]},
        )
        self.assertEqual(marked.count("H2"), 1)

    def test_unaligned_translation_addition_stays_unmarked(self) -> None:
        plain = "Додане слово"
        marked = render_strong_markup(
            plain, exact_word_tokens(plain), {2: ["G3056", "G2198"]}
        )
        self.assertTrue(marked.startswith("Додане "))
        self.assertNotIn("Додане G", marked)
        self.assertEqual(strip_strong_markup(marked), plain)

    def test_invalid_and_dangling_strong_are_rejected(self) -> None:
        plain = "Одне слово"
        tokens = exact_word_tokens(plain)
        with self.assertRaisesRegex(ValueError, "Invalid classic Strong"):
            render_strong_markup(plain, tokens, {1: ["H9001"]})
        with self.assertRaises(ValueError):
            render_strong_markup(plain, tokens, {99: ["H1"]})

    def test_renderer_rejects_a_nonexact_token_partition(self) -> None:
        plain = "Одне слово"
        tokens = exact_word_tokens(plain)
        damaged = [replace(tokens[0], surface="Інше"), tokens[1]]
        with self.assertRaises(ValueError):
            render_strong_markup(plain, damaged, {1: ["H1"]})

    def test_round_trip_property_across_joiners_punctuation_and_repetition(self) -> None:
        samples = (
            "слово",
            " слово ",
            "ім'я ім’я імʼя",
            "пів-слова пів‑слова",
            "раз, раз; раз!",
            "число 12 — знак?",
            "Словоѣ та їжак",
            "перед🙂після",
        )
        for plain in samples:
            with self.subTest(plain=plain):
                tokens = exact_word_tokens(plain)
                mapping = {
                    token.order: [
                        f"H{token.order}",
                        f"G{token.order}",
                    ]
                    for token in tokens
                }
                marked = render_strong_markup(plain, tokens, mapping)
                self.assertEqual(strip_strong_markup(marked), plain)


class EvidenceAndCalibrationContractTest(unittest.TestCase):
    def test_position_neighbor_verse_bag_and_majority_only_do_not_count(self) -> None:
        banned = (
            "position",
            "nearest",
            "neighbor",
            "verse_bag",
            "majority_only",
            "legacy_position",
        )
        for channel in banned:
            with self.subTest(channel=channel):
                self.assertFalse(
                    candidate_is_evidence_backed({"evidence_channels": [channel]})
                )
        self.assertFalse(candidate_is_evidence_backed({"evidence_channels": []}))

    def test_legacy_can_only_be_a_feature_beside_real_evidence(self) -> None:
        self.assertTrue(
            candidate_is_evidence_backed(
                {"evidence_channels": ["legacy_position", "lexical_morphological"]}
            )
        )
        self.assertFalse(
            candidate_is_evidence_backed(
                {"evidence_channels": ["manual_bridge_russyn"]}
            )
        )
        self.assertTrue(
            candidate_is_evidence_backed(
                {"evidence_channels": ["position", "lexical_morphological"]}
            )
        )
        for prohibited in (
            "nearest",
            "neighbor",
            "proportional",
            "verse_bag",
            "majority_only",
            "frequency_only",
            "one_translation",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertFalse(
                    candidate_is_evidence_backed(
                        {
                            "evidence_channels": [
                                prohibited,
                                "lexical_morphological",
                            ]
                        }
                    )
                )

    def test_one_sided_wilson_threshold_is_not_rounded_up(self) -> None:
        self.assertLess(wilson_lower_bound(538, 538), 0.995)
        self.assertGreaterEqual(wilson_lower_bound(539, 539), 0.995)
        self.assertLess(wilson_lower_bound(892, 893), 0.995)
        self.assertGreaterEqual(wilson_lower_bound(893, 894), 0.995)

    def test_wilson_invalid_support_fails_closed(self) -> None:
        self.assertEqual(wilson_lower_bound(0, 0), 0.0)
        self.assertEqual(wilson_lower_bound(2, 1), 0.0)
        self.assertEqual(wilson_lower_bound(-1, 10), 0.0)

    def test_fold_assignment_is_stable_and_requires_multiple_folds(self) -> None:
        self.assertEqual(deterministic_fold("uk7:ot:001"), 5)
        self.assertEqual(deterministic_fold("uk7:nt:001"), 1)
        self.assertEqual(deterministic_fold("uk7:ot:001", folds=5), 0)
        with self.assertRaises(ValueError):
            deterministic_fold("uk7:ot:001", folds=1)

    def test_normalized_edit_similarity_is_comparison_only(self) -> None:
        self.assertEqual(normalized_edit_similarity("ІМ’Я́", "ім'я"), 1.0)
        self.assertLess(normalized_edit_similarity("перше", "друге"), 1.0)
        self.assertEqual(normalized_edit_similarity("", "слово"), 0.0)

    def test_canonical_json_and_jsonl_digest_are_order_independent(self) -> None:
        left = {"b": 2, "a": "ї"}
        right = {"a": "ї", "b": 2}
        self.assertEqual(stable_json(left), stable_json(right))
        self.assertEqual(sha256_lines([left]), sha256_lines([right]))
        expected = sha256((stable_json(left) + "\n").encode("utf-8")).hexdigest()
        self.assertEqual(sha256_lines([left]), expected)

    def test_override_requires_exact_current_sha256_inputs(self) -> None:
        digest = "a" * 64
        override = {"stale": False, "input_digests": {"stage6_text": digest}}
        self.assertTrue(override_is_current(override, {"stage6_text": digest}))
        self.assertFalse(
            override_is_current(override, {"stage6_text": "b" * 64})
        )
        self.assertFalse(override_is_current({**override, "stale": True}, {"stage6_text": digest}))
        self.assertFalse(
            override_is_current(
                {"stale": False, "input_digests": {}}, {"stage6_text": digest}
            )
        )
        self.assertFalse(
            override_is_current(
                {"stale": False, "input_digests": {"stage6_text": "not-a-sha"}},
                {"stage6_text": "not-a-sha"},
            )
        )

    def test_many_to_many_and_explicit_null_hyperedges(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        valid_original_ids = {"orig:1", "orig:2", "orig:3"}
        valid_target_token_ids = {"uk:1", "uk:2", "uk:3"}
        for edge in fixture["hyperedges"]:
            with self.subTest(edge=edge["edge_id"]):
                validate_hyperedge(
                    edge,
                    valid_original_ids=valid_original_ids,
                    valid_target_token_ids=valid_target_token_ids,
                )

    def test_split_merge_reorder_repetition_and_compound_hyperedges(self) -> None:
        valid_original_ids = {"orig:1", "orig:2"}
        valid_target_token_ids = {"uk:1", "uk:2"}
        valid = (
            ("one_to_one", ["orig:1"], ["uk:1"]),
            ("one_to_many", ["orig:1"], ["uk:2", "uk:1"]),
            ("many_to_one", ["orig:1", "orig:2"], ["uk:1"]),
            ("many_to_many", ["orig:1", "orig:2"], ["uk:2", "uk:1"]),
            ("grouped_expression", ["orig:1", "orig:2"], ["uk:1", "uk:2"]),
            ("textual_alternative", ["orig:1"], ["uk:1"]),
        )
        for relation, originals, targets in valid:
            with self.subTest(relation=relation):
                validate_hyperedge(
                    {
                        "relation": relation,
                        "original_token_ids": originals,
                        "target_token_ids": targets,
                        "evidence_channels": ["manual_oh1988_review"],
                        "top_k_alternatives": [
                            {
                                "original_token_ids": originals,
                                "target_token_ids": list(reversed(targets)),
                            }
                        ],
                    },
                    valid_original_ids=valid_original_ids,
                    valid_target_token_ids=valid_target_token_ids,
                )

    def test_hyperedge_rejects_dangling_duplicate_and_positional_only_ids(self) -> None:
        valid_original_ids = {"orig:1", "orig:2"}
        valid_target_token_ids = {"uk:1", "uk:2"}
        base = {
            "relation": "one_to_one",
            "original_token_ids": ["orig:1"],
            "target_token_ids": ["uk:1"],
            "evidence_channels": ["lexical_morphological"],
        }
        for changed in (
            {**base, "original_token_ids": ["orig:missing"]},
            {**base, "target_token_ids": ["uk:missing"]},
            {**base, "original_token_ids": ["orig:1", "orig:1"]},
            {**base, "evidence_channels": ["nearest", "verse_bag"]},
        ):
            with self.subTest(edge=changed):
                with self.assertRaises(ValueError):
                    validate_hyperedge(
                        changed,
                        valid_original_ids=valid_original_ids,
                        valid_target_token_ids=valid_target_token_ids,
                    )

    def test_hyperedge_relation_cardinality_is_enforced(self) -> None:
        valid_original_ids = {"orig:1", "orig:2"}
        valid_target_token_ids = {"uk:1", "uk:2"}
        invalid = (
            ("one_to_one", ["orig:1", "orig:2"], ["uk:1", "uk:2"]),
            ("one_to_many", ["orig:1", "orig:2"], ["uk:1"]),
            ("many_to_one", ["orig:1"], ["uk:1", "uk:2"]),
            ("many_to_many", ["orig:1"], ["uk:1", "uk:2"]),
        )
        for relation, originals, targets in invalid:
            with self.subTest(relation=relation):
                with self.assertRaises(ValueError):
                    validate_hyperedge(
                        {
                            "relation": relation,
                            "original_token_ids": originals,
                            "target_token_ids": targets,
                            "evidence_channels": ["lexical_morphological"],
                        },
                        valid_original_ids=valid_original_ids,
                        valid_target_token_ids=valid_target_token_ids,
                    )

    def test_hyperedge_cannot_cross_a_verse_boundary(self) -> None:
        edge = {
            "target_ref": "Gen.1.1",
            "relation": "many_to_one",
            "original_token_ids": ["orig:1", "orig:2"],
            "target_token_ids": ["uk:1"],
            "evidence_channels": ["manual_oh1988_review"],
        }
        with self.assertRaisesRegex(ValueError, "verse boundary"):
            validate_hyperedge(
                edge,
                valid_original_ids={"orig:1", "orig:2"},
                valid_target_token_ids={"uk:1"},
                original_ref_by_id={"orig:1": "Gen.1.1", "orig:2": "Gen.1.2"},
                target_ref_by_id={"uk:1": "Gen.1.1"},
            )

    def test_single_translation_bridge_cannot_be_final_hyperedge_evidence(self) -> None:
        base = {
            "target_ref": "Gen.1.1",
            "relation": "one_to_one",
            "original_token_ids": ["orig:1"],
            "target_token_ids": ["uk:1"],
        }
        for evidence in (
            ["manual_bridge_russyn"],
            ["manual_bridge_ylt"],
            ["manual_bridge_russyn", "legacy_position"],
        ):
            with self.subTest(evidence=evidence):
                with self.assertRaises(ValueError):
                    validate_hyperedge(
                        {**base, "evidence_channels": evidence},
                        valid_original_ids={"orig:1"},
                        valid_target_token_ids={"uk:1"},
                    )


class OriginalReferenceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_tahot_and_tagnt_annotation_semantics(self) -> None:
        for case in self.fixture["raw_references"]:
            with self.subTest(raw=case["raw"]):
                parsed = parse_raw_reference(case["raw"], family=case["family"])
                self.assertIsNotNone(parsed)
                assert parsed is not None
                self.assertEqual(parsed["target_ref"], case["target_ref"])
                self.assertEqual(parsed["annotation_kind"], case["annotation_kind"])

    def test_unknown_malformed_and_mismatched_refs_are_rejected(self) -> None:
        self.assertIsNone(parse_raw_reference("Unknown.1.1#01=L", family="TAHOT"))
        self.assertIsNone(parse_raw_reference("Act.2#01=NKO", family="TAGNT"))
        self.assertIsNone(parse_raw_reference("Act.2.11#01=NKO", family="UNKNOWN"))
        self.assertIsNone(parse_raw_reference("Act.2.11[2.10]#01=NKO", family="TAHOT"))
        self.assertIsNone(
            parse_raw_reference("Act.2.11[2.10)#01=NKO", family="TAGNT")
        )

    def test_2chr_split_and_tagnt_application_projection_are_pure(self) -> None:
        split = parse_raw_reference(
            "2Ch.14.1(13.23)#12=L", family="TAHOT"
        )
        assert split is not None
        self.assertEqual(
            resolve_original_target_ref(split, family="TAHOT", order=12),
            ("2Chr.13.23", "stage5_split_first"),
        )
        self.assertEqual(
            resolve_original_target_ref(split, family="TAHOT", order=13),
            ("2Chr.14.1", "stage5_split_second"),
        )
        application = parse_raw_reference(
            "Act.2.11[2.10]#01=NKO", family="TAGNT"
        )
        assert application is not None
        self.assertEqual(
            resolve_original_target_ref(application, family="TAGNT", order=1),
            ("Acts.2.10", "kjv_square"),
        )

    def test_tagnt_textual_variants_are_locus_specific(self) -> None:
        self.assertEqual(
            _tagnt_reading_status("Luke.2.11", 1, "NA28+SBL+TR+Byz"),
            "primary_shared_reading",
        )
        self.assertEqual(
            _tagnt_reading_status("Acts.8.37", 1, "TR+Byz"),
            "primary_fingerprint_traditional",
        )
        self.assertEqual(
            _tagnt_reading_status("Mat.1.25", 8, "TR"),
            "primary_fingerprint_traditional",
        )
        self.assertEqual(
            _tagnt_reading_status("Mat.1.25", 9, "TR"),
            "alternative_unresolved_textual_reading",
        )
        self.assertEqual(
            _tagnt_reading_status("Rev.1.11", 1, "NA28+SBL"),
            "primary_critical_reading",
        )
        self.assertEqual(
            _tagnt_reading_status("Rev.1.11", 1, "TR+Byz"),
            "alternative_unresolved_textual_reading",
        )
        self.assertEqual(
            _tagnt_reading_status("Mat.5.22", 1, "Treg+TR+Byz"),
            "alternative_unresolved_textual_reading",
        )

    def test_ps22_tahot_surface_alternative_has_its_own_stable_identity(self) -> None:
        row = parse_tahot_surface_alternative(
            "Psa.22.16(22.17)#07=L(D)",
            'D= ka.\'a.Ru (כָּ֝אֲרוּ) "they dug" (H3738A=HVqp3cp)',
            "tahot:parent",
        )
        assert row is not None
        self.assertEqual(
            row["alternative_token_id"],
            "tahot:parent:alternative:tahot-c06:01",
        )
        self.assertEqual(row["surface_normalized"], "כארו")
        self.assertEqual(row["strong_raw"], ["H3738A"])
        self.assertEqual(row["strong_classic"], ["H3738"])
        self.assertEqual(row["morphology_raw"], "HVqp3cp")
        with self.assertRaises(RuntimeError):
            parse_tahot_surface_alternative(
                "Psa.22.16(22.17)#07=L(D)", "drift", "tahot:parent"
            )

    def test_tahot_lxx_reconstructions_are_never_promoted_to_mt(self) -> None:
        self.assertEqual(
            _tahot_reading_status("Gen.4.8", "X"),
            "alternative_lxx_reconstruction_unresolved",
        )
        self.assertEqual(
            _tahot_reading_status("Gen.4.8", "L"),
            "primary_mt",
        )
        self.assertEqual(
            _tahot_reading_status("Gen.27.3", "Q(K)"),
            "primary_qere_with_alternative_preserved",
        )
        self.assertEqual(
            _tahot_reading_status("Ps.22.16", "L(D)"),
            "unresolved_blocking_textual_locus",
        )

    def test_tagnt_textual_alternative_has_its_own_surface_and_strong(self) -> None:
        parsed = parse_tagnt_textual_alternative(
            "υἱός (T=huios) son - G5207=N-NSM in: Tyn+TR+Byz"
        )
        assert parsed is not None
        self.assertEqual(parsed["surface_raw"], "υἱός")
        self.assertEqual(parsed["strong_classic"], ["G5207"])
        self.assertEqual(parsed["morphology_raw"], "N-NSM")
        self.assertEqual(parsed["textual_witnesses"], ["Tyn", "TR", "Byz"])
        self.assertIsNone(parse_tagnt_textual_alternative(""))
        with self.assertRaises(RuntimeError):
            parse_tagnt_textual_alternative("not a valid apparatus reading")


class BridgeCrosswalkContractTest(unittest.TestCase):
    @staticmethod
    def _universe() -> dict[str, object]:
        return {
            "by_source_ref_order": {
                ("Gen.1.1", 1): ["orig:h1"],
                ("Gen.1.1", 2): ["orig:h2"],
                ("Mat.1.1", 1): ["orig:g1"],
            },
            "original_meta": {
                "orig:h1": {
                    "family": "TAHOT",
                    "surface": comparison_form("alpha"),
                    "classic": {"H1"},
                },
                "orig:h2": {
                    "family": "TAHOT",
                    "surface": comparison_form("beta"),
                    "classic": {"H2"},
                },
                "orig:g1": {
                    "family": "TAGNT",
                    "surface": comparison_form("logos"),
                    "classic": {"G3056"},
                },
            },
            "by_source_ref_surface": {
                ("TAHOT", "Gen.1.1", "alpha"): ["orig:h1"],
                ("TAHOT", "Gen.1.1", "beta"): ["orig:h2"],
                ("TAGNT", "Mat.1.1", "logos"): ["orig:g1"],
            },
            "by_source_ref_strong": {
                ("TAHOT", "Gen.1.1", "H1"): ["orig:h1"],
                ("TAHOT", "Gen.1.1", "H2"): ["orig:h2"],
                ("TAGNT", "Mat.1.1", "G3056"): ["orig:g1"],
            },
        }

    def test_bcvwp_decoder_accepts_declared_bridge_prefixes(self) -> None:
        self.assertEqual(_decode_bcvwp("01001001001"), ("Gen", 1, 1, 1))
        self.assertEqual(_decode_bcvwp("o01001001001"), ("Gen", 1, 1, 1))
        self.assertEqual(_decode_bcvwp("n40001001001"), ("Mat", 1, 1, 1))
        for invalid in (
            "bad-selector",
            "on01001001001",
            "ooo01001001001",
            "01000000000",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                _decode_bcvwp(invalid)

    def test_tahot_crosswalk_requires_surface_or_strong_not_position(self) -> None:
        universe = self._universe()
        token_id, evidence = _source_to_original(
            "01001001001",
            source_row={"text": "unrelated", "strongs": "1"},
            family="TAHOT",
            universe=universe,
        )
        self.assertEqual((token_id, evidence), ("orig:h1", "verse_wide_strong"))
        token_id, reason = _source_to_original(
            "01001001001",
            source_row={"text": "unrelated", "strongs": "999"},
            family="TAHOT",
            universe=universe,
        )
        self.assertIsNone(token_id)
        self.assertEqual(reason, "no_original_candidate")

    def test_tagnt_crosswalk_requires_both_surface_and_strong(self) -> None:
        universe = self._universe()
        token_id, evidence = _source_to_original(
            "40001001001",
            source_row={"text": "logos", "strongs": "3056"},
            family="TAGNT",
            universe=universe,
        )
        self.assertEqual(
            (token_id, evidence),
            ("orig:g1", "verse_wide_surface_and_strong"),
        )
        token_id, reason = _source_to_original(
            "40001001001",
            source_row={"text": "logos", "strongs": "999"},
            family="TAGNT",
            universe=universe,
        )
        self.assertIsNone(token_id)
        self.assertEqual(reason, "no_original_candidate")

    def test_multiple_matching_originals_are_rejected_as_ambiguous(self) -> None:
        universe = self._universe()
        universe["by_source_ref_order"][("Gen.1.1", 1)].append("orig:h1-copy")
        universe["original_meta"]["orig:h1-copy"] = {
            "family": "TAHOT",
            "surface": "alpha",
            "classic": {"H1"},
        }
        universe["by_source_ref_surface"][("TAHOT", "Gen.1.1", "alpha")].append(
            "orig:h1-copy"
        )
        universe["by_source_ref_strong"][("TAHOT", "Gen.1.1", "H1")].append(
            "orig:h1-copy"
        )
        token_id, reason = _source_to_original(
            "01001001001",
            source_row={"text": "alpha", "strongs": "1"},
            family="TAHOT",
            universe=universe,
        )
        self.assertIsNone(token_id)
        self.assertEqual(reason, "ambiguous_or_unproven_crosswalk")

    def test_russyn_style_bundle_keeps_original_and_target_ids_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    {
                        "records": [
                            {
                                "source": ["o01001001001"],
                                "target": ["01001001002"],
                                "meta": {"id": "fixture.1", "process": "manual"},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            source.write_text(
                "id\ttext\tstrongs\no01001001001\talpha\tH1\n",
                encoding="utf-8",
            )
            target.write_text(
                "id\ttext\n01001001002\ttarget-alpha\n", encoding="utf-8"
            )
            rows, summary = _load_bridge_bundle(
                family_id="RUSSYN",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        self.assertEqual(summary["counts"], {"accepted_manual_bridge": 1})
        self.assertEqual(rows[0]["original_token_ids"], ["orig:h1"])
        self.assertEqual(rows[0]["target_token_ids"], ["01001001002"])
        self.assertNotEqual(rows[0]["original_token_ids"], rows[0]["target_token_ids"])

    def test_ylt_legacy_nested_selectors_are_flattened_without_position_alias(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    [
                        {
                            "id": "fixture.1",
                            "source_ids": [["01001001001", "01001001002"]],
                            "target_ids": ["01001001003", "01001001004"],
                            "meta": {"process": "manual"},
                        }
                    ]
                ),
                encoding="utf-8",
            )
            source.write_text(
                "id\ttext\tstrongs\n"
                "01001001001\talpha\tH1\n"
                "01001001002\tbeta\tH2\n",
                encoding="utf-8",
            )
            target.write_text(
                "identifier\ttext\n"
                "01001001003\ttarget-alpha\n"
                "01001001004\ttarget-beta\n",
                encoding="utf-8",
            )
            rows, summary = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        self.assertEqual(summary["counts"], {"accepted_manual_bridge": 1})
        self.assertEqual(rows[0]["source_selectors"], ["01001001001", "01001001002"])
        self.assertEqual(rows[0]["original_token_ids"], ["orig:h1", "orig:h2"])

    def test_bridge_target_addition_is_not_accepted_as_original_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    [
                        {
                            "id": "fixture.null",
                            "source_ids": [],
                            "target_ids": ["01001001003"],
                            "meta": {"process": "manual"},
                        }
                    ]
                ),
                encoding="utf-8",
            )
            source.write_text("id\ttext\tstrongs\n", encoding="utf-8")
            target.write_text(
                "id\ttext\n01001001003\ttarget-only\n", encoding="utf-8"
            )
            rows, _ = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        self.assertEqual(rows[0]["original_token_ids"], [])
        self.assertEqual(rows[0]["status"], "accepted_manual_null_source")
        self.assertTrue(rows[0]["explicit_null_source"])
        self.assertFalse(rows[0]["cross_verse_manual_record"])

    def test_modern_clear_null_source_is_also_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    {
                        "records": [
                            {
                                "source": [],
                                "target": ["01001001003"],
                                "meta": {
                                    "id": "fixture.modern-null",
                                    "process": "manual",
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            source.write_text("id\ttext\tstrongs\n", encoding="utf-8")
            target.write_text(
                "id\ttext\n01001001003\ttarget-only\n", encoding="utf-8"
            )
            rows, _ = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        self.assertEqual(rows[0]["status"], "accepted_manual_null_source")
        self.assertTrue(rows[0]["explicit_null_source"])
        self.assertEqual(rows[0]["original_token_ids"], [])
        self.assertFalse(rows[0]["cross_verse_manual_record"])

    def test_generic_null_target_and_empty_hyperedge_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    [
                        {
                            "id": "fixture.null-target",
                            "source_ids": ["01001001001"],
                            "target_ids": [],
                            "meta": {"process": "manual"},
                        },
                        {
                            "id": "fixture.empty-edge",
                            "source_ids": [],
                            "target_ids": [],
                            "meta": {"process": "manual"},
                        },
                    ]
                ),
                encoding="utf-8",
            )
            source.write_text(
                "id\ttext\tstrongs\n01001001001\talpha\tH1\n",
                encoding="utf-8",
            )
            target.write_text("id\ttext\n", encoding="utf-8")
            rows, _ = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        omission, empty = rows
        self.assertEqual(omission["status"], "accepted_manual_null_target")
        self.assertFalse(omission["explicit_null_source"])
        self.assertTrue(omission["explicit_null_target"])
        self.assertEqual(omission["original_token_ids"], ["orig:h1"])
        self.assertEqual(omission["target_token_ids"], [])
        self.assertFalse(omission["cross_verse_manual_record"])
        self.assertEqual(empty["status"], "rejected_invalid_empty_manual_edge")
        self.assertTrue(empty["explicit_null_source"])
        self.assertTrue(empty["explicit_null_target"])
        self.assertFalse(empty["cross_verse_manual_record"])

    def test_ylt_alias_and_mixed_null_keep_raw_selector_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    [
                        {
                            "id": "fixture.alias",
                            "source_ids": ["010010010011"],
                            "target_ids": ["01001001003"],
                            "meta": {"process": "manual"},
                        },
                        {
                            "id": "fixture.mixed-null",
                            "source_ids": ["", "01001001001"],
                            "target_ids": ["01001001004"],
                            "meta": {"process": "manual"},
                        },
                        {
                            "id": "fixture.empty-string-null",
                            "source_ids": [""],
                            "target_ids": ["01001001005"],
                            "meta": {"process": "manual"},
                        },
                    ]
                ),
                encoding="utf-8",
            )
            source.write_text(
                "id\ttext\tstrongs\n01001001001\talpha\tH1\n",
                encoding="utf-8",
            )
            target.write_text(
                "id\ttext\n"
                "01001001003\ttarget-alpha\n"
                "01001001004\ttarget-added\n"
                "01001001005\ttarget-only\n",
                encoding="utf-8",
            )
            rows, _ = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        alias, mixed, empty_string_null = rows
        self.assertEqual(alias["source_selectors"], ["010010010011"])
        self.assertEqual(alias["original_token_ids"], ["orig:h1"])
        crosswalk = alias["source_selector_crosswalk"][0]
        self.assertEqual(crosswalk["raw_selector"], "010010010011")
        self.assertEqual(crosswalk["canonical_selector"], "01001001001")
        self.assertNotEqual(crosswalk["canonicalization_rule"], "position_only")
        self.assertTrue(crosswalk["source_tsv_present"])
        self.assertEqual(mixed["status"], "accepted_manual_bridge_with_null_member")
        self.assertTrue(mixed["explicit_null_source"])
        self.assertEqual(mixed["original_token_ids"], ["orig:h1"])
        self.assertEqual(empty_string_null["status"], "accepted_manual_null_source")
        self.assertTrue(empty_string_null["explicit_null_source"])
        self.assertEqual(empty_string_null["original_token_ids"], [])
        self.assertFalse(empty_string_null["cross_verse_manual_record"])

    def test_ylt_alias_prefers_an_exact_12_digit_source_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment = root / "alignment.json"
            source = root / "source.tsv"
            target = root / "target.tsv"
            alignment.write_text(
                stable_json(
                    [
                        {
                            "id": "fixture.exact-alias",
                            "source_ids": ["010010010011"],
                            "target_ids": ["01001001003"],
                            "meta": {"process": "manual"},
                        }
                    ]
                ),
                encoding="utf-8",
            )
            source.write_text(
                "id\ttext\tstrongs\n"
                "01001001001\talpha\tH1\n"
                "010010010011\tunrelated\tH999\n",
                encoding="utf-8",
            )
            target.write_text(
                "id\ttext\n01001001003\ttarget-alpha\n", encoding="utf-8"
            )
            rows, _ = _load_bridge_bundle(
                family_id="YLT",
                scope="OT",
                alignment_path=alignment,
                source_path=source,
                target_path=target,
                source_family="TAHOT",
                universe=self._universe(),
            )
        self.assertEqual(rows[0]["original_token_ids"], [])
        self.assertEqual(rows[0]["status"], "rejected_unproven_original_crosswalk")
        crosswalk = rows[0]["source_selector_crosswalk"][0]
        self.assertEqual(crosswalk["raw_selector"], "010010010011")
        self.assertEqual(crosswalk["canonical_selector"], "010010010011")
        self.assertEqual(crosswalk["canonicalization_rule"], "exact")


class LeakageFreeLexemeLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_each_out_of_fold_count_excludes_its_held_out_fold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "inventory.jsonl"
            inventory.write_text(
                "".join(stable_json(row) + "\n" for row in self.fixture["lexeme_tokens"]),
                encoding="utf-8",
                newline="\n",
            )
            result = _lexeme_inventory({"path": inventory}, root / "ledger")
            ledger = {row["normalized_form"]: row for row in _read_jsonl(result["path"])}
        self.assertEqual(result["nonlexical_skipped"], 1)
        self.assertNotIn("", ledger)
        word = ledger["слово"]
        self.assertEqual(word["occurrence_count"], 3)
        self.assertEqual(word["fold_occurrences"], {"0": 2, "3": 1})
        self.assertEqual(
            word["out_of_fold_training_occurrences"], {"0": 1, "3": 2}
        )
        for fold, held_out in word["fold_occurrences"].items():
            self.assertEqual(
                word["out_of_fold_training_occurrences"][fold] + held_out,
                word["occurrence_count"],
            )
        self.assertEqual(word["strong_distribution"], {})
        self.assertEqual(
            word["genres"], {"gospel_narrative": 1, "torah_prose_law": 2}
        )
        self.assertEqual(
            word["lemma_pos_morphology_candidates"][0]["occurrence_count"], 3
        )
        self.assertEqual(
            set(word["candidate_strong_evidence"]),
            {"direct_original", "RUSSYN", "YLT", "contextual_gloss", "manual"},
        )
        self.assertIsNone(word["entropy"])
        self.assertIn("leaks", word["negative_evidence"][0])

    def test_ledger_generation_is_deterministic(self) -> None:
        digests: list[str] = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "inventory.jsonl"
            inventory.write_text(
                "".join(stable_json(row) + "\n" for row in self.fixture["lexeme_tokens"]),
                encoding="utf-8",
                newline="\n",
            )
            for name in ("left", "right"):
                result = _lexeme_inventory({"path": inventory}, root / name)
                digests.append(result["sha256"])
        self.assertEqual(digests[0], digests[1])


class FingerprintSelectedOriginalLayerTest(unittest.TestCase):
    def test_post_candidate_textual_choices_are_fail_closed_and_stable(self) -> None:
        def target_text(spec: dict[str, object]) -> str:
            target = spec["target"]
            assert isinstance(target, dict)
            order = int(str(target["token_id"]).split(":")[2])
            start_scalar = int(target["start_scalar"])
            start_byte = int(target["start_byte"])
            if order == 1:
                prefix = ""
            else:
                word_count = order - 1
                separator_count = word_count
                cyrillic_count = start_byte - start_scalar
                ascii_count = start_scalar - separator_count - cyrillic_count
                self.assertGreaterEqual(ascii_count, 0)
                letters = [*(["а"] * cyrillic_count), *(["x"] * ascii_count)]
                self.assertGreaterEqual(len(letters), word_count)
                words = [[letters.pop(0)] for _ in range(word_count)]
                words[0].extend(letters)
                prefix = " ".join("".join(word) for word in words) + " "
            self.assertEqual(len(prefix), start_scalar)
            self.assertEqual(len(prefix.encode("utf-8")), start_byte)
            return prefix + str(target["surface"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "original.jsonl"
            alternative_path = root / "alternative.jsonl"
            raw_rows: list[dict[str, object]] = []
            alternative_rows: list[dict[str, object]] = []
            original_meta: dict[str, dict[str, object]] = {}
            alternative_meta: dict[str, dict[str, object]] = {}
            stage6_by_ref: dict[str, dict[str, object]] = {}
            for index, (ref, spec) in enumerate(
                stage7._POST_CANDIDATE_TEXTUAL_CHOICES.items(), 1
            ):
                expected = spec["expected_strongs"]
                assert isinstance(expected, list)
                primary_id = str(spec["primary_id"])
                alternative_id = str(spec["alternative_id"])
                lexical_id = (
                    str(spec["excluded_lexical_id"])
                    if spec["excluded_lexical_id"] is not None
                    else None
                )
                parent_id = primary_id.removesuffix(":c01")
                target = spec["target"]
                assert isinstance(target, dict)
                verse_key = str(target["token_id"]).split(":")[1]
                plain_text = target_text(spec)
                stage6_by_ref[ref] = {
                    "verse_key": verse_key,
                    "plain_text_nfc": plain_text,
                    "plain_text_sha256": sha256_text(plain_text),
                }
                common = {
                    "schema_version": 1,
                    "contract_version": CONTRACT_VERSION,
                    "target_ref": ref,
                    "verse_key": verse_key,
                    "order": index,
                    "parent_token_id": parent_id,
                    "source_locator": spec["source_locator"],
                    "source_family": "TAGNT",
                    "source_id": "cc0-tagnt",
                    "source_sha256": "a" * 64,
                    "mapping_rule_id": f"cc0-rule-{index}",
                    "mapping_contract_version": MAPPING_CONTRACT,
                    "projection_status": "direct",
                    "transliteration_raw": "cc0",
                    "gloss_raw": "cc0",
                    "strong_status": "classic",
                    "textual_witnesses": ["CC0-A"],
                }
                primary = {
                    **common,
                    "original_token_id": primary_id,
                    "component_order": 1,
                    "component_group": 1,
                    "component_kind": "tagnt_strong_component",
                    "surface_raw": "alpha",
                    "surface_normalized": "alpha",
                    "lemma_raw": "alpha",
                    "lemma_source": "CC0",
                    "morphology_raw": "N",
                    "strong_raw": list(expected[0]),
                    "strong_normalized": [
                        {"raw": value, "classic": value, "status": "classic"}
                        for value in expected[0]
                    ],
                    "strong_classic": list(expected[0]),
                    "reading_status": "primary_shared_reading",
                    "textual_variant_raw": {},
                }
                raw_rows.append(primary)
                original_meta[primary_id] = {}
                for token_id, strong, column in (
                    (alternative_id, expected[1], 6),
                    (lexical_id, expected[1], 12),
                ):
                    if token_id is None:
                        continue
                    alternative_rows.append(
                        {
                            **common,
                            "alternative_token_id": token_id,
                            "apparatus_column": column,
                            "alternative_kind": "textual_surface_strong_candidate"
                            if column == 6
                            else "lexical_strong_candidate",
                            "surface_raw": "beta",
                            "surface_normalized": "beta",
                            "lemma_raw": None,
                            "morphology_raw": "N" if column == 6 else None,
                            "strong_raw": list(strong),
                            "strong_normalized": [
                                {
                                    "raw": value,
                                    "classic": value,
                                    "status": "classic",
                                }
                                for value in strong
                            ],
                            "strong_classic": list(strong),
                            "reading_status": "alternative_textual_candidate_unadjudicated",
                        }
                    )
                    alternative_meta[token_id] = {}
            raw_path.write_text(
                "".join(stable_json(row) + "\n" for row in raw_rows),
                encoding="utf-8",
                newline="\n",
            )
            alternative_path.write_text(
                "".join(stable_json(row) + "\n" for row in alternative_rows),
                encoding="utf-8",
                newline="\n",
            )
            universe = {
                "path": raw_path,
                "alternative_path": alternative_path,
                "original_meta": original_meta,
                "alternative_meta": alternative_meta,
            }
            first = stage7._post_candidate_textual_choice_resolutions(
                stage6_by_ref, universe
            )
            second = stage7._post_candidate_textual_choice_resolutions(
                stage6_by_ref, universe
            )
            self.assertEqual(first, second)
            self.assertEqual(set(first), set(stage7._FINGERPRINT_UNRESOLVED))
            self.assertEqual(first["Acts.2.38"]["rendered_strong"], ["G1909"])
            self.assertEqual(first["1Cor.14.34"]["rendered_strong"], ["G2010"])
            for ref in ("Mark.1.2", "Mark.16.9", "Rev.22.19"):
                self.assertEqual(first[ref]["rendered_strong"], [])
                self.assertEqual(
                    first[ref]["gold_overlay_original_token"]["strong_classic"],
                    [],
                )
            for resolution in first.values():
                for excluded_id in resolution["excluded_lexical_candidate_ids"]:
                    self.assertNotIn(
                        excluded_id,
                        resolution["candidate_original_token_ids"],
                    )
                self.assertEqual(
                    resolution["candidate_layer_status"],
                    "frozen_pre_resolution_choices_excluded",
                )

    def test_traditional_whole_verse_keeps_primary_and_alternative_buckets(self) -> None:
        universe = {
            "original_meta": {
                "primary": {"source_locator": "Act.8.37#01=K"},
                "alternative": {"source_locator": "Act.8.37#02=K"},
            },
            "alternative_meta": {},
        }
        result = stage7._fingerprint_selection(
            "Acts.8.37",
            ["primary"],
            ["alternative"],
            [],
            universe,
        )
        self.assertEqual(
            result["selected_original_token_ids"], ["primary", "alternative"]
        )
        self.assertEqual(
            result["selection_rule"],
            "selected_traditional_complete_component_layer",
        )

    def test_selected_layer_unifies_proven_readings_and_excludes_choices(self) -> None:
        def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
            path.write_text(
                "".join(stable_json(row) + "\n" for row in rows),
                encoding="utf-8",
                newline="\n",
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "raw.jsonl"
            alternative_path = root / "alternatives.jsonl"
            control_path = root / "controls.jsonl"
            common_raw = {
                "schema_version": 1,
                "contract_version": CONTRACT_VERSION,
                "source_id": "cc0-source",
                "source_family": "TAGNT",
                "source_locator": "Cco.1.1#01=K",
                "order": 1,
                "surface_raw": "alpha",
                "surface_normalized": "alpha",
                "transliteration_raw": "alpha",
                "morphology_raw": "N",
                "strong_classic": ["G1"],
            }
            write_jsonl(
                raw_path,
                [
                    {
                        **common_raw,
                        "original_token_id": "raw-selected",
                        "target_ref": "Gen.1.1",
                        "reading_status": "alternative_unresolved_textual_reading",
                    },
                    {
                        **common_raw,
                        "original_token_id": "raw-choice",
                        "target_ref": "Gen.1.1",
                        "reading_status": "alternative_unresolved_textual_reading",
                    },
                    {
                        **common_raw,
                        "original_token_id": "raw-primary",
                        "target_ref": "Gen.1.2",
                        "reading_status": "primary_shared_reading",
                    },
                    {
                        **common_raw,
                        "original_token_id": "raw-unresolved",
                        "target_ref": "Gen.1.2",
                        "reading_status": "unresolved_other_reading",
                    },
                ],
            )
            write_jsonl(
                alternative_path,
                [
                    {
                        **common_raw,
                        "alternative_token_id": "apparatus-selected",
                        "alternative_kind": "textual_surface_strong_candidate",
                        "target_ref": "Gen.1.1",
                        "reading_status": "alternative_textual_candidate_unadjudicated",
                    },
                    {
                        **common_raw,
                        "alternative_token_id": "apparatus-unselected",
                        "alternative_kind": "textual_surface_strong_candidate",
                        "target_ref": "Gen.1.1",
                        "reading_status": "alternative_textual_candidate_unadjudicated",
                    },
                ],
            )
            write_jsonl(
                control_path,
                [
                    {
                        "schema_version": 1,
                        "contract_version": CONTRACT_VERSION,
                        "control_token_id": "control-selected",
                        "source_id": "cc0-control",
                        "source_order": 3,
                        "source_ref": "Gen.1.1",
                        "native_id": "cc0-3",
                        "surface_raw": "gamma",
                        "surface_normalized": "gamma",
                        "strong_classic": ["G3"],
                        "reading_status": "primary_control_reading",
                    }
                ],
            )
            stage6 = {
                ref: {
                    "verse_key": f"key-{order}",
                    "rule_id": f"rule-{order}",
                    "mapping_contract_version": MAPPING_CONTRACT,
                    "order": order,
                }
                for order, ref in enumerate(("Gen.1.1", "Gen.1.2"), 1)
            }
            fingerprint = {
                "loci": [
                    {
                        "locus": "Gen.1.1",
                        "selection_rule": "cc0_component_selection",
                        "selected_original_token_ids": [
                            "raw-selected",
                            "apparatus-selected",
                        ],
                        "supplemental_control_candidate_ids": ["control-selected"],
                        "unresolved_choice_groups": [
                            {"candidate_original_token_ids": ["raw-choice"]}
                        ],
                    }
                ]
            }
            arguments = {
                "stage6_by_ref": stage6,
                "universe": {
                    "path": raw_path,
                    "alternative_path": alternative_path,
                },
                "controls": {"token_path": control_path},
                "fingerprint": fingerprint,
                "work": root,
            }
            first = stage7._build_fingerprint_selected_original_layer(**arguments)
            first_bytes = first["path"].read_bytes()
            second = stage7._build_fingerprint_selected_original_layer(**arguments)
            self.assertEqual(first["sha256"], second["sha256"])
            self.assertEqual(first_bytes, second["path"].read_bytes())
            rows = _read_jsonl(first["path"])
            by_id = {str(row["original_token_id"]): row for row in rows}
            self.assertEqual(
                set(by_id),
                {
                    "raw-selected",
                    "apparatus-selected",
                    "control-selected",
                    "raw-primary",
                },
            )
            for token_id in (
                "raw-selected",
                "apparatus-selected",
                "control-selected",
            ):
                self.assertEqual(
                    by_id[token_id]["reading_status"],
                    "primary_fingerprint_selected_controlled",
                )
            self.assertEqual(
                by_id["raw-primary"]["reading_status"], "primary_shared_reading"
            )
            self.assertEqual(first["ref_count"], 2)
            self.assertEqual(first["choice_candidate_count"], 1)


class ImmutableStage6IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not stage7.STAGE6_TEXT.is_file():
            raise unittest.SkipTest("ignored immutable stage-6 work input is unavailable")
        cls.rows, cls.by_ref = _stage6_rows()

    def test_exact_input_hashes_and_target_count(self) -> None:
        self.assertEqual(_sha256_file(stage7.STAGE6_TEXT), EXPECTED_STAGE6_TEXT_SHA256)
        self.assertEqual(
            _sha256_file(stage7.STAGE6_MANIFEST), EXPECTED_STAGE6_MANIFEST_SHA256
        )
        self.assertEqual(
            _sha256_file(stage7.STAGE6_COMMENTS), EXPECTED_STAGE6_COMMENT_SHA256
        )
        self.assertEqual(len(self.rows), EXPECTED_TARGET_COUNT)
        self.assertEqual(len(self.by_ref), EXPECTED_TARGET_COUNT)

    def test_exact_key_equality_and_mapping_contract(self) -> None:
        keys = [
            (row["order"], row["verse_key"], row["target_ref"])
            for row in self.rows
        ]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(
            all(row["mapping_contract_version"] == MAPPING_CONTRACT for row in self.rows)
        )

    def test_plain_text_and_comments_remain_frozen_before_markup(self) -> None:
        report = _plain_preservation(self.rows)
        self.assertTrue(report["exact_key_equality"])
        self.assertEqual(report["plain_text_mismatch_count"], 0)
        self.assertEqual(report["comment_mismatch_count"], 0)
        self.assertEqual(report["text_key_count"], EXPECTED_TARGET_COUNT)
        self.assertEqual(report["comment_key_count"], EXPECTED_TARGET_COUNT)
        self.assertEqual(report["markup_round_trip_status"], "not_applicable_until_links_accepted")


class TextualFingerprintSourceLockTest(unittest.TestCase):
    def test_acts_15_34_external_evidence_is_exact_and_fail_closed(self) -> None:
        evidence = _acts_15_34_external_evidence()
        self.assertEqual(
            evidence["status"],
            "resolved_composite_original_plus_versional_addition",
        )
        self.assertEqual(
            evidence["d05_primary_token_ids"],
            [
                "bezae05-v1.03:B05K15V34:w16",
                "bezae05-v1.03:B05K15V34:w18",
                "bezae05-v1.03:B05K15V34:w20",
                "bezae05-v1.03:B05K15V34:w22",
            ],
        )
        self.assertEqual(
            evidence["proven_omitted_original_ids"],
            [
                "ugnt:19394bb7cec7b91be5c78842776cb3e30ec6ecc7cf14bef8d8edb48de698ef3c"
            ],
        )
        self.assertEqual(len(evidence["selected_supplemental_original_token_ids"]), 4)
        self.assertEqual(len(evidence["d05_to_ugnt_token_crosswalk"]), 4)
        self.assertEqual(
            evidence["versional_addition_target_ids"],
            ["uk7:L79:009:46:48", "uk7:L79:010:49:58"],
        )
        self.assertEqual(
            evidence["forbidden_strong_on_versional_addition"], ["G2419"]
        )
        self.assertEqual(len(evidence["evidence_records"]), 3)


class GeneratedFailClosedArtifactTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (REPORT / "generation_summary.json").is_file():
            raise unittest.SkipTest("stage-7 reports have not been generated yet")

    def test_stage_is_blocked_and_emits_no_production_markup(self) -> None:
        summary = json.loads((REPORT / "generation_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "blocked_before_gold_and_alignment_acceptance")
        self.assertEqual(summary["accepted_links"], 0)
        coverage = json.loads((REPORT / "strong_coverage_report.json").read_text(encoding="utf-8"))
        self.assertEqual(coverage["accepted_strong_occurrences"], 0)
        self.assertEqual(coverage["accepted_surface_bindings"], 0)
        self.assertEqual(coverage["calibration"]["status"], "not_run")
        self.assertEqual(
            coverage["legacy_rejected_baseline"]["strong_occurrences"], 440_280
        )
        self.assertEqual(
            coverage["legacy_rejected_baseline"]["surface_bindings"], 399_645
        )
        self.assertEqual(
            coverage["legacy_rejected_baseline"]["automatic_vote_weight"], 0
        )
        self.assertFalse((REPORT / "strong_markup.jsonl").exists())
        self.assertFalse((stage7.WORK / "strong_markup.jsonl").exists())

    def test_required_counterexamples_and_second_pass_gate_are_preserved(self) -> None:
        annotations = _read_jsonl(REPORT / "gold_alignment.annotations.jsonl")
        refs = {row["target"]["target_ref"] for row in annotations}
        self.assertTrue({"Isa.53.5", "Mic.6.8", "Luke.2.11", "Acts.2.38"} <= refs)
        self.assertTrue(all(row["label"]["decision"] == "reject_link" for row in annotations))
        self.assertTrue(all(row["review"]["pass_2"] is None for row in annotations))
        manifest = json.loads((REPORT / "gold_alignment.manifest.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(manifest["counts"]["selected_verses"], 2_000)
        self.assertGreaterEqual(
            manifest["counts"]["projected_assignment_or_null_decisions"], 25_000
        )
        self.assertEqual(manifest["counts"]["accepted_assignment_or_null_decisions"], 0)

    def test_manual_textual_dispositions_and_calibration_gate(self) -> None:
        reviews = _read_jsonl(REPORT / "manual_review.jsonl")
        unresolved = [
            row
            for row in reviews
            if row["status"] == "unresolved"
            and row["severity"] in {"critical", "high"}
        ]
        self.assertTrue(unresolved)
        self.assertTrue(
            {"gold", "review", "A_auto"} <= {row["scope"] for row in unresolved}
        )
        self.assertNotIn("textual_locus", {row["scope"] for row in unresolved})
        fingerprint = json.loads(
            (REPORT / "textual_fingerprint.manifest.json").read_text(encoding="utf-8")
        )
        ps22 = next(item for item in fingerprint["loci"] if item["locus"] == "Ps.22.16")
        self.assertFalse(ps22["automation_allowed"])
        self.assertEqual(ps22["status"], "resolved_original_component_universe")
        self.assertEqual(fingerprint["unresolved_textual_loci"], [])
        self.assertEqual(fingerprint["unresolved_critical_count"], 0)
        self.assertEqual(fingerprint["unresolved_high_count"], 0)
        self.assertEqual(
            fingerprint["post_candidate_manual_textual_resolution_count"], 5
        )
        manual_by_ref = {
            item["locus"]: item["manual_textual_resolution"]
            for item in fingerprint["loci"]
            if item["manual_textual_resolution"] is not None
        }
        self.assertEqual(set(manual_by_ref), set(stage7._FINGERPRINT_UNRESOLVED))
        self.assertEqual(manual_by_ref["Acts.2.38"]["rendered_strong"], ["G1909"])
        self.assertEqual(
            manual_by_ref["1Cor.14.34"]["rendered_strong"], ["G2010"]
        )
        for ref in ("Mark.1.2", "Mark.16.9", "Rev.22.19"):
            self.assertEqual(manual_by_ref[ref]["rendered_strong"], [])
        acts = next(
            item for item in fingerprint["loci"] if item["locus"] == "Acts.15.34"
        )
        self.assertEqual(acts["status"], "resolved_original_component_universe")
        self.assertEqual(
            acts["versional_addition_target_ids"],
            ["uk7:L79:009:46:48", "uk7:L79:010:49:58"],
        )
        self.assertEqual(
            acts["proven_omitted_original_ids"],
            ["bezae05-v1.03:B05K15V34:w16"],
        )
        self.assertEqual(len(acts["supplemental_original_crosswalk"]), 4)
        self.assertEqual(acts["forbidden_strong_on_versional_addition"], ["G2419"])
        self.assertNotIn("G2419", acts["selected_original_token_ids"])
        john = next(item for item in fingerprint["loci"] if item["locus"] == "John.1.18")
        self.assertTrue(
            any(
                token_id.endswith(":alternative:tagnt-c06:01")
                for token_id in john["selected_original_token_ids"]
            )
        )
        self.assertFalse(
            any(
                token_id == "tagnt:2af59d2154556e164944d8bac09013f7b11ccd2e45d948c3d84aa63cd1f03c36:c01"
                for token_id in john["selected_original_token_ids"]
            )
        )

    def test_original_universe_and_token_inventory_cover_the_exact_grid(self) -> None:
        universe = json.loads(
            (REPORT / "original_token_universe.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        inventory = json.loads(
            (REPORT / "ukrainian_token_inventory.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(universe["missing_target_refs"], [])
        self.assertEqual(
            universe["counts"]["target_ref_coverage"], EXPECTED_TARGET_COUNT
        )
        self.assertEqual(universe["processed_count"], 2_141_080)
        self.assertEqual(universe["counts"]["parent_tokens"], 447_748)
        self.assertEqual(universe["counts"]["alternative_candidates"], 28_543)
        self.assertEqual(
            universe["counts"]["TAHOT_textual_surface_alternatives"], 1
        )
        self.assertEqual(
            universe["counts"]["TAHOT_alternative_strong_candidates"], 5_557
        )
        self.assertEqual(
            universe["counts"]["TAGNT_textual_surface_alternatives"], 3_866
        )
        self.assertEqual(
            universe["counts"]["TAGNT_alternative_strong_candidates"], 19_119
        )
        self.assertEqual(
            universe["counts"]["TAHOT_components_including_primary_null"],
            540_481,
        )
        self.assertEqual(universe["counts"]["TAGNT_components"], 142_355)
        self.assertEqual(universe["counts"]["control_tokens"], 751_557)
        self.assertEqual(universe["counts"]["OSHB_tokens"], 306_785)
        self.assertEqual(universe["counts"]["UXLC_tokens"], 306_782)
        self.assertEqual(universe["counts"]["UGNT_tokens"], 137_990)
        self.assertEqual(universe["counts"]["UGNT_nonclassic_unresolved"], 210)
        self.assertEqual(
            universe["control_ref_audit"],
            {
                "OSHB_native_refs": 23_213,
                "OT_exact_set_equality": True,
                "TAGNT_base_refs": 7_958,
                "TAHOT_native_refs": 23_213,
                "UGNT_native_refs": 7_958,
                "UXLC_native_refs": 23_213,
                "NT_exact_set_equality": True,
                "control_token_id_collisions": 0,
                "unique_control_token_ids": 751_557,
            },
        )
        self.assertEqual(
            universe["control_native_token_type_counts"],
            {
                "OSHB.ketiv": 1_258,
                "OSHB.ordinary": 304_249,
                "OSHB.qere": 1_278,
                "OSHB.strong_occurrences": 300_007,
                "UGNT.classic_terminal_zero": 137_780,
                "UGNT.nonclassic_or_invalid": 210,
                "UXLC.k": 1_269,
                "UXLC.q": 1_279,
                "UXLC.structural_pe_skipped": 1_181,
                "UXLC.structural_reversednun_skipped": 9,
                "UXLC.structural_samekh_skipped": 1_981,
                "UXLC.w": 304_223,
                "UXLC.x": 11,
            },
        )
        self.assertEqual(
            universe["counts"]["TAHOT_classic_base_renderable"], 299_594
        )
        self.assertEqual(
            universe["counts"]["TAGNT_classic_base_renderable"], 141_982
        )
        self.assertEqual(
            inventory["counts"]["target_positions"], EXPECTED_TARGET_COUNT
        )
        self.assertGreater(
            inventory["counts"]["surface_tokens"], EXPECTED_TARGET_COUNT
        )

    def test_bridges_remain_independent_and_do_not_prove_oh1988_links(self) -> None:
        manifest = json.loads(
            (REPORT / "parallel_bridge_alignment.manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {(bundle["family"], bundle["scope"]) for bundle in manifest["bundles"]},
            {("RUSSYN", "OT"), ("RUSSYN", "NT"), ("YLT", "OT"), ("YLT", "NT")},
        )
        self.assertTrue(
            any("OH remains unproven" in note for note in manifest["notes"])
        )
        independence = json.loads(
            (REPORT / "evidence_independence_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(independence["pseudo_consensus_count"], 0)
        self.assertEqual(independence["prohibited_sources_used"], [])
        self.assertFalse(independence["BSB_MACULA_used"])
        legacy = next(
            channel
            for channel in independence["channels"]
            if channel["id"] == "legacy_experiment"
        )
        self.assertEqual(legacy["vote_weight"], 0)
        registry = json.loads(
            (REPORT / "source_registry.json").read_text(encoding="utf-8")
        )
        by_id = {source["source_id"]: source for source in registry["sources"]}
        self.assertEqual(
            by_id["clear_ylt_nt_main_alias"]["usage_status"],
            "rejected_integrity",
        )
        self.assertEqual(
            by_id["clear_ylt_nt_v010_transfer"]["usage_status"],
            "licensed_input_imported_original_crosswalk_partial",
        )
        for source_id in (
            "openscriptures_oshb_v2_2",
            "tanach_us_uxlc_2_5_27_6",
            "unfoldingword_ugnt_v0_34",
        ):
            with self.subTest(source_id=source_id):
                self.assertEqual(
                    by_id[source_id]["usage_status"],
                    "consumed_original_control_crosswalk_fail_closed",
                )
        legacy_registry = by_id[
            "ukrainian_stage_7_rejected_legacy_experiment"
        ]
        self.assertEqual(
            legacy_registry["usage_status"],
            "rejected_zero_vote_baseline_only",
        )
        self.assertEqual(
            legacy_registry["pin"]["value"],
            "d3a6371d2371a48c33fb7b756e0ef4e39f6815701f52bdd6c6eb714c010c6f4b",
        )
        self.assertEqual(
            by_id["local_revelation_uk_greek_descs"]["pin"]["value"],
            "3b489b074aa4a71dee2817a6c8a8fb290f7ca8f445ff9e890f131d2a2da0496b",
        )
        self.assertEqual(
            by_id["local_bible_lxx_tr_control"]["usage_status"],
            "consumed_read_only_control_zero_vote",
        )
        self.assertEqual(
            by_id["local_bible_kjv_control"]["usage_status"],
            "consumed_read_only_control_zero_vote",
        )
        self.assertEqual(
            by_id["scrivener_codex_bezae_1864"]["license"], "Public domain"
        )
        self.assertEqual(
            by_id["igntp_codex_bezae_greek_xml_v1_03"]["usage_status"],
            "verification_only_no_derived_corpus_no_alignment_vote",
        )
        self.assertFalse(
            by_id["igntp_codex_bezae_greek_xml_v1_03"]["redistributable"]
        )
        self.assertEqual(
            by_id["clementine_vulgate_1598_latvuc"]["usage_status"],
            "consumed_versional_locus_evidence_zero_strong_vote",
        )

    def test_versioned_overrides_have_current_nonempty_input_digests(self) -> None:
        registry_digest = _sha256_file(REPORT / "source_registry.json")
        overrides = _read_jsonl(REPORT / "alignment_overrides.jsonl")
        self.assertTrue(overrides)
        for row in overrides:
            with self.subTest(override=row["override_id"]):
                self.assertFalse(row["stale"])
                self.assertTrue(row["input_digests"])
                if "source_registry" in row["input_digests"]:
                    self.assertEqual(row["input_digests"]["source_registry"], registry_digest)
                if "stage6_text" in row["input_digests"]:
                    self.assertEqual(
                        row["input_digests"]["stage6_text"],
                        EXPECTED_STAGE6_TEXT_SHA256,
                    )

    def test_json_and_jsonl_artifacts_use_deterministic_serialization(self) -> None:
        json_names = [
            "source_registry.json",
            "textual_fingerprint.manifest.json",
            "author_comment_evidence.manifest.json",
            "original_token_universe.manifest.json",
            "parallel_bridge_alignment.manifest.json",
            "ukrainian_token_inventory.manifest.json",
            "ukrainian_lexeme_strong_ledger.manifest.json",
            "gold_alignment.manifest.json",
            "alignment_candidates.manifest.json",
            "strong_alignment.manifest.json",
            "strong_coverage_report.json",
            "plain_text_preservation_report.json",
            "evidence_independence_report.json",
            "generation_summary.json",
        ]
        for name in json_names:
            with self.subTest(name=name):
                path = REPORT / name
                value = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(path.read_text(encoding="utf-8"), stable_json(value) + "\n")
                self.assertEqual(value["contract_version"], CONTRACT_VERSION)
                self.assertIn("schema_version", value)
                self.assertIn("processed_count", value)
                self.assertIn("skipped_count", value)
                self.assertIn("error_count", value)
                self.assertIn("input_sha256", value)
                self.assertIn("output_sha256", value)

    def test_author_comments_are_complete_zero_vote_evidence(self) -> None:
        manifest = json.loads(
            (REPORT / "author_comment_evidence.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["processed_count"], 1329)
        self.assertEqual(manifest["counts"]["definition_count"], 1204)
        self.assertEqual(manifest["counts"]["verse_use_count"], 1318)
        self.assertEqual(manifest["counts"]["heading_non_verse_use_count"], 11)
        self.assertEqual(manifest["selection_mutation_count"], 0)
        self.assertEqual(manifest["automatic_assignment_count"], 0)
        rows = _read_jsonl(
            WORK / "author_comment_evidence/author_comment_evidence.jsonl"
        )
        self.assertEqual(len(rows), 1329)
        self.assertTrue(
            all(
                row["candidate_vote_weight"] == 0
                and row["auto_assignment_allowed"] is False
                and row["alignment_input_allowed"] is False
                for row in rows
            )
        )
        variant_rows = [
            row for row in rows if "textual_variant_claim" in row["categories"]
        ]
        self.assertEqual(len(variant_rows), 7)
        manual_rows = _read_jsonl(REPORT / "manual_review.jsonl")
        author_variant_reviews = [
            row
            for row in manual_rows
            if row.get("scope") == "author_printed_textual_variant_note"
        ]
        self.assertEqual(len(author_variant_reviews), 7)
        self.assertTrue(
            all(
                row["severity"] == "high"
                and row["status"] == "unresolved"
                and "author_text_sha256" in row["evidence"]
                and "author_text" not in row["evidence"]
                for row in author_variant_reviews
            )
        )
        author_form_reviews = [
            row
            for row in manual_rows
            if row.get("scope") == "author_printed_original_form_note"
        ]
        self.assertEqual(len(author_form_reviews), 329)
        self.assertTrue(
            all(
                row["severity"] == "medium"
                and row["status"] == "unresolved"
                and "author_text_sha256" in row["evidence"]
                and "author_text" not in row["evidence"]
                for row in author_form_reviews
            )
        )
        summary = json.loads(
            (REPORT / "generation_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(summary["author_comment_actionable_manual_review_count"], 336)
        gen_1_rows = [
            row
            for row in rows
            if row["target_ref"]
            in {"Gen.1.1", "Gen.1.2", "Gen.1.5", "Gen.1.6"}
            and row["exact_original_form_matches"]
        ]
        self.assertEqual(
            {row["target_ref"] for row in gen_1_rows},
            {"Gen.1.1", "Gen.1.2", "Gen.1.5", "Gen.1.6"},
        )
        by_mention = {
            mention["normalized"]: row
            for row in gen_1_rows
            for mention in row["transliteration_mentions"]
        }
        for mention, strong in {
            "shamayim": "H8064",
            "tehom": "H8415",
            "mayim": "H4325",
            "yom": "H3117",
            "rakia": "H7549",
        }.items():
            with self.subTest(mention=mention):
                self.assertIn(
                    strong,
                    {
                        code
                        for match in by_mention[mention][
                            "exact_original_form_matches"
                        ]
                        for code in match["strong_classic"]
                    },
                )
        penei_row = next(
            row
            for row in gen_1_rows
            if {item["normalized"] for item in row["transliteration_mentions"]}
            >= {"penei", "tehom"}
        )
        self.assertEqual(
            {
                code
                for match in penei_row["exact_original_form_matches"]
                for code in match["strong_classic"]
            },
            {"H5921", "H6440", "H8415"},
        )
        self.assertEqual(
            penei_row["review_status"],
            "author_original_form_matches_multiple_selected_tokens",
        )
        for name in (
            "gold_alignment.annotations.jsonl",
            "alignment_overrides.jsonl",
            "manual_review.jsonl",
        ):
            with self.subTest(name=name):
                path = REPORT / name
                lines = path.read_text(encoding="utf-8").splitlines()
                self.assertTrue(lines)
                for line in lines:
                    self.assertEqual(line, stable_json(json.loads(line)))


if __name__ == "__main__":
    unittest.main()

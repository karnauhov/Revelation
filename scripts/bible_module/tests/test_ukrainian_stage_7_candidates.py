"""CC0 focused tests for candidate-only Ukrainian stage-7 generators."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_candidates import (
    BRIDGE_GENERATOR_ID,
    CANDIDATE_CONTRACT_VERSION,
    GENERATOR_ORDER,
    LEGACY_GENERATOR_ID,
    LEXICAL_GENERATOR_ID,
    TRANSLITERATION_GENERATOR_ID,
    BridgeTargetBundle,
    _default_paths,
    build_generator_registry,
    generate_candidate_only_artifacts,
    generate_bridge_surface_candidates,
    generate_legacy_candidates,
    generate_lexical_morphological_candidates,
    generate_transliteration_candidates,
    load_context,
    load_ukrainian_greek_description_terms,
    stable_json,
    validate_candidate,
    validate_generator_registry,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "candidate_generator_cases.json"
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class CandidateGeneratorFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        if cls.fixture["license"] != "CC0-1.0":
            raise AssertionError("Candidate fixture must remain CC0")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.target_path = self.root / "targets.jsonl"
        self.original_path = self.root / "originals.jsonl"
        self.bridge_path = self.root / "bridges.jsonl"
        self.bridge_target_path = self.root / "bridge-target.tsv"
        self.legacy_path = self.root / "legacy.jsonl"
        _write_jsonl(self.target_path, self.fixture["target_tokens"])
        _write_jsonl(self.original_path, self.fixture["original_tokens"])
        _write_jsonl(self.bridge_path, self.fixture["bridge_records"])
        _write_jsonl(self.legacy_path, [self.fixture["legacy_verse"]])
        self.bridge_target_path.write_text(
            "".join("\t".join(row) + "\n" for row in self.fixture["bridge_target_tsv"]),
            encoding="utf-8",
            newline="\n",
        )
        self.context = load_context(self.target_path, self.original_path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_default_cli_consumes_the_fingerprint_selected_original_layer(self) -> None:
        paths = _default_paths(self.root)
        self.assertEqual(
            paths["original_universe"].name,
            "fingerprint_selected_original_layer.jsonl",
        )
        self.assertNotEqual(paths["original_universe"].name, "original_token_universe.jsonl")

    def _bridge_rows(self) -> tuple[list[dict[str, object]], dict[str, int]]:
        rows, counters = generate_bridge_surface_candidates(
            context=self.context,
            bridge_alignment_path=self.bridge_path,
            target_bundles=(
                BridgeTargetBundle(
                    family="RUSSYN",
                    scope="OT",
                    path=self.bridge_target_path,
                    source_id="fixture-russyn",
                ),
            ),
        )
        return list(rows), dict(counters)

    def test_bridge_preserves_full_group_and_all_nonpositional_ties(self) -> None:
        rows, counters = self._bridge_rows()
        self.assertEqual(len(rows), 3)
        grouped = next(row for row in rows if row["relation"] == "many_to_many")
        self.assertEqual(
            grouped["original_token_ids"], ["orig:adam", "orig:light"]
        )
        self.assertEqual(
            grouped["target_token_ids"],
            ["uk7:AAA:003:12:16", "uk7:AAA:004:17:21"],
        )
        repeated = [
            row
            for row in rows
            if row["original_token_ids"] == ["orig:adam"]
            and row["relation"] == "one_to_one"
        ]
        self.assertEqual(len(repeated), 2)
        self.assertTrue(all(row["manual_record_count"] == 2 for row in repeated))
        self.assertTrue(
            all(
                len(row["evidence"][0]["records"]) == 2
                for row in repeated
            )
        )
        self.assertTrue(
            all(
                {group["alternative_count"] for group in row["alternative_groups"]}
                == {2}
                for row in repeated
            )
        )
        self.assertTrue(
            all(
                {group["alternative_rank"] for group in row["alternative_groups"]}
                == {None}
                for row in repeated
            )
        )
        self.assertTrue(
            all(
                evidence.get("positional_tie_break") is False
                for row in repeated
                for evidence in row["evidence"]
                if evidence["kind"].startswith("exact_full_group")
            )
        )
        self.assertEqual(counters["skipped_no_full_surface_multiset"], 1)
        self.assertEqual(counters["skipped_bridge_target_ref_or_surface"], 1)
        self.assertEqual(counters["skipped_original_ref_or_textual_status"], 1)
        self.assertEqual(counters["coalesced_duplicate_evidence_occurrences"], 2)

    def test_every_bridge_candidate_is_fail_closed_and_verse_local(self) -> None:
        rows, _ = self._bridge_rows()
        for row in rows:
            validate_candidate(row, context=self.context)
            self.assertEqual(row["generator_id"], BRIDGE_GENERATOR_ID)
            self.assertFalse(row["auto_acceptance"])
            self.assertFalse(row["resolver_eligible"])
            self.assertNotIn("position_only", row["evidence_channels"])
            self.assertEqual(row["prohibited_assignment_methods_used"], [])
            self.assertTrue(
                all(
                    evidence.get("positional_tie_break") is not True
                    for evidence in row["evidence"]
                )
            )

    def test_legacy_rows_have_zero_vote_and_no_current_original_id(self) -> None:
        iterator, counters = generate_legacy_candidates(
            context=self.context,
            legacy_alignment_path=self.legacy_path,
        )
        rows = list(iterator)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["generator_id"], LEGACY_GENERATOR_ID)
        self.assertEqual(row["original_token_ids"], [])
        self.assertEqual(row["target_token_ids"], ["uk7:AAA:002:5:11"])
        self.assertEqual(row["vote_weight"], 0)
        self.assertEqual(row["legacy_current_original_crosswalk"], "forbidden_verse_bag_not_run")
        self.assertEqual(counters["emitted_candidates"], 1)

    def test_transliteration_is_direct_uncalibrated_and_excludes_empty_mark(self) -> None:
        iterator, counters = generate_transliteration_candidates(
            context=self.context,
            minimum_score=0.60,
            minimum_length=3,
        )
        rows = list(iterator)
        adam_rows = [row for row in rows if row["original_token_ids"] == ["orig:adam"]]
        self.assertEqual(len(adam_rows), 2)
        self.assertEqual(
            {row["target_token_ids"][0] for row in adam_rows},
            {"uk7:AAA:001:0:4", "uk7:AAA:005:22:26"},
        )
        self.assertTrue(all(row["generator_id"] == TRANSLITERATION_GENERATOR_ID for row in rows))
        self.assertTrue(all(row["generator_score"]["calibrated"] is False for row in rows))
        self.assertFalse(
            any("uk7:AAA:006:27:28" in row["target_token_ids"] for row in rows)
        )
        self.assertGreater(counters["evaluated_verse_local_pairs"], 0)

    def test_lexical_channel_requires_exact_direct_oh_token_evidence(self) -> None:
        database = self.root / "lexical.sqlite"
        connection = sqlite3.connect(database)
        connection.execute("CREATE TABLE db_metadata(key TEXT PRIMARY KEY,value TEXT)")
        connection.execute("CREATE TABLE greek_descs(id INTEGER PRIMARY KEY,desc TEXT)")
        connection.executemany(
            "INSERT INTO db_metadata VALUES (?,?)",
            [("schema_version", "fixture"), ("data_version", "fixture")],
        )
        connection.executemany(
            "INSERT INTO greek_descs VALUES (?,?)", self.fixture["greek_descriptions"]
        )
        connection.commit()
        connection.close()
        terms, metadata = load_ukrainian_greek_description_terms(database)
        iterator, counters = generate_lexical_morphological_candidates(
            context=self.context,
            description_terms=terms,
            lexical_source_id="fixture-uk-descriptions",
            lexical_source_sha256=metadata["database_sha256"],
        )
        rows = list(iterator)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["generator_id"], LEXICAL_GENERATOR_ID)
        self.assertEqual(row["original_token_ids"], ["orig:greek-see"])
        self.assertEqual(row["target_token_ids"], ["uk7:AAA:002:5:11"])
        self.assertFalse(row["independent_vote"])
        self.assertEqual(counters["emitted_candidates"], 1)

    def test_validator_rejects_auto_acceptance_and_dangling_ids(self) -> None:
        rows, _ = self._bridge_rows()
        invalid = dict(rows[0])
        invalid["auto_acceptance"] = True
        with self.assertRaisesRegex(ValueError, "cannot enable"):
            validate_candidate(invalid, context=self.context)
        dangling = dict(rows[0])
        dangling["target_token_ids"] = ["uk7:missing"]
        with self.assertRaisesRegex(ValueError, "dangling OH"):
            validate_candidate(dangling, context=self.context)
        stale_span = json.loads(stable_json(rows[0]))
        stale_span["target_spans"][0]["start_byte"] += 1
        with self.assertRaisesRegex(ValueError, "span offsets are stale"):
            validate_candidate(stale_span, context=self.context)

    def test_registry_is_versioned_digest_locked_and_external_model_free(self) -> None:
        digest = "a" * 64
        source_contract = {
            "version": "fixture-v1",
            "sha256": digest,
            "license": "CC0-1.0",
            "usage_status": "fixture",
        }
        source_contracts = {
            source_id: {"source_id": source_id, **source_contract}
            for source_id in (
                "clear_russyn_ot",
                "clear_russyn_nt",
                "clear_ylt_ot",
                "clear_ylt_nt_v010_transfer",
                "step_tahot",
                "step_tagnt",
                "ukrainian_stage_7_rejected_legacy_experiment",
                "stage6_synthesized_text",
                "local_revelation_uk_greek_descs",
            )
        }
        registry = build_generator_registry(
            input_sha256={"fixture": digest},
            source_contracts=source_contracts,
        )
        validate_generator_registry(registry)
        self.assertEqual(registry["candidate_contract_version"], CANDIDATE_CONTRACT_VERSION)
        self.assertEqual(
            [item["generator_id"] for item in registry["generators"]],
            list(GENERATOR_ORDER),
        )
        self.assertTrue(
            all(item["external_model"] is None for item in registry["generators"])
        )
        invalid = json.loads(stable_json(registry))
        invalid["generators"][0]["source_contracts"][0]["license"] = None
        with self.assertRaisesRegex(ValueError, "source contract is incomplete"):
            validate_generator_registry(invalid)

    def test_generation_is_deterministic(self) -> None:
        left, _ = self._bridge_rows()
        right, _ = self._bridge_rows()
        self.assertEqual(
            "".join(stable_json(row) + "\n" for row in left),
            "".join(stable_json(row) + "\n" for row in right),
        )

    def test_end_to_end_artifact_api_is_deterministic(self) -> None:
        database = self.root / "integration-lexical.sqlite"
        connection = sqlite3.connect(database)
        connection.execute("CREATE TABLE db_metadata(key TEXT PRIMARY KEY,value TEXT)")
        connection.execute("CREATE TABLE greek_descs(id INTEGER PRIMARY KEY,desc TEXT)")
        connection.executemany(
            "INSERT INTO db_metadata VALUES (?,?)",
            [("schema_version", "fixture"), ("data_version", "fixture")],
        )
        connection.executemany(
            "INSERT INTO greek_descs VALUES (?,?)", self.fixture["greek_descriptions"]
        )
        connection.commit()
        connection.close()

        digest = "b" * 64
        source_ids = (
            "clear_russyn_ot",
            "clear_russyn_nt",
            "clear_ylt_ot",
            "clear_ylt_nt_v010_transfer",
            "step_tahot_fixture",
            "step_tagnt_fixture",
            "ukrainian_stage_7_rejected_legacy_experiment",
            "stage6_synthesized_text",
            "local_revelation_uk_greek_descs",
        )
        registry_path = self.root / "source_registry.json"
        registry_path.write_text(
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
                        for source_id in source_ids
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        manifests = []
        for output_name in ("left", "right"):
            manifests.append(
                generate_candidate_only_artifacts(
                    token_inventory_path=self.target_path,
                    original_universe_path=self.original_path,
                    bridge_alignment_path=self.bridge_path,
                    bridge_target_bundles=(
                        BridgeTargetBundle(
                            "RUSSYN",
                            "OT",
                            self.bridge_target_path,
                            "clear_russyn_ot",
                        ),
                    ),
                    legacy_alignment_path=self.legacy_path,
                    ukrainian_greek_description_database=database,
                    source_registry_path=registry_path,
                    output_dir=self.root / output_name,
                )
            )
        self.assertEqual(manifests[0]["counts"]["total_candidates"], 7)
        self.assertEqual(manifests[0]["output_sha256"], manifests[1]["output_sha256"])
        with self.assertRaises(FileExistsError):
            generate_candidate_only_artifacts(
                token_inventory_path=self.target_path,
                original_universe_path=self.original_path,
                bridge_alignment_path=self.bridge_path,
                bridge_target_bundles=(
                    BridgeTargetBundle(
                        "RUSSYN",
                        "OT",
                        self.bridge_target_path,
                        "clear_russyn_ot",
                    ),
                ),
                legacy_alignment_path=self.legacy_path,
                ukrainian_greek_description_database=database,
                source_registry_path=registry_path,
                output_dir=self.root / "left",
            )


if __name__ == "__main__":
    unittest.main()

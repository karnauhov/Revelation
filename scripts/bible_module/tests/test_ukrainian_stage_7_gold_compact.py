from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_gold import (
    ingest_review_pass,
    prepare_reviewer_packets,
)
from scripts.bible_module.ukrainian_stage_7_gold_compact import (
    COMPACT_REVIEW_VERSION,
    check_compact_review,
    expand_compact_review,
    prepare_compact_review,
)
from scripts.bible_module.ukrainian_stage_7_gold_shards import (
    merge_review_shards,
    split_reviewer_packet,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    exact_word_tokens,
    sha256_text,
    stable_json,
)


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "gold_compact_review_cases.json"
)


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class GoldCompactReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _prepare_parent(self, root: Path) -> tuple[Path, Path]:
        text = self.fixture["plain_text"]
        target_tokens = [
            {
                "token_id": f"cc0:compact:target:{token.order}",
                "order": token.order,
                "surface": token.surface,
                "comparison": token.comparison,
                "start_scalar": token.start_scalar,
                "end_scalar": token.end_scalar,
                "start_byte": token.start_byte,
                "end_byte": token.end_byte,
            }
            for token in exact_word_tokens(text)
        ]
        originals = [
            {
                **row,
                "order": ordinal,
                "lemma": f"lemma-{ordinal}",
                "morphology": "CC0",
                "reading_status": "primary_mt",
            }
            for ordinal, row in enumerate(self.fixture["originals"], 1)
        ]
        strata = {
            "testament": "OT",
            "genre": "torah_prose_law",
            "mapping_operation": "merge",
            "textual_fingerprint_locus": True,
            "original_frequency_bands": ["rare_1_to_5", "frequent_1000_plus"],
        }
        panel = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "selection_id": "gold7:cc0:compact:verse",
            "target_ref": "Gen.1.1",
            "verse_key": "cc0-compact-verse",
            "book": "Gen",
            "testament": "OT",
            "plain_text_sha256": sha256_text(text),
            "comment_sha256": sha256_text(""),
            "original_token_ids": [row["original_token_id"] for row in originals],
            "projected_decision_count": len(originals),
            "strata": strata,
        }
        workbench = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "selection_id": panel["selection_id"],
            "target_ref": panel["target_ref"],
            "plain_text_nfc": text,
            "target_comment": "",
            "target_tokens": target_tokens,
            "original_tokens": originals,
            "strata": strata,
        }
        panel_path = root / "panel.jsonl"
        workbench_path = root / "workbench.jsonl"
        _write_jsonl(panel_path, [panel])
        _write_jsonl(workbench_path, [workbench])
        parent = root / "parent"
        prepare_reviewer_packets(
            panel_path=panel_path,
            workbench_path=workbench_path,
            output_dir=parent,
            minimum_verses=1,
            minimum_decisions=1,
            require_full_canon=False,
            _allow_cc0_fixture_without_immutable_corpus=True,
        )
        return (
            parent / "review_pass_1.packet.jsonl",
            parent / "gold_reviewer_packets.manifest.json",
        )

    def _prepare_compact(
        self, root: Path
    ) -> tuple[Path, Path, Path, Path]:
        packet, parent_manifest = self._prepare_parent(root)
        compact_dir = root / "compact"
        prepare_compact_review(
            packet_path=packet,
            packet_manifest_path=parent_manifest,
            output_dir=compact_dir,
        )
        return (
            packet,
            parent_manifest,
            compact_dir / "review_pass_1.compact.template.jsonl",
            compact_dir / "gold_compact_review.manifest.json",
        )

    def _filled(
        self,
        *,
        packet: Path,
        parent_manifest: Path,
        template: Path,
        compact_manifest: Path,
        reviewer: str = "reviewer-compact-a",
    ) -> list[dict[str, object]]:
        parent = json.loads(parent_manifest.read_text(encoding="utf-8"))
        template_row = _read_jsonl(template)[0]
        groups: list[dict[str, object]] = []
        for ordinal, fixture_group in enumerate(self.fixture["groups"], 1):
            groups.append(
                {
                    **fixture_group,
                    "severity": "high" if ordinal == 1 else "normal",
                    "evidence": [
                        {
                            "kind": "manual_token_context",
                            "evidence_id": f"cc0:compact:{reviewer}:group:{ordinal}",
                        }
                    ],
                    "rationale": "CC0 synthetic manual compact group rationale.",
                }
            )
        target_nulls = [
            {
                **row,
                "severity": "normal",
                "evidence": [
                    {
                        "kind": "manual_target_context",
                        "evidence_id": f"cc0:compact:{reviewer}:target-null:1",
                    }
                ],
                "rationale": "CC0 synthetic manual target-null rationale.",
            }
            for row in self.fixture["target_nulls"]
        ]
        return [
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "compact_review_version": COMPACT_REVIEW_VERSION,
                "record_type": "compact_review_metadata",
                "review_pass": 1,
                "reviewer_id": reviewer,
                "blind_to_other_pass": True,
                "packet_sha256": _sha(packet),
                "packet_manifest_sha256": _sha(parent_manifest),
                "input_sha256": parent["input_sha256"],
                "compact_template_sha256": _sha(template),
                "compact_manifest_sha256": _sha(compact_manifest),
            },
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "compact_review_version": COMPACT_REVIEW_VERSION,
                "record_type": "compact_review_verse_submission",
                "selection_id": template_row["selection_id"],
                "target_ref": template_row["target_ref"],
                "template_row_sha256": template_row["template_row_sha256"],
                "reviewer_id": reviewer,
                "groups": groups,
                "target_nulls": target_nulls,
            },
        ]

    def _expand(
        self, root: Path, *, reviewer: str = "reviewer-compact-a"
    ) -> tuple[Path, Path, Path, Path, Path]:
        packet, parent_manifest, template, compact_manifest = self._prepare_compact(
            root
        )
        filled = root / "manual-compact-submission.jsonl"
        _write_jsonl(
            filled,
            self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
                reviewer=reviewer,
            ),
        )
        expanded = root / "expanded" / "review-pass-1.jsonl"
        expand_compact_review(
            packet_path=packet,
            packet_manifest_path=parent_manifest,
            template_path=template,
            compact_manifest_path=compact_manifest,
            filled_path=filled,
            output_path=expanded,
        )
        return packet, parent_manifest, template, compact_manifest, expanded

    def _prepare_shard_compact(
        self, root: Path, *, review_pass: int = 1
    ) -> tuple[Path, dict[str, object], dict[str, object], Path, Path, Path]:
        packet, parent_manifest = self._prepare_parent(root)
        if review_pass == 2:
            packet = packet.with_name("review_pass_2.packet.jsonl")
        elif review_pass != 1:
            raise ValueError("CC0 compact helper supports only pass 1 or 2")
        shard_dir = root / "shards"
        shard_manifest = split_reviewer_packet(
            packet_path=packet,
            packet_manifest_path=parent_manifest,
            output_dir=shard_dir,
        )
        shard_manifest_path = (
            shard_dir / "gold_reviewer_packet_shards.manifest.json"
        )
        entry = shard_manifest["shards"][0]
        compact_dir = root / "compact-shard"
        prepare_compact_review(
            shard_manifest_path=shard_manifest_path,
            shard_id=entry["shard_id"],
            output_dir=compact_dir,
        )
        compact_manifest = compact_dir / "gold_compact_review.manifest.json"
        compact = json.loads(compact_manifest.read_text(encoding="utf-8"))
        return (
            shard_manifest_path,
            shard_manifest,
            entry,
            compact_dir / compact["template_name"],
            compact_manifest,
            shard_dir / entry["packet_file"],
        )

    def _filled_shard(
        self,
        *,
        shard_manifest_path: Path,
        shard_manifest: dict[str, object],
        entry: dict[str, object],
        template: Path,
        compact_manifest: Path,
        packet: Path,
        reviewer: str = "reviewer-shard-a",
    ) -> list[dict[str, object]]:
        rows = self._filled(
            packet=packet,
            parent_manifest=shard_manifest_path,
            template=template,
            compact_manifest=compact_manifest,
            reviewer=reviewer,
        )
        rows[0]["input_sha256"] = shard_manifest["parent_input_sha256"]
        rows[0]["review_pass"] = shard_manifest["review_pass"]
        rows[0].update(
            {
                "review_scope": "shard",
                "shard_contract_version": shard_manifest[
                    "shard_contract_version"
                ],
                "shard_id": entry["shard_id"],
                "shard_ordinal": entry["ordinal"],
                "shard_packet_sha256": entry["packet_sha256"],
                "shard_manifest_sha256": _sha(shard_manifest_path),
                "parent_packet_sha256": shard_manifest[
                    "parent_packet_sha256"
                ],
                "parent_packet_manifest_sha256": shard_manifest[
                    "parent_packet_manifest_sha256"
                ],
            }
        )
        return rows

    def test_prepare_is_deterministic_answer_free_and_nonoverwriting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            packet1, manifest1, template1, compact1 = self._prepare_compact(first)
            _, _, template2, compact2 = self._prepare_compact(second)
            self.assertEqual(_sha(template1), _sha(template2))
            self.assertEqual(_sha(compact1), _sha(compact2))
            row = _read_jsonl(template1)[0]
            self.assertEqual(row["reviewer_answers"], {"groups": [], "target_nulls": []})
            encoded = stable_json(row).lower()
            for prohibited in ("candidate", "legacy", "confidence", "score"):
                self.assertNotIn(prohibited, encoded)
            self.assertEqual(len(row["original_index"]), 7)
            self.assertEqual(len(row["target_index"]), 7)
            self.assertEqual(
                row["original_index"][0]["display"]["transliteration_raw"],
                "alpha-translit",
            )
            self.assertEqual(
                row["original_index"][0]["display"]["gloss_raw"],
                "first synthetic gloss",
            )
            self.assertEqual(
                row["original_index"][0]["display"]["source_locator"],
                "CC0.1.1#01",
            )
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                prepare_compact_review(
                    packet_path=packet1,
                    packet_manifest_path=manifest1,
                    output_dir=template1.parent,
                )

    def test_expand_is_deterministic_checkable_and_ingest_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, parent_manifest, template, compact_manifest, expanded = self._expand(
                root / "first"
            )
            _, _, _, _, expanded2 = self._expand(root / "second")
            self.assertEqual(_sha(expanded), _sha(expanded2))
            result = check_compact_review(
                packet_path=packet,
                packet_manifest_path=parent_manifest,
                template_path=template,
                compact_manifest_path=compact_manifest,
                expanded_path=expanded,
            )
            self.assertEqual(
                result["status"],
                "valid_compact_review_and_ingest_ready_expansion",
            )
            normalized = root / "normalized.jsonl"
            ingested = ingest_review_pass(
                review_pass=1,
                packet_path=packet,
                packet_manifest_path=parent_manifest,
                submission_path=expanded,
                output_path=normalized,
            )
            self.assertEqual(ingested["counts"]["original_decisions"], 7)
            self.assertEqual(ingested["counts"]["target_accounting"], 7)
            records = _read_jsonl(expanded)
            original_relations = {
                row["relation"]
                for row in records
                if row["record_type"] == "original_decision"
            }
            self.assertTrue(
                {"one_to_many", "many_to_one", "many_to_many", "original_omitted"}
                <= original_relations
            )
            addition = next(
                row
                for row in records
                if row.get("target_status") == "translation_addition"
            )
            self.assertEqual(addition["linked_original_token_ids"], [])

    def test_exact_once_original_and_target_accounting_is_mandatory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, parent_manifest, template, compact_manifest = self._prepare_compact(root)
            base = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            missing_original = deepcopy(base)
            missing_original[1]["groups"] = missing_original[1]["groups"][:-1]
            for label, rows, pattern in (
                ("missing-original", missing_original, "exact-once original"),
                (
                    "missing-target",
                    deepcopy(base),
                    "exact-once target",
                ),
                (
                    "duplicate-target",
                    deepcopy(base),
                    "accounted more than once",
                ),
            ):
                if label == "missing-target":
                    rows[1]["target_nulls"] = []
                if label == "duplicate-target":
                    rows[1]["groups"][3]["target_indices"].append("t002")
                filled = root / f"{label}.jsonl"
                _write_jsonl(filled, rows)
                with self.assertRaisesRegex(ValueError, pattern):
                    expand_compact_review(
                        packet_path=packet,
                        packet_manifest_path=parent_manifest,
                        template_path=template,
                        compact_manifest_path=compact_manifest,
                        filled_path=filled,
                        output_path=root / f"{label}.expanded.jsonl",
                    )

    def test_cardinality_verse_local_ids_and_manual_evidence_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, parent_manifest, template, compact_manifest = self._prepare_compact(root)
            cases: list[tuple[str, list[dict[str, object]], str]] = []
            cardinality = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            cardinality[1]["groups"][1]["relation"] = "one_to_one"
            cases.append(("cardinality", cardinality, "one_to_one cardinality"))
            nonlocal_index = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            nonlocal_index[1]["groups"][0]["original_indices"] = ["o999"]
            cases.append(("nonlocal", nonlocal_index, "non-local original"))
            no_evidence = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            no_evidence[1]["groups"][0]["evidence"] = []
            cases.append(("no-evidence", no_evidence, "lacks evidence/rationale"))
            injected_id = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            injected_id[1]["groups"][0]["target_token_ids"] = ["foreign:target"]
            cases.append(("injected-id", injected_id, "unknown/prohibited fields"))
            for label, rows, pattern in cases:
                filled = root / f"{label}.jsonl"
                _write_jsonl(filled, rows)
                with self.assertRaisesRegex(ValueError, pattern):
                    expand_compact_review(
                        packet_path=packet,
                        packet_manifest_path=parent_manifest,
                        template_path=template,
                        compact_manifest_path=compact_manifest,
                        filled_path=filled,
                        output_path=root / f"{label}.expanded.jsonl",
                    )

    def test_stale_tampered_identity_and_output_overwrite_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, parent_manifest, template, compact_manifest = self._prepare_compact(root)
            rows = self._filled(
                packet=packet,
                parent_manifest=parent_manifest,
                template=template,
                compact_manifest=compact_manifest,
            )
            stale = deepcopy(rows)
            stale[0]["compact_template_sha256"] = "0" * 64
            stale_path = root / "stale.jsonl"
            _write_jsonl(stale_path, stale)
            with self.assertRaisesRegex(ValueError, "stale identity/pass/SHA locks"):
                expand_compact_review(
                    packet_path=packet,
                    packet_manifest_path=parent_manifest,
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    filled_path=stale_path,
                    output_path=root / "stale-expanded.jsonl",
                )
            bad_reviewer = deepcopy(rows)
            bad_reviewer[0]["reviewer_id"] = "placeholder reviewer"
            bad_reviewer[1]["reviewer_id"] = "placeholder reviewer"
            bad_path = root / "bad-reviewer.jsonl"
            _write_jsonl(bad_path, bad_reviewer)
            with self.assertRaisesRegex(ValueError, "stable 3-128"):
                expand_compact_review(
                    packet_path=packet,
                    packet_manifest_path=parent_manifest,
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    filled_path=bad_path,
                    output_path=root / "bad-reviewer-expanded.jsonl",
                )
            filled = root / "valid.jsonl"
            _write_jsonl(filled, rows)
            output = root / "valid-expanded.jsonl"
            expand_compact_review(
                packet_path=packet,
                packet_manifest_path=parent_manifest,
                template_path=template,
                compact_manifest_path=compact_manifest,
                filled_path=filled,
                output_path=output,
            )
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                expand_compact_review(
                    packet_path=packet,
                    packet_manifest_path=parent_manifest,
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    filled_path=filled,
                    output_path=output,
                )
            output.write_text(
                output.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "differs from its SHA chain"):
                check_compact_review(
                    packet_path=packet,
                    packet_manifest_path=parent_manifest,
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    expanded_path=output,
                )

    def test_tampered_template_fails_before_any_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet, parent_manifest, template, compact_manifest = self._prepare_compact(root)
            template.write_text(
                template.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "differs from its manifest"):
                check_compact_review(
                    packet_path=packet,
                    packet_manifest_path=parent_manifest,
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                )

    def test_shard_prepare_expand_check_and_merge_preserve_exact_provenance(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                shard_manifest_path,
                shard_manifest,
                entry,
                template,
                compact_manifest,
                packet,
            ) = self._prepare_shard_compact(root)
            (_, _, _, template2, compact_manifest2, _) = (
                self._prepare_shard_compact(root / "deterministic-second")
            )
            self.assertEqual(_sha(template), _sha(template2))
            self.assertEqual(_sha(compact_manifest), _sha(compact_manifest2))
            template_rows = _read_jsonl(template)
            self.assertEqual(len(template_rows), entry["verse_count"])
            self.assertEqual(
                sum(len(row["original_index"]) for row in template_rows),
                entry["original_decision_count"],
            )
            self.assertEqual(
                sum(len(row["target_index"]) for row in template_rows),
                entry["target_accounting_count"],
            )
            for row in template_rows:
                self.assertEqual(
                    [item["index"] for item in row["original_index"]],
                    [
                        f"o{index:03d}"
                        for index in range(1, len(row["original_index"]) + 1)
                    ],
                )
                self.assertEqual(
                    [item["index"] for item in row["target_index"]],
                    [
                        f"t{index:03d}"
                        for index in range(1, len(row["target_index"]) + 1)
                    ],
                )
                self.assertEqual(
                    row["reviewer_answers"], {"groups": [], "target_nulls": []}
                )
                keys: set[str] = set()

                def collect(value: object) -> None:
                    if isinstance(value, dict):
                        for key, child in value.items():
                            keys.add(str(key).casefold())
                            collect(child)
                    elif isinstance(value, list):
                        for child in value:
                            collect(child)

                collect(row)
                self.assertFalse(
                    any(
                        fragment in key
                        for key in keys
                        for fragment in (
                            "candidate",
                            "legacy",
                            "score",
                            "confidence",
                            "label",
                            "other_reviewer",
                            "prior_annotation",
                        )
                    )
                )

            filled = root / "filled-shard.jsonl"
            _write_jsonl(
                filled,
                self._filled_shard(
                    shard_manifest_path=shard_manifest_path,
                    shard_manifest=shard_manifest,
                    entry=entry,
                    template=template,
                    compact_manifest=compact_manifest,
                    packet=packet,
                ),
            )
            expanded = root / "expanded-shard.jsonl"
            expand_compact_review(
                shard_manifest_path=shard_manifest_path,
                shard_id=entry["shard_id"],
                template_path=template,
                compact_manifest_path=compact_manifest,
                filled_path=filled,
                output_path=expanded,
            )
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                expand_compact_review(
                    shard_manifest_path=shard_manifest_path,
                    shard_id=entry["shard_id"],
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    filled_path=filled,
                    output_path=expanded,
                )
            checked = check_compact_review(
                shard_manifest_path=shard_manifest_path,
                shard_id=entry["shard_id"],
                template_path=template,
                compact_manifest_path=compact_manifest,
                expanded_path=expanded,
            )
            self.assertEqual(
                checked["status"],
                "valid_compact_shard_review_and_merge_ready_expansion",
            )
            expanded_rows = _read_jsonl(expanded)
            metadata = expanded_rows[0]
            self.assertEqual(metadata["shard_id"], entry["shard_id"])
            self.assertEqual(metadata["reviewer_id"], "reviewer-shard-a")
            for row in expanded_rows[1:]:
                self.assertEqual(row["reviewer_id"], "reviewer-shard-a")
            merged = root / "merged-pass.jsonl"
            merged_manifest = merge_review_shards(
                shard_manifest_path=shard_manifest_path,
                submission_paths=[expanded],
                output_path=merged,
            )
            self.assertEqual(merged_manifest["counts"]["shards"], 1)
            self.assertEqual(
                merged_manifest["reviewer_roster"],
                [
                    {
                        "reviewer_id": "reviewer-shard-a",
                        "shard_ids": [entry["shard_id"]],
                    }
                ],
            )

    def test_shard_wrong_id_pass_and_nonoverwrite_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                shard_manifest_path,
                shard_manifest,
                entry,
                template,
                compact_manifest,
                packet,
            ) = self._prepare_shard_compact(root)
            with self.assertRaisesRegex(ValueError, "Unknown frozen"):
                prepare_compact_review(
                    shard_manifest_path=shard_manifest_path,
                    shard_id="gold7:p1:shard:999:Missing-Missing",
                    output_dir=root / "wrong-shard",
                )
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                prepare_compact_review(
                    shard_manifest_path=shard_manifest_path,
                    shard_id=entry["shard_id"],
                    output_dir=template.parent,
                )
            rows = self._filled_shard(
                shard_manifest_path=shard_manifest_path,
                shard_manifest=shard_manifest,
                entry=entry,
                template=template,
                compact_manifest=compact_manifest,
                packet=packet,
            )
            rows[0]["review_pass"] = 2
            wrong_pass = root / "wrong-pass.jsonl"
            _write_jsonl(wrong_pass, rows)
            with self.assertRaisesRegex(ValueError, "stale identity/pass/SHA"):
                expand_compact_review(
                    shard_manifest_path=shard_manifest_path,
                    shard_id=entry["shard_id"],
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                    filled_path=wrong_pass,
                    output_path=root / "wrong-pass-expanded.jsonl",
                )

    def test_second_blind_pass_shard_expands_with_distinct_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                shard_manifest_path,
                shard_manifest,
                entry,
                template,
                compact_manifest,
                packet,
            ) = self._prepare_shard_compact(root, review_pass=2)
            filled = root / "pass2-filled.jsonl"
            _write_jsonl(
                filled,
                self._filled_shard(
                    shard_manifest_path=shard_manifest_path,
                    shard_manifest=shard_manifest,
                    entry=entry,
                    template=template,
                    compact_manifest=compact_manifest,
                    packet=packet,
                    reviewer="reviewer-shard-b",
                ),
            )
            expanded = root / "pass2-expanded.jsonl"
            expand_compact_review(
                shard_manifest_path=shard_manifest_path,
                shard_id=entry["shard_id"],
                template_path=template,
                compact_manifest_path=compact_manifest,
                filled_path=filled,
                output_path=expanded,
            )
            result = check_compact_review(
                shard_manifest_path=shard_manifest_path,
                shard_id=entry["shard_id"],
                template_path=template,
                compact_manifest_path=compact_manifest,
                expanded_path=expanded,
            )
            self.assertEqual(
                result["status"],
                "valid_compact_shard_review_and_merge_ready_expansion",
            )
            metadata = _read_jsonl(expanded)[0]
            self.assertEqual(metadata["review_pass"], 2)
            self.assertEqual(metadata["reviewer_id"], "reviewer-shard-b")
            self.assertTrue(metadata["blind_to_other_pass"])
            for prohibited in (
                "other_pass_sha256",
                "other_reviewer_id",
                "prior_annotations_sha256",
            ):
                self.assertNotIn(prohibited, metadata)

    def test_shard_stale_manifest_and_template_tamper_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (
                shard_manifest_path,
                _,
                entry,
                template,
                compact_manifest,
                _,
            ) = self._prepare_shard_compact(root)
            stale_manifest = json.loads(
                shard_manifest_path.read_text(encoding="utf-8")
            )
            stale_manifest["parent_packet_manifest_sha256"] = "0" * 64
            stale_path = shard_manifest_path.with_name("stale-shards.manifest.json")
            stale_path.write_text(
                stable_json(stale_manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "stale source SHA locks"):
                prepare_compact_review(
                    shard_manifest_path=stale_path,
                    shard_id=entry["shard_id"],
                    output_dir=root / "stale-output",
                )
            incomplete = json.loads(
                shard_manifest_path.read_text(encoding="utf-8")
            )
            incomplete["parent_packet_sha256"] = "0" * 64
            incomplete["input_sha256"]["parent_packet"] = "0" * 64
            incomplete_path = shard_manifest_path.with_name(
                "incomplete-shards.manifest.json"
            )
            incomplete_path.write_text(
                stable_json(incomplete) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "exactly reconstruct"):
                prepare_compact_review(
                    shard_manifest_path=incomplete_path,
                    shard_id=entry["shard_id"],
                    output_dir=root / "incomplete-output",
                )
            template.write_text(
                template.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "differs from its manifest"):
                check_compact_review(
                    shard_manifest_path=shard_manifest_path,
                    shard_id=entry["shard_id"],
                    template_path=template,
                    compact_manifest_path=compact_manifest,
                )


if __name__ == "__main__":
    unittest.main()

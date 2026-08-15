from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_gold import (
    finalize_gold,
    ingest_review_pass,
    prepare_reviewer_packets,
)
from scripts.bible_module.ukrainian_stage_7_gold_shards import (
    merge_review_shards,
    parse_book_ranges,
    split_reviewer_packet,
    validate_merged_pass_independence,
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


class GoldShardWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["license"], "CC0-1.0")

    def _prepare_parent(self, root: Path) -> tuple[Path, Path, Path]:
        panels: list[dict[str, object]] = []
        workbenches: list[dict[str, object]] = []
        source_surfaces = self.fixture["plain_text"].split()
        for index, (book, surface) in enumerate(
            (("Gen", source_surfaces[0]), ("Exod", source_surfaces[1])), 1
        ):
            target_ref = f"{book}.1.1"
            selection_id = f"gold7:cc0:{book}"
            verse_key = f"cc0-{book.lower()}"
            original_id = f"cc0:{book.lower()}:original:1"
            token = exact_word_tokens(surface)[0]
            target_token = {
                "token_id": f"cc0:{book.lower()}:target:1",
                "order": token.order,
                "surface": token.surface,
                "comparison": token.comparison,
                "start_scalar": token.start_scalar,
                "end_scalar": token.end_scalar,
                "start_byte": token.start_byte,
                "end_byte": token.end_byte,
            }
            strata = {
                "testament": "OT",
                "genre": "torah_prose_law",
                "mapping_operation": "1:1",
                "textual_fingerprint_locus": index == 1,
                "original_frequency_bands": [
                    "rare_1_to_5" if index == 1 else "frequent_1000_plus"
                ],
            }
            panels.append(
                {
                    "schema_version": 1,
                    "contract_version": CONTRACT_VERSION,
                    "selection_id": selection_id,
                    "target_ref": target_ref,
                    "verse_key": verse_key,
                    "book": book,
                    "testament": "OT",
                    "plain_text_sha256": sha256_text(surface),
                    "comment_sha256": sha256_text(""),
                    "original_token_ids": [original_id],
                    "projected_decision_count": 1,
                    "strata": strata,
                }
            )
            workbenches.append(
                {
                    "schema_version": 1,
                    "contract_version": CONTRACT_VERSION,
                    "selection_id": selection_id,
                    "target_ref": target_ref,
                    "plain_text_nfc": surface,
                    "target_comment": "",
                    "target_tokens": [target_token],
                    "original_tokens": [
                        {
                            "original_token_id": original_id,
                            "order": 1,
                            "surface_normalized": f"source-{index}",
                            "strong_classic": [f"H{index}"],
                            "reading_status": "primary_mt",
                        }
                    ],
                    "strata": strata,
                }
            )
        panel_path = root / "panel.jsonl"
        workbench_path = root / "workbench.jsonl"
        _write_jsonl(panel_path, panels)
        _write_jsonl(workbench_path, workbenches)
        packet_dir = root / "parent"
        prepare_reviewer_packets(
            panel_path=panel_path,
            workbench_path=workbench_path,
            output_dir=packet_dir,
            minimum_verses=2,
            minimum_decisions=2,
            require_full_canon=False,
            _allow_cc0_fixture_without_immutable_corpus=True,
        )
        return (
            packet_dir / "review_pass_1.packet.jsonl",
            packet_dir / "review_pass_2.packet.jsonl",
            packet_dir / "gold_reviewer_packets.manifest.json",
        )

    def _split(
        self, packet: Path, parent_manifest: Path, output_dir: Path
    ) -> tuple[dict[str, object], Path]:
        manifest = split_reviewer_packet(
            packet_path=packet,
            packet_manifest_path=parent_manifest,
            output_dir=output_dir,
        )
        return manifest, output_dir / "gold_reviewer_packet_shards.manifest.json"

    def _submission(
        self,
        *,
        shard_manifest: dict[str, object],
        shard_manifest_path: Path,
        entry: dict[str, object],
        reviewer: str,
        output_path: Path,
    ) -> Path:
        packet_path = shard_manifest_path.parent / entry["packet_file"]
        packet_rows = _read_jsonl(packet_path)
        output: list[dict[str, object]] = [
            {
                "record_type": "review_metadata",
                "review_pass": shard_manifest["review_pass"],
                "reviewer_id": reviewer,
                "blind_to_other_pass": True,
                "shard_id": entry["shard_id"],
                "shard_packet_sha256": entry["packet_sha256"],
                "shard_manifest_sha256": _sha(shard_manifest_path),
                "parent_packet_sha256": shard_manifest["parent_packet_sha256"],
                "parent_packet_manifest_sha256": shard_manifest[
                    "parent_packet_manifest_sha256"
                ],
                "input_sha256": shard_manifest["parent_input_sha256"],
            }
        ]
        for packet in packet_rows:
            original_request = packet["original_decision_requests"][0]
            target_request = packet["target_accounting_requests"][0]
            original_id = original_request["original_token_id"]
            target_id = target_request["target_token_id"]
            output.extend(
                [
                    {
                        "record_type": "original_decision",
                        "decision_status": "decided",
                        "decision_id": original_request["decision_id"],
                        "original_token_id": original_id,
                        "target_ref": packet["target_ref"],
                        "relation": "one_to_one",
                        "group_original_token_ids": [original_id],
                        "target_token_ids": [target_id],
                        "null_reason": None,
                        "severity": "normal",
                        "phenomena": [],
                        "evidence": [
                            {
                                "kind": "manual_token_context",
                                "evidence_id": f"cc0:{reviewer}:{original_id}",
                            }
                        ],
                        "rationale": "CC0 synthetic shard decision.",
                    },
                    {
                        "record_type": "target_accounting",
                        "decision_status": "decided",
                        "accounting_id": target_request["accounting_id"],
                        "target_token_id": target_id,
                        "target_ref": packet["target_ref"],
                        "target_status": "aligned",
                        "linked_original_token_ids": [original_id],
                        "severity": "normal",
                        "phenomena": [],
                        "evidence": [
                            {
                                "kind": "manual_target_context",
                                "evidence_id": f"cc0:{reviewer}:{target_id}",
                            }
                        ],
                        "rationale": "CC0 synthetic shard target accounting.",
                    },
                ]
            )
        _write_jsonl(output_path, output)
        return output_path

    def _merge_pass(
        self,
        *,
        root: Path,
        packet: Path,
        parent_manifest: Path,
        reviewers: dict[str, str],
        label: str,
    ) -> tuple[Path, Path, dict[str, object], Path, list[Path]]:
        shard_dir = root / f"shards-{label}"
        shard_manifest, shard_manifest_path = self._split(
            packet, parent_manifest, shard_dir
        )
        submissions: list[Path] = []
        for entry in shard_manifest["shards"]:
            book = entry["books"][0]
            submissions.append(
                self._submission(
                    shard_manifest=shard_manifest,
                    shard_manifest_path=shard_manifest_path,
                    entry=entry,
                    reviewer=reviewers[book],
                    output_path=root / f"{label}-{book}.submission.jsonl",
                )
            )
        merged = root / f"{label}.merged.jsonl"
        merge_review_shards(
            shard_manifest_path=shard_manifest_path,
            submission_paths=submissions,
            output_path=merged,
        )
        return merged, shard_manifest_path, shard_manifest, shard_dir, submissions

    def test_split_exact_coverage_ranges_and_determinism(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, _, parent_manifest = self._prepare_parent(root)
            first, _ = self._split(packet1, parent_manifest, root / "split-a")
            second, _ = self._split(packet1, parent_manifest, root / "split-b")
            self.assertEqual(first, second)
            self.assertEqual(first["counts"]["shards"], 2)
            self.assertEqual(first["counts"]["selected_verses"], 2)
            self.assertEqual(first["counts"]["primary_original_decisions"], 2)
            self.assertEqual(first["counts"]["target_token_accounting_decisions"], 2)
            for left, right in zip(first["shards"], second["shards"], strict=True):
                self.assertEqual(left["packet_sha256"], right["packet_sha256"])
            combined_dir = root / "combined"
            combined = split_reviewer_packet(
                packet_path=packet1,
                packet_manifest_path=parent_manifest,
                output_dir=combined_dir,
                book_ranges=parse_book_ranges(["Gen-Exod"]),
            )
            self.assertEqual(combined["counts"]["shards"], 1)
            with self.assertRaisesRegex(ValueError, "exactly cover"):
                split_reviewer_packet(
                    packet_path=packet1,
                    packet_manifest_path=parent_manifest,
                    output_dir=root / "bad-range",
                    book_ranges=parse_book_ranges(["Gen-Gen"]),
                )
            with self.assertRaisesRegex(ValueError, "Overlapping"):
                parse_book_ranges(["Gen-Exod", "Exod-Lev"])

    def test_merge_rejects_missing_duplicate_and_incomplete_shards(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, _, parent_manifest = self._prepare_parent(root)
            _, shard_manifest_path, _, _, submissions = self._merge_pass(
                root=root,
                packet=packet1,
                parent_manifest=parent_manifest,
                reviewers={"Gen": "reviewer-a", "Exod": "reviewer-b"},
                label="pass1",
            )
            with self.assertRaisesRegex(ValueError, "missing"):
                merge_review_shards(
                    shard_manifest_path=shard_manifest_path,
                    submission_paths=submissions[:1],
                    output_path=root / "missing.jsonl",
                )
            with self.assertRaisesRegex(ValueError, "duplicate"):
                merge_review_shards(
                    shard_manifest_path=shard_manifest_path,
                    submission_paths=[submissions[0], submissions[0], submissions[1]],
                    output_path=root / "duplicate.jsonl",
                )
            incomplete_rows = _read_jsonl(submissions[0])[:-1]
            _write_jsonl(submissions[0], incomplete_rows)
            with self.assertRaisesRegex(ValueError, "target-token accounting"):
                merge_review_shards(
                    shard_manifest_path=shard_manifest_path,
                    submission_paths=submissions,
                    output_path=root / "incomplete.jsonl",
                )

    def test_per_decision_independence_is_mandatory_in_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, parent_manifest = self._prepare_parent(root)
            merged1, _, _, _, _ = self._merge_pass(
                root=root,
                packet=packet1,
                parent_manifest=parent_manifest,
                reviewers={"Gen": "reviewer-shared", "Exod": "reviewer-a"},
                label="pass1",
            )
            merged2, _, _, _, _ = self._merge_pass(
                root=root,
                packet=packet2,
                parent_manifest=parent_manifest,
                reviewers={"Gen": "reviewer-shared", "Exod": "reviewer-b"},
                label="pass2",
            )
            normalized1 = root / "normalized1.jsonl"
            normalized2 = root / "normalized2.jsonl"
            ingest_review_pass(
                review_pass=1,
                packet_path=packet1,
                packet_manifest_path=parent_manifest,
                submission_path=merged1,
                output_path=normalized1,
            )
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=parent_manifest,
                submission_path=merged2,
                output_path=normalized2,
            )
            with self.assertRaisesRegex(ValueError, "Reviewer independence failed"):
                validate_merged_pass_independence(
                    pass1_path=merged1, pass2_path=merged2
                )
            with self.assertRaisesRegex(ValueError, "distinct reviewers"):
                finalize_gold(
                    pass1_path=normalized1,
                    pass2_path=normalized2,
                    packet_manifest_path=parent_manifest,
                    report_dir=root / "rejected-final",
                    minimum_verses=2,
                    minimum_decisions=2,
                    required_phenomena=set(),
                    required_relations=set(),
                )

    def test_distinct_shard_reviewers_survive_ingest_and_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, packet2, parent_manifest = self._prepare_parent(root)
            merged1, _, _, _, _ = self._merge_pass(
                root=root,
                packet=packet1,
                parent_manifest=parent_manifest,
                reviewers={"Gen": "reviewer-a", "Exod": "reviewer-b"},
                label="pass1",
            )
            merged2, _, _, _, _ = self._merge_pass(
                root=root,
                packet=packet2,
                parent_manifest=parent_manifest,
                reviewers={"Gen": "reviewer-c", "Exod": "reviewer-d"},
                label="pass2",
            )
            independence = validate_merged_pass_independence(
                pass1_path=merged1, pass2_path=merged2
            )
            self.assertEqual(
                independence["status"],
                "independent_reviewers_for_every_stable_decision",
            )
            normalized1 = root / "normalized1.jsonl"
            normalized2 = root / "normalized2.jsonl"
            ingest_review_pass(
                review_pass=1,
                packet_path=packet1,
                packet_manifest_path=parent_manifest,
                submission_path=merged1,
                output_path=normalized1,
            )
            ingest_review_pass(
                review_pass=2,
                packet_path=packet2,
                packet_manifest_path=parent_manifest,
                submission_path=merged2,
                output_path=normalized2,
            )
            final = root / "final"
            manifest = finalize_gold(
                pass1_path=normalized1,
                pass2_path=normalized2,
                packet_manifest_path=parent_manifest,
                report_dir=final,
                minimum_verses=2,
                minimum_decisions=2,
                required_phenomena=set(),
                required_relations=set(),
            )
            self.assertEqual(
                manifest["counts"]["accepted_assignment_or_null_decisions"], 2
            )
            originals = [
                row
                for row in _read_jsonl(final / "gold_alignment.annotations.jsonl")
                if row["record_type"] == "original_decision"
            ]
            reviewers = {
                row["target_ref"]: (row["review"]["pass_1"], row["review"]["pass_2"])
                for row in originals
            }
            self.assertEqual(reviewers["Gen.1.1"], ("reviewer-a", "reviewer-c"))
            self.assertEqual(reviewers["Exod.1.1"], ("reviewer-b", "reviewer-d"))
            target_reviewers = {
                row["target_ref"]: (row["review"]["pass_1"], row["review"]["pass_2"])
                for row in _read_jsonl(final / "gold_alignment.annotations.jsonl")
                if row["record_type"] == "target_accounting"
            }
            self.assertEqual(
                target_reviewers,
                {
                    "Gen.1.1": ("reviewer-a", "reviewer-c"),
                    "Exod.1.1": ("reviewer-b", "reviewer-d"),
                },
            )

    def test_tamper_and_stale_shard_sha_chains_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet1, _, parent_manifest = self._prepare_parent(root)
            merged, shard_manifest_path, shard_manifest, shard_dir, submissions = (
                self._merge_pass(
                    root=root,
                    packet=packet1,
                    parent_manifest=parent_manifest,
                    reviewers={"Gen": "reviewer-a", "Exod": "reviewer-b"},
                    label="pass1",
                )
            )
            stale_rows = _read_jsonl(submissions[0])
            stale_rows[0]["input_sha256"] = dict(stale_rows[0]["input_sha256"])
            stale_rows[0]["input_sha256"]["stage6_text"] = "0" * 64
            _write_jsonl(submissions[0], stale_rows)
            with self.assertRaisesRegex(ValueError, "SHA input locks differ"):
                merge_review_shards(
                    shard_manifest_path=shard_manifest_path,
                    submission_paths=submissions,
                    output_path=root / "stale.jsonl",
                )

            entry = shard_manifest["shards"][1]
            shard_packet = shard_dir / entry["packet_file"]
            shard_packet.write_text(
                shard_packet.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "differs from its manifest"):
                merge_review_shards(
                    shard_manifest_path=shard_manifest_path,
                    submission_paths=[
                        self._submission(
                            shard_manifest=shard_manifest,
                            shard_manifest_path=shard_manifest_path,
                            entry=shard_manifest["shards"][0],
                            reviewer="reviewer-a",
                            output_path=root / "fresh-gen.jsonl",
                        ),
                        submissions[1],
                    ],
                    output_path=root / "tampered-shard.jsonl",
                )

            # The already merged full pass is also SHA-chained into its sidecar;
            # arbitrary post-merge edits cannot enter normal pass ingestion.
            merged.write_text(
                merged.read_text(encoding="utf-8") + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "merge SHA chain"):
                ingest_review_pass(
                    review_pass=1,
                    packet_path=packet1,
                    packet_manifest_path=parent_manifest,
                    submission_path=merged,
                    output_path=root / "normalized.jsonl",
                )


if __name__ == "__main__":
    unittest.main()

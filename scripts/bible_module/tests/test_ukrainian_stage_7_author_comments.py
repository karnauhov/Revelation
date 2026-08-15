from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_author_comments import (
    OUTPUT_NAME,
    _sha256_file,
    classify_author_comment,
    generate_author_comment_evidence,
    original_script_form,
    transliteration_form,
    validate_author_comment_evidence_bundle,
)
from scripts.bible_module.ukrainian_stage_7_model import sha256_text, stable_json


FIXTURE = (
    Path(__file__).parent
    / "fixtures/ukrainian_stage_7/author_comment_evidence_cases.json"
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


class AuthorCommentPureContractTest(unittest.TestCase):
    def test_cc0_classification_cases(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(payload["license"], "CC0-1.0")
        for case in payload["cases"]:
            with self.subTest(case=case["id"]):
                actual = classify_author_comment(case["text"])
                self.assertEqual(actual["languages"], case["expected_languages"])
                self.assertEqual(actual["categories"], case["expected_categories"])
                if "expected_transliteration" in case:
                    self.assertIn(
                        case["expected_transliteration"],
                        [item["normalized"] for item in actual["transliteration_mentions"]],
                    )

    def test_transliteration_profile_matches_author_and_tahot_forms(self) -> None:
        pairs = (
            ("šamajim", "sha.Ma.yim"),
            ("majim", "ma.Yim"),
            ("jom", "Yom"),
            ("Rakia", "ra.Ki.a'"),
            ("tehom", "te.Hom"),
            ("pnej", "pe.Nei"),
            ("pnei", "pe.Nei"),
        )
        for author, source in pairs:
            with self.subTest(author=author):
                self.assertEqual(
                    transliteration_form(author), transliteration_form(source)
                )

    def test_original_script_profile_preserves_letters_and_removes_marks(self) -> None:
        self.assertEqual(original_script_form("λόγος"), "λογοσ")
        self.assertEqual(original_script_form("שָׁמַיִם"), "שמים")
        analysis = classify_author_comment("Грецьке λόγος — джерельна форма.")
        self.assertIn("original_script_source_form", analysis["categories"])
        self.assertEqual(
            analysis["original_script_mentions"][0]["normalized"], "λογοσ"
        )


class AuthorCommentBundleTest(unittest.TestCase):
    def _generate(self, root: Path) -> tuple[dict, dict[str, str]]:
        definitions = root / "definitions.jsonl"
        uses = root / "uses.jsonl"
        headings = root / "headings.jsonl"
        comments = root / "comments.jsonl"
        tokens = root / "tokens.jsonl"
        originals = root / "originals.jsonl"
        output = root / "output"
        note_text = "По-гебрейському šamajim уживається в множині."
        _write_jsonl(
            definitions,
            [
                {"footnote_id": "fn1", "full_text_nfc": note_text, "definition_order": 1},
                {"footnote_id": "fn2", "full_text_nfc": "Коротка примітка до заголовка.", "definition_order": 2},
            ],
        )
        _write_jsonl(
            uses,
            [
                {
                    "use_id": "use1",
                    "footnote_id": "fn1",
                    "full_text_nfc": note_text,
                    "source_order": 1,
                    "target_ref": "Gen.1.1",
                    "target_anchor": {"start_scalar": 4, "end_scalar": 4},
                    "anchor_status": "resolved_by_proven_source_target_interval",
                    "mapping_rule_id": "fixture-rule",
                    "operation": "1:1",
                    "marker": "1",
                    "provenance": {
                        "page": 1,
                        "title": "CC0 fixture",
                        "source_path": "fixture.json",
                        "input_sha256": "0" * 64,
                        "source_revision": "1" * 64,
                        "revision_id": 7,
                    },
                }
            ],
        )
        _write_jsonl(
            headings,
            [
                {
                    "use_id": "use2",
                    "footnote_id": "fn2",
                    "full_text_nfc": "Коротка примітка до заголовка.",
                    "source_order": 2,
                    "anchor_status": "non_verse_source_material",
                    "provenance": {"page": 2, "title": "CC0 fixture", "input_sha256": "0" * 64},
                }
            ],
        )
        comment = "1 " + note_text
        _write_jsonl(
            comments,
            [{"target_ref": "Gen.1.1", "target_comment": comment, "comment_sha256": sha256_text(comment), "use_ids": ["use1"]}],
        )
        _write_jsonl(
            tokens,
            [{"target_ref": "Gen.1.1", "token_id": "uk7:fixture:1", "start_scalar": 0, "end_scalar": 4}],
        )
        _write_jsonl(
            originals,
            [
                {
                    "target_ref": "Gen.1.1",
                    "original_token_id": "tahot:fixture:g01:a01",
                    "source_family": "TAHOT",
                    "source_locator": "Gen.1.1#01=L",
                    "surface_raw": "fixture-hebrew",
                    "transliteration_raw": "sha.Ma.yim",
                    "strong_classic": ["H8064"],
                    "reading_status": "primary_mt",
                    "selection_kind": "resolved_primary_raw_component",
                }
            ],
        )
        paths = {
            "footnote_definitions": definitions,
            "footnote_uses": uses,
            "heading_footnotes": headings,
            "stage6_target_comments": comments,
            "ukrainian_token_inventory": tokens,
            "fingerprint_selected_original_layer": originals,
        }
        locks = {key: _sha256_file(path) for key, path in paths.items()}
        manifest = generate_author_comment_evidence(
            footnote_definitions_path=definitions,
            footnote_uses_path=uses,
            heading_footnotes_path=headings,
            target_comments_path=comments,
            token_inventory_path=tokens,
            selected_original_layer_path=originals,
            output_dir=output,
            expected_input_sha256=locks,
        )
        return manifest, locks

    def test_bundle_is_complete_zero_vote_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            manifest, locks = self._generate(root)
            self.assertEqual(manifest["processed_count"], 2)
            self.assertEqual(manifest["selection_mutation_count"], 0)
            rows = [json.loads(line) for line in (root / "output" / OUTPUT_NAME).read_text(encoding="utf-8").splitlines()]
            verse = next(row for row in rows if row["scope"] == "verse")
            self.assertEqual(verse["candidate_vote_weight"], 0)
            self.assertFalse(verse["auto_assignment_allowed"])
            self.assertFalse(verse["alignment_input_allowed"])
            self.assertEqual(verse["review_status"], "author_original_form_uniquely_corroborates_selected_token")
            self.assertEqual(verse["exact_marker_boundary"]["preceding_target_token_ids"], ["uk7:fixture:1"])
            self.assertEqual(verse["exact_original_form_matches"][0]["original_token_id"], "tahot:fixture:g01:a01")
            self.assertEqual(verse["author_text_nfc"], "По-гебрейському šamajim уживається в множині.")
            self.assertEqual(sha256_text(verse["author_text_nfc"]), verse["author_text_sha256"])
            self.assertEqual(verse["source_input_sha256"], "0" * 64)
            self.assertEqual(verse["source_revision_lock_sha256"], "1" * 64)
            self.assertEqual(verse["source_revision_id"], 7)
            self.assertEqual(verse["source_path"], "fixture.json")
            validate_author_comment_evidence_bundle(output_dir=root / "output", expected_input_sha256=locks)
            first = (root / "output" / OUTPUT_NAME).read_bytes()
            self._generate(root)
            self.assertEqual(first, (root / "output" / OUTPUT_NAME).read_bytes())

    def test_stale_input_lock_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            _manifest, locks = self._generate(root)
            locks["footnote_uses"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "input digest changed"):
                validate_author_comment_evidence_bundle(output_dir=root / "output", expected_input_sha256=locks)

    def test_unused_definition_and_wrong_comment_ref_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._generate(root)
            uses = root / "uses.jsonl"
            _write_jsonl(uses, [])
            paths = {
                "footnote_definitions": root / "definitions.jsonl",
                "footnote_uses": uses,
                "heading_footnotes": root / "headings.jsonl",
                "stage6_target_comments": root / "comments.jsonl",
                "ukrainian_token_inventory": root / "tokens.jsonl",
                "fingerprint_selected_original_layer": root / "originals.jsonl",
            }
            locks = {key: _sha256_file(path) for key, path in paths.items()}
            with self.assertRaisesRegex(ValueError, "not fully accounted"):
                generate_author_comment_evidence(
                    footnote_definitions_path=paths["footnote_definitions"],
                    footnote_uses_path=uses,
                    heading_footnotes_path=paths["heading_footnotes"],
                    target_comments_path=paths["stage6_target_comments"],
                    token_inventory_path=paths["ukrainian_token_inventory"],
                    selected_original_layer_path=paths[
                        "fingerprint_selected_original_layer"
                    ],
                    output_dir=root / "unused-output",
                    expected_input_sha256=locks,
                )

            self._generate(root)
            comment = json.loads((root / "comments.jsonl").read_text(encoding="utf-8"))
            comment["target_ref"] = "Gen.1.2"
            _write_jsonl(root / "comments.jsonl", [comment])
            locks["footnote_uses"] = _sha256_file(root / "uses.jsonl")
            locks["stage6_target_comments"] = _sha256_file(root / "comments.jsonl")
            with self.assertRaisesRegex(ValueError, "wrong target comment"):
                generate_author_comment_evidence(
                    footnote_definitions_path=paths["footnote_definitions"],
                    footnote_uses_path=root / "uses.jsonl",
                    heading_footnotes_path=paths["heading_footnotes"],
                    target_comments_path=root / "comments.jsonl",
                    token_inventory_path=paths["ukrainian_token_inventory"],
                    selected_original_layer_path=paths[
                        "fingerprint_selected_original_layer"
                    ],
                    output_dir=root / "wrong-ref-output",
                    expected_input_sha256=locks,
                )

    def test_manifest_counter_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            manifest, locks = self._generate(root)
            manifest["counts"]["scope.verse"] += 1
            (root / "output" / "author_comment_evidence.manifest.json").write_text(
                stable_json(manifest) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "counter changed"):
                validate_author_comment_evidence_bundle(
                    output_dir=root / "output", expected_input_sha256=locks
                )

    def test_partial_source_form_match_requires_manual_scope(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self._generate(root)
            definitions = [
                json.loads(line)
                for line in (root / "definitions.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            uses = [
                json.loads(line)
                for line in (root / "uses.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            note_text = "В ориґіналі šamajim та qwerty."
            definitions[0]["full_text_nfc"] = note_text
            uses[0]["full_text_nfc"] = note_text
            comment = "1 " + note_text
            _write_jsonl(root / "definitions.jsonl", definitions)
            _write_jsonl(root / "uses.jsonl", uses)
            _write_jsonl(
                root / "comments.jsonl",
                [
                    {
                        "target_ref": "Gen.1.1",
                        "target_comment": comment,
                        "comment_sha256": sha256_text(comment),
                        "use_ids": ["use1"],
                    }
                ],
            )
            paths = {
                "footnote_definitions": root / "definitions.jsonl",
                "footnote_uses": root / "uses.jsonl",
                "heading_footnotes": root / "headings.jsonl",
                "stage6_target_comments": root / "comments.jsonl",
                "ukrainian_token_inventory": root / "tokens.jsonl",
                "fingerprint_selected_original_layer": root / "originals.jsonl",
            }
            locks = {key: _sha256_file(path) for key, path in paths.items()}
            generate_author_comment_evidence(
                footnote_definitions_path=paths["footnote_definitions"],
                footnote_uses_path=paths["footnote_uses"],
                heading_footnotes_path=paths["heading_footnotes"],
                target_comments_path=paths["stage6_target_comments"],
                token_inventory_path=paths["ukrainian_token_inventory"],
                selected_original_layer_path=paths[
                    "fingerprint_selected_original_layer"
                ],
                output_dir=root / "partial-output",
                expected_input_sha256=locks,
            )
            rows = [
                json.loads(line)
                for line in (root / "partial-output" / OUTPUT_NAME)
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            verse = next(row for row in rows if row["scope"] == "verse")
            self.assertEqual(
                verse["review_status"],
                "partial_original_form_match_requires_manual_scope",
            )
            self.assertEqual(
                [item["normalized"] for item in verse["unmatched_transliteration_mentions"]],
                ["qwerty"],
            )


if __name__ == "__main__":
    unittest.main()

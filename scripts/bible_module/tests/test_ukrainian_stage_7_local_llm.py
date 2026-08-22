from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.bible_module.ukrainian_stage_7_local_llm import (
    _canonicalize_answer_format,
    _completion_messages,
    _parse_response_json,
    _prompt_view,
    _response_content,
    _response_reasoning_content,
    _response_token_counts,
    _validate_answer,
    _write_run_progress,
)
from scripts.bible_module.ukrainian_stage_7_local_llm_batch import (
    _link_null_signature,
    _same_index_signal,
)


def _evidence(identifier: str) -> list[dict[str, str]]:
    return [{"kind": "local_llm_token_context", "evidence_id": identifier}]


class UkrainianStage7LocalLlmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.template = {
            "original_index": [{"index": "o001"}, {"index": "o002"}],
            "target_index": [{"index": "t001"}, {"index": "t002"}],
        }
        self.answer = {
            "groups": [
                {
                    "original_indices": ["o001", "o002"],
                    "target_indices": ["t001"],
                    "relation": "many_to_one",
                    "null_reason": None,
                    "severity": "high",
                    "phenomena": ["merge"],
                    "evidence": _evidence("o001+o002->t001"),
                    "rationale": "Two originals form one Ukrainian expression.",
                }
            ],
            "target_nulls": [
                {
                    "target_index": "t002",
                    "target_status": "function_token",
                    "severity": "normal",
                    "phenomena": ["function_token"],
                    "evidence": _evidence("t002:null"),
                    "rationale": "Ukrainian grammar supplies the function token.",
                }
            ],
        }

    def test_exact_many_to_one_and_target_null_are_accepted(self) -> None:
        groups, target_nulls = _validate_answer(self.answer, self.template)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(target_nulls), 1)

    def test_missing_original_is_rejected_fail_closed(self) -> None:
        self.answer["groups"][0]["original_indices"] = ["o001"]
        self.answer["groups"][0]["relation"] = "one_to_one"
        with self.assertRaisesRegex(ValueError, "Original exact accounting differs"):
            _validate_answer(self.answer, self.template)

    def test_empty_phenomena_is_rejected(self) -> None:
        self.answer["groups"][0]["phenomena"] = []
        with self.assertRaisesRegex(ValueError, "phenomena must be nonempty"):
            _validate_answer(self.answer, self.template)

    def test_cardinality_labels_and_grouped_omissions_are_repaired_without_links(self) -> None:
        answer = {
            "groups": [
                {
                    "original_indices": ["o001", "o002"],
                    "target_indices": ["t001", "t002"],
                    "relation": "one_to_many",
                    "null_reason": None,
                    "severity": "normal",
                    "phenomena": ["merge"],
                    "evidence": _evidence("fixture"),
                    "rationale": "Fixture.",
                },
                {
                    "original_indices": ["o003", "o004"],
                    "target_indices": [],
                    "relation": "original_omitted",
                    "null_reason": "translation_omission",
                    "severity": "normal",
                    "phenomena": ["omission"],
                    "evidence": _evidence("fixture-null"),
                    "rationale": "Fixture null.",
                },
            ],
            "target_nulls": [],
        }
        normalized, repairs = _canonicalize_answer_format(answer)
        self.assertEqual(normalized["groups"][0]["relation"], "many_to_many")
        self.assertEqual(normalized["groups"][1]["original_indices"], ["o003"])
        self.assertEqual(normalized["groups"][2]["original_indices"], ["o004"])
        self.assertEqual(repairs["relation_one_to_many_to_many_to_many"], 1)
        self.assertEqual(repairs["split_multi_original_omission"], 1)

    def test_non_semantic_response_wrappers_and_evidence_id_lists_are_repaired(self) -> None:
        parsed, parse_repairs = _parse_response_json(
            "<think>private analysis</think>\n```json\n"
            '{"groups":[],"target_nulls":[]}\n```'
        )
        self.assertEqual(parsed, {"groups": [], "target_nulls": []})
        self.assertEqual(parse_repairs["reasoning_prefix_removed"], 1)
        self.assertEqual(parse_repairs["markdown_json_fence_removed"], 1)
        answer = {
            "groups": [
                {
                    "original_indices": ["o001"],
                    "target_indices": ["t001"],
                    "relation": "one_to_one",
                    "evidence": [
                        {
                            "kind": "local_llm_token_context",
                            "evidence_id": ["o001", "t001"],
                        }
                    ],
                }
            ],
            "target_nulls": [],
        }
        normalized, repairs = _canonicalize_answer_format(answer)
        self.assertEqual(
            normalized["groups"][0]["evidence"][0]["evidence_id"],
            "o001|t001",
        )
        self.assertEqual(repairs["evidence_id_string_list_joined"], 1)

    def test_malformed_wrapper_or_evidence_is_not_guessed(self) -> None:
        with self.assertRaises(json.JSONDecodeError):
            _parse_response_json("commentary\n```json\n{}\n```")
        answer = {
            "groups": [
                {
                    "original_indices": ["o001"],
                    "target_indices": ["t001"],
                    "relation": "one_to_one",
                    "evidence": [
                        {
                            "kind": "local_llm_token_context",
                            "evidence_id": ["o001", 7],
                        }
                    ],
                }
            ],
            "target_nulls": [],
        }
        normalized, repairs = _canonicalize_answer_format(answer)
        self.assertEqual(
            normalized["groups"][0]["evidence"][0]["evidence_id"],
            ["o001", 7],
        )
        self.assertFalse(repairs)

    def test_response_requires_exactly_one_text_choice(self) -> None:
        self.assertEqual(
            _response_content({"choices": [{"message": {"content": '{"ok":true}'}}]}),
            '{"ok":true}',
        )
        with self.assertRaises(ValueError):
            _response_content({"choices": []})

    def test_reasoning_content_and_usage_are_auditable(self) -> None:
        response = {
            "choices": [
                {"message": {"content": "{}", "reasoning_content": "private trace"}}
            ]
        }
        self.assertEqual(_response_reasoning_content(response), "private trace")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "0001.attempt-1.json"
            path.write_text(
                json.dumps(
                    {
                        "response_usage": {
                            "prompt_tokens": 10,
                            "completion_tokens": 7,
                            "completion_tokens_details": {"reasoning_tokens": 3},
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                _response_token_counts(Path(temp)),
                {"prompt_tokens": 10, "completion_tokens": 7, "reasoning_tokens": 3},
            )

    def test_retry_context_includes_previous_answer_before_validation_error(self) -> None:
        messages = _completion_messages(
            user_prompt="frozen verse",
            validation_error="missing t002",
            previous_content='{"groups":[],"target_nulls":[]}',
        )
        self.assertEqual([row["role"] for row in messages], ["system", "user", "assistant", "user"])
        self.assertIn("missing t002", messages[-1]["content"])
        with self.assertRaisesRegex(ValueError, "previous completion"):
            _completion_messages(user_prompt="verse", validation_error="invalid")

    def test_prompt_view_keeps_linguistic_context_and_removes_strong_and_ids(self) -> None:
        template = {
            "target_ref": "Fixture.1.1",
            "book": "Fixture",
            "testament": "OT",
            "plain_text_nfc": "Текст",
            "target_comment": "Коментар",
            "original_index": [
                {
                    "index": "o001",
                    "decision_id": "secret-decision-id",
                    "original_token_id": "secret-token-id",
                    "display": {
                        "surface_raw": "אב",
                        "lemma_raw": "lemma",
                        "gloss_raw": "gloss",
                        "strong_raw": ["H1"],
                        "mapping_rule_id": "hidden-rule",
                    },
                }
            ],
            "target_index": [
                {
                    "index": "t001",
                    "order": 1,
                    "surface": "Текст",
                    "comparison": "текст",
                    "target_token_id": "secret-target-id",
                }
            ],
        }
        prompt = _prompt_view(template)
        serialized = json.dumps(prompt, ensure_ascii=False)
        self.assertIn("Коментар", serialized)
        self.assertIn("lemma", serialized)
        self.assertNotIn("H1", serialized)
        self.assertNotIn("secret", serialized)

    def test_link_null_signature_ignores_rationale_but_not_links(self) -> None:
        first = {
            "record_type": "original_decision",
            "relation": "many_to_one",
            "group_original_token_ids": ["o2", "o1"],
            "target_token_ids": ["t1"],
            "null_reason": None,
            "rationale": "first",
        }
        second = {**first, "rationale": "second"}
        self.assertEqual(_link_null_signature(first), _link_null_signature(second))
        second["target_token_ids"] = ["t2"]
        self.assertNotEqual(_link_null_signature(first), _link_null_signature(second))

    def test_same_index_signal_counts_position_collapse(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "compact.jsonl"
            rows = [
                {
                    "record_type": "compact_review_verse_submission",
                    "groups": [
                        {
                            "relation": "one_to_one",
                            "original_indices": ["o001"],
                            "target_indices": ["t001"],
                        },
                        {
                            "relation": "one_to_one",
                            "original_indices": ["o002"],
                            "target_indices": ["t003"],
                        },
                    ],
                }
            ]
            path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            signal = _same_index_signal(path)
            self.assertEqual(signal["one_to_one_groups"], 2)
            self.assertEqual(signal["same_local_index_groups"], 1)
            self.assertEqual(signal["same_local_index_ratio"], 0.5)

    def test_progress_files_are_updated_per_verse(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            task = {
                "task_id": "fixture-task",
                "review_pass": 2,
                "reviewer_id": "fixture-reviewer",
            }
            progress = _write_run_progress(
                run_dir=run_dir,
                task=task,
                run_id="run_1",
                total=4,
                completed=1,
                failed=0,
                current_ref="Fixture.1.1",
                started=0.0,
                status="running_local_blind_review",
            )
            self.assertEqual(progress["counts"]["verses_remaining"], 3)
            self.assertTrue((run_dir / "progress.json").is_file())
            self.assertIn("1 / 4", (run_dir / "STATUS.ru.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

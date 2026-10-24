"""Synthetic, first-party fixtures; no source corpus is redistributed here."""

from __future__ import annotations

import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.bible_module import build_ohienko_1988 as builder
from scripts.bible_module.ukrainian_stage_2_contract import build_ukrainian_schema_contract
from scripts.bible_module.ukrainian_stage_6_model import (
    CONTRACT_VERSION, MAPPING_CONTRACT_VERSION, sha256_text,
)


def fixture():
    texts, comments = [], []
    grid = [("001", "Gen.1.1"), ("002", "Gen.1.2")]
    for order, (key, ref) in enumerate(grid, 1):
        base = {"verse_key": key, "target_ref": ref, "order": order,
                "contract_version": CONTRACT_VERSION, "schema_version": 1}
        text = f"Тестовий вірш {order}."
        texts.append({**base, "plain_text_nfc": text, "plain_text_sha256": sha256_text(text),
                      "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                      "operation": "1:1", "rule_id": f"rule-{order}"})
        comment = "1 Тестова примітка." if order == 1 else ""
        comments.append({**base, "target_comment": comment,
                         "comment_sha256": sha256_text(comment),
                         "use_ids": ["u1"] if order == 1 else []})
    uses = [{"use_id": "u1", "target_ref": "Gen.1.1", "target_order": 1,
             "contract_version": CONTRACT_VERSION,
             "mapping_contract_version": MAPPING_CONTRACT_VERSION,
             "anchor_status": "resolved_by_proven_source_target_interval",
             "mapping_rule_id": "rule-1", "target_anchor": {"start_scalar": 5, "end_scalar": 5},
             "marker": "1", "full_text_nfc": "Тестова примітка.", "source_order": 1}]
    return texts, comments, uses, grid


class InputValidationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = fixture()

    def test_exact_text_comment_and_statistics(self):
        rows, stats = builder.validate_rows(*self.inputs)
        self.assertEqual(rows[0], ("001", "Тестовий вірш 1.", "1 Тестова примітка."))
        self.assertEqual(rows[1][2], "")
        self.assertEqual(stats["totals"]["verses"], 2)
        self.assertEqual(stats["totals"]["words"], 6)
        self.assertEqual(stats["totals"]["footnote_uses"], 1)

    def test_missing_duplicate_reordered_and_extra_rows(self):
        for index in (0, 1):
            for mode in ("missing", "duplicate", "reverse", "extra"):
                with self.subTest(index=index, mode=mode):
                    data = copy.deepcopy(self.inputs)
                    if mode == "missing": data[index].pop()
                    elif mode == "duplicate": data[index][1] = data[index][0]
                    elif mode == "reverse": data[index].reverse()
                    else: data[index].append(copy.deepcopy(data[index][0]))
                    with self.assertRaises(ValueError): builder.validate_rows(*data)

    def test_null_empty_corrupt_text_and_invalid_strong_fail(self):
        for value in (None, "", " ", "Змінено", "Тест G1.", "Тест H0"):
            with self.subTest(value=value):
                data = copy.deepcopy(self.inputs)
                data[0][0]["plain_text_nfc"] = value
                if isinstance(value, str): data[0][0]["plain_text_sha256"] = sha256_text(value)
                if value == "Змінено": data[0][0]["plain_text_sha256"] = "bad"
                with self.assertRaises(ValueError): builder.validate_rows(*data)

    def test_missing_rule_and_contract_fail(self):
        for key, value in (("rule_id", ""), ("operation", "guess"),
                           ("mapping_contract_version", "other"), ("contract_version", "other")):
            data = copy.deepcopy(self.inputs)
            data[0][0][key] = value
            with self.assertRaises(ValueError): builder.validate_rows(*data)

    def test_missing_null_lost_and_rebound_comments_fail(self):
        for mode in ("null", "missing", "lost", "digest", "rebound", "wrong_text", "strong"):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.inputs)
                comment = data[1][0]
                if mode == "null": comment["target_comment"] = None
                elif mode == "missing": del comment["target_comment"]
                elif mode == "lost": comment["use_ids"] = []
                elif mode == "digest": comment["comment_sha256"] = "bad"
                elif mode == "rebound": data[1].reverse()
                else:
                    comment["target_comment"] = "Примітка G1" if mode == "strong" else "Інша примітка"
                    comment["comment_sha256"] = sha256_text(comment["target_comment"])
                with self.assertRaises(ValueError): builder.validate_rows(*data)

    def test_duplicate_unproved_outside_and_wrong_anchor_uses_fail(self):
        for mode in ("duplicate", "unproved", "outside", "anchor", "rule", "order"):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.inputs)
                use = data[2][0]
                if mode == "duplicate": data[2].append(copy.deepcopy(use))
                elif mode == "unproved": use["anchor_status"] = "nearest"
                elif mode == "outside": use["target_ref"] = "Gen.2.1"
                elif mode == "anchor": use["target_anchor"]["end_scalar"] = 1000
                elif mode == "rule": use["mapping_rule_id"] = "other"
                else: use["target_order"] = 2
                with self.assertRaises(ValueError): builder.validate_rows(*data)

    def test_corrupted_source_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "synthesized_text.jsonl").write_text("corrupted", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Sealed input changed"):
                builder.load_inputs(work)


class DatabaseBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name) / "candidate.sqlite"
        self.schema = build_ukrainian_schema_contract()["schema"]
        self.rows, _ = builder.validate_rows(*fixture())
        self.info = json.loads((builder.PROJECT_ROOT / "scripts/bible_module/reports/oh1988_text_release/info.json").read_text(encoding="utf-8"))
        self.date = "2026-10-24T12:00:00Z"

    def build(self, **kwargs):
        return builder.build_database(self.target, self.rows, self.info, self.schema,
                                      data_version=1, built_at=self.date, **kwargs)

    def test_round_trip_schema_metadata_and_read_only_audit(self):
        result = self.build()
        self.assertEqual(result["verified_verses"], 2)
        self.assertIsNone(result["backup_path"])
        before = self.target.read_bytes()
        again = builder.audit_database(self.target, self.rows, self.info, self.schema, 1, self.date)
        self.assertEqual(before, self.target.read_bytes())
        self.assertEqual(again["sha256"], result["sha256"])

    def test_date_independent_semantics_and_byte_reproducibility(self):
        first = self.build()
        same = Path(self.temporary.name) / "same.sqlite"
        second = builder.build_database(same, self.rows, self.info, self.schema,
                                        data_version=1, built_at=self.date)
        self.assertEqual(self.target.read_bytes(), same.read_bytes())
        later = builder.build_database(Path(self.temporary.name) / "later.sqlite", self.rows, self.info,
                                       self.schema, data_version=1, built_at="2026-10-25T12:00:00Z")
        self.assertEqual(first["semantic_sha256_without_build_date"], later["semantic_sha256_without_build_date"])
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertNotEqual(first["sha256"], later["sha256"])

    def test_existing_target_requires_explicit_replacement_and_verified_backup(self):
        self.target.write_bytes(b"existing database")
        with self.assertRaises(FileExistsError): self.build()
        result = self.build(replace=True)
        self.assertEqual(Path(result["backup_path"]).read_bytes(), b"existing database")
        self.assertNotEqual(self.target.read_bytes(), b"existing database")

    def test_validation_and_replace_errors_preserve_target(self):
        self.target.write_bytes(b"existing database")
        for failure in ("audit", "replace"):
            with self.subTest(failure=failure):
                with patch.object(builder, "audit_database", side_effect=ValueError("audit")) if failure == "audit" else patch("scripts.bible_module.build_ohienko_1988.os.replace", side_effect=OSError("replace")):
                    with self.assertRaises((ValueError, OSError)): self.build(replace=True)
                self.assertEqual(self.target.read_bytes(), b"existing database")
                self.assertEqual(list(self.target.parent.glob(".oh1988-*")), [])

    def test_invalid_output_rows_and_metadata_preserve_target(self):
        self.target.write_bytes(b"existing database")
        for rows in ([], self.rows[::-1], [self.rows[0], self.rows[0]],
                     [("001", "", "")], [("001", "Текст", None)], [("001", "Текст G1", "")]):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    builder.build_database(self.target, rows, self.info, self.schema,
                                           data_version=1, built_at=self.date, replace=True)
                self.assertEqual(self.target.read_bytes(), b"existing database")
        for version, date in ((0, self.date), (True, self.date), (1, "bad"), (1, "2026-10-24")):
            with self.assertRaises(ValueError):
                builder.build_database(self.target, self.rows, self.info, self.schema,
                                       data_version=version, built_at=date, replace=True)

    def test_tampering_is_found_by_full_readback(self):
        self.build()
        with closing(sqlite3.connect(self.target)) as connection:
            connection.execute("UPDATE verses SET comment='wrong' WHERE verse_key='001'")
            connection.commit()
        with self.assertRaisesRegex(ValueError, "text/comment/key"):
            builder.audit_database(self.target, self.rows, self.info, self.schema, 1, self.date)

    def test_info_is_exact_edition_and_nonempty(self):
        for field, value in (("module_id", "ukrainian"), ("license", ""), ("language", "ru")):
            info = {**self.info, field: value}
            with self.assertRaises(ValueError): builder.validate_info(info)


if __name__ == "__main__":
    unittest.main()

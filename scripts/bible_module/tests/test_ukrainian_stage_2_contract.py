from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import string
import unittest
from pathlib import Path

from scripts.bible_module import build_kjv, build_lxx_tr
from scripts.bible_module.canon import CANONICAL_BOOKS, canonical_verses
from scripts.bible_module.ukrainian_stage_2_contract import (
    APPLICATION_SCHEMA_VERSION,
    DEFAULT_BASELINE_PATH,
    FINAL_IDENTIFIERS,
    INFO_DESCRIPTION,
    INFO_LICENSE,
    INFO_SOURCE_SUMMARY_PLACEHOLDERS,
    INFO_SOURCE_SUMMARY_TEMPLATE,
    MODULE_CODE,
    MODULE_FILENAME,
    MODULE_ID,
    PROJECT_ROOT,
    TARGET_CHAPTERS_COUNT,
    TARGET_VERSE_KEYS_COUNT,
    TARGET_VERSES_COUNT,
    build_baseline_manifest,
    load_baseline_manifest,
    render_final_identifiers_csv,
    schema_snapshot,
)
from scripts.bible_module.ukrainian_strong import (
    StrongContractError,
    normalize_classic_strong,
    normalize_strong_for_output,
    strong_contract_manifest,
)
from scripts.content_tool.bible_map import BibleCatalog
from scripts.content_tool.mixins.bibles import BIBLE_MODULE_DB_SCHEMA_VERSION


class UkrainianStage2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = load_baseline_manifest()

    def test_checked_in_baseline_is_exactly_reproducible(self) -> None:
        self.assertEqual(build_baseline_manifest(), self.baseline)

    def test_reference_database_schema_metadata_info_and_keys_are_locked(
        self,
    ) -> None:
        reference = self.baseline["reference_database"]
        target_grid = self.baseline["target_grid"]

        self.assertEqual(
            reference["sha256"],
            "b105f174c37c6703b71831a99ff838fed3439b84132c743bd3b58b37a326c780",
        )
        self.assertEqual(
            reference["schema"]["fingerprint_sha256"],
            "e14d4e2b2727122240f3765104cf4e2d63f789d5904be6aa3766cf761f5583b8",
        )
        self.assertEqual(reference["pragma_user_version"], 3)
        self.assertEqual(
            reference["db_metadata"],
            {
                "data_version": "6",
                "date": "2026-07-25T07:16:08Z",
                "schema_version": "3",
            },
        )
        self.assertEqual(reference["info"]["code"], "KJV")
        self.assertEqual(reference["info"]["module_id"], "kjv")
        self.assertEqual(reference["info"]["canon"], "protestant_66")
        self.assertEqual(
            reference["info"]["versification"],
            "kjv_protestant",
        )
        self.assertEqual(reference["verse_rows"], TARGET_VERSES_COUNT)
        self.assertEqual(
            reference["nonempty_verse_rows"],
            TARGET_VERSES_COUNT,
        )
        self.assertEqual(
            len(target_grid["verse_keys"]),
            TARGET_VERSE_KEYS_COUNT,
        )
        self.assertEqual(target_grid["verse_keys"][0], "001")
        self.assertEqual(target_grid["verse_keys"][-1], "NZY")
        self.assertEqual(
            target_grid["verse_key_sequence_sha256"],
            "43324c450e6158f77ea92eedbc9d6dc0df60184dee43ce14eac27baa0dae6e60",
        )
        self.assertEqual(
            target_grid["canonical_reference_sequence_sha256"],
            "5d4cd6efdb51ca99d6affa9cb924cf63c5bc8f9f7a46dea375dbb7b8a05cdf23",
        )
        self.assertEqual(
            target_grid["verse_key_reference_pair_sequence_sha256"],
            "6e3ce3af65ec2ecee9edbf1d261917398d943534e772a5458d0117102c6187e4",
        )

    def test_canon_app_map_and_content_tool_have_identical_target_order(
        self,
    ) -> None:
        target_grid = self.baseline["target_grid"]
        catalog = BibleCatalog.load(PROJECT_ROOT)
        canon_refs = [
            verse.canonical_ref
            for verse in canonical_verses()
        ]
        map_refs: list[str] = []
        content_tool_keys: list[str] = []
        for book in catalog.books:
            for chapter, verse_count in enumerate(book.chapters, start=1):
                for verse in range(1, verse_count + 1):
                    map_refs.append(f"{book.code}.{chapter}.{verse}")
                    content_tool_keys.append(
                        catalog.key_for(
                            book_id=book.id,
                            chapter=chapter,
                            verse=verse,
                        )
                    )

        self.assertEqual(len(CANONICAL_BOOKS), 66)
        self.assertEqual(
            sum(len(book.chapter_verse_counts) for book in CANONICAL_BOOKS),
            TARGET_CHAPTERS_COUNT,
        )
        self.assertEqual(canon_refs, map_refs)
        self.assertEqual(content_tool_keys, target_grid["verse_keys"])

    def test_builders_runtime_and_editor_share_application_schema(self) -> None:
        baseline_schema = self.baseline["reference_database"]["schema"]

        for create_schema in (
            lambda connection: build_kjv.create_kjv_schema(
                connection,
                data_version=1,
                date_iso="2026-08-01T00:00:00Z",
            ),
            lambda connection: build_lxx_tr.create_lxx_tr_schema(
                connection,
                data_version=1,
                date_iso="2026-08-01T00:00:00Z",
                source_summary="test",
            ),
        ):
            with self.subTest(create_schema=create_schema):
                connection = sqlite3.connect(":memory:")
                try:
                    create_schema(connection)
                    self.assertEqual(
                        schema_snapshot(connection),
                        baseline_schema,
                    )
                finally:
                    connection.close()

        self.assertEqual(build_kjv.KJV_SCHEMA_VERSION, 3)
        self.assertEqual(build_lxx_tr.LXX_TR_SCHEMA_VERSION, 3)
        self.assertEqual(BIBLE_MODULE_DB_SCHEMA_VERSION, 3)
        runtime_source = (
            PROJECT_ROOT
            / "lib"
            / "infra"
            / "db"
            / "bible"
            / "bible_module_db.dart"
        ).read_text(encoding="utf-8")
        self.assertIn("int get schemaVersion => 3;", runtime_source)
        for column in (
            "code",
            "module_id",
            "title",
            "description",
            "language",
            "canon",
            "versification",
            "license",
            "source_summary",
            "verse_key",
            "text",
        ):
            with self.subTest(column=column):
                self.assertIn(column, runtime_source)

    def test_final_identifiers_and_info_templates_are_exact(self) -> None:
        final_module = self.baseline["final_module"]
        expected_identifiers = {
            "filename": "bible_ohienko_1988.sqlite",
            "module_id": "ohienko_1988",
            "code": "OH1988",
            "language": "uk",
            "title": "Біблія Огієнка (ювілейне видання 1988 року)",
            "translation": (
                "Біблія або Книги Святого Письма Старого і Нового "
                "Заповіту, переклад Івана Огієнка"
            ),
            "edition": "ювілейне видання 1988 року",
            "canon": "protestant_66",
            "target_versification": "kjv_protestant",
            "schema_version": 3,
            "target_books": 66,
            "target_chapters": 1189,
            "target_verses": 31_102,
            "target_verse_keys": 31_102,
        }
        self.assertEqual(FINAL_IDENTIFIERS, expected_identifiers)
        for key, value in FINAL_IDENTIFIERS.items():
            self.assertEqual(final_module[key], value)
        self.assertEqual(final_module["filename"], MODULE_FILENAME)
        self.assertEqual(final_module["module_id"], MODULE_ID)
        self.assertEqual(final_module["code"], MODULE_CODE)
        self.assertEqual(final_module["info_description"], INFO_DESCRIPTION)
        self.assertEqual(final_module["info_license"], INFO_LICENSE)
        self.assertEqual(
            final_module["info_source_summary_template"],
            INFO_SOURCE_SUMMARY_TEMPLATE,
        )
        self.assertEqual(
            hashlib.sha256(INFO_DESCRIPTION.encode("utf-8")).hexdigest(),
            "349b7d32f4e34db0a3e7cd3133e585cbdd8393ffbc3258a461d84ffc8dfe0e65",
        )
        self.assertEqual(
            hashlib.sha256(INFO_LICENSE.encode("utf-8")).hexdigest(),
            "ad3e3ce1d5b276664e80ef562065b4867eae75be924e066310e27571bfe63471",
        )
        self.assertEqual(
            hashlib.sha256(
                INFO_SOURCE_SUMMARY_TEMPLATE.encode("utf-8")
            ).hexdigest(),
            "d1ecd3825f3aab9eb0a3fd0fc1585a3a7cb4e659f742c1c3c9cb5cc3f4ea7ca4",
        )

        placeholders = {
            field_name
            for _literal, field_name, _format_spec, _conversion in (
                string.Formatter().parse(INFO_SOURCE_SUMMARY_TEMPLATE)
            )
            if field_name is not None
        }
        self.assertEqual(
            placeholders,
            set(INFO_SOURCE_SUMMARY_PLACEHOLDERS),
        )

        existing_ids = {
            build_kjv.MODULE_ID,
            build_lxx_tr.MODULE_ID,
        }
        existing_codes = {
            build_kjv.MODULE_CODE,
            build_lxx_tr.MODULE_CODE,
        }
        existing_filenames = {
            build_kjv.DEFAULT_TARGET_PATH.name,
            build_lxx_tr.DEFAULT_TARGET_PATH.name,
        }
        self.assertNotIn(MODULE_ID, existing_ids)
        self.assertNotIn(MODULE_CODE, existing_codes)
        self.assertNotIn(MODULE_FILENAME, existing_filenames)

    def test_identifiers_csv_is_exact_and_unique(self) -> None:
        csv_text = render_final_identifiers_csv()
        checked_in = (
            DEFAULT_BASELINE_PATH.parent / "final_identifiers.csv"
        ).read_text(encoding="utf-8")
        self.assertEqual(checked_in, csv_text)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        self.assertEqual(
            [row["field"] for row in rows],
            list(FINAL_IDENTIFIERS),
        )
        self.assertEqual(len(rows), len(FINAL_IDENTIFIERS))

    def test_strong_contract_is_locked_by_the_baseline(self) -> None:
        expected_contract = {
            "version": 1,
            "final_pattern": "^[HG][1-9][0-9]*$",
            "classic_ranges": {
                "H": {"min": 1, "max": 8674},
                "G": {"min": 1, "max": 5624},
            },
            "leading_zeroes": "removed_before_final_output",
            "known_extended_to_classic": {
                "G6031": "G1650",
                "G6053": "G2737",
                "G6063": "G1492",
                "G6083": "G4894",
                "G6094": "G3166",
            },
            "unmapped_extended": (
                "preserve_raw_and_block_output_until_explicit_versioned_mapping"
            ),
            "alternatives": (
                "preserve_relation_and_candidates; "
                "select_one_explicitly_or_block"
            ),
            "composites": (
                "preserve_components_and_relation; "
                "never_split_or_flatten_silently"
            ),
            "deduplication": (
                "stable_per_surface_token_after_explicit_resolution"
            ),
            "testament_namespaces": {
                "OT": "H_only_in_final_module",
                "NT": "G_only_in_final_module",
            },
        }
        self.assertEqual(strong_contract_manifest(), expected_contract)
        self.assertEqual(
            self.baseline["strong_contract"],
            expected_contract,
        )
        self.assertEqual(normalize_classic_strong("h0001"), "H1")
        self.assertEqual(normalize_classic_strong("G05624"), "G5624")
        self.assertEqual(normalize_classic_strong("H08674"), "H8674")
        self.assertEqual(normalize_strong_for_output("G06031"), "G1650")
        self.assertEqual(normalize_strong_for_output("G6053"), "G2737")

    def test_strong_contract_blocks_silent_extended_or_composite_loss(
        self,
    ) -> None:
        for raw_strong in (
            "H0",
            "G5625",
            "H8675",
            "H1234a",
            "G1/G2",
            "H1+H2",
            "G1|G2",
            "",
        ):
            with self.subTest(raw_strong=raw_strong):
                with self.assertRaises(StrongContractError):
                    normalize_strong_for_output(raw_strong)

        self.assertEqual(
            normalize_strong_for_output(
                "H1234a",
                extended_replacements={"H1234A": "H1234"},
            ),
            "H1234",
        )

    def test_stage_1_machine_evidence_still_authorizes_stage_2(self) -> None:
        stage_1_path = (
            PROJECT_ROOT
            / "scripts"
            / "bible_module"
            / "reports"
            / "ukrainian_stage_1_20260801"
            / "source_probe.json"
        )
        evidence = json.loads(stage_1_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "stage_1_complete")
        selected = evidence["recommended_candidate"]
        self.assertTrue(selected["owner_confirmation"])
        self.assertEqual(
            selected["edition"],
            "ювілейне видання 1988 року",
        )
        self.assertIn("CC BY-SA 4.0", selected["owner_confirmation_scope"])
        self.assertIn(
            "no mixing with later UBS editions",
            selected["owner_confirmation_scope"],
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
import unicodedata
import zipfile
from pathlib import Path

from scripts.bible_module import ukrainian_stage_4_parsers as parsers
from scripts.bible_module.ukrainian_stage_4_model import (
    SourceRef,
    Stage4ContractError,
    Token,
    make_record,
    normalize_source_text,
    normalize_strong_candidate,
    validate_record,
)
from scripts.bible_module.ukrainian_stage_4_parsers import (
    SourceContext,
    Stage4ParseError,
    parse_crosswire_kjv_osis,
    parse_oshb_zip,
    parse_step_word_table,
    parse_ugnt_zip,
    parse_uxlc_zip,
    parse_wikisource_bundle,
    verify_locked_input,
)

FIXTURES = Path(__file__).parent / "fixtures" / "ukrainian_stage_4"


def _context(path: Path, source_id: str, *, edition: bool = False) -> SourceContext:
    payload = path.read_bytes()
    return SourceContext(
        source_id=source_id,
        role="synthetic test role",
        version="synthetic-v1",
        revision="fixture-revision-1",
        path=path,
        expected_bytes=len(payload),
        expected_sha256=hashlib.sha256(payload).hexdigest(),
        edition_applicable=edition,
    )


class Stage4NormalizationTests(unittest.TestCase):
    def test_unicode_nfc_and_idempotence_preserve_punctuation(self) -> None:
        cases = json.loads((FIXTURES / "normalization_cases.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if "text" not in case:
                continue
            raw = unicodedata.normalize("NFD", case["text"])
            normalized = normalize_source_text(raw)
            self.assertEqual(normalized, unicodedata.normalize("NFC", normalized))
            self.assertEqual(normalize_source_text(normalized), normalized)
        value = "п'ять Пам’ять південно-західний — так"
        self.assertEqual(normalize_source_text(value), value)
        markerless = next(case for case in cases if case["id"] == "footnote_without_printed_marker")
        self.assertIsNone(markerless["printed_marker"])
        self.assertFalse(markerless["printed_marker_present"])

    def test_line_endings_and_spaces_are_deterministic(self) -> None:
        self.assertEqual(normalize_source_text("  слово\r\n\tдалі  "), "слово далі")

    def test_strong_normalization_preserves_unresolved_values(self) -> None:
        self.assertEqual(normalize_strong_candidate("H0001", source_id="x")["normalized"], "H1")
        augmented = normalize_strong_candidate("H7225G", source_id="x")
        self.assertEqual(augmented["normalized"], "H7225G")
        self.assertEqual(augmented["status"], "extended_unresolved")
        ugnt = normalize_strong_candidate("G030560", source_id="unfoldingword_ugnt_v0_34")
        self.assertEqual(ugnt["normalized"], "G3056")
        self.assertEqual(normalize_strong_candidate("bad", source_id="x")["status"], "invalid")

    def test_source_native_record_forbids_target_projection(self) -> None:
        record = make_record(
            source_id="synthetic",
            source_role="test",
            source_version="v1",
            source_revision="r1",
            source_order=1,
            source_locator={"line": 1},
            source_kind="canonical_verse",
            source_plain_raw="Слово.",
            source_ref=SourceRef("Gen", 1, 1),
            tokens=[Token(1, "word", "Слово")],
            provenance={"fixture": True},
        )
        self.assertEqual(record["projection_status"], "unprojected")
        self.assertFalse(any(key.startswith("target_") for key in record))
        invalid = dict(record)
        invalid["verse_key"] = "001"
        with self.assertRaises(Stage4ContractError):
            validate_record(invalid)


class Stage4StepParserTests(unittest.TestCase):
    def test_tahot_structure_order_multiple_and_missing_strong(self) -> None:
        path = FIXTURES / "step_tahot_fixture.txt"
        result = parse_step_word_table(_context(path, "step_tahot_fixture"), family="TAHOT")
        self.assertEqual(len(result.records), 1)
        record = result.records[0]
        self.assertEqual([token["order"] for token in record["tokens"]], [1, 2])
        self.assertEqual(record["source_plain_nfc"], "אב גד")
        self.assertGreaterEqual(result.counters["tokens_with_multiple_strong"], 1)
        self.assertEqual(result.counters["tokens_without_strong"], 1)
        self.assertEqual(
            result.counters["input_lines"],
            result.counters["processed_data_lines"] + result.counters["skipped_lines"],
        )

    def test_tagnt_structure_and_round_trip_surface_without_strong(self) -> None:
        path = FIXTURES / "step_tagnt_fixture.txt"
        result = parse_step_word_table(_context(path, "step_tagnt_fixture"), family="TAGNT")
        self.assertEqual(len(result.records), 1)
        record = result.records[0]
        self.assertEqual(record["tokens"][0]["surface_raw"], "λόγος (logos)")
        self.assertEqual(record["source_plain_nfc"], normalize_source_text(record["source_plain_raw"]))
        self.assertTrue(record["provenance"])

    def test_unverified_and_post_1990_ubt_inputs_fail_closed(self) -> None:
        path = FIXTURES / "step_tagnt_fixture.txt"
        context = _context(path, "step_tagnt_fixture")
        damaged = SourceContext(**{**context.__dict__, "expected_sha256": "0" * 64})
        with self.assertRaises(Stage4ParseError):
            verify_locked_input(damaged)
        prohibited = SourceContext(**{**context.__dict__, "source_id": "ubt_1991"})
        with self.assertRaises(Stage4ParseError):
            verify_locked_input(prohibited)


class Stage4MediaWikiTests(unittest.TestCase):
    def _bundle(self, directory: Path) -> tuple[Path, dict[str, int]]:
        fixture = json.loads((FIXTURES / "wikisource_pages.json").read_text(encoding="utf-8"))
        revisions = [
            {"title": "Біблія", "revid": 1, "content": "root"},
            {"title": "Індекс", "revid": 2, "content": "index"},
        ]
        for page in fixture["pages"]:
            revisions.append(
                {
                    "title": f"Сторінка:Ivan Ohienko Bible.djvu/{page['page']}",
                    "revid": page["revid"],
                    "content": page["content"],
                }
            )
        path = directory / "bundle.json"
        path.write_text(json.dumps({"revisions": revisions}, ensure_ascii=False), encoding="utf-8")
        counters = {name: 0 for name in (
            "raw_carrier_ref_opening", "raw_carrier_ref_closing",
            "raw_carrier_ref_self_closing", "raw_carrier_reflist", "raw_carrier_anchor",
        )}
        for revision in revisions:
            content = revision["content"]
            counters["raw_carrier_ref_opening"] += len(parsers._REF_OPEN_RE.findall(content))
            counters["raw_carrier_ref_closing"] += len(parsers._REF_CLOSE_RE.findall(content))
            counters["raw_carrier_ref_self_closing"] += len(parsers._REF_SELF_RE.findall(content))
            counters["raw_carrier_reflist"] += len(parsers.re.findall(r"{{\s*reflist\b", content, parsers.re.I))
            counters["raw_carrier_anchor"] += len(parsers.re.findall(r"{{\s*anchor\b", content, parsers.re.I))
        return path, counters

    def _parse(self, directory: Path):
        path, carriers = self._bundle(directory)
        return parse_wikisource_bundle(
            _context(path, "wikisource_ohienko_1988_revisions", edition=True),
            expected_revision_count=5,
            expected_page_count=3,
            expected_carriers=carriers,
        )

    def test_footnotes_are_structural_ordered_and_excluded_from_plain_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._parse(Path(temporary))
        verse = next(record for record in result.records if record["source_ref_raw"] == "Gen.1.1")
        plain = verse["source_plain_nfc"]
        self.assertIn("слово, далі", plain)
        self.assertNotIn("синтетична сноска", plain.casefold())
        self.assertNotIn("варіант", plain.casefold())
        self.assertEqual(len(verse["footnotes"]), 3)
        self.assertEqual([note["printed_marker"] for note in verse["footnotes"]], ["2", "3", "4"])
        self.assertTrue(all(note["printed_marker_present"] is True for note in verse["footnotes"]))
        self.assertEqual(
            [note["source_order"] for note in verse["footnotes"]],
            sorted(note["source_order"] for note in verse["footnotes"]),
        )
        named = [note for note in verse["footnotes"] if note.get("name") == "n"]
        self.assertEqual(len(named), 2)
        self.assertEqual(named[0]["footnote_id"], named[1]["footnote_id"])
        self.assertNotEqual(named[0]["use_id"], named[1]["use_id"])
        first = verse["footnotes"][0]
        self.assertEqual(first["anchor_start_scalar"], first["anchor_end_scalar"])
        self.assertEqual(plain[first["anchor_start_scalar"]], ",")
        self.assertIn("{{sp|", first["full_text_raw"])
        self.assertIn("синтетична сноска", first["full_text_nfc"].casefold())

    def test_page_boundary_binding_and_missing_heading_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._parse(Path(temporary))
        verse = next(record for record in result.records if record["source_ref_raw"] == "Gen.1.2")
        boundary_note = next(note for note in verse["footnotes"] if note["source_page"] == 12)
        self.assertEqual(boundary_note["binding_status"], "unambiguous")
        self.assertEqual(boundary_note["source_ref"], SourceRef("Gen", 1, 2).as_dict())
        missing = [
            note
            for record in result.records
            for note in record["footnotes"]
            if note["binding_status"] == "missing"
        ]
        self.assertEqual(len(missing), 1)
        self.assertIsNone(missing[0]["anchor_start_scalar"])
        self.assertEqual(missing[0]["binding_candidates"], [])

    def test_all_carriers_consumed_round_trip_and_repeat_run_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = self._parse(Path(temporary))
            second = self._parse(Path(temporary))
        self.assertEqual(first.counters["raw_ref_opening"], first.counters["raw_carrier_ref_opening"])
        first_notes = [note for record in first.records for note in record["footnotes"]]
        second_notes = [note for record in second.records for note in record["footnotes"]]
        self.assertEqual(first_notes, second_notes)
        self.assertEqual(len(first_notes), first.counters["footnote_uses"])
        self.assertFalse(any(token["strong"] for record in first.records for token in record["tokens"]))


class Stage4XmlAndArchiveParserTests(unittest.TestCase):
    def test_tvtms_service_and_mapping_records_are_not_projected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "tvtms.txt"
            prefix = "\n" * 162
            path.write_text(
                prefix
                + "$Gen.1:1\tEnglish KJV\tHebrew\n"
                + "TEST: If...\tGen.1:1=Last\tGen.1:1=Last\n"
                + "OneToOne\tGen.1:1\tGen.1:1\n",
                encoding="utf-8",
            )
            result = parsers.parse_tvtms(_context(path, "step_tvtms"))
        self.assertEqual([record["source_kind"] for record in result.records], [
            "versification_section", "versification_test", "versification_mapping_expression"
        ])
        self.assertTrue(all(record["projection_status"] == "unprojected" for record in result.records))
        self.assertTrue(all("target_refs" not in record for record in result.records))

    def test_oshb_uxlc_and_ugnt_native_formats(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            oshb_path = directory / "oshb.zip"
            oshb_xml = (FIXTURES / "oshb_fixture.xml").read_bytes()
            with zipfile.ZipFile(oshb_path, "w") as archive:
                for osis in parsers._UXLC_FILE_TO_OSIS.values():
                    archive.writestr(f"root/wlc/{osis}.xml", oshb_xml)
                archive.writestr("root/LICENSE.md", "CC0 fixture")
            oshb = parse_oshb_zip(_context(oshb_path, "openscriptures_oshb_v2_2"))
            self.assertEqual(len(oshb.records), 39)
            self.assertEqual(oshb.records[0]["tokens"][0]["morphology"], ["HNcmsa", "HVqp3ms"])

            uxlc_path = directory / "uxlc.zip"
            uxlc_xml = (FIXTURES / "uxlc_fixture.xml").read_bytes()
            with zipfile.ZipFile(uxlc_path, "w") as archive:
                for filename in parsers._UXLC_FILE_TO_OSIS:
                    archive.writestr(f"Books/{filename}.xml", uxlc_xml)
                archive.writestr("License.html", "CC0 fixture")
            uxlc = parse_uxlc_zip(_context(uxlc_path, "tanach_us_uxlc_2_5_27_6"))
            self.assertEqual(len(uxlc.records), 39)
            self.assertTrue(all(not token["strong"] for token in uxlc.records[0]["tokens"]))

            ugnt_path = directory / "ugnt.zip"
            usfm = (FIXTURES / "ugnt_fixture.usfm").read_bytes()
            with zipfile.ZipFile(ugnt_path, "w") as archive:
                for number in range(27):
                    archive.writestr(f"root/{number:02d}.usfm", usfm)
                archive.writestr("root/LICENSE.md", "CC0 fixture")
            ugnt = parse_ugnt_zip(_context(ugnt_path, "unfoldingword_ugnt_v0_34"))
            self.assertEqual(len(ugnt.records), 27)
            self.assertEqual(ugnt.records[0]["tokens"][0]["strong"][0]["normalized"], "G3056")
            self.assertEqual(ugnt.counters["tokens_without_strong"], 27)

    def test_crosswire_milestone_osis_multiple_strong(self) -> None:
        path = FIXTURES / "crosswire_fixture.xml"
        result = parse_crosswire_kjv_osis(_context(path, "crosswire_kjv_3_1"))
        self.assertEqual(len(result.records), 1)
        self.assertEqual(len(result.records[0]["tokens"][0]["strong"]), 2)
        self.assertEqual(result.counters["tokens_with_multiple_strong"], 1)

    def test_djvu_s_expression_and_duplicate_container_are_structural(self) -> None:
        parsed = parsers._parse_s_expressions('(page 0 0 10 10 (line 0 0 10 2 "Слово "))\n()')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(list(parsers._walk_nodes(parsed[0], "line"))[0][5], "Слово ")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            chunk = b"FORM" + (4).to_bytes(4, "big") + b"DJVM"
            path = directory / "duplicate.djvu"
            path.write_bytes(b"AT&T" + chunk + b"AT&T" + chunk)
            logical, details = parsers._djvu_logical_container(
                path, work_dir=directory / "work", source_id="commons_test"
            )
            self.assertTrue(details["duplicate_containers"])
            self.assertEqual(logical.read_bytes(), b"AT&T" + chunk)


class Stage4ArchitectureInvariantTests(unittest.TestCase):
    def test_source_parsers_do_not_call_other_public_source_parsers(self) -> None:
        tree = ast.parse(Path(parsers.__file__).read_text(encoding="utf-8"))
        public_parsers = {
            "parse_step_word_table", "parse_tvtms", "parse_oshb_zip", "parse_uxlc_zip",
            "parse_ugnt_zip", "parse_crosswire_kjv_osis", "parse_wikisource_bundle",
            "parse_djvu_hidden_text",
        }
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name not in public_parsers:
                continue
            calls = {
                call.func.id
                for call in ast.walk(node)
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            }
            self.assertFalse((calls & public_parsers) - {node.name}, node.name)


if __name__ == "__main__":
    unittest.main()

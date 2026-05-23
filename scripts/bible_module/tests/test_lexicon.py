from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.bible_module.lexicon import (
    LexiconEntry,
    StrongOccurrence,
    iter_step_lexicon_entries,
    iter_tegmc_entries,
    parse_step_lexicon_row,
    strong_occurrences_from_lxx_module_verses,
    strong_occurrences_from_tagnt_tokens,
    verify_strong_coverage,
)
from scripts.bible_module.tagnt import parse_tagnt_row


def tagnt_line(*fields: str) -> str:
    return "\t".join(fields)


def lexicon_text(data_line: str) -> str:
    return "\n".join(
        [
            "metadata before table",
            "eStrong\tdStrong\tuStrong\tGreek\tTransliteration\tMorph\tGloss\tDefinition",
            data_line,
        ]
    )


class LexiconImportTests(unittest.TestCase):
    def test_tbesg_imports_dictionary_input_entries(self) -> None:
        entry = parse_step_lexicon_row(
            "G0746\tG0746 =\tG0746\tarche\tarche\tG:N-F\tbeginning\tbrief definition",
            source_id="step_tbesg",
            line_number=91,
        )

        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.source_id, "step_tbesg")
        self.assertEqual(entry.raw_strong, "G0746")
        self.assertEqual(entry.strong, "G746")
        self.assertEqual(entry.definition, "brief definition")

        row = entry.as_dictionary_input_row(entry_id=1)
        self.assertEqual(row["entry_id"], 1)
        self.assertEqual(row["strong"], "G746")
        self.assertNotIn("module_verse_id", row)
        self.assertNotIn("canonical_verse_id", row)
        self.assertNotIn("text_plain", row)

    def test_tflsj_0_5624_imports_dictionary_input_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "step_tflsj_0_5624.txt"
            path.write_text(
                lexicon_text(
                    "G0002\tG0002 = the Greek of\tH0175\tAaron\tAaroon\t"
                    "N:N-M-P\tAaron\tfull LSJ definition"
                ),
                encoding="utf-8",
            )

            entries = list(
                iter_step_lexicon_entries(path, source_id="step_tflsj_0_5624")
            )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].source_id, "step_tflsj_0_5624")
        self.assertEqual(entries[0].strong, "G2")
        self.assertEqual(entries[0].ustrong, "H0175")

    def test_tflsj_extra_imports_dictionary_input_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "step_tflsj_extra.txt"
            path.write_text(
                lexicon_text(
                    "G6000\tG6000 =\tG6000\textra\textra\t"
                    "G:N\tlexical extra\textra LSJ definition"
                ),
                encoding="utf-8",
            )

            entries = list(
                iter_step_lexicon_entries(path, source_id="step_tflsj_extra")
            )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].source_id, "step_tflsj_extra")
        self.assertEqual(entries[0].strong, "G6000")
        self.assertEqual(entries[0].gloss, "lexical extra")

    def test_tegmc_imports_morphology_dictionary_inputs(self) -> None:
        tegmc_text = "\n".join(
            [
                "Code\tExample in English\tMeaning",
                "G:A\tthoughtful\tGreek Adjective",
                '"1 CODE"\t"2 TAG"\t"3 MEANING"',
                "$",
                "N-NSF\tFunction=Noun; Case=Nominative; Number=Singular; Gender=Feminine",
                "\tNoun Nominative Singular Feminine",
                "\tDESCRIBING a female person or thing doing something",
                '\t"a _woman_ speaks"',
                "$",
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "step_tegmc.txt"
            path.write_text(tegmc_text, encoding="utf-8")

            entries = iter_tegmc_entries(path)

        self.assertEqual(entries[0].code, "G:A")
        self.assertEqual(entries[0].brief_meaning, "Greek Adjective")

        full = next(entry for entry in entries if entry.code == "N-NSF")
        self.assertEqual(full.properties["Function"], "Noun")
        self.assertEqual(full.properties["Case"], "Nominative")
        self.assertEqual(full.summary, "Noun Nominative Singular Feminine")
        self.assertIn("female person", full.description)

        row = full.as_dictionary_input_row(entry_id=3)
        self.assertEqual(row["source_id"], "step_tegmc")
        self.assertIn("properties_json", row)
        self.assertNotIn("module_verse_id", row)
        self.assertNotIn("text_plain", row)

    def test_coverage_warnings_use_normalized_strongs_for_tagnt(self) -> None:
        token = parse_tagnt_row(
            tagnt_line(
                "Mat.1.1#01=NKO",
                "Biblos (Biblos)",
                "[The] book",
                "G0976=N-NSF",
                "biblos=book",
                "NA28+NA27",
                "",
                "",
                "Libro",
                "book",
                "#01",
                "G0976",
                "",
            )
        )
        self.assertIsNotNone(token)
        assert token is not None

        lexicon_entries = [
            _lexicon_entry(raw_strong="G0976", source_id="step_tbesg"),
        ]
        occurrences = tuple(strong_occurrences_from_tagnt_tokens([token]))
        warnings = verify_strong_coverage(
            occurrences,
            lexicon_entries,
            source_label="TAGNT",
        )

        self.assertEqual(occurrences[0].strong, "G976")
        self.assertEqual(warnings, ())

    def test_coverage_warnings_report_missing_lxx_strongs_with_stable_refs(self) -> None:
        module_verse = SimpleNamespace(
            canonical_verse_id=1001001,
            canonical_ref="Gen.1.1",
            tokens=(
                SimpleNamespace(
                    source_ref="Gen.1.1#1",
                    surface="en",
                    strong_segments=(
                        SimpleNamespace(strong="G0746", raw_strong="G0746"),
                    ),
                ),
                SimpleNamespace(
                    source_ref="Gen.1.1#2",
                    surface="missing",
                    strong_segments=(
                        SimpleNamespace(strong="G9999", raw_strong="G9999"),
                    ),
                ),
            ),
        )
        lexicon_entries = [_lexicon_entry(raw_strong="G746", source_id="step_tbesg")]

        occurrences = tuple(strong_occurrences_from_lxx_module_verses([module_verse]))
        warnings = verify_strong_coverage(
            occurrences,
            lexicon_entries,
            source_label="LXX",
        )

        self.assertEqual([occurrence.strong for occurrence in occurrences], ["G746", "G9999"])
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].strong, "G9999")
        self.assertEqual(warnings[0].sample_refs, ("Gen.1.1 (Gen.1.1#2)",))
        self.assertIn("G9999", warnings[0].as_warning_row()["message"])

    def test_occurrence_inputs_keep_canonical_refs_outside_bible_text_rows(self) -> None:
        occurrence = StrongOccurrence(
            source="NA28_LXX",
            strong="G746",
            raw_strong="G0746",
            canonical_verse_id=1001001,
            canonical_ref="Gen.1.1",
            source_ref="Gen.1.1#1",
            surface="arche",
        )

        row = occurrence.as_dictionary_input_row(occurrence_id=5)

        self.assertEqual(row["canonical_verse_id"], 1001001)
        self.assertEqual(row["canonical_ref"], "Gen.1.1")
        self.assertNotIn("module_verse_id", row)
        self.assertNotIn("source_text_id", row)
        self.assertNotIn("text_plain", row)
        json.dumps(row)


def _lexicon_entry(*, raw_strong: str, source_id: str) -> LexiconEntry:
    return LexiconEntry(
        source_id=source_id,
        raw_strong=raw_strong,
        strong=raw_strong.replace("G0", "G"),
        dstrong="",
        ustrong=raw_strong,
        greek="",
        transliteration="",
        morphology="",
        gloss="",
        definition="",
        line_number=1,
        raw_line=raw_strong,
    )


if __name__ == "__main__":
    unittest.main()

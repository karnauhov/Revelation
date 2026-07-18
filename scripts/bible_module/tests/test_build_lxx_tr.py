from __future__ import annotations

import sqlite3
import tempfile
import unittest
import json
from pathlib import Path

from scripts.bible_module.build_lxx_tr import (
    LXX_TR_SCHEMA_VERSION,
    LxxProjectionRule,
    LxxProjectionSpan,
    build_lxx_verse_texts,
    build_lxx_tr_module_from_tokens,
    build_tr_verse_texts,
    iter_lxx_tr_tagnt_tokens,
    is_valid_tagged_text,
    load_lxx_projection_plan,
    load_lxx_projection_rules,
    validate_lxx_tr_database,
    verse_key_for,
)
from scripts.bible_module.canon import canonical_verses, get_canonical_verse
from scripts.bible_module.lxx import LxxSourceVerse
from scripts.bible_module.tagnt import parse_tagnt_row


def tagnt_line(*fields: str) -> str:
    return "\t".join(fields)


def tr_row(
    reference: str,
    surface: str,
    strong_grammar: str,
    *,
    editions: str = "TR+Byz",
) -> str:
    return tagnt_line(
        reference,
        surface,
        "fixture translation",
        strong_grammar,
        "fixture=fixture",
        editions,
        "",
        "",
        "fixture",
        "fixture",
        "#01",
        "",
        "",
    )


def lxx_source_verse(reference: str, raw_osis: str) -> LxxSourceVerse:
    book_code, chapter, verse = reference.split(".")
    return LxxSourceVerse(
        source_book_code=book_code,
        chapter=int(chapter),
        verse=int(verse),
        entry_index=1,
        block_index=1,
        raw_osis=raw_osis,
    )


class LxxTrBuilderTests(unittest.TestCase):
    def test_tr_text_builder_adds_primary_strong_after_each_word(self) -> None:
        token = parse_tagnt_row(
            tr_row("Mat.1.1#01=NKO", "Biblos.", "G0976=N-NSF")
        )
        self.assertIsNotNone(token)
        assert token is not None

        result = build_tr_verse_texts([token])
        mat_1_1 = get_canonical_verse("Mat", 1, 1)

        self.assertEqual(result.tr_tokens_count, 1)
        self.assertEqual(result.verse_texts_by_id[mat_1_1.canonical_verse_id], "Biblos G976")
        self.assertNotIn("Mat.1.1", result.missing_tr_verses)
        self.assertEqual(result.extra_tr_verses, ())
        self.assertEqual(result.missing_strong_tokens, ())
        self.assertTrue(is_valid_tagged_text(result.verse_texts_by_id[mat_1_1.canonical_verse_id]))

    def test_tr_text_builder_replaces_extended_strongs_with_classic_keys(self) -> None:
        token = parse_tagnt_row(
            tr_row("Mat.6.8#01=NKO", "Oiden", "G6063=V-RAI-3S")
        )
        self.assertIsNotNone(token)
        assert token is not None

        result = build_tr_verse_texts([token])
        mat_6_8 = get_canonical_verse("Mat", 6, 8)

        self.assertEqual(result.verse_texts_by_id[mat_6_8.canonical_verse_id], "Oiden G1492")
        self.assertEqual(result.missing_strong_tokens, ())

    def test_tr_text_builder_reports_words_without_strong(self) -> None:
        token = parse_tagnt_row(
            tr_row("Mat.1.2#01=NKO", "NoStrong", "N-NSF")
        )
        self.assertIsNotNone(token)
        assert token is not None

        result = build_tr_verse_texts([token])
        mat_1_2 = get_canonical_verse("Mat", 1, 2)

        self.assertEqual(result.verse_texts_by_id[mat_1_2.canonical_verse_id], "NoStrong")
        self.assertEqual(len(result.missing_strong_tokens), 1)
        self.assertEqual(result.missing_strong_tokens[0].source_ref, "Mat.1.2#01=NKO")

    def test_lxx_text_builder_extracts_token_span(self) -> None:
        source = lxx_source_verse(
            "Gen.31.48",
            (
                '<w lemma="strong:G3037">heap</w> '
                '<w lemma="strong:G3778">this</w> '
                '<w lemma="strong:G3037">heap</w> '
                '<w lemma="strong:G2476">pillar</w>'
            ),
        )
        rule = LxxProjectionRule(
            target_ref="Gen.31.51",
            spans=(
                LxxProjectionSpan(
                    source_ref="Gen.31.48",
                    token_start=1,
                    token_end=4,
                ),
            ),
        )

        result = build_lxx_verse_texts([source], projection_rules=(rule,))
        gen_31_51 = get_canonical_verse("Gen", 31, 51)

        self.assertEqual(result.lxx_tokens_count, 3)
        self.assertEqual(
            result.verse_texts_by_id[gen_31_51.canonical_verse_id],
            "this G3778 heap G3037 pillar G2476",
        )
        self.assertNotIn("Gen.31.51", result.missing_lxx_verses)
        self.assertEqual(result.missing_strong_tokens, ())

    def test_lxx_text_builder_accepts_external_literal_with_manual_strong(self) -> None:
        rule = LxxProjectionRule(
            target_ref="Ps.116.17",
            tagged_text=(
                "soi G4771 thyso G2380 thysian G2378 aineseos G133 "
                "kai G2532 en G1722 onomati G3686 kyriou G2962 "
                "epikalesomai G1941"
            ),
            status="manual_external_ancient_greek_literal",
        )

        result = build_lxx_verse_texts([], projection_rules=(rule,))
        ps_116_17 = get_canonical_verse("Ps", 116, 17)

        self.assertEqual(result.lxx_tokens_count, 9)
        self.assertEqual(
            result.verse_texts_by_id[ps_116_17.canonical_verse_id],
            (
                "soi G4771 thyso G2380 thysian G2378 aineseos G133 "
                "kai G2532 en G1722 onomati G3686 kyriou G2962 "
                "epikalesomai G1941"
            ),
        )
        self.assertNotIn("Ps.116.17", result.missing_lxx_verses)
        self.assertEqual(result.missing_strong_tokens, ())

    def test_lxx_text_builder_merges_multiple_source_spans(self) -> None:
        sources = [
            lxx_source_verse(
                "Dan.5.2",
                (
                    '<w lemma="strong:G3588">the</w> '
                    '<w lemma="strong:G4221">cup</w>'
                ),
            ),
            lxx_source_verse(
                "Dan.5.3",
                (
                    '<w lemma="strong:G5342">bring</w> '
                    '<w lemma="strong:G5552">gold</w>'
                ),
            ),
        ]
        rule = LxxProjectionRule(
            target_ref="Dan.5.2",
            spans=(
                LxxProjectionSpan(source_ref="Dan.5.2"),
                LxxProjectionSpan(source_ref="Dan.5.3", token_start=0, token_end=1),
            ),
        )

        result = build_lxx_verse_texts(sources, projection_rules=(rule,))
        dan_5_2 = get_canonical_verse("Dan", 5, 2)

        self.assertEqual(
            result.verse_texts_by_id[dan_5_2.canonical_verse_id],
            "the G3588 cup G4221 bring G5342",
        )

    def test_lxx_text_builder_selects_theodotion_x2_segment(self) -> None:
        source = lxx_source_verse(
            "Dan.5.2",
            (
                '<seg type="x-variant" subType="x-1">'
                '<w lemma="strong:G1">old</w>'
                '</seg>'
                '<seg type="x-variant" subType="x-2">'
                '<w lemma="strong:G3588">the</w> '
                '<w lemma="strong:G935">king</w> '
                '<w lemma="strong:G5346">said</w>'
                '</seg>'
            ),
        )
        rule = LxxProjectionRule(
            target_ref="Dan.5.1",
            spans=(
                LxxProjectionSpan(
                    source_ref="Dan.5.2",
                    segment_index=2,
                    sub_type="x-2",
                    token_start=0,
                    token_end=2,
                ),
            ),
        )

        result = build_lxx_verse_texts([source], projection_rules=(rule,))
        dan_5_1 = get_canonical_verse("Dan", 5, 1)

        self.assertEqual(
            result.verse_texts_by_id[dan_5_1.canonical_verse_id],
            "the G3588 king G935",
        )

    def test_lxx_projection_rules_can_load_token_span_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_path = Path(temp_dir) / "rules.json"
            rules_path.write_text(
                json.dumps(
                    {
                        "rules": [
                            {
                                "target_ref": "Dan.5.1",
                                "spans": [
                                    {
                                        "source_ref": "Dan.5.2",
                                        "segment_index": 2,
                                        "sub_type": "x-2",
                                        "token_start": 0,
                                        "token_end": 16,
                                    }
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            rules = load_lxx_projection_rules(rules_path)

        self.assertEqual(
            rules,
            (
                LxxProjectionRule(
                    target_ref="Dan.5.1",
                    spans=(
                        LxxProjectionSpan(
                            source_ref="Dan.5.2",
                            segment_index=2,
                            sub_type="x-2",
                            token_start=0,
                            token_end=16,
                        ),
                    ),
                ),
            ),
        )

    def test_lxx_projection_rules_can_load_consolidated_json(self) -> None:
        candidate_content = {
            "groups": [
                {
                    "id": "fixture_candidate",
                    "pairs": [
                        {
                            "source_ref": "Gen.1.1",
                            "target_ref": "Gen.1.1",
                        }
                    ],
                },
                {
                    "id": "fixture_exclusion",
                    "kind": "source_exclusion_composite_split_or_extraction",
                    "source_refs": ["Gen.1.2"],
                },
            ]
        }
        manual_content = {
            "metadata": {
                "info_source_summary_notes": ["fixture external source"],
                "info_license_notes": ["fixture public domain license"],
            },
            "rules": [
                {
                    "target_ref": "Gen.1.3",
                    "spans": [
                        {
                            "source_ref": "Gen.1.3",
                            "token_start": 0,
                            "token_end": 2,
                        }
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            rules_path = Path(temp_dir) / "consolidated.json"
            rules_path.write_text(
                json.dumps(
                    {
                        "projection_inputs": {
                            "versification_candidate_map": {
                                "content": candidate_content,
                            },
                            "token_span_rules_manual": {
                                "content": manual_content,
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            plan = load_lxx_projection_plan(rules_path)

        self.assertEqual(
            [rule.target_ref for rule in plan.rules],
            ["Gen.1.1", "Gen.1.3"],
        )
        self.assertEqual(plan.rules[1].spans[0].token_start, 0)
        self.assertEqual(plan.rules[1].spans[0].token_end, 2)
        self.assertEqual(
            plan.info_source_summary_notes,
            ("fixture external source",),
        )
        self.assertEqual(
            plan.info_license_notes,
            ("fixture public domain license",),
        )

    def test_tagnt_iterator_maps_annotated_references_to_kjv_versification(self) -> None:
        lines = [
            tr_row("Jhn.7.53{8.1}#01=KO", "Kai", "G2532=CONJ"),
            tr_row("Act.19.41(19.40)#01=NKO", "kai", "G2532=CONJ"),
            tr_row("Rom.16.25{14.24}#01=NKO", "To", "G3588=T-DSM"),
            tr_row("Rom.16.27{14.26}#13=NKO", "amen", "G0281=INJ-HEB"),
            tr_row(
                "Rom.16.27{14.26}#14=K",
                "pros",
                "G4314=PREP",
                editions="TR",
            ),
            tr_row("2Co.13.12[13.13]#06=NKO", "Aspazontai", "G0782=V-PNI-3P"),
            tr_row("2Co.13.13[13.14]#01=NKO", "He", "G3588=T-NSF"),
            tr_row(
                "2Co.13.13[13.14]#22=K",
                "pros",
                "G4314=PREP",
                editions="TR",
            ),
            tr_row("Php.1.16[1.17]#01=NKO", "agapes", "G0026=N-GSF"),
            tr_row("Php.1.17[1.16]#01=NKO", "eritheias", "G2052=N-GSF"),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "tagnt.txt"
            source_path.write_text("\n".join(lines), encoding="utf-8")

            tokens = list(iter_lxx_tr_tagnt_tokens([source_path]))

        self.assertEqual(
            [token.source_ref for token in tokens],
            [
                "Jhn.7.53#01=KO",
                "Act.19.41#01=NKO",
                "Rom.16.25#01=NKO",
                "Rom.16.27#13=NKO",
                "2Co.13.13#06=NKO",
                "2Co.13.14#01=NKO",
                "Php.1.17#01=NKO",
                "Php.1.16#01=NKO",
            ],
        )

        result = build_tr_verse_texts(tokens)
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("John", 7, 53).canonical_verse_id
            ],
            "Kai G2532",
        )
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("Rom", 16, 27).canonical_verse_id
            ],
            "amen G281",
        )
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("2Cor", 13, 13).canonical_verse_id
            ],
            "Aspazontai G782",
        )
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("2Cor", 13, 14).canonical_verse_id
            ],
            "He G3588",
        )
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("Phil", 1, 16).canonical_verse_id
            ],
            "eritheias G2052",
        )
        self.assertEqual(
            result.verse_texts_by_id[
                get_canonical_verse("Phil", 1, 17).canonical_verse_id
            ],
            "agapes G26",
        )

    def test_fixture_build_creates_full_kjv_scaffold_and_fills_tr_nt(self) -> None:
        token = parse_tagnt_row(
            tr_row("Mat.1.1#01=NKO", "Biblos.", "G0976=N-NSF")
        )
        self.assertIsNotNone(token)
        assert token is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bible_lxx_tr.sqlite"
            report = build_lxx_tr_module_from_tokens(
                target_path=target_path,
                tr_source_tokens=[token],
                source_summary="fixture source",
                license_summary="fixture license",
                built_at="2026-05-30T00:00:00Z",
            )

            self.assertEqual(report.target_path, target_path.resolve())
            self.assertIsNone(report.backup_path)
            self.assertEqual(report.verses_count, len(canonical_verses()))
            self.assertEqual(report.filled_verses_count, 1)
            self.assertEqual(report.empty_verses_count, len(canonical_verses()) - 1)
            validate_lxx_tr_database(target_path)

            connection = sqlite3.connect(target_path)
            try:
                self.assertEqual(
                    int(connection.execute("PRAGMA user_version").fetchone()[0]),
                    LXX_TR_SCHEMA_VERSION,
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM info").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT license, source_summary FROM info"
                    ).fetchone(),
                    ("fixture license", "fixture source"),
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0],
                    len(canonical_verses()),
                )
                self.assertEqual(
                    {
                        row[0]
                        for row in connection.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table'"
                        )
                    },
                    {"db_metadata", "info", "verses"},
                )
                self.assertEqual(
                    [
                        row[1]
                        for row in connection.execute("PRAGMA table_info(verses)")
                    ],
                    ["verse_key", "text"],
                )
                self.assertEqual(
                    [
                        row[1]
                        for row in connection.execute("PRAGMA table_info(info)")
                    ],
                    [
                        "code",
                        "module_id",
                        "title",
                        "description",
                        "language",
                        "canon",
                        "versification",
                        "license",
                        "source_summary",
                    ],
                )

                mat_1_1 = get_canonical_verse("Mat", 1, 1)
                stored = connection.execute(
                    """
                    SELECT verse_key, text
                    FROM verses
                    WHERE verse_key = ?
                    """,
                    (verse_key_for(mat_1_1),),
                ).fetchone()
                self.assertEqual(tuple(stored), (verse_key_for(mat_1_1), "Biblos G976"))

                gen_1_1 = get_canonical_verse("Gen", 1, 1)
                empty_ot = connection.execute(
                    """
                    SELECT text
                    FROM verses
                    WHERE verse_key = ?
                    """,
                    (verse_key_for(gen_1_1),),
                ).fetchone()[0]
                self.assertEqual(empty_ot, "")
            finally:
                connection.close()

    def test_existing_target_is_backed_up_before_replacement(self) -> None:
        token = parse_tagnt_row(
            tr_row("Mat.1.1#01=NKO", "Biblos.", "G0976=N-NSF")
        )
        self.assertIsNotNone(token)
        assert token is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bible_lxx_tr.sqlite"
            target_path.write_bytes(b"old database")

            report = build_lxx_tr_module_from_tokens(
                target_path=target_path,
                tr_source_tokens=[token],
                source_summary="fixture source",
                built_at="2026-05-30T00:00:00Z",
            )

            self.assertIsNotNone(report.backup_path)
            assert report.backup_path is not None
            self.assertEqual(report.backup_path.read_bytes(), b"old database")
            validate_lxx_tr_database(target_path)

    def test_verse_keys_are_three_character_sequential_base36_values(self) -> None:
        self.assertEqual(verse_key_for(get_canonical_verse("Gen", 1, 1)), "001")
        self.assertEqual(verse_key_for(get_canonical_verse("Gen", 1, 2)), "002")
        self.assertEqual(verse_key_for(get_canonical_verse("Rev", 22, 21)), "NZY")

    def test_tagged_text_validation_allows_optional_lxx_strong_tokens(self) -> None:
        self.assertTrue(is_valid_tagged_text("Biblos G976 geneseos G1078"))
        self.assertTrue(is_valid_tagged_text("Biblos geneseos G1078"))
        self.assertTrue(is_valid_tagged_text("Biblos geneseos"))
        self.assertFalse(is_valid_tagged_text("Biblos G976 G1078"))
        self.assertFalse(is_valid_tagged_text("G976 Biblos"))
        self.assertFalse(is_valid_tagged_text("Biblos<G976>"))


if __name__ == "__main__":
    unittest.main()

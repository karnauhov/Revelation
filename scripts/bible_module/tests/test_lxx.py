from __future__ import annotations

import sqlite3
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

from scripts.bible_module.lxx import (
    CROSSWIRE_LXX_SOURCE_TEXT_ID,
    LxxSourceVerse,
    build_lxx_import_result,
    crosswire_lxx_module_source_row,
    iter_crosswire_lxx_source_verses,
    parse_lxx_tokens,
    read_crosswire_lxx_metadata,
)
from scripts.bible_module.schema import (
    create_bible_module_schema,
    insert_minimal_module_fixture,
)
from scripts.bible_module.tagnt import normalize_strong


FAKE_LXX_CONF = """## Sword module configuration file
[LXX]
Description=Septuagint, Morphologically Tagged Rahlfs'
DataPath=./modules/texts/ztext/lxx/
ModDrv=zText
SourceType=OSIS
Encoding=UTF-8
CompressType=ZIP
BlockType=BOOK
Versification=LXX
DistributionLicense=Copyrighted; Free non-commercial distribution
TextSource=http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/
SwordVersionDate=2025-03-15
Version=3.2
"""


def word(
    surface: str,
    *,
    strong: str | None = "G0001",
    morph: str = "packard:N1-NSF",
) -> str:
    attrs = []
    if strong is not None:
        attrs.append(f'lemma="strong:{strong}"')
    if morph:
        attrs.append(f'morph="{morph}"')
    attrs.append("xlit=\"betacode:TEST\"")
    return f"<w {' '.join(attrs)}>{surface}</w>"


def write_fake_lxx_zip(path: Path, fragments: list[str]) -> None:
    module_intro = (
        '<milestone type="x-importer" subType="x-osis2mod" '
        'n="$Rev: test $ (SWORD: test)"/>'
    ).encode("utf-8")
    block_payload = "".join(fragments).encode("utf-8")
    compressed_blocks = [zlib.compress(module_intro), zlib.compress(block_payload)]

    bzs = bytearray()
    bzz = bytearray()
    for raw_block, compressed_block in (
        (module_intro, compressed_blocks[0]),
        (block_payload, compressed_blocks[1]),
    ):
        offset = len(bzz)
        bzz.extend(compressed_block)
        bzs.extend(struct.pack("<III", offset, len(compressed_block), len(raw_block)))

    bzv = bytearray()
    bzv.extend(struct.pack("<IIH", 0, 0, 0))
    bzv.extend(struct.pack("<IIH", 0, 0, len(module_intro)))
    start = 0
    for fragment in fragments:
        encoded = fragment.encode("utf-8")
        bzv.extend(struct.pack("<IIH", 1, start, len(encoded) % 65_536))
        start += len(encoded)

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mods.d/lxx.conf", FAKE_LXX_CONF)
        archive.writestr("modules/texts/ztext/lxx/ot.bzs", bytes(bzs))
        archive.writestr("modules/texts/ztext/lxx/ot.bzv", bytes(bzv))
        archive.writestr("modules/texts/ztext/lxx/ot.bzz", bytes(bzz))
        archive.writestr("modules/texts/ztext/lxx/nt.bzs", b"")
        archive.writestr("modules/texts/ztext/lxx/nt.bzv", b"")
        archive.writestr("modules/texts/ztext/lxx/nt.bzz", b"")


def book_fragment(book: str) -> str:
    return f'<div osisID="{book}" sID="{book}.book" type="book"/> '


def chapter_fragment(book: str, chapter: int) -> str:
    return f'<chapter osisID="{book}.{chapter}" sID="{book}.{chapter}"/> '


def fake_lxx_fragments() -> list[str]:
    fragments = [
        book_fragment("Gen"),
        chapter_fragment("Gen", 1),
        (
            '<w lemma="strong:G1722" morph="packard:P" xlit="betacode:E)N">ἐν</w> '
            '<w lemma="strong:G0746" morph="packard:N1-DSF" '
            'xlit="betacode:A)RXH=|">ἀρχῇ</w>'
        ),
        book_fragment("Ps"),
        chapter_fragment("Ps", 9),
        word("τίτλος"),
    ]
    fragments.extend(word(f"ψ9_{index}") for index in range(2, 22))
    fragments.append(word("ψ10_1"))
    fragments.extend(
        [
            chapter_fragment("Ps", 151),
            word("ψ151"),
            book_fragment("Jdt"),
            chapter_fragment("Jdt", 1),
            word("Ἰουδίθ"),
            book_fragment("Dan"),
            chapter_fragment("Dan", 3),
        ]
    )
    fragments.extend(word(f"δ{index}") for index in range(1, 92))
    fragments.extend(
        [
            book_fragment("Esth"),
            chapter_fragment("Esth", 1),
            word("προσθήκη"),
            book_fragment("Odes"),
            chapter_fragment("Odes", 12),
            word("προσευχή"),
        ]
    )
    return fragments


class CrosswireLxxImportTests(unittest.TestCase):
    def test_metadata_and_source_row_store_exact_crosswire_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            write_fake_lxx_zip(zip_path, fake_lxx_fragments())

            metadata = read_crosswire_lxx_metadata(zip_path)
            source_row = crosswire_lxx_module_source_row(
                zip_path,
                module_id="na28_lxx",
            )

            self.assertEqual(metadata.module_name, "LXX")
            self.assertEqual(metadata.exact_version, "3.2 (2025-03-15)")
            self.assertEqual(source_row["source_version"], "3.2 (2025-03-15)")
            self.assertEqual(
                source_row["license"],
                "Copyrighted; Free non-commercial distribution",
            )
            self.assertRegex(str(source_row["checksum_sha256"]), r"^[0-9a-f]{64}$")

    def test_exports_ztext_to_intermediate_source_verses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            write_fake_lxx_zip(zip_path, fake_lxx_fragments())

            source_verses = list(iter_crosswire_lxx_source_verses(zip_path))

            self.assertEqual(source_verses[0].native_ref, "Gen.1.1")
            self.assertIn("raw_osis", source_verses[0].__dataclass_fields__)
            self.assertIn("Ps.9.22", [verse.native_ref for verse in source_verses])
            self.assertIn("Dan.3.91", [verse.native_ref for verse in source_verses])

    def test_ztext_reader_expands_16_bit_size_overflow_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            long_surface = "α" * 33_000
            write_fake_lxx_zip(
                zip_path,
                [
                    book_fragment("Gen"),
                    chapter_fragment("Gen", 1),
                    word(long_surface),
                ],
            )

            source_verses = list(iter_crosswire_lxx_source_verses(zip_path))
            result = build_lxx_import_result(tuple(source_verses))

            self.assertTrue(source_verses[0].raw_osis.endswith("</w>"))
            self.assertEqual(result.module_verses[0].tokens[0].surface, long_surface)
            self.assertFalse(
                any(warning.code == "unparseable_osis" for warning in result.warnings)
            )

    def test_genesis_1_1_imports_words_strong_morphology_and_schema_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            write_fake_lxx_zip(zip_path, fake_lxx_fragments())
            result = build_lxx_import_result(tuple(iter_crosswire_lxx_source_verses(zip_path)))

            verse = next(
                module_verse
                for module_verse in result.module_verses
                if module_verse.canonical_ref == "Gen.1.1"
            )
            self.assertEqual(verse.native_ref, "Gen.1.1")
            self.assertEqual(verse.text_plain, "ἐν ἀρχῇ")
            self.assertEqual(verse.tokens_count, 2)
            self.assertEqual(verse.tokens[0].lemma, "strong:G1722")
            self.assertEqual(verse.tokens[0].morphology, "packard:P")
            self.assertEqual(verse.tokens[0].strong_segments[0].strong, "G1722")
            self.assertEqual(verse.tokens[1].strong_segments[0].strong, "G746")
            self.assertEqual(normalize_strong("G0746"), "G746")

            connection = sqlite3.connect(":memory:")
            try:
                create_bible_module_schema(
                    connection,
                    include_token_tables=True,
                    date_iso="2026-05-23T00:00:00Z",
                )
                insert_minimal_module_fixture(
                    connection,
                    code="NA28_LXX",
                    module_kind="original_language",
                    source_id="crosswire_lxx",
                    source_text_id=CROSSWIRE_LXX_SOURCE_TEXT_ID,
                )
                connection.execute(
                    """
                    INSERT INTO module_verses(
                      module_verse_id,
                      source_text_id,
                      native_ref,
                      book_id,
                      chapter,
                      verse,
                      subverse,
                      text_plain,
                      text_display,
                      tokens_count,
                      sort_key
                    )
                    VALUES(
                      :module_verse_id,
                      :source_text_id,
                      :native_ref,
                      :book_id,
                      :chapter,
                      :verse,
                      :subverse,
                      :text_plain,
                      :text_display,
                      :tokens_count,
                      :sort_key
                    )
                    """,
                    verse.as_module_verse_row(module_verse_id=1),
                )
                token = verse.tokens[1]
                connection.execute(
                    """
                    INSERT INTO tokens(
                      token_id,
                      module_verse_id,
                      source_text_id,
                      token_order,
                      source_ref,
                      text_type,
                      surface,
                      surface_normalized,
                      surface_search,
                      transliteration,
                      lemma,
                      morphology,
                      gloss,
                      raw_json
                    )
                    VALUES(
                      :token_id,
                      :module_verse_id,
                      :source_text_id,
                      :token_order,
                      :source_ref,
                      :text_type,
                      :surface,
                      :surface_normalized,
                      :surface_search,
                      :transliteration,
                      :lemma,
                      :morphology,
                      :gloss,
                      :raw_json
                    )
                    """,
                    token.as_token_row(module_verse_id=1, token_id=1),
                )
                connection.execute(
                    """
                    INSERT INTO token_strongs(
                      token_id,
                      strong,
                      raw_strong,
                      role,
                      segment_order,
                      segment_surface,
                      is_primary
                    )
                    VALUES(
                      :token_id,
                      :strong,
                      :raw_strong,
                      :role,
                      :segment_order,
                      :segment_surface,
                      :is_primary
                    )
                    """,
                    token.token_strong_rows(token_id=1)[0],
                )

                stored = connection.execute(
                    "SELECT strong, raw_strong FROM token_strongs"
                ).fetchone()
                self.assertEqual(tuple(stored), ("G746", "G0746"))
            finally:
                connection.close()

    def test_psalm_numbering_preserves_native_ref_and_links_to_protestant_ref(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            write_fake_lxx_zip(zip_path, fake_lxx_fragments())

            result = build_lxx_import_result(tuple(iter_crosswire_lxx_source_verses(zip_path)))
            mapped = next(
                verse for verse in result.module_verses if verse.native_ref == "Ps.9.22"
            )

            self.assertEqual(mapped.canonical_ref, "Ps.10.1")
            self.assertEqual(mapped.chapter, 10)
            self.assertEqual(mapped.verse, 1)
            self.assertTrue(
                any(warning.code == "excluded_psalm_title" for warning in result.warnings)
            )
            self.assertTrue(
                any(warning.code == "excluded_psalm_151" for warning in result.warnings)
            )

    def test_apocrypha_odes_daniel_and_esther_additions_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "LXX.zip"
            write_fake_lxx_zip(zip_path, fake_lxx_fragments())

            result = build_lxx_import_result(tuple(iter_crosswire_lxx_source_verses(zip_path)))
            native_refs = {verse.native_ref for verse in result.module_verses}
            warning_codes = {warning.code for warning in result.warnings}

            self.assertNotIn("Jdt.1.1", native_refs)
            self.assertNotIn("Odes.12.1", native_refs)
            self.assertNotIn("Dan.3.24", native_refs)
            self.assertNotIn("Esth.1.1", native_refs)
            self.assertIn("Dan.3.91", native_refs)
            self.assertIn("excluded_apocrypha", warning_codes)
            self.assertIn("excluded_odes", warning_codes)
            self.assertIn("excluded_daniel_addition", warning_codes)
            self.assertIn("ambiguous_source_mapping", warning_codes)

            dan_tail = next(
                verse for verse in result.module_verses if verse.native_ref == "Dan.3.91"
            )
            self.assertEqual(dan_tail.canonical_ref, "Dan.3.24")

    def test_warnings_cover_missing_strong_and_unparseable_morphology(self) -> None:
        source_verse = LxxSourceVerse(
            source_book_code="Gen",
            chapter=1,
            verse=1,
            entry_index=1,
            block_index=1,
            raw_osis='<w morph="bad-code">ἄνευ</w>',
        )

        _tokens, warnings = parse_lxx_tokens(
            source_verse,
            canonical_verse=next(
                verse
                for verse in build_lxx_import_result([source_verse]).module_verses
                if verse.canonical_ref == "Gen.1.1"
            ),
        )

        self.assertEqual(
            {warning.code for warning in warnings},
            {"missing_strong", "unparseable_morphology"},
        )


if __name__ == "__main__":
    unittest.main()

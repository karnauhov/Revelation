from __future__ import annotations

import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from .canon import CanonicalVerse, get_canonical_verse, lxx_canonical_code_for_source_book
from .guards import ImportGuardError
from .sources import SOURCE_SPECS_BY_ID
from .tagnt import normalize_strong, normalize_surface, surface_search_text

CROSSWIRE_LXX_SOURCE_ID = "crosswire_lxx"
CROSSWIRE_LXX_SOURCE_TEXT_ID = "crosswire_lxx_ot"

_CONF_PATH = "mods.d/lxx.conf"
_ZTEXT_BASE_PATH = "modules/texts/ztext/lxx"
_BOOK_START_PATTERN = re.compile(
    r'<div\b(?=[^>]*\bsID=)(?=[^>]*\btype="book")[^>]*\bosisID="([^"]+)"[^>]*/>'
)
_CHAPTER_START_PATTERN = re.compile(
    r'<chapter\b(?=[^>]*\bsID=)[^>]*\bosisID="([^"]+)"[^>]*/>'
)
_STRUCTURAL_MILESTONE_PATTERN = re.compile(
    r"\s*<(?:(?:div|chapter)\b[^>]*/>|seg\b[^>]*/>)\s*"
)
_TAG_PATTERN = re.compile(r"<[^>]+>")
_SPACE_BEFORE_PUNCTUATION_PATTERN = re.compile(r"\s+([,.;:!?··\]\)])")
_SPACE_AFTER_OPEN_BRACKET_PATTERN = re.compile(r"([\[\(])\s+")
_STRONG_ATTR_PATTERN = re.compile(r"strong:([GH]\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?)")
_PACKARD_MORPH_PATTERN = re.compile(r"^packard:[A-Za-z0-9?+_.-]+$")

_DANIEL_ADDITION_RANGE = range(24, 91)
_DANIEL_CANONICAL_TAIL_START = 91
_DANIEL_CANONICAL_TAIL_END = 97
_ESTHER_MIXED_ADDITION_REFS = {
    (1, 1),
    (3, 13),
    (4, 17),
    (5, 1),
    (5, 2),
    (8, 12),
    (8, 13),
    (10, 3),
}


@dataclass(frozen=True)
class CrosswireLxxMetadata:
    module_name: str
    description: str
    version: str
    sword_version_date: str
    distribution_license: str
    source_type: str
    encoding: str
    compress_type: str
    block_type: str
    versification: str
    text_source: str
    raw_config: str

    @property
    def exact_version(self) -> str:
        if self.sword_version_date:
            return f"{self.version} ({self.sword_version_date})"
        return self.version


@dataclass(frozen=True)
class ZTextEntry:
    entry_index: int
    block_index: int
    start: int
    size: int
    text: str


@dataclass(frozen=True)
class LxxSourceVerse:
    source_book_code: str
    chapter: int
    verse: int
    entry_index: int
    block_index: int
    raw_osis: str

    @property
    def native_ref(self) -> str:
        return f"{self.source_book_code}.{self.chapter}.{self.verse}"


@dataclass(frozen=True)
class LxxImportWarning:
    severity: str
    code: str
    source_ref: str
    message: str
    raw_payload: dict[str, object]

    def as_import_warning_row(
        self,
        *,
        source_id: str = CROSSWIRE_LXX_SOURCE_ID,
        warning_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "source_id": source_id,
            "severity": self.severity,
            "code": self.code,
            "source_ref": self.source_ref,
            "message": self.message,
            "raw_json": json.dumps(self.raw_payload, ensure_ascii=False, sort_keys=True),
        }
        if warning_id is not None:
            row["warning_id"] = warning_id
        return row


@dataclass(frozen=True)
class LxxStrongSegment:
    strong: str
    raw_strong: str
    role: str
    segment_order: int
    segment_surface: str
    is_primary: bool

    def as_token_strong_row(self, *, token_id: int) -> dict[str, object]:
        return {
            "token_id": token_id,
            "strong": self.strong,
            "raw_strong": self.raw_strong,
            "role": self.role,
            "segment_order": self.segment_order,
            "segment_surface": self.segment_surface,
            "is_primary": 1 if self.is_primary else 0,
        }


@dataclass(frozen=True)
class LxxToken:
    source_ref: str
    canonical_ref: str
    token_order: int
    surface: str
    surface_normalized: str
    surface_search: str
    transliteration: str
    lemma: str
    morphology: str
    strong_segments: tuple[LxxStrongSegment, ...]
    raw_json: str

    def as_token_row(
        self,
        *,
        module_verse_id: int,
        source_text_id: str = CROSSWIRE_LXX_SOURCE_TEXT_ID,
        token_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "module_verse_id": module_verse_id,
            "source_text_id": source_text_id,
            "token_order": self.token_order,
            "source_ref": self.source_ref,
            "text_type": "w",
            "surface": self.surface,
            "surface_normalized": self.surface_normalized,
            "surface_search": self.surface_search,
            "transliteration": self.transliteration,
            "lemma": self.lemma,
            "morphology": self.morphology,
            "gloss": "",
            "raw_json": self.raw_json,
        }
        if token_id is not None:
            row["token_id"] = token_id
        return row

    def token_strong_rows(self, *, token_id: int) -> list[dict[str, object]]:
        return [
            segment.as_token_strong_row(token_id=token_id)
            for segment in self.strong_segments
        ]


@dataclass(frozen=True)
class LxxModuleVerse:
    canonical_verse_id: int
    canonical_ref: str
    native_ref: str
    book_id: int
    chapter: int
    verse: int
    text_plain: str
    text_display: str
    tokens_count: int
    sort_key: int
    tokens: tuple[LxxToken, ...]

    def as_module_verse_row(
        self,
        *,
        module_verse_id: int,
        source_text_id: str = CROSSWIRE_LXX_SOURCE_TEXT_ID,
    ) -> dict[str, object]:
        return {
            "module_verse_id": module_verse_id,
            "source_text_id": source_text_id,
            "native_ref": self.native_ref,
            "book_id": self.book_id,
            "chapter": self.chapter,
            "verse": self.verse,
            "subverse": "",
            "text_plain": self.text_plain,
            "text_display": self.text_display,
            "tokens_count": self.tokens_count,
            "sort_key": self.sort_key,
        }

    def as_module_verse_link_row(self, *, module_verse_id: int) -> dict[str, object]:
        return {
            "module_verse_id": module_verse_id,
            "canonical_verse_id": self.canonical_verse_id,
            "link_kind": "exact",
            "note": f"native_ref={self.native_ref}",
        }


@dataclass(frozen=True)
class LxxImportResult:
    metadata: CrosswireLxxMetadata | None
    source_verses_count: int
    module_verses: tuple[LxxModuleVerse, ...]
    warnings: tuple[LxxImportWarning, ...]


def parse_crosswire_lxx_config(config_text: str) -> CrosswireLxxMetadata:
    module_name = ""
    values: dict[str, str] = {}
    for raw_line in config_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            module_name = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return CrosswireLxxMetadata(
        module_name=module_name,
        description=values.get("Description", ""),
        version=values.get("Version", ""),
        sword_version_date=values.get("SwordVersionDate", ""),
        distribution_license=values.get("DistributionLicense", ""),
        source_type=values.get("SourceType", ""),
        encoding=values.get("Encoding", ""),
        compress_type=values.get("CompressType", ""),
        block_type=values.get("BlockType", ""),
        versification=values.get("Versification", ""),
        text_source=values.get("TextSource", ""),
        raw_config=config_text,
    )


def read_crosswire_lxx_metadata(zip_path: str | Path) -> CrosswireLxxMetadata:
    with zipfile.ZipFile(zip_path) as archive:
        return parse_crosswire_lxx_config(
            archive.read(_CONF_PATH).decode("utf-8", errors="replace")
        )


def crosswire_lxx_module_source_row(
    zip_path: str | Path,
    *,
    module_id: str,
    source_id: str = CROSSWIRE_LXX_SOURCE_ID,
) -> dict[str, object]:
    metadata = read_crosswire_lxx_metadata(zip_path)
    source_spec = SOURCE_SPECS_BY_ID[CROSSWIRE_LXX_SOURCE_ID]
    return {
        "source_id": source_id,
        "module_id": module_id,
        "title": source_spec.title,
        "source_url": source_spec.source_page_url,
        "source_version": metadata.exact_version,
        "license": metadata.distribution_license or source_spec.license_name,
        "checksum_sha256": _sha256_file(zip_path),
        "import_notes": (
            f"CrossWire module={metadata.module_name}; "
            f"Versification={metadata.versification}; "
            f"BlockType={metadata.block_type}; CompressType={metadata.compress_type}"
        ),
    }


def iter_crosswire_lxx_ztext_entries(
    zip_path: str | Path,
    *,
    testament: str = "ot",
) -> Iterator[ZTextEntry]:
    base = f"{_ZTEXT_BASE_PATH}/{testament}"
    with zipfile.ZipFile(zip_path) as archive:
        block_index = _read_ztext_block_index(archive.read(f"{base}.bzs"))
        verse_index = _read_ztext_verse_index(archive.read(f"{base}.bzv"))
        compressed_payload = archive.read(f"{base}.bzz")
        block_cache: dict[int, bytes] = {}

        for entry_index, (block_number, start, size) in enumerate(verse_index):
            if size == 0:
                continue
            if block_number not in block_cache:
                offset, compressed_size, _uncompressed_size = block_index[block_number]
                block_cache[block_number] = zlib.decompress(
                    compressed_payload[offset : offset + compressed_size]
                )
            raw_block = block_cache[block_number]
            actual_size = _expanded_ztext_entry_size(
                verse_index,
                entry_index=entry_index,
                block_size=len(raw_block),
            )
            text = raw_block[start : start + actual_size].decode("utf-8", errors="replace")
            yield ZTextEntry(
                entry_index=entry_index,
                block_index=block_number,
                start=start,
                size=size,
                text=text,
            )


def iter_crosswire_lxx_source_verses(zip_path: str | Path) -> Iterator[LxxSourceVerse]:
    current_book: str | None = None
    current_chapter: int | None = None
    current_verse = 0

    for entry in iter_crosswire_lxx_ztext_entries(zip_path):
        for marker in _iter_ordered_markers(entry.text):
            marker_kind, marker_value = marker
            if marker_kind == "book":
                current_book = marker_value
                current_chapter = None
                current_verse = 0
            elif marker_kind == "chapter":
                chapter_book, chapter = _parse_chapter_osis_id(marker_value)
                current_book = chapter_book
                current_chapter = chapter
                current_verse = 0

        if current_book is None or current_chapter is None:
            continue
        if not _has_verse_content(entry.text):
            continue

        current_verse += 1
        yield LxxSourceVerse(
            source_book_code=current_book,
            chapter=current_chapter,
            verse=current_verse,
            entry_index=entry.entry_index,
            block_index=entry.block_index,
            raw_osis=entry.text,
        )


def build_lxx_import_result(
    source_verses: Sequence[LxxSourceVerse],
    *,
    metadata: CrosswireLxxMetadata | None = None,
) -> LxxImportResult:
    module_verses: list[LxxModuleVerse] = []
    warnings: list[LxxImportWarning] = []

    for source_verse in source_verses:
        mapping = _canonical_verse_for_lxx_source_verse(source_verse)
        if isinstance(mapping, LxxImportWarning):
            warnings.append(mapping)
            continue

        tokens, token_warnings = parse_lxx_tokens(source_verse, mapping)
        warnings.extend(token_warnings)
        text_plain = join_lxx_surfaces(tokens)
        module_verses.append(
            LxxModuleVerse(
                canonical_verse_id=mapping.canonical_verse_id,
                canonical_ref=mapping.canonical_ref,
                native_ref=source_verse.native_ref,
                book_id=mapping.book_id,
                chapter=mapping.chapter,
                verse=mapping.verse,
                text_plain=text_plain,
                text_display=text_plain,
                tokens_count=len(tokens),
                sort_key=mapping.sort_key,
                tokens=tuple(tokens),
            )
        )

    module_verses.sort(key=lambda verse: (verse.sort_key, verse.native_ref))
    return LxxImportResult(
        metadata=metadata,
        source_verses_count=len(source_verses),
        module_verses=tuple(module_verses),
        warnings=tuple(warnings),
    )


def build_lxx_import_result_from_zip(zip_path: str | Path) -> LxxImportResult:
    metadata = read_crosswire_lxx_metadata(zip_path)
    source_verses = tuple(iter_crosswire_lxx_source_verses(zip_path))
    return build_lxx_import_result(source_verses, metadata=metadata)


def parse_lxx_tokens(
    source_verse: LxxSourceVerse,
    canonical_verse: CanonicalVerse,
) -> tuple[tuple[LxxToken, ...], tuple[LxxImportWarning, ...]]:
    try:
        root = ET.fromstring(f"<root>{source_verse.raw_osis}</root>")
    except ET.ParseError as error:
        return (), (
            _warning(
                code="unparseable_osis",
                source_ref=source_verse.native_ref,
                message=f"Could not parse LXX OSIS fragment: {error}",
                raw_payload={"raw_osis": source_verse.raw_osis},
            ),
        )

    tokens: list[LxxToken] = []
    warnings: list[LxxImportWarning] = []
    for token_order, element in enumerate(root.iter("w"), start=1):
        surface = "".join(element.itertext()).strip()
        lemma_attr = element.attrib.get("lemma", "").strip()
        morph_attr = element.attrib.get("morph", "").strip()
        xlit_attr = element.attrib.get("xlit", "").strip()
        strong_segments = _parse_lxx_strong_segments(
            lemma_attr,
            surface=surface,
        )

        token_ref = f"{source_verse.native_ref}#{token_order}"
        if not strong_segments:
            warnings.append(
                _warning(
                    code="missing_strong",
                    source_ref=token_ref,
                    message="LXX word has no Strong lemma tag.",
                    raw_payload={
                        "attrs": dict(element.attrib),
                        "surface": surface,
                        "native_ref": source_verse.native_ref,
                    },
                )
            )
        if not morph_attr:
            warnings.append(
                _warning(
                    code="missing_morphology",
                    source_ref=token_ref,
                    message="LXX word has no morphology tag.",
                    raw_payload={
                        "attrs": dict(element.attrib),
                        "surface": surface,
                        "native_ref": source_verse.native_ref,
                    },
                )
            )
        elif not _PACKARD_MORPH_PATTERN.match(morph_attr):
            warnings.append(
                _warning(
                    code="unparseable_morphology",
                    source_ref=token_ref,
                    message="LXX word morphology is not a recognized Packard code.",
                    raw_payload={
                        "attrs": dict(element.attrib),
                        "surface": surface,
                        "morphology": morph_attr,
                        "native_ref": source_verse.native_ref,
                    },
                )
            )

        raw_payload = {
            "attrs": dict(element.attrib),
            "canonical_ref": canonical_verse.canonical_ref,
            "entry_index": source_verse.entry_index,
            "native_ref": source_verse.native_ref,
            "raw_osis": ET.tostring(element, encoding="unicode"),
            "source_book_code": source_verse.source_book_code,
        }
        tokens.append(
            LxxToken(
                source_ref=token_ref,
                canonical_ref=canonical_verse.canonical_ref,
                token_order=token_order,
                surface=surface,
                surface_normalized=normalize_surface(surface),
                surface_search=surface_search_text(surface),
                transliteration=xlit_attr,
                lemma=lemma_attr,
                morphology=morph_attr,
                strong_segments=strong_segments,
                raw_json=json.dumps(raw_payload, ensure_ascii=False, sort_keys=True),
            )
        )

    return tuple(tokens), tuple(warnings)


def join_lxx_surfaces(tokens: Sequence[LxxToken]) -> str:
    text = " ".join(token.surface for token in tokens if token.surface)
    text = _SPACE_BEFORE_PUNCTUATION_PATTERN.sub(r"\1", text)
    text = _SPACE_AFTER_OPEN_BRACKET_PATTERN.sub(r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_verse_for_lxx_source_verse(
    source_verse: LxxSourceVerse,
) -> CanonicalVerse | LxxImportWarning:
    source_book = source_verse.source_book_code
    chapter = source_verse.chapter
    verse = source_verse.verse

    if source_book == "Ps":
        mapped = _map_lxx_psalm_ref(chapter, verse)
        if isinstance(mapped, LxxImportWarning):
            return mapped
        chapter, verse = mapped

    if source_book == "Dan":
        if source_verse.chapter == 3 and source_verse.verse in _DANIEL_ADDITION_RANGE:
            return _warning(
                code="excluded_daniel_addition",
                source_ref=source_verse.native_ref,
                message="Daniel 3 Greek addition is excluded from canonical NA28_LXX.",
                raw_payload={"native_ref": source_verse.native_ref},
            )
        if (
            source_verse.chapter == 3
            and _DANIEL_CANONICAL_TAIL_START
            <= source_verse.verse
            <= _DANIEL_CANONICAL_TAIL_END
        ):
            verse = source_verse.verse - 67

    if source_book == "Esth":
        if (chapter, verse) in _ESTHER_MIXED_ADDITION_REFS:
            return _warning(
                code="ambiguous_source_mapping",
                source_ref=source_verse.native_ref,
                message=(
                    "Greek Esther addition is mixed with canonical text in this "
                    "source verse; it is excluded pending explicit canonical mapping."
                ),
                raw_payload={"native_ref": source_verse.native_ref},
            )

    try:
        canonical_code = lxx_canonical_code_for_source_book(source_book)
        return get_canonical_verse(canonical_code, chapter, verse)
    except (ImportGuardError, KeyError) as error:
        return _warning(
            code=_exclusion_code_for(source_book, chapter, verse),
            source_ref=source_verse.native_ref,
            message=str(error),
            raw_payload={
                "native_ref": source_verse.native_ref,
                "source_book_code": source_book,
                "chapter": chapter,
                "verse": verse,
            },
        )


def _map_lxx_psalm_ref(
    chapter: int,
    verse: int,
) -> tuple[int, int] | LxxImportWarning:
    if chapter == 151:
        return _warning(
            code="excluded_psalm_151",
            source_ref=f"Ps.{chapter}.{verse}",
            message="Psalm 151 is outside the 150-Psalm Protestant canon.",
            raw_payload={"native_ref": f"Ps.{chapter}.{verse}"},
        )
    if chapter <= 8:
        return chapter, verse
    if chapter == 9:
        if verse == 1:
            return _warning(
                code="excluded_psalm_title",
                source_ref=f"Ps.{chapter}.{verse}",
                message="LXX Psalm superscription is not imported as a canonical verse.",
                raw_payload={"native_ref": f"Ps.{chapter}.{verse}"},
            )
        if 2 <= verse <= 21:
            return 9, verse - 1
        if 22 <= verse <= 39:
            return 10, verse - 21
        return _warning(
            code="ambiguous_source_mapping",
            source_ref=f"Ps.{chapter}.{verse}",
            message="LXX Psalm 9 source verse is outside the mapped Protestant range.",
            raw_payload={"native_ref": f"Ps.{chapter}.{verse}"},
        )
    if 10 <= chapter <= 112:
        return chapter + 1, verse
    if chapter == 113:
        if verse <= 8:
            return 114, verse
        return 115, verse - 8
    if chapter == 114:
        return 116, verse
    if chapter == 115:
        return 116, verse + 9
    if 116 <= chapter <= 145:
        return chapter + 1, verse
    if chapter == 146:
        return 147, verse
    if chapter == 147:
        return 147, verse + 11
    return chapter, verse


def _parse_lxx_strong_segments(
    lemma_attr: str,
    *,
    surface: str,
) -> tuple[LxxStrongSegment, ...]:
    segments: list[LxxStrongSegment] = []
    seen: set[str] = set()
    for raw_strong in _STRONG_ATTR_PATTERN.findall(lemma_attr):
        strong = normalize_strong(raw_strong)
        if strong in seen:
            continue
        segments.append(
            LxxStrongSegment(
                strong=strong,
                raw_strong=raw_strong,
                role="primary" if not segments else "secondary",
                segment_order=len(segments),
                segment_surface=surface,
                is_primary=not segments,
            )
        )
        seen.add(strong)
    return tuple(segments)


def _read_ztext_block_index(data: bytes) -> tuple[tuple[int, int, int], ...]:
    if len(data) % 12 != 0:
        raise ValueError("SWORD zText block index size must be divisible by 12")
    return tuple(
        struct.unpack("<III", data[offset : offset + 12])
        for offset in range(0, len(data), 12)
    )


def _read_ztext_verse_index(data: bytes) -> tuple[tuple[int, int, int], ...]:
    if len(data) % 10 != 0:
        raise ValueError("SWORD zText verse index size must be divisible by 10")
    return tuple(
        struct.unpack("<IIH", data[offset : offset + 10])
        for offset in range(0, len(data), 10)
    )


def _expanded_ztext_entry_size(
    verse_index: Sequence[tuple[int, int, int]],
    *,
    entry_index: int,
    block_size: int,
) -> int:
    block_number, start, stored_size = verse_index[entry_index]
    next_start = block_size
    if entry_index + 1 < len(verse_index):
        next_block_number, candidate_start, _candidate_size = verse_index[entry_index + 1]
        if next_block_number == block_number and candidate_start > start:
            next_start = candidate_start

    span = next_start - start
    if span > stored_size and (span - stored_size) % 65_536 == 0:
        return span
    return stored_size


def _iter_ordered_markers(text: str) -> Iterator[tuple[str, str]]:
    matches: list[tuple[int, str, str]] = []
    matches.extend(
        (match.start(), "book", match.group(1))
        for match in _BOOK_START_PATTERN.finditer(text)
    )
    matches.extend(
        (match.start(), "chapter", match.group(1))
        for match in _CHAPTER_START_PATTERN.finditer(text)
    )
    for _position, kind, value in sorted(matches, key=lambda item: item[0]):
        yield kind, value


def _parse_chapter_osis_id(osis_id: str) -> tuple[str, int]:
    book_code, chapter = osis_id.rsplit(".", 1)
    return book_code, int(chapter)


def _has_verse_content(text: str) -> bool:
    markerless = _STRUCTURAL_MILESTONE_PATTERN.sub("", text)
    plain = _TAG_PATTERN.sub("", markerless).strip()
    return "<w" in markerless or bool(plain)


def _warning(
    *,
    code: str,
    source_ref: str,
    message: str,
    raw_payload: dict[str, object],
    severity: str = "warning",
) -> LxxImportWarning:
    return LxxImportWarning(
        severity=severity,
        code=code,
        source_ref=source_ref,
        message=message,
        raw_payload=raw_payload,
    )


def _exclusion_code_for(source_book: str, chapter: int, verse: int) -> str:
    if source_book in {"Jdt", "Tob", "Wis", "Sir", "Bar", "EpJer", "Sus", "Bel"}:
        return "excluded_apocrypha"
    if source_book in {"1Esd", "1Macc", "2Macc", "3Macc", "4Macc", "PssSol"}:
        return "excluded_apocrypha"
    if source_book == "Odes":
        return "excluded_odes"
    if source_book == "Ps" and chapter == 151:
        return "excluded_psalm_151"
    if source_book == "Dan" and chapter == 3 and verse in _DANIEL_ADDITION_RANGE:
        return "excluded_daniel_addition"
    if source_book == "Esth":
        return "excluded_esther_addition"
    return "ambiguous_source_mapping"


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from .canon import CanonicalVerse, get_canonical_verse

TAGNT_SOURCE_ID = "stepbible_tagnt"
TAGNT_SOURCE_TEXT_ID = "tagnt_na28_nt"

_REFERENCE_PATTERN = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]+)\."
    r"(?P<chapter>\d+)\."
    r"(?P<verse>\d+)#"
    r"(?P<token_order>\d+)="
    r"(?P<text_type>\S+)$"
)
_STRONG_PATTERN = re.compile(r"[GH]\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?")
_PAREN_TRANSLITERATION_PATTERN = re.compile(r"^(?P<surface>.*?)(?:\s+\((?P<transliteration>[^()]*)\))\s*$")
_SPACE_BEFORE_PUNCTUATION_PATTERN = re.compile(r"\s+([,.;:!?··\]\)])")
_SPACE_AFTER_OPEN_BRACKET_PATTERN = re.compile(r"([\[\(])\s+")

_TAGNT_BOOK_TO_CANONICAL = {
    "Mat": "Mat",
    "Matt": "Mat",
    "Mrk": "Mark",
    "Mar": "Mark",
    "Mark": "Mark",
    "Luk": "Luke",
    "Luke": "Luke",
    "Jhn": "John",
    "Joh": "John",
    "John": "John",
    "Act": "Acts",
    "Acts": "Acts",
    "Rom": "Rom",
    "1Co": "1Cor",
    "1Cor": "1Cor",
    "2Co": "2Cor",
    "2Cor": "2Cor",
    "Gal": "Gal",
    "Eph": "Eph",
    "Php": "Phil",
    "Phil": "Phil",
    "Col": "Col",
    "1Th": "1Thess",
    "1Thess": "1Thess",
    "2Th": "2Thess",
    "2Thess": "2Thess",
    "1Ti": "1Tim",
    "1Tim": "1Tim",
    "2Ti": "2Tim",
    "2Tim": "2Tim",
    "Tit": "Titus",
    "Titus": "Titus",
    "Phm": "Phlm",
    "Phlm": "Phlm",
    "Heb": "Heb",
    "Jas": "Jas",
    "Jam": "Jas",
    "1Pe": "1Pet",
    "1Pet": "1Pet",
    "2Pe": "2Pet",
    "2Pet": "2Pet",
    "1Jn": "1John",
    "1John": "1John",
    "2Jn": "2John",
    "2John": "2John",
    "3Jn": "3John",
    "3John": "3John",
    "Jud": "Jude",
    "Jude": "Jude",
    "Rev": "Rev",
}


@dataclass(frozen=True)
class TagntReference:
    source_ref: str
    source_book_code: str
    canonical_book_code: str
    chapter: int
    verse: int
    token_order: int
    text_type: str

    @property
    def native_ref(self) -> str:
        return f"{self.source_book_code}.{self.chapter}.{self.verse}"

    @property
    def canonical_verse(self) -> CanonicalVerse:
        return get_canonical_verse(self.canonical_book_code, self.chapter, self.verse)


@dataclass(frozen=True)
class TagntStrongSegment:
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
class TagntToken:
    reference: TagntReference
    surface: str
    surface_normalized: str
    surface_search: str
    transliteration: str
    lemma: str
    morphology: str
    gloss: str
    english: str
    spanish: str
    submeaning: str
    conjoin_word: str
    editions: tuple[str, ...]
    meaning_variants: str
    spelling_variants: str
    strong_segments: tuple[TagntStrongSegment, ...]
    raw_json: str

    @property
    def source_ref(self) -> str:
        return self.reference.source_ref

    @property
    def native_ref(self) -> str:
        return self.reference.native_ref

    @property
    def canonical_verse(self) -> CanonicalVerse:
        return self.reference.canonical_verse

    @property
    def is_na28(self) -> bool:
        return "NA28" in self.editions

    def as_token_row(
        self,
        *,
        module_verse_id: int,
        source_text_id: str = TAGNT_SOURCE_TEXT_ID,
        token_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "module_verse_id": module_verse_id,
            "source_text_id": source_text_id,
            "token_order": self.reference.token_order,
            "source_ref": self.source_ref,
            "text_type": self.reference.text_type,
            "surface": self.surface,
            "surface_normalized": self.surface_normalized,
            "surface_search": self.surface_search,
            "transliteration": self.transliteration,
            "lemma": self.lemma,
            "morphology": self.morphology,
            "gloss": self.gloss,
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
class TagntModuleVerse:
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
    tokens: tuple[TagntToken, ...]

    def as_module_verse_row(
        self,
        *,
        module_verse_id: int,
        source_text_id: str = TAGNT_SOURCE_TEXT_ID,
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
            "note": "",
        }


def tagnt_canonical_code_for_source_book(source_book_code: str) -> str:
    canonical_code = _TAGNT_BOOK_TO_CANONICAL.get(source_book_code)
    if canonical_code is None:
        raise ValueError(f"Unknown TAGNT NT book code: {source_book_code}")
    return canonical_code


def parse_tagnt_reference(raw_reference: str) -> TagntReference:
    match = _REFERENCE_PATTERN.match(raw_reference.strip())
    if match is None:
        raise ValueError(f"Invalid TAGNT data reference: {raw_reference}")
    source_book_code = match.group("book")
    return TagntReference(
        source_ref=raw_reference.strip(),
        source_book_code=source_book_code,
        canonical_book_code=tagnt_canonical_code_for_source_book(source_book_code),
        chapter=int(match.group("chapter")),
        verse=int(match.group("verse")),
        token_order=int(match.group("token_order")),
        text_type=match.group("text_type"),
    )


def normalize_strong(raw_strong: str) -> str:
    value = raw_strong.strip()
    match = re.match(r"^([GH])0*(\d+)(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?$", value)
    if match is None:
        raise ValueError(f"Invalid Strong key: {raw_strong}")
    prefix = match.group(1)
    number = int(match.group(2))
    return f"{prefix}{number}"


def parse_tagnt_row(
    line: str,
    *,
    source_path: str | Path | None = None,
    line_number: int | None = None,
) -> TagntToken | None:
    stripped = line.strip("\ufeff\r\n")
    if not stripped:
        return None
    columns = stripped.split("\t")
    first_column = _field(columns, 0)
    if _REFERENCE_PATTERN.match(first_column) is None:
        return None

    reference = parse_tagnt_reference(first_column)
    surface, transliteration = _parse_surface(_field(columns, 1))
    lemma, gloss = _parse_lemma_gloss(_field(columns, 4))
    morphology, primary_raw_strong = _parse_dstrong_grammar(_field(columns, 3))
    editions = _parse_editions(_field(columns, 5))
    strong_segments = _parse_strong_segments(
        primary_raw_strong=primary_raw_strong,
        alt_strongs=_field(columns, 12),
        surface=surface,
    )
    raw_payload = {
        "source_path": str(source_path) if source_path is not None else "",
        "line_number": line_number,
        "raw_line": stripped,
        "columns": columns,
        "source_ref": reference.source_ref,
        "native_ref": reference.native_ref,
        "canonical_ref": reference.canonical_verse.canonical_ref,
        "editions": editions,
        "meaning_variants": _field(columns, 6),
        "spelling_variants": _field(columns, 7),
        "dstrong_grammar": _field(columns, 3),
        "dictionary": _field(columns, 4),
        "sstrong_instance": _field(columns, 11),
        "alt_strongs": _field(columns, 12),
    }

    return TagntToken(
        reference=reference,
        surface=surface,
        surface_normalized=normalize_surface(surface),
        surface_search=surface_search_text(surface),
        transliteration=transliteration,
        lemma=lemma,
        morphology=morphology,
        gloss=gloss,
        english=_field(columns, 2),
        spanish=_field(columns, 8),
        submeaning=_field(columns, 9),
        conjoin_word=_field(columns, 10),
        editions=editions,
        meaning_variants=_field(columns, 6),
        spelling_variants=_field(columns, 7),
        strong_segments=strong_segments,
        raw_json=json.dumps(raw_payload, ensure_ascii=False, sort_keys=True),
    )


def iter_tagnt_tokens(paths: Iterable[str | Path]) -> Iterator[TagntToken]:
    for path in paths:
        source_path = Path(path)
        with source_path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                token = parse_tagnt_row(
                    line,
                    source_path=source_path,
                    line_number=line_number,
                )
                if token is not None:
                    yield token


def iter_na28_tagnt_tokens(paths: Iterable[str | Path]) -> Iterator[TagntToken]:
    for token in iter_tagnt_tokens(paths):
        if token.is_na28:
            yield token


def build_na28_module_verses(tokens: Iterable[TagntToken]) -> tuple[TagntModuleVerse, ...]:
    grouped: dict[tuple[int, str], list[TagntToken]] = defaultdict(list)
    for token in tokens:
        if token.is_na28:
            canonical_verse = token.canonical_verse
            grouped[(canonical_verse.canonical_verse_id, token.native_ref)].append(token)

    verses: list[TagntModuleVerse] = []
    for (canonical_verse_id, native_ref), verse_tokens in grouped.items():
        verse_tokens.sort(
            key=lambda token: (
                token.reference.token_order,
                token.source_ref,
            )
        )
        canonical_verse = verse_tokens[0].canonical_verse
        text_plain = join_tagnt_surfaces(verse_tokens)
        verses.append(
            TagntModuleVerse(
                canonical_verse_id=canonical_verse_id,
                canonical_ref=canonical_verse.canonical_ref,
                native_ref=native_ref,
                book_id=canonical_verse.book_id,
                chapter=canonical_verse.chapter,
                verse=canonical_verse.verse,
                text_plain=text_plain,
                text_display=text_plain,
                tokens_count=len(verse_tokens),
                sort_key=canonical_verse.sort_key,
                tokens=tuple(verse_tokens),
            )
        )

    verses.sort(key=lambda verse: verse.sort_key)
    return tuple(verses)


def join_tagnt_surfaces(tokens: Sequence[TagntToken]) -> str:
    text = " ".join(token.surface for token in tokens if token.surface)
    text = _SPACE_BEFORE_PUNCTUATION_PATTERN.sub(r"\1", text)
    text = _SPACE_AFTER_OPEN_BRACKET_PATTERN.sub(r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_surface(surface: str) -> str:
    return " ".join(surface.split())


def surface_search_text(surface: str) -> str:
    characters: list[str] = []
    previous_was_space = False
    for character in normalize_surface(surface):
        category = unicodedata.category(character)
        if category[0] in {"L", "M", "N"}:
            characters.append(character)
            previous_was_space = False
        elif character.isspace() and not previous_was_space:
            characters.append(" ")
            previous_was_space = True
    return "".join(characters).strip()


def _field(columns: Sequence[str], index: int) -> str:
    if index >= len(columns):
        return ""
    return columns[index].strip()


def _parse_surface(value: str) -> tuple[str, str]:
    match = _PAREN_TRANSLITERATION_PATTERN.match(value)
    if match is None:
        return value.strip(), ""
    return match.group("surface").strip(), match.group("transliteration").strip()


def _parse_lemma_gloss(value: str) -> tuple[str, str]:
    if "=" not in value:
        return value.strip(), ""
    lemma, gloss = value.split("=", 1)
    return lemma.strip(), gloss.strip()


def _parse_dstrong_grammar(value: str) -> tuple[str, str]:
    if "=" not in value:
        return "", ""
    strong_expression, morphology = value.rsplit("=", 1)
    strong_candidates = _STRONG_PATTERN.findall(strong_expression)
    primary_raw_strong = _select_primary_strong(strong_candidates)
    return morphology.strip(), primary_raw_strong


def _select_primary_strong(strong_candidates: Sequence[str]) -> str:
    if not strong_candidates:
        return ""
    greek_candidates = [candidate for candidate in strong_candidates if candidate.startswith("G")]
    if greek_candidates:
        return greek_candidates[-1]
    return strong_candidates[-1]


def _parse_editions(value: str) -> tuple[str, ...]:
    return tuple(edition.strip() for edition in value.split("+") if edition.strip())


def _parse_strong_segments(
    *,
    primary_raw_strong: str,
    alt_strongs: str,
    surface: str,
) -> tuple[TagntStrongSegment, ...]:
    segments: list[TagntStrongSegment] = []
    seen: set[tuple[str, str]] = set()
    if primary_raw_strong:
        strong = normalize_strong(primary_raw_strong)
        segments.append(
            TagntStrongSegment(
                strong=strong,
                raw_strong=primary_raw_strong,
                role="primary",
                segment_order=0,
                segment_surface=surface,
                is_primary=True,
            )
        )
        seen.add(("primary", strong))

    for raw_alt in _STRONG_PATTERN.findall(alt_strongs):
        strong = normalize_strong(raw_alt)
        key = ("alt", strong)
        if key in seen:
            continue
        segments.append(
            TagntStrongSegment(
                strong=strong,
                raw_strong=raw_alt,
                role="alt",
                segment_order=len(segments),
                segment_surface=surface,
                is_primary=False,
            )
        )
        seen.add(key)

    return tuple(segments)

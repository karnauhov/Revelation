from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from .tagnt import normalize_strong

LEXICON_SOURCE_IDS = (
    "step_tbesg",
    "step_tflsj_0_5624",
    "step_tflsj_extra",
)
MORPHOLOGY_SOURCE_ID = "step_tegmc"

_LEXICON_HEADER_PREFIX = "eStrong\tdStrong\tuStrong\tGreek\tTransliteration\tMorph\tGloss"
_GREEK_STRONG_PATTERN = re.compile(r"^G\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?$")
_BRIEF_MORPHOLOGY_HEADER = "Code\tExample in English\tMeaning"
_FULL_MORPHOLOGY_HEADER_PREFIX = '"1 CODE"\t'


@dataclass(frozen=True)
class LexiconEntry:
    source_id: str
    raw_strong: str
    strong: str
    dstrong: str
    ustrong: str
    greek: str
    transliteration: str
    morphology: str
    gloss: str
    definition: str
    line_number: int
    raw_line: str

    def as_dictionary_input_row(
        self,
        *,
        entry_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "source_id": self.source_id,
            "raw_strong": self.raw_strong,
            "strong": self.strong,
            "dstrong": self.dstrong,
            "ustrong": self.ustrong,
            "greek": self.greek,
            "transliteration": self.transliteration,
            "morphology": self.morphology,
            "gloss": self.gloss,
            "definition": self.definition,
            "line_number": self.line_number,
            "raw_json": json.dumps(
                {
                    "raw_line": self.raw_line,
                    "source_id": self.source_id,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        if entry_id is not None:
            row["entry_id"] = entry_id
        return row


@dataclass(frozen=True)
class MorphologyEntry:
    source_id: str
    code: str
    brief_example: str
    brief_meaning: str
    properties: dict[str, str]
    summary: str
    description: str
    example: str
    line_number: int
    raw_lines: tuple[str, ...]

    def as_dictionary_input_row(
        self,
        *,
        entry_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "source_id": self.source_id,
            "code": self.code,
            "brief_example": self.brief_example,
            "brief_meaning": self.brief_meaning,
            "properties_json": json.dumps(
                self.properties,
                ensure_ascii=False,
                sort_keys=True,
            ),
            "summary": self.summary,
            "description": self.description,
            "example": self.example,
            "line_number": self.line_number,
            "raw_json": json.dumps(
                {
                    "raw_lines": self.raw_lines,
                    "source_id": self.source_id,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        if entry_id is not None:
            row["entry_id"] = entry_id
        return row


@dataclass(frozen=True)
class StrongOccurrence:
    source: str
    strong: str
    raw_strong: str
    canonical_verse_id: int
    canonical_ref: str
    source_ref: str
    surface: str

    def as_dictionary_input_row(
        self,
        *,
        occurrence_id: int | None = None,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "source": self.source,
            "strong": self.strong,
            "raw_strong": self.raw_strong,
            "canonical_verse_id": self.canonical_verse_id,
            "canonical_ref": self.canonical_ref,
            "source_ref": self.source_ref,
            "surface": self.surface,
        }
        if occurrence_id is not None:
            row["occurrence_id"] = occurrence_id
        return row


@dataclass(frozen=True)
class StrongCoverageWarning:
    source: str
    strong: str
    occurrences_count: int
    sample_refs: tuple[str, ...]
    message: str

    def as_warning_row(self, *, warning_id: int | None = None) -> dict[str, object]:
        row: dict[str, object] = {
            "source": self.source,
            "strong": self.strong,
            "occurrences_count": self.occurrences_count,
            "sample_refs_json": json.dumps(self.sample_refs, ensure_ascii=False),
            "message": self.message,
        }
        if warning_id is not None:
            row["warning_id"] = warning_id
        return row


def parse_step_lexicon_row(
    line: str,
    *,
    source_id: str,
    line_number: int,
) -> LexiconEntry | None:
    if source_id not in LEXICON_SOURCE_IDS:
        raise ValueError(f"Unsupported STEP Greek lexicon source: {source_id}")

    stripped = line.strip("\ufeff\r\n")
    if not stripped:
        return None
    columns = stripped.split("\t")
    if len(columns) < 8:
        return None

    raw_strong = columns[0].strip()
    if _GREEK_STRONG_PATTERN.match(raw_strong) is None:
        return None

    return LexiconEntry(
        source_id=source_id,
        raw_strong=raw_strong,
        strong=normalize_strong(raw_strong),
        dstrong=columns[1].strip(),
        ustrong=columns[2].strip(),
        greek=columns[3].strip(),
        transliteration=columns[4].strip(),
        morphology=columns[5].strip(),
        gloss=columns[6].strip(),
        definition=columns[7].strip(),
        line_number=line_number,
        raw_line=stripped,
    )


def iter_step_lexicon_entries(
    path: str | Path,
    *,
    source_id: str,
) -> Iterator[LexiconEntry]:
    seen_header = False
    source_path = Path(path)
    with source_path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip("\ufeff\r\n")
            if not seen_header:
                seen_header = stripped.startswith(_LEXICON_HEADER_PREFIX)
                continue
            entry = parse_step_lexicon_row(
                line,
                source_id=source_id,
                line_number=line_number,
            )
            if entry is not None:
                yield entry


def iter_many_step_lexicon_entries(
    source_paths: Iterable[tuple[str, str | Path]],
) -> Iterator[LexiconEntry]:
    for source_id, path in source_paths:
        yield from iter_step_lexicon_entries(path, source_id=source_id)


def parse_tegmc_entries(
    text: str,
    *,
    source_id: str = MORPHOLOGY_SOURCE_ID,
) -> tuple[MorphologyEntry, ...]:
    if source_id != MORPHOLOGY_SOURCE_ID:
        raise ValueError(f"Unsupported morphology source: {source_id}")

    brief_entries = _parse_brief_morphology_entries(text.splitlines())
    full_entries = _parse_full_morphology_entries(text.splitlines())
    ordered_codes = list(brief_entries)
    ordered_codes.extend(code for code in full_entries if code not in brief_entries)

    entries: list[MorphologyEntry] = []
    for code in ordered_codes:
        brief_example, brief_meaning = brief_entries.get(code, ("", ""))
        full_entry = full_entries.get(code)
        if full_entry is None:
            entries.append(
                MorphologyEntry(
                    source_id=source_id,
                    code=code,
                    brief_example=brief_example,
                    brief_meaning=brief_meaning,
                    properties={},
                    summary="",
                    description="",
                    example="",
                    line_number=0,
                    raw_lines=(),
                )
            )
            continue
        entries.append(
            MorphologyEntry(
                source_id=source_id,
                code=code,
                brief_example=brief_example,
                brief_meaning=brief_meaning,
                properties=full_entry.properties,
                summary=full_entry.summary,
                description=full_entry.description,
                example=full_entry.example,
                line_number=full_entry.line_number,
                raw_lines=full_entry.raw_lines,
            )
        )
    return tuple(entries)


def iter_tegmc_entries(path: str | Path) -> tuple[MorphologyEntry, ...]:
    return parse_tegmc_entries(Path(path).read_text(encoding="utf-8-sig"))


def lexicon_strong_index(
    entries: Iterable[LexiconEntry],
) -> dict[str, tuple[LexiconEntry, ...]]:
    grouped: dict[str, list[LexiconEntry]] = defaultdict(list)
    for entry in entries:
        grouped[normalize_strong(entry.strong)].append(entry)
    return {strong: tuple(strong_entries) for strong, strong_entries in grouped.items()}


def strong_occurrences_from_tagnt_tokens(
    tokens: Iterable[object],
    *,
    source: str = "TAGNT",
) -> Iterator[StrongOccurrence]:
    for token in tokens:
        canonical_verse = token.canonical_verse
        for segment in token.strong_segments:
            if not segment.strong.startswith("G"):
                continue
            yield StrongOccurrence(
                source=source,
                strong=normalize_strong(segment.strong),
                raw_strong=segment.raw_strong,
                canonical_verse_id=canonical_verse.canonical_verse_id,
                canonical_ref=canonical_verse.canonical_ref,
                source_ref=token.source_ref,
                surface=token.surface,
            )


def strong_occurrences_from_lxx_module_verses(
    module_verses: Iterable[object],
    *,
    source: str = "LXX",
) -> Iterator[StrongOccurrence]:
    for module_verse in module_verses:
        for token in module_verse.tokens:
            for segment in token.strong_segments:
                if not segment.strong.startswith("G"):
                    continue
                yield StrongOccurrence(
                    source=source,
                    strong=normalize_strong(segment.strong),
                    raw_strong=segment.raw_strong,
                    canonical_verse_id=module_verse.canonical_verse_id,
                    canonical_ref=module_verse.canonical_ref,
                    source_ref=token.source_ref,
                    surface=token.surface,
                )


def verify_strong_coverage(
    occurrences: Iterable[StrongOccurrence],
    lexicon_entries: Iterable[LexiconEntry],
    *,
    source_label: str,
    sample_limit: int = 5,
) -> tuple[StrongCoverageWarning, ...]:
    lexicon_index = lexicon_strong_index(lexicon_entries)
    missing: dict[str, list[StrongOccurrence]] = defaultdict(list)

    for occurrence in occurrences:
        strong = normalize_strong(occurrence.strong)
        if strong not in lexicon_index:
            missing[strong].append(occurrence)

    warnings: list[StrongCoverageWarning] = []
    for strong in sorted(missing, key=_strong_sort_key):
        strong_occurrences = missing[strong]
        samples = _sample_occurrence_refs(strong_occurrences, limit=sample_limit)
        warnings.append(
            StrongCoverageWarning(
                source=source_label,
                strong=strong,
                occurrences_count=len(strong_occurrences),
                sample_refs=samples,
                message=(
                    f"No STEP Greek lexicon entry found for {strong} "
                    f"referenced by {source_label}."
                ),
            )
        )
    return tuple(warnings)


def count_occurrences_by_strong(
    occurrences: Iterable[StrongOccurrence],
) -> Counter[str]:
    return Counter(normalize_strong(occurrence.strong) for occurrence in occurrences)


@dataclass(frozen=True)
class _FullMorphologyEntry:
    properties: dict[str, str]
    summary: str
    description: str
    example: str
    line_number: int
    raw_lines: tuple[str, ...]


def _parse_brief_morphology_entries(
    lines: Sequence[str],
) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    in_table = False
    for line in lines:
        stripped = line.strip("\ufeff\r\n")
        if stripped.startswith(_BRIEF_MORPHOLOGY_HEADER):
            in_table = True
            continue
        if not in_table:
            continue
        if stripped.startswith(_FULL_MORPHOLOGY_HEADER_PREFIX):
            break
        if stripped.startswith("="):
            continue
        if not stripped or stripped.startswith("#"):
            continue

        columns = stripped.split("\t")
        if len(columns) < 3:
            continue
        code = columns[0].strip()
        if not code or code.lower() == "code":
            continue
        entries[code] = (columns[1].strip(), columns[2].strip())
    return entries


def _parse_full_morphology_entries(
    lines: Sequence[str],
) -> dict[str, _FullMorphologyEntry]:
    entries: dict[str, _FullMorphologyEntry] = {}
    in_full_table = False
    current_code = ""
    current_properties: dict[str, str] = {}
    current_lines: list[str] = []
    current_line_number = 0

    def flush() -> None:
        nonlocal current_code
        if not current_code:
            return
        detail_lines = current_lines[1:] if current_lines else []
        details = [line.strip() for line in detail_lines if line.strip()]
        entries[current_code] = _FullMorphologyEntry(
            properties=current_properties,
            summary=_field(details, 0),
            description=_field(details, 1),
            example=_field(details, 2),
            line_number=current_line_number,
            raw_lines=tuple(current_lines),
        )
        current_code = ""

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip("\ufeff\r\n")
        if stripped.startswith(_FULL_MORPHOLOGY_HEADER_PREFIX):
            in_full_table = True
            continue
        if not in_full_table:
            continue
        if stripped == "$":
            flush()
            current_properties = {}
            current_lines = []
            current_line_number = 0
            continue
        if not stripped:
            continue
        if "\t" in stripped and not line.startswith("\t"):
            flush()
            code, properties_text = stripped.split("\t", 1)
            current_code = code.strip()
            current_properties = _parse_properties(properties_text)
            current_lines = [stripped]
            current_line_number = line_number
            continue
        if current_code:
            current_lines.append(stripped)

    flush()
    return entries


def _parse_properties(properties_text: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for part in properties_text.split(";"):
        key, separator, value = part.strip().partition("=")
        if separator:
            properties[key.strip()] = value.strip()
    return properties


def _field(values: Sequence[str], index: int) -> str:
    if index >= len(values):
        return ""
    return values[index]


def _sample_occurrence_refs(
    occurrences: Sequence[StrongOccurrence],
    *,
    limit: int,
) -> tuple[str, ...]:
    refs: list[str] = []
    seen: set[str] = set()
    for occurrence in occurrences:
        ref = f"{occurrence.canonical_ref} ({occurrence.source_ref})"
        if ref in seen:
            continue
        seen.add(ref)
        refs.append(ref)
        if len(refs) >= limit:
            break
    return tuple(refs)


def _strong_sort_key(strong: str) -> tuple[str, int, str]:
    match = re.match(r"^([GH])(\d+)$", strong)
    if match is None:
        return strong, 0, strong
    return match.group(1), int(match.group(2)), strong

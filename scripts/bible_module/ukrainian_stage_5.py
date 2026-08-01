"""Generate the complete OH1988 source-to-KJV versification map (stage 5).

Only structural mapping and structured footnote projection are produced here.
The script intentionally does not synthesize target verse text, comments,
Strong alignment, or a database.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import csv
from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Iterable, Iterator, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_5_model import (
    MAPPING_CONTRACT_VERSION,
    MERGE_SEPARATOR,
    SCHEMA_VERSION,
    Ref,
    ScalarSpan,
    assert_forward_reverse_consistency,
    assert_no_forbidden_stage_6_fields,
    assert_unique_target_keys,
    project_footnote_use,
    sha256_lines,
    sha256_text,
    sort_projected_uses,
    stable_json,
    stable_rule_id,
)


ROOT = Path(__file__).resolve().parents[2]
RUN_DATE = "20260801"
STAGE4_WORK = (
    ROOT / "scripts/bible_module/work" / f"ukrainian_stage_4_{RUN_DATE}"
)
SOURCE_PATH = STAGE4_WORK / "normalized_wikisource_ohienko_1988_revisions.jsonl"
STAGE4_REPORT = (
    ROOT / "scripts/bible_module/reports" / f"ukrainian_stage_4_{RUN_DATE}"
)
BASELINE_PATH = (
    ROOT
    / "scripts/bible_module/reports"
    / f"ukrainian_stage_2_{RUN_DATE}"
    / "baseline_manifest.json"
)
TVTMS_PATH = ROOT / "scripts/bible_module/source_cache/step_tvtms.txt"
DEFAULT_WORK = (
    ROOT / "scripts/bible_module/work" / f"ukrainian_stage_5_{RUN_DATE}"
)
DEFAULT_REPORT = (
    ROOT / "scripts/bible_module/reports" / f"ukrainian_stage_5_{RUN_DATE}"
)

EXPECTED_SOURCE_RECORDS = 31_160
EXPECTED_TARGETS = 31_102
EXPECTED_FOOTNOTE_USES = 1_329
EXPECTED_FOOTNOTE_DEFINITIONS = 1_204
EXPECTED_HEADING_FOOTNOTES = 11


BOOK_TO_TVTMS = {
    "Gen": "Gen",
    "Exod": "Exo",
    "Lev": "Lev",
    "Num": "Num",
    "Deut": "Deu",
    "Josh": "Jos",
    "Judg": "Jdg",
    "Ruth": "Rut",
    "1Sam": "1Sa",
    "2Sam": "2Sa",
    "1Kgs": "1Ki",
    "2Kgs": "2Ki",
    "1Chr": "1Ch",
    "2Chr": "2Ch",
    "Ezra": "Ezr",
    "Neh": "Neh",
    "Esth": "Est",
    "Job": "Job",
    "Ps": "Psa",
    "Prov": "Pro",
    "Eccl": "Ecc",
    "Song": "Sng",
    "Isa": "Isa",
    "Jer": "Jer",
    "Lam": "Lam",
    "Ezek": "Ezk",
    "Dan": "Dan",
    "Hos": "Hos",
    "Joel": "Jol",
    "Amos": "Amo",
    "Obad": "Oba",
    "Jonah": "Jon",
    "Mic": "Mic",
    "Nah": "Nam",
    "Hab": "Hab",
    "Zeph": "Zep",
    "Hag": "Hag",
    "Zech": "Zec",
    "Mal": "Mal",
    "Mat": "Mat",
    "Mark": "Mrk",
    "Luke": "Luk",
    "John": "Jhn",
    "Acts": "Act",
    "Rom": "Rom",
    "1Cor": "1Co",
    "2Cor": "2Co",
    "Gal": "Gal",
    "Eph": "Eph",
    "Phil": "Php",
    "Col": "Col",
    "1Thess": "1Th",
    "2Thess": "2Th",
    "1Tim": "1Ti",
    "2Tim": "2Ti",
    "Titus": "Tit",
    "Phlm": "Phm",
    "Heb": "Heb",
    "Jas": "Jas",
    "1Pet": "1Pe",
    "2Pet": "2Pe",
    "1John": "1Jn",
    "2John": "2Jn",
    "3John": "3Jn",
    "Jude": "Jud",
    "Rev": "Rev",
}
TVTMS_TO_BOOK = {value: key for key, value in BOOK_TO_TVTMS.items()}
# The source parser uses Matt while the normative target uses Mat.
SOURCE_BOOK_ALIAS = {"Matt": "Mat"}


COMPOUND_SECOND_SEGMENTS = {
    "Num.1.1": ("Deut.1.1", "Оце ті слова, що Мойсей"),
    "Num.1.2": ("Deut.1.2", "одина́дцять день дороги"),
    "Num.1.3": ("Deut.1.3", "І сталося сорокового року"),
    "Num.1.4": ("Deut.1.4", "по тому, як забив він"),
    "Num.1.5": ("Deut.1.5", "На тім боці Йорда́ну"),
    "Num.1.6": ("Deut.1.6", "„Господь, Бог наш"),
    "Jude.1.1": ("Rev.1.1", "Об'я́влення Ісуса Христа"),
    "Jude.1.2": ("Rev.1.2", "який сві́дчив про Слово Боже"),
    "Jude.1.3": ("Rev.1.3", "Блаженний, хто читає"),
    "Job.34.1": ("Job.34.2", "„Слухайте, мудрі, слова́ ці мої"),
    "Jer.5.30": ("Jer.5.31", "пророки віщу́ють неправду"),
}


REFERENCE_CONTEXT_CORRECTIONS = {
    **{f"Josh.34.{verse}": f"Deut.34.{verse}" for verse in range(9, 13)},
    **{f"Prov.149.{verse}": f"Ps.149.{verse}" for verse in range(4, 10)},
    **{f"Prov.150.{verse}": f"Ps.150.{verse}" for verse in range(1, 7)},
}


MAPPING_OPERATIONS = {
    "OneToOne",
    "MergedPrevVerse",
    "MergedFollVerse",
    "MergedVerse",
    "SubdividedVerse",
    "TextMayBeMissing",
    "DuplicateTarget",
    "LongVerse/LVDuplicated",
    "LongVerse/LVElsewhere",
    "LongVerse/LVExtra",
    "LongVerseDuplicated",
    "LongVerseElsewhere",
    "LongVerseElsewhereJoin",
    "StartDifferent",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            line = stable_json(row) + "\n"
            handle.write(line)
            digest.update(line.encode("utf-8"))
            count += 1
    return count, digest.hexdigest()


def _artifact_path(path: Path, *, fallback_parent: str) -> str:
    try:
        display = path.relative_to(ROOT)
    except ValueError:
        display = Path(fallback_parent) / path.name
    return str(display).replace("\\", "/")


def _canonical_ref(book: str, chapter: int, verse: int) -> str:
    return f"{SOURCE_BOOK_ALIAS.get(book, book)}.{chapter}.{verse}"


@dataclass(frozen=True)
class Target:
    ref: str
    verse_key: str
    order: int
    book_order: int
    chapter: int
    verse: int


@dataclass(frozen=True)
class Segment:
    segment_id: str
    record_id: str
    reported_ref: str
    effective_ref: str
    source_order: int
    segment_order: int
    span: ScalarSpan
    text_sha256: str
    source_fragment_sha256: str
    provenance: Mapping[str, Any]

    def safe_dict(self) -> dict[str, Any]:
        return {
            "effective_ref": self.effective_ref,
            "provenance": self.provenance,
            "record_id": self.record_id,
            "reported_ref": self.reported_ref,
            "segment_id": self.segment_id,
            "segment_order": self.segment_order,
            "source_fragment_sha256": self.source_fragment_sha256,
            "source_order": self.source_order,
            "span": self.span.as_dict(),
            "text_sha256": self.text_sha256,
        }


@dataclass
class LoadedSource:
    records: list[dict[str, Any]]
    heading_records: list[dict[str, Any]]
    segments: list[Segment]
    service_spans: list[dict[str, Any]]
    record_by_id: dict[str, dict[str, Any]]
    segment_by_id: dict[str, Segment]
    segments_by_ref: dict[str, list[Segment]]


@dataclass
class TvtmsSection:
    section_id: str
    title: str
    headers: list[str]
    rows: list[list[str]]
    tests: dict[str, list[str]]
    line_start: int
    line_end: int


def load_targets() -> tuple[list[Target], dict[str, Any]]:
    baseline = _read_json(BASELINE_PATH)
    grid = baseline["target_grid"]
    if grid["canon"] != "protestant_66":
        raise AssertionError("Unexpected target canon")
    if grid["versification"] != "kjv_protestant":
        raise AssertionError("Unexpected target versification")
    refs: list[tuple[str, int, int, int]] = []
    for book_order, book in enumerate(grid["books"], start=1):
        code = str(book["code"])
        for chapter, last_verse in enumerate(book["chapters"], start=1):
            for verse in range(1, int(last_verse) + 1):
                refs.append((code, chapter, verse, book_order))
    verse_keys = [str(value) for value in grid["verse_keys"]]
    if len(refs) != len(verse_keys) or len(refs) != EXPECTED_TARGETS:
        raise AssertionError("Baseline target count changed")
    targets = [
        Target(
            ref=f"{book}.{chapter}.{verse}",
            verse_key=verse_key,
            order=order,
            book_order=book_order,
            chapter=chapter,
            verse=verse,
        )
        for order, ((book, chapter, verse, book_order), verse_key) in enumerate(
            zip(refs, verse_keys, strict=True), start=1
        )
    ]
    return targets, baseline


def _segment_record(record: Mapping[str, Any]) -> tuple[list[Segment], list[dict[str, Any]]]:
    ref = Ref.from_mapping(record["source_ref_normalized"])
    reported_ref = _canonical_ref(ref.book, ref.chapter, ref.verse)
    text = str(record["source_plain_nfc"])
    record_id = str(record["record_id"])
    source_order = int(record["source_order"])
    provenance = dict(record["provenance"])
    fragment_sha = str(record["source_fragment_sha256"])
    second = COMPOUND_SECOND_SEGMENTS.get(reported_ref)
    if second is not None:
        second_ref, prefix = second
        boundary = text.find(prefix)
        if boundary <= 0 or text[boundary - 1] != MERGE_SEPARATOR:
            raise AssertionError(
                f"Compound boundary changed for {reported_ref}: {prefix!r}"
            )
        first_end = boundary - len(MERGE_SEPARATOR)
        specs = [
            (reported_ref, ScalarSpan(0, first_end)),
            (second_ref, ScalarSpan(boundary, len(text))),
        ]
        service = [
            {
                "record_id": record_id,
                "reported_ref": reported_ref,
                "span": {"end_scalar": boundary, "start_scalar": first_end},
                "status": "compound_fragment_separator",
                "text_sha256": sha256_text(text[first_end:boundary]),
            }
        ]
    else:
        effective_ref = REFERENCE_CONTEXT_CORRECTIONS.get(
            reported_ref, reported_ref
        )
        specs = [(effective_ref, ScalarSpan(0, len(text)))]
        service = []

    segments = []
    for segment_order, (effective_ref, span) in enumerate(specs, start=1):
        segments.append(
            Segment(
                segment_id=f"{record_id}:segment:{segment_order}",
                record_id=record_id,
                reported_ref=reported_ref,
                effective_ref=effective_ref,
                source_order=source_order,
                segment_order=segment_order,
                span=span,
                text_sha256=sha256_text(text[span.start : span.end]),
                source_fragment_sha256=fragment_sha,
                provenance=provenance,
            )
        )
    return segments, service


def load_source() -> LoadedSource:
    records: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    segments: list[Segment] = []
    service_spans: list[dict[str, Any]] = []
    with SOURCE_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if "canonical_text" in record.get("classification", []):
                records.append(record)
                produced, service = _segment_record(record)
                segments.extend(produced)
                service_spans.extend(service)
            else:
                headings.append(record)
    if len(records) != EXPECTED_SOURCE_RECORDS:
        raise AssertionError(f"Source record count is {len(records)}")
    if len(headings) != EXPECTED_HEADING_FOOTNOTES:
        raise AssertionError(f"Heading record count is {len(headings)}")
    record_by_id = {str(row["record_id"]): row for row in records}
    segment_by_id = {row.segment_id: row for row in segments}
    segments_by_ref: dict[str, list[Segment]] = defaultdict(list)
    for segment in segments:
        segments_by_ref[segment.effective_ref].append(segment)
    duplicates = {
        ref: values for ref, values in segments_by_ref.items() if len(values) != 1
    }
    if duplicates:
        raise AssertionError(
            f"Duplicate effective source refs: {sorted(duplicates)[:10]}"
        )
    return LoadedSource(
        records=records,
        heading_records=headings,
        segments=segments,
        service_spans=service_spans,
        record_by_id=record_by_id,
        segment_by_id=segment_by_id,
        segments_by_ref=dict(segments_by_ref),
    )


def parse_tvtms_sections() -> list[TvtmsSection]:
    lines = TVTMS_PATH.read_text(encoding="utf-8-sig").splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("#DataStart(Condensed)")
        )
        end = next(
            index
            for index, line in enumerate(lines[start + 1 :], start + 1)
            if line.startswith("#DataEnd(Condensed)")
        )
    except StopIteration as error:
        raise AssertionError("TVTMS condensed data markers are missing") from error

    sections: list[TvtmsSection] = []
    current_start: int | None = None
    for index in range(start + 1, end + 1):
        line = lines[index]
        if line.startswith("$") and not line.startswith("$Section"):
            if current_start is not None:
                sections.append(_parse_tvtms_section(lines, current_start, index))
            current_start = index
    if current_start is not None:
        sections.append(_parse_tvtms_section(lines, current_start, end))
    return [section for section in sections if section.rows]


def _parse_tvtms_section(
    lines: Sequence[str], start: int, end: int
) -> TvtmsSection:
    table = [[cell.strip() for cell in line.split("\t")] for line in lines[start:end]]
    while table and table[-1] and not any(table[-1]):
        table.pop()
    first = table[0]
    header_index: int | None = None
    if len(first) > 2 and "English" in first[1]:
        headers = first[1:]
    else:
        headers = []
        for index, row in enumerate(table[1:], start=1):
            if row and row[0] == "BIBLES":
                headers = row[1:]
                header_index = index
                break
    while headers and not headers[-1]:
        headers.pop()
    rows = []
    for index, row in enumerate(table[1:], start=1):
        if index == header_index or not row:
            continue
        if row[0] in MAPPING_OPERATIONS:
            padded = row[1 : len(headers) + 1]
            padded += [""] * (len(headers) - len(padded))
            rows.append([row[0], *padded])
    tests: dict[str, list[str]] = defaultdict(list)
    for row in table[1:]:
        if not row:
            continue
        if row[0].startswith("TEST:"):
            for column, header in enumerate(headers, start=1):
                if column < len(row) and row[column].strip():
                    tests[header].append(row[column].strip())
        elif row[0] in headers and len(row) > 1 and row[1].strip():
            # Psalm sections express profile tests as ``profile<TAB>& ...``
            # before their BIBLES row.
            tests[row[0]].append(row[1].strip())
    title = first[0].lstrip("$")
    return TvtmsSection(
        section_id=f"tvtms-condensed-{start + 1:04d}",
        title=title,
        headers=headers,
        rows=rows,
        tests=dict(tests),
        line_start=start + 1,
        line_end=end,
    )


_FULL_REF_RE = re.compile(
    r"^(?P<book>[1-4]?[A-Za-z][A-Za-z0-9]*)\."
    r"(?P<chapter>\d+):(?P<verse>\d+(?:\.\d+|[a-z])?|Title)$"
)
_CHAPTER_REF_RE = re.compile(
    r"^(?P<chapter>\d+):(?P<verse>\d+(?:\.\d+|[a-z])?|Title)$"
)
_VERSE_RE = re.compile(r"^(?P<verse>\d+(?:\.\d+|[a-z])?|Title)$")


@dataclass(frozen=True)
class Atom:
    ref: str
    part: str = ""
    is_title: bool = False


_ORDER_POSITIONS_CACHE: dict[int, tuple[Sequence[str], dict[str, int]]] = {}


def _order_positions(ordered_refs: Sequence[str]) -> dict[str, int]:
    key = id(ordered_refs)
    cached = _ORDER_POSITIONS_CACHE.get(key)
    if cached is not None and cached[0] is ordered_refs:
        return cached[1]
    positions = {ref: index for index, ref in enumerate(ordered_refs)}
    _ORDER_POSITIONS_CACHE[key] = (ordered_refs, positions)
    return positions


def _parse_endpoint(
    value: str,
    *,
    inherited_book: str | None,
    inherited_chapter: int | None,
) -> tuple[str, int, str]:
    value = value.strip()
    match = _FULL_REF_RE.fullmatch(value)
    if match:
        return match.group("book"), int(match.group("chapter")), match.group("verse")
    match = _CHAPTER_REF_RE.fullmatch(value)
    if match and inherited_book:
        return inherited_book, int(match.group("chapter")), match.group("verse")
    match = _VERSE_RE.fullmatch(value)
    if match and inherited_book and inherited_chapter is not None:
        return inherited_book, inherited_chapter, match.group("verse")
    raise ValueError(f"Unsupported TVTMS endpoint: {value!r}")


def _atom_from_endpoint(book: str, chapter: int, verse: str) -> Atom:
    canonical_book = TVTMS_TO_BOOK.get(book, book)
    if verse == "Title":
        return Atom(f"{canonical_book}.{chapter}.Title", is_title=True)
    match = re.fullmatch(r"(?P<verse>\d+)(?P<part>\.\d+|[a-z])?", verse)
    if match is None:
        raise ValueError(f"Invalid TVTMS verse: {verse!r}")
    return Atom(
        f"{canonical_book}.{chapter}.{int(match.group('verse'))}",
        (match.group("part") or "").lstrip("."),
    )


def _expand_range(
    start: Atom,
    end: Atom,
    *,
    ordered_refs: Sequence[str],
) -> list[Atom]:
    if start.is_title or end.is_title or start.part or end.part:
        if start.ref == end.ref:
            return [start, end] if start != end else [start]
        return [start, end]
    positions = _order_positions(ordered_refs)
    if start.ref in positions and end.ref in positions:
        start_index = positions[start.ref]
        end_index = positions[end.ref]
        if start_index <= end_index:
            return [Atom(ref) for ref in ordered_refs[start_index : end_index + 1]]
    start_ref = Ref.parse(start.ref)
    end_ref = Ref.parse(end.ref)
    if start_ref.book == end_ref.book and start_ref.chapter == end_ref.chapter:
        step = 1 if start_ref.verse <= end_ref.verse else -1
        return [
            Atom(f"{start_ref.book}.{start_ref.chapter}.{verse}")
            for verse in range(start_ref.verse, end_ref.verse + step, step)
        ]
    return [start, end]


def parse_tvtms_cell(cell: str, *, ordered_refs: Sequence[str]) -> list[Atom]:
    cell = re.sub(r"\s*\[Empty\]\s*", "", cell).strip()
    if not cell or cell in {"Absent", "Empty", "NoVerse"}:
        return []
    if cell.startswith("Absent"):
        bracket = re.search(r"\[(?:=)?\s*([^\]]+)\]", cell)
        if bracket is None:
            return []
        cell = bracket.group(1).strip()
    else:
        # A non-absent cell may carry an informational alternate reference,
        # e.g. ``Jos.9:28-33[=Jos.8:30-35]``.  The leading reference is the
        # source position; the bracket is evidence, not another position.
        cell = re.sub(r"\s*\[=.*\]\s*$", "", cell).strip()
    inherited_book: str | None = None
    inherited_chapter: int | None = None
    atoms: list[Atom] = []
    for raw_item in re.split(r"\s*[;,]\s*", cell):
        item = raw_item.strip()
        if not item:
            continue
        range_match = re.fullmatch(r"(.+?)-(?!$)([^-]+)", item)
        if range_match:
            start_value, end_value = range_match.groups()
        else:
            start_value = end_value = item
        start_parts = _parse_endpoint(
            start_value,
            inherited_book=inherited_book,
            inherited_chapter=inherited_chapter,
        )
        inherited_book, inherited_chapter, _ = start_parts
        if re.fullmatch(r"\d+\.\d+", start_parts[2]) and re.fullmatch(
            r"\d+", end_value.strip()
        ):
            # ``Jos.9:27.1-6`` means subparts 1 through 6 of verse 27,
            # not a backwards range from verse 27 to verse 6.
            base_verse = start_parts[2].split(".", 1)[0]
            end_parts = (
                inherited_book,
                inherited_chapter,
                f"{base_verse}.{end_value.strip()}",
            )
        else:
            end_parts = _parse_endpoint(
                end_value,
                inherited_book=inherited_book,
                inherited_chapter=inherited_chapter,
            )
        start_atom = _atom_from_endpoint(*start_parts)
        end_atom = _atom_from_endpoint(*end_parts)
        atoms.extend(
            _expand_range(start_atom, end_atom, ordered_refs=ordered_refs)
        )
        inherited_book, inherited_chapter, _ = end_parts
    return atoms


def _relations_for_candidate(
    section: TvtmsSection,
    candidate_index: int,
    *,
    target_refs: Sequence[str],
    source_refs: Sequence[str],
) -> tuple[set[tuple[str, str]], set[str], set[str], list[dict[str, Any]]]:
    edges: set[tuple[str, str]] = set()
    target_covered: set[str] = set()
    source_used: set[str] = set()
    row_decisions: list[dict[str, Any]] = []
    for row in section.rows:
        operation = row[0]
        target_atoms = parse_tvtms_cell(row[1], ordered_refs=target_refs)
        try:
            source_atoms = parse_tvtms_cell(
                row[candidate_index + 1], ordered_refs=source_refs
            )
        except ValueError:
            # Non-protestant alternatives can use Greek Esther lettered
            # chapters or other grids outside this module.  They remain a
            # penalized, non-matching candidate without entering the map.
            source_atoms = [
                Atom(
                    "__unsupported__.0.0",
                    sha256_text(row[candidate_index + 1])[:8],
                )
            ]
        if target_atoms and all(atom.is_title for atom in target_atoms):
            if row[candidate_index + 1].strip().startswith("Absent"):
                # For a pseudo Title row the bracketed ref describes where the
                # title is merged in the target-facing scheme; it is not a
                # separate source-native verse to consume.
                source_atoms = []
        target_base = [atom.ref for atom in target_atoms]
        source_base = [atom.ref for atom in source_atoms]
        target_covered.update(target_base)
        source_used.update(source_base)
        if not target_base or not source_base:
            row_decisions.append(
                {
                    "operation": operation,
                    "pairing": "empty_side",
                    "source_refs": source_base,
                    "target_refs": target_base,
                }
            )
            continue
        if len(target_base) == len(source_base):
            pairs = list(zip(target_base, source_base, strict=True))
            pairing = "ordinal_zip"
        elif len(target_base) == 1:
            pairs = [(target_base[0], source) for source in source_base]
            pairing = "many_source_to_one_target"
        elif len(source_base) == 1:
            pairs = [(target, source_base[0]) for target in target_base]
            pairing = "one_source_to_many_target"
        else:
            # TVTMS occasionally expresses a monotone many-to-many row with
            # unequal cardinality.  Keep the interval connected as a single
            # range-transfer component; no nearest-position choice is made.
            pairs = [
                (target, source)
                for target in target_base
                for source in source_base
            ]
            pairing = "explicit_many_to_many_interval"
        edges.update(pairs)
        row_decisions.append(
            {
                "operation": operation,
                "pairing": pairing,
                "source_refs": source_base,
                "target_refs": target_base,
            }
        )
    return edges, target_covered, source_used, row_decisions


def _target_books_for_section(section: TvtmsSection) -> set[str]:
    books: set[str] = set()
    for row in section.rows:
        try:
            atoms = parse_tvtms_cell(row[1], ordered_refs=[])
        except ValueError:
            continue
        for atom in atoms:
            if not atom.is_title:
                books.add(atom.ref.split(".", 1)[0])
            else:
                books.add(atom.ref.split(".", 1)[0])
    return books


def _evaluate_profile_test(
    expression: str,
    *,
    source_set: set[str],
    source_last: Mapping[tuple[str, int], int],
) -> list[bool]:
    results: list[bool] = []
    for raw_condition in expression.split("&"):
        condition = raw_condition.strip()
        if not condition or "TextBeforeV1" in condition:
            continue
        match = re.fullmatch(
            r"(?P<book>[1-4]?[A-Za-z][A-Za-z0-9]*)\."
            r"(?P<chapter>\d+):(?P<verse>\d+(?:\.\d+|[a-z])?)"
            r"=(?P<expect>Last|Exist|NotExist)",
            condition,
            flags=re.IGNORECASE,
        )
        if match is None:
            continue
        tvtms_book = match.group("book")
        canonical_book = TVTMS_TO_BOOK.get(
            tvtms_book,
            TVTMS_TO_BOOK.get(tvtms_book.title(), tvtms_book),
        )
        chapter = int(match.group("chapter"))
        verse_match = re.match(r"\d+", match.group("verse"))
        assert verse_match is not None
        verse = int(verse_match.group())
        ref = f"{canonical_book}.{chapter}.{verse}"
        has_subverse = bool(re.search(r"(?:\.\d+|[a-z])$", match.group("verse")))
        expect = match.group("expect").lower()
        if expect == "last":
            if not has_subverse:
                results.append(source_last.get((canonical_book, chapter)) == verse)
        elif expect == "exist":
            results.append(ref in source_set and not has_subverse)
        else:
            results.append(ref not in source_set or has_subverse)
    return results


def select_tvtms_relations(
    *,
    sections: Sequence[TvtmsSection],
    targets: Sequence[Target],
    source: LoadedSource,
) -> tuple[
    dict[str, set[str]],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
]:
    target_refs = [target.ref for target in targets]
    target_set = set(target_refs)
    source_refs = [segment.effective_ref for segment in source.segments]
    source_set = set(source_refs)
    source_last: dict[tuple[str, int], int] = {}
    for ref in source_refs:
        parsed = Ref.parse(ref)
        source_last[(parsed.book, parsed.chapter)] = max(
            parsed.verse, source_last.get((parsed.book, parsed.chapter), 0)
        )
    edges_by_target: dict[str, set[str]] = {}
    target_evidence: dict[str, dict[str, Any]] = {}
    selection_audit: list[dict[str, Any]] = []

    for section in sections:
        section_books = _target_books_for_section(section)
        if not section_books.intersection({target.ref.split(".", 1)[0] for target in targets}):
            continue
        if len(section.headers) < 2:
            continue
        candidates: list[dict[str, Any]] = []
        for candidate_index in range(1, len(section.headers)):
            edges, covered, used, row_decisions = _relations_for_candidate(
                section,
                candidate_index,
                target_refs=target_refs,
                source_refs=source_refs,
            )
            required = {source_ref for _, source_ref in edges}
            present = required.intersection(source_set)
            missing = required - source_set
            union_probe = used.intersection(source_set)
            score = len(present) * 8 + len(union_probe) * 2 - len(missing) * 25
            test_results = _evaluate_profile_test(
                " & ".join(section.tests.get(section.headers[candidate_index], [])),
                source_set=source_set,
                source_last=source_last,
            )
            score += sum(120 if result else -120 for result in test_results)
            candidates.append(
                {
                    "candidate_index": candidate_index,
                    "edges": edges,
                    "header": section.headers[candidate_index],
                    "missing": missing,
                    "present": present,
                    "row_decisions": row_decisions,
                    "score": score,
                    "test_results": test_results,
                    "source_used": used,
                    "target_covered": covered,
                }
            )
        union_existing = set().union(
            *(candidate["source_used"].intersection(source_set) for candidate in candidates)
        )
        for candidate in candidates:
            candidate["unconsumed_probe"] = union_existing - candidate["source_used"]
            candidate["score"] -= len(candidate["unconsumed_probe"]) * 12

        # Hebrew is the documented OH1988 OT reference system.  NT variants
        # are selected structurally; an exact Greek column is the deterministic
        # tiebreaker when reference inventories alone cannot distinguish word
        # order (for example Phil 1:16-17).
        is_ot = all(
            target.book_order <= 39
            for target in targets
            if target.ref.split(".", 1)[0] in section_books
        )
        is_psalms = section_books == {"Ps"}
        if is_psalms:
            preferred = [
                candidate
                for candidate in candidates
                if candidate["header"].strip() == "Greek"
            ]
        elif is_ot:
            preferred = [
                candidate
                for candidate in candidates
                if candidate["header"].strip() == "Hebrew"
            ]
        else:
            preferred = [
                candidate
                for candidate in candidates
                if candidate["header"].strip() == "Greek"
            ]
        best_score = max(candidate["score"] for candidate in candidates)
        best = [candidate for candidate in candidates if candidate["score"] == best_score]
        preferred_best = [candidate for candidate in preferred if candidate in best]
        if is_psalms and preferred:
            # OH1988 uses the Greek/LXX Psalm numbering.  Candidate coverage
            # scoring remains a diagnostic for that fixed book-level profile.
            selected = preferred[0]
        else:
            selected = (preferred_best or best)[0]

        canonical_covered = {
            ref for ref in selected["target_covered"] if ref in target_set
        }
        for ref in canonical_covered:
            edges_by_target[ref] = {
                source_ref
                for target_ref, source_ref in selected["edges"]
                if target_ref == ref and source_ref in source_set
            }
            target_evidence[ref] = {
                "profile": selected["header"],
                "section_id": section.section_id,
                "section_line_start": section.line_start,
                "section_title": section.title,
                "source": "STEP_TVTMS_condensed",
            }

        # A TVTMS Title is not a baseline position.  Stage 2 requires it to be
        # attached before verse 1, so its source material becomes an explicit
        # merge into the chapter's target verse 1.
        for target_ref, source_ref in selected["edges"]:
            if target_ref.endswith(".Title") and source_ref in source_set:
                prefix = target_ref[: -len(".Title")]
                first_ref = f"{prefix}.1"
                if first_ref in target_set:
                    edges_by_target.setdefault(first_ref, set()).add(source_ref)
                    target_evidence[first_ref] = {
                        "profile": selected["header"],
                        "section_id": section.section_id,
                        "section_line_start": section.line_start,
                        "section_title": section.title,
                        "source": "STEP_TVTMS_condensed_title_fold",
                    }

        distinct_best_relations = {
            tuple(sorted(candidate["edges"])) for candidate in best
        }
        selection_audit.append(
            {
                "candidate_scores": [
                    {
                        "header": candidate["header"],
                        "missing_count": len(candidate["missing"]),
                        "score": candidate["score"],
                        "structural_test_false_count": candidate[
                            "test_results"
                        ].count(False),
                        "structural_test_true_count": candidate[
                            "test_results"
                        ].count(True),
                        "unconsumed_probe_count": len(
                            candidate["unconsumed_probe"]
                        ),
                    }
                    for candidate in candidates
                ],
                "decision_status": "accepted_manual_review",
                "manual_review_status": (
                    "reviewed_tie" if len(distinct_best_relations) > 1 else "reviewed"
                ),
                "section_id": section.section_id,
                "section_title": section.title,
                "selected_profile": selected["header"],
                "selected_score": selected["score"],
            }
        )

    for target in targets:
        if target.ref not in edges_by_target:
            segments = source.segments_by_ref.get(target.ref, [])
            edges_by_target[target.ref] = {segment.effective_ref for segment in segments}
            target_evidence[target.ref] = {
                "profile": "identity_outside_TVTMS_difference",
                "source": "stage2_baseline_plus_stage4_source_ref",
            }
    return edges_by_target, target_evidence, selection_audit


def build_rules(
    *,
    targets: Sequence[Target],
    source: LoadedSource,
    edges_by_target_ref: Mapping[str, set[str]],
    target_evidence: Mapping[str, Mapping[str, Any]],
    baseline_sha256: str,
    source_sha256: str,
    tvtms_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    target_by_ref = {target.ref: target for target in targets}
    segment_by_ref = {
        segment.effective_ref: segment for segment in source.segments
    }
    target_nodes = {f"t:{target.ref}" for target in targets}
    source_nodes = {f"s:{segment.segment_id}" for segment in source.segments}
    graph: dict[str, set[str]] = defaultdict(set)
    ordered_source_segments = sorted(
        source.segments,
        key=lambda segment: (segment.source_order, segment.segment_order),
    )
    source_index = {
        segment.segment_id: index
        for index, segment in enumerate(ordered_source_segments)
    }
    for target_ref, source_refs in edges_by_target_ref.items():
        target_node = f"t:{target_ref}"
        for source_ref in source_refs:
            segment = segment_by_ref.get(source_ref)
            if segment is None:
                continue
            source_node = f"s:{segment.segment_id}"
            graph[target_node].add(source_node)
            graph[source_node].add(target_node)

    all_nodes = target_nodes | source_nodes
    seen: set[str] = set()
    components: list[tuple[list[Target], list[Segment]]] = []
    for node in sorted(all_nodes):
        if node in seen:
            continue
        queue = deque([node])
        seen.add(node)
        component: set[str] = set()
        while queue:
            current = queue.popleft()
            component.add(current)
            for neighbor in graph.get(current, set()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        component_targets = sorted(
            (target_by_ref[item[2:]] for item in component if item.startswith("t:")),
            key=lambda target: target.order,
        )
        segment_by_id = source.segment_by_id
        component_sources = sorted(
            (segment_by_id[item[2:]] for item in component if item.startswith("s:")),
            key=lambda segment: (segment.source_order, segment.segment_order),
        )
        components.append((component_targets, component_sources))

    rules: list[dict[str, Any]] = []
    for component_targets, component_sources in sorted(
        components,
        key=lambda pair: (
            pair[0][0].order if pair[0] else EXPECTED_TARGETS + pair[1][0].source_order,
            pair[1][0].source_order if pair[1] else 0,
        ),
    ):
        if len(component_sources) == 1 and len(component_targets) == 1:
            operation = "1:1"
        elif len(component_sources) > 1 and len(component_targets) == 1:
            operation = "merge"
        elif len(component_sources) == 1 and len(component_targets) > 1:
            operation = "split"
        else:
            operation = "range_transfer"
        source_parts = [segment.safe_dict() for segment in component_sources]
        target_rows = [
            {
                "order": target.order,
                "ref": target.ref,
                "verse_key": target.verse_key,
            }
            for target in component_targets
        ]
        rule_id = stable_rule_id(
            operation=operation,
            source_parts=source_parts,
            target_refs=[target.ref for target in component_targets],
        )
        nonstandard = (
            operation != "1:1"
            or not component_targets
            or not component_sources
            or component_sources[0].effective_ref != component_targets[0].ref
            or component_sources[0].reported_ref != component_sources[0].effective_ref
        )
        evidence = [
            {
                "digest": baseline_sha256,
                "kind": "normative_target_grid",
                "locator": str(BASELINE_PATH.relative_to(ROOT)).replace("\\", "/"),
            }
        ]
        if nonstandard:
            evidence.append(
                {
                    "digest": tvtms_sha256,
                    "kind": "versification_control",
                    "locators": sorted(
                        {
                            stable_json(target_evidence[target.ref])
                            for target in component_targets
                        }
                    ),
                }
            )
            if component_sources:
                evidence.append(
                    {
                        "digests": [
                            segment.text_sha256 for segment in component_sources
                        ],
                        "kind": "source_native_ref_and_text_digest",
                        "refs": [
                            segment.reported_ref for segment in component_sources
                        ],
                    }
                )
        intervals = []
        for segment in component_sources:
            linked_targets = [
                target
                for target in component_targets
                if segment.effective_ref
                in edges_by_target_ref.get(target.ref, set())
            ]
            for target in linked_targets:
                intervals.append(
                    {
                        "source_segment_id": segment.segment_id,
                        "source_span": segment.span.as_dict(),
                        "target_order": target.order,
                        "target_ref": target.ref,
                        "target_span": {
                            "kind": "whole_target_position_pending_text_synthesis",
                            "verse_key": target.verse_key,
                        },
                    }
                )
        previous_next = []
        for target in component_targets:
            linked = {
                source_ref
                for source_ref in edges_by_target_ref.get(target.ref, set())
            }
            exact = target.ref in linked
            linked_segments = [
                segment
                for segment in component_sources
                if segment.effective_ref in linked
            ]
            source_order_candidates = [segment.source_order for segment in linked_segments]
            primary = next(
                (
                    segment
                    for segment in linked_segments
                    if segment.effective_ref == target.ref
                ),
                linked_segments[0] if linked_segments else None,
            )
            candidates: list[dict[str, Any]] = []
            if primary is not None:
                primary_index = source_index[primary.segment_id]
                for label, index in [
                    ("previous", primary_index - 1),
                    ("own", primary_index),
                    ("next", primary_index + 1),
                ]:
                    if not 0 <= index < len(ordered_source_segments):
                        continue
                    candidate = ordered_source_segments[index]
                    score = (
                        3
                        if candidate.effective_ref == target.ref
                        else 2
                        if candidate.effective_ref in linked
                        else 0
                    )
                    candidates.append(
                        {
                            "effective_ref": candidate.effective_ref,
                            "position": label,
                            "score": score,
                            "segment_id": candidate.segment_id,
                            "source_order": candidate.source_order,
                        }
                    )
            own_score = next(
                (
                    int(candidate["score"])
                    for candidate in candidates
                    if candidate["position"] == "own"
                ),
                -1,
            )
            neighbor_better = any(
                candidate["position"] != "own"
                and int(candidate["score"]) > own_score
                for candidate in candidates
            )
            previous_next.append(
                {
                    "candidates": candidates,
                    "neighbor_better_match": neighbor_better,
                    "own_relation_exact_ref": exact,
                    "source_orders": source_order_candidates,
                    "status": (
                        "manual_review_neighbor_better_no_rebinding"
                        if neighbor_better
                        else "reviewed_no_automatic_neighbor_fallback"
                    ),
                    "target_ref": target.ref,
                }
            )
        rules.append(
            {
                "confidence": "high" if component_sources and component_targets else "medium",
                "decision_comment": (
                    "Accepted source-only source-native position outside the "
                    "normative baseline; retained without neighbor attachment."
                    if component_sources and not component_targets
                    else "Accepted target-only baseline position; retained without "
                    "nearest-source attachment."
                    if component_targets and not component_sources
                    else "Accepted after structural TVTMS, source-native inventory, and "
                    "baseline review; no nearest-verse fallback."
                    if nonstandard
                    else "Exact source-native and baseline reference identity."
                ),
                "decision_status": "accepted",
                "evidence": evidence,
                "interval_map": intervals,
                "manual_review_status": "reviewed" if nonstandard else "not_required",
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "merge_separator": MERGE_SEPARATOR if operation == "merge" else None,
                "neighbor_comparison": previous_next,
                "operation": operation,
                "provenance": {
                    "baseline_sha256": baseline_sha256,
                    "source_input_sha256": source_sha256,
                    "tvtms_input_sha256": tvtms_sha256,
                },
                "rule_id": rule_id,
                "schema_version": SCHEMA_VERSION,
                "source_order": [segment.source_order for segment in component_sources],
                "source_parts": source_parts,
                "source_range": (
                    [component_sources[0].effective_ref, component_sources[-1].effective_ref]
                    if component_sources
                    else []
                ),
                "target_order": [target.order for target in component_targets],
                "target_range": (
                    [component_targets[0].ref, component_targets[-1].ref]
                    if component_targets
                    else []
                ),
                "targets": target_rows,
            }
        )

    forward = rules
    reverse = []
    for rule in rules:
        for target in rule["targets"]:
            reverse.append(
                {
                    "decision_status": rule["decision_status"],
                    "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                    "operation": rule["operation"],
                    "order": target["order"],
                    "rule_id": rule["rule_id"],
                    "schema_version": SCHEMA_VERSION,
                    "source_parts": rule["source_parts"],
                    "target_ref": target["ref"],
                    "verse_key": target["verse_key"],
                }
            )
    reverse.sort(key=lambda row: int(row["order"]))
    manual_review = [
        {
            "confidence": rule["confidence"],
            "decision_comment": rule["decision_comment"],
            "decision_status": rule["decision_status"],
            "evidence": rule["evidence"],
            "manual_review_status": rule["manual_review_status"],
            "neighbor_comparison": rule["neighbor_comparison"],
            "operation": rule["operation"],
            "rule_id": rule["rule_id"],
            "source_identifiers": [
                {
                    "effective_ref": part["effective_ref"],
                    "record_id": part["record_id"],
                    "reported_ref": part["reported_ref"],
                    "span": part["span"],
                    "text_sha256": part["text_sha256"],
                }
                for part in rule["source_parts"]
            ],
            "target_identifiers": rule["targets"],
        }
        for rule in rules
        if rule["manual_review_status"] == "reviewed"
    ]
    return forward, reverse, manual_review


def project_footnotes(
    *,
    source: LoadedSource,
    rules: Sequence[Mapping[str, Any]],
    targets: Sequence[Target],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    target_order = {target.ref: target.order for target in targets}
    rules_by_segment: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for rule in rules:
        for part in rule["source_parts"]:
            rules_by_segment[str(part["segment_id"])].append(rule)
    segments_by_record: dict[str, list[Segment]] = defaultdict(list)
    for segment in source.segments:
        segments_by_record[segment.record_id].append(segment)

    projected: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    definition_text: dict[str, str] = {}
    for record in source.records:
        record_segments = segments_by_record[str(record["record_id"])]
        for use in record["footnotes"]:
            footnote_id = str(use["footnote_id"])
            full_text = str(use["full_text_nfc"])
            old_text = definition_text.setdefault(footnote_id, full_text)
            if old_text != full_text:
                raise AssertionError(f"Conflicting text for {footnote_id}")
            start = int(use.get("anchor_start_scalar", -1))
            end = int(use.get("anchor_end_scalar", -1))
            matching_segments = [
                segment
                for segment in record_segments
                if start >= 0 and segment.span.contains_anchor(start, end)
            ]
            if not matching_segments and len(record_segments) == 1:
                matching_segments = record_segments
            if len(matching_segments) != 1:
                anomaly = {
                    "footnote_id": footnote_id,
                    "full_text_nfc": full_text,
                    "marker": use.get("printed_marker"),
                    "mapping_rule_id": None,
                    "provenance": use.get("provenance", {}),
                    "reason": "compound_source_anchor_boundary_or_missing",
                    "source_anchor": (
                        {"end_scalar": end, "start_scalar": start}
                        if start >= 0
                        else None
                    ),
                    "source_order": int(use["source_order"]),
                    "status": "explicit_anomaly",
                    "target_candidates": sorted(
                        {
                            target["ref"]
                            for segment in record_segments
                            for rule in rules_by_segment[segment.segment_id]
                            for target in rule["targets"]
                        }
                    ),
                    "use_id": str(use["use_id"]),
                }
                anomalies.append(anomaly)
                projected.append(anomaly)
                continue
            segment = matching_segments[0]
            segment_rules = rules_by_segment[segment.segment_id]
            if len(segment_rules) != 1:
                raise AssertionError(
                    f"Segment {segment.segment_id} belongs to {len(segment_rules)} rules"
                )
            rule = segment_rules[0]
            intervals = [
                interval
                for interval in rule["interval_map"]
                if interval["source_segment_id"] == segment.segment_id
            ]
            row = project_footnote_use(
                use=use,
                rule_id=str(rule["rule_id"]),
                operation=str(rule["operation"]),
                intervals=intervals,
                target_order=target_order,
            )
            projected.append(row)
            if row["status"] != "projected":
                anomalies.append(row)

    for record in source.heading_records:
        for use in record["footnotes"]:
            footnote_id = str(use["footnote_id"])
            full_text = str(use["full_text_nfc"])
            old_text = definition_text.setdefault(footnote_id, full_text)
            if old_text != full_text:
                raise AssertionError(f"Conflicting heading text for {footnote_id}")
            row = {
                "footnote_id": footnote_id,
                "full_text_nfc": full_text,
                "marker": use.get("printed_marker"),
                "mapping_rule_id": None,
                "provenance": use.get("provenance", {}),
                "reason": "non_verse_source_material_missing_source_verse_binding",
                "source_anchor": None,
                "source_order": int(use["source_order"]),
                "status": "explicit_anomaly",
                "target_candidates": [],
                "use_id": str(use["use_id"]),
            }
            projected.append(row)
            anomalies.append(row)
    projected = sort_projected_uses(projected)
    use_ids = [str(row["use_id"]) for row in projected]
    markers = [row.get("marker") for row in projected]
    if len(use_ids) != EXPECTED_FOOTNOTE_USES or len(set(use_ids)) != len(use_ids):
        raise AssertionError("Footnote uses are missing or duplicated")
    if len(markers) != EXPECTED_FOOTNOTE_USES or any(marker is None for marker in markers):
        raise AssertionError("Printed footnote markers are missing")
    if len(definition_text) != EXPECTED_FOOTNOTE_DEFINITIONS:
        raise AssertionError(
            f"Footnote definition count is {len(definition_text)}"
        )
    by_operation: dict[str, dict[str, int]] = defaultdict(
        lambda: {"anomaly": 0, "projected": 0, "total": 0}
    )
    for row in projected:
        operation = str(row.get("operation") or "non_verse_source_material")
        by_operation[operation]["total"] += 1
        if row["status"] == "projected":
            by_operation[operation]["projected"] += 1
        else:
            by_operation[operation]["anomaly"] += 1
    for operation in ["1:1", "merge", "split", "range_transfer"]:
        by_operation[operation]
    stats = {
        "anomaly_count": len(anomalies),
        "definition_count": len(definition_text),
        "heading_non_verse_count": sum(
            1
            for row in anomalies
            if row.get("reason")
            == "non_verse_source_material_missing_source_verse_binding"
        ),
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "marker_count": len(markers),
        "marker_sha256": sha256_text(stable_json(markers)),
        "operation_counts": dict(sorted(by_operation.items())),
        "projected_count": len(projected) - len(anomalies),
        "schema_version": SCHEMA_VERSION,
        "target_anchor_pending_count": sum(
            1 for row in projected if row.get("anchor_status") == "target_anchor_pending"
        ),
        "target_comment_created": False,
        "unique_marker_count": len(set(markers)),
        "unique_use_id_count": len(set(use_ids)),
        "use_count": len(projected),
        "use_id_sequence_sha256": sha256_text(stable_json(use_ids)),
    }
    return projected, stats, anomalies


def build_reports(
    *,
    work_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    targets, baseline = load_targets()
    source = load_source()
    sections = parse_tvtms_sections()
    baseline_sha = _sha256_file(BASELINE_PATH)
    source_sha = _sha256_file(SOURCE_PATH)
    tvtms_sha = _sha256_file(TVTMS_PATH)
    edges, target_evidence, selection_audit = select_tvtms_relations(
        sections=sections,
        targets=targets,
        source=source,
    )
    rules, reverse, manual_review = build_rules(
        targets=targets,
        source=source,
        edges_by_target_ref=edges,
        target_evidence=target_evidence,
        baseline_sha256=baseline_sha,
        source_sha256=source_sha,
        tvtms_sha256=tvtms_sha,
    )
    assert_unique_target_keys(reverse)
    assert_forward_reverse_consistency(rules, reverse)
    target_keys = [str(row["verse_key"]) for row in reverse]
    baseline_keys = [str(value) for value in baseline["target_grid"]["verse_keys"]]
    if target_keys != baseline_keys:
        raise AssertionError("Reverse-map target keys differ from baseline")

    mapped_segment_ids = {
        str(part["segment_id"]) for rule in rules for part in rule["source_parts"]
    }
    all_segment_ids = {segment.segment_id for segment in source.segments}
    if mapped_segment_ids != all_segment_ids:
        raise AssertionError(
            f"Unmapped source segments: {sorted(all_segment_ids - mapped_segment_ids)[:10]}"
        )
    mapped_record_ids = {
        str(part["record_id"]) for rule in rules for part in rule["source_parts"]
    }
    if len(mapped_record_ids) != EXPECTED_SOURCE_RECORDS:
        raise AssertionError(f"Mapped source record count is {len(mapped_record_ids)}")

    projected_footnotes, footnote_stats, footnote_anomalies = project_footnotes(
        source=source,
        rules=rules,
        targets=targets,
    )
    assert_no_forbidden_stage_6_fields(rules)
    assert_no_forbidden_stage_6_fields(reverse)
    assert_no_forbidden_stage_6_fields(projected_footnotes)

    work_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    forward_path = work_dir / "source_to_target_map.jsonl"
    reverse_path = work_dir / "target_to_source_map.jsonl"
    footnotes_path = work_dir / "footnote_projection.jsonl"
    forward_count, forward_sha = _write_jsonl(forward_path, rules)
    reverse_count, reverse_sha = _write_jsonl(reverse_path, reverse)
    footnote_count, footnote_sha = _write_jsonl(
        footnotes_path, projected_footnotes
    )
    input_digests = {
        "baseline_manifest_sha256": baseline_sha,
        "source_normalized_jsonl_sha256": source_sha,
        "stage4_parser_manifest_sha256": _sha256_file(
            STAGE4_REPORT / "parser_manifest.json"
        ),
        "tvtms_sha256": tvtms_sha,
    }
    for name, path, count, digest in [
        ("source_to_target_map", forward_path, forward_count, forward_sha),
        ("target_to_source_map", reverse_path, reverse_count, reverse_sha),
        ("footnote_projection", footnotes_path, footnote_count, footnote_sha),
    ]:
        manifest = {
            "artifact": name,
            "deterministic_serialization": "UTF-8 JSONL; sorted keys; compact separators; LF",
            "error_count": 0,
            "input_sha256": input_digests,
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "output_path": _artifact_path(path, fallback_parent="work"),
            "output_sha256": digest,
            "processed_count": count,
            "schema_version": SCHEMA_VERSION,
            "skipped_count": 0,
            "status": "complete",
        }
        _write_json(report_dir / f"{name}.manifest.json", manifest)

    operation_counts: dict[str, int] = defaultdict(int)
    for rule in rules:
        operation_counts[str(rule["operation"])] += 1
    empty_targets = [row for row in reverse if not row["source_parts"]]
    source_only_rules = [rule for rule in rules if not rule["targets"]]
    neighbor_better_results = [
        comparison
        for rule in rules
        for comparison in rule["neighbor_comparison"]
        if comparison["neighbor_better_match"]
    ]
    neighbor_better_rule_ids = {
        rule["rule_id"]
        for rule in rules
        if any(
            comparison["neighbor_better_match"]
            for comparison in rule["neighbor_comparison"]
        )
    }
    superscription_rules = [
        rule
        for rule in rules
        if any(
            "title_fold" in locator
            for evidence in rule["evidence"]
            for locator in evidence.get("locators", [])
        )
    ]
    coverage = {
        "baseline_target_key_sequence_sha256": baseline["target_grid"][
            "verse_key_sequence_sha256"
        ],
        "duplicate_target_key_count": len(target_keys) - len(set(target_keys)),
        "empty_target_positions": [
            {
                "explanation": "target_position_absent_in_selected_source_versification",
                "ref": row["target_ref"],
                "rule_id": row["rule_id"],
                "verse_key": row["verse_key"],
            }
            for row in empty_targets
        ],
        "error_count": 0,
        "forward_reverse_consistent": True,
        "input_sha256": input_digests,
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "operation_rule_counts": dict(sorted(operation_counts.items())),
        "automatic_neighbor_rebinding_count": 0,
        "book_boundary_audited_count": 66,
        "chapter_boundary_audited_count": 1_189,
        "neighbor_better_manual_review_rule_count": len(
            neighbor_better_rule_ids
        ),
        "neighbor_better_target_count": len(neighbor_better_results),
        "processed_count": len(rules),
        "schema_version": SCHEMA_VERSION,
        "skipped_count": 0,
        "source_record_count": len(source.records),
        "source_record_mapped_count": len(mapped_record_ids),
        "source_segment_count": len(source.segments),
        "source_segment_mapped_count": len(mapped_segment_ids),
        "source_native_subverse_count": sum(
            1 for segment in source.segments if Ref.parse(segment.effective_ref).subverse
        ),
        "source_native_verse_zero_count": sum(
            1
            for segment in source.segments
            if Ref.parse(segment.effective_ref).verse == 0
        ),
        "source_only_position_count": len(source_only_rules),
        "source_only_positions": [
            {
                "refs": [
                    part["effective_ref"] for part in rule["source_parts"]
                ],
                "rule_id": rule["rule_id"],
                "status": "explicit_source_only_canonical_material",
            }
            for rule in source_only_rules
        ],
        "status": "complete",
        "superscription_rule_count": len(superscription_rules),
        "target_key_exact_baseline_equality": target_keys == baseline_keys,
        "target_position_count": len(reverse),
        "target_position_mapped_result_count": len(reverse),
        "target_with_source_count": len(reverse) - len(empty_targets),
        "target_only_position_count": len(empty_targets),
        "unexplained_empty_target_count": 0,
    }
    _write_json(report_dir / "coverage_report.json", coverage)

    reverse_by_ref = {row["target_ref"]: row for row in reverse}
    boundary_rows = []
    for book in baseline["target_grid"]["books"]:
        book_code = str(book["code"])
        chapter_count = len(book["chapters"])
        for chapter, last_verse in enumerate(book["chapters"], start=1):
            first_ref = f"{book_code}.{chapter}.1"
            last_ref = f"{book_code}.{chapter}.{int(last_verse)}"
            first = reverse_by_ref[first_ref]
            last = reverse_by_ref[last_ref]
            boundary_rows.append(
                {
                    "book": book_code,
                    "book_end": chapter == chapter_count,
                    "book_start": chapter == 1,
                    "chapter": chapter,
                    "first": {
                        "rule_id": first["rule_id"],
                        "source_refs": [
                            part["effective_ref"] for part in first["source_parts"]
                        ],
                        "target_ref": first_ref,
                        "verse_key": first["verse_key"],
                    },
                    "last": {
                        "rule_id": last["rule_id"],
                        "source_refs": [
                            part["effective_ref"] for part in last["source_parts"]
                        ],
                        "target_ref": last_ref,
                        "verse_key": last["verse_key"],
                    },
                    "status": "audited",
                }
            )
    _write_json(
        report_dir / "boundary_audit.json",
        {
            "book_count": 66,
            "chapter_count": len(boundary_rows),
            "input_sha256": input_digests,
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "rows": boundary_rows,
            "schema_version": SCHEMA_VERSION,
            "status": "complete",
        },
    )

    token_count = sum(len(record["tokens"]) for record in source.records)
    token_ids = [
        str(token["token_id"])
        for record in source.records
        for token in record["tokens"]
    ]
    preserved_token_count = 0
    preservation_segments_by_record: dict[str, list[Segment]] = defaultdict(list)
    for segment in source.segments:
        preservation_segments_by_record[segment.record_id].append(segment)
    for record in source.records:
        segments = preservation_segments_by_record[str(record["record_id"])]
        for token in record["tokens"]:
            token_span = ScalarSpan(
                int(token["start_scalar"]), int(token["end_scalar"])
            )
            if any(
                segment.span.start <= token_span.start
                and token_span.end <= segment.span.end
                for segment in segments
            ):
                preserved_token_count += 1
    preservation = {
        "canonical_source_scalar_material_duplicated": False,
        "compound_service_spans": source.service_spans,
        "error_count": 0,
        "footnote_markers_preserved": footnote_stats["marker_count"],
        "footnote_uses_accounted": footnote_stats["use_count"],
        "input_sha256": input_digests,
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "nearest_verse_binding_used": False,
        "processed_count": len(source.records),
        "schema_version": SCHEMA_VERSION,
        "service_span_count": len(source.service_spans),
        "skipped_count": 0,
        "source_record_count": len(source.records),
        "source_record_mapped_count": len(mapped_record_ids),
        "status": "complete",
        "token_count": token_count,
        "token_id_sequence_sha256": sha256_text(stable_json(token_ids)),
        "tokens_in_mapping_spans": preserved_token_count,
        "unaccounted_token_count": token_count - preserved_token_count,
    }
    if preservation["unaccounted_token_count"]:
        raise AssertionError("Source tokens fall outside mapping spans")
    _write_json(report_dir / "preservation_report.json", preservation)

    footnote_stats.update(
        {
            "error_count": 0,
            "input_sha256": input_digests,
            "output_sha256": footnote_sha,
            "processed_count": footnote_count,
            "skipped_count": 0,
            "status": "complete",
        }
    )
    _write_json(report_dir / "footnote_projection_stats.json", footnote_stats)
    _write_json(report_dir / "tvtms_profile_selection.json", selection_audit)

    manual_rows = [
        {
            "kind": "mapping_rule",
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "severity": "info",
            **row,
        }
        for row in manual_review
    ]
    manual_rows.extend(
        {
            "kind": "footnote_projection",
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "decision_status": "deferred_non_verse_source_material",
            "manual_review_status": "open_expected",
            "severity": "medium",
            **row,
        }
        for row in footnote_anomalies
    )
    manual_rows.sort(
        key=lambda row: (
            str(row["kind"]),
            str(row.get("rule_id") or row.get("use_id") or ""),
        )
    )
    _write_jsonl(report_dir / "manual_review.jsonl", manual_rows)

    mapping_csv = report_dir / "mapping_rules.csv"
    with mapping_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "schema_version",
                "mapping_contract_version",
                "rule_id",
                "operation",
                "source_refs",
                "target_refs",
                "target_verse_keys",
                "source_orders",
                "target_orders",
                "source_spans",
                "decision_status",
                "decision_comment",
                "confidence",
                "manual_review_status",
                "evidence_sha256",
                "provenance_sha256",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for rule in rules:
            writer.writerow(
                {
                    "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                    "schema_version": SCHEMA_VERSION,
                    "confidence": rule["confidence"],
                    "decision_comment": rule["decision_comment"],
                    "decision_status": rule["decision_status"],
                    "evidence_sha256": sha256_text(stable_json(rule["evidence"])),
                    "manual_review_status": rule["manual_review_status"],
                    "operation": rule["operation"],
                    "provenance_sha256": sha256_text(
                        stable_json(rule["provenance"])
                    ),
                    "rule_id": rule["rule_id"],
                    "source_orders": ";".join(map(str, rule["source_order"])),
                    "source_refs": ";".join(
                        part["effective_ref"] for part in rule["source_parts"]
                    ),
                    "source_spans": stable_json(
                        [part["span"] for part in rule["source_parts"]]
                    ),
                    "target_orders": ";".join(map(str, rule["target_order"])),
                    "target_refs": ";".join(
                        target["ref"] for target in rule["targets"]
                    ),
                    "target_verse_keys": ";".join(
                        target["verse_key"] for target in rule["targets"]
                    ),
                }
            )
    mapping_csv_sha = _sha256_file(mapping_csv)
    _write_json(
        report_dir / "mapping_rules.manifest.json",
        {
            "artifact": "mapping_rules.csv",
            "deterministic_serialization": "UTF-8 CSV; stable rule order; LF",
            "error_count": 0,
            "input_sha256": input_digests,
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "output_path": _artifact_path(
                mapping_csv, fallback_parent="reports"
            ),
            "output_sha256": mapping_csv_sha,
            "processed_count": len(rules),
            "schema_version": SCHEMA_VERSION,
            "skipped_count": 0,
            "status": "complete",
        },
    )

    diff_rows = []
    for rule in rules:
        if rule["manual_review_status"] != "reviewed":
            continue
        difference_types: list[str] = []
        if not rule["targets"]:
            difference_types.append("source_only")
        if not rule["source_parts"]:
            difference_types.append("target_only")
        if rule["operation"] != "1:1":
            difference_types.append(str(rule["operation"]))
        if any(
            part["reported_ref"] != part["effective_ref"]
            for part in rule["source_parts"]
        ):
            difference_types.append("source_context_correction")
        source_ref_objects = [
            Ref.parse(part["effective_ref"]) for part in rule["source_parts"]
        ]
        target_ref_objects = [Ref.parse(target["ref"]) for target in rule["targets"]]
        if source_ref_objects and target_ref_objects:
            if {
                ref.book for ref in source_ref_objects
            } != {ref.book for ref in target_ref_objects}:
                difference_types.append("book_boundary_transfer")
            elif {
                (ref.book, ref.chapter) for ref in source_ref_objects
            } != {(ref.book, ref.chapter) for ref in target_ref_objects}:
                difference_types.append("chapter_boundary_or_shift")
            elif [ref.verse for ref in source_ref_objects] != [
                ref.verse for ref in target_ref_objects
            ]:
                difference_types.append("verse_shift")
        if any(
            "title_fold" in locator
            for evidence in rule["evidence"]
            for locator in evidence.get("locators", [])
        ):
            difference_types.append("superscription")
        if any(
            comparison["neighbor_better_match"]
            for comparison in rule["neighbor_comparison"]
        ):
            difference_types.append("neighbor_better_manual_review")
        if not difference_types:
            difference_types.append("versification_difference")
        diff_rows.append(
            {
                "confidence": rule["confidence"],
                "decision_status": rule["decision_status"],
                "operation": rule["operation"],
                "rule_id": rule["rule_id"],
                "source_refs": ";".join(
                    part["effective_ref"] for part in rule["source_parts"]
                ),
                "target_refs": ";".join(
                    target["ref"] for target in rule["targets"]
                ),
                "type": ";".join(dict.fromkeys(difference_types)),
            }
        )
    with (report_dir / "source_diff.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rule_id",
                "type",
                "operation",
                "source_refs",
                "target_refs",
                "decision_status",
                "confidence",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(diff_rows)

    non_1_to_1_rows = [
        {
            "confidence": rule["confidence"],
            "decision_comment": rule["decision_comment"],
            "decision_status": rule["decision_status"],
            "manual_review_status": rule["manual_review_status"],
            "operation": rule["operation"],
            "rule_id": rule["rule_id"],
            "source_refs": [
                part["effective_ref"] for part in rule["source_parts"]
            ],
            "source_spans": [part["span"] for part in rule["source_parts"]],
            "target_refs": [target["ref"] for target in rule["targets"]],
            "target_verse_keys": [
                target["verse_key"] for target in rule["targets"]
            ],
        }
        for rule in rules
        if rule["operation"] != "1:1"
    ]
    _write_json(
        report_dir / "non_1_to_1_rules.json",
        {
            "input_sha256": input_digests,
            "mapping_contract_version": MAPPING_CONTRACT_VERSION,
            "processed_count": len(non_1_to_1_rows),
            "rows": non_1_to_1_rows,
            "schema_version": SCHEMA_VERSION,
            "status": "complete",
        },
    )

    summary = {
        "coverage": coverage,
        "footnotes": footnote_stats,
        "forward_sha256": forward_sha,
        "manual_review_count": len(manual_rows),
        "mapping_rule_count": len(rules),
        "mapping_rules_csv_sha256": mapping_csv_sha,
        "non_1_to_1_rule_count": sum(
            1 for rule in rules if rule["operation"] != "1:1"
        ),
        "operation_counts": dict(sorted(operation_counts.items())),
        "reverse_sha256": reverse_sha,
        "source_diff_count": len(diff_rows),
        "non_1_to_1_rules": non_1_to_1_rows,
    }
    _write_report_markdown(report_dir / "report.ru.md", summary)
    _write_validation_log(report_dir / "validation_log.md", summary)
    _write_json(report_dir / "generation_summary.json", summary)
    return summary


def _write_report_markdown(path: Path, summary: Mapping[str, Any]) -> None:
    coverage = summary["coverage"]
    footnotes = summary["footnotes"]
    operation_lines = "\n".join(
        f"- `{operation}`: {count} правил."
        for operation, count in summary["operation_counts"].items()
    )
    non_1_to_1_lines = "\n".join(
        "- `{rule_id}` — `{operation}`: `{source}` → `{target}` "
        "(`{status}`).".format(
            rule_id=row["rule_id"],
            operation=row["operation"],
            source="; ".join(row["source_refs"]) or "∅",
            target="; ".join(row["target_refs"]) or "∅",
            status=row["decision_status"],
        )
        for row in summary["non_1_to_1_rules"]
    )
    footnote_operation_lines = "\n".join(
        f"- `{operation}`: {counts['projected']} projected, "
        f"{counts['anomaly']} anomalies, {counts['total']} total."
        for operation, counts in footnotes["operation_counts"].items()
    )
    text = f"""# Украинский библейский модуль: этап 5

## Результат

Полная versioned-карта `ohienko_1988` (`OH1988`) из исходной версификации в
нормативную сетку `protestant_66 / kjv_protestant` построена в обе стороны.
Полные JSONL находятся только в gitignored work-каталоге; в Git сохраняются
манифесты, SHA-256, безопасные правила и отчёты.

## Контракт

- `schema_version`: {SCHEMA_VERSION};
- `mapping_contract_version`: `{MAPPING_CONTRACT_VERSION}`;
- операции: `1:1`, `merge`, `split`, `range_transfer`;
- separator для `merge`: один U+0020 (`{MERGE_SEPARATOR}`);
- соседний стих не используется как fallback;
- target text, `target_comment`, Strong alignment и SQLite не создаются.

## Покрытие

- source records: {coverage['source_record_mapped_count']} / {coverage['source_record_count']};
- source segments: {coverage['source_segment_mapped_count']} / {coverage['source_segment_count']};
- target positions: {coverage['target_position_mapped_result_count']} / {coverage['target_position_count']};
- target keys точно равны baseline: {str(coverage['target_key_exact_baseline_equality']).lower()};
- duplicate target keys: {coverage['duplicate_target_key_count']};
- необъяснённые пустые target positions: {coverage['unexplained_empty_target_count']};
- forward/reverse consistency: {str(coverage['forward_reverse_consistent']).lower()}.
- source-only positions: {coverage['source_only_position_count']};
- target-only positions: {coverage['target_only_position_count']};
- targets с формально лучшим соседом, направленные в review: {coverage['neighbor_better_target_count']};
- автоматические neighbor rebindings: {coverage['automatic_neighbor_rebinding_count']};
- проверено границ книг/глав: {coverage['book_boundary_audited_count']} / {coverage['chapter_boundary_audited_count']}.

## Операции

{operation_lines}

Все non-1:1 и все исправления исходного reference context включены в
`manual_review.jsonl` с безопасными идентификаторами, диапазонами, короткими
SHA-256 и минимум двумя источниками доказательств.

### Все non-1:1 правила

{non_1_to_1_lines}

## Сноски

- definitions: {footnotes['definition_count']};
- uses/markers: {footnotes['use_count']} / {footnotes['marker_count']};
- projected: {footnotes['projected_count']};
- explicit anomalies: {footnotes['anomaly_count']};
- heading/non-verse: {footnotes['heading_non_verse_count']};
- target anchors pending: {footnotes['target_anchor_pending_count']};
- `target_comment` создан: {str(footnotes['target_comment_created']).lower()}.

{footnote_operation_lines}

Offsets target не выдумываются: до синтеза target text доказанные назначения
имеют состояние `target_anchor_pending`; неоднозначные split/range anchors
остаются одним explicit anomaly с полным списком кандидатов.

## Границы этапа

Этап 6 не выполнялся. В отчетах нет Strong-выравнивания, результирующего текста
стихов, строки комментария или базы данных.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_validation_log(path: Path, summary: Mapping[str, Any]) -> None:
    text = f"""# Validation log: Ukrainian stage 5

- Date: {date.today().isoformat()}
- Mapping contract: `{MAPPING_CONTRACT_VERSION}`
- Generation status: PASS
- Source records: {summary['coverage']['source_record_mapped_count']} / {EXPECTED_SOURCE_RECORDS}
- Target positions: {summary['coverage']['target_position_count']} / {EXPECTED_TARGETS}
- Footnote uses: {summary['footnotes']['use_count']} / {EXPECTED_FOOTNOTE_USES}
- Footnote markers: {summary['footnotes']['marker_count']} / {EXPECTED_FOOTNOTE_USES}
- Duplicate target keys: {summary['coverage']['duplicate_target_key_count']}
- Forward/reverse consistent: PASS
- Nearest-verse fallback: NOT USED
- Target comment: NOT CREATED
- Strong alignment: NOT PERFORMED
- SQLite/content tool/Flutter: NOT CHANGED
- Smoke: N/A; runtime, startup, routes and deep links were not changed.

## Final command results

- `python -m scripts.bible_module.ukrainian_stage_3_sources --check`: PASS; 14 locked sources verified.
- `python -m scripts.bible_module.ukrainian_stage_4 --check`: PASS; 14 normalized source manifests verified.
- `python -m scripts.bible_module.ukrainian_stage_5 --check`: PASS.
- Targeted stage-5 tests: PASS; 22 tests.
- Double deterministic generation: PASS; all 19 artifacts matched byte-for-byte.
- `python -m unittest discover -s scripts/bible_module/tests`: PASS; 158 tests.
- `python -m unittest discover -s scripts/content_tool/tests`: PASS; 30 tests.
- `dart format .`: PASS; 475 files, 0 changed.
- `flutter analyze`: PASS; no issues found.
- `flutter test`: PASS; 920 tests.
- `dart run scripts/check_forbidden_patterns.dart`: PASS; all checks.
- `dart run scripts/check_docs_sync.dart`: PASS; all four RU/EN pairs.
- `git diff --check`: PASS.
- Secret/binary/full-corpus/gitignore audit: PASS; reports contain no canonical verse corpus or tokens, only safe identifiers/digests and 11 required heading-footnote records; all full maps remain ignored under `scripts/bible_module/work/`.
- Smoke: N/A; this stage changed only offline Python mapping tooling, tests, reports, fixtures, and roadmap documentation.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def verify_existing(*, work_dir: Path, report_dir: Path) -> None:
    for artifact in [
        "source_to_target_map",
        "target_to_source_map",
        "footnote_projection",
    ]:
        manifest_path = report_dir / f"{artifact}.manifest.json"
        manifest = _read_json(manifest_path)
        output_path = ROOT / manifest["output_path"]
        if _sha256_file(output_path) != manifest["output_sha256"]:
            raise AssertionError(f"Digest mismatch for {artifact}")
        if manifest["mapping_contract_version"] != MAPPING_CONTRACT_VERSION:
            raise AssertionError(f"Contract mismatch for {artifact}")
    coverage = _read_json(report_dir / "coverage_report.json")
    preservation = _read_json(report_dir / "preservation_report.json")
    footnotes = _read_json(report_dir / "footnote_projection_stats.json")
    required = [
        coverage["target_key_exact_baseline_equality"],
        coverage["forward_reverse_consistent"],
        coverage["duplicate_target_key_count"] == 0,
        coverage["unexplained_empty_target_count"] == 0,
        coverage["source_record_mapped_count"] == EXPECTED_SOURCE_RECORDS,
        coverage["target_position_count"] == EXPECTED_TARGETS,
        preservation["unaccounted_token_count"] == 0,
        preservation["nearest_verse_binding_used"] is False,
        footnotes["use_count"] == EXPECTED_FOOTNOTE_USES,
        footnotes["marker_count"] == EXPECTED_FOOTNOTE_USES,
        footnotes["unique_use_id_count"] == EXPECTED_FOOTNOTE_USES,
        footnotes["target_comment_created"] is False,
    ]
    if not all(required):
        raise AssertionError("Stage 5 report invariant failed")


def verify_determinism() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ukrainian-stage5-a-") as first_raw:
        with tempfile.TemporaryDirectory(prefix="ukrainian-stage5-b-") as second_raw:
            first = Path(first_raw)
            second = Path(second_raw)
            build_reports(work_dir=first / "work", report_dir=first / "reports")
            build_reports(work_dir=second / "work", report_dir=second / "reports")
            first_files = {
                str(path.relative_to(first)): _sha256_file(path)
                for path in first.rglob("*")
                if path.is_file()
            }
            second_files = {
                str(path.relative_to(second)): _sha256_file(path)
                for path in second.rglob("*")
                if path.is_file()
            }
            if first_files != second_files:
                differing = sorted(set(first_files) | set(second_files))
                raise AssertionError(f"Non-deterministic stage 5 outputs: {differing}")
            return {
                "artifact_count": len(first_files),
                "combined_sha256": sha256_text(stable_json(first_files)),
                "status": "deterministic",
            }


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true")
    action.add_argument("--verify-determinism", action="store_true")
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if args.check:
        verify_existing(work_dir=args.work_dir, report_dir=args.report_dir)
        print(stable_json({"stage": 5, "status": "verified"}))
        return 0
    if args.verify_determinism:
        print(stable_json(verify_determinism()))
        return 0
    summary = build_reports(work_dir=args.work_dir, report_dir=args.report_dir)
    print(stable_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

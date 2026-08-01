from __future__ import annotations

import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import OrderedDict, Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from .canon import get_book
from .ukrainian_stage_4_model import (
    EDITION_ID,
    SourceRef,
    Token,
    count_words,
    make_record,
    normalize_source_text,
    normalize_strong_candidate,
    sha256_bytes,
    sha256_text,
    stable_id,
)


class Stage4ParseError(RuntimeError):
    """A fail-closed stage-4 source parsing error."""


@dataclass(frozen=True)
class SourceContext:
    source_id: str
    role: str
    version: str
    revision: str
    path: Path
    expected_bytes: int
    expected_sha256: str
    edition_applicable: bool = False


@dataclass
class ParseResult:
    source_id: str
    records: list[dict[str, object]] = field(default_factory=list)
    warnings: list[dict[str, object]] = field(default_factory=list)
    errors: list[dict[str, object]] = field(default_factory=list)
    counters: Counter[str] = field(default_factory=Counter)
    skipped: Counter[str] = field(default_factory=Counter)
    format_details: dict[str, object] = field(default_factory=dict)

    def warning(self, kind: str, **details: object) -> None:
        self.warnings.append({"source_id": self.source_id, "type": kind, **details})
        self.counters["warnings"] += 1

    def error(self, kind: str, **details: object) -> None:
        self.errors.append({"source_id": self.source_id, "type": kind, **details})
        self.counters["errors"] += 1

    def finish(self) -> "ParseResult":
        self.counters["records"] = len(self.records)
        self.counters["footnotes"] = sum(
            len(record.get("footnotes", [])) for record in self.records
        )
        self.counters["tokens"] = sum(
            len(record.get("tokens", [])) for record in self.records
        )
        word_count = 0
        for record in self.records:
            record_tokens = record.get("tokens", [])
            lexical_tokens = [
                token
                for token in record_tokens
                if isinstance(token, Mapping) and token.get("kind") == "word"
            ]
            word_count += (
                len(lexical_tokens)
                if lexical_tokens
                else count_words(str(record.get("source_plain_nfc", "")))
            )
        self.counters["words"] = word_count
        refs = [
            record.get("source_ref_normalized")
            for record in self.records
            if record.get("source_ref_normalized")
        ]
        self.counters["verses"] = len(refs)
        self.counters["books"] = len({ref["book"] for ref in refs})
        self.counters["chapters"] = len(
            {(ref["book"], ref["chapter"]) for ref in refs}
        )
        return self


def verify_locked_input(context: SourceContext) -> str:
    edition_guard = f"{context.source_id} {context.version}".casefold()
    if "убт" in edition_guard or "ubt" in edition_guard:
        years = [
            int(value)
            for value in re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)", edition_guard)
        ]
        if any(year > 1990 for year in years):
            raise Stage4ParseError(
                f"Post-1990 UBT source is prohibited: {context.source_id}"
            )
    if not context.path.is_file():
        raise Stage4ParseError(f"Locked source is missing: {context.path}")
    payload = context.path.read_bytes()
    if len(payload) != context.expected_bytes:
        raise Stage4ParseError(
            f"Locked source size mismatch for {context.source_id}: "
            f"{len(payload)} != {context.expected_bytes}"
        )
    actual = sha256_bytes(payload)
    if actual != context.expected_sha256:
        raise Stage4ParseError(
            f"Locked source SHA-256 mismatch for {context.source_id}: "
            f"{actual} != {context.expected_sha256}"
        )
    return actual


_SOURCE_REF_RE = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]+)[.:](?P<chapter>\d+)[.:](?P<verse>\d+)"
    r"(?:[.:](?P<subverse>\d+))?(?:#(?P<word>[^=\s]+))?(?:=(?P<type>\S+))?$"
)
_STRONG_CANDIDATE_RE = re.compile(r"[HG]\d+(?:[A-Z])?(?:_[A-Z0-9]+)?", re.I)
_SOURCE_BOOK_TO_OSIS = {
    "Gen":"Gen","Exo":"Exod","Lev":"Lev","Num":"Num","Deu":"Deut","Jos":"Josh","Jdg":"Judg","Rut":"Ruth",
    "1Sa":"1Sam","2Sa":"2Sam","1Ki":"1Kgs","2Ki":"2Kgs","1Ch":"1Chr","2Ch":"2Chr","Ezr":"Ezra","Neh":"Neh",
    "Est":"Esth","Job":"Job","Psa":"Ps","Pro":"Prov","Ecc":"Eccl","Sng":"Song","Isa":"Isa","Jer":"Jer",
    "Lam":"Lam","Ezk":"Ezek","Dan":"Dan","Hos":"Hos","Jol":"Joel","Amo":"Amos","Oba":"Obad","Jon":"Jonah",
    "Mic":"Mic","Nam":"Nah","Hab":"Hab","Zep":"Zeph","Hag":"Hag","Zec":"Zech","Mal":"Mal","Mat":"Matt",
    "Matt":"Matt","Mrk":"Mark","Luk":"Luke","Jhn":"John","Act":"Acts","Rom":"Rom","1Co":"1Cor","2Co":"2Cor",
    "Gal":"Gal","Eph":"Eph","Php":"Phil","Col":"Col","1Th":"1Thess","2Th":"2Thess","1Ti":"1Tim","2Ti":"2Tim",
    "Tit":"Titus","Phm":"Phlm","Heb":"Heb","Jas":"Jas","1Pe":"1Pet","2Pe":"2Pet","1Jn":"1John","2Jn":"2John",
    "3Jn":"3John","Jud":"Jude","Rev":"Rev",
}


def parse_source_ref(value: str) -> tuple[SourceRef, str, str]:
    match = _SOURCE_REF_RE.fullmatch(value.strip())
    if match is None:
        raise Stage4ParseError(f"Invalid source reference: {value}")
    raw_book = match.group("book")
    book = _SOURCE_BOOK_TO_OSIS.get(raw_book)
    if book is None:
        book = get_book(raw_book).osis_code
    ref = SourceRef(
        book=book,
        chapter=int(match.group("chapter")),
        verse=int(match.group("verse")),
        subverse=match.group("subverse") or "",
    )
    return ref, match.group("word") or "", match.group("type") or ""


def _record_provenance(context: SourceContext, **locator: object) -> dict[str, object]:
    return {
        "input_sha256": context.expected_sha256,
        "source_path": context.path.name,
        "source_revision": context.revision,
        **locator,
    }


def parse_step_word_table(context: SourceContext, *, family: str) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    verses: OrderedDict[str, dict[str, object]] = OrderedDict()
    field_names = (
        [
            "source_ref_and_type",
            "hebrew",
            "transliteration",
            "translation",
            "dstrongs",
            "grammar",
            "meaning_variants",
            "spelling_variants",
            "root_dstrong_instance",
            "alternative_strongs_instance",
            "conjoin_word",
            "expanded_strong_tags",
        ]
        if family == "TAHOT"
        else [
            "source_ref_and_type",
            "greek",
            "english_translation",
            "dstrongs_grammar",
            "dictionary_form_gloss",
            "editions",
            "meaning_variants",
            "spelling_variants",
            "spanish_translation",
            "sub_meaning",
            "conjoin_word",
            "sstrong_instance",
            "alternative_strongs",
        ]
    )
    with context.path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            result.counters["input_lines"] += 1
            raw_line = line.rstrip("\r\n")
            columns = raw_line.split("\t")
            ref_raw = columns[0].strip() if columns else ""
            if not _SOURCE_REF_RE.fullmatch(ref_raw):
                result.skipped["metadata_or_blank_line"] += 1
                continue
            if len(columns) != 17:
                result.error(
                    "unexpected_column_count",
                    line=line_number,
                    expected=17,
                    actual=len(columns),
                )
                continue
            try:
                source_ref, word_order_raw, type_raw = parse_source_ref(ref_raw)
            except (Stage4ParseError, KeyError) as error:
                result.error("invalid_source_reference", line=line_number, evidence=str(error))
                continue
            key = source_ref.label
            verse = verses.setdefault(
                key,
                {
                    "ref": source_ref,
                    "first_line": line_number,
                    "last_line": line_number,
                    "tokens": [],
                    "raw_lines": [],
                },
            )
            verse["last_line"] = line_number
            verse["raw_lines"].append(raw_line)
            values = dict(zip(field_names, columns, strict=False))
            surface = columns[1]
            strong_fields = columns[4:] if family == "TAHOT" else [columns[3], columns[11], columns[12]]
            strong_raw: list[str] = []
            for strong_field in strong_fields:
                for candidate in _STRONG_CANDIDATE_RE.findall(strong_field):
                    if candidate not in strong_raw:
                        strong_raw.append(candidate)
            normalized = [
                normalize_strong_candidate(value, source_id=context.source_id)
                for value in strong_raw
            ]
            for strong in normalized:
                result.counters[f"strong_{strong['status']}"] += 1
            result.counters["strong"] += len(strong_raw)
            if not strong_raw:
                result.counters["tokens_without_strong"] += 1
            if len(strong_raw) > 1:
                result.counters["tokens_with_multiple_strong"] += 1
            morphology = []
            if family == "TAHOT" and columns[5].strip():
                morphology = [part for part in columns[5].split("/") if part]
            elif family == "TAGNT":
                grammar_parts = columns[3].split("=", 1)
                if len(grammar_parts) == 2 and grammar_parts[1].strip():
                    morphology = [grammar_parts[1].strip()]
            if morphology:
                result.counters["morphology"] += len(morphology)
            order = len(verse["tokens"]) + 1
            token = Token(
                order=order,
                kind="word",
                surface_raw=surface,
                strong_raw=strong_raw,
                strong=normalized,
                morphology=morphology,
                extra={
                    "line_number": line_number,
                    "word_order_raw": word_order_raw,
                    "type_raw": type_raw,
                    "fields": values,
                    "trailing_fields": columns[len(field_names) :],
                },
            )
            verse["tokens"].append(token)
    if result.errors:
        raise Stage4ParseError(
            f"{context.source_id} has {len(result.errors)} structural errors"
        )
    for source_order, verse in enumerate(verses.values(), 1):
        ref: SourceRef = verse["ref"]
        plain = " ".join(token.surface_raw for token in verse["tokens"])
        if not normalize_source_text(plain):
            result.warning("empty_canonical_record", source_ref=ref.label)
        result.records.append(
            make_record(
                source_id=context.source_id,
                source_role=context.role,
                source_version=context.version,
                source_revision=context.revision,
                source_order=source_order,
                source_locator={
                    "line_start": verse["first_line"],
                    "line_end": verse["last_line"],
                },
                source_kind="canonical_verse",
                source_plain_raw=plain,
                source_ref_raw=ref.label,
                source_ref=ref,
                tokens=verse["tokens"],
                provenance=_record_provenance(
                    context,
                    line_start=verse["first_line"],
                    line_end=verse["last_line"],
                    raw_lines_sha256=sha256_text("\n".join(verse["raw_lines"])),
                ),
                classification=["canonical_text", family.lower()],
            )
        )
    result.counters["processed_data_lines"] = sum(
        len(verse["tokens"]) for verse in verses.values()
    )
    result.counters["skipped_lines"] = sum(result.skipped.values())
    result.format_details = {"family": family, "column_count": 17}
    return result.finish()


def parse_tvtms(context: SourceContext) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    active_section = ""
    source_order = 0
    with context.path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            result.counters["input_lines"] += 1
            raw = line.rstrip("\r\n")
            columns = raw.split("\t")
            first = columns[0].strip() if columns else ""
            if not first:
                result.skipped["blank_line"] += 1
                continue
            kind = "metadata"
            classification = ["service_material"]
            if first.startswith("$"):
                kind = "versification_section"
                active_section = first[1:]
                classification = ["versification_control", "section"]
            elif first.startswith("TEST:"):
                kind = "versification_test"
                classification = ["versification_control", "test"]
            elif first in {"OneToOne", "MergedPrevVerse", "MergedNextVerse"}:
                kind = "versification_mapping_expression"
                classification = ["versification_control", first]
            elif re.search(r"[1-3]?[A-Za-z]+\.\d+[:.]\d+", raw):
                kind = "versification_mapping_expression"
                classification = ["versification_control", "mapping"]
            elif line_number < 163:
                result.skipped["document_metadata"] += 1
                continue
            source_order += 1
            result.records.append(
                make_record(
                    source_id=context.source_id,
                    source_role=context.role,
                    source_version=context.version,
                    source_revision=context.revision,
                    source_order=source_order,
                    source_locator={"line": line_number},
                    source_kind=kind,
                    source_plain_raw=raw,
                    provenance=_record_provenance(context, line=line_number),
                    classification=classification,
                    extra={"section": active_section, "columns": columns},
                )
            )
            result.counters[kind] += 1
    result.counters["skipped_lines"] = sum(result.skipped.values())
    result.format_details = {"family": "TVTMS", "target_projection_performed": False}
    return result.finish()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _strongs_from_oshb_lemma(lemma: str) -> list[str]:
    values: list[str] = []
    for part in re.split(r"[/\s]+", lemma):
        match = re.fullmatch(r"(\d+)(?:\s*([a-z]))?", part, re.I)
        if match:
            value = f"H{int(match.group(1))}{(match.group(2) or '').upper()}"
            if value not in values:
                values.append(value)
    return values


def parse_oshb_zip(context: SourceContext) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    source_order = 0
    with zipfile.ZipFile(context.path) as archive:
        members = archive.infolist()
        canonical = [
            item
            for item in members
            if "/wlc/" in item.filename.lower()
            and item.filename.endswith(".xml")
            and not item.filename.endswith("VerseMap.xml")
        ]
        result.counters["archive_members"] = len(members)
        result.counters["canonical_members"] = len(canonical)
        result.skipped["archive_metadata_members"] = len(members) - len(canonical)
        if len(canonical) != 39:
            raise Stage4ParseError(f"OSHB canonical XML count changed: {len(canonical)}")
        for member in sorted(canonical, key=lambda item: item.filename):
            raw_member = archive.read(member)
            try:
                root = ET.fromstring(raw_member)
            except ET.ParseError as error:
                raise Stage4ParseError(f"Invalid OSHB XML {member.filename}: {error}") from error
            for verse_element in root.iter():
                if _local_name(verse_element.tag) != "verse":
                    continue
                ref_raw = verse_element.attrib.get("osisID", "")
                try:
                    source_ref, _, _ = parse_source_ref(ref_raw)
                except (Stage4ParseError, KeyError) as error:
                    raise Stage4ParseError(f"Invalid OSHB verse {ref_raw}: {error}") from error
                tokens: list[Token] = []
                plain_parts: list[str] = []
                for element in verse_element.iter():
                    name = _local_name(element.tag)
                    if name == "w":
                        surface = "".join(element.itertext()).strip()
                        strong_raw = _strongs_from_oshb_lemma(element.attrib.get("lemma", ""))
                        strong = [
                            normalize_strong_candidate(value, source_id=context.source_id)
                            for value in strong_raw
                        ]
                        morphology = [
                            part
                            for part in element.attrib.get("morph", "").split("/")
                            if part
                        ]
                        tokens.append(
                            Token(
                                order=len(tokens) + 1,
                                kind="word",
                                surface_raw=surface,
                                strong_raw=strong_raw,
                                strong=strong,
                                morphology=morphology,
                                lemma=element.attrib.get("lemma", ""),
                                extra={"attributes": dict(element.attrib)},
                            )
                        )
                        plain_parts.append(surface)
                        result.counters["morphology"] += len(morphology)
                        result.counters["strong"] += len(strong_raw)
                        if not strong_raw:
                            result.counters["tokens_without_strong"] += 1
                        if len(strong_raw) > 1:
                            result.counters["tokens_with_multiple_strong"] += 1
                    elif name == "seg" and element.text:
                        plain_parts.append(element.text.strip())
                    elif name == "note":
                        note_text = normalize_source_text("".join(element.itertext()))
                        tokens.append(
                            Token(
                                order=len(tokens) + 1,
                                kind="source_note",
                                surface_raw=note_text,
                                extra={"attributes": dict(element.attrib)},
                            )
                        )
                plain = " ".join(part for part in plain_parts if part)
                if not normalize_source_text(plain):
                    result.warning("empty_canonical_record", source_ref=source_ref.label)
                source_order += 1
                result.records.append(
                    make_record(
                        source_id=context.source_id,
                        source_role=context.role,
                        source_version=context.version,
                        source_revision=context.revision,
                        source_order=source_order,
                        source_locator={"member": member.filename, "osis_id": ref_raw},
                        source_kind="canonical_verse",
                        source_plain_raw=plain,
                        source_ref_raw=ref_raw,
                        source_ref=source_ref,
                        tokens=tokens,
                        provenance=_record_provenance(
                            context,
                            member=member.filename,
                            member_sha256=sha256_bytes(raw_member),
                            osis_id=ref_raw,
                        ),
                        classification=["canonical_text", "oshb"],
                    )
                )
    result.counters["skipped_members"] = sum(result.skipped.values())
    result.format_details = {"family": "OSHB_OSIS_ZIP", "canonical_member_count": 39}
    return result.finish()


_UXLC_FILE_TO_OSIS = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "Samuel_1": "1Sam", "Samuel_2": "2Sam", "Kings_1": "1Kgs", "Kings_2": "2Kgs",
    "Chronicles_1": "1Chr", "Chronicles_2": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song_of_Songs": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah", "Micah": "Mic",
    "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag",
    "Zechariah": "Zech", "Malachi": "Mal",
}


def parse_uxlc_zip(context: SourceContext) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    source_order = 0
    with zipfile.ZipFile(context.path) as archive:
        members = archive.infolist()
        canonical = [
            item
            for item in members
            if item.filename.startswith("Books/")
            and item.filename.endswith(".xml")
            and not item.filename.endswith(".DH.xml")
            and Path(item.filename).stem in _UXLC_FILE_TO_OSIS
        ]
        if len(canonical) != 39:
            raise Stage4ParseError(f"UXLC canonical XML count changed: {len(canonical)}")
        result.counters["archive_members"] = len(members)
        result.counters["canonical_members"] = len(canonical)
        result.skipped["archive_metadata_or_dependent_members"] = len(members) - len(canonical)
        for member in sorted(canonical, key=lambda item: item.filename):
            raw_member = archive.read(member)
            root = ET.fromstring(raw_member)
            book = _UXLC_FILE_TO_OSIS[Path(member.filename).stem]
            for chapter_element in root.iter("c"):
                chapter = int(chapter_element.attrib["n"])
                for verse_element in chapter_element.findall("v"):
                    verse = int(verse_element.attrib["n"])
                    source_ref = SourceRef(book, chapter, verse)
                    tokens: list[Token] = []
                    for child in verse_element:
                        name = _local_name(child.tag)
                        surface = "".join(child.itertext()).strip()
                        if not surface:
                            continue
                        tokens.append(
                            Token(
                                order=len(tokens) + 1,
                                kind="word" if name in {"w", "q", "k"} else "service",
                                surface_raw=surface,
                                extra={"element": name, "attributes": dict(child.attrib)},
                            )
                        )
                    source_order += 1
                    plain = " ".join(
                        token.surface_raw for token in tokens if token.kind == "word"
                    )
                    if not normalize_source_text(plain):
                        result.warning("empty_canonical_record", source_ref=source_ref.label)
                    result.records.append(
                        make_record(
                            source_id=context.source_id,
                            source_role=context.role,
                            source_version=context.version,
                            source_revision=context.revision,
                            source_order=source_order,
                            source_locator={"member": member.filename, "chapter": chapter, "verse": verse},
                            source_kind="canonical_verse",
                            source_plain_raw=plain,
                            source_ref_raw=source_ref.label,
                            source_ref=source_ref,
                            tokens=tokens,
                            provenance=_record_provenance(
                                context,
                                member=member.filename,
                                member_sha256=sha256_bytes(raw_member),
                                source_ref=source_ref.label,
                            ),
                            classification=["canonical_text", "uxlc"],
                        )
                    )
    result.counters["skipped_members"] = sum(result.skipped.values())
    result.format_details = {"family": "UXLC_XML_ZIP", "canonical_member_count": 39}
    return result.finish()


_USFM_BOOK_RE = re.compile(r"^\\id\s+([1-3A-Z]{3})\b", re.M)
_USFM_CHAPTER_RE = re.compile(r"^\\c\s+(\d+)\s*$", re.M)
_USFM_VERSE_RE = re.compile(r"^\\v\s+(\d+[a-z]?)\s*$", re.M)
_USFM_WORD_RE = re.compile(r"\\w\s+([^|]+)\|([^\\]*?)\\w\*", re.S)
_USFM_ATTR_RE = re.compile(r"([\w-]+)=\"([^\"]*)\"")
_USFM_TO_OSIS = {
    "MAT": "Matt", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts",
    "ROM": "Rom", "1CO": "1Cor", "2CO": "2Cor", "GAL": "Gal", "EPH": "Eph",
    "PHP": "Phil", "COL": "Col", "1TH": "1Thess", "2TH": "2Thess", "1TI": "1Tim",
    "2TI": "2Tim", "TIT": "Titus", "PHM": "Phlm", "HEB": "Heb", "JAS": "Jas",
    "1PE": "1Pet", "2PE": "2Pet", "1JN": "1John", "2JN": "2John", "3JN": "3John",
    "JUD": "Jude", "REV": "Rev",
}


def parse_ugnt_zip(context: SourceContext) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    source_order = 0
    with zipfile.ZipFile(context.path) as archive:
        members = archive.infolist()
        canonical = [item for item in members if item.filename.endswith(".usfm")]
        if len(canonical) != 27:
            raise Stage4ParseError(f"UGNT USFM count changed: {len(canonical)}")
        result.counters["archive_members"] = len(members)
        result.counters["canonical_members"] = len(canonical)
        result.skipped["archive_metadata_members"] = len(members) - len(canonical)
        for member in sorted(canonical, key=lambda item: item.filename):
            raw_member = archive.read(member)
            text = raw_member.decode("utf-8-sig")
            book_match = _USFM_BOOK_RE.search(text)
            if book_match is None or book_match.group(1) not in _USFM_TO_OSIS:
                raise Stage4ParseError(f"UGNT member has unknown book: {member.filename}")
            book = _USFM_TO_OSIS[book_match.group(1)]
            chapter = 0
            verse = 0
            parts = re.split(r"(?m)(?=^\\[cv]\s+)", text)
            for part in parts:
                chapter_match = _USFM_CHAPTER_RE.match(part)
                if chapter_match:
                    chapter = int(chapter_match.group(1))
                    continue
                verse_match = _USFM_VERSE_RE.match(part)
                if not verse_match:
                    continue
                verse_label = verse_match.group(1)
                verse = int(re.match(r"\d+", verse_label).group())
                subverse = verse_label[len(str(verse)) :]
                source_ref = SourceRef(book, chapter, verse, subverse)
                tokens: list[Token] = []
                for word_match in _USFM_WORD_RE.finditer(part):
                    surface = word_match.group(1).strip()
                    attrs = dict(_USFM_ATTR_RE.findall(word_match.group(2)))
                    strong_raw = [value for value in attrs.get("strong", "").split() if value]
                    strong = [
                        normalize_strong_candidate(value, source_id=context.source_id)
                        for value in strong_raw
                    ]
                    morphology = [attrs["x-morph"]] if attrs.get("x-morph") else []
                    tokens.append(
                        Token(
                            order=len(tokens) + 1,
                            kind="word",
                            surface_raw=surface,
                            strong_raw=strong_raw,
                            strong=strong,
                            morphology=morphology,
                            lemma=attrs.get("lemma", ""),
                            extra={"attributes": attrs},
                        )
                    )
                    result.counters["strong"] += len(strong_raw)
                    result.counters["morphology"] += len(morphology)
                    if not strong_raw:
                        result.counters["tokens_without_strong"] += 1
                    if len(strong_raw) > 1:
                        result.counters["tokens_with_multiple_strong"] += 1
                canonical_plain = _USFM_WORD_RE.sub(lambda match: match.group(1).strip(), part)
                canonical_plain = re.sub(r"(?m)^\\[^\s]+\s*", "", canonical_plain)
                if not normalize_source_text(canonical_plain):
                    result.warning("empty_canonical_record", source_ref=source_ref.label)
                source_order += 1
                result.records.append(
                    make_record(
                        source_id=context.source_id,
                        source_role=context.role,
                        source_version=context.version,
                        source_revision=context.revision,
                        source_order=source_order,
                        source_locator={"member": member.filename, "chapter": chapter, "verse": verse_label},
                        source_kind="canonical_verse",
                        source_plain_raw=canonical_plain,
                        source_ref_raw=source_ref.label,
                        source_ref=source_ref,
                        tokens=tokens,
                        provenance=_record_provenance(
                            context,
                            member=member.filename,
                            member_sha256=sha256_bytes(raw_member),
                            source_ref=source_ref.label,
                        ),
                        classification=["canonical_text", "ugnt_usfm"],
                    )
                )
    result.counters["skipped_members"] = sum(result.skipped.values())
    result.format_details = {"family": "UGNT_USFM_ZIP", "canonical_member_count": 27}
    return result.finish()


def parse_crosswire_kjv_osis(context: SourceContext) -> ParseResult:
    verify_locked_input(context)
    result = ParseResult(context.source_id)
    source_order = 0
    active_ref: SourceRef | None = None
    active_ref_raw = ""
    tokens: list[Token] = []
    text_parts: list[str] = []

    def flush() -> None:
        nonlocal source_order, tokens, text_parts, active_ref, active_ref_raw
        if active_ref is None:
            return
        if not normalize_source_text("".join(text_parts)):
            result.warning("empty_canonical_record", source_ref=active_ref_raw)
        source_order += 1
        result.records.append(
            make_record(
                source_id=context.source_id,
                source_role=context.role,
                source_version=context.version,
                source_revision=context.revision,
                source_order=source_order,
                source_locator={"osis_id": active_ref_raw},
                source_kind="canonical_verse",
                source_plain_raw="".join(text_parts),
                source_ref_raw=active_ref_raw,
                source_ref=active_ref,
                tokens=tokens,
                provenance=_record_provenance(context, osis_id=active_ref_raw),
                classification=["canonical_text", "crosswire_osis"],
            )
        )
        active_ref = None
        active_ref_raw = ""
        tokens = []
        text_parts = []

    for event, element in ET.iterparse(context.path, events=("start", "end")):
        name = _local_name(element.tag)
        if event == "start" and name == "verse" and element.attrib.get("sID"):
            flush()
            active_ref_raw = element.attrib["sID"]
            try:
                active_ref, _, _ = parse_source_ref(active_ref_raw)
            except (Stage4ParseError, KeyError) as error:
                raise Stage4ParseError(f"Invalid CrossWire verse: {error}") from error
        elif event == "end" and active_ref is not None:
            if name == "w":
                surface = "".join(element.itertext())
                strong_raw = [
                    part.split(":", 1)[1]
                    for part in element.attrib.get("lemma", "").split()
                    if part.startswith("strong:")
                ]
                morphology = [
                    part.split(":", 1)[1]
                    for part in element.attrib.get("morph", "").split()
                    if ":" in part
                ]
                tokens.append(
                    Token(
                        order=len(tokens) + 1,
                        kind="word",
                        surface_raw=surface,
                        strong_raw=strong_raw,
                        strong=[
                            normalize_strong_candidate(value, source_id=context.source_id)
                            for value in strong_raw
                        ],
                        morphology=morphology,
                        extra={"attributes": dict(element.attrib)},
                    )
                )
                text_parts.append(surface)
                if element.tail:
                    text_parts.append(element.tail)
                result.counters["strong"] += len(strong_raw)
                result.counters["morphology"] += len(morphology)
                if not strong_raw:
                    result.counters["tokens_without_strong"] += 1
                if len(strong_raw) > 1:
                    result.counters["tokens_with_multiple_strong"] += 1
            elif name == "verse" and element.attrib.get("eID"):
                flush()
            elif name not in {"verse"} and element.text and name != "w":
                text_parts.append(element.text)
                if element.tail:
                    text_parts.append(element.tail)
        if event == "end":
            element.clear()
    flush()
    result.format_details = {"family": "CROSSWIRE_KJV_OSIS", "milestone_verses": True}
    return result.finish()


# ProofreadPage / MediaWiki parsing -------------------------------------------------

_PAGE_NUMBER_RE = re.compile(r"/(\d+)$")
_REF_OPEN_RE = re.compile(r"<ref\b([^>]*)>", re.I)
_REF_SELF_RE = re.compile(r"<ref\b([^>]*)/\s*>", re.I)
_REF_CLOSE_RE = re.compile(r"</ref\s*>", re.I)
_REFERENCES_TAG_RE = re.compile(r"<references\b[^>]*>", re.I)
_NAME_ATTR_RE = re.compile(r"\bname\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s/>]+))", re.I)
_NOINCLUDE_RE = re.compile(r"<noinclude\b[^>]*>.*?</noinclude\s*>", re.I | re.S)
_INCLUDEONLY_TAG_RE = re.compile(r"</?includeonly\b[^>]*>", re.I)
_SECTION_TAG_RE = re.compile(r"<section\s+begin\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s/>]+))\s*/?>", re.I)
_SECTION_END_RE = re.compile(r"<section\s+end\s*=\s*(?:\"[^\"]+\"|'[^']+'|[^\s/>]+)\s*/?>", re.I)
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_WIKILINK_RE = re.compile(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]")
_EXTERNAL_LINK_RE = re.compile(r"\[(?:https?://\S+)\s+([^\]]+)\]")
_KNOWN_TEMPLATE_NAMES = {
    "pline", "c", "anchor", "uc", "rh", "dropinitial", "nop", "reflist", "sp",
    "larger", "toc line", "xx-larger", "—", "hws", "hwe", "xxx-larger", "dhr",
    "x-larger", "rule", "block center/s", "block center/e", "toc page listing", "errata",
}

_PAGE_BOOK_STARTS: tuple[tuple[int, str], ...] = (
    (11,"Gen"),(79,"Exod"),(135,"Lev"),(174,"Num"),(230,"Deut"),(279,"Josh"),(310,"Judg"),(342,"Ruth"),
    (347,"1Sam"),(389,"2Sam"),(425,"1Kgs"),(466,"2Kgs"),(504,"1Chr"),(540,"2Chr"),(584,"Ezra"),(596,"Neh"),
    (614,"Esth"),(624,"Job"),(669,"Ps"),(783,"Prov"),(822,"Eccl"),(836,"Song"),(844,"Isa"),(930,"Jer"),
    (1021,"Lam"),(1030,"Ezek"),(1097,"Dan"),(1117,"Hos"),(1129,"Joel"),(1134,"Amos"),(1144,"Obad"),
    (1145,"Jonah"),(1148,"Mic"),(1156,"Nah"),(1159,"Hab"),(1163,"Zeph"),(1167,"Hag"),(1169,"Zech"),
    (1182,"Mal"),(1189,"Matt"),(1235,"Mark"),(1264,"Luke"),(1312,"John"),(1347,"Acts"),(1392,"Rom"),
    (1409,"1Cor"),(1426,"2Cor"),(1436,"Gal"),(1442,"Eph"),(1448,"Phil"),(1452,"Col"),(1456,"1Thess"),
    (1459,"2Thess"),(1462,"1Tim"),(1466,"2Tim"),(1470,"Titus"),(1472,"Phlm"),(1473,"Heb"),(1486,"Jas"),
    (1490,"1Pet"),(1495,"2Pet"),(1498,"1John"),(1503,"2John"),(1504,"Jude"),(1505,"Rev"),
)
_SECTION_BOOKS = {
    "Перша книга Мойсеєва: Буття":"Gen","Друга книга Мойсеєва: Вихід":"Exod","Третя книга Мойсеєва: Левит":"Lev",
    "Четверта книга Мойсеєва: Числа":"Num","П":"Deut","Книга Ісуса Навина (Книга Єгошуї)":"Josh","Книга Суддів":"Judg",
    "Книга Рут":"Ruth","Перша книга Самуїлова (або Перша книга царів)":"1Sam","Друга книга Самуїлова (або Друга книга царів)":"2Sam",
    "Перша книга царів":"1Kgs","Друга книга царів":"2Kgs","Перша книга хроніки":"1Chr","Друга книга хроніки":"2Chr",
    "Книга Ездри":"Ezra","Книга Неемії":"Neh","Книга Естер":"Esth","Книга Йова":"Job","Книга Псалмів":"Ps",
    "Книга приказок Соломонових":"Prov","Книга Екклезіястова (або Проповідника)":"Eccl","Пісня над піснями":"Song",
    "Книга пророка Ісаї":"Isa","Книга пророка Єремії":"Jer","Плач Єремії":"Lam","Книга пророка Єзекіїля":"Ezek",
    "Книга пророка Даниїла":"Dan","Книга пророка Осії":"Hos","Книга пророка Йоіла":"Joel","Книга пророка Амоса":"Amos",
    "Книга пророка Овдія":"Obad","Книга пророка Йони":"Jonah","Книга пророка Михея":"Mic","Книга пророка Наума":"Nah",
    "Книга пророка Авакума":"Hab","Книга пророка Софонії":"Zeph","Книга пророка Огія":"Hag","Книга пророка Захарія":"Zech",
    "Книга пророка Малахії":"Mal","Євангелія від св. Матвія":"Matt","Євангелія від св. Марка":"Mark",
    "Євангелія від св. Івана":"John","Дії святих апостолів":"Acts","Послання св. апостола Павла до римлян":"Rom",
    "Перше послання св. апостола Павла до коринтян":"1Cor","Друге послання св. апостола Павла до коринтян":"2Cor",
    "Послання св. апостола Павла до галатів":"Gal","Послання св. апостола Павла до ефесян":"Eph",
    "Перше послання св. апостола Павла до солунян":"1Thess","Друге послання св. апостола Павла до солунян":"2Thess",
    "Перше послання св. апостола Павла до Тимофія":"1Tim","Друге послання св. апостола до Тимофія":"2Tim",
    "Соборне послання св. апостола Якова":"Jas","Перше соборне послання св. апостола Петра":"1Pet",
    "Друге соборне послання св. апостола Петра":"2Pet","Перше соборне послання св. апостола Івана":"1John",
    "Друге соборне послання св. апостола Івана":"2John","Третє соборне послання св. апостола Івана":"3John",
    "Соборне послання св. апостола Юди":"Jude","Об":"Rev",
}


def _book_for_page(page: int) -> str | None:
    book = None
    for start, candidate in _PAGE_BOOK_STARTS:
        if page < start:
            break
        book = candidate
    return book


def _find_template_end(text: str, start: int) -> int:
    depth = 0
    i = start
    while i < len(text) - 1:
        pair = text[i : i + 2]
        if pair == "{{":
            depth += 1
            i += 2
            continue
        if pair == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return i
            continue
        i += 1
    raise Stage4ParseError(f"Unclosed MediaWiki template at scalar {start}")


def _split_template_args(inner: str) -> list[str]:
    args: list[str] = []
    start = 0
    template_depth = 0
    link_depth = 0
    i = 0
    while i < len(inner):
        pair = inner[i : i + 2]
        if pair == "{{":
            template_depth += 1; i += 2; continue
        if pair == "}}" and template_depth:
            template_depth -= 1; i += 2; continue
        if pair == "[[":
            link_depth += 1; i += 2; continue
        if pair == "]]" and link_depth:
            link_depth -= 1; i += 2; continue
        if inner[i] == "|" and template_depth == 0 and link_depth == 0:
            args.append(inner[start:i]); start = i + 1
        i += 1
    args.append(inner[start:])
    return args


def _template_names(value: str) -> list[str]:
    names: list[str] = []
    i = 0
    while i < len(value):
        start = value.find("{{", i)
        if start < 0:
            break
        end = _find_template_end(value, start)
        inner = value[start + 2 : end - 2]
        parts = _split_template_args(inner)
        if parts:
            names.append(parts[0].strip().casefold())
        names.extend(_template_names(inner))
        i = end
    return names


def _render_wikitext(value: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(value):
        if value.startswith("{{", i):
            end = _find_template_end(value, i)
            parts = _split_template_args(value[i + 2 : end - 2])
            name = parts[0].strip().casefold()
            positional = [part for part in parts[1:] if "=" not in part.split("{{", 1)[0]]
            rendered = ""
            if name in {"anchor", "pline", "dropinitial", "reflist", "rh", "c", "toc line", "toc page listing", "dhr", "rule", "block center s", "block center e", "nop"}:
                rendered = ""
            elif name == "hws" and positional:
                rendered = positional[0]
            elif name == "hwe" and positional:
                rendered = positional[0]
            elif name == "errata" and len(positional) >= 2:
                rendered = positional[1]
            elif name in {"—", "-"}:
                rendered = "—"
            elif positional:
                rendered = positional[-1] if name == "lang" and len(positional) > 1 else positional[0]
            out.append(_render_wikitext(rendered))
            i = end
            continue
        out.append(value[i]); i += 1
    rendered = "".join(out)
    rendered = _NOINCLUDE_RE.sub("", rendered)
    rendered = _INCLUDEONLY_TAG_RE.sub("", rendered)
    rendered = _HTML_TAG_RE.sub("", rendered)
    rendered = _WIKILINK_RE.sub(r"\1", rendered)
    rendered = _EXTERNAL_LINK_RE.sub(r"\1", rendered)
    rendered = rendered.replace("'''", "").replace("''", "")
    return html.unescape(rendered)


def _ref_name(attrs: str) -> str:
    match = _NAME_ATTR_RE.search(attrs)
    if not match:
        return ""
    return next(value for value in match.groups() if value is not None).strip()


def _refs_nested_in_templates(value: str) -> list[tuple[int, int, str, str, bool]]:
    """Return refs hidden inside template arguments without regex-only nesting."""

    found: list[tuple[int, int, str, str, bool]] = []
    depth = 0
    i = 0
    while i < len(value):
        if value.startswith("{{", i):
            depth += 1
            i += 2
            continue
        if value.startswith("}}", i) and depth:
            depth -= 1
            i += 2
            continue
        if depth and value[i : i + 4].casefold() == "<ref":
            self_match = _REF_SELF_RE.match(value, i)
            if self_match:
                found.append((i, self_match.end(), self_match.group(1), "", True))
                i = self_match.end()
                continue
            open_match = _REF_OPEN_RE.match(value, i)
            if open_match:
                close_match = _REF_CLOSE_RE.search(value, open_match.end())
                if close_match is None:
                    raise Stage4ParseError(
                        f"Unclosed ref nested in MediaWiki template at scalar {i}"
                    )
                found.append(
                    (
                        i,
                        close_match.end(),
                        open_match.group(1),
                        value[open_match.end() : close_match.start()],
                        False,
                    )
                )
                i = close_match.end()
                continue
        i += 1
    return found


@dataclass
class _VerseBuilder:
    ref: SourceRef
    first_page: int
    last_page: int
    fragments: list[str] = field(default_factory=list)
    footnotes: list[dict[str, object]] = field(default_factory=list)
    fragment_digests: list[str] = field(default_factory=list)

    @property
    def plain(self) -> str:
        return "".join(self.fragments)


def _parse_verse_marker(name: str, args: Sequence[str], current_chapter: int) -> tuple[int, int] | None:
    if name == "anchor" and args:
        marker = args[0].strip()
        match = re.fullmatch(r"(\d+):(\d+)", marker)
        if match:
            return int(match.group(1)), int(match.group(2))
    if name == "pline":
        named = {part.split("=", 1)[0].strip(): part.split("=", 1)[1].strip() for part in args if "=" in part}
        marker = named.get("id", "")
        match = re.fullmatch(r"(\d+):(\d+)", marker)
        if match:
            return int(match.group(1)), int(match.group(2))
        if args and args[0].strip().isdigit() and current_chapter:
            return current_chapter, int(args[0].strip())
    return None


def parse_wikisource_bundle(
    context: SourceContext,
    *,
    expected_revision_count: int = 1540,
    expected_page_count: int = 1538,
    expected_carriers: Mapping[str, int] | None = None,
) -> ParseResult:
    verify_locked_input(context)
    root = json.loads(context.path.read_text(encoding="utf-8"))
    revisions = root.get("revisions")
    if not isinstance(revisions, list) or len(revisions) != expected_revision_count:
        raise Stage4ParseError(
            "Wikisource revision bundle count changed: "
            f"{len(revisions) if isinstance(revisions, list) else 'invalid'} "
            f"!= {expected_revision_count}"
        )
    result = ParseResult(context.source_id)
    verses: OrderedDict[str, _VerseBuilder] = OrderedDict()
    active: _VerseBuilder | None = None
    active_book: str | None = None
    current_chapter = 0
    footnote_definitions: dict[str, dict[str, object]] = {}
    use_index = 0

    page_revisions: list[tuple[int, Mapping[str, object]]] = []
    for revision in revisions:
        title = str(revision.get("title", ""))
        match = _PAGE_NUMBER_RE.search(title)
        if match:
            page_revisions.append((int(match.group(1)), revision))
        else:
            result.skipped["root_or_index_revision"] += 1
    if len(page_revisions) != expected_page_count:
        raise Stage4ParseError(f"ProofreadPage count changed: {len(page_revisions)}")
    for page, revision in sorted(page_revisions):
        content = str(revision.get("content", ""))
        included = _NOINCLUDE_RE.sub("", content)
        result.counters["proofread_pages"] += 1
        result.counters["raw_carrier_ref_opening"] += len(_REF_OPEN_RE.findall(content))
        result.counters["raw_carrier_ref_closing"] += len(_REF_CLOSE_RE.findall(content))
        result.counters["raw_carrier_ref_self_closing"] += len(_REF_SELF_RE.findall(content))
        result.counters["raw_carrier_reflist"] += len(re.findall(r"{{\s*reflist\b", content, re.I))
        result.counters["raw_carrier_anchor"] += len(re.findall(r"{{\s*anchor\b", content, re.I))
        result.counters["raw_carrier_references_tag"] += len(_REFERENCES_TAG_RE.findall(content))
        for template_name in _template_names(content):
            result.counters[f"template_inventory_{template_name}"] += 1
            if template_name not in _KNOWN_TEMPLATE_NAMES:
                result.warning(
                    "unexpected_mediawiki_template",
                    page=page,
                    template_name=template_name,
                )
        page_default_book = _book_for_page(page)
        mapped_sections = [
            _SECTION_BOOKS.get(next(value for value in match.groups() if value is not None))
            for match in _SECTION_TAG_RE.finditer(included)
        ]
        if active_book is None or (
            page_default_book != active_book and active_book not in mapped_sections
        ):
            active_book = page_default_book
            active = None
            current_chapter = 0
        page_definitions: dict[str, dict[str, object]] = {}
        pending_named_uses: list[dict[str, object]] = []
        cursor = 0
        printed_marker_by_scalar = {
            match.start(): str(order)
            for order, match in enumerate(_REF_OPEN_RE.finditer(included), 1)
        }
        nested_template_refs = _refs_nested_in_templates(included)
        for nested_start, nested_end, attrs, raw_body, self_closing in nested_template_refs:
            name = _ref_name(attrs)
            if self_closing:
                result.counters["raw_ref_self_closing"] += 1
                result.counters["named_ref_uses"] += 1
                result.warning(
                    "heading_self_closing_named_ref_unresolved",
                    page=page,
                    name=name,
                    scalar=nested_start,
                )
                continue
            rendered_body = normalize_source_text(_render_wikitext(raw_body))
            footnote_id = f"{context.source_id}:footnote:{stable_id(page, nested_start, rendered_body)}"
            definition = {
                "footnote_id": footnote_id,
                "name": name or None,
                "full_text_raw": raw_body,
                "full_text_nfc": rendered_body,
                "printed_marker": printed_marker_by_scalar[nested_start],
                "printed_marker_present": True,
                "printed_marker_status": "unambiguous_page_local_ref_ordinal",
                "printed_marker_evidence": {
                    "page": page,
                    "ref_ordinal": int(printed_marker_by_scalar[nested_start]),
                    "carrier": "paired_ref_inside_template",
                },
                "definition_order": result.counters["footnote_definitions"] + 1,
                "source_id": context.source_id,
                "source_revision": str(revision.get("revid", "")),
                "source_page": page,
                "definition_locator": {"page": page, "source_scalar": nested_start},
                "provenance": _record_provenance(
                    context,
                    page=page,
                    revision_id=revision.get("revid"),
                    title=revision.get("title"),
                ),
                "source_fragment_sha256": sha256_text(included[nested_start:nested_end]),
                "definition_status": "defined" if rendered_body else "empty",
            }
            footnote_definitions[footnote_id] = definition
            result.counters["raw_ref_paired"] += 1
            result.counters["footnote_definitions"] += 1
            result.counters["footnote_uses"] += 1
            result.counters["printed_markers_resolved"] += 1
            if name:
                result.counters["named_ref_definitions"] += 1
                result.counters["named_ref_uses"] += 1
            use_index += 1
            footprint = {
                **definition,
                "use_id": f"{context.source_id}:use:{stable_id(page, use_index, nested_start)}",
                "source_order": result.counters["resolved_footnote_uses"] + 1,
                "source_ref": None,
                "anchor_locator": {"page": page, "source_scalar": nested_start, "context": "heading_template"},
                "anchor_start_scalar": None,
                "anchor_end_scalar": None,
                "binding_status": "missing",
                "binding_candidates": [],
                "binding_evidence": ["ref_is_inside_heading_or_service_template"],
                "carrier": "paired_ref_inside_template",
            }
            result.warning(
                "heading_footnote_without_source_verse",
                page=page,
                footnote_id=footnote_id,
            )
            result.records.append(
                make_record(
                    source_id=context.source_id,
                    source_role=context.role,
                    source_version=context.version,
                    source_revision=context.revision,
                    source_order=len(result.records) + 1,
                    source_locator={"page": page, "use_id": footprint["use_id"]},
                    source_kind="unresolved_footnote",
                    source_plain_raw="",
                    footnotes=[footprint],
                    provenance=_record_provenance(
                        context, page=page, revision_id=revision.get("revid")
                    ),
                    classification=["footnote", "heading", "manual_review"],
                    edition_applicable=True,
                )
            )
        while cursor < len(included):
            next_positions = [
                position
                for position in (
                    included.find("{{", cursor),
                    included.lower().find("<ref", cursor),
                    included.lower().find("<section", cursor),
                )
                if position >= 0
            ]
            if not next_positions:
                if active is not None:
                    active.fragments.append(_render_wikitext(included[cursor:]))
                break
            next_pos = min(next_positions)
            if active is not None and next_pos > cursor:
                active.fragments.append(_render_wikitext(included[cursor:next_pos]))
            if included.startswith("{{", next_pos):
                end = _find_template_end(included, next_pos)
                raw_template = included[next_pos:end]
                parts = _split_template_args(raw_template[2:-2])
                name = parts[0].strip().casefold()
                args = parts[1:]
                result.counters[f"template_{name}"] += 1
                marker = _parse_verse_marker(name, args, current_chapter)
                if marker and active_book:
                    current_chapter, verse_number = marker
                    source_ref = SourceRef(active_book, current_chapter, verse_number)
                    active = verses.get(source_ref.label)
                    if active is None:
                        active = _VerseBuilder(source_ref, page, page)
                        verses[source_ref.label] = active
                    active.last_page = page
                    active.fragment_digests.append(sha256_text(raw_template))
                elif name == "anchor" and args:
                    chapter_match = re.fullmatch(r"(\d+):", args[0].strip())
                    if chapter_match:
                        current_chapter = int(chapter_match.group(1))
                elif active is not None:
                    active.fragments.append(_render_wikitext(raw_template))
                if name in {"c", "rh", "larger", "x-larger", "xx-larger", "xxx-larger"}:
                    result.counters["headings"] += 1
                cursor = end
                continue
            section_match = _SECTION_TAG_RE.match(included, next_pos)
            if section_match:
                section = next(value for value in section_match.groups() if value is not None)
                mapped_book = _SECTION_BOOKS.get(section)
                if mapped_book and mapped_book != active_book:
                    active_book = mapped_book
                    active = None
                    current_chapter = 0
                cursor = section_match.end()
                result.counters["section_markers"] += 1
                continue
            section_end_match = _SECTION_END_RE.match(included, next_pos)
            if section_end_match:
                cursor = section_end_match.end()
                result.counters["section_end_markers"] += 1
                continue
            references_match = _REFERENCES_TAG_RE.match(included, next_pos)
            if references_match:
                result.counters["references_carriers"] += 1
                cursor = references_match.end()
                continue
            self_match = _REF_SELF_RE.match(included, next_pos)
            open_match = _REF_OPEN_RE.match(included, next_pos)
            if self_match:
                attrs = self_match.group(1)
                name = _ref_name(attrs)
                use_index += 1
                use = {
                    "use_id": f"{context.source_id}:use:{stable_id(page, use_index, name, next_pos)}",
                    "name": name,
                    "page": page,
                    "source_scalar": next_pos,
                    "verse": active,
                    "anchor_scalar": len(normalize_source_text(active.plain)) if active else None,
                    "carrier": "self_closing_named_ref",
                    "printed_marker": printed_marker_by_scalar[next_pos],
                }
                pending_named_uses.append(use)
                result.counters["raw_ref_self_closing"] += 1
                result.counters["named_ref_uses"] += 1
                cursor = self_match.end()
                continue
            if open_match:
                close_match = _REF_CLOSE_RE.search(included, open_match.end())
                if close_match is None:
                    result.error("unclosed_ref", page=page, scalar=next_pos)
                    cursor = open_match.end()
                    continue
                attrs = open_match.group(1)
                name = _ref_name(attrs)
                raw_body = included[open_match.end() : close_match.start()]
                rendered_body = normalize_source_text(_render_wikitext(raw_body))
                definition_key = f"page:{page}:name:{name}" if name else f"page:{page}:scalar:{next_pos}"
                footnote_id = f"{context.source_id}:footnote:{stable_id(definition_key, rendered_body)}"
                definition = {
                    "footnote_id": footnote_id,
                    "name": name or None,
                    "full_text_raw": raw_body,
                    "full_text_nfc": rendered_body,
                    "printed_marker": printed_marker_by_scalar[next_pos],
                    "printed_marker_present": True,
                    "printed_marker_status": "unambiguous_page_local_ref_ordinal",
                    "printed_marker_evidence": {
                        "page": page,
                        "ref_ordinal": int(printed_marker_by_scalar[next_pos]),
                        "carrier": "paired_ref_definition_and_use",
                    },
                    "definition_order": result.counters["footnote_definitions"] + 1,
                    "source_id": context.source_id,
                    "source_revision": str(revision.get("revid", "")),
                    "source_page": page,
                    "definition_locator": {"page": page, "source_scalar": next_pos},
                    "provenance": _record_provenance(
                        context,
                        page=page,
                        revision_id=revision.get("revid"),
                        title=revision.get("title"),
                    ),
                    "source_fragment_sha256": sha256_text(included[next_pos:close_match.end()]),
                }
                if not rendered_body:
                    definition["definition_status"] = "empty"
                    result.warning("empty_footnote", page=page, footnote_id=footnote_id)
                else:
                    definition["definition_status"] = "defined"
                if name:
                    prior = page_definitions.get(name)
                    if prior and prior["full_text_nfc"] != rendered_body:
                        result.warning(
                            "conflicting_named_ref_definition",
                            page=page,
                            name=name,
                            first_digest=prior["source_fragment_sha256"],
                            second_digest=definition["source_fragment_sha256"],
                        )
                    else:
                        page_definitions[name] = definition
                footnote_definitions[footnote_id] = definition
                use_index += 1
                use = {
                    "use_id": f"{context.source_id}:use:{stable_id(page, use_index, footnote_id, next_pos)}",
                    "name": name,
                    "page": page,
                    "source_scalar": next_pos,
                    "verse": active,
                    "anchor_scalar": len(normalize_source_text(active.plain)) if active else None,
                    "carrier": "paired_ref_definition_and_use",
                    "printed_marker": printed_marker_by_scalar[next_pos],
                    "definition": definition,
                }
                pending_named_uses.append(use)
                result.counters["raw_ref_paired"] += 1
                result.counters["footnote_definitions"] += 1
                result.counters["footnote_uses"] += 1
                result.counters["printed_markers_resolved"] += 1
                if name:
                    result.counters["named_ref_definitions"] += 1
                    result.counters["named_ref_uses"] += 1
                cursor = close_match.end()
                continue
            # Unknown '<ref' or '<section' spelling: consume one scalar and report.
            result.warning("unparsed_mediawiki_carrier", page=page, scalar=next_pos)
            cursor = next_pos + 1
        # Resolve definitions after the page so use-before-definition remains valid.
        for use in pending_named_uses:
            definition = use.get("definition")
            if definition is None and use["name"]:
                definition = page_definitions.get(str(use["name"]))
            verse_builder: _VerseBuilder | None = use["verse"]
            if definition is None:
                result.warning(
                    "undefined_named_ref",
                    page=page,
                    name=use["name"],
                    use_id=use["use_id"],
                )
                footprint = {
                    "footnote_id": None,
                    "use_id": use["use_id"],
                    "full_text_raw": "",
                    "full_text_nfc": "",
                    "printed_marker": use["printed_marker"],
                    "printed_marker_present": True,
                    "printed_marker_status": "unambiguous_page_local_ref_ordinal",
                    "printed_marker_evidence": {
                        "page": page,
                        "ref_ordinal": int(use["printed_marker"]),
                        "carrier": use["carrier"],
                    },
                    "source_order": use_index,
                    "source_id": context.source_id,
                    "source_revision": str(revision.get("revid", "")),
                    "source_page": page,
                    "source_ref": verse_builder.ref.as_dict() if verse_builder else None,
                    "anchor_locator": {"page": page, "source_scalar": use["source_scalar"]},
                    "anchor_start_scalar": use["anchor_scalar"],
                    "anchor_end_scalar": use["anchor_scalar"],
                    "binding_status": "unresolved",
                    "binding_candidates": [verse_builder.ref.as_dict()] if verse_builder else [],
                    "binding_evidence": ["named_ref_definition_missing"],
                    "source_fragment_sha256": sha256_text(str(use["name"])),
                    "carrier": use["carrier"],
                }
            else:
                binding = "unambiguous" if verse_builder is not None else "missing"
                footprint = {
                    **definition,
                    "printed_marker": use["printed_marker"],
                    "printed_marker_present": True,
                    "printed_marker_status": "unambiguous_page_local_ref_ordinal",
                    "printed_marker_evidence": {
                        "page": page,
                        "ref_ordinal": int(use["printed_marker"]),
                        "carrier": use["carrier"],
                    },
                    "use_id": use["use_id"],
                    "source_order": result.counters["resolved_footnote_uses"] + 1,
                    "source_ref": verse_builder.ref.as_dict() if verse_builder else None,
                    "anchor_locator": {"page": page, "source_scalar": use["source_scalar"]},
                    "anchor_start_scalar": use["anchor_scalar"],
                    "anchor_end_scalar": use["anchor_scalar"],
                    "binding_status": binding,
                    "binding_candidates": [verse_builder.ref.as_dict()] if verse_builder else [],
                    "binding_evidence": ["inline_ref_with_active_source_verse"] if verse_builder else ["no_active_source_verse"],
                    "carrier": use["carrier"],
                }
                result.counters["resolved_footnote_uses"] += 1
                if use["carrier"] == "self_closing_named_ref":
                    result.counters["footnote_uses"] += 1
                    result.counters["printed_markers_resolved"] += 1
            if verse_builder is not None:
                verse_builder.footnotes.append(footprint)
            else:
                result.warning(
                    "footnote_without_source_verse",
                    page=page,
                    use_id=use["use_id"],
                    footnote_id=footprint.get("footnote_id"),
                )
                source_order = len(result.records) + 1
                result.records.append(
                    make_record(
                        source_id=context.source_id,
                        source_role=context.role,
                        source_version=context.version,
                        source_revision=context.revision,
                        source_order=source_order,
                        source_locator={"page": page, "use_id": use["use_id"]},
                        source_kind="unresolved_footnote",
                        source_plain_raw="",
                        footnotes=[footprint],
                        provenance=_record_provenance(context, page=page, revision_id=revision.get("revid")),
                        classification=["footnote", "manual_review"],
                        edition_applicable=True,
                    )
                )
        for name, definition in page_definitions.items():
            uses = [use for use in pending_named_uses if use["name"] == name]
            if not uses:
                result.warning(
                    "unused_named_ref_definition",
                    page=page,
                    name=name,
                    footnote_id=definition["footnote_id"],
                )
    verse_records: list[dict[str, object]] = []
    for source_order, builder in enumerate(verses.values(), 1):
        raw_plain = builder.plain
        if not normalize_source_text(raw_plain):
            result.warning("empty_canonical_verse", source_ref=builder.ref.label)
        tokens: list[Token] = []
        for match in re.finditer(r"\S+", normalize_source_text(raw_plain)):
            tokens.append(
                Token(
                    order=len(tokens) + 1,
                    kind="word_or_punctuation",
                    surface_raw=match.group(),
                    start_scalar=match.start(),
                    end_scalar=match.end(),
                )
            )
        verse_records.append(
            make_record(
                source_id=context.source_id,
                source_role=context.role,
                source_version=context.version,
                source_revision=context.revision,
                source_order=source_order,
                source_locator={"page_start": builder.first_page, "page_end": builder.last_page},
                source_kind="canonical_verse",
                source_plain_raw=raw_plain,
                source_ref_raw=builder.ref.label,
                source_ref=builder.ref,
                tokens=tokens,
                footnotes=builder.footnotes,
                provenance=_record_provenance(
                    context,
                    page_start=builder.first_page,
                    page_end=builder.last_page,
                    fragment_digests=builder.fragment_digests,
                ),
                classification=["canonical_text", "wikisource_transcription"],
                edition_applicable=True,
            )
        )
    unresolved_records = [record for record in result.records if record["source_kind"] == "unresolved_footnote"]
    result.records = verse_records + unresolved_records
    for stable_order, record in enumerate(result.records, 1):
        record["source_order"] = stable_order
    result.counters["raw_ref_opening"] = result.counters["raw_ref_paired"] + result.counters["raw_ref_self_closing"]
    result.counters["raw_ref_closing"] = result.counters["raw_ref_paired"]
    result.counters["unique_footnote_definitions"] = len(footnote_definitions)
    statuses = Counter(
        footnote["binding_status"]
        for record in result.records
        for footnote in record.get("footnotes", [])
    )
    for status, count in statuses.items():
        result.counters[f"footnote_binding_{status}"] = count
    result.counters["verses_with_footnotes"] = sum(bool(record.get("footnotes")) for record in verse_records)
    result.counters["verses_with_multiple_footnotes"] = sum(len(record.get("footnotes", [])) > 1 for record in verse_records)
    result.format_details = {
        "family": "MEDIAWIKI_PROOFREADPAGE_JSON",
        "revision_count": expected_revision_count,
        "proofread_page_count": expected_page_count,
        "named_ref_scope": "ProofreadPage page",
        "target_projection_performed": False,
    }
    expected_carriers = expected_carriers or {
        "raw_carrier_ref_opening": 1329,
        "raw_carrier_ref_closing": 1204,
        "raw_carrier_ref_self_closing": 125,
        "raw_carrier_reflist": 735,
        "raw_carrier_anchor": 2201,
    }
    for counter, expected in expected_carriers.items():
        if result.counters[counter] != expected:
            raise Stage4ParseError(
                f"Wikisource carrier inventory changed for {counter}: "
                f"{result.counters[counter]} != {expected}"
            )
    if result.counters["raw_ref_opening"] != result.counters["raw_carrier_ref_opening"]:
        raise Stage4ParseError(
            "Not every Wikisource <ref> carrier was structurally consumed: "
            f"{result.counters['raw_ref_opening']} != "
            f"{result.counters['raw_carrier_ref_opening']}"
        )
    return result.finish()


# DjVu hidden-text parsing ---------------------------------------------------------

_S_EXPR_TOKEN = re.compile(r'\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^\s()]+))', re.S)


def _parse_s_expressions(value: str) -> list[object]:
    stack: list[list[object]] = []
    roots: list[object] = []
    position = 0
    for match in _S_EXPR_TOKEN.finditer(value):
        if value[position:match.start()].strip():
            raise Stage4ParseError(f"Invalid DjVu S-expression at scalar {position}")
        position = match.end()
        if match.group(1):
            node: list[object] = []
            if stack:
                stack[-1].append(node)
            else:
                roots.append(node)
            stack.append(node)
        elif match.group(2):
            if not stack:
                raise Stage4ParseError("Unexpected DjVu S-expression closing parenthesis")
            stack.pop()
        elif match.group(3):
            token = json.loads(match.group(3))
            if not stack:
                roots.append(token)
            else:
                stack[-1].append(token)
        else:
            token = match.group(4)
            try:
                parsed: object = int(token)
            except ValueError:
                parsed = token
            if not stack:
                roots.append(parsed)
            else:
                stack[-1].append(parsed)
    if stack:
        raise Stage4ParseError("Unclosed DjVu S-expression")
    if value[position:].strip():
        raise Stage4ParseError(f"Unconsumed DjVu text at scalar {position}")
    return roots


def _walk_nodes(node: object, kind: str) -> Iterator[list[object]]:
    if isinstance(node, list):
        if node and node[0] == kind:
            yield node
        for child in node:
            yield from _walk_nodes(child, kind)


def _djvu_logical_container(path: Path, *, work_dir: Path, source_id: str) -> tuple[Path, dict[str, object]]:
    payload = path.read_bytes()
    if len(payload) < 16 or payload[:4] != b"AT&T":
        raise Stage4ParseError(f"{source_id} is not an AT&T DjVu container")
    offset = 4
    containers: list[bytes] = []
    while offset + 12 <= len(payload):
        if payload[offset : offset + 4] != b"FORM":
            raise Stage4ParseError(f"Unexpected DjVu container boundary at {offset}")
        length = int.from_bytes(payload[offset + 4 : offset + 8], "big")
        # Top-level DjVu FORM chunks in these locked files have no trailing IFF
        # pad byte; the next concatenated AT&T header starts immediately.
        total = 8 + length
        containers.append(payload[offset : offset + total])
        offset += total
        if offset < len(payload) and payload[offset : offset + 4] == b"AT&T":
            offset += 4
    if offset != len(payload):
        raise Stage4ParseError(f"Unconsumed DjVu container bytes: {len(payload) - offset}")
    details = {
        "physical_container_count": len(containers),
        "physical_container_sha256": [sha256_bytes(container) for container in containers],
        "duplicate_containers": len(containers) > 1 and len({sha256_bytes(c) for c in containers}) == 1,
    }
    if len(containers) == 1:
        return path, details
    if not details["duplicate_containers"]:
        raise Stage4ParseError("Multiple non-identical DjVu containers require explicit handling")
    work_dir.mkdir(parents=True, exist_ok=True)
    logical_path = work_dir / f"_{source_id}_logical_container.djvu"
    logical_path.write_bytes(b"AT&T" + containers[0])
    details["logical_container_path"] = str(logical_path)
    details["logical_container_sha256"] = sha256_bytes(logical_path.read_bytes())
    return logical_path, details


def parse_djvu_hidden_text(
    context: SourceContext,
    *,
    djvutxt_path: Path,
    work_dir: Path,
) -> ParseResult:
    verify_locked_input(context)
    if not djvutxt_path.is_file():
        raise Stage4ParseError(f"djvutxt is unavailable: {djvutxt_path}")
    logical_path, container_details = _djvu_logical_container(
        context.path, work_dir=work_dir, source_id=context.source_id
    )
    process = subprocess.run(
        [str(djvutxt_path), "-page=1-1538", "-detail=line", str(logical_path)],
        check=False,
        capture_output=True,
        timeout=300,
    )
    if process.returncode != 0:
        raise Stage4ParseError(
            f"djvutxt failed for {context.source_id}: "
            f"{process.stderr.decode('utf-8', errors='replace')[:400]}"
        )
    text = process.stdout.decode("utf-8")
    roots = _parse_s_expressions(text)
    if len(roots) != 1538:
        raise Stage4ParseError(f"DjVu logical page count changed: {len(roots)}")
    result = ParseResult(context.source_id)
    if container_details["duplicate_containers"]:
        result.warning("duplicate_physical_djvu_container", **container_details)
    for page_number, root_node in enumerate(roots, 1):
        page_node = (
            root_node
            if isinstance(root_node, list) and root_node and root_node[0] == "page"
            else ["page", 0, 0, 0, 0]
        )
        lines: list[dict[str, object]] = []
        for line_order, line_node in enumerate(_walk_nodes(page_node, "line"), 1):
            if len(line_node) < 6:
                raise Stage4ParseError(f"Malformed DjVu line on page {page_number}")
            coords = [int(value) for value in line_node[1:5]]
            content = "".join(str(value) for value in line_node[5:] if isinstance(value, str))
            lines.append({"order": line_order, "bbox": coords, "text": content})
        page_text = "\n".join(str(line["text"]) for line in lines)
        page_height = int(page_node[4]) if len(page_node) > 4 and isinstance(page_node[4], int) else 0
        footnote_candidates = [
            line
            for line in lines
            if page_height and int(line["bbox"][3]) < max(850, int(page_height * 0.25))
            and re.search(r"(?:^|\s)(?:\d+|[*†‡•])\s+\D", str(line["text"]))
        ]
        tokens = [
            Token(
                order=index,
                kind="ocr_line",
                surface_raw=str(line["text"]),
                extra={"bbox": line["bbox"], "line_order": line["order"]},
            )
            for index, line in enumerate(lines, 1)
        ]
        result.records.append(
            make_record(
                source_id=context.source_id,
                source_role=context.role,
                source_version=context.version,
                source_revision=context.revision,
                source_order=page_number,
                source_locator={"page": page_number},
                source_kind="print_page_ocr",
                source_plain_raw=page_text,
                tokens=tokens,
                provenance=_record_provenance(
                    context,
                    page=page_number,
                    logical_container_sha256=container_details.get("logical_container_sha256", context.expected_sha256),
                ),
                classification=["print_scan", "ocr", "source_comment_candidate"]
                if footnote_candidates
                else ["print_scan", "ocr"],
                extra={
                    "page_bbox": page_node[1:5],
                    "line_count": len(lines),
                    "footnote_candidate_line_count": len(footnote_candidates),
                    "footnote_candidate_digests": [sha256_text(str(line["text"])) for line in footnote_candidates],
                },
                edition_applicable=True,
            )
        )
        result.counters["ocr_lines"] += len(lines)
        result.counters["source_comment_candidates"] += len(footnote_candidates)
        if not lines:
            result.counters["pages_without_hidden_text"] += 1
    result.format_details = {
        "family": "DJVU_HIDDEN_TEXT_S_EXPRESSION",
        "djvutxt_path": str(djvutxt_path),
        "djvutxt_sha256": sha256_bytes(djvutxt_path.read_bytes()),
        **container_details,
        "logical_page_count": 1538,
    }
    return result.finish()

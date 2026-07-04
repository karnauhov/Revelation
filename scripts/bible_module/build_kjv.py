from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .canon import CANON_NAME, CANONICAL_BOOKS, CanonicalVerse, canonical_verses
from .schema import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    DB_METADATA_SCHEMA_VERSION_KEY,
    now_utc_iso,
)

MODULE_ID = "kjv"
MODULE_CODE = "KJV"
MODULE_TITLE = "King James Version (1769)"
DEFAULT_TARGET_PATH = Path.home() / "Documents" / "revelation" / "db" / "bible_kjv.sqlite"
DEFAULT_SOURCE_ZIP_PATH = Path(__file__).resolve().parent / "source_cache" / "eng-kjv2006_usfx.zip"
SOURCE_ZIP_MEMBER = "eng-kjv2006_usfx.xml"

KJV_SCHEMA_VERSION = 3
KJV_DATA_VERSION_INITIAL = 1
KJV_SOURCE_URL = "https://ebible.org/Scriptures/eng-kjv2006_usfx.zip"
KJV_SOURCE_PAGE_URL = "https://ebible.org/find/show.php?id=eng-kjv2006"
KJV_SOURCE_VERSION = "eBible eng-kjv2006, last updated 2026-05-16"
KJV_LICENSE_SUMMARY = (
    "Public Domain outside the United Kingdom; UK Crown Letters Patent "
    "restrictions apply to printing, publishing, and importing the Authorized "
    "Version in the UK. CrossWire/eBible KJV text is provided for free use."
)
KJV_SOURCE_SUMMARY = (
    "KJV 1769 protocanon text from eBible eng-kjv2006 USFX, courtesy of "
    "CrossWire Bible Society and eBible.org. Strong's numbers are retained as "
    "inline H/G tokens compatible with the Bible reader; morphology, footnotes, "
    "and study notes are omitted. Canonical Psalm descriptors are merged into "
    "Psalm verse 1 text. The eBible 2CH.14.1-15 boundary is projected to the "
    "app canon as 2Chr.13.23 and 2Chr.14.1-14."
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS db_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS info (
  code TEXT PRIMARY KEY,
  module_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  language TEXT NOT NULL,
  canon TEXT NOT NULL,
  versification TEXT NOT NULL,
  license TEXT NOT NULL,
  source_summary TEXT NOT NULL,
  CHECK (length(trim(code)) > 0),
  CHECK (length(trim(module_id)) > 0)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS verses (
  verse_key TEXT PRIMARY KEY,
  text TEXT NOT NULL DEFAULT '',
  CHECK (length(trim(verse_key)) = 3)
) WITHOUT ROWID;
"""

USFX_BOOK_CODES_BY_CANONICAL_CODE: Mapping[str, str] = {
    "Gen": "GEN",
    "Exod": "EXO",
    "Lev": "LEV",
    "Num": "NUM",
    "Deut": "DEU",
    "Josh": "JOS",
    "Judg": "JDG",
    "Ruth": "RUT",
    "1Sam": "1SA",
    "2Sam": "2SA",
    "1Kgs": "1KI",
    "2Kgs": "2KI",
    "1Chr": "1CH",
    "2Chr": "2CH",
    "Ezra": "EZR",
    "Neh": "NEH",
    "Esth": "EST",
    "Job": "JOB",
    "Ps": "PSA",
    "Prov": "PRO",
    "Eccl": "ECC",
    "Song": "SNG",
    "Isa": "ISA",
    "Jer": "JER",
    "Lam": "LAM",
    "Ezek": "EZK",
    "Dan": "DAN",
    "Hos": "HOS",
    "Joel": "JOL",
    "Amos": "AMO",
    "Obad": "OBA",
    "Jonah": "JON",
    "Mic": "MIC",
    "Nah": "NAM",
    "Hab": "HAB",
    "Zeph": "ZEP",
    "Hag": "HAG",
    "Zech": "ZEC",
    "Mal": "MAL",
    "Mat": "MAT",
    "Mark": "MRK",
    "Luke": "LUK",
    "John": "JHN",
    "Acts": "ACT",
    "Rom": "ROM",
    "1Cor": "1CO",
    "2Cor": "2CO",
    "Gal": "GAL",
    "Eph": "EPH",
    "Phil": "PHP",
    "Col": "COL",
    "1Thess": "1TH",
    "2Thess": "2TH",
    "1Tim": "1TI",
    "2Tim": "2TI",
    "Titus": "TIT",
    "Phlm": "PHM",
    "Heb": "HEB",
    "Jas": "JAS",
    "1Pet": "1PE",
    "2Pet": "2PE",
    "1John": "1JN",
    "2John": "2JN",
    "3John": "3JN",
    "Jude": "JUD",
    "Rev": "REV",
}
CANONICAL_CODE_BY_USFX_BOOK_CODE = {
    usfx_code: canonical_code
    for canonical_code, usfx_code in USFX_BOOK_CODES_BY_CANONICAL_CODE.items()
}
USFX_REF_OVERRIDES = {
    "2CH.14.1": "2Chr.13.23",
    **{f"2CH.14.{verse}": f"2Chr.14.{verse - 1}" for verse in range(2, 16)},
}

_BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_WHITESPACE_PATTERN = re.compile(r"\s+")
_PARAGRAPH_MARK = "\u00b6"
_STRONG_ATTR_PATTERN = re.compile(r"\s+")
_STRONG_TOKEN_PATTERN = re.compile(r"^[GH]\d+$", re.IGNORECASE)
_LEADING_PUNCTUATION_PATTERN = re.compile(
    r"^([,.;:?!\)\]\}\"'\u2013\u2014\u201d\u2019]+)(.*)$",
    re.DOTALL,
)
_TRAILING_STRONG_PUNCTUATION_PATTERN = re.compile(
    r"\s+((?:[GH]\d+\s*)+)([,.;:?!\)\]\}\"'\u2013\u2014\u201d\u2019]+)",
    re.IGNORECASE,
)
_WORD_SUFFIX_PATTERN = re.compile(r"^([A-Za-z0-9]+)(.*)$", re.DOTALL)
_WORD_CONNECTOR_PATTERN = re.compile(r"^[-'\u2019]+$")
_FOOTNOTE_TAGS = {"f", "x"}
_PSALM_DESCRIPTOR_TAGS = {"d"}


@dataclass(frozen=True)
class KjvBuildReport:
    target_path: Path
    backup_path: Path | None
    source_path: Path
    source_sha256: str
    source_size_bytes: int
    verses_count: int
    filled_verses_count: int
    empty_verses_count: int
    strong_tokens_count: int
    verses_with_strong_numbers_count: int
    books_count: int
    chapters_count: int
    built_at: str


@dataclass(frozen=True)
class KjvValidationReport:
    verses_count: int
    filled_verses_count: int
    empty_verses_count: int
    missing_refs: tuple[str, ...]
    extra_refs: tuple[str, ...]
    duplicate_refs: tuple[str, ...]


def build_kjv_module(
    *,
    target_path: Path = DEFAULT_TARGET_PATH,
    source_zip_path: Path = DEFAULT_SOURCE_ZIP_PATH,
    data_version: int = KJV_DATA_VERSION_INITIAL,
    built_at: str | None = None,
) -> KjvBuildReport:
    target_path = target_path.resolve()
    source_zip_path = source_zip_path.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    actual_built_at = built_at or now_utc_iso()
    timestamp = _filesystem_timestamp(actual_built_at)
    temp_path = _new_temp_db_path(target_path)
    backup_path: Path | None = None

    source_bytes = source_zip_path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    source_text = read_usfx_xml_from_zip(source_zip_path)
    verse_texts = extract_kjv_verse_texts(source_text)
    validate_kjv_source_texts(verse_texts)
    strong_tokens_count = _strong_tokens_count(verse_texts.values())
    verses_with_strong_numbers_count = _verses_with_strong_numbers_count(
        verse_texts.values()
    )

    try:
        connection = sqlite3.connect(str(temp_path))
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN")
            create_kjv_schema(
                connection,
                data_version=data_version,
                date_iso=actual_built_at,
            )
            _apply_verse_texts(connection, verse_texts)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        _vacuum_database(temp_path)
        validate_kjv_database(temp_path)
        if target_path.exists():
            backup_path = target_path.with_name(f"{target_path.name}.{timestamp}.bak")
            shutil.copy2(target_path, backup_path)
        temp_path.replace(target_path)
        validate_kjv_database(target_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return KjvBuildReport(
        target_path=target_path,
        backup_path=backup_path,
        source_path=source_zip_path,
        source_sha256=source_sha256,
        source_size_bytes=len(source_bytes),
        verses_count=len(canonical_verses()),
        filled_verses_count=len(verse_texts),
        empty_verses_count=0,
        strong_tokens_count=strong_tokens_count,
        verses_with_strong_numbers_count=verses_with_strong_numbers_count,
        books_count=len(CANONICAL_BOOKS),
        chapters_count=sum(len(book.chapter_verse_counts) for book in CANONICAL_BOOKS),
        built_at=actual_built_at,
    )


def read_usfx_xml_from_zip(source_zip_path: Path) -> str:
    if not source_zip_path.exists():
        raise FileNotFoundError(f"KJV source ZIP not found: {source_zip_path}")
    with zipfile.ZipFile(source_zip_path) as archive:
        try:
            raw = archive.read(SOURCE_ZIP_MEMBER)
        except KeyError as error:
            raise ValueError(
                f"KJV source ZIP is missing {SOURCE_ZIP_MEMBER}: {source_zip_path}"
            ) from error
    return raw.decode("utf-8-sig")


def extract_kjv_verse_texts(usfx_xml: str) -> dict[str, str]:
    root = ET.fromstring(usfx_xml)
    extractor = _UsfxVerseExtractor()
    extractor.walk(root)
    return extractor.verse_texts


def validate_kjv_source_texts(verse_texts: Mapping[str, str]) -> KjvValidationReport:
    expected_refs = {canonical_verse.osis_ref for canonical_verse in canonical_verses()}
    actual_refs = set(verse_texts)
    missing_refs = tuple(
        verse.osis_ref for verse in canonical_verses() if verse.osis_ref not in actual_refs
    )
    extra_refs = tuple(sorted(actual_refs - expected_refs))
    empty_refs = tuple(
        ref for ref, text in sorted(verse_texts.items()) if not plain_kjv_text(text)
    )
    duplicate_refs = ()
    padded_strong_refs = tuple(
        ref
        for ref, text in sorted(verse_texts.items())
        if re.search(r"\b[GH]0\d+\b", text)
    )

    if missing_refs or extra_refs or empty_refs or padded_strong_refs:
        details = {
            "missing_refs": missing_refs,
            "extra_refs": extra_refs,
            "empty_refs": empty_refs,
            "padded_strong_refs": padded_strong_refs,
        }
        raise ValueError(f"KJV source does not match the canonical verse map: {details}")

    return KjvValidationReport(
        verses_count=len(expected_refs),
        filled_verses_count=len(verse_texts),
        empty_verses_count=0,
        missing_refs=missing_refs,
        extra_refs=extra_refs,
        duplicate_refs=duplicate_refs,
    )


def create_kjv_schema(
    connection: sqlite3.Connection,
    *,
    data_version: int,
    date_iso: str,
) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA user_version = {KJV_SCHEMA_VERSION}")
    connection.executescript(SCHEMA_SQL)
    connection.executemany(
        """
        INSERT INTO db_metadata(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        [
            (DB_METADATA_SCHEMA_VERSION_KEY, str(KJV_SCHEMA_VERSION)),
            (DB_METADATA_DATA_VERSION_KEY, str(data_version)),
            (DB_METADATA_DATE_KEY, date_iso),
        ],
    )
    connection.execute(
        """
        INSERT INTO info(
          code,
          module_id,
          title,
          description,
          language,
          canon,
          versification,
          license,
          source_summary
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            MODULE_CODE,
            MODULE_ID,
            MODULE_TITLE,
            (
                "King James Version Bible module with inline Strong's numbers "
                "built from the eBible/CrossWire eng-kjv2006 USFX source."
            ),
            "en",
            CANON_NAME,
            "kjv_protestant",
            KJV_LICENSE_SUMMARY,
            KJV_SOURCE_SUMMARY,
        ),
    )
    connection.executemany(
        """
        INSERT INTO verses(verse_key, text)
        VALUES(?, '')
        """,
        [(verse_key_for(canonical_verse),) for canonical_verse in canonical_verses()],
    )


def validate_kjv_database(db_path: Path) -> KjvValidationReport:
    connection = sqlite3.connect(str(db_path))
    try:
        expected_tables = {"db_metadata", "info", "verses"}
        actual_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if actual_tables != expected_tables:
            raise ValueError(f"KJV table mismatch: {sorted(actual_tables)}")

        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if user_version != KJV_SCHEMA_VERSION:
            raise ValueError("KJV PRAGMA user_version mismatch")

        metadata = dict(connection.execute("SELECT key, value FROM db_metadata"))
        if metadata.get(DB_METADATA_SCHEMA_VERSION_KEY) != str(KJV_SCHEMA_VERSION):
            raise ValueError("KJV db_metadata.schema_version mismatch")

        info_count = int(connection.execute("SELECT COUNT(*) FROM info").fetchone()[0])
        if info_count != 1:
            raise ValueError("KJV info table must contain exactly one row")

        rows = connection.execute("SELECT verse_key, text FROM verses").fetchall()
        expected_count = len(canonical_verses())
        if len(rows) != expected_count:
            raise ValueError(f"KJV verse count mismatch: {len(rows)} != {expected_count}")

        expected_keys = {verse_key_for(verse) for verse in canonical_verses()}
        actual_keys = {str(row[0]) for row in rows}
        missing_keys = expected_keys - actual_keys
        extra_keys = actual_keys - expected_keys
        empty_keys = {str(row[0]) for row in rows if not plain_kjv_text(str(row[1]))}
        padded_strong_keys = {
            str(row[0]) for row in rows if re.search(r"\b[GH]0\d+\b", str(row[1]))
        }
        if missing_keys or extra_keys or empty_keys or padded_strong_keys:
            raise ValueError(
                "KJV database verses do not match canonical keys: "
                f"missing={sorted(missing_keys)[:10]} "
                f"extra={sorted(extra_keys)[:10]} "
                f"empty={sorted(empty_keys)[:10]} "
                f"padded_strong={sorted(padded_strong_keys)[:10]}"
            )

        verse_texts = _read_database_osis_texts(connection)
        return validate_kjv_source_texts(verse_texts)
    finally:
        connection.close()


def build_book_chapter_statistics(verse_texts: Mapping[str, str] | None = None) -> list[dict[str, object]]:
    text_lengths = _text_lengths_by_osis_ref(verse_texts or {})
    strong_counts = _strong_counts_by_osis_ref(verse_texts or {})
    stats: list[dict[str, object]] = []
    for book in CANONICAL_BOOKS:
        chapters: list[dict[str, int]] = []
        book_verse_count = 0
        book_word_count = 0
        book_strong_count = 0
        for chapter_index, verse_count in enumerate(book.chapter_verse_counts, start=1):
            chapter_refs = [
                f"{book.osis_code}.{chapter_index}.{verse}"
                for verse in range(1, verse_count + 1)
            ]
            chapter_word_count = sum(text_lengths.get(ref, 0) for ref in chapter_refs)
            chapter_strong_count = sum(strong_counts.get(ref, 0) for ref in chapter_refs)
            chapters.append(
                {
                    "chapter": chapter_index,
                    "verses": verse_count,
                    "words": chapter_word_count,
                    "strong_tokens": chapter_strong_count,
                }
            )
            book_verse_count += verse_count
            book_word_count += chapter_word_count
            book_strong_count += chapter_strong_count
        stats.append(
            {
                "book_id": book.book_id,
                "code": book.canonical_code,
                "osis_code": book.osis_code,
                "title": book.title,
                "chapters_count": len(book.chapter_verse_counts),
                "verses_count": book_verse_count,
                "words_count": book_word_count,
                "strong_tokens_count": book_strong_count,
                "chapters": chapters,
            }
        )
    return stats


def _read_database_osis_texts(connection: sqlite3.Connection) -> dict[str, str]:
    verse_by_key = {
        str(row[0]): str(row[1])
        for row in connection.execute("SELECT verse_key, text FROM verses")
    }
    return {
        canonical_verse.osis_ref: verse_by_key[verse_key_for(canonical_verse)]
        for canonical_verse in canonical_verses()
    }


def _apply_verse_texts(
    connection: sqlite3.Connection,
    verse_texts_by_ref: Mapping[str, str],
) -> None:
    canonical_by_ref = {verse.osis_ref: verse for verse in canonical_verses()}
    rows = []
    for osis_ref, text in sorted(
        verse_texts_by_ref.items(),
        key=lambda item: canonical_by_ref[item[0]].sort_key,
    ):
        rows.append((text, verse_key_for(canonical_by_ref[osis_ref])))
    connection.executemany(
        """
        UPDATE verses
        SET text = ?
        WHERE verse_key = ?
        """,
        rows,
    )


def verse_key_for(canonical_verse: CanonicalVerse) -> str:
    key_by_id = _verse_keys_by_id()
    return key_by_id[canonical_verse.canonical_verse_id]


@lru_cache(maxsize=1)
def _verse_keys_by_id() -> dict[int, str]:
    verses = canonical_verses()
    if len(verses) > 36**3:
        raise ValueError("Three-character base36 verse_key cannot fit the canon")
    return {
        canonical_verse.canonical_verse_id: _base36(index).rjust(3, "0")
        for index, canonical_verse in enumerate(verses, start=1)
    }


class _UsfxVerseExtractor:
    def __init__(self) -> None:
        self.verse_texts: dict[str, str] = {}
        self._current_ref: str | None = None
        self._current_parts: list[str] = []
        self._pending_descriptors: list[str] = []
        self._seen_refs: Counter[str] = Counter()

    def walk(self, element: ET.Element) -> None:
        tag = _local_name(element.tag)
        if tag in _FOOTNOTE_TAGS:
            return

        if tag in _PSALM_DESCRIPTOR_TAGS and self._current_ref is None:
            descriptor = _normalize_kjv_display_text(_element_text_with_strongs(element))
            if descriptor:
                self._pending_descriptors.append(descriptor)
            return

        if tag == "v":
            self._start_verse(element)
            return

        if tag == "ve":
            self._end_verse()
            return

        if self._current_ref is not None and element.text:
            self._current_parts.append(element.text)

        children = list(element)
        child_index = 0
        while child_index < len(children):
            child = children[child_index]
            if self._current_ref is not None and _local_name(child.tag) == "w":
                cluster, child_index = _collect_word_cluster(
                    children,
                    child_index,
                )
                _append_word_cluster_with_strongs(
                    cluster,
                    self._current_parts,
                )
                continue

            self.walk(child)
            if self._current_ref is not None and child.tail:
                self._current_parts.append(child.tail)
            child_index += 1

    def _start_verse(self, element: ET.Element) -> None:
        raw_ref = element.attrib.get("bcv", "").strip()
        if not raw_ref:
            raise ValueError("USFX verse start is missing bcv")
        self._current_ref = _usfx_ref_to_osis_ref(raw_ref)
        self._seen_refs[self._current_ref] += 1
        if self._seen_refs[self._current_ref] > 1:
            raise ValueError(f"Duplicate KJV source verse: {self._current_ref}")
        self._current_parts = []
        if self._pending_descriptors:
            self._current_parts.append(
                " ".join(descriptor for descriptor in self._pending_descriptors if descriptor)
            )
            self._current_parts.append(" ")
            self._pending_descriptors = []
        if element.text:
            self._current_parts.append(element.text)

    def _end_verse(self) -> None:
        if self._current_ref is None:
            raise ValueError("USFX verse end encountered without an open verse")
        self.verse_texts[self._current_ref] = _normalize_kjv_display_text(
            "".join(self._current_parts)
        )
        self._current_ref = None
        self._current_parts = []


def _element_text(element: ET.Element) -> str:
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in list(element):
        if _local_name(child.tag) not in _FOOTNOTE_TAGS:
            parts.append(_element_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def _element_text_with_strongs(element: ET.Element) -> str:
    parts: list[str] = []
    _append_element_text_with_strongs(element, parts)
    return "".join(parts)


def _append_element_text_with_strongs(
    element: ET.Element,
    parts: list[str],
) -> None:
    tag = _local_name(element.tag)
    if tag in _FOOTNOTE_TAGS:
        return
    if tag == "w":
        _append_word_with_strongs(element, parts, tail="")
        return

    if element.text:
        parts.append(element.text)
    children = list(element)
    child_index = 0
    while child_index < len(children):
        child = children[child_index]
        if _local_name(child.tag) == "w":
            cluster, child_index = _collect_word_cluster(children, child_index)
            _append_word_cluster_with_strongs(
                cluster,
                parts,
            )
            continue
        _append_element_text_with_strongs(child, parts)
        if child.tail:
            parts.append(child.tail)
        child_index += 1


@dataclass(frozen=True)
class _WordCluster:
    surface: str
    strong_tokens: tuple[str, ...]
    tail: str


def _collect_word_cluster(
    children: list[ET.Element],
    start_index: int,
) -> tuple[_WordCluster, int]:
    surface_parts: list[str] = []
    strong_tokens: list[str] = []
    child_index = start_index
    while child_index < len(children):
        child = children[child_index]
        surface_parts.append(_normalize_text(_element_text(child)))
        strong_tokens.extend(_strong_tokens_for_word(child))
        tail = child.tail or ""
        next_is_word = (
            child_index + 1 < len(children)
            and _local_name(children[child_index + 1].tag) == "w"
        )

        if not tail and next_is_word:
            child_index += 1
            continue

        if next_is_word and _WORD_CONNECTOR_PATTERN.fullmatch(tail):
            surface_parts.append(tail)
            child_index += 1
            continue

        suffix, remaining_tail = _split_leading_word_suffix(tail)
        surface_parts.append(suffix)
        return (
            _WordCluster(
                surface="".join(surface_parts),
                strong_tokens=tuple(strong_tokens),
                tail=remaining_tail,
            ),
            child_index + 1,
        )

    return (
        _WordCluster(
            surface="".join(surface_parts),
            strong_tokens=tuple(strong_tokens),
            tail="",
        ),
        child_index,
    )


def _append_word_with_strongs(
    element: ET.Element,
    parts: list[str],
    *,
    tail: str,
) -> None:
    suffix, remaining_tail = _split_leading_word_suffix(tail)
    _append_word_cluster_with_strongs(
        _WordCluster(
            surface=_normalize_text(_element_text(element)) + suffix,
            strong_tokens=_strong_tokens_for_word(element),
            tail=remaining_tail,
        ),
        parts,
    )


def _append_word_cluster_with_strongs(
    cluster: _WordCluster,
    parts: list[str],
) -> None:
    surface = cluster.surface
    leading_punctuation, remaining_tail = _split_leading_punctuation(cluster.tail)
    if surface:
        parts.append(surface + leading_punctuation)
        if cluster.strong_tokens:
            parts.append(" ")
            parts.append(" ".join(cluster.strong_tokens))
            parts.append(" ")
    elif leading_punctuation:
        parts.append(leading_punctuation)
    if remaining_tail:
        parts.append(remaining_tail)


def _split_leading_punctuation(text: str) -> tuple[str, str]:
    match = _LEADING_PUNCTUATION_PATTERN.match(text)
    if match is None:
        return "", text
    return match.group(1), match.group(2)


def _split_leading_word_suffix(text: str) -> tuple[str, str]:
    match = _WORD_SUFFIX_PATTERN.match(text)
    if match is None:
        return "", text
    suffix = match.group(1)
    leading_punctuation, remaining_tail = _split_leading_punctuation(match.group(2))
    return suffix + leading_punctuation, remaining_tail


def _strong_tokens_for_word(element: ET.Element) -> tuple[str, ...]:
    raw_value = element.attrib.get("s", "").strip()
    if not raw_value:
        return ()
    return tuple(_normalize_strong(raw) for raw in _STRONG_ATTR_PATTERN.split(raw_value) if raw)


def _normalize_strong(raw_strong: str) -> str:
    value = raw_strong.strip().upper()
    match = re.fullmatch(r"([GH])0*(\d+)", value)
    if match is None:
        raise ValueError(f"Invalid KJV Strong key: {raw_strong}")
    return f"{match.group(1)}{int(match.group(2))}"


def _usfx_ref_to_osis_ref(usfx_ref: str) -> str:
    override = USFX_REF_OVERRIDES.get(usfx_ref)
    if override is not None:
        return override
    parts = usfx_ref.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid USFX bcv reference: {usfx_ref}")
    book_code = CANONICAL_CODE_BY_USFX_BOOK_CODE.get(parts[0])
    if book_code is None:
        raise ValueError(f"Unsupported KJV source book: {parts[0]}")
    book = next(book for book in CANONICAL_BOOKS if book.canonical_code == book_code)
    return f"{book.osis_code}.{int(parts[1])}.{int(parts[2])}"


def _text_lengths_by_osis_ref(verse_texts: Mapping[str, str]) -> dict[str, int]:
    return {
        osis_ref: len(_word_tokens(plain_kjv_text(text)))
        for osis_ref, text in verse_texts.items()
    }


def _strong_counts_by_osis_ref(verse_texts: Mapping[str, str]) -> dict[str, int]:
    return {
        osis_ref: _strong_tokens_count((text,))
        for osis_ref, text in verse_texts.items()
    }


def plain_kjv_text(text: str) -> str:
    return " ".join(
        token
        for token in _normalize_text(text).split(" ")
        if token and _STRONG_TOKEN_PATTERN.fullmatch(token) is None
    ).strip()


def _strong_tokens_count(texts: Iterable[str]) -> int:
    return sum(
        1
        for text in texts
        for token in _normalize_text(text).split(" ")
        if _STRONG_TOKEN_PATTERN.fullmatch(token) is not None
    )


def _verses_with_strong_numbers_count(texts: Iterable[str]) -> int:
    return sum(
        1
        for text in texts
        if any(
            _STRONG_TOKEN_PATTERN.fullmatch(token) is not None
            for token in _normalize_text(text).split(" ")
        )
    )


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[\'\u2019-][A-Za-z0-9]+)*", text)


def _normalize_text(text: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def _normalize_kjv_display_text(text: str) -> str:
    return _normalize_text(
        _move_wrapped_punctuation_before_strongs(
            text.replace(_PARAGRAPH_MARK, " "),
        )
    )


def _move_wrapped_punctuation_before_strongs(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        strongs = " ".join(match.group(1).split())
        return f"{match.group(2)} {strongs}"

    return _TRAILING_STRONG_PUNCTUATION_PATTERN.sub(replace, text)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _base36(number: int) -> str:
    if number <= 0:
        raise ValueError(f"base36 requires a positive integer, got {number}")
    value = number
    characters: list[str] = []
    while value:
        value, remainder = divmod(value, 36)
        characters.append(_BASE36_ALPHABET[remainder])
    return "".join(reversed(characters))


def _new_temp_db_path(target_path: Path) -> Path:
    temp_file = tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(target_path.parent),
        prefix=f".{target_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_file.name)
    temp_file.close()
    temp_path.unlink(missing_ok=True)
    return temp_path


def _vacuum_database(db_path: Path) -> None:
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute("VACUUM")
        connection.execute("PRAGMA optimize")
    finally:
        connection.close()


def _filesystem_timestamp(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the simplified KJV SQLite Bible module from eBible USFX.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET_PATH,
        help="Output bible_kjv.sqlite path.",
    )
    parser.add_argument(
        "--source-zip",
        type=Path,
        default=DEFAULT_SOURCE_ZIP_PATH,
        help="Source eng-kjv2006_usfx.zip path.",
    )
    parser.add_argument(
        "--data-version",
        type=int,
        default=KJV_DATA_VERSION_INITIAL,
        help="db_metadata.data_version value.",
    )
    parser.add_argument(
        "--stats-json",
        type=Path,
        default=None,
        help="Optional path to write book/chapter statistics JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_kjv_module(
        target_path=args.target,
        source_zip_path=args.source_zip,
        data_version=args.data_version,
    )
    source_text = read_usfx_xml_from_zip(args.source_zip)
    verse_texts = extract_kjv_verse_texts(source_text)
    stats = build_book_chapter_statistics(verse_texts)
    if args.stats_json is not None:
        args.stats_json.parent.mkdir(parents=True, exist_ok=True)
        args.stats_json.write_text(
            json.dumps(
                {
                    "source": {
                        "url": KJV_SOURCE_URL,
                        "page_url": KJV_SOURCE_PAGE_URL,
                        "version": KJV_SOURCE_VERSION,
                        "sha256": report.source_sha256,
                        "bytes": report.source_size_bytes,
                    },
                    "built_at": report.built_at,
                    "totals": {
                        "books": report.books_count,
                        "chapters": report.chapters_count,
                        "verses": report.verses_count,
                        "filled_verses": report.filled_verses_count,
                        "empty_verses": report.empty_verses_count,
                        "verses_with_strong_numbers": report.verses_with_strong_numbers_count,
                        "verses_without_strong_numbers": (
                            report.verses_count
                            - report.verses_with_strong_numbers_count
                        ),
                        "strong_tokens": report.strong_tokens_count,
                        "words": sum(int(book["words_count"]) for book in stats),
                    },
                    "verses_without_strong_number_refs": _refs_without_strong_numbers(
                        verse_texts
                    ),
                    "books": stats,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(_report_json(report), ensure_ascii=False, indent=2))
    return 0


def _report_json(report: KjvBuildReport) -> dict[str, object]:
    return {
        "target_path": str(report.target_path),
        "backup_path": str(report.backup_path) if report.backup_path else None,
        "source_path": str(report.source_path),
        "source_url": KJV_SOURCE_URL,
        "source_page_url": KJV_SOURCE_PAGE_URL,
        "source_version": KJV_SOURCE_VERSION,
        "source_sha256": report.source_sha256,
        "source_size_bytes": report.source_size_bytes,
        "verses_count": report.verses_count,
        "filled_verses_count": report.filled_verses_count,
        "empty_verses_count": report.empty_verses_count,
        "strong_tokens_count": report.strong_tokens_count,
        "verses_with_strong_numbers_count": report.verses_with_strong_numbers_count,
        "verses_without_strong_numbers_count": (
            report.verses_count - report.verses_with_strong_numbers_count
        ),
        "books_count": report.books_count,
        "chapters_count": report.chapters_count,
        "built_at": report.built_at,
    }


def _refs_without_strong_numbers(verse_texts: Mapping[str, str]) -> list[str]:
    refs: list[str] = []
    for verse in canonical_verses():
        text = verse_texts[verse.osis_ref]
        if not any(
            _STRONG_TOKEN_PATTERN.fullmatch(token) is not None
            for token in _normalize_text(text).split(" ")
        ):
            refs.append(verse.osis_ref)
    return refs


if __name__ == "__main__":
    raise SystemExit(main())

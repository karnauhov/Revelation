from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from .guards import ImportGuardError, normalize_guard_key

CANON_NAME = "protestant_66"
CANONICAL_VERSE_ID_BOOK_MULTIPLIER = 1_000_000
CANONICAL_VERSE_ID_CHAPTER_MULTIPLIER = 1_000


@dataclass(frozen=True)
class CanonicalBook:
    book_id: int
    canonical_code: str
    osis_code: str
    title: str
    testament: str
    sort_order: int
    chapter_verse_counts: tuple[int, ...]


@dataclass(frozen=True)
class CanonicalVerse:
    canonical_verse_id: int
    canonical_ref: str
    osis_ref: str
    book_id: int
    book_code: str
    osis_book_code: str
    chapter: int
    verse: int
    subverse: str
    sort_key: int

    def as_row(self) -> dict[str, object]:
        return {
            "canonical_verse_id": self.canonical_verse_id,
            "canonical_ref": self.canonical_ref,
            "osis_ref": self.osis_ref,
            "book_id": self.book_id,
            "chapter": self.chapter,
            "verse": self.verse,
            "subverse": self.subverse,
            "sort_key": self.sort_key,
        }


@dataclass(frozen=True)
class CanonImportPolicy:
    canon: str
    psalm_titles: str
    psalm_numbering: str
    esther: str
    daniel: str
    source_native_ref_storage: str
    osis_ref_storage: str


@dataclass(frozen=True)
class LxxBookMapping:
    source_name: str
    canonical_code: str
    note: str = ""

    @property
    def canonical_book_id(self) -> int:
        return BOOKS_BY_CODE[self.canonical_code].book_id


@dataclass(frozen=True)
class LxxExclusionRule:
    source_name: str
    reason: str
    chapter_start: int | None = None
    chapter_end: int | None = None
    verse_start: int | None = None
    verse_end: int | None = None

    def matches(self, chapter: int | None = None, verse: int | None = None) -> bool:
        if self.chapter_start is None:
            return True
        if chapter is None:
            return False
        end_chapter = self.chapter_end if self.chapter_end is not None else self.chapter_start
        if chapter < self.chapter_start or chapter > end_chapter:
            return False
        if self.verse_start is None:
            return True
        if verse is None:
            return False
        end_verse = self.verse_end if self.verse_end is not None else self.verse_start
        return self.verse_start <= verse <= end_verse


CANON_POLICY = CanonImportPolicy(
    canon=CANON_NAME,
    psalm_titles=(
        "Psalm titles/superscriptions are imported as headings or warnings, "
        "not as canonical verses and never as verse 0."
    ),
    psalm_numbering=(
        "canonical_ref uses Protestant/English Psalm numbering for Psalms 1-150; "
        "LXX-native Psalm numbering is preserved only in native_ref and mapped "
        "explicitly during import."
    ),
    esther=(
        "Esther canonical identity is limited to Protestant Esther 1:1-10:3; "
        "Greek additions are excluded unless an owner-approved canonical mapping "
        "is added later."
    ),
    daniel=(
        "Daniel canonical identity is limited to Protestant Daniel 1:1-12:13; "
        "Susanna, Bel and the Dragon, and Prayer of Azariah material are excluded."
    ),
    source_native_ref_storage=(
        "Source-native references are stored separately as native_ref in module "
        "verse records."
    ),
    osis_ref_storage=(
        "OSIS references are stored separately as osis_ref in canonical verse "
        "records or source mapping metadata."
    ),
)


CANONICAL_BOOKS: tuple[CanonicalBook, ...] = (
    CanonicalBook(
        1,
        "Gen",
        "Gen",
        "Genesis",
        "OT",
        1,
        (
            31,
            25,
            24,
            26,
            32,
            22,
            24,
            22,
            29,
            32,
            32,
            20,
            18,
            24,
            21,
            16,
            27,
            33,
            38,
            18,
            34,
            24,
            20,
            67,
            34,
            35,
            46,
            22,
            35,
            43,
            55,
            32,
            20,
            31,
            29,
            43,
            36,
            30,
            23,
            23,
            57,
            38,
            34,
            34,
            28,
            34,
            31,
            22,
            33,
            26,
        ),
    ),
    CanonicalBook(
        2,
        "Exod",
        "Exod",
        "Exodus",
        "OT",
        2,
        (
            22,
            25,
            22,
            31,
            23,
            30,
            25,
            32,
            35,
            29,
            10,
            51,
            22,
            31,
            27,
            36,
            16,
            27,
            25,
            26,
            36,
            31,
            33,
            18,
            40,
            37,
            21,
            43,
            46,
            38,
            18,
            35,
            23,
            35,
            35,
            38,
            29,
            31,
            43,
            38,
        ),
    ),
    CanonicalBook(
        3,
        "Lev",
        "Lev",
        "Leviticus",
        "OT",
        3,
        (
            17,
            16,
            17,
            35,
            19,
            30,
            38,
            36,
            24,
            20,
            47,
            8,
            59,
            57,
            33,
            34,
            16,
            30,
            37,
            27,
            24,
            33,
            44,
            23,
            55,
            46,
            34,
        ),
    ),
    CanonicalBook(
        4,
        "Num",
        "Num",
        "Numbers",
        "OT",
        4,
        (
            54,
            34,
            51,
            49,
            31,
            27,
            89,
            26,
            23,
            36,
            35,
            16,
            33,
            45,
            41,
            50,
            13,
            32,
            22,
            29,
            35,
            41,
            30,
            25,
            18,
            65,
            23,
            31,
            40,
            16,
            54,
            42,
            56,
            29,
            34,
            13,
        ),
    ),
    CanonicalBook(
        5,
        "Deut",
        "Deut",
        "Deuteronomy",
        "OT",
        5,
        (
            46,
            37,
            29,
            49,
            33,
            25,
            26,
            20,
            29,
            22,
            32,
            32,
            18,
            29,
            23,
            22,
            20,
            22,
            21,
            20,
            23,
            30,
            25,
            22,
            19,
            19,
            26,
            68,
            29,
            20,
            30,
            52,
            29,
            12,
        ),
    ),
    CanonicalBook(6, "Josh", "Josh", "Joshua", "OT", 6, (18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33)),
    CanonicalBook(7, "Judg", "Judg", "Judges", "OT", 7, (36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25)),
    CanonicalBook(8, "Ruth", "Ruth", "Ruth", "OT", 8, (22, 23, 18, 22)),
    CanonicalBook(9, "1Sam", "1Sam", "1 Samuel", "OT", 9, (28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13)),
    CanonicalBook(10, "2Sam", "2Sam", "2 Samuel", "OT", 10, (27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25)),
    CanonicalBook(11, "1Kgs", "1Kgs", "1 Kings", "OT", 11, (53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53)),
    CanonicalBook(12, "2Kgs", "2Kgs", "2 Kings", "OT", 12, (18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30)),
    CanonicalBook(13, "1Chr", "1Chr", "1 Chronicles", "OT", 13, (54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30)),
    CanonicalBook(14, "2Chr", "2Chr", "2 Chronicles", "OT", 14, (17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 23, 14, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23)),
    CanonicalBook(15, "Ezra", "Ezra", "Ezra", "OT", 15, (11, 70, 13, 24, 17, 22, 28, 36, 15, 44)),
    CanonicalBook(16, "Neh", "Neh", "Nehemiah", "OT", 16, (11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31)),
    CanonicalBook(17, "Esth", "Esth", "Esther", "OT", 17, (22, 23, 15, 17, 14, 14, 10, 17, 32, 3)),
    CanonicalBook(18, "Job", "Job", "Job", "OT", 18, (22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17)),
    CanonicalBook(
        19,
        "Ps",
        "Ps",
        "Psalms",
        "OT",
        19,
        (
            6,
            12,
            8,
            8,
            12,
            10,
            17,
            9,
            20,
            18,
            7,
            8,
            6,
            7,
            5,
            11,
            15,
            50,
            14,
            9,
            13,
            31,
            6,
            10,
            22,
            12,
            14,
            9,
            11,
            12,
            24,
            11,
            22,
            22,
            28,
            12,
            40,
            22,
            13,
            17,
            13,
            11,
            5,
            26,
            17,
            11,
            9,
            14,
            20,
            23,
            19,
            9,
            6,
            7,
            23,
            13,
            11,
            11,
            17,
            12,
            8,
            12,
            11,
            10,
            13,
            20,
            7,
            35,
            36,
            5,
            24,
            20,
            28,
            23,
            10,
            12,
            20,
            72,
            13,
            19,
            16,
            8,
            18,
            12,
            13,
            17,
            7,
            18,
            52,
            17,
            16,
            15,
            5,
            23,
            11,
            13,
            12,
            9,
            9,
            5,
            8,
            28,
            22,
            35,
            45,
            48,
            43,
            13,
            31,
            7,
            10,
            10,
            9,
            8,
            18,
            19,
            2,
            29,
            176,
            7,
            8,
            9,
            4,
            8,
            5,
            6,
            5,
            6,
            8,
            8,
            3,
            18,
            3,
            3,
            21,
            26,
            9,
            8,
            24,
            13,
            10,
            7,
            12,
            15,
            21,
            10,
            20,
            14,
            9,
            6,
        ),
    ),
    CanonicalBook(20, "Prov", "Prov", "Proverbs", "OT", 20, (33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31)),
    CanonicalBook(21, "Eccl", "Eccl", "Ecclesiastes", "OT", 21, (18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14)),
    CanonicalBook(22, "Song", "Song", "Song of Songs", "OT", 22, (17, 17, 11, 16, 16, 13, 13, 14)),
    CanonicalBook(23, "Isa", "Isa", "Isaiah", "OT", 23, (31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24)),
    CanonicalBook(24, "Jer", "Jer", "Jeremiah", "OT", 24, (19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34)),
    CanonicalBook(25, "Lam", "Lam", "Lamentations", "OT", 25, (22, 22, 66, 22, 22)),
    CanonicalBook(26, "Ezek", "Ezek", "Ezekiel", "OT", 26, (28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35)),
    CanonicalBook(27, "Dan", "Dan", "Daniel", "OT", 27, (21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13)),
    CanonicalBook(28, "Hos", "Hos", "Hosea", "OT", 28, (11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9)),
    CanonicalBook(29, "Joel", "Joel", "Joel", "OT", 29, (20, 32, 21)),
    CanonicalBook(30, "Amos", "Amos", "Amos", "OT", 30, (15, 16, 15, 13, 27, 14, 17, 14, 15)),
    CanonicalBook(31, "Obad", "Obad", "Obadiah", "OT", 31, (21,)),
    CanonicalBook(32, "Jonah", "Jonah", "Jonah", "OT", 32, (17, 10, 10, 11)),
    CanonicalBook(33, "Mic", "Mic", "Micah", "OT", 33, (16, 13, 12, 13, 15, 16, 20)),
    CanonicalBook(34, "Nah", "Nah", "Nahum", "OT", 34, (15, 13, 19)),
    CanonicalBook(35, "Hab", "Hab", "Habakkuk", "OT", 35, (17, 20, 19)),
    CanonicalBook(36, "Zeph", "Zeph", "Zephaniah", "OT", 36, (18, 15, 20)),
    CanonicalBook(37, "Hag", "Hag", "Haggai", "OT", 37, (15, 23)),
    CanonicalBook(38, "Zech", "Zech", "Zechariah", "OT", 38, (21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21)),
    CanonicalBook(39, "Mal", "Mal", "Malachi", "OT", 39, (14, 17, 18, 6)),
    CanonicalBook(40, "Mat", "Matt", "Matthew", "NT", 40, (25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20)),
    CanonicalBook(41, "Mark", "Mark", "Mark", "NT", 41, (45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20)),
    CanonicalBook(42, "Luke", "Luke", "Luke", "NT", 42, (80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53)),
    CanonicalBook(43, "John", "John", "John", "NT", 43, (51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25)),
    CanonicalBook(44, "Acts", "Acts", "Acts", "NT", 44, (26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31)),
    CanonicalBook(45, "Rom", "Rom", "Romans", "NT", 45, (32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27)),
    CanonicalBook(46, "1Cor", "1Cor", "1 Corinthians", "NT", 46, (31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24)),
    CanonicalBook(47, "2Cor", "2Cor", "2 Corinthians", "NT", 47, (24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14)),
    CanonicalBook(48, "Gal", "Gal", "Galatians", "NT", 48, (24, 21, 29, 31, 26, 18)),
    CanonicalBook(49, "Eph", "Eph", "Ephesians", "NT", 49, (23, 22, 21, 32, 33, 24)),
    CanonicalBook(50, "Phil", "Phil", "Philippians", "NT", 50, (30, 30, 21, 23)),
    CanonicalBook(51, "Col", "Col", "Colossians", "NT", 51, (29, 23, 25, 18)),
    CanonicalBook(52, "1Thess", "1Thess", "1 Thessalonians", "NT", 52, (10, 20, 13, 18, 28)),
    CanonicalBook(53, "2Thess", "2Thess", "2 Thessalonians", "NT", 53, (12, 17, 18)),
    CanonicalBook(54, "1Tim", "1Tim", "1 Timothy", "NT", 54, (20, 15, 16, 16, 25, 21)),
    CanonicalBook(55, "2Tim", "2Tim", "2 Timothy", "NT", 55, (18, 26, 17, 22)),
    CanonicalBook(56, "Titus", "Titus", "Titus", "NT", 56, (16, 15, 15)),
    CanonicalBook(57, "Phlm", "Phlm", "Philemon", "NT", 57, (25,)),
    CanonicalBook(58, "Heb", "Heb", "Hebrews", "NT", 58, (14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25)),
    CanonicalBook(59, "Jas", "Jas", "James", "NT", 59, (27, 26, 18, 17, 20)),
    CanonicalBook(60, "1Pet", "1Pet", "1 Peter", "NT", 60, (25, 25, 22, 19, 14)),
    CanonicalBook(61, "2Pet", "2Pet", "2 Peter", "NT", 61, (21, 22, 18)),
    CanonicalBook(62, "1John", "1John", "1 John", "NT", 62, (10, 29, 24, 21, 21)),
    CanonicalBook(63, "2John", "2John", "2 John", "NT", 63, (13,)),
    CanonicalBook(64, "3John", "3John", "3 John", "NT", 64, (14,)),
    CanonicalBook(65, "Jude", "Jude", "Jude", "NT", 65, (25,)),
    CanonicalBook(66, "Rev", "Rev", "Revelation", "NT", 66, (20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21)),
)

BOOKS_BY_CODE = {book.canonical_code: book for book in CANONICAL_BOOKS}
BOOKS_BY_OSIS = {book.osis_code: book for book in CANONICAL_BOOKS}
BOOKS_BY_ID = {book.book_id: book for book in CANONICAL_BOOKS}

_REF_PATTERN = re.compile(r"^([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)$")


def canonical_verse_id_for(book_id: int, chapter: int, verse: int) -> int:
    return (
        book_id * CANONICAL_VERSE_ID_BOOK_MULTIPLIER
        + chapter * CANONICAL_VERSE_ID_CHAPTER_MULTIPLIER
        + verse
    )


def canonical_ref_for(book_code: str, chapter: int, verse: int) -> str:
    return f"{book_code}.{chapter}.{verse}"


def osis_ref_for(osis_book_code: str, chapter: int, verse: int) -> str:
    return f"{osis_book_code}.{chapter}.{verse}"


def get_book(code_or_osis: str) -> CanonicalBook:
    book = BOOKS_BY_CODE.get(code_or_osis) or BOOKS_BY_OSIS.get(code_or_osis)
    if book is None:
        raise KeyError(f"Unknown canonical book code: {code_or_osis}")
    return book


def get_canonical_verse(book_code: str, chapter: int, verse: int) -> CanonicalVerse:
    book = get_book(book_code)
    if chapter < 1 or chapter > len(book.chapter_verse_counts):
        raise KeyError(f"Chapter out of canonical range: {book_code}.{chapter}")
    max_verse = book.chapter_verse_counts[chapter - 1]
    if verse < 1 or verse > max_verse:
        raise KeyError(f"Verse out of canonical range: {book_code}.{chapter}.{verse}")
    verse_id = canonical_verse_id_for(book.book_id, chapter, verse)
    return CanonicalVerse(
        canonical_verse_id=verse_id,
        canonical_ref=canonical_ref_for(book.canonical_code, chapter, verse),
        osis_ref=osis_ref_for(book.osis_code, chapter, verse),
        book_id=book.book_id,
        book_code=book.canonical_code,
        osis_book_code=book.osis_code,
        chapter=chapter,
        verse=verse,
        subverse="",
        sort_key=verse_id,
    )


def parse_canonical_ref(canonical_ref: str) -> CanonicalVerse:
    match = _REF_PATTERN.match(canonical_ref)
    if match is None:
        raise KeyError(f"Invalid canonical_ref: {canonical_ref}")
    return get_canonical_verse(match.group(1), int(match.group(2)), int(match.group(3)))


@lru_cache(maxsize=1)
def canonical_verses() -> tuple[CanonicalVerse, ...]:
    verses: list[CanonicalVerse] = []
    for book in CANONICAL_BOOKS:
        for chapter_index, max_verse in enumerate(book.chapter_verse_counts):
            chapter = chapter_index + 1
            for verse in range(1, max_verse + 1):
                verses.append(get_canonical_verse(book.canonical_code, chapter, verse))
    return tuple(verses)


def canonical_verse_rows() -> list[dict[str, object]]:
    return [verse.as_row() for verse in canonical_verses()]


def _alias_pairs(book: CanonicalBook, *aliases: str) -> tuple[tuple[str, str], ...]:
    values = {book.canonical_code, book.osis_code, book.title, *aliases}
    return tuple((normalize_guard_key(alias), book.canonical_code) for alias in values)


_CANONICAL_ALIAS_PAIRS: list[tuple[str, str]] = []
for _book in CANONICAL_BOOKS:
    _CANONICAL_ALIAS_PAIRS.extend(_alias_pairs(_book))

_CANONICAL_ALIAS_PAIRS.extend(
    [
        (normalize_guard_key("Matthew"), "Mat"),
        (normalize_guard_key("Matt"), "Mat"),
        (normalize_guard_key("Mat"), "Mat"),
        (normalize_guard_key("Mrk"), "Mark"),
        (normalize_guard_key("Mar"), "Mark"),
        (normalize_guard_key("Luk"), "Luke"),
        (normalize_guard_key("Jhn"), "John"),
        (normalize_guard_key("Joh"), "John"),
        (normalize_guard_key("Apocalypse"), "Rev"),
        (normalize_guard_key("Revelation of John"), "Rev"),
    ]
)


LXX_BOOK_MAPPINGS: tuple[LxxBookMapping, ...] = (
    LxxBookMapping("1 Kingdoms", "1Sam", "LXX Kingdoms maps to Samuel/Kings."),
    LxxBookMapping("2 Kingdoms", "2Sam", "LXX Kingdoms maps to Samuel/Kings."),
    LxxBookMapping("3 Kingdoms", "1Kgs", "LXX Kingdoms maps to Samuel/Kings."),
    LxxBookMapping("4 Kingdoms", "2Kgs", "LXX Kingdoms maps to Samuel/Kings."),
    LxxBookMapping("1 Reigns", "1Sam", "Alternate English title for 1 Kingdoms."),
    LxxBookMapping("2 Reigns", "2Sam", "Alternate English title for 2 Kingdoms."),
    LxxBookMapping("3 Reigns", "1Kgs", "Alternate English title for 3 Kingdoms."),
    LxxBookMapping("4 Reigns", "2Kgs", "Alternate English title for 4 Kingdoms."),
    LxxBookMapping("1 Paraleipomenon", "1Chr", "LXX Chronicles title."),
    LxxBookMapping("2 Paraleipomenon", "2Chr", "LXX Chronicles title."),
    LxxBookMapping("I Paraleipomenon", "1Chr", "LXX Chronicles title."),
    LxxBookMapping("II Paraleipomenon", "2Chr", "LXX Chronicles title."),
    LxxBookMapping("Psalms", "Ps", "Canonical Psalm ids use Protestant numbering."),
    LxxBookMapping("Canticle of Canticles", "Song", "LXX title for Song of Songs."),
    LxxBookMapping("Ecclesiastes", "Eccl", "Canonical book in the 66-book canon."),
    LxxBookMapping("Ezra", "Ezra", "CrossWire LXX exposes Ezra separately."),
    LxxBookMapping("Nehemiah", "Neh", "CrossWire LXX exposes Nehemiah separately."),
)

_LXX_BOOK_MAP = dict(_CANONICAL_ALIAS_PAIRS)
for mapping in LXX_BOOK_MAPPINGS:
    _LXX_BOOK_MAP[normalize_guard_key(mapping.source_name)] = mapping.canonical_code


LXX_EXCLUSION_RULES: tuple[LxxExclusionRule, ...] = (
    LxxExclusionRule("1Esd", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("1 Esdras", "Outside the 66-book Protestant canon."),
    LxxExclusionRule(
        "2 Esdras",
        "Ambiguous LXX aggregate; import Ezra and Nehemiah from exact source books only.",
    ),
    LxxExclusionRule("2Esd", "Ambiguous LXX aggregate; import exact canonical books only."),
    LxxExclusionRule("3Esd", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("3 Esdras", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("4Esd", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("4 Esdras", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Tob", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Tobit", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Jdt", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Judith", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Wis", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Wisdom of Solomon", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Sir", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Sirach", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Bar", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Baruch", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("EpJer", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Epistle of Jeremiah", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("1Macc", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("1 Maccabees", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("2Macc", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("2 Maccabees", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("3Macc", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("3 Maccabees", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("4Macc", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("4 Maccabees", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("PssSol", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Psalms of Solomon", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Odes", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("PrMan", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Prayer of Manasseh", "Outside the 66-book Protestant canon."),
    LxxExclusionRule("Ps151", "Outside the 150-Psalm Protestant canon."),
    LxxExclusionRule("Psalm 151", "Outside the 150-Psalm Protestant canon."),
    LxxExclusionRule("Psalms", "Psalm 151 is outside the canon.", 151, 151),
    LxxExclusionRule("Sus", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("Susanna", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("Bel", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("Bel and the Dragon", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("PrAzar", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("Prayer of Azariah", "Greek Daniel addition excluded from NA28_LXX."),
    LxxExclusionRule("AddEsth", "Greek Esther additions excluded from NA28_LXX."),
    LxxExclusionRule("EsthGr", "Greek Esther additions excluded from NA28_LXX."),
    LxxExclusionRule("Greek Esther Additions", "Greek Esther additions excluded from NA28_LXX."),
    LxxExclusionRule("Additions to Esther", "Greek Esther additions excluded from NA28_LXX."),
    LxxExclusionRule("Esther", "Greek Esther additions outside Protestant Esther.", 11, 16),
    LxxExclusionRule("Daniel", "Greek Daniel additions outside Protestant Daniel.", 13, 14),
)

_LXX_EXCLUSION_RULES_BY_KEY: dict[str, list[LxxExclusionRule]] = {}
for _rule in LXX_EXCLUSION_RULES:
    _LXX_EXCLUSION_RULES_BY_KEY.setdefault(normalize_guard_key(_rule.source_name), []).append(_rule)


def lxx_canonical_code_for_source_book(source_book: str) -> str:
    normalized = normalize_guard_key(source_book)
    exclusion_rules = _LXX_EXCLUSION_RULES_BY_KEY.get(normalized, [])
    if any(rule.matches() for rule in exclusion_rules):
        raise ImportGuardError(f"Refusing to import excluded LXX book: {source_book}")
    canonical_code = _LXX_BOOK_MAP.get(normalized)
    if canonical_code is None:
        raise ImportGuardError(f"Unknown LXX source book mapping: {source_book}")
    return canonical_code


def lxx_book_id_for_source_book(source_book: str) -> int:
    return BOOKS_BY_CODE[lxx_canonical_code_for_source_book(source_book)].book_id


def assert_lxx_source_ref_allowed(
    source_book: str,
    *,
    chapter: int | None = None,
    verse: int | None = None,
) -> None:
    normalized = normalize_guard_key(source_book)
    for rule in _LXX_EXCLUSION_RULES_BY_KEY.get(normalized, []):
        if rule.matches(chapter=chapter, verse=verse):
            raise ImportGuardError(f"Refusing to import excluded LXX range: {source_book}")

    canonical_code = lxx_canonical_code_for_source_book(source_book)
    if chapter is not None and verse is not None:
        try:
            get_canonical_verse(canonical_code, chapter, verse)
        except KeyError as error:
            raise ImportGuardError(
                f"Refusing to import out-of-canon source ref: {source_book}.{chapter}.{verse}"
            ) from error

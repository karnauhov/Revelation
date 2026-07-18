from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_VERSE_KEY_RE = re.compile(r"^[0-9A-Z]{3}$")
_REFERENCE_RE = re.compile(r"^(?P<book>.+?)\s+(?P<chapter>\d+)\s*[:.]\s*(?P<verse>\d+)$")
_BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass(frozen=True)
class BibleBook:
    id: int
    code: str
    name: str
    chapters: tuple[int, ...]
    aliases: tuple[str, ...] = ()

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def verse_count(self) -> int:
        return sum(self.chapters)

    def display_label(self) -> str:
        return f"{self.name} [{self.code}]"


class BibleCatalog:
    """The canonical book/verse mapping shared with the Flutter application."""

    def __init__(self, books: tuple[BibleBook, ...]) -> None:
        self.books = books
        self._books_by_id = {book.id: book for book in books}
        self._books_by_alias: dict[str, BibleBook] = {}
        self._verse_ranges: dict[int, tuple[int, int]] = {}
        ordinal = 0
        for book in books:
            for alias in (book.code, book.name, book.display_label(), *book.aliases):
                self._books_by_alias[_normalize_alias(alias)] = book
            first = ordinal + 1
            ordinal += book.verse_count
            self._verse_ranges[book.id] = (first, ordinal)
        self.total_verses = ordinal

    @classmethod
    def load(cls, project_root: Path) -> "BibleCatalog":
        map_path = project_root / "assets" / "data" / "bible_verse_map.json"
        payload = json.loads(map_path.read_text(encoding="utf-8"))
        books_payload = _required_list(payload, "books")
        locale_payloads = {
            locale: _load_arb_book_fields(project_root / "lib" / "l10n" / f"app_{locale}.arb")
            for locale in ("en", "es", "uk", "ru")
        }

        books: list[BibleBook] = []
        for raw_book in books_payload:
            book = _as_dict(raw_book)
            book_id = _required_int(book, "id")
            code = _required_string(book, "code")
            chapters = tuple(_as_positive_int(value) for value in _required_list(book, "chapters"))
            names: list[str] = []
            aliases: list[str] = []
            for locale in ("ru", "en", "es", "uk"):
                localized_code, localized_name = locale_payloads[locale].get(book_id, (code, code))
                if localized_name not in names:
                    names.append(localized_name)
                for alias in (localized_code, localized_name):
                    if alias and alias != code and alias not in aliases:
                        aliases.append(alias)
            books.append(
                BibleBook(
                    id=book_id,
                    code=code,
                    name=names[0] if names else code,
                    chapters=chapters,
                    aliases=tuple(aliases),
                )
            )

        catalog = cls(tuple(books))
        expected_total = _required_int(payload, "verses_count")
        if catalog.total_verses != expected_total:
            raise ValueError(
                f"Bible map count mismatch: expected {expected_total}, got {catalog.total_verses}"
            )
        return catalog

    def book(self, book_id: int) -> BibleBook:
        try:
            return self._books_by_id[book_id]
        except KeyError as exc:
            raise ValueError(f"Unknown Bible book id: {book_id}") from exc

    def book_for_value(self, value: str) -> BibleBook | None:
        normalized = _normalize_alias(value)
        if not normalized:
            return None
        if normalized.isdigit():
            return self._books_by_id.get(int(normalized))
        return self._books_by_alias.get(normalized)

    def key_for(self, *, book_id: int, chapter: int, verse: int) -> str:
        book = self.book(book_id)
        if chapter < 1 or chapter > book.chapter_count:
            raise ValueError(f"Unknown chapter {chapter} for {book.code}")
        verse_count = book.chapters[chapter - 1]
        if verse < 1 or verse > verse_count:
            raise ValueError(f"Unknown verse {verse} for {book.code} {chapter}")
        first, _last = self._verse_ranges[book_id]
        ordinal = first + sum(book.chapters[: chapter - 1]) + verse - 1
        return _base36(ordinal).rjust(3, "0")

    def reference_for_key(self, verse_key: str) -> tuple[BibleBook, int, int] | None:
        if not _VERSE_KEY_RE.fullmatch(verse_key.strip().upper()):
            return None
        ordinal = _base36_to_int(verse_key)
        if ordinal is None or ordinal < 1 or ordinal > self.total_verses:
            return None
        for book in self.books:
            first, last = self._verse_ranges[book.id]
            if first <= ordinal <= last:
                local_ordinal = ordinal - first
                chapter = 1
                for verse_count in book.chapters:
                    if local_ordinal < verse_count:
                        return book, chapter, local_ordinal + 1
                    local_ordinal -= verse_count
                    chapter += 1
        return None

    def parse_reference(self, value: str) -> tuple[BibleBook, int, int] | None:
        text = value.strip()
        if _VERSE_KEY_RE.fullmatch(text.upper()):
            return self.reference_for_key(text)
        match = _REFERENCE_RE.fullmatch(text)
        if match is None:
            return None
        book = self.book_for_value(match.group("book"))
        if book is None:
            return None
        return book, int(match.group("chapter")), int(match.group("verse"))

    def reference_label(self, verse_key: str) -> str:
        reference = self.reference_for_key(verse_key)
        if reference is None:
            return verse_key
        book, chapter, verse = reference
        return f"{book.name} {chapter}:{verse}"

    def verse_keys_for_chapter(self, *, book_id: int, chapter: int) -> tuple[str, ...]:
        book = self.book(book_id)
        if chapter < 1 or chapter > book.chapter_count:
            raise ValueError(f"Unknown chapter {chapter} for {book.code}")
        return tuple(
            self.key_for(book_id=book_id, chapter=chapter, verse=verse)
            for verse in range(1, book.chapters[chapter - 1] + 1)
        )


def _load_arb_book_fields(path: Path) -> dict[int, tuple[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fields: dict[int, tuple[str, str]] = {}
    for key, value in payload.items():
        match = re.fullmatch(r"book_(code|name)_(\d+)", key)
        if match is None or not isinstance(value, str):
            continue
        book_id = int(match.group(2))
        code, name = fields.get(book_id, ("", ""))
        if match.group(1) == "code":
            code = value
        else:
            name = value
        fields[book_id] = (code, name)
    return fields


def _normalize_alias(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _base36(value: int) -> str:
    if value < 0:
        raise ValueError("base36 value cannot be negative")
    if value == 0:
        return "0"
    digits: list[str] = []
    while value:
        value, remainder = divmod(value, 36)
        digits.append(_BASE36_ALPHABET[remainder])
    return "".join(reversed(digits))


def _base36_to_int(value: str) -> int | None:
    result = 0
    for character in value.strip().upper():
        try:
            digit = _BASE36_ALPHABET.index(character)
        except ValueError:
            return None
        result = result * 36 + digit
    return result


def _as_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Bible map book must be an object")
    return value


def _required_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Bible map field {key!r} must be a list")
    return value


def _required_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Bible map field {key!r} must be an integer")
    return value


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Bible map field {key!r} must be a non-empty string")
    return value


def _as_positive_int(value: Any) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("Bible chapter verse counts must be positive integers")
    return value

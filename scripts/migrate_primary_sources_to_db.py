#!/usr/bin/env python3
"""Migrate the legacy primary sources snapshot into SQLite databases."""

from __future__ import annotations

import argparse
import ast
import json
import mimetypes
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


LOCALES = ("en", "es", "ru", "uk")
STANDARD_LINK_TITLES = {
    "loc.wikipedia": ("wikipedia", "wikipedia"),
    "loc.intf": ("intf", "intf"),
    "loc.image_source": ("image_source", "image_source"),
}
LOCALIZED_TEXT_FIELDS = (
    ("title_markup", "title"),
    ("date_label", "date"),
    ("content_label", "content"),
    ("material_text", "material"),
    ("text_style_text", "textStyle"),
    ("found_text", "found"),
    ("classification_text", "classification"),
    ("current_location_text", "currentLocation"),
)


class ParseError(RuntimeError):
    """Raised when the legacy snapshot cannot be parsed safely."""


@dataclass(frozen=True)
class LinkRecord:
    source_id: str
    link_id: str
    sort_order: int
    link_role: str
    url: str


@dataclass(frozen=True)
class AttributionRecord:
    source_id: str
    attribution_id: str
    sort_order: int
    text: str
    url: str


@dataclass(frozen=True)
class PageRecord:
    source_id: str
    page_name: str
    sort_order: int
    content_ref: str
    image_path: str
    mobile_image_path: str | None


@dataclass(frozen=True)
class WordRecord:
    source_id: str
    page_name: str
    word_index: int
    text: str
    strong_number: int | None
    strong_pronounce: bool
    strong_x_shift: float
    missing_char_indexes: list[int]
    rectangles: list[list[float]]


@dataclass(frozen=True)
class VerseRecord:
    source_id: str
    page_name: str
    verse_index: int
    chapter_number: int
    verse_number: int
    label_x: float
    label_y: float
    word_indexes: list[int]
    contours: list[list[list[float]]]


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    family: str
    number: int
    group_kind: str
    sort_order: int
    verses_count: int
    preview_asset_path: str
    preview_resource_key: str
    default_max_scale: float
    can_show_images: bool
    images_are_monochrome: bool
    localization_prefix: str
    links: list[LinkRecord]
    attributions: list[AttributionRecord]
    pages: list[PageRecord]
    words: list[WordRecord]
    verses: list[VerseRecord]


@dataclass(frozen=True)
class ParsedDataset:
    repository_path: Path
    preview_dir: Path
    sources: list[SourceRecord]


def default_repository_path() -> Path:
    return Path(__file__).resolve().parent / "legacy" / "primary_sources_repository.dart.txt"


def default_l10n_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "lib" / "l10n"


def default_preview_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "images" / "PrimarySources"


def default_db_dir() -> Path:
    return Path.home() / "OneDrive" / "Documents" / "revelation" / "db"


def default_backup_root(db_dir: Path) -> Path:
    return db_dir / "backups"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_arb(path: Path) -> dict[str, str]:
    data = json.loads(load_text(path))
    return {
        key: value
        for key, value in data.items()
        if not key.startswith("@") and isinstance(value, str)
    }


def parse_string_literal(expr: str) -> str:
    try:
        value = ast.literal_eval(expr.strip())
    except (SyntaxError, ValueError) as exc:
        raise ParseError(f"Не удалось разобрать строковый литерал: {expr!r}") from exc
    if not isinstance(value, str):
        raise ParseError(f"Ожидалась строка, получено: {expr!r}")
    return value


def parse_bool(expr: str) -> bool:
    normalized = expr.strip()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ParseError(f"Ожидалось bool-значение, получено: {expr!r}")


def parse_int(expr: str) -> int:
    try:
        return int(expr.strip())
    except ValueError as exc:
        raise ParseError(f"Ожидалось целое число, получено: {expr!r}") from exc


def parse_float(expr: str) -> float:
    try:
        return float(expr.strip())
    except ValueError as exc:
        raise ParseError(f"Ожидалось число, получено: {expr!r}") from exc


def strip_const(expr: str) -> str:
    stripped = expr.strip()
    if stripped.startswith("const "):
        return stripped[6:].strip()
    return stripped


def strip_enclosing(expr: str, open_char: str, close_char: str) -> str:
    stripped = strip_const(expr)
    if not stripped.startswith(open_char) or not stripped.endswith(close_char):
        raise ParseError(f"Ожидалось выражение {open_char}...{close_char}, получено: {expr!r}")
    return stripped[1:-1]


def find_matching(text: str, start_index: int, open_char: str = "(", close_char: str = ")") -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start_index, len(text)):
        char = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == open_char:
            depth += 1
            continue
        if char == close_char:
            depth -= 1
            if depth == 0:
                return index
    raise ParseError(f"Не найдено закрывающее {close_char!r} для позиции {start_index}")


def split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    quote: str | None = None
    escaped = False
    round_depth = 0
    square_depth = 0
    curly_depth = 0
    start = 0

    for index, char in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ("'", '"'):
            quote = char
            continue
        if char == "(":
            round_depth += 1
            continue
        if char == ")":
            round_depth -= 1
            continue
        if char == "[":
            square_depth += 1
            continue
        if char == "]":
            square_depth -= 1
            continue
        if char == "{":
            curly_depth += 1
            continue
        if char == "}":
            curly_depth -= 1
            continue
        if (
            char == delimiter
            and round_depth == 0
            and square_depth == 0
            and curly_depth == 0
        ):
            part = text[start:index].strip()
            if part:
                parts.append(part)
            start = index + 1

    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def split_top_level_key_value(part: str) -> tuple[str, str] | None:
    quote: str | None = None
    escaped = False
    round_depth = 0
    square_depth = 0
    curly_depth = 0
    for index, char in enumerate(part):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == "(":
            round_depth += 1
            continue
        if char == ")":
            round_depth -= 1
            continue
        if char == "[":
            square_depth += 1
            continue
        if char == "]":
            square_depth -= 1
            continue
        if char == "{":
            curly_depth += 1
            continue
        if char == "}":
            curly_depth -= 1
            continue
        if (
            char == ":"
            and round_depth == 0
            and square_depth == 0
            and curly_depth == 0
        ):
            return part[:index].strip(), part[index + 1 :].strip()
    return None


def parse_arguments(expr: str) -> tuple[list[str], dict[str, str]]:
    positional: list[str] = []
    named: dict[str, str] = {}
    for part in split_top_level(expr):
        key_value = split_top_level_key_value(part)
        if key_value is None:
            positional.append(part)
            continue
        key, value = key_value
        named[key] = value
    return positional, named


def iter_constructor_bodies(text: str, constructor_name: str) -> list[str]:
    bodies: list[str] = []
    needle = f"{constructor_name}("
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            break
        open_index = index + len(constructor_name)
        close_index = find_matching(text, open_index)
        bodies.append(text[open_index + 1 : close_index])
        start = close_index + 1
    return bodies


def extract_method_source_ids(text: str) -> dict[str, list[str]]:
    method_names = (
        "getFullPrimarySources",
        "getSignificantPrimarySources",
        "getFragmentsPrimarySources",
    )
    result: dict[str, list[str]] = {}
    for method_name in method_names:
        marker = f"List<PrimarySource> {method_name}(BuildContext context)"
        method_index = text.find(marker)
        if method_index == -1:
            raise ParseError(f"Не найден метод {method_name}")
        body_start = text.find("{", method_index)
        if body_start == -1:
            raise ParseError(f"Не найдено тело метода {method_name}")
        body_end = find_matching(text, body_start, "{", "}")
        body = text[body_start + 1 : body_end]
        result[method_name] = []
        for source_body in iter_constructor_bodies(body, "PrimarySource"):
            _, named = parse_arguments(source_body)
            result[method_name].append(parse_string_literal(require_named(named, "id")))
    return result


def require_named(named: dict[str, str], key: str) -> str:
    if key not in named:
        raise ParseError(f"Не найден обязательный аргумент {key!r}")
    return named[key]


def parse_loc_key(expr: str) -> str:
    value = expr.strip()
    if not value.startswith("loc."):
        raise ParseError(f"Ожидалось loc.* выражение, получено: {expr!r}")
    return value[4:]


def parse_loc_prefix(source_id: str, named: dict[str, str]) -> str:
    title_key = parse_loc_key(require_named(named, "title"))
    if not title_key.endswith("_title"):
        raise ParseError(f"Для {source_id} ожидается *_title, получено: {title_key}")
    prefix = title_key[: -len("_title")]
    expected_suffixes = {
        "date": "_date",
        "content": "_content",
        "material": "_material",
        "textStyle": "_textStyle",
        "found": "_found",
        "classification": "_classification",
        "currentLocation": "_currentLocation",
    }
    for field_name, suffix in expected_suffixes.items():
        key = parse_loc_key(require_named(named, field_name))
        expected = f"{prefix}{suffix}"
        if key != expected:
            raise ParseError(
                f"У {source_id} нарушена связка локализационных ключей: {field_name} -> {key}, ожидается {expected}"
            )
    return prefix


def parse_family_and_number(source_id: str) -> tuple[str, int]:
    if len(source_id) != 4:
        raise ParseError(f"Неожиданный source_id: {source_id}")
    family_code = source_id[0]
    number = parse_int(source_id[1:])
    if family_code == "U":
        return "uncial", number
    if family_code == "P":
        return "papyrus", number
    raise ParseError(f"Неизвестное семейство источника: {source_id}")


def parse_int_list(expr: str) -> list[int]:
    inner = strip_enclosing(expr, "[", "]").strip()
    if not inner:
        return []
    return [parse_int(part) for part in split_top_level(inner)]


def parse_offsets_list(expr: str) -> list[list[float]]:
    offsets: list[list[float]] = []
    for body in iter_constructor_bodies(strip_const(expr), "Offset"):
        positional, named = parse_arguments(body)
        if named:
            raise ParseError(f"Offset не должен содержать именованные аргументы: {body}")
        if len(positional) != 2:
            raise ParseError(f"Offset должен содержать 2 позиционных аргумента: {body}")
        offsets.append([parse_float(positional[0]), parse_float(positional[1])])
    return offsets


def parse_page_rectangles(expr: str) -> list[list[float]]:
    rectangles: list[list[float]] = []
    for body in iter_constructor_bodies(strip_const(expr), "PageRect"):
        positional, named = parse_arguments(body)
        if named:
            raise ParseError(f"PageRect не должен содержать именованные аргументы: {body}")
        if len(positional) != 4:
            raise ParseError(f"PageRect должен содержать 4 позиционных аргумента: {body}")
        rectangles.append([parse_float(part) for part in positional])
    return rectangles


def parse_contours(expr: str) -> list[list[list[float]]]:
    inner = strip_enclosing(expr, "[", "]").strip()
    if not inner:
        return []
    contours: list[list[list[float]]] = []
    for contour_expr in split_top_level(inner):
        contour_inner = strip_enclosing(contour_expr, "[", "]").strip()
        if not contour_inner:
            contours.append([])
            continue
        contour = parse_offsets_list(f"[{contour_inner}]")
        contours.append(contour)
    return contours


def parse_attributes(source_id: str, expr: str) -> list[AttributionRecord]:
    inner = strip_enclosing(expr, "[", "]").strip()
    if not inner:
        return []
    records: list[AttributionRecord] = []
    for sort_order, item_expr in enumerate(split_top_level(inner), start=1):
        map_inner = strip_enclosing(item_expr, "{", "}").strip()
        map_items = {}
        for part in split_top_level(map_inner):
            key_value = split_top_level_key_value(part)
            if key_value is None:
                raise ParseError(f"Некорректная map-запись attribution: {part!r}")
            raw_key, raw_value = key_value
            key = parse_string_literal(raw_key)
            map_items[key] = parse_string_literal(raw_value)
        records.append(
            AttributionRecord(
                source_id=source_id,
                attribution_id=f"attr_{sort_order}",
                sort_order=sort_order - 1,
                text=map_items.get("text", ""),
                url=map_items.get("url", ""),
            )
        )
    return records


def parse_links(source_id: str, named: dict[str, str]) -> list[LinkRecord]:
    records: list[LinkRecord] = []
    used_ids: set[str] = set()
    for index in range(1, 4):
        title_expr = require_named(named, f"link{index}Title")
        url = parse_string_literal(require_named(named, f"link{index}Url"))
        if not url:
            continue
        standardized = STANDARD_LINK_TITLES.get(title_expr.strip())
        if standardized is None:
            raise ParseError(
                f"У {source_id} link{index}Title имеет неподдерживаемое значение {title_expr!r}. "
                "Скрипт Phase 2 ожидает стандартные loc.wikipedia/loc.intf/loc.image_source или пустую строку."
            )
        link_id, link_role = standardized
        if link_id in used_ids:
            suffix = 2
            while f"{link_id}_{suffix}" in used_ids:
                suffix += 1
            link_id = f"{link_id}_{suffix}"
        used_ids.add(link_id)
        records.append(
            LinkRecord(
                source_id=source_id,
                link_id=link_id,
                sort_order=index - 1,
                link_role=link_role,
                url=url,
            )
        )
    return records


def parse_words(source_id: str, page_name: str, expr: str) -> list[WordRecord]:
    records: list[WordRecord] = []
    for word_index, body in enumerate(iter_constructor_bodies(strip_const(expr), "PageWord")):
        positional, named = parse_arguments(body)
        if len(positional) < 2:
            raise ParseError(f"PageWord должен содержать минимум 2 позиционных аргумента: {body}")
        records.append(
            WordRecord(
                source_id=source_id,
                page_name=page_name,
                word_index=word_index,
                text=parse_string_literal(positional[0]),
                strong_number=parse_int(named["sn"]) if "sn" in named else None,
                strong_pronounce=parse_bool(named["snPronounce"]) if "snPronounce" in named else False,
                strong_x_shift=parse_float(named["snXshift"]) if "snXshift" in named else 0.0,
                missing_char_indexes=parse_int_list(named["notExist"]) if "notExist" in named else [],
                rectangles=parse_page_rectangles(positional[1]),
            )
        )
    return records


def parse_verses(source_id: str, page_name: str, expr: str) -> list[VerseRecord]:
    records: list[VerseRecord] = []
    for verse_index, body in enumerate(iter_constructor_bodies(strip_const(expr), "Verse")):
        positional, named = parse_arguments(body)
        if positional:
            raise ParseError(f"Verse ожидается только с именованными аргументами: {body}")
        label_body_list = iter_constructor_bodies(require_named(named, "labelPosition"), "Offset")
        if len(label_body_list) != 1:
            raise ParseError(f"labelPosition должен содержать ровно один Offset: {body}")
        label_positional, label_named = parse_arguments(label_body_list[0])
        if label_named or len(label_positional) != 2:
            raise ParseError(f"Некорректный Offset в labelPosition: {body}")
        records.append(
            VerseRecord(
                source_id=source_id,
                page_name=page_name,
                verse_index=verse_index,
                chapter_number=parse_int(require_named(named, "chapterNumber")),
                verse_number=parse_int(require_named(named, "verseNumber")),
                label_x=parse_float(label_positional[0]),
                label_y=parse_float(label_positional[1]),
                word_indexes=parse_int_list(named["wordIndexes"]) if "wordIndexes" in named else [],
                contours=parse_contours(named["contours"]) if "contours" in named else [],
            )
        )
    return records


def parse_pages(source_id: str, expr: str) -> tuple[list[PageRecord], list[WordRecord], list[VerseRecord]]:
    pages: list[PageRecord] = []
    words: list[WordRecord] = []
    verses: list[VerseRecord] = []
    for sort_order, body in enumerate(iter_constructor_bodies(strip_const(expr), "model.Page")):
        positional, named = parse_arguments(body)
        if positional:
            raise ParseError(f"model.Page ожидается только с именованными аргументами: {body}")
        page_name = parse_string_literal(require_named(named, "name"))
        pages.append(
            PageRecord(
                source_id=source_id,
                page_name=page_name,
                sort_order=sort_order,
                content_ref=parse_string_literal(require_named(named, "content")),
                image_path=parse_string_literal(require_named(named, "image")),
                mobile_image_path=None,
            )
        )
        if "words" in named:
            words.extend(parse_words(source_id, page_name, named["words"]))
        if "verses" in named:
            verses.extend(parse_verses(source_id, page_name, named["verses"]))
    return pages, words, verses


def parse_repository(repository_path: Path, preview_dir: Path) -> ParsedDataset:
    text = load_text(repository_path)
    method_source_ids = extract_method_source_ids(text)
    source_group_order: dict[str, tuple[str, int]] = {}
    for group_kind, method_name in (
        ("full", "getFullPrimarySources"),
        ("significant", "getSignificantPrimarySources"),
        ("fragment", "getFragmentsPrimarySources"),
    ):
        for sort_order, source_id in enumerate(method_source_ids[method_name]):
            source_group_order[source_id] = (group_kind, sort_order)

    sources: list[SourceRecord] = []
    for body in iter_constructor_bodies(text, "PrimarySource"):
        positional, named = parse_arguments(body)
        if positional:
            raise ParseError(f"PrimarySource ожидается только с именованными аргументами: {body[:120]}...")
        source_id = parse_string_literal(require_named(named, "id"))
        if source_id not in source_group_order:
            raise ParseError(f"Источник {source_id} не найден в групповых методах repository")
        family, number = parse_family_and_number(source_id)
        localization_prefix = parse_loc_prefix(source_id, named)
        group_kind, sort_order = source_group_order[source_id]
        preview_asset_path = parse_string_literal(require_named(named, "preview"))
        preview_asset_name = Path(preview_asset_path).name
        if not (preview_dir / preview_asset_name).exists():
            raise ParseError(f"Не найден preview asset для {source_id}: {preview_dir / preview_asset_name}")
        pages, words, verses = parse_pages(source_id, require_named(named, "pages"))
        sources.append(
            SourceRecord(
                source_id=source_id,
                family=family,
                number=number,
                group_kind=group_kind,
                sort_order=sort_order,
                verses_count=parse_int(require_named(named, "quantity")),
                preview_asset_path=preview_asset_path,
                preview_resource_key=f"primary_sources/previews/{source_id}.png",
                default_max_scale=parse_float(require_named(named, "maxScale")),
                can_show_images=parse_bool(require_named(named, "permissionsReceived")),
                images_are_monochrome=parse_bool(require_named(named, "isMonochrome")),
                localization_prefix=localization_prefix,
                links=parse_links(source_id, named),
                attributions=parse_attributes(source_id, require_named(named, "attributes")),
                pages=pages,
                words=words,
                verses=verses,
            )
        )
    return ParsedDataset(repository_path=repository_path, preview_dir=preview_dir, sources=sources)


def collect_localized_rows(
    dataset: ParsedDataset,
    arb_by_locale: dict[str, dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {locale: [] for locale in LOCALES}
    for source in dataset.sources:
        for locale in LOCALES:
            arb = arb_by_locale[locale]
            row: dict[str, str] = {"source_id": source.source_id}
            for column_name, suffix in LOCALIZED_TEXT_FIELDS:
                key = f"{source.localization_prefix}_{suffix}"
                if key not in arb:
                    raise ParseError(f"В locale {locale} отсутствует ключ {key}")
                row[column_name] = arb[key]
            result[locale].append(row)
    return result


def calculate_dataset_totals(dataset: ParsedDataset) -> dict[str, Any]:
    group_counts = {"full": 0, "significant": 0, "fragment": 0}
    overlay_sources: list[str] = []
    zero_page_sources: list[str] = []
    permissions_true = 0
    permissions_false = 0
    pages_count = 0
    words_count = 0
    rectangles_count = 0
    verses_count = 0
    links_count = 0
    attributions_count = 0

    for source in dataset.sources:
        group_counts[source.group_kind] += 1
        if source.can_show_images:
            permissions_true += 1
        else:
            permissions_false += 1
        if not source.pages:
            zero_page_sources.append(source.source_id)
        if source.words or source.verses:
            overlay_sources.append(source.source_id)
        pages_count += len(source.pages)
        words_count += len(source.words)
        rectangles_count += sum(len(word.rectangles) for word in source.words)
        verses_count += len(source.verses)
        links_count += len(source.links)
        attributions_count += len(source.attributions)

    return {
        "sources": len(dataset.sources),
        "pages": pages_count,
        "words": words_count,
        "rectangles": rectangles_count,
        "verses": verses_count,
        "permissions_true": permissions_true,
        "permissions_false": permissions_false,
        "groups": group_counts,
        "zero_page_sources": zero_page_sources,
        "overlay_sources": overlay_sources,
        "links": links_count,
        "attributions": attributions_count,
        "preview_resources": len(dataset.sources),
    }


COMMON_SCHEMA_SQL = (
    """
    CREATE TABLE IF NOT EXISTS common_resources (
      key TEXT NOT NULL PRIMARY KEY,
      file_name TEXT NOT NULL,
      mime_type TEXT NOT NULL,
      data BLOB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_sources (
      id TEXT NOT NULL PRIMARY KEY,
      family TEXT NOT NULL,
      number INTEGER NOT NULL,
      group_kind TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      verses_count INTEGER NOT NULL DEFAULT 0,
      preview_resource_key TEXT NOT NULL,
      default_max_scale REAL NOT NULL DEFAULT 3.0,
      can_show_images INTEGER NOT NULL DEFAULT 1,
      images_are_monochrome INTEGER NOT NULL DEFAULT 0,
      notes TEXT NOT NULL DEFAULT ''
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_links (
      source_id TEXT NOT NULL,
      link_id TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      link_role TEXT NOT NULL,
      url TEXT NOT NULL,
      PRIMARY KEY (source_id, link_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_attributions (
      source_id TEXT NOT NULL,
      attribution_id TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      text TEXT NOT NULL,
      url TEXT NOT NULL,
      PRIMARY KEY (source_id, attribution_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_pages (
      source_id TEXT NOT NULL,
      page_name TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      content_ref TEXT NOT NULL,
      image_path TEXT NOT NULL,
      mobile_image_path TEXT,
      PRIMARY KEY (source_id, page_name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_words (
      source_id TEXT NOT NULL,
      page_name TEXT NOT NULL,
      word_index INTEGER NOT NULL,
      text TEXT NOT NULL,
      strong_number INTEGER,
      strong_pronounce INTEGER NOT NULL DEFAULT 0,
      strong_x_shift REAL NOT NULL DEFAULT 0.0,
      missing_char_indexes_json TEXT NOT NULL DEFAULT '[]',
      rectangles_json TEXT NOT NULL DEFAULT '[]',
      PRIMARY KEY (source_id, page_name, word_index)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_verses (
      source_id TEXT NOT NULL,
      page_name TEXT NOT NULL,
      verse_index INTEGER NOT NULL,
      chapter_number INTEGER NOT NULL,
      verse_number INTEGER NOT NULL,
      label_x REAL NOT NULL,
      label_y REAL NOT NULL,
      word_indexes_json TEXT NOT NULL DEFAULT '[]',
      contours_json TEXT NOT NULL DEFAULT '[]',
      PRIMARY KEY (source_id, page_name, verse_index)
    )
    """,
)

LOCALIZED_SCHEMA_SQL = (
    """
    CREATE TABLE IF NOT EXISTS primary_source_texts (
      source_id TEXT NOT NULL PRIMARY KEY,
      title_markup TEXT NOT NULL,
      date_label TEXT NOT NULL,
      content_label TEXT NOT NULL,
      material_text TEXT NOT NULL,
      text_style_text TEXT NOT NULL,
      found_text TEXT NOT NULL,
      classification_text TEXT NOT NULL,
      current_location_text TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS primary_source_link_texts (
      source_id TEXT NOT NULL,
      link_id TEXT NOT NULL,
      title TEXT NOT NULL,
      PRIMARY KEY (source_id, link_id)
    )
    """,
)


def ensure_common_schema(connection: sqlite3.Connection) -> None:
    for statement in COMMON_SCHEMA_SQL:
        connection.execute(statement)


def ensure_localized_schema(connection: sqlite3.Connection) -> None:
    for statement in LOCALIZED_SCHEMA_SQL:
        connection.execute(statement)


def guess_mime_type(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type or "application/octet-stream"


def backup_databases(db_paths: list[Path], backup_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"primary_sources_phase2_{timestamp}"
    suffix = 2
    while backup_dir.exists():
        backup_dir = backup_root / f"primary_sources_phase2_{timestamp}_{suffix}"
        suffix += 1
    backup_dir.mkdir(parents=True, exist_ok=False)
    for path in db_paths:
        shutil.copy2(path, backup_dir / path.name)
    return backup_dir


def write_common_db(common_db_path: Path, dataset: ParsedDataset) -> None:
    preview_rows = []
    for source in dataset.sources:
        preview_path = dataset.preview_dir / Path(source.preview_asset_path).name
        preview_rows.append(
            (
                source.preview_resource_key,
                preview_path.name,
                guess_mime_type(preview_path),
                preview_path.read_bytes(),
            )
        )

    with sqlite3.connect(common_db_path) as connection:
        ensure_common_schema(connection)
        with connection:
            connection.execute("DELETE FROM primary_source_verses")
            connection.execute("DELETE FROM primary_source_words")
            connection.execute("DELETE FROM primary_source_pages")
            connection.execute("DELETE FROM primary_source_attributions")
            connection.execute("DELETE FROM primary_source_links")
            connection.execute("DELETE FROM primary_sources")
            connection.executemany(
                "DELETE FROM common_resources WHERE key = ?",
                [(source.preview_resource_key,) for source in dataset.sources],
            )
            connection.executemany(
                """
                INSERT INTO primary_sources(
                  id, family, number, group_kind, sort_order, verses_count,
                  preview_resource_key, default_max_scale, can_show_images,
                  images_are_monochrome, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        source.source_id,
                        source.family,
                        source.number,
                        source.group_kind,
                        source.sort_order,
                        source.verses_count,
                        source.preview_resource_key,
                        source.default_max_scale,
                        1 if source.can_show_images else 0,
                        1 if source.images_are_monochrome else 0,
                        "",
                    )
                    for source in dataset.sources
                ],
            )
            connection.executemany(
                """
                INSERT INTO primary_source_links(source_id, link_id, sort_order, link_role, url)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (row.source_id, row.link_id, row.sort_order, row.link_role, row.url)
                    for source in dataset.sources
                    for row in source.links
                ],
            )
            connection.executemany(
                """
                INSERT INTO primary_source_attributions(source_id, attribution_id, sort_order, text, url)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (row.source_id, row.attribution_id, row.sort_order, row.text, row.url)
                    for source in dataset.sources
                    for row in source.attributions
                ],
            )
            connection.executemany(
                """
                INSERT INTO primary_source_pages(
                  source_id, page_name, sort_order, content_ref, image_path, mobile_image_path
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.source_id,
                        row.page_name,
                        row.sort_order,
                        row.content_ref,
                        row.image_path,
                        row.mobile_image_path,
                    )
                    for source in dataset.sources
                    for row in source.pages
                ],
            )
            connection.executemany(
                """
                INSERT INTO primary_source_words(
                  source_id, page_name, word_index, text, strong_number, strong_pronounce,
                  strong_x_shift, missing_char_indexes_json, rectangles_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.source_id,
                        row.page_name,
                        row.word_index,
                        row.text,
                        row.strong_number,
                        1 if row.strong_pronounce else 0,
                        row.strong_x_shift,
                        json.dumps(row.missing_char_indexes, ensure_ascii=False),
                        json.dumps(row.rectangles, ensure_ascii=False),
                    )
                    for source in dataset.sources
                    for row in source.words
                ],
            )
            connection.executemany(
                """
                INSERT INTO primary_source_verses(
                  source_id, page_name, verse_index, chapter_number, verse_number,
                  label_x, label_y, word_indexes_json, contours_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.source_id,
                        row.page_name,
                        row.verse_index,
                        row.chapter_number,
                        row.verse_number,
                        row.label_x,
                        row.label_y,
                        json.dumps(row.word_indexes, ensure_ascii=False),
                        json.dumps(row.contours, ensure_ascii=False),
                    )
                    for source in dataset.sources
                    for row in source.verses
                ],
            )
            connection.executemany(
                """
                INSERT INTO common_resources(key, file_name, mime_type, data)
                VALUES (?, ?, ?, ?)
                """,
                preview_rows,
            )
            connection.execute("PRAGMA user_version = 3")


def write_localized_db(localized_db_path: Path, rows: list[dict[str, str]]) -> None:
    with sqlite3.connect(localized_db_path) as connection:
        ensure_localized_schema(connection)
        with connection:
            connection.execute("DELETE FROM primary_source_link_texts")
            connection.execute("DELETE FROM primary_source_texts")
            connection.executemany(
                """
                INSERT INTO primary_source_texts(
                  source_id, title_markup, date_label, content_label, material_text,
                  text_style_text, found_text, classification_text, current_location_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row["source_id"],
                        row["title_markup"],
                        row["date_label"],
                        row["content_label"],
                        row["material_text"],
                        row["text_style_text"],
                        row["found_text"],
                        row["classification_text"],
                        row["current_location_text"],
                    )
                    for row in rows
                ],
            )
            connection.execute("PRAGMA user_version = 5")


def validate_common_db(common_db_path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    with sqlite3.connect(common_db_path) as connection:
        actual_sources = connection.execute("SELECT COUNT(*) FROM primary_sources").fetchone()[0]
        actual_pages = connection.execute("SELECT COUNT(*) FROM primary_source_pages").fetchone()[0]
        actual_words = connection.execute("SELECT COUNT(*) FROM primary_source_words").fetchone()[0]
        actual_verses = connection.execute("SELECT COUNT(*) FROM primary_source_verses").fetchone()[0]
        actual_links = connection.execute("SELECT COUNT(*) FROM primary_source_links").fetchone()[0]
        actual_attributions = connection.execute("SELECT COUNT(*) FROM primary_source_attributions").fetchone()[0]
        permissions_true = connection.execute(
            "SELECT COUNT(*) FROM primary_sources WHERE can_show_images = 1"
        ).fetchone()[0]
        permissions_false = connection.execute(
            "SELECT COUNT(*) FROM primary_sources WHERE can_show_images = 0"
        ).fetchone()[0]
        actual_preview_resources = connection.execute(
            "SELECT COUNT(*) FROM common_resources WHERE key LIKE 'primary_sources/previews/%'"
        ).fetchone()[0]
        actual_groups = {
            group_kind: count
            for group_kind, count in connection.execute(
                "SELECT group_kind, COUNT(*) FROM primary_sources GROUP BY group_kind"
            ).fetchall()
        }
        zero_page_sources = [
            row[0]
            for row in connection.execute(
                """
                SELECT ps.id
                FROM primary_sources ps
                LEFT JOIN primary_source_pages p ON p.source_id = ps.id
                GROUP BY ps.id
                HAVING COUNT(p.page_name) = 0
                ORDER BY ps.id
                """
            ).fetchall()
        ]
        overlay_sources = [
            row[0]
            for row in connection.execute(
                """
                SELECT ps.id
                FROM primary_sources ps
                LEFT JOIN primary_source_words w ON w.source_id = ps.id
                LEFT JOIN primary_source_verses v ON v.source_id = ps.id
                GROUP BY ps.id
                HAVING COUNT(w.word_index) > 0 OR COUNT(v.verse_index) > 0
                ORDER BY ps.id
                """
            ).fetchall()
        ]
        rectangles = 0
        for (rectangles_json,) in connection.execute("SELECT rectangles_json FROM primary_source_words"):
            rectangles += len(json.loads(rectangles_json))

    actual = {
        "sources": actual_sources,
        "pages": actual_pages,
        "words": actual_words,
        "rectangles": rectangles,
        "verses": actual_verses,
        "permissions_true": permissions_true,
        "permissions_false": permissions_false,
        "groups": {
            "full": actual_groups.get("full", 0),
            "significant": actual_groups.get("significant", 0),
            "fragment": actual_groups.get("fragment", 0),
        },
        "zero_page_sources": zero_page_sources,
        "overlay_sources": overlay_sources,
        "links": actual_links,
        "attributions": actual_attributions,
        "preview_resources": actual_preview_resources,
    }

    if actual != expected:
        raise RuntimeError(
            "Валидация common DB не прошла.\n"
            f"Ожидалось: {json.dumps(expected, ensure_ascii=False, indent=2)}\n"
            f"Получено: {json.dumps(actual, ensure_ascii=False, indent=2)}"
        )
    return actual


def validate_localized_db(localized_db_path: Path, expected_rows: int) -> dict[str, int]:
    with sqlite3.connect(localized_db_path) as connection:
        actual_texts = connection.execute("SELECT COUNT(*) FROM primary_source_texts").fetchone()[0]
        actual_link_texts = connection.execute("SELECT COUNT(*) FROM primary_source_link_texts").fetchone()[0]
    if actual_texts != expected_rows or actual_link_texts != 0:
        raise RuntimeError(
            f"Валидация localized DB не прошла для {localized_db_path.name}: "
            f"primary_source_texts={actual_texts}, primary_source_link_texts={actual_link_texts}, "
            f"ожидалось {expected_rows} и 0"
        )
    return {
        "primary_source_texts": actual_texts,
        "primary_source_link_texts": actual_link_texts,
    }


def build_report(
    dataset: ParsedDataset,
    localized_rows: dict[str, list[dict[str, str]]],
    db_dir: Path,
    apply: bool,
    backup_dir: Path | None,
    validation: dict[str, Any] | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "repository": str(dataset.repository_path),
        "preview_dir": str(dataset.preview_dir),
        "db_dir": str(db_dir),
        "backup_dir": str(backup_dir) if backup_dir else None,
        "parsed_totals": calculate_dataset_totals(dataset),
        "localized_rows": {locale: len(rows) for locale, rows in localized_rows.items()},
    }
    if validation is not None:
        report["validation"] = validation
    return report


def print_summary(report: dict[str, Any]) -> None:
    totals = report["parsed_totals"]
    print(f"Mode: {report['mode']}")
    print(f"Repository: {report['repository']}")
    print(f"Preview dir: {report['preview_dir']}")
    print(f"DB dir: {report['db_dir']}")
    if report["backup_dir"]:
        print(f"Backup dir: {report['backup_dir']}")
    print(f"Sources: {totals['sources']}")
    print(
        "Groups: "
        f"full={totals['groups']['full']}, "
        f"significant={totals['groups']['significant']}, "
        f"fragment={totals['groups']['fragment']}"
    )
    print(
        f"Pages={totals['pages']}, Words={totals['words']}, "
        f"Rectangles={totals['rectangles']}, Verses={totals['verses']}"
    )
    print(
        f"Permissions: true={totals['permissions_true']}, "
        f"false={totals['permissions_false']}"
    )
    print(
        f"Links={totals['links']}, "
        f"Attributions={totals['attributions']}, "
        f"Preview resources={totals['preview_resources']}"
    )
    print(f"Zero-page sources: {', '.join(totals['zero_page_sources']) or '-'}")
    print(f"Overlay sources: {', '.join(totals['overlay_sources']) or '-'}")
    print(
        "Localized rows: "
        + ", ".join(f"{locale}={count}" for locale, count in report["localized_rows"].items())
    )
    if "validation" in report:
        print("Validation: OK")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate the legacy primary sources snapshot into revelation SQLite databases."
    )
    parser.add_argument(
        "--repository",
        type=Path,
        default=default_repository_path(),
        help="Path to the legacy primary_sources_repository.dart.txt snapshot",
    )
    parser.add_argument(
        "--l10n-dir",
        type=Path,
        default=default_l10n_dir(),
        help="Path to lib/l10n directory containing app_<lang>.arb files",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=default_preview_dir(),
        help="Path to preview image directory",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        default=default_db_dir(),
        help="Path to directory with revelation*.sqlite files",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=None,
        help="Where to store DB backups when --apply is used (default: <db-dir>/backups)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write into the SQLite databases. Without this flag the script only validates and prints the plan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the final report as JSON.",
    )
    return parser.parse_args()


def ensure_target_db_files_exist(db_dir: Path) -> dict[str, Path]:
    result = {"common": db_dir / "revelation.sqlite"}
    for locale in LOCALES:
        result[locale] = db_dir / f"revelation_{locale}.sqlite"
    missing = [path for path in result.values() if not path.exists()]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Не найдены ожидаемые БД: {joined}")
    return result


def main() -> int:
    args = parse_args()
    repository_path = args.repository.resolve()
    l10n_dir = args.l10n_dir.resolve()
    preview_dir = args.preview_dir.resolve()
    db_dir = args.db_dir.resolve()
    backup_root = (args.backup_root.resolve() if args.backup_root else default_backup_root(db_dir))

    dataset = parse_repository(repository_path, preview_dir)
    arb_by_locale = {
        locale: load_arb((l10n_dir / f"app_{locale}.arb").resolve())
        for locale in LOCALES
    }
    localized_rows = collect_localized_rows(dataset, arb_by_locale)
    db_paths = ensure_target_db_files_exist(db_dir)

    backup_dir: Path | None = None
    validation: dict[str, Any] | None = None

    if args.apply:
        backup_dir = backup_databases(list(db_paths.values()), backup_root)
        write_common_db(db_paths["common"], dataset)
        for locale in LOCALES:
            write_localized_db(db_paths[locale], localized_rows[locale])

        expected = calculate_dataset_totals(dataset)
        validation = {
            "common": validate_common_db(db_paths["common"], expected),
            "localized": {
                locale: validate_localized_db(db_paths[locale], len(localized_rows[locale]))
                for locale in LOCALES
            },
        }

    report = build_report(
        dataset=dataset,
        localized_rows=localized_rows,
        db_dir=db_dir,
        apply=args.apply,
        backup_dir=backup_dir,
        validation=validation,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

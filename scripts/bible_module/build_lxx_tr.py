from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .canon import CANON_NAME, CanonicalVerse, canonical_verses, parse_canonical_ref
from .fetch_sources import load_manifest, verify_source_manifest
from .lxx import (
    CROSSWIRE_LXX_SOURCE_ID,
    _canonical_verse_for_lxx_source_verse,
    LxxSourceVerse,
    iter_crosswire_lxx_source_verses,
)
from .schema import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    DB_METADATA_SCHEMA_VERSION_KEY,
    now_utc_iso,
)
from .sources import DEFAULT_SOURCE_LOCK_PATH
from .tagnt import TagntToken, normalize_strong, parse_tagnt_row

MODULE_ID = "lxx_tr"
MODULE_CODE = "LXX_TR"
MODULE_TITLE = "LXX / Textus Receptus Greek Bible Module"
DEFAULT_TARGET_PATH = (
    Path.home() / "Documents" / "revelation" / "db" / "bible_lxx_tr.sqlite"
)

LXX_TR_SCHEMA_VERSION = 3
LXX_TR_DATA_VERSION_INITIAL = 4
MODULE_LICENSE_SUMMARY = (
    "STEPBible CC BY 4.0 for TAGNT Textus Receptus data; "
    "CrossWire LXX Copyrighted; Free non-commercial distribution for OT LXX data."
)

TAGNT_LOCKED_SOURCE_IDS = ("step_tagnt_mat_jhn", "step_tagnt_act_rev")

_BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_STRONG_TOKEN_PATTERN = re.compile(r"^G[1-9][0-9]*$")
_LXX_STRONG_ATTR_PATTERN = re.compile(r"strong:([GH]\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?)")
_TAGNT_ANNOTATED_REFERENCE_PATTERN = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]+)\."
    r"(?P<chapter>\d+)\."
    r"(?P<verse>\d+)"
    r"(?P<open_marker>[\[\{\(])"
    r"(?P<alternate_chapter>\d+)\."
    r"(?P<alternate_verse>\d+)"
    r"(?P<close_marker>[\]\}\)])#"
    r"(?P<token_order>\d+)="
    r"(?P<text_type>\S+)$"
)
_LEADING_MARKS = set("([{\"'") | {"\u00ab", "\u201c", "\u2018"}
_TRAILING_MARKS = set(",.;:!?])}\"'") | {
    "\u00b7",
    "\u00b6",
    "\u00bb",
    "\u037e",
    "\u0387",
    "\u2019",
    "\u201d",
    "\u2026",
}

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


@dataclass(frozen=True)
class MissingStrongToken:
    source_ref: str
    surface: str
    editions: tuple[str, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "source_ref": self.source_ref,
            "surface": self.surface,
            "editions": list(self.editions),
        }


@dataclass(frozen=True)
class TrTextBuildResult:
    verse_texts_by_id: Mapping[int, str]
    tr_tokens_count: int
    missing_tr_verses: tuple[str, ...]
    extra_tr_verses: tuple[str, ...]
    missing_strong_tokens: tuple[MissingStrongToken, ...]

    @property
    def filled_verses_count(self) -> int:
        return len(self.verse_texts_by_id)


@dataclass(frozen=True)
class LxxProjectionSpan:
    source_ref: str
    segment_index: int | None = None
    sub_type: str | None = None
    token_start: int | None = None
    token_end: int | None = None


@dataclass(frozen=True)
class LxxProjectionRule:
    target_ref: str
    spans: tuple[LxxProjectionSpan, ...] = ()
    tagged_text: str | None = None
    status: str = "manual_token_span_projection"
    note: str = ""


@dataclass(frozen=True)
class LxxProjectionPlan:
    rules: tuple[LxxProjectionRule, ...]
    source_exclusions: tuple[str, ...] = ()
    info_source_summary_notes: tuple[str, ...] = ()
    info_license_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class LxxTaggedWord:
    source_ref: str
    token_order: int
    surface: str
    primary_strong: str | None


@dataclass(frozen=True)
class LxxTextBuildResult:
    verse_texts_by_id: Mapping[int, str]
    lxx_tokens_count: int
    missing_lxx_verses: tuple[str, ...]
    extra_lxx_verses: tuple[str, ...]
    missing_strong_tokens: tuple[MissingStrongToken, ...]
    duplicate_target_refs: tuple[str, ...]

    @property
    def filled_verses_count(self) -> int:
        return len(self.verse_texts_by_id)


@dataclass(frozen=True)
class LxxTrBuildReport:
    target_path: Path
    backup_path: Path | None
    verses_count: int
    filled_verses_count: int
    empty_verses_count: int
    tr_tokens_count: int
    lxx_tokens_count: int
    missing_tr_verses: tuple[str, ...]
    extra_tr_verses: tuple[str, ...]
    missing_lxx_verses: tuple[str, ...]
    extra_lxx_verses: tuple[str, ...]
    missing_strong_tokens: tuple[MissingStrongToken, ...]
    duplicate_lxx_target_refs: tuple[str, ...]
    built_at: str


def build_lxx_tr_module(
    *,
    target_path: Path = DEFAULT_TARGET_PATH,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    lxx_projection_rules_path: Path | Sequence[Path] | None = None,
    data_version: int = LXX_TR_DATA_VERSION_INITIAL,
    built_at: str | None = None,
) -> LxxTrBuildReport:
    manifest = _load_verified_manifest(manifest_path)
    source_paths = _source_paths_by_id(manifest, manifest_path)
    tagnt_paths = [source_paths[source_id] for source_id in TAGNT_LOCKED_SOURCE_IDS]
    crosswire_lxx_path = source_paths[CROSSWIRE_LXX_SOURCE_ID]
    lxx_projection_plan = load_lxx_projection_plan(lxx_projection_rules_path)
    return build_lxx_tr_module_from_tokens(
        target_path=target_path,
        tr_source_tokens=iter_lxx_tr_tagnt_tokens(tagnt_paths),
        lxx_source_verses=iter_crosswire_lxx_source_verses(crosswire_lxx_path),
        lxx_projection_rules=lxx_projection_plan.rules,
        lxx_source_exclusions=lxx_projection_plan.source_exclusions,
        include_identity_lxx_projection=True,
        source_summary=_source_summary(
            manifest,
            additional_notes=lxx_projection_plan.info_source_summary_notes,
        ),
        license_summary=_license_summary(lxx_projection_plan.info_license_notes),
        data_version=data_version,
        built_at=built_at,
    )


def iter_lxx_tr_tagnt_tokens(paths: Iterable[str | Path]) -> Iterator[TagntToken]:
    for path in paths:
        source_path = Path(path)
        with source_path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                normalized_line = _normalize_lxx_tr_tagnt_line(line)
                if normalized_line is None:
                    continue
                token = parse_tagnt_row(
                    normalized_line,
                    source_path=source_path,
                    line_number=line_number,
                )
                if token is not None:
                    yield token


def _normalize_lxx_tr_tagnt_line(line: str) -> str | None:
    columns = line.rstrip("\r\n").split("\t")
    if not columns:
        return line

    raw_reference = columns[0].lstrip("\ufeff").strip()
    match = _TAGNT_ANNOTATED_REFERENCE_PATTERN.match(raw_reference)
    if match is None:
        return line

    if _is_lxx_tr_subscription_tail(match, columns):
        return None

    if not _has_matching_verse_marker(match):
        return line

    # TAGNT uses NRSV as its base reference. Square brackets carry the KJV
    # verse number, while round/curly markers point to non-KJV alternatives.
    if match.group("open_marker") == "[":
        chapter = match.group("alternate_chapter")
        verse = match.group("alternate_verse")
    else:
        chapter = match.group("chapter")
        verse = match.group("verse")

    columns[0] = (
        f"{match.group('book')}.{chapter}.{verse}"
        f"#{match.group('token_order')}={match.group('text_type')}"
    )
    return "\t".join(columns)


def _has_matching_verse_marker(match: re.Match[str]) -> bool:
    return {
        "[": "]",
        "{": "}",
        "(": ")",
    }.get(match.group("open_marker")) == match.group("close_marker")


def _is_lxx_tr_subscription_tail(
    match: re.Match[str],
    columns: Sequence[str],
) -> bool:
    if match.group("text_type") != "K":
        return False
    if _tagnt_column(columns, 5) != "TR":
        return False

    tail_starts = {
        ("Rom", "16", "27", "{"): 14,
        ("2Co", "13", "13", "["): 22,
    }
    key = (
        match.group("book"),
        match.group("chapter"),
        match.group("verse"),
        match.group("open_marker"),
    )
    tail_start = tail_starts.get(key)
    if tail_start is None:
        return False
    return int(match.group("token_order")) >= tail_start


def _tagnt_column(columns: Sequence[str], index: int) -> str:
    if index >= len(columns):
        return ""
    return columns[index].strip()


def build_lxx_tr_module_from_tokens(
    *,
    target_path: Path,
    tr_source_tokens: Iterable[TagntToken],
    lxx_source_verses: Iterable[LxxSourceVerse] | None = None,
    lxx_projection_rules: Sequence[LxxProjectionRule] = (),
    lxx_source_exclusions: Sequence[str] = (),
    include_identity_lxx_projection: bool = False,
    source_summary: str,
    license_summary: str = MODULE_LICENSE_SUMMARY,
    data_version: int = LXX_TR_DATA_VERSION_INITIAL,
    built_at: str | None = None,
) -> LxxTrBuildReport:
    target_path = target_path.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    actual_built_at = built_at or now_utc_iso()
    timestamp = _filesystem_timestamp(actual_built_at)
    temp_path = _new_temp_db_path(target_path)
    backup_path: Path | None = None

    tr_texts = build_tr_verse_texts(tr_source_tokens)
    lxx_texts = build_lxx_verse_texts(
        lxx_source_verses or (),
        projection_rules=lxx_projection_rules,
        source_exclusions=lxx_source_exclusions,
        include_identity_projection=include_identity_lxx_projection,
    )
    combined_texts = _combine_verse_texts(tr_texts, lxx_texts)

    try:
        connection = sqlite3.connect(str(temp_path))
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN")
            create_lxx_tr_schema(
                connection,
                data_version=data_version,
                date_iso=actual_built_at,
                source_summary=source_summary,
                license_summary=license_summary,
            )
            _apply_verse_texts(connection, combined_texts)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        _vacuum_lxx_tr_database(temp_path)
        validate_lxx_tr_database(temp_path)
        if target_path.exists():
            backup_path = target_path.with_name(f"{target_path.name}.{timestamp}.bak")
            shutil.copy2(target_path, backup_path)
        temp_path.replace(target_path)
        validate_lxx_tr_database(target_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    verses_count = len(canonical_verses())
    filled_verses_count = len(combined_texts)
    return LxxTrBuildReport(
        target_path=target_path,
        backup_path=backup_path,
        verses_count=verses_count,
        filled_verses_count=filled_verses_count,
        empty_verses_count=verses_count - filled_verses_count,
        tr_tokens_count=tr_texts.tr_tokens_count,
        lxx_tokens_count=lxx_texts.lxx_tokens_count,
        missing_tr_verses=tr_texts.missing_tr_verses,
        extra_tr_verses=tr_texts.extra_tr_verses,
        missing_lxx_verses=lxx_texts.missing_lxx_verses,
        extra_lxx_verses=lxx_texts.extra_lxx_verses,
        missing_strong_tokens=(
            tr_texts.missing_strong_tokens + lxx_texts.missing_strong_tokens
        ),
        duplicate_lxx_target_refs=lxx_texts.duplicate_target_refs,
        built_at=actual_built_at,
    )


def create_lxx_tr_schema(
    connection: sqlite3.Connection,
    *,
    data_version: int,
    date_iso: str,
    source_summary: str,
    license_summary: str = MODULE_LICENSE_SUMMARY,
) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA user_version = {LXX_TR_SCHEMA_VERSION}")
    connection.executescript(SCHEMA_SQL)
    connection.executemany(
        """
        INSERT INTO db_metadata(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        [
            (DB_METADATA_SCHEMA_VERSION_KEY, str(LXX_TR_SCHEMA_VERSION)),
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
                "KJV/protestant 66-book Greek Bible module scaffold. "
                "New Testament is filled from STEPBible TAGNT Textus Receptus; "
                "Old Testament LXX text is filled from owner-approved CrossWire "
                "LXX projection rules when those rules are supplied."
            ),
            "grc",
            CANON_NAME,
            "kjv_protestant",
            license_summary,
            source_summary,
        ),
    )
    connection.executemany(
        """
        INSERT INTO verses(verse_key, text)
        VALUES(?, '')
        """,
        [
            (verse_key_for(canonical_verse),)
            for canonical_verse in canonical_verses()
        ],
    )


def build_tr_verse_texts(tokens: Iterable[TagntToken]) -> TrTextBuildResult:
    expected_nt_refs = {
        canonical_verse.canonical_ref: canonical_verse
        for canonical_verse in canonical_verses()
        if canonical_verse.book_id >= 40
    }
    expected_nt_ref_set = set(expected_nt_refs)
    canonical_by_id = {
        canonical_verse.canonical_verse_id: canonical_verse
        for canonical_verse in canonical_verses()
    }
    grouped: dict[int, list[tuple[TagntToken, str | None]]] = defaultdict(list)
    actual_refs: set[str] = set()
    extra_refs: set[str] = set()
    missing_strong_tokens: list[MissingStrongToken] = []
    tr_tokens_count = 0

    for token in tokens:
        if not _is_textus_receptus_token(token):
            continue

        tr_tokens_count += 1
        canonical_verse = token.canonical_verse
        canonical_ref = canonical_verse.canonical_ref
        if canonical_ref not in expected_nt_ref_set:
            extra_refs.add(canonical_ref)
            continue

        actual_refs.add(canonical_ref)
        primary_strong = _primary_strong_for_token(token)
        if primary_strong is None:
            missing_strong_tokens.append(
                MissingStrongToken(
                    source_ref=token.source_ref,
                    surface=token.surface,
                    editions=token.editions,
                )
            )
        grouped[canonical_verse.canonical_verse_id].append((token, primary_strong))

    verse_texts: dict[int, str] = {}
    for canonical_verse_id, verse_tokens in grouped.items():
        verse_tokens.sort(
            key=lambda item: (
                item[0].reference.token_order,
                item[0].source_ref,
            )
        )
        verse_texts[canonical_verse_id] = _join_tagged_tokens(verse_tokens)

    missing_refs = tuple(
        sorted(
            expected_nt_ref_set - actual_refs,
            key=lambda canonical_ref: expected_nt_refs[canonical_ref].sort_key,
        )
    )
    extra_ref_values = tuple(
        sorted(
            extra_refs,
            key=lambda canonical_ref: expected_nt_refs.get(
                canonical_ref,
                canonical_by_id[min(canonical_by_id)],
            ).sort_key,
        )
    )
    return TrTextBuildResult(
        verse_texts_by_id=verse_texts,
        tr_tokens_count=tr_tokens_count,
        missing_tr_verses=missing_refs,
        extra_tr_verses=extra_ref_values,
        missing_strong_tokens=tuple(missing_strong_tokens),
    )


def build_lxx_verse_texts(
    source_verses: Iterable[LxxSourceVerse],
    *,
    projection_rules: Sequence[LxxProjectionRule],
    source_exclusions: Sequence[str] = (),
    include_identity_projection: bool = False,
) -> LxxTextBuildResult:
    expected_ot_refs = {
        canonical_verse.canonical_ref: canonical_verse
        for canonical_verse in canonical_verses()
        if canonical_verse.book_id < 40
    }
    expected_ot_ref_set = set(expected_ot_refs)
    source_by_ref = {source_verse.native_ref: source_verse for source_verse in source_verses}
    excluded_source_refs = set(source_exclusions)
    explicit_source_refs = {
        span.source_ref for rule in projection_rules for span in rule.spans
    }
    explicit_target_refs = {
        rule.target_ref
        for rule in projection_rules
        if isinstance(rule.target_ref, str) and rule.target_ref
    }

    grouped: dict[int, list[LxxTaggedWord]] = defaultdict(list)
    literal_texts: dict[int, str] = {}
    actual_refs: set[str] = set()
    extra_refs: set[str] = set()
    missing_refs: set[str] = set()
    duplicate_target_refs: set[str] = set()
    missing_strong_tokens: list[MissingStrongToken] = []
    lxx_tokens_count = 0

    for rule in projection_rules:
        try:
            canonical_verse = parse_canonical_ref(rule.target_ref)
        except KeyError:
            extra_refs.add(rule.target_ref)
            continue

        if canonical_verse.canonical_ref not in expected_ot_ref_set:
            extra_refs.add(canonical_verse.canonical_ref)
            continue
        if canonical_verse.canonical_ref in actual_refs:
            duplicate_target_refs.add(canonical_verse.canonical_ref)
            continue

        if rule.tagged_text is not None:
            if rule.spans:
                raise ValueError(
                    "LXX projection rule must not mix spans and tagged_text: "
                    f"{canonical_verse.canonical_ref}"
                )
            tagged_text = rule.tagged_text.strip()
            if not tagged_text or not is_valid_tagged_text(tagged_text):
                raise ValueError(
                    "LXX projection tagged_text must use alternating word/Strong format: "
                    f"{canonical_verse.canonical_ref}"
                )
            actual_refs.add(canonical_verse.canonical_ref)
            literal_texts[canonical_verse.canonical_verse_id] = tagged_text
            literal_words = _literal_tagged_words(tagged_text)
            lxx_tokens_count += len(literal_words)
            missing_strong_tokens.extend(
                _literal_missing_strong_tokens(
                    rule=rule,
                    tagged_text=tagged_text,
                )
            )
            continue

        words: list[LxxTaggedWord] = []
        for span in rule.spans:
            source_verse = source_by_ref.get(span.source_ref)
            if source_verse is None:
                missing_refs.add(canonical_verse.canonical_ref)
                words = []
                break
            span_words = _extract_lxx_span_words(source_verse, span)
            words.extend(span_words)

        if not words:
            missing_refs.add(canonical_verse.canonical_ref)
            continue

        actual_refs.add(canonical_verse.canonical_ref)
        grouped[canonical_verse.canonical_verse_id].extend(words)
        lxx_tokens_count += len(words)
        for word in words:
            if word.primary_strong is None:
                missing_strong_tokens.append(
                    MissingStrongToken(
                        source_ref=f"{word.source_ref}#{word.token_order}",
                        surface=word.surface,
                        editions=("CrossWire LXX",),
                    )
                )

    if include_identity_projection:
        for source_verse in source_by_ref.values():
            if source_verse.native_ref in excluded_source_refs:
                continue
            if source_verse.native_ref in explicit_source_refs:
                continue
            canonical_verse = _identity_projection_target(source_verse)
            if canonical_verse is None:
                continue
            canonical_ref = canonical_verse.canonical_ref
            if canonical_ref in explicit_target_refs or canonical_ref in actual_refs:
                continue
            if canonical_ref not in expected_ot_ref_set:
                extra_refs.add(canonical_ref)
                continue
            if _has_parallel_lxx_variant_segments(source_verse):
                continue

            words = _extract_lxx_span_words(
                source_verse,
                LxxProjectionSpan(source_ref=source_verse.native_ref),
            )
            if not words:
                continue
            actual_refs.add(canonical_ref)
            grouped[canonical_verse.canonical_verse_id].extend(words)
            lxx_tokens_count += len(words)
            for word in words:
                if word.primary_strong is None:
                    missing_strong_tokens.append(
                        MissingStrongToken(
                            source_ref=f"{word.source_ref}#{word.token_order}",
                            surface=word.surface,
                            editions=("CrossWire LXX",),
                        )
                    )

    verse_texts = {
        canonical_verse_id: _join_lxx_tagged_words(words)
        for canonical_verse_id, words in grouped.items()
    }
    verse_texts.update(literal_texts)
    ordered_missing_refs = tuple(
        sorted(
            (expected_ot_ref_set - actual_refs) | missing_refs,
            key=lambda canonical_ref: expected_ot_refs[canonical_ref].sort_key,
        )
    )
    return LxxTextBuildResult(
        verse_texts_by_id=verse_texts,
        lxx_tokens_count=lxx_tokens_count,
        missing_lxx_verses=ordered_missing_refs,
        extra_lxx_verses=tuple(sorted(extra_refs)),
        missing_strong_tokens=tuple(missing_strong_tokens),
        duplicate_target_refs=tuple(sorted(duplicate_target_refs)),
    )


def load_lxx_projection_rules(
    path: Path | Sequence[Path] | None,
) -> tuple[LxxProjectionRule, ...]:
    return load_lxx_projection_plan(path).rules


def load_lxx_projection_plan(path: Path | Sequence[Path] | None) -> LxxProjectionPlan:
    if path is None:
        return LxxProjectionPlan(rules=())
    if isinstance(path, Sequence) and not isinstance(path, (str, bytes, Path)):
        plans = [load_lxx_projection_plan(item) for item in path]
        return LxxProjectionPlan(
            rules=tuple(rule for plan in plans for rule in plan.rules),
            source_exclusions=tuple(
                sorted(
                    {
                        source_ref
                        for plan in plans
                        for source_ref in plan.source_exclusions
                    }
                )
            ),
            info_source_summary_notes=_merge_projection_notes(
                plans,
                "info_source_summary_notes",
            ),
            info_license_notes=_merge_projection_notes(
                plans,
                "info_license_notes",
            ),
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, Mapping) and isinstance(data.get("projection_inputs"), Mapping):
        return _projection_plan_from_consolidated_mapping(data["projection_inputs"])
    return _projection_plan_from_mapping(data)


def _projection_plan_from_consolidated_mapping(
    projection_inputs: Mapping[str, object],
) -> LxxProjectionPlan:
    plans: list[LxxProjectionPlan] = []
    for key in (
        "versification_candidate_map",
        "token_span_rules_generated",
        "token_span_rules_manual",
    ):
        entry = projection_inputs.get(key)
        if not isinstance(entry, Mapping):
            continue
        content = entry.get("content")
        if isinstance(content, Mapping):
            plans.append(_projection_plan_from_mapping(content))

    return LxxProjectionPlan(
        rules=tuple(rule for plan in plans for rule in plan.rules),
        source_exclusions=tuple(
            sorted(
                {
                    source_ref
                    for plan in plans
                    for source_ref in plan.source_exclusions
                }
            )
        ),
        info_source_summary_notes=_merge_projection_notes(
            plans,
            "info_source_summary_notes",
        ),
        info_license_notes=_merge_projection_notes(
            plans,
            "info_license_notes",
        ),
    )


def _projection_plan_from_mapping(data: Mapping[str, object]) -> LxxProjectionPlan:
    if not isinstance(data, Mapping):
        raise ValueError("LXX projection rules file must contain a JSON object")

    rules_value = data.get("rules")
    source_exclusions: tuple[str, ...] = ()
    if rules_value is None and isinstance(data.get("groups"), list):
        groups = data["groups"]
        rules_value = _whole_verse_rules_from_candidate_groups(groups)
        source_exclusions = tuple(sorted(_source_exclusions_from_candidate_groups(groups)))
    if not isinstance(rules_value, list):
        raise ValueError("LXX projection rules file must contain a rules array")

    explicit_source_exclusions = data.get("source_exclusions")
    if isinstance(explicit_source_exclusions, list):
        source_exclusions = tuple(
            sorted(
                set(source_exclusions).union(
                    item for item in explicit_source_exclusions if isinstance(item, str)
                )
            )
        )

    return LxxProjectionPlan(
        rules=tuple(_parse_lxx_projection_rule(entry) for entry in rules_value),
        source_exclusions=source_exclusions,
        info_source_summary_notes=_projection_metadata_notes(
            data,
            "info_source_summary_notes",
        ),
        info_license_notes=_projection_metadata_notes(
            data,
            "info_license_notes",
        ),
    )


def _merge_projection_notes(
    plans: Sequence[LxxProjectionPlan],
    attribute: str,
) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            note
            for plan in plans
            for note in getattr(plan, attribute)
        )
    )


def _projection_metadata_notes(
    data: Mapping[str, object],
    key: str,
) -> tuple[str, ...]:
    metadata = data.get("metadata")
    value = metadata.get(key) if isinstance(metadata, Mapping) else None
    if value is None:
        return ()
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip()
        for item in value
    ):
        raise ValueError(f"LXX projection metadata {key} must contain strings")
    return tuple(item.strip() for item in value)


def validate_lxx_tr_database(db_path: Path) -> None:
    connection = sqlite3.connect(str(db_path))
    try:
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if user_version != LXX_TR_SCHEMA_VERSION:
            raise ValueError(f"Unexpected LXX_TR user_version: {user_version}")

        table_names = {
            str(row[0])
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }
        expected_tables = {"db_metadata", "info", "verses"}
        if table_names != expected_tables:
            raise ValueError(
                "LXX_TR table set mismatch: "
                f"expected {sorted(expected_tables)}, got {sorted(table_names)}"
            )

        verse_columns = [
            str(row[1])
            for row in connection.execute("PRAGMA table_info(verses)").fetchall()
        ]
        if verse_columns != ["verse_key", "text"]:
            raise ValueError(f"LXX_TR verses columns mismatch: {verse_columns}")

        info_columns = [
            str(row[1])
            for row in connection.execute("PRAGMA table_info(info)").fetchall()
        ]
        expected_info_columns = [
            "code",
            "module_id",
            "title",
            "description",
            "language",
            "canon",
            "versification",
            "license",
            "source_summary",
        ]
        if info_columns != expected_info_columns:
            raise ValueError(f"LXX_TR info columns mismatch: {info_columns}")

        metadata = dict(connection.execute("SELECT key, value FROM db_metadata"))
        if metadata.get(DB_METADATA_SCHEMA_VERSION_KEY) != str(LXX_TR_SCHEMA_VERSION):
            raise ValueError("LXX_TR db_metadata.schema_version mismatch")

        info_count = int(connection.execute("SELECT COUNT(*) FROM info").fetchone()[0])
        if info_count != 1:
            raise ValueError(f"LXX_TR info must contain one row, got {info_count}")

        verses_count = int(
            connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        )
        expected_verses_count = len(canonical_verses())
        if verses_count != expected_verses_count:
            raise ValueError(
                f"LXX_TR must contain {expected_verses_count} verses, got {verses_count}"
            )

        verse_keys_count = int(
            connection.execute("SELECT COUNT(DISTINCT verse_key) FROM verses").fetchone()[0]
        )
        if verse_keys_count != expected_verses_count:
            raise ValueError("LXX_TR verse_key values are not unique")
        invalid_key_lengths_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM verses WHERE length(verse_key) != 3"
            ).fetchone()[0]
        )
        if invalid_key_lengths_count:
            raise ValueError("LXX_TR verse_key values must be exactly 3 characters")

        ordered_keys = [
            str(row[0])
            for row in connection.execute(
                """
                SELECT verse_key
                FROM verses
                ORDER BY verse_key
                """
            )
        ]
        expected_keys = [
            _base36(index).rjust(3, "0")
            for index in range(1, expected_verses_count + 1)
        ]
        if ordered_keys != expected_keys:
            raise ValueError("LXX_TR verse_key values are not sequential base36 keys")

        invalid_text_rows = connection.execute(
            """
            SELECT verse_key, text
            FROM verses
            WHERE verses.text <> ''
            ORDER BY verse_key
            """
        ).fetchall()
        for verse_key, text in invalid_text_rows:
            if not is_valid_tagged_text(str(text)):
                raise ValueError(
                    "LXX_TR verse text is not alternating word/Strong format: "
                    f"{verse_key}"
                )
    finally:
        connection.close()


def verse_key_for(canonical_verse: CanonicalVerse) -> str:
    return _verse_key_by_canonical_id()[canonical_verse.canonical_verse_id]


@lru_cache(maxsize=1)
def _verse_key_by_canonical_id() -> dict[int, str]:
    verses = canonical_verses()
    if len(verses) > (36**3 - 1):
        raise ValueError("Three-character base36 verse_key cannot fit the canon")
    return {
        canonical_verse.canonical_verse_id: _base36(index).rjust(3, "0")
        for index, canonical_verse in enumerate(verses, start=1)
    }


def is_valid_tagged_text(text: str) -> bool:
    if not text:
        return True
    if "<" in text or ">" in text:
        return False
    parts = text.split()
    previous_token_was_word = False
    for part in parts:
        is_strong = bool(_STRONG_TOKEN_PATTERN.match(part))
        if is_strong:
            if not previous_token_was_word:
                return False
            previous_token_was_word = False
            continue
        previous_token_was_word = True
    return True


def _combine_verse_texts(
    tr_texts: TrTextBuildResult,
    lxx_texts: LxxTextBuildResult,
) -> dict[int, str]:
    combined = dict(lxx_texts.verse_texts_by_id)
    overlap = set(combined).intersection(tr_texts.verse_texts_by_id)
    if overlap:
        refs_by_id = {
            canonical_verse.canonical_verse_id: canonical_verse.canonical_ref
            for canonical_verse in canonical_verses()
        }
        refs = ", ".join(
            refs_by_id[canonical_verse_id]
            for canonical_verse_id in sorted(overlap)
        )
        raise ValueError(f"LXX/TR text overlap is not allowed: {refs}")
    combined.update(tr_texts.verse_texts_by_id)
    return combined


def _apply_verse_texts(
    connection: sqlite3.Connection,
    verse_texts_by_id: Mapping[int, str],
) -> None:
    canonical_by_id = {
        canonical_verse.canonical_verse_id: canonical_verse
        for canonical_verse in canonical_verses()
    }
    rows = []
    for canonical_verse_id, text in sorted(
        verse_texts_by_id.items(),
        key=lambda item: canonical_by_id[item[0]].sort_key,
    ):
        canonical_verse = canonical_by_id[canonical_verse_id]
        rows.append(
            (
                text,
                verse_key_for(canonical_verse),
            )
        )
    connection.executemany(
        """
        UPDATE verses
        SET text = ?
        WHERE verse_key = ?
        """,
        rows,
    )


def _join_tagged_tokens(
    verse_tokens: Sequence[tuple[TagntToken, str | None]],
) -> str:
    parts: list[str] = []
    for token, primary_strong in verse_tokens:
        surface = _word_surface(token.surface)
        if not surface:
            continue
        parts.append(surface)
        if primary_strong is not None:
            parts.append(primary_strong)
    return " ".join(parts)


def _extract_lxx_span_words(
    source_verse: LxxSourceVerse,
    span: LxxProjectionSpan,
) -> list[LxxTaggedWord]:
    elements = _selected_lxx_word_elements(source_verse, span)
    start = span.token_start if span.token_start is not None else 0
    end = span.token_end if span.token_end is not None else len(elements)
    if start < 0 or end < start or end > len(elements):
        raise ValueError(
            "LXX projection token span is out of range: "
            f"{span.source_ref} [{start}:{end}] over {len(elements)} tokens"
        )

    words: list[LxxTaggedWord] = []
    for local_index, element in enumerate(elements[start:end], start=start + 1):
        surface = "".join(element.itertext()).strip()
        surface = _word_surface(surface)
        if not surface:
            continue
        words.append(
            LxxTaggedWord(
                source_ref=source_verse.native_ref,
                token_order=local_index,
                surface=surface,
                primary_strong=_primary_strong_for_lxx_word(element),
            )
        )
    return words


def _selected_lxx_word_elements(
    source_verse: LxxSourceVerse,
    span: LxxProjectionSpan,
) -> list[ET.Element]:
    try:
        root = ET.fromstring(f"<root>{source_verse.raw_osis}</root>")
    except ET.ParseError as error:
        raise ValueError(
            f"Could not parse LXX OSIS for projection span {span.source_ref}: {error}"
        ) from error

    selection_root: ET.Element = root
    if span.segment_index is not None or span.sub_type is not None:
        segments = [
            segment
            for segment_index, segment in enumerate(root.iter("seg"), start=1)
            if (span.segment_index is None or segment_index == span.segment_index)
            and (
                span.sub_type is None
                or segment.attrib.get("subType", "").strip() == span.sub_type
            )
        ]
        if len(segments) != 1:
            raise ValueError(
                "LXX projection segment selector must match exactly one segment: "
                f"{span.source_ref} segment_index={span.segment_index} "
                f"sub_type={span.sub_type!r} matched {len(segments)}"
            )
        selection_root = segments[0]

    return list(selection_root.iter("w"))


def _identity_projection_target(source_verse: LxxSourceVerse) -> CanonicalVerse | None:
    mapping = _canonical_verse_for_lxx_source_verse(source_verse)
    if isinstance(mapping, CanonicalVerse) and mapping.book_id < 40:
        return mapping
    return None


def _has_parallel_lxx_variant_segments(source_verse: LxxSourceVerse) -> bool:
    return '<seg type="x-variant"' in source_verse.raw_osis


def _primary_strong_for_lxx_word(element: ET.Element) -> str | None:
    lemma_attr = element.attrib.get("lemma", "").strip()
    match = _LXX_STRONG_ATTR_PATTERN.search(lemma_attr)
    if match is None:
        return None
    return normalize_strong(match.group(1))


def _join_lxx_tagged_words(words: Sequence[LxxTaggedWord]) -> str:
    parts: list[str] = []
    for word in words:
        if not word.surface:
            continue
        parts.append(word.surface)
        if word.primary_strong is not None:
            parts.append(word.primary_strong)
    return " ".join(parts)


def _literal_tagged_words(tagged_text: str) -> tuple[str, ...]:
    return tuple(
        part
        for part in tagged_text.split()
        if not _STRONG_TOKEN_PATTERN.match(part)
    )


def _literal_missing_strong_tokens(
    *,
    rule: LxxProjectionRule,
    tagged_text: str,
) -> tuple[MissingStrongToken, ...]:
    parts = tagged_text.split()
    missing: list[MissingStrongToken] = []
    word_order = 0
    for index, part in enumerate(parts):
        if _STRONG_TOKEN_PATTERN.match(part):
            continue
        word_order += 1
        next_part = parts[index + 1] if index + 1 < len(parts) else None
        if next_part is not None and _STRONG_TOKEN_PATTERN.match(next_part):
            continue
        missing.append(
            MissingStrongToken(
                source_ref=f"{rule.target_ref}#literal:{word_order}",
                surface=part,
                editions=(rule.status,),
            )
        )
    return tuple(missing)


def _parse_lxx_projection_rule(entry: object) -> LxxProjectionRule:
    if not isinstance(entry, Mapping):
        raise ValueError("LXX projection rule entries must be JSON objects")
    target_ref = entry.get("target_ref")
    spans_value = entry.get("spans")
    tagged_text = _optional_str(entry.get("tagged_text"), "tagged_text")
    if not isinstance(target_ref, str) or not target_ref:
        raise ValueError("LXX projection rule target_ref must be a non-empty string")
    if tagged_text is not None:
        if spans_value is not None:
            raise ValueError(
                f"LXX projection rule {target_ref} must not mix spans and tagged_text"
            )
        if not tagged_text.strip() or not is_valid_tagged_text(tagged_text):
            raise ValueError(
                f"LXX projection rule {target_ref} tagged_text is invalid"
            )
    elif not isinstance(spans_value, list) or not spans_value:
        raise ValueError(
            f"LXX projection rule {target_ref} must contain spans or tagged_text"
        )
    return LxxProjectionRule(
        target_ref=target_ref,
        spans=(
            tuple(_parse_lxx_projection_span(span) for span in spans_value)
            if isinstance(spans_value, list)
            else ()
        ),
        tagged_text=tagged_text,
        status=str(entry.get("status") or "manual_token_span_projection"),
        note=str(entry.get("note") or ""),
    )


def _parse_lxx_projection_span(entry: object) -> LxxProjectionSpan:
    if not isinstance(entry, Mapping):
        raise ValueError("LXX projection span entries must be JSON objects")
    source_ref = entry.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref:
        raise ValueError("LXX projection span source_ref must be a non-empty string")
    return LxxProjectionSpan(
        source_ref=source_ref,
        segment_index=_optional_int(entry.get("segment_index"), "segment_index"),
        sub_type=_optional_str(entry.get("sub_type"), "sub_type"),
        token_start=_optional_int(entry.get("token_start"), "token_start"),
        token_end=_optional_int(entry.get("token_end"), "token_end"),
    )


def _whole_verse_rules_from_candidate_groups(
    groups: Sequence[object],
) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        pairs = group.get("pairs")
        if not isinstance(pairs, list):
            continue
        status = str(group.get("status") or "candidate_whole_source_projection")
        note = str(group.get("id") or "")
        kind = str(group.get("kind") or "")
        for pair in pairs:
            if not isinstance(pair, Mapping):
                continue
            source_ref = pair.get("source_ref")
            target_ref = pair.get("target_ref")
            if not isinstance(source_ref, str) or not isinstance(target_ref, str):
                continue
            rule: dict[str, object] = {
                "target_ref": target_ref,
                "status": status,
                "note": note,
                "spans": [{"source_ref": source_ref}],
            }
            if "theodotion_x2" in kind:
                span = rule["spans"][0]
                assert isinstance(span, dict)
                span["sub_type"] = "x-2"
            source_segment = pair.get("source_segment")
            if isinstance(source_segment, Mapping):
                span = rule["spans"][0]
                assert isinstance(span, dict)
                segment_index = source_segment.get("segment_index")
                if isinstance(segment_index, int):
                    span["segment_index"] = segment_index
                sub_type = source_segment.get("sub_type") or source_segment.get("subType")
                if isinstance(sub_type, str):
                    span["sub_type"] = sub_type
            rules.append(rule)
    return rules


def _source_exclusions_from_candidate_groups(groups: Sequence[object]) -> set[str]:
    source_exclusions: set[str] = set()
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        kind = str(group.get("kind") or "")
        if not kind.startswith("source_exclusion"):
            continue
        source_refs = group.get("source_refs")
        if not isinstance(source_refs, list):
            continue
        source_exclusions.update(
            source_ref for source_ref in source_refs if isinstance(source_ref, str)
        )
    return source_exclusions


def _optional_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    raise ValueError(f"LXX projection {field_name} must be an integer or null")


def _optional_str(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    raise ValueError(f"LXX projection {field_name} must be a string or null")


def _word_surface(surface: str) -> str:
    value = surface.strip()
    while value and value[0] in _LEADING_MARKS:
        value = value[1:]
    while value and value[-1] in _TRAILING_MARKS:
        value = value[:-1]
    return value


def _primary_strong_for_token(token: TagntToken) -> str | None:
    for segment in token.strong_segments:
        if segment.is_primary:
            return segment.strong
    if token.strong_segments:
        return token.strong_segments[0].strong
    return None


def _is_textus_receptus_token(token: TagntToken) -> bool:
    return any(edition.startswith("TR") for edition in token.editions)


def _base36(number: int) -> str:
    if number <= 0:
        raise ValueError(f"base36 requires a positive integer, got {number}")
    value = number
    characters: list[str] = []
    while value:
        value, remainder = divmod(value, 36)
        characters.append(_BASE36_ALPHABET[remainder])
    return "".join(reversed(characters))


def _load_verified_manifest(manifest_path: Path) -> Mapping[str, object]:
    errors = verify_source_manifest(manifest_path=manifest_path)
    if errors:
        details = "\n".join(errors)
        raise ValueError(f"Cannot build LXX_TR from invalid source manifest:\n{details}")
    manifest = load_manifest(manifest_path)
    if manifest is None:
        raise ValueError(f"Missing source manifest: {manifest_path}")
    return manifest


def _source_paths_by_id(
    manifest: Mapping[str, object],
    manifest_path: Path,
) -> dict[str, Path]:
    entries = manifest.get("sources")
    if not isinstance(entries, list):
        raise ValueError("Invalid source manifest: sources must be a list")
    paths: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        source_id = entry.get("source_id")
        local_path = entry.get("local_path")
        if isinstance(source_id, str) and isinstance(local_path, str):
            path = Path(local_path)
            paths[source_id] = path if path.is_absolute() else manifest_path.parent / path

    required_source_ids = (*TAGNT_LOCKED_SOURCE_IDS, CROSSWIRE_LXX_SOURCE_ID)
    missing = [source_id for source_id in required_source_ids if source_id not in paths]
    if missing:
        raise ValueError(f"Missing locked source paths: {', '.join(missing)}")
    return paths


def _source_summary(
    manifest: Mapping[str, object],
    *,
    additional_notes: Sequence[str] = (),
) -> str:
    entries = manifest.get("sources")
    if not isinstance(entries, list):
        return _append_summary_notes(
            "NT: STEPBible TAGNT Textus Receptus; OT: pending LXX import.",
            additional_notes,
        )
    by_id = {
        str(entry.get("source_id")): entry
        for entry in entries
        if isinstance(entry, Mapping)
    }
    tagnt_entries = [by_id[source_id] for source_id in TAGNT_LOCKED_SOURCE_IDS]
    tagnt_versions = ", ".join(str(entry.get("version") or "") for entry in tagnt_entries)
    return _append_summary_notes(
        "NT: STEPBible TAGNT Textus Receptus from locked source chunks "
        f"{', '.join(TAGNT_LOCKED_SOURCE_IDS)} ({tagnt_versions}). "
        "OT: CrossWire LXX via explicit KJV-versification projection rules, "
        "including owner-approved full Addition D rows at Esth.5.1-2.",
        additional_notes,
    )


def _license_summary(additional_notes: Sequence[str] = ()) -> str:
    return _append_summary_notes(MODULE_LICENSE_SUMMARY, additional_notes)


def _append_summary_notes(summary: str, notes: Sequence[str]) -> str:
    normalized_notes = tuple(note.strip() for note in notes if note.strip())
    if not normalized_notes:
        return summary
    return f"{summary} {' '.join(normalized_notes)}"


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


def _vacuum_lxx_tr_database(db_path: Path) -> None:
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
        description=(
            "Build the simplified LXX_TR SQLite module and fill Textus "
            "Receptus NT plus rule-projected LXX OT verses."
        ),
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET_PATH,
        help="Output bible_lxx_tr.sqlite path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_LOCK_PATH,
        help="Locked source_manifest.lock.json path.",
    )
    parser.add_argument(
        "--data-version",
        type=int,
        default=LXX_TR_DATA_VERSION_INITIAL,
        help="db_metadata.data_version value.",
    )
    parser.add_argument(
        "--lxx-projection-rules",
        type=Path,
        action="append",
        default=None,
        help=(
            "Optional JSON file with LXX projection rules. The preferred shape is "
            "{rules:[{target_ref,spans:[{source_ref,segment_index,sub_type,"
            "token_start,token_end}]}]}; candidate-map groups with whole-verse "
            "pairs are also accepted. Pass more than once to merge candidate and "
            "token-span rule files."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_lxx_tr_module(
        target_path=args.target,
        manifest_path=args.manifest,
        lxx_projection_rules_path=args.lxx_projection_rules,
        data_version=args.data_version,
    )
    print(json.dumps(_report_json(report), ensure_ascii=False, indent=2))
    return 0


def _report_json(report: LxxTrBuildReport) -> dict[str, object]:
    return {
        "target_path": str(report.target_path),
        "backup_path": str(report.backup_path) if report.backup_path else None,
        "verses_count": report.verses_count,
        "filled_verses_count": report.filled_verses_count,
        "empty_verses_count": report.empty_verses_count,
        "tr_tokens_count": report.tr_tokens_count,
        "lxx_tokens_count": report.lxx_tokens_count,
        "missing_tr_verses_count": len(report.missing_tr_verses),
        "missing_tr_verses": list(report.missing_tr_verses),
        "extra_tr_verses_count": len(report.extra_tr_verses),
        "extra_tr_verses": list(report.extra_tr_verses),
        "missing_lxx_verses_count": len(report.missing_lxx_verses),
        "missing_lxx_verses": list(report.missing_lxx_verses),
        "extra_lxx_verses_count": len(report.extra_lxx_verses),
        "extra_lxx_verses": list(report.extra_lxx_verses),
        "duplicate_lxx_target_refs_count": len(report.duplicate_lxx_target_refs),
        "duplicate_lxx_target_refs": list(report.duplicate_lxx_target_refs),
        "missing_strong_tokens_count": len(report.missing_strong_tokens),
        "missing_strong_tokens": [
            token.as_json() for token in report.missing_strong_tokens
        ],
        "built_at": report.built_at,
    }


if __name__ == "__main__":
    raise SystemExit(main())

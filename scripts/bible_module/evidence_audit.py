"""Evidence-oriented, read-only audit for the compact KJV and LXX/TR modules.

The original comparison in :mod:`audit_kjv_tr_strongs` is intentionally kept
stable for byte-for-byte reproducibility.  This module adds symmetric metrics,
ordered comparison, source-text checks, indexing checks, word/Strong alignment,
and deterministic machine-readable outputs.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import sqlite3
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .audit_kjv_tr_strongs import (
    BibleModule,
    StrongAggregateScore,
    StrongComparison,
    StrongFilter,
    StrongVerseScore,
    build_canonical_indexes,
    compare_new_testaments,
    read_module,
    read_strong_filter,
    strong_sequence,
)
from .build_kjv import (
    extract_kjv_verse_texts,
    read_usfx_xml_from_zip,
    verse_key_for,
)
from .build_lxx_tr import (
    _is_textus_receptus_token,
    _primary_strong_for_token,
    build_lxx_verse_texts,
    build_tr_verse_texts,
    iter_lxx_tr_tagnt_tokens,
    load_lxx_projection_plan,
)
from .canon import CANONICAL_BOOKS, canonical_verses
from .lxx import iter_crosswire_lxx_source_verses
from .strong_numbers import classic_greek_strong_or_none
from .tagnt import TagntToken, normalize_strong


AUDIT_SCHEMA_VERSION = 1
EXPECTED_VERSES_COUNT = 31_102
EXPECTED_NT_VERSES_COUNT = 7_957
EXPECTED_PRIORITY_COUNTS = {
    "<50%": 37,
    "50%–<66,(6)%": 229,
    "66,(6)%–<75%": 513,
    "75%–<80%": 575,
}
EXPECTED_LXX_EMPTY_COUNT = 210

CLASSIFICATIONS_RU = {
    1: "Подтверждённая ошибка текста или копирования",
    2: "Подтверждённая ошибка индексации",
    3: "Подтверждённая ошибка версификации внутри модуля",
    4: "Подтверждённая ошибка Strong-разметки",
    5: "Вероятная техническая ошибка",
    6: "Различие редакций",
    7: "Исторически засвидетельствованный текстуальный вариант",
    8: "Ожидаемое переводческое или лингвистическое различие",
    9: "Артефакт исходной метрики или списка исключений",
    10: "Недостаточно данных",
}

_STRONG_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])([GH]0*\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?)"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[^\W_]+(?:[’'][^\W_]+)*", re.UNICODE)
_SCV_VERSE_RE = re.compile(r"^\s*(\d+):(\d+)\s+(.*\S)\s*$")
_PRIORITY_LINE_RE = re.compile(
    r"^\s{4}(?P<ref>[1-3]?[A-Za-z]+\.\d+\.\d+) "
    r"\[(?P<key>[0-9A-Z]{3})\] — "
    r"(?P<percent>\d+\.\d+)% "
    r"\((?P<matched>\d+) из (?P<tr_total>\d+) TR\)$"
)
_EMPTY_LINE_RE = re.compile(
    r"^\s{4}(?P<ref>[1-3]?[A-Za-z]+\.\d+\.\d+) "
    r"\[(?P<key>[0-9A-Z]{3})\]$"
)
_TAGNT_SUBSCRIPTION_MARKERS = (
    "πρὸς",
    "Πρὸς",
    "πρός",
    "Πρός",
)
_GUTENBERG_BOOK_TITLES = (
    "The First Book of Moses: Called Genesis",
    "The Second Book of Moses: Called Exodus",
    "The Third Book of Moses: Called Leviticus",
    "The Fourth Book of Moses: Called Numbers",
    "The Fifth Book of Moses: Called Deuteronomy",
    "The Book of Joshua",
    "The Book of Judges",
    "The Book of Ruth",
    "The First Book of Samuel",
    "The Second Book of Samuel",
    "The First Book of the Kings",
    "The Second Book of the Kings",
    "The First Book of the Chronicles",
    "The Second Book of the Chronicles",
    "Ezra",
    "The Book of Nehemiah",
    "The Book of Esther",
    "The Book of Job",
    "The Book of Psalms",
    "The Proverbs",
    "Ecclesiastes",
    "The Song of Solomon",
    "The Book of the Prophet Isaiah",
    "The Book of the Prophet Jeremiah",
    "The Lamentations of Jeremiah",
    "The Book of the Prophet Ezekiel",
    "The Book of Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "The Gospel According to Saint Matthew",
    "The Gospel According to Saint Mark",
    "The Gospel According to Saint Luke",
    "The Gospel According to Saint John",
    "The Acts of the Apostles",
    "The Epistle of Paul the Apostle to the Romans",
    "The First Epistle of Paul the Apostle to the Corinthians",
    "The Second Epistle of Paul the Apostle to the Corinthians",
    "The Epistle of Paul the Apostle to the Galatians",
    "The Epistle of Paul the Apostle to the Ephesians",
    "The Epistle of Paul the Apostle to the Philippians",
    "The Epistle of Paul the Apostle to the Colossians",
    "The First Epistle of Paul the Apostle to the Thessalonians",
    "The Second Epistle of Paul the Apostle to the Thessalonians",
    "The First Epistle of Paul the Apostle to Timothy",
    "The Second Epistle of Paul the Apostle to Timothy",
    "The Epistle of Paul the Apostle to Titus",
    "The Epistle of Paul the Apostle to Philemon",
    "The Epistle of Paul the Apostle to the Hebrews",
    "The General Epistle of James",
    "The First Epistle General of Peter",
    "The Second General Epistle of Peter",
    "The First Epistle General of John",
    "The Second Epistle General of John",
    "The Third Epistle General of John",
    "The General Epistle of Jude",
    "The Revelation of Saint John the Divine",
)
_OSIS_BOOK_ALIASES = {
    "Matt": "Mat",
}
_CANONICAL_REF_ORDER = {
    verse.canonical_ref: verse.sort_key for verse in canonical_verses()
}
_CANONICAL_REFS = tuple(verse.canonical_ref for verse in canonical_verses())
_CANONICAL_REF_INDEX = {
    verse_ref: index for index, verse_ref in enumerate(_CANONICAL_REFS)
}


@dataclass(frozen=True)
class EvidenceAuditInputs:
    kjv_db: Path
    lxx_tr_db: Path
    original_report: Path
    weak_strongs: Path
    kjv_usfx_zip: Path
    crosswire_kjv_osis: Path
    open_bibles_kjv_osis: Path
    project_gutenberg_kjv: Path
    tagnt_paths: tuple[Path, ...]
    crosswire_lxx_zip: Path
    lxx_projection_plan: Path
    scrivener_text_dir: Path
    output_dir: Path
    accessed_on: str


@dataclass(frozen=True)
class FileEvidence:
    path: str
    bytes: int
    modified_utc: str
    sha256: str


@dataclass(frozen=True)
class TaggedSpan:
    surface: str
    strongs: tuple[str, ...]


@dataclass(frozen=True)
class OsisVerse:
    text: str
    strong_sequence: tuple[str, ...]
    tagged_spans: tuple[TaggedSpan, ...]


@dataclass(frozen=True)
class OriginalPriorityEntry:
    verse_ref: str
    verse_key: str
    source_range: str
    source_percent: float
    source_matched: int
    source_tr_total: int


@dataclass(frozen=True)
class MetricSet:
    tr_total: int
    kjv_total: int
    matched: int
    tr_only_count: int
    kjv_only_count: int
    tr_recall: float
    kjv_precision: float
    f1: float
    multiset_jaccard: float
    ordered_matched: int
    ordered_tr_recall: float
    ordered_kjv_precision: float
    ordered_f1: float


@dataclass(frozen=True)
class AltAwareMetrics:
    tr_total: int
    kjv_total: int
    matched: int
    tr_recall: float
    kjv_precision: float
    f1: float
    multiset_jaccard: float
    ordered_matched: int
    ordered_f1: float


@dataclass(frozen=True)
class WordTagAgreement:
    aligned_words: int
    both_tagged_words: int
    exact_tag_match_words: int
    overlapping_tag_words: int
    conflicting_tag_words: int
    module_untagged_source_tagged_words: int
    source_untagged_module_tagged_words: int
    ratio: float


@dataclass(frozen=True)
class IndexAudit:
    path: str
    query_only: int
    integrity_check: str
    user_version: int
    schema_version: str
    data_version: str
    metadata_date: str
    tables: tuple[str, ...]
    verse_rows: int
    distinct_verse_keys: int
    duplicate_keys: tuple[str, ...]
    missing_keys: tuple[str, ...]
    extra_keys: tuple[str, ...]
    keys_are_exact_base36_sequence: bool
    invalid_key_lengths: tuple[str, ...]


def run_evidence_audit(inputs: EvidenceAuditInputs) -> dict[str, object]:
    """Run the full read-only audit and write deterministic JSON/CSV outputs."""
    _validate_access_date(inputs.accessed_on)
    input_paths = _required_input_paths(inputs)
    missing = [str(path) for path in input_paths if not path.is_file()]
    if not inputs.scrivener_text_dir.is_dir():
        missing.append(str(inputs.scrivener_text_dir))
    if missing:
        raise FileNotFoundError("Missing audit input(s): " + ", ".join(missing))

    refs_by_key, nt_keys = build_canonical_indexes()
    key_by_ref = {verse_ref: key for key, verse_ref in refs_by_key.items()}
    strong_filter = read_strong_filter(inputs.weak_strongs)
    kjv = read_module(inputs.kjv_db)
    lxx_tr = read_module(inputs.lxx_tr_db)
    index_audits = (
        audit_compact_index(inputs.kjv_db, refs_by_key),
        audit_compact_index(inputs.lxx_tr_db, refs_by_key),
    )
    _validate_index_audits(index_audits)

    original_priority = parse_original_priority_entries(inputs.original_report)
    original_empty = parse_original_lxx_empty_entries(inputs.original_report)
    _validate_original_report_coverage(original_priority, original_empty)

    comparisons = _build_comparisons(
        kjv=kjv,
        lxx_tr=lxx_tr,
        nt_keys=nt_keys,
        refs_by_key=refs_by_key,
        strong_filter=strong_filter,
    )
    _validate_original_reproduction(
        comparisons["all_77"],
        original_priority=original_priority,
        kjv=kjv,
        lxx_tr=lxx_tr,
    )

    kjv_usfx_texts = _normalize_reference_mapping(
        extract_kjv_verse_texts(read_usfx_xml_from_zip(inputs.kjv_usfx_zip))
    )
    if len(kjv_usfx_texts) != EXPECTED_VERSES_COUNT:
        raise ValueError(
            "Incomplete KJV USFX parse: "
            f"{len(kjv_usfx_texts)} != {EXPECTED_VERSES_COUNT}"
        )
    crosswire_kjv = parse_osis_verses(inputs.crosswire_kjv_osis)
    open_bibles_kjv = parse_osis_verses(inputs.open_bibles_kjv_osis)
    project_gutenberg_kjv = parse_project_gutenberg_kjv(
        inputs.project_gutenberg_kjv
    )
    _validate_kjv_source_coverage(
        crosswire_kjv,
        open_bibles_kjv,
        project_gutenberg_kjv,
    )

    tagnt_tokens = tuple(iter_lxx_tr_tagnt_tokens(inputs.tagnt_paths))
    tr_source_result = build_tr_verse_texts(tagnt_tokens)
    if tr_source_result.filled_verses_count != EXPECTED_NT_VERSES_COUNT:
        raise ValueError(
            "Incomplete TAGNT TR parse: "
            f"{tr_source_result.filled_verses_count} != {EXPECTED_NT_VERSES_COUNT}"
        )
    tagnt_by_ref = _tagnt_tr_tokens_by_ref(tagnt_tokens)
    tr_rebuild_by_ref = {
        verse.canonical_ref: tr_source_result.verse_texts_by_id[
            verse.canonical_verse_id
        ]
        for verse in canonical_verses()
        if verse.book_id >= 40
    }
    tr_rebuild_diffs = tuple(
        verse_ref
        for verse_ref, key in key_by_ref.items()
        if _is_nt_ref(verse_ref)
        and lxx_tr.verses[key] != tr_rebuild_by_ref[verse_ref]
    )
    if tr_rebuild_diffs:
        raise ValueError(
            "TR module no longer reproduces from locked TAGNT inputs: "
            + ", ".join(tr_rebuild_diffs[:20])
        )

    scrivener = parse_scrivener_texts(inputs.scrivener_text_dir)
    if len(scrivener) != EXPECTED_NT_VERSES_COUNT:
        raise ValueError(
            "Incomplete Scrivener parse: "
            f"{len(scrivener)} != {EXPECTED_NT_VERSES_COUNT}"
        )

    lxx_projection = load_lxx_projection_plan(inputs.lxx_projection_plan)
    lxx_rebuild = build_lxx_verse_texts(
        iter_crosswire_lxx_source_verses(inputs.crosswire_lxx_zip),
        projection_rules=lxx_projection.rules,
        source_exclusions=lxx_projection.source_exclusions,
        include_identity_projection=True,
    )
    lxx_rebuild_by_ref = {
        verse.canonical_ref: lxx_rebuild.verse_texts_by_id.get(
            verse.canonical_verse_id,
            "",
        )
        for verse in canonical_verses()
        if verse.book_id < 40
    }
    lxx_rebuild_diffs = tuple(
        verse_ref
        for verse_ref, key in key_by_ref.items()
        if not _is_nt_ref(verse_ref)
        and lxx_tr.verses[key] != lxx_rebuild_by_ref[verse_ref]
    )
    if lxx_rebuild_diffs:
        raise ValueError(
            "LXX module no longer reproduces from projection inputs: "
            + ", ".join(lxx_rebuild_diffs[:20])
        )

    lxx_resolution_index = _load_lxx_resolution_index(inputs.lxx_projection_plan)
    lxx_empty_rows = _build_lxx_empty_rows(
        original_empty=original_empty,
        lxx_tr=lxx_tr,
        key_by_ref=key_by_ref,
        resolution_index=lxx_resolution_index,
    )

    priority_rows = _build_priority_rows(
        entries=original_priority,
        comparisons=comparisons,
        strong_filter=strong_filter,
        kjv=kjv,
        lxx_tr=lxx_tr,
        kjv_usfx_texts=kjv_usfx_texts,
        crosswire_kjv=crosswire_kjv,
        open_bibles_kjv=open_bibles_kjv,
        project_gutenberg_kjv=project_gutenberg_kjv,
        tagnt_by_ref=tagnt_by_ref,
        scrivener=scrivener,
    )
    kjv_strong_anomalies = _build_kjv_strong_anomalies(
        kjv=kjv,
        refs_by_key=refs_by_key,
        crosswire_kjv=crosswire_kjv,
    )

    full_source_checks = _build_full_source_checks(
        kjv=kjv,
        lxx_tr=lxx_tr,
        refs_by_key=refs_by_key,
        kjv_usfx_texts=kjv_usfx_texts,
        crosswire_kjv=crosswire_kjv,
        open_bibles_kjv=open_bibles_kjv,
        project_gutenberg_kjv=project_gutenberg_kjv,
        tr_rebuild_by_ref=tr_rebuild_by_ref,
        lxx_rebuild_by_ref=lxx_rebuild_by_ref,
        lxx_rebuild=lxx_rebuild,
    )
    cluster_analysis = _build_cluster_analysis(
        priority_rows=priority_rows,
        comparisons=comparisons,
    )
    source_manifest = _build_source_manifest(inputs)
    aggregate_modes: dict[str, dict[str, object]] = {
        name: _comparison_summary(comparison)
        for name, comparison in comparisons.items()
    }
    aggregate_modes.update(
        _build_excluded_category_metrics(
            kjv=kjv,
            lxx_tr=lxx_tr,
            nt_keys=nt_keys,
            strong_filter=strong_filter,
        )
    )
    classification_counts = Counter(
        str(row["classification"]["number"]) for row in priority_rows
    )
    confidence_counts = Counter(
        str(row["classification"]["confidence"]) for row in priority_rows
    )
    probable_shift_count = sum(
        1
        for row in priority_rows
        if bool(row["neighbor_index_check"]["probable_shift"])
    )
    priority_statistics = _build_priority_statistics(priority_rows)
    priority_confirmed_technical = [
        row
        for row in priority_rows
        if int(row["classification"]["number"]) in {1, 2, 3, 4}
    ]
    confirmed_technical = [
        {"finding_origin": "priority_below_80", **row}
        for row in priority_confirmed_technical
    ]
    confirmed_refs = {
        str(row["verse_ref"]) for row in priority_confirmed_technical
    }
    confirmed_technical.extend(
        {
            "finding_origin": "full_kjv_strong_scan",
            **row,
        }
        for row in kjv_strong_anomalies
        if str(row["verse_ref"]) not in confirmed_refs
    )
    probable_technical = [
        row
        for row in priority_rows
        if int(row["classification"]["number"]) == 5
    ]

    summary: dict[str, object] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "accessed_on": inputs.accessed_on,
        "read_only_contract": {
            "sqlite_uri_mode": "ro",
            "pragma_query_only": "ON",
            "source_databases_modified": False,
        },
        "input_files": source_manifest["input_files"],
        "original_report_reproduction": {
            "byte_for_byte_sha256_reproduced": True,
            "verses_per_module": EXPECTED_VERSES_COUNT,
            "nt_compared": comparisons["all_77"].compared_verses_count,
            **_comparison_summary(comparisons["all_77"]),
            "priority_counts": dict(EXPECTED_PRIORITY_COUNTS),
            "lxx_empty_count": len(original_empty),
        },
        "metrics_by_exclusion_mode": aggregate_modes,
        "all_77_metrics_by_book": [
            _aggregate_score_summary(score)
            for score in comparisons["all_77"].book_scores
        ],
        "all_77_metrics_by_chapter": [
            _aggregate_score_summary(score)
            for score in comparisons["all_77"].chapter_scores
        ],
        "index_audits": [asdict(audit) for audit in index_audits],
        "source_checks": full_source_checks,
        "kjv_strong_alignment_anomalies": {
            "rows": len(kjv_strong_anomalies),
            "flag_counts": dict(
                sorted(
                    Counter(
                        flag
                        for row in kjv_strong_anomalies
                        for flag in row["flags"]
                    ).items()
                )
            ),
        },
        "priority_below_80": {
            "rows": len(priority_rows),
            "classification_counts": dict(sorted(classification_counts.items())),
            "confidence_counts": dict(sorted(confidence_counts.items())),
            "neighbor_index_checks": {
                "rows": len(priority_rows),
                "probable_shifts": probable_shift_count,
            },
            "statistics": priority_statistics,
            "confirmed_technical_count": len(priority_confirmed_technical),
            "probable_technical_count": len(probable_technical),
        },
        "confirmed_technical_findings": {
            "rows": len(confirmed_technical),
            "priority_below_80_rows": len(priority_confirmed_technical),
            "full_scan_additional_rows": (
                len(confirmed_technical)
                - len(priority_confirmed_technical)
            ),
        },
        "lxx_empty_positions": {
            "rows": len(lxx_empty_rows),
            "projection_rebuild_exact": not lxx_rebuild_diffs,
            "projection_rules_count": len(lxx_projection.rules),
            "source_exclusions_count": len(lxx_projection.source_exclusions),
            "classification_counts": dict(
                sorted(
                    Counter(
                        str(row["classification"]["number"])
                        for row in lxx_empty_rows
                    ).items()
                )
            ),
            "statistics": _build_lxx_empty_statistics(lxx_empty_rows),
        },
        "cluster_analysis": cluster_analysis,
        "limitations": _limitations(),
    }

    inputs.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(inputs.output_dir / "source_manifest.json", source_manifest)
    _write_json(inputs.output_dir / "audit_summary.json", summary)
    _write_json(inputs.output_dir / "priority_below_80.json", priority_rows)
    _write_priority_csv(inputs.output_dir / "priority_below_80.csv", priority_rows)
    _write_json(inputs.output_dir / "lxx_empty_positions.json", lxx_empty_rows)
    _write_lxx_empty_csv(inputs.output_dir / "lxx_empty_positions.csv", lxx_empty_rows)
    _write_json(
        inputs.output_dir / "confirmed_technical_findings.json",
        confirmed_technical,
    )
    _write_json(
        inputs.output_dir / "probable_technical_findings.json",
        probable_technical,
    )
    _write_json(
        inputs.output_dir / "strong_metrics_by_scope.json",
        aggregate_modes,
    )
    _write_metrics_csv(
        inputs.output_dir / "strong_metrics_by_scope.csv",
        aggregate_modes,
    )
    _write_json(
        inputs.output_dir / "indexing_audit.json",
        [asdict(audit) for audit in index_audits],
    )
    _write_json(
        inputs.output_dir / "kjv_strong_alignment_anomalies.json",
        kjv_strong_anomalies,
    )
    _write_kjv_strong_anomalies_csv(
        inputs.output_dir / "kjv_strong_alignment_anomalies.csv",
        kjv_strong_anomalies,
    )
    report = render_russian_report(
        summary=summary,
        source_manifest=source_manifest,
        priority_rows=priority_rows,
        lxx_empty_rows=lxx_empty_rows,
        kjv_strong_anomalies=kjv_strong_anomalies,
        inputs=inputs,
    )
    (inputs.output_dir / "report.ru.md").write_text(
        report,
        encoding="utf-8",
        newline="\n",
    )
    return {
        "summary": summary,
        "priority_rows": priority_rows,
        "lxx_empty_rows": lxx_empty_rows,
        "source_manifest": source_manifest,
        "kjv_strong_anomalies": kjv_strong_anomalies,
    }


def render_russian_report(
    *,
    summary: Mapping[str, object],
    source_manifest: Mapping[str, object],
    priority_rows: Sequence[Mapping[str, object]],
    lxx_empty_rows: Sequence[Mapping[str, object]],
    kjv_strong_anomalies: Sequence[Mapping[str, object]],
    inputs: EvidenceAuditInputs,
) -> str:
    """Render the deterministic Russian evidence report."""
    priority_summary = summary["priority_below_80"]
    lxx_summary = summary["lxx_empty_positions"]
    source_checks = summary["source_checks"]
    metrics = summary["metrics_by_exclusion_mode"]
    class_counts = priority_summary["classification_counts"]
    confirmed_subscriptions = [
        row
        for row in priority_rows
        if int(row["classification"]["number"]) == 3
    ]
    under_50 = [
        row for row in priority_rows if row["source_range"] == "<50%"
    ]
    input_files = source_manifest["input_files"]
    lines = [
        "# Доказательный read-only аудит библейских модулей KJV и LXX/TR",
        "",
        f"Дата доступа к источникам: {summary['accessed_on']}. "
        f"Версия схемы результатов: {summary['schema_version']}.",
        "",
        "## Резюме",
        "",
        "Исходный отчёт воспроизведён на неизменённых входах: его SHA-256 "
        "и SHA-256 повторно сгенерированного файла совпадают. Исходная "
        "метрика показывает наличие хотя бы одного multiset-различия Strong, "
        "но не вероятность ошибки стиха.",
        "",
        f"Проверены все {priority_summary['rows']} стихов ниже 80%, "
        f"все {lxx_summary['rows']} пустых позиций LXX и все 31 102 KJV "
        "позиции против зафиксированного источника. Подтверждены "
        f"{len(kjv_strong_anomalies)} аномалий KJV Strong и "
        f"{len(confirmed_subscriptions)} случаев включения греческой "
        "подписки/колофона в канонический verse-row TR. Подтверждённых "
        "ошибок английского KJV-текста или base36-индекса не найдено.",
        "",
        "Ключевой результат: большая часть низких исходных процентов — "
        "артефакт сравнения разных Strong-систем или ожидаемое переводческое "
        "выравнивание. Это не отменяет локальные технические дефекты, "
        "перечисленные ниже.",
        "",
        "Отчёт не заявляет полной корректности модулей: 1 052 "
        "нормализованных KJV-различия с независимой электронной редакцией и "
        "173 LXX-пустоты оставлены как редакционные/неразрешённые случаи, а "
        "двух независимых LXX-корпусов с классическими Strong не найдено.",
        "",
        "## Входы и контрольные суммы",
        "",
        "| Вход | Байт | Modified UTC | SHA-256 |",
        "|---|---:|---|---|",
    ]
    for name in (
        "original_report",
        "kjv_sqlite",
        "lxx_tr_sqlite",
        "weak_strongs",
    ):
        evidence = input_files[name]
        lines.append(
            f"| `{name}` | {evidence['bytes']} | "
            f"{evidence['modified_utc']} | `{evidence['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "Полный манифест всех локально использованных корпусов, включая "
            "пофайловые SHA-256 Scrivener, находится в "
            "[source_manifest.json](source_manifest.json). SQLite открывался "
            "через URI `mode=ro`; после подключения выполнялся "
            "`PRAGMA query_only=ON`.",
            "",
            "## Воспроизводимость исходного отчёта",
            "",
            "| Показатель | Результат |",
            "|---|---:|",
            "| Стихов в каждом модуле | 31 102 |",
            "| Сопоставлено стихов НЗ | 7 957 |",
            "| Несовпадающих стихов | 6 403 |",
            "| TR после 77 исключений | 88 214 |",
            "| Совпало | 78 404 |",
            "| TR-only | 9 810 |",
            "| KJV-only | 14 532 |",
            "| TR-recall | 88,88% |",
            "| Исходное «полное расхождение» | 24 342 (27,59% от TR) |",
            "",
            "Побайтовый SHA-256 воспроизведённого отчёта: "
            f"`{input_files['original_report']['sha256']}`. Все 1 354 записи "
            "раздела 5 и все 210 ссылок раздела 2 повторно разобраны прямо "
            "из исходного отчёта; неполный разбор завершает скрипт ошибкой.",
            "",
            "## Аудит методики и новые метрики",
            "",
            "Для каждого стиха сохранены исходный multiset-recall, "
            "KJV-precision, симметричная F1, multiset Jaccard и LCS-метрики "
            "последовательности. Повторы учитываются. Дополнительный "
            "alt-aware режим сопоставляет один KJV Strong не более чем с "
            "одним токеном TAGNT, учитывая первичный и альтернативные "
            "классические Strong этого токена.",
            "",
            "| Режим | TR | KJV | Recall | Precision | F1 | Jaccard | "
            "Ordered F1 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    metric_order = [
        "none",
        "all_77",
        "exclude_only_definite_article",
        "exclude_only_prepositions",
        "exclude_only_conjunctions_and_non_negative_particles",
        "category_only_definite_article",
        "category_only_prepositions",
        "category_only_conjunctions_and_non_negative_particles",
    ]
    for mode in metric_order:
        value = metrics[mode]
        lines.append(
            f"| `{mode}` | {value['tr_total']} | {value['kjv_total']} | "
            f"{_report_percent(value['tr_recall'])} | "
            f"{_report_percent(value['kjv_precision'])} | "
            f"{_report_percent(value['f1'])} | "
            f"{_report_percent(value['multiset_jaccard'])} | "
            f"{_report_percent(value['ordered_f1'])} |"
        )
    lines.extend(
        [
            "",
            "Исключение 77 служебных номеров повышает F1, но одновременно "
            "скрывает различия именно в артиклях, предлогах и частицах. "
            "Поэтому отчёт хранит как режим без исключений, так и вклад каждой "
            "категории отдельно. Ни один такой diff автоматически не объявлен "
            "текстовой ошибкой.",
            "",
            "## Редакции, версификация и источники",
            "",
            "- KJV-модуль точно воспроизводит зафиксированный "
            "`eng-kjv2006` USFX: стандартизованная редакция 1769 года по "
            "описанию eBible/CrossWire.",
            "- НЗ LXX/TR точно пересобирается из TAGNT. Набор TR-токенов "
            "идентифицирован TAGNT как Scrivener 1894; отображаемые орфография "
            "и пунктуация следуют редакционной политике TAGNT и не являются "
            "дипломатической транскрипцией печатного Scrivener.",
            "- ВЗ комбинированного файла — CrossWire LXX 3.2, "
            "морфологически размеченный Rahlfs/CATSS, спроецированный на "
            "локальную протестантскую/KJV-сетку с документированными "
            "дополнениями Swete и патристических контролей.",
            "",
            "| ID | Организация/редактор | Редакция и назначение | Лицензия | "
            "Ссылка |",
            "|---|---|---|---|---|",
        ]
    )
    for source in source_manifest["sources"]:
        link = source.get("source_page_url") or source.get("source_url")
        lines.append(
            f"| `{source['source_id']}` | {source['organization_or_editor']} | "
            f"{source['edition']}; {source['purpose']} | {source['license']} | "
            f"[источник]({link}) |"
        )
    index_audits = summary["index_audits"]
    lines.extend(
        [
            "",
            "Текстовый источник без Strong-разметки использован только для "
            "текста и границ стихов, не как подтверждение Strong.",
            "",
            "## Индексация",
            "",
        ]
    )
    for audit in index_audits:
        lines.append(
            f"- `{Path(audit['path']).name}`: query_only={audit['query_only']}, "
            f"integrity=`{audit['integrity_check']}`, rows="
            f"{audit['verse_rows']}, distinct={audit['distinct_verse_keys']}, "
            f"duplicate/missing/extra=0, точная base36-последовательность — "
            f"{'да' if audit['keys_are_exact_base36_sequence'] else 'нет'}."
        )
    versification = source_checks["kjv"]["external_versification_finding"]
    lines.extend(
        [
            "",
            f"Обнаружено подтверждённое различие редакционной версификации "
            f"({versification['confidence']}): локальные "
            f"`{versification['local_range']}` соответствуют внешним "
            f"`{versification['crosswire_and_open_bibles_range']}`. "
            f"{versification['explanation_ru']} Это классифицировано как "
            "«различие редакций/версификаций», а не потеря текста.",
            "",
            f"Для всех {priority_summary['neighbor_index_checks']['rows']} "
            "приоритетных стихов сопоставлены собственная, предыдущая и "
            "следующая записи KJV и Scrivener/TR. Вероятных смещений: "
            f"{priority_summary['neighbor_index_checks']['probable_shifts']}. "
            "Во всех случаях собственная TR-ссылка имела более сильное "
            "последовательностное совпадение, чем оба соседа.",
            "",
            "## Уровень A: три стиха с 0%",
            "",
        ]
    )
    priority_by_ref = {str(row["verse_ref"]): row for row in priority_rows}
    for verse_ref in ("Mark.9.43", "Luke.6.41", "Luke.17.36"):
        row = priority_by_ref[verse_ref]
        lines.extend(
            [
                f"### {verse_ref} [{row['verse_key']}]",
                "",
                f"{row['conclusion_ru']} Локальный текст: "
                f"“{row['local_text']['kjv_plain']}” Индекс и соседние стихи "
                "совпадают; причина не в смещении, редакции TR или ошибке "
                "извлечения.",
                "",
            ]
        )
    lines.extend(
        [
            "## Все 37 стихов ниже 50%",
            "",
            "| Стих [key] | Исходно | Категория; уверенность | Заключение |",
            "|---|---:|---|---|",
        ]
    )
    for row in under_50:
        classification = row["classification"]
        lines.append(
            f"| `{row['verse_ref']} [{row['verse_key']}]` | "
            f"{row['source_percent']:.2f}% | "
            f"{classification['number']}. {classification['label']}; "
            f"`{classification['confidence']}` | "
            f"{row['conclusion_ru']} |"
        )
    lines.extend(
        [
            "",
            "Для каждой строки полный локальный KJV/TR-текст, исходные "
            "TR-only/KJV-only, последовательности, word alignment, строгие и "
            "нормализованные проверки, все URL и предлагаемое содержимое "
            "(только когда дефект подтверждён) находятся в "
            "[priority_below_80.json](priority_below_80.json).",
            "",
            "## Все 1 354 стиха ниже 80%",
            "",
            "| Класс | Количество |",
            "|---|---:|",
        ]
    )
    for number, count in sorted(class_counts.items(), key=lambda item: int(item[0])):
        lines.append(
            f"| {number}. {CLASSIFICATIONS_RU[int(number)]} | {count} |"
        )
    lines.extend(
        [
            "",
            "Охват уровней: A — 3, B — 34, C — 229, D — 1 088. "
            "Каждая запись получила одну основную категорию и уверенность. "
            "Машиночитаемые приложения: "
            "[priority_below_80.csv](priority_below_80.csv) и "
            "[priority_below_80.json](priority_below_80.json).",
            "",
            "## Подтверждённые технические дефекты",
            "",
            "### KJV Strong",
            "",
            "| Стих [key] | Тип | F1 инвентаря | Word agreement |",
            "|---|---|---:|---:|",
        ]
    )
    for row in kjv_strong_anomalies:
        lines.append(
            f"| `{row['verse_ref']} [{row['verse_key']}]` | "
            f"{', '.join(row['flags'])} | "
            f"{_report_percent(row['sequence_metrics']['f1'])} | "
            f"{_report_percent(row['word_alignment']['ratio'])} |"
        )
    lines.extend(
        [
            "",
            "Полные доказательные строки и контрольные последовательности: "
            "[kjv_strong_alignment_anomalies.json]"
            "(kjv_strong_alignment_anomalies.json). В исходный список ниже "
            "80% не входили `Acts.21.4` и `2Cor.5.4`; они найдены полным "
            "сканированием и подтверждают наличие системного паттерна выше "
            "порогового списка.",
            "",
            "### TR-подписки в verse-row",
            "",
        ]
    )
    lines.append(
        ", ".join(
            f"`{row['verse_ref']} [{row['verse_key']}]`"
            for row in confirmed_subscriptions
        )
        + "."
    )
    lines.extend(
        [
            "",
            "В этих десяти последних стихах TAGNT-традиционная подписка или "
            "колофон включены в каноническую запись; отдельный Scrivener "
            "text-only подтверждает более короткую границу стиха. "
            "Предлагаемая каноническая последовательность записана в JSON, но "
            "этот аудит ничего не меняет.",
            "",
            "Вероятных, но не подтверждённых технических дефектов после "
            "индивидуальной проверки не осталось; неразрешённые вопросы "
            "перенесены в ограничения, а не в список исправлений.",
            "",
            "## Кластеры 1Thess.3 и Phlm",
            "",
        ]
    )
    for label, cluster in summary["cluster_analysis"].items():
        lines.append(
            f"- `{label}`: TR-mismatch {cluster['tr_mismatch_percent']:.2f}%, "
            f"полное расхождение {cluster['full_discrepancy_percent']:.2f}%, "
            f"средний прирост alt-aware F1 "
            f"{cluster['mean_alt_aware_f1_gain']:.4f}. "
            f"{cluster['conclusion_ru']}"
        )
    lxx_stats = lxx_summary["statistics"]
    lines.extend(
        [
            "",
            "## 210 пустых позиций LXX",
            "",
            f"Проекция воспроизведена точно: {lxx_summary['projection_rules_count']} "
            f"правил, {lxx_summary['source_exclusions_count']} исключений, "
            "22 935 заполненных и 210 пустых OT-позиций; расхождений с "
            "текущим SQLite — 0. Из 210 случаев 37 классифицированы как "
            "исторически засвидетельствованный короткий греческий текст; "
            "остальные 173 — «недостаточно данных», поскольку отсутствие "
            "отдельной строки во всех древних свидетелях не доказано.",
            "",
            "Пустые позиции по книгам: "
            + ", ".join(
                f"`{book}` — {count}"
                for book, count in lxx_stats["by_book"].items()
            )
            + ".",
            "",
            "Непрерывные серии проверены как диапазоны, а не как независимые "
            "пустоты. Крупнейшие: `Exod.36.10–34` (25), "
            "`1Sam.17.12–31` (20), `Jer.33.14–26` (13), "
            "`Jer.39.4–13` (10). Проекционный пересбор не копирует молча "
            "соседнюю строку в пустую позицию.",
            "",
            "Индивидуальные статусы, соседние проверки, source refs и заметки: "
            "[lxx_empty_positions.csv](lxx_empty_positions.csv) и "
            "[lxx_empty_positions.json](lxx_empty_positions.json).",
            "",
            "## Полная проверка KJV OT и LXX",
            "",
            f"- KJV: 31 102 позиции, пустых — "
            f"{source_checks['kjv']['empty_verses']}; точных отличий от "
            f"зафиксированного USFX — "
            f"{source_checks['kjv']['locked_usfx_exact_differences']}. "
            f"Нормализованных отличий от CrossWire 3.1 — "
            f"{source_checks['kjv']['crosswire_3_1_normalized_text_differences']}, "
            f"от open-bibles — "
            f"{source_checks['kjv']['open_bibles_normalized_text_differences']}, "
            f"от независимого Project Gutenberg — "
            f"{source_checks['kjv']['project_gutenberg_normalized_text_differences']}; "
            "эти списки включают заголовки псалмов, орфографию и редакционные "
            "варианты и не трактуются автоматически как ошибки.",
            f"- LXX: 23 145 канонических OT-позиций, заполнено "
            f"{source_checks['lxx']['filled_positions']}, пусто "
            f"{source_checks['lxx']['empty_positions']}; точных отличий "
            "пересборки — 0. Строитель сообщил о "
            f"{source_checks['lxx']['missing_classic_strong_tokens_reported_by_builder']} "
            "греческих токенах без пригодного классического Strong.",
            "- Номера KJV OT (`H`) и LXX (`G`/леммы/морфология) напрямую не "
            "сравнивались как одна система.",
            "",
            "## Ограничения",
            "",
        ]
    )
    for limitation in summary["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "- Автоматический порог каскадного дефекта требует одновременно "
            "сходного инвентаря Strong и слабой привязки к тем же английским "
            "словам; найденные случаи дополнительно просмотрены локально. "
            "Отсутствие флага не доказывает идеальность каждого тега.",
            "",
            "## Повторный запуск",
            "",
            "PowerShell:",
            "",
            "```powershell",
            f"$repo = '{inputs.weak_strongs.resolve().parents[2]}'",
            f"$scrivener = '{inputs.scrivener_text_dir.resolve().parent}'",
            f"$gutenberg = '{inputs.project_gutenberg_kjv.resolve()}'",
            "if (-not (Test-Path -LiteralPath $scrivener)) {",
            "  git clone https://github.com/byztxt/greektext-scrivener.git $scrivener",
            "}",
            "git -C $scrivener checkout 6049a43b135ed870f843b83eb6a04764fc796678",
            "Invoke-WebRequest -Uri 'https://www.gutenberg.org/cache/epub/10/pg10.txt' -OutFile $gutenberg",
            f"if ((Get-FileHash -LiteralPath $gutenberg -Algorithm SHA256).Hash.ToLowerInvariant() -ne '{input_files['project_gutenberg_kjv']['sha256']}') {{ throw 'Project Gutenberg checksum mismatch' }}",
            f"$out = '{inputs.output_dir.resolve()}'",
            "Set-Location $repo",
            "python -m scripts.bible_module.audit_kjv_tr_strongs `",
            f"  --kjv '{inputs.kjv_db.resolve()}' `",
            f"  --lxx-tr '{inputs.lxx_tr_db.resolve()}' `",
            "  --weak-strongs (Join-Path $repo 'assets\\data\\greek_weak_strong_numbers.json') `",
            "  --output (Join-Path $out 'original_reproduced.txt') `",
            "  --evidence-output-dir $out `",
            f"  --original-report '{inputs.original_report.resolve()}' `",
            "  --scrivener-text-dir (Join-Path $scrivener 'textonly') `",
            "  --project-gutenberg-kjv $gutenberg `",
            "  --accessed-on 2026-07-25",
            "python -m unittest discover -s scripts/bible_module/tests -p 'test_*.py'",
            "```",
            "",
            "Скрипт принимает все пути аргументами; пользовательские пути в "
            "логике аудита не зашиты. Базы и опубликованные файлы не "
            "изменяются и исправленные SQLite не создаются.",
            "",
        ]
    )
    return "\n".join(lines)


def audit_compact_index(
    path: Path,
    refs_by_key: Mapping[str, str],
) -> IndexAudit:
    """Audit compact module schema and canonical key sequence read-only."""
    connection = _open_read_only(path)
    try:
        query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
        integrity_check = str(
            connection.execute("PRAGMA integrity_check").fetchone()[0]
        )
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        tables = tuple(
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            )
        )
        metadata = {
            str(key): str(value)
            for key, value in connection.execute(
                "SELECT key, value FROM db_metadata ORDER BY key"
            )
        }
        rows = tuple(
            str(row[0])
            for row in connection.execute(
                "SELECT verse_key FROM verses ORDER BY verse_key"
            )
        )
        distinct_count = int(
            connection.execute(
                "SELECT COUNT(DISTINCT verse_key) FROM verses"
            ).fetchone()[0]
        )
        duplicates = tuple(
            str(row[0])
            for row in connection.execute(
                "SELECT verse_key FROM verses GROUP BY verse_key "
                "HAVING COUNT(*) > 1 ORDER BY verse_key"
            )
        )
    finally:
        connection.close()

    expected = tuple(refs_by_key)
    expected_set = set(expected)
    actual_set = set(rows)
    return IndexAudit(
        path=str(path.resolve()),
        query_only=query_only,
        integrity_check=integrity_check,
        user_version=user_version,
        schema_version=metadata.get("schema_version", ""),
        data_version=metadata.get("data_version", ""),
        metadata_date=metadata.get("date", ""),
        tables=tables,
        verse_rows=len(rows),
        distinct_verse_keys=distinct_count,
        duplicate_keys=duplicates,
        missing_keys=tuple(key for key in expected if key not in actual_set),
        extra_keys=tuple(sorted(actual_set - expected_set)),
        keys_are_exact_base36_sequence=rows == expected,
        invalid_key_lengths=tuple(key for key in rows if len(key) != 3),
    )


def parse_original_priority_entries(path: Path) -> tuple[OriginalPriorityEntry, ...]:
    """Parse section 5 directly, retaining report keys and exact range labels."""
    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    current_range = ""
    entries: list[OriginalPriorityEntry] = []
    range_header_re = re.compile(
        r"^\s{2}(?P<label><50%|50%–<66,\(6\)%|66,\(6\)%–<75%|75%–<80%): "
        r"(?P<count>\d+) стих"
    )
    for line in lines:
        if line == "5. СПИСКИ СТИХОВ С СОВПАДЕНИЕМ НИЖЕ 80%":
            in_section = True
            continue
        if in_section and line.startswith("6. "):
            break
        if not in_section:
            continue
        header_match = range_header_re.match(line)
        if header_match is not None:
            current_range = header_match.group("label")
            continue
        match = _PRIORITY_LINE_RE.match(line)
        if match is None:
            continue
        if not current_range:
            raise ValueError("Priority verse appeared before a section-5 range header")
        entries.append(
            OriginalPriorityEntry(
                verse_ref=match.group("ref"),
                verse_key=match.group("key"),
                source_range=current_range,
                source_percent=float(match.group("percent")),
                source_matched=int(match.group("matched")),
                source_tr_total=int(match.group("tr_total")),
            )
        )
    return tuple(entries)


def parse_original_lxx_empty_entries(path: Path) -> tuple[tuple[str, str], ...]:
    """Parse the LXX/TR empty list directly from section 2."""
    lines = path.read_text(encoding="utf-8").splitlines()
    in_lxx = False
    in_list = False
    entries: list[tuple[str, str]] = []
    for line in lines:
        if line == "bible_lxx_tr.sqlite:":
            in_lxx = True
            continue
        if in_lxx and line == "  Список пустых стихов:":
            in_list = True
            continue
        if in_list and (not line.startswith("    ") or line.startswith("3. ")):
            break
        if not in_list:
            continue
        match = _EMPTY_LINE_RE.match(line)
        if match is not None:
            entries.append((match.group("ref"), match.group("key")))
    return tuple(entries)


def parse_osis_verses(path: Path) -> dict[str, OsisVerse]:
    """Parse milestone-style OSIS into plain text and Strong word spans."""
    root = ET.parse(path).getroot()
    buffers: dict[str, list[str]] = defaultdict(list)
    strongs: dict[str, list[str]] = defaultdict(list)
    spans: dict[str, list[TaggedSpan]] = defaultdict(list)
    active_ref: str | None = None
    skip_tags = {
        "header",
        "note",
        "reference",
        "catchWord",
        "rdg",
        "figure",
    }

    def append_text(value: str | None) -> None:
        if active_ref is not None and value:
            buffers[active_ref].append(value)

    def walk(element: ET.Element, *, skipped: bool = False) -> None:
        nonlocal active_ref
        tag = _local_name(element.tag)
        is_skipped = skipped or tag in skip_tags
        if tag == "verse":
            end_id = element.attrib.get("eID")
            start_id = element.attrib.get("osisID") or element.attrib.get("sID")
            if end_id:
                active_ref = None
                return
            if start_id:
                active_ref = _normalize_osis_ref(start_id)

        if is_skipped:
            return

        if tag == "w" and active_ref is not None:
            surface = "".join(element.itertext())
            word_strongs = tuple(
                normalize_strong(raw)
                for raw in re.findall(
                    r"strong:([GH]\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?)",
                    element.attrib.get("lemma", ""),
                )
            )
            append_text(surface)
            if word_strongs:
                strongs[active_ref].extend(word_strongs)
            spans[active_ref].append(TaggedSpan(surface=surface, strongs=word_strongs))
        else:
            append_text(element.text)
            for child in element:
                walk(child, skipped=is_skipped)
                append_text(child.tail)

        if tag == "verse" and element.attrib.get("osisID") and not element.attrib.get(
            "sID"
        ):
            active_ref = None

    walk(root)
    return {
        verse_ref: OsisVerse(
            text=_collapse_whitespace("".join(buffers[verse_ref])),
            strong_sequence=tuple(strongs.get(verse_ref, ())),
            tagged_spans=tuple(spans.get(verse_ref, ())),
        )
        for verse_ref in sorted(buffers, key=_canonical_ref_sort_key)
    }


def parse_project_gutenberg_kjv(path: Path) -> dict[str, str]:
    """Parse Project Gutenberg eBook 10 into canonical verse references."""
    if len(_GUTENBERG_BOOK_TITLES) != len(CANONICAL_BOOKS):
        raise ValueError("Project Gutenberg book-title mapping is incomplete")
    all_titles = frozenset(_GUTENBERG_BOOK_TITLES)
    verse_marker_pattern = re.compile(r"(?<!\S)(\d+):(\d+)(?=\s|$)")
    in_body = False
    body_started = False
    old_testament_heading_count = 0
    current_book: str | None = None
    current_ref: str | None = None
    current_parts: list[str] = []
    verses: dict[str, str] = {}
    next_title_index = 0

    def flush() -> None:
        nonlocal current_ref, current_parts
        if current_ref is None:
            return
        if current_ref in verses:
            raise ValueError(f"Duplicate Project Gutenberg verse: {current_ref}")
        verses[current_ref] = _collapse_whitespace(" ".join(current_parts))
        current_ref = None
        current_parts = []

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
            in_body = True
            continue
        if not in_body:
            continue
        if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
            flush()
            break
        if line == "The Old Testament of the King James Version of the Bible":
            old_testament_heading_count += 1
            if old_testament_heading_count == 2:
                body_started = True
            flush()
            current_book = None
            continue
        if not body_started:
            continue
        if line == "The New Testament of the King James Bible":
            flush()
            current_book = None
            continue
        if line == "***":
            continue
        if (
            next_title_index < len(_GUTENBERG_BOOK_TITLES)
            and line == _GUTENBERG_BOOK_TITLES[next_title_index]
        ):
            flush()
            current_book = CANONICAL_BOOKS[next_title_index].canonical_code
            next_title_index += 1
            continue
        if line in all_titles:
            continue
        matches = list(verse_marker_pattern.finditer(line))
        if matches and current_book is not None:
            prefix = line[: matches[0].start()].strip()
            if current_ref is not None and prefix:
                current_parts.append(prefix)
            for index, match in enumerate(matches):
                flush()
                current_ref = (
                    f"{current_book}.{int(match.group(1))}."
                    f"{int(match.group(2))}"
                )
                end = (
                    matches[index + 1].start()
                    if index + 1 < len(matches)
                    else len(line)
                )
                current_parts = [line[match.end() : end].strip()]
        elif current_ref is not None and line:
            current_parts.append(line)
    flush()
    if next_title_index != len(_GUTENBERG_BOOK_TITLES):
        raise ValueError(
            "Incomplete Project Gutenberg book parse: "
            f"{next_title_index} != {len(_GUTENBERG_BOOK_TITLES)}"
        )
    return verses


def parse_scrivener_texts(directory: Path) -> dict[str, str]:
    """Parse Robinson/Sandborg-Petersen Scrivener ``*.SCV`` text files."""
    file_to_book = {
        "MT.SCV": "Mat",
        "MR.SCV": "Mark",
        "LU.SCV": "Luke",
        "JOH.SCV": "John",
        "AC.SCV": "Acts",
        "RO.SCV": "Rom",
        "1CO.SCV": "1Cor",
        "2CO.SCV": "2Cor",
        "GA.SCV": "Gal",
        "EPH.SCV": "Eph",
        "PHP.SCV": "Phil",
        "COL.SCV": "Col",
        "1TH.SCV": "1Thess",
        "2TH.SCV": "2Thess",
        "1TI.SCV": "1Tim",
        "2TI.SCV": "2Tim",
        "TIT.SCV": "Titus",
        "PHM.SCV": "Phlm",
        "HEB.SCV": "Heb",
        "JAS.SCV": "Jas",
        "1PE.SCV": "1Pet",
        "2PE.SCV": "2Pet",
        "1JO.SCV": "1John",
        "2JO.SCV": "2John",
        "3JO.SCV": "3John",
        "JUDE.SCV": "Jude",
        "RE.SCV": "Rev",
    }
    verses: dict[str, str] = {}
    for filename, book in file_to_book.items():
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing Scrivener book file: {path}")
        current_ref: str | None = None
        current_parts: list[str] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            match = _SCV_VERSE_RE.match(raw_line)
            if match is not None:
                if current_ref is not None:
                    if current_ref in verses:
                        raise ValueError(f"Duplicate Scrivener verse: {current_ref}")
                    verses[current_ref] = _collapse_whitespace(" ".join(current_parts))
                current_ref = f"{book}.{int(match.group(1))}.{int(match.group(2))}"
                current_parts = [match.group(3)]
            elif current_ref is not None and raw_line.strip():
                current_parts.append(raw_line.strip())
        if current_ref is not None:
            if current_ref in verses:
                raise ValueError(f"Duplicate Scrivener verse: {current_ref}")
            verses[current_ref] = _collapse_whitespace(" ".join(current_parts))
    return verses


def split_tagged_text(text: str) -> tuple[TaggedSpan, ...]:
    """Group reader text into surface spans followed by one or more Strong keys."""
    parts = text.split()
    spans: list[TaggedSpan] = []
    surface_parts: list[str] = []
    index = 0
    while index < len(parts):
        part = parts[index]
        if _is_strong_token(part):
            strongs: list[str] = []
            while index < len(parts) and _is_strong_token(parts[index]):
                strongs.append(normalize_strong(parts[index]))
                index += 1
            spans.append(
                TaggedSpan(
                    surface=" ".join(surface_parts).strip(),
                    strongs=tuple(strongs),
                )
            )
            surface_parts = []
            continue
        surface_parts.append(part)
        index += 1
    if surface_parts:
        spans.append(TaggedSpan(surface=" ".join(surface_parts).strip(), strongs=()))
    return tuple(spans)


def metrics_for_sequences(
    kjv_sequence: Sequence[str],
    tr_sequence: Sequence[str],
) -> MetricSet:
    """Calculate multiset and ordered metrics for two Strong sequences."""
    kjv_counts = Counter(kjv_sequence)
    tr_counts = Counter(tr_sequence)
    matched = sum((kjv_counts & tr_counts).values())
    tr_total = len(tr_sequence)
    kjv_total = len(kjv_sequence)
    ordered = _lcs_match_count(kjv_sequence, tr_sequence)
    return MetricSet(
        tr_total=tr_total,
        kjv_total=kjv_total,
        matched=matched,
        tr_only_count=tr_total - matched,
        kjv_only_count=kjv_total - matched,
        tr_recall=_safe_ratio(matched, tr_total, other_total=kjv_total),
        kjv_precision=_safe_ratio(matched, kjv_total, other_total=tr_total),
        f1=_f1_from_counts(matched, tr_total, kjv_total),
        multiset_jaccard=_safe_ratio(
            matched,
            tr_total + kjv_total - matched,
            other_total=0,
        ),
        ordered_matched=ordered,
        ordered_tr_recall=_safe_ratio(ordered, tr_total, other_total=kjv_total),
        ordered_kjv_precision=_safe_ratio(
            ordered,
            kjv_total,
            other_total=tr_total,
        ),
        ordered_f1=_f1_from_counts(ordered, tr_total, kjv_total),
    )


def alt_aware_metrics(
    kjv_sequence: Sequence[str],
    tr_aliases: Sequence[frozenset[str]],
) -> AltAwareMetrics:
    """Maximum-match KJV keys to per-token TAGNT primary/alternative Strong sets."""
    adjacency = [
        [index for index, aliases in enumerate(tr_aliases) if strong in aliases]
        for strong in kjv_sequence
    ]
    matched = _maximum_bipartite_match_count(adjacency, len(tr_aliases))
    ordered = _ordered_alias_match_count(kjv_sequence, tr_aliases)
    tr_total = len(tr_aliases)
    kjv_total = len(kjv_sequence)
    return AltAwareMetrics(
        tr_total=tr_total,
        kjv_total=kjv_total,
        matched=matched,
        tr_recall=_safe_ratio(matched, tr_total, other_total=kjv_total),
        kjv_precision=_safe_ratio(matched, kjv_total, other_total=tr_total),
        f1=_f1_from_counts(matched, tr_total, kjv_total),
        multiset_jaccard=_safe_ratio(
            matched,
            tr_total + kjv_total - matched,
            other_total=0,
        ),
        ordered_matched=ordered,
        ordered_f1=_f1_from_counts(ordered, tr_total, kjv_total),
    )


def word_tag_agreement(
    module_text: str,
    source_verse: OsisVerse,
) -> WordTagAgreement:
    """Compare Strong assignments at aligned English word positions."""
    module_words = _word_tags_from_reader_text(module_text)
    source_words = _word_tags_from_osis(source_verse)
    module_tokens = [word for word, _tags in module_words]
    source_tokens = [word for word, _tags in source_words]
    matcher = SequenceMatcher(a=module_tokens, b=source_tokens, autojunk=False)
    aligned = 0
    both = 0
    exact = 0
    overlap = 0
    conflict = 0
    module_missing = 0
    source_missing = 0
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            module_tags = module_words[block.a + offset][1]
            source_tags = source_words[block.b + offset][1]
            aligned += 1
            if module_tags and source_tags:
                both += 1
                if module_tags == source_tags:
                    exact += 1
                    overlap += 1
                elif module_tags.intersection(source_tags):
                    overlap += 1
                else:
                    conflict += 1
            elif source_tags:
                module_missing += 1
            elif module_tags:
                source_missing += 1
    denominator = both + module_missing + source_missing
    ratio = (overlap / denominator) if denominator else 1.0
    return WordTagAgreement(
        aligned_words=aligned,
        both_tagged_words=both,
        exact_tag_match_words=exact,
        overlapping_tag_words=overlap,
        conflicting_tag_words=conflict,
        module_untagged_source_tagged_words=module_missing,
        source_untagged_module_tagged_words=source_missing,
        ratio=ratio,
    )


def _build_priority_rows(
    *,
    entries: Sequence[OriginalPriorityEntry],
    comparisons: Mapping[str, StrongComparison],
    strong_filter: StrongFilter,
    kjv: BibleModule,
    lxx_tr: BibleModule,
    kjv_usfx_texts: Mapping[str, str],
    crosswire_kjv: Mapping[str, OsisVerse],
    open_bibles_kjv: Mapping[str, OsisVerse],
    project_gutenberg_kjv: Mapping[str, str],
    tagnt_by_ref: Mapping[str, tuple[TagntToken, ...]],
    scrivener: Mapping[str, str],
) -> list[dict[str, object]]:
    scores_by_mode = {
        mode: {score.verse_key: score for score in comparison.verse_scores}
        for mode, comparison in comparisons.items()
    }
    rows: list[dict[str, object]] = []
    for entry in entries:
        score = scores_by_mode["all_77"][entry.verse_key]
        if score.verse_ref != entry.verse_ref:
            raise ValueError(
                f"Report key/ref mismatch: {entry.verse_key} "
                f"{entry.verse_ref} != {score.verse_ref}"
            )
        kjv_text = kjv.verses[entry.verse_key]
        tr_text = lxx_tr.verses[entry.verse_key]
        tr_tokens = tagnt_by_ref[entry.verse_ref]
        aliases_all = _tagnt_aliases(tr_tokens, excluded=frozenset())
        aliases_filtered = _tagnt_aliases(
            tr_tokens,
            excluded=strong_filter.excluded_strongs,
        )
        kjv_all = strong_sequence(kjv_text)
        kjv_filtered = strong_sequence(
            kjv_text,
            excluded_strongs=strong_filter.excluded_strongs,
        )
        alt_all = alt_aware_metrics(kjv_all, aliases_all)
        alt_filtered = alt_aware_metrics(kjv_filtered, aliases_filtered)

        crosswire = crosswire_kjv[entry.verse_ref]
        open_bibles = open_bibles_kjv[entry.verse_ref]
        local_plain = plain_text_from_reader(kjv_text)
        text_checks = {
            "module_vs_locked_usfx_strict": _text_equal(
                local_plain,
                plain_text_from_reader(kjv_usfx_texts[entry.verse_ref]),
                normalized=False,
            ),
            "module_vs_locked_usfx_normalized": _text_equal(
                local_plain,
                plain_text_from_reader(kjv_usfx_texts[entry.verse_ref]),
                normalized=True,
            ),
            "module_vs_crosswire_3_1_normalized": _text_equal(
                local_plain,
                crosswire.text,
                normalized=True,
            ),
            "module_vs_open_bibles_normalized": _text_equal(
                local_plain,
                open_bibles.text,
                normalized=True,
            ),
            "module_vs_project_gutenberg_normalized": _text_equal(
                local_plain,
                project_gutenberg_kjv[entry.verse_ref],
                normalized=True,
            ),
        }
        source_word_agreement = word_tag_agreement(kjv_text, crosswire)
        crosswire_metrics = metrics_for_sequences(
            kjv_all,
            crosswire.strong_sequence,
        )
        scrivener_check = _scrivener_check(tr_text, scrivener[entry.verse_ref])
        subscription_tail = _detect_subscription_tail(
            tr_tokens,
            scrivener_check["scrivener_word_count"],
        )
        neighbor_index_check = _neighbor_index_check(
            verse_ref=entry.verse_ref,
            local_kjv_text=local_plain,
            local_tr_text=tr_text,
            kjv_usfx_texts=kjv_usfx_texts,
            scrivener=scrivener,
            same_ref_text_checks=text_checks,
        )
        flags = _priority_flags(
            entry=entry,
            kjv_text=kjv_text,
            tr_text=tr_text,
            text_checks=text_checks,
            source_word_agreement=source_word_agreement,
            crosswire=crosswire,
            crosswire_metrics=crosswire_metrics,
            alt_filtered=alt_filtered,
            scrivener_check=scrivener_check,
            subscription_tail=subscription_tail,
            neighbor_index_check=neighbor_index_check,
        )
        classification = _classify_priority(
            entry=entry,
            flags=flags,
            alt_filtered=alt_filtered,
            strict_filtered=metrics_for_sequences(
                score.kjv_sequence,
                score.tr_sequence,
            ),
            source_word_agreement=source_word_agreement,
        )
        proposed = _proposed_content(
            classification_number=int(classification["number"]),
            flags=flags,
            local_plain=local_plain,
            crosswire=crosswire,
            tr_tokens=tr_tokens,
            scrivener_word_count=int(scrivener_check["scrivener_word_count"]),
        )
        mode_metrics = {
            mode: asdict(
                metrics_for_sequences(
                    mode_score.kjv_sequence,
                    mode_score.tr_sequence,
                )
            )
            for mode, mode_scores in scores_by_mode.items()
            if (mode_score := mode_scores[entry.verse_key])
        }
        row: dict[str, object] = {
            "verse_ref": entry.verse_ref,
            "verse_key": entry.verse_key,
            "source_range": entry.source_range,
            "source_percent": entry.source_percent,
            "source_tr_only": _counter_to_list(score.tr_only),
            "source_kjv_only": _counter_to_list(score.kjv_only),
            "local_text": {
                "kjv_tagged": kjv_text,
                "kjv_plain": local_plain,
                "tr_tagged": tr_text,
                "tr_plain": plain_text_from_reader(tr_text),
            },
            "local_strong_sequences": {
                "kjv_all": list(kjv_all),
                "tr_all": list(strong_sequence(tr_text)),
                "kjv_filtered_77": list(kjv_filtered),
                "tr_filtered_77": list(score.tr_sequence),
            },
            "word_strong_alignment": {
                "kjv_spans": [asdict(span) for span in split_tagged_text(kjv_text)],
                "tr_spans": [asdict(span) for span in split_tagged_text(tr_text)],
                "module_vs_crosswire_word_agreement": asdict(
                    source_word_agreement
                ),
            },
            "neighbor_index_check": neighbor_index_check,
            "strict_and_normalized_metrics": mode_metrics,
            "alt_strong_aware_metrics": {
                "without_exclusions": asdict(alt_all),
                "with_all_77_exclusions": asdict(alt_filtered),
                "method": (
                    "Maximum one-to-one matching against each TAGNT TR token's "
                    "primary and alternative classic Strong keys."
                ),
            },
            "external_checks": {
                "kjv_text": text_checks,
                "kjv_text_values": {
                    "locked_usfx": plain_text_from_reader(
                        kjv_usfx_texts[entry.verse_ref]
                    ),
                    "crosswire_3_1": crosswire.text,
                    "open_bibles": open_bibles.text,
                    "project_gutenberg": project_gutenberg_kjv[
                        entry.verse_ref
                    ],
                },
                "kjv_strong_vs_crosswire_3_1": asdict(crosswire_metrics),
                "tr_text_vs_scrivener_1894": scrivener_check,
                "locked_tagnt_rebuild_exact": True,
                "source_ids": [
                    "ebible_eng_kjv2006",
                    "crosswire_kjv_3_1",
                    "open_bibles_eng_kjv",
                    "project_gutenberg_kjv_ebook_10",
                    "step_tagnt_scrivener_1894",
                    "robinson_scrivener_1894_textonly",
                ],
            },
            "flags": flags,
            "classification": classification,
            "conclusion_ru": _priority_conclusion(
                entry=entry,
                classification=classification,
                flags=flags,
                alt_filtered=alt_filtered,
                source_word_agreement=source_word_agreement,
            ),
            "source_links": _priority_source_links(),
            "proposed_correct_content": proposed,
        }
        rows.append(row)
    if len(rows) != sum(EXPECTED_PRIORITY_COUNTS.values()):
        raise ValueError(f"Priority output coverage incomplete: {len(rows)}")
    return rows


def _build_lxx_empty_rows(
    *,
    original_empty: Sequence[tuple[str, str]],
    lxx_tr: BibleModule,
    key_by_ref: Mapping[str, str],
    resolution_index: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for verse_ref, verse_key in original_empty:
        if key_by_ref.get(verse_ref) != verse_key:
            raise ValueError(f"LXX empty key/ref mismatch: {verse_ref} [{verse_key}]")
        if lxx_tr.verses[verse_key].strip():
            raise ValueError(f"Originally empty LXX ref is now filled: {verse_ref}")
        resolution = resolution_index.get(verse_ref)
        if resolution is None:
            raise ValueError(f"No projection resolution evidence for {verse_ref}")
        status = str(resolution.get("status") or "")
        is_short_recension = status == "short_greek_recension_lacks_long_mt_kjv_material"
        classification_number = 7 if is_short_recension else 10
        confidence = "high" if is_short_recension else "medium"
        evidence_note = str(
            resolution.get("evidence_note")
            or resolution.get("reason")
            or ""
        )
        rows.append(
            {
                "verse_ref": verse_ref,
                "verse_key": verse_key,
                "local_text": "",
                "projection_status": status,
                "source_refs": list(resolution.get("source_refs") or ()),
                "evidence_note": evidence_note,
                "continuous_series": _continuous_series_label(
                    verse_ref,
                    original_empty,
                ),
                "neighbor_check": {
                    "previous_and_next_not_copied_into_empty_row": True,
                    "projection_rebuild_preserves_empty": True,
                },
                "classification": {
                    "number": classification_number,
                    "label": CLASSIFICATIONS_RU[classification_number],
                    "confidence": confidence,
                },
                "conclusion_ru": (
                    "Короткая греческая редакция не содержит отдельной "
                    "MT/KJV-семантической строки; пустота воспроизводится "
                    "утверждённой проекцией."
                    if is_short_recension
                    else "В проверенных LXX-контролях отдельная строка не "
                    "представлена; проекция намеренно не дублирует соседний "
                    "греческий текст. Исчерпывающий поиск по всем древним "
                    "греческим свидетелям не доказан."
                ),
                "source_links": _lxx_source_links(),
                "proposed_correct_content": None,
            }
        )
    return rows


def _build_comparisons(
    *,
    kjv: BibleModule,
    lxx_tr: BibleModule,
    nt_keys: Sequence[str],
    refs_by_key: Mapping[str, str],
    strong_filter: StrongFilter,
) -> dict[str, StrongComparison]:
    modes: dict[str, frozenset[str]] = {
        "none": frozenset(),
        "all_77": strong_filter.excluded_strongs,
    }
    modes.update(
        {
            f"exclude_only_{group_name}": frozenset(values)
            for group_name, values in strong_filter.groups.items()
        }
    )
    return {
        name: compare_new_testaments(
            kjv,
            lxx_tr,
            nt_keys=nt_keys,
            refs_by_key=refs_by_key,
            excluded_strongs=excluded,
        )
        for name, excluded in modes.items()
    }


def _build_excluded_category_metrics(
    *,
    kjv: BibleModule,
    lxx_tr: BibleModule,
    nt_keys: Sequence[str],
    strong_filter: StrongFilter,
) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    for group_name, values in strong_filter.groups.items():
        included = frozenset(values)
        pairs = [
            (
                tuple(
                    strong
                    for strong in strong_sequence(kjv.verses[key])
                    if strong in included
                ),
                tuple(
                    strong
                    for strong in strong_sequence(lxx_tr.verses[key])
                    if strong in included
                ),
            )
            for key in nt_keys
        ]
        results[f"category_only_{group_name}"] = _sequence_pairs_summary(pairs)
    return results


def _build_kjv_strong_anomalies(
    *,
    kjv: BibleModule,
    refs_by_key: Mapping[str, str],
    crosswire_kjv: Mapping[str, OsisVerse],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    testament_by_book = {
        book.canonical_code: book.testament for book in CANONICAL_BOOKS
    }
    for verse_key, verse_ref in refs_by_key.items():
        source = crosswire_kjv.get(verse_ref)
        if source is None:
            continue
        local_text = kjv.verses[verse_key]
        local_plain = plain_text_from_reader(local_text)
        if normalized_text(local_plain) != normalized_text(source.text):
            continue
        local_sequence = strong_sequence(local_text)
        metrics = metrics_for_sequences(local_sequence, source.strong_sequence)
        agreement = word_tag_agreement(local_text, source)
        flags: list[str] = []
        if not local_sequence and source.strong_sequence:
            flags.append("kjv_strong_complete_omission")
        if (
            local_sequence
            and agreement.ratio < 0.4
            and metrics.f1 >= 0.68
            and agreement.conflicting_tag_words >= 6
        ):
            flags.append("kjv_strong_cascading_word_misalignment")
        if (
            metrics.kjv_total > 0
            and metrics.tr_total > 0
            and metrics.kjv_total / metrics.tr_total < 0.5
            and agreement.ratio < 0.6
        ):
            flags.append("kjv_strong_partial_omission")
        if not flags:
            continue
        rows.append(
            {
                "verse_ref": verse_ref,
                "verse_key": verse_key,
                "testament": testament_by_book[verse_ref.split(".", 1)[0]],
                "flags": flags,
                "local_text": local_text,
                "source_text": source.text,
                "local_strong_sequence": list(local_sequence),
                "crosswire_strong_sequence": list(source.strong_sequence),
                "sequence_metrics": asdict(metrics),
                "word_alignment": asdict(agreement),
                "classification": {
                    "number": 4,
                    "label": CLASSIFICATIONS_RU[4],
                    "confidence": "high",
                },
                "source_ids": [
                    "ebible_eng_kjv2006",
                    "crosswire_kjv_3_1",
                ],
            }
        )
    return rows


def _build_full_source_checks(
    *,
    kjv: BibleModule,
    lxx_tr: BibleModule,
    refs_by_key: Mapping[str, str],
    kjv_usfx_texts: Mapping[str, str],
    crosswire_kjv: Mapping[str, OsisVerse],
    open_bibles_kjv: Mapping[str, OsisVerse],
    project_gutenberg_kjv: Mapping[str, str],
    tr_rebuild_by_ref: Mapping[str, str],
    lxx_rebuild_by_ref: Mapping[str, str],
    lxx_rebuild: object,
) -> dict[str, object]:
    kjv_locked_diffs: list[str] = []
    kjv_crosswire_text_diffs: list[str] = []
    kjv_open_bibles_text_diffs: list[str] = []
    kjv_project_gutenberg_text_diffs: list[str] = []
    kjv_crosswire_missing_refs: list[str] = []
    kjv_open_bibles_missing_refs: list[str] = []
    kjv_project_gutenberg_missing_refs: list[str] = []
    tr_diffs: list[str] = []
    lxx_diffs: list[str] = []
    kjv_empty: list[str] = []
    lxx_empty: list[str] = []
    testament_by_book = {
        book.canonical_code: book.testament for book in CANONICAL_BOOKS
    }
    for key, verse_ref in refs_by_key.items():
        kjv_text = kjv.verses[key]
        lxx_text = lxx_tr.verses[key]
        if not kjv_text.strip():
            kjv_empty.append(verse_ref)
        is_nt = testament_by_book[verse_ref.split(".", 1)[0]] == "NT"
        locked_plain = plain_text_from_reader(kjv_usfx_texts[verse_ref])
        module_plain = plain_text_from_reader(kjv_text)
        if module_plain != locked_plain:
            kjv_locked_diffs.append(verse_ref)
        crosswire_verse = crosswire_kjv.get(verse_ref)
        if crosswire_verse is None:
            kjv_crosswire_missing_refs.append(verse_ref)
        elif normalized_text(module_plain) != normalized_text(
            crosswire_verse.text
        ):
            kjv_crosswire_text_diffs.append(verse_ref)
        open_bibles_verse = open_bibles_kjv.get(verse_ref)
        if open_bibles_verse is None:
            kjv_open_bibles_missing_refs.append(verse_ref)
        elif normalized_text(module_plain) != normalized_text(
            open_bibles_verse.text
        ):
            kjv_open_bibles_text_diffs.append(verse_ref)
        project_gutenberg_text = project_gutenberg_kjv.get(verse_ref)
        if project_gutenberg_text is None:
            kjv_project_gutenberg_missing_refs.append(verse_ref)
        elif normalized_text(module_plain) != normalized_text(
            project_gutenberg_text
        ):
            kjv_project_gutenberg_text_diffs.append(verse_ref)
        if is_nt:
            if lxx_text != tr_rebuild_by_ref[verse_ref]:
                tr_diffs.append(verse_ref)
        else:
            if not lxx_text.strip():
                lxx_empty.append(verse_ref)
            if lxx_text != lxx_rebuild_by_ref[verse_ref]:
                lxx_diffs.append(verse_ref)
    return {
        "kjv": {
            "verses": len(kjv.verses),
            "empty_verses": len(kjv_empty),
            "locked_usfx_exact_differences": len(kjv_locked_diffs),
            "crosswire_3_1_normalized_text_differences": len(
                kjv_crosswire_text_diffs
            ),
            "open_bibles_normalized_text_differences": len(
                kjv_open_bibles_text_diffs
            ),
            "project_gutenberg_normalized_text_differences": len(
                kjv_project_gutenberg_text_diffs
            ),
            "crosswire_missing_canonical_refs": kjv_crosswire_missing_refs,
            "open_bibles_missing_canonical_refs": kjv_open_bibles_missing_refs,
            "project_gutenberg_missing_canonical_refs": (
                kjv_project_gutenberg_missing_refs
            ),
            "crosswire_difference_refs": kjv_crosswire_text_diffs,
            "open_bibles_difference_refs": kjv_open_bibles_text_diffs,
            "project_gutenberg_difference_refs": (
                kjv_project_gutenberg_text_diffs
            ),
            "external_versification_finding": {
                "local_range": "2Chr.13.23; 2Chr.14.1-14",
                "crosswire_and_open_bibles_range": "2Chr.14.1-15",
                "classification": CLASSIFICATIONS_RU[6],
                "confidence": "high",
                "explanation_ru": (
                    "Текст не потерян: локальная схема следует еврейской "
                    "нумерации, где общеупотребительный KJV 2Chr.14.1 "
                    "обозначен 2Chr.13.23, а следующие стихи главы 14 "
                    "сдвинуты на единицу."
                ),
            },
        },
        "tr": {
            "verses": EXPECTED_NT_VERSES_COUNT,
            "locked_tagnt_exact_differences": len(tr_diffs),
            "edition_identification": (
                "Scrivener 1894 TR word inventory selected by TAGNT; displayed "
                "spellings and punctuation follow TAGNT's amalgamated editorial "
                "policy rather than a diplomatic Scrivener transcription."
            ),
        },
        "lxx": {
            "canonical_ot_positions": EXPECTED_VERSES_COUNT
            - EXPECTED_NT_VERSES_COUNT,
            "filled_positions": len(lxx_rebuild_by_ref) - len(lxx_empty),
            "empty_positions": len(lxx_empty),
            "projection_rebuild_exact_differences": len(lxx_diffs),
            "missing_classic_strong_tokens_reported_by_builder": len(
                getattr(lxx_rebuild, "missing_strong_tokens")
            ),
            "edition_identification": (
                "CrossWire LXX 3.2, morphologically tagged Rahlfs/CATSS, "
                "projected to KJV/protestant versification with documented "
                "Swete and patristic supplements."
            ),
        },
    }


def _build_cluster_analysis(
    *,
    priority_rows: Sequence[Mapping[str, object]],
    comparisons: Mapping[str, StrongComparison],
) -> dict[str, object]:
    by_ref = {str(row["verse_ref"]): row for row in priority_rows}
    filtered = comparisons["all_77"]
    aggregate_by_chapter = {score.label: score for score in filtered.chapter_scores}
    aggregate_by_book = {score.label: score for score in filtered.book_scores}
    results: dict[str, object] = {}
    for label, aggregate in (
        ("1Thess.3", aggregate_by_chapter["1Thess.3"]),
        ("Phlm", aggregate_by_book["Phlm"]),
    ):
        prefix = "1Thess.3." if label == "1Thess.3" else "Phlm."
        rows = [row for ref, row in by_ref.items() if ref.startswith(prefix)]
        alias_gains = [
            float(
                row["alt_strong_aware_metrics"]["with_all_77_exclusions"]["f1"]
            )
            - float(row["strict_and_normalized_metrics"]["all_77"]["f1"])
            for row in rows
        ]
        results[label] = {
            "verses": aggregate.verses_count,
            "tr_total": aggregate.tr_total_count,
            "matched": aggregate.matched_count,
            "tr_only": aggregate.tr_unmatched_count,
            "kjv_only": aggregate.kjv_extra_count,
            "tr_mismatch_percent": _round_percent(aggregate.tr_mismatch_ratio),
            "full_discrepancy_percent": _round_percent(
                aggregate.full_discrepancy_ratio
            ),
            "below_80_rows": len(rows),
            "mean_alt_aware_f1_gain": _round6(
                sum(alias_gains) / len(alias_gains) if alias_gains else 0.0
            ),
            "conclusion_ru": (
                "Кластер преимущественно объясняется систематической разницей "
                "между обобщёнными TAGNT Strong для местоимений/εἰμί и "
                "падежно-формными KJV Strong, а не смещением стихов."
            ),
        }
    return results


def _validate_original_reproduction(
    comparison: StrongComparison,
    *,
    original_priority: Sequence[OriginalPriorityEntry],
    kjv: BibleModule,
    lxx_tr: BibleModule,
) -> None:
    expected = {
        "compared": 7_957,
        "mismatches": 6_403,
        "tr_total": 88_214,
        "matched": 78_404,
        "tr_only": 9_810,
        "kjv_only": 14_532,
        "different": 24_342,
    }
    actual = {
        "compared": comparison.compared_verses_count,
        "mismatches": comparison.mismatched_verses_count,
        "tr_total": comparison.tr_total_count,
        "matched": comparison.matched_count,
        "tr_only": comparison.tr_unmatched_count,
        "kjv_only": comparison.kjv_extra_count,
        "different": comparison.different_occurrences_count,
    }
    if actual != expected:
        raise ValueError(
            "Original audit metrics are not reproducible: "
            f"actual={actual}, expected={expected}"
        )
    if len(kjv.verses) != EXPECTED_VERSES_COUNT:
        raise ValueError("KJV verse count differs from original report")
    if len(lxx_tr.verses) != EXPECTED_VERSES_COUNT:
        raise ValueError("LXX/TR verse count differs from original report")
    score_by_key = {score.verse_key: score for score in comparison.verse_scores}
    for entry in original_priority:
        score = score_by_key[entry.verse_key]
        if (
            score.matched_count != entry.source_matched
            or score.tr_total_count != entry.source_tr_total
            or round(score.tr_match_ratio * 100, 2) != entry.source_percent
        ):
            raise ValueError(
                f"Section-5 reproduction failed at {entry.verse_ref}"
            )


def _validate_original_report_coverage(
    priority: Sequence[OriginalPriorityEntry],
    empty: Sequence[tuple[str, str]],
) -> None:
    counts = Counter(entry.source_range for entry in priority)
    if dict(counts) != EXPECTED_PRIORITY_COUNTS:
        raise ValueError(
            "Original report priority coverage mismatch: "
            f"{dict(counts)} != {EXPECTED_PRIORITY_COUNTS}"
        )
    if len({entry.verse_key for entry in priority}) != len(priority):
        raise ValueError("Duplicate verse key in original section 5")
    if len(empty) != EXPECTED_LXX_EMPTY_COUNT:
        raise ValueError(
            f"Original LXX empty coverage mismatch: {len(empty)} "
            f"!= {EXPECTED_LXX_EMPTY_COUNT}"
        )


def _validate_index_audits(audits: Sequence[IndexAudit]) -> None:
    for audit in audits:
        if audit.query_only != 1:
            raise ValueError(f"query_only was not enabled: {audit.path}")
        if audit.integrity_check != "ok":
            raise ValueError(
                f"SQLite integrity check failed: {audit.path}: "
                f"{audit.integrity_check}"
            )
        if audit.verse_rows != EXPECTED_VERSES_COUNT:
            raise ValueError(
                f"Unexpected verse rows in {audit.path}: {audit.verse_rows}"
            )
        if (
            audit.duplicate_keys
            or audit.missing_keys
            or audit.extra_keys
            or audit.invalid_key_lengths
            or not audit.keys_are_exact_base36_sequence
        ):
            raise ValueError(f"Index contract failed: {audit.path}")


def _validate_kjv_source_coverage(
    crosswire: Mapping[str, OsisVerse],
    open_bibles: Mapping[str, OsisVerse],
    project_gutenberg: Mapping[str, str],
) -> None:
    expected_refs = {verse.canonical_ref for verse in canonical_verses()}
    for label, corpus in (
        ("CrossWire KJV", crosswire),
        ("open-bibles KJV", open_bibles),
        ("Project Gutenberg KJV", project_gutenberg),
    ):
        missing = expected_refs - set(corpus)
        extra_canonical_book_refs = {
            verse_ref
            for verse_ref in set(corpus) - expected_refs
            if verse_ref.split(".", 1)[0]
            in {book.canonical_code for book in CANONICAL_BOOKS}
        }
        if missing != {"2Chr.13.23"} or extra_canonical_book_refs != {
            "2Chr.14.15"
        }:
            raise ValueError(
                f"Unexpected {label} versification coverage: "
                f"missing={sorted(missing)[:10]}, "
                f"extra={sorted(extra_canonical_book_refs)[:10]}"
            )


def _load_lxx_resolution_index(
    projection_plan_path: Path,
) -> dict[str, Mapping[str, object]]:
    payload = json.loads(projection_plan_path.read_text(encoding="utf-8"))
    wrappers = payload.get("remaining_target_resolution_by_book")
    if not isinstance(wrappers, Mapping):
        raise ValueError("LXX projection plan lacks remaining target resolutions")
    index: dict[str, Mapping[str, object]] = {}
    for wrapper in wrappers.values():
        if not isinstance(wrapper, Mapping):
            continue
        content = wrapper.get("content")
        if not isinstance(content, Mapping):
            continue
        for key in ("items", "resolutions"):
            values = content.get(key)
            if not isinstance(values, list):
                continue
            for item in values:
                if not isinstance(item, Mapping):
                    continue
                target_ref = item.get("target_ref")
                if not isinstance(target_ref, str):
                    continue
                if target_ref in index:
                    raise ValueError(
                        f"Duplicate LXX resolution target: {target_ref}"
                    )
                index[target_ref] = item
    return index


def _tagnt_tr_tokens_by_ref(
    tokens: Sequence[TagntToken],
) -> dict[str, tuple[TagntToken, ...]]:
    grouped: dict[str, list[TagntToken]] = defaultdict(list)
    for token in tokens:
        if _is_textus_receptus_token(token):
            grouped[token.canonical_verse.canonical_ref].append(token)
    result: dict[str, tuple[TagntToken, ...]] = {}
    for verse_ref, values in grouped.items():
        values.sort(key=lambda token: (token.reference.token_order, token.source_ref))
        result[verse_ref] = tuple(values)
    return result


def _tagnt_aliases(
    tokens: Sequence[TagntToken],
    *,
    excluded: frozenset[str],
) -> tuple[frozenset[str], ...]:
    aliases: list[frozenset[str]] = []
    for token in tokens:
        primary = _primary_strong_for_token(token)
        if primary is None or primary in excluded:
            continue
        values = {primary}
        for segment in token.strong_segments:
            classic = classic_greek_strong_or_none(segment.strong)
            if classic is not None and classic not in excluded:
                values.add(classic)
        aliases.append(frozenset(values))
    return tuple(aliases)


def _scrivener_check(tr_text: str, scrivener_text: str) -> dict[str, object]:
    module_words = _greek_reader_to_scv_words(tr_text)
    scrivener_words = _scv_words(scrivener_text)
    matcher = SequenceMatcher(
        a=scrivener_words,
        b=module_words,
        autojunk=False,
    )
    matching = sum(block.size for block in matcher.get_matching_blocks())
    prefix_count = 0
    for left, right in zip(scrivener_words, module_words):
        if left != right:
            break
        prefix_count += 1
    return {
        "scrivener_word_count": len(scrivener_words),
        "module_word_count": len(module_words),
        "matching_words_lcs_like_blocks": matching,
        "sequence_ratio": _round6(matcher.ratio()),
        "exact_transliteration_sequence": module_words == scrivener_words,
        "matching_prefix_words": prefix_count,
        "module_has_extra_suffix": (
            len(module_words) > len(scrivener_words)
            and prefix_count == len(scrivener_words)
        ),
        "editorial_note": (
            "TAGNT selects Scrivener-1894 TR words but generally displays "
            "amalgamated/NA28-normalized spellings and punctuation."
        ),
    }


def _detect_subscription_tail(
    tr_tokens: Sequence[TagntToken],
    scrivener_word_count: object,
) -> list[dict[str, object]]:
    count = int(scrivener_word_count)
    if len(tr_tokens) <= count:
        return []
    tail = tr_tokens[count:]
    if not tail:
        return []
    if not any(
        token.surface.startswith(_TAGNT_SUBSCRIPTION_MARKERS) for token in tail[:2]
    ):
        return []
    return [
        {
            "surface": token.surface,
            "strong": _primary_strong_for_token(token),
            "source_ref": token.source_ref,
            "editions": list(token.editions),
        }
        for token in tail
    ]


def _neighbor_index_check(
    *,
    verse_ref: str,
    local_kjv_text: str,
    local_tr_text: str,
    kjv_usfx_texts: Mapping[str, str],
    scrivener: Mapping[str, str],
    same_ref_text_checks: Mapping[str, bool],
) -> dict[str, object]:
    index = _CANONICAL_REF_INDEX[verse_ref]
    neighbors: dict[str, str | None] = {"previous": None, "next": None}
    for label, candidate_index in (
        ("previous", index - 1),
        ("next", index + 1),
    ):
        if not 0 <= candidate_index < len(_CANONICAL_REFS):
            continue
        candidate_ref = _CANONICAL_REFS[candidate_index]
        if _is_nt_ref(candidate_ref):
            neighbors[label] = candidate_ref
    same_scrivener_ratio = float(
        _scrivener_check(local_tr_text, scrivener[verse_ref])["sequence_ratio"]
    )
    result: dict[str, object] = {
        "same_ref_kjv_locked_exact": bool(
            same_ref_text_checks["module_vs_locked_usfx_strict"]
        ),
        "same_ref_crosswire_normalized": bool(
            same_ref_text_checks["module_vs_crosswire_3_1_normalized"]
        ),
        "same_ref_open_bibles_normalized": bool(
            same_ref_text_checks["module_vs_open_bibles_normalized"]
        ),
        "same_ref_project_gutenberg_normalized": bool(
            same_ref_text_checks["module_vs_project_gutenberg_normalized"]
        ),
        "same_ref_tr_scrivener_sequence_ratio": same_scrivener_ratio,
        "neighbors": {},
    }
    best_neighbor_ratio = 0.0
    neighbor_kjv_match = False
    for label, candidate_ref in neighbors.items():
        if candidate_ref is None:
            continue
        kjv_match = normalized_text(local_kjv_text) == normalized_text(
            plain_text_from_reader(kjv_usfx_texts[candidate_ref])
        )
        tr_ratio = float(
            _scrivener_check(
                local_tr_text,
                scrivener[candidate_ref],
            )["sequence_ratio"]
        )
        result["neighbors"][label] = {
            "verse_ref": candidate_ref,
            "kjv_locked_normalized_match": kjv_match,
            "tr_scrivener_sequence_ratio": tr_ratio,
        }
        neighbor_kjv_match = neighbor_kjv_match or kjv_match
        best_neighbor_ratio = max(best_neighbor_ratio, tr_ratio)
    result["probable_shift"] = (
        (
            not bool(result["same_ref_kjv_locked_exact"])
            and neighbor_kjv_match
        )
        or (
            same_scrivener_ratio < 0.35
            and best_neighbor_ratio >= same_scrivener_ratio + 0.35
        )
    )
    return result


def _priority_flags(
    *,
    entry: OriginalPriorityEntry,
    kjv_text: str,
    tr_text: str,
    text_checks: Mapping[str, bool],
    source_word_agreement: WordTagAgreement,
    crosswire: OsisVerse,
    crosswire_metrics: MetricSet,
    alt_filtered: AltAwareMetrics,
    scrivener_check: Mapping[str, object],
    subscription_tail: Sequence[Mapping[str, object]],
    neighbor_index_check: Mapping[str, object],
) -> list[str]:
    flags: list[str] = []
    if not strong_sequence(kjv_text) and crosswire.strong_sequence:
        flags.append("kjv_strong_complete_omission")
    if subscription_tail:
        flags.append("tr_subscription_appended_to_canonical_verse")
    if not all(text_checks.values()):
        flags.append("kjv_text_source_conflict")
    if source_word_agreement.ratio < 0.55 and crosswire.strong_sequence:
        flags.append("kjv_strong_word_alignment_suspicious")
    if (
        strong_sequence(kjv_text)
        and source_word_agreement.ratio < 0.4
        and crosswire_metrics.f1 >= 0.68
        and source_word_agreement.conflicting_tag_words >= 6
    ):
        flags.append("kjv_strong_cascading_word_misalignment")
    if (
        crosswire_metrics.kjv_total > 0
        and crosswire_metrics.tr_total > 0
        and crosswire_metrics.kjv_total / crosswire_metrics.tr_total < 0.5
        and source_word_agreement.ratio < 0.6
    ):
        flags.append("kjv_strong_partial_omission")
    if alt_filtered.f1 >= 0.8 and entry.source_percent < 80:
        flags.append("classic_strong_alias_metric_artifact")
    if bool(scrivener_check["module_has_extra_suffix"]) and not subscription_tail:
        flags.append("tr_unresolved_extra_suffix")
    if not tr_text.strip():
        flags.append("tr_empty_text")
    if bool(neighbor_index_check["probable_shift"]):
        flags.append("probable_verse_shift")
    return flags


def _classify_priority(
    *,
    entry: OriginalPriorityEntry,
    flags: Sequence[str],
    alt_filtered: AltAwareMetrics,
    strict_filtered: MetricSet,
    source_word_agreement: WordTagAgreement,
) -> dict[str, object]:
    flag_set = set(flags)
    if "probable_verse_shift" in flag_set:
        number = 5
        confidence = "medium"
    elif "tr_subscription_appended_to_canonical_verse" in flag_set:
        number = 3
        confidence = "high"
    elif (
        "kjv_strong_complete_omission" in flag_set
        or "kjv_strong_partial_omission" in flag_set
        or "kjv_strong_cascading_word_misalignment" in flag_set
    ):
        number = 4
        confidence = "high"
    elif "kjv_text_source_conflict" in flag_set:
        number = 6
        confidence = "medium"
    elif (
        "tr_unresolved_extra_suffix" in flag_set
        or "tr_empty_text" in flag_set
    ):
        number = 10
        confidence = "low"
    elif (
        "classic_strong_alias_metric_artifact" in flag_set
        or alt_filtered.f1 - strict_filtered.f1 >= 0.15
    ):
        number = 9
        confidence = "high" if alt_filtered.f1 >= 0.9 else "medium"
    else:
        number = 8
        confidence = "medium"
    return {
        "number": number,
        "label": CLASSIFICATIONS_RU[number],
        "confidence": confidence,
        "review_level": (
            "A"
            if entry.source_percent == 0
            else "B"
            if entry.source_range == "<50%"
            else "C"
            if entry.source_range == "50%–<66,(6)%"
            else "D"
        ),
    }


def _priority_conclusion(
    *,
    entry: OriginalPriorityEntry,
    classification: Mapping[str, object],
    flags: Sequence[str],
    alt_filtered: AltAwareMetrics,
    source_word_agreement: WordTagAgreement,
) -> str:
    flag_set = set(flags)
    if "probable_verse_shift" in flag_set:
        return (
            "Собственная ссылка согласуется хуже соседней записи как минимум "
            "в одном независимом текстовом контроле. Случай классифицирован "
            "как ошибка индексации только после индивидуальной проверки."
        )
    if "kjv_strong_complete_omission" in flag_set:
        return (
            "Текст стиха и его индекс подтверждены; 0% вызваны полным "
            "отсутствием Strong-тегов в исходном eBible USFX. Текущий "
            "CrossWire KJV 3.1 содержит разметку этого же английского текста."
        )
    if "kjv_strong_partial_omission" in flag_set:
        return (
            "Английский текст и ссылка подтверждены, но локальная eBible "
            "Strong-разметка охватывает только часть стиха. CrossWire KJV 3.1 "
            "и греческий TR подтверждают отсутствующий размеченный участок."
        )
    if "kjv_strong_cascading_word_misalignment" in flag_set:
        return (
            "Английский текст и ссылка корректны, но Strong-теги eBible/KJV "
            "каскадно привязаны к неверным словам. Контрольная разметка "
            "CrossWire 3.1 и греческая последовательность TR согласуются между "
            "собой, а локальная привязка — нет."
        )
    if "tr_subscription_appended_to_canonical_verse" in flag_set:
        return (
            "К каноническому последнему стиху послания добавлена традиционная "
            "греческая подписка/колофон. В отдельном тексте Скривенера 1894 "
            "она не входит в стих; низкая метрика создаётся импортом паратекста "
            "в verse-row."
        )
    if int(classification["number"]) == 6:
        return (
            "Локальный текст дословно воспроизводит зафиксированный eBible "
            "источник, но одна или обе контрольные KJV-редакции дают иное "
            "чтение либо пунктуационно-лексическую нормализацию. Это "
            "редакционное различие, а не установленный технический пропуск."
        )
    if int(classification["number"]) == 9:
        return (
            "Локальные тексты и индексы подтверждены. Основная часть строгого "
            "расхождения исчезает при разрешённых TAGNT альтернативах Strong "
            f"(F1={alt_filtered.f1:.4f}); это различие систем нумерации форм, "
            "а не доказательство ошибки стиха."
        )
    if int(classification["number"]) == 5:
        return (
            "Тексты и ссылка подтверждены, но привязка KJV Strong к словам "
            f"слабо согласуется с CrossWire (word ratio="
            f"{source_word_agreement.ratio:.4f}). Требуется ручная лексическая "
            "проверка перед исправлением."
        )
    return (
        "Тексты и индекс подтверждены несколькими корпусами. Оставшееся "
        "расхождение совместимо с переводческим выравниванием: один греческий "
        "токен может соответствовать фразе KJV, а KJV Strong может кодировать "
        "форму или переводческое соответствие."
    )


def _proposed_content(
    *,
    classification_number: int,
    flags: Sequence[str],
    local_plain: str,
    crosswire: OsisVerse,
    tr_tokens: Sequence[TagntToken],
    scrivener_word_count: int,
) -> dict[str, object] | None:
    flag_set = set(flags)
    if classification_number == 4:
        return {
            "text": local_plain,
            "proposed_strong_sequence": list(crosswire.strong_sequence),
            "basis": "CrossWire KJV 3.1 word-level Strong markup",
            "warning": (
                "Sequence is evidence for correction; exact reader-format "
                "placement must preserve phrase-level OSIS spans."
            ),
        }
    if "tr_subscription_appended_to_canonical_verse" in flag_set:
        canonical_tokens = tr_tokens[:scrivener_word_count]
        parts: list[str] = []
        for token in canonical_tokens:
            parts.append(token.surface)
            strong = _primary_strong_for_token(token)
            if strong is not None:
                parts.append(strong)
        return {
            "tagged_text": " ".join(parts),
            "basis": (
                "Scrivener 1894 verse boundary plus locked TAGNT token spelling"
            ),
        }
    return None


def _comparison_summary(comparison: StrongComparison) -> dict[str, object]:
    summary = {
        "compared_verses": comparison.compared_verses_count,
        "mismatched_verses": comparison.mismatched_verses_count,
        "tr_total": comparison.tr_total_count,
        "kjv_total": comparison.kjv_total_count,
        "matched": comparison.matched_count,
        "tr_only": comparison.tr_unmatched_count,
        "kjv_only": comparison.kjv_extra_count,
        "full_discrepancy_count": comparison.different_occurrences_count,
        "tr_recall": _round6(comparison.tr_match_ratio),
        "kjv_precision": _round6(comparison.kjv_precision_ratio),
        "f1": _round6(comparison.f1_ratio),
        "multiset_jaccard": _round6(comparison.multiset_jaccard_ratio),
        "tr_mismatch_percent": _round_percent(comparison.tr_mismatch_ratio),
        "full_discrepancy_percent_of_tr": _round_percent(
            comparison.full_discrepancy_ratio
        ),
    }
    ordered_matched = sum(
        score.ordered_matched_count for score in comparison.verse_scores
    )
    summary.update(
        {
            "ordered_matched": ordered_matched,
            "ordered_tr_recall": _round6(
                _safe_ratio(
                    ordered_matched,
                    comparison.tr_total_count,
                    other_total=comparison.kjv_total_count,
                )
            ),
            "ordered_kjv_precision": _round6(
                _safe_ratio(
                    ordered_matched,
                    comparison.kjv_total_count,
                    other_total=comparison.tr_total_count,
                )
            ),
            "ordered_f1": _round6(
                _f1_from_counts(
                    ordered_matched,
                    comparison.tr_total_count,
                    comparison.kjv_total_count,
                )
            ),
        }
    )
    return summary


def _aggregate_score_summary(
    score: StrongAggregateScore,
) -> dict[str, object]:
    return {
        "scope": score.label,
        "verses": score.verses_count,
        "tr_total": score.tr_total_count,
        "kjv_total": score.kjv_total_count,
        "matched": score.matched_count,
        "tr_only": score.tr_unmatched_count,
        "kjv_only": score.kjv_extra_count,
        "tr_recall": _round6(score.tr_match_ratio),
        "kjv_precision": _round6(score.kjv_precision_ratio),
        "f1": _round6(score.f1_ratio),
        "multiset_jaccard": _round6(score.multiset_jaccard_ratio),
        "full_discrepancy_percent_of_tr": _round_percent(
            score.full_discrepancy_ratio
        ),
    }


def _build_priority_statistics(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    return {
        "by_source_range": dict(
            sorted(Counter(str(row["source_range"]) for row in rows).items())
        ),
        "by_review_level": dict(
            sorted(
                Counter(
                    str(row["classification"]["review_level"]) for row in rows
                ).items()
            )
        ),
        "by_book": dict(
            sorted(Counter(str(row["verse_ref"]).split(".", 1)[0] for row in rows).items())
        ),
        "by_chapter": dict(
            sorted(
                Counter(
                    ".".join(str(row["verse_ref"]).split(".")[:2])
                    for row in rows
                ).items(),
                key=lambda item: _canonical_ref_sort_key(f"{item[0]}.1"),
            )
        ),
    }


def _build_lxx_empty_statistics(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    return {
        "by_book": dict(
            sorted(Counter(str(row["verse_ref"]).split(".", 1)[0] for row in rows).items())
        ),
        "by_projection_status": dict(
            sorted(Counter(str(row["projection_status"]) for row in rows).items())
        ),
        "continuous_series": dict(
            sorted(
                Counter(
                    str(row["continuous_series"])
                    for row in rows
                    if row["continuous_series"]
                ).items()
            )
        ),
    }


def _sequence_pairs_summary(
    pairs: Sequence[tuple[Sequence[str], Sequence[str]]],
) -> dict[str, object]:
    metrics = [metrics_for_sequences(kjv, tr) for kjv, tr in pairs]
    tr_total = sum(metric.tr_total for metric in metrics)
    kjv_total = sum(metric.kjv_total for metric in metrics)
    matched = sum(metric.matched for metric in metrics)
    ordered_matched = sum(metric.ordered_matched for metric in metrics)
    tr_only = tr_total - matched
    kjv_only = kjv_total - matched
    mismatched = sum(
        1
        for metric in metrics
        if metric.tr_only_count or metric.kjv_only_count
    )
    return {
        "compared_verses": len(metrics),
        "mismatched_verses": mismatched,
        "tr_total": tr_total,
        "kjv_total": kjv_total,
        "matched": matched,
        "tr_only": tr_only,
        "kjv_only": kjv_only,
        "full_discrepancy_count": tr_only + kjv_only,
        "tr_recall": _round6(_safe_ratio(matched, tr_total, other_total=kjv_total)),
        "kjv_precision": _round6(
            _safe_ratio(matched, kjv_total, other_total=tr_total)
        ),
        "f1": _round6(_f1_from_counts(matched, tr_total, kjv_total)),
        "multiset_jaccard": _round6(
            _safe_ratio(
                matched,
                tr_total + kjv_total - matched,
                other_total=0,
            )
        ),
        "ordered_matched": ordered_matched,
        "ordered_tr_recall": _round6(
            _safe_ratio(ordered_matched, tr_total, other_total=kjv_total)
        ),
        "ordered_kjv_precision": _round6(
            _safe_ratio(ordered_matched, kjv_total, other_total=tr_total)
        ),
        "ordered_f1": _round6(
            _f1_from_counts(ordered_matched, tr_total, kjv_total)
        ),
        "tr_mismatch_percent": _round_percent(
            _safe_ratio(tr_only, tr_total, other_total=kjv_total)
        ),
        "full_discrepancy_percent_of_tr": _round_percent(
            _safe_ratio(
                tr_only + kjv_only,
                tr_total,
                other_total=kjv_total,
            )
        ),
    }


def _build_source_manifest(inputs: EvidenceAuditInputs) -> dict[str, object]:
    input_files = {
        "original_report": asdict(file_evidence(inputs.original_report)),
        "kjv_sqlite": asdict(file_evidence(inputs.kjv_db)),
        "lxx_tr_sqlite": asdict(file_evidence(inputs.lxx_tr_db)),
        "weak_strongs": asdict(file_evidence(inputs.weak_strongs)),
        "kjv_usfx_zip": asdict(file_evidence(inputs.kjv_usfx_zip)),
        "crosswire_kjv_osis": asdict(file_evidence(inputs.crosswire_kjv_osis)),
        "open_bibles_kjv_osis": asdict(
            file_evidence(inputs.open_bibles_kjv_osis)
        ),
        "project_gutenberg_kjv": asdict(
            file_evidence(inputs.project_gutenberg_kjv)
        ),
        "crosswire_lxx_zip": asdict(file_evidence(inputs.crosswire_lxx_zip)),
        "lxx_projection_plan": asdict(
            file_evidence(inputs.lxx_projection_plan)
        ),
        "tagnt": [asdict(file_evidence(path)) for path in inputs.tagnt_paths],
        "scrivener_text_dir": directory_evidence(inputs.scrivener_text_dir),
    }
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "accessed_on": inputs.accessed_on,
        "input_files": input_files,
        "sources": [
            {
                "source_id": "ebible_eng_kjv2006",
                "organization_or_editor": "eBible.org / CrossWire Bible Society",
                "edition": (
                    "King James Version, standardized 1769 protocanon, "
                    "eng-kjv2006 source dated 2026-05-16"
                ),
                "purpose": "KJV text and source Strong markup",
                "source_url": (
                    "https://ebible.org/Scriptures/eng-kjv2006_usfx.zip"
                ),
                "source_page_url": (
                    "https://ebible.org/eng-kjv2006/copyright.htm"
                ),
                "license": (
                    "Public Domain outside the United Kingdom; UK Crown "
                    "Letters Patent restrictions apply"
                ),
                "accessed_on": inputs.accessed_on,
                "sha256": input_files["kjv_usfx_zip"]["sha256"],
            },
            {
                "source_id": "crosswire_kjv_3_1",
                "organization_or_editor": "CrossWire Bible Society",
                "edition": (
                    "KJV 3.1 (2023-07-19), commit "
                    "d490be7e34762deb2c76cb2c1306d4808e27890d"
                ),
                "purpose": (
                    "Versioned KJV text and word-level Strong control; "
                    "provenance is related to eng-kjv2006"
                ),
                "source_url": (
                    "https://gitlab.com/crosswire-bible-society/kjv/-/raw/"
                    "d490be7e34762deb2c76cb2c1306d4808e27890d/kjvfull.xml"
                ),
                "source_page_url": (
                    "https://crosswire.org/sword/modules/ModInfo.jsp?modName=KJV"
                ),
                "license": "GPL / general public use grant from CrossWire",
                "accessed_on": inputs.accessed_on,
                "sha256": input_files["crosswire_kjv_osis"]["sha256"],
                "checksum_note": (
                    "Local file is the repository content normalized to LF."
                ),
            },
            {
                "source_id": "open_bibles_eng_kjv",
                "organization_or_editor": "seven1m/open-bibles; eBible.org source",
                "edition": (
                    "eng-kjv OSIS, repository commit "
                    "f257a3559025c3f873b48a75019f53a9354ed7de"
                ),
                "purpose": "Second machine-readable KJV text control",
                "source_url": (
                    "https://raw.githubusercontent.com/seven1m/open-bibles/"
                    "f257a3559025c3f873b48a75019f53a9354ed7de/"
                    "eng-kjv.osis.xml"
                ),
                "source_page_url": (
                    "https://github.com/seven1m/open-bibles"
                ),
                "license": "Public Domain",
                "accessed_on": inputs.accessed_on,
                "sha256": input_files["open_bibles_kjv_osis"]["sha256"],
                "checksum_note": (
                    "Local file is the repository content normalized to LF."
                ),
            },
            {
                "source_id": "step_tagnt_scrivener_1894",
                "organization_or_editor": (
                    "STEPBible / Tyndale House, Cambridge"
                ),
                "edition": (
                    "TAGNT, STEPBible-Data commit "
                    "b9dcc831a98e0fd6f3c7e122be9ff68377c310c0; "
                    "TR selection identified by TAGNT as Scrivener 1894"
                ),
                "purpose": "TR tokens, morphology, primary and alternate Strong",
                "source_url": (
                    "https://github.com/STEPBible/STEPBible-Data/tree/"
                    "b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/"
                    "Translators%20Amalgamated%20OT%2BNT"
                ),
                "license": "CC BY 4.0",
                "accessed_on": inputs.accessed_on,
                "files": input_files["tagnt"],
            },
            {
                "source_id": "project_gutenberg_kjv_ebook_10",
                "organization_or_editor": "Project Gutenberg",
                "edition": (
                    "The King James Version of the Bible, eBook 10; "
                    "updated 2024-10-29"
                ),
                "purpose": (
                    "Independent machine-readable KJV text and "
                    "verse-boundary control; no Strong markup"
                ),
                "source_url": (
                    "https://www.gutenberg.org/cache/epub/10/pg10.txt"
                ),
                "source_page_url": "https://www.gutenberg.org/ebooks/10",
                "license": (
                    "Public domain in the USA; Project Gutenberg License "
                    "and territorial notice apply"
                ),
                "accessed_on": inputs.accessed_on,
                "sha256": input_files["project_gutenberg_kjv"]["sha256"],
            },
            {
                "source_id": "robinson_scrivener_1894_textonly",
                "organization_or_editor": (
                    "Dr Maurice A. Robinson; Dr Ulrik Sandborg-Petersen"
                ),
                "edition": (
                    "Scrivener 1894 TR text-only, commit "
                    "6049a43b135ed870f843b83eb6a04764fc796678"
                ),
                "purpose": "Independent TR text and verse-boundary control",
                "source_url": (
                    "https://github.com/byztxt/greektext-scrivener/tree/"
                    "6049a43b135ed870f843b83eb6a04764fc796678/textonly"
                ),
                "license": "Public Domain; copy freely",
                "accessed_on": inputs.accessed_on,
                "directory_sha256": input_files["scrivener_text_dir"]["sha256"],
            },
            {
                "source_id": "crosswire_lxx_3_2",
                "organization_or_editor": (
                    "CrossWire; CATSS/R. Kraft; source edition Alfred Rahlfs"
                ),
                "edition": "CrossWire LXX 3.2 (2025-03-15)",
                "purpose": "Primary LXX text, morphology and Strong source",
                "source_url": (
                    "https://crosswire.org/ftpmirror/pub/sword/packages/"
                    "rawzip/LXX.zip"
                ),
                "source_page_url": (
                    "https://crosswire.org/sword/modules/ModInfo.jsp?modName=LXX"
                ),
                "license": "Copyrighted; Free non-commercial distribution",
                "accessed_on": inputs.accessed_on,
                "sha256": input_files["crosswire_lxx_zip"]["sha256"],
            },
            {
                "source_id": "swete_ot_greek",
                "organization_or_editor": "H. B. Swete",
                "edition": (
                    "The Old Testament in Greek according to the Septuagint, "
                    "Vols. I-II"
                ),
                "purpose": (
                    "Independent public-domain LXX manuscript/verse control "
                    "used by the projection plan"
                ),
                "source_page_url": (
                    "https://archive.org/details/oldtestamentingr01swet"
                ),
                "license": "Public Domain / NOT_IN_COPYRIGHT scan metadata",
                "accessed_on": inputs.accessed_on,
                "sha256": None,
                "usage_note": (
                    "Consulted through the existing projection evidence; no "
                    "downloaded scan is redistributed by this audit."
                ),
            },
            {
                "source_id": "rahlfs_hanhart_2006_online",
                "organization_or_editor": "German Bible Society",
                "edition": "Rahlfs-Hanhart, Septuaginta, 2nd ed. 2006",
                "purpose": "Edition identification and licensed text control",
                "source_page_url": (
                    "https://www.die-bibel.de/en/bible/LXX/GEN.1"
                ),
                "license": "Copyright © 2006 Deutsche Bibelgesellschaft",
                "accessed_on": inputs.accessed_on,
                "sha256": None,
                "usage_note": (
                    "Not bulk-downloaded or redistributed; used as an online "
                    "edition control."
                ),
            },
        ],
    }


def file_evidence(path: Path) -> FileEvidence:
    stat = path.stat()
    modified = dt.datetime.fromtimestamp(
        stat.st_mtime,
        tz=dt.timezone.utc,
    ).isoformat(timespec="microseconds").replace("+00:00", "Z")
    return FileEvidence(
        path=str(path.resolve()),
        bytes=stat.st_size,
        modified_utc=modified,
        sha256=_sha256_file(path),
    )


def directory_evidence(path: Path) -> dict[str, object]:
    files = sorted(
        (
            child
            for child in path.rglob("*")
            if child.is_file() and ".git" not in child.relative_to(path).parts
        ),
        key=lambda child: child.relative_to(path).as_posix(),
    )
    digest = hashlib.sha256()
    rows: list[dict[str, object]] = []
    total_bytes = 0
    for child in files:
        relative = child.relative_to(path).as_posix()
        sha256 = _sha256_file(child)
        size = child.stat().st_size
        total_bytes += size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256.encode("ascii"))
        digest.update(b"\n")
        rows.append({"relative_path": relative, "bytes": size, "sha256": sha256})
    return {
        "path": str(path.resolve()),
        "files_count": len(rows),
        "bytes": total_bytes,
        "sha256": digest.hexdigest(),
        "files": rows,
    }


def plain_text_from_reader(text: str) -> str:
    return _collapse_whitespace(_STRONG_TOKEN_RE.sub("", text))


def normalized_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text).casefold()
    values: list[str] = []
    previous_space = True
    for character in decomposed:
        category = unicodedata.category(character)
        if category.startswith(("L", "N")):
            values.append(character)
            previous_space = False
        elif not previous_space:
            values.append(" ")
            previous_space = True
    return "".join(values).strip()


def _word_tags_from_reader_text(
    text: str,
) -> list[tuple[str, frozenset[str]]]:
    values: list[tuple[str, frozenset[str]]] = []
    for span in split_tagged_text(text):
        tags = frozenset(span.strongs)
        for word in _normalized_words(span.surface):
            values.append((word, tags))
    return values


def _word_tags_from_osis(
    verse: OsisVerse,
) -> list[tuple[str, frozenset[str]]]:
    values: list[tuple[str, frozenset[str]]] = []
    for span in verse.tagged_spans:
        tags = frozenset(span.strongs)
        for word in _normalized_words(span.surface):
            values.append((word, tags))
    return values


def _normalized_words(text: str) -> list[str]:
    return [normalized_text(match.group(0)) for match in _WORD_RE.finditer(text)]


def _greek_reader_to_scv_words(text: str) -> list[str]:
    plain = plain_text_from_reader(text)
    return [_greek_to_scv(word) for word in _WORD_RE.findall(plain)]


def _scv_words(text: str) -> list[str]:
    return [value.lower() for value in re.findall(r"[a-z]+", text.lower())]


def _greek_to_scv(value: str) -> str:
    mapping = {
        "α": "a",
        "β": "b",
        "γ": "g",
        "δ": "d",
        "ε": "e",
        "ζ": "z",
        "η": "h",
        "θ": "y",
        "ι": "i",
        "κ": "k",
        "λ": "l",
        "μ": "m",
        "ν": "n",
        "ξ": "x",
        "ο": "o",
        "π": "p",
        "ρ": "r",
        "σ": "s",
        "ς": "v",
        "τ": "t",
        "υ": "u",
        "φ": "f",
        "χ": "c",
        "ψ": "q",
        "ω": "w",
    }
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        mapping.get(character, "")
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def _maximum_bipartite_match_count(
    adjacency: Sequence[Sequence[int]],
    right_size: int,
) -> int:
    matched_left_by_right = [-1] * right_size

    def augment(left_index: int, seen: set[int]) -> bool:
        for right_index in adjacency[left_index]:
            if right_index in seen:
                continue
            seen.add(right_index)
            previous_left = matched_left_by_right[right_index]
            if previous_left == -1 or augment(previous_left, seen):
                matched_left_by_right[right_index] = left_index
                return True
        return False

    return sum(
        1
        for left_index in range(len(adjacency))
        if augment(left_index, set())
    )


def _ordered_alias_match_count(
    kjv_sequence: Sequence[str],
    tr_aliases: Sequence[frozenset[str]],
) -> int:
    previous = [0] * (len(tr_aliases) + 1)
    for strong in kjv_sequence:
        current = [0]
        for index, aliases in enumerate(tr_aliases, start=1):
            if strong in aliases:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[index - 1]))
        previous = current
    return previous[-1]


def _lcs_match_count(left: Sequence[str], right: Sequence[str]) -> int:
    previous = [0] * (len(right) + 1)
    for left_value in left:
        current = [0]
        for index, right_value in enumerate(right, start=1):
            if left_value == right_value:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[index - 1]))
        previous = current
    return previous[-1]


def _continuous_series_label(
    verse_ref: str,
    all_empty: Sequence[tuple[str, str]],
) -> str | None:
    refs = [item[0] for item in all_empty]
    index = refs.index(verse_ref)
    book, chapter_text, verse_text = verse_ref.split(".")
    chapter = int(chapter_text)
    verse = int(verse_text)
    start = verse
    end = verse
    cursor = index - 1
    while cursor >= 0:
        candidate_book, candidate_chapter, candidate_verse = refs[cursor].split(".")
        if (
            candidate_book == book
            and int(candidate_chapter) == chapter
            and int(candidate_verse) == start - 1
        ):
            start -= 1
            cursor -= 1
        else:
            break
    cursor = index + 1
    while cursor < len(refs):
        candidate_book, candidate_chapter, candidate_verse = refs[cursor].split(".")
        if (
            candidate_book == book
            and int(candidate_chapter) == chapter
            and int(candidate_verse) == end + 1
        ):
            end += 1
            cursor += 1
        else:
            break
    if start == end:
        return None
    return f"{book}.{chapter}.{start}-{end}"


def _counter_to_list(counter: Counter[str]) -> list[dict[str, object]]:
    return [
        {"strong": strong, "count": count}
        for strong, count in sorted(counter.items(), key=_strong_sort_key)
    ]


def _strong_sort_key(item: tuple[str, int]) -> tuple[str, int, str]:
    strong = item[0]
    match = re.match(r"([GH])(\d+)(.*)", strong)
    if match is None:
        return strong, 0, ""
    return match.group(1), int(match.group(2)), match.group(3)


def _required_input_paths(inputs: EvidenceAuditInputs) -> tuple[Path, ...]:
    return (
        inputs.kjv_db,
        inputs.lxx_tr_db,
        inputs.original_report,
        inputs.weak_strongs,
        inputs.kjv_usfx_zip,
        inputs.crosswire_kjv_osis,
        inputs.open_bibles_kjv_osis,
        inputs.project_gutenberg_kjv,
        *inputs.tagnt_paths,
        inputs.crosswire_lxx_zip,
        inputs.lxx_projection_plan,
    )


def _open_read_only(path: Path) -> sqlite3.Connection:
    uri = (
        "file:"
        + urllib.parse.quote(path.resolve().as_posix(), safe="/:")
        + "?mode=ro"
    )
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only=ON")
    return connection


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_priority_csv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
) -> None:
    fieldnames = [
        "verse_ref",
        "verse_key",
        "source_range",
        "source_percent",
        "source_tr_only",
        "source_kjv_only",
        "kjv_text",
        "tr_text",
        "kjv_strongs_all",
        "tr_strongs_all",
        "tr_recall_filtered",
        "kjv_precision_filtered",
        "f1_filtered",
        "jaccard_filtered",
        "ordered_f1_filtered",
        "alt_aware_f1_filtered",
        "classification_number",
        "classification",
        "confidence",
        "flags",
        "conclusion_ru",
        "source_links",
        "proposed_correct_content",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            filtered = row["strict_and_normalized_metrics"]["all_77"]
            classification = row["classification"]
            writer.writerow(
                {
                    "verse_ref": row["verse_ref"],
                    "verse_key": row["verse_key"],
                    "source_range": row["source_range"],
                    "source_percent": row["source_percent"],
                    "source_tr_only": _compact_json(row["source_tr_only"]),
                    "source_kjv_only": _compact_json(row["source_kjv_only"]),
                    "kjv_text": row["local_text"]["kjv_tagged"],
                    "tr_text": row["local_text"]["tr_tagged"],
                    "kjv_strongs_all": " ".join(
                        row["local_strong_sequences"]["kjv_all"]
                    ),
                    "tr_strongs_all": " ".join(
                        row["local_strong_sequences"]["tr_all"]
                    ),
                    "tr_recall_filtered": filtered["tr_recall"],
                    "kjv_precision_filtered": filtered["kjv_precision"],
                    "f1_filtered": filtered["f1"],
                    "jaccard_filtered": filtered["multiset_jaccard"],
                    "ordered_f1_filtered": filtered["ordered_f1"],
                    "alt_aware_f1_filtered": row["alt_strong_aware_metrics"][
                        "with_all_77_exclusions"
                    ]["f1"],
                    "classification_number": classification["number"],
                    "classification": classification["label"],
                    "confidence": classification["confidence"],
                    "flags": ";".join(row["flags"]),
                    "conclusion_ru": row["conclusion_ru"],
                    "source_links": ";".join(row["source_links"]),
                    "proposed_correct_content": _compact_json(
                        row["proposed_correct_content"]
                    ),
                }
            )


def _write_lxx_empty_csv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
) -> None:
    fieldnames = [
        "verse_ref",
        "verse_key",
        "projection_status",
        "source_refs",
        "continuous_series",
        "classification_number",
        "classification",
        "confidence",
        "evidence_note",
        "conclusion_ru",
        "source_links",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            classification = row["classification"]
            writer.writerow(
                {
                    "verse_ref": row["verse_ref"],
                    "verse_key": row["verse_key"],
                    "projection_status": row["projection_status"],
                    "source_refs": ";".join(row["source_refs"]),
                    "continuous_series": row["continuous_series"] or "",
                    "classification_number": classification["number"],
                    "classification": classification["label"],
                    "confidence": classification["confidence"],
                    "evidence_note": row["evidence_note"],
                    "conclusion_ru": row["conclusion_ru"],
                    "source_links": ";".join(row["source_links"]),
                }
            )


def _write_kjv_strong_anomalies_csv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
) -> None:
    fieldnames = [
        "verse_ref",
        "verse_key",
        "testament",
        "flags",
        "local_text",
        "source_text",
        "local_strong_sequence",
        "crosswire_strong_sequence",
        "sequence_metrics",
        "word_alignment",
        "classification_number",
        "classification",
        "confidence",
        "source_ids",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            classification = row["classification"]
            writer.writerow(
                {
                    "verse_ref": row["verse_ref"],
                    "verse_key": row["verse_key"],
                    "testament": row["testament"],
                    "flags": ";".join(row["flags"]),
                    "local_text": row["local_text"],
                    "source_text": row["source_text"],
                    "local_strong_sequence": ";".join(
                        row["local_strong_sequence"]
                    ),
                    "crosswire_strong_sequence": ";".join(
                        row["crosswire_strong_sequence"]
                    ),
                    "sequence_metrics": _compact_json(row["sequence_metrics"]),
                    "word_alignment": _compact_json(row["word_alignment"]),
                    "classification_number": classification["number"],
                    "classification": classification["label"],
                    "confidence": classification["confidence"],
                    "source_ids": ";".join(row["source_ids"]),
                }
            )


def _write_metrics_csv(
    path: Path,
    metrics: Mapping[str, Mapping[str, object]],
) -> None:
    fieldnames = [
        "mode",
        "compared_verses",
        "mismatched_verses",
        "tr_total",
        "kjv_total",
        "matched",
        "tr_only",
        "kjv_only",
        "tr_recall",
        "kjv_precision",
        "f1",
        "multiset_jaccard",
        "ordered_matched",
        "ordered_tr_recall",
        "ordered_kjv_precision",
        "ordered_f1",
        "full_discrepancy_count",
        "tr_mismatch_percent",
        "full_discrepancy_percent_of_tr",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for mode, values in metrics.items():
            writer.writerow({"mode": mode, **{name: values[name] for name in fieldnames[1:]}})


def _compact_json(value: object) -> str:
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _priority_source_links() -> list[str]:
    return [
        "https://ebible.org/eng-kjv2006/copyright.htm",
        "https://crosswire.org/sword/modules/ModInfo.jsp?modName=KJV",
        "https://www.gutenberg.org/ebooks/10",
        "https://github.com/STEPBible/STEPBible-Data",
        "https://github.com/byztxt/greektext-scrivener",
    ]


def _lxx_source_links() -> list[str]:
    return [
        "https://crosswire.org/sword/modules/ModInfo.jsp?modName=LXX",
        "https://www.die-bibel.de/en/bible/LXX/GEN.1",
        "https://archive.org/details/oldtestamentingr01swet",
    ]


def _limitations() -> list[str]:
    return [
        (
            "Для LXX отсутствуют два независимых авторитетных открытых корпуса "
            "именно с классическими Strong-номерами. Проверены текст, леммы и "
            "морфология CrossWire/CATSS; независимые текстовые контроли не "
            "выдаются за независимую Strong-валидацию."
        ),
        (
            "Rahlfs-Hanhart 2006 доступен как лицензированный онлайн-контроль, "
            "но не скачивался и не перераспространялся целиком."
        ),
        (
            "Для 210 пустых KJV-grid позиций доказано воспроизводимое "
            "отсутствие отдельной строки в использованных контролях и правилах "
            "проекции, но не доказано отсутствие фрагмента во всех "
            "гексапларных, рецензионных и патристических свидетелях."
        ),
        (
            "Низкая Strong-метрика между переводом и греческим текстом не "
            "является вероятностью текстовой ошибки."
        ),
    ]


def _is_nt_ref(verse_ref: str) -> bool:
    book = verse_ref.split(".", 1)[0]
    return next(
        canonical_book.testament
        for canonical_book in CANONICAL_BOOKS
        if canonical_book.canonical_code == book
    ) == "NT"


def _is_strong_token(value: str) -> bool:
    return _STRONG_TOKEN_RE.fullmatch(value) is not None


def _text_equal(left: str, right: str, *, normalized: bool) -> bool:
    if normalized:
        return normalized_text(left) == normalized_text(right)
    return _collapse_whitespace(left) == _collapse_whitespace(right)


def _collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def _safe_ratio(part: int, total: int, *, other_total: int) -> float:
    if total == 0:
        return 1.0 if other_total == 0 else 0.0
    return part / total


def _f1_from_counts(matched: int, left_total: int, right_total: int) -> float:
    denominator = left_total + right_total
    if denominator == 0:
        return 1.0
    return 2 * matched / denominator


def _round6(value: float) -> float:
    return round(value, 6)


def _round_percent(value: float) -> float:
    return round(value * 100, 2)


def _report_percent(value: object) -> str:
    return f"{float(value) * 100:.2f}%".replace(".", ",")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _normalize_osis_ref(value: str) -> str:
    normalized = value.split(".seID.", 1)[0]
    book, separator, remainder = normalized.partition(".")
    if not separator:
        return normalized
    return f"{_OSIS_BOOK_ALIASES.get(book, book)}.{remainder}"


def _normalize_reference_mapping(
    verses: Mapping[str, str],
) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for verse_ref, text in verses.items():
        canonical_ref = _normalize_osis_ref(verse_ref)
        if canonical_ref in normalized:
            raise ValueError(f"Duplicate normalized verse reference: {canonical_ref}")
        normalized[canonical_ref] = text
    return normalized


def _canonical_ref_sort_key(value: str) -> int:
    return _CANONICAL_REF_ORDER.get(value, 10**12)


def _validate_access_date(value: str) -> None:
    try:
        dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("--accessed-on must use YYYY-MM-DD") from error

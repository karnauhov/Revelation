"""Audit empty verses and compare Strong's numbers in KJV and LXX/TR modules."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from .build_kjv import verse_key_for
from .canon import CANONICAL_BOOKS, canonical_verses
from .tagnt import normalize_strong

DEFAULT_DB_DIR = Path.home() / "Documents" / "revelation" / "db"
DEFAULT_KJV_PATH = DEFAULT_DB_DIR / "bible_kjv.sqlite"
DEFAULT_LXX_TR_PATH = DEFAULT_DB_DIR / "bible_lxx_tr.sqlite"
DEFAULT_WEAK_STRONGS_PATH = (
    Path(__file__).resolve().parents[2]
    / "assets"
    / "data"
    / "greek_weak_strong_numbers.json"
)

_STRONG_TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"([GH]0*\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?)"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BibleModule:
    path: Path
    verses: Mapping[str, str]

    @property
    def empty_keys(self) -> tuple[str, ...]:
        return tuple(key for key, text in self.verses.items() if not text.strip())


@dataclass(frozen=True)
class StrongFilter:
    source_path: Path
    groups: Mapping[str, tuple[str, ...]]
    notes: tuple[str, ...] = ()

    @property
    def excluded_strongs(self) -> frozenset[str]:
        return frozenset(
            strong for group in self.groups.values() for strong in group
        )


@dataclass(frozen=True)
class StrongVerseScore:
    verse_key: str
    verse_ref: str
    kjv_counts: Counter[str]
    tr_counts: Counter[str]

    @property
    def tr_total_count(self) -> int:
        return sum(self.tr_counts.values())

    @property
    def kjv_total_count(self) -> int:
        return sum(self.kjv_counts.values())

    @property
    def matched_count(self) -> int:
        return sum((self.kjv_counts & self.tr_counts).values())

    @property
    def tr_only(self) -> Counter[str]:
        return _counter_excess(self.tr_counts, self.kjv_counts)

    @property
    def kjv_only(self) -> Counter[str]:
        return _counter_excess(self.kjv_counts, self.tr_counts)

    @property
    def tr_unmatched_count(self) -> int:
        return sum(self.tr_only.values())

    @property
    def kjv_extra_count(self) -> int:
        return sum(self.kjv_only.values())

    @property
    def different_occurrences_count(self) -> int:
        return self.tr_unmatched_count + self.kjv_extra_count

    @property
    def tr_match_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 1.0 if self.kjv_total_count == 0 else 0.0
        return self.matched_count / self.tr_total_count

    @property
    def tr_mismatch_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0
        return self.tr_unmatched_count / self.tr_total_count

    @property
    def full_discrepancy_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0 if self.kjv_total_count == 0 else 1.0
        return self.different_occurrences_count / self.tr_total_count

    @property
    def has_mismatch(self) -> bool:
        return bool(self.tr_only or self.kjv_only)


@dataclass(frozen=True)
class StrongAggregateScore:
    label: str
    verses_count: int
    tr_total_count: int
    matched_count: int
    tr_unmatched_count: int
    kjv_extra_count: int

    @property
    def different_occurrences_count(self) -> int:
        return self.tr_unmatched_count + self.kjv_extra_count

    @property
    def tr_match_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 1.0 if self.kjv_extra_count == 0 else 0.0
        return self.matched_count / self.tr_total_count

    @property
    def tr_mismatch_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0
        return self.tr_unmatched_count / self.tr_total_count

    @property
    def full_discrepancy_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0 if self.kjv_extra_count == 0 else 1.0
        return self.different_occurrences_count / self.tr_total_count


@dataclass(frozen=True)
class MatchDistributionBucket:
    label: str
    verses_count: int


@dataclass(frozen=True)
class MatchRange:
    label: str
    verse_scores: tuple[StrongVerseScore, ...]


@dataclass(frozen=True)
class StrongComparison:
    compared_verses_count: int
    verse_scores: tuple[StrongVerseScore, ...]
    chapter_scores: tuple[StrongAggregateScore, ...]
    book_scores: tuple[StrongAggregateScore, ...]

    @property
    def mismatches(self) -> tuple[StrongVerseScore, ...]:
        return tuple(score for score in self.verse_scores if score.has_mismatch)

    @property
    def mismatched_verses_count(self) -> int:
        return len(self.mismatches)

    @property
    def different_occurrences_count(self) -> int:
        return sum(item.different_occurrences_count for item in self.verse_scores)

    @property
    def tr_total_count(self) -> int:
        return sum(item.tr_total_count for item in self.verse_scores)

    @property
    def matched_count(self) -> int:
        return sum(item.matched_count for item in self.verse_scores)

    @property
    def tr_unmatched_count(self) -> int:
        return sum(item.tr_unmatched_count for item in self.verse_scores)

    @property
    def kjv_extra_count(self) -> int:
        return sum(item.kjv_extra_count for item in self.verse_scores)

    @property
    def tr_match_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 1.0 if self.kjv_extra_count == 0 else 0.0
        return self.matched_count / self.tr_total_count

    @property
    def tr_mismatch_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0
        return self.tr_unmatched_count / self.tr_total_count

    @property
    def full_discrepancy_ratio(self) -> float:
        if self.tr_total_count == 0:
            return 0.0 if self.kjv_extra_count == 0 else 1.0
        return self.different_occurrences_count / self.tr_total_count

    @property
    def max_chapter_tr_mismatch(self) -> tuple[StrongAggregateScore, ...]:
        return _max_scores(self.chapter_scores, lambda score: score.tr_mismatch_ratio)

    @property
    def max_book_tr_mismatch(self) -> tuple[StrongAggregateScore, ...]:
        return _max_scores(self.book_scores, lambda score: score.tr_mismatch_ratio)

    @property
    def max_chapter_full_discrepancy(self) -> tuple[StrongAggregateScore, ...]:
        return _max_scores(
            self.chapter_scores,
            lambda score: score.full_discrepancy_ratio,
        )

    @property
    def max_book_full_discrepancy(self) -> tuple[StrongAggregateScore, ...]:
        return _max_scores(
            self.book_scores,
            lambda score: score.full_discrepancy_ratio,
        )

    @property
    def match_distribution(self) -> tuple[MatchDistributionBucket, ...]:
        return build_match_distribution(self.verse_scores)

    @property
    def match_ranges(self) -> tuple[MatchRange, ...]:
        return build_match_ranges(self.verse_scores)


def read_module(path: Path) -> BibleModule:
    """Read a bible module without opening it in writable mode."""
    if not path.is_file():
        raise FileNotFoundError(f"SQLite file was not found: {path}")

    sqlite_uri = f"file:{quote(path.resolve().as_posix(), safe='/:')}?mode=ro"
    connection = sqlite3.connect(sqlite_uri, uri=True)
    try:
        connection.execute("PRAGMA query_only = ON")
        rows = connection.execute(
            "SELECT verse_key, text FROM verses ORDER BY verse_key"
        ).fetchall()
    finally:
        connection.close()

    return BibleModule(
        path=path,
        verses={str(key): str(text or "") for key, text in rows},
    )


def read_strong_filter(path: Path = DEFAULT_WEAK_STRONGS_PATH) -> StrongFilter:
    """Read the reusable list of low-semantic-load Strong numbers."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_groups = payload.get("excluded_strong_numbers_by_category")
    if not isinstance(raw_groups, dict) or not raw_groups:
        raise ValueError(
            f"Strong filter asset must contain non-empty category groups: {path}"
        )

    groups: dict[str, tuple[str, ...]] = {}
    all_strongs: list[str] = []
    for group_name, raw_values in raw_groups.items():
        if not isinstance(group_name, str) or not isinstance(raw_values, list):
            raise ValueError(f"Invalid Strong filter group in {path}")
        normalized = tuple(normalize_strong(str(value)) for value in raw_values)
        if len(set(normalized)) != len(normalized):
            raise ValueError(f"Duplicate Strong number in group {group_name}: {path}")
        groups[group_name] = normalized
        all_strongs.extend(normalized)

    if len(set(all_strongs)) != len(all_strongs):
        raise ValueError(f"Strong filter groups overlap: {path}")

    raw_notes = payload.get("selection_policy", {}).get(
        "excluded_from_this_list",
        [],
    )
    notes = tuple(str(note) for note in raw_notes) if isinstance(raw_notes, list) else ()
    return StrongFilter(source_path=path, groups=groups, notes=notes)


def strong_counter(
    text: str,
    *,
    excluded_strongs: frozenset[str] = frozenset(),
) -> Counter[str]:
    """Extract normalized Strong keys, preserving multiplicity."""
    return Counter(
        strong
        for raw in _STRONG_TOKEN_PATTERN.findall(text)
        if (strong := normalize_strong(raw)) not in excluded_strongs
    )


def build_canonical_indexes() -> tuple[dict[str, str], tuple[str, ...]]:
    """Return verse-key labels and canonical-order NT keys."""
    testament_by_book_id = {book.book_id: book.testament for book in CANONICAL_BOOKS}
    refs_by_key: dict[str, str] = {}
    nt_keys: list[str] = []
    for verse in canonical_verses():
        key = verse_key_for(verse)
        refs_by_key[key] = verse.canonical_ref
        if testament_by_book_id[verse.book_id] == "NT":
            nt_keys.append(key)
    return refs_by_key, tuple(nt_keys)


def compare_new_testaments(
    kjv: BibleModule,
    lxx_tr: BibleModule,
    *,
    nt_keys: Sequence[str],
    refs_by_key: Mapping[str, str],
    excluded_strongs: frozenset[str] = frozenset(),
) -> StrongComparison:
    verse_scores: list[StrongVerseScore] = []
    for key in nt_keys:
        kjv_counts = strong_counter(
            kjv.verses.get(key, ""),
            excluded_strongs=excluded_strongs,
        )
        lxx_tr_counts = strong_counter(
            lxx_tr.verses.get(key, ""),
            excluded_strongs=excluded_strongs,
        )

        verse_scores.append(
            StrongVerseScore(
                verse_key=key,
                verse_ref=refs_by_key.get(key, key),
                kjv_counts=kjv_counts,
                tr_counts=lxx_tr_counts,
            )
        )

    frozen_scores = tuple(verse_scores)

    return StrongComparison(
        compared_verses_count=len(nt_keys),
        verse_scores=frozen_scores,
        chapter_scores=_aggregate_scores(frozen_scores, level="chapter"),
        book_scores=_aggregate_scores(frozen_scores, level="book"),
    )


def _aggregate_scores(
    scores: Sequence[StrongVerseScore],
    *,
    level: str,
) -> tuple[StrongAggregateScore, ...]:
    if level not in {"chapter", "book"}:
        raise ValueError(f"Unsupported aggregate level: {level}")

    totals: dict[str, list[int]] = {}
    for score in scores:
        book, chapter, _ = score.verse_ref.split(".", 2)
        label = book if level == "book" else f"{book}.{chapter}"
        aggregate = totals.setdefault(label, [0, 0, 0, 0, 0])
        aggregate[0] += 1
        aggregate[1] += score.tr_total_count
        aggregate[2] += score.matched_count
        aggregate[3] += score.tr_unmatched_count
        aggregate[4] += score.kjv_extra_count

    return tuple(
        StrongAggregateScore(
            label=label,
            verses_count=values[0],
            tr_total_count=values[1],
            matched_count=values[2],
            tr_unmatched_count=values[3],
            kjv_extra_count=values[4],
        )
        for label, values in totals.items()
    )


def _max_scores(
    scores: Sequence[StrongAggregateScore],
    value_getter: Callable[[StrongAggregateScore], float],
) -> tuple[StrongAggregateScore, ...]:
    if not scores:
        return ()
    maximum = max(value_getter(score) for score in scores)
    return tuple(
        score
        for score in scores
        if abs(value_getter(score) - maximum) < 1e-12
    )


def build_match_distribution(
    scores: Sequence[StrongVerseScore],
) -> tuple[MatchDistributionBucket, ...]:
    """Group verses by TR-match percentage, keeping 0% and 100% separate."""
    labels = ["100%", *[f"{lower}–<{lower + 5}%" for lower in range(95, 0, -5)]]
    labels.extend(["0–<5%", "0%"])
    counts = {label: 0 for label in labels}

    for score in scores:
        if score.matched_count == 0:
            label = "0%"
        elif score.matched_count == score.tr_total_count:
            label = "100%"
        else:
            lower_bound = (score.matched_count * 100 // score.tr_total_count // 5) * 5
            label = "0–<5%" if lower_bound == 0 else f"{lower_bound}–<{lower_bound + 5}%"
        counts[label] += 1

    return tuple(
        MatchDistributionBucket(label=label, verses_count=counts[label])
        for label in labels
    )


def build_match_ranges(
    scores: Sequence[StrongVerseScore],
) -> tuple[MatchRange, ...]:
    """Return exact fractional ranges requested for the detailed verse lists."""
    definitions = (
        ("<50%", 0, 1, 1, 2),
        ("50%–<66,(6)%", 1, 2, 2, 3),
        ("66,(6)%–<75%", 2, 3, 3, 4),
        ("75%–<80%", 3, 4, 4, 5),
    )
    grouped: dict[str, list[StrongVerseScore]] = {
        label: [] for label, *_ in definitions
    }
    for score in scores:
        total = score.tr_total_count
        matched = score.matched_count
        if total == 0:
            continue
        for label, lower_n, lower_d, upper_n, upper_d in definitions:
            if (
                matched * lower_d >= lower_n * total
                and matched * upper_d < upper_n * total
            ):
                grouped[label].append(score)
                break

    return tuple(
        MatchRange(label=label, verse_scores=tuple(grouped[label]))
        for label, *_ in definitions
    )


def format_report(
    kjv: BibleModule,
    lxx_tr: BibleModule,
    *,
    refs_by_key: Mapping[str, str],
    comparison: StrongComparison,
    strong_filter: StrongFilter,
) -> str:
    mismatched_percentage = _percentage(
        comparison.mismatched_verses_count,
        comparison.compared_verses_count,
    )
    lines = [
        "ПРОВЕРКА БИБЛЕЙСКИХ МОДУЛЕЙ",
        f"KJV:     {kjv.path}",
        f"LXX/TR:  {lxx_tr.path}",
        "Режим доступа к SQLite: только чтение (mode=ro, query_only=ON)",
        "",
        "1. ИСКЛЮЧАЕМЫЕ НОМЕРА СТРОНГА",
        f"Ассет: {strong_filter.source_path}",
        f"Всего исключаемых номеров: {len(strong_filter.excluded_strongs)}",
        "Из сравнения исключаются следующие категории:",
    ]

    for group_name, strongs in strong_filter.groups.items():
        lines.append(f"  {group_name} ({len(strongs)}): {', '.join(strongs)}")
    if strong_filter.notes:
        lines.append("Сохранены в сравнении:")
        lines.extend(f"  - {note}" for note in strong_filter.notes)

    lines.extend(["", "2. ПУСТЫЕ СТИХИ"])

    for module, label in ((kjv, "bible_kjv.sqlite"), (lxx_tr, "bible_lxx_tr.sqlite")):
        empty_keys = _ordered_keys(module.empty_keys, refs_by_key)
        empty_percentage = _percentage(len(empty_keys), len(module.verses))
        lines.extend(
            [
                f"{label}:",
                f"  Всего стихов: {len(module.verses)}",
                f"  Пустых стихов: {len(empty_keys)} ({empty_percentage}%)",
                "  Список пустых стихов:",
            ]
        )
        lines.extend(
            f"    {_verse_label(key, refs_by_key)}" for key in empty_keys
        )
        if not empty_keys:
            lines.append("    —")

    lines.extend(
        [
            "",
            "3. ПРОЦЕНТ СОВПАДЕНИЯ КАЖДОГО СТИХА KJV С TR",
            "TR используется как эталон; порядок номеров не учитывается, "
            "повторения учитываются.",
            "Процент совпадения = совпало / все номера TR.",
            "Процент несовпадения по TR = номера TR, отсутствующие в KJV / все номера TR.",
            "Полное расхождение дополнительно учитывает лишние номера KJV.",
            f"Сопоставлено стихов НЗ: {comparison.compared_verses_count}",
        ]
    )
    for score in comparison.verse_scores:
        lines.append(
            f"  {_verse_label(score.verse_key, refs_by_key)}: "
            f"TR={score.tr_total_count}; "
            f"совпало={score.matched_count}; "
            f"не совпало по TR={score.tr_unmatched_count}; "
            f"лишних KJV={score.kjv_extra_count}; "
            f"совпадение={_percentage_ratio(score.tr_match_ratio)}%; "
            f"несовпадение={_percentage_ratio(score.tr_mismatch_ratio)}%; "
            f"полное расхождение={_percentage_ratio(score.full_discrepancy_ratio)}%"
        )

    lines.extend(
        [
            "",
            "4. РАСПРЕДЕЛЕНИЕ СТИХОВ ПО ПРОЦЕНТУ СОВПАДЕНИЯ",
            "Промежуточные интервалы имеют вид: нижняя граница включается, "
            "верхняя — нет. 0% и 100% выделены отдельно.",
        ]
    )
    for bucket in comparison.match_distribution:
        lines.append(
            f"  {bucket.label}: {bucket.verses_count} стихов "
            f"({_percentage(bucket.verses_count, comparison.compared_verses_count)}% от НЗ)"
        )

    lines.extend(
        [
            "",
            "5. СПИСКИ СТИХОВ С СОВПАДЕНИЕМ НИЖЕ 80%",
            "Границы 50%, 66,(6)%, 75% и 80% сравниваются как точные дроби; "
            "верхняя граница каждого интервала не включается.",
        ]
    )
    for match_range in comparison.match_ranges:
        lines.append(
            f"  {match_range.label}: {len(match_range.verse_scores)} стихов "
            f"({_percentage(len(match_range.verse_scores), comparison.compared_verses_count)}% от НЗ)"
        )
        for score in match_range.verse_scores:
            lines.append(
                f"    {_verse_label(score.verse_key, refs_by_key)} — "
                f"{_percentage_ratio(score.tr_match_ratio)}% "
                f"({score.matched_count} из {score.tr_total_count} TR)"
            )

    lines.extend(
        [
            "",
            "6. МАКСИМАЛЬНОЕ НЕСОВПАДЕНИЕ ПО ГЛАВАМ И КНИГАМ",
            "Сначала показан максимум пропущенных номеров TR; затем — "
            "полное расхождение с учётом лишних номеров KJV.",
        ]
    )
    _append_maximum(
        lines,
        "Максимум по главам — несовпадение относительно TR",
        comparison.max_chapter_tr_mismatch,
        lambda score: score.tr_mismatch_ratio,
    )
    _append_maximum(
        lines,
        "Максимум по книгам — несовпадение относительно TR",
        comparison.max_book_tr_mismatch,
        lambda score: score.tr_mismatch_ratio,
    )
    _append_maximum(
        lines,
        "Максимум по главам — полное расхождение",
        comparison.max_chapter_full_discrepancy,
        lambda score: score.full_discrepancy_ratio,
    )
    _append_maximum(
        lines,
        "Максимум по книгам — полное расхождение",
        comparison.max_book_full_discrepancy,
        lambda score: score.full_discrepancy_ratio,
    )

    lines.extend(["", "7. ДЕТАЛЬНЫЕ НЕСОВПАДЕНИЯ ПО СТИХАМ"])
    if comparison.mismatches:
        for mismatch in comparison.mismatches:
            lines.extend(
                [
                    f"  {_verse_label(mismatch.verse_key, refs_by_key)}:",
                    "    Только TR (отсутствует в KJV): "
                    f"{_format_counter(mismatch.tr_only)}",
                    "    Только KJV (лишние относительно TR): "
                    f"{_format_counter(mismatch.kjv_only)}",
                    "    Совпало вхождений: "
                    f"{mismatch.matched_count} из {mismatch.tr_total_count} TR",
                    "    Процент совпадения: "
                    f"{_percentage_ratio(mismatch.tr_match_ratio)}%",
                    "    Полное расхождение по количеству: "
                    f"{mismatch.different_occurrences_count}",
                ]
            )
    else:
        lines.append("  —")

    lines.extend(
        [
            "",
            "8. ИТОГ СРАВНЕНИЯ НЗ:",
            f"  Несовпадающих стихов: {comparison.mismatched_verses_count} "
            f"из {comparison.compared_verses_count} "
            f"({mismatched_percentage}%)",
            f"  Номеров TR-эталона: {comparison.tr_total_count}",
            f"  Совпало: {comparison.matched_count}",
            f"  Не совпало по TR: {comparison.tr_unmatched_count}",
            f"  Лишних номеров KJV: {comparison.kjv_extra_count}",
            "  Процент совпадения с TR: "
            f"{_percentage_ratio(comparison.tr_match_ratio)}%",
            "  Процент несовпадения по TR: "
            f"{_percentage_ratio(comparison.tr_mismatch_ratio)}%",
            "  Полное расхождение: "
            f"{comparison.different_occurrences_count} "
            f"({_percentage_ratio(comparison.full_discrepancy_ratio)}% от TR)",
        ]
    )
    return "\n".join(lines) + "\n"


def _append_maximum(
    lines: list[str],
    title: str,
    scores: Sequence[StrongAggregateScore],
    ratio_getter: Callable[[StrongAggregateScore], float],
) -> None:
    if not scores:
        lines.append(f"{title}: —")
        return

    maximum_percentage = _percentage_ratio(ratio_getter(scores[0]))
    lines.append(f"{title}: {maximum_percentage}%")
    for score in scores:
        lines.append(
            f"  {score.label}: стихов={score.verses_count}; "
            f"TR={score.tr_total_count}; "
            f"совпало={score.matched_count}; "
            f"TR-only={score.tr_unmatched_count}; "
            f"KJV-only={score.kjv_extra_count}; "
            f"полное расхождение={_percentage_ratio(score.full_discrepancy_ratio)}%"
        )


def _counter_excess(left: Counter[str], right: Counter[str]) -> Counter[str]:
    return Counter(
        {
            strong: count - right[strong]
            for strong, count in left.items()
            if count > right[strong]
        }
    )


def _ordered_keys(keys: Sequence[str], refs_by_key: Mapping[str, str]) -> list[str]:
    known_order = {key: index for index, key in enumerate(refs_by_key)}
    return sorted(keys, key=lambda key: (known_order.get(key, len(known_order)), key))


def _verse_label(key: str, refs_by_key: Mapping[str, str]) -> str:
    return f"{refs_by_key.get(key, key)} [{key}]"


def _format_counter(values: Counter[str]) -> str:
    if not values:
        return "—"
    ordered = sorted(values.items(), key=lambda item: (item[0][0], int(item[0][1:])))
    return ", ".join(
        f"{strong}x{count}" if count > 1 else strong
        for strong, count in ordered
    )


def _percentage(part: int, total: int) -> str:
    return f"{(part / total * 100) if total else 0:.2f}"


def _percentage_ratio(ratio: float) -> str:
    return f"{ratio * 100:.2f}"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit empty verses and compare Strong's numbers in KJV and LXX/TR modules."
    )
    parser.add_argument("--kjv", type=Path, default=DEFAULT_KJV_PATH)
    parser.add_argument("--lxx-tr", type=Path, default=DEFAULT_LXX_TR_PATH)
    parser.add_argument(
        "--weak-strongs",
        type=Path,
        default=DEFAULT_WEAK_STRONGS_PATH,
        help="JSON asset with Strong numbers excluded from comparison.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the full UTF-8 report to this file instead of printing it.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    refs_by_key, nt_keys = build_canonical_indexes()
    strong_filter = read_strong_filter(args.weak_strongs)
    kjv = read_module(args.kjv)
    lxx_tr = read_module(args.lxx_tr)
    comparison = compare_new_testaments(
        kjv,
        lxx_tr,
        nt_keys=nt_keys,
        refs_by_key=refs_by_key,
        excluded_strongs=strong_filter.excluded_strongs,
    )
    report = format_report(
        kjv,
        lxx_tr,
        refs_by_key=refs_by_key,
        comparison=comparison,
        strong_filter=strong_filter,
    )

    sys.stdout.reconfigure(encoding="utf-8")
    if args.output is None:
        sys.stdout.write(report)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Полный отчёт сохранён: {args.output}")
        mismatched_percentage = _percentage(
            comparison.mismatched_verses_count,
            comparison.compared_verses_count,
        )
        print(
            f"Несовпадающих стихов НЗ: {comparison.mismatched_verses_count} "
            f"из {comparison.compared_verses_count} "
            f"({mismatched_percentage}%)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

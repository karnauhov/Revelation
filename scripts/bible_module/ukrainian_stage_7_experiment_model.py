"""Contracts for the rejected pre-stage-7 Strong-alignment experiment.

The functions in this module deliberately avoid corpus I/O.  They are shared by
the generator and the small CC0 fixture tests so that synthesis, token markup,
anchor rebasing, and comment serialization have one executable definition.

The contract name is frozen because the generated snapshot already uses it.
It does not designate an accepted stage-7 output contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


SCHEMA_VERSION = 1
CONTRACT_VERSION = "ukrainian-stage-7-strong-alignment-v1"
MAPPING_CONTRACT_VERSION = "oh1988-kjv-protestant-v1"
MERGE_SEPARATOR = " "
STRONG_RE = re.compile(r"^[GH][1-9][0-9]{0,3}$")
INTERNAL_CONNECTORS = {"'", "\u2019", "\u02bc", "-", "\u2010", "\u2011"}


def stable_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_lines(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(stable_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


@dataclass(frozen=True)
class WordToken:
    order: int
    start_scalar: int
    end_scalar: int
    surface: str


@dataclass(frozen=True)
class SynthesisPart:
    record_id: str
    source_start: int
    source_end: int
    target_start: int
    target_end: int
    text: str


def _is_letter_mark_or_number(char: str) -> bool:
    return unicodedata.category(char)[0] in {"L", "M", "N"}


def word_tokens(text: str) -> list[WordToken]:
    """Tokenize Unicode words while retaining exact scalar offsets."""

    result: list[WordToken] = []
    index = 0
    while index < len(text):
        if not _is_letter_mark_or_number(text[index]):
            index += 1
            continue
        start = index
        index += 1
        while index < len(text):
            char = text[index]
            if _is_letter_mark_or_number(char):
                index += 1
                continue
            if (
                char in INTERNAL_CONNECTORS
                and index + 1 < len(text)
                and _is_letter_mark_or_number(text[index + 1])
            ):
                index += 1
                continue
            break
        result.append(
            WordToken(
                order=len(result) + 1,
                start_scalar=start,
                end_scalar=index,
                surface=text[start:index],
            )
        )
    return result


def alignment_form(value: str) -> str:
    """Stage-2 comparison form; the display surface is never changed."""

    value = unicodedata.normalize("NFD", value.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("'", "\u02bc").replace("\u2019", "\u02bc")
    value = value.replace("-", "\u2010").replace("\u2011", "\u2010")
    return unicodedata.normalize("NFC", value)


def join_synthesis_parts(
    parts: Sequence[tuple[str, int, int, str]],
    *,
    separator: str = MERGE_SEPARATOR,
) -> tuple[str, list[SynthesisPart]]:
    """Join proven intervals and return their exact target offsets."""

    if not parts:
        raise ValueError("A target position must contain at least one source part")
    output = ""
    mapped: list[SynthesisPart] = []
    for record_id, source_start, source_end, text in parts:
        if source_start < 0 or source_end <= source_start:
            raise ValueError("Source intervals must be non-empty and ordered")
        if not text:
            raise ValueError("Source interval text must be non-empty")
        if output and not output[-1].isspace() and not text[0].isspace():
            output += separator
        target_start = len(output)
        output += text
        mapped.append(
            SynthesisPart(
                record_id=record_id,
                source_start=source_start,
                source_end=source_end,
                target_start=target_start,
                target_end=len(output),
                text=text,
            )
        )
    if not output:
        raise ValueError("Synthesized target text must be non-empty")
    return output, mapped


def validate_partition(
    source_length: int, intervals: Sequence[tuple[int, int]]
) -> None:
    """Require an exact, ordered, gapless scalar partition."""

    if source_length <= 0 or not intervals:
        raise ValueError("A partition requires a non-empty source")
    cursor = 0
    for start, end in intervals:
        if start != cursor or end <= start or end > source_length:
            raise ValueError("Intervals must cover the source exactly without overlap")
        cursor = end
    if cursor != source_length:
        raise ValueError("Intervals do not cover the complete source")


def rebase_anchor(
    source_start: int,
    source_end: int,
    parts: Sequence[SynthesisPart],
) -> tuple[int, int]:
    """Rebase only through a proven source interval; never bind by proximity."""

    candidates = [
        part
        for part in parts
        if part.source_start <= source_start <= source_end <= part.source_end
    ]
    if len(candidates) != 1:
        raise ValueError("Anchor has no unique proven source-to-target interval")
    part = candidates[0]
    return (
        part.target_start + source_start - part.source_start,
        part.target_start + source_end - part.source_start,
    )


def validate_strong(value: str) -> bool:
    if not STRONG_RE.fullmatch(value):
        return False
    number = int(value[1:])
    return (value[0] == "H" and number <= 8674) or (
        value[0] == "G" and number <= 5624
    )


def render_strong_markup(
    plain_text: str,
    tokens: Sequence[WordToken],
    strong_by_token: Mapping[int, Sequence[str]],
) -> str:
    """Insert standalone Strong markers after exact Ukrainian surface tokens."""

    cursor = 0
    output: list[str] = []
    for token in tokens:
        output.append(plain_text[cursor : token.end_scalar])
        markers = list(strong_by_token.get(token.order, ()))
        if any(not validate_strong(marker) for marker in markers):
            raise ValueError("Invalid classic Strong marker")
        if markers:
            output.append(" " + " ".join(markers))
        cursor = token.end_scalar
    output.append(plain_text[cursor:])
    return "".join(output)


def strip_strong_markup(marked_text: str) -> str:
    """Remove only standalone classic markers emitted by ``render``."""

    return re.sub(r" (?:(?:H|G)[1-9][0-9]{0,3})(?= |\W|$)", "", marked_text)


def serialize_comment_uses(uses: Sequence[Mapping[str, Any]]) -> str:
    """Serialize use instances in source order without deduplication."""

    blocks: list[str] = []
    for use in sorted(uses, key=lambda row: (int(row["source_order"]), row["use_id"])):
        text = str(use["full_text_nfc"])
        marker = str(use.get("marker") or "")
        blocks.append(f"{marker} {text}" if marker else text)
    return "\n\n".join(blocks)


def multiset_metrics(left: Sequence[str], right: Sequence[str]) -> dict[str, float | int]:
    """Return deterministic multiset and ordered sequence metrics."""

    from collections import Counter

    left_counts = Counter(left)
    right_counts = Counter(right)
    intersection = sum((left_counts & right_counts).values())
    precision = intersection / len(left) if left else (1.0 if not right else 0.0)
    recall = intersection / len(right) if right else (1.0 if not left else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    union = sum((left_counts | right_counts).values())
    jaccard = intersection / union if union else 1.0
    previous = [0] * (len(right) + 1)
    for left_value in left:
        current = [0]
        for index, right_value in enumerate(right, 1):
            current.append(
                previous[index - 1] + 1
                if left_value == right_value
                else max(previous[index], current[-1])
            )
        previous = current
    lcs = previous[-1]
    lcs_ratio = lcs / max(len(left), len(right)) if left or right else 1.0
    ordered_precision = lcs / len(left) if left else (1.0 if not right else 0.0)
    ordered_recall = lcs / len(right) if right else (1.0 if not left else 0.0)
    ordered_f1 = (
        2 * ordered_precision * ordered_recall / (ordered_precision + ordered_recall)
        if ordered_precision + ordered_recall
        else 0.0
    )
    return {
        "f1": round(f1, 6),
        "intersection": intersection,
        "jaccard": round(jaccard, 6),
        "lcs": lcs,
        "lcs_ratio": round(lcs_ratio, 6),
        "left_count": len(left),
        "ordered_f1": round(ordered_f1, 6),
        "ordered_precision": round(ordered_precision, 6),
        "ordered_recall": round(ordered_recall, 6),
        "right_count": len(right),
    }


def lexical_score(
    *,
    joint: int,
    strong_frequency: int,
    word_frequency: int,
    verse_count: int,
    source_position: float,
    target_position: float,
    transliteration_similarity: float = 0.0,
) -> float:
    """Evidence score used by the corpus-derived alignment model."""

    del verse_count  # retained in the versioned signature for fixture stability
    association = (
        5.0
        * joint
        / math.sqrt(max(strong_frequency * word_frequency, 1))
        + 0.15 * math.log1p(joint)
    )
    distortion = -0.65 * abs(source_position - target_position)
    return association + distortion + 1.25 * transliteration_similarity


def maximum_weight_assignment(weights: Sequence[Sequence[float]]) -> list[int]:
    """Return a deterministic maximum-weight rectangular assignment.

    Rows are assigned to distinct columns.  The implementation is the
    shortest-augmenting-path form of the Hungarian algorithm and deliberately
    has no third-party runtime dependency.
    """

    if not weights:
        return []
    column_count = len(weights[0])
    if column_count < len(weights) or any(len(row) != column_count for row in weights):
        raise ValueError("Assignment requires a rectangular matrix with rows <= columns")
    maximum = max(max(row) for row in weights)
    costs = [[maximum - value for value in row] for row in weights]
    row_count = len(costs)
    row_potential = [0.0] * (row_count + 1)
    column_potential = [0.0] * (column_count + 1)
    matching = [0] * (column_count + 1)
    predecessor = [0] * (column_count + 1)
    for row_index in range(1, row_count + 1):
        matching[0] = row_index
        minimum = [math.inf] * (column_count + 1)
        used = [False] * (column_count + 1)
        column = 0
        while True:
            used[column] = True
            current_row = matching[column]
            delta = math.inf
            next_column = 0
            for candidate in range(1, column_count + 1):
                if used[candidate]:
                    continue
                reduced = (
                    costs[current_row - 1][candidate - 1]
                    - row_potential[current_row]
                    - column_potential[candidate]
                )
                if reduced < minimum[candidate]:
                    minimum[candidate] = reduced
                    predecessor[candidate] = column
                if minimum[candidate] < delta:
                    delta = minimum[candidate]
                    next_column = candidate
            for candidate in range(column_count + 1):
                if used[candidate]:
                    row_potential[matching[candidate]] += delta
                    column_potential[candidate] -= delta
                else:
                    minimum[candidate] -= delta
            column = next_column
            if matching[column] == 0:
                break
        while True:
            previous = predecessor[column]
            matching[column] = matching[previous]
            column = previous
            if column == 0:
                break
    result = [-1] * row_count
    for column in range(1, column_count + 1):
        if matching[column]:
            result[matching[column] - 1] = column - 1
    if any(column < 0 for column in result):
        raise AssertionError("Assignment did not cover every row")
    return result

"""Pure contracts for Ukrainian OH1988 text synthesis (stage 6)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


SCHEMA_VERSION = 1
CONTRACT_VERSION = "ukrainian-stage-6-text-synthesis-v1"
MAPPING_CONTRACT_VERSION = "oh1988-kjv-protestant-v1"
MERGE_SEPARATOR = " "
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


def serialize_comment_uses(uses: Sequence[Mapping[str, Any]]) -> str:
    """Serialize use instances in source order without deduplication."""

    blocks: list[str] = []
    for use in sorted(uses, key=lambda row: (int(row["source_order"]), row["use_id"])):
        text = str(use["full_text_nfc"])
        marker = str(use.get("marker") or "")
        blocks.append(f"{marker} {text}" if marker else text)
    return "\n\n".join(blocks)

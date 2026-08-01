"""Pure data model and invariants for Ukrainian Bible roadmap stage 5.

The production generator lives in :mod:`ukrainian_stage_5`.  This module is
deliberately dependency-free so the mapping and footnote rules can be tested
with small CC0 fixtures without loading the normalized corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
MAPPING_CONTRACT_VERSION = "oh1988-kjv-protestant-v1"
MERGE_SEPARATOR = " "


def stable_json(value: Any) -> str:
    """Return the canonical JSON representation used by every artifact."""

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


@dataclass(frozen=True, order=True)
class Ref:
    book: str
    chapter: int
    verse: int
    subverse: str = ""

    @property
    def label(self) -> str:
        suffix = f".{self.subverse}" if self.subverse else ""
        return f"{self.book}.{self.chapter}.{self.verse}{suffix}"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Ref":
        return cls(
            book=str(value["book"]),
            chapter=int(value["chapter"]),
            verse=int(value["verse"]),
            subverse=str(value.get("subverse") or ""),
        )

    @classmethod
    def parse(cls, value: str) -> "Ref":
        match = re.fullmatch(
            r"(?P<book>[1-4]?[A-Za-z][A-Za-z0-9]*)\."
            r"(?P<chapter>\d+)[:.](?P<verse>\d+)"
            r"(?P<subverse>(?:\.[0-9]+|[a-z])?)",
            value.strip(),
        )
        if match is None:
            raise ValueError(f"Unsupported reference: {value!r}")
        subverse = match.group("subverse").lstrip(".")
        return cls(
            match.group("book"),
            int(match.group("chapter")),
            int(match.group("verse")),
            subverse,
        )


@dataclass(frozen=True)
class ScalarSpan:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"Invalid scalar span: {self.start}:{self.end}")

    def contains_anchor(self, start: int, end: int) -> bool:
        # Zero-width anchors are insertion points and belong only to the open
        # interval.  Exact split boundaries remain intentionally ambiguous.
        if start == end:
            return self.start < start < self.end
        return self.start <= start and end <= self.end

    def as_dict(self) -> dict[str, int]:
        return {"end_scalar": self.end, "start_scalar": self.start}


def stable_rule_id(
    *,
    operation: str,
    source_parts: Sequence[Mapping[str, Any]],
    target_refs: Sequence[str],
) -> str:
    """Create a stable identifier independent of report paths and timestamps."""

    identity = {
        "contract": MAPPING_CONTRACT_VERSION,
        "operation": operation,
        "source_parts": [
            {
                "record_id": part["record_id"],
                "segment_id": part["segment_id"],
                "span": part["span"],
            }
            for part in source_parts
        ],
        "target_refs": list(target_refs),
    }
    return f"uk5-{sha256_text(stable_json(identity))[:20]}"


def _target_for_anchor(
    *,
    operation: str,
    source_anchor_start: int,
    source_anchor_end: int,
    intervals: Sequence[Mapping[str, Any]],
) -> tuple[str | None, list[str], str]:
    candidates: list[str] = []
    for interval in intervals:
        span = ScalarSpan(
            int(interval["source_span"]["start_scalar"]),
            int(interval["source_span"]["end_scalar"]),
        )
        target_ref = str(interval["target_ref"])
        if span.contains_anchor(source_anchor_start, source_anchor_end):
            candidates.append(target_ref)

    if len(candidates) == 1:
        return candidates[0], candidates, "target_anchor_pending"

    all_targets = sorted(
        {str(interval["target_ref"]) for interval in intervals}
    )
    if len(all_targets) == 1:
        return all_targets[0], all_targets, "target_anchor_pending"
    return None, all_targets, "manual_review"


def project_footnote_use(
    *,
    use: Mapping[str, Any],
    rule_id: str,
    operation: str,
    intervals: Sequence[Mapping[str, Any]],
    target_order: Mapping[str, int],
) -> dict[str, Any]:
    """Project one source use without inventing a target scalar offset.

    ``intervals`` is the proved source-span to target-position relation.  A
    split/range boundary never chooses the nearest target.  Since stage 5 does
    not synthesize target text, successful projections preserve the source
    anchor and explicitly leave the target anchor pending.
    """

    start = int(use.get("anchor_start_scalar", -1))
    end = int(use.get("anchor_end_scalar", -1))
    has_anchor = start >= 0 and end >= start
    if has_anchor:
        target_ref, candidates, anchor_status = _target_for_anchor(
            operation=operation,
            source_anchor_start=start,
            source_anchor_end=end,
            intervals=intervals,
        )
    else:
        target_ref = None
        candidates = sorted(
            {str(interval["target_ref"]) for interval in intervals}
        )
        if operation == "1:1" and len(candidates) == 1:
            target_ref = candidates[0]
            anchor_status = "target_anchor_pending"
        else:
            anchor_status = "manual_review"

    projected = {
        "anchor_status": anchor_status,
        "footnote_id": str(use["footnote_id"]),
        "full_text_nfc": str(use["full_text_nfc"]),
        "mapping_rule_id": rule_id,
        "marker": use.get("printed_marker"),
        "operation": operation,
        "provenance": use.get("provenance", {}),
        "source_anchor": (
            {
                "end_scalar": end,
                "start_scalar": start,
            }
            if has_anchor
            else None
        ),
        "source_order": int(use["source_order"]),
        "status": "projected" if target_ref is not None else "explicit_anomaly",
        "target_anchor": None,
        "target_candidates": candidates,
        "target_order": target_order.get(target_ref) if target_ref else None,
        "target_ref": target_ref,
        "use_id": str(use["use_id"]),
    }
    return projected


def sort_projected_uses(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in sorted(
            rows,
            key=lambda row: (
                row.get("target_order") is None,
                row.get("target_order") or 0,
                int(row["source_order"]),
                str(row["use_id"]),
            ),
        )
    ]


def assert_forward_reverse_consistency(
    forward: Sequence[Mapping[str, Any]],
    reverse: Sequence[Mapping[str, Any]],
) -> None:
    forward_edges = {
        (
            str(row["rule_id"]),
            str(source["segment_id"]),
            str(target["verse_key"]),
        )
        for row in forward
        for source in row["source_parts"]
        for target in row["targets"]
    }
    reverse_edges = {
        (
            str(row["rule_id"]),
            str(source["segment_id"]),
            str(row["verse_key"]),
        )
        for row in reverse
        for source in row["source_parts"]
    }
    if forward_edges != reverse_edges:
        missing_reverse = sorted(forward_edges - reverse_edges)[:10]
        missing_forward = sorted(reverse_edges - forward_edges)[:10]
        raise AssertionError(
            "Forward/reverse mismatch: "
            f"missing_reverse={missing_reverse}, missing_forward={missing_forward}"
        )


def assert_unique_target_keys(reverse: Sequence[Mapping[str, Any]]) -> None:
    keys = [str(row["verse_key"]) for row in reverse]
    if len(keys) != len(set(keys)):
        raise AssertionError("Duplicate target verse_key in reverse map")


def assert_no_forbidden_stage_6_fields(value: Any) -> None:
    forbidden = {"strong_alignment", "strong_number", "target_comment"}

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            intersection = forbidden.intersection(node)
            if intersection:
                raise AssertionError(
                    f"Stage-6-only fields found: {sorted(intersection)}"
                )
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)

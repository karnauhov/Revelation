from __future__ import annotations

from .tagnt import normalize_strong

CLASSIC_GREEK_STRONG_MAX = 5624

EXTENDED_TO_CLASSIC_GREEK_STRONG_REPLACEMENTS: dict[str, str] = {
    "G6031": "G1650",
    "G6053": "G2737",
    "G6063": "G1492",
    "G6083": "G4894",
    "G6094": "G3166",
}


def strong_number(strong: str) -> int:
    normalized = normalize_strong(strong)
    if not normalized.startswith("G"):
        raise ValueError(f"Expected Greek Strong key: {strong}")
    return int(normalized[1:])


def is_classic_greek_strong(strong: str) -> bool:
    return 1 <= strong_number(strong) <= CLASSIC_GREEK_STRONG_MAX


def classic_greek_strong_or_none(strong: str) -> str | None:
    normalized = normalize_strong(strong)
    if not normalized.startswith("G"):
        return None

    replacement = EXTENDED_TO_CLASSIC_GREEK_STRONG_REPLACEMENTS.get(
        normalized,
        normalized,
    )
    if is_classic_greek_strong(replacement):
        return replacement
    return None

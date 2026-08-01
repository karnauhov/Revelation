from __future__ import annotations

import re
from collections.abc import Mapping

from .strong_numbers import (
    CLASSIC_GREEK_STRONG_MAX,
    EXTENDED_TO_CLASSIC_GREEK_STRONG_REPLACEMENTS,
)

STRONG_CONTRACT_VERSION = 1
CLASSIC_HEBREW_STRONG_MAX = 8674
FINAL_STRONG_PATTERN = r"^[HG][1-9][0-9]*$"

_NUMERIC_STRONG_PATTERN = re.compile(r"^([HG])0*(\d+)$", re.IGNORECASE)
_EXTENDED_STRONG_PATTERN = re.compile(
    r"^[HG]\d+(?:[A-Z])?(?:_[A-Z0-9]+)?$",
    re.IGNORECASE,
)


class StrongContractError(ValueError):
    """Raised when a Strong value cannot enter the Ukrainian runtime module."""


def classic_strong_max(prefix: str) -> int:
    normalized_prefix = prefix.strip().upper()
    if normalized_prefix == "H":
        return CLASSIC_HEBREW_STRONG_MAX
    if normalized_prefix == "G":
        return CLASSIC_GREEK_STRONG_MAX
    raise StrongContractError(f"Unknown Strong namespace: {prefix}")


def normalize_classic_strong(raw_strong: str) -> str:
    """Normalize one classic Strong key and enforce its namespace range."""

    match = _NUMERIC_STRONG_PATTERN.fullmatch(raw_strong.strip())
    if match is None:
        raise StrongContractError(f"Invalid classic Strong key: {raw_strong}")
    prefix = match.group(1).upper()
    number = int(match.group(2))
    maximum = classic_strong_max(prefix)
    if number < 1 or number > maximum:
        raise StrongContractError(
            f"Classic Strong key is outside {prefix}1-{prefix}{maximum}: "
            f"{raw_strong}"
        )
    return f"{prefix}{number}"


def normalize_strong_for_output(
    raw_strong: str,
    *,
    extended_replacements: Mapping[str, str] | None = None,
) -> str:
    """Resolve one raw Strong value to the strict runtime representation.

    Extended, alternative, or composite values are never truncated. They must
    have an explicit, versioned replacement or this function fails.
    """

    raw_value = raw_strong.strip()
    if not raw_value:
        raise StrongContractError("Strong key must not be empty")

    numeric_match = _NUMERIC_STRONG_PATTERN.fullmatch(raw_value)
    if numeric_match is not None:
        prefix = numeric_match.group(1).upper()
        number = int(numeric_match.group(2))
        normalized_input = f"{prefix}{number}"
    else:
        normalized_input = raw_value.upper()
        if _EXTENDED_STRONG_PATTERN.fullmatch(normalized_input) is None:
            raise StrongContractError(
                "Composite or malformed Strong key requires an explicit "
                f"intermediate representation: {raw_strong}"
            )

    replacements = {
        key.upper(): value
        for key, value in EXTENDED_TO_CLASSIC_GREEK_STRONG_REPLACEMENTS.items()
    }
    if extended_replacements is not None:
        for raw_key, replacement in extended_replacements.items():
            key = raw_key.strip().upper()
            if not key:
                raise StrongContractError("Extended Strong mapping key is empty")
            existing = replacements.get(key)
            if existing is not None and existing != replacement:
                raise StrongContractError(
                    f"Conflicting extended Strong mapping for {key}: "
                    f"{existing} != {replacement}"
                )
            replacements[key] = replacement

    replacement = replacements.get(normalized_input)
    if replacement is not None:
        return normalize_classic_strong(replacement)

    try:
        return normalize_classic_strong(normalized_input)
    except StrongContractError as error:
        raise StrongContractError(
            "Unresolved extended or out-of-range Strong key must be preserved "
            f"in the intermediate model and audited: {raw_strong}"
        ) from error


def strong_contract_manifest() -> dict[str, object]:
    return {
        "version": STRONG_CONTRACT_VERSION,
        "final_pattern": FINAL_STRONG_PATTERN,
        "classic_ranges": {
            "H": {"min": 1, "max": CLASSIC_HEBREW_STRONG_MAX},
            "G": {"min": 1, "max": CLASSIC_GREEK_STRONG_MAX},
        },
        "leading_zeroes": "removed_before_final_output",
        "known_extended_to_classic": dict(
            sorted(EXTENDED_TO_CLASSIC_GREEK_STRONG_REPLACEMENTS.items())
        ),
        "unmapped_extended": (
            "preserve_raw_and_block_output_until_explicit_versioned_mapping"
        ),
        "alternatives": (
            "preserve_relation_and_candidates; select_one_explicitly_or_block"
        ),
        "composites": (
            "preserve_components_and_relation; never_split_or_flatten_silently"
        ),
        "deduplication": "stable_per_surface_token_after_explicit_resolution",
        "testament_namespaces": {
            "OT": "H_only_in_final_module",
            "NT": "G_only_in_final_module",
        },
    }

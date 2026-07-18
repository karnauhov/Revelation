from __future__ import annotations

import re
from collections.abc import Iterable


class ImportGuardError(ValueError):
    """Raised when a Bible import source violates a hard project guard."""


_BOOK_KEY_PATTERN = re.compile(r"[^0-9a-z]+")

_FORBIDDEN_BOOK_KEYS = {
    "1esd",
    "1esdras",
    "1macc",
    "1maccabees",
    "2esd",
    "2esdras",
    "2macc",
    "2maccabees",
    "3esd",
    "3esdras",
    "3macc",
    "3maccabees",
    "4esd",
    "4esdras",
    "4macc",
    "4maccabees",
    "adddan",
    "addesth",
    "additionsdaniel",
    "additionsesther",
    "azariah",
    "bar",
    "baruch",
    "bel",
    "belanddragon",
    "deuterocanonical",
    "epistlejeremiah",
    "epjer",
    "esdras1",
    "esdras3",
    "esdras4",
    "greekestheradditions",
    "jdt",
    "judith",
    "maccabees",
    "maccabees1",
    "maccabees2",
    "maccabees3",
    "maccabees4",
    "odes",
    "prayerazariah",
    "prayermanasseh",
    "prazar",
    "prman",
    "ps151",
    "psalm151",
    "psalmssolomon",
    "psssol",
    "sir",
    "sirach",
    "sus",
    "susanna",
    "tob",
    "tobit",
    "wis",
    "wisdom",
    "wisdomofsolomon",
}

_RVR1960_KEYS = {
    "rvr1960",
    "rvr60",
    "reinavalera1960",
    "reinavalera60",
    "reina-valera1960",
    "reina-valera60",
}


def normalize_guard_key(value: str) -> str:
    return _BOOK_KEY_PATTERN.sub("", value.strip().casefold())


def assert_canonical_import_book(book_name_or_code: str) -> None:
    normalized = normalize_guard_key(book_name_or_code)
    if normalized in _FORBIDDEN_BOOK_KEYS:
        raise ImportGuardError(
            f"Refusing to import non-canonical/apocryphal book: {book_name_or_code}"
        )


def assert_no_forbidden_books(book_names_or_codes: Iterable[str]) -> None:
    for book_name_or_code in book_names_or_codes:
        assert_canonical_import_book(book_name_or_code)


def assert_source_allowed(
    source_name_or_code: str,
    *,
    explicit_rvr1960_permission: bool = False,
) -> None:
    normalized = normalize_guard_key(source_name_or_code)
    if normalized in _RVR1960_KEYS and not explicit_rvr1960_permission:
        raise ImportGuardError(
            "Refusing to import RVR1960 without explicit owner permission."
        )

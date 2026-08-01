from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

STAGE_4_SCHEMA_VERSION = 1
PARSER_CONTRACT_VERSION = "ukrainian-stage-4-source-native-v1"
EDITION_ID = "ohienko_1988"

_LINE_ENDINGS = re.compile(r"\r\n?|\u2028|\u2029")
_INLINE_SPACE = re.compile(r"[\t\v\f\u00a0\u2000-\u200a\u202f\u205f\u3000]+")
_SPACE_AROUND_NEWLINE = re.compile(r" *\n *")
_MULTI_SPACE = re.compile(r" {2,}")
_STRONG_TOKEN = re.compile(r"(?i)([HG])0*(\d+)([A-Z]?)(?:_([A-Z0-9]+))?")


class Stage4ContractError(ValueError):
    """Raised when a source-native stage-4 record violates the contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def normalize_source_text(value: str, *, multiline: bool = False) -> str:
    """Apply loss-visible NFC and whitespace normalization.

    Apostrophes, hyphens, dashes, punctuation, case, and Ukrainian spelling are
    intentionally preserved. The raw value is always stored beside this value.
    """

    normalized = unicodedata.normalize("NFC", _LINE_ENDINGS.sub("\n", value))
    normalized = _INLINE_SPACE.sub(" ", normalized)
    normalized = _SPACE_AROUND_NEWLINE.sub("\n", normalized)
    if multiline:
        return "\n".join(_MULTI_SPACE.sub(" ", line).strip() for line in normalized.split("\n")).strip()
    return _MULTI_SPACE.sub(" ", normalized.replace("\n", " ")).strip()


def normalize_ukrainian_surface(value: str) -> str:
    return normalize_source_text(value)


def normalize_strong_candidate(raw: str, *, source_id: str) -> dict[str, object]:
    """Normalize the spelling of one Strong candidate without resolving it.

    Stage 4 preserves augmented, alternative, and source-specific identifiers;
    it does not perform the stage-6 alignment decision.
    """

    cleaned = raw.strip().strip("{}\\")
    match = _STRONG_TOKEN.fullmatch(cleaned)
    if match is None:
        return {"raw": raw, "normalized": None, "status": "invalid"}
    prefix, digits, suffix, extension = match.groups()
    number = int(digits)
    normalized = f"{prefix.upper()}{number}{suffix.upper()}"
    if extension:
        normalized += f"_{extension.upper()}"
    status = "classic"
    if suffix or extension:
        status = "extended_unresolved"
    if source_id == "unfoldingword_ugnt_v0_34" and prefix.upper() == "G":
        # UGNT encodes the classic number with a trailing variant digit.
        if len(digits) == 5 and digits.endswith("0"):
            number = int(digits[:-1])
            normalized = f"G{number}"
            status = "classic_source_encoding"
    maximum = 8674 if prefix.upper() == "H" else 5624
    if status.startswith("classic") and not 1 <= number <= maximum:
        status = "out_of_range"
    return {"raw": raw, "normalized": normalized, "status": status}


def stable_id(*parts: object) -> str:
    payload = "\u001f".join(str(part) for part in parts)
    return sha256_text(payload)[:24]


@dataclass(frozen=True)
class SourceRef:
    book: str
    chapter: int
    verse: int
    subverse: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "book": self.book,
            "chapter": self.chapter,
            "verse": self.verse,
            "subverse": self.subverse,
        }

    @property
    def label(self) -> str:
        suffix = f".{self.subverse}" if self.subverse else ""
        return f"{self.book}.{self.chapter}.{self.verse}{suffix}"


@dataclass
class Token:
    order: int
    kind: str
    surface_raw: str
    surface_nfc: str | None = None
    start_scalar: int | None = None
    end_scalar: int | None = None
    strong_raw: list[str] = field(default_factory=list)
    strong: list[dict[str, object]] = field(default_factory=list)
    morphology: list[str] = field(default_factory=list)
    lemma: str = ""
    extra: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "token_id": stable_id(self.order, self.kind, self.surface_raw),
            "order": self.order,
            "kind": self.kind,
            "surface_raw": self.surface_raw,
            "surface_nfc": self.surface_nfc
            if self.surface_nfc is not None
            else normalize_source_text(self.surface_raw),
            "start_scalar": self.start_scalar,
            "end_scalar": self.end_scalar,
            "strong_raw": self.strong_raw,
            "strong": self.strong,
            "morphology": self.morphology,
            "lemma": self.lemma,
            "extra": self.extra,
        }


def make_record(
    *,
    source_id: str,
    source_role: str,
    source_version: str,
    source_revision: str,
    source_order: int,
    source_locator: Mapping[str, object],
    source_kind: str,
    source_plain_raw: str,
    source_ref_raw: str = "",
    source_ref: SourceRef | None = None,
    tokens: Sequence[Token | Mapping[str, object]] = (),
    footnotes: Sequence[Mapping[str, object]] = (),
    provenance: Mapping[str, object] | None = None,
    classification: Sequence[str] = (),
    extra: Mapping[str, object] | None = None,
    edition_applicable: bool = False,
) -> dict[str, object]:
    locator = dict(source_locator)
    record_id = f"{source_id}:{stable_id(source_id, source_order, canonical_json(locator), source_ref_raw)}"
    raw_fragment_digest = sha256_text(source_plain_raw)
    record: dict[str, object] = {
        "schema_version": STAGE_4_SCHEMA_VERSION,
        "parser_contract_version": PARSER_CONTRACT_VERSION,
        "record_id": record_id,
        "edition_id": EDITION_ID if edition_applicable else None,
        "source_id": source_id,
        "source_role": source_role,
        "source_version": source_version,
        "source_revision": source_revision,
        "source_ref_raw": source_ref_raw,
        "source_ref_normalized": source_ref.as_dict() if source_ref else None,
        "source_order": source_order,
        "source_locator": locator,
        "source_kind": source_kind,
        "source_plain_raw": source_plain_raw,
        "source_plain_nfc": normalize_source_text(source_plain_raw),
        "tokens": [token.as_dict() if isinstance(token, Token) else dict(token) for token in tokens],
        "footnotes": [dict(footnote) for footnote in footnotes],
        "provenance": dict(provenance or {}),
        "source_fragment_sha256": raw_fragment_digest,
        "classification": list(classification),
        "projection_status": "unprojected",
        "extra": dict(extra or {}),
    }
    validate_record(record)
    return record


def validate_record(record: Mapping[str, object]) -> None:
    forbidden = {
        "target_ref",
        "target_refs",
        "target_spans",
        "target_comment",
        "decision_comment",
        "alignment_comment",
        "verse_key",
    }
    present = forbidden.intersection(record)
    if present:
        raise Stage4ContractError(f"Premature target fields: {sorted(present)}")
    if record.get("projection_status") != "unprojected":
        raise Stage4ContractError("Stage-4 projection_status must be unprojected")
    raw = record.get("source_plain_raw")
    nfc = record.get("source_plain_nfc")
    if not isinstance(raw, str) or not isinstance(nfc, str):
        raise Stage4ContractError("Source text fields must be strings")
    if nfc != normalize_source_text(raw):
        raise Stage4ContractError("source_plain_nfc is not deterministically normalized")
    tokens = record.get("tokens")
    if not isinstance(tokens, list):
        raise Stage4ContractError("tokens must be a list")
    orders = [token.get("order") for token in tokens if isinstance(token, Mapping)]
    if orders != sorted(orders) or len(orders) != len(set(orders)):
        raise Stage4ContractError("Token order is not strictly stable")
    if not isinstance(record.get("provenance"), Mapping):
        raise Stage4ContractError("Every record requires provenance")


def write_jsonl(records: Iterable[Mapping[str, object]]) -> tuple[bytes, int]:
    lines: list[str] = []
    count = 0
    for record in records:
        validate_record(record)
        lines.append(canonical_json(record))
        count += 1
    payload = ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")
    return payload, count


def count_words(value: str) -> int:
    return len(re.findall(r"[^\W\d_]+(?:[’'ʼ\-][^\W\d_]+)*", value, re.UNICODE))

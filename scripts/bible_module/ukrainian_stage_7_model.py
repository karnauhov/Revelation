"""Pure contracts and invariants for Ukrainian Strong alignment stage 7.

The production pipeline deliberately keeps exact Ukrainian surface text apart
from comparison forms.  Nothing in this module reads a corpus or assigns an
alignment; it only provides deterministic primitives that can be unit-tested
without any licensed source material.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from statistics import NormalDist
import json
import re
import unicodedata
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
CONTRACT_VERSION = "ukrainian-stage-7-evidence-alignment-v1"
TOKENIZER_VERSION = "ukrainian-stage-7-exact-scalar-byte-v1"

_APOSTROPHES = "'\N{RIGHT SINGLE QUOTATION MARK}\N{MODIFIER LETTER APOSTROPHE}\N{SINGLE HIGH-REVERSED-9 QUOTATION MARK}`"
_STRONG_MARKER_RE = re.compile(r"(?<!\w)([HG][1-9][0-9]*)(?!\w)")
_RAW_STRONG_RE = re.compile(
    r"^(?P<prefix>[HGA])0*(?P<number>[0-9]+)(?P<suffix>[A-Za-z]*)"
    r"(?:_[A-Za-z0-9]+)?$",
    re.IGNORECASE,
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def stable_json(value: Any) -> str:
    """Return the sole canonical JSON representation used by stage 7."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def sha256_lines(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = sha256()
    for row in rows:
        digest.update(stable_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


@dataclass(frozen=True)
class ExactToken:
    order: int
    surface: str
    start_scalar: int
    end_scalar: int
    start_byte: int
    end_byte: int
    comparison: str

    @property
    def token_id_suffix(self) -> str:
        return f"{self.order:03d}:{self.start_scalar}:{self.end_scalar}"


def _is_word_char(value: str) -> bool:
    return unicodedata.category(value)[0] in {"L", "M", "N"}


def comparison_form(value: str) -> str:
    """Normalize for comparison only; this value is never rendered.

    Stress marks and other combining marks are removed, apostrophes are
    unified and case is folded.  Historic spelling remains untouched in the
    source ``surface`` field.
    """

    output: list[str] = []
    for source_char in unicodedata.normalize("NFC", value.casefold()):
        # Ukrainian й/ї (and Cyrillic ё in bridge controls) are independent
        # letters, not optional accents.  Keep precomposed Cyrillic letters;
        # Hebrew/Greek comparison still benefits from mark-insensitive NFKD.
        if _is_word_char(source_char) and "CYRILLIC" in unicodedata.name(source_char, ""):
            output.append(source_char)
            continue
        for char in unicodedata.normalize("NFKD", source_char):
            if unicodedata.category(char).startswith("M"):
                continue
            if char in _APOSTROPHES:
                output.append("'")
            elif char in {"\N{HYPHEN}", "\N{NON-BREAKING HYPHEN}", "\N{EN DASH}", "\N{EM DASH}"}:
                output.append("-")
            elif _is_word_char(char) or char in {"'", "-"}:
                output.append(char)
    return "".join(output).strip("'-")


def exact_word_tokens(text: str) -> list[ExactToken]:
    """Tokenize word surfaces while retaining scalar and UTF-8 byte spans."""

    tokens: list[ExactToken] = []
    start: int | None = None
    byte_offsets = [0]
    for char in text:
        byte_offsets.append(byte_offsets[-1] + len(char.encode("utf-8")))

    for index, char in enumerate(text + "\0"):
        word = index < len(text) and _is_word_char(char)
        internal_joiner = (
            index < len(text)
            and char in _APOSTROPHES + "-\N{HYPHEN}\N{NON-BREAKING HYPHEN}"
            and start is not None
            and index + 1 < len(text)
            and _is_word_char(text[index + 1])
        )
        if word or internal_joiner:
            if start is None:
                start = index
            continue
        if start is None:
            continue
        surface = text[start:index]
        tokens.append(
            ExactToken(
                order=len(tokens) + 1,
                surface=surface,
                start_scalar=start,
                end_scalar=index,
                start_byte=byte_offsets[start],
                end_byte=byte_offsets[index],
                comparison=comparison_form(surface),
            )
        )
        start = None
    return tokens


def validate_exact_partition(text: str, tokens: Sequence[ExactToken]) -> None:
    previous_end_scalar = 0
    previous_end_byte = 0
    encoded = text.encode("utf-8")
    for expected_order, token in enumerate(tokens, 1):
        if token.order != expected_order:
            raise ValueError("Non-contiguous token order")
        if (
            token.start_scalar < previous_end_scalar
            or token.start_byte < previous_end_byte
            or token.end_scalar <= token.start_scalar
            or token.end_byte <= token.start_byte
            or token.end_scalar > len(text)
            or token.end_byte > len(encoded)
        ):
            raise ValueError("Token offsets overlap or are out of bounds")
        if text[token.start_scalar : token.end_scalar] != token.surface:
            raise ValueError("Scalar token round-trip failed")
        if encoded[token.start_byte : token.end_byte].decode("utf-8") != token.surface:
            raise ValueError("Byte token round-trip failed")
        previous_end_scalar = token.end_scalar
        previous_end_byte = token.end_byte


def normalize_strong(raw: str) -> dict[str, Any]:
    """Preserve a raw source code and derive a runtime classic Strong code.

    ``A`` is the WLC marker for an Aramaic Strong entry and shares the Hebrew
    dictionary number at runtime.  Source suffixes/sense tags remain in
    ``raw`` and are never represented as a separate classic number.
    """

    value = raw.strip()
    match = _RAW_STRONG_RE.fullmatch(value)
    if match is None:
        return {
            "raw": value,
            "classic": None,
            "status": "nonclassic_source_code",
            "source_suffix": "",
        }
    prefix = match.group("prefix").upper()
    number = int(match.group("number"))
    runtime_prefix = "H" if prefix in {"H", "A"} else "G"
    maximum = 8674 if runtime_prefix == "H" else 5624
    classic = f"{runtime_prefix}{number}"
    status = "classic"
    if not 1 <= number <= maximum:
        classic = None
        status = "out_of_classic_range"
    elif prefix == "A":
        status = "classic_aramaic_source"
    elif match.group("suffix"):
        status = "classic_with_source_suffix"
    return {
        "raw": value,
        "classic": classic,
        "status": status,
        "source_suffix": match.group("suffix"),
    }


def validate_classic_strong(value: str) -> bool:
    normalized = normalize_strong(value)
    return normalized["classic"] == value and normalized["status"] == "classic"


def render_strong_markup(
    plain_text: str,
    tokens: Sequence[ExactToken],
    strong_by_token: Mapping[int, Sequence[str]],
) -> str:
    """Insert standalone Strong markers after exact Ukrainian surfaces."""

    validate_exact_partition(plain_text, tokens)
    valid_orders = {token.order for token in tokens}
    if any(not isinstance(order, int) or order not in valid_orders for order in strong_by_token):
        raise ValueError("Dangling Ukrainian token order in Strong assignment")
    cursor = 0
    output: list[str] = []
    for token in tokens:
        output.append(plain_text[cursor : token.end_scalar])
        markers = list(dict.fromkeys(strong_by_token.get(token.order, ())))
        if any(not validate_classic_strong(marker) for marker in markers):
            raise ValueError("Invalid classic Strong marker")
        if markers:
            output.append(" " + " ".join(markers))
        cursor = token.end_scalar
    output.append(plain_text[cursor:])
    return "".join(output)


def strip_strong_markup(marked_text: str) -> str:
    # The renderer owns the separator immediately before every marker.  Drop
    # that separator together with the marker, one occurrence at a time.  A
    # repeated substitution is required for ``surface H1 H2`` because the
    # second marker only becomes adjacent to the surface after H1 is removed.
    marker_with_separator = re.compile(
        r" ([HG][1-9][0-9]*)(?=$|\s|[^\w])"
    )
    previous = None
    stripped = marked_text
    while stripped != previous:
        previous = stripped
        stripped = marker_with_separator.sub("", stripped)
    return stripped


def wilson_lower_bound(
    correct: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> float:
    """One-sided Wilson score lower bound."""

    if total <= 0 or correct < 0 or correct > total:
        return 0.0
    z = NormalDist().inv_cdf(confidence)
    proportion = correct / total
    denominator = 1 + z * z / total
    centre = proportion + z * z / (2 * total)
    adjustment = z * sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    )
    return (centre - adjustment) / denominator


def deterministic_fold(stable_id: str, folds: int = 10) -> int:
    if folds <= 1:
        raise ValueError("At least two folds are required")
    return int(sha256_text(stable_id)[:16], 16) % folds


def normalized_edit_similarity(left: str, right: str) -> float:
    """Small deterministic similarity primitive for candidate generation."""

    a = comparison_form(left)
    b = comparison_form(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (char_a != char_b),
                )
            )
        previous = current
    distance = previous[-1]
    return 1.0 - distance / max(len(a), len(b))


def candidate_is_evidence_backed(candidate: Mapping[str, Any]) -> bool:
    """Reject banned positional/verse-bag-only candidates fail-closed."""

    evidence = set(candidate.get("evidence_channels", ()))
    prohibited = {
        "nearest",
        "neighbor",
        "proportional",
        "verse_bag",
        "majority_only",
        "frequency_only",
        "one_translation",
    }
    direct_target_evidence = {
        "lexical",
        "lexical_morphological",
        "morphology",
        "lemma",
        "surface_identity",
        "manual_oh1988_review",
        "gold_annotation",
        "bidirectional_statistical",
        "multilingual_contextual",
        "transliteration_named_entity",
    }
    return bool(evidence & direct_target_evidence) and not bool(evidence & prohibited)


def override_is_current(
    override: Mapping[str, Any],
    current_input_digests: Mapping[str, str],
) -> bool:
    """Return whether a manual override is safe to apply, fail-closed."""

    if override.get("stale") is not False:
        return False
    recorded = override.get("input_digests")
    if not isinstance(recorded, Mapping) or not recorded:
        return False
    if {str(key) for key in recorded} != {
        str(key) for key in current_input_digests
    }:
        return False
    return all(
        isinstance(value, str)
        and _SHA256_RE.fullmatch(value) is not None
        and _SHA256_RE.fullmatch(current_input_digests.get(str(key), "")) is not None
        and current_input_digests.get(str(key)) == value
        for key, value in recorded.items()
    )


def resolve_override_current_input_digests(
    override: Mapping[str, Any],
    *,
    source_registry_sha256: str,
    stage6_text_sha256: str,
    stage6_verse_sha256_by_target_token_id: Mapping[str, str],
    legacy_snapshot_sha256: str,
    fingerprint_sha256: str,
    fingerprint_selected_original_layer_sha256: str,
    source_apparatus_sha256_by_original_token_id: Mapping[str, str],
) -> dict[str, str]:
    """Resolve the exact current digest set required by one override.

    The resolver is deliberately pure: recorded ``input_digests`` never
    participate in choosing or computing the current values.  Callers must
    obtain the supplied values from immutable inputs or freshly validated
    artifacts.
    """

    def require_sha256(value: object, *, label: str) -> str:
        if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
            raise ValueError(f"Current override input lacks valid SHA-256: {label}")
        return value

    def current_verse_sha256() -> str:
        token_ids = override.get("stable_oh1988_token_ids")
        if (
            not isinstance(token_ids, (list, tuple))
            or not token_ids
            or len(set(token_ids)) != len(token_ids)
            or any(not isinstance(token_id, str) for token_id in token_ids)
        ):
            raise ValueError("Override lacks a unique nonempty OH1988 token span")
        digests: set[str] = set()
        for token_id in token_ids:
            digest = stage6_verse_sha256_by_target_token_id.get(token_id)
            digests.add(require_sha256(digest, label=f"stage6 verse for {token_id}"))
        if len(digests) != 1:
            raise ValueError("Override OH1988 token span crosses stage-6 verses")
        return next(iter(digests))

    decision = override.get("decision")
    if decision == "reject_source_bridge":
        return {
            "source_registry": require_sha256(
                source_registry_sha256, label="source_registry"
            )
        }
    if decision == "reject_legacy_link":
        return {
            "legacy_snapshot": require_sha256(
                legacy_snapshot_sha256, label="legacy_snapshot"
            ),
            "stage6_text": require_sha256(
                stage6_text_sha256, label="stage6_text"
            ),
            "verse": current_verse_sha256(),
        }

    textual_member_ids = override.get("textual_alternative_member_ids")
    if (
        not isinstance(textual_member_ids, (list, tuple))
        or not textual_member_ids
        or len(set(textual_member_ids)) != len(textual_member_ids)
        or any(not isinstance(token_id, str) for token_id in textual_member_ids)
    ):
        raise ValueError("Unknown or incomplete alignment override decision contract")
    apparatus_digests: set[str] = set()
    for token_id in textual_member_ids:
        digest = source_apparatus_sha256_by_original_token_id.get(token_id)
        apparatus_digests.add(
            require_sha256(digest, label=f"source apparatus for {token_id}")
        )
    if len(apparatus_digests) != 1:
        raise ValueError("Textual override members do not share one source apparatus")
    return {
        "fingerprint": require_sha256(fingerprint_sha256, label="fingerprint"),
        "fingerprint_selected_original_layer": require_sha256(
            fingerprint_selected_original_layer_sha256,
            label="fingerprint_selected_original_layer",
        ),
        "source_apparatus": next(iter(apparatus_digests)),
        "source_registry": require_sha256(
            source_registry_sha256, label="source_registry"
        ),
        "stage6_text": require_sha256(stage6_text_sha256, label="stage6_text"),
        "stage6_verse": current_verse_sha256(),
    }


def validate_versioned_alignment_overrides(
    overrides: Sequence[Mapping[str, Any]],
    *,
    source_registry_sha256: str,
    stage6_text_sha256: str,
    stage6_verse_sha256_by_target_token_id: Mapping[str, str],
    legacy_snapshot_sha256: str,
    fingerprint_sha256: str,
    fingerprint_selected_original_layer_sha256: str,
    source_apparatus_sha256_by_original_token_id: Mapping[str, str],
) -> dict[str, Mapping[str, Any]]:
    """Validate current versioned overrides and their supersedes graph."""

    by_id: dict[str, Mapping[str, Any]] = {}
    for override in overrides:
        override_id = override.get("override_id")
        if not isinstance(override_id, str) or not override_id:
            raise ValueError("Alignment override lacks a stable override_id")
        if override_id in by_id:
            raise ValueError(f"Duplicate alignment override ID: {override_id}")
        if override.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"Alignment override schema drift: {override_id}")
        if override.get("contract_version") != CONTRACT_VERSION:
            raise ValueError(f"Alignment override contract drift: {override_id}")
        if override.get("stale") is not False:
            raise ValueError(f"Alignment override is stale: {override_id}")
        by_id[override_id] = override

    if not by_id:
        raise ValueError("Alignment override collection is empty")

    parent_by_id: dict[str, str | None] = {}
    for override_id, override in by_id.items():
        supersedes = override.get("supersedes")
        if supersedes is not None and (
            not isinstance(supersedes, str) or not supersedes
        ):
            raise ValueError(f"Invalid supersedes ID: {override_id}")
        if supersedes is not None and supersedes not in by_id:
            raise ValueError(
                f"Alignment override supersedes missing ID: {override_id} -> {supersedes}"
            )
        parent_by_id[override_id] = supersedes

    for start in sorted(parent_by_id):
        visiting: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in visiting:
                raise ValueError(f"Alignment override supersedes cycle at {current}")
            visiting.add(current)
            current = parent_by_id[current]

    for override_id, override in by_id.items():
        current = resolve_override_current_input_digests(
            override,
            source_registry_sha256=source_registry_sha256,
            stage6_text_sha256=stage6_text_sha256,
            stage6_verse_sha256_by_target_token_id=(
                stage6_verse_sha256_by_target_token_id
            ),
            legacy_snapshot_sha256=legacy_snapshot_sha256,
            fingerprint_sha256=fingerprint_sha256,
            fingerprint_selected_original_layer_sha256=(
                fingerprint_selected_original_layer_sha256
            ),
            source_apparatus_sha256_by_original_token_id=(
                source_apparatus_sha256_by_original_token_id
            ),
        )
        if not override_is_current(override, current):
            raise ValueError(
                f"Alignment override input digests are stale or tampered: {override_id}"
            )
    superseded_ids = {
        supersedes for supersedes in parent_by_id.values() if supersedes is not None
    }
    return {
        override_id: by_id[override_id]
        for override_id in sorted(set(by_id) - superseded_ids)
    }


def validate_hyperedge(
    edge: Mapping[str, Any],
    *,
    valid_original_ids: set[str],
    valid_target_token_ids: set[str],
    original_ref_by_id: Mapping[str, str] | None = None,
    target_ref_by_id: Mapping[str, str] | None = None,
) -> None:
    """Validate a verse-local many-to-many/null alignment hyperedge."""

    originals = tuple(edge.get("original_token_ids", ()))
    targets = tuple(edge.get("target_token_ids", ()))
    relation = edge.get("relation")
    allowed = {
        "one_to_one",
        "one_to_many",
        "many_to_one",
        "many_to_many",
        "original_omitted",
        "translation_addition",
        "grouped_expression",
        "textual_alternative",
    }
    if relation not in allowed:
        raise ValueError("Unknown hyperedge relation")
    if len(set(originals)) != len(originals) or len(set(targets)) != len(targets):
        raise ValueError("Hyperedge contains duplicate token IDs")
    if any(value not in valid_original_ids for value in originals):
        raise ValueError("Hyperedge contains dangling original token ID")
    if any(value not in valid_target_token_ids for value in targets):
        raise ValueError("Hyperedge contains dangling Ukrainian token ID")
    if relation == "original_omitted":
        if not originals or targets:
            raise ValueError("Original omission requires original IDs and a null target")
    elif relation == "translation_addition":
        if originals or not targets:
            raise ValueError("Translation addition requires a null original and target IDs")
    elif not originals or not targets:
        raise ValueError("Non-null hyperedge requires both sides")
    cardinalities = {
        "one_to_one": (1, 1),
        "one_to_many": (1, None),
        "many_to_one": (None, 1),
        "many_to_many": (None, None),
    }
    if relation in cardinalities:
        original_expected, target_expected = cardinalities[relation]
        if original_expected is not None and len(originals) != original_expected:
            raise ValueError("Hyperedge original cardinality contradicts relation")
        if target_expected is not None and len(targets) != target_expected:
            raise ValueError("Hyperedge target cardinality contradicts relation")
        if relation in {"one_to_many", "many_to_many"} and len(targets) < 2:
            raise ValueError("Hyperedge target cardinality contradicts relation")
        if relation in {"many_to_one", "many_to_many"} and len(originals) < 2:
            raise ValueError("Hyperedge original cardinality contradicts relation")
    if not candidate_is_evidence_backed(edge):
        raise ValueError("Hyperedge has only prohibited positional/verse-bag evidence")
    if original_ref_by_id is not None or target_ref_by_id is not None:
        refs = {
            (original_ref_by_id or {}).get(value, "") for value in originals
        } | {
            (target_ref_by_id or {}).get(value, "") for value in targets
        }
        refs.discard("")
        if len(refs) > 1 or (edge.get("target_ref") and refs != {edge["target_ref"]}):
            raise ValueError("Hyperedge crosses a verse boundary")

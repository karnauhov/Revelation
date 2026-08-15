"""Deterministic candidate-only generators for Ukrainian stage 7.

This module intentionally does not make alignment decisions.  It emits raw,
verse-local evidence candidates that a separately calibrated hypergraph
resolver may consume only after the frozen gold contract is complete.

The implementation has no external model dependency.  Translation bridges
retain each complete manual hyperedge, legacy rows have zero vote and no
current original ID, transliteration scores are explicitly uncalibrated, and
local Ukrainian Strong descriptions are lexical context rather than proof.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from hashlib import sha256
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import sqlite3
import sys
import unicodedata
from typing import Any, Iterable, Iterator, Mapping, Sequence, TextIO

from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    comparison_form,
    exact_word_tokens,
    normalize_strong,
    stable_json,
)


CANDIDATE_CONTRACT_VERSION = "ukrainian-stage-7-candidate-only-v1"

BRIDGE_GENERATOR_ID = "bridge-full-group-surface-v1"
LEGACY_GENERATOR_ID = "legacy-zero-vote-v1"
TRANSLITERATION_GENERATOR_ID = "transliteration-named-entity-v1"
LEXICAL_GENERATOR_ID = "local-uk-strong-description-lexical-v1"

GENERATOR_ORDER = (
    BRIDGE_GENERATOR_ID,
    LEGACY_GENERATOR_ID,
    TRANSLITERATION_GENERATOR_ID,
    LEXICAL_GENERATOR_ID,
)

FORBIDDEN_ASSIGNMENT_METHODS = frozenset(
    {
        "nearest",
        "neighbor",
        "proportional",
        "position_only",
        "verse_bag",
        "majority_only",
        "frequency_only",
        "single_translation_proof",
    }
)

BOOKS = (
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth",
    "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh",
    "Esth", "Job", "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam",
    "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic",
    "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Mat", "Mark", "Luke",
    "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
    "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas",
    "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
)
NUMBER_BOOK = {index: book for index, book in enumerate(BOOKS, 1)}
BOOK_NUMBER = {book: index for index, book in enumerate(BOOKS, 1)}

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_TAGNT_PROPER_RE = re.compile(r"^N-.*-P$")
_LETTERS_RE = re.compile(r"[^a-z]+")

# Candidate filtering only.  These words remain exact tokens in the immutable
# inventory; this set merely prevents dictionary prose from producing a large
# number of obviously non-lexical Strong candidates.
_UKRAINIAN_FUNCTION_WORDS = frozenset(
    {
        "аби", "або", "але", "ані", "без", "би", "був", "була", "були",
        "було", "бути", "вам", "вами", "вас", "весь", "від", "він", "вона",
        "вони", "воно", "для", "його", "йому", "коли", "мене", "мені", "між",
        "над", "нам", "нами", "нас", "наш", "нехай", "ніби", "перед", "при",
        "про", "себе", "собі", "таки", "тебе", "тебе", "тим", "тими", "тих",
        "той", "тому", "хай", "хто", "через", "щоб", "який", "якщо",
    }
)

_UKRAINIAN_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d",
    "е": "e", "є": "ie", "ж": "zh", "з": "z", "и": "y", "і": "i",
    "ї": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh",
    "щ": "shch", "ь": "", "ю": "iu", "я": "ia", "ы": "y", "э": "e",
    "ё": "io", "ъ": "",
}


@dataclass(frozen=True, slots=True)
class TargetToken:
    token_id: str
    verse_key: str
    target_ref: str
    order: int
    comparison: str
    surface: str
    start_scalar: int
    end_scalar: int
    start_byte: int
    end_byte: int
    plain_text_sha256: str


@dataclass(frozen=True, slots=True)
class OriginalToken:
    token_id: str
    target_ref: str | None
    order: int
    source_family: str
    reading_status: str
    morphology: str
    transliteration: str
    strong_classic: tuple[str, ...]

    @property
    def is_resolved_primary(self) -> bool:
        return (
            self.target_ref is not None
            and self.reading_status.startswith("primary_")
            and "unresolved" not in self.reading_status
        )


@dataclass(frozen=True, slots=True)
class BridgeTargetBundle:
    family: str
    scope: str
    path: Path
    source_id: str


@dataclass(slots=True)
class CandidateContext:
    target_by_id: dict[str, TargetToken]
    target_by_ref_comparison: dict[tuple[str, str], tuple[TargetToken, ...]]
    target_by_verse_order: dict[tuple[str, int], TargetToken]
    originals_by_id: dict[str, OriginalToken]
    proper_originals: tuple[OriginalToken, ...]
    greek_originals_by_ref: dict[str, tuple[OriginalToken, ...]]


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_rows(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = sha256()
    for row in rows:
        digest.update(stable_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _candidate_id(identity: Mapping[str, Any]) -> str:
    return "uk7cand:" + sha256(stable_json(identity).encode("utf-8")).hexdigest()


def _generator_code_sha256() -> str:
    return _sha256_file(Path(__file__))


def _runtime_record() -> dict[str, Any]:
    executable = Path(sys.executable).resolve()
    return {
        "implementation": "CPython standard library; single process",
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable_sha256": _sha256_file(executable),
        "hash_randomization_dependency": False,
        "thread_count": 1,
        "floating_point_rounding": "scores serialized to 12 decimal places",
    }


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")
            yield value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _decode_bridge_bcvwp(value: str) -> tuple[str, int, int, int]:
    code = value[1:] if value[:1] in {"o", "n"} else value
    if len(code) not in {11, 12} or not code.isdigit():
        raise ValueError(f"Invalid bridge BCVWP selector: {value}")
    book = NUMBER_BOOK.get(int(code[0:2]))
    chapter = int(code[2:5])
    verse = int(code[5:8])
    word = int(code[8:11])
    if book is None or chapter < 1 or verse < 0 or word < 1:
        raise ValueError(f"Invalid bridge BCVWP selector: {value}")
    return book, chapter, verse, word


def load_context(
    token_inventory_path: Path,
    original_universe_path: Path,
) -> CandidateContext:
    """Load compact current-token indexes used by all candidate generators."""

    target_by_id: dict[str, TargetToken] = {}
    target_by_ref_comparison_mutable: dict[tuple[str, str], list[TargetToken]] = defaultdict(list)
    target_by_verse_order: dict[tuple[str, int], TargetToken] = {}
    for row in _read_jsonl(token_inventory_path):
        token = TargetToken(
            token_id=str(row["token_id"]),
            verse_key=str(row["verse_key"]),
            target_ref=str(row["target_ref"]),
            order=int(row["order"]),
            comparison=str(row["comparison"]),
            surface=str(row["surface"]),
            start_scalar=int(row["start_scalar"]),
            end_scalar=int(row["end_scalar"]),
            start_byte=int(row["start_byte"]),
            end_byte=int(row["end_byte"]),
            plain_text_sha256=str(row["plain_text_sha256"]),
        )
        if token.token_id in target_by_id:
            raise ValueError(f"Duplicate target token ID: {token.token_id}")
        target_by_id[token.token_id] = token
        target_by_verse_order[(token.verse_key, token.order)] = token
        if token.comparison:
            target_by_ref_comparison_mutable[(token.target_ref, token.comparison)].append(token)

    originals_by_id: dict[str, OriginalToken] = {}
    proper_originals: list[OriginalToken] = []
    greek_by_ref_mutable: dict[str, list[OriginalToken]] = defaultdict(list)
    for row in _read_jsonl(original_universe_path):
        token = OriginalToken(
            token_id=str(row["original_token_id"]),
            target_ref=None if row.get("target_ref") is None else str(row["target_ref"]),
            order=int(row["order"]),
            source_family=str(row["source_family"]),
            reading_status=str(row["reading_status"]),
            morphology=str(row.get("morphology_raw") or ""),
            transliteration=str(row.get("transliteration_raw") or ""),
            strong_classic=tuple(sorted({str(value) for value in row.get("strong_classic", ())})),
        )
        if token.token_id in originals_by_id:
            raise ValueError(f"Duplicate original token ID: {token.token_id}")
        originals_by_id[token.token_id] = token
        if token.is_resolved_primary and _is_proper_name(token):
            proper_originals.append(token)
        if (
            token.is_resolved_primary
            and token.source_family == "TAGNT"
            and any(value.startswith("G") for value in token.strong_classic)
        ):
            greek_by_ref_mutable[token.target_ref].append(token)  # type: ignore[index]

    target_by_ref_comparison = {
        key: tuple(sorted(value, key=lambda item: (item.order, item.token_id)))
        for key, value in target_by_ref_comparison_mutable.items()
    }
    greek_originals_by_ref = {
        key: tuple(sorted(value, key=lambda item: (item.order, item.token_id)))
        for key, value in greek_by_ref_mutable.items()
    }
    return CandidateContext(
        target_by_id=target_by_id,
        target_by_ref_comparison=target_by_ref_comparison,
        target_by_verse_order=target_by_verse_order,
        originals_by_id=originals_by_id,
        proper_originals=tuple(proper_originals),
        greek_originals_by_ref=greek_originals_by_ref,
    )


def _is_proper_name(token: OriginalToken) -> bool:
    if token.source_family == "TAHOT":
        return "Np" in token.morphology
    if token.source_family == "TAGNT":
        return _TAGNT_PROPER_RE.fullmatch(token.morphology) is not None
    return False


def _ordered_original_ids(
    values: Iterable[str],
    originals: Mapping[str, OriginalToken],
) -> tuple[str, ...]:
    return tuple(sorted(set(values), key=lambda value: (originals[value].order, value)))


def _ordered_target_ids(
    values: Iterable[str],
    targets: Mapping[str, TargetToken],
) -> tuple[str, ...]:
    return tuple(sorted(set(values), key=lambda value: (targets[value].order, value)))


def _relation(original_count: int, target_count: int) -> str:
    if original_count == 1 and target_count == 1:
        return "one_to_one"
    if original_count == 1 and target_count > 1:
        return "one_to_many"
    if original_count > 1 and target_count == 1:
        return "many_to_one"
    if original_count > 1 and target_count > 1:
        return "many_to_many"
    raise ValueError("Candidate-only lexical edges require both sides")


def _strongs_for_originals(
    original_ids: Sequence[str],
    originals: Mapping[str, OriginalToken],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                strong
                for token_id in original_ids
                for strong in originals[token_id].strong_classic
            }
        )
    )


def _base_candidate(
    *,
    generator_id: str,
    target_ref: str,
    original_ids: Sequence[str],
    target_ids: Sequence[str],
    strongs: Sequence[str],
    relation: str,
    evidence_channels: Sequence[str],
    evidence: Sequence[Mapping[str, Any]],
    dependency_family_ids: Sequence[str],
    identity_extra: Mapping[str, Any],
    score: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    identity = {
        "generator_id": generator_id,
        "target_ref": target_ref,
        "original_token_ids": list(original_ids),
        "target_token_ids": list(target_ids),
        "identity_extra": identity_extra,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "candidate_contract_version": CANDIDATE_CONTRACT_VERSION,
        "candidate_id": _candidate_id(identity),
        "generator_id": generator_id,
        "target_ref": target_ref,
        "original_token_ids": list(original_ids),
        "target_token_ids": list(target_ids),
        "strong_classic": list(strongs),
        "relation": relation,
        "evidence_channels": sorted(set(evidence_channels)),
        "evidence": list(evidence),
        "dependency_family_ids": sorted(set(dependency_family_ids)),
        "generator_score": score,
        "candidate_only": True,
        "calibrated": False,
        "auto_acceptance": False,
        "resolver_eligible": False,
        "decision_status": "candidate_only_unreviewed",
        "proof_limitations": [
            "raw candidate is not alignment proof",
            "A_auto requires frozen gold calibration and independent non-conflicting evidence",
        ],
        "prohibited_assignment_methods_used": [],
    }


def _attach_target_spans(
    row: dict[str, Any],
    *,
    context: CandidateContext,
) -> dict[str, Any]:
    row["target_spans"] = [
        {
            "target_token_id": token_id,
            "start_scalar": context.target_by_id[token_id].start_scalar,
            "end_scalar": context.target_by_id[token_id].end_scalar,
            "start_byte": context.target_by_id[token_id].start_byte,
            "end_byte": context.target_by_id[token_id].end_byte,
            "surface_sha256": sha256(
                context.target_by_id[token_id].surface.encode("utf-8")
            ).hexdigest(),
            "comparison_sha256": sha256(
                context.target_by_id[token_id].comparison.encode("utf-8")
            ).hexdigest(),
        }
        for token_id in row["target_token_ids"]
    ]
    return row


def validate_candidate(
    row: Mapping[str, Any],
    *,
    context: CandidateContext,
) -> None:
    """Fail closed if a raw candidate could be mistaken for an accepted edge."""

    if row.get("candidate_only") is not True:
        raise ValueError("Candidate must be explicitly candidate-only")
    if re.fullmatch(r"uk7cand:[0-9a-f]{64}", str(row.get("candidate_id", ""))) is None:
        raise ValueError("Candidate ID is not a stable SHA-256 identity")
    if row.get("auto_acceptance") is not False or row.get("resolver_eligible") is not False:
        raise ValueError("Candidate-only generators cannot enable resolver acceptance")
    if row.get("calibrated") is not False:
        raise ValueError("Candidate-only score cannot be marked calibrated")
    prohibited = set(row.get("prohibited_assignment_methods_used", ()))
    if prohibited:
        raise ValueError(f"Candidate uses prohibited methods: {sorted(prohibited)}")
    if set(row.get("evidence_channels", ())) & FORBIDDEN_ASSIGNMENT_METHODS:
        raise ValueError("Forbidden assignment method appears as an evidence channel")
    if not row.get("evidence_channels") or not row.get("evidence"):
        raise ValueError("Candidate lacks concrete evidence")
    score = row.get("generator_score")
    if score is not None and score.get("calibrated") is not False:
        raise ValueError("Generator score must remain explicitly uncalibrated")

    generator_id = str(row.get("generator_id"))
    original_ids = tuple(str(value) for value in row.get("original_token_ids", ()))
    target_ids = tuple(str(value) for value in row.get("target_token_ids", ()))
    if len(original_ids) != len(set(original_ids)) or len(target_ids) != len(set(target_ids)):
        raise ValueError("Candidate contains duplicate stable token IDs")
    if any(value not in context.target_by_id for value in target_ids):
        raise ValueError("Candidate contains dangling OH token ID")
    if any(context.target_by_id[value].target_ref != row.get("target_ref") for value in target_ids):
        raise ValueError("Candidate crosses an OH verse boundary")
    spans = row.get("target_spans")
    if (
        not isinstance(spans, list)
        or [item.get("target_token_id") for item in spans] != list(target_ids)
    ):
        raise ValueError("Candidate target spans do not match stable target IDs")
    for span in spans:
        token = context.target_by_id[str(span["target_token_id"])]
        expected = (
            token.start_scalar,
            token.end_scalar,
            token.start_byte,
            token.end_byte,
        )
        actual = (
            span.get("start_scalar"),
            span.get("end_scalar"),
            span.get("start_byte"),
            span.get("end_byte"),
        )
        if actual != expected:
            raise ValueError("Candidate target span offsets are stale")
        if span.get("surface_sha256") != sha256(token.surface.encode("utf-8")).hexdigest():
            raise ValueError("Candidate target surface digest is stale")
        if span.get("comparison_sha256") != sha256(
            token.comparison.encode("utf-8")
        ).hexdigest():
            raise ValueError("Candidate target comparison digest is stale")

    strongs = tuple(str(value) for value in row.get("strong_classic", ()))
    if len(strongs) != len(set(strongs)):
        raise ValueError("Candidate contains duplicate Strong numbers")
    if any(normalize_strong(value)["classic"] != value for value in strongs):
        raise ValueError("Candidate contains a non-classic Strong value")

    if generator_id == LEGACY_GENERATOR_ID:
        if original_ids:
            raise ValueError("Legacy candidate must not claim a current original token")
        if row.get("strong_classic") and not target_ids:
            raise ValueError("Legacy Strong feature requires a current OH token")
        return

    if not original_ids or not target_ids:
        raise ValueError("Non-legacy lexical candidate requires both token sides")
    if any(value not in context.originals_by_id for value in original_ids):
        raise ValueError("Candidate contains dangling original token ID")
    originals = [context.originals_by_id[value] for value in original_ids]
    if any(not value.is_resolved_primary for value in originals):
        raise ValueError("Candidate uses unresolved/alternative original token")
    if any(value.target_ref != row.get("target_ref") for value in originals):
        raise ValueError("Candidate crosses an original verse boundary")
    if row.get("relation") != _relation(len(original_ids), len(target_ids)):
        raise ValueError("Candidate relation does not match edge cardinality")
    expected_strongs = list(_strongs_for_originals(original_ids, context.originals_by_id))
    if list(row.get("strong_classic", ())) != expected_strongs:
        raise ValueError("Candidate Strong set is not derived from current original IDs")


def validate_generator_registry(registry: Mapping[str, Any]) -> None:
    if registry.get("candidate_contract_version") != CANDIDATE_CONTRACT_VERSION:
        raise ValueError("Wrong candidate registry contract")
    generators = registry.get("generators")
    if not isinstance(generators, list):
        raise ValueError("Generator registry requires a generator list")
    ids = [str(item.get("generator_id")) for item in generators]
    if ids != list(GENERATOR_ORDER) or len(ids) != len(set(ids)):
        raise ValueError("Generator registry order/identity is not canonical")
    for item in generators:
        if item.get("status") != "candidate_only_no_auto_acceptance":
            raise ValueError("Generator registry must prohibit auto acceptance")
        if item.get("license") != "first-party project code":
            raise ValueError("Generator implementation license must be explicit")
        digest = str(item.get("implementation_sha256", ""))
        if _SHA256_RE.fullmatch(digest) is None:
            raise ValueError("Generator implementation SHA-256 is invalid")
        if item.get("external_model") is not None:
            raise ValueError("This first-party module cannot claim an external model")
        if item.get("calibrated") is not False or item.get("auto_acceptance") is not False:
            raise ValueError("Generator registry incorrectly enables decisions")
        contracts = item.get("source_contracts")
        if not isinstance(contracts, list) or not contracts:
            raise ValueError("Generator registry lacks source/license contracts")
        for contract in contracts:
            if (
                not contract.get("source_id")
                or not contract.get("version")
                or not contract.get("license")
            ):
                raise ValueError("Generator source contract is incomplete")
            if _SHA256_RE.fullmatch(str(contract.get("sha256", ""))) is None:
                raise ValueError("Generator source contract SHA-256 is invalid")
    for digest in registry.get("input_sha256", {}).values():
        if _SHA256_RE.fullmatch(str(digest)) is None:
            raise ValueError("Generator registry input SHA-256 is invalid")
    runtime_digest = str(registry.get("runtime", {}).get("executable_sha256", ""))
    if _SHA256_RE.fullmatch(runtime_digest) is None:
        raise ValueError("Generator registry runtime SHA-256 is invalid")


def _load_bridge_targets(
    bundles: Sequence[BridgeTargetBundle],
) -> dict[tuple[str, str, str], tuple[str, str, str, str]]:
    result: dict[tuple[str, str, str], tuple[str, str, str, str]] = {}
    for bundle in bundles:
        with bundle.path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            id_field = "id" if "id" in (reader.fieldnames or ()) else "identifier"
            for row in reader:
                identifier = row[id_field]
                try:
                    book, chapter, verse, _word = _decode_bridge_bcvwp(identifier)
                except ValueError:
                    continue
                result[(bundle.family, bundle.scope, identifier)] = (
                    f"{book}.{chapter}.{verse}",
                    comparison_form(row.get("text", "")),
                    sha256(str(row.get("text", "")).encode("utf-8")).hexdigest(),
                    bundle.source_id,
                )
    return result


def generate_bridge_surface_candidates(
    *,
    context: CandidateContext,
    bridge_alignment_path: Path,
    target_bundles: Sequence[BridgeTargetBundle],
) -> tuple[Iterator[dict[str, Any]], Counter[str]]:
    """Generate full-group manual-bridge surface candidates without order priors."""

    bridge_targets = _load_bridge_targets(target_bundles)
    counters: Counter[str] = Counter()

    def rows() -> Iterator[dict[str, Any]]:
        candidates_by_id: dict[str, dict[str, Any]] = {}
        for bridge in _read_jsonl(bridge_alignment_path):
            counters["processed_bridge_records"] += 1
            if bridge.get("status") != "accepted_manual_bridge":
                counters["skipped_non_full_manual_bridge"] += 1
                continue
            if bridge.get("explicit_null_source") or bridge.get("explicit_null_target"):
                counters["skipped_null_bridge_member"] += 1
                continue
            raw_original_ids = [str(value) for value in bridge.get("original_token_ids", ())]
            if (
                not raw_original_ids
                or len(raw_original_ids) != len(set(raw_original_ids))
                or any(value not in context.originals_by_id for value in raw_original_ids)
            ):
                counters["skipped_dangling_original"] += 1
                continue
            originals = [context.originals_by_id[value] for value in raw_original_ids]
            refs = {value.target_ref for value in originals if value.target_ref is not None}
            if len(refs) != 1 or any(not value.is_resolved_primary for value in originals):
                counters["skipped_original_ref_or_textual_status"] += 1
                continue
            target_ref = next(iter(refs))
            original_ids = _ordered_original_ids(raw_original_ids, context.originals_by_id)

            family = str(bridge["bridge_family"])
            scope = str(bridge["scope"])
            raw_bridge_target_ids = [str(value) for value in bridge.get("target_token_ids", ())]
            if not raw_bridge_target_ids or len(raw_bridge_target_ids) != len(set(raw_bridge_target_ids)):
                counters["skipped_empty_or_duplicate_bridge_target"] += 1
                continue
            bridge_forms: list[str] = []
            bridge_surface_hashes: list[str] = []
            bridge_source_ids: list[str] = []
            invalid_target = False
            for token_id in raw_bridge_target_ids:
                target = bridge_targets.get((family, scope, token_id))
                if target is None or target[0] != target_ref or not target[1]:
                    invalid_target = True
                    break
                bridge_forms.append(target[1])
                bridge_surface_hashes.append(target[2])
                bridge_source_ids.append(target[3])
            if invalid_target:
                counters["skipped_bridge_target_ref_or_surface"] += 1
                continue

            required = Counter(bridge_forms)
            choice_groups: list[list[tuple[TargetToken, ...]]] = []
            no_full_match = False
            for form, required_count in sorted(required.items()):
                available = context.target_by_ref_comparison.get((target_ref, form), ())
                if len(available) < required_count:
                    no_full_match = True
                    break
                choice_groups.append(list(itertools.combinations(available, required_count)))
            if no_full_match:
                counters["skipped_no_full_surface_multiset"] += 1
                continue

            counters["full_match_bridge_records"] += 1
            alternative_count = math.prod(len(group) for group in choice_groups)
            alternative_group_id = "uk7bridgealt:" + sha256(
                str(bridge["bridge_id"]).encode("utf-8")
            ).hexdigest()
            for selection in itertools.product(*choice_groups):
                counters["raw_candidate_evidence_occurrences"] += 1
                target_ids = _ordered_target_ids(
                    (token.token_id for group in selection for token in group),
                    context.target_by_id,
                )
                row = _base_candidate(
                    generator_id=BRIDGE_GENERATOR_ID,
                    target_ref=target_ref,
                    original_ids=original_ids,
                    target_ids=target_ids,
                    strongs=_strongs_for_originals(original_ids, context.originals_by_id),
                    relation=_relation(len(original_ids), len(target_ids)),
                    evidence_channels=(
                        f"manual_bridge_{family.lower()}",
                        "surface_identity",
                    ),
                    evidence=(
                        {
                            "kind": "manual_original_to_translation_hyperedge_records",
                            "bridge_family": family,
                            "records": [
                                {
                                    "bridge_id": bridge["bridge_id"],
                                    "bridge_target_token_ids": raw_bridge_target_ids,
                                    "bridge_surface_sha256": bridge_surface_hashes,
                                    "source_ids": sorted(set(bridge_source_ids)),
                                }
                            ],
                        },
                        {
                            "kind": "exact_full_group_translation_to_oh_surface_multiset",
                            "comparison_forms_sha256": sha256(
                                stable_json(sorted(bridge_forms)).encode("utf-8")
                            ).hexdigest(),
                            "positional_tie_break": False,
                        },
                    ),
                    dependency_family_ids=(f"clear-{family.lower()}-manual",),
                    identity_extra={
                        "bridge_family": family,
                        "scope": scope,
                    },
                    score={
                        "kind": "exact_surface_group_identity",
                        "raw": 1.0,
                        "calibrated": False,
                    },
                )
                _attach_target_spans(row, context=context)
                row["bridge_family"] = family
                row["scope"] = scope
                row["manual_record_count"] = 1
                row["alternative_groups"] = [
                    {
                        "alternative_group_id": alternative_group_id,
                        "alternative_count": alternative_count,
                        "alternative_rank": None,
                        "bridge_id": bridge["bridge_id"],
                    }
                ]
                row["proof_limitations"].append(
                    "one translation bridge is never sufficient proof for A_auto"
                )
                existing = candidates_by_id.get(row["candidate_id"])
                if existing is not None:
                    existing["evidence"][0]["records"].extend(
                        row["evidence"][0]["records"]
                    )
                    existing["alternative_groups"].extend(row["alternative_groups"])
                    existing["manual_record_count"] += 1
                    counters["coalesced_duplicate_evidence_occurrences"] += 1
                    continue
                candidates_by_id[row["candidate_id"]] = row

        for row in candidates_by_id.values():
            row["evidence"][0]["records"].sort(key=lambda item: item["bridge_id"])
            row["alternative_groups"].sort(
                key=lambda item: (item["alternative_group_id"], item["bridge_id"])
            )
            validate_candidate(row, context=context)
            counters[f"emitted_{row['bridge_family']}_{row['scope']}"] += 1
            counters["emitted_candidates"] += 1
            yield row

    return rows(), counters


def generate_legacy_candidates(
    *,
    context: CandidateContext,
    legacy_alignment_path: Path,
) -> tuple[Iterator[dict[str, Any]], Counter[str]]:
    counters: Counter[str] = Counter()

    def rows() -> Iterator[dict[str, Any]]:
        for verse in _read_jsonl(legacy_alignment_path):
            counters["processed_verses"] += 1
            verse_key = str(verse["verse_key"])
            target_ref = str(verse["target_ref"])
            for alignment_index, alignment in enumerate(verse.get("alignments", ()), 1):
                counters["processed_occurrences"] += 1
                target = context.target_by_verse_order.get(
                    (verse_key, int(alignment["target_token_order"]))
                )
                if (
                    target is None
                    or target.target_ref != target_ref
                    or target.plain_text_sha256 != verse.get("plain_text_sha256")
                ):
                    counters["skipped_stale_or_dangling_target"] += 1
                    continue
                normalized = normalize_strong(str(alignment.get("strong", "")))
                classic = normalized["classic"]
                if classic is None:
                    counters["skipped_nonclassic_strong"] += 1
                    continue
                legacy_source_token_id = str(
                    alignment.get("evidence", {}).get("source_token_id", "")
                )
                row = _base_candidate(
                    generator_id=LEGACY_GENERATOR_ID,
                    target_ref=target_ref,
                    original_ids=(),
                    target_ids=(target.token_id,),
                    strongs=(classic,),
                    relation="legacy_unproven_feature",
                    evidence_channels=("legacy_zero_vote",),
                    evidence=(
                        {
                            "kind": "rejected_legacy_occurrence",
                            "legacy_source_token_id": legacy_source_token_id,
                            "legacy_alignment_method": alignment.get("evidence", {}).get(
                                "alignment_method"
                            ),
                            "legacy_confidence_label": alignment.get("confidence"),
                            "legacy_target_token_order": alignment["target_token_order"],
                            "current_plain_text_sha256": target.plain_text_sha256,
                            "target_remap_rule": "exact verse digest plus deterministic tokenizer order; no original assignment inferred",
                        },
                    ),
                    dependency_family_ids=("rejected-stage7-legacy",),
                    identity_extra={
                        "verse_key": verse_key,
                        "alignment_index": alignment_index,
                        "legacy_source_token_id": legacy_source_token_id,
                        "strong": classic,
                    },
                    score={
                        "kind": "rejected_legacy_zero_vote",
                        "raw": 0.0,
                        "calibrated": False,
                    },
                )
                _attach_target_spans(row, context=context)
                row["vote_weight"] = 0
                row["legacy_current_original_crosswalk"] = "forbidden_verse_bag_not_run"
                row["proof_limitations"].append(
                    "legacy position/global-corpus assignment is rejected and cannot identify a current original token"
                )
                validate_candidate(row, context=context)
                counters["emitted_candidates"] += 1
                yield row

    return rows(), counters


def _latin_letters(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    without_marks = "".join(
        char for char in decomposed if not unicodedata.category(char).startswith("M")
    )
    return _LETTERS_RE.sub("", without_marks)


def _phonetic_key(value: str) -> str:
    result = _latin_letters(value)
    for source, target in (
        ("shch", "sc"),
        ("sch", "sc"),
        ("tch", "c"),
        ("ch", "h"),
        ("kh", "h"),
        ("ph", "f"),
        ("th", "t"),
        ("zh", "z"),
        ("sh", "s"),
        ("ts", "c"),
        ("ou", "u"),
        ("oo", "u"),
        ("w", "v"),
        ("y", "i"),
        ("j", "i"),
    ):
        result = result.replace(source, target)
    return result


def ukrainian_transliteration(value: str) -> str:
    return "".join(_UKRAINIAN_LATIN.get(char, char) for char in value.casefold())


def _edit_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return 1.0 - previous[-1] / max(len(left), len(right))


def generate_transliteration_candidates(
    *,
    context: CandidateContext,
    minimum_score: float = 0.60,
    minimum_length: int = 3,
) -> tuple[Iterator[dict[str, Any]], Counter[str]]:
    if not (0.0 <= minimum_score <= 1.0) or minimum_length < 1:
        raise ValueError("Invalid transliteration candidate configuration")
    targets_by_ref: dict[str, list[TargetToken]] = defaultdict(list)
    for target in context.target_by_id.values():
        if target.comparison:
            targets_by_ref[target.target_ref].append(target)
    for targets in targets_by_ref.values():
        targets.sort(key=lambda item: (item.order, item.token_id))
    counters: Counter[str] = Counter()

    def rows() -> Iterator[dict[str, Any]]:
        for original in context.proper_originals:
            counters["processed_proper_originals"] += 1
            source_key = _phonetic_key(original.transliteration)
            if len(source_key) < minimum_length or not original.strong_classic:
                counters["skipped_source_key_or_strong"] += 1
                continue
            for target in targets_by_ref.get(original.target_ref or "", ()):
                counters["evaluated_verse_local_pairs"] += 1
                target_key = _phonetic_key(ukrainian_transliteration(target.comparison))
                if len(target_key) < minimum_length:
                    continue
                score = _edit_similarity(source_key, target_key)
                if score < minimum_score:
                    continue
                rounded_score = round(score, 12)
                row = _base_candidate(
                    generator_id=TRANSLITERATION_GENERATOR_ID,
                    target_ref=original.target_ref or "",
                    original_ids=(original.token_id,),
                    target_ids=(target.token_id,),
                    strongs=original.strong_classic,
                    relation="one_to_one",
                    evidence_channels=("morphology", "transliteration_named_entity"),
                    evidence=(
                        {
                            "kind": "original_proper_name_morphology",
                            "source_family": original.source_family,
                            "morphology_raw": original.morphology,
                        },
                        {
                            "kind": "direct_oh_surface_phonetic_comparison",
                            "original_transliteration_key": source_key,
                            "oh_transliteration_key": target_key,
                            "oh_surface_sha256": sha256(
                                target.surface.encode("utf-8")
                            ).hexdigest(),
                            "minimum_score": minimum_score,
                            "minimum_length": minimum_length,
                            "position_feature_used": False,
                        },
                    ),
                    dependency_family_ids=(
                        f"{original.source_family.lower()}-original-apparatus",
                        "first-party-transliteration-rules",
                    ),
                    identity_extra={
                        "original_key": source_key,
                        "target_key": target_key,
                    },
                    score={
                        "kind": "uncalibrated_normalized_edit_similarity",
                        "raw": rounded_score,
                        "calibrated": False,
                    },
                )
                _attach_target_spans(row, context=context)
                validate_candidate(row, context=context)
                counters[f"emitted_{original.source_family}"] += 1
                counters["emitted_candidates"] += 1
                yield row

    return rows(), counters


def load_ukrainian_greek_description_terms(
    database_path: Path,
) -> tuple[dict[str, frozenset[str]], dict[str, Any]]:
    """Read owner-local lexical context through a read-only SQLite connection."""

    connection = sqlite3.connect(
        f"file:{database_path.resolve().as_posix()}?mode=ro", uri=True
    )
    try:
        connection.execute("PRAGMA query_only=ON")
        metadata = dict(connection.execute("SELECT key,value FROM db_metadata"))
        rows = connection.execute("SELECT id,desc FROM greek_descs ORDER BY id")
        terms: dict[str, frozenset[str]] = {}
        count = 0
        for strong_number, description in rows:
            count += 1
            values = {
                token.comparison
                for token in exact_word_tokens(str(description or ""))
                if len(token.comparison) >= 3
                and token.comparison not in _UKRAINIAN_FUNCTION_WORDS
            }
            terms[f"G{int(strong_number)}"] = frozenset(sorted(values))
    finally:
        connection.close()
    return terms, {
        "database_sha256": _sha256_file(database_path),
        "description_count": count,
        "metadata": dict(sorted(metadata.items())),
        "read_mode": "SQLite URI mode=ro plus PRAGMA query_only=ON",
    }


def generate_lexical_morphological_candidates(
    *,
    context: CandidateContext,
    description_terms: Mapping[str, frozenset[str]],
    lexical_source_id: str,
    lexical_source_sha256: str,
) -> tuple[Iterator[dict[str, Any]], Counter[str]]:
    if _SHA256_RE.fullmatch(lexical_source_sha256) is None:
        raise ValueError("Lexical source SHA-256 is invalid")
    counters: Counter[str] = Counter()

    def rows() -> Iterator[dict[str, Any]]:
        for target in sorted(
            context.target_by_id.values(),
            key=lambda item: (
                BOOK_NUMBER[item.target_ref.split(".", 1)[0]],
                item.target_ref,
                item.order,
                item.token_id,
            ),
        ):
            counters["processed_oh_tokens"] += 1
            form = target.comparison
            if (
                not form
                or len(form) < 3
                or form in _UKRAINIAN_FUNCTION_WORDS
            ):
                counters["skipped_nonlexical_or_function_form"] += 1
                continue
            for original in context.greek_originals_by_ref.get(target.target_ref, ()):
                matched_strongs = tuple(
                    strong
                    for strong in original.strong_classic
                    if form in description_terms.get(strong, frozenset())
                )
                if not matched_strongs:
                    continue
                row = _base_candidate(
                    generator_id=LEXICAL_GENERATOR_ID,
                    target_ref=target.target_ref,
                    original_ids=(original.token_id,),
                    target_ids=(target.token_id,),
                    strongs=original.strong_classic,
                    relation="one_to_one",
                    evidence_channels=("lexical_morphological", "surface_identity"),
                    evidence=(
                        {
                            "kind": "strong_indexed_ukrainian_description_term",
                            "source_id": lexical_source_id,
                            "source_sha256": lexical_source_sha256,
                            "matched_strong": list(matched_strongs),
                            "original_morphology_raw": original.morphology,
                            "comparison_form_sha256": sha256(
                                form.encode("utf-8")
                            ).hexdigest(),
                        },
                        {
                            "kind": "direct_exact_oh_token_evidence",
                            "oh_token_id": target.token_id,
                            "oh_surface_sha256": sha256(
                                target.surface.encode("utf-8")
                            ).hexdigest(),
                            "position_feature_used": False,
                        },
                    ),
                    dependency_family_ids=(
                        "owner-local-strong-lexical-context",
                        "tagnt-original-apparatus",
                    ),
                    identity_extra={
                        "lexical_source_id": lexical_source_id,
                        "matched_strongs": matched_strongs,
                    },
                    score={
                        "kind": "uncalibrated_exact_description_term_match",
                        "raw": 1.0,
                        "calibrated": False,
                    },
                )
                _attach_target_spans(row, context=context)
                row["independent_vote"] = False
                row["proof_limitations"].append(
                    "owner-local description provenance is lexical context and has zero independent vote"
                )
                validate_candidate(row, context=context)
                counters["emitted_candidates"] += 1
                yield row

    return rows(), counters


def build_generator_registry(
    *,
    input_sha256: Mapping[str, str],
    source_contracts: Mapping[str, Mapping[str, Any]],
    configurations: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    code_sha = _generator_code_sha256()
    configs = configurations or {}
    source_ids = {
        BRIDGE_GENERATOR_ID: [
            "clear_russyn_ot", "clear_russyn_nt", "clear_ylt_ot",
            "clear_ylt_nt_v010_transfer", "step_tahot", "step_tagnt",
        ],
        LEGACY_GENERATOR_ID: ["ukrainian_stage_7_rejected_legacy_experiment"],
        TRANSLITERATION_GENERATOR_ID: ["step_tahot", "step_tagnt", "stage6_synthesized_text"],
        LEXICAL_GENERATOR_ID: ["local_revelation_uk_greek_descs", "step_tagnt", "stage6_synthesized_text"],
    }
    descriptions = {
        BRIDGE_GENERATOR_ID: "complete manual bridge group plus exact OH comparison multiset; all ties retained",
        LEGACY_GENERATOR_ID: "rejected occurrence feature remapped only to a current OH token; no current original ID",
        TRANSLITERATION_GENERATOR_ID: "proper-name morphology plus direct OH phonetic comparison",
        LEXICAL_GENERATOR_ID: "Strong-indexed Ukrainian description term plus direct exact OH token evidence",
    }
    generators: list[dict[str, Any]] = []
    for generator_id in GENERATOR_ORDER:
        contracts = [
            source_contracts[source_id]
            for source_id in source_ids[generator_id]
            if source_id in source_contracts
        ]
        generators.append(
            {
                "generator_id": generator_id,
                "version": generator_id,
                "status": "candidate_only_no_auto_acceptance",
                "description": descriptions[generator_id],
                "implementation": "scripts/bible_module/ukrainian_stage_7_candidates.py",
                "implementation_sha256": code_sha,
                "license": "first-party project code",
                "external_model": None,
                "source_contracts": contracts,
                "configuration": dict(configs.get(generator_id, {})),
                "calibrated": False,
                "auto_acceptance": False,
                "position_feature_used": False,
                "forbidden_as_sole_proof": sorted(FORBIDDEN_ASSIGNMENT_METHODS),
            }
        )
    registry = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "candidate_contract_version": CANDIDATE_CONTRACT_VERSION,
        "artifact": "candidate_generator_registry",
        "status": "candidate_only_no_external_models_no_auto_acceptance",
        "runtime": _runtime_record(),
        "input_sha256": dict(sorted(input_sha256.items())),
        "generators": generators,
        "processed_count": len(generators),
        "skipped_count": 0,
        "error_count": 0,
        "serialization": "UTF-8 JSON/JSONL; sorted keys; compact separators; LF; canonical generator then source order",
    }
    validate_generator_registry(registry)
    return registry


def source_contracts_from_registry(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, Any]] = {}
    for source in payload.get("sources", ()):
        source_id = str(source["source_id"])
        result[source_id] = {
            "source_id": source_id,
            "version": source.get("version"),
            "sha256": source.get("sha256"),
            "license": source.get("license"),
            "usage_status": source.get("usage_status"),
        }
    # The primary STEP families are represented by multiple locked source files.
    for family, prefix in (("step_tahot", "step_tahot_"), ("step_tagnt", "step_tagnt_")):
        members = [value for key, value in sorted(result.items()) if key.startswith(prefix)]
        if members:
            result[family] = {
                "source_id": family,
                "version": sorted({str(value["version"]) for value in members}),
                "sha256": sha256(stable_json(members).encode("utf-8")).hexdigest(),
                "license": "all registered family members carry CC BY 4.0",
                "usage_status": "consumed_primary_raw_reparse",
            }
    return result


def generate_candidate_only_artifacts(
    *,
    token_inventory_path: Path,
    original_universe_path: Path,
    bridge_alignment_path: Path,
    bridge_target_bundles: Sequence[BridgeTargetBundle],
    legacy_alignment_path: Path,
    ukrainian_greek_description_database: Path,
    source_registry_path: Path,
    output_dir: Path,
    transliteration_minimum_score: float = 0.60,
    transliteration_minimum_length: int = 3,
) -> dict[str, Any]:
    """Generate all first-party raw channels and a deterministic manifest."""

    if output_dir.exists():
        raise FileExistsError(
            f"First-party candidate output directory already exists: {output_dir}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    run_dir = output_dir.with_name(f".{output_dir.name}.tmp-{os.getpid()}")
    if run_dir.exists():
        raise FileExistsError(
            f"First-party candidate temporary output already exists: {run_dir}"
        )

    paths = {
        "ukrainian_token_inventory": token_inventory_path,
        "original_token_universe": original_universe_path,
        "parallel_bridge_alignment": bridge_alignment_path,
        "legacy_alignment": legacy_alignment_path,
        "ukrainian_greek_descriptions": ukrainian_greek_description_database,
        "source_registry": source_registry_path,
    }
    for bundle in bridge_target_bundles:
        paths[f"bridge_target_{bundle.family}_{bundle.scope}"] = bundle.path
    input_sha256 = {key: _sha256_file(value) for key, value in sorted(paths.items())}
    source_contracts = source_contracts_from_registry(source_registry_path)
    registry = build_generator_registry(
        input_sha256=input_sha256,
        source_contracts=source_contracts,
        configurations={
            BRIDGE_GENERATOR_ID: {
                "surface_comparison": "exact nonempty full-group multiset",
                "retain_all_ties": True,
                "partial_group_transfer": False,
            },
            LEGACY_GENERATOR_ID: {
                "vote_weight": 0,
                "current_original_crosswalk": "forbidden",
            },
            TRANSLITERATION_GENERATOR_ID: {
                "minimum_score": transliteration_minimum_score,
                "minimum_length": transliteration_minimum_length,
                "score_kind": "uncalibrated_normalized_edit_similarity",
            },
            LEXICAL_GENERATOR_ID: {
                "minimum_term_length": 3,
                "function_word_filter_version": "uk7-candidate-function-words-v1",
                "independent_vote": False,
            },
        },
    )

    context = load_context(token_inventory_path, original_universe_path)
    description_terms, description_metadata = load_ukrainian_greek_description_terms(
        ukrainian_greek_description_database
    )
    generators: list[tuple[str, Iterator[dict[str, Any]], Counter[str]]] = []
    bridge_rows, bridge_counts = generate_bridge_surface_candidates(
        context=context,
        bridge_alignment_path=bridge_alignment_path,
        target_bundles=bridge_target_bundles,
    )
    generators.append((BRIDGE_GENERATOR_ID, bridge_rows, bridge_counts))
    legacy_rows, legacy_counts = generate_legacy_candidates(
        context=context,
        legacy_alignment_path=legacy_alignment_path,
    )
    generators.append((LEGACY_GENERATOR_ID, legacy_rows, legacy_counts))
    transliteration_rows, transliteration_counts = generate_transliteration_candidates(
        context=context,
        minimum_score=transliteration_minimum_score,
        minimum_length=transliteration_minimum_length,
    )
    generators.append(
        (TRANSLITERATION_GENERATOR_ID, transliteration_rows, transliteration_counts)
    )
    lexical_rows, lexical_counts = generate_lexical_morphological_candidates(
        context=context,
        description_terms=description_terms,
        lexical_source_id="local_revelation_uk_greek_descs",
        lexical_source_sha256=input_sha256["ukrainian_greek_descriptions"],
    )
    generators.append((LEXICAL_GENERATOR_ID, lexical_rows, lexical_counts))

    run_dir.mkdir()
    output_path = run_dir / "alignment_candidates.first_party.jsonl"
    output_digest = sha256()
    total_count = 0
    channel_counts: dict[str, dict[str, int]] = {}
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for generator_id, rows, counters in generators:
            for row in rows:
                serialized = stable_json(row)
                handle.write(serialized + "\n")
                output_digest.update(serialized.encode("utf-8"))
                output_digest.update(b"\n")
                total_count += 1
            channel_counts[generator_id] = dict(sorted(counters.items()))

    registry_path = run_dir / "candidate_generator_registry.json"
    _write_json(registry_path, registry)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "candidate_contract_version": CANDIDATE_CONTRACT_VERSION,
        "artifact": "first_party_alignment_candidates",
        "status": "complete_candidate_only_no_auto_acceptance",
        "input_sha256": input_sha256,
        "output_sha256": {
            output_path.name: output_digest.hexdigest(),
            registry_path.name: _sha256_file(registry_path),
        },
        "counts": {
            "total_candidates": total_count,
            "channels": channel_counts,
            "target_tokens": len(context.target_by_id),
            "original_tokens": len(context.originals_by_id),
            "resolved_primary_proper_originals": len(context.proper_originals),
            "description_terms": sum(len(value) for value in description_terms.values()),
        },
        "description_source": description_metadata,
        "processed_count": total_count,
        "skipped_count": sum(
            value
            for counters in channel_counts.values()
            for key, value in counters.items()
            if key.startswith("skipped_")
        ),
        "error_count": 0,
        "calibration": "not_run",
        "automatic_acceptance": False,
        "serialization": "UTF-8 JSONL; sorted keys; compact separators; LF; canonical generator then source order",
    }
    _write_json(run_dir / "alignment_candidates.first_party.manifest.json", manifest)
    run_dir.replace(output_dir)
    return manifest


def _default_paths(root: Path) -> dict[str, Any]:
    work = root / "scripts/bible_module/work/ukrainian_stage_7_20260801"
    clear = root / "scripts/bible_module/source_cache/clear_bible_alignments"
    clear_v010 = root / "scripts/bible_module/source_cache/clear_bible_alignments_v0_1_0"
    return {
        "token_inventory": work / "ukrainian_token_inventory.jsonl",
        "original_universe": work / "fingerprint_selected_original_layer.jsonl",
        "bridges": work / "parallel_bridge_alignment.jsonl",
        "legacy": root / "scripts/bible_module/work/ukrainian_stage_7_experiment_20260801/strong_aligned_text.jsonl",
        "registry": root / "scripts/bible_module/reports/ukrainian_stage_7_20260801/source_registry.json",
        "output": work / "first_party_candidates",
        "bundles": (
            BridgeTargetBundle("RUSSYN", "OT", clear / "data/rus/targets/RUSSYN/ot_RUSSYN.tsv", "clear_russyn_ot"),
            BridgeTargetBundle("RUSSYN", "NT", clear / "data/rus/targets/RUSSYN/nt_RUSSYN.tsv", "clear_russyn_nt"),
            BridgeTargetBundle("YLT", "OT", clear / "data/eng/targets/YLT/ot_YLT.tsv", "clear_ylt_ot"),
            BridgeTargetBundle("YLT", "NT", clear_v010 / "data/targets/SBLGNT-YLT.tsv", "clear_ylt_nt_v010_transfer"),
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--uk-greek-db", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--transliteration-minimum-score", type=float, default=0.60)
    parser.add_argument("--transliteration-minimum-length", type=int, default=3)
    args = parser.parse_args(argv)
    defaults = _default_paths(args.root.resolve())
    output = args.output_dir or defaults["output"]
    manifest = generate_candidate_only_artifacts(
        token_inventory_path=defaults["token_inventory"],
        original_universe_path=defaults["original_universe"],
        bridge_alignment_path=defaults["bridges"],
        bridge_target_bundles=defaults["bundles"],
        legacy_alignment_path=defaults["legacy"],
        ukrainian_greek_description_database=args.uk_greek_db,
        source_registry_path=defaults["registry"],
        output_dir=output,
        transliteration_minimum_score=args.transliteration_minimum_score,
        transliteration_minimum_length=args.transliteration_minimum_length,
    )
    print(stable_json(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

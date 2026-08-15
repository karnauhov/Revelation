"""Author-footnote evidence channel for Ukrainian Strong stage 7.

The printed notes in the exact OH1988 edition are valuable first-party
evidence about source-language forms, grammar, lexical meaning and textual
variants.  They are not verse text and must never be fed into an aligner as
additional target tokens.  This module inventories every verse and heading
footnote, records exact anchors and conservatively cross-checks explicit
transliterations against the already fingerprint-selected original layer.

Every emitted row is corroboration/manual-review evidence only.  It has zero
automatic vote and cannot create a Strong assignment by itself.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Iterable, Iterator, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    sha256_text,
    stable_json,
)


AUTHOR_COMMENT_CONTRACT_VERSION = "ukrainian-stage-7-author-comment-evidence-v1"
OUTPUT_NAME = "author_comment_evidence.jsonl"

_LANGUAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("hebrew", re.compile(r"(?:гебрей|єврей|еврей|hebrew)", re.IGNORECASE)),
    ("greek", re.compile(r"(?:грецьк|грец|greek)", re.IGNORECASE)),
    ("aramaic", re.compile(r"(?:арамей|арамейськ|aramaic)", re.IGNORECASE)),
    ("syriac", re.compile(r"(?:сирійськ|сирийск|syriac)", re.IGNORECASE)),
    ("latin", re.compile(r"(?:латин|latin)", re.IGNORECASE)),
)

_CATEGORY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "explicit_original_language_claim",
        re.compile(
            r"(?:в\s+ори[гґ]інал|в\s+оригинал|по[- ]?(?:гебрей|єврей|еврей|грецьк)|"
            r"(?:гебрей|єврей|еврей|грецьк)(?:а|е|ею|ий|ій|ому|ою|у|ьке|ськ))",
            re.IGNORECASE,
        ),
    ),
    (
        "textual_variant_claim",
        re.compile(
            r"(?:інш(?:е|ий|а)\s+чит|варіант|рукопис|кодекс|у\s+деяких|"
            r"в\s+деяких|додан|пропущ|немає\s+в|відсутн)",
            re.IGNORECASE,
        ),
    ),
    (
        "morphology_grammar_claim",
        re.compile(
            r"(?:множин|однин|дієслов|іменник|прикметник|відмін|форма\s+слова|"
            r"час\s+дієсл|грамат|рід\s+слова)",
            re.IGNORECASE,
        ),
    ),
    (
        "lexical_semantic_claim",
        re.compile(
            r"(?:означає|визначає|цебто|тобто|переклада|дослівно|"
            r"це\s+(?:є|значить)|—\s*це\s|–\s*це\s)",
            re.IGNORECASE,
        ),
    ),
    (
        "cross_reference",
        re.compile(r"(?:\bпор\.|\bдив\.|порівн)", re.IGNORECASE),
    ),
    (
        "edition_or_translation_note",
        re.compile(
            r"(?:переклад|видан|редакц|текст\s+має|буквально|дослівно)",
            re.IGNORECASE,
        ),
    ),
)

_TRANSLITERATION_EQUIVALENTS = str.maketrans(
    {
        "š": "sh",
        "ś": "sh",
        "ŝ": "sh",
        "ž": "zh",
        "ź": "zh",
        "č": "ch",
        "ć": "ch",
        "j": "y",
        "ḥ": "h",
        "ḫ": "h",
        "ḵ": "kh",
        "ṣ": "ts",
        "ṭ": "t",
        "ḏ": "d",
        "ṯ": "t",
        "ʿ": "",
        "ʾ": "",
    }
)

# Exact, reviewable spelling equivalences attested in the printed OH1988
# notes.  This is deliberately not a fuzzy transliteration algorithm.
_TRANSLITERATION_FORM_ALIASES = {
    "pnei": "penei",
    "pney": "penei",
}
_SAFE_SHORT_TRANSLITERATION_FORMS = {"al"}


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.endswith("\n"):
                raise ValueError(f"JSONL row lacks LF terminator: {path}:{line_number}")
            yield json.loads(line)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256()
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            encoded = (stable_json(row) + "\n").encode("utf-8")
            handle.write(encoded.decode("utf-8"))
            digest.update(encoded)
            count += 1
    return count, digest.hexdigest()


def transliteration_form(value: str) -> str:
    """Return a conservative comparison form for printed transliterations."""

    value = unicodedata.normalize("NFC", value.casefold()).translate(
        _TRANSLITERATION_EQUIVALENTS
    )
    output: list[str] = []
    for source_char in value:
        for char in unicodedata.normalize("NFKD", source_char):
            if unicodedata.category(char).startswith("M"):
                continue
            if "LATIN" in unicodedata.name(char, "") and char.isalpha():
                output.append(char)
    normalized = "".join(output)
    return _TRANSLITERATION_FORM_ALIASES.get(normalized, normalized)


def _is_matchable_transliteration(value: str) -> bool:
    return len(value) >= 3 or value in _SAFE_SHORT_TRANSLITERATION_FORMS


def _latin_word_runs(value: str) -> list[str]:
    runs: list[str] = []
    current: list[str] = []
    for char in unicodedata.normalize("NFC", value):
        is_latin = "LATIN" in unicodedata.name(char, "") and char.isalpha()
        is_mark = unicodedata.category(char).startswith("M") and bool(current)
        if is_latin or is_mark:
            current.append(char)
            continue
        if current:
            runs.append("".join(current))
            current = []
    if current:
        runs.append("".join(current))
    return runs


def original_script_form(value: str) -> str:
    """Normalize only Hebrew/Greek letters for exact source-script matching."""

    output: list[str] = []
    for source_char in unicodedata.normalize("NFC", value.casefold()):
        for char in unicodedata.normalize("NFKD", source_char):
            if unicodedata.category(char).startswith("M"):
                continue
            name = unicodedata.name(char, "")
            if char.isalpha() and ("HEBREW" in name or "GREEK" in name):
                output.append(char)
    return "".join(output)


def _original_script_word_runs(value: str) -> list[dict[str, str]]:
    runs: list[dict[str, str]] = []
    current: list[str] = []
    current_script: str | None = None
    for char in unicodedata.normalize("NFC", value):
        name = unicodedata.name(char, "")
        script = "hebrew" if "HEBREW" in name else "greek" if "GREEK" in name else None
        is_mark = unicodedata.category(char).startswith("M") and current_script is not None
        if script or is_mark:
            effective_script = script or current_script
            if current and effective_script != current_script:
                raw = "".join(current)
                runs.append(
                    {
                        "script": str(current_script),
                        "raw": raw,
                        "normalized": original_script_form(raw),
                    }
                )
                current = []
            current_script = effective_script
            current.append(char)
            continue
        if current:
            raw = "".join(current)
            runs.append(
                {
                    "script": str(current_script),
                    "raw": raw,
                    "normalized": original_script_form(raw),
                }
            )
            current = []
            current_script = None
    if current:
        raw = "".join(current)
        runs.append(
            {
                "script": str(current_script),
                "raw": raw,
                "normalized": original_script_form(raw),
            }
        )
    return [row for row in runs if row["normalized"]]


def classify_author_comment(text: str) -> dict[str, Any]:
    """Classify a note without inferring an alignment or textual reading."""

    languages = [name for name, pattern in _LANGUAGE_PATTERNS if pattern.search(text)]
    categories = [name for name, pattern in _CATEGORY_PATTERNS if pattern.search(text)]
    raw_mentions = _latin_word_runs(text)
    mentions: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw in raw_mentions:
        normalized = transliteration_form(raw)
        if not normalized:
            continue
        key = (raw, normalized)
        if key in seen:
            continue
        seen.add(key)
        mentions.append({"raw": raw, "normalized": normalized})
    if mentions and "transliteration_or_source_form" not in categories:
        categories.append("transliteration_or_source_form")
    script_mentions = _original_script_word_runs(text)
    if script_mentions and "original_script_source_form" not in categories:
        categories.append("original_script_source_form")
    if (
        (mentions or script_mentions)
        and re.search(r"\s[—–-]\s", text)
        and "lexical_semantic_claim" not in categories
    ):
        categories.append("lexical_semantic_claim")
    if not categories:
        categories.append("general_author_commentary")
    return {
        "categories": sorted(categories),
        "languages": sorted(languages),
        "transliteration_mentions": mentions,
        "original_script_mentions": script_mentions,
    }


def _exact_anchor_evidence(
    *,
    anchor: Mapping[str, Any] | None,
    target_tokens: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not anchor:
        return {
            "anchor_status": "non_verse_or_missing_anchor",
            "boundary_scalar": None,
            "preceding_target_token_ids": [],
            "following_target_token_ids": [],
        }
    start = anchor.get("start_scalar")
    end = anchor.get("end_scalar")
    if not isinstance(start, int) or not isinstance(end, int) or start != end:
        return {
            "anchor_status": "non_point_anchor_requires_manual_scope",
            "boundary_scalar": None,
            "preceding_target_token_ids": [],
            "following_target_token_ids": [],
        }
    preceding = [
        str(row["token_id"])
        for row in target_tokens
        if row.get("end_scalar") == start
    ]
    following = [
        str(row["token_id"])
        for row in target_tokens
        if row.get("start_scalar") == start
    ]
    return {
        "anchor_status": (
            "exact_stage6_marker_boundary"
            if preceding or following
            else "exact_stage6_marker_boundary_without_adjacent_word_token"
        ),
        "boundary_scalar": start,
        "preceding_target_token_ids": preceding,
        "following_target_token_ids": following,
    }


def _original_matches(
    *,
    analysis: Mapping[str, Any],
    original_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    mention_forms = {
        str(item["normalized"])
        for item in analysis["transliteration_mentions"]
        if _is_matchable_transliteration(str(item["normalized"]))
    }
    script_forms = {
        str(item["normalized"])
        for item in analysis["original_script_mentions"]
        if len(str(item["normalized"])) >= 2
    }
    matches_by_id: dict[str, dict[str, Any]] = {}
    matched_forms: set[str] = set()
    matched_script_forms: set[str] = set()
    for row in original_rows:
        raw = str(row.get("transliteration_raw") or "")
        normalized = transliteration_form(raw)
        surface_raw = str(row.get("surface_raw") or "")
        surface_normalized = original_script_form(surface_raw)
        bases: list[str] = []
        if _is_matchable_transliteration(normalized) and normalized in mention_forms:
            bases.append("exact_transliteration_form")
            matched_forms.add(normalized)
        if len(surface_normalized) >= 2 and surface_normalized in script_forms:
            bases.append("exact_original_script_form")
            matched_script_forms.add(surface_normalized)
        if not bases:
            continue
        original_token_id = str(row["original_token_id"])
        matches_by_id[original_token_id] = {
                "original_token_id": original_token_id,
                "source_family": row.get("source_family"),
                "source_locator": row.get("source_locator"),
                "surface_raw": surface_raw,
                "surface_normalized": surface_normalized,
                "transliteration_raw": raw,
                "transliteration_normalized": normalized,
                "match_basis": bases,
                "strong_classic": list(row.get("strong_classic") or []),
                "reading_status": row.get("reading_status"),
                "selection_kind": row.get("selection_kind"),
            }
    unmatched = [
        dict(item)
        for item in analysis["transliteration_mentions"]
        if _is_matchable_transliteration(str(item["normalized"]))
        and str(item["normalized"]) not in matched_forms
    ]
    unmatched_script = [
        dict(item)
        for item in analysis["original_script_mentions"]
        if len(str(item["normalized"])) >= 2
        and str(item["normalized"]) not in matched_script_forms
    ]
    return list(matches_by_id.values()), unmatched, unmatched_script


def _validate_locked_inputs(
    actual: Mapping[str, str], expected: Mapping[str, str] | None
) -> None:
    if expected is None:
        return
    if set(actual) != set(expected):
        raise ValueError("Author-comment input lock keys differ")
    for key, digest in expected.items():
        if not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
            raise ValueError(f"Author-comment expected digest is not SHA-256: {key}")
        if actual[key] != digest:
            raise ValueError(f"Author-comment input digest changed: {key}")


def generate_author_comment_evidence(
    *,
    footnote_definitions_path: Path,
    footnote_uses_path: Path,
    heading_footnotes_path: Path,
    target_comments_path: Path,
    token_inventory_path: Path,
    selected_original_layer_path: Path,
    output_dir: Path,
    expected_input_sha256: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Inventory all author notes and emit a deterministic evidence bundle."""

    paths = {
        "footnote_definitions": footnote_definitions_path,
        "footnote_uses": footnote_uses_path,
        "heading_footnotes": heading_footnotes_path,
        "stage6_target_comments": target_comments_path,
        "ukrainian_token_inventory": token_inventory_path,
        "fingerprint_selected_original_layer": selected_original_layer_path,
    }
    input_sha256 = {key: _sha256_file(path) for key, path in paths.items()}
    _validate_locked_inputs(input_sha256, expected_input_sha256)

    definitions: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(footnote_definitions_path):
        footnote_id = str(row.get("footnote_id") or "")
        if not footnote_id or footnote_id in definitions:
            raise ValueError("Footnote definition IDs must be nonempty and unique")
        definitions[footnote_id] = row

    verse_uses = list(_read_jsonl(footnote_uses_path))
    heading_uses = list(_read_jsonl(heading_footnotes_path))
    all_uses = [
        ("verse", row) for row in verse_uses
    ] + [("heading_non_verse", row) for row in heading_uses]
    seen_use_ids: set[str] = set()
    used_footnote_ids: set[str] = set()
    verse_use_target_refs: dict[str, str] = {}
    relevant_refs: set[str] = set()
    for scope, row in all_uses:
        use_id = str(row.get("use_id") or "")
        if not use_id or use_id in seen_use_ids:
            raise ValueError("Footnote use IDs must be nonempty and unique")
        seen_use_ids.add(use_id)
        footnote_id = str(row.get("footnote_id") or "")
        if footnote_id not in definitions:
            raise ValueError(f"Footnote use has no definition: {use_id}")
        used_footnote_ids.add(footnote_id)
        if row.get("full_text_nfc") != definitions[footnote_id].get("full_text_nfc"):
            raise ValueError(f"Footnote text differs from definition: {use_id}")
        if scope == "verse":
            target_ref = str(row.get("target_ref") or "")
            if not target_ref:
                raise ValueError(f"Verse footnote lacks target_ref: {use_id}")
            verse_use_target_refs[use_id] = target_ref
            relevant_refs.add(target_ref)
    unused_definition_ids = sorted(set(definitions) - used_footnote_ids)
    if unused_definition_ids:
        raise ValueError(
            "Footnote definitions are not fully accounted by uses: "
            f"{unused_definition_ids[:5]}"
        )

    comment_use_ids: set[str] = set()
    comment_rows = 0
    nonempty_comment_rows = 0
    comment_target_refs: set[str] = set()
    for row in _read_jsonl(target_comments_path):
        comment_rows += 1
        target_ref = str(row.get("target_ref") or "")
        if not target_ref or target_ref in comment_target_refs:
            raise ValueError("Stage-6 target comment refs must be nonempty and unique")
        comment_target_refs.add(target_ref)
        target_comment = str(row.get("target_comment") or "")
        if sha256_text(target_comment) != row.get("comment_sha256"):
            raise ValueError("Stage-6 target comment hash mismatch")
        if target_comment:
            nonempty_comment_rows += 1
        for use_id in row.get("use_ids") or []:
            if use_id in comment_use_ids:
                raise ValueError(f"Footnote use appears in two target comments: {use_id}")
            if verse_use_target_refs.get(str(use_id)) != target_ref:
                raise ValueError(
                    f"Footnote use appears in the wrong target comment: {use_id}"
                )
            comment_use_ids.add(str(use_id))
    expected_verse_use_ids = {str(row["use_id"]) for row in verse_uses}
    if comment_use_ids != expected_verse_use_ids:
        raise ValueError("Target comments do not account for every verse footnote exactly once")

    target_tokens: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _read_jsonl(token_inventory_path):
        target_ref = str(row.get("target_ref") or "")
        if target_ref in relevant_refs:
            target_tokens[target_ref].append(row)
    original_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _read_jsonl(selected_original_layer_path):
        target_ref = str(row.get("target_ref") or "")
        if target_ref in relevant_refs:
            original_rows[target_ref].append(row)
    missing_target_refs = sorted(
        ref for ref in relevant_refs if ref not in target_tokens or ref not in original_rows
    )
    if missing_target_refs:
        raise ValueError(
            f"Footnote evidence lacks token/original context: {missing_target_refs[:5]}"
        )

    counters: Counter[str] = Counter()
    output_rows: list[dict[str, Any]] = []
    for scope, use in sorted(
        all_uses,
        key=lambda item: (
            int(item[1].get("source_order") or item[1].get("heading_order") or 0),
            str(item[1]["use_id"]),
        ),
    ):
        text = str(use["full_text_nfc"])
        analysis = classify_author_comment(text)
        target_ref = str(use.get("target_ref") or "") if scope == "verse" else None
        matches, unmatched, unmatched_script = _original_matches(
            analysis=analysis,
            original_rows=original_rows.get(target_ref or "", []),
        )
        anchor = _exact_anchor_evidence(
            anchor=use.get("target_anchor") if scope == "verse" else None,
            target_tokens=target_tokens.get(target_ref or "", []),
        )
        if "textual_variant_claim" in analysis["categories"]:
            review_status = "manual_textual_review_required"
        elif matches and (unmatched or unmatched_script):
            review_status = "partial_original_form_match_requires_manual_scope"
        elif matches:
            unique_ids = {item["original_token_id"] for item in matches}
            review_status = (
                "author_original_form_uniquely_corroborates_selected_token"
                if len(unique_ids) == 1
                else "author_original_form_matches_multiple_selected_tokens"
            )
        elif "explicit_original_language_claim" in analysis["categories"]:
            review_status = "explicit_original_claim_without_exact_selected_token_match"
        else:
            review_status = "context_only_no_original_token_claim"
        evidence_id = "uk7author:" + sha256_text(
            AUTHOR_COMMENT_CONTRACT_VERSION
            + "\0"
            + str(use["use_id"])
            + "\0"
            + sha256_text(text)
        )
        row = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "author_comment_contract_version": AUTHOR_COMMENT_CONTRACT_VERSION,
            "evidence_id": evidence_id,
            "scope": scope,
            "use_id": use["use_id"],
            "footnote_id": use["footnote_id"],
            "source_order": use.get("source_order"),
            "target_ref": target_ref,
            "mapping_rule_id": use.get("mapping_rule_id"),
            "operation": use.get("operation"),
            "marker": use.get("marker"),
            "anchor_status_upstream": use.get("anchor_status"),
            "author_text_nfc": text,
            "author_text_sha256": sha256_text(text),
            "source_page": (use.get("provenance") or {}).get("page"),
            "source_title": (use.get("provenance") or {}).get("title"),
            "source_path": (use.get("provenance") or {}).get("source_path"),
            "source_input_sha256": (use.get("provenance") or {}).get(
                "input_sha256"
            ),
            "source_revision_lock_sha256": (use.get("provenance") or {}).get(
                "source_revision"
            ),
            "source_revision_id": (use.get("provenance") or {}).get(
                "revision_id"
            ),
            "categories": analysis["categories"],
            "languages": analysis["languages"],
            "transliteration_mentions": analysis["transliteration_mentions"],
            "original_script_mentions": analysis["original_script_mentions"],
            "unmatched_transliteration_mentions": unmatched,
            "unmatched_original_script_mentions": unmatched_script,
            "exact_original_form_matches": matches,
            "exact_marker_boundary": anchor,
            "review_status": review_status,
            "fingerprint_effect": "corroboration_or_manual_review_only_no_selection_mutation",
            "candidate_vote_weight": 0,
            "auto_assignment_allowed": False,
            "alignment_input_allowed": False,
            "strong_assignment_policy": "never_from_comment_alone",
        }
        output_rows.append(row)
        counters[f"scope.{scope}"] += 1
        counters[f"review.{review_status}"] += 1
        for category in analysis["categories"]:
            counters[f"category.{category}"] += 1
        for language in analysis["languages"]:
            counters[f"language.{language}"] += 1
        counters["exact_original_matches"] += len(matches)
        counters["unmatched_transliteration_mentions"] += len(unmatched)
        counters["unmatched_original_script_mentions"] += len(unmatched_script)
        counters[f"anchor.{anchor['anchor_status']}"] += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_NAME
    output_count, output_sha256 = _write_jsonl(output_path, output_rows)
    if output_count != len(all_uses):
        raise AssertionError("Author-comment output accounting drifted")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "author_comment_contract_version": AUTHOR_COMMENT_CONTRACT_VERSION,
        "artifact": "author_comment_evidence",
        "status": "complete_author_note_inventory_corroboration_only",
        "deterministic_serialization": (
            "UTF-8; source codepoints preserved; LF; JSON keys sorted; compact separators"
        ),
        "input_sha256": dict(sorted(input_sha256.items())),
        "output_sha256": {OUTPUT_NAME: output_sha256},
        "dependency_graph": [
            {
                "node": "author_comment_evidence",
                "depends_on": sorted(input_sha256),
                "relation": (
                    "exact-edition note extraction plus immutable stage-6 "
                    "anchor and same-locus selected-original corroboration"
                ),
            }
        ],
        "processed_count": output_count,
        "skipped_count": 0,
        "error_count": 0,
        "counts": {
            "definition_count": len(definitions),
            "verse_use_count": len(verse_uses),
            "heading_non_verse_use_count": len(heading_uses),
            "target_comment_row_count": comment_rows,
            "nonempty_target_comment_count": nonempty_comment_rows,
            "target_ref_count": len(relevant_refs),
            **dict(sorted(counters.items())),
        },
        "selection_mutation_count": 0,
        "automatic_assignment_count": 0,
        "notes": [
            "all printed verse and heading footnote uses are accounted exactly once",
            "exact printed note text is retained only in the gitignored work JSONL; versioned reports contain hashes and safe decisions",
            "comments remain outside verse text and outside statistical/contextual aligner input",
            "exact transliteration matches are corroboration/manual-review evidence only",
            "no author note can create a Strong assignment without reviewed original-token-to-OH span evidence",
        ],
    }
    manifest_path = output_dir / "author_comment_evidence.manifest.json"
    _write_json(manifest_path, manifest)
    return manifest


def validate_author_comment_evidence_bundle(
    *, output_dir: Path, expected_input_sha256: Mapping[str, str]
) -> dict[str, Any]:
    manifest_path = output_dir / "author_comment_evidence.manifest.json"
    output_path = output_dir / OUTPUT_NAME
    if not manifest_path.is_file() or not output_path.is_file():
        raise ValueError("Author-comment evidence bundle is incomplete")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Author-comment evidence schema changed")
    if manifest.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Author-comment evidence parent contract changed")
    if manifest.get("author_comment_contract_version") != AUTHOR_COMMENT_CONTRACT_VERSION:
        raise ValueError("Author-comment evidence contract changed")
    _validate_locked_inputs(manifest.get("input_sha256") or {}, expected_input_sha256)
    expected_dependencies = [
        {
            "node": "author_comment_evidence",
            "depends_on": sorted(expected_input_sha256),
            "relation": (
                "exact-edition note extraction plus immutable stage-6 "
                "anchor and same-locus selected-original corroboration"
            ),
        }
    ]
    if manifest.get("dependency_graph") != expected_dependencies:
        raise ValueError("Author-comment evidence dependency graph changed")
    output_sha256 = manifest.get("output_sha256") or {}
    if set(output_sha256) != {OUTPUT_NAME}:
        raise ValueError("Author-comment evidence output inventory changed")
    if _sha256_file(output_path) != output_sha256.get(OUTPUT_NAME):
        raise ValueError("Author-comment evidence output digest changed")
    count = 0
    seen_evidence_ids: set[str] = set()
    seen_use_ids: set[str] = set()
    counters: Counter[str] = Counter()
    for row in _read_jsonl(output_path):
        count += 1
        if row.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Author-comment row schema changed")
        if row.get("contract_version") != CONTRACT_VERSION:
            raise ValueError("Author-comment row parent contract changed")
        if row.get("author_comment_contract_version") != AUTHOR_COMMENT_CONTRACT_VERSION:
            raise ValueError("Author-comment row contract changed")
        evidence_id = str(row.get("evidence_id") or "")
        use_id = str(row.get("use_id") or "")
        if not evidence_id or evidence_id in seen_evidence_ids:
            raise ValueError("Author-comment evidence IDs must be nonempty and unique")
        if not use_id or use_id in seen_use_ids:
            raise ValueError("Author-comment use IDs must be nonempty and unique")
        seen_evidence_ids.add(evidence_id)
        seen_use_ids.add(use_id)
        scope = row.get("scope")
        if scope not in {"verse", "heading_non_verse"}:
            raise ValueError("Author-comment evidence has an invalid scope")
        if (scope == "verse") != bool(row.get("target_ref")):
            raise ValueError("Author-comment target_ref does not match its scope")
        if row.get("candidate_vote_weight") != 0:
            raise ValueError("Author-comment evidence gained an assignment vote")
        if row.get("auto_assignment_allowed") is not False:
            raise ValueError("Author-comment evidence became auto-assignable")
        if row.get("alignment_input_allowed") is not False:
            raise ValueError("Author comments leaked into aligner input")
        if row.get("fingerprint_effect") != (
            "corroboration_or_manual_review_only_no_selection_mutation"
        ):
            raise ValueError("Author-comment evidence mutated textual selection")
        if row.get("strong_assignment_policy") != "never_from_comment_alone":
            raise ValueError("Author-comment evidence gained sole-proof authority")
        author_text = row.get("author_text_nfc")
        if not isinstance(author_text, str) or sha256_text(author_text) != row.get(
            "author_text_sha256"
        ):
            raise ValueError("Author-comment text/hash provenance changed")
        match_ids = [
            str(item.get("original_token_id") or "")
            for item in row.get("exact_original_form_matches") or []
        ]
        if any(not item for item in match_ids) or len(match_ids) != len(set(match_ids)):
            raise ValueError("Author-comment original matches are dangling or duplicated")
        counters[f"scope.{scope}"] += 1
        counters[f"review.{row.get('review_status')}"] += 1
        for category in row.get("categories") or []:
            counters[f"category.{category}"] += 1
        for language in row.get("languages") or []:
            counters[f"language.{language}"] += 1
        counters["exact_original_matches"] += len(match_ids)
        counters["unmatched_transliteration_mentions"] += len(
            row.get("unmatched_transliteration_mentions") or []
        )
        counters["unmatched_original_script_mentions"] += len(
            row.get("unmatched_original_script_mentions") or []
        )
        anchor = row.get("exact_marker_boundary") or {}
        anchor_status = str(anchor.get("anchor_status") or "")
        if not anchor_status:
            raise ValueError("Author-comment marker anchor is unaccounted")
        counters[f"anchor.{anchor_status}"] += 1
    if count != manifest.get("processed_count"):
        raise ValueError("Author-comment evidence row count changed")
    manifest_counts = manifest.get("counts") or {}
    for key, value in counters.items():
        if manifest_counts.get(key) != value:
            raise ValueError(f"Author-comment evidence counter changed: {key}")
    if manifest.get("skipped_count") != 0 or manifest.get("error_count") != 0:
        raise ValueError("Author-comment evidence is not completely accounted")
    if manifest.get("selection_mutation_count") != 0:
        raise ValueError("Author-comment evidence mutated the frozen textual selection")
    if manifest.get("automatic_assignment_count") != 0:
        raise ValueError("Author-comment evidence gained automatic assignments")
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--footnote-definitions", type=Path, required=True)
    parser.add_argument("--footnote-uses", type=Path, required=True)
    parser.add_argument("--heading-footnotes", type=Path, required=True)
    parser.add_argument("--target-comments", type=Path, required=True)
    parser.add_argument("--token-inventory", type=Path, required=True)
    parser.add_argument("--selected-original-layer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    manifest = generate_author_comment_evidence(
        footnote_definitions_path=args.footnote_definitions,
        footnote_uses_path=args.footnote_uses,
        heading_footnotes_path=args.heading_footnotes,
        target_comments_path=args.target_comments,
        token_inventory_path=args.token_inventory,
        selected_original_layer_path=args.selected_original_layer,
        output_dir=args.output,
    )
    print(stable_json(manifest))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

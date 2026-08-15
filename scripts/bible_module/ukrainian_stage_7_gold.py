"""Deterministic, fail-closed manual gold workflow for Ukrainian stage 7.

The ordinary stage-7 generator prepares an ignored annotation workbench.  This
module turns that workbench into two answer-free reviewer packets, validates
two complete blind review passes, and finalizes reviewed link/null decisions.
It never infers or manufactures a manual decision.

Finalization writes ``gold_alignment.annotations.jsonl`` together with a
cryptographic lock.  Call :func:`validated_finalized_gold_lock` before an
ordinary generator writes that artifact; a valid lock means the reviewed file
and its manifest must be preserved byte-for-byte.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable, Iterator, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    TOKENIZER_VERSION,
    exact_word_tokens,
    sha256_text,
    stable_json,
    validate_exact_partition,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_20260801"
DEFAULT_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"
DEFAULT_STAGE6_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_6_20260801"
EXPECTED_STAGE6_TEXT_SHA256 = (
    "e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf"
)
EXPECTED_STAGE6_COMMENT_SHA256 = (
    "5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4"
)
GOLD_WORKFLOW_VERSION = "ukrainian-stage-7-gold-workflow-v2"
SHARD_CONTRACT_VERSION = "ukrainian-stage-7-gold-shards-v1"
GOLD_PREPARATION_MANIFEST = "gold_alignment.preparation.manifest.json"

PRODUCTION_PACKET_INPUT_KEYS = frozenset(
    {
        "stage6_text",
        "stage6_comments",
        "source_registry",
        "original_token_universe",
        "fingerprint_selected_original_layer",
        "gold_selected_original_layer",
        "ukrainian_token_inventory",
        "original_token_universe_manifest",
        "gold_alignment_preparation_manifest",
        "gold_selection_panel",
        "gold_annotation_workbench",
    }
)

BOOKS = (
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam",
    "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job",
    "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos",
    "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag",
    "Zech", "Mal", "Mat", "Mark", "Luke", "John", "Acts", "Rom", "1Cor",
    "2Cor", "Gal", "Eph", "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim",
    "Titus", "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John",
    "Jude", "Rev",
)
BOOK_NUMBER = {book: number for number, book in enumerate(BOOKS, 1)}

ALLOWED_RELATIONS = {
    "one_to_one",
    "one_to_many",
    "many_to_one",
    "many_to_many",
    "grouped_expression",
    "original_omitted",
}
ALLOWED_NULL_REASONS = {
    "translation_omission",
    "grammatical_function_not_overt",
    "absorbed_by_grouped_expression",
    "repetition_not_rendered",
    "source_text_not_rendered",
}
ALLOWED_TARGET_STATUSES = {"aligned", "translation_addition", "function_token"}
ALLOWED_SEVERITIES = {"normal", "high", "critical"}
REQUIRED_PHENOMENA = {
    "textual_variant",
    "merge_split",
    "reorder",
    "omission",
    "addition",
    "repetition",
    "named_entity",
    "particle",
    "compound",
    "multiple_strong",
    "rare_lemma",
    "frequent_lemma",
    "polysemy",
}
REQUIRED_RELATIONS = {
    "one_to_many",
    "many_to_one",
    "many_to_many",
    "original_omitted",
    "translation_addition",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row {line_number} is not an object: {path}")
            yield value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256()
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            encoded = stable_json(row) + "\n"
            handle.write(encoded)
            digest.update(encoded.encode("utf-8"))
            count += 1
    return count, digest.hexdigest()


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{label} is not an exact lowercase SHA-256")
    return value


def _manifest(
    *,
    artifact: str,
    status: str,
    inputs: Mapping[str, str],
    outputs: Mapping[str, str],
    processed: int,
    skipped: int,
    errors: int,
    counts: Mapping[str, Any],
    notes: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "artifact": artifact,
        "status": status,
        "input_sha256": dict(sorted(inputs.items())),
        "output_sha256": dict(sorted(outputs.items())),
        "processed_count": processed,
        "skipped_count": skipped,
        "error_count": errors,
        "counts": dict(sorted(counts.items())),
        "notes": list(notes),
        "serialization": "UTF-8 JSON; sorted keys, compact separators, LF; canonical ID order",
    }


def _token_exactly_matches(text: str, row: Mapping[str, Any]) -> bool:
    start_scalar = row.get("start_scalar")
    end_scalar = row.get("end_scalar")
    start_byte = row.get("start_byte")
    end_byte = row.get("end_byte")
    surface = row.get("surface")
    if not all(isinstance(value, int) for value in (start_scalar, end_scalar, start_byte, end_byte)):
        return False
    if not isinstance(surface, str):
        return False
    encoded = text.encode("utf-8")
    try:
        return (
            text[start_scalar:end_scalar] == surface
            and encoded[start_byte:end_byte].decode("utf-8") == surface
        )
    except (UnicodeDecodeError, IndexError):
        return False


def _validate_workbench_pair(
    panel: Mapping[str, Any],
    workbench: Mapping[str, Any],
) -> tuple[list[str], list[str]]:
    for field in ("selection_id", "target_ref"):
        if panel.get(field) != workbench.get(field):
            raise ValueError(f"Panel/workbench {field} mismatch")
    text = workbench.get("plain_text_nfc")
    if not isinstance(text, str):
        raise ValueError("Workbench lacks exact plain text")
    if sha256_text(text) != panel.get("plain_text_sha256"):
        raise ValueError("Workbench plain text differs from its frozen stage-6 hash")
    comment = workbench.get("target_comment")
    if not isinstance(comment, str) or sha256_text(comment) != panel.get("comment_sha256"):
        raise ValueError("Workbench comment differs from its frozen stage-6 hash")
    tokens = exact_word_tokens(text)
    validate_exact_partition(text, tokens)
    target_rows = workbench.get("target_tokens")
    if not isinstance(target_rows, list) or len(target_rows) != len(tokens):
        raise ValueError("Workbench target token partition is incomplete")
    target_ids: list[str] = []
    for expected, actual in zip(tokens, target_rows, strict=True):
        if not isinstance(actual, dict) or not _token_exactly_matches(text, actual):
            raise ValueError("Workbench target scalar/byte offset round-trip failed")
        expected_fields = {
            "order": expected.order,
            "surface": expected.surface,
            "comparison": expected.comparison,
            "start_scalar": expected.start_scalar,
            "end_scalar": expected.end_scalar,
            "start_byte": expected.start_byte,
            "end_byte": expected.end_byte,
        }
        if any(actual.get(key) != value for key, value in expected_fields.items()):
            raise ValueError("Workbench target tokenization contract drifted")
        token_id = actual.get("token_id")
        if not isinstance(token_id, str) or not token_id:
            raise ValueError("Workbench target token lacks a stable ID")
        target_ids.append(token_id)
    if len(set(target_ids)) != len(target_ids):
        raise ValueError("Duplicate target token ID inside verse")

    originals = workbench.get("original_tokens")
    if not isinstance(originals, list):
        raise ValueError("Workbench original token list is missing")
    original_by_id: dict[str, Mapping[str, Any]] = {}
    for original in originals:
        if not isinstance(original, dict):
            raise ValueError("Malformed original token")
        token_id = original.get("original_token_id")
        if not isinstance(token_id, str) or not token_id or token_id in original_by_id:
            raise ValueError("Missing or duplicate original token ID")
        original_by_id[token_id] = original
    primary_ids = panel.get("original_token_ids")
    if not isinstance(primary_ids, list) or not all(isinstance(value, str) for value in primary_ids):
        raise ValueError("Panel primary-original IDs are malformed")
    if len(set(primary_ids)) != len(primary_ids):
        raise ValueError("Panel repeats a primary-original ID")
    for token_id in primary_ids:
        original = original_by_id.get(token_id)
        if original is None:
            raise ValueError("Panel primary-original ID is absent from workbench")
        reading = str(original.get("reading_status", ""))
        if not reading.startswith("primary_") or "unresolved" in reading:
            raise ValueError("Panel includes a non-primary or unresolved original token")
    if panel.get("projected_decision_count") != len(primary_ids):
        raise ValueError("Panel projected decision count drifted")
    return primary_ids, target_ids


def _packet_rows(
    panels: Sequence[Mapping[str, Any]],
    workbenches: Mapping[str, Mapping[str, Any]],
    *,
    review_pass: int,
    input_sha256: Mapping[str, str],
) -> Iterator[dict[str, Any]]:
    for panel in panels:
        selection_id = str(panel["selection_id"])
        workbench = workbenches[selection_id]
        primary_ids, target_ids = _validate_workbench_pair(panel, workbench)
        original_by_id = {
            str(row["original_token_id"]): row
            for row in workbench["original_tokens"]
        }
        yield {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "record_type": "reviewer_packet_verse",
            "review_pass": review_pass,
            "blind_to_other_pass": True,
            "selection_id": selection_id,
            "target_ref": panel["target_ref"],
            "verse_key": panel["verse_key"],
            "book": panel["book"],
            "testament": panel["testament"],
            "stage6_plain_sha256": panel["plain_text_sha256"],
            "stage6_comment_sha256": panel["comment_sha256"],
            "input_sha256": dict(sorted(input_sha256.items())),
            "plain_text_nfc": workbench["plain_text_nfc"],
            "target_comment": workbench["target_comment"],
            "target_tokens": workbench["target_tokens"],
            "original_tokens": [original_by_id[token_id] for token_id in primary_ids],
            "original_decision_requests": [
                {
                    "decision_id": "gold7:original:" + sha256_text(token_id)[:32],
                    "original_token_id": token_id,
                    "required": True,
                }
                for token_id in primary_ids
            ],
            "target_accounting_requests": [
                {
                    "accounting_id": "gold7:target:" + sha256_text(token_id)[:32],
                    "target_token_id": token_id,
                    "required": True,
                }
                for token_id in target_ids
            ],
            "strata": panel["strata"],
            "answer_template": {
                "relation": None,
                "group_original_token_ids": [],
                "target_token_ids": [],
                "null_reason": None,
                "severity": None,
                "phenomena": [],
                "evidence": [],
                "rationale": None,
            },
        }


def prepare_reviewer_packets(
    *,
    panel_path: Path,
    workbench_path: Path,
    output_dir: Path,
    minimum_verses: int = 2_000,
    minimum_decisions: int = 25_000,
    require_full_canon: bool = True,
    stage6_work_dir: Path = DEFAULT_STAGE6_WORK,
    stage7_work_dir: Path = DEFAULT_WORK,
    report_dir: Path = DEFAULT_REPORT,
    _allow_cc0_fixture_without_immutable_corpus: bool = False,
) -> dict[str, Any]:
    """Create two deterministic, answer-free and mutually blind packets."""

    panels = list(_read_jsonl(panel_path))
    workbench_rows = list(_read_jsonl(workbench_path))
    if len(panels) < minimum_verses:
        raise ValueError("Gold panel has fewer than the required 2,000 verses")
    panel_ids = [str(row.get("selection_id", "")) for row in panels]
    if not all(panel_ids) or len(set(panel_ids)) != len(panel_ids):
        raise ValueError("Gold panel selection IDs are missing or duplicated")
    workbenches: dict[str, Mapping[str, Any]] = {}
    for row in workbench_rows:
        selection_id = str(row.get("selection_id", ""))
        if not selection_id or selection_id in workbenches:
            raise ValueError("Gold workbench selection IDs are missing or duplicated")
        workbenches[selection_id] = row
    if set(panel_ids) != set(workbenches):
        raise ValueError("Gold panel/workbench selection sets differ")

    def reference_key(row: Mapping[str, Any]) -> tuple[int, int, int, str]:
        ref = str(row.get("target_ref", ""))
        try:
            book, chapter, verse = ref.split(".")
            return BOOK_NUMBER[book], int(chapter), int(verse), str(row.get("selection_id"))
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Panel target reference is not canonical: {ref}") from None

    canonical_panels = sorted(panels, key=reference_key)
    original_ids: set[str] = set()
    target_ids: set[str] = set()
    books: set[str] = set()
    testaments: set[str] = set()
    genres: set[str] = set()
    mapping_operations: set[str] = set()
    frequency_bands: set[str] = set()
    fingerprint_count = 0
    for panel in canonical_panels:
        selection_id = str(panel["selection_id"])
        primary, targets = _validate_workbench_pair(panel, workbenches[selection_id])
        if original_ids.intersection(primary) or target_ids.intersection(targets):
            raise ValueError("Stable original/target token ID is reused across verses")
        original_ids.update(primary)
        target_ids.update(targets)
        books.add(str(panel.get("book")))
        testaments.add(str(panel.get("testament")))
        strata = panel.get("strata")
        if not isinstance(strata, dict):
            raise ValueError("Panel row lacks explicit strata")
        genres.add(str(strata.get("genre")))
        mapping_operations.add(str(strata.get("mapping_operation")))
        frequency_bands.update(str(value) for value in strata.get("original_frequency_bands", []))
        fingerprint_count += int(strata.get("textual_fingerprint_locus") is True)
    if len(original_ids) < minimum_decisions:
        raise ValueError("Gold panel has fewer than the required 25,000 original decisions")
    if require_full_canon:
        if books != set(BOOKS):
            raise ValueError("Gold panel does not cover all 66 books")
        if testaments != {"OT", "NT"}:
            raise ValueError("Gold panel does not cover both Testaments")
        required_genres = {
            "torah_prose_law", "historical_prose", "poetry_wisdom", "prophetic",
            "gospel_narrative", "acts_narrative", "epistle", "apocalyptic",
        }
        if not required_genres <= genres:
            raise ValueError("Gold panel genre strata are incomplete")
        if not {"merge", "split"} <= mapping_operations:
            raise ValueError("Gold panel lacks merge/split mapping anomalies")
        if not {"rare_1_to_5", "frequent_1000_plus"} <= frequency_bands:
            raise ValueError("Gold panel lacks rare/frequent original strata")
        if fingerprint_count == 0:
            raise ValueError("Gold panel lacks textual-fingerprint loci")

    immutable_inputs: dict[str, str] = {
        "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
        "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
    }
    if not _allow_cc0_fixture_without_immutable_corpus:
        stage6_text = stage6_work_dir / "synthesized_text.jsonl"
        stage6_comments = stage6_work_dir / "target_comments.jsonl"
        universe = stage7_work_dir / "original_token_universe.jsonl"
        selected_original_layer = stage7_work_dir / "gold_selected_original_layer.jsonl"
        token_inventory = stage7_work_dir / "ukrainian_token_inventory.jsonl"
        candidate_selected_original_layer = (
            stage7_work_dir / "fingerprint_selected_original_layer.jsonl"
        )
        universe_manifest = report_dir / "original_token_universe.manifest.json"
        source_registry = report_dir / "source_registry.json"
        preparation_manifest = report_dir / GOLD_PREPARATION_MANIFEST
        if _sha256_file(stage6_text) != EXPECTED_STAGE6_TEXT_SHA256:
            raise ValueError("Immutable stage-6 text SHA-256 changed")
        if _sha256_file(stage6_comments) != EXPECTED_STAGE6_COMMENT_SHA256:
            raise ValueError("Immutable stage-6 comment SHA-256 changed")
        universe_digest = _sha256_file(universe)
        selected_original_layer_digest = _sha256_file(selected_original_layer)
        candidate_selected_original_layer_digest = _sha256_file(
            candidate_selected_original_layer
        )
        universe_manifest_value = _read_json(universe_manifest)
        preparation_manifest_value = _read_json(preparation_manifest)
        if (
            preparation_manifest_value.get("artifact")
            != "gold_alignment_preparation"
            or preparation_manifest_value.get("status")
            != "prepared_answer_free_gold_inputs"
            or preparation_manifest_value.get("gold_workflow_version")
            != GOLD_WORKFLOW_VERSION
        ):
            raise ValueError("Gold preparation manifest contract/status is invalid")
        if (
            universe_manifest_value.get("output_sha256", {}).get(
                "original_token_universe.jsonl"
            )
            != universe_digest
        ):
            raise ValueError("Original-token universe differs from its manifest")
        if (
            preparation_manifest_value.get("output_sha256", {}).get(
                "gold_selected_original_layer.jsonl"
            )
            != selected_original_layer_digest
        ):
            raise ValueError(
                "Gold-selected original layer differs from its manifest"
            )
        preparation_outputs = preparation_manifest_value.get("output_sha256", {})
        expected_preparation_outputs = {
            "gold_selection_panel.jsonl": _sha256_file(panel_path),
            "gold_annotation_workbench.jsonl": _sha256_file(workbench_path),
            "gold_selected_original_layer.jsonl": selected_original_layer_digest,
        }
        if preparation_outputs != expected_preparation_outputs:
            raise ValueError("Gold preparation inputs differ from their manifest")
        if (
            universe_manifest_value.get("output_sha256", {}).get(
                "fingerprint_selected_original_layer.jsonl"
            )
            != candidate_selected_original_layer_digest
        ):
            raise ValueError(
                "Candidate-selected original layer differs from its manifest"
            )
        immutable_inputs.update(
            {
                "original_token_universe": universe_digest,
                "gold_selected_original_layer": selected_original_layer_digest,
                "fingerprint_selected_original_layer": candidate_selected_original_layer_digest,
                "ukrainian_token_inventory": _sha256_file(token_inventory),
                "original_token_universe_manifest": _sha256_file(universe_manifest),
                "gold_alignment_preparation_manifest": _sha256_file(
                    preparation_manifest
                ),
                "source_registry": _sha256_file(source_registry),
            }
        )
    input_sha256 = {
        **immutable_inputs,
        "gold_selection_panel": _sha256_file(panel_path),
        "gold_annotation_workbench": _sha256_file(workbench_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for review_pass in (1, 2):
        path = output_dir / f"review_pass_{review_pass}.packet.jsonl"
        count, digest = _write_jsonl(
            path,
            _packet_rows(
                canonical_panels,
                workbenches,
                review_pass=review_pass,
                input_sha256=input_sha256,
            ),
        )
        if count != len(canonical_panels):
            raise RuntimeError("Reviewer packet row count drifted")
        outputs[path.name] = digest
    manifest = _manifest(
        artifact="gold_reviewer_packets",
        status="prepared_unanswered_blind_packets",
        inputs=input_sha256,
        outputs=outputs,
        processed=len(canonical_panels),
        skipped=0,
        errors=0,
        counts={
            "selected_verses": len(canonical_panels),
            "primary_original_decisions": len(original_ids),
            "target_token_accounting_decisions": len(target_ids),
            "books": len(books),
            "fingerprint_loci": fingerprint_count,
            "review_passes": 2,
        },
        notes=(
            "Packets contain no answer, candidate score, legacy assignment or other-pass decision.",
            "Every resolved primary original ID and every Ukrainian target token ID has exactly one request per pass.",
            "Full text remains under the gitignored stage-7 work directory.",
        ),
    )
    manifest["corpus_contract"] = (
        "cc0_fixture"
        if _allow_cc0_fixture_without_immutable_corpus
        else "ohienko_1988_production"
    )
    manifest["strata"] = {
        "books": sorted(books, key=BOOK_NUMBER.get),
        "testaments": sorted(testaments),
        "genres": sorted(genres),
        "mapping_operations": sorted(mapping_operations),
        "original_frequency_bands": sorted(frequency_bands),
    }
    manifest_path = output_dir / "gold_reviewer_packets.manifest.json"
    _write_json(manifest_path, manifest)
    return manifest


def _packet_requests(packet_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    originals: dict[str, dict[str, Any]] = {}
    targets: dict[str, dict[str, Any]] = {}
    refs: dict[str, str] = {}
    target_ref_by_id: dict[str, str] = {}
    for packet in packet_rows:
        ref = str(packet["target_ref"])
        target_token_by_id = {
            str(row["token_id"]): row for row in packet["target_tokens"]
        }
        for request in packet["original_decision_requests"]:
            decision_id = str(request["decision_id"])
            token_id = str(request["original_token_id"])
            if decision_id in originals or token_id in refs:
                raise ValueError("Packet duplicates an original decision or token ID")
            originals[decision_id] = {"token_id": token_id, "target_ref": ref}
            refs[token_id] = ref
        for request in packet["target_accounting_requests"]:
            accounting_id = str(request["accounting_id"])
            token_id = str(request["target_token_id"])
            if accounting_id in targets or token_id in target_ref_by_id:
                raise ValueError("Packet duplicates a target accounting or token ID")
            token = target_token_by_id.get(token_id)
            if token is None:
                raise ValueError("Target-accounting request has no token metadata")
            targets[accounting_id] = {
                "token_id": token_id,
                "target_ref": ref,
                "span": {
                    "start_scalar": token["start_scalar"],
                    "end_scalar": token["end_scalar"],
                    "start_byte": token["start_byte"],
                    "end_byte": token["end_byte"],
                    "surface_sha256": sha256_text(str(token["surface"])),
                },
            }
            target_ref_by_id[token_id] = ref
    return {
        "originals": originals,
        "targets": targets,
        "original_ref_by_id": refs,
        "target_ref_by_id": target_ref_by_id,
    }


def _evidence_ok(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, dict)
            and isinstance(item.get("kind"), str)
            and bool(item["kind"].strip())
            and isinstance(item.get("evidence_id"), str)
            and bool(item["evidence_id"].strip())
            for item in value
        )
    )


def _semantic_original(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "original_decision",
        "decision_status": "decided",
        "decision_id": row["decision_id"],
        "original_token_id": row["original_token_id"],
        "target_ref": row["target_ref"],
        "relation": row["relation"],
        "group_original_token_ids": sorted(row["group_original_token_ids"]),
        "target_token_ids": sorted(row["target_token_ids"]),
        "null_reason": row.get("null_reason"),
        "severity": row["severity"],
        "phenomena": sorted(set(row.get("phenomena", []))),
    }


def _semantic_target(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "target_accounting",
        "decision_status": "decided",
        "accounting_id": row["accounting_id"],
        "target_token_id": row["target_token_id"],
        "target_ref": row["target_ref"],
        "target_status": row["target_status"],
        "linked_original_token_ids": sorted(row["linked_original_token_ids"]),
        "severity": row["severity"],
        "phenomena": sorted(set(row.get("phenomena", []))),
    }


def _validate_original_decision(
    row: Mapping[str, Any],
    request: Mapping[str, Any],
    requests: Mapping[str, Any],
) -> dict[str, Any]:
    if row.get("decision_status") != "decided":
        raise ValueError("Original decision is unresolved or lacks an explicit decided status")
    if row.get("original_token_id") != request["token_id"]:
        raise ValueError("Original decision ID/token ID mismatch")
    if row.get("target_ref") != request["target_ref"]:
        raise ValueError("Original decision crosses a verse")
    relation = row.get("relation")
    if relation not in ALLOWED_RELATIONS:
        raise ValueError("Original decision has an unknown relation")
    group = row.get("group_original_token_ids")
    targets = row.get("target_token_ids")
    if not isinstance(group, list) or not group or len(set(group)) != len(group):
        raise ValueError("Original decision has an invalid group")
    if request["token_id"] not in group:
        raise ValueError("Original decision group omits the accounted original")
    if not isinstance(targets, list) or len(set(targets)) != len(targets):
        raise ValueError("Original decision target IDs are malformed")
    for original_id in group:
        if requests["original_ref_by_id"].get(original_id) != request["target_ref"]:
            raise ValueError("Original group contains a dangling or cross-verse ID")
    for target_id in targets:
        if requests["target_ref_by_id"].get(target_id) != request["target_ref"]:
            raise ValueError("Original decision contains a dangling or cross-verse target ID")
    null_reason = row.get("null_reason")
    if relation == "original_omitted":
        if targets or null_reason not in ALLOWED_NULL_REASONS or len(group) != 1:
            raise ValueError("Original omission requires one original, no targets and an allowed reason")
    else:
        if not targets or null_reason is not None:
            raise ValueError("Non-null original decision requires targets and no null reason")
    cardinality = (len(group), len(targets))
    if relation == "one_to_one" and cardinality != (1, 1):
        raise ValueError("one_to_one cardinality mismatch")
    if relation == "one_to_many" and not (cardinality[0] == 1 and cardinality[1] >= 2):
        raise ValueError("one_to_many cardinality mismatch")
    if relation == "many_to_one" and not (cardinality[0] >= 2 and cardinality[1] == 1):
        raise ValueError("many_to_one cardinality mismatch")
    if relation == "many_to_many" and not (cardinality[0] >= 2 and cardinality[1] >= 2):
        raise ValueError("many_to_many cardinality mismatch")
    if row.get("severity") not in ALLOWED_SEVERITIES:
        raise ValueError("Original decision severity is invalid")
    if not isinstance(row.get("phenomena"), list):
        raise ValueError("Original decision phenomena are malformed")
    if not _evidence_ok(row.get("evidence")) or not str(row.get("rationale", "")).strip():
        raise ValueError("Original decision lacks token-level evidence/rationale")
    return _semantic_original(row)


def _validate_target_accounting(
    row: Mapping[str, Any],
    request: Mapping[str, Any],
    requests: Mapping[str, Any],
) -> dict[str, Any]:
    if row.get("decision_status") != "decided":
        raise ValueError("Target accounting is unresolved or lacks an explicit decided status")
    if row.get("target_token_id") != request["token_id"]:
        raise ValueError("Target accounting ID/token ID mismatch")
    if row.get("target_ref") != request["target_ref"]:
        raise ValueError("Target accounting crosses a verse")
    status = row.get("target_status")
    if status not in ALLOWED_TARGET_STATUSES:
        raise ValueError("Target accounting status is invalid")
    originals = row.get("linked_original_token_ids")
    if not isinstance(originals, list) or len(set(originals)) != len(originals):
        raise ValueError("Target accounting original IDs are malformed")
    for original_id in originals:
        if requests["original_ref_by_id"].get(original_id) != request["target_ref"]:
            raise ValueError("Target accounting contains a dangling or cross-verse original ID")
    if status == "aligned" and not originals:
        raise ValueError("Aligned target token lacks original IDs")
    if status != "aligned" and originals:
        raise ValueError("Translation addition/function token cannot carry original IDs")
    if row.get("severity") not in ALLOWED_SEVERITIES:
        raise ValueError("Target accounting severity is invalid")
    if not isinstance(row.get("phenomena"), list):
        raise ValueError("Target accounting phenomena are malformed")
    if not _evidence_ok(row.get("evidence")) or not str(row.get("rationale", "")).strip():
        raise ValueError("Target accounting lacks token-level evidence/rationale")
    return _semantic_target(row)


def ingest_review_pass(
    *,
    review_pass: int,
    packet_path: Path,
    packet_manifest_path: Path,
    submission_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Validate and normalize one complete blind review pass."""

    if review_pass not in {1, 2}:
        raise ValueError("Review pass must be 1 or 2")
    manifest = _read_json(packet_manifest_path)
    if manifest.get("status") != "prepared_unanswered_blind_packets":
        raise ValueError("Reviewer packet manifest is not an unanswered frozen packet")
    packet_digest = _sha256_file(packet_path)
    if manifest.get("output_sha256", {}).get(packet_path.name) != packet_digest:
        raise ValueError("Reviewer packet digest does not match its manifest")
    packet_rows = list(_read_jsonl(packet_path))
    if any(row.get("review_pass") != review_pass for row in packet_rows):
        raise ValueError("Reviewer packet pass number mismatch")
    if any(row.get("input_sha256") != manifest.get("input_sha256") for row in packet_rows):
        raise ValueError("Reviewer packet row input SHA locks differ from the manifest")
    requests = _packet_requests(packet_rows)
    if (
        len(packet_rows) != manifest.get("counts", {}).get("selected_verses")
        or len(requests["originals"]) != manifest.get("counts", {}).get("primary_original_decisions")
        or len(requests["targets"]) != manifest.get("counts", {}).get("target_token_accounting_decisions")
    ):
        raise ValueError("Reviewer packet request counts differ from the manifest")

    submissions = list(_read_jsonl(submission_path))
    metadata_rows = [row for row in submissions if row.get("record_type") == "review_metadata"]
    if len(metadata_rows) != 1:
        raise ValueError("Review submission requires exactly one metadata row")
    metadata = metadata_rows[0]
    reviewer_id = metadata.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError("Review submission lacks a stable reviewer ID")
    if metadata.get("review_pass") != review_pass or metadata.get("blind_to_other_pass") is not True:
        raise ValueError("Review submission is not declared as the requested blind pass")
    for prohibited in ("other_pass_sha256", "other_reviewer_id", "prior_annotations_sha256"):
        if prohibited in metadata:
            raise ValueError("Blind review metadata exposes another pass")
    manifest_digest = _sha256_file(packet_manifest_path)
    if metadata.get("packet_sha256") != packet_digest:
        raise ValueError("Review submission packet SHA lock differs")
    if metadata.get("packet_manifest_sha256") != manifest_digest:
        raise ValueError("Review submission manifest SHA lock differs")
    if metadata.get("input_sha256") != manifest.get("input_sha256"):
        raise ValueError("Review submission source input SHA locks differ")
    reviewer_mode = metadata.get("reviewer_mode", "single")
    reviewer_roster = metadata.get("reviewer_roster", [])
    if reviewer_mode == "single":
        if reviewer_roster not in ([], None):
            raise ValueError("Single-reviewer pass cannot carry a reviewer roster")
        allowed_reviewers = {reviewer_id}
    elif reviewer_mode == "sharded":
        if (
            not isinstance(reviewer_roster, list)
            or not reviewer_roster
            or any(
                not isinstance(item, dict)
                or not isinstance(item.get("reviewer_id"), str)
                or not item["reviewer_id"].strip()
                or not isinstance(item.get("shard_ids"), list)
                or not item["shard_ids"]
                for item in reviewer_roster
            )
        ):
            raise ValueError("Sharded review pass has an invalid reviewer roster")
        canonical_roster = sorted(
            (
                {
                    "reviewer_id": item["reviewer_id"],
                    "shard_ids": sorted(set(item["shard_ids"])),
                }
                for item in reviewer_roster
            ),
            key=lambda item: item["reviewer_id"],
        )
        if len({item["reviewer_id"] for item in canonical_roster}) != len(
            canonical_roster
        ):
            raise ValueError("Sharded review roster repeats a reviewer ID")
        expected_roster_id = (
            "reviewer-roster:" + sha256_text(stable_json(canonical_roster))[:32]
        )
        if reviewer_id != expected_roster_id or reviewer_roster != canonical_roster:
            raise ValueError("Sharded review roster identity/order is not canonical")
        allowed_reviewers = {item["reviewer_id"] for item in canonical_roster}
        shard_merge_manifest_path = Path(str(submission_path) + ".manifest.json")
        if not shard_merge_manifest_path.is_file():
            raise ValueError("Sharded review pass lacks its merge digest sidecar")
        shard_merge_manifest = _read_json(shard_merge_manifest_path)
        if (
            shard_merge_manifest.get("artifact")
            != f"gold_merged_shard_review_pass_{review_pass}"
            or shard_merge_manifest.get("status")
            != "complete_shard_merge_ready_for_pass_ingestion"
            or shard_merge_manifest.get("shard_contract_version")
            != SHARD_CONTRACT_VERSION
            or shard_merge_manifest.get("review_pass") != review_pass
            or shard_merge_manifest.get("reviewer_id") != reviewer_id
            or shard_merge_manifest.get("reviewer_roster") != canonical_roster
            or shard_merge_manifest.get("output_sha256", {}).get(
                submission_path.name
            )
            != _sha256_file(submission_path)
            or shard_merge_manifest.get("input_sha256", {}).get(
                "shard_manifest"
            )
            != metadata.get("shard_manifest_sha256")
            or shard_merge_manifest.get("input_sha256", {}).get("parent_packet")
            != packet_digest
            or shard_merge_manifest.get("input_sha256", {}).get(
                "parent_packet_manifest"
            )
            != manifest_digest
        ):
            raise ValueError("Sharded review pass differs from its merge SHA chain")
    else:
        raise ValueError("Unknown review mode")

    decisions: dict[str, dict[str, Any]] = {}
    target_rows: dict[str, dict[str, Any]] = {}
    evidence_by_key: dict[str, dict[str, Any]] = {}
    reviewer_by_key: dict[str, str] = {}
    for row in submissions:
        record_type = row.get("record_type")
        if record_type == "review_metadata":
            continue
        if record_type == "original_decision":
            key = str(row.get("decision_id", ""))
            request = requests["originals"].get(key)
            if request is None or key in decisions:
                raise ValueError("Unknown or duplicate original decision")
            decisions[key] = _validate_original_decision(row, request, requests)
            row_reviewer = row.get("reviewer_id", reviewer_id)
            if row_reviewer not in allowed_reviewers:
                raise ValueError("Decision reviewer is absent from the pass roster")
            reviewer_by_key["original:" + key] = str(row_reviewer)
            evidence_by_key["original:" + key] = {
                "evidence": row["evidence"], "rationale": row["rationale"]
            }
        elif record_type == "target_accounting":
            key = str(row.get("accounting_id", ""))
            request = requests["targets"].get(key)
            if request is None or key in target_rows:
                raise ValueError("Unknown or duplicate target accounting decision")
            target_rows[key] = _validate_target_accounting(row, request, requests)
            target_rows[key]["target_span"] = request["span"]
            row_reviewer = row.get("reviewer_id", reviewer_id)
            if row_reviewer not in allowed_reviewers:
                raise ValueError("Target-accounting reviewer is absent from the pass roster")
            reviewer_by_key["target:" + key] = str(row_reviewer)
            evidence_by_key["target:" + key] = {
                "evidence": row["evidence"], "rationale": row["rationale"]
            }
        else:
            raise ValueError("Review submission contains an unknown record type")
    if set(decisions) != set(requests["originals"]):
        raise ValueError("Review pass does not account exactly once for every primary original ID")
    if set(target_rows) != set(requests["targets"]):
        raise ValueError("Review pass does not account exactly once for every target token ID")
    _validate_semantic_accounting(decisions, target_rows)

    normalized = [{
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "record_type": "review_metadata",
        "status": "complete_blind_review_pass",
        "review_pass": review_pass,
        "reviewer_id": reviewer_id,
        "reviewer_mode": reviewer_mode,
        "reviewer_roster": reviewer_roster if reviewer_mode == "sharded" else [],
        "blind_to_other_pass": True,
        "packet_sha256": packet_digest,
        "packet_manifest_sha256": manifest_digest,
        "input_sha256": manifest["input_sha256"],
        "raw_submission_sha256": _sha256_file(submission_path),
    }]
    for key in sorted(decisions):
        row = dict(decisions[key])
        row.update(evidence_by_key["original:" + key])
        row["reviewer_id"] = reviewer_by_key["original:" + key]
        normalized.append(row)
    for key in sorted(target_rows):
        row = dict(target_rows[key])
        row.update(evidence_by_key["target:" + key])
        row["reviewer_id"] = reviewer_by_key["target:" + key]
        normalized.append(row)
    count, digest = _write_jsonl(output_path, normalized)
    result = _manifest(
        artifact=f"gold_review_pass_{review_pass}",
        status="complete_blind_review_pass",
        inputs={
            "reviewer_packet": packet_digest,
            "reviewer_packet_manifest": manifest_digest,
            "raw_submission": _sha256_file(submission_path),
            **{
                f"source_{key}": value
                for key, value in manifest["input_sha256"].items()
            },
            **(
                {
                    "shard_merge_manifest": _sha256_file(
                        Path(str(submission_path) + ".manifest.json")
                    )
                }
                if reviewer_mode == "sharded"
                else {}
            ),
        },
        outputs={output_path.name: digest},
        processed=count - 1,
        skipped=0,
        errors=0,
        counts={
            "original_decisions": len(decisions),
            "target_accounting": len(target_rows),
            "reviewers": len(allowed_reviewers),
        },
        notes=(
            "This normalized pass is complete and blind to the other pass.",
            "The sidecar digest must validate before finalization.",
        ),
    )
    result["review_pass"] = review_pass
    result["reviewer_id"] = reviewer_id
    result["reviewer_mode"] = reviewer_mode
    result["reviewer_roster"] = reviewer_roster if reviewer_mode == "sharded" else []
    _write_json(Path(str(output_path) + ".manifest.json"), result)
    return result


def _validate_semantic_accounting(
    originals: Mapping[str, Mapping[str, Any]],
    targets: Mapping[str, Mapping[str, Any]],
) -> None:
    original_by_token = {str(row["original_token_id"]): row for row in originals.values()}
    referenced_targets: dict[str, set[str]] = defaultdict(set)
    for row in originals.values():
        group = set(row["group_original_token_ids"])
        for member in group:
            peer = original_by_token.get(member)
            if peer is None:
                raise ValueError("Hyperedge group contains an unaccounted original")
            if _semantic_group(peer) != _semantic_group(row):
                raise ValueError("Hyperedge members do not declare an identical group")
        for target_id in row["target_token_ids"]:
            referenced_targets[target_id].update(group)
    target_by_token = {str(row["target_token_id"]): row for row in targets.values()}
    for target_id, row in target_by_token.items():
        linked = set(row["linked_original_token_ids"])
        expected = referenced_targets.get(target_id, set())
        if row["target_status"] == "aligned":
            if linked != expected:
                raise ValueError("Aligned target accounting disagrees with original hyperedges")
        elif expected:
            raise ValueError("A translation addition/function token is referenced by an original edge")
    if set(referenced_targets) - set(target_by_token):
        raise ValueError("Original hyperedge points to an unaccounted target")


def _semantic_group(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["target_ref"],
        row["relation"],
        tuple(row["group_original_token_ids"]),
        tuple(row["target_token_ids"]),
        row.get("null_reason"),
    )


def _validate_final_grid(
    final_values: Mapping[str, Mapping[str, Any]],
    frozen_values: Mapping[str, Mapping[str, Any]],
) -> None:
    """Revalidate adjudicated semantics against the frozen pass ID/ref grid."""

    requests: dict[str, Any] = {
        "originals": {},
        "targets": {},
        "original_ref_by_id": {},
        "target_ref_by_id": {},
    }
    for key, row in frozen_values.items():
        if key.startswith("original:"):
            decision_id = key.removeprefix("original:")
            token_id = str(row["original_token_id"])
            request = {"token_id": token_id, "target_ref": row["target_ref"]}
            requests["originals"][decision_id] = request
            requests["original_ref_by_id"][token_id] = row["target_ref"]
        else:
            accounting_id = key.removeprefix("target:")
            token_id = str(row["target_token_id"])
            request = {"token_id": token_id, "target_ref": row["target_ref"]}
            requests["targets"][accounting_id] = request
            requests["target_ref_by_id"][token_id] = row["target_ref"]
    for key, row in final_values.items():
        if key.startswith("original:"):
            request = requests["originals"][key.removeprefix("original:")]
            _validate_original_decision(row, request, requests)
        else:
            request = requests["targets"][key.removeprefix("target:")]
            _validate_target_accounting(row, request, requests)


def _load_normalized_pass(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    sidecar_path = Path(str(path) + ".manifest.json")
    if not sidecar_path.is_file():
        raise ValueError("Normalized review pass lacks its digest sidecar")
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("status") != "complete_blind_review_pass"
        or sidecar.get("output_sha256", {}).get(path.name) != _sha256_file(path)
    ):
        raise ValueError("Normalized review pass differs from its digest sidecar")
    rows = list(_read_jsonl(path))
    metadata = [row for row in rows if row.get("record_type") == "review_metadata"]
    if len(metadata) != 1 or metadata[0].get("status") != "complete_blind_review_pass":
        raise ValueError("Normalized review pass is missing complete metadata")
    values: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("record_type") == "original_decision":
            key = "original:" + str(row["decision_id"])
        elif row.get("record_type") == "target_accounting":
            key = "target:" + str(row["accounting_id"])
        else:
            continue
        if key in values:
            raise ValueError("Normalized pass contains a duplicate decision")
        values[key] = row
    return metadata[0], values


def _semantic_for_key(row: Mapping[str, Any]) -> dict[str, Any]:
    if row["record_type"] == "original_decision":
        return _semantic_original(row)
    return _semantic_target(row)


def _load_adjudication(
    path: Path,
    *,
    all_keys: set[str],
    disagreement_keys: set[str],
    pass1_sha256: str,
    pass2_sha256: str,
    packet_manifest_sha256: str,
    reviewer_ids: set[str],
) -> tuple[str, dict[str, dict[str, Any]]]:
    rows = list(_read_jsonl(path))
    headers = [row for row in rows if row.get("record_type") == "adjudication_metadata"]
    if len(headers) != 1:
        raise ValueError("Adjudication requires exactly one metadata row")
    header = headers[0]
    adjudicator = header.get("adjudicator_id")
    if not isinstance(adjudicator, str) or not adjudicator.strip() or adjudicator in reviewer_ids:
        raise ValueError("Adjudicator must be stable and distinct from both reviewers")
    if (
        header.get("pass_1_sha256") != pass1_sha256
        or header.get("pass_2_sha256") != pass2_sha256
        or header.get("packet_manifest_sha256") != packet_manifest_sha256
    ):
        raise ValueError("Adjudication input SHA locks differ")
    values: dict[str, dict[str, Any]] = {}
    for row in rows:
        record_type = row.get("record_type")
        if record_type == "adjudication_metadata":
            continue
        if record_type == "original_decision":
            key = "original:" + str(row.get("decision_id", ""))
        elif record_type == "target_accounting":
            key = "target:" + str(row.get("accounting_id", ""))
        else:
            raise ValueError("Adjudication contains an unknown record type")
        if key not in all_keys or key in values:
            raise ValueError("Adjudication contains an unknown or duplicate decision")
        if not _evidence_ok(row.get("evidence")) or not str(row.get("rationale", "")).strip():
            raise ValueError("Adjudication lacks evidence/rationale")
        values[key] = dict(row)
    if not disagreement_keys <= set(values):
        raise ValueError("Not every pass disagreement was adjudicated")
    return adjudicator, values


def _make_final_rows(
    final_values: Mapping[str, Mapping[str, Any]],
    pass1: Mapping[str, Mapping[str, Any]],
    pass2: Mapping[str, Mapping[str, Any]],
    *,
    adjudicator: str | None,
    adjudicated_keys: set[str],
) -> list[dict[str, Any]]:
    originals = {
        key.removeprefix("original:"): value
        for key, value in final_values.items()
        if key.startswith("original:")
    }
    targets = {
        key.removeprefix("target:"): value
        for key, value in final_values.items()
        if key.startswith("target:")
    }
    _validate_semantic_accounting(originals, targets)
    target_span_by_id = {
        str(row["target_token_id"]): pass1["target:" + key]["target_span"]
        for key, row in targets.items()
    }
    edge_members: dict[tuple[Any, ...], set[str]] = defaultdict(set)
    for row in originals.values():
        edge_members[_semantic_group(row)].add(str(row["decision_id"]))
    edge_id_by_group: dict[tuple[Any, ...], str] = {}
    rows: list[dict[str, Any]] = []
    for group in sorted(edge_members, key=lambda value: stable_json(value)):
        ref, relation, original_ids, target_ids, null_reason = group
        edge_payload = {
            "target_ref": ref,
            "relation": relation,
            "original_token_ids": list(original_ids),
            "target_token_ids": list(target_ids),
            "null_reason": null_reason,
        }
        edge_id = "gold7:edge:" + sha256_text(stable_json(edge_payload))[:32]
        edge_id_by_group[group] = edge_id
        rows.append({
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "record_type": "hyperedge",
            "edge_id": edge_id,
            **edge_payload,
            "decision_ids": sorted(edge_members[group]),
            "status": "reviewed_accepted",
        })
    for key in sorted(originals):
        value = originals[key]
        compound_key = "original:" + key
        rows.append({
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            **_semantic_original(value),
            "edge_id": edge_id_by_group[_semantic_group(value)],
            "target_spans": [
                {
                    "target_token_id": target_id,
                    **target_span_by_id[target_id],
                }
                for target_id in value["target_token_ids"]
            ],
            "review": {
                "pass_1": pass1[compound_key]["reviewer_id"],
                "pass_2": pass2[compound_key]["reviewer_id"],
                "agreement": compound_key not in adjudicated_keys,
                "adjudicator": adjudicator if compound_key in adjudicated_keys else None,
            },
            "evidence": {
                "pass_1": pass1[compound_key]["evidence"],
                "pass_2": pass2[compound_key]["evidence"],
                "adjudication": value.get("evidence") if compound_key in adjudicated_keys else None,
            },
            "rationale": {
                "pass_1": pass1[compound_key]["rationale"],
                "pass_2": pass2[compound_key]["rationale"],
                "adjudication": value.get("rationale") if compound_key in adjudicated_keys else None,
            },
            "status": "reviewed_accepted",
        })
    for key in sorted(targets):
        value = targets[key]
        compound_key = "target:" + key
        rows.append({
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            **_semantic_target(value),
            "target_span": target_span_by_id[value["target_token_id"]],
            "review": {
                "pass_1": pass1[compound_key]["reviewer_id"],
                "pass_2": pass2[compound_key]["reviewer_id"],
                "agreement": compound_key not in adjudicated_keys,
                "adjudicator": adjudicator if compound_key in adjudicated_keys else None,
            },
            "evidence": {
                "pass_1": pass1[compound_key]["evidence"],
                "pass_2": pass2[compound_key]["evidence"],
                "adjudication": value.get("evidence") if compound_key in adjudicated_keys else None,
            },
            "rationale": {
                "pass_1": pass1[compound_key]["rationale"],
                "pass_2": pass2[compound_key]["rationale"],
                "adjudication": value.get("rationale") if compound_key in adjudicated_keys else None,
            },
            "status": "reviewed_accepted",
        })
        if value["target_status"] != "aligned":
            relation = "translation_addition"
            edge_payload = {
                "target_ref": value["target_ref"],
                "relation": relation,
                "original_token_ids": [],
                "target_token_ids": [value["target_token_id"]],
                "null_reason": value["target_status"],
            }
            rows.append({
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                "record_type": "hyperedge",
                "edge_id": "gold7:edge:" + sha256_text(stable_json(edge_payload))[:32],
                **edge_payload,
                "accounting_ids": [value["accounting_id"]],
                "status": "reviewed_accepted",
            })
    order = {"hyperedge": 0, "original_decision": 1, "target_accounting": 2}
    return sorted(
        rows,
        key=lambda row: (
            BOOK_NUMBER[str(row["target_ref"]).split(".", 1)[0]],
            str(row["target_ref"]),
            order[row["record_type"]],
            str(row.get("edge_id") or row.get("decision_id") or row.get("accounting_id")),
        ),
    )


def finalize_gold(
    *,
    pass1_path: Path,
    pass2_path: Path,
    packet_manifest_path: Path,
    report_dir: Path,
    adjudication_path: Path | None = None,
    minimum_verses: int = 2_000,
    minimum_decisions: int = 25_000,
    required_phenomena: set[str] = REQUIRED_PHENOMENA,
    required_relations: set[str] = REQUIRED_RELATIONS,
) -> dict[str, Any]:
    """Finalize only complete, independently reviewed and fully accounted gold."""

    packet_manifest = _read_json(packet_manifest_path)
    if (
        packet_manifest.get("artifact") != "gold_reviewer_packets"
        or packet_manifest.get("status") != "prepared_unanswered_blind_packets"
        or packet_manifest.get("contract_version") != CONTRACT_VERSION
        or packet_manifest.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
    ):
        raise ValueError("Frozen reviewer packet manifest contract/status is invalid")
    if packet_manifest.get("input_sha256", {}).get("stage6_text") != EXPECTED_STAGE6_TEXT_SHA256:
        raise ValueError("Frozen reviewer packet is locked to another stage-6 text")
    if packet_manifest.get("input_sha256", {}).get("stage6_comments") != EXPECTED_STAGE6_COMMENT_SHA256:
        raise ValueError("Frozen reviewer packet is locked to another stage-6 comment stream")
    corpus_contract = packet_manifest.get("corpus_contract")
    packet_inputs = packet_manifest.get("input_sha256")
    if corpus_contract == "ohienko_1988_production":
        if not isinstance(packet_inputs, Mapping) or set(packet_inputs) != set(
            PRODUCTION_PACKET_INPUT_KEYS
        ):
            raise ValueError(
                "Production reviewer packet lacks the exact immutable input lock set"
            )
    elif corpus_contract != "cc0_fixture":
        raise ValueError("Frozen reviewer packet corpus contract is invalid")
    if packet_manifest.get("counts", {}).get("selected_verses", 0) < minimum_verses:
        raise ValueError("Frozen reviewer packet is below the verse minimum")
    if packet_manifest.get("counts", {}).get("primary_original_decisions", 0) < minimum_decisions:
        raise ValueError("Frozen reviewer packet is below the decision minimum")
    metadata1, pass1 = _load_normalized_pass(pass1_path)
    metadata2, pass2 = _load_normalized_pass(pass2_path)
    if metadata1.get("review_pass") != 1 or metadata2.get("review_pass") != 2:
        raise ValueError("Normalized reviews are not pass 1 and pass 2")
    reviewer1 = str(metadata1["reviewer_id"])
    reviewer2 = str(metadata2["reviewer_id"])
    manifest_digest = _sha256_file(packet_manifest_path)
    for metadata in (metadata1, metadata2):
        if metadata.get("packet_manifest_sha256") != manifest_digest:
            raise ValueError("Review pass is locked to another packet manifest")
        if metadata.get("input_sha256") != packet_manifest.get("input_sha256"):
            raise ValueError("Review pass source input SHA locks differ")
    if set(pass1) != set(pass2):
        raise ValueError("Review passes account for different stable decision IDs")
    same_reviewer_keys = [
        key
        for key in sorted(pass1)
        if pass1[key].get("reviewer_id") == pass2[key].get("reviewer_id")
    ]
    if same_reviewer_keys:
        raise ValueError(
            "Blind review passes require distinct reviewers for every decision: "
            + ", ".join(same_reviewer_keys[:5])
        )
    disagreements = {
        key for key in pass1 if _semantic_for_key(pass1[key]) != _semantic_for_key(pass2[key])
    }
    final_values: dict[str, Mapping[str, Any]] = {
        key: dict(pass1[key]) for key in pass1 if key not in disagreements
    }
    adjudicator: str | None = None
    adjudicated: dict[str, dict[str, Any]] = {}
    if disagreements:
        if adjudication_path is None:
            raise ValueError("Review disagreements require explicit adjudication")
        adjudicator, adjudicated = _load_adjudication(
            adjudication_path,
            all_keys=set(pass1),
            disagreement_keys=disagreements,
            pass1_sha256=_sha256_file(pass1_path),
            pass2_sha256=_sha256_file(pass2_path),
            packet_manifest_sha256=manifest_digest,
            reviewer_ids={
                str(row["reviewer_id"])
                for row in (*pass1.values(), *pass2.values())
            },
        )
        final_values.update(adjudicated)
    elif adjudication_path is not None:
        raise ValueError("Adjudication is forbidden when the blind passes agree")
    if set(final_values) != set(pass1):
        raise ValueError("Adjudication did not produce exact decision accounting")
    _validate_final_grid(final_values, pass1)
    if any(row.get("severity") in {"critical", "high"} for row in final_values.values()):
        # Both complete pass files necessarily contain each of these IDs.  This
        # explicit assertion keeps the critical/high two-pass gate visible.
        if same_reviewer_keys:
            raise ValueError("Critical/high decisions lack two independent passes")

    original_values = {
        key.removeprefix("original:"): value
        for key, value in final_values.items()
        if key.startswith("original:")
    }
    target_values = {
        key.removeprefix("target:"): value
        for key, value in final_values.items()
        if key.startswith("target:")
    }
    _validate_semantic_accounting(original_values, target_values)
    phenomena = {
        str(item)
        for row in final_values.values()
        for item in row.get("phenomena", [])
    }
    relations = {str(row["relation"]) for row in original_values.values()}
    if any(row["target_status"] != "aligned" for row in target_values.values()):
        relations.add("translation_addition")
    if not required_phenomena <= phenomena:
        raise ValueError("Final gold lacks required anomaly/lexical phenomena strata")
    if not required_relations <= relations:
        raise ValueError("Final gold lacks required cardinality/null relations")

    final_rows = _make_final_rows(
        final_values,
        pass1,
        pass2,
        adjudicator=adjudicator,
        adjudicated_keys=set(adjudicated),
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    annotations_path = report_dir / "gold_alignment.annotations.jsonl"
    annotation_count, annotation_sha = _write_jsonl(annotations_path, final_rows)
    relation_counts = Counter(
        row["relation"] for row in final_rows if row["record_type"] == "hyperedge"
    )
    manifest = _manifest(
        artifact="gold_alignment",
        status="finalized_reviewed_gold",
        inputs={
            **packet_manifest["input_sha256"],
            "reviewer_packets_manifest": manifest_digest,
            "review_pass_1": _sha256_file(pass1_path),
            "review_pass_1_manifest": _sha256_file(Path(str(pass1_path) + ".manifest.json")),
            "review_pass_2": _sha256_file(pass2_path),
            "review_pass_2_manifest": _sha256_file(Path(str(pass2_path) + ".manifest.json")),
            **(
                {"adjudication": _sha256_file(adjudication_path)}
                if adjudication_path is not None
                else {}
            ),
        },
        outputs={
            "gold_selection_panel.jsonl": packet_manifest["input_sha256"][
                "gold_selection_panel"
            ],
            "gold_annotation_workbench.jsonl": packet_manifest["input_sha256"][
                "gold_annotation_workbench"
            ],
            **(
                {
                    "gold_selected_original_layer.jsonl": packet_manifest[
                        "input_sha256"
                    ]["gold_selected_original_layer"]
                }
                if "gold_selected_original_layer"
                in packet_manifest["input_sha256"]
                else {}
            ),
            "gold_alignment.annotations.jsonl": annotation_sha,
        },
        processed=annotation_count,
        skipped=0,
        errors=0,
        counts={
            "selected_verses": packet_manifest["counts"]["selected_verses"],
            "accepted_assignment_or_null_decisions": len(original_values),
            "target_token_accounting_decisions": len(target_values),
            "hyperedges": sum(relation_counts.values()),
            "review_disagreements": len(disagreements),
            "adjudicated_decisions": len(adjudicated),
            "unresolved_critical_high": 0,
        },
        notes=(
            "Every resolved primary original ID has exactly one reviewed link/null decision.",
            "Every Ukrainian token is aligned or has a reviewed addition/function-token status.",
            "Distinct blind passes are retained; disagreements are accepted only through a distinct adjudicator.",
        ),
    )
    manifest["reviewers"] = {
        "pass_1": sorted({str(row["reviewer_id"]) for row in pass1.values()}),
        "pass_2": sorted({str(row["reviewer_id"]) for row in pass2.values()}),
        "pass_1_roster_id": reviewer1,
        "pass_2_roster_id": reviewer2,
        "adjudicator": adjudicator,
    }
    manifest["relation_counts"] = dict(sorted(relation_counts.items()))
    manifest["phenomena"] = sorted(phenomena)
    manifest["corpus_contract"] = corpus_contract
    manifest_path = report_dir / "gold_alignment.manifest.json"
    _write_json(manifest_path, manifest)
    lock = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "corpus_contract": corpus_contract,
        "status": "finalized_reviewed_gold",
        "artifact_sha256": annotation_sha,
        "manifest_sha256": _sha256_file(manifest_path),
        "input_sha256": manifest["input_sha256"],
        "processed_count": annotation_count,
        "skipped_count": 0,
        "error_count": 0,
        "protection_contract": "ordinary_stage7_generation_must_preserve_artifact_and_manifest_byte_for_byte",
    }
    _write_json(report_dir / "gold_alignment.finalized.lock.json", lock)
    validated_finalized_gold_lock(report_dir)
    return manifest


def validated_finalized_gold_lock(report_dir: Path) -> dict[str, Any] | None:
    """Return a valid final lock, ``None`` if absent, and raise if stale/tampered."""

    lock_path = report_dir / "gold_alignment.finalized.lock.json"
    if not lock_path.exists():
        return None
    lock = _read_json(lock_path)
    if (
        lock.get("schema_version") != SCHEMA_VERSION
        or lock.get("contract_version") != CONTRACT_VERSION
        or lock.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or lock.get("corpus_contract")
        not in {"ohienko_1988_production", "cc0_fixture"}
        or lock.get("status") != "finalized_reviewed_gold"
    ):
        raise ValueError("Finalized gold lock contract/status is invalid")
    annotations = report_dir / "gold_alignment.annotations.jsonl"
    manifest = report_dir / "gold_alignment.manifest.json"
    if not annotations.is_file() or not manifest.is_file():
        raise ValueError("Finalized gold lock points to a missing artifact")
    _require_sha256(lock.get("artifact_sha256"), "Finalized gold artifact lock")
    _require_sha256(lock.get("manifest_sha256"), "Finalized gold manifest lock")
    if _sha256_file(annotations) != lock["artifact_sha256"]:
        raise ValueError("Finalized gold annotations were changed after review")
    if _sha256_file(manifest) != lock["manifest_sha256"]:
        raise ValueError("Finalized gold manifest was changed after review")
    manifest_value = _read_json(manifest)
    if manifest_value.get("status") != "finalized_reviewed_gold":
        raise ValueError("Finalized gold manifest status is invalid")
    if manifest_value.get("output_sha256", {}).get(annotations.name) != lock["artifact_sha256"]:
        raise ValueError("Finalized gold manifest/artifact hashes disagree")
    if manifest_value.get("input_sha256") != lock.get("input_sha256"):
        raise ValueError("Finalized gold input SHA lock differs from its manifest")
    if manifest_value.get("corpus_contract") != lock.get("corpus_contract"):
        raise ValueError("Finalized gold corpus contract differs from its manifest")
    if lock.get("corpus_contract") == "ohienko_1988_production":
        locked_inputs = lock.get("input_sha256")
        if not isinstance(locked_inputs, Mapping) or not set(
            PRODUCTION_PACKET_INPUT_KEYS
        ) <= set(locked_inputs):
            raise ValueError("Finalized production gold lacks immutable input locks")
        if (
            manifest_value.get("output_sha256", {}).get(
                "gold_selected_original_layer.jsonl"
            )
            != locked_inputs.get("gold_selected_original_layer")
        ):
            raise ValueError(
                "Finalized production gold selected-layer locks disagree"
            )
    return lock


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare", help="prepare two answer-free blind packets")
    prepare.add_argument("--panel", type=Path, default=DEFAULT_WORK / "gold_selection_panel.jsonl")
    prepare.add_argument("--workbench", type=Path, default=DEFAULT_WORK / "gold_annotation_workbench.jsonl")
    prepare.add_argument("--output-dir", type=Path, default=DEFAULT_WORK / "gold_review")
    prepare.add_argument("--stage6-work-dir", type=Path, default=DEFAULT_STAGE6_WORK)
    prepare.add_argument("--stage7-work-dir", type=Path, default=DEFAULT_WORK)
    prepare.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    for review_pass in (1, 2):
        command = subparsers.add_parser(f"ingest-pass{review_pass}", help=f"validate blind review pass {review_pass}")
        command.add_argument("--packet", type=Path, required=True)
        command.add_argument("--packet-manifest", type=Path, required=True)
        command.add_argument("--submission", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        command.set_defaults(review_pass=review_pass)
    finalize = subparsers.add_parser("finalize", help="finalize two reviewed passes")
    finalize.add_argument("--pass1", type=Path, required=True)
    finalize.add_argument("--pass2", type=Path, required=True)
    finalize.add_argument("--packet-manifest", type=Path, required=True)
    finalize.add_argument("--adjudication", type=Path)
    finalize.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    check = subparsers.add_parser("check-final", help="verify finalized gold lock")
    check.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "prepare":
        result = prepare_reviewer_packets(
            panel_path=args.panel,
            workbench_path=args.workbench,
            output_dir=args.output_dir,
            stage6_work_dir=args.stage6_work_dir,
            stage7_work_dir=args.stage7_work_dir,
            report_dir=args.report_dir,
        )
    elif args.command in {"ingest-pass1", "ingest-pass2"}:
        result = ingest_review_pass(
            review_pass=args.review_pass,
            packet_path=args.packet,
            packet_manifest_path=args.packet_manifest,
            submission_path=args.submission,
            output_path=args.output,
        )
    elif args.command == "finalize":
        result = finalize_gold(
            pass1_path=args.pass1,
            pass2_path=args.pass2,
            packet_manifest_path=args.packet_manifest,
            report_dir=args.report_dir,
            adjudication_path=args.adjudication,
        )
    else:
        result = validated_finalized_gold_lock(args.report_dir)
        if result is None:
            raise ValueError("No finalized gold lock exists")
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

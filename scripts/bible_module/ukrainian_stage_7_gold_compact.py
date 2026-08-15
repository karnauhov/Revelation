"""Compact, answer-free manual-review scaffold for Ukrainian stage 7.

The frozen gold reviewer packet is deliberately verbose.  This module makes a
smaller per-verse view with local ``oNNN``/``tNNN`` indices and expands a
human-filled compact submission back into the exact raw schema accepted by
``ukrainian_stage_7_gold.ingest_review_pass`` (full packets) or
``ukrainian_stage_7_gold_shards.merge_review_shards`` (frozen shards).

No candidate, legacy, score, confidence, label, link or null answer is inferred
or copied into a template.  Every original group and every target null must be
entered explicitly by the reviewer.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold import (
    ALLOWED_NULL_REASONS,
    ALLOWED_RELATIONS,
    ALLOWED_SEVERITIES,
    ALLOWED_TARGET_STATUSES,
    GOLD_WORKFLOW_VERSION,
    SHARD_CONTRACT_VERSION,
    _evidence_ok,
    _manifest,
    _packet_requests,
    _read_json,
    _read_jsonl,
    _sha256_file,
    _validate_original_decision,
    _validate_semantic_accounting,
    _validate_target_accounting,
    _write_json,
    _write_jsonl,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    sha256_lines,
    sha256_text,
    stable_json,
)


COMPACT_REVIEW_VERSION = "ukrainian-stage-7-gold-compact-review-v1"
_REVIEWER_ID_RE = re.compile(r"^[^\x00-\x20\x7f]{3,128}$")
_PROHIBITED_BLIND_KEYS = {
    "other_pass_sha256",
    "other_reviewer_id",
    "prior_annotations_sha256",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ORIGINAL_DISPLAY_FIELDS = (
    "order",
    "component_group",
    "component_kind",
    "surface_raw",
    "surface_normalized",
    "transliteration_raw",
    "gloss_raw",
    "lemma_raw",
    "lemma_source",
    "morphology_raw",
    "strong_raw",
    "strong_normalized",
    "strong_classic",
    "strong_status",
    "reading_status",
    "source_reading_status",
    "textual_witnesses",
    "textual_variant_raw",
    "source_family",
    "source_id",
    "source_locator",
    "mapping_rule_id",
    "projection_status",
    "gold_selection_provenance",
)


@dataclass(frozen=True)
class _PacketContext:
    manifest: dict[str, Any]
    rows: list[dict[str, Any]]
    review_pass: int
    packet_path: Path
    packet_sha: str
    packet_manifest_sha: str
    parent_input_sha256: dict[str, str]
    review_scope: str
    parent_packet_sha256: str
    parent_packet_manifest_sha256: str
    shard_entry: dict[str, Any] | None = None

    @property
    def shard_id(self) -> str | None:
        if self.shard_entry is None:
            return None
        return str(self.shard_entry["shard_id"])


def _row_sha256(row: Mapping[str, Any]) -> str:
    return sha256_text(stable_json(row))


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _assert_nonexistent(path: Path, label: str) -> None:
    if path.exists():
        raise FileExistsError(f"{label} already exists; refusing to overwrite: {path}")


def _require_reviewer_id(value: Any) -> str:
    if not isinstance(value, str) or _REVIEWER_ID_RE.fullmatch(value) is None:
        raise ValueError(
            "Compact submission requires a stable 3-128 character reviewer ID "
            "without whitespace/control characters"
        )
    return value


def _require_exact_keys(
    value: Mapping[str, Any], allowed: set[str], label: str
) -> None:
    extra = set(value) - allowed
    if extra:
        raise ValueError(f"{label} has unknown/prohibited fields: {sorted(extra)}")


def _assert_no_other_pass_leakage(value: Any, label: str) -> None:
    """Reject other-pass/prior-answer keys at any nesting depth."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).casefold()
            if (
                normalized in _PROHIBITED_BLIND_KEYS
                or (
                    "other_pass" in normalized
                    and normalized != "blind_to_other_pass"
                )
                or "other_reviewer" in normalized
                or "prior_annotation" in normalized
            ):
                raise ValueError(f"{label} exposes another review pass")
            _assert_no_other_pass_leakage(child, label)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_other_pass_leakage(child, label)


def _assert_no_answer_channel_keys(value: Any, label: str) -> None:
    """Keep candidate and decision answer channels out of blind templates."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).casefold()
            if (
                any(
                    fragment in normalized
                    for fragment in ("candidate", "legacy", "confidence", "score")
                )
                or normalized
                in {
                    "label",
                    "labels",
                    "link",
                    "links",
                    "decision_status",
                    "relation",
                    "null_reason",
                    "target_status",
                    "target_token_ids",
                    "linked_original_token_ids",
                }
            ):
                raise ValueError(f"{label} contains a prohibited answer channel")
            _assert_no_answer_channel_keys(child, label)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_answer_channel_keys(child, label)


def _validate_answer_free_packet_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    review_pass: int,
    input_sha256: Mapping[str, str],
    label: str,
) -> None:
    if any(
        row.get("record_type") != "reviewer_packet_verse"
        or row.get("review_pass") != review_pass
        or row.get("blind_to_other_pass") is not True
        or row.get("input_sha256") != input_sha256
        for row in rows
    ):
        raise ValueError(f"{label} row locks/contract differ")
    for row in rows:
        _assert_no_other_pass_leakage(row, label)
        answer = row.get("answer_template")
        if not isinstance(answer, dict) or any(
            value not in (None, [], {}) for value in answer.values()
        ):
            raise ValueError(f"{label} is not answer-free")


def _load_packet(
    packet_path: Path, packet_manifest_path: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], int, str, str]:
    manifest = _read_json(packet_manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Frozen reviewer packet manifest is not an object")
    _assert_no_other_pass_leakage(manifest, "Frozen reviewer packet manifest")
    if (
        manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("artifact") != "gold_reviewer_packets"
        or manifest.get("status") != "prepared_unanswered_blind_packets"
        or manifest.get("contract_version") != CONTRACT_VERSION
        or manifest.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or manifest.get("skipped_count") != 0
        or manifest.get("error_count") != 0
    ):
        raise ValueError("Frozen reviewer packet manifest contract/status is invalid")
    packet_sha = _sha256_file(packet_path)
    manifest_sha = _sha256_file(packet_manifest_path)
    if manifest.get("output_sha256", {}).get(packet_path.name) != packet_sha:
        raise ValueError("Frozen reviewer packet differs from its manifest")
    rows = list(_read_jsonl(packet_path))
    if not rows or sha256_lines(rows) != packet_sha:
        raise ValueError("Frozen reviewer packet is empty or not canonically serialized")
    passes = {row.get("review_pass") for row in rows}
    if len(passes) != 1 or next(iter(passes)) not in {1, 2}:
        raise ValueError("Frozen reviewer packet contains mixed/invalid pass numbers")
    review_pass = int(next(iter(passes)))
    if any(
        row.get("record_type") != "reviewer_packet_verse"
        or row.get("blind_to_other_pass") is not True
        or row.get("input_sha256") != manifest.get("input_sha256")
        for row in rows
    ):
        raise ValueError("Frozen reviewer packet row locks/contract differ")
    for row in rows:
        answer = row.get("answer_template")
        if not isinstance(answer, dict) or any(
            value not in (None, [], {}) for value in answer.values()
        ):
            raise ValueError("Frozen reviewer packet is not answer-free")
    requests = _packet_requests(rows)
    counts = manifest.get("counts", {})
    if (
        len(rows) != counts.get("selected_verses")
        or len(requests["originals"])
        != counts.get("primary_original_decisions")
        or len(requests["targets"])
        != counts.get("target_token_accounting_decisions")
        or manifest.get("processed_count") != len(rows)
    ):
        raise ValueError("Frozen reviewer packet request counts differ")
    return manifest, rows, review_pass, packet_sha, manifest_sha


def _full_packet_context(
    packet_path: Path, packet_manifest_path: Path
) -> _PacketContext:
    manifest, rows, review_pass, packet_sha, manifest_sha = _load_packet(
        packet_path, packet_manifest_path
    )
    return _PacketContext(
        manifest=manifest,
        rows=rows,
        review_pass=review_pass,
        packet_path=packet_path,
        packet_sha=packet_sha,
        packet_manifest_sha=manifest_sha,
        parent_input_sha256=dict(manifest["input_sha256"]),
        review_scope="full_packet",
        parent_packet_sha256=packet_sha,
        parent_packet_manifest_sha256=manifest_sha,
    )


def _load_shard_packet_context(
    shard_manifest_path: Path, shard_id: str
) -> _PacketContext:
    """Validate an entire frozen shard set and select one exact shard."""

    manifest = _read_json(shard_manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Frozen shard manifest is not an object")
    _assert_no_other_pass_leakage(manifest, "Frozen shard manifest")
    if (
        manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("contract_version") != CONTRACT_VERSION
        or manifest.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or manifest.get("shard_contract_version") != SHARD_CONTRACT_VERSION
        or manifest.get("artifact") != "gold_reviewer_packet_shards"
        or manifest.get("status") != "prepared_answer_free_complete_shards"
        or manifest.get("skipped_count") != 0
        or manifest.get("error_count") != 0
        or manifest.get("review_pass") not in {1, 2}
    ):
        raise ValueError("Frozen shard manifest contract/status/pass is invalid")
    review_pass = int(manifest["review_pass"])
    parent_input = manifest.get("parent_input_sha256")
    if not isinstance(parent_input, dict) or not all(
        isinstance(key, str) and _is_sha256(value)
        for key, value in parent_input.items()
    ):
        raise ValueError("Frozen shard manifest has malformed parent source locks")
    parent_packet_sha = manifest.get("parent_packet_sha256")
    parent_manifest_sha = manifest.get("parent_packet_manifest_sha256")
    if not _is_sha256(parent_packet_sha) or not _is_sha256(parent_manifest_sha):
        raise ValueError("Frozen shard manifest has malformed parent packet locks")
    expected_inputs = {
        "parent_packet": parent_packet_sha,
        "parent_packet_manifest": parent_manifest_sha,
        **{f"source_{key}": value for key, value in parent_input.items()},
    }
    if manifest.get("input_sha256") != expected_inputs:
        raise ValueError("Frozen shard manifest has stale source SHA locks")

    entries_raw = manifest.get("shards")
    if not isinstance(entries_raw, list) or not entries_raw:
        raise ValueError("Frozen shard manifest has no shard entries")
    entries: dict[str, dict[str, Any]] = {}
    for raw_entry in entries_raw:
        if not isinstance(raw_entry, dict):
            raise ValueError("Frozen shard manifest has a malformed shard entry")
        entry_id = str(raw_entry.get("shard_id", ""))
        if not entry_id or entry_id in entries:
            raise ValueError("Frozen shard manifest repeats a shard ID")
        entries[entry_id] = raw_entry
    counts = manifest.get("counts", {})
    ordinals = sorted(entry.get("ordinal") for entry in entries.values())
    if (
        len(entries) != counts.get("shards")
        or ordinals != list(range(1, len(entries) + 1))
    ):
        raise ValueError("Frozen shard manifest shard count/ordinals differ")
    if shard_id not in entries:
        raise ValueError(f"Unknown frozen reviewer packet shard: {shard_id}")

    outputs = manifest.get("output_sha256")
    expected_outputs: dict[str, str] = {}
    reconstructed: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] | None = None
    selected_path: Path | None = None
    seen_selections: set[str] = set()
    seen_original_ids: set[str] = set()
    seen_target_ids: set[str] = set()
    total_originals = 0
    total_targets = 0
    for entry in sorted(entries.values(), key=lambda value: int(value["ordinal"])):
        packet_file = entry.get("packet_file")
        if (
            not isinstance(packet_file, str)
            or not packet_file
            or Path(packet_file).name != packet_file
        ):
            raise ValueError(
                "Frozen shard packet path is not a local manifest filename"
            )
        packet_path = shard_manifest_path.parent / packet_file
        packet_sha = _sha256_file(packet_path)
        if (
            entry.get("review_pass") != review_pass
            or entry.get("packet_sha256") != packet_sha
            or not _is_sha256(packet_sha)
        ):
            raise ValueError("Frozen shard packet differs from its entry locks")
        expected_outputs[packet_file] = packet_sha
        rows = list(_read_jsonl(packet_path))
        if not rows or sha256_lines(rows) != packet_sha:
            raise ValueError("Frozen shard packet is empty or non-canonical")
        _validate_answer_free_packet_rows(
            rows,
            review_pass=review_pass,
            input_sha256=parent_input,
            label="Frozen shard packet",
        )
        requests = _packet_requests(rows)
        original_ids = {
            str(request["token_id"]) for request in requests["originals"].values()
        }
        target_ids = {
            str(request["token_id"]) for request in requests["targets"].values()
        }
        selection_values = [str(row.get("selection_id", "")) for row in rows]
        selection_ids = set(selection_values)
        if (
            "" in selection_ids
            or len(selection_ids) != len(selection_values)
            or seen_selections & selection_ids
            or seen_original_ids & original_ids
            or seen_target_ids & target_ids
        ):
            raise ValueError("Frozen shard packets overlap stable IDs")
        seen_selections.update(selection_ids)
        seen_original_ids.update(original_ids)
        seen_target_ids.update(target_ids)
        if (
            entry.get("verse_count") != len(rows)
            or entry.get("original_decision_count") != len(requests["originals"])
            or entry.get("target_accounting_count") != len(requests["targets"])
            or entry.get("first_target_ref") != rows[0].get("target_ref")
            or entry.get("last_target_ref") != rows[-1].get("target_ref")
            or set(entry.get("books", [])) != {str(row.get("book")) for row in rows}
        ):
            raise ValueError("Frozen shard packet counts/range differ from its entry")
        total_originals += len(requests["originals"])
        total_targets += len(requests["targets"])
        reconstructed.extend(rows)
        if entry["shard_id"] == shard_id:
            selected_rows = rows
            selected_path = packet_path
    if outputs != expected_outputs:
        raise ValueError("Frozen shard manifest output SHA map differs")
    if (
        sha256_lines(reconstructed) != parent_packet_sha
        or manifest.get("processed_count") != len(reconstructed)
        or counts.get("selected_verses") != len(reconstructed)
        or counts.get("primary_original_decisions") != total_originals
        or counts.get("target_token_accounting_decisions") != total_targets
    ):
        raise ValueError("Frozen shard packets do not exactly reconstruct the parent")
    if selected_rows is None or selected_path is None:  # pragma: no cover
        raise RuntimeError("Selected shard vanished during validation")
    selected = entries[shard_id]
    return _PacketContext(
        manifest=manifest,
        rows=selected_rows,
        review_pass=review_pass,
        packet_path=selected_path,
        packet_sha=str(selected["packet_sha256"]),
        packet_manifest_sha=_sha256_file(shard_manifest_path),
        parent_input_sha256=dict(parent_input),
        review_scope="shard",
        parent_packet_sha256=str(parent_packet_sha),
        parent_packet_manifest_sha256=str(parent_manifest_sha),
        shard_entry=selected,
    )


def _resolve_packet_context(
    *,
    packet_path: Path | None,
    packet_manifest_path: Path | None,
    shard_manifest_path: Path | None,
    shard_id: str | None,
) -> _PacketContext:
    shard_mode = shard_manifest_path is not None or shard_id is not None
    if shard_mode:
        if (
            shard_manifest_path is None
            or not shard_id
            or packet_path is not None
            or packet_manifest_path is not None
        ):
            raise ValueError(
                "Shard compact mode requires exactly --shard-manifest and --shard-id"
            )
        return _load_shard_packet_context(shard_manifest_path, shard_id)
    if packet_path is None or packet_manifest_path is None:
        raise ValueError("Full compact mode requires --packet and --packet-manifest")
    return _full_packet_context(packet_path, packet_manifest_path)


def _indexed_originals(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    originals = {
        str(row["original_token_id"]): row for row in packet["original_tokens"]
    }
    requests = packet.get("original_decision_requests")
    if not isinstance(requests, list):
        raise ValueError("Reviewer packet lacks original decision requests")
    width = max(3, len(str(len(requests))))
    indexed: list[dict[str, Any]] = []
    for ordinal, request in enumerate(requests, 1):
        token_id = str(request.get("original_token_id", ""))
        token = originals.get(token_id)
        if token is None:
            raise ValueError("Original request has no source token metadata")
        display = {
            field: token[field]
            for field in _ORIGINAL_DISPLAY_FIELDS
            if field in token
        }
        indexed.append(
            {
                "index": f"o{ordinal:0{width}d}",
                "decision_id": request["decision_id"],
                "original_token_id": token_id,
                "display": display,
            }
        )
    return indexed


def _indexed_targets(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    targets = {str(row["token_id"]): row for row in packet["target_tokens"]}
    requests = packet.get("target_accounting_requests")
    if not isinstance(requests, list):
        raise ValueError("Reviewer packet lacks target accounting requests")
    width = max(3, len(str(len(requests))))
    indexed: list[dict[str, Any]] = []
    for ordinal, request in enumerate(requests, 1):
        token_id = str(request.get("target_token_id", ""))
        token = targets.get(token_id)
        if token is None:
            raise ValueError("Target request has no token metadata")
        indexed.append(
            {
                "index": f"t{ordinal:0{width}d}",
                "accounting_id": request["accounting_id"],
                "target_token_id": token_id,
                "order": token["order"],
                "surface": token["surface"],
                "comparison": token["comparison"],
                "start_scalar": token["start_scalar"],
                "end_scalar": token["end_scalar"],
                "start_byte": token["start_byte"],
                "end_byte": token["end_byte"],
            }
        )
    return indexed


def _compact_artifact(context: _PacketContext) -> str:
    base = f"gold_compact_review_template_pass_{context.review_pass}"
    if context.shard_entry is None:
        return base
    return f"{base}_shard_{int(context.shard_entry['ordinal']):03d}"


def _expanded_artifact(context: _PacketContext) -> str:
    base = f"gold_compact_expanded_review_pass_{context.review_pass}"
    if context.shard_entry is None:
        return base
    return f"{base}_shard_{int(context.shard_entry['ordinal']):03d}"


def _expanded_status(context: _PacketContext) -> str:
    if context.shard_entry is None:
        return "complete_compact_expansion_ready_for_pass_ingestion"
    return "complete_compact_shard_expansion_ready_for_merge"


def _compact_inputs(context: _PacketContext) -> dict[str, str]:
    sources = {
        f"source_{key}": value
        for key, value in context.parent_input_sha256.items()
    }
    if context.shard_entry is None:
        return {
            "parent_packet": context.packet_sha,
            "parent_packet_manifest": context.packet_manifest_sha,
            **sources,
        }
    return {
        "review_packet": context.packet_sha,
        "review_packet_manifest": context.packet_manifest_sha,
        "parent_packet": context.parent_packet_sha256,
        "parent_packet_manifest": context.parent_packet_manifest_sha256,
        **sources,
    }


def _shard_locks(context: _PacketContext) -> dict[str, Any]:
    if context.shard_entry is None:
        return {}
    return {
        "review_scope": "shard",
        "shard_contract_version": SHARD_CONTRACT_VERSION,
        "shard_id": context.shard_id,
        "shard_ordinal": int(context.shard_entry["ordinal"]),
        "shard_packet_sha256": context.packet_sha,
        "shard_manifest_sha256": context.packet_manifest_sha,
        "parent_packet_sha256": context.parent_packet_sha256,
        "parent_packet_manifest_sha256": context.parent_packet_manifest_sha256,
    }


def _compact_template_rows(
    packet_rows: Sequence[Mapping[str, Any]],
    *,
    review_pass: int,
    packet_sha: str,
    packet_manifest_sha: str,
    input_sha256: Mapping[str, str],
    shard_locks: Mapping[str, Any] | None = None,
) -> Iterable[dict[str, Any]]:
    for packet in packet_rows:
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "compact_review_version": COMPACT_REVIEW_VERSION,
            "record_type": "compact_review_verse_template",
            "review_pass": review_pass,
            "blind_to_other_pass": True,
            "selection_id": packet["selection_id"],
            "target_ref": packet["target_ref"],
            "verse_key": packet["verse_key"],
            "book": packet["book"],
            "testament": packet["testament"],
            "packet_sha256": packet_sha,
            "packet_manifest_sha256": packet_manifest_sha,
            "input_sha256": dict(sorted(input_sha256.items())),
            "plain_text_nfc": packet["plain_text_nfc"],
            "target_comment": packet["target_comment"],
            "original_index": _indexed_originals(packet),
            "target_index": _indexed_targets(packet),
            "reviewer_answers": {"groups": [], "target_nulls": []},
        }
        if shard_locks:
            row.update(shard_locks)
        _assert_no_other_pass_leakage(row, "Compact template")
        _assert_no_answer_channel_keys(row, "Compact template")
        row["template_row_sha256"] = _row_sha256(row)
        yield row


def prepare_compact_review(
    *,
    packet_path: Path | None = None,
    packet_manifest_path: Path | None = None,
    shard_manifest_path: Path | None = None,
    shard_id: str | None = None,
    output_dir: Path,
) -> dict[str, Any]:
    """Create an answer-free compact template for a full packet or one shard."""

    context = _resolve_packet_context(
        packet_path=packet_path,
        packet_manifest_path=packet_manifest_path,
        shard_manifest_path=shard_manifest_path,
        shard_id=shard_id,
    )
    _assert_nonexistent(output_dir, "Compact review output directory")
    if context.shard_entry is None:
        template_name = f"review_pass_{context.review_pass}.compact.template.jsonl"
    else:
        template_name = (
            f"review_pass_{context.review_pass}."
            f"shard_{int(context.shard_entry['ordinal']):03d}.compact.template.jsonl"
        )
    template_rows = list(
        _compact_template_rows(
            context.rows,
            review_pass=context.review_pass,
            packet_sha=context.packet_sha,
            packet_manifest_sha=context.packet_manifest_sha,
            input_sha256=context.parent_input_sha256,
            shard_locks=_shard_locks(context),
        )
    )
    original_count = sum(len(row["original_index"]) for row in template_rows)
    target_count = sum(len(row["target_index"]) for row in template_rows)
    output_dir.mkdir(parents=True, exist_ok=False)
    _, template_sha = _write_jsonl(output_dir / template_name, template_rows)
    result = _manifest(
        artifact=_compact_artifact(context),
        status="prepared_answer_free_compact_review",
        inputs=_compact_inputs(context),
        outputs={template_name: template_sha},
        processed=len(template_rows),
        skipped=0,
        errors=0,
        counts={
            "selected_verses": len(template_rows),
            "primary_original_decisions": original_count,
            "target_token_accounting_decisions": target_count,
            "manual_group_answers": 0,
            "manual_target_null_answers": 0,
        },
        notes=(
            "The compact template contains local indices and no answer/candidate/legacy channel.",
            "The reviewer must explicitly fill every original group and every target null.",
            "Expansion is impossible unless all frozen SHA locks and exact accounting validate.",
        ),
    )
    result["compact_review_version"] = COMPACT_REVIEW_VERSION
    result["review_pass"] = context.review_pass
    result["parent_packet_name"] = context.manifest.get(
        "parent_packet_name", context.packet_path.name
    )
    result["parent_packet_sha256"] = context.parent_packet_sha256
    result["parent_packet_manifest_sha256"] = (
        context.parent_packet_manifest_sha256
    )
    result["parent_input_sha256"] = context.parent_input_sha256
    result["template_name"] = template_name
    if context.shard_entry is not None:
        result.update(_shard_locks(context))
        result["shard_packet_name"] = context.packet_path.name
    _write_json(output_dir / "gold_compact_review.manifest.json", result)
    return result


def _load_compact_bundle(
    *,
    packet_path: Path | None,
    packet_manifest_path: Path | None,
    shard_manifest_path: Path | None,
    shard_id: str | None,
    template_path: Path,
    compact_manifest_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], _PacketContext]:
    context = _resolve_packet_context(
        packet_path=packet_path,
        packet_manifest_path=packet_manifest_path,
        shard_manifest_path=shard_manifest_path,
        shard_id=shard_id,
    )
    compact = _read_json(compact_manifest_path)
    if not isinstance(compact, dict):
        raise ValueError("Compact review manifest is not an object")
    _assert_no_other_pass_leakage(compact, "Compact review manifest")
    if (
        compact.get("schema_version") != SCHEMA_VERSION
        or compact.get("artifact") != _compact_artifact(context)
        or compact.get("status") != "prepared_answer_free_compact_review"
        or compact.get("contract_version") != CONTRACT_VERSION
        or compact.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
        or compact.get("compact_review_version") != COMPACT_REVIEW_VERSION
        or compact.get("review_pass") != context.review_pass
        or compact.get("skipped_count") != 0
        or compact.get("error_count") != 0
    ):
        raise ValueError("Compact review manifest contract/status/pass is invalid")
    if (
        compact.get("parent_packet_sha256") != context.parent_packet_sha256
        or compact.get("parent_packet_manifest_sha256")
        != context.parent_packet_manifest_sha256
        or compact.get("parent_input_sha256") != context.parent_input_sha256
    ):
        raise ValueError("Compact review manifest has stale parent SHA locks")
    if compact.get("input_sha256") != _compact_inputs(context):
        raise ValueError("Compact review manifest has stale source SHA locks")
    if context.shard_entry is not None:
        expected_shard_locks = _shard_locks(context)
        if any(
            compact.get(key) != value
            for key, value in expected_shard_locks.items()
        ):
            raise ValueError("Compact review manifest has stale shard locks")
        if compact.get("shard_packet_name") != context.packet_path.name:
            raise ValueError("Compact review manifest selects the wrong shard packet")
    template_sha = _sha256_file(template_path)
    if compact.get("output_sha256") != {template_path.name: template_sha}:
        raise ValueError("Compact template differs from its manifest")
    templates = list(_read_jsonl(template_path))
    if not templates or sha256_lines(templates) != template_sha:
        raise ValueError("Compact template is empty or non-canonical")
    if len(templates) != len(context.rows):
        raise ValueError("Compact template verse count differs from frozen packet")
    packet_by_selection = {
        str(row["selection_id"]): row for row in context.rows
    }
    if len(packet_by_selection) != len(context.rows):
        raise ValueError("Frozen packet repeats a selection ID")
    seen: set[str] = set()
    for row in templates:
        _assert_no_other_pass_leakage(row, "Compact template")
        _assert_no_answer_channel_keys(row, "Compact template")
        selection_id = str(row.get("selection_id", ""))
        packet = packet_by_selection.get(selection_id)
        if packet is None or selection_id in seen:
            raise ValueError("Compact template has unknown/duplicate selection ID")
        seen.add(selection_id)
        locked = dict(row)
        lock = locked.pop("template_row_sha256", None)
        if lock != _row_sha256(locked):
            raise ValueError("Compact template row lock is stale/tampered")
        if (
            row.get("record_type") != "compact_review_verse_template"
            or row.get("review_pass") != context.review_pass
            or row.get("blind_to_other_pass") is not True
            or row.get("target_ref") != packet.get("target_ref")
            or row.get("packet_sha256") != context.packet_sha
            or row.get("packet_manifest_sha256") != context.packet_manifest_sha
            or row.get("input_sha256") != context.parent_input_sha256
            or row.get("reviewer_answers") != {"groups": [], "target_nulls": []}
        ):
            raise ValueError("Compact template row is stale or not answer-free")
        expected_shard_locks = _shard_locks(context)
        if any(row.get(key) != value for key, value in expected_shard_locks.items()):
            raise ValueError("Compact template row has stale shard locks")
        expected_originals = _indexed_originals(packet)
        expected_targets = _indexed_targets(packet)
        if (
            row.get("original_index") != expected_originals
            or row.get("target_index") != expected_targets
        ):
            raise ValueError("Compact template index grid differs from frozen packet")
    counts = compact.get("counts", {})
    if (
        counts.get("selected_verses") != len(templates)
        or counts.get("primary_original_decisions")
        != sum(len(row["original_index"]) for row in templates)
        or counts.get("target_token_accounting_decisions")
        != sum(len(row["target_index"]) for row in templates)
        or counts.get("manual_group_answers") != 0
        or counts.get("manual_target_null_answers") != 0
        or compact.get("processed_count") != len(templates)
    ):
        raise ValueError("Compact template counts are stale")
    return compact, templates, context


def _validate_group(
    group: Mapping[str, Any],
    *,
    originals: Mapping[str, Mapping[str, Any]],
    targets: Mapping[str, Mapping[str, Any]],
) -> tuple[list[str], list[str]]:
    _require_exact_keys(
        group,
        {
            "original_indices",
            "target_indices",
            "relation",
            "null_reason",
            "severity",
            "phenomena",
            "evidence",
            "rationale",
        },
        "Compact manual group",
    )
    original_indices = group.get("original_indices")
    target_indices = group.get("target_indices")
    if (
        not isinstance(original_indices, list)
        or not original_indices
        or len(set(original_indices)) != len(original_indices)
        or any(index not in originals for index in original_indices)
    ):
        raise ValueError("Compact manual group has invalid/non-local original indices")
    if (
        not isinstance(target_indices, list)
        or len(set(target_indices)) != len(target_indices)
        or any(index not in targets for index in target_indices)
    ):
        raise ValueError("Compact manual group has invalid/non-local target indices")
    relation = group.get("relation")
    if relation not in ALLOWED_RELATIONS:
        raise ValueError("Compact manual group has an unknown relation")
    cardinality = (len(original_indices), len(target_indices))
    null_reason = group.get("null_reason")
    if relation == "original_omitted":
        if cardinality != (1, 0) or null_reason not in ALLOWED_NULL_REASONS:
            raise ValueError("Compact original omission cardinality/reason is invalid")
    else:
        if not target_indices or null_reason is not None:
            raise ValueError("Compact non-null group requires targets and null_reason=null")
        if relation == "one_to_one" and cardinality != (1, 1):
            raise ValueError("Compact one_to_one cardinality mismatch")
        if relation == "one_to_many" and not (
            cardinality[0] == 1 and cardinality[1] >= 2
        ):
            raise ValueError("Compact one_to_many cardinality mismatch")
        if relation == "many_to_one" and not (
            cardinality[0] >= 2 and cardinality[1] == 1
        ):
            raise ValueError("Compact many_to_one cardinality mismatch")
        if relation == "many_to_many" and not (
            cardinality[0] >= 2 and cardinality[1] >= 2
        ):
            raise ValueError("Compact many_to_many cardinality mismatch")
        if relation == "grouped_expression" and not (
            cardinality[0] >= 1 and cardinality[1] >= 1
        ):
            raise ValueError("Compact grouped_expression cardinality mismatch")
    if group.get("severity") not in ALLOWED_SEVERITIES:
        raise ValueError("Compact manual group severity is invalid")
    if not isinstance(group.get("phenomena"), list) or any(
        not isinstance(item, str) or not item.strip()
        for item in group["phenomena"]
    ):
        raise ValueError("Compact manual group phenomena are malformed")
    if not _evidence_ok(group.get("evidence")) or not str(
        group.get("rationale", "")
    ).strip():
        raise ValueError("Compact manual group lacks evidence/rationale")
    if any(set(item) != {"kind", "evidence_id"} for item in group["evidence"]):
        raise ValueError("Compact manual group evidence has hidden/prohibited fields")
    return list(original_indices), list(target_indices)


def _validate_target_null(
    row: Mapping[str, Any], targets: Mapping[str, Mapping[str, Any]]
) -> str:
    _require_exact_keys(
        row,
        {
            "target_index",
            "target_status",
            "severity",
            "phenomena",
            "evidence",
            "rationale",
        },
        "Compact target null",
    )
    target_index = row.get("target_index")
    if target_index not in targets:
        raise ValueError("Compact target null has an invalid/non-local target index")
    if row.get("target_status") not in ALLOWED_TARGET_STATUSES - {"aligned"}:
        raise ValueError("Compact target null status must be addition/function_token")
    if row.get("severity") not in ALLOWED_SEVERITIES:
        raise ValueError("Compact target null severity is invalid")
    if not isinstance(row.get("phenomena"), list) or any(
        not isinstance(item, str) or not item.strip()
        for item in row["phenomena"]
    ):
        raise ValueError("Compact target null phenomena are malformed")
    if not _evidence_ok(row.get("evidence")) or not str(
        row.get("rationale", "")
    ).strip():
        raise ValueError("Compact target null lacks evidence/rationale")
    if any(set(item) != {"kind", "evidence_id"} for item in row["evidence"]):
        raise ValueError("Compact target null evidence has hidden/prohibited fields")
    return str(target_index)


def _expanded_rows(
    *,
    filled_rows: Sequence[Mapping[str, Any]],
    templates: Sequence[Mapping[str, Any]],
    packet_rows: Sequence[Mapping[str, Any]],
    review_pass: int,
    reviewer_id: str,
    packet_sha: str,
    packet_manifest_sha: str,
    parent_input_sha256: Mapping[str, str],
    compact_template_sha: str,
    compact_manifest_sha: str,
) -> tuple[list[dict[str, Any]], int, int]:
    template_by_id = {str(row["selection_id"]): row for row in templates}
    packet_by_id = {str(row["selection_id"]): row for row in packet_rows}
    answers: dict[str, Mapping[str, Any]] = {}
    allowed_submission_keys = {
        "schema_version",
        "contract_version",
        "compact_review_version",
        "record_type",
        "selection_id",
        "target_ref",
        "template_row_sha256",
        "reviewer_id",
        "groups",
        "target_nulls",
    }
    for row in filled_rows:
        _require_exact_keys(row, allowed_submission_keys, "Compact verse submission")
        selection_id = str(row.get("selection_id", ""))
        template = template_by_id.get(selection_id)
        if template is None or selection_id in answers:
            raise ValueError("Compact response has unknown/duplicate verse submission")
        if (
            row.get("record_type") != "compact_review_verse_submission"
            or row.get("schema_version") != SCHEMA_VERSION
            or row.get("contract_version") != CONTRACT_VERSION
            or row.get("compact_review_version") != COMPACT_REVIEW_VERSION
            or row.get("target_ref") != template["target_ref"]
            or row.get("template_row_sha256") != template["template_row_sha256"]
            or row.get("reviewer_id") != reviewer_id
        ):
            raise ValueError("Compact verse submission identity/pass locks are stale")
        if not isinstance(row.get("groups"), list) or not isinstance(
            row.get("target_nulls"), list
        ):
            raise ValueError("Compact verse submission lacks explicit answer arrays")
        answers[selection_id] = row
    if set(answers) != set(template_by_id):
        raise ValueError("Compact response does not contain every verse exactly once")

    original_rows: dict[str, dict[str, Any]] = {}
    target_rows: dict[str, dict[str, Any]] = {}
    manual_group_count = 0
    manual_target_null_count = 0
    for selection_id in sorted(template_by_id):
        template = template_by_id[selection_id]
        packet = packet_by_id[selection_id]
        answer = answers[selection_id]
        originals = {row["index"]: row for row in template["original_index"]}
        targets = {row["index"]: row for row in template["target_index"]}
        used_originals: set[str] = set()
        used_targets: set[str] = set()
        target_group: dict[str, Mapping[str, Any]] = {}
        for group in answer["groups"]:
            if not isinstance(group, dict):
                raise ValueError("Compact manual group is not an object")
            original_indices, target_indices = _validate_group(
                group, originals=originals, targets=targets
            )
            if used_originals.intersection(original_indices):
                raise ValueError("An original index is manually accounted more than once")
            if used_targets.intersection(target_indices):
                raise ValueError("A target index is manually accounted more than once")
            used_originals.update(original_indices)
            used_targets.update(target_indices)
            original_ids = [originals[index]["original_token_id"] for index in original_indices]
            target_ids = [targets[index]["target_token_id"] for index in target_indices]
            for index in original_indices:
                indexed = originals[index]
                expanded = {
                    "schema_version": SCHEMA_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                    "compact_review_version": COMPACT_REVIEW_VERSION,
                    "record_type": "original_decision",
                    "decision_status": "decided",
                    "decision_id": indexed["decision_id"],
                    "original_token_id": indexed["original_token_id"],
                    "target_ref": template["target_ref"],
                    "relation": group["relation"],
                    "group_original_token_ids": original_ids,
                    "target_token_ids": target_ids,
                    "null_reason": group["null_reason"],
                    "severity": group["severity"],
                    "phenomena": group["phenomena"],
                    "evidence": group["evidence"],
                    "rationale": group["rationale"],
                    "reviewer_id": reviewer_id,
                }
                original_rows[str(indexed["decision_id"])] = expanded
            for index in target_indices:
                target_group[index] = group
            manual_group_count += 1
        if used_originals != set(originals):
            raise ValueError("Compact response lacks exact-once original accounting")

        null_by_target: dict[str, Mapping[str, Any]] = {}
        for target_null in answer["target_nulls"]:
            if not isinstance(target_null, dict):
                raise ValueError("Compact target null is not an object")
            index = _validate_target_null(target_null, targets)
            if index in used_targets or index in null_by_target:
                raise ValueError("A target index is manually accounted more than once")
            null_by_target[index] = target_null
            used_targets.add(index)
            manual_target_null_count += 1
        if used_targets != set(targets):
            raise ValueError("Compact response lacks exact-once target accounting")
        for index, indexed in targets.items():
            group = target_group.get(index)
            target_null = null_by_target.get(index)
            if group is not None:
                linked_original_ids = [
                    originals[value]["original_token_id"]
                    for value in group["original_indices"]
                ]
                status = "aligned"
                evidence = group["evidence"]
                rationale = group["rationale"]
                severity = group["severity"]
                phenomena = group["phenomena"]
            elif target_null is not None:
                linked_original_ids = []
                status = target_null["target_status"]
                evidence = target_null["evidence"]
                rationale = target_null["rationale"]
                severity = target_null["severity"]
                phenomena = target_null["phenomena"]
            else:  # guarded by exact accounting; retained as fail-closed invariant.
                raise RuntimeError("Target accounting vanished during expansion")
            target_rows[str(indexed["accounting_id"])] = {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "gold_workflow_version": GOLD_WORKFLOW_VERSION,
                "compact_review_version": COMPACT_REVIEW_VERSION,
                "record_type": "target_accounting",
                "decision_status": "decided",
                "accounting_id": indexed["accounting_id"],
                "target_token_id": indexed["target_token_id"],
                "target_ref": template["target_ref"],
                "target_status": status,
                "linked_original_token_ids": linked_original_ids,
                "severity": severity,
                "phenomena": phenomena,
                "evidence": evidence,
                "rationale": rationale,
                "reviewer_id": reviewer_id,
            }

    requests = _packet_requests(packet_rows)
    if set(original_rows) != set(requests["originals"]):
        raise ValueError("Expanded response differs from frozen original request IDs")
    if set(target_rows) != set(requests["targets"]):
        raise ValueError("Expanded response differs from frozen target request IDs")
    for key, row in original_rows.items():
        _validate_original_decision(row, requests["originals"][key], requests)
    for key, row in target_rows.items():
        _validate_target_accounting(row, requests["targets"][key], requests)
    _validate_semantic_accounting(original_rows, target_rows)

    output: list[dict[str, Any]] = [
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "compact_review_version": COMPACT_REVIEW_VERSION,
            "record_type": "review_metadata",
            "review_pass": review_pass,
            "reviewer_id": reviewer_id,
            "reviewer_mode": "single",
            "reviewer_roster": [],
            "blind_to_other_pass": True,
            "packet_sha256": packet_sha,
            "packet_manifest_sha256": packet_manifest_sha,
            "input_sha256": dict(sorted(parent_input_sha256.items())),
            "compact_template_sha256": compact_template_sha,
            "compact_manifest_sha256": compact_manifest_sha,
        }
    ]
    output.extend(original_rows[key] for key in sorted(original_rows))
    output.extend(target_rows[key] for key in sorted(target_rows))
    return output, manual_group_count, manual_target_null_count


def expand_compact_review(
    *,
    packet_path: Path | None = None,
    packet_manifest_path: Path | None = None,
    shard_manifest_path: Path | None = None,
    shard_id: str | None = None,
    template_path: Path,
    compact_manifest_path: Path,
    filled_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Validate manual compact answers and emit an ingest-compatible pass."""

    compact, templates, context = _load_compact_bundle(
        packet_path=packet_path,
        packet_manifest_path=packet_manifest_path,
        shard_manifest_path=shard_manifest_path,
        shard_id=shard_id,
        template_path=template_path,
        compact_manifest_path=compact_manifest_path,
    )
    _assert_nonexistent(output_path, "Expanded compact review")
    sidecar_path = Path(str(output_path) + ".manifest.json")
    _assert_nonexistent(sidecar_path, "Expanded compact review sidecar")
    rows = list(_read_jsonl(filled_path))
    metadata_rows = [
        row for row in rows if row.get("record_type") == "compact_review_metadata"
    ]
    if len(metadata_rows) != 1:
        raise ValueError("Compact response requires exactly one metadata row")
    metadata = metadata_rows[0]
    metadata_keys = {
            "schema_version",
            "contract_version",
            "compact_review_version",
            "record_type",
            "review_pass",
            "reviewer_id",
            "blind_to_other_pass",
            "packet_sha256",
            "packet_manifest_sha256",
            "input_sha256",
            "compact_template_sha256",
            "compact_manifest_sha256",
    }
    if context.shard_entry is not None:
        metadata_keys.update(_shard_locks(context))
    _require_exact_keys(metadata, metadata_keys, "Compact review metadata")
    _assert_no_other_pass_leakage(metadata, "Compact review metadata")
    reviewer_id = _require_reviewer_id(metadata.get("reviewer_id"))
    template_sha = _sha256_file(template_path)
    compact_manifest_sha = _sha256_file(compact_manifest_path)
    if (
        metadata.get("schema_version") != SCHEMA_VERSION
        or metadata.get("contract_version") != CONTRACT_VERSION
        or metadata.get("compact_review_version") != COMPACT_REVIEW_VERSION
        or metadata.get("review_pass") != context.review_pass
        or metadata.get("blind_to_other_pass") is not True
        or metadata.get("packet_sha256") != context.packet_sha
        or metadata.get("packet_manifest_sha256") != context.packet_manifest_sha
        or metadata.get("input_sha256") != compact.get("parent_input_sha256")
        or metadata.get("compact_template_sha256") != template_sha
        or metadata.get("compact_manifest_sha256") != compact_manifest_sha
    ):
        raise ValueError("Compact review metadata has stale identity/pass/SHA locks")
    if context.shard_entry is not None and any(
        metadata.get(key) != value for key, value in _shard_locks(context).items()
    ):
        raise ValueError("Compact review metadata has stale shard/pass/SHA locks")
    filled_verses = [
        row for row in rows if row.get("record_type") != "compact_review_metadata"
    ]
    output_rows, group_count, target_null_count = _expanded_rows(
        filled_rows=filled_verses,
        templates=templates,
        packet_rows=context.rows,
        review_pass=context.review_pass,
        reviewer_id=reviewer_id,
        packet_sha=context.packet_sha,
        packet_manifest_sha=context.packet_manifest_sha,
        parent_input_sha256=compact["parent_input_sha256"],
        compact_template_sha=template_sha,
        compact_manifest_sha=compact_manifest_sha,
    )
    if context.shard_entry is not None:
        output_rows[0].update(_shard_locks(context))
        output_rows[0]["reviewer_mode"] = "single_shard"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count, output_sha = _write_jsonl(output_path, output_rows)
    result = _manifest(
        artifact=_expanded_artifact(context),
        status=_expanded_status(context),
        inputs={
            **_compact_inputs(context),
            "compact_template": template_sha,
            "compact_manifest": compact_manifest_sha,
            "manual_compact_submission": _sha256_file(filled_path),
        },
        outputs={output_path.name: output_sha},
        processed=count - 1,
        skipped=0,
        errors=0,
        counts={
            "selected_verses": len(templates),
            "original_decisions": sum(
                1 for row in output_rows if row.get("record_type") == "original_decision"
            ),
            "target_accounting": sum(
                1 for row in output_rows if row.get("record_type") == "target_accounting"
            ),
            "manual_groups": group_count,
            "manual_target_nulls": target_null_count,
            "reviewers": 1,
        },
        notes=(
            "Every emitted decision is a deterministic expansion of an explicit "
            "manual compact answer.",
            (
                "The output schema is accepted unchanged by merge_review_shards."
                if context.shard_entry is not None
                else "The output schema is accepted unchanged by ingest_review_pass."
            ),
            "No candidate, legacy or other-pass data entered the expansion.",
        ),
    )
    result["compact_review_version"] = COMPACT_REVIEW_VERSION
    result["review_pass"] = context.review_pass
    result["reviewer_id"] = reviewer_id
    if context.shard_entry is not None:
        result.update(_shard_locks(context))
    _write_json(sidecar_path, result)
    return result


def check_compact_review(
    *,
    packet_path: Path | None = None,
    packet_manifest_path: Path | None = None,
    shard_manifest_path: Path | None = None,
    shard_id: str | None = None,
    template_path: Path,
    compact_manifest_path: Path,
    expanded_path: Path | None = None,
) -> dict[str, Any]:
    """Verify a compact bundle and, optionally, an expanded raw submission."""

    compact, templates, context = _load_compact_bundle(
        packet_path=packet_path,
        packet_manifest_path=packet_manifest_path,
        shard_manifest_path=shard_manifest_path,
        shard_id=shard_id,
        template_path=template_path,
        compact_manifest_path=compact_manifest_path,
    )
    processed = len(templates)
    status = (
        "valid_answer_free_compact_shard_review"
        if context.shard_entry is not None
        else "valid_answer_free_compact_review"
    )
    outputs: dict[str, str] = {template_path.name: _sha256_file(template_path)}
    if expanded_path is not None:
        sidecar_path = Path(str(expanded_path) + ".manifest.json")
        if not sidecar_path.is_file():
            raise ValueError("Expanded compact review lacks its digest sidecar")
        sidecar = _read_json(sidecar_path)
        if not isinstance(sidecar, dict):
            raise ValueError("Expanded compact review sidecar is not an object")
        _assert_no_other_pass_leakage(
            sidecar, "Expanded compact review sidecar"
        )
        expanded_sha = _sha256_file(expanded_path)
        if (
            sidecar.get("schema_version") != SCHEMA_VERSION
            or sidecar.get("contract_version") != CONTRACT_VERSION
            or sidecar.get("gold_workflow_version") != GOLD_WORKFLOW_VERSION
            or sidecar.get("artifact") != _expanded_artifact(context)
            or sidecar.get("status") != _expanded_status(context)
            or sidecar.get("compact_review_version") != COMPACT_REVIEW_VERSION
            or sidecar.get("review_pass") != context.review_pass
            or sidecar.get("skipped_count") != 0
            or sidecar.get("error_count") != 0
            or sidecar.get("output_sha256") != {expanded_path.name: expanded_sha}
            or sidecar.get("input_sha256", {}).get("compact_template")
            != _sha256_file(template_path)
            or sidecar.get("input_sha256", {}).get("compact_manifest")
            != _sha256_file(compact_manifest_path)
        ):
            raise ValueError("Expanded compact review differs from its SHA chain")
        if context.shard_entry is not None and any(
            sidecar.get(key) != value for key, value in _shard_locks(context).items()
        ):
            raise ValueError("Expanded compact review sidecar has stale shard locks")
        rows = list(_read_jsonl(expanded_path))
        metadata = [row for row in rows if row.get("record_type") == "review_metadata"]
        if len(metadata) != 1:
            raise ValueError("Expanded compact review lacks exact metadata")
        reviewer_id = _require_reviewer_id(metadata[0].get("reviewer_id"))
        expected_reviewer_mode = (
            "single_shard" if context.shard_entry is not None else "single"
        )
        if (
            metadata[0].get("review_pass") != context.review_pass
            or metadata[0].get("reviewer_mode") != expected_reviewer_mode
            or metadata[0].get("blind_to_other_pass") is not True
            or metadata[0].get("packet_sha256") != context.packet_sha
            or metadata[0].get("packet_manifest_sha256")
            != context.packet_manifest_sha
            or metadata[0].get("input_sha256") != compact["parent_input_sha256"]
            or sidecar.get("reviewer_id") != reviewer_id
        ):
            raise ValueError("Expanded compact review metadata is stale")
        _assert_no_other_pass_leakage(metadata[0], "Expanded compact review metadata")
        if context.shard_entry is not None and any(
            metadata[0].get(key) != value
            for key, value in _shard_locks(context).items()
        ):
            raise ValueError("Expanded compact review metadata has stale shard locks")
        requests = _packet_requests(context.rows)
        originals: dict[str, dict[str, Any]] = {}
        targets: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row.get("record_type") == "original_decision":
                key = str(row.get("decision_id", ""))
                if key in originals or key not in requests["originals"]:
                    raise ValueError("Expanded review repeats/introduces an original decision")
                if row.get("reviewer_id") != reviewer_id:
                    raise ValueError("Expanded original reviewer identity drifted")
                _validate_original_decision(row, requests["originals"][key], requests)
                originals[key] = row
            elif row.get("record_type") == "target_accounting":
                key = str(row.get("accounting_id", ""))
                if key in targets or key not in requests["targets"]:
                    raise ValueError("Expanded review repeats/introduces target accounting")
                if row.get("reviewer_id") != reviewer_id:
                    raise ValueError("Expanded target reviewer identity drifted")
                _validate_target_accounting(row, requests["targets"][key], requests)
                targets[key] = row
            elif row.get("record_type") != "review_metadata":
                raise ValueError("Expanded compact review has an unknown row type")
        if set(originals) != set(requests["originals"]) or set(targets) != set(
            requests["targets"]
        ):
            raise ValueError("Expanded compact review lacks exact request accounting")
        _validate_semantic_accounting(originals, targets)
        expected_sidecar_inputs = {
            **_compact_inputs(context),
            "compact_template": _sha256_file(template_path),
            "compact_manifest": _sha256_file(compact_manifest_path),
        }
        actual_sidecar_inputs = sidecar.get("input_sha256")
        if not isinstance(actual_sidecar_inputs, dict):
            raise ValueError("Expanded compact review sidecar input locks are malformed")
        manual_submission_sha = actual_sidecar_inputs.get(
            "manual_compact_submission"
        )
        if not _is_sha256(manual_submission_sha):
            raise ValueError("Expanded compact review manual-submission lock is invalid")
        expected_sidecar_inputs["manual_compact_submission"] = manual_submission_sha
        if actual_sidecar_inputs != expected_sidecar_inputs:
            raise ValueError("Expanded compact review sidecar source locks are stale")
        expected_counts = {
            "selected_verses": len(templates),
            "original_decisions": len(originals),
            "target_accounting": len(targets),
            "manual_groups": sidecar.get("counts", {}).get("manual_groups"),
            "manual_target_nulls": sidecar.get("counts", {}).get(
                "manual_target_nulls"
            ),
            "reviewers": 1,
        }
        if (
            sidecar.get("processed_count") != len(originals) + len(targets)
            or sidecar.get("counts") != expected_counts
            or not isinstance(expected_counts["manual_groups"], int)
            or expected_counts["manual_groups"] < 0
            or not isinstance(expected_counts["manual_target_nulls"], int)
            or expected_counts["manual_target_nulls"] < 0
        ):
            raise ValueError("Expanded compact review sidecar counts are stale")
        processed += len(originals) + len(targets)
        outputs[expanded_path.name] = expanded_sha
        status = (
            "valid_compact_shard_review_and_merge_ready_expansion"
            if context.shard_entry is not None
            else "valid_compact_review_and_ingest_ready_expansion"
        )
    if context.shard_entry is None:
        check_inputs = {
            "parent_packet": context.packet_sha,
            "parent_packet_manifest": context.packet_manifest_sha,
            "compact_manifest": _sha256_file(compact_manifest_path),
        }
    else:
        check_inputs = {
            **_compact_inputs(context),
            "compact_manifest": _sha256_file(compact_manifest_path),
        }
    result = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "gold_workflow_version": GOLD_WORKFLOW_VERSION,
        "compact_review_version": COMPACT_REVIEW_VERSION,
        "status": status,
        "input_sha256": check_inputs,
        "output_sha256": dict(sorted(outputs.items())),
        "processed_count": processed,
        "skipped_count": 0,
        "error_count": 0,
    }
    if context.shard_entry is not None:
        result.update(_shard_locks(context))
    return result


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="prepare an answer-free compact template")
    prepare.add_argument("--packet", type=Path)
    prepare.add_argument("--packet-manifest", type=Path)
    prepare.add_argument("--shard-manifest", type=Path)
    prepare.add_argument("--shard-id")
    prepare.add_argument("--output-dir", type=Path, required=True)
    expand = commands.add_parser("expand", help="expand a complete manual compact response")
    expand.add_argument("--packet", type=Path)
    expand.add_argument("--packet-manifest", type=Path)
    expand.add_argument("--shard-manifest", type=Path)
    expand.add_argument("--shard-id")
    expand.add_argument("--template", type=Path, required=True)
    expand.add_argument("--compact-manifest", type=Path, required=True)
    expand.add_argument("--filled", type=Path, required=True)
    expand.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check", help="verify compact SHA/accounting locks")
    check.add_argument("--packet", type=Path)
    check.add_argument("--packet-manifest", type=Path)
    check.add_argument("--shard-manifest", type=Path)
    check.add_argument("--shard-id")
    check.add_argument("--template", type=Path, required=True)
    check.add_argument("--compact-manifest", type=Path, required=True)
    check.add_argument("--expanded", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "prepare":
        result = prepare_compact_review(
            packet_path=args.packet,
            packet_manifest_path=args.packet_manifest,
            shard_manifest_path=args.shard_manifest,
            shard_id=args.shard_id,
            output_dir=args.output_dir,
        )
    elif args.command == "expand":
        result = expand_compact_review(
            packet_path=args.packet,
            packet_manifest_path=args.packet_manifest,
            shard_manifest_path=args.shard_manifest,
            shard_id=args.shard_id,
            template_path=args.template,
            compact_manifest_path=args.compact_manifest,
            filled_path=args.filled,
            output_path=args.output,
        )
    else:
        result = check_compact_review(
            packet_path=args.packet,
            packet_manifest_path=args.packet_manifest,
            shard_manifest_path=args.shard_manifest,
            shard_id=args.shard_id,
            template_path=args.template,
            compact_manifest_path=args.compact_manifest,
            expanded_path=args.expanded,
        )
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

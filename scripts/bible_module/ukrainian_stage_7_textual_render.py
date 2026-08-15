"""Fail-closed render validation for the five post-candidate textual choices.

The candidate layer deliberately excludes the eventual textual decision.  A
separate gold-selected layer replaces each unresolved c01/c06 choice with one
reviewed overlay token.  This module is the downstream boundary: it joins that
overlay to finalized gold hyperedges and target accounting, then emits only
the Strong markers which the reviewed overlay itself is allowed to render.

It does not score candidates, choose a reading, mutate gold, or render verse
text.  The returned marker rows are therefore safe input to a later markup
builder only after this validator succeeds.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    sha256_text,
    validate_classic_strong,
)


TEXTUAL_RENDER_VALIDATOR_VERSION = (
    "ukrainian-stage-7-post-candidate-textual-render-v1"
)

_NO_RENDER_DISPOSITION = (
    "resolved_manual_textual_alternative_group_no_rendered_strong"
)
_PRIMARY_COMPONENT_DISPOSITION = "resolved_manual_b_primary_component"
_STRONG_EQUIVALENT_DISPOSITION = (
    "resolved_manual_textual_alternative_group_strong_equivalent"
)
_ALLOWED_DISPOSITIONS = frozenset(
    {
        _NO_RENDER_DISPOSITION,
        _PRIMARY_COMPONENT_DISPOSITION,
        _STRONG_EQUIVALENT_DISPOSITION,
    }
)


# This is an independent downstream lock, not an input to candidate
# generation.  Keeping the exact IDs and spans here makes stale regeneration
# fail before any Strong marker can be handed to the renderer.
PRODUCTION_POST_CANDIDATE_TEXTUAL_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "Mark.1.2": {
        "overlay_original_token_id": (
            "gold7:textual-choice:"
            "d3d705eb5179703214998d7d1954ce76dbf07e18ba501d74340ecc90ee511c9e"
        ),
        "member_original_token_ids": [
            "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:c01",
            "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:alternative:tagnt-c06:01",
        ],
        "excluded_lexical_candidate_ids": [
            "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:alternative:tagnt-c12:01"
        ],
        "target_span": {
            "token_id": "uk7:IOQ:001:0:2",
            "surface": "Як",
            "start_scalar": 0,
            "end_scalar": 2,
            "start_byte": 0,
            "end_byte": 4,
        },
        "disposition": _NO_RENDER_DISPOSITION,
        "rendered_strong": [],
    },
    "Mark.16.9": {
        "overlay_original_token_id": (
            "gold7:textual-choice:"
            "ca45c9262c32ceb6eaafe5c7eff3bca6e8684cfa7dff9d8a912c8c625a8d6bdf"
        ),
        "member_original_token_ids": [
            "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:c01",
            "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:alternative:tagnt-c06:01",
        ],
        "excluded_lexical_candidate_ids": [
            "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:alternative:tagnt-c12:01"
        ],
        "target_span": {
            "token_id": "uk7:J77:014:82:84",
            "surface": "із",
            "start_scalar": 82,
            "end_scalar": 84,
            "start_byte": 148,
            "end_byte": 152,
        },
        "disposition": _NO_RENDER_DISPOSITION,
        "rendered_strong": [],
    },
    "Acts.2.38": {
        "overlay_original_token_id": (
            "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:c01"
        ),
        "member_original_token_ids": [
            "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:c01",
            "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:alternative:tagnt-c06:01",
        ],
        "excluded_lexical_candidate_ids": [
            "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:alternative:tagnt-c12:01"
        ],
        "target_span": {
            "token_id": "uk7:KTO:014:69:70",
            "surface": "у",
            "start_scalar": 69,
            "end_scalar": 70,
            "start_byte": 124,
            "end_byte": 126,
        },
        "disposition": _PRIMARY_COMPONENT_DISPOSITION,
        "rendered_strong": ["G1909"],
    },
    "1Cor.14.34": {
        "overlay_original_token_id": (
            "gold7:textual-choice:"
            "64d8e4db296bc06c1f302129d8c04f29139444e4ae942cf90e698f2369972d4a"
        ),
        "member_original_token_ids": [
            "tagnt:61666077ea81e467ffe1fe7b8e659c098d3ae332557bb4c58b93a084ca98e0ba:c01",
            "tagnt:61666077ea81e467ffe1fe7b8e659c098d3ae332557bb4c58b93a084ca98e0ba:alternative:tagnt-c06:01",
        ],
        "excluded_lexical_candidate_ids": [],
        "target_span": {
            "token_id": "uk7:M5L:011:53:62",
            "surface": "позволено",
            "start_scalar": 53,
            "end_scalar": 62,
            "start_byte": 95,
            "end_byte": 113,
        },
        "disposition": _STRONG_EQUIVALENT_DISPOSITION,
        "rendered_strong": ["G2010"],
    },
    "Rev.22.19": {
        "overlay_original_token_id": (
            "gold7:textual-choice:"
            "b09c46f13734e416fb1a33503cb72a58a3c870c122aa543d1eb93e7408a134ff"
        ),
        "member_original_token_ids": [
            "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:c01",
            "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:alternative:tagnt-c06:01",
        ],
        "excluded_lexical_candidate_ids": [
            "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:alternative:tagnt-c12:01"
        ],
        "target_span": {
            "token_id": "uk7:NZW:008:32:37",
            "surface": "книги",
            "start_scalar": 32,
            "end_scalar": 37,
            "start_byte": 57,
            "end_byte": 67,
        },
        "disposition": _NO_RENDER_DISPOSITION,
        "rendered_strong": [],
    },
}


def production_post_candidate_textual_expectations() -> dict[str, dict[str, Any]]:
    """Return a defensive copy of the frozen production expectations."""

    return deepcopy(PRODUCTION_POST_CANDIDATE_TEXTUAL_EXPECTATIONS)


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row {line_number} is not an object")
            yield value


def _string_list(value: Any, *, label: str, allow_empty: bool = True) -> list[str]:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != len(value)
    ):
        raise ValueError(f"{label} must be a duplicate-free string list")
    return list(value)


def _validate_span(value: Any, *, label: str) -> dict[str, Any]:
    expected_keys = {
        "token_id",
        "surface",
        "start_scalar",
        "end_scalar",
        "start_byte",
        "end_byte",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ValueError(f"{label} has a stale or malformed field set")
    token_id = value["token_id"]
    surface = value["surface"]
    offsets = [
        value["start_scalar"],
        value["end_scalar"],
        value["start_byte"],
        value["end_byte"],
    ]
    if (
        not isinstance(token_id, str)
        or not token_id
        or not isinstance(surface, str)
        or not surface
        or any(not isinstance(offset, int) or isinstance(offset, bool) for offset in offsets)
        or value["start_scalar"] < 0
        or value["start_byte"] < 0
        or value["end_scalar"] - value["start_scalar"] != len(surface)
        or value["end_byte"] - value["start_byte"] != len(surface.encode("utf-8"))
    ):
        raise ValueError(f"{label} has invalid exact surface offsets")
    return dict(value)


def _accounting_span(target_span: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "start_scalar": target_span["start_scalar"],
        "end_scalar": target_span["end_scalar"],
        "start_byte": target_span["start_byte"],
        "end_byte": target_span["end_byte"],
        "surface_sha256": sha256_text(str(target_span["surface"])),
    }


def _validate_expectations(
    expectations: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    if not isinstance(expectations, Mapping) or not expectations:
        raise ValueError("Textual render expectations are empty or malformed")
    normalized: dict[str, dict[str, Any]] = {}
    all_members: set[str] = set()
    all_excluded_lexical: set[str] = set()
    for ref in sorted(expectations):
        spec = expectations[ref]
        if not isinstance(ref, str) or not ref or not isinstance(spec, Mapping):
            raise ValueError("Textual render expectation ref/spec is malformed")
        overlay_id = spec.get("overlay_original_token_id")
        if not isinstance(overlay_id, str) or not overlay_id:
            raise ValueError(f"Textual overlay ID is malformed at {ref}")
        members = _string_list(
            spec.get("member_original_token_ids"),
            label=f"Textual member IDs at {ref}",
            allow_empty=False,
        )
        if len(members) != 2 or all_members.intersection(members):
            raise ValueError(f"Textual alternatives are lost or duplicated at {ref}")
        all_members.update(members)
        excluded_lexical = _string_list(
            spec.get("excluded_lexical_candidate_ids", []),
            label=f"Excluded lexical candidate IDs at {ref}",
        )
        if all_excluded_lexical.intersection(excluded_lexical):
            raise ValueError("An excluded lexical candidate is reused across loci")
        all_excluded_lexical.update(excluded_lexical)
        disposition = spec.get("disposition")
        if disposition not in _ALLOWED_DISPOSITIONS:
            raise ValueError(f"Unknown textual disposition at {ref}")
        rendered = _string_list(
            spec.get("rendered_strong"), label=f"Rendered Strong at {ref}"
        )
        if any(not validate_classic_strong(value) for value in rendered):
            raise ValueError(f"Invalid classic Strong in expectation at {ref}")
        if disposition == _NO_RENDER_DISPOSITION and rendered:
            raise ValueError(f"No-render expectation carries a Strong at {ref}")
        if disposition == _PRIMARY_COMPONENT_DISPOSITION:
            if overlay_id != members[0] or rendered != ["G1909"]:
                raise ValueError("Primary-component expectation must select only G1909")
        if disposition == _STRONG_EQUIVALENT_DISPOSITION:
            if overlay_id in members or rendered != ["G2010"]:
                raise ValueError("Strong-equivalent expectation must render one G2010")
        normalized[ref] = {
            "overlay_original_token_id": overlay_id,
            "member_original_token_ids": members,
            "excluded_lexical_candidate_ids": excluded_lexical,
            "target_span": _validate_span(
                spec.get("target_span"), label=f"Expected target span at {ref}"
            ),
            "disposition": disposition,
            "rendered_strong": rendered,
        }
    if all_members & all_excluded_lexical:
        raise ValueError("A textual member is also classified as a lexical candidate")
    return normalized


def validate_post_candidate_textual_render_contract(
    *,
    selected_original_rows: Iterable[Mapping[str, Any]],
    finalized_gold_rows: Iterable[Mapping[str, Any]],
    expectations: Mapping[str, Mapping[str, Any]] = (
        PRODUCTION_POST_CANDIDATE_TEXTUAL_EXPECTATIONS
    ),
) -> dict[str, Any]:
    """Validate overlays against finalized gold and return render marker rows.

    All stale IDs, dangling IDs, duplicate accounting and verse crossings raise
    ``ValueError``.  No partial report or marker list is returned on failure.
    """

    expected = _validate_expectations(expectations)
    selected_by_id: dict[str, Mapping[str, Any]] = {}
    overlay_by_ref: dict[str, Mapping[str, Any]] = {}
    for row in selected_original_rows:
        if not isinstance(row, Mapping):
            raise ValueError("Selected original layer contains a non-object row")
        token_id = row.get("original_token_id")
        if not isinstance(token_id, str) or not token_id or token_id in selected_by_id:
            raise ValueError("Selected original layer has a missing or duplicate stable ID")
        selected_by_id[token_id] = row
        disposition = row.get("manual_textual_disposition")
        if disposition is None:
            continue
        ref = row.get("target_ref")
        if not isinstance(ref, str) or ref not in expected or ref in overlay_by_ref:
            raise ValueError("Selected layer has an unexpected or duplicate textual overlay")
        overlay_by_ref[ref] = row
    if set(overlay_by_ref) != set(expected):
        raise ValueError("Selected layer does not contain the exact textual overlay ref set")

    expected_members: set[str] = set()
    excluded_lexical_ids: set[str] = set()
    member_owner: dict[str, str] = {}
    for ref, spec in expected.items():
        row = overlay_by_ref[ref]
        overlay_id = spec["overlay_original_token_id"]
        if row.get("original_token_id") != overlay_id:
            raise ValueError(f"Stale textual overlay ID at {ref}")
        if row.get("target_ref") != ref:
            raise ValueError(f"Textual overlay crosses a verse at {ref}")
        if row.get("contract_version") != CONTRACT_VERSION:
            raise ValueError(f"Textual overlay contract version drift at {ref}")
        if row.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"Textual overlay schema version drift at {ref}")
        if row.get("manual_textual_disposition") != spec["disposition"]:
            raise ValueError(f"Textual disposition drift at {ref}")
        members = _string_list(
            row.get("manual_textual_member_ids"),
            label=f"Selected textual member IDs at {ref}",
            allow_empty=False,
        )
        if members != spec["member_original_token_ids"]:
            raise ValueError(f"Textual alternatives are lost, reordered or stale at {ref}")
        for member in members:
            if member in member_owner:
                raise ValueError("A textual alternative is accounted by multiple overlays")
            member_owner[member] = ref
        expected_members.update(members)
        excluded_lexical = _string_list(
            row.get("excluded_lexical_candidate_ids", []),
            label=f"Selected excluded lexical IDs at {ref}",
        )
        if excluded_lexical != spec["excluded_lexical_candidate_ids"]:
            raise ValueError(f"Excluded lexical candidate drift at {ref}")
        excluded_lexical_ids.update(excluded_lexical)
        if row.get("reviewed_target_span") != spec["target_span"]:
            raise ValueError(f"Reviewed textual target span drift at {ref}")
        rendered = _string_list(
            row.get("rendered_strong"), label=f"Overlay rendered Strong at {ref}"
        )
        classic = _string_list(
            row.get("strong_classic"), label=f"Overlay classic Strong at {ref}"
        )
        if rendered != spec["rendered_strong"] or classic != rendered:
            raise ValueError(f"Textual overlay Strong drift at {ref}")
        if spec["disposition"] == _NO_RENDER_DISPOSITION:
            if (
                row.get("strong_status") != "textual_group_no_render"
                or row.get("strong_raw") != []
                or row.get("strong_normalized") != []
            ):
                raise ValueError(f"No-render textual overlay can emit a Strong at {ref}")
        elif spec["disposition"] == _PRIMARY_COMPONENT_DISPOSITION:
            if (
                overlay_id != members[0]
                or row.get("reading_status") != "primary_manual_textual_choice_b"
                or row.get("excluded_textual_member_ids") != [members[1]]
                or rendered != ["G1909"]
            ):
                raise ValueError("Acts.2.38 primary overlay must render only G1909")
        else:
            if rendered != ["G2010"]:
                raise ValueError("1Cor.14.34 textual group must render one G2010")
        if spec["disposition"] != _PRIMARY_COMPONENT_DISPOSITION:
            variant = row.get("textual_variant_raw")
            if (
                row.get("component_kind") != "manual_textual_alternative_group"
                or row.get("reading_status") != "primary_manual_textual_choice_group"
                or not isinstance(variant, Mapping)
                or variant.get("member_original_token_ids") != members
                or variant.get("exact_form_selected") is not False
                or overlay_id in members
            ):
                raise ValueError(f"Synthetic textual alternative group drift at {ref}")

    # A grouped member may not remain as a second selected original.  The one
    # exception is the selected c01 token at Acts.2.38, whose ID is the overlay.
    overlay_ids = {
        str(spec["overlay_original_token_id"]) for spec in expected.values()
    }
    for member in expected_members:
        if member in selected_by_id and member not in overlay_ids:
            raise ValueError("A textual member is duplicated beside its selected overlay")
    if excluded_lexical_ids & set(selected_by_id):
        raise ValueError("An excluded lexical candidate leaked into the selected layer")

    edge_by_id: dict[str, Mapping[str, Any]] = {}
    edge_by_original: dict[str, Mapping[str, Any]] = {}
    edge_by_target: dict[str, Mapping[str, Any]] = {}
    target_accounting: dict[str, Mapping[str, Any]] = {}
    original_decisions: dict[str, Mapping[str, Any]] = {}
    for row in finalized_gold_rows:
        if not isinstance(row, Mapping):
            raise ValueError("Finalized gold contains a non-object row")
        record_type = row.get("record_type")
        if row.get("contract_version") != CONTRACT_VERSION:
            raise ValueError("Finalized gold contract version drift")
        if row.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Finalized gold schema version drift")
        if row.get("status") != "reviewed_accepted":
            raise ValueError("Finalized gold contains an unaccepted row")
        ref = row.get("target_ref")
        if not isinstance(ref, str) or not ref:
            raise ValueError("Finalized gold row lacks a target ref")
        if record_type == "hyperedge":
            edge_id = row.get("edge_id")
            if not isinstance(edge_id, str) or not edge_id or edge_id in edge_by_id:
                raise ValueError("Finalized gold has a missing or duplicate edge ID")
            originals = _string_list(
                row.get("original_token_ids"), label="Gold hyperedge original IDs"
            )
            targets = _string_list(
                row.get("target_token_ids"), label="Gold hyperedge target IDs"
            )
            if not originals and not targets:
                raise ValueError("Finalized gold contains an empty hyperedge")
            for original_id in originals:
                selected = selected_by_id.get(original_id)
                if selected is None:
                    raise ValueError("Gold hyperedge has a stale or dangling original ID")
                if selected.get("target_ref") != ref:
                    raise ValueError("Gold hyperedge original ID crosses a verse")
                if original_id in edge_by_original:
                    raise ValueError("Gold original ID is linked by multiple hyperedges")
                edge_by_original[original_id] = row
            for target_id in targets:
                if target_id in edge_by_target:
                    raise ValueError("Gold target ID is linked by multiple hyperedges")
                edge_by_target[target_id] = row
            edge_by_id[edge_id] = row
        elif record_type == "target_accounting":
            target_id = row.get("target_token_id")
            if (
                not isinstance(target_id, str)
                or not target_id
                or target_id in target_accounting
            ):
                raise ValueError("Finalized gold has duplicate target accounting")
            _string_list(
                row.get("linked_original_token_ids"),
                label="Target-accounting original IDs",
            )
            target_accounting[target_id] = row
        elif record_type == "original_decision":
            original_id = row.get("original_token_id")
            if (
                not isinstance(original_id, str)
                or not original_id
                or original_id in original_decisions
            ):
                raise ValueError("Finalized gold has duplicate original decisions")
            original_decisions[original_id] = row
        else:
            raise ValueError("Finalized gold contains an unknown record type")

    for target_id, edge in edge_by_target.items():
        accounting = target_accounting.get(target_id)
        if accounting is None:
            raise ValueError("Gold hyperedge has a dangling target ID")
        if accounting.get("target_ref") != edge.get("target_ref"):
            raise ValueError("Gold target accounting crosses a verse")
        originals = set(_string_list(edge.get("original_token_ids"), label="Edge IDs"))
        linked = set(
            _string_list(
                accounting.get("linked_original_token_ids"),
                label="Target-accounting links",
            )
        )
        if originals:
            if accounting.get("target_status") != "aligned" or linked != originals:
                raise ValueError("Gold target accounting disagrees with its hyperedge")
        elif linked:
            raise ValueError("Gold target null accounting carries original IDs")
    for target_id, accounting in target_accounting.items():
        if accounting.get("target_status") == "aligned" and target_id not in edge_by_target:
            raise ValueError("Aligned target accounting has no accepted hyperedge")

    # If original-decision rows are present, verify their edge/ref locks too.
    for original_id, decision in original_decisions.items():
        selected = selected_by_id.get(original_id)
        edge = edge_by_original.get(original_id)
        if selected is None or edge is None:
            raise ValueError("Original decision has a stale or dangling original ID")
        if (
            decision.get("target_ref") != selected.get("target_ref")
            or decision.get("edge_id") != edge.get("edge_id")
        ):
            raise ValueError("Original decision crosses a verse or names a stale edge")

    # Member IDs are represented by exactly one overlay ledger entry.  They
    # must never be promoted as independent gold edges (except selected c01,
    # whose stable ID is the Acts overlay itself).
    for member in expected_members:
        if member in edge_by_original and member not in overlay_ids:
            raise ValueError("A textual alternative leaked into an independent gold edge")
    if excluded_lexical_ids & set(edge_by_original):
        raise ValueError("An excluded lexical candidate leaked into finalized gold")

    markers: list[dict[str, Any]] = []
    member_ledger: list[dict[str, Any]] = []
    no_render_count = 0
    for ref in sorted(expected):
        spec = expected[ref]
        overlay_id = str(spec["overlay_original_token_id"])
        target_span = spec["target_span"]
        target_id = str(target_span["token_id"])
        edge = edge_by_original.get(overlay_id)
        if edge is None or target_id not in edge.get("target_token_ids", []):
            raise ValueError(f"Textual overlay lacks its exact accepted target edge at {ref}")
        if edge.get("target_ref") != ref:
            raise ValueError(f"Textual overlay gold edge crosses a verse at {ref}")
        accounting = target_accounting.get(target_id)
        if accounting is None or accounting.get("target_ref") != ref:
            raise ValueError(f"Textual target accounting is missing or cross-verse at {ref}")
        if accounting.get("target_span") != _accounting_span(target_span):
            raise ValueError(f"Final target-accounting span drift at {ref}")
        linked = _string_list(
            accounting.get("linked_original_token_ids"),
            label=f"Final target-accounting links at {ref}",
        )
        if overlay_id not in linked:
            raise ValueError(f"Final target accounting omits the textual overlay at {ref}")
        rendered = list(spec["rendered_strong"])
        if not rendered:
            no_render_count += 1
        for strong in rendered:
            markers.append(
                {
                    "target_ref": ref,
                    "target_token_id": target_id,
                    "target_span": dict(target_span),
                    "source_original_token_id": overlay_id,
                    "strong_classic": strong,
                    "evidence_class": "manual_post_candidate_textual_overlay",
                }
            )
        member_ledger.append(
            {
                "target_ref": ref,
                "overlay_original_token_id": overlay_id,
                "member_original_token_ids": list(
                    spec["member_original_token_ids"]
                ),
                "member_status": "accounted_as_textual_alternatives",
                "rendered_strong": rendered,
            }
        )

    marker_counts = defaultdict(int)
    for marker in markers:
        marker_counts[(marker["target_ref"], marker["strong_classic"])] += 1
    if marker_counts[("Acts.2.38", "G1909")] not in {0, 1}:
        raise ValueError("Acts.2.38 emits G1909 more than once")
    if "Acts.2.38" in expected and marker_counts[("Acts.2.38", "G1909")] != 1:
        raise ValueError("Acts.2.38 must emit exactly one G1909")
    if "Acts.2.38" in expected and any(
        marker["target_ref"] == "Acts.2.38" and marker["strong_classic"] != "G1909"
        for marker in markers
    ):
        raise ValueError("Acts.2.38 emits a Strong other than G1909")
    if "1Cor.14.34" in expected and marker_counts[("1Cor.14.34", "G2010")] != 1:
        raise ValueError("1Cor.14.34 must emit exactly one G2010")

    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "validator_version": TEXTUAL_RENDER_VALIDATOR_VERSION,
        "status": "validated_post_candidate_textual_render_contract",
        "processed_count": len(expected),
        "skipped_count": 0,
        "error_count": 0,
        "counts": {
            "textual_loci": len(expected),
            "textual_alternative_members": len(expected_members),
            "no_render_loci": no_render_count,
            "strong_marker_occurrences": len(markers),
        },
        "markers": markers,
        "textual_alternative_member_accounting": member_ledger,
    }


def validate_post_candidate_textual_render_paths(
    *,
    selected_original_layer_path: Path,
    finalized_gold_annotations_path: Path,
    expectations: Mapping[str, Mapping[str, Any]] = (
        PRODUCTION_POST_CANDIDATE_TEXTUAL_EXPECTATIONS
    ),
) -> dict[str, Any]:
    """Path adapter for the pure downstream validator."""

    return validate_post_candidate_textual_render_contract(
        selected_original_rows=_read_jsonl(selected_original_layer_path),
        finalized_gold_rows=_read_jsonl(finalized_gold_annotations_path),
        expectations=expectations,
    )

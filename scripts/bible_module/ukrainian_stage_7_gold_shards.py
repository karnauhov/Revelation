"""Deterministic book/range sharding for stage-7 gold review packets.

This module never labels a decision.  It only splits an already frozen,
answer-free reviewer packet, validates complete human submissions for every
shard, merges them back into the exact full-pass schema, and checks reviewer
independence per stable decision across two merged passes.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold import (
    BOOKS,
    BOOK_NUMBER,
    GOLD_WORKFLOW_VERSION,
    SHARD_CONTRACT_VERSION,
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
    sha256_text,
    sha256_lines,
    stable_json,
)


def _reference_key(row: Mapping[str, Any]) -> tuple[int, int, int, str]:
    ref = str(row.get("target_ref", ""))
    try:
        book, chapter, verse = ref.split(".")
        return BOOK_NUMBER[book], int(chapter), int(verse), str(row["selection_id"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Non-canonical reviewer-packet reference: {ref}") from None


def parse_book_ranges(values: Sequence[str]) -> list[tuple[str, str]]:
    """Parse canonical inclusive ``Gen-Deut`` ranges."""

    ranges: list[tuple[str, str]] = []
    occupied: set[str] = set()
    for value in values:
        parts = value.split("-", 1)
        if len(parts) != 2 or any(part not in BOOK_NUMBER for part in parts):
            raise ValueError(f"Invalid canonical book range: {value}")
        first, last = parts
        if BOOK_NUMBER[first] > BOOK_NUMBER[last]:
            raise ValueError(f"Reversed canonical book range: {value}")
        books = set(BOOKS[BOOK_NUMBER[first] - 1 : BOOK_NUMBER[last]])
        if occupied & books:
            raise ValueError(f"Overlapping canonical book range: {value}")
        occupied.update(books)
        ranges.append((first, last))
    return sorted(ranges, key=lambda item: BOOK_NUMBER[item[0]])


def _ranges_for_packet(
    packet_books: set[str], requested: Sequence[tuple[str, str]] | None
) -> list[tuple[str, str]]:
    if requested is None:
        return [(book, book) for book in BOOKS if book in packet_books]
    ranges = list(requested)
    covered: set[str] = set()
    for first, last in ranges:
        covered.update(BOOKS[BOOK_NUMBER[first] - 1 : BOOK_NUMBER[last]])
    if covered != packet_books:
        missing = sorted(packet_books - covered, key=BOOK_NUMBER.get)
        extra = sorted(covered - packet_books, key=BOOK_NUMBER.get)
        raise ValueError(
            f"Book ranges do not exactly cover packet books; missing={missing}, extra={extra}"
        )
    return ranges


def split_reviewer_packet(
    *,
    packet_path: Path,
    packet_manifest_path: Path,
    output_dir: Path,
    book_ranges: Sequence[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Split one frozen pass packet into exact, non-overlapping book ranges."""

    parent_manifest = _read_json(packet_manifest_path)
    if (
        parent_manifest.get("artifact") != "gold_reviewer_packets"
        or parent_manifest.get("status") != "prepared_unanswered_blind_packets"
        or parent_manifest.get("contract_version") != CONTRACT_VERSION
    ):
        raise ValueError("Parent reviewer-packet manifest contract/status is invalid")
    packet_sha = _sha256_file(packet_path)
    if parent_manifest.get("output_sha256", {}).get(packet_path.name) != packet_sha:
        raise ValueError("Parent reviewer packet differs from its manifest")
    rows = sorted(_read_jsonl(packet_path), key=_reference_key)
    if not rows:
        raise ValueError("Cannot shard an empty reviewer packet")
    if sha256_lines(rows) != packet_sha:
        raise ValueError("Parent reviewer packet is not in deterministic canonical order")
    passes = {row.get("review_pass") for row in rows}
    if len(passes) != 1 or next(iter(passes)) not in {1, 2}:
        raise ValueError("Reviewer packet contains mixed/invalid pass numbers")
    review_pass = int(next(iter(passes)))
    if any(
        row.get("record_type") != "reviewer_packet_verse"
        or row.get("blind_to_other_pass") is not True
        or row.get("input_sha256") != parent_manifest.get("input_sha256")
        for row in rows
    ):
        raise ValueError("Parent reviewer packet row contract/input locks differ")
    selection_ids = [str(row.get("selection_id", "")) for row in rows]
    if not all(selection_ids) or len(set(selection_ids)) != len(selection_ids):
        raise ValueError("Parent reviewer packet repeats a verse selection ID")
    packet_books = {str(row.get("book")) for row in rows}
    if not packet_books <= set(BOOKS):
        raise ValueError("Parent reviewer packet contains an unknown book")
    ranges = _ranges_for_packet(packet_books, book_ranges)

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    shard_entries: list[dict[str, Any]] = []
    all_original_ids: set[str] = set()
    all_target_ids: set[str] = set()
    for ordinal, (first, last) in enumerate(ranges, 1):
        allowed = set(BOOKS[BOOK_NUMBER[first] - 1 : BOOK_NUMBER[last]])
        shard_rows = [row for row in rows if row["book"] in allowed]
        if not shard_rows:
            raise ValueError("Book range produced an empty shard")
        requests = _packet_requests(shard_rows)
        original_ids = {
            str(value["token_id"]) for value in requests["originals"].values()
        }
        target_ids = {
            str(value["token_id"]) for value in requests["targets"].values()
        }
        if all_original_ids & original_ids or all_target_ids & target_ids:
            raise ValueError("Shard split duplicates a stable token ID")
        all_original_ids.update(original_ids)
        all_target_ids.update(target_ids)
        shard_id = f"gold7:p{review_pass}:shard:{ordinal:03d}:{first}-{last}"
        filename = f"review_pass_{review_pass}.{ordinal:03d}.{first}-{last}.packet.jsonl"
        count, digest = _write_jsonl(output_dir / filename, shard_rows)
        outputs[filename] = digest
        shard_entries.append(
            {
                "shard_id": shard_id,
                "ordinal": ordinal,
                "review_pass": review_pass,
                "books": [book for book in BOOKS if book in allowed],
                "first_target_ref": shard_rows[0]["target_ref"],
                "last_target_ref": shard_rows[-1]["target_ref"],
                "packet_file": filename,
                "packet_sha256": digest,
                "verse_count": count,
                "original_decision_count": len(requests["originals"]),
                "target_accounting_count": len(requests["targets"]),
            }
        )
    full_requests = _packet_requests(rows)
    if (
        len(all_original_ids) != len(full_requests["originals"])
        or len(all_target_ids) != len(full_requests["targets"])
    ):
        raise ValueError("Shard split does not exactly cover the full packet requests")

    manifest = _manifest(
        artifact="gold_reviewer_packet_shards",
        status="prepared_answer_free_complete_shards",
        inputs={
            "parent_packet": packet_sha,
            "parent_packet_manifest": _sha256_file(packet_manifest_path),
            **{
                f"source_{key}": value
                for key, value in parent_manifest["input_sha256"].items()
            },
        },
        outputs=outputs,
        processed=len(rows),
        skipped=0,
        errors=0,
        counts={
            "shards": len(shard_entries),
            "selected_verses": len(rows),
            "primary_original_decisions": len(full_requests["originals"]),
            "target_token_accounting_decisions": len(full_requests["targets"]),
        },
        notes=(
            "Shard packets retain exact parent rows and contain no answers.",
            "Book ranges are canonical, non-overlapping and cover the parent packet exactly.",
            "A merged pass remains invalid until every shard has complete original and target accounting.",
        ),
    )
    manifest["shard_contract_version"] = SHARD_CONTRACT_VERSION
    manifest["review_pass"] = review_pass
    manifest["parent_packet_name"] = packet_path.name
    manifest["parent_packet_sha256"] = packet_sha
    manifest["parent_packet_manifest_sha256"] = _sha256_file(packet_manifest_path)
    manifest["parent_input_sha256"] = parent_manifest["input_sha256"]
    manifest["shards"] = shard_entries
    _write_json(output_dir / "gold_reviewer_packet_shards.manifest.json", manifest)
    return manifest


def _submission_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = list(_read_jsonl(path))
    metadata = [row for row in rows if row.get("record_type") == "review_metadata"]
    if len(metadata) != 1:
        raise ValueError("Shard submission requires exactly one review_metadata row")
    decisions = [row for row in rows if row.get("record_type") != "review_metadata"]
    return metadata[0], decisions


def merge_review_shards(
    *,
    shard_manifest_path: Path,
    submission_paths: Sequence[Path],
    output_path: Path,
) -> dict[str, Any]:
    """Validate every shard and merge it into one complete raw review pass."""

    shard_manifest = _read_json(shard_manifest_path)
    if (
        shard_manifest.get("artifact") != "gold_reviewer_packet_shards"
        or shard_manifest.get("status") != "prepared_answer_free_complete_shards"
        or shard_manifest.get("shard_contract_version") != SHARD_CONTRACT_VERSION
    ):
        raise ValueError("Shard manifest contract/status is invalid")
    manifest_sha = _sha256_file(shard_manifest_path)
    expected_entries = {
        str(item["shard_id"]): item for item in shard_manifest.get("shards", [])
    }
    if len(expected_entries) != shard_manifest.get("counts", {}).get("shards"):
        raise ValueError("Shard manifest IDs/count differ")
    ordinals = sorted(int(item["ordinal"]) for item in expected_entries.values())
    if ordinals != list(range(1, len(expected_entries) + 1)):
        raise ValueError("Shard manifest ordinals are not exact and contiguous")
    if any(
        shard_manifest.get("output_sha256", {}).get(item["packet_file"])
        != item["packet_sha256"]
        for item in expected_entries.values()
    ):
        raise ValueError("Shard manifest output and entry SHA-256 values differ")
    submissions: dict[str, tuple[Path, dict[str, Any], list[dict[str, Any]]]] = {}
    for path in submission_paths:
        metadata, rows = _submission_rows(path)
        shard_id = str(metadata.get("shard_id", ""))
        if shard_id not in expected_entries or shard_id in submissions:
            raise ValueError("Unknown or duplicate shard submission")
        submissions[shard_id] = (path, metadata, rows)
    if set(submissions) != set(expected_entries):
        raise ValueError("Merged review pass is missing one or more shard submissions")

    merged_originals: dict[str, dict[str, Any]] = {}
    merged_targets: dict[str, dict[str, Any]] = {}
    reviewer_shards: dict[str, list[str]] = defaultdict(list)
    input_digests: dict[str, str] = {
        "shard_manifest": manifest_sha,
        "parent_packet": shard_manifest["parent_packet_sha256"],
        "parent_packet_manifest": shard_manifest["parent_packet_manifest_sha256"],
    }
    reconstructed_parent_rows: list[dict[str, Any]] = []
    for shard_id in sorted(expected_entries, key=lambda value: expected_entries[value]["ordinal"]):
        entry = expected_entries[shard_id]
        packet_path = shard_manifest_path.parent / entry["packet_file"]
        if _sha256_file(packet_path) != entry["packet_sha256"]:
            raise ValueError("Shard packet differs from its manifest")
        packet_rows = list(_read_jsonl(packet_path))
        if len(packet_rows) != entry["verse_count"]:
            raise ValueError("Shard packet verse count differs from its manifest")
        if any(
            row.get("review_pass") != shard_manifest["review_pass"]
            or row.get("input_sha256") != shard_manifest["parent_input_sha256"]
            for row in packet_rows
        ):
            raise ValueError("Shard packet pass or source input locks differ")
        reconstructed_parent_rows.extend(packet_rows)
        requests = _packet_requests(packet_rows)
        if (
            len(requests["originals"]) != entry["original_decision_count"]
            or len(requests["targets"]) != entry["target_accounting_count"]
        ):
            raise ValueError("Shard packet request counts differ from its manifest")
        submission_path, metadata, rows = submissions[shard_id]
        reviewer = metadata.get("reviewer_id")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("Shard submission lacks a stable reviewer ID")
        if (
            metadata.get("review_pass") != shard_manifest["review_pass"]
            or metadata.get("blind_to_other_pass") is not True
            or metadata.get("shard_packet_sha256") != entry["packet_sha256"]
            or metadata.get("shard_manifest_sha256") != manifest_sha
            or metadata.get("parent_packet_sha256")
            != shard_manifest["parent_packet_sha256"]
            or metadata.get("parent_packet_manifest_sha256")
            != shard_manifest["parent_packet_manifest_sha256"]
            or metadata.get("input_sha256") != shard_manifest["parent_input_sha256"]
        ):
            raise ValueError("Shard submission pass or SHA input locks differ")
        for prohibited in (
            "other_pass_sha256",
            "other_reviewer_id",
            "prior_annotations_sha256",
        ):
            if prohibited in metadata:
                raise ValueError("Blind shard submission exposes another pass")
        shard_originals: dict[str, dict[str, Any]] = {}
        shard_targets: dict[str, dict[str, Any]] = {}
        for row in rows:
            record_type = row.get("record_type")
            if row.get("reviewer_id", reviewer) != reviewer:
                raise ValueError("Shard decision reviewer differs from shard metadata")
            if record_type == "original_decision":
                key = str(row.get("decision_id", ""))
                request = requests["originals"].get(key)
                if request is None or key in shard_originals or key in merged_originals:
                    raise ValueError("Unknown or duplicate shard original decision")
                _validate_original_decision(row, request, requests)
                normalized = dict(row)
                normalized["reviewer_id"] = reviewer
                shard_originals[key] = normalized
            elif record_type == "target_accounting":
                key = str(row.get("accounting_id", ""))
                request = requests["targets"].get(key)
                if request is None or key in shard_targets or key in merged_targets:
                    raise ValueError("Unknown or duplicate shard target accounting")
                _validate_target_accounting(row, request, requests)
                normalized = dict(row)
                normalized["reviewer_id"] = reviewer
                shard_targets[key] = normalized
            else:
                raise ValueError("Shard submission contains an unknown record type")
        if set(shard_originals) != set(requests["originals"]):
            raise ValueError("Shard lacks exact one-decision-per-primary-original accounting")
        if set(shard_targets) != set(requests["targets"]):
            raise ValueError("Shard lacks exact target-token accounting")
        _validate_semantic_accounting(shard_originals, shard_targets)
        merged_originals.update(shard_originals)
        merged_targets.update(shard_targets)
        reviewer_shards[reviewer].append(shard_id)
        input_digests[f"submission_{entry['ordinal']:03d}"] = _sha256_file(
            submission_path
        )

    if sha256_lines(reconstructed_parent_rows) != shard_manifest[
        "parent_packet_sha256"
    ]:
        raise ValueError("Shard packets do not reconstruct the exact parent packet")

    if (
        len(merged_originals)
        != shard_manifest["counts"]["primary_original_decisions"]
        or len(merged_targets)
        != shard_manifest["counts"]["target_token_accounting_decisions"]
    ):
        raise ValueError("Merged shard request counts differ from the full packet")
    roster = [
        {"reviewer_id": reviewer, "shard_ids": sorted(shards)}
        for reviewer, shards in sorted(reviewer_shards.items())
    ]
    roster_id = "reviewer-roster:" + sha256_text(stable_json(roster))[:32]
    output_rows: list[dict[str, Any]] = [
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": GOLD_WORKFLOW_VERSION,
            "shard_contract_version": SHARD_CONTRACT_VERSION,
            "record_type": "review_metadata",
            "review_pass": shard_manifest["review_pass"],
            "reviewer_id": roster_id,
            "reviewer_mode": "sharded",
            "reviewer_roster": roster,
            "blind_to_other_pass": True,
            "packet_sha256": shard_manifest["parent_packet_sha256"],
            "packet_manifest_sha256": shard_manifest[
                "parent_packet_manifest_sha256"
            ],
            "input_sha256": shard_manifest["parent_input_sha256"],
            "shard_manifest_sha256": manifest_sha,
        }
    ]
    output_rows.extend(merged_originals[key] for key in sorted(merged_originals))
    output_rows.extend(merged_targets[key] for key in sorted(merged_targets))
    count, digest = _write_jsonl(output_path, output_rows)
    manifest = _manifest(
        artifact=f"gold_merged_shard_review_pass_{shard_manifest['review_pass']}",
        status="complete_shard_merge_ready_for_pass_ingestion",
        inputs=input_digests,
        outputs={output_path.name: digest},
        processed=count - 1,
        skipped=0,
        errors=0,
        counts={
            "shards": len(expected_entries),
            "reviewers": len(roster),
            "original_decisions": len(merged_originals),
            "target_accounting": len(merged_targets),
        },
        notes=(
            "Every shard and every stable request is present exactly once.",
            "Per-decision reviewer IDs are retained for cross-pass independence checks.",
            "The merged output is a raw full-pass submission for ingest-pass1/ingest-pass2.",
        ),
    )
    manifest["shard_contract_version"] = SHARD_CONTRACT_VERSION
    manifest["review_pass"] = shard_manifest["review_pass"]
    manifest["reviewer_id"] = roster_id
    manifest["reviewer_roster"] = roster
    _write_json(Path(str(output_path) + ".manifest.json"), manifest)
    return manifest


def _reviewer_by_key(path: Path) -> tuple[int, dict[str, str]]:
    sidecar_path = Path(str(path) + ".manifest.json")
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("status")
        != "complete_shard_merge_ready_for_pass_ingestion"
        or sidecar.get("shard_contract_version") != SHARD_CONTRACT_VERSION
        or sidecar.get("output_sha256", {}).get(path.name) != _sha256_file(path)
    ):
        raise ValueError("Merged review pass differs from its sidecar")
    metadata, rows = _submission_rows(path)
    reviewers: dict[str, str] = {}
    for row in rows:
        if row.get("record_type") == "original_decision":
            key = "original:" + str(row.get("decision_id", ""))
        elif row.get("record_type") == "target_accounting":
            key = "target:" + str(row.get("accounting_id", ""))
        else:
            raise ValueError("Merged pass contains an unknown decision type")
        reviewer = row.get("reviewer_id")
        if key in reviewers or not isinstance(reviewer, str) or not reviewer:
            raise ValueError("Merged pass has duplicate IDs or missing reviewer identity")
        reviewers[key] = reviewer
    return int(metadata["review_pass"]), reviewers


def validate_merged_pass_independence(
    *, pass1_path: Path, pass2_path: Path
) -> dict[str, Any]:
    """Require distinct reviewers for every stable decision/accounting ID."""

    number1, reviewers1 = _reviewer_by_key(pass1_path)
    number2, reviewers2 = _reviewer_by_key(pass2_path)
    if (number1, number2) != (1, 2):
        raise ValueError("Merged files are not review pass 1 and review pass 2")
    if set(reviewers1) != set(reviewers2):
        raise ValueError("Merged review passes account for different stable IDs")
    collisions = [
        key for key in sorted(reviewers1) if reviewers1[key] == reviewers2[key]
    ]
    if collisions:
        raise ValueError(
            "Reviewer independence failed for stable decisions: "
            + ", ".join(collisions[:5])
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "shard_contract_version": SHARD_CONTRACT_VERSION,
        "status": "independent_reviewers_for_every_stable_decision",
        "input_sha256": {
            "pass_1": _sha256_file(pass1_path),
            "pass_2": _sha256_file(pass2_path),
        },
        "output_sha256": {},
        "processed_count": len(reviewers1),
        "skipped_count": 0,
        "error_count": 0,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    split = commands.add_parser("split")
    split.add_argument("--packet", type=Path, required=True)
    split.add_argument("--packet-manifest", type=Path, required=True)
    split.add_argument("--output-dir", type=Path, required=True)
    split.add_argument(
        "--book-range",
        action="append",
        default=[],
        help="inclusive canonical range such as Gen-Deut; repeat as needed",
    )
    merge = commands.add_parser("merge")
    merge.add_argument("--shard-manifest", type=Path, required=True)
    merge.add_argument("--submission", type=Path, action="append", required=True)
    merge.add_argument("--output", type=Path, required=True)
    pair = commands.add_parser("check-pair")
    pair.add_argument("--pass1", type=Path, required=True)
    pair.add_argument("--pass2", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "split":
        ranges = parse_book_ranges(args.book_range) if args.book_range else None
        result = split_reviewer_packet(
            packet_path=args.packet,
            packet_manifest_path=args.packet_manifest,
            output_dir=args.output_dir,
            book_ranges=ranges,
        )
    elif args.command == "merge":
        result = merge_review_shards(
            shard_manifest_path=args.shard_manifest,
            submission_paths=args.submission,
            output_path=args.output,
        )
    else:
        result = validate_merged_pass_independence(
            pass1_path=args.pass1, pass2_path=args.pass2
        )
    print(stable_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

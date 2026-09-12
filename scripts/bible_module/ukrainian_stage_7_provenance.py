"""Deterministic metadata-only repair for three frozen blind-review shards.

The original compact and expanded submissions remain immutable. This scoped
repair changes only a copied Mat renderer label and evidence namespace; it
cannot change any token/span alignment decision or manufacture a new review.
"""

from __future__ import annotations

import argparse
import copy
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .ukrainian_stage_7_model import stable_json


BASE = Path("scripts/bible_module/work/ukrainian_stage_7_20260801")
FROZEN_COMPACT = {
    "Mark": ("041", "9b28793cc46133f07952833cd8b308bfcd1195e7388ad53dd2d98bddac49ee14", 40, 693),
    "Luke": ("042", "9dbcee634800282f54dc95868e3bfd76f50a82f65837ccaf04d53034657c40cb", 39, 603),
    "John": ("043", "67f060df7bfe36c17501da4daee7645b9be87d0900eb8e96520c73cbd59cbb3d", 36, 597),
}
FROZEN_EXPANDED_DECISIONS = {"Mark": 1328, "Luke": 1210, "John": 1170}
OLD_PREFIX = "uk7:mat:p2:"
OLD_LABEL = "Independent blind Mat pass 2 at "


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _canonical_rows(data: bytes) -> list[dict[str, Any]]:
    if not data or not data.endswith(b"\n") or b"\r" in data:
        raise ValueError("Frozen compact JSONL is not LF-terminated")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines()]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Frozen compact JSONL has a non-object row")
    if data != ("\n".join(stable_json(row) for row in rows) + "\n").encode("utf-8"):
        raise ValueError("Frozen compact JSONL is not canonical")
    return rows


def _without_provenance(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_provenance(item)
            for key, item in value.items()
            if key not in {"rationale", "evidence"}
        }
    if isinstance(value, list):
        return [_without_provenance(item) for item in value]
    return value


def repair_compact_rows(rows: list[dict[str, Any]], book: str) -> tuple[list[dict[str, Any]], int]:
    """Return a provenance-corrected copy, preserving every semantic field."""

    if book not in FROZEN_COMPACT:
        raise ValueError("Book is outside the frozen metadata defect scope")
    _, _, expected_verses, expected_evidence = FROZEN_COMPACT[book]
    if len(rows) != expected_verses + 1:
        raise ValueError("Frozen compact verse count differs")
    result = copy.deepcopy(rows)
    metadata = result[0]
    if (
        metadata.get("record_type") != "compact_review_metadata"
        or metadata.get("review_pass") != 2
        or metadata.get("reviewer_id") != f"codex-blind-{book.lower()}-pass2-20260912-independent"
    ):
        raise ValueError("Frozen compact review identity differs")
    replacements = 0
    ids: set[str] = set()
    for row in result[1:]:
        ref = row.get("target_ref")
        if row.get("record_type") != "compact_review_verse_submission" or not isinstance(ref, str) or not ref.startswith(book + "."):
            raise ValueError("Frozen compact contains a foreign verse")
        for item in [*row.get("groups", []), *row.get("target_nulls", [])]:
            old_rationale = item.get("rationale")
            if not isinstance(old_rationale, str) or not old_rationale.startswith(OLD_LABEL + ref + ";"):
                raise ValueError("Frozen rationale is not the exact known template defect")
            item["rationale"] = "Independent blind " + book + " pass 2 at " + old_rationale[len(OLD_LABEL):]
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or len(evidence) != 1 or not isinstance(evidence[0], dict):
                raise ValueError("Frozen evidence cardinality differs")
            old_id = evidence[0].get("evidence_id")
            if not isinstance(old_id, str) or not old_id.startswith(OLD_PREFIX):
                raise ValueError("Frozen evidence namespace differs")
            evidence[0]["evidence_id"] = f"uk7:{book.lower()}:p2:" + old_id[len(OLD_PREFIX):]
            if evidence[0]["evidence_id"] in ids:
                raise ValueError("Repaired evidence IDs collide")
            ids.add(evidence[0]["evidence_id"])
            replacements += 1
    if replacements != expected_evidence or _without_provenance(rows) != _without_provenance(result):
        raise ValueError("Metadata repair changed the exact decision scope")
    serialized = "\n".join(stable_json(row) for row in result)
    if OLD_LABEL in serialized or OLD_PREFIX in serialized:
        raise ValueError("Mat renderer provenance remains in repaired shard")
    return result, replacements


def repair_book(book: str, output: Path) -> dict[str, Any]:
    shard, expected_sha, expected_verses, _ = FROZEN_COMPACT[book]
    source = BASE / "gold_compact_review" / "pass_2" / book / f"review_pass_2.shard_{shard}.compact.completed.manual.jsonl"
    original = source.read_bytes()
    if _sha(original) != expected_sha:
        raise ValueError("Frozen compact SHA-256 differs")
    rows = _canonical_rows(original)
    repaired, replacements = repair_compact_rows(rows, book)
    data = ("\n".join(stable_json(row) for row in repaired) + "\n").encode("utf-8")
    if output.exists() and output.read_bytes() != data:
        raise ValueError("Existing repaired output differs; refusing overwrite")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return {
        "book": book,
        "frozen_compact_sha256": expected_sha,
        "repaired_compact_sha256": _sha(data),
        "selected_verses": expected_verses,
        "provenance_entries_repaired": replacements,
        "semantic_decisions_changed": 0,
    }


def prove_expanded_semantics(old_path: Path, new_path: Path, book: str) -> dict[str, Any]:
    """Prove that expanded raw review decisions survived metadata repair."""

    if book not in FROZEN_COMPACT:
        raise ValueError("Book is outside the frozen metadata defect scope")
    old_rows = _canonical_rows(old_path.read_bytes())
    new_rows = _canonical_rows(new_path.read_bytes())
    if len(old_rows) != len(new_rows) or not old_rows or old_rows[0] != new_rows[0]:
        raise ValueError("Expanded review scope or header changed")
    if len(old_rows) - 1 != FROZEN_EXPANDED_DECISIONS[book]:
        raise ValueError("Expanded review cardinality differs")
    old_semantics = [_without_provenance(row) for row in old_rows]
    new_semantics = [_without_provenance(row) for row in new_rows]
    if old_semantics != new_semantics:
        raise ValueError("Expanded review semantic decisions changed")
    if any(str(row.get("target_ref", "")).split(".", 1)[0] != book for row in old_rows[1:]):
        raise ValueError("Expanded review contains a foreign verse")
    semantic_digest = _sha(("\n".join(stable_json(row) for row in old_semantics) + "\n").encode("utf-8"))
    return {
        "book": book,
        "stable_decisions": len(old_rows) - 1,
        "semantic_decisions_changed": 0,
        "semantic_projection_sha256": semantic_digest,
        "frozen_expanded_sha256": _sha(old_path.read_bytes()),
        "repaired_expanded_sha256": _sha(new_path.read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", choices=tuple(FROZEN_COMPACT))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--old-expanded", type=Path)
    parser.add_argument("--new-expanded", type=Path)
    args = parser.parse_args()
    result = repair_book(args.book, args.output)
    if (args.old_expanded is None) != (args.new_expanded is None):
        raise ValueError("Both expanded review paths are required for proof")
    if args.old_expanded is not None:
        result.update(prove_expanded_semantics(args.old_expanded, args.new_expanded, args.book))
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

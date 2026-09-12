"""Explicit SHA rebase of frozen Mark/Luke adjudications after metadata repair.

No original/target decision row is edited. The old and new blind-pass
semantics, exact disagreement stable IDs, and both old/new adjudication
validators must agree before the rebased artifact is reported usable.
"""

from __future__ import annotations

import argparse
import copy
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .ukrainian_stage_7_gold_compare import validate_adjudication_shard
from .ukrainian_stage_7_model import stable_json
from .ukrainian_stage_7_provenance import BASE, _canonical_rows, prove_expanded_semantics


SCOPE = {
    "Mark": ("041", "76d2f8276df6d2c43c43034c45d389be75e88b9d5ccd8331d084dda9db1d0630", "ee29b8e4ce761716edbf1456471422cbb0f16cb5e7fb9f63e90e01c9ab08600e"),
    "Luke": ("042", "7f4e8a7d1fde9fb2ee5abd8fd1aa20437d273f8643e768b9c2a611d2de1b3a4f", "889ccdfb60cd9d5d8446ce3f171b2b2d55ea5245ff85fe3a7eeffef4b227847f"),
}


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _canonical_object(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    obj = json.loads(data.decode("utf-8"))
    if not isinstance(obj, dict) or data != (stable_json(obj) + "\n").encode("utf-8"):
        raise ValueError("Adjudication sidecar is not canonical")
    return obj


def _write_identical_or_new(path: Path, data: bytes) -> None:
    if path.exists() and path.read_bytes() != data:
        raise ValueError("Existing rebase output differs; refusing overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _comparison_keys(path: Path) -> set[str]:
    rows = _canonical_rows(path.read_bytes())
    if len(rows) < 2 or rows[0].get("record_type") != "comparison_metadata":
        raise ValueError("Comparison metadata differs")
    keys = [row.get("stable_key") for row in rows[1:]]
    if any(row.get("record_type") != "alignment_disagreement" for row in rows[1:]) or len(keys) != len(set(keys)):
        raise ValueError("Comparison disagreement scope is invalid")
    return set(keys)


def rebase_book(book: str, output: Path) -> dict[str, Any]:
    if book not in SCOPE:
        raise ValueError("Book is outside the frozen adjudication rebase scope")
    shard, expected_old_adjud_sha, expected_old_sidecar_sha = SCOPE[book]
    pass1 = BASE / f"external_chatgpt/uk7ext_gold_{book}_pass1_{shard}/completed_external/review_pass_1.shard_{shard}.raw.external-v1.canonical-v2.jsonl"
    old_pass2 = BASE / f"gold_compact_review/pass_2/{book}/completed/review_pass_2.shard_{shard}.raw.manual-v2.jsonl"
    new_pass2 = BASE / f"gold_compact_review/pass_2/{book}/provenance_repair/repro_run_1/review_pass_2.shard_{shard}.raw.provenance-v1.jsonl"
    old_comparison = BASE / f"gold_review_comparisons/{book}.pass1-pass2.disagreements.jsonl"
    new_comparison = BASE / f"gold_review_comparisons/provenance_repair/repro_run_1/{book}.pass1-pass2.disagreements.jsonl"
    old_adjudication = BASE / f"gold_review_adjudication/{book}/completed/{book}.shard_{shard}.pass1-pass2.third_adjudication.jsonl"
    old_sidecar_path = Path(str(old_adjudication) + ".manifest.json")
    if _sha(old_adjudication.read_bytes()) != expected_old_adjud_sha or _sha(old_sidecar_path.read_bytes()) != expected_old_sidecar_sha:
        raise ValueError("Frozen adjudication SHA-256 differs")
    validate_adjudication_shard(
        pass1_path=pass1, pass2_path=old_pass2,
        comparison_path=old_comparison, adjudication_path=old_adjudication,
    )
    semantic_proof = prove_expanded_semantics(old_pass2, new_pass2, book)
    if _comparison_keys(old_comparison) != _comparison_keys(new_comparison):
        raise ValueError("Repaired comparison changed disagreement stable IDs")
    rows = _canonical_rows(old_adjudication.read_bytes())
    if not rows or rows[0].get("record_type") != "adjudication_shard_metadata":
        raise ValueError("Frozen adjudication header differs")
    rebased_rows = copy.deepcopy(rows)
    rebased_rows[0]["pass_2_sha256"] = _sha(new_pass2.read_bytes())
    rebased_rows[0]["comparison_sha256"] = _sha(new_comparison.read_bytes())
    if rows[1:] != rebased_rows[1:]:
        raise ValueError("Adjudication decision rows changed")
    data = ("\n".join(stable_json(row) for row in rebased_rows) + "\n").encode("utf-8")
    sidecar = copy.deepcopy(_canonical_object(old_sidecar_path))
    replacements = {
        "review_pass_2": new_pass2,
        "review_pass_2_manifest": Path(str(new_pass2) + ".manifest.json"),
        "comparison": new_comparison,
        "comparison_manifest": Path(str(new_comparison) + ".manifest.json"),
    }
    for name, path in replacements.items():
        sidecar["input_sha256"][name] = _sha(path.read_bytes())
        sidecar["input_bytes"][name] = path.stat().st_size
    sidecar["output_sha256"][output.name] = _sha(data)
    if output.name != old_adjudication.name:
        del sidecar["output_sha256"][old_adjudication.name]
    sidecar["metadata_only_rebase"] = {
        "old_adjudication_sha256": expected_old_adjud_sha,
        "old_adjudication_sidecar_sha256": expected_old_sidecar_sha,
        "repaired_pass2_semantic_projection_sha256": semantic_proof["semantic_projection_sha256"],
        "decision_rows_changed": 0,
        "comparison_disagreement_keys_changed": 0,
    }
    sidecar["notes"] = [
        *sidecar.get("notes", []),
        "Metadata-only pass2 provenance repair: every adjudication decision row is byte-equivalent; pass2/comparison SHA locks explicitly rebased. This is not a new adjudication or book acceptance.",
    ]
    sidecar_data = (stable_json(sidecar) + "\n").encode("utf-8")
    _write_identical_or_new(output, data)
    _write_identical_or_new(Path(str(output) + ".manifest.json"), sidecar_data)
    validation = validate_adjudication_shard(
        pass1_path=pass1, pass2_path=new_pass2,
        comparison_path=new_comparison, adjudication_path=output,
    )
    if validation.get("status") != "valid_complete_manual_adjudication_shard":
        raise ValueError("Rebased adjudication failed independent validator")
    return {
        "book": book,
        "old_adjudication_sha256": expected_old_adjud_sha,
        "rebased_adjudication_sha256": _sha(data),
        "rebased_adjudication_sidecar_sha256": _sha(sidecar_data),
        "adjudicated_decisions": len(rows) - 1,
        "decision_rows_changed": 0,
        "comparison_disagreement_keys_changed": 0,
        "pass2_semantic_projection_sha256": semantic_proof["semantic_projection_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", choices=tuple(SCOPE))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(stable_json(rebase_book(args.book, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

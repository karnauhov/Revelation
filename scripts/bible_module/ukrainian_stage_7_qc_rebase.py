"""Explicit metadata-only SHA rebase of blocked Mark/Luke independent QC.

The original independent review and every QC result row remain frozen.  This
only reconnects the audit header/sidecar to the separately proved repaired
pass-2, comparison, and adjudication chain.  A source-choice blocking verdict
is deliberately preserved; this command never accepts a book.
"""

from __future__ import annotations

import argparse
import copy
from hashlib import sha256
from pathlib import Path
from typing import Any

from .ukrainian_stage_7_gold_compare import _key, validate_adjudication_qc, validate_adjudication_shard
from .ukrainian_stage_7_gold_rebase import _canonical_object, _write_identical_or_new
from .ukrainian_stage_7_model import stable_json
from .ukrainian_stage_7_provenance import BASE, _canonical_rows, prove_expanded_semantics


SCOPE = {
    "Mark": ("041", "753de840b931fe5e3fc84acc47ad7ea8c0abb1490ea8c1b6ad4844a1948414c3", "416193d237cbea34629525f9a2372d056a7e387f7fe668dbc76883559c3bd2ab"),
    "Luke": ("042", "9c34b5a29de75af485fa77dc241c93193f7843cae94e7272bc07c346fa8d8cc8", "c5df3e4b359c5e2048a96bd09f985629aceb52edd29387a9ff28068c1d51901b"),
}
_REBASE_KEYS = (
    "review_pass_2", "review_pass_2_manifest", "comparison", "comparison_manifest",
    "adjudication", "adjudication_manifest",
)


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _related_paths(book: str, shard: str) -> tuple[dict[str, Path], dict[str, Path], Path]:
    pass1 = BASE / f"external_chatgpt/uk7ext_gold_{book}_pass1_{shard}/completed_external/review_pass_1.shard_{shard}.raw.external-v1.canonical-v2.jsonl"
    old_pass2 = BASE / f"gold_compact_review/pass_2/{book}/completed/review_pass_2.shard_{shard}.raw.manual-v2.jsonl"
    new_pass2 = BASE / f"gold_compact_review/pass_2/{book}/provenance_repair/repro_run_1/review_pass_2.shard_{shard}.raw.provenance-v1.jsonl"
    old_comparison = BASE / f"gold_review_comparisons/{book}.pass1-pass2.disagreements.jsonl"
    new_comparison = BASE / f"gold_review_comparisons/provenance_repair/repro_run_1/{book}.pass1-pass2.disagreements.jsonl"
    old_adjudication = BASE / f"gold_review_adjudication/{book}/completed/{book}.shard_{shard}.pass1-pass2.third_adjudication.jsonl"
    new_adjudication = BASE / f"gold_review_adjudication/{book}/provenance_repair/repro_run_1/{book}.shard_{shard}.pass1-pass2.third_adjudication.jsonl"
    template = BASE / f"gold_compact_review/pass_2/{book}/review_pass_2.shard_{shard}.compact.template.jsonl"
    template_manifest = BASE / f"gold_compact_review/pass_2/{book}/gold_compact_review.manifest.json"
    shared = {"review_pass_1": pass1, "review_pass_1_manifest": Path(str(pass1) + ".manifest.json"), "answer_free_template": template, "answer_free_template_manifest": template_manifest}
    old = {**shared, "review_pass_2": old_pass2, "comparison": old_comparison, "adjudication": old_adjudication}
    new = {**shared, "review_pass_2": new_pass2, "comparison": new_comparison, "adjudication": new_adjudication}
    for values in (old, new):
        for key in ("review_pass_2", "comparison", "adjudication"):
            values[key + "_manifest"] = Path(str(values[key]) + ".manifest.json")
    qc = BASE / f"gold_review_adjudication/{book}/qc/completed/{book}.shard_{shard}.third_adjudication.blocking_content_qc.codex-20260912.jsonl"
    return old, new, qc


def _require_blocked_qc_complete(rows: list[dict[str, Any]], sidecar: dict[str, Any], adjudication: Path, book: str) -> None:
    if len(rows) < 2 or rows[0].get("record_type") != "qc_metadata":
        raise ValueError("Frozen QC has no canonical header/results")
    if rows[0].get("overall_verdict") != "uncertain" or rows[0].get("shard_blocked") is not True:
        raise ValueError("Frozen QC does not preserve its blocking verdict")
    if sidecar.get("shard_blocked") is not True or sidecar.get("overall_verdict") != "uncertain":
        raise ValueError("Frozen QC sidecar does not preserve its blocking verdict")
    if sidecar.get("error_count") != 0 or sidecar.get("counts", {}).get("full_grid_verdict", {}).get("error") != 0:
        raise ValueError("Frozen QC contains a content error")
    adjud_rows = _canonical_rows(adjudication.read_bytes())
    keys = [row.get("stable_key") for row in rows[1:]]
    expected = {_key(row) for row in adjud_rows[1:]}
    if len(keys) != len(set(keys)) or set(keys) != expected or any(row.get("record_type") != "qc_adjudication_result" for row in rows[1:]):
        raise ValueError("Frozen QC result scope differs from adjudication")
    counts = sidecar["counts"]
    if counts.get("audited_result_rows") != len(keys) or counts.get("full_final_grid") != len(keys) + counts.get("pass_agreed_decisions_checked", -1):
        raise ValueError("Frozen QC has incomplete full-grid accounting")
    verdict = counts["full_grid_verdict"]
    if verdict.get("accepted", -1) + verdict.get("uncertain", -1) != counts["full_final_grid"] or verdict.get("uncertain", 0) <= 0:
        raise ValueError("Frozen QC full-grid verdict is inconsistent")
    if sidecar.get("input_sha256", {}).get("adjudication") != _sha(adjudication):
        raise ValueError(f"Frozen {book} QC refers to another adjudication")


def rebase_blocked_qc(book: str, output: Path) -> dict[str, Any]:
    if book not in SCOPE:
        raise ValueError("Book is outside frozen QC rebase scope")
    shard, old_qc_sha, old_sidecar_sha = SCOPE[book]
    old, new, qc_path = _related_paths(book, shard)
    old_sidecar_path = Path(str(qc_path) + ".manifest.json")
    if _sha(qc_path) != old_qc_sha or _sha(old_sidecar_path) != old_sidecar_sha:
        raise ValueError("Frozen independent QC SHA-256 differs")
    rows = _canonical_rows(qc_path.read_bytes())
    sidecar = _canonical_object(old_sidecar_path)
    if sidecar.get("output_sha256", {}).get(qc_path.name) != old_qc_sha:
        raise ValueError("Frozen QC output lock differs")
    _require_blocked_qc_complete(rows, sidecar, old["adjudication"], book)
    for key in _REBASE_KEYS:
        if sidecar.get("input_sha256", {}).get(key) != _sha(old[key]) or rows[0].get("input_sha256", {}).get(key) != _sha(old[key]):
            raise ValueError(f"Frozen QC {key} input lock differs")
    proof = prove_expanded_semantics(old["review_pass_2"], new["review_pass_2"], book)
    old_adjud_rows = _canonical_rows(old["adjudication"].read_bytes())
    new_adjud_rows = _canonical_rows(new["adjudication"].read_bytes())
    if old_adjud_rows[1:] != new_adjud_rows[1:]:
        raise ValueError("Repaired adjudication changed decision rows")
    adjudication_validation = validate_adjudication_shard(
        pass1_path=new["review_pass_1"], pass2_path=new["review_pass_2"],
        comparison_path=new["comparison"], adjudication_path=new["adjudication"],
    )
    new_rows = copy.deepcopy(rows)
    new_sidecar = copy.deepcopy(sidecar)
    for key in _REBASE_KEYS:
        digest = _sha(new[key])
        new_rows[0]["input_sha256"][key] = digest
        new_sidecar["input_sha256"][key] = digest
        new_sidecar["input_bytes"][key] = new[key].stat().st_size
        new_sidecar["input_paths"][key] = str(new[key]).replace("/", "\\")
    if new_rows[1:] != rows[1:]:
        raise ValueError("Independent QC result rows changed")
    new_sidecar["check_adjudication_result"] = adjudication_validation
    new_sidecar["metadata_only_rebase"] = {
        "old_qc_sha256": old_qc_sha,
        "old_qc_sidecar_sha256": old_sidecar_sha,
        "qc_result_rows_changed": 0,
        "pass2_semantic_projection_sha256": proof["semantic_projection_sha256"],
        "book_accepted": False,
    }
    data = ("\n".join(stable_json(row) for row in new_rows) + "\n").encode("utf-8")
    new_sidecar["output_sha256"] = {output.name: sha256(data).hexdigest()}
    sidecar_data = (stable_json(new_sidecar) + "\n").encode("utf-8")
    _write_identical_or_new(output, data)
    _write_identical_or_new(Path(str(output) + ".manifest.json"), sidecar_data)
    try:
        validate_adjudication_qc(
            pass1_path=new["review_pass_1"], pass2_path=new["review_pass_2"],
            comparison_path=new["comparison"], adjudication_path=new["adjudication"],
            answer_free_template_path=new["answer_free_template"],
            answer_free_template_manifest_path=new["answer_free_template_manifest"],
            qc_path=output, qc_manifest_sha256=sha256(sidecar_data).hexdigest(),
        )
    except ValueError as exc:
        if str(exc) != "Independent adjudication QC status or reviewer independence differs":
            raise
    else:
        raise ValueError("Blocked QC unexpectedly passed book acceptance")
    return {
        "book": book,
        "old_qc_sha256": old_qc_sha,
        "rebased_qc_sha256": sha256(data).hexdigest(),
        "rebased_qc_sidecar_sha256": sha256(sidecar_data).hexdigest(),
        "qc_result_rows_changed": 0,
        "full_grid": new_sidecar["counts"]["full_final_grid"],
        "source_choice_uncertain": new_sidecar["counts"]["full_grid_verdict"]["uncertain"],
        "book_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", choices=tuple(SCOPE))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(stable_json(rebase_blocked_qc(args.book, args.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

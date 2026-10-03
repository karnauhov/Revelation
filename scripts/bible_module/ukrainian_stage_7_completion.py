"""Versioned book completion, separate from strict gold acceptance.

The projection is review evidence only. Consumers must validate its exact
locks before any later training/scoring/export; this module performs no export.
Frozen decisions and original QC verdicts are never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold import (
    _validate_final_grid,
    _validate_semantic_accounting,
)
from scripts.bible_module.ukrainian_stage_7_gold_compare import (
    _validated_post_adjudication_values,
)
from scripts.bible_module.ukrainian_stage_7_model import stable_json

COMPLETION_VERSION = "ukrainian-stage-7-registered-deferral-completion-v1"


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def canonical_bytes(value: Any) -> bytes:
    return (stable_json(value) + "\n").encode("utf-8")


def locked_file(spec: Mapping[str, Any], root: Path) -> Path:
    if set(spec) != {"path", "sha256", "bytes"}:
        raise ValueError("An exact path/SHA/byte lock is required")
    path = (root / spec["path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence is outside the repository")
    if (not path.is_file() or path.stat().st_size != spec["bytes"]
            or sha256_file(path) != spec["sha256"]):
        raise ValueError(f"Physical lock differs: {spec['path']}")
    return path


def emit_immutable(path: Path, data: bytes) -> None:
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"Refusing to replace sealed evidence: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)


def reciprocal_components(grid: Mapping[str, Mapping[str, Any]]) -> list[set[str]]:
    """Closed hyperedge components include grouped/function and NULL nodes."""
    originals = {row["original_token_id"]: key for key, row in grid.items() if key.startswith("original:")}
    targets = {row["target_token_id"]: key for key, row in grid.items() if key.startswith("target:")}
    if len(originals) + len(targets) != len(grid):
        raise ValueError("Duplicate physical node IDs")
    graph = {key: {key} for key in grid}
    for key, row in grid.items():
        if key.startswith("original:"):
            sources = row["group_original_token_ids"]
            destinations = row["target_token_ids"]
        else:
            sources = row["linked_original_token_ids"]
            destinations = [row["target_token_id"]]
        try:
            members = {key} | {originals[item] for item in sources} | {targets[item] for item in destinations}
        except KeyError as error:
            raise ValueError("Unknown reciprocal node") from error
        if any(grid[item]["target_ref"] != row["target_ref"] for item in members):
            raise ValueError("Cross-verse reciprocal edge")
        for member in members:
            graph[member].update(members)
    components = []
    remaining = set(grid)
    while remaining:
        component = set()
        pending = {min(remaining)}
        while pending:
            member = pending.pop()
            if member in component:
                continue
            component.add(member)
            pending.update(graph[member] - component)
        remaining -= component
        components.append(component)
    return components


def reciprocal_edges(grid: Mapping[str, Mapping[str, Any]], keys: set[str]) -> list[dict[str, Any]]:
    edges = {}
    for key in sorted(keys):
        row = grid[key]
        if not key.startswith("original:") or not row["target_token_ids"]:
            continue
        edge = {"target_ref": row["target_ref"], "relation": row["relation"],
                "original_token_ids": sorted(row["group_original_token_ids"]),
                "target_token_ids": sorted(row["target_token_ids"])}
        identity = "gold7:edge:" + hashlib.sha256(stable_json(edge).encode("utf-8")).hexdigest()[:32]
        edges[identity] = {"edge_id": identity, **edge}
    return [edges[key] for key in sorted(edges)]


def build_projection(
    grid: Mapping[str, Mapping[str, Any]],
    observations: Sequence[Mapping[str, Any]],
    issues: Sequence[Mapping[str, Any]],
    *, reviewer_id: str, author_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Require complete independent QC and registered closed exclusions."""
    if not reviewer_id or reviewer_id in author_ids:
        raise ValueError("Reviewer authored reviewed work")
    checked = {}
    for row in observations:
        key = row.get("stable_key")
        if key not in grid or key in checked:
            raise ValueError("QC contains an extra or duplicate stable key")
        if (row.get("final_decision") != grid[key]
                or row.get("reviewer_id") != reviewer_id
                or row.get("reciprocal_accounting_checked") is not True
                or row.get("verdict") not in {"accepted", "uncertain", "error"}
                or not str(row.get("rationale", "")).strip()):
            raise ValueError(f"QC payload/evidence differs: {key}")
        checked[key] = row
    if set(checked) != set(grid):
        raise ValueError("QC does not cover the complete final grid")
    unresolved = {key for key, row in checked.items() if row["verdict"] != "accepted"}
    registered: dict[str, str] = {}
    issue_ids = set()
    for issue in issues:
        issue_id = issue.get("issue_id")
        if not issue_id or issue_id in issue_ids:
            raise ValueError("Absent or duplicate issue ID")
        issue_ids.add(issue_id)
        keys = issue.get("affected_stable_keys", [])
        if (not keys or len(keys) != len(set(keys))
                or issue.get("status") != "deferred_strong_unassigned"
                or issue.get("strong_assignment") is not None
                or issue.get("new_Strong_assigned") is not False
                or issue.get("leave_without_Strong") is not True
                or not issue.get("missing_proof")
                or not issue.get("input_digests")
                or not issue.get("attempted_alternatives")
                or not issue.get("evidence_files")
                or not issue.get("module_code") or not issue.get("edition")
                or not issue.get("follow_up")
                or issue.get("qc_verdict") not in {"uncertain", "error"}):
            raise ValueError("Deferral lacks scope, research or unassigned policy")
        for key in keys:
            if key not in grid or key in registered:
                raise ValueError("Deferral has an unknown or duplicated stable key")
            if issue.get("target_ref") != grid[key]["target_ref"]:
                raise ValueError("Deferral verse differs")
            registered[key] = issue_id
    excluded = set()
    for component in reciprocal_components(grid):
        if component & unresolved:
            excluded.update(component)
    if set(registered) != excluded:
        raise ValueError("Registered exclusions are not the exact closed unresolved components")
    # A dependency can be accepted content but must be unassigned if it shares
    # an unresolved hyperedge. Its content verdict remains accepted.
    projection = []
    for key in sorted(grid):
        decision = grid[key]
        deferred = key in excluded
        effective = dict(decision)
        if deferred:
            # Preserve node identity, without carrying an unproved frozen
            # omission/addition classification into the effective layer.
            effective = {field: decision[field] for field in (
                "record_type", "target_ref", "original_token_id", "target_token_id"
            ) if field in decision}
            for field in ("target_token_ids", "linked_original_token_ids", "group_original_token_ids"):
                if field in decision:
                    effective[field] = []
        projection.append({
            "stable_key": key, "target_ref": decision["target_ref"],
            "frozen_decision_sha256": hashlib.sha256(canonical_bytes(decision)).hexdigest(),
            "content_verdict": checked[key]["verdict"],
            "assignment_status": "deferred_strong_unassigned" if deferred else "accepted_alignment_evidence",
            "effective_decision": effective,
            "assigned_strongs": [],
            "strong_assignment": None,
            "issue_id": registered.get(key),
            "include_in_training": not deferred, "include_in_scoring": not deferred,
            "include_in_strong_export": not deferred,
            "null_omission_asserted_by_overlay": False,
            "translation_addition_asserted_by_overlay": False,
        })
    excluded_edges = reciprocal_edges(grid, excluded)
    return projection, {
        "reviewed_decision_labels": len(grid), "effective_proven_decision_labels": len(grid) - len(excluded),
        "deferred_decision_labels": len(excluded), "registered_issues": len(issues),
        "content_errors": sum(row["verdict"] == "error" for row in checked.values()),
        "content_uncertainties": sum(row["verdict"] == "uncertain" for row in checked.values()),
        "excluded_reciprocal_edges": len(excluded_edges),
        "accepted_dependency_exclusions": sum(checked[key]["verdict"] == "accepted" for key in excluded),
        "excluded_stable_keys": sorted(excluded),
    }


def validate_config(config_path: Path, root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    config = read_json(config_path)
    if config.get("completion_version") != COMPLETION_VERSION:
        raise ValueError("Completion version differs")
    chain = {name: locked_file(spec, root) for name, spec in config["chain"].items()}
    # Verify all physical locks before parsing the full work files.
    observation_path = locked_file(config["observations"], root)
    ledger_path = locked_file(config["ledger"], root)
    attestation = read_json(locked_file(config["role_attestation"], root))
    if (attestation.get("reviewer_id") != config["reviewer_id"]
            or attestation.get("actual_role") != "independent_content_and_completion_reviewer"
            or attestation.get("reviewed_author_ids") != sorted(set(config["author_ids"]))
            or attestation.get("no_authorship_of_reviewed_research_corrections_ledger_validator") is not True
            or not attestation.get("independence_basis")):
        raise ValueError("Actual reviewer role attestation differs")
    for spec in config["evidence_locks"]:
        locked_file(spec, root)
    lock_map = {spec["path"]: spec["sha256"] for spec in (
        *config["chain"].values(), config["observations"],
        config["role_attestation"], *config["evidence_locks"],
    )}
    metadata1, metadata2, pass1, pass2, grid, adjudicator = _validated_post_adjudication_values(
        pass1_path=chain["pass1"], pass2_path=chain["pass2"],
        comparison_path=chain["comparison"], adjudication_path=chain["adjudication"],
    )
    if len(grid) != config["expected_grid_count"] or {r["target_ref"].split(".")[0] for r in grid.values()} != {config["book"]}:
        raise ValueError("Book/grid scope differs")
    _validate_final_grid(grid, pass1)
    _validate_semantic_accounting(
        {k.removeprefix("original:"): v for k, v in grid.items() if k.startswith("original:")},
        {k.removeprefix("target:"): v for k, v in grid.items() if k.startswith("target:")},
    )
    frozen_authors = {metadata1["reviewer_id"], metadata2["reviewer_id"], adjudicator}
    frozen_authors.update(row.get("reviewer_id") for row in (*pass1.values(), *pass2.values()))
    if config["reviewer_id"] in frozen_authors:
        raise ValueError("Reviewer authored frozen passes or adjudication")
    templates = {row["target_ref"]: row for row in read_rows(chain["answer_free_template"])}
    observations = read_rows(observation_path)
    for row in observations:
        key = row.get("stable_key")
        if key not in grid or grid[key]["target_ref"] not in templates:
            raise ValueError("Observation/answer-free verse scope differs")
        decision = grid[key]
        template = templates[decision["target_ref"]]
        originals = {item["original_token_id"]: item for item in template["original_index"]}
        targets = {item["target_token_id"]: item for item in template["target_index"]}
        source_ids = (decision["group_original_token_ids"] if key.startswith("original:") else decision["linked_original_token_ids"])
        target_ids = (decision["target_token_ids"] if key.startswith("original:") else [decision["target_token_id"]])
        if key.startswith("original:"):
            source_ids = sorted(set(source_ids) | {decision["original_token_id"]})
        expected_sources = [originals[item] for item in source_ids]
        expected_targets = [targets[item] for item in target_ids]
        if row.get("source_evidence") != expected_sources or row.get("target_evidence") != expected_targets:
            raise ValueError(f"Exact source/target span evidence differs: {key}")
    ledger = read_rows(ledger_path)
    ids = [row.get("issue_id") for row in ledger]
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError("Shared issue inventory has absent/duplicate IDs")
    wanted = config["deferral_issue_ids"]
    if len(wanted) != len(set(wanted)) or not set(wanted) <= set(ids):
        raise ValueError("Completion issue IDs differ from shared inventory")
    issues = [row for row in ledger if row["issue_id"] in wanted]
    if any(row.get("book") != config["book"] for row in issues):
        raise ValueError("Completion inventory book differs")
    for issue in issues:
        for spec in issue["evidence_files"]:
            locked_file({key: spec[key] for key in ("path", "sha256", "bytes")}, root)
        if any(lock_map.get(path) != digest for path, digest in issue["input_digests"].items()):
            raise ValueError("Issue input digest is absent from exact physical locks")
        expected_edges = reciprocal_edges(grid, set(issue["affected_stable_keys"]))
        if issue.get("excluded_reciprocal_edges") != expected_edges or issue.get("edge_count") != len(expected_edges):
            raise ValueError("Issue exact reciprocal edge exclusions differ")
        if issue["input_digests"].get(config["observations"]["path"]) != config["observations"]["sha256"]:
            raise ValueError("Issue does not bind exact independent observation digest")
        decisions = {row["stable_key"]: row for row in issue["individual_decisions"]}
        if len(decisions) != len(issue["individual_decisions"]) or set(decisions) != set(issue["affected_stable_keys"]):
            raise ValueError("Issue individual accounting scope differs")
        observation_map = {row["stable_key"]: row for row in observations}
        for key, item in decisions.items():
            actual = observation_map[key]
            if (item.get("alignment_snapshot") != grid[key]
                    or item.get("current_content_verdict") != actual["verdict"]
                    or item.get("source_evidence") != actual["source_evidence"]
                    or item.get("target_evidence") != actual["target_evidence"]):
                raise ValueError("Issue frozen token/span/content proof differs")
    return build_projection(grid, observations, issues,
                            reviewer_id=config["reviewer_id"], author_ids=set(config["author_ids"]))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    projection, counts = validate_config(args.config, root)
    data = b"".join(canonical_bytes(row) for row in projection)
    if args.check:
        if not args.projection.is_file() or args.projection.read_bytes() != data:
            raise ValueError("Effective projection is absent or differs from live inputs")
    else:
        emit_immutable(args.projection, data)
    print(json.dumps({"status": "completion_projection_verified", "counts": counts,
                      "projection_sha256": hashlib.sha256(data).hexdigest()}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

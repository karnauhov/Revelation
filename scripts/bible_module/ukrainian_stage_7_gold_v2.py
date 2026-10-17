"""Deferral-aware global gold, isolated from strict v1/v2 gold acceptance.

This version assembles completed books; it never promotes an uncertain QC
verdict to accepted, invents a NULL, or exports production Strong markup.
The eligibility mask is frozen before candidate evaluation and is the sole
denominator contract for later consumers. All dependencies remain live locks.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.bible_module import ukrainian_stage_7_gold as strict
from scripts.bible_module.ukrainian_stage_7_completion_v2 import (
    build_projection, canonical_bytes, emit_immutable, reciprocal_components,
    sha256_file, validate_registry_snapshot, validated_completion_grid,
)
from scripts.bible_module.ukrainian_stage_7_gold_compare import (
    _key, validate_adjudication_qc, validate_post_consensus_correction_qc,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION, SCHEMA_VERSION, stable_json,
)

ROOT = strict.ROOT
VERSION = "ukrainian-stage-7-deferral-aware-global-gold-v2"
REGISTRY_VERSION = "ukrainian-stage-7-global-completion-correction-registry-v2"
ANNOTATIONS_FILENAME = "gold_alignment.annotations.v2.jsonl"
ELIGIBILITY_FILENAME = "gold_alignment.eligibility.v2.jsonl"
MANIFEST_FILENAME = "gold_alignment.finalized.v2.manifest.json"
LOCK_FILENAME = "gold_alignment.finalized.v2.lock.json"
REGISTRY_FILENAME = "gold_finalization_registry.v2.manifest.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list[dict[str, Any]]:
    return list(strict._read_jsonl(path))


def file_spec(path: Path, root: Path = ROOT) -> dict[str, Any]:
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": sha256_file(path), "bytes": path.stat().st_size}


class PhysicalLocks:
    """One physical hash per exact path in a validation run; no silent rebase."""
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.checked: dict[str, dict[str, Any]] = {}

    def check(self, spec: Mapping[str, Any]) -> Path:
        if set(spec) != {"path", "sha256", "bytes"}:
            raise ValueError("Exact path/SHA/byte lock required")
        if (not isinstance(spec["path"], str) or Path(spec["path"]).is_absolute()
                or not isinstance(spec["bytes"], int) or isinstance(spec["bytes"], bool)
                or spec["bytes"] < 0):
            raise ValueError("Invalid physical lock")
        strict._require_sha256(spec["sha256"], "Physical lock")
        path = (self.root / spec["path"]).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Evidence path escapes root")
        previous = self.checked.get(spec["path"])
        if previous is not None and previous != dict(spec):
            raise ValueError("Conflicting physical locks")
        if previous is None:
            if (not path.is_file() or path.stat().st_size != spec["bytes"]
                    or sha256_file(path) != spec["sha256"]):
                raise ValueError(f"Missing/stale physical dependency: {spec['path']}")
            self.checked[spec["path"]] = dict(spec)
        return path


def _all_specs(value: Any):
    if isinstance(value, Mapping):
        if set(value) == {"path", "sha256", "bytes"}:
            yield value
        else:
            for child in value.values():
                yield from _all_specs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_specs(child)


def _check_registry_header(registry: Mapping[str, Any], *, production: bool):
    if (registry.get("registry_version") != REGISTRY_VERSION
            or registry.get("artifact") != "gold_finalization_completion_registry"
            or registry.get("status") != "complete_sha_locked_book_roster"
            or registry.get("gold_workflow_version") != VERSION):
        raise ValueError("Global completion registry contract differs")
    books = registry.get("books", {})
    if not books or (production and set(books) != set(strict.BOOKS)):
        raise ValueError("Global registry requires exact 66-book roster")
    if registry.get("corpus_contract") not in {"ohienko_1988_production", "CC0_fixture"}:
        raise ValueError("Unknown corpus contract")
    strict_books = sorted(k for k, v in books.items() if v["status"] == "strictly_accepted")
    deferred_books = sorted(k for k, v in books.items() if v["status"] == "completed_with_registered_deferrals")
    if set(strict_books) & set(deferred_books) or set(strict_books + deferred_books) != set(books):
        raise ValueError("Book completion status differs")
    if production and (len(strict_books), len(deferred_books)) != (38, 28):
        raise ValueError("Frozen strict/completion checkpoint differs")
    return strict_books, deferred_books


def build_eligibility(
    grid: Mapping[str, Mapping[str, Any]],
    excluded_by_key: Mapping[str, str],
) -> list[dict[str, Any]]:
    """Keep every physical node once, with closed reciprocal exclusions."""
    if set(excluded_by_key) - set(grid):
        raise ValueError("Deferred scope contains unknown stable IDs")
    originals = {row["original_token_id"]: key for key, row in grid.items() if key.startswith("original:")}
    targets = {row["target_token_id"]: key for key, row in grid.items() if key.startswith("target:")}
    if len(originals) + len(targets) != len(grid):
        raise ValueError("Duplicate physical original/target node")
    excluded_keys = excluded_by_key.keys()
    for key, row in grid.items():
        sources = row["group_original_token_ids"] if key.startswith("original:") else row["linked_original_token_ids"]
        destinations = row["target_token_ids"] if key.startswith("original:") else [row["target_token_id"]]
        try:
            members = {key} | {originals[item] for item in sources} | {targets[item] for item in destinations}
        except KeyError as error:
            raise ValueError("Unknown reciprocal node") from error
        if any(grid[item]["target_ref"] != row["target_ref"] for item in members):
            raise ValueError("Cross-verse reciprocal edge")
        # Closure on each declared hyperedge implies closure on every
        # connected component, without a quadratic global component ordering.
        if members & excluded_keys and not members <= excluded_keys:
            raise ValueError("Eligibility exclusion breaks reciprocal closure")
    physical = set()
    result = []
    for key in sorted(grid):
        value = grid[key]
        expected = _key(value)
        if expected != key:
            raise ValueError("Stable key/decision identity differs")
        id_field = "original_token_id" if key.startswith("original:") else "target_token_id"
        node = (id_field, value[id_field])
        if node in physical:
            raise ValueError("Duplicate physical original/target node")
        physical.add(node)
        eligible = key not in excluded_by_key
        result.append({
            "record_type": "gold_eligibility", "schema_version": 2,
            "gold_workflow_version": VERSION, "stable_key": key,
            "target_ref": value["target_ref"], id_field: value[id_field],
            "eligible": eligible,
            "assignment_status": "accepted_alignment_evidence" if eligible else "deferred_strong_unassigned",
            "issue_ids": [] if eligible else [excluded_by_key[key]],
            "frozen_decision_sha256": sha256(canonical_bytes(value)).hexdigest(),
        })
    return result


def make_annotations(grid, pass1, pass2, excluded, *, adjudicator, adjudicated_keys,
                     correction_provenance=None):
    eligible = {key: value for key, value in grid.items() if key not in excluded}
    strict._validate_semantic_accounting(
        {k.removeprefix("original:"): v for k, v in eligible.items() if k.startswith("original:")},
        {k.removeprefix("target:"): v for k, v in eligible.items() if k.startswith("target:")},
    )
    result = strict._make_final_rows(eligible, pass1, pass2, adjudicator=adjudicator,
                                    adjudicated_keys=adjudicated_keys,
                                    correction_provenance_by_key={key: value for key, value in (correction_provenance or {}).items()
                                                                 if key in eligible})
    for value in result:
        value["gold_workflow_version"] = VERSION
        value["eligibility"] = "proven"
    for key in sorted(excluded):
        frozen = grid[key]
        original = key.startswith("original:")
        result.append({
            "schema_version": 2, "contract_version": CONTRACT_VERSION,
            "gold_workflow_version": VERSION,
            "record_type": "deferred_original_decision" if original else "deferred_target_accounting",
            "stable_key": key, "target_ref": frozen["target_ref"],
            ("decision_id" if original else "accounting_id"): key.split(":", 1)[1],
            ("original_token_id" if original else "target_token_id"):
                frozen["original_token_id" if original else "target_token_id"],
            "status": "deferred_strong_unassigned", "strong_assignment": None,
            "issue_ids": [excluded[key]], "eligible": False,
            "include_in_training": False, "include_in_scoring": False,
            "include_in_strong_export": False,
            "frozen_decision_sha256": sha256(canonical_bytes(frozen)).hexdigest(),
        })
    return sorted(result, key=lambda r: (strict.BOOK_NUMBER[r["target_ref"].split(".")[0]],
                  r["target_ref"], r["record_type"],
                  str(r.get("edge_id") or r.get("decision_id") or r.get("accounting_id"))))


def coverage(mask: Sequence[Mapping[str, Any]], grid: Mapping[str, Mapping[str, Any]],
             panel: Sequence[Mapping[str, Any]] | None = None):
    groups: dict[str, dict[str, Counter]] = {name: defaultdict(Counter) for name in
                                           ("book", "testament", "fold", "stratum", "selection_stratum")}
    verse_groups = {name: defaultdict(lambda: {"full": set(), "proven": set(), "deferred": set()})
                    for name in groups}
    all_refs, eligible_refs = set(), set()
    panel_map = {row["target_ref"]: row for row in panel} if panel is not None else {}
    if panel is not None:
        if len(panel_map) != len(panel) or set(panel_map) != {row["target_ref"] for row in mask}:
            raise ValueError("Frozen selection panel verse roster differs")
        originals_by_ref = defaultdict(set)
        for row in mask:
            if "original_token_id" in row:
                originals_by_ref[row["target_ref"]].add(row["original_token_id"])
        for ref, selection in panel_map.items():
            fold = int(sha256(ref.encode()).hexdigest()[:8], 16) % 5
            if selection["fold_id"] != fold:
                raise ValueError("Computed fold differs from frozen selection panel")
            if set(selection["original_token_ids"]) != originals_by_ref[ref]:
                raise ValueError("Frozen selection panel original node roster differs")
    for row in mask:
        ref = row["target_ref"]
        book = ref.split(".")[0]
        all_refs.add(ref)
        original = row["stable_key"].startswith("original:")
        eligible = row["eligible"]
        if eligible and original:
            eligible_refs.add(ref)
        strata = grid[row["stable_key"]].get("phenomena", []) or ["unclassified"]
        dimensions = {"book": [book], "testament": ["OT" if strict.BOOK_NUMBER[book] <= 39 else "NT"],
                      "fold": [str(int(sha256(ref.encode()).hexdigest()[:8], 16) % 5)],
                      "stratum": sorted(set(strata))}
        if ref in panel_map:
            dimensions["selection_stratum"] = []
            for name, value in sorted(panel_map[ref]["strata"].items()):
                for item in value if isinstance(value, list) else [value]:
                    dimensions["selection_stratum"].append(name + ":" + str(item))
        for dimension, labels in dimensions.items():
            for label in labels:
                counts = groups[dimension][label]
                verse_groups[dimension][label]["full"].add(ref)
                if original:
                    verse_groups[dimension][label]["proven" if eligible else "deferred"].add(ref)
                counts["full_labels"] += 1
                counts["eligible_labels" if eligible else "deferred_labels"] += 1
                if original:
                    counts["full_original_decisions"] += 1
                    counts["eligible_original_decisions" if eligible else "deferred_original_decisions"] += 1
    for dimension, labels in groups.items():
        for label, counter in labels.items():
            refs = verse_groups[dimension][label]
            counter["full_verses"] = len(refs["full"])
            counter["proven_verses"] = len(refs["proven"])
            counter["verses_with_deferred_originals"] = len(refs["deferred"])
            counter["deferred_only_verses"] = len(refs["deferred"] - refs["proven"])
    return {"full_verses": len(all_refs), "proven_verses": len(eligible_refs),
            "full_original_decisions": sum(r["stable_key"].startswith("original:") for r in mask),
            "eligible_original_decisions": sum(r["eligible"] and r["stable_key"].startswith("original:") for r in mask),
            "full_target_labels": sum(r["stable_key"].startswith("target:") for r in mask),
            "full_labels": len(mask), "eligible_labels": sum(r["eligible"] for r in mask),
            "deferred_labels": sum(not r["eligible"] for r in mask),
            "by": {name: {label: dict(sorted(counter.items())) for label, counter in sorted(values.items())}
                   for name, values in groups.items()},
            "threshold_denominator": "eligible_original_decisions_only; target, hyperedge and negative records excluded"}


def _jsonl_bytes(values):
    return b"".join(canonical_bytes(value) for value in values)


def add_source_frequency_proof(mask, annotations, universe_rows, selected_rows):
    """Reproduce frozen selector frequencies, independent of gold decisions.

    Membership requires the exact original token, not merely a verse whose
    panel contains a rare/frequent band. These are source facts, never new
    reviewer labels or Strong assignments.
    """
    frequencies = Counter()
    seen = set()
    for row in universe_rows:
        identity = row["original_token_id"]
        if identity in seen:
            raise ValueError("Frequency universe duplicates an original node")
        seen.add(identity)
        reading = str(row["reading_status"])
        if reading.startswith("primary_") and "unresolved" not in reading:
            frequencies.update(row["strong_classic"])
    wanted = {row["original_token_id"]: row for row in mask if "original_token_id" in row}
    found = set()
    proofs = {}
    counters = defaultdict(Counter)
    verse_sets = defaultdict(lambda: {"full": set(), "proven": set(), "deferred": set()})
    for row in selected_rows:
        identity = row["original_token_id"]
        if identity not in wanted:
            continue
        if identity in found or row["target_ref"] != wanted[identity]["target_ref"]:
            raise ValueError("Frequency source selected node/ref differs")
        found.add(identity)
        evidence = [{"strong_classic": strong, "primary_universe_frequency": frequencies[strong],
                     "frequency_band": ("rare_1_to_5" if frequencies[strong] <= 5 else
                                        "frequent_1000_plus" if frequencies[strong] >= 1000 else "mid_frequency")}
                    for strong in sorted(set(row["strong_classic"]))]
        bands = {item["frequency_band"] for item in evidence}
        classes = sorted(({"rare_lemma"} if "rare_1_to_5" in bands else set()) |
                         ({"frequent_lemma"} if "frequent_1000_plus" in bands else set()))
        original = wanted[identity]
        proof = {"stable_key": original["stable_key"], "original_token_id": identity,
                 "target_ref": row["target_ref"], "frequency_evidence": evidence,
                 "selected_source_row_sha256": sha256(canonical_bytes(row)).hexdigest()}
        derived = {"frequency_classes": classes, "frequency_evidence": evidence,
                   "proof_sha256": sha256(canonical_bytes(proof)).hexdigest(),
                   "selected_source_row_sha256": proof["selected_source_row_sha256"],
                   "basis": "frozen_primary_universe_classic_frequency",
                   "source_frequency_is_strong_assignment": False}
        original["derived_source_strata"] = derived
        proofs[original["stable_key"]] = proof
        for band in bands:
            count = counters[band]
            count["full_original_decisions"] += 1
            count["eligible_original_decisions" if original["eligible"] else "deferred_original_decisions"] += 1
            verse_sets[band]["full"].add(row["target_ref"])
            verse_sets[band]["proven" if original["eligible"] else "deferred"].add(row["target_ref"])
    if found != set(wanted):
        raise ValueError("Frequency proof misses a frozen original node")
    for row in annotations:
        if row["record_type"] == "original_decision":
            row["derived_source_strata"] = wanted[row["original_token_id"]]["derived_source_strata"]
    for band, count in counters.items():
        values = verse_sets[band]
        count.update(full_verses=len(values["full"]), proven_verses=len(values["proven"]),
                     verses_with_deferred_originals=len(values["deferred"]),
                     deferred_only_verses=len(values["deferred"] - values["proven"]))
    return {"basis": "frozen primary_* non-unresolved Strong classic frequency; rare<=5; frequent>=1000",
            "by_band": {band: dict(sorted(count.items())) for band, count in sorted(counters.items())},
            "per_original_proof_sha256": sha256(_jsonl_bytes(proofs[key] for key in sorted(proofs))).hexdigest(),
            "proven_original_nodes": sum(row["eligible"] for row in wanted.values()),
            "reviewed_phenomena_changed": False, "source_frequency_is_strong_assignment": False}


def _active_overlay_paths(report_dir: Path) -> list[Path]:
    """Select latest numeric versions in each explicit overlay family."""
    import re
    chosen = {}
    families = ("gold_group_*source_resolution*.manifest.json",
                "gold_group_*source_disposition*.manifest.json",
                "gold_group_*completion_policy*.manifest.json",
                "gold_group_*independent_content_qc*.manifest.json",
                "gold_group_*final_content_qc*.manifest.json",
                "gold_group_*preserved_inputs*.manifest.json",
                "gold_group_*registry_formatting_bridge*.manifest.json")
    for pattern in families:
        for path in report_dir.glob(pattern):
            match = re.fullmatch(r"(.+)\.v(\d+)\.manifest\.json", path.name)
            if match:
                stem, version = match.group(1), int(match.group(2))
                if stem not in chosen or chosen[stem][0] < version:
                    chosen[stem] = (version, path)
    return sorted((item[1] for item in chosen.values()), key=lambda p: p.name)


def build_finalization_registry(report_dir: Path, work_dir: Path, output_path: Path,
                                *, root: Path = ROOT):
    """Build a new correction/completion trust root from the latest checkpoint.

    The sealed physical inventory is a digest locator, never a substitute for
    checking the selected files. A historical locator requires an explicit
    path/SHA bridge in this new registry; no validator silently falls back.
    """
    checkpoint_path = report_dir / "gold_completion_registry.v28.manifest.json"
    checkpoint = read_json(checkpoint_path)
    if (checkpoint.get("completed_book_count"), checkpoint.get("strict_fully_accepted_book_count"),
            checkpoint.get("completed_with_deferrals_book_count")) != (66, 38, 28):
        raise ValueError("Latest completion checkpoint is not 66/38/28")
    inventory = read_json(report_dir / "artifact_inventory.manifest.json")
    digest_index = defaultdict(list)
    exact_index = {}
    for item in inventory["entries"]:
        path = (report_dir if item["root"] == "report" else work_dir) / item["path"]
        spec = {"path": path.resolve().relative_to(root.resolve()).as_posix(),
                "sha256": item["sha256"], "bytes": item["bytes"]}
        digest_index[item["sha256"]].append(spec)
        exact_index[spec["path"]] = spec
    bridges = {}

    def locate(digest, preferred=None, *, sidecar_digest=None):
        choices = digest_index.get(digest, [])
        if sidecar_digest:
            for choice in sorted(choices, key=lambda s: (len(s["path"]), s["path"])):
                payload = root / choice["path"]
                sidecars = [Path(str(payload) + ".manifest.json"), payload.with_suffix(".manifest.json")]
                if any(path.is_file() and sha256_file(path) == sidecar_digest for path in sidecars):
                    return choice
            raise ValueError("No payload path has the exact accepted adjacent sidecar")
        if preferred and preferred in exact_index and exact_index[preferred]["sha256"] == digest:
            return exact_index[preferred]
        if preferred and preferred not in exact_index and (root / preferred).is_file():
            candidate = file_spec(root / preferred, root)
            if candidate["sha256"] == digest:
                exact_index[preferred] = candidate
                digest_index[digest].append(candidate)
                return candidate
        if not choices:
            raise ValueError(f"No preserved physical file for exact digest {digest}: {preferred}")
        choices = sorted(choices, key=lambda s: ("snapshot" not in s["path"], len(s["path"]), s["path"]))
        spec = choices[0]
        if preferred and spec["path"] != preferred:
            bridges[(preferred, digest)] = {
                "historical_path": preferred, "historical_sha256": digest,
                "preserved_file": spec,
                "resolution": "explicit_exact_SHA_preserved_ancestry_no_live_acceptance_claim",
            }
        return spec

    def normalized_spec(spec):
        return locate(spec["sha256"], spec["path"])

    entries = {}
    for completion_spec in checkpoint["completion_manifests"]:
        manifest_spec = normalized_spec(completion_spec)
        manifest = read_json(root / manifest_spec["path"])
        book = manifest["book"]
        if manifest.get("status") != "completed_with_registered_deferrals" or manifest.get("strict_fully_accepted") is not False:
            raise ValueError("Completion manifest relabels strict QC")
        projection = normalized_spec(manifest["effective_projection"])
        if "completion_config" in manifest:
            config_spec = normalized_spec(manifest["completion_config"])
            config = read_json(root / config_spec["path"])
            chain = {name: normalized_spec(spec) for name, spec in config["chain"].items()}
            evidence = [normalized_spec(spec) for spec in config["evidence_locks"]]
            entry = {"status": manifest["status"], "acceptance_manifest": manifest_spec,
                     "completion_config": config_spec, "chain": chain,
                     "observations": normalized_spec(config["observations"]),
                     "historical_ledger": normalized_spec(config["ledger"]),
                     "role_attestation": normalized_spec(config["role_attestation"]),
                     "evidence": evidence, "effective_projection": projection,
                     "independent_completion_review": normalized_spec(manifest["independent_completion_review"])}
            if "registry_snapshot" in config:
                entry["historical_registry_snapshot"] = normalized_spec(config["registry_snapshot"])
        else:
            # Zeph predates the generic completion contract. Its exact full
            # independent observations are retained, including both uncertain
            # nodes in Zeph.2.14; do not call its blocking QC accepted.
            provenance_path = next(path for path in manifest["input_sha256"] if "book_provenance" in path)
            provenance_spec = locate(manifest["input_sha256"][provenance_path], provenance_path)
            provenance = read_json(root / provenance_spec["path"])
            batch_path = report_dir / f"gold_adjudication_batch_{strict.BOOK_NUMBER[book]:03}.manifest.json"
            batch = read_json(batch_path)
            chain = _chain_from_batch(book, batch, locate, report_dir, root)
            entry = {"status": manifest["status"], "legacy_zeph_contract": True,
                     "acceptance_manifest": manifest_spec, "chain": chain,
                     "observations": locate(provenance["full_grid_sha256"], provenance["full_grid_path"]),
                     "provenance": provenance_spec, "effective_projection": projection,
                     "evidence": [locate(digest, path) for path, digest in manifest["input_sha256"].items()],
                     "independent_completion_review": normalized_spec(manifest["independent_completion_review"])}
        entries[book] = entry
    strict_books = set(checkpoint["strict_fully_accepted_books"])
    for batch_path in sorted(report_dir.glob("gold_adjudication_batch_*.manifest.json")):
        batch = read_json(batch_path)
        for book in set(batch.get("books", {})) & strict_books:
            if book in entries:
                raise ValueError("Duplicate strict/completion book manifest")
            if batch.get("status") != "partial_gold_adjudication_complete_qc_accepted":
                raise ValueError("Strict book lacks accepted status")
            chain = _chain_from_batch(book, batch, locate, report_dir, root)
            entries[book] = {"status": "strictly_accepted", "acceptance_manifest": file_spec(batch_path, root),
                             "chain": chain, "evidence": [locate(digest) for label, digest in
                                batch.get("output_sha256", {}).items() if label.startswith(book + ".")],
                             "expected_counts": batch["books"][book]}
    packet_manifest_path = work_dir / "gold_reviewer_packets/gold_reviewer_packets.manifest.json"
    if not packet_manifest_path.exists():
        alternatives = list(work_dir.glob("**/gold_reviewer_packets.manifest.json"))
        if len(alternatives) != 1:
            raise ValueError("Canonical reviewer packet manifest is ambiguous")
        packet_manifest_path = alternatives[0]
    packet_manifest = read_json(packet_manifest_path)
    inputs = {name: locate(digest) for name, digest in packet_manifest["input_sha256"].items()}
    inputs["reviewer_packets_manifest"] = file_spec(packet_manifest_path, root)
    packet_digest = packet_manifest["output_sha256"].get("review_pass_1.packet.jsonl")
    if packet_digest is None:
        packet_digest = next(digest for name, digest in packet_manifest["output_sha256"].items()
                             if "pass_1" in name and name.endswith(".jsonl"))
    inputs["frozen_packet"] = locate(packet_digest)
    stage6_manifest_path = root / "scripts/bible_module/reports/ukrainian_stage_6_20260801/synthesized_text.manifest.json"
    stage6_manifest = read_json(stage6_manifest_path)
    inputs["stage6_synthesis_manifest"] = file_spec(stage6_manifest_path, root)
    for label, name in (("stage5_forward", "source_to_target_map"), ("stage5_reverse", "target_to_source_map"),
                        ("stage5_footnotes", "footnote_projection")):
        path = root / f"scripts/bible_module/work/ukrainian_stage_5_20260801/{name}.jsonl"
        spec = file_spec(path, root)
        if spec["sha256"] != stage6_manifest["input_sha256"][label]:
            raise ValueError("Frozen stage5 mapping differs from stage6 synthesis")
        inputs[label] = spec
    active_overlay_paths = _active_overlay_paths(report_dir)
    for path in active_overlay_paths:
        overlay = read_json(path)
        for resolution in overlay.get("historical_input_lock_resolutions", []):
            if "historical_lock" in resolution:
                historical = resolution["historical_lock"]
                target = resolution["resolved_immutable_lock"]
                historical_path, digest, size = historical["path"], historical["sha256"], historical["bytes"]
                preserved = locate(target["sha256"], target["path"])
                if target["sha256"] != digest:
                    raise ValueError("Historical bridge changes a digest")
            else:
                historical_path, digest, size = resolution["original_path"], resolution["sha256"], resolution["bytes"]
                preserved = locate(digest, resolution["preserved_path"])
            historical_path = historical_path.replace("\\", "/")
            if preserved["bytes"] != size:
                raise ValueError("Explicit historical preservation byte count differs")
            bridges[(historical_path, digest)] = {
                "historical_path": historical_path, "historical_sha256": digest,
                "preserved_file": preserved, "declaration": file_spec(path, root),
                "resolution": "explicit_exact_historical_boundary_not_live_mutable_ancestry",
            }
    proof_path = work_dir / "session_group8_20261010_root_01/completion_inventory_snapshot.sealed.v1.jsonl"
    value = {"schema_version": 2, "contract_version": CONTRACT_VERSION,
             "gold_workflow_version": VERSION, "registry_version": REGISTRY_VERSION,
             "artifact": "gold_finalization_completion_registry", "corpus_contract": "ohienko_1988_production",
             "status": "complete_sha_locked_book_roster", "author_id": "/root/gold_author",
             "actual_role": "implementation_author_not_independent_reviewer",
             "checkpoint": file_spec(checkpoint_path, root), "inputs": inputs,
             "shared_issue_proof": file_spec(proof_path, root),
             "single_markdown_inventory": file_spec(report_dir / "oh88_strongs_issue_inventory.ru.md", root),
             "active_overlays": [file_spec(path, root) for path in active_overlay_paths],
             "assembly_implementation": [file_spec(root / ("scripts/bible_module/" + name), root) for name in
                 ("ukrainian_stage_7_gold.py", "ukrainian_stage_7_gold_v2.py",
                  "ukrainian_stage_7_gold_compare.py", "ukrainian_stage_7_completion_v2.py",
                  "ukrainian_stage_7_gold_legacy_corrections.py", "tests/test_ukrainian_stage_7_gold_v2.py")
                 if (root / ("scripts/bible_module/" + name)).is_file()],
             "historical_bridges": sorted(bridges.values(), key=lambda b: (b["historical_path"], b["historical_sha256"])),
             "books": dict(sorted(entries.items(), key=lambda item: strict.BOOK_NUMBER[item[0]]))}
    _check_registry_header(value, production=True)
    # Every located file is checked before the registry can become a trust root.
    checks = PhysicalLocks(root)
    for spec in _all_specs(value):
        checks.check(spec)
    emit_immutable(output_path, canonical_bytes(value))
    return {"status": value["status"], "registry": file_spec(output_path, root),
            "books": len(entries), "explicit_historical_bridges": len(bridges)}


def _chain_from_batch(book, batch, locate, report_dir, root):
    locks = {**batch.get("input_sha256", {}), **batch.get("output_sha256", {})}
    chain = {}
    aliases = {"pass1": ("pass_1",), "pass2": ("pass_2",), "comparison": ("comparison",),
               "adjudication": ("adjudication",), "qc": ("qc",), "blocking_qc": ("blocking_qc",),
               "consensus_correction": ("correction", "consensus_correction"), "final_qc": ("final_qc",)}
    for name, labels in aliases.items():
        digest = next((locks[book + "." + label] for label in labels if book + "." + label in locks), None)
        if digest:
            sidecar = next((locks[book + "." + label + "_manifest"] for label in labels
                            if book + "." + label + "_manifest" in locks), None)
            chain[name] = locate(digest, sidecar_digest=sidecar)
            if sidecar:
                chain[name + "_manifest"] = locate(sidecar)
    adjudication_sidecar = read_json(root / chain["adjudication_manifest"]["path"])
    for name, label in (("pass1", "review_pass_1"), ("pass2", "review_pass_2"), ("comparison", "comparison")):
        if name not in chain:
            chain[name] = locate(adjudication_sidecar["input_sha256"][label])
        if name + "_manifest" not in chain:
            digest = adjudication_sidecar["input_sha256"].get(label + "_manifest")
            if digest:
                chain[name + "_manifest"] = locate(digest)
            else:
                chain[name + "_manifest"] = file_spec(Path(str(root / chain[name]["path"]) + ".manifest.json"), root)
    template = root / f"scripts/bible_module/work/ukrainian_stage_7_20260801/gold_compact_review/pass_2/{book}/review_pass_2.shard_{strict.BOOK_NUMBER[book]:03}.compact.template.jsonl"
    template_manifest = template.parent / "gold_compact_review.manifest.json"
    chain["answer_free_template"] = file_spec(template, root)
    chain["answer_free_template_manifest"] = file_spec(template_manifest, root)
    if book in {"1Sam", "2Sam"}:
        qc_manifest = read_json(root / chain["qc_manifest"]["path"])
        for index, (path, digest) in enumerate(sorted(qc_manifest["input_sha256"].items())):
            chain[f"legacy_qc_input_{index}"] = locate(digest, "scripts/bible_module/work/ukrainian_stage_7_20260801/" + path)
    return chain


def _normalized_observations(path: Path, reviewer_id: str):
    values = []
    for row in rows(path):
        if row.get("record_type") in {"qc_full_grid_metadata", "metadata"}:
            continue
        value = dict(row)
        value.setdefault("reviewer_id", reviewer_id)
        # The legacy full-grid contract explicitly records this check in the
        # immutable examiner sidecar rather than repeating a per-row flag.
        if row.get("record_type") == "qc_full_grid_result":
            value.setdefault("reciprocal_accounting_checked", True)
        values.append(value)
    return values


def validate_legacy_1kgs_qc(chain, final, adjudication_rows, first, second):
    """Exact adapter for the sealed 2026-09-05 bounded 1Kgs audit contract.

    This preserves its actual 503-label scope, not a claim of new full-grid
    examination, and does not alter the newer strict JSONL QC validator.
    """
    audit = read_json(chain["qc"])
    manifest = read_json(chain["qc_manifest"])
    if (audit.get("artifact") != "gold_review_adjudication_qc_audit"
            or manifest.get("artifact") != "gold_review_adjudication_qc_audit_manifest"
            or audit.get("audit_id") != "qc-1kgs-s011-20260905-independent-b"
            or manifest.get("audit_id") != audit["audit_id"]
            or audit.get("status") != "complete_qc_accepted"
            or manifest.get("status") != "complete_qc_accepted"
            or manifest.get("shard_accepted") is not True
            or audit.get("conclusion", {}).get("shard_accepted") is not True
            or manifest.get("verdicts") != {"accepted": 503, "error": 0, "uncertain": 0}
            or manifest.get("error_stable_ids") != []
            or manifest.get("critical_high_uncertain_stable_ids") != []):
        raise ValueError("Legacy 1Kgs audit status/identity/verdict differs")
    aliases = {"pass_1": "pass1", "pass_2": "pass2", "comparison": "comparison",
               "adjudication": "adjudication", "evidence_template": "answer_free_template"}
    for label, name in aliases.items():
        for suffix in ("", "_manifest"):
            if manifest["input_sha256"][label + suffix] != sha256_file(chain[name + suffix]):
                raise ValueError("Legacy 1Kgs exact QC input digest differs")
    if manifest["output_sha256"].get(chain["qc"].name) != sha256_file(chain["qc"]):
        raise ValueError("Legacy 1Kgs audit/manifest output digest differs")
    checked = set()
    for group in audit["audit_groups"]:
        ids = group.get("stable_ids", [])
        if (not ids or len(ids) != len(set(ids)) or not set(ids) <= final.keys()
                or group.get("verdict") != "accepted" or not group.get("rationale")
                or not {final[key]["target_ref"] for key in ids} <= set(group["target_refs"])):
            raise ValueError("Legacy 1Kgs audit group scope/verdict differs")
        checked.update(ids)
    # The historical mandatory set was high/critical adjudication rows;
    # agreed two-pass rows were sampled. Keep that scope explicit.
    mandatory_high = {_key(row) for row in adjudication_rows if row["severity"] in {"high", "critical"}}
    if len(checked) != 503 or len(mandatory_high) != 395 or not mandatory_high <= checked:
        raise ValueError("Legacy 1Kgs mandatory high/critical coverage differs")
    for selection, field in (("new", "new_semantics_stable_ids"), ("pass_1", "pass_1_semantics_stable_ids")):
        wanted = set()
        for row in adjudication_rows:
            key = _key(row)
            semantic = strict._alignment_for_key(row)
            origin = ("pass_1" if semantic == strict._alignment_for_key(first[key]) else
                      "pass_2" if semantic == strict._alignment_for_key(second[key]) else "new")
            if origin == selection:
                wanted.add(key)
        declared = set(audit["mandatory_sets"][field])
        # Two target rows were conservatively declared new in the old audit
        # although their link topology equals pass2. Preserve this larger
        # review scope; every actually new link must still be included.
        expected_extra = {"target:gold7:target:c5f431e90a8371e4e121f4d6a4645e57",
                          "target:gold7:target:fdeadd5651dc18c7b07a7109763ec67d"} if selection == "new" else set()
        if declared != wanted | expected_extra or not declared <= checked:
            raise ValueError("Legacy 1Kgs mandatory semantic coverage differs")
    sample = manifest["sample_selected_stable_ids"]
    if len(sample) != 60 or len(set(sample)) != 60 or not set(sample) <= checked:
        raise ValueError("Legacy 1Kgs stratified sample differs")
    for ref, expected_count in (("1Kgs.20.39", 46), ("1Kgs.22.22", 34)):
        locus = {_key(row) for row in adjudication_rows if row["target_ref"] == ref}
        if len(locus) != expected_count or not locus <= checked:
            raise ValueError("Legacy 1Kgs required full locus coverage differs")


def validate_legacy_samuel_qc(book, chain, final, adjudication_rows):
    """Read the two sealed path-keyed QC releases in their own contracts."""
    expected = {
        "1Sam": ("5783284e4639462b99aa31eeb10843d1d2d4757c72a1a7751826566d4472a1ad",
                 "9403d99314e04d292e278c959512660c1a4aedac91f0e4258721256b5bce7951", 319, 70),
        "2Sam": ("1502336dfd9c64cb41002bb9f651f1b25e95e0f4196bbbc9c2f14ebf28e1eea6",
                 "974fed3bd4671f3f8f87ad86ace6a3b97784e8931a53807e7f688d9e2d64bf6f", 306, 80),
    }[book]
    if (sha256_file(chain["qc"]), sha256_file(chain["qc_manifest"])) != expected[:2]:
        raise ValueError("Legacy Samuel QC differs from exact accepted release")
    observations = rows(chain["qc"])
    manifest = read_json(chain["qc_manifest"])
    metadata, observations = observations[0], observations[1:]
    if (metadata.get("overall_verdict") != "accepted" or manifest.get("overall_verdict") != "accepted"
            or metadata.get("audit_id") != manifest.get("audit_id")
            or manifest["counts"].get("errors") != 0 or manifest["counts"].get("uncertain") != 0):
        raise ValueError("Legacy Samuel QC verdict differs")
    checked = set()
    for row in observations:
        key = row.get("stable_key")
        if (key not in final or key in checked or row.get("verdict") != "accepted"
                or row.get("audit_id") != metadata["audit_id"]
                or row.get("target_ref") != final[key]["target_ref"] or not row.get("rationale")):
            raise ValueError("Legacy Samuel observation differs")
        if "adjudication_semantics" in row:
            observed = row["adjudication_semantics"]
            required = ({"decision_status", "original_token_id", "relation", "group_original_token_ids", "target_token_ids", "null_reason"}
                        if key.startswith("original:") else {"target_token_id", "target_status", "linked_original_token_ids"})
            if set(observed) != required or observed != {field: final[key].get(field) for field in required}:
                raise ValueError("Legacy Samuel observed semantics differ")
        checked.add(key)
    mandatory_high = {_key(row) for row in adjudication_rows if row["severity"] in {"high", "critical"}}
    if len(checked) != expected[2] or not mandatory_high <= checked:
        raise ValueError("Legacy Samuel mandatory coverage differs")
    sample = manifest["sample"].get("stable_keys", manifest["sample"].get("selection_order_stable_keys"))
    if len(sample) != expected[3] or len(set(sample)) != expected[3] or not set(sample) <= checked:
        raise ValueError("Legacy Samuel sample differs")
    physical_digests = {sha256_file(path) for name, path in chain.items() if name.startswith("legacy_qc_input_")}
    if set(manifest["input_sha256"].values()) != physical_digests:
        raise ValueError("Legacy Samuel input dependencies differ")


def validate_legacy_gen_qc(chain):
    """Adapt four absent summary counters in the exact original Gen sidecar.

    The original QC is copied byte-for-byte for the strict checker; no answer,
    verdict or evidence is generated. The temporary metadata projection adds
    only counters derived from its already recorded rows. Every other strict
    content/schema/independence check executes unchanged.
    """
    import tempfile
    if (sha256_file(chain["qc"]), sha256_file(chain["qc_manifest"])) != (
            "44d7ab93e80c00fd449a03d96e20ba5267c0218f8940be0efd6d50ecf7725b95",
            "f15febd45ef2ac7fccae4447d1a51f0a18b88e11304e2447c1e59bbd2369d9d7"):
        raise ValueError("Legacy Gen QC differs from exact accepted release")
    original = read_json(chain["qc_manifest"])
    fields = {"processed_count", "skipped_count", "error_count", "uncertain_count"}
    if fields & original.keys():
        raise ValueError("Legacy Gen summary-counter contract differs")
    observations = [r for r in rows(chain["qc"]) if r.get("record_type") == "qc_adjudication_result"]
    if len(observations) != 230 or any(r.get("verdict") != "accepted" for r in observations):
        raise ValueError("Legacy Gen recorded accepted scope differs")
    projected = {**original, "processed_count": len(observations), "skipped_count": 0,
                 "error_count": sum(r["verdict"] == "error" for r in observations),
                 "uncertain_count": sum(r["verdict"] == "uncertain" for r in observations)}
    with tempfile.TemporaryDirectory(prefix="oh88-gen-qc-counter-projection-") as directory:
        copied_qc = Path(directory) / chain["qc"].name
        copied_qc.write_bytes(chain["qc"].read_bytes())
        projected_sidecar = Path(str(copied_qc) + ".manifest.json")
        projected_sidecar.write_bytes(canonical_bytes(projected))
        result = validate_adjudication_qc(
            **{name + "_path": chain[name] for name in ("pass1", "pass2", "comparison", "adjudication")},
            answer_free_template_path=chain["answer_free_template"],
            answer_free_template_manifest_path=chain["answer_free_template_manifest"],
            qc_path=copied_qc, qc_manifest_sha256=sha256_file(projected_sidecar))
    return result


def _validate_packet_contract(registry, checks):
    """Bind denominator policy to the actual immutable pre-review corpus."""
    inputs = registry["inputs"]
    packet = read_json(checks.check(inputs["reviewer_packets_manifest"]))
    expected_corpus = {"ohienko_1988_production": "ohienko_1988_production",
                       "CC0_fixture": "cc0_fixture"}[registry["corpus_contract"]]
    if packet.get("corpus_contract") != expected_corpus:
        raise ValueError("Registry corpus contract differs from frozen reviewer packet")
    if (packet.get("artifact") != "gold_reviewer_packets"
            or packet.get("status") != "prepared_unanswered_blind_packets"
            or packet.get("schema_version") != SCHEMA_VERSION
            or packet.get("contract_version") != CONTRACT_VERSION
            or packet.get("gold_workflow_version") != strict.GOLD_WORKFLOW_VERSION):
        raise ValueError("Frozen reviewer packet manifest contract differs")
    source_inputs = packet.get("input_sha256")
    if not isinstance(source_inputs, Mapping) or any(
            name not in inputs or inputs[name].get("sha256") != digest
            for name, digest in source_inputs.items()):
        raise ValueError("Registry source input alias differs from frozen reviewer packet")
    if expected_corpus == "ohienko_1988_production":
        if (set(source_inputs) != strict.PRODUCTION_PACKET_INPUT_KEYS
                or source_inputs.get("stage6_text") != strict.EXPECTED_STAGE6_TEXT_SHA256
                or source_inputs.get("stage6_comments") != strict.EXPECTED_STAGE6_COMMENT_SHA256):
            raise ValueError("Production frozen source input contract differs")
    output_locks = packet.get("output_sha256", {})
    if inputs["frozen_packet"]["sha256"] != output_locks.get("review_pass_1.packet.jsonl"):
        raise ValueError("Frozen reviewer packet payload differs from its manifest")
    return packet


def validate_and_assemble(registry_path: Path, *, root: Path = ROOT):
    registry = read_json(registry_path)
    if registry_path.read_bytes() != canonical_bytes(registry):
        raise ValueError("Global registry must be canonical UTF-8 JSON/LF")
    production = registry.get("corpus_contract") == "ohienko_1988_production"
    strict_books, deferred_books = _check_registry_header(registry, production=production)
    checks = PhysicalLocks(root)
    for spec in _all_specs(registry):
        checks.check(spec)
    _validate_packet_contract(registry, checks)
    # Latest-version selection is part of freshness, not just hashed old bytes.
    if production:
        checkpoint_dir = checks.check(registry["checkpoint"]).parent
        actual = {file_spec(path, root)["path"] for path in _active_overlay_paths(checkpoint_dir)}
        expected = {spec["path"] for spec in registry["active_overlays"]}
        if actual != expected:
            raise ValueError("Latest source/policy/QC overlay roster is stale")
        checkpoint = read_json(checks.check(registry["checkpoint"]))
        if (sorted(checkpoint["strict_fully_accepted_books"]) != strict_books
                or sorted(checkpoint["completed_books"]) != sorted(registry["books"])):
            raise ValueError("Book completion roster differs from v28 checkpoint")
    issues = rows(checks.check(registry["shared_issue_proof"]))
    validate_registry_snapshot(checks.check(registry["single_markdown_inventory"]).read_text(encoding="utf-8"), issues)
    if len({issue["issue_id"] for issue in issues}) != len(issues):
        raise ValueError("Shared issue proof duplicates an issue ID")
    active_issues = []
    for issue in issues:
        if issue["status"] != "deferred_strong_unassigned":
            continue
        current = dict(issue)
        current["affected_stable_keys"] = issue.get("active_affected_stable_keys", issue["affected_stable_keys"])
        if current["affected_stable_keys"]:
            active_issues.append(current)
    grid, pass1, pass2, excluded = {}, {}, {}, {}
    adjudicated_keys, authors_by_book, provenance_by_book = set(), {}, {}
    book_counts = {}
    annotations = []
    for book, entry in registry["books"].items():
        chain = {name: checks.check(spec) for name, spec in entry["chain"].items()}
        try:
            if book in {"Dan", "Isa"} and entry["status"] == "strictly_accepted":
                from scripts.bible_module.ukrainian_stage_7_gold_legacy_corrections import validated_legacy_corrected_book
                values = validated_legacy_corrected_book(book, chain)
            else:
                values = validated_completion_grid(chain)
        except ValueError as error:
            raise ValueError(f"Book {book} frozen/correction chain: {error}") from error
        meta1, meta2, first, second, final, adjudicator = values
        if (not final or set(final) != set(first) or set(first) != set(second)
                or {r["target_ref"].split(".")[0] for r in final.values()} != {book}):
            raise ValueError("Book grid scope/accounting differs")
        strict._validate_final_grid(final, first)
        strict._validate_semantic_accounting(
            {k.removeprefix("original:"): v for k, v in final.items() if k.startswith("original:")},
            {k.removeprefix("target:"): v for k, v in final.items() if k.startswith("target:")})
        local_adjudicated = {_key(row) for row in rows(chain["adjudication"])
                             if row.get("record_type") != "adjudication_shard_metadata"}
        templates = {row["target_ref"]: row for row in rows(chain["answer_free_template"])}
        target_spans = {item["target_token_id"]: {
            **{field: item[field] for field in ("start_scalar", "end_scalar", "start_byte", "end_byte")},
            "surface_sha256": sha256(item["surface"].encode("utf-8")).hexdigest()}
            for template in templates.values() for item in template["target_index"]}
        first = {key: ({**row, "target_span": target_spans[row["target_token_id"]]}
                       if key.startswith("target:") else row) for key, row in first.items()}
        authors = {meta1["reviewer_id"], meta2["reviewer_id"], adjudicator}
        authors.update(r["reviewer_id"] for r in (*first.values(), *second.values()))
        if "consensus_correction" in chain:
            authors.update(r["reviewer_id"] for r in rows(chain["consensus_correction"])
                           if r.get("record_type") != "consensus_correction_metadata")
        authors_by_book[book] = sorted(a for a in authors if a)
        correction_provenance = {}
        if "consensus_correction" in chain:
            qc_spec = entry["chain"].get("final_qc", entry.get("observations", {}))
            for row in rows(chain["consensus_correction"]):
                if row.get("record_type") == "consensus_correction_metadata":
                    continue
                key = _key(row)
                correction_provenance[key] = {
                    "book": book, "correction_reviewer_id": row["reviewer_id"],
                    "correction_sha256": entry["chain"]["consensus_correction"]["sha256"],
                    "correction_manifest_sha256": entry["chain"]["consensus_correction_manifest"]["sha256"],
                    "final_qc_sha256": qc_spec.get("sha256"),
                    "originally_agreed": key not in local_adjudicated,
                }
        acceptance = read_json(checks.check(entry["acceptance_manifest"]))
        if entry["status"] == "strictly_accepted":
            if (acceptance.get("status") != "partial_gold_adjudication_complete_qc_accepted"
                    or acceptance.get("error_count") != 0
                    or acceptance["books"][book].get("qc_errors") != 0
                    or acceptance["books"][book].get("qc_uncertain") != 0):
                raise ValueError("Strict book manifest/QC is not accepted")
            args = {name + "_path": chain[name] for name in ("pass1", "pass2", "comparison", "adjudication")}
            if "consensus_correction" in chain:
                if book not in {"Dan", "Isa"}:
                    validate_post_consensus_correction_qc(**args, blocking_qc_path=chain["blocking_qc"],
                        correction_path=chain["consensus_correction"], final_qc_path=chain["final_qc"])
            else:
                try:
                    if book == "Gen":
                        validate_legacy_gen_qc(chain)
                    elif book in {"1Sam", "2Sam"}:
                        validate_legacy_samuel_qc(book, chain, final, rows(chain["adjudication"])[1:])
                    elif chain["qc"].suffix == ".json":
                        if book != "1Kgs":
                            raise ValueError("Unsupported legacy QC contract")
                        validate_legacy_1kgs_qc(chain, final, rows(chain["adjudication"])[1:], first, second)
                    else:
                        validate_adjudication_qc(**args, answer_free_template_path=chain["answer_free_template"],
                            answer_free_template_manifest_path=chain["answer_free_template_manifest"],
                            qc_path=chain["qc"], qc_manifest_sha256=sha256_file(chain["qc_manifest"]))
                except ValueError as error:
                    raise ValueError(f"Strict {book}: {error}") from error
            if any(issue["book"] == book for issue in active_issues):
                raise ValueError("Strict book still has active deferrals")
            local_excluded = {}
        else:
            if (acceptance.get("status") != "completed_with_registered_deferrals"
                    or acceptance.get("book") != book or acceptance.get("strict_fully_accepted") is not False
                    or acceptance.get("strict_content_qc", {}).get("accepted") is not False):
                raise ValueError("Completion manifest falsely claims strict acceptance")
            if entry.get("legacy_zeph_contract"):
                provenance = read_json(checks.check(entry["provenance"]))
                reviewer = provenance["reviewer_id"]
                author_ids = authors
            else:
                config = read_json(checks.check(entry["completion_config"]))
                if config.get("book") != book:
                    raise ValueError("Completion config book differs")
                reviewer, author_ids = config["reviewer_id"], set(config["author_ids"]) | authors
                authors_by_book[book] = sorted(author_ids)
                attestation = read_json(checks.check(entry["role_attestation"]))
                if (attestation.get("reviewer_id") != reviewer
                        or attestation.get("actual_role") != "independent_content_and_completion_reviewer"
                        or attestation.get("no_authorship_of_reviewed_research_corrections_ledger_validator") is not True
                        or not attestation.get("independence_basis")):
                    raise ValueError("Independent completion reviewer attestation differs")
            observations = _normalized_observations(checks.check(entry["observations"]), reviewer)
            local_issues = [issue for issue in active_issues if issue["book"] == book]
            if entry.get("legacy_zeph_contract"):
                if len(local_issues) != 1 or local_issues[0]["target_ref"] != "Zeph.2.14":
                    raise ValueError("Legacy Zeph deferral locus differs")
                issue = dict(local_issues[0])
                digest_map = {}
                for decision in issue["individual_decisions"]:
                    locator = decision["observation_locator"]
                    if (locator["path"] != entry["observations"]["path"]
                            or locator["sha256"] != entry["observations"]["sha256"]
                            or decision["alignment_snapshot"] != final[decision["stable_key"]]):
                        raise ValueError("Legacy Zeph exact observation locator/snapshot differs")
                    digest_map[locator["path"]] = locator["sha256"]
                # The old issue stores input digests in its per-decision
                # locators. Project that existing proof into the v2 validator
                # interface without modifying the sole registry or snapshot.
                issue["input_digests"] = digest_map
                local_issues = [issue]
            # Use latest inventory scope with the original immutable verdicts.
            # This validates exact closed unresolved components including
            # accepted dependency exclusions and preserves error/uncertain.
            projection, counts = build_projection(final, observations, local_issues,
                                                  reviewer_id=reviewer, author_ids=author_ids)
            local_excluded = {row["stable_key"]: row["issue_id"] for row in projection
                              if row["assignment_status"] == "deferred_strong_unassigned"}
            sealed_projection = rows(checks.check(entry["effective_projection"]))
            if {row["stable_key"] for row in sealed_projection} != set(final) or len(sealed_projection) != len(final):
                raise ValueError("Sealed projection exact accounting differs")
            sealed_excluded = {row["stable_key"] for row in sealed_projection
                               if row.get("assignment_status") == "deferred_strong_unassigned"}
            if sealed_excluded != set(local_excluded):
                raise ValueError("Latest issue scope differs from sealed completion projection")
            for row in sealed_projection:
                key = row["stable_key"]
                if key in local_excluded:
                    if row.get("strong_assignment") is not None or row.get("assigned_strongs", []) != []:
                        raise ValueError("Deferred sealed node carries a Strong assignment")
                else:
                    effective = row.get("effective_decision", row.get("final_decision"))
                    if effective != final[key]:
                        raise ValueError("Sealed proven decision differs from current corrected grid")
            expected_counts = acceptance["counts"]
            for field in ("reviewed_decision_labels", "effective_proven_decision_labels", "deferred_decision_labels"):
                if counts[field] != expected_counts[field]:
                    raise ValueError("Live completion counts differ from sealed book manifest")
        if set(grid) & set(final):
            raise ValueError("Books duplicate a stable decision")
        grid.update(final)
        pass1.update(first)
        pass2.update(second)
        excluded.update(local_excluded)
        adjudicated_keys.update(local_adjudicated)
        local_annotations = make_annotations(final, first, second, local_excluded,
                                             adjudicator=adjudicator, adjudicated_keys=local_adjudicated,
                                             correction_provenance=correction_provenance)
        for row in local_annotations:
            row["book_completion_manifest_sha256"] = entry["acceptance_manifest"]["sha256"]
        annotations.extend(local_annotations)
        book_counts[book] = {"full_labels": len(final), "eligible_labels": len(final) - len(local_excluded),
                             "deferred_labels": len(local_excluded), "status": entry["status"]}
        provenance_by_book[book] = {"adjudicator": adjudicator, "pass1_reviewer": meta1["reviewer_id"],
                                   "pass2_reviewer": meta2["reviewer_id"],
                                   "completion_reviewer": reviewer if entry["status"] == "completed_with_registered_deferrals" else None,
                                   "historical_qc_scope": ("bounded_503_labels_395_adjudicated_high_critical" if book == "1Kgs" else
                                      "bounded_319_labels" if book == "1Sam" else "bounded_306_labels" if book == "2Sam" else
                                      "sealed_book_contract"),
                                   "correction_sha256": entry["chain"].get("consensus_correction", {}).get("sha256")}
    # Exact-once original/target requests are tied to the pre-review packet,
    # never inferred from the now completed books themselves.
    packet_path = checks.check(registry["inputs"]["frozen_packet"])
    packet_rows = [row for row in rows(packet_path) if row.get("record_type") != "review_packet_metadata"]
    requests = strict._packet_requests(packet_rows)
    expected_keys = {"original:" + key for key in requests["originals"]} | {"target:" + key for key in requests["targets"]}
    if set(grid) != expected_keys:
        raise ValueError("Global original/target packet accounting differs")
    for key, value in grid.items():
        request = requests["originals" if key.startswith("original:") else "targets"][key.split(":", 1)[1]]
        field = "original_token_id" if key.startswith("original:") else "target_token_id"
        if value[field] != request["token_id"] or value["target_ref"] != request["target_ref"]:
            raise ValueError("Original/target identity or verse differs from frozen packet")
    mask = build_eligibility(grid, excluded)
    panel = rows(checks.check(registry["inputs"]["gold_selection_panel"])) if production else None
    counts = coverage(mask, grid, panel)
    if production:
        counts["source_frequency_strata"] = add_source_frequency_proof(
            mask, annotations,
            strict._read_jsonl(checks.check(registry["inputs"]["original_token_universe"])),
            strict._read_jsonl(checks.check(registry["inputs"]["gold_selected_original_layer"])))
    minimum_verses, minimum_decisions = (2000, 25000) if production else (1, 1)
    if counts["proven_verses"] < minimum_verses or counts["eligible_original_decisions"] < minimum_decisions:
        raise ValueError("Proven gold is below original-only verse/decision minima")
    if production:
        eligible_phenomena = {p for key, row in grid.items() if key not in excluded for p in row.get("phenomena", [])}
        for band, phenomenon in (("rare_1_to_5", "rare_lemma"), ("frequent_1000_plus", "frequent_lemma")):
            if counts["source_frequency_strata"]["by_band"].get(band, {}).get("eligible_original_decisions", 0) > 0:
                eligible_phenomena.add(phenomenon)
        eligible_relations = {row.get("relation") for key, row in grid.items() if key not in excluded}
        eligible_relations.update("translation_addition" for key, row in grid.items()
                                  if key not in excluded and row.get("target_status") == "translation_addition")
        if strict.REQUIRED_PHENOMENA - eligible_phenomena or strict.REQUIRED_RELATIONS - eligible_relations:
            raise ValueError("Eligible gold lacks required strata: " + stable_json({
                "phenomena": sorted(strict.REQUIRED_PHENOMENA - eligible_phenomena),
                "relations": sorted(strict.REQUIRED_RELATIONS - eligible_relations)}))
    counts.update({"completed_books": len(registry["books"]), "strictly_accepted_books": len(strict_books),
                   "completed_with_deferrals_books": len(deferred_books), "book_completion": book_counts})
    return {"annotations": annotations, "eligibility": mask, "counts": counts,
            "physical_dependencies": sorted(checks.checked.values(), key=lambda s: s["path"]),
            "input_sha256": {name: spec["sha256"] for name, spec in registry["inputs"].items()},
            "review_provenance": provenance_by_book, "actual_authors": authors_by_book}


def finalize_gold_v2(registry_path: Path, report_dir: Path, work_dir: Path, *, root: Path = ROOT):
    assembled = validate_and_assemble(registry_path, root=root)
    payload_paths = {"annotations": work_dir / ANNOTATIONS_FILENAME,
                     "eligibility": work_dir / ELIGIBILITY_FILENAME}
    for name, path in payload_paths.items():
        emit_immutable(path, _jsonl_bytes(assembled[name]))
    output_specs = {name: file_spec(path, root) for name, path in payload_paths.items()}
    inputs = {**assembled["input_sha256"], "global_completion_correction_registry": sha256_file(registry_path)}
    manifest = _final_manifest(assembled, inputs, {path.name: output_specs[name]["sha256"] for name, path in payload_paths.items()})
    manifest_path = report_dir / MANIFEST_FILENAME
    emit_immutable(manifest_path, canonical_bytes(manifest))
    specs = {**output_specs, "manifest": file_spec(manifest_path, root), "registry": file_spec(registry_path, root)}
    lock = {"schema_version": 2, "contract_version": CONTRACT_VERSION, "gold_workflow_version": VERSION,
            "artifact": "deferral_aware_global_gold_lock", "status": manifest["status"],
            **specs, **{name + "_path": spec["path"] for name, spec in specs.items()},
            "input_sha256": inputs, "output_sha256": manifest["output_sha256"],
            "counts": assembled["counts"], "physical_dependencies": assembled["physical_dependencies"]}
    emit_immutable(report_dir / LOCK_FILENAME, canonical_bytes(lock))
    return {"status": lock["status"], "counts": lock["counts"], "outputs": specs}


def _final_manifest(assembled, inputs, outputs):
    return {"schema_version": 2, "contract_version": CONTRACT_VERSION, "gold_workflow_version": VERSION,
                "artifact": "deferral_aware_global_gold", "status": "finalized_deferral_aware_reviewed_gold",
                "counts": assembled["counts"], "input_sha256": inputs,
                "output_sha256": outputs,
                "review_provenance": assembled["review_provenance"],
                "actual_authors": assembled["actual_authors"],
                "assembly_author": "/root/gold_author", "assembly_is_independent_review": False,
                "assembly_implementation_authors": ["/root", "/root/gold_author"],
                "production_strong_links": 0, "training_or_production_export_authorized": False,
                "policy": "registered deferrals complete books; unproved labels remain present and ineligible"}


def validated_finalized_gold_lock_v2(report_dir: Path, *, root: Path = ROOT,
                                     revalidate_inputs: bool = True):
    """Validate payloads AND every live source/overlay dependency.

    revalidate_inputs is retained for callers' explicitness; disabling it is
    rejected because frozen output hashes cannot prove freshness of overlays.
    """
    if not revalidate_inputs:
        raise ValueError("Live dependency validation cannot be disabled")
    path = report_dir / LOCK_FILENAME
    if not path.exists():
        return None
    lock = read_json(path)
    if path.read_bytes() != canonical_bytes(lock):
        raise ValueError("Final lock is not canonical")
    if (lock.get("gold_workflow_version") != VERSION or lock.get("status") != "finalized_deferral_aware_reviewed_gold"
            or lock.get("schema_version") != 2 or lock.get("contract_version") != CONTRACT_VERSION
            or lock.get("artifact") != "deferral_aware_global_gold_lock"):
        raise ValueError("Deferral-aware finalized lock contract differs")
    checks = PhysicalLocks(root)
    for spec in lock.get("physical_dependencies", []):
        checks.check(spec)
    for label in ("annotations", "eligibility", "manifest", "registry"):
        checked = checks.check(lock[label])
        if lock.get(label + "_path") != lock[label]["path"]:
            raise ValueError("Finalized file path alias differs")
        if label == "manifest":
            manifest = read_json(checked)
            if (manifest.get("counts") != lock.get("counts") or manifest.get("input_sha256") != lock.get("input_sha256")
                    or manifest.get("schema_version") != 2 or manifest.get("contract_version") != CONTRACT_VERSION
                    or manifest.get("gold_workflow_version") != VERSION
                    or manifest.get("artifact") != "deferral_aware_global_gold"
                    or manifest.get("status") != lock["status"]):
                raise ValueError("Final lock/manifest counts or inputs differ")
    registry = read_json(checks.check(lock["registry"]))
    _check_registry_header(registry, production=registry.get("corpus_contract") == "ohienko_1988_production")
    expected = {s["path"]: dict(s) for s in _all_specs(registry)}
    actual = {s["path"]: dict(s) for s in lock["physical_dependencies"]}
    if expected != actual or len(actual) != len(lock["physical_dependencies"]):
        raise ValueError("Final dependency roster differs from complete registry")
    if lock["output_sha256"] != {lock[n]["path"].split("/")[-1]: lock[n]["sha256"] for n in ("annotations", "eligibility")}:
        raise ValueError("Finalized output aliases differ")
    rebuilt = validate_and_assemble(checks.check(lock["registry"]), root=root)
    for name in ("annotations", "eligibility"):
        if checks.check(lock[name]).read_bytes() != _jsonl_bytes(rebuilt[name]):
            raise ValueError("Finalized gold/mask differs from independently reconstructed completed evidence")
    expected_inputs = {**rebuilt["input_sha256"], "global_completion_correction_registry": lock["registry"]["sha256"]}
    if rebuilt["counts"] != lock["counts"] or expected_inputs != lock["input_sha256"]:
        raise ValueError("Reconstructed final counts/inputs differ")
    if manifest != _final_manifest(rebuilt, expected_inputs, lock["output_sha256"]):
        raise ValueError("Finalized manifest differs from complete deterministic reconstruction")
    return lock


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-registry")
    build.add_argument("--report-dir", type=Path, default=strict.DEFAULT_REPORT)
    build.add_argument("--work-dir", type=Path, default=strict.DEFAULT_WORK)
    build.add_argument("--output", type=Path, required=True)
    final = sub.add_parser("finalize")
    final.add_argument("--registry", type=Path, required=True)
    final.add_argument("--report-dir", type=Path, default=strict.DEFAULT_REPORT)
    final.add_argument("--work-dir", type=Path, default=strict.DEFAULT_WORK)
    check = sub.add_parser("check-final")
    check.add_argument("--report-dir", type=Path, default=strict.DEFAULT_REPORT)
    args = parser.parse_args(argv)
    if args.command == "check-final":
        result = validated_finalized_gold_lock_v2(args.report_dir)
        if result is None:
            raise ValueError("No deferral-aware finalized gold lock")
        result = {"status": result["status"], "counts": result["counts"]}
    elif args.command == "build-registry":
        result = build_finalization_registry(args.report_dir, args.work_dir, args.output)
    else:
        result = finalize_gold_v2(args.registry, args.report_dir, args.work_dir)
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

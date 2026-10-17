"""Post-freeze exact hyperedge evaluation with full eligible denominators."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from . import VERSION
from .core import GUARDS, fold, identity, load_mask, load_nodes, masked, physical, validate_graph
from .io import canonical, check_freeze, digest, read, rows, sha, spec, verify, write


def source_frequency(path):
    result = Counter()
    seen = set()
    for row in rows(path):
        token = row["original_token_id"]
        if token in seen:
            raise ValueError("Duplicate source universe node")
        seen.add(token)
        status = row.get("reading_status", "")
        if status.startswith("primary_") and "unresolved" not in status:
            result.update(set(row.get("strong_classic", [])))
    return result


def bands(tokens, originals, frequencies):
    values = {frequencies.get(s, 0) for t in tokens for s in originals[t].get("strong_classic", [])}
    result = []
    if any(0 < n <= 5 for n in values):
        result.append("source_frequency:rare_1_to_5")
    if any(n >= 1000 for n in values):
        result.append("source_frequency:frequent_1000_plus")
    if any(5 < n < 1000 for n in values):
        result.append("source_frequency:mid")
    return result or ["source_frequency:unclassified"]


def load_gold(path, mask, originals, targets, folds, frequencies):
    gold, original_edges, target_edges = {}, {}, defaultdict(set)
    originals_rows, target_rows = {}, {}
    seen_edge_ids, seen_physical, seen_nodes = set(), set(), set()
    exclusions = Counter()
    # Structural validation precedes fold selection/masking; excluded labels are
    # never read for relation, taxonomy, source frequency or membership.
    for row in rows(path):
        kind, ref = row.get("record_type"), row.get("target_ref")
        f = fold(ref)
        if kind == "hyperedge":
            o, t = physical(row, originals, targets)
            eid = row.get("edge_id")
            endpoints = ref, o, t
            if not isinstance(eid, str) or eid in seen_edge_ids or endpoints in seen_physical:
                raise ValueError("Duplicate/missing gold hyperedge including excluded rows")
            seen_edge_ids.add(eid)
            seen_physical.add(endpoints)
            if masked(o, t, mask):
                if f in folds:
                    exclusions["hyperedges"] += 1
                continue
            if f not in folds:
                continue
            if any(("original", v) not in mask for v in o) or any(("target", v) not in mask for v in t):
                raise ValueError("Gold endpoint absent from mask")
            key = identity(row)
            if row.get("status") != "reviewed_accepted" or key in gold:
                raise ValueError("Gold hyperedge is not proven unique")
            for token in o:
                if token in original_edges:
                    raise ValueError("Duplicate original gold assignment")
                original_edges[token] = key
            for token in t:
                target_edges[token].add(key)
            gold[key] = {"edge_id": eid, "row": row, "strata": bands(o, originals, frequencies)}
        elif kind in {"original_decision", "target_accounting", "deferred_original_decision", "deferred_target_accounting"}:
            side = "original" if "original_decision" in kind else "target"
            token = row.get(side + "_token_id")
            nodes = originals if side == "original" else targets
            node = side, token
            if token not in nodes or nodes[token]["target_ref"] != ref or node in seen_nodes or node not in mask:
                raise ValueError("Dangling/cross-verse/duplicate gold node accounting")
            seen_nodes.add(node)
            if not mask[node]:
                if not kind.startswith("deferred_") or row.get("status") != "deferred_strong_unassigned":
                    raise ValueError("Deferred node has an accepted label")
                if f in folds:
                    exclusions[side + "_nodes"] += 1
                continue
            if f not in folds:
                continue
            if kind.startswith("deferred_") or row.get("status") != "reviewed_accepted":
                raise ValueError("Eligible node has no accepted accounting")
            (originals_rows if side == "original" else target_rows)[token] = row
        else:
            raise ValueError("Unknown finalized gold row type")
    expected_o = {t for (s, t), eligible in mask.items() if s == "original" and eligible and fold(originals[t]["target_ref"]) in folds}
    expected_t = {t for (s, t), eligible in mask.items() if s == "target" and eligible and fold(targets[t]["target_ref"]) in folds}
    if set(originals_rows) != expected_o or set(original_edges) != expected_o or set(target_rows) != expected_t or set(target_edges) != expected_t:
        raise ValueError("Incomplete eligible gold hyperedge/node accounting")
    for token, row in originals_rows.items():
        key = original_edges[token]
        reciprocal = {"target_ref": row["target_ref"], "relation": row["relation"],
                      "original_token_ids": row["group_original_token_ids"], "target_token_ids": row["target_token_ids"],
                      "null_reason": row.get("null_reason")}
        if identity(reciprocal) != key or row["edge_id"] != gold[key]["edge_id"]:
            raise ValueError("Original gold reciprocal edge mismatch")
    for token, row in target_rows.items():
        keys = target_edges[token]
        union = sorted({o for key in keys for o in key[2]})
        if sorted(row["linked_original_token_ids"]) != union:
            raise ValueError("Target reciprocal union mismatch")
        if union and any(not key[2] for key in keys):
            raise ValueError("Gold shared target also has incompatible NULL")
    # Taxonomy is accessed only for the selected eligible partition.
    for key, value in gold.items():
        involved = [originals_rows[t] for t in key[2]] + [target_rows[t] for t in key[3]]
        phenomena = sorted({p for row in involved for p in row.get("phenomena", [])})
        value["strata"] += ["reviewed:" + p for p in phenomena] or ["reviewed:unclassified"]
    return gold, dict(exclusions), {"original_decisions": len(expected_o), "target_accounting": len(expected_t), "hyperedges": len(gold)}


def semantic_tuple(row):
    return identity(row)


def metric(tp, fp, fn):
    return {"tp": tp, "fp": fp, "fn": fn, "predicted": tp + fp, "gold_support": tp + fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}


def classify(key, gold, original_to_gold, target_to_gold):
    if key in gold:
        return "exact_complete_hyperedge"
    overlaps = {original_to_gold[t] for t in key[2] if t in original_to_gold}
    overlaps.update(g for t in key[3] for g in target_to_gold.get(t, set()))
    if not overlaps:
        return "outside_eligible_gold_endpoints"
    if len(overlaps) > 1:
        return "cross_gold_group_endpoints"
    expected = next(iter(overlaps))
    if key[2:4] == expected[2:4]:
        return "wrong_relation_or_null_reason"
    return "incomplete_or_wrong_group_endpoints"


def evaluate(repo, freeze_path, requested, out, gate_path=None):
    frozen = check_freeze(freeze_path, repo)
    folds = set(requested)
    if not folds or not folds <= {0, 1, 2, 3, 4} or (4 in folds and folds != {4}) or (3 in folds and folds != {3}):
        raise ValueError("Development/validation/sealed partitions must be separate")
    predecessors = []
    if folds == {4}:
        if gate_path is None:
            raise ValueError("Independent code and raw-payload review gate required")
        gate = read(gate_path)
        if gate.get("approved") is not True or gate.get("freeze_sha256") != sha(freeze_path) or gate.get("reviewer") in {None, frozen["author"]} or gate.get("code_review_pass") is not True or gate.get("payload_review_pass") is not True:
            raise ValueError("Independent review gate does not bind this exact pipeline")
        predecessors = gate.get("predecessors", [])
        partitions = []
        for predecessor in predecessors:
            p = verify(predecessor, repo)
            value = read(p)
            if value.get("artifact") != "consensus76_exact_hyperedge_evaluation" or value.get("freeze") != spec(freeze_path, repo):
                raise ValueError("Evaluation predecessor uses another pipeline")
            verify(value["output"], repo)
            partitions.append(value["folds"])
        if sorted(partitions) != [[0, 1, 2], [3]]:
            raise ValueError("Sealed gate requires exact development and validation predecessors")
        claim = Path(freeze_path).with_name(Path(freeze_path).name + ".fold4.claim.json")
        with claim.open("x", encoding="utf-8") as handle:
            handle.write(canonical({"freeze_sha256": sha(freeze_path), "gate": spec(gate_path, repo), "output": str(out), "one_time_score_claim": True}) + "\n")
    out.mkdir(parents=True, exist_ok=False)
    inputs = read(repo / frozen["input_lock"]["path"])
    paths = {k: repo / v for k, v in inputs["paths"].items()}
    originals, targets, _ = load_nodes(paths["gold_originals"], paths["targets"])
    mask = load_mask(paths["mask"], originals, targets)
    frequency = source_frequency(paths["source_universe"])
    gold, excluded_gold, support = load_gold(paths["annotations"], mask, originals, targets, folds, frequency)
    by_ref = defaultdict(set)
    og, tg = {}, defaultdict(set)
    for key in gold:
        by_ref[key[0]].add(key)
        for t in key[2]:
            og[t] = key
        for t in key[3]:
            tg[t].add(key)
    scores = defaultdict(lambda: {"top1": Counter(), "nbest_union": Counter(), "candidate_union": Counter()})
    group_taxonomy = defaultdict(lambda: {mode: Counter() for mode in ("top1", "nbest_union", "candidate_union")})
    group_coverage = defaultdict(Counter)
    testament_by_ref = {n["target_ref"]: n.get("testament", "unknown") for n in targets.values()}
    for (side, token), eligible in mask.items():
        node = originals[token] if side == "original" else targets[token]
        ref = node["target_ref"]
        if fold(ref) not in folds:
            continue
        for group in ("all", "book:" + ref.split(".")[0], "fold:" + str(fold(ref)), "testament:" + testament_by_ref[ref]):
            group_coverage[group]["full_" + side + "_nodes"] += 1
            group_coverage[group][("eligible_" if eligible else "excluded_") + side + "_nodes"] += 1
    taxonomy = {mode: Counter() for mode in ("top1", "nbest_union", "candidate_union")}
    coverage = Counter()
    graph_path = next(repo / item["path"] for item in frozen["build"] if item["path"].endswith("graph.v1.jsonl"))
    with (out / "evaluation.v1.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows(graph_path):
            validate_graph(row)
            ref = row["target_ref"]
            if fold(ref) not in folds:
                coverage["outside_requested_fold_graph_verses"] += 1
                continue
            if ref not in by_ref:
                coverage["outside_gold_graph_verses"] += 1
                continue
            coverage["eligible_gold_graph_verses"] += 1
            expected = by_ref[ref]
            index = {e["edge_id"]: e for e in row["edges"]}
            selections = {"top1": set(row["nbest"][0]["edge_ids"]),
                          "nbest_union": {k for s in row["nbest"] for k in s["edge_ids"]},
                          "candidate_union": set(index)}
            for mode, chosen in selections.items():
                predicted = set()
                for eid in sorted(chosen):
                    edge = index[eid]
                    physical(edge, originals, targets)
                    if masked(edge["original_token_ids"], edge["target_token_ids"], mask):
                        coverage[mode + "_whole_edges_excluded"] += 1
                        for group in ("all", "book:" + ref.split(".")[0], "fold:" + str(fold(ref)), "testament:" + testament_by_ref[ref]):
                            group_coverage[group][mode + "_whole_edges_excluded"] += 1
                        continue
                    key = identity(edge)
                    predicted.add(key)
                    category = classify(key, gold, og, tg)
                    taxonomy[mode][category] += 1
                    handle.write(canonical({"target_ref": ref, "fold": fold(ref), "mode": mode, "edge_id": eid,
                                            "identity": key, "taxonomy": category, "exact": key in gold}) + "\n")
                groups = {"all", "book:" + ref.split(".")[0], "fold:" + str(fold(ref))}
                testament = next(iter(row["target_nodes"]), {}).get("testament", "unknown")
                groups.add("testament:" + testament)
                strata = {s for k in expected for s in gold[k]["strata"]}
                strata.update(s for k in predicted for s in bands(k[2], originals, frequency))
                for group in groups | strata:
                    if group in groups:
                        gset, pset = expected, predicted
                    else:
                        gset = {k for k in expected if group in gold[k]["strata"]}
                        if group.startswith("source_frequency:"):
                            pset = {k for k in predicted if group in bands(k[2], originals, frequency)}
                        else:
                            pset = {k for k in predicted if (k in gold and group in gold[k]["strata"]) or
                                    (k not in gold and any(group in gold[g]["strata"] for g in expected if set(k[2]) & set(g[2]) or set(k[3]) & set(g[3])))}
                    scores[group][mode].update({"tp": len(pset & gset), "fp": len(pset - gset), "fn": len(gset - pset)})
                    group_coverage[group][mode + "_eligible_gold_support"] += len(gset)
                    group_coverage[group][mode + "_eligible_prediction_support"] += len(pset)
                    group_coverage[group][mode + "_gold_supported_by_prediction"] += len(pset & gset)
                    for key in pset:
                        group_taxonomy[group][mode][classify(key, gold, og, tg)] += 1
    for group in ("source_frequency:rare_1_to_5", "source_frequency:frequent_1000_plus", "source_frequency:mid",
                  "source_frequency:unclassified", "reviewed:rare_lemma", "reviewed:frequent_lemma"):
        scores[group]
    check_freeze(freeze_path, repo)
    result = {"version": VERSION, "artifact": "consensus76_exact_hyperedge_evaluation", "folds": sorted(folds),
              "freeze": spec(freeze_path, repo), "support": support, "excluded_gold": excluded_gold,
              "coverage": dict(coverage), "taxonomy": {m: dict(c) for m, c in taxonomy.items()},
              "coverage_by_group": {g: dict(c) for g, c in sorted(group_coverage.items())},
              "taxonomy_by_group": {g: {m: dict(c) for m, c in value.items()} for g, value in sorted(group_taxonomy.items())},
              "excluded_reviewed_strata_policy": "not_read_for_deferred_nodes;exclusion_coverage_by_physical_book_testament_fold",
              "metrics": {g: {mode: metric(c["tp"], c["fp"], c["fn"]) for mode, c in modes.items()} for g, modes in sorted(scores.items())},
              "unit": "declared_exact_semantic_hyperedge", "recall_denominator": "all_eligible_gold_hyperedges_in_partition",
              "nbest_is_top1": False, "calibration_performed": False, "threshold_tuning_performed": False,
              "preserved_baseline_artifacts": frozen["preserved_baseline_artifacts"],
              "predecessors": predecessors, "review_gate": spec(gate_path, repo) if gate_path else None,
              "supersedes": None, "contract_relation": "additive_candidate_only_does_not_replace_stage7.4_gold_or_metrics",
              "output": spec(out / "evaluation.v1.jsonl", repo), **GUARDS}
    # Missing candidate graph verses must still count as false negatives.
    if result["metrics"]["all"]["top1"]["gold_support"] != len(gold):
        raise ValueError("Gold recall denominator incomplete")
    write(out / "evaluation.v1.manifest.json", result)
    return result

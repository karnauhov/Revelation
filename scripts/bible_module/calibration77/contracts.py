"""Physical-first readers; deferred semantic metadata is deliberately opaque."""
from __future__ import annotations

import math
from collections import Counter, defaultdict

from scripts.bible_module.consensus76.core import (
    GUARDS as PREDECESSOR_GUARDS, accounting, compatible, edge_key, fold, identity,
    load_mask, load_nodes, masked, physical,
)
from scripts.bible_module.consensus76.evaluation import bands, source_frequency

from .io import digest, rows

PHENOMENA = {"textual_variant", "merge_split", "reorder", "omission", "addition", "repetition", "named_entity",
             "particle", "compound", "multiple_strong", "rare_lemma", "frequent_lemma", "polysemy", "unclassified"}
GENRES = {"torah_prose_law", "historical_prose", "poetry_wisdom", "prophetic", "gospel_narrative",
          "acts_narrative", "epistle", "apocalyptic", "missing"}
RELATIONS = {"one_to_one", "one_to_many", "many_to_one", "many_to_many", "grouped_expression", "textual_alternative",
             "original_omitted", "translation_addition"}
EVIDENCE = {"parallel_translation", "lexical_description", "transliteration", "multilingual_contextual", "missing"}
ANOMALIES = {"mapping:1:1", "mapping:merge", "mapping:split", "mapping:other", "mapping:missing",
             "reading:primary", "reading:nonprimary_or_unresolved", "reading:missing", "textual_alternative",
             "explicit_conflict", "none"}


def safe_nodes(paths):
    originals, targets, by_ref = load_nodes(paths["gold_originals"], paths["targets"])
    mask = load_mask(paths["mask"], originals, targets)
    return originals, targets, by_ref, mask


def fixed_universe(originals, targets, reviewed=()):
    books = {n["target_ref"].split(".")[0] for n in list(originals.values()) + list(targets.values())}
    genres = GENRES | {str(n.get("genre") or "missing") for n in targets.values()}
    names = {"book:" + b for b in books} | {"testament:OT", "testament:NT", "testament:missing"}
    for prefix, values in (("genre:", genres), ("relation:", RELATIONS), ("reviewed:", PHENOMENA | set(reviewed)),
                           ("evidence:", EVIDENCE), ("anomaly:", ANOMALIES)):
        names.update(prefix + v for v in values)
    names.update("source_frequency:" + b for b in ("rare_1_to_5", "mid", "frequent_1000_plus", "unclassified"))
    return sorted(names)


def conflict(edge, originals):
    if edge["relation"] == "textual_alternative":
        return True
    for token in edge["original_token_ids"]:
        status = originals[token].get("reading_status", "")
        if not status.startswith("primary_") or "unresolved" in status:
            return True
    return any(p.get("conflicting_evidence") is True or p.get("conflict") is True for p in edge.get("provenance", []))


def evidence_strata(edge):
    found = {label.split(":", 1)[1] for group in edge.get("dependence_groups", [])
             for label in group.get("labels", []) if label.startswith("channel:")}
    if found - EVIDENCE:
        raise ValueError("Evidence channel outside preregistered universe")
    return ["evidence:" + v for v in sorted(found or {"missing"})]


def base_strata(edge, originals, targets, frequencies):
    os = [originals[t] for t in edge["original_token_ids"]]
    ts = [targets[t] for t in edge["target_token_ids"]]
    all_target_nodes = ts or [n for n in targets.values() if n["target_ref"] == edge["target_ref"]]
    # Targets are supplied verse-locally by the full graph reader to keep NULL
    # handling bounded; gold callers also provide a verse-local target mapping.
    genre = {str(n.get("genre") or "missing") for n in all_target_nodes} or {"missing"}
    testament = {str(n.get("testament") or "missing") for n in all_target_nodes} or {"missing"}
    anomalies = set()
    for node in os:
        op = node.get("mapping_operation")
        anomalies.add("mapping:" + (op if op in {"1:1", "merge", "split"} else "other" if op else "missing"))
        status = node.get("reading_status")
        anomalies.add("reading:" + ("primary" if status and status.startswith("primary_") and "unresolved" not in status else "nonprimary_or_unresolved" if status else "missing"))
    if edge["relation"] == "textual_alternative":
        anomalies.add("textual_alternative")
    if any(p.get("conflicting_evidence") is True or p.get("conflict") is True for p in edge.get("provenance", [])):
        anomalies.add("explicit_conflict")
    return sorted({"book:" + edge["target_ref"].split(".")[0], "relation:" + edge["relation"],
                   *("genre:" + v for v in genre), *("testament:" + v for v in testament),
                   *("anomaly:" + v for v in (anomalies or {"none"})),
                   *bands(edge["original_token_ids"], originals, frequencies)})


def load_labels(path, mask, originals, targets, selected_folds, frequencies, reviewed_universe=PHENOMENA):
    """Only selected, eligible semantic labels are accessed; all IDs checked."""
    gold, original_edges, target_edges = {}, {}, defaultdict(set)
    original_rows, target_rows = {}, {}
    ids_seen, physical_seen, nodes_seen = set(), set(), set()
    excluded = Counter()
    local_targets = defaultdict(dict)
    for token, node in targets.items():
        local_targets[node["target_ref"]][token] = node
    for row in rows(path):
        kind, ref = row.get("record_type"), row.get("target_ref")
        f = fold(ref)
        if kind == "hyperedge":
            o, t = physical(row, originals, targets)
            eid, endpoint_key = row.get("edge_id"), (ref, o, t)
            if not isinstance(eid, str) or not eid or eid in ids_seen or endpoint_key in physical_seen:
                raise ValueError("Duplicate/missing physical gold hyperedge before mask")
            ids_seen.add(eid)
            physical_seen.add(endpoint_key)
            if masked(o, t, mask):
                if f in selected_folds:
                    excluded["whole_hyperedges"] += 1
                continue
            if f not in selected_folds:
                continue
            if any(("original", v) not in mask for v in o) or any(("target", v) not in mask for v in t):
                raise ValueError("Gold endpoint absent from eligibility mask")
            key = identity(row)
            if key in gold or row.get("status") != "reviewed_accepted":
                raise ValueError("Unproven/duplicate eligible semantic gold edge")
            for token in o:
                if token in original_edges:
                    raise ValueError("Duplicate gold original assignment")
                original_edges[token] = key
            for token in t:
                target_edges[token].add(key)
            gold[key] = {"row": row, "edge_id": eid,
                         "strata": base_strata(row, originals, local_targets[ref], frequencies)}
        elif kind in {"original_decision", "target_accounting", "deferred_original_decision", "deferred_target_accounting"}:
            side = "original" if "original_decision" in kind else "target"
            token = row.get(side + "_token_id")
            nodes, node_key = (originals if side == "original" else targets), (side, token)
            if token not in nodes or nodes[token]["target_ref"] != ref or node_key in nodes_seen or node_key not in mask:
                raise ValueError("Dangling/cross-verse/duplicate gold accounting before mask")
            nodes_seen.add(node_key)
            if not mask[node_key]:
                if f in selected_folds:
                    excluded[side + "_nodes"] += 1
                continue
            if f not in selected_folds:
                continue
            if kind.startswith("deferred_") or row.get("status") != "reviewed_accepted":
                raise ValueError("Eligible gold node has no accepted accounting")
            (original_rows if side == "original" else target_rows)[token] = row
        else:
            raise ValueError("Unknown gold physical record kind")
    expected_o = {t for (s, t), eligible in mask.items() if s == "original" and eligible and fold(originals[t]["target_ref"]) in selected_folds}
    expected_t = {t for (s, t), eligible in mask.items() if s == "target" and eligible and fold(targets[t]["target_ref"]) in selected_folds}
    if set(original_rows) != expected_o or set(original_edges) != expected_o or set(target_rows) != expected_t or set(target_edges) != expected_t:
        raise ValueError("Incomplete eligible gold accounting")
    for token, row in original_rows.items():
        reciprocal = {"target_ref": row["target_ref"], "relation": row["relation"],
                      "original_token_ids": row["group_original_token_ids"], "target_token_ids": row["target_token_ids"],
                      "null_reason": row.get("null_reason")}
        if identity(reciprocal) != original_edges[token] or row["edge_id"] != gold[original_edges[token]]["edge_id"]:
            raise ValueError("Original reciprocal mismatch")
    for token, row in target_rows.items():
        linked = sorted({o for key in target_edges[token] for o in key[2]})
        if sorted(row["linked_original_token_ids"]) != linked or (linked and any(not k[2] for k in target_edges[token])):
            raise ValueError("Target reciprocal union mismatch")
    for key, value in gold.items():
        involved = [original_rows[t] for t in key[2]] + [target_rows[t] for t in key[3]]
        phenomena = {p for row in involved for p in row.get("phenomena", [])} or {"unclassified"}
        if phenomena - set(reviewed_universe):
            raise ValueError("Reviewed phenomenon outside fixed universe")
        value["strata"] += ["reviewed:" + p for p in sorted(phenomena)]
    return gold, dict(excluded)


def inspect_graph(row, originals, targets, mask):
    ref = row.get("target_ref")
    if row.get("version") != "consensus76-v1" or row.get("fold_id") != fold(ref):
        raise ValueError("Wrong frozen graph version/fold")
    for key, expected in PREDECESSOR_GUARDS.items():
        if type(row.get(key)) is not type(expected) or row[key] != expected:
            raise ValueError("Frozen graph candidate guard changed")
    os, ts = {}, {}
    for side, values, result, universe in (("original", row["original_nodes"], os, originals),
                                            ("target", row["target_nodes"], ts, targets)):
        for node in values:
            token = node.get("token_id")
            if token in result or token not in universe or node.get("target_ref") != ref or node != universe[token]:
                raise ValueError("Duplicate/cross-verse/stale graph node")
            result[token] = node
    index, semantics, excluded = {}, set(), []
    for edge in row["edges"]:
        o, t = physical(edge, os, ts)
        eid = edge.get("edge_id")
        if not isinstance(eid, str) or not eid or eid in index:
            raise ValueError("Duplicate/invalid graph edge ID before mask")
        index[eid] = edge
        blocked = masked(o, t, mask)
        if type(edge.get("excluded_whole_edge")) is not bool or edge["excluded_whole_edge"] != blocked:
            raise ValueError("Graph whole-edge mask differs")
        if blocked:
            excluded.append(eid)
            continue
        for guard, expected in PREDECESSOR_GUARDS.items():
            if type(edge.get(guard)) is not type(expected) or edge[guard] != expected:
                raise ValueError("Eligible frozen edge candidate guard changed")
        key = identity(edge)
        if key in semantics or eid != edge_key(edge):
            raise ValueError("Duplicate/stale eligible semantic graph edge")
        semantics.add(key)
        rank = edge.get("rank_score")
        if isinstance(rank, bool) or not isinstance(rank, (int, float)) or not math.isfinite(rank):
            raise ValueError("Eligible graph rank invalid")
    if not row["nbest"]:
        raise ValueError("Missing frozen top1 assignment")
    chosen = row["nbest"][0]["edge_ids"]
    if len(chosen) != len(set(chosen)) or any(eid not in index or eid in excluded for eid in chosen):
        raise ValueError("Duplicate/unknown/deferred top1 edge")
    for i, eid in enumerate(chosen):
        if any(not compatible(index[eid], index[other]) for other in chosen[i + 1:]):
            raise ValueError("Top1 incompatible edge set")
    if row["accounting"] != accounting(list(os), list(ts), row["edges"], chosen):
        raise ValueError("Graph accounting is not complete and reciprocal")
    return os, ts, index, chosen, sorted(excluded)

"""Intact hyperedge comparison; no decisions or source inference."""
from __future__ import annotations

from scripts.bible_module.consensus76.core import compatible, fold, identity, physical
from scripts.bible_module.consensus76.io import digest

GUARDS = {"A_auto": 0, "candidate_only": True, "resolver_eligible": False,
          "auto_acceptance": False, "automatic_promotions": 0, "production_acceptance": 0}


def endpoint_delta(prediction, expected):
    """One complete comparison, never a union of alternative gold groups."""
    result = {"expected_edge_id": expected["edge_id"]}
    for side in ("original", "target"):
        actual, wanted = set(prediction[side + "_token_ids"]), set(expected[side + "_token_ids"])
        result["missing_" + side] = sorted(wanted - actual)
        result["extra_" + side] = sorted(actual - wanted)
    result["relation_differs"] = prediction["relation"] != expected["relation"]
    result["null_reason_differs"] = prediction.get("null_reason") != expected.get("null_reason")
    return result


def compile_case(case, graph, gold, classification):
    ref = graph["target_ref"]
    if fold(ref) not in {0, 1, 2} or case["target_ref"] != ref or case["fold"] != fold(ref):
        raise ValueError("Only the existing development cohort is allowed")
    if case["source_graph_row_digest"] != digest(graph):
        raise ValueError("Stale graph row")
    originals = {n["token_id"]: n for n in graph["original_nodes"]}
    targets = {n["token_id"]: n for n in graph["target_nodes"]}
    index = {e["edge_id"]: e for e in graph["edges"] if not e["excluded_whole_edge"]}
    if case["prediction_edge_id"] not in graph["nbest"][0]["edge_ids"]:
        raise ValueError("Case no longer refers to frozen selected top1")
    prediction = index[case["prediction_edge_id"]]
    if digest(identity(prediction)) != digest(case["semantic_identity"]):
        raise ValueError("Stale semantic identity")
    physical(prediction, originals, targets)
    nearest = []
    for eid in case["nearest_gold_edge_ids"]:
        expected = gold[eid]
        physical(expected, originals, targets)
        if digest(expected) != case["gold_row_digests"][eid]:
            raise ValueError("Stale gold row")
        nearest.append(endpoint_delta(prediction, expected))
    if classification["edge_id"] != prediction["edge_id"] or classification["final_class"] not in {"B_review", "C_unresolved"}:
        raise ValueError("No new class policy or A_auto allowed")
    if classification["exact"] is not False or identity(classification) != identity(prediction):
        raise ValueError("Not the locked development error case")
    if classification["calibration_provenance"]["input_graph_row_sha256"] != digest(graph):
        raise ValueError("Stale classification provenance")
    conflicts, shared = [], []
    for eid, other in sorted(index.items()):
        if eid == prediction["edge_id"]:
            continue
        overlap = bool(set(prediction["original_token_ids"]) & set(other["original_token_ids"]) or
                       set(prediction["target_token_ids"]) & set(other["target_token_ids"]))
        if not compatible(prediction, other):
            conflicts.append(eid)
        elif overlap:
            shared.append(eid)
    return {**case, "final_class": classification["final_class"],
            "classification_provenance": classification["calibration_provenance"],
            "gold_comparisons": nearest, "conflicting_candidate_edge_ids": conflicts,
            "compatible_shared_candidate_edge_ids": shared, "review_note_status": "not_started", **GUARDS}

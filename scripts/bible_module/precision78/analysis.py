"""Frozen-frame support and descriptive development error signatures."""
from __future__ import annotations

from collections import Counter, defaultdict

from scripts.bible_module.calibration77.contracts import base_strata, evidence_strata, conflict
from scripts.bible_module.calibration77.model import lexical_keys
from scripts.bible_module.consensus76.core import compatible, fold, identity
from scripts.bible_module.consensus76.evaluation import source_frequency
from scripts.bible_module.consensus76.io import canonical, digest, read, sha, spec

from .io import ROOT, REPORT, SESSION, SUPPORT, rows, write
from .statistics import hypergeom_precision_lower, hypergeom_zero_error_requirement, iid_wilson_power, required_support


class Components:
    """Induced lexical/verse connectivity, without an independence assertion."""
    def __init__(self):
        self.parent, self.first = [], {}

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def add(self, keys):
        i = len(self.parent)
        self.parent.append(i)
        for key in keys:
            if key in self.first:
                a, b = self.find(i), self.find(self.first[key])
                self.parent[max(a, b)] = min(a, b)
            else:
                self.first[key] = i

    def count(self):
        return len({self.find(i) for i in range(len(self.parent))})


def mask_frame(path):
    mask, reviewed = {}, set()
    for row in rows(path):
        side = "original" if "original_token_id" in row else "target"
        key = side, row[side + "_token_id"]
        if key in mask or type(row["eligible"]) is not bool:
            raise ValueError("Duplicate/invalid eligibility")
        mask[key] = row["eligible"]
        reviewed.add(row["target_ref"])
    return mask, reviewed


def eligible(edge, mask):
    return all(mask.get((side, token), True) for side in ("original", "target") for token in edge[side + "_token_ids"])


def feasibility(paths):
    """No annotation file or old correctness metric is opened in this phase."""
    mask, reviewed = mask_frame(paths["mask"])
    frequencies = source_frequency(paths["source_universe"])
    universe = ["global", *read(SUPPORT)["strata_universe"]]
    if len(set(universe)) != 342:
        raise ValueError("Mandatory claim universe changed")
    data = {name: [] for name in universe if not name.startswith("reviewed:")}
    all_refs, reviewed_found = set(), set()
    edge_ids, deferred_count = set(), 0
    book_refs, book_fresh = defaultdict(set), defaultdict(set)
    frame_path = SESSION / "frame.v1.jsonl"
    with frame_path.open("x", encoding="utf8", newline="\n") as output:
        for graph in rows(paths["graph"]):
            ref = graph["target_ref"]
            if ref in all_refs or graph["fold_id"] != fold(ref):
                raise ValueError("Duplicate graph verse or wrong fold")
            all_refs.add(ref)
            book = ref.split(".")[0]
            book_refs[book].add(ref)
            if ref in reviewed:
                reviewed_found.add(ref)
            else:
                book_fresh[book].add(ref)
            os = {n["token_id"]: n for n in graph["original_nodes"]}
            ts = {n["token_id"]: n for n in graph["target_nodes"]}
            chosen = set(graph["nbest"][0]["edge_ids"])
            semantic_seen = set()
            for edge in graph["edges"]:
                eid = edge["edge_id"]
                if eid in edge_ids:
                    raise ValueError("Repeated graph edge ID")
                edge_ids.add(eid)
                for side, nodes in (("original", os), ("target", ts)):
                    ids = edge[side + "_token_ids"]
                    if len(ids) != len(set(ids)) or any(t not in nodes or nodes[t]["target_ref"] != ref for t in ids):
                        raise ValueError("Invalid physical edge endpoints")
                admitted = eligible(edge, mask)
                if edge["excluded_whole_edge"] != (not admitted):
                    raise ValueError("Frozen mask differs")
                if not admitted:
                    if eid in chosen:
                        raise ValueError("Deferred selected edge")
                    deferred_count += 1
                    continue
                key = identity(edge)
                if key in semantic_seen:
                    raise ValueError("Duplicate semantic edge")
                semantic_seen.add(key)
                names = {"global", *base_strata(edge, os, ts, frequencies), *evidence_strata(edge)}
                if names - data.keys():
                    raise ValueError("Unexpected stratum")
                keys = tuple(lexical_keys(edge, os, ts))
                record = (ref, eid in chosen, ref not in reviewed, keys)
                for name in names:
                    data[name].append(record)
                output.write(canonical({"edge_id": eid, "semantic_identity": key, "strata": sorted(names), "top1": eid in chosen, "fresh": ref not in reviewed, "lexical_keys": keys}) + "\n")
            if not chosen <= {e["edge_id"] for e in graph["edges"]}:
                raise ValueError("Unknown top1 edge")
            if len(all_refs) % 5000 == 0:
                print("feasibility verses", len(all_refs), flush=True)
    if len(all_refs) != 31102 or reviewed_found != reviewed or len(book_refs) != 66:
        raise ValueError("Incomplete graph/review frame")
    matrix = []
    for name in universe:
        if name.startswith("reviewed:"):
            matrix.append({"stratum": name, "membership": "unknown_requires_independent_phenomenon_annotation", "A_auto_actual": 0,
                           "A_top1_envelope_edges": None, "unique_candidate_edges": None, "top1_verses": None,
                           "top1_lexical_components": None, "fresh_top1_edges": None, "fresh_candidate_edges": None,
                           "fresh_top1_verses": None, "fresh_top1_lexical_components": None,
                           "fresh_candidate_upper_ceiling": sum(r[2] for r in data["global"]),
                           "design_zero_error_support_on_fresh_top1_envelope": None, "selector_status": "BLOCKED_UNKNOWN_MEMBERSHIP",
                           "wilson_zero_error_support": 539, "status": "BLOCKED_UNKNOWN_MEMBERSHIP"})
            continue
        records = data[name]
        top1 = [r for r in records if r[1]]
        fresh = [r for r in records if r[2]]
        fresh_top = [r for r in fresh if r[1]]
        counts = []
        for selected in (top1, fresh_top):
            c = Components()
            for r in selected:
                c.add(r[3])
            counts.append(c.count())
        status = "STRUCTURAL_NO_GO" if len(fresh) < 539 else "SUPPORT_CEILING_ONLY_NOT_CERTIFIED"
        matrix.append({"stratum": name, "membership": "label_free", "A_auto_actual": 0,
                       "A_top1_envelope_edges": len(top1), "unique_candidate_edges": len(records),
                       "top1_verses": len({r[0] for r in top1}), "top1_lexical_components": counts[0],
                       "fresh_top1_edges": len(fresh_top), "fresh_candidate_edges": len(fresh),
                       "fresh_top1_verses": len({r[0] for r in fresh_top}), "fresh_top1_lexical_components": counts[1],
                       "design_zero_error_support_on_fresh_top1_envelope": hypergeom_zero_error_requirement(len(fresh_top), .05/342),
                       "selector_status": "STRUCTURAL_NO_GO" if len(fresh_top) < 539 else "SUPPORT_CEILING_ONLY_NOT_CERTIFIED",
                       "fresh_candidate_upper_ceiling": len(fresh), "wilson_zero_error_support": 539, "status": status})
    books = {b: {"total_verses": len(v), "reviewed_verses": len(v & reviewed), "fresh_verses": len(book_fresh[b])} for b, v in sorted(book_refs.items())}
    blockers = [r["stratum"] for r in matrix if r["status"] == "STRUCTURAL_NO_GO"]
    if not blockers:
        raise ValueError("This stopped-study protocol requires an actual structural blocker")
    result = {"artifact": "precision78_feasibility", "status": "STRUCTURAL_NO_GO", "annotations_opened": False,
              "matrix": matrix, "books": books, "required_claims": 342, "unique_required_strata": 341,
              "population_basis": "upper_envelope_not_frozen_A_policy", "all_graph_verses": len(all_refs), "reviewed_verses": len(reviewed),
              "whole_deferred_candidate_edges_excluded": deferred_count, "frame": spec(frame_path, ROOT),
              "components_independent": False, "freshness": "upper_bound_excludes_all_v2_reviewed_refs;other_uncatalogued_prior_reviews_can_only_reduce_it",
              "structural_blockers": blockers,
              "proof": "fresh_candidate_union_is_superset_of_any_selector_or_saved_candidate_reranker;required_zero_fresh_books_cannot_acquire_539_unique_new_cases",
              "A_auto": 0, "training_runs": 0, "new_annotation_cases": 0}
    write(SESSION / "feasibility.v1.json", result)
    arithmetic = {"nominal_zero_errors": required_support(), "nominal_one_error": required_support(1),
                  "bonferroni342_zero_errors_illustrative": required_support(alpha=.05/342),
                  "iid_power_illustrations": [iid_wilson_power(n) for n in (539, 894, 1500, 2000, 2611, 3000)],
                  "finite_population_examples": [{"N": N, "n": n, "errors": 0, "lower95": hypergeom_precision_lower(N, n, 0)} for N, n in ((100, 100), (10000, 539), (10000, 3000))],
                  "not_a_certification_or_final_sample_budget": True}
    write(SESSION / "arithmetic.v1.json", arithmetic)


def difference(edge, gold_rows):
    """Nearest complete gold groups; ties kept, sides never projected as labels."""
    os, ts = set(edge["original_token_ids"]), set(edge["target_token_ids"])
    overlaps = [g for g in gold_rows if os.intersection(g["original_token_ids"]) or ts.intersection(g["target_token_ids"])]
    if not overlaps:
        return {"structural": ["wrong_endpoints"], "nearest_gold_edge_ids": [], "ties": 0}
    distance = lambda g: len(os.symmetric_difference(g["original_token_ids"])) + len(ts.symmetric_difference(g["target_token_ids"]))
    best = min(map(distance, overlaps))
    nearest = [g for g in overlaps if distance(g) == best]
    signatures = set()
    for g in nearest:
        go, gt = set(g["original_token_ids"]), set(g["target_token_ids"])
        if os == go and ts == gt:
            if (edge["relation"], edge.get("null_reason")) != (g["relation"], g.get("null_reason")):
                signatures.add("relation_null_semantics")
        else:
            missing = bool(go-os or gt-ts)
            extra = bool(os-go or ts-gt)
            if missing:
                signatures.add("incomplete_group")
            if extra:
                signatures.add("extra_participant")
            if missing and extra:
                signatures.add("wrong_endpoints")
    return {"structural": sorted(signatures), "nearest_gold_edge_ids": sorted(g["edge_id"] for g in nearest), "ties": len(nearest), "endpoint_symmetric_difference": best}


def taxonomy(paths):
    if read(SESSION / "feasibility.v1.json")["status"] != "STRUCTURAL_NO_GO":
        raise ValueError("Feasibility must precede development inspection")
    mask, reviewed = mask_frame(paths["mask"])
    gold = defaultdict(list)
    for row in rows(paths["annotations"]):
        if fold(row["target_ref"]) not in {0, 1, 2}:
            continue  # No validation/test semantic fields accessed.
        if row["record_type"] == "hyperedge" and eligible(row, mask):
            if row["status"] != "reviewed_accepted":
                raise ValueError("Unproven gold")
            identity(row)
            gold[row["target_ref"]].append(row)
    counters, hints, opportunities = Counter(), Counter(), Counter()
    detail_path = SESSION / "development_error_taxonomy.v1.jsonl"
    inspected = 0
    with detail_path.open("x", encoding="utf8", newline="\n") as out:
        for graph in rows(paths["graph"]):
            ref = graph["target_ref"]
            if fold(ref) not in {0, 1, 2} or ref not in reviewed:
                continue
            os = {n["token_id"]: n for n in graph["original_nodes"]}
            ts = {n["token_id"]: n for n in graph["target_nodes"]}
            index = {e["edge_id"]: e for e in graph["edges"] if eligible(e, mask)}
            expected = {identity(g): g for g in gold[ref]}
            selected = set(graph["nbest"][0]["edge_ids"])
            candidate_gold = {eid: e for eid, e in index.items() if identity(e) in expected}
            for eid in sorted(selected):
                edge = index[eid]
                # Restrict inspection to the full eligible reviewed universe.
                if any((s, t) not in mask for s in ("original", "target") for t in edge[s + "_token_ids"]):
                    raise ValueError("Selected reviewed edge has endpoint outside mask")
                if identity(edge) in expected:
                    continue
                inspected += 1
                result = difference(edge, gold[ref])
                flags = []
                for nodes, field in ((os, "strong_classic"), (ts, "comparison")):
                    values = [canonical(n.get(field)) for n in nodes.values() if n.get(field)]
                    if len(values) != len(set(values)):
                        flags.append("repetition")
                        break
                if edge.get("prior", {}).get("polysemous"):
                    flags.append("polysemy")
                if conflict(edge, os):
                    flags.append("textual_conflict")
                missing_morph = any(not os[t].get("morphology_raw") for t in edge["original_token_ids"])
                uncertain_morph = any(any("unresolved" in str(c.get("morphology", "")) for c in ts[t].get("lemma_pos_morphology_candidates", [])) for t in edge["target_token_ids"])
                if missing_morph or uncertain_morph:
                    flags.append("morphology_unresolved")
                alternatives = sorted(other for other, e in candidate_gold.items() if other not in selected and not compatible(edge, e))
                in_nbest = [d["rank"] for d in graph["nbest"][1:] if set(alternatives).intersection(d["edge_ids"])]
                if alternatives:
                    opportunities["false_edges_conflicting_with_available_gold_alternative"] += 1
                counters.update(result["structural"])
                hints.update(flags)
                out.write(canonical({"case_id": "p78:" + digest([ref, eid]), "target_ref": ref, "fold": graph["fold_id"],
                                     "prediction_edge_id": eid, "semantic_identity": identity(edge), **result,
                                     "evidence_hints_not_causal_labels": flags,
                                     "decomposition_selection": {"conflicting_correct_candidate_edge_ids": alternatives, "alternative_nbest_ranks": in_nbest, "joint_improvement_proved": False},
                                     "source_graph_row_digest": digest(graph), "gold_row_digests": {g["edge_id"]: digest(g) for g in gold[ref] if g["edge_id"] in result["nearest_gold_edge_ids"]}}) + "\n")
    # Historical outcome counts are quoted, never re-evaluated as new metrics.
    historical = read_report_counts()
    write(SESSION / "taxonomy.v1.json", {"artifact": "precision78_development_error_taxonomy", "folds": [0, 1, 2],
          "status": "structural_inspection_complete_not_manual_causal_annotation", "inspected_false_edges": inspected,
          "structural_multilabel_counts": dict(counters), "evidence_hint_counts": dict(hints), "selection_opportunities": dict(opportunities),
          "categories": ["wrong_endpoints", "incomplete_group", "extra_participant", "relation_null_semantics", "repetition", "morphology_polysemy", "textual_conflict", "decomposition_selection"],
          "no_retrieval_or_top1_evaluation_rerun": True, "historical76": historical,
          "selected_subclass_precision": None, "within_graph_selection_improvement": None, "generator_retrieval_coverage": "historical76_only",
          "actual_experiments": 0, "no_new_labels": True, "details": spec(detail_path, ROOT)})


def read_report_counts():
    path = REPORT / "consensus76.v1.ru.md"
    text = path.read_text(encoding="utf8")
    required = ["| development0–2 | candidate_union | 7401 | 9208 | 20061 |", "| development0–2 | top1 | 6479 | 5782 | 20983 |"]
    if not all(s in text for s in required):
        raise ValueError("Frozen historical report rows changed")
    return {"source": spec(path, ROOT), "candidate_union_correct": 7401, "top1_correct": 6479,
            "available_correct_difference_upper_bound": 922, "gold_absent_from_union": 20061,
            "eligible_gold_denominator": 27462, "candidate_retrieval_coverage": 7401/27462,
            "all_922_simultaneously_compatible": "not_proved"}

"""Evidence graph, intact-group OOF prior and bounded candidate-only search."""
from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path

from . import VERSION
from .io import PACKAGE, canonical, check_inputs, digest, read, rows, sha, spec, write

GUARDS = {"resolver_eligible": False, "calibrated_probability": None, "automatic_strong_promotions": 0,
          "candidate_only": True, "calibrated": False, "auto_acceptance": False}
RELATIONS = {"one_to_one", "one_to_many", "many_to_one", "many_to_many", "grouped_expression", "textual_alternative"}
ORIGINAL_NULL = {"not_overtly_translated", "grammatical_function", "textual_absence", "omitted_in_translation"}


def fold(ref):
    return int(hashlib.sha256(ref.encode("utf-8")).hexdigest()[:8], 16) % 5


def ids(value):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value) or len(value) != len(set(value)):
        raise ValueError("Missing/duplicate/invalid physical token IDs")
    return tuple(sorted(value))


def identity(row):
    o, t = ids(row["original_token_ids"]), ids(row["target_token_ids"])
    relation, null = row.get("relation"), row.get("null_reason")
    if relation == "original_omitted":
        if not o or t or not isinstance(null, str) or not null:
            raise ValueError("Unproved original NULL/cardinality")
    elif relation == "translation_addition":
        if o or not t or not isinstance(null, str) or not null:
            raise ValueError("Unproved target NULL/cardinality")
    else:
        if relation not in RELATIONS or not o or not t or null is not None:
            raise ValueError("Invalid non-null hyperedge")
        if relation == "one_to_one" and (len(o), len(t)) != (1, 1):
            raise ValueError("Invalid one-to-one cardinality")
        if relation == "one_to_many" and (len(o) != 1 or len(t) < 2):
            raise ValueError("Invalid one-to-many cardinality")
        if relation == "many_to_one" and (len(o) < 2 or len(t) != 1):
            raise ValueError("Invalid many-to-one cardinality")
        if relation == "many_to_many" and (len(o) < 2 or len(t) < 2):
            raise ValueError("Invalid many-to-many cardinality")
    return row["target_ref"], relation, o, t, null


def edge_key(row):
    return "c76edge:" + digest(identity(row))


def physical(row, originals, targets):
    """Always validate endpoints before masking or any gold-membership lookup."""
    ref = row.get("target_ref")
    o, t = ids(row.get("original_token_ids")), ids(row.get("target_token_ids"))
    if not isinstance(ref, str) or len(ref.split(".")) != 3:
        raise ValueError("Invalid verse reference")
    if any(v not in originals or originals[v]["target_ref"] != ref for v in o):
        raise ValueError("Dangling/cross-verse original endpoint")
    if any(v not in targets or targets[v]["target_ref"] != ref for v in t):
        raise ValueError("Dangling/cross-verse target endpoint")
    return o, t


def masked(o, t, mask):
    return any(mask.get(("original", v)) is False for v in o) or any(mask.get(("target", v)) is False for v in t)


def load_nodes(original_path, target_path):
    originals, targets = {}, {}
    by_ref = defaultdict(lambda: {"original": [], "target": []})
    for path, side, result in ((original_path, "original", originals), (target_path, "target", targets)):
        for row in rows(path):
            key = row.get("original_token_id") if side == "original" else row.get("target_token_id")
            key = key or row.get("token_id")
            if not isinstance(key, str) or key in result:
                raise ValueError("Missing/duplicate physical node identity")
            ref = row.get("target_ref")
            if not isinstance(ref, str):
                raise ValueError("Selected node lacks target mapping")
            if side == "original":
                keep = ("target_ref", "source_family", "source_id", "source_ref", "native_ref", "native_locator",
                        "mapping_operation", "order", "word_order", "component_index", "parent_token_id", "lemma_raw",
                        "lemma_source", "morphology", "morphology_raw", "strong_classic", "surface", "reading_status",
                        "selection_rule", "provenance", "selected_original_layer", "apparatus_provenance",
                        "source_locator", "source_commit", "source_sha256", "mapping_rule_id", "mapping_contract_version",
                        "projection_status", "base_ref", "component_group", "component_order", "component_kind",
                        "surface_raw", "surface_normalized", "raw_line_sha256")
            else:
                keep = ("target_ref", "surface", "comparison", "token_index", "verse_token_index", "start_scalar", "end_scalar",
                        "start_byte", "end_byte", "context", "context_window", "lemma_pos_morphology_candidates",
                        "testament", "book", "genre", "verse_sha256", "context_sha256", "order", "left_context", "right_context", "plain_text_sha256")
            result[key] = {k: row[k] for k in keep if k in row}
            result[key]["token_id"] = key
            # Lock exact raw node even when the readable feature projection is compact.
            result[key]["input_record_sha256"] = digest(row)
            by_ref[ref][side].append(key)
    for value in by_ref.values():
        for side in value:
            value[side].sort()
    return originals, targets, dict(by_ref)


def load_mask(path, originals, targets):
    result, keys = {}, set()
    for row in rows(path):
        side = "original" if "original_token_id" in row else "target"
        token = row.get(side + "_token_id")
        nodes = originals if side == "original" else targets
        if token not in nodes or nodes[token]["target_ref"] != row.get("target_ref"):
            raise ValueError("Dangling/cross-verse eligibility node")
        key = (side, token)
        stable = row.get("stable_key")
        if key in result or stable in keys or not isinstance(stable, str) or not isinstance(row.get("eligible"), bool):
            raise ValueError("Duplicate/invalid eligibility node")
        result[key] = row["eligible"]
        keys.add(stable)
    return result


def ordered_nodes(tokens, nodes):
    return sorted((nodes[v] for v in tokens), key=lambda v: (v.get("order", v.get("verse_token_index", v.get("token_index", 0))), v["token_id"]))


def original_signature(tokens, originals):
    # The whole ordered signature remains intact, including unknown lemma/morphology.
    return [{"source_family": n.get("source_family"), "lemma_raw": n.get("lemma_raw"),
             "lemma_source": n.get("lemma_source"), "strong_classic": n.get("strong_classic", []),
             "morphology": n.get("morphology", n.get("morphology_raw")),
             "component_kind": n.get("component_kind"), "component_group": n.get("component_group"),
             "component_order": n.get("component_order")} for n in ordered_nodes(tokens, originals)]


def target_signature(tokens, targets):
    return [{"surface": n.get("surface"), "comparison": n.get("comparison"),
             "lemma_pos_morphology_candidates": n.get("lemma_pos_morphology_candidates", []),
             "context": n.get("context", n.get("context_window", {"left": n.get("left_context"), "right": n.get("right_context")}))}
            for n in ordered_nodes(tokens, targets)]


def prior_keys(row, originals, targets):
    src = original_signature(row["original_token_ids"], originals)
    dst = {"target_group": target_signature(row["target_token_ids"], targets),
           "relation": row["relation"], "null_reason": row.get("null_reason")}
    return digest(src), digest(dst), src, dst


def target_overlap_components(declarations):
    """Partition declared edges by physical target co-use; empty targets stay separate."""
    components = []
    for row in sorted(declarations, key=lambda r: r["edge_id"]):
        component = {"targets": set(row["target_token_ids"]), "edges": [row]}
        for other in list(components):
            if component["targets"] & other["targets"]:
                components.remove(other)
                component["targets"].update(other["targets"])
                component["edges"].extend(other["edges"])
        components.append(component)
    return sorted((sorted(c["edges"], key=lambda r: r["edge_id"]) for c in components),
                  key=lambda c: tuple(r["edge_id"] for r in c))


def joint_prior_keys(declarations, originals, targets):
    """ID-independent whole-bundle outcome, retaining every declared constituent."""
    if len(declarations) < 2 or len({r["target_ref"] for r in declarations}) != 1:
        raise ValueError("Joint prior query requires one verse and multiple declarations")
    seen_originals, seen_edges = set(), set()
    for row in declarations:
        o, _ = physical(row, originals, targets)
        identity(row)
        edge = row.get("edge_id")
        if not isinstance(edge, str) or edge in seen_edges:
            raise ValueError("Joint prior query has missing/duplicate declaration ID")
        if seen_originals.intersection(o):
            raise ValueError("Joint prior query reuses an original across declarations")
        seen_originals.update(o)
        seen_edges.add(edge)
    if len(target_overlap_components(declarations)) != 1:
        raise ValueError("Joint prior query must be one target-overlap component")
    union = [n["token_id"] for n in ordered_nodes(
        {v for r in declarations for v in r["target_token_ids"]}, targets)]
    positions = {token: i for i, token in enumerate(union)}
    # A list preserves multiplicity when two distinct originals have identical
    # lexical signatures. Each subspan refers to positions in the ordered union.
    src = {"declared_constituents": sorted([
        {"original_group": original_signature(r["original_token_ids"], originals),
         "target_union_positions": sorted(positions[v] for v in r["target_token_ids"]),
         "relation": r["relation"], "null_reason": r.get("null_reason")}
        for r in declarations], key=canonical)}
    dst = {"target_union": target_signature(union, targets)}
    return digest(src), digest(dst), src, dst


def build_prior(annotation_path, mask, originals, targets):
    """A single streaming pass; fold3/4 label metadata is never inspected."""
    counts, reverse = defaultdict(Counter), defaultdict(Counter)
    signatures, outcomes = {}, {}
    joint_counts = defaultdict(Counter)
    joint_signatures, joint_targets, joint_observations = {}, {}, []
    development = defaultdict(list)
    seen_ids, seen_semantics, seen_observations = set(), set(), set()
    excluded = 0
    for row in rows(annotation_path):
        if row.get("record_type") != "hyperedge":
            continue
        o, t = physical(row, originals, targets)
        eid = row.get("edge_id")
        if not isinstance(eid, str) or eid in seen_ids:
            raise ValueError("Duplicate/missing gold edge ID including excluded edges")
        seen_ids.add(eid)
        # Raw endpoints, not relation/phenomena/Strong labels, suffice to detect duplicate physical edges.
        physical_semantic = (row["target_ref"], o, t)
        if physical_semantic in seen_semantics:
            raise ValueError("Duplicate semantic gold edge including excluded edges")
        seen_semantics.add(physical_semantic)
        if masked(o, t, mask):
            excluded += 1
            continue
        f = fold(row["target_ref"])
        if f not in (0, 1, 2):
            continue
        if row.get("status") != "reviewed_accepted" or any(("original", v) not in mask for v in o) or any(("target", v) not in mask for v in t):
            raise ValueError("Prior label lacks proven eligible gold acceptance")
        identity(row)
        development[row["target_ref"]].append(row)
    for ref, declarations in sorted(development.items()):
        f = fold(ref)
        for component in target_overlap_components(declarations):
            joint = len(component) > 1
            source, target, src, dst = (joint_prior_keys(component, originals, targets) if joint else
                                      prior_keys(component[0], originals, targets))
            observation = (ref, joint, source, target)
            counted = observation not in seen_observations
            seen_observations.add(observation)
            if joint:
                joint_signatures[source], joint_targets[target] = src, dst
                joint_observations.append({"target_ref": ref, "fold": f, "counted": counted,
                    "outcome_signature_sha256": source, "target_signature_sha256": target,
                    "ordered_target_union_ids": [n["token_id"] for n in ordered_nodes(
                        {v for r in component for v in r["target_token_ids"]}, targets)],
                    "declared_constituents": [{"input_record_sha256": digest(r), "declaration": r}
                                              for r in component]})
                if counted:
                    joint_counts[target][(source, f)] += 1
                # Co-used constituents never become independent singleton labels.
                continue
            if counted:
                counts[source][(target, f)] += 1
                reverse[target][(source, f)] += 1
                signatures[source], outcomes[target] = src, dst
    ordinary = sum(sum(c.values()) for c in counts.values())
    joint = sum(sum(c.values()) for c in joint_counts.values())
    return {"version": VERSION, "unit": "target_overlap_component_occurrence_with_intact_declared_edges",
            "prior_contract_version": "joint_components_v2", "development_folds": [0, 1, 2],
            "excluded_whole_edges": excluded, "observations": ordinary + joint,
            "ordinary_rank_observations": ordinary, "joint_observation_count": joint,
            "joint_constituent_hyperedges": sum(len(v["declared_constituents"]) for v in joint_observations if v["counted"]),
            "joint_rank_policy": "whole_bundle_only;no_projection_to_singleton_rank_counts",
            "joint_outcome_signatures": joint_signatures, "joint_target_signatures": joint_targets,
            "joint_observations": joint_observations,
            "joint_target_to_outcome_counts": {t: [{"source": s, "fold": f, "count": n} for (s, f), n in sorted(c.items())]
                                               for t, c in sorted(joint_counts.items())},
            "source_signatures": signatures, "target_signatures": outcomes,
            "target_to_original_counts": {t: [{"source": s, "fold": f, "count": n} for (s, f), n in sorted(c.items())]
                                          for t, c in sorted(reverse.items())},
            "counts": {s: [{"target": t, "fold": f, "count": n} for (t, f), n in sorted(c.items())]
                       for s, c in sorted(counts.items())}, **GUARDS}


def query_distribution(source, target, f, index):
    observed = Counter()
    for item in index.get(target, []):
        if f in (0, 1, 2) and item["fold"] == f:
            continue
        if item["fold"] not in (0, 1, 2):
            raise ValueError("Prior contaminated by non-development fold")
        observed[item["source"]] += item["count"]
    total, matching = sum(observed.values()), observed[source]
    return {"source_signature_sha256": source, "target_signature_sha256": target,
            "excluded_prediction_fold": f if f in (0, 1, 2) else None,
            "support": total, "matching_support": matching, "distinct_outcomes": len(observed),
            "sparse": total < 3, "unknown": total == 0, "polysemous": len(observed) > 1,
            "empirical_support_ratio": matching / total if total else 0.0,
            "conditioning": "whole_target_surface_lemma_context_morphology_group",
            "outcomes": dict(sorted(observed.items())),
            "outcome_unit": "intact_original_group_signature_including_Strong_candidates"}


def query_prior(row, prior, originals, targets):
    source, target, _, _ = prior_keys(row, originals, targets)
    return query_distribution(source, target, fold(row["target_ref"]), prior["target_to_original_counts"])


def query_joint_prior(declarations, prior, originals, targets):
    source, target, _, _ = joint_prior_keys(declarations, originals, targets)
    result = query_distribution(source, target, fold(declarations[0]["target_ref"]), prior["joint_target_to_outcome_counts"])
    result.update({"conditioning": "whole_shared_target_union_surface_lemma_context_morphology",
                   "outcome_unit": "joint_bundle_of_intact_declared_constituents_with_union_subspans",
                   "constituent_count": len(declarations), "singleton_rank_projection": False})
    return result


def candidate_quality(row, config):
    value = row.get("generator_score")
    raw = value.get("raw", value.get("value")) if isinstance(value, dict) else None
    if not isinstance(raw, (int, float)) or isinstance(raw, bool) or not math.isfinite(raw):
        return config["unknown_raw_quality"]
    return max(config["raw_quality_floor"], min(1.0, raw))


def read_candidates(paths, originals, targets, config):
    """Preserve source IDs and digests; legacy retained separately with zero influence."""
    per_ref = defaultdict(dict)
    legacy = defaultdict(list)
    candidate_ids = set()
    counts = Counter()
    for label, path in sorted(paths.items()):
        for row in rows(path):
            o, t = physical(row, originals, targets)
            cid = row.get("candidate_id")
            if not isinstance(cid, str) or cid in candidate_ids:
                raise ValueError("Duplicate/missing candidate ID including excluded/outside-gold")
            candidate_ids.add(cid)
            if row.get("candidate_only") is not True or row.get("resolver_eligible") is not False or row.get("auto_acceptance") is not False or row.get("calibrated") is not False:
                raise ValueError("Candidate promotion/calibration guard changed")
            if row.get("calibrated_probability") is not None or row.get("prohibited_assignment_methods_used"):
                raise ValueError("Candidate has forbidden method/probability")
            generator = row.get("generator_id")
            counts[generator] += 1
            if generator == "legacy-zero-vote-v1":
                if row.get("vote_weight") != 0 or row.get("generator_score", {}).get("raw") != 0 or o:
                    raise ValueError("Legacy cannot vote")
                legacy[row["target_ref"]].append({"candidate_id": cid, "input_record_sha256": digest(row), "vote_weight": 0,
                    "target_token_ids": list(t), "strong_classic": row.get("strong_classic", []), "relation": "legacy_unproven_feature"})
                continue
            if generator not in config["channels"] or not row.get("evidence") or not row.get("evidence_channels"):
                raise ValueError("Unknown/unproved candidate channel")
            identity(row)
            declared = row.get("joint_use_with_candidate_ids", [])
            ids(declared)
            if cid in declared:
                raise ValueError("Candidate joint-use declaration references itself")
            key = edge_key(row)
            projection = {"candidate_id": cid, "generator_id": generator, "input_channel": label,
                          "input_record_sha256": digest(row), "dependency_family_ids": row.get("dependency_family_ids", []),
                          "evidence_channels": row["evidence_channels"], "evidence": row["evidence"],
                          "generator_score": row.get("generator_score"), "alternative_groups": row.get("alternative_groups", []),
                          "target_spans": row.get("target_spans", []),
                          "quality": candidate_quality(row, config),
                          "joint_use_with_candidate_ids": row.get("joint_use_with_candidate_ids", [])}
            edge = per_ref[row["target_ref"]].setdefault(key, {"edge_id": key, "target_ref": row["target_ref"],
                "original_token_ids": list(o), "target_token_ids": list(t), "relation": row["relation"],
                "null_reason": row.get("null_reason"), "provenance": [], **GUARDS})
            edge["provenance"].append(projection)
    for values in per_ref.values():
        for edge in values.values():
            edge["provenance"].sort(key=lambda p: p["candidate_id"])
            if any(cid not in candidate_ids for p in edge["provenance"] for cid in p["joint_use_with_candidate_ids"]):
                raise ValueError("Dangling candidate joint-use declaration")
    return dict(per_ref), dict(legacy), dict(sorted(counts.items()))


def evidence_groups(edge, config):
    """Collapse candidate observations connected by group or shared source family."""
    components = []
    for p in edge["provenance"]:
        labels = {"channel:" + config["channels"][p["generator_id"]]}
        labels.update("source:" + v for v in p["dependency_family_ids"])
        component = {"labels": labels, "quality": p["quality"], "candidate_ids": {p["candidate_id"]}}
        touching = [c for c in components if c["labels"] & labels]
        for c in touching:
            components.remove(c)
            component["labels"].update(c["labels"])
            component["candidate_ids"].update(c["candidate_ids"])
            component["quality"] = max(component["quality"], c["quality"])
        components.append(component)
    return sorted(({"labels": sorted(c["labels"]), "quality": min(config["group_cap"], c["quality"]),
                    "candidate_ids": sorted(c["candidate_ids"])} for c in components), key=canonical)


def compatible(left, right):
    if set(left["original_token_ids"]) & set(right["original_token_ids"]):
        return False
    if not set(left["target_token_ids"]) & set(right["target_token_ids"]):
        return True
    if not left["original_token_ids"] or not right["original_token_ids"]:
        return False
    # Joint sharing must be declared reciprocally by the raw candidate producers.
    # Missing evidence leaves alternatives unresolved; it does not prove sharing invalid.
    return any(lp["candidate_id"] in rp["joint_use_with_candidate_ids"] and
               rp["candidate_id"] in lp["joint_use_with_candidate_ids"]
               for lp in left["provenance"] for rp in right["provenance"])


def search(edges, original_ids, config):
    ordered = sorted((e for e in edges if not e.get("excluded_whole_edge", False)), key=lambda e: (-e["rank_score"], e["edge_id"]))
    allowed = set()
    local_pruned = 0
    for token in sorted(original_ids):
        relevant = [e for e in ordered if token in e["original_token_ids"]]
        allowed.update(e["edge_id"] for e in relevant[:config["max_edges_per_original"]])
        local_pruned += max(0, len(relevant) - config["max_edges_per_original"])
    allowed.update(e["edge_id"] for e in ordered if not e["original_token_ids"])
    # Each edge is considered once, so the search is a bounded set-packing beam.
    states = [(0.0, ())]
    index = {e["edge_id"]: e for e in edges}
    pruned = 0
    for edge in ordered:
        if edge["edge_id"] not in allowed:
            continue
        expanded = list(states)
        for score, chosen in states:
            if all(compatible(edge, index[k]) for k in chosen):
                new_chosen = tuple(sorted((*chosen, edge["edge_id"])))
                expanded.append((round(math.fsum(index[k]["rank_score"] for k in new_chosen), 12), new_chosen))
        expanded = sorted(set(expanded), key=lambda s: (-s[0], s[1]))
        pruned += max(0, len(expanded) - config["beam_width"])
        states = expanded[:config["beam_width"]]
    result = [{"rank": i + 1, "rank_score": s, "edge_ids": list(k), **GUARDS}
              for i, (s, k) in enumerate(states[:config["nbest"]])]
    return result, {"algorithm": "deterministic_edge_set_beam", "status": "approximate_bounded_search",
                    "global_optimum_claimed": False, "beam_width": config["beam_width"], "nbest_limit": config["nbest"],
                    "max_edges_per_original": config["max_edges_per_original"], "local_pruned_incidents": local_pruned,
                    "edges_removed_from_search": len(ordered) - len(allowed), "beam_states_pruned": pruned,
                    "deferred_edges_excluded_from_search": len(edges) - len(ordered),
                    "all_raw_edges_retained": True}


def accounting(original_ids, target_ids, edges, chosen):
    index = {e["edge_id"]: e for e in edges}
    os, ts = defaultdict(list), defaultdict(list)
    for eid in chosen:
        for token in index[eid]["original_token_ids"]:
            os[token].append(eid)
        for token in index[eid]["target_token_ids"]:
            ts[token].append(eid)
    originals = [{"token_id": token, "status": "candidate_selected" if os[token] else "unresolved_uncovered",
                  "edge_ids": sorted(os[token])} for token in sorted(original_ids)]
    targets = [{"token_id": token, "status": "candidate_selected" if ts[token] else "unresolved_uncovered",
                "edge_ids": sorted(ts[token]), "linked_original_token_ids": sorted({o for eid in ts[token] for o in index[eid]["original_token_ids"]})}
               for token in sorted(target_ids)]
    return {"original": originals, "target": targets}


def validate_graph(row):
    config = read(PACKAGE / "config.v1.json")
    def guards(value):
        for key, expected in GUARDS.items():
            actual = value.get(key)
            if type(actual) is not type(expected) or actual != expected:
                raise ValueError("Candidate-only guard changed or coerced")
    if row.get("version") != VERSION:
        raise ValueError("Graph contract version mismatch")
    guards(row)
    os, ts = [n["token_id"] for n in row["original_nodes"]], [n["token_id"] for n in row["target_nodes"]]
    if row.get("fold_id") != fold(row["target_ref"]) or any(n["target_ref"] != row["target_ref"] for n in row["original_nodes"] + row["target_nodes"]):
        raise ValueError("Graph fold/ref identity mismatch")
    if len(os) != len(set(os)) or len(ts) != len(set(ts)):
        raise ValueError("Duplicate graph node")
    index = {e["edge_id"]: e for e in row["edges"]}
    if len(index) != len(row["edges"]):
        raise ValueError("Duplicate graph hyperedge")
    for edge in row["edges"]:
        guards(edge)
        identity(edge)
        if edge["target_ref"] != row["target_ref"] or set(edge["original_token_ids"]) - set(os) or set(edge["target_token_ids"]) - set(ts) or edge["edge_id"] != edge_key(edge):
            raise ValueError("Dangling/stale graph hyperedge")
        if edge.get("excluded_whole_edge"):
            if edge["rank_score"] is not None or edge["prior"] is not None or edge["dependence_groups"]:
                raise ValueError("Deferred edge contributes ranking/prior evidence")
        else:
            if edge["dependence_groups"] != evidence_groups(edge, config):
                raise ValueError("Dependence cap decomposition invalid")
            expected_rank = round(sum(g["quality"] for g in edge["dependence_groups"]) +
                config["prior_weight"] * math.log1p(edge["prior"]["empirical_support_ratio"]), 12)
            if not math.isfinite(edge["rank_score"]) or edge["rank_score"] != expected_rank:
                raise ValueError("Rank decomposition invalid")
    for expected_rank, solution in enumerate(row["nbest"], 1):
        guards(solution)
        if solution.get("rank") != expected_rank or not math.isfinite(solution["rank_score"]):
            raise ValueError("Solution guard/rank invalid")
        chosen = solution["edge_ids"]
        if len(chosen) != len(set(chosen)) or any(eid not in index for eid in chosen):
            raise ValueError("Invalid solution references")
        if any(not compatible(index[a], index[b]) for i, a in enumerate(chosen) for b in chosen[i + 1:]):
            raise ValueError("Solution violates evidence compatibility")
        if any(index[k].get("excluded_whole_edge") for k in chosen):
            raise ValueError("Deferred edge selected")
        if round(math.fsum(index[k]["rank_score"] for k in chosen), 12) != round(solution["rank_score"], 12):
            raise ValueError("Solution score differs from selected edges")
    if row["nbest"] != sorted(row["nbest"], key=lambda s: (-s["rank_score"], tuple(s["edge_ids"]))):
        raise ValueError("Nbest ranking order is invalid")
    top = row["nbest"][0]["edge_ids"] if row["nbest"] else []
    if row["accounting"] != accounting(os, ts, row["edges"], top):
        raise ValueError("Incomplete/duplicated/nonreciprocal graph accounting")
    if row["search"]["global_optimum_claimed"] is not False:
        raise ValueError("Approximate search cannot claim optimum")


def build(repo, inputs, out):
    lock = check_inputs(inputs, repo)
    config = read(PACKAGE / "config.v1.json")
    from .io import source_roster
    generation_source = [spec(p, repo) for p in source_roster()]
    paths = {k: repo / v for k, v in lock["paths"].items()}
    print(canonical({"phase": "loading_frozen_answer_free_selected_nodes"}), flush=True)
    # Frozen answer-free preparation selected layer: candidate source universe
    # plus its already-proven manual textual-selection overlay, never gold links.
    originals, targets, by_ref = load_nodes(paths["gold_originals"], paths["targets"])
    if len(by_ref) != config["expected_verses"]:
        raise ValueError("Incomplete full verse grid")
    print(canonical({"phase": "building_development_only_group_prior", "original_nodes": len(originals), "target_nodes": len(targets), "verses": len(by_ref)}), flush=True)
    mask = load_mask(paths["mask"], originals, targets)
    prior = build_prior(paths["annotations"], mask, originals, targets)
    out.mkdir(parents=True, exist_ok=False)
    write(out / "prior.v1.json", prior)
    prior_counts = {"total": prior["observations"], "ordinary_rank": prior["ordinary_rank_observations"],
                    "joint_components": prior["joint_observation_count"], "joint_constituents": prior["joint_constituent_hyperedges"]}
    print(canonical({"phase": "loading_five_frozen_candidate_channels_and_legacy_diagnostics", "development_observations": prior_counts}), flush=True)
    candidates, legacy, counts = read_candidates({k: paths[k] for k in ("first_party", "statistical", "contextual")}, originals, targets, config)
    summary = Counter()
    print(canonical({"phase": "writing_full_grid_candidate_graph", "candidate_channel_rows": counts}), flush=True)
    with (out / "graph.v1.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for ref in sorted(by_ref):
            nodes = by_ref[ref]
            edges = sorted(candidates.get(ref, {}).values(), key=lambda e: e["edge_id"])
            for edge in edges:
                edge["excluded_whole_edge"] = masked(edge["original_token_ids"], edge["target_token_ids"], mask)
                if edge["excluded_whole_edge"]:
                    edge.update({"dependence_groups": [], "prior": None, "rank_score": None,
                                 "rank_contract": "whole_edge_deferred_exclusion_before_statistics"})
                    continue
                edge["dependence_groups"] = evidence_groups(edge, config)
                edge["prior"] = query_prior(edge, prior, originals, targets)
                edge["rank_score"] = round(sum(g["quality"] for g in edge["dependence_groups"]) +
                    config["prior_weight"] * math.log1p(edge["prior"]["empirical_support_ratio"]), 12)
                edge["rank_contract"] = "uncalibrated_candidate_only_rank"
            nbest, diagnostics = search(edges, nodes["original"], config)
            row = {"version": VERSION, "target_ref": ref, "fold_id": fold(ref),
                   "original_nodes": [originals[k] for k in nodes["original"]],
                   "target_nodes": [targets[k] for k in nodes["target"]], "edges": edges,
                   "nbest": nbest, "accounting": accounting(nodes["original"], nodes["target"], edges, nbest[0]["edge_ids"]),
                   "search": diagnostics, "legacy_zero_vote_diagnostics": sorted(legacy.get(ref, []), key=canonical), **GUARDS}
            validate_graph(row)
            handle.write(canonical(row) + "\n")
            summary.update({"verses": 1, "original_nodes": len(nodes["original"]), "target_nodes": len(nodes["target"]), "edges": len(edges),
                            "verses_without_candidates": not edges, "beam_states_pruned": diagnostics["beam_states_pruned"]})
    result = {"version": VERSION, "role": "implementation_author", "counts": dict(summary), "candidate_channel_rows": counts,
              "prior_observations": prior_counts,
              "generation_source": generation_source,
              "inputs": spec(inputs, repo), "config_sha256": sha(PACKAGE / "config.v1.json"),
              "outputs": [spec(out / n, repo) for n in ("graph.v1.jsonl", "prior.v1.json")], **GUARDS}
    write(out / "build.v1.manifest.json", result)
    return result


def validate_build(repo, inputs, out):
    from .io import verify, source_roster
    check_inputs(inputs, repo)
    manifest = read(out / "build.v1.manifest.json")
    expected_outputs = {(out / n).relative_to(repo).as_posix() for n in ("graph.v1.jsonl", "prior.v1.json")}
    if len(manifest["outputs"]) != 2 or {v["path"] for v in manifest["outputs"]} != expected_outputs:
        raise ValueError("Build outputs missing/duplicated/redirected")
    if manifest["generation_source"] != [spec(p, repo) for p in source_roster()]:
        raise ValueError("Generation source changed after build")
    if manifest["config_sha256"] != sha(PACKAGE / "config.v1.json") or manifest["inputs"] != spec(inputs, repo):
        raise ValueError("Build config/input is stale")
    for item in manifest["outputs"]:
        verify(item, repo)
    refs, originals, targets = set(), set(), set()
    for row in rows(out / "graph.v1.jsonl"):
        validate_graph(row)
        if row["target_ref"] in refs:
            raise ValueError("Duplicate verse graph")
        refs.add(row["target_ref"])
        for field, seen in (("original_nodes", originals), ("target_nodes", targets)):
            for node in row[field]:
                if node["token_id"] in seen or node["target_ref"] != row["target_ref"]:
                    raise ValueError("Duplicate/cross-verse graph node")
                seen.add(node["token_id"])
    lock = read(inputs)
    expected_o, expected_t, expected_refs = load_nodes(repo / lock["paths"]["gold_originals"], repo / lock["paths"]["targets"])
    if refs != set(expected_refs) or originals != set(expected_o) or targets != set(expected_t):
        raise ValueError("Incomplete full-grid accounting")
    return {"status": "PASS", "verses": len(refs), "original_nodes": len(originals), "target_nodes": len(targets)}

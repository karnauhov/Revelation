"""Bounded single-fit workflow and exclusive validation claim; test4 is skipped."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from . import VERSION
from .contracts import (base_strata, conflict, edge_key, evidence_strata, fixed_universe, fold, identity,
                        inspect_graph, load_labels, masked, safe_nodes, source_frequency)
from .io import (AUTHOR_SESSION, CANONICAL_FREEZE, GUARDS, PACKAGE, PREDECESSOR, canonical, check_code, check_protocol, claim, current_code,
                 digest, predecessor, read, rows, sha, spec, validate_guards, verify, write)
from .model import (all_success_requirement, components, diagnostic_class, final_class, fit_pava, lexical_keys,
                    metrics_by_stratum, probability, wilson_lower)

OUTPUTS = ("prepared.v1.jsonl", "model.v1.json", "predictions.v1.jsonl", "development.examples.v1.jsonl", "development.metrics.v1.json")


def prefit_support(repo, out, preflight):
    if read(preflight).get("status") != "PASS":
        raise ValueError("Root preflight PASS required")
    paths = predecessor(repo)
    originals, targets, by_ref, mask = safe_nodes(paths)
    config = read(PACKAGE / "config.v1.json")
    if len(by_ref) != config["expected_verses"]:
        raise ValueError("Incomplete full verse grid")
    by_book = defaultdict(lambda: defaultdict(Counter))
    eligible_refs = defaultdict(set)
    for (side, token), eligible in mask.items():
        node = (originals if side == "original" else targets)[token]
        ref, f = node["target_ref"], fold(node["target_ref"])
        group = by_book[ref.split(".")[0]][str(f)]
        group["full_" + side + "_nodes"] += 1
        group[("eligible_" if eligible else "deferred_") + side + "_nodes"] += 1
        if eligible:
            eligible_refs[(ref.split(".")[0], str(f))].add(ref)
    if len(by_book) != config["expected_books"]:
        raise ValueError("Mandatory all66 books missing from frozen mask")
    reviewed = set(read(paths["gold_contract"])["counts"]["by"]["stratum"])
    minimum = all_success_requirement(config["required_precision_lower_bound"], config["wilson_z"])
    books = {}
    for book, folds in sorted(by_book.items()):
        books[book] = {}
        for f in ["0", "1", "2", "3", "4"]:
            n = len(eligible_refs[(book, f)])
            books[book][f] = {**dict(folds[f]), "eligible_verses": n,
                             "hypothetical_all_success_verse_wilson_lower": wilson_lower(n, n),
                             "independent_verse_ceiling_sufficient": n >= minimum}
    result = {"version": VERSION, "artifact": "calibration77_prefit_support", "labels_read": False,
              "label_fields_accessed": [], "score_features_read": False, "model_fit": False,
              "predecessor": spec(repo / PREDECESSOR, repo), "preflight": spec(preflight, repo),
              "source_metadata_inputs": {k: spec(paths[k], repo) for k in ("gold_originals", "targets", "mask")},
              "full_verses": len(by_ref), "full_original_nodes": len(originals), "full_target_nodes": len(targets),
              "books": books, "required_book_count": 66, "strata_universe": fixed_universe(originals, targets, reviewed),
              "reviewed_taxonomy_vocabulary": sorted(reviewed),
              "reviewed_taxonomy_basis": "frozen_gold_contract_aggregate_names_only_no_annotation_rows_or_correctness",
              "all_success_independent_trials_required": minimum,
              "verse_ceiling_is_not_actual_independent_trial_count": True,
              "dependence_model_justified": config["certification_dependence_model_justified"],
              "certification_status": "NO_GO", "early_futility": True,
              "reasons": ["edge_Bernoulli_independence_not_justified",
                          "all66_book_conditional_precision_requires_more_independent_support_than_frozen_book_verse_ceiling"],
              "required_strata_may_not_be_dropped": True, "test4_action": "SKIP_WITHOUT_LABELS", **GUARDS}
    write(out, result)
    return result


def gold_indexes(gold):
    by_ref, og, tg = defaultdict(set), defaultdict(set), defaultdict(set)
    for key in gold:
        by_ref[key[0]].add(key)
        for token in key[2]:
            og[token].add(key)
        for token in key[3]:
            tg[token].add(key)
    return by_ref, og, tg


def labeled(edge, gold, og, tg):
    key = identity(edge)
    overlapped = set().union(*(og[t] for t in key[2]), *(tg[t] for t in key[3]))
    reviewed = {s for other in overlapped for s in gold[other]["strata"] if s.startswith("reviewed:")}
    return {**edge, "exact": key in gold, "strata": sorted(set(edge["strata"]) | (reviewed or {"reviewed:unclassified"}))}


def classify_prepared(row, model, model_spec, protocol_spec, config):
    edges = []
    for edge in row["edges"]:
        p = probability(model, edge["rank_score"])
        edges.append({**edge, "calibration_probability": p,
                      "diagnostic_class": diagnostic_class(p, edge["conflict"], config),
                      "final_class": final_class(diagnostic_class(p, edge["conflict"], config)),
                      "calibration_provenance": probability_provenance(row, edge, model_spec, protocol_spec, p), **GUARDS})
    index = {e["edge_id"]: e for e in edges}
    accounting = {}
    for side in ("original", "target"):
        accounting[side] = [{**n, "diagnostic_classes": sorted({index[e]["diagnostic_class"] for e in n["edge_ids"]}),
                            "final_classes": sorted({index[e]["final_class"] for e in n["edge_ids"]})}
                            for n in row["accounting"][side]]
    return {**row, "version": VERSION, "edges": edges, "accounting": accounting,
            "calibration_provenance": {"version": VERSION, "model": model_spec, "protocol": protocol_spec}, **GUARDS}


def probability_provenance(row, edge, model_spec, protocol_spec, p):
    return {"version": VERSION, "model": model_spec, "protocol": protocol_spec,
            "trained_folds": [0, 1, 2], "prediction_fold": row["fold_id"], "probability_is_certification": False,
            "input_graph_row_sha256": row["frozen_graph_row_sha256"], "feature_name": "frozen_top1_rank_score",
            "feature_sha256": digest({"edge_id": edge["edge_id"], "rank_score": edge["rank_score"],
                                      "input_graph_row_sha256": row["frozen_graph_row_sha256"]}),
            "correctness_unit": "exact_semantic_top1_hyperedge",
            "applicability": "frozen_consensus76_selected_top1_only_not_candidate_union_or_verse",
            "supported_in_development_score_range": p is not None}


def validate_prediction(row, model=None, model_spec=None, protocol_spec=None, config=None):
    if any(value is None for value in (model, model_spec, protocol_spec, config)):
        raise ValueError("Immutable model/protocol/config context required to consume probabilities")
    validate_guards(row)
    if row.get("version") != VERSION or row.get("fold_id") != fold(row["target_ref"]):
        raise ValueError("Wrong calibration version/fold")
    index = {}
    if row.get("calibration_provenance") != {"version": VERSION, "model": model_spec, "protocol": protocol_spec}:
        raise ValueError("Missing/stale verse calibration provenance")
    for edge in row["edges"]:
        validate_guards(edge)
        if edge["edge_id"] in index or edge.get("diagnostic_class") not in {"A_proposed", "B_review", "C_unresolved"}:
            raise ValueError("Duplicate calibration edge or invalid class")
        identity(edge)
        if edge["edge_id"] != edge_key(edge):
            raise ValueError("Calibrated semantic identity differs from frozen edge ID")
        p = edge["calibration_probability"]
        if p is not None and (isinstance(p, bool) or not isinstance(p, (int, float)) or not 0 <= p <= 1):
            raise ValueError("Invalid diagnostic probability")
        expected_p = probability(model, edge["rank_score"])
        if ("calibrated_probability" in edge or
            edge.get("calibration_provenance") != probability_provenance(row, edge, model_spec, protocol_spec, expected_p) or
            p != expected_p or edge["diagnostic_class"] != diagnostic_class(expected_p, edge["conflict"], config) or
            edge.get("final_class") != final_class(edge["diagnostic_class"])):
            raise ValueError("Missing standalone calibration provenance")
        index[edge["edge_id"]] = edge
    for side in ("original", "target"):
        seen = set()
        for node in row["accounting"][side]:
            token = node["token_id"]
            if token in seen or any(e not in index for e in node["edge_ids"]):
                raise ValueError("Duplicate/dangling calibration node accounting")
            seen.add(token)
            expected = sorted(eid for eid, edge in index.items() if token in edge[side + "_token_ids"])
            if node["edge_ids"] != expected:
                raise ValueError("Nonreciprocal calibration accounting")
            if node["status"] == "deferred_strong_unassigned" and expected:
                raise ValueError("Deferred node has a calibrated link")
            if node["diagnostic_classes"] != sorted({index[e]["diagnostic_class"] for e in expected}):
                raise ValueError("Node class accounting differs from incident edges")
            if node["final_classes"] != sorted({index[e]["final_class"] for e in expected}):
                raise ValueError("Node final class accounting differs from incident edges")
            if side == "target" and node["linked_original_token_ids"] != sorted({o for eid in expected for o in index[eid]["original_token_ids"]}):
                raise ValueError("Nonreciprocal target union")
        if {t for edge in index.values() for t in edge[side + "_token_ids"]} - seen:
            raise ValueError("Calibration edge endpoint missing from node accounting")


def develop(repo, protocol_path, out):
    paths = check_protocol(repo, protocol_path)
    protocol = read(protocol_path)
    config = protocol["config"]
    support_path = repo / protocol["support"]["path"]
    support = read(support_path)
    # One immutable protocol permits one development label access/fit, even if
    # an execution fails. Fixture-level deterministic replays need no real labels.
    if out.resolve() != (repo / AUTHOR_SESSION / "build.v1").resolve():
        raise ValueError("Development output must use preregistered canonical path")
    claim(repo, "development",
          {"protocol": spec(protocol_path, repo), "out": str(out), "one_fit_only": True})
    out.mkdir(parents=True, exist_ok=False)
    originals, targets, by_ref, mask = safe_nodes(paths)
    print(canonical({"phase": "label_free_source_frequency"}), flush=True)
    frequencies = source_frequency(paths["source_universe"])
    print(canonical({"phase": "development_only_eligible_labels", "folds": [0, 1, 2]}), flush=True)
    reviewed = {s.split(":", 1)[1] for s in support["strata_universe"] if s.startswith("reviewed:")}
    gold, excluded = load_labels(paths["annotations"], mask, originals, targets, {0, 1, 2}, frequencies, reviewed)
    gold_by_ref, og, tg = gold_indexes(gold)
    examples, refs, seen_o, seen_t = [], set(), set(), set()
    counts = Counter()
    print(canonical({"phase": "read_frozen_graph_once_all31102_no_validation_test_labels"}), flush=True)
    with (out / "prepared.v1.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for graph in rows(paths["graph"]):
            ref = graph["target_ref"]
            if ref in refs:
                raise ValueError("Duplicate graph verse")
            refs.add(ref)
            os, ts, index, chosen, deferred = inspect_graph(graph, originals, targets, mask)
            if seen_o & set(os) or seen_t & set(ts):
                raise ValueError("Duplicate physical graph node across verses")
            seen_o.update(os)
            seen_t.update(ts)
            edge_rows = []
            eligible_incidence, deferred_incidence = defaultdict(Counter), defaultdict(Counter)
            for eid, edge in index.items():
                for side in ("original", "target"):
                    for token in edge[side + "_token_ids"]:
                        (deferred_incidence if eid in deferred else eligible_incidence)[side][token] += 1
                if eid in deferred:
                    continue
                key = identity(edge)
                if key in gold:
                    gold[key]["strata"] += evidence_strata(edge)
                    gold[key]["strata"] += [s for s in base_strata(edge, os, ts, frequencies) if s == "anomaly:explicit_conflict"]
            for eid in chosen:
                edge = index[eid]
                # inspect_graph already rejects selected whole-edge deferrals.
                value = {k: edge[k] for k in ("edge_id", "target_ref", "original_token_ids", "target_token_ids", "relation", "null_reason", "rank_score")}
                value.update({"strata": sorted(set(base_strata(edge, os, ts, frequencies) + evidence_strata(edge))),
                              "cluster_keys": lexical_keys(edge, os, ts), "conflict": conflict(edge, os)})
                edge_rows.append(value)
                if ref in gold_by_ref:
                    examples.append(labeled(value, gold, og, tg))
            accounting = {}
            for side in ("original", "target"):
                accounting[side] = []
                for node in graph["accounting"][side]:
                    value = dict(node)
                    if mask.get((side, node["token_id"])) is False:
                        if node["edge_ids"]:
                            raise ValueError("Deferred graph node selected")
                        value["status"] = "deferred_strong_unassigned"
                    elif not node["edge_ids"]:
                        value["status"] = ("C_unresolved_unselected" if eligible_incidence[side][node["token_id"]]
                                           else "unresolved_only_deferred_candidates" if deferred_incidence[side][node["token_id"]]
                                           else "unresolved_uncovered")
                    value["eligible_raw_candidate_incidence"] = eligible_incidence[side][node["token_id"]]
                    value["deferred_raw_candidate_incidence"] = deferred_incidence[side][node["token_id"]]
                    accounting[side].append(value)
                    counts[side + ":" + value["status"]] += 1
            value = {"version": VERSION, "target_ref": ref, "fold_id": fold(ref), "edges": edge_rows,
                     "deferred_whole_edge_ids": deferred, "accounting": accounting,
                     "frozen_graph_row_sha256": digest(graph), **GUARDS}
            handle.write(canonical(value) + "\n")
            counts.update({"verses": 1, "original_nodes": len(os), "target_nodes": len(ts),
                           "top1_edges": len(chosen), "deferred_whole_edges": len(deferred)})
    if refs != set(by_ref) or seen_o != set(originals) or seen_t != set(targets) or len(refs) != config["expected_verses"]:
        raise ValueError("Full31102 exact-once graph node coverage failed")
    for value in gold.values():
        if not any(s.startswith("evidence:") for s in value["strata"]):
            value["strata"].append("evidence:missing")
        value["strata"] = sorted(set(value["strata"]))
    print(canonical({"phase": "single_fixed_in_sample_PAVA_fit", "examples": len(examples)}), flush=True)
    model = {"version": VERSION, "artifact": "calibration77_model", **fit_pava(examples),
             "protocol": spec(protocol_path, repo), "support": spec(support_path, repo),
             "certification_status": "NO_GO", "thresholds": {"A_proposed": config["a_threshold"], "B_review": config["b_threshold"]}, **GUARDS}
    write(out / "model.v1.json", model)
    model_spec, protocol_spec = spec(out / "model.v1.json", repo), spec(protocol_path, repo)
    by_id = {r["edge_id"]: r for r in examples}
    classified = []
    full_class_counts = defaultdict(Counter)
    full_topology_examples = defaultdict(list)
    with (out / "predictions.v1.jsonl").open("x", encoding="utf-8", newline="\n") as predictions:
        for row in rows(out / "prepared.v1.jsonl"):
            value = classify_prepared(row, model, model_spec, protocol_spec, config)
            validate_prediction(value, model, model_spec, protocol_spec, config)
            predictions.write(canonical(value) + "\n")
            f = str(row["fold_id"])
            for group in ("all", "fold:" + f):
                full_class_counts[group]["verses"] += 1
                for side in ("original", "target"):
                    for n in value["accounting"][side]:
                        full_class_counts[group][side + ":" + n["status"]] += 1
                for cls in ("A_auto", "B_review", "C_unresolved", "diagnostic:A_proposed"):
                    chosen = [e for e in value["edges"] if (e["diagnostic_class"] == "A_proposed" if cls == "diagnostic:A_proposed" else e["final_class"] == cls)]
                    full_class_counts[group][cls + ":edges"] += len(chosen)
                    full_class_counts[group][cls + ":verses"] += bool(chosen)
                    for side in ("original", "target"):
                        full_class_counts[group][cls + ":" + side + "_nodes"] += len({t for e in chosen for t in e[side + "_token_ids"]})
                for edge in value["edges"]:
                    topo = {"target_ref": edge["target_ref"], "cluster_keys": edge["cluster_keys"], "exact": False}
                    full_topology_examples[group].append(topo)
                    full_topology_examples[group + ":" + edge["final_class"]].append(topo)
                full_topology_examples[group + ":A_auto"]
            for edge in value["edges"]:
                if edge["edge_id"] in by_id:
                    classified.append({**by_id[edge["edge_id"]], **edge, "exact": by_id[edge["edge_id"]]["exact"],
                                       "strata": by_id[edge["edge_id"]]["strata"]})
    with (out / "development.examples.v1.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for row in sorted(classified, key=lambda r: r["edge_id"]):
            handle.write(canonical(row) + "\n")
    topology = {}
    for group, values in sorted(full_topology_examples.items()):
        raw = components(values)
        topology[group] = {k: raw[k] for k in ("edge_count", "verse_count", "component_count", "largest_component_edges", "component_size_histogram")}
        topology[group]["labels_read_for_topology"] = False
    metrics = {"version": VERSION, "artifact": "calibration77_development_diagnostics", "folds": [0, 1, 2],
               "protocol": protocol_spec, "model": model_spec, "counts": dict(counts), "excluded_gold": excluded,
               "full_label_free_classification_counts": {k: dict(v) for k, v in sorted(full_class_counts.items())},
               "full_label_free_cluster_topology": topology,
               "metrics": metrics_by_stratum(classified, gold, config, support["strata_universe"]),
               "in_sample": True, "nested_cross_validation": False, "dependence_adjusted_certification": False,
               "certification_status": "NO_GO", "test4_action": "SKIP_WITHOUT_LABELS", **GUARDS}
    write(out / "development.metrics.v1.json", metrics)
    check_protocol(repo, protocol_path, full_inputs=False)
    result = {"version": VERSION, "artifact": "calibration77_development", "protocol": protocol_spec,
              "outputs": [spec(out / n, repo) for n in OUTPUTS], "counts": dict(counts),
              "certification_status": "NO_GO", "development_fit_count": 1, "validation_labels_read": False,
              "test4_labels_read": False, **GUARDS}
    write(out / "development.v1.manifest.json", result)
    return result


def freeze(repo, protocol_path, build, out):
    if out.resolve() != (repo / CANONICAL_FREEZE).resolve() or build.resolve() != (repo / AUTHOR_SESSION / "build.v1").resolve():
        raise ValueError("Freeze/build must use preregistered canonical paths")
    check_protocol(repo, protocol_path)
    manifest_path = build / "development.v1.manifest.json"
    manifest = read(manifest_path)
    expected = [spec(build / n, repo) for n in OUTPUTS]
    if manifest.get("artifact") != "calibration77_development" or manifest.get("protocol") != spec(protocol_path, repo) or manifest.get("outputs") != expected:
        raise ValueError("Development output roster changed, missing or redirected")
    result = {"version": VERSION, "artifact": "calibration77_pipeline_freeze", "author": "/root/calibration_author",
              "protocol": spec(protocol_path, repo), "development": spec(manifest_path, repo), "outputs": expected,
              "certification_status": "NO_GO", "model_fit_count": 1, "threshold_search": False,
              **current_code(repo), **GUARDS}
    write(out, result)
    return result


def check_freeze(repo, path):
    if path.resolve() != (repo / CANONICAL_FREEZE).resolve():
        raise ValueError("Copied/redirected calibration freeze forbidden")
    value = read(path)
    validate_guards(value)
    if value.get("artifact") != "calibration77_pipeline_freeze" or value.get("version") != VERSION or value.get("certification_status") != "NO_GO":
        raise ValueError("Wrong or unsafe calibration freeze")
    check_code(value, repo)
    protocol_path = verify(value["protocol"], repo)
    paths = check_protocol(repo, protocol_path)
    manifest_path = verify(value["development"], repo)
    manifest = read(manifest_path)
    expected = [spec(manifest_path.parent / n, repo) for n in OUTPUTS]
    if value.get("outputs") != expected or manifest.get("outputs") != expected or manifest.get("protocol") != value["protocol"]:
        raise ValueError("Frozen output roster missing, stale, duplicated or redirected")
    return value, paths


def validate(repo, freeze_path, out):
    frozen, paths = check_freeze(repo, freeze_path)
    protocol = read(repo / frozen["protocol"]["path"])
    config, support = protocol["config"], read(repo / protocol["support"]["path"])
    claim(repo, "validation3",
          {"freeze": spec(freeze_path, repo), "output": str(out), "one_validation_only": True})
    out.mkdir(parents=True, exist_ok=False)
    originals, targets, _, mask = safe_nodes(paths)
    frequencies = source_frequency(paths["source_universe"])
    reviewed = {s.split(":", 1)[1] for s in support["strata_universe"] if s.startswith("reviewed:")}
    gold, excluded = load_labels(paths["annotations"], mask, originals, targets, {3}, frequencies, reviewed)
    by_ref, og, tg = gold_indexes(gold)
    prediction_path = next(repo / s["path"] for s in frozen["outputs"] if s["path"].endswith("predictions.v1.jsonl"))
    model_spec = next(s for s in frozen["outputs"] if s["path"].endswith("model.v1.json"))
    model = read(repo / model_spec["path"])
    examples = []
    coverage = Counter()
    # No graph ranking, fit or threshold adjustment is performed here.
    with (out / "validation3.examples.v1.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows(prediction_path):
            validate_prediction(row, model, model_spec, frozen["protocol"], config)
            if row["fold_id"] != 3:
                continue
            coverage["full_graph_verses"] += 1
            if row["target_ref"] not in by_ref:
                coverage["outside_gold_verses"] += 1
                continue
            coverage["eligible_gold_verses"] += 1
            for side in ("original", "target"):
                for n in row["accounting"][side]:
                    coverage[side + ":" + n["status"]] += 1
            for edge in row["edges"]:
                value = labeled(edge, gold, og, tg)
                examples.append(value)
                handle.write(canonical(value) + "\n")
    # Frozen raw graph supplies evidence-channel strata for exact gold candidates,
    # including gold candidates absent from selected top1. No labels become features.
    for graph in rows(paths["graph"]):
        if graph["fold_id"] != 3 or graph["target_ref"] not in by_ref:
            continue
        os, ts, index, _, deferred = inspect_graph(graph, originals, targets, mask)
        for eid, edge in index.items():
            if eid not in deferred and identity(edge) in gold:
                gold[identity(edge)]["strata"] += evidence_strata(edge)
                gold[identity(edge)]["strata"] += [s for s in base_strata(edge, os, ts, frequencies) if s == "anomaly:explicit_conflict"]
    for value in gold.values():
        if not any(s.startswith("evidence:") for s in value["strata"]):
            value["strata"].append("evidence:missing")
        value["strata"] = sorted(set(value["strata"]))
    result = {"version": VERSION, "artifact": "calibration77_validation3_diagnostics", "folds": [3],
              "freeze": spec(freeze_path, repo), "coverage": dict(coverage), "excluded_gold": excluded,
              "metrics": metrics_by_stratum(examples, gold, config, support["strata_universe"]),
              "output": spec(out / "validation3.examples.v1.jsonl", repo),
              "tuning_performed": False, "certification_status": "NO_GO", "A_auto": 0,
              "test4_metrics": "SKIPPED", "test4_labels_read": False, **GUARDS}
    check_code(frozen, repo)
    write(out / "validation3.v1.manifest.json", result)
    return result


def skip_test4(repo, freeze_path, validation_path, out):
    frozen, _ = check_freeze(repo, freeze_path)
    validation = read(validation_path)
    if validation.get("artifact") != "calibration77_validation3_diagnostics" or validation.get("freeze") != spec(freeze_path, repo) or validation.get("certification_status") != "NO_GO":
        raise ValueError("Test skip requires exact NO_GO validation predecessor")
    verify(validation["output"], repo)
    result = {"version": VERSION, "artifact": "calibration77_test4_predefined_skip", "status": "SKIPPED",
              "freeze": spec(freeze_path, repo), "validation3": spec(validation_path, repo),
              "reason": "prefit_dependence_and_required_strata_NO_GO", "test4_labels_read": False,
              "test4_scoring_invocations": 0, "test4_metrics": None, "historically_reused_test": True,
              "label_free_test4_predictions_exist": True, "A_auto": 0, **GUARDS}
    write(out, result)
    return result

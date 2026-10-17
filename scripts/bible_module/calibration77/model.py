"""Fixed deterministic isotonic fit and explicitly descriptive diagnostics."""
from __future__ import annotations

import bisect
import math
from collections import Counter, defaultdict

from .io import canonical, digest


def wilson_lower(successes, trials, z=1.6448536269514722):
    if type(successes) is not int or type(trials) is not int or not 0 <= successes <= trials:
        raise ValueError("Invalid Bernoulli counts")
    if not trials:
        return None
    p = successes / trials
    return (p + z * z / (2 * trials) - z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))) / (1 + z * z / trials)


def all_success_requirement(bound=.995, z=1.6448536269514722):
    n = 1
    while wilson_lower(n, n, z) < bound:
        n += 1
    return n


def fit_pava(examples):
    grouped = defaultdict(lambda: [0, 0])
    for row in examples:
        x, y = row["rank_score"], row["exact"]
        if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or type(y) is not bool:
            raise ValueError("PAVA needs finite rank and exact boolean correctness")
        grouped[x][0] += int(y)
        grouped[x][1] += 1
    if not grouped:
        raise ValueError("No eligible development top1 examples")
    blocks = []
    for x, (positive, count) in sorted(grouped.items()):
        blocks.append({"low": x, "high": x, "positive": positive, "count": count})
        while len(blocks) > 1 and blocks[-2]["positive"] * blocks[-1]["count"] > blocks[-1]["positive"] * blocks[-2]["count"]:
            right, left = blocks.pop(), blocks.pop()
            blocks.append({"low": left["low"], "high": right["high"],
                           "positive": left["positive"] + right["positive"], "count": left["count"] + right["count"]})
    for block in blocks:
        block["probability"] = block["positive"] / block["count"]
    return {"method": "rank_only_exact_score_PAVA", "blocks": blocks, "fit_examples": sum(v[1] for v in grouped.values()),
            "fit_folds": [0, 1, 2], "score_min": min(grouped), "score_max": max(grouped),
            "calibration_cross_fitted": False, "nested_cross_validation": False,
            "development_diagnostics_in_sample": True}


def probability(model, score):
    if isinstance(score, bool) or not isinstance(score, (float, int)) or not math.isfinite(score):
        raise ValueError("Nonfinite rank score")
    if not model["score_min"] <= score <= model["score_max"]:
        return None
    index = bisect.bisect_right([b["low"] for b in model["blocks"]], score) - 1
    return model["blocks"][index]["probability"]


def diagnostic_class(p, conflict, config):
    if p is None or conflict:
        return "C_unresolved"
    if p >= config["a_threshold"]:
        return "A_proposed"
    return "B_review" if p >= config["b_threshold"] else "C_unresolved"


def final_class(diagnostic):
    return "B_review" if diagnostic == "B_review" else "C_unresolved"


def lexical_keys(edge, originals, targets):
    result = {"verse:" + edge["target_ref"]}
    for token in edge["original_token_ids"]:
        node = originals[token]
        lemma, strong = node.get("lemma_raw"), node.get("strong_classic", [])
        family = node.get("source_family")
        if lemma:
            result.add("original_lemma:" + digest([family, lemma]))
        for atom in strong:
            result.add("original_Strong:" + digest([family, atom]))
        if not lemma and not strong:
            result.add("original:unknown")
    for token in edge["target_token_ids"]:
        node = targets[token]
        form = node.get("comparison") or node.get("surface")
        result.add("target:" + str(form) if form else "target:unknown")
    return sorted(result)


def components(examples):
    """Conservative connected components; no claim of independent components."""
    parent, first = list(range(len(examples))), {}
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, row in enumerate(examples):
        for key in row["cluster_keys"]:
            if key in first:
                a, b = find(i), find(first[key])
                parent[max(a, b)] = min(a, b)
            else:
                first[key] = i
    groups = defaultdict(list)
    for i, row in enumerate(examples):
        groups[find(i)].append(row)
    good = sum(all(r["exact"] for r in group) for group in groups.values())
    sizes = sorted((len(v) for v in groups.values()), reverse=True)
    return {"edge_count": len(examples), "verse_count": len({r["target_ref"] for r in examples}),
            "component_count": len(groups), "all_correct_components": good,
            "largest_component_edges": sizes[0] if sizes else 0,
            "component_size_histogram": dict(sorted(Counter(sizes).items())),
            "all_correct_component_wilson_lower_descriptive": wilson_lower(good, len(groups)),
            "component_estimand": "probability_all_edges_in_component_correct_not_edge_precision",
            "components_independent_claimed": False, "certifies_edge_precision": False}


def descriptive(examples, gold_support, config):
    counts = Counter(final_class(r["diagnostic_class"]) for r in examples)
    supported = [r for r in examples if r["calibration_probability"] is not None]
    bins = [{"bin": i, "count": 0, "positive": 0, "probabilities": []} for i in range(config["calibration_bins"])]
    briers, losses = [], []
    for row in supported:
        p, y = row["calibration_probability"], int(row["exact"])
        bucket = bins[min(len(bins) - 1, int(p * len(bins)))]
        bucket["count"] += 1
        bucket["positive"] += y
        bucket["probabilities"].append(p)
        briers.append((p - y) ** 2)
        q = min(1 - 1e-15, max(1e-15, p))
        losses.append(-(y * math.log(q) + (1 - y) * math.log1p(-q)))
    ece = 0.0
    for bucket in bins:
        n = bucket["count"]
        bucket["mean_probability"] = math.fsum(bucket.pop("probabilities")) / n if n else None
        bucket["accuracy"] = bucket["positive"] / n if n else None
        if n:
            ece += n * abs(bucket["accuracy"] - bucket["mean_probability"])
    proposed = [r for r in examples if r["diagnostic_class"] == "A_proposed"]
    correct = sum(r["exact"] for r in proposed)
    exact = sum(r["exact"] for r in examples)
    def class_metrics(selected):
        tp = sum(r["exact"] for r in selected)
        return {"tp": tp, "fp": len(selected) - tp, "fn": gold_support - tp,
                          "predicted_edge_denominator": len(selected), "full_eligible_gold_edge_denominator": gold_support,
                          "precision": tp / len(selected) if selected else None,
                          "recall": tp / gold_support if gold_support else None,
                          "edge_wilson_lower_descriptive": wilson_lower(tp, len(selected), config["wilson_z"]),
                          "original_nodes": len({t for r in selected for t in r["original_token_ids"]}),
                          "target_nodes": len({t for r in selected for t in r["target_token_ids"]}),
                          "verses": len({r["target_ref"] for r in selected}), "clusters": components(selected),
                          "accepted": False}
    by_class = {name: class_metrics([r for r in examples if final_class(r["diagnostic_class"]) == name])
                for name in ("A_auto", "B_review", "C_unresolved")}
    diagnostic_buckets = {name: class_metrics([r for r in examples if r["diagnostic_class"] == name])
                          for name in ("A_proposed", "B_review", "C_unresolved")}
    return {"top1_edges": len(examples), "exact_top1_edges": exact, "gold_support": gold_support,
            "top1_precision": exact / len(examples) if examples else None,
            "top1_recall": exact / gold_support if gold_support else None,
            "classes": {k: counts[k] for k in ("A_auto", "B_review", "C_unresolved")},
            "A_auto": 0, "per_class": by_class, "diagnostic_buckets": diagnostic_buckets, "A_proposed_exact": correct,
            "A_proposed_precision": correct / len(proposed) if proposed else None,
            "A_proposed_edge_wilson_lower_descriptive": wilson_lower(correct, len(proposed), config["wilson_z"]),
            "A_proposed_recall": correct / gold_support if gold_support else None,
            "supported_edges": len(supported), "unsupported_edges": len(examples) - len(supported),
            "brier_supported_only": math.fsum(briers) / len(supported) if supported else None,
            "log_loss_supported_only": math.fsum(losses) / len(supported) if supported else None,
            "ece_supported_only": ece / len(supported) if supported else None,
            "equal_width_reliability": bins, "all_prediction_clusters": components(examples),
            "A_proposed_clusters": components(proposed), "edge_independence_claimed": False,
            "precision_certified": False, "certification_status": "NO_GO"}


def metrics_by_stratum(examples, gold, config, universe=()):
    predicted, support = defaultdict(list), Counter()
    for row in examples:
        for name in ["all"] + row["strata"]:
            predicted[name].append(row)
    for value in gold.values():
        for name in ["all"] + value["strata"]:
            support[name] += 1
    names = set(predicted) | set(support) | set(universe)
    names.update({"testament:OT", "testament:NT", "source_frequency:rare_1_to_5", "source_frequency:mid",
                  "source_frequency:frequent_1000_plus", "source_frequency:unclassified"})
    result = {name: descriptive(predicted[name], support[name], config) for name in sorted(names)}
    for name, metric in result.items():
        keys = [key for key, value in gold.items() if name == "all" or name in value["strata"]]
        metric["eligible_gold_original_nodes"] = len({t for k in keys for t in k[2]})
        metric["eligible_gold_target_nodes"] = len({t for k in keys for t in k[3]})
        metric["eligible_gold_verses"] = len({k[0] for k in keys})
        metric["required_stratum_support_status"] = "present_descriptive_only" if metric["top1_edges"] else "unsupported_missing_or_zero_predictions"
        if any(c["fn"] < 0 for c in metric["per_class"].values()):
            raise ValueError("Stratum predicted exact support exceeds full eligible gold support")
    return result

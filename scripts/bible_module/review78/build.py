"""Compile verifiable verse packets without modifying any frozen input."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.bible_module.consensus76.core import fold, identity, physical
from scripts.bible_module.consensus76.io import canonical, digest, read, runtime_roster, sha, spec, verify

from .contracts import GUARDS, compile_case

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_20260801"
REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"
SESSION = WORK / "session_review78_20261017_root_01"
PREVIOUS = WORK / "session_precision78_20261017_root_01"
CLASSIFICATION = WORK / "session_calibration77_20261017_author_01/build.v1/development.examples.v1.jsonl"
STAGE6 = ROOT / "scripts/bible_module/work/ukrainian_stage_6_20260801/synthesized_text.jsonl"


def rows(path):
    with Path(path).open(encoding="utf8") as stream:
        for line in stream:
            yield json.loads(line)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf8", newline="\n") as stream:
        stream.write(canonical(value) + "\n")


def source_specs():
    return [spec(p, ROOT) for p in sorted(PACKAGE.rglob("*")) if p.is_file() and p.suffix in {".py", ".json", ".js", ".css", ".html"}]


def lock():
    if read(SESSION / "preflight.v1.json")["status"] != "PASS":
        raise ValueError("Preflight required")
    previous = read(REPORT / "precision78.v1.manifest.json")
    for item in previous["evidence"]:
        verify(item, ROOT)
    frozen = read(PREVIOUS / "inputs.v1.lock.json")
    paths = {k: ROOT / v for k, v in frozen["paths"].items()}
    inputs = list(frozen["dependencies"])
    inputs += [spec(p, ROOT) for p in (PREVIOUS / "development_error_taxonomy.v1.jsonl", PREVIOUS / "taxonomy.v1.json", REPORT / "precision78.v1.manifest.json", CLASSIFICATION, STAGE6)]
    # Pin classification to the existing calibration77 freeze, not arbitrary labels.
    freeze = read(WORK / "session_calibration77_20261017_author_01/pipeline.v1.lock.json")
    expected = next(v for v in freeze["outputs"] if v["path"].endswith("development.examples.v1.jsonl"))
    verify(expected, ROOT)
    if sha(STAGE6) != "e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf":
        raise ValueError("Immutable OH1988 text changed")
    write(SESSION / "inputs.v1.lock.json", {"paths": {k: p.relative_to(ROOT).as_posix() for k, p in paths.items()}, "inputs": inputs})
    write(SESSION / "source_runtime.v1.lock.json", {"source": source_specs(), "upstream_source": read(PREVIOUS / "source_runtime.v1.lock.json")["source"], "runtime": [spec(p) for p in runtime_roster()]})
    write(SESSION / "protocol.v1.lock.json", {"protocol": read(PACKAGE / "protocol.v1.json"), "inputs": spec(SESSION / "inputs.v1.lock.json", ROOT), "source_runtime": spec(SESSION / "source_runtime.v1.lock.json", ROOT), "preflight": spec(SESSION / "preflight.v1.json", ROOT)})


def build():
    protocol = read(SESSION / "protocol.v1.lock.json")
    for key in ("inputs", "source_runtime", "preflight"):
        verify(protocol[key], ROOT)
    locked = read(SESSION / "source_runtime.v1.lock.json")
    if source_specs() != locked["source"]:
        raise ValueError("Source changed after lock")
    inputs = read(SESSION / "inputs.v1.lock.json")
    for item in inputs["inputs"] + locked["runtime"] + locked["upstream_source"]:
        verify(item, ROOT)
    paths = {k: ROOT / v for k, v in inputs["paths"].items()}
    cases = list(rows(PREVIOUS / "development_error_taxonomy.v1.jsonl"))
    if len(cases) != 5782 or len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("Taxonomy cohort changed")
    by_ref = defaultdict(list)
    for case in cases:
        if fold(case["target_ref"]) not in {0, 1, 2}:
            raise ValueError("Historical validation/test is not a review development case")
        by_ref[case["target_ref"]].append(case)
    wanted_edges = {c["prediction_edge_id"] for c in cases}
    classes = {r["edge_id"]: r for r in rows(CLASSIFICATION) if r["edge_id"] in wanted_edges}
    if set(classes) != wanted_edges:
        raise ValueError("Missing calibration77 class")
    mask, reviewed_refs = {}, set()
    for row in rows(paths["mask"]):
        side = "original" if "original_token_id" in row else "target"
        mask[side, row[side + "_token_id"]] = row["eligible"]
        reviewed_refs.add(row["target_ref"])
    gold = defaultdict(dict)
    for row in rows(paths["annotations"]):
        ref = row["target_ref"]
        if ref not in by_ref:
            continue
        if row["record_type"] == "hyperedge" and all(mask.get((side, t), False) for side in ("original", "target") for t in row[side + "_token_ids"]):
            identity(row)
            gold[ref][row["edge_id"]] = row
    # Exact source text and mapping are carried intact, not reconstructed by joining tokens.
    texts = {}
    for row in rows(STAGE6):
        ref = row.get("target_ref")
        if ref in by_ref:
            texts[ref] = row
    out = SESSION / "build.v1"
    out.mkdir(exist_ok=False)
    packets, index, counts = [], [], Counter()
    for graph in rows(paths["graph"]):
        ref = graph["target_ref"]
        if ref not in by_ref:
            continue
        if ref not in reviewed_refs:
            raise ValueError("Case outside reviewed cohort")
        os = {n["token_id"]: n for n in graph["original_nodes"]}
        ts = {n["token_id"]: n for n in graph["target_nodes"]}
        edges = []
        for edge in graph["edges"]:
            o, t = physical(edge, os, ts)
            blocked = any(mask.get(("original", v)) is False for v in o) or any(mask.get(("target", v)) is False for v in t)
            if blocked != edge["excluded_whole_edge"]:
                raise ValueError("Deferred eligibility mismatch")
            if not blocked:
                identity(edge)
                edges.append(edge)
        compiled = [compile_case(c, graph, gold[ref], classes[c["prediction_edge_id"]]) for c in by_ref[ref]]
        packet = {"version": "review78-v1", "target_ref": ref, "fold": fold(ref), "source_graph_row_sha256": digest(graph),
                  "oh1988_source": texts.get(ref), "original_nodes": graph["original_nodes"], "target_nodes": graph["target_nodes"],
                  "deferred_original_ids": sorted(t for t in os if mask.get(("original", t)) is False),
                  "deferred_target_ids": sorted(t for t in ts if mask.get(("target", t)) is False),
                  "candidate_edges": edges, "nbest": graph["nbest"], "historical_gold_edges": list(gold[ref].values()), "cases": compiled, **GUARDS}
        if packet["oh1988_source"] is None:
            raise ValueError("Missing exact verse source text")
        # Exact scalar spans must continue to address the immutable source text.
        text = packet["oh1988_source"]["plain_text_nfc"]
        for n in graph["target_nodes"]:
            if text[n["start_scalar"]:n["end_scalar"]] != n["surface"]:
                raise ValueError("OH1988 span is stale")
        path = out / "verses" / (digest(ref) + ".json")
        write(path, packet)
        packet_spec = {**spec(path), "path": path.relative_to(out).as_posix(), "target_ref": ref}
        packets.append(packet_spec)
        for c in compiled:
            prediction = next(e for e in edges if e["edge_id"] == c["prediction_edge_id"])
            label = " ".join(ts[t]["surface"] for t in prediction["target_token_ids"]) or "NULL"
            index.append({"case_id": c["case_id"], "target_ref": ref, "final_class": c["final_class"], "structural": c["structural"],
                          "hint_tags": c["evidence_hints_not_causal_labels"], "conflict_count": len(c["conflicting_candidate_edge_ids"]), "target_label": label})
            counts[c["final_class"]] += 1
        if len(packets) % 250 == 0:
            print("compiled verses", len(packets), flush=True)
    if len(index) != len(cases) or {p["target_ref"] for p in packets} != set(by_ref):
        raise ValueError("Incomplete development workbench")
    write(out / "index.json", {"version": "review78-v1", "cases": index, "counts": dict(counts), "folds": [0, 1, 2], **GUARDS})
    write(out / "manifest.json", {"version": "review78-v1", "protocol": spec(SESSION / "protocol.v1.lock.json", ROOT),
          "index": {**spec(out / "index.json"), "path": "index.json"}, "packets": packets, "case_count": len(index), "verse_count": len(packets), **GUARDS})
    print(canonical({"status": "PASS", "cases": len(index), "verses": len(packets), "classes": dict(counts), "output": str(out)}))

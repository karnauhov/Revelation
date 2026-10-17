from __future__ import annotations

import copy
import json
import math
import random
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from scripts.bible_module.calibration77 import contracts, io, model, pipeline
from scripts.bible_module.consensus76 import core


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = io.read(io.PACKAGE / "config.v1.json")
        self.ref = next(f"Gen.1.{v}" for v in range(1, 100) if core.fold(f"Gen.1.{v}") == 0)
        self.originals = {"o1": {"token_id": "o1", "target_ref": self.ref, "lemma_raw": "lemma", "strong_classic": ["H1"],
                                   "source_family": "fixture", "reading_status": "primary_mt", "mapping_operation": "1:1"},
                          "o2": {"token_id": "o2", "target_ref": self.ref, "lemma_raw": "other", "strong_classic": ["H2"],
                                   "source_family": "fixture", "reading_status": "primary_mt"}}
        self.targets = {"t1": {"token_id": "t1", "target_ref": self.ref, "surface": "word", "comparison": "word",
                                "genre": "torah_prose_law", "testament": "OT"},
                        "t2": {"token_id": "t2", "target_ref": self.ref, "surface": "other", "comparison": "other",
                                "genre": "torah_prose_law", "testament": "OT"}}
        self.mask = {("original", t): True for t in self.originals} | {("target", t): True for t in self.targets}

    def edge(self, o="o1", t="t1", rank=.7):
        edge = {"target_ref": self.ref, "original_token_ids": [o], "target_token_ids": [t], "relation": "one_to_one",
                "null_reason": None, "rank_score": rank, "provenance": [], "dependence_groups": [],
                "excluded_whole_edge": False, **core.GUARDS}
        edge["edge_id"] = core.edge_key(edge)
        return edge

    def graph(self, edges=None, chosen=None):
        edges = edges if edges is not None else [self.edge()]
        chosen = chosen if chosen is not None else [e["edge_id"] for e in edges if not e["excluded_whole_edge"]]
        return {"version": "consensus76-v1", "target_ref": self.ref, "fold_id": core.fold(self.ref),
                "original_nodes": list(self.originals.values()), "target_nodes": list(self.targets.values()),
                "edges": edges, "nbest": [{"edge_ids": chosen}],
                "accounting": core.accounting(list(self.originals), list(self.targets), edges, chosen), **core.GUARDS}

    def jsonl(self, records):
        path = self.root / "fixture.jsonl"
        path.write_text("".join(io.canonical(r) + "\n" for r in records), encoding="utf-8")
        return path

    def gold_rows(self):
        result = []
        for i in (1, 2):
            e = self.edge(f"o{i}", f"t{i}")
            e.update({"record_type": "hyperedge", "status": "reviewed_accepted"})
            result += [e,
                {"record_type": "original_decision", "target_ref": self.ref, "original_token_id": f"o{i}",
                 "status": "reviewed_accepted", "relation": "one_to_one", "group_original_token_ids": [f"o{i}"],
                 "target_token_ids": [f"t{i}"], "edge_id": e["edge_id"], "phenomena": ["reorder"]},
                {"record_type": "target_accounting", "target_ref": self.ref, "target_token_id": f"t{i}",
                 "status": "reviewed_accepted", "linked_original_token_ids": [f"o{i}"], "phenomena": []}]
        return result

    def prediction(self):
        e = self.edge()
        e = {k: e[k] for k in ("edge_id", "target_ref", "original_token_ids", "target_token_ids", "relation", "null_reason", "rank_score")}
        e.update({"strata": [], "cluster_keys": ["verse:" + self.ref], "conflict": False})
        prepared = {"target_ref": self.ref, "fold_id": 0, "edges": [e],
                    "accounting": core.accounting(list(self.originals), list(self.targets), [e], [e["edge_id"]]),
                    "frozen_graph_row_sha256": "a" * 64}
        fitted = model.fit_pava([{**e, "exact": True}])
        ms, ps = {"path": "model.json", "sha256": "b" * 64, "bytes": 1}, {"path": "protocol.json", "sha256": "c" * 64, "bytes": 1}
        result = pipeline.classify_prepared(prepared, fitted, ms, ps, self.config)
        return result, fitted, ms, ps

    def test_wilson_one_sided_and_low_support(self):
        self.assertEqual(model.all_success_requirement(), 539)
        self.assertLess(model.wilson_lower(538, 538), .995)
        self.assertGreaterEqual(model.wilson_lower(539, 539), .995)
        self.assertIsNone(model.wilson_lower(0, 0))
        self.assertAlmostEqual(model.wilson_lower(1, 1), 1 / (1 + self.config["wilson_z"] ** 2))
        with self.assertRaises(ValueError):
            model.wilson_lower(True, 1)

    def test_pava_known_adjacent_pool_and_ties(self):
        fit = model.fit_pava([{"rank_score": 1, "exact": True}, {"rank_score": 2, "exact": False},
                              {"rank_score": 3, "exact": True}, {"rank_score": 3, "exact": True}])
        self.assertEqual([(b["low"], b["high"], b["probability"]) for b in fit["blocks"]], [(1, 2, .5), (3, 3, 1)])
        self.assertEqual(model.probability(fit, 2.5), .5)
        self.assertEqual(model.probability(fit, 3), 1)

    def test_no_extrapolation_to_unsupported_high_rank(self):
        fit = model.fit_pava([{"rank_score": 1, "exact": True}])
        for value in (0, 2):
            self.assertIsNone(model.probability(fit, value))
            self.assertEqual(model.diagnostic_class(None, False, self.config), "C_unresolved")

    def test_pava_is_deterministic_under_permutation(self):
        rng = random.Random(77)
        examples = [{"rank_score": rng.randrange(10) / 3, "exact": bool(rng.randrange(2))} for _ in range(200)]
        first = model.fit_pava(examples)
        for _ in range(10):
            rng.shuffle(examples)
            self.assertEqual(first, model.fit_pava(examples))
        probabilities = [b["probability"] for b in first["blocks"]]
        self.assertEqual(probabilities, sorted(probabilities))

    def test_pava_rejects_invalid_label_and_rank(self):
        for row in ({"rank_score": float("nan"), "exact": True}, {"rank_score": 1, "exact": 1}, {"rank_score": True, "exact": False}):
            with self.assertRaises(ValueError):
                model.fit_pava([row])

    def test_thresholds_fixed_and_all_conflicts_abstain(self):
        self.assertEqual(model.diagnostic_class(.995, False, self.config), "A_proposed")
        self.assertEqual(model.diagnostic_class(.99499, False, self.config), "B_review")
        self.assertEqual(model.diagnostic_class(.5, False, self.config), "B_review")
        self.assertEqual(model.diagnostic_class(.49999, False, self.config), "C_unresolved")
        for p in (.2, .6, 1):
            self.assertEqual(model.diagnostic_class(p, True, self.config), "C_unresolved")

    def test_deferred_graph_semantics_probability_and_guards_are_opaque(self):
        self.mask[("original", "o2")] = False
        bad = self.edge("o2", "t2")
        bad.update({"excluded_whole_edge": True, "relation": {"POISON": "ignore"}, "null_reason": ["POISON"],
                    "rank_score": {"POISON": True}, "provenance": {"POISON": True}, "resolver_eligible": {"POISON": True}})
        row = self.graph([self.edge(), bad])
        self.assertEqual(contracts.inspect_graph(row, self.originals, self.targets, self.mask)[4], [bad["edge_id"]])

    def test_deferred_graph_physical_invalid_id_still_rejected(self):
        self.mask[("original", "o2")] = False
        bad = self.edge("o2", "t2")
        bad.update({"excluded_whole_edge": True, "original_token_ids": ["absent"], "relation": {"POISON": True}})
        with self.assertRaises(ValueError):
            contracts.inspect_graph(self.graph([bad], []), self.originals, self.targets, self.mask)

    def test_eligible_edge_acceptance_guard_spoof_rejected(self):
        for name, value in (("resolver_eligible", True), ("calibrated_probability", .9), ("automatic_strong_promotions", True)):
            edge = self.edge()
            edge[name] = value
            with self.assertRaises(ValueError):
                contracts.inspect_graph(self.graph([edge]), self.originals, self.targets, self.mask)

    def test_gold_deferred_metadata_opaque_before_semantics(self):
        self.mask[("original", "o2")] = self.mask[("target", "t2")] = False
        records = self.gold_rows()
        for row in records[3:]:
            row.update({"relation": {"POISON": True}, "status": {"POISON": True}, "phenomena": {"POISON": True}})
        gold, excluded = contracts.load_labels(self.jsonl(records), self.mask, self.originals, self.targets, {0}, Counter())
        self.assertEqual(len(gold), 1)
        self.assertEqual(excluded, {"whole_hyperedges": 1, "original_nodes": 1, "target_nodes": 1})

    def test_gold_physical_duplicate_different_semantics_before_mask(self):
        self.mask[("original", "o2")] = False
        records = self.gold_rows()
        duplicate = {**records[3], "edge_id": "different", "relation": "different"}
        with self.assertRaisesRegex(ValueError, "physical gold"):
            contracts.load_labels(self.jsonl(records + [duplicate]), self.mask, self.originals, self.targets, {0}, Counter())

    def test_partition_labels_not_accessed_semantically(self):
        records = self.gold_rows()
        for row in records:
            row.update({"relation": {"POISON": True}, "status": {"POISON": True}, "phenomena": {"POISON": True}})
        gold, _ = contracts.load_labels(self.jsonl(records), self.mask, self.originals, self.targets, {3}, Counter())
        self.assertEqual(gold, {})

    def test_semantic_exactness_includes_relation_null_and_whole_group(self):
        edge = self.edge()
        key = core.identity(edge)
        self.assertNotEqual(key, core.identity({**edge, "relation": "grouped_expression"}))
        self.assertNotEqual(key, core.identity({**edge, "original_token_ids": ["o1", "o2"], "relation": "many_to_one"}))
        null = {**edge, "target_token_ids": [], "relation": "original_omitted", "null_reason": "not_overtly_translated"}
        self.assertNotEqual(core.identity(null), core.identity({**null, "null_reason": "grammatical_function"}))

    def test_lexical_components_connect_multistrong_overlap_and_verse(self):
        self.originals["o1"]["strong_classic"] = ["H1", "H2"]
        a = {"target_ref": self.ref, "cluster_keys": model.lexical_keys(self.edge(), self.originals, self.targets), "exact": True}
        self.originals["o2"]["strong_classic"] = ["H2", "H3"]
        b = {"target_ref": "Exod.1.1", "cluster_keys": model.lexical_keys(self.edge("o2", "t2"), self.originals, self.targets), "exact": False}
        stats = model.components([a, b])
        self.assertEqual(stats["component_count"], 1)
        self.assertFalse(stats["certifies_edge_precision"])
        self.assertEqual(stats["all_correct_components"], 0)

    def test_all_class_fn_uses_full_eligible_gold_support(self):
        row, fitted, ms, ps = self.prediction()
        edge = row["edges"][0]
        metrics = model.descriptive([{**edge, "exact": True}], 5, self.config)
        self.assertEqual(metrics["diagnostic_buckets"]["A_proposed"]["fn"], 4)
        self.assertEqual(metrics["per_class"]["A_auto"]["fn"], 5)
        self.assertIsNone(metrics["per_class"]["A_auto"]["precision"])
        self.assertEqual(metrics["per_class"]["C_unresolved"]["fn"], 4)
        self.assertEqual(metrics["per_class"]["B_review"]["fn"], 5)
        self.assertEqual(metrics["A_auto"], 0)

    def test_provenance_and_probability_spoofs_rejected(self):
        row, fitted, ms, ps = self.prediction()
        pipeline.validate_prediction(row, fitted, ms, ps, self.config)
        mutations = [lambda r: r["edges"][0]["calibration_provenance"].pop("model"),
                     lambda r: r["edges"][0]["calibration_provenance"].update(trained_folds=[3]),
                     lambda r: r["edges"][0]["calibration_provenance"].update(feature_sha256="x"),
                     lambda r: r["edges"][0]["calibration_provenance"].update(prediction_fold=4),
                     lambda r: r["edges"][0].update(calibration_probability=.8),
                     lambda r: r["edges"][0].update(diagnostic_class="B_review"),
                     lambda r: r.update(resolver_eligible=True)]
        for mutate in mutations:
            changed = copy.deepcopy(row)
            mutate(changed)
            with self.assertRaises(ValueError):
                pipeline.validate_prediction(changed, fitted, ms, ps, self.config)
        with self.assertRaises(ValueError):
            pipeline.validate_prediction(row)

    def test_node_accounting_reciprocal_and_shared_target_union(self):
        row, fitted, ms, ps = self.prediction()
        row["accounting"]["target"][0]["linked_original_token_ids"] = []
        with self.assertRaises(ValueError):
            pipeline.validate_prediction(row, fitted, ms, ps, self.config)

    def test_physical_lock_tampering_missing_and_exclusive_write(self):
        path = self.root / "file.json"
        io.write(path, {"value": 1})
        locked = io.spec(path, self.root)
        self.assertEqual(io.verify(locked, self.root), path)
        with self.assertRaises(FileExistsError):
            io.write(path, {"value": 2})
        path.write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            io.verify(locked, self.root)
        path.unlink()
        with self.assertRaises(ValueError):
            io.verify(locked, self.root)

    def test_source_runtime_roster_tampering(self):
        package = self.root / "package"
        package.mkdir()
        source, runtime = package / "source.py", self.root / "python.exe"
        source.write_text("x=1\n", encoding="utf-8")
        runtime.write_text("runtime", encoding="utf-8")
        with patch.object(io, "PACKAGE", package), patch.object(io, "runtime_roster", return_value=[runtime]):
            locked = io.current_code(self.root)
            io.check_code(locked, self.root)
            runtime.write_text("changed", encoding="utf-8")
            with self.assertRaises(ValueError):
                io.check_code(locked, self.root)
            runtime.write_text("runtime", encoding="utf-8")
            (package / "added.py").write_text("x=2\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                io.check_code(locked, self.root)

    def test_validation_claim_persists_and_forbids_second_label_read(self):
        freeze_path = self.root / "freeze.json"
        frozen = {"protocol": {"path": "protocol.json"}}
        io.write(self.root / "protocol.json", {"config": self.config, "support": {"path": "support.json"}})
        io.write(self.root / "support.json", {"strata_universe": []})
        with patch.object(pipeline, "check_freeze", return_value=(frozen, {})), patch.object(pipeline, "safe_nodes", side_effect=RuntimeError("fixture stop before labels")):
            freeze_path.write_text("{}", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                pipeline.validate(self.root, freeze_path, self.root / "validation")
            self.assertTrue((self.root / io.AUTHOR_SESSION / "validation3.claim.v1.json").is_file())
            with self.assertRaises(FileExistsError):
                pipeline.validate(self.root, freeze_path, self.root / "another")

    def test_copied_protocol_and_freeze_path_cannot_bypass_claims(self):
        for method in (lambda: io.check_protocol(self.root, self.root / "copied_protocol.json"),
                       lambda: pipeline.check_freeze(self.root, self.root / "copied_freeze.json")):
            with self.assertRaisesRegex(ValueError, "Copied/redirected"):
                method()
        io.claim(self.root, "development", {"freeze": "same"})
        with self.assertRaises(FileExistsError):
            io.claim(self.root, "development", {"freeze": "copied"})

    def test_required_missing_strata_retained_and_extra_reviewed_vocabulary(self):
        universe = contracts.fixed_universe(self.originals, self.targets, ["age_idiom"])
        self.assertIn("reviewed:age_idiom", universe)
        self.assertIn("genre:missing", universe)
        self.assertIn("evidence:missing", universe)
        metric = model.metrics_by_stratum([], {}, self.config, ["book:Gen", "reviewed:age_idiom"])
        self.assertIsNone(metric["book:Gen"]["per_class"]["A_auto"]["precision"])
        self.assertEqual(metric["reviewed:age_idiom"]["top1_edges"], 0)

    def test_final_class_high_score_is_unresolved_under_nogo(self):
        row, fitted, ms, ps = self.prediction()
        self.assertEqual(row["edges"][0]["diagnostic_class"], "A_proposed")
        self.assertEqual(row["edges"][0]["final_class"], "C_unresolved")
        row["edges"][0]["final_class"] = "A_auto"
        with self.assertRaises(ValueError):
            pipeline.validate_prediction(row, fitted, ms, ps, self.config)

    def test_null_and_multiword_edges_remain_whole_in_probability_contract(self):
        row, fitted, ms, ps = self.prediction()
        edge = row["edges"][0]
        changed = copy.deepcopy(row)
        changed["edges"][0]["original_token_ids"].append("o2")
        changed["edges"][0]["relation"] = "many_to_one"
        with self.assertRaises(ValueError):
            pipeline.validate_prediction(changed, fitted, ms, ps, self.config)

    def test_test4_skip_never_loads_labels_or_scores(self):
        freeze_path, validation_path = self.root / "freeze.json", self.root / "validation.json"
        freeze_path.write_text("{}", encoding="utf-8")
        output = self.root / "examples.jsonl"
        output.write_text("", encoding="utf-8")
        io.write(validation_path, {"artifact": "calibration77_validation3_diagnostics", "freeze": io.spec(freeze_path, self.root),
                                   "certification_status": "NO_GO", "output": io.spec(output, self.root)})
        with patch.object(pipeline, "check_freeze", return_value=({}, {})), patch.object(pipeline, "load_labels", side_effect=AssertionError("test labels forbidden")):
            receipt = pipeline.skip_test4(self.root, freeze_path, validation_path, self.root / "skip.json")
        self.assertEqual(receipt["status"], "SKIPPED")
        self.assertEqual(receipt["test4_scoring_invocations"], 0)

    def test_development_fixture_full_accounting_unselected_and_final_classes(self):
        protocol_path = self.root / io.CANONICAL_PROTOCOL
        support_path = self.root / io.AUTHOR_SESSION / "support.v1.json"
        io.write(support_path, {"strata_universe": contracts.fixed_universe(self.originals, self.targets)})
        config = {**self.config, "expected_verses": 1}
        io.write(protocol_path, {"config": config, "support": io.spec(support_path, self.root)})
        annotation_path = self.jsonl(self.gold_rows())
        graph_path = self.root / "graph.jsonl"
        first, second = self.edge(), self.edge("o2", "t2")
        graph_path.write_text(io.canonical(self.graph([first, second], [first["edge_id"]])) + "\n", encoding="utf-8")
        source_path = self.root / "source.jsonl"
        source_path.write_text("".join(io.canonical({**n, "original_token_id": t}) + "\n" for t, n in self.originals.items()), encoding="utf-8")
        paths = {"annotations": annotation_path, "source_universe": source_path, "graph": graph_path}
        out = self.root / io.AUTHOR_SESSION / "build.v1"
        with patch.object(pipeline, "check_protocol", return_value=paths), patch.object(pipeline, "safe_nodes", return_value=(self.originals, self.targets, {self.ref: {}}, self.mask)):
            result = pipeline.develop(self.root, protocol_path, out)
        self.assertEqual(result["development_fit_count"], 1)
        prediction = list(io.rows(out / "predictions.v1.jsonl"))[0]
        self.assertEqual(prediction["edges"][0]["final_class"], "C_unresolved")
        self.assertEqual(prediction["accounting"]["original"][1]["status"], "C_unresolved_unselected")
        metrics = io.read(out / "development.metrics.v1.json")
        self.assertEqual(metrics["metrics"]["all"]["per_class"]["A_auto"]["fn"], 2)
        self.assertEqual(metrics["full_label_free_classification_counts"]["all"]["C_unresolved:edges"], 1)


if __name__ == "__main__":
    unittest.main()

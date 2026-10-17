import copy
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.bible_module.consensus76 import core, evaluation, io


class ConsensusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = io.read(io.PACKAGE / "config.v1.json")

    def jsonl(self, name, records):
        p = self.root / name
        p.write_text("".join(io.canonical(r) + "\n" for r in records), encoding="utf-8")
        return p

    def ref(self, f):
        return next(f"Gen.1.{v}" for v in range(1, 1000) if core.fold(f"Gen.1.{v}") == f)

    def nodes(self, refs=None):
        refs = refs or [self.ref(0)]
        originals, targets = {}, {}
        for i, ref in enumerate(refs):
            for j in range(3):
                originals[f"o{i}{j}"] = {"token_id": f"o{i}{j}", "target_ref": ref, "order": j,
                    "source_family": "test", "lemma_raw": f"L{j}", "strong_classic": [f"H{j + 1}"], "morphology_raw": "N"}
                targets[f"t{i}{j}"] = {"token_id": f"t{i}{j}", "target_ref": ref, "order": j,
                    "surface": f"word{j}", "comparison": f"word{j}", "lemma_pos_morphology_candidates": [{"lemma": f"word{j}"}],
                    "left_context": ["left"], "right_context": ["right"], "testament": "OT"}
        return originals, targets

    def candidate(self, ref=None, os=None, ts=None, cid="candidate1", generator="bridge-full-group-surface-v1"):
        return {"target_ref": ref or self.ref(0), "original_token_ids": os if os is not None else ["o00"],
                "target_token_ids": ts if ts is not None else ["t00"], "relation": "one_to_one", "null_reason": None,
                "candidate_id": cid, "generator_id": generator, "generator_score": {"raw": .7, "calibrated": False},
                "evidence": [{"kind": "direct_source"}], "evidence_channels": ["lexical"], "dependency_family_ids": ["shared"],
                "prohibited_assignment_methods_used": [], **core.GUARDS}

    def edge(self, os=None, ts=None, cid="a"):
        row = self.candidate(os=os, ts=ts, cid=cid)
        row["edge_id"] = core.edge_key(row)
        row["provenance"] = [{"candidate_id": cid, "generator_id": row["generator_id"], "quality": .7,
                              "dependency_family_ids": ["shared"], "joint_use_with_candidate_ids": []}]
        row["dependence_groups"] = core.evidence_groups(row, self.config)
        row["prior"] = {"empirical_support_ratio": 0.0}
        row["rank_score"] = .7
        row["excluded_whole_edge"] = False
        return row

    def gold(self, row, eid="g"):
        value = copy.deepcopy(row)
        value.update({"record_type": "hyperedge", "edge_id": eid, "status": "reviewed_accepted"})
        return value

    def test_full_accounting_uncovered_is_not_null(self):
        a = self.edge()
        value = core.accounting(["o00", "o01"], ["t00", "t01"], [a], [a["edge_id"]])
        self.assertEqual(value["original"][1]["status"], "unresolved_uncovered")
        self.assertEqual(value["target"][1]["linked_original_token_ids"], [])
        self.assertNotIn("null_reason", value["original"][1])

    def test_shared_target_requires_reciprocal_raw_joint_witness(self):
        a, b = self.edge(cid="a"), self.edge(os=["o01"], cid="b")
        self.assertFalse(core.compatible(a, b))
        a["provenance"][0]["joint_use_with_candidate_ids"] = ["b"]
        self.assertFalse(core.compatible(a, b))
        b["provenance"][0]["joint_use_with_candidate_ids"] = ["a"]
        self.assertTrue(core.compatible(a, b))
        solutions, _ = core.search([a, b], ["o00", "o01"], self.config)
        self.assertEqual(len(solutions[0]["edge_ids"]), 2)
        acc = core.accounting(["o00", "o01"], ["t00"], [a, b], solutions[0]["edge_ids"])
        self.assertEqual(acc["target"][0]["linked_original_token_ids"], ["o00", "o01"])
        self.assertEqual(len(acc["target"]), 1)

    def test_original_exclusivity_and_null_conflict(self):
        a, b = self.edge(), self.edge(ts=["t01"], cid="b")
        self.assertFalse(core.compatible(a, b))
        b = self.edge(cid="addition")
        b["original_token_ids"] = []
        b["relation"], b["null_reason"] = "translation_addition", "translation_expansion"
        self.assertFalse(core.compatible(a, b))
        with self.assertRaises(ValueError):
            core.identity({**a, "target_token_ids": []})

    def test_many_many_stays_group_and_null_needs_reason(self):
        a = self.candidate(os=["o00", "o01"], ts=["t00", "t01"])
        a["relation"] = "many_to_many"
        self.assertEqual(len(core.identity(a)[2]), 2)
        a.update({"target_token_ids": [], "relation": "original_omitted"})
        with self.assertRaises(ValueError):
            core.identity(a)
        a["null_reason"] = "source_text_not_rendered"
        self.assertEqual(core.identity(a)[1], "original_omitted")

    def test_dependencies_cap_correlated_generators(self):
        a = self.edge()
        p = copy.deepcopy(a["provenance"][0])
        p.update({"candidate_id": "b", "quality": .9, "generator_id": "ibm1-bidirectional-oof-v1"})
        a["provenance"].append(p)
        groups = core.evidence_groups(a, self.config)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["quality"], .9)
        a["provenance"].append({**p, "candidate_id": "c", "generator_id": "transliteration-named-entity-v1", "dependency_family_ids": ["independent"]})
        self.assertEqual(len(core.evidence_groups(a, self.config)), 2)

    def test_prior_oof_no_fold3_4_label_access_poison(self):
        refs = [self.ref(f) for f in range(5)]
        originals, targets = self.nodes(refs)
        records = []
        for i, ref in enumerate(refs):
            row = self.gold(self.candidate(ref, [f"o{i}0"], [f"t{i}0"]), f"g{i}")
            if i >= 3:
                row["relation"] = {"POISON": "must not be read"}
                row["status"] = {"POISON": "must not be read"}
            records.append(row)
        mask = {(s, t): True for s, values in (("original", originals), ("target", targets)) for t in values}
        prior = core.build_prior(self.jsonl("gold", records), mask, originals, targets)
        self.assertEqual(prior["observations"], 3)
        for i in range(5):
            q = core.query_prior(self.candidate(refs[i], [f"o{i}0"], [f"t{i}0"]), prior, originals, targets)
            self.assertEqual(q["support"], 2 if i < 3 else 3)
        self.assertEqual({v["fold"] for values in prior["target_to_original_counts"].values() for v in values}, {0, 1, 2})

    def test_prior_whole_edge_mask_before_poison_metadata(self):
        originals, targets = self.nodes()
        row = self.gold(self.candidate())
        row["relation"] = {"POISON": True}
        mask = {("original", "o00"): False}
        prior = core.build_prior(self.jsonl("gold", [row]), mask, originals, targets)
        self.assertEqual(prior["observations"], 0)
        self.assertEqual(prior["excluded_whole_edges"], 1)
        bad = {**row, "original_token_ids": ["DANGLING"]}
        with self.assertRaises(ValueError):
            core.build_prior(self.jsonl("bad", [bad]), mask, originals, targets)
        with self.assertRaises(ValueError):
            core.build_prior(self.jsonl("duplicate", [row, row]), mask, originals, targets)

    def test_prior_group_count_no_pairwise_or_repeat_inflation_polysemy(self):
        originals, targets = self.nodes([self.ref(0), self.ref(1), self.ref(2)])
        a = self.candidate(os=["o00", "o01"], ts=["t00", "t01"])
        a["relation"] = "many_to_many"
        b = self.candidate(self.ref(1), ["o10", "o11"], ["t10", "t11"])
        b["relation"] = "many_to_many"
        c = self.candidate(self.ref(2), ["o20", "o21"], ["t20", "t21"])
        c["relation"] = "many_to_many"
        originals["o20"]["strong_classic"] = ["H99"]
        prior = core.build_prior(self.jsonl("gold", [self.gold(a, "a"), self.gold(b, "b"), self.gold(c, "c")]),
                    {(s, t): True for s, vals in (("original", originals), ("target", targets)) for t in vals}, originals, targets)
        self.assertEqual(prior["observations"], 3)
        self.assertTrue(all(len(sig) == 2 for sig in prior["source_signatures"].values()))
        query = core.query_prior({**a, "target_ref": self.ref(4)}, prior, originals, targets)
        self.assertTrue(query["polysemous"])
        self.assertEqual(query["support"], 3)

    def test_context_morphology_and_source_signature_preserved(self):
        originals, targets = self.nodes()
        src, dst, sig, target = core.prior_keys(self.candidate(), originals, targets)
        self.assertEqual(target["target_group"][0]["context"]["left"], ["left"])
        targets["t00"]["right_context"] = ["changed"]
        self.assertNotEqual(dst, core.prior_keys(self.candidate(), originals, targets)[1])
        originals["o00"]["lemma_raw"] = None
        self.assertNotEqual(src, core.prior_keys(self.candidate(), originals, targets)[0])

    def test_legacy_zero_vote_and_candidate_guard(self):
        originals, targets = self.nodes()
        legacy = self.candidate(os=[], generator="legacy-zero-vote-v1")
        legacy.update({"vote_weight": 0, "generator_score": {"raw": 0}, "relation": "legacy_unproven_feature"})
        edges, diagnostics, _ = core.read_candidates({"a": self.jsonl("c", [legacy])}, originals, targets, self.config)
        self.assertEqual(edges, {})
        self.assertEqual(len(diagnostics[self.ref(0)]), 1)
        legacy["vote_weight"] = 1
        with self.assertRaises(ValueError):
            core.read_candidates({"a": self.jsonl("bad", [legacy])}, originals, targets, self.config)

    def test_row_permutation_deterministic(self):
        originals, targets = self.nodes()
        a, b = self.candidate(), self.candidate(os=["o01"], ts=["t01"], cid="b")
        left = core.read_candidates({"a": self.jsonl("a", [a, b])}, originals, targets, self.config)
        right = core.read_candidates({"a": self.jsonl("b", [b, a])}, originals, targets, self.config)
        self.assertEqual(io.canonical(left), io.canonical(right))
        ea, eb = self.edge(), self.edge(os=["o01"], ts=["t01"], cid="b")
        self.assertEqual(core.search([ea, eb], ["o00", "o01"], self.config), core.search([eb, ea], ["o01", "o00"], self.config))

    def test_graph_mutations_guard_fold_accounting_rank(self):
        originals, targets = self.nodes()
        edge = self.edge()
        solutions, diagnostics = core.search([edge], list(originals), self.config)
        row = {"version": "consensus76-v1", "target_ref": self.ref(0), "fold_id": 0, "original_nodes": list(originals.values()),
               "target_nodes": list(targets.values()), "edges": [edge], "nbest": solutions,
               "accounting": core.accounting(list(originals), list(targets), [edge], solutions[0]["edge_ids"]),
               "search": diagnostics, **core.GUARDS}
        core.validate_graph(row)
        for change in [lambda r: r.update(fold_id=4), lambda r: r["nbest"][0].update(resolver_eligible=True),
                       lambda r: r.update(resolver_eligible=0),
                       lambda r: r["accounting"]["target"][0].update(linked_original_token_ids=[]),
                       lambda r: r["edges"][0].update(rank_score=float("nan")), lambda r: r["edges"][0].update(excluded_whole_edge=True)]:
            bad = copy.deepcopy(row)
            change(bad)
            with self.assertRaises(ValueError):
                core.validate_graph(bad)

    def test_full_recall_denominator_and_exact_hyperedge(self):
        self.assertEqual(evaluation.metric(1, 1, 9)["recall"], .1)
        key = core.identity(self.candidate())
        self.assertEqual(evaluation.classify(key, {key: {}}, {"o00": key}, {"t00": {key}}), "exact_complete_hyperedge")
        wrong = (*key[:1], "grouped_expression", *key[2:])
        self.assertEqual(evaluation.classify(wrong, {key: {}}, {"o00": key}, {"t00": {key}}), "wrong_relation_or_null_reason")

    def test_source_frequency_not_reviewed_stratum(self):
        path = self.jsonl("freq", [{"original_token_id": "a", "reading_status": "primary_mt", "strong_classic": ["H1"]},
                                  {"original_token_id": "b", "reading_status": "alternative", "strong_classic": ["H1"]}])
        self.assertEqual(evaluation.source_frequency(path)["H1"], 1)
        self.assertEqual(evaluation.bands(["a"], {"a": {"strong_classic": ["H1"]}}, {"H1": 1}), ["source_frequency:rare_1_to_5"])

    def test_physical_tamper_and_source_roster_addition(self):
        p = self.root / "source.py"
        p.write_text("original", encoding="utf-8")
        item = io.spec(p)
        io.verify(item, self.root)
        p.write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            io.verify(item, self.root)
        self.assertTrue(any(p.name == "test_consensus76.py" for p in io.source_roster()))
        self.assertTrue(any(p.name == "schema.v1.json" for p in io.source_roster()))

    def test_no_mask_evidence_and_no_optimum_claim(self):
        edge = self.edge()
        edge.update(excluded_whole_edge=True, rank_score=None, prior=None, dependence_groups=[])
        solutions, diagnostics = core.search([edge], ["o00"], self.config)
        self.assertEqual(solutions[0]["edge_ids"], [])
        self.assertEqual(diagnostics["deferred_edges_excluded_from_search"], 1)
        self.assertFalse(diagnostics["global_optimum_claimed"])

    def test_gold_shared_target_keeps_declared_edges_and_reciprocal_union(self):
        originals, targets = self.nodes()
        a, b = self.gold(self.candidate(), "a"), self.gold(self.candidate(os=["o01"]), "b")
        records = [a, b]
        for row in [a, b]:
            token = row["original_token_ids"][0]
            records.append({"record_type": "original_decision", "target_ref": row["target_ref"], "status": "reviewed_accepted",
                            "original_token_id": token, "group_original_token_ids": [token], "target_token_ids": ["t00"],
                            "relation": "one_to_one", "edge_id": row["edge_id"]})
        records.append({"record_type": "target_accounting", "target_ref": a["target_ref"], "status": "reviewed_accepted",
                        "target_token_id": "t00", "linked_original_token_ids": ["o00", "o01"]})
        mask = {("original", "o00"): True, ("original", "o01"): True, ("target", "t00"): True}
        gold, excluded, support = evaluation.load_gold(self.jsonl("gold_shared", records), mask, originals, targets, {0}, {"H1": 2, "H2": 2})
        self.assertEqual(len(gold), 2)
        self.assertEqual(support["original_decisions"], 2)
        records[-1]["linked_original_token_ids"] = ["o00"]
        with self.assertRaises(ValueError):
            evaluation.load_gold(self.jsonl("gold_broken", records), mask, originals, targets, {0}, {})

    def test_repeated_semantic_group_observation_counts_once_per_verse(self):
        originals, targets = self.nodes()
        originals["o01"] = {**originals["o00"], "token_id": "o01"}
        targets["t01"] = {**targets["t00"], "token_id": "t01"}
        records = [self.gold(self.candidate(), "a"), self.gold(self.candidate(os=["o01"], ts=["t01"]), "b")]
        mask = {(s, t): True for s, values in (("original", originals), ("target", targets)) for t in values}
        prior = core.build_prior(self.jsonl("repeat", records), mask, originals, targets)
        self.assertEqual(prior["observations"], 1)

    def test_shared_same_target_is_one_joint_outcome_without_singleton_leakage(self):
        originals, targets = self.nodes([self.ref(0), self.ref(4)])
        declarations = [self.gold(self.candidate(os=["o00"]), "a"),
                        self.gold(self.candidate(os=["o01"]), "b")]
        mask = {(side, token): True for side, values in (("original", originals), ("target", targets)) for token in values}
        prior = core.build_prior(self.jsonl("joint", declarations), mask, originals, targets)
        self.assertEqual((prior["observations"], prior["ordinary_rank_observations"], prior["joint_observation_count"]), (1, 0, 1))
        self.assertEqual(prior["joint_constituent_hyperedges"], 2)
        query = [self.gold(self.candidate(self.ref(4), ["o10"], ["t10"]), "x"),
                 self.gold(self.candidate(self.ref(4), ["o11"], ["t10"]), "y")]
        joint = core.query_joint_prior(query, prior, originals, targets)
        self.assertEqual((joint["support"], joint["matching_support"], joint["distinct_outcomes"]), (1, 1, 1))
        self.assertEqual(joint["empirical_support_ratio"], 1)
        self.assertFalse(joint["polysemous"])
        self.assertEqual(core.query_joint_prior(declarations, prior, originals, targets)["support"], 0)
        self.assertEqual(core.query_prior(query[0], prior, originals, targets)["support"], 0)
        self.assertEqual([v["declaration"] for v in prior["joint_observations"][0]["declared_constituents"]], declarations)
        for mutation in [lambda rows: rows[1].update(original_token_ids=["o00"]),
                         lambda rows: rows[1].update(original_token_ids=["dangling"]),
                         lambda rows: rows[1].update(target_token_ids=["t10"]),
                         lambda rows: rows[1].update(original_token_ids=["o01", "o01"]),
                         lambda rows: rows[1].update(edge_id="a"),
                         lambda rows: rows[1].update(relation="unknown"),
                         lambda rows: rows[1].update(target_ref=self.ref(4))]:
            bad = copy.deepcopy(declarations)
            mutation(bad)
            with self.assertRaises(ValueError):
                core.query_joint_prior(bad, prior, originals, targets)

    def test_joint_transitive_partial_overlap_mask_and_multiplicity(self):
        originals, targets = self.nodes()
        originals["o01"] = {**originals["o00"], "token_id": "o01"}
        a = self.gold(self.candidate(), "a")
        b = self.gold(self.candidate(os=["o01"], ts=["t00", "t01"]), "b")
        c = self.gold(self.candidate(os=["o02"], ts=["t01", "t02"]), "c")
        b["relation"] = c["relation"] = "one_to_many"
        mask = {(side, token): True for side, values in (("original", originals), ("target", targets)) for token in values}
        path = self.jsonl("transitive", [c, a, b])
        prior = core.build_prior(path, mask, originals, targets)
        self.assertEqual((prior["observations"], prior["joint_constituent_hyperedges"]), (1, 3))
        outcome = next(iter(prior["joint_outcome_signatures"].values()))["declared_constituents"]
        self.assertEqual(len(outcome), 3)
        self.assertEqual(sorted(v["target_union_positions"] for v in outcome), [[0], [0, 1], [1, 2]])
        self.assertEqual(core.build_prior(self.jsonl("permuted", [b, c, a]), mask, originals, targets), prior)
        # A masked bridge is removed before components are constructed.
        mask[("original", "o01")] = False
        excluded = core.build_prior(path, mask, originals, targets)
        self.assertEqual((excluded["ordinary_rank_observations"], excluded["joint_observation_count"]), (2, 0))
        # Equal lexical constituents remain separate declarations in one outcome.
        b = self.gold(self.candidate(os=["o01"]), "b")
        _, _, source, _ = core.joint_prior_keys([a, b], originals, targets)
        self.assertEqual(len(source["declared_constituents"]), 2)
        self.assertEqual(source["declared_constituents"][0], source["declared_constituents"][1])

    def test_repeated_joint_semantics_and_oof_count_components_once(self):
        refs = [self.ref(i) for i in (0, 1, 2, 4)]
        originals, targets = self.nodes(refs)
        records = []
        for i in range(3):
            records.extend([self.gold(self.candidate(refs[i], [f"o{i}0"], [f"t{i}0"]), f"a{i}"),
                            self.gold(self.candidate(refs[i], [f"o{i}1"], [f"t{i}0"]), f"b{i}")])
        mask = {(side, token): True for side, values in (("original", originals), ("target", targets)) for token in values}
        prior = core.build_prior(self.jsonl("joint_oof", records), mask, originals, targets)
        self.assertEqual((prior["observations"], prior["joint_constituent_hyperedges"]), (3, 6))
        self.assertEqual(core.query_joint_prior(records[:2], prior, originals, targets)["support"], 2)
        query = [self.gold(self.candidate(refs[3], [f"o3{j}"], ["t30"]), f"q{j}") for j in range(2)]
        self.assertEqual(core.query_joint_prior(query, prior, originals, targets)["support"], 3)
        originals["o20"]["strong_classic"] = ["H99"]
        polysemous = core.build_prior(self.jsonl("joint_polysemy", records), mask, originals, targets)
        distribution = core.query_joint_prior(query, polysemous, originals, targets)
        self.assertEqual((distribution["support"], distribution["matching_support"], distribution["distinct_outcomes"]), (3, 2, 2))
        self.assertTrue(distribution["polysemous"])
        originals["o20"]["strong_classic"] = ["H1"]
        # A second physical occurrence with the same complete bundle in one verse
        # retains its declarations but contributes no repeated semantic count.
        for j in (0, 1):
            originals[f"o0{j+3}"] = {**originals[f"o0{j}"], "token_id": f"o0{j+3}"}
        targets["t03"] = {**targets["t00"], "token_id": "t03"}
        records.extend([self.gold(self.candidate(refs[0], ["o03"], ["t03"]), "repeat_a"),
                        self.gold(self.candidate(refs[0], ["o04"], ["t03"]), "repeat_b")])
        mask.update({("original", "o03"): True, ("original", "o04"): True, ("target", "t03"): True})
        repeated = core.build_prior(self.jsonl("joint_repeat", records), mask, originals, targets)
        self.assertEqual(repeated["observations"], 3)
        self.assertEqual(len(repeated["joint_observations"]), 4)
        self.assertEqual(sum(v["counted"] for v in repeated["joint_observations"]), 3)

    def test_actual_shared_target_partial_overlap_declarations_retained(self):
        fixture = io.read(Path(__file__).with_name("shared_target_fixtures.v1.json"))
        declarations = fixture["declarations"]
        originals, targets = {}, {}
        for row in declarations:
            for side, nodes in (("original", originals), ("target", targets)):
                for token in row[side + "_token_ids"]:
                    nodes[token] = {"token_id": token, "target_ref": row["target_ref"],
                                    "order": int(token.split(":")[2]) if side == "target" else 0,
                                    "surface": token, "lemma_raw": token, "strong_classic": []}
        mask = {(side, token): True for side, values in (("original", originals), ("target", targets)) for token in values}
        prior = core.build_prior(self.jsonl("actual_joint", declarations), mask, originals, targets)
        self.assertEqual((prior["observations"], prior["ordinary_rank_observations"], prior["joint_constituent_hyperedges"]), (3, 0, 6))
        self.assertEqual({v["target_ref"]: len(v["ordered_target_union_ids"]) for v in prior["joint_observations"]},
                         {"Judg.18.24": 2, "Mat.5.11": 3, "Ruth.2.7": 2})
        retained = [v["declaration"] for obs in prior["joint_observations"] for v in obs["declared_constituents"]]
        self.assertEqual(sorted(retained, key=lambda r: r["edge_id"]), declarations)
        self.assertTrue(all(v["fold"] in (0, 1, 2) for v in prior["joint_observations"]))

    def test_missing_redirected_duplicate_input_lock_rejected(self):
        expected = {"version": "consensus76-v1", "gold_lock_sha256": io.GOLD_HASH,
                    "dependencies": [{"path": "a", "sha256": "a", "bytes": 1}], "paths": {"targets": "a"}, "consumer_roster": []}
        for mutation in [lambda x: x.update(dependencies=[]), lambda x: x["paths"].update(targets="elsewhere"),
                         lambda x: x["dependencies"].append(x["dependencies"][0])]:
            bad = copy.deepcopy(expected)
            mutation(bad)
            p = self.root / "inputs.json"
            io.write(p, bad)
            with patch.object(io, "lock_inputs", return_value=expected), self.assertRaises(ValueError):
                io.check_inputs(p, self.root)

    def test_sealed_gate_blocks_before_label_read_and_one_time_claim(self):
        out = self.root / "sealed"
        freeze = self.root / "freeze.json"
        io.write(freeze, {"test": True})
        with patch.object(evaluation, "check_freeze", return_value={"author": "author"}):
            with self.assertRaises(ValueError):
                evaluation.evaluate(self.root, freeze, {4}, out)
        self.assertFalse(out.exists())
        gate = self.root / "gate.json"
        io.write(gate, {"approved": True, "freeze_sha256": "wrong", "reviewer": "independent", "code_review_pass": True, "payload_review_pass": True})
        with patch.object(evaluation, "check_freeze", return_value={"author": "author"}), self.assertRaises(ValueError):
            evaluation.evaluate(self.root, freeze, {4}, out, gate)

    def test_candidate_malformed_cross_verse_duplicate_and_guard_rejected(self):
        originals, targets = self.nodes()
        base = self.candidate()
        for mutation in [lambda x: x.update(original_token_ids=["dangling"]), lambda x: x.update(target_ref="Gen.99.1"),
                         lambda x: x.update(original_token_ids=["o00", "o00"]), lambda x: x.update(calibrated_probability=.99),
                         lambda x: x.update(resolver_eligible=True)]:
            value = copy.deepcopy(base)
            mutation(value)
            with self.assertRaises(ValueError):
                core.read_candidates({"x": self.jsonl("malformed", [value])}, originals, targets, self.config)
        with self.assertRaises(ValueError):
            core.read_candidates({"x": self.jsonl("dup", [base, base])}, originals, targets, self.config)

    def test_actual_build_excludes_whole_deferred_edge_before_rank_consumers(self):
        originals, targets = self.nodes()
        op = self.jsonl("originals", list(originals.values()))
        tp = self.jsonl("targets", list(targets.values()))
        mask_rows = [{"stable_key": side + ":" + token, "target_ref": self.ref(0), side + "_token_id": token,
                      "eligible": token not in {"o00", "t00"}} for side, values in (("original", originals), ("target", targets)) for token in values]
        mp = self.jsonl("mask", mask_rows)
        candidate = self.candidate()
        candidate["generator_score"] = {"raw": {"POISON": "not lexical evidence"}}
        cp = self.jsonl("candidates", [candidate])
        empty = self.jsonl("empty", [])
        gold = self.gold(candidate)
        gold["relation"] = {"POISON": "not inspected before whole-edge exclusion"}
        gp = self.jsonl("gold", [gold])
        lock = {"paths": {"gold_originals": op.name, "targets": tp.name, "mask": mp.name, "annotations": gp.name,
                          "first_party": cp.name, "statistical": empty.name, "contextual": empty.name}}
        ip = self.root / "inputs"
        io.write(ip, lock)
        original_read = core.read
        def test_read(path):
            return {**self.config, "expected_verses": 1} if Path(path).name == "config.v1.json" else original_read(path)
        with patch.object(core, "check_inputs", return_value=lock), patch.object(io, "source_roster", return_value=[]), patch.object(core, "read", side_effect=test_read):
            core.build(self.root, ip, self.root / "build")
        row = next(io.rows(self.root / "build/graph.v1.jsonl"))
        edge = row["edges"][0]
        self.assertTrue(edge["excluded_whole_edge"])
        self.assertIsNone(edge["prior"])
        self.assertIsNone(edge["rank_score"])
        self.assertEqual(row["nbest"][0]["edge_ids"], [])
        self.assertEqual(io.read(self.root / "build/prior.v1.json")["observations"], 0)


if __name__ == "__main__":
    unittest.main()

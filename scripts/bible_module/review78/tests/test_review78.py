import copy
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts.bible_module.consensus76.core import fold, identity
from scripts.bible_module.consensus76.io import digest, spec
from scripts.bible_module.review78.contracts import GUARDS, compile_case, endpoint_delta
from scripts.bible_module.review78.server import Store, handler

REF = next("Gen.1." + str(i) for i in range(1, 50) if fold("Gen.1." + str(i)) in {0, 1, 2})


def edge(eid, original, target, relation="one_to_one", shared=()):
    return {"edge_id": eid, "target_ref": REF, "original_token_ids": original, "target_token_ids": target,
            "relation": relation, "null_reason": None, "excluded_whole_edge": False,
            "provenance": [{"candidate_id": eid, "joint_use_with_candidate_ids": list(shared)}]}


def fixture():
    prediction = edge("p", ["a", "b"], ["x", "y"], "many_to_many")
    other = edge("c", ["a"], ["x"])
    g1, g2 = edge("g1", ["a"], ["x"]), edge("g2", ["b"], ["y"])
    graph = {"target_ref": REF, "original_nodes": [{"token_id": t, "target_ref": REF} for t in ("a", "b", "d")],
             "target_nodes": [{"token_id": t, "target_ref": REF} for t in ("x", "y", "z")],
             "edges": [prediction, other], "nbest": [{"edge_ids": ["p"]}]}
    case = {"case_id": "case", "target_ref": REF, "fold": fold(REF), "source_graph_row_digest": digest(graph),
            "prediction_edge_id": "p", "semantic_identity": identity(prediction), "nearest_gold_edge_ids": ["g1", "g2"],
            "gold_row_digests": {g["edge_id"]: digest(g) for g in (g1, g2)}}
    classification = {**prediction, "exact": False, "final_class": "B_review", "calibration_provenance": {"input_graph_row_sha256": digest(graph)}}
    return case, graph, {g["edge_id"]: g for g in (g1, g2)}, classification


class ReviewContracts(unittest.TestCase):
    def test_ties_and_many_to_many_are_not_flattened_or_merged(self):
        c, g, gold, cl = fixture()
        result = compile_case(c, g, gold, cl)
        self.assertEqual(len(result["gold_comparisons"]), 2)
        self.assertEqual(result["gold_comparisons"][0]["extra_original"], ["b"])
        self.assertEqual(result["gold_comparisons"][1]["extra_original"], ["a"])
        self.assertEqual(result["conflicting_candidate_edge_ids"], ["c"])
        self.assertEqual(result["semantic_identity"], identity(g["edges"][0]))
        self.assertEqual(result["A_auto"], 0)

    def test_missing_and_extra_separate_both_sides(self):
        p = edge("p", ["a", "b"], ["x", "y"], "many_to_many")
        g = edge("g", ["a", "d"], ["x", "z"], "many_to_many")
        d = endpoint_delta(p, g)
        self.assertEqual([d[k] for k in ("missing_original", "extra_original", "missing_target", "extra_target")], [["d"], ["b"], ["z"], ["y"]])

    def test_null_reason_explicit_and_no_invented_null(self):
        p = edge("p", ["a"], ["x"])
        g = {**edge("g", ["a"], [], "original_omitted"), "null_reason": "source_text_not_rendered"}
        d = endpoint_delta(p, g)
        self.assertEqual(d["extra_target"], ["x"])
        self.assertTrue(d["relation_differs"])
        self.assertTrue(d["null_reason_differs"])
        self.assertEqual(p["target_token_ids"], ["x"])

    def test_reciprocal_shared_declaration_is_compatible_not_conflict(self):
        c, graph, gold, cl = fixture()
        prediction = edge("p", ["a"], ["x"], shared=["s"])
        shared = edge("s", ["b"], ["x"], shared=["p"])
        graph["edges"] = [prediction, shared]
        c.update(semantic_identity=identity(prediction), source_graph_row_digest=digest(graph))
        cl.update(prediction);cl["calibration_provenance"]["input_graph_row_sha256"] = digest(graph)
        result = compile_case(c, graph, gold, cl)
        self.assertEqual(result["conflicting_candidate_edge_ids"], [])
        self.assertEqual(result["compatible_shared_candidate_edge_ids"], ["s"])

    def test_stale_graph_gold_and_classification_rejected(self):
        for kind in ("graph", "gold", "classification"):
            c, graph, gold, cl = fixture()
            if kind == "graph": graph["nbest"].append({"edge_ids": []})
            if kind == "gold": gold["g1"]["null_reason"] = "changed"
            if kind == "classification": cl["calibration_provenance"]["input_graph_row_sha256"] = "stale"
            with self.assertRaises(ValueError): compile_case(c, graph, gold, cl)

    def test_deferred_candidate_cannot_be_opened_as_case(self):
        c, graph, gold, cl = fixture()
        graph["edges"][0]["excluded_whole_edge"] = True
        c["source_graph_row_digest"] = digest(graph)
        with self.assertRaises((KeyError, ValueError)): compile_case(c, graph, gold, cl)

    def test_validation_fold_and_A_class_rejected(self):
        c, graph, gold, cl = fixture();cl["final_class"] = "A_auto"
        with self.assertRaises(ValueError): compile_case(c, graph, gold, cl)
        c, graph, gold, cl = fixture();c["fold"] = 4
        with self.assertRaises(ValueError): compile_case(c, graph, gold, cl)


class ServerContracts(unittest.TestCase):
    def test_hot_manifest_and_index_mutation_rejected(self):
        from scripts.bible_module.consensus76.io import sha
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.json";manifest.write_text('{}', encoding="utf8")
            index = root / "index.json";index.write_text('{}', encoding="utf8")
            store = object.__new__(Store);store.directory = root;store.manifest_path = manifest
            store.manifest_sha256 = sha(manifest);store.manifest = {"index": {**spec(index), "path": "index.json"}}
            store.verify_snapshot()
            index.write_text('{"changed":true}', encoding="utf8")
            with self.assertRaises(ValueError): store.verify_snapshot()
            index.write_text('{}', encoding="utf8");manifest.write_text('{"new":true}', encoding="utf8")
            with self.assertRaises(ValueError): store.verify_snapshot()

    def test_local_packet_tampering_and_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            packet = directory / "p.json";packet.write_text('{}', encoding="utf8")
            store = object.__new__(Store);store.directory = directory
            item = {**spec(packet), "path": "p.json"}
            self.assertEqual(store.verify_local(item), packet)
            packet.write_text('{"changed":true}', encoding="utf8")
            with self.assertRaises(ValueError): store.verify_local(item)
            with self.assertRaises(ValueError): store.verify_local({**item, "path": "../outside"})

    def test_HTTP_is_GET_only_and_never_serves_arbitrary_files(self):
        class FakeStore:
            index = {"cases": [], **GUARDS}
            def verify_snapshot(self): pass
            def case(self, key):
                if key == "stale": raise ValueError("changed")
                raise KeyError(key)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler(FakeStore()))
        worker = threading.Thread(target=server.serve_forever, daemon=True);worker.start()
        url = "http://127.0.0.1:" + str(server.server_port)
        try:
            with urlopen(url + "/api/index") as response:
                self.assertEqual(json.load(response)["A_auto"], 0)
                self.assertIn("script-src 'self'", response.headers["Content-Security-Policy"])
            for path, method, expected in (("/api/case?id=unknown", "GET", 404), ("/api/case?id=stale", "GET", 409), ("/../api-keys.json", "GET", 404), ("/api/case", "POST", 405), ("/api/index", "DELETE", 405)):
                with self.assertRaises(HTTPError) as error: urlopen(Request(url + path, method=method))
                self.assertEqual(error.exception.code, expected)
        finally:
            server.shutdown();server.server_close();worker.join()


if __name__ == "__main__":
    unittest.main()

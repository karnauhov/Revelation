import itertools
import math
import unittest

from scripts.bible_module.precision78.analysis import Components, difference, eligible
from scripts.bible_module.precision78.statistics import (
    hypergeom_cdf_errors, hypergeom_precision_lower, hypergeom_zero_error_requirement, iid_wilson_power,
    required_support, wilson_lower,
)


def edge(o, t, relation="one_to_one", reason=None, eid="g"):
    return {"edge_id": eid, "original_token_ids": o, "target_token_ids": t,
            "relation": relation, "null_reason": reason}


class Precision78Tests(unittest.TestCase):
    def test_wilson_boundary_minima(self):
        for errors, alpha, expected in ((0, .05, 539), (1, .05, 894), (0, .05/342, 2611)):
            self.assertEqual(required_support(errors, alpha), expected)
            self.assertLess(wilson_lower(expected-1-errors, expected-1, alpha), .995)
            self.assertGreaterEqual(wilson_lower(expected-errors, expected, alpha), .995)
        self.assertIsNone(wilson_lower(0, 0))

    def test_invalid_statistics(self):
        for args in ((-1, 2), (3, 2), (True, 2)):
            with self.assertRaises(ValueError):
                wilson_lower(*args)
        with self.assertRaises(ValueError):
            hypergeom_precision_lower(10, 11, 0)

    def test_hypergeometric_exhaustive_sample_enumeration(self):
        for N in range(1, 8):
            for D in range(N+1):
                for n in range(N+1):
                    totals = [sum(i < D for i in sample) for sample in itertools.combinations(range(N), n)]
                    for e in range(n+1):
                        expected = sum(x <= e for x in totals) / len(totals)
                        self.assertAlmostEqual(hypergeom_cdf_errors(N, D, n, e), expected)

    def test_exact_bound_coverage_all_small_finite_populations(self):
        for N in range(1, 13):
            for D in range(N+1):
                for n in range(1, N+1):
                    miss = 0.
                    for e in range(n+1):
                        probability = hypergeom_cdf_errors(N, D, n, e)-hypergeom_cdf_errors(N, D, n, e-1)
                        if hypergeom_precision_lower(N, n, e) > (N-D)/N + 1e-12:
                            miss += probability
                    self.assertLessEqual(miss, .05+1e-12)

    def test_census_and_empty_sample(self):
        self.assertEqual(hypergeom_precision_lower(100, 100, 0), 1)
        self.assertEqual(hypergeom_precision_lower(100, 100, 3), .97)
        self.assertEqual(hypergeom_precision_lower(100, 0, 0), 0)
        self.assertAlmostEqual(iid_wilson_power(539)["iid_power"], .999**539)

    def test_finite_population_zero_error_requirement_boundary(self):
        self.assertIsNone(hypergeom_zero_error_requirement(0))
        for N in (1, 10, 100, 200, 400, 1000, 10000):
            for alpha in (.05, .05/342):
                n = hypergeom_zero_error_requirement(N, alpha)
                self.assertGreaterEqual(hypergeom_precision_lower(N, n, 0, alpha), .995)
                self.assertLess(hypergeom_precision_lower(N, n-1, 0, alpha), .995)

    def test_multimember_identity_not_flattened(self):
        result = difference(edge(["a"], ["x"]), [edge(["a", "b"], ["x", "y"])])
        self.assertEqual(result["structural"], ["incomplete_group"])
        result = difference(edge(["a", "b", "c"], ["x", "y"]), [edge(["a", "b"], ["x", "y"])])
        self.assertEqual(result["structural"], ["extra_participant"])

    def test_relation_and_null_semantics(self):
        result = difference(edge(["a"], [], "original_omitted", "bad"), [edge(["a"], [], "original_omitted", "explicit")])
        self.assertEqual(result["structural"], ["relation_null_semantics"])
        result = difference(edge(["a"], ["y"]), [edge(["a"], ["x"])])
        self.assertEqual(result["structural"], ["extra_participant", "incomplete_group", "wrong_endpoints"])

    def test_tied_shared_declarations_retained(self):
        result = difference(edge(["a", "b"], ["x"]), [edge(["a"], ["x"], eid="g1"), edge(["b"], ["x"], eid="g2")])
        self.assertEqual(result["nearest_gold_edge_ids"], ["g1", "g2"])
        self.assertEqual(result["ties"], 2)

    def test_mask_before_semantics_and_unknown_is_not_null(self):
        self.assertFalse(eligible(edge(["deferred"], ["x"]), {("original", "deferred"): False}))
        self.assertTrue(eligible(edge(["unreviewed"], ["x"]), {}))

    def test_components_transitive_and_domain_induced(self):
        c = Components()
        for keys in (("verse1", "lemmaA"), ("verse2", "lemmaB"), ("lemmaA", "lemmaB"), ("other",)):
            c.add(keys)
        self.assertEqual(c.count(), 2)
        self.assertEqual(Components().count(), 0)


if __name__ == "__main__":
    unittest.main()

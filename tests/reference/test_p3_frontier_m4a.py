"""Independent literal and resource checks for the M4-A prototype."""
from fractions import Fraction
from itertools import combinations, product
from unittest import TestCase
from unittest.mock import patch

from p3_frontier_verifier import Budget, Incomplete, Invalid, sparse_compatible, verify_frontier
from test_p3_frontier_verifier import certificate, fixture
from p3_rank_cost import Deletion, Packing, closes, rank_cost
from rgs_oracle import compatible, rgs


def owners(n):
    for labels in rgs(n):
        yield tuple(labels.index(label) for label in labels)


def words(text):
    return tuple(tuple(ord(c) - ord("a") for c in w) for w in text.split())


class SparseExact(TestCase):
    def test_exhaustive_literal_parity(self):
        for n in range(4):
            traces = [w for k in range(3) for w in product(range(n), repeat=k)]
            # Sort the two-trace multisamples, retaining duplicates.
            samples = [()] + [(w,) for w in traces]
            samples += [(x, y) for i, x in enumerate(traces) for y in traces[i:]]
            for p, x, y in product(owners(n), samples, samples):
                self.assertEqual(sparse_compatible(p, x, y, Budget()),
                                 compatible(p, x, y), (p, x, y))

    def test_forced_hash_collisions(self):
        p = (0, 0)
        with patch("p3_frontier_verifier.hash", return_value=0, create=True):
            self.assertTrue(sparse_compatible(p, words("ab aa"), words("ba"), Budget()))
            self.assertFalse(sparse_compatible(p, words("ab aa"), words("aa"), Budget()))

    def test_wire_binding_and_incomplete_envelope(self):
        raw = dict(alphabet=["a", "b"], positive=[["a"]], negative=[["b"]])
        journal, scope = fixture(raw)
        for mode in ("one", "all"):
            cert = certificate(raw, scope, mode)
            for version in ("v1", "v2"):
                fmt = "p3-region-frontier/" + version
                cert["format"] = fmt

                def verify(**overrides):
                    options = dict(sparse_exact=True, expected_format=fmt, expected_mode=mode)
                    return verify_frontier(raw, journal, scope, cert, **(options | overrides))

                self.assertEqual(verify()["status"], "VERIFIED")
                self.assertEqual(verify(expected_mode="one" if mode == "all" else "all")["status"],
                                 "INVALID")
                other = "v1" if version == "v2" else "v2"
                self.assertEqual(verify(expected_format="p3-region-frontier/" + other)["status"],
                                 "INVALID")
                capped = verify(max_exact_checks=0)
                self.assertEqual(capped["status"], "INCOMPLETE")
                self.assertNotIn("result", capped)

    def test_large_sparse_and_caps(self):
        p = tuple(range(250_000))
        x = ((0, 1, 0),) * 1000
        y = ((1,),) * 1000
        b = Budget(max_work=30_000, max_entries=32, max_exact_checks=2000)
        self.assertTrue(sparse_compatible(p, x, y, b))
        self.assertEqual(b.exact, 2000)
        self.assertFalse(sparse_compatible(p, x, x, Budget(max_work=30_000)))
        self.assertFalse(sparse_compatible(p, x + ((),), y, Budget(max_work=30_000)))
        for cap in (dict(max_work=10), dict(max_entries=2),
                    dict(max_exact_checks=1), dict(seconds=0)):
            with self.assertRaises(Incomplete):
                sparse_compatible(p, x, y, Budget(**cap))

        word = tuple(range(40_000))
        self.assertFalse(sparse_compatible(p, (word,), (word,),
                                           Budget(max_work=1_000_000)))
        with self.assertRaises(Incomplete):
            sparse_compatible(p, (word,), (word,), Budget(max_entries=79_999))


class RankCost(TestCase):
    def check_literal(self, owner, x, y, packing, weights):
        base, local, bound = result = rank_cost(owner, x, y, packing, weights)
        compatible_costs = []
        for p in owners(len(owner)):
            if all(p[i] == p[rep] for i, rep in enumerate(owner)) and compatible(p, x, y):
                cost = len(p) - len(set(p))
                compatible_costs.append(cost)
                self.assertGreaterEqual(cost, bound)
                for support, floor in local:
                    self.assertGreaterEqual(len(support) - len({p[v] for v in support}), floor)
        self.assertTrue(compatible_costs)
        return result, min(compatible_costs)

    def test_triangle_fractional_overlap(self):
        p = tuple(range(6))
        x, y = words("abcdef"), words("badcef abdcfe bacdfe")
        packing = tuple(Packing(i, (Deletion(0, a), Deletion(0, b)))
                        for i, (a, b) in enumerate((
                            ((0, 2), (1, 3)), ((2, 4), (3, 5)), ((0, 4), (1, 5)))))
        (_, local, bound), optimum = self.check_literal(p, x, y, packing, (Fraction(1, 2),) * 3)
        self.assertEqual([floor for _, floor in local], [1, 1, 1])
        self.assertEqual((bound, optimum), (2, 2))
        with self.assertRaisesRegex(Invalid, "overloaded"):
            rank_cost(p, x, y, packing, (Fraction(1),) * 3)

    def test_quotient_distinct_witnesses_and_cutoffs(self):
        p = (0, 0, 2, 3)
        x, y = words("acd adc"), words("bcd")
        # Distinct positives are essential in this case.
        proof = Packing(0, (Deletion(0, (1,)), Deletion(1, (0, 2))))
        with self.assertRaisesRegex(Invalid, "overlapping"):
            rank_cost(p, x, y, (proof,), (Fraction(1),))
        x, y = words("bcd ac"), words("acd")
        proof = Packing(0, (Deletion(0, (1,)), Deletion(1, (3,))))
        (base, local, bound), optimum = self.check_literal(p, x, y, (proof,), (Fraction(1),))
        self.assertEqual((base, local, bound, optimum),
                         (1, ((frozenset({0, 3}), 1),), 2, 2))
        self.assertTrue(closes("one", bound, optimum))
        self.assertFalse(closes("all", bound, optimum))
        self.assertTrue(closes("all", bound + 1, optimum))
        self.assertFalse(closes("one", bound - 1, optimum))
        self.assertFalse(closes("one", bound, None))
        self.assertFalse(closes("all", bound, None))

    def test_double_count_and_truncated_or_cross_negative_evidence(self):
        p = (0, 1, 2)
        x, y = words("abc"), words("bac bac")
        rows = tuple(Packing(i, (Deletion(0, (0,)), Deletion(0, (1,)))) for i in range(2))
        (_, _, bound), optimum = self.check_literal(p, x, y, rows, (Fraction(1, 2),) * 2)
        self.assertEqual((bound, optimum), (1, 1))
        with self.assertRaisesRegex(Invalid, "overloaded"):
            rank_cost(p, x, y, rows, (Fraction(1),) * 2)
        malformed = Packing(0, (Deletion(0, (0,)), Deletion(0, (2,))))
        for negatives in (words("bac acb"), words("cba")):
            with self.assertRaisesRegex(Invalid, "false ordered"):
                rank_cost(p, x, negatives, (malformed,), (Fraction(1),))
        for weight in (0.5, Fraction(-1, 2), Fraction(1, 2**32)):
            with self.assertRaisesRegex(Invalid, "weight"):
                rank_cost(p, x, y, rows[:1], (weight,))
        with self.assertRaises(Incomplete):
            rank_cost(p, x, y, rows[:1], (Fraction(1),), Budget(max_exact_checks=1))

    def test_exhaustive_trace_realizable_local_floors(self):
        n = 3
        traces = [w for k in range(3) for w in product(range(n), repeat=k)]
        proofs = 0
        for p, x, y in product(owners(n), traces, traces):
            atoms = sorted(set(p))
            supports = [s for k in range(1, len(atoms) + 1) for s in combinations(atoms, k)
                        if tuple(a for a in x if p[a] not in s) ==
                        tuple(a for a in y if p[a] not in s)]
            for a, b in combinations(supports, 2):
                if x == y or set(a).intersection(b):
                    continue
                packing = Packing(0, (Deletion(0, a), Deletion(0, b)))
                self.check_literal(p, (x,), (y,), (packing,), (Fraction(1),))
                proofs += 1
        self.assertGreater(proofs, 0)

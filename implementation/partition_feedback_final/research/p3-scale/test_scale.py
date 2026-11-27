"""Literal controls for the isolated scale paths."""
from collections import defaultdict
from itertools import product
import unittest
from unittest.mock import patch

from selector_v2.core import Sample
from selector_v2.edr_bb import SearchBudget, SearchCaps, SearchCapExceeded
from selector_v2.edr_cross import discover
from selector_v2.edr_sparse import discover_join
from selector_v2.scale_projections import CompactProjections
from selector_v2.scale_witness import TargetedDiscovery


def literal_fail(sample, owner):
    for i, y in enumerate(sample.negative):
        if all(any(tuple(a for a in x if owner[a] == g) ==
                   tuple(a for a in y if owner[a] == g) for x in sample.positive)
               for g in set(owner)):
            return i
    return None


def verify_witness(test, sample, owner, witness):
    test.assertIsNotNone(witness)
    i = int(witness["negative_id"][1:])
    y = sample.negative[i]
    test.assertFalse(set(witness["support_s"]) & set(witness["support_t"]))
    for side in ("s", "t"):
        x = sample.positive[int(witness[f"positive_{side}_id"][1:])]
        deleted = witness[f"support_{side}"]
        test.assertEqual(tuple(a for a in x if owner[a] not in deleted),
                         tuple(a for a in y if owner[a] not in deleted))


class ScaleTests(unittest.TestCase):
    def test_literal_parity(self):
        words = [()] + [(a,) for a in range(3)] + list(product(range(3), repeat=2))
        for x, y in product(words, repeat=2):
            sample = Sample(("a", "b", "c"), (x, x, (0, 0, 1)), (y, y, (1, 0, 0)))
            counters = {}
            index = CompactProjections(sample)
            for owner in ((0, 1, 2), (0, 0, 2), (0, 1, 0), (0, 1, 1), (0, 0, 0)):
                expected = literal_fail(sample, owner)
                observed = index.check(owner, SearchBudget(), counters)
                self.assertEqual(observed.negative_id, expected)
                self.assertEqual(observed.compatible, expected is None)
            self.assertEqual(counters["singleton_builds"], 1)

    def test_empty_classes_and_alphabet(self):
        for alphabet, owner in (((), ()), (("a",), (0,))):
            for pos, neg in product(((), ((),)), repeat=2):
                sample = Sample(alphabet, pos, neg)
                result = CompactProjections(sample).check(owner, SearchBudget(), {})
                self.assertEqual(result.negative_id, literal_fail(sample, owner))

    def test_witness_reuse_and_scope(self):
        sample = Sample(("a", "b", "c"), ((0,), (1,)), ((2,), (0, 1)))
        index = CompactProjections(sample)
        target = TargetedDiscovery(sample)
        counters = {}
        for owner in ((0, 1, 2), (0, 1, 0), (0, 0, 0)):
            failed = index.check(owner, SearchBudget(), counters)
            if failed.compatible:
                continue
            self.assertEqual(failed.negative_id, literal_fail(sample, owner))
            witness = target.find(failed, SearchBudget(), counters)
            if owner != (0, 0, 0):
                verify_witness(self, sample, owner, witness)
                self.assertEqual(witness["negative_id"], "N1")
            else:
                self.assertIsNone(witness)
        self.assertGreater(counters["target_fact_rechecks"], 0)
        other = Sample(sample.alphabet, sample.positive, sample.negative)
        with self.assertRaises(ValueError):
            TargetedDiscovery(other).find(failed, SearchBudget(), {})

    def test_caps_and_fallback(self):
        sample = Sample(("a", "b"), ((0,), (1,)), ((0, 1),))
        owner = (0, 1)
        for index, caps in ((CompactProjections(sample, 1), SearchCaps()),
                            (CompactProjections(sample), SearchCaps(work=2))):
            with self.assertRaises(SearchCapExceeded):
                index.check(owner, SearchBudget(caps), {})
            self.assertIsNone(index._singleton)
        failed = CompactProjections(sample).check(owner, SearchBudget(), {})
        counters = defaultdict(int)
        target = TargetedDiscovery(sample, work_limit=0, fact_limit=0)
        self.assertEqual(target.discover(failed, SearchBudget(), counters),
                         discover(owner, sample, SearchBudget(), defaultdict(int)))
        self.assertEqual(counters["target_local_caps"], 1)
        with self.assertRaises(SearchCapExceeded):
            TargetedDiscovery(sample).find(failed, SearchBudget(SearchCaps(work=0)), {})

    def test_join_collision_control(self):
        from selector_v2 import edr_sparse

        original = edr_sparse._signatures

        def collide(word, owner, charge):
            full, deleted = original(word, owner, charge)
            return (full[0], 0), {group: (key[0], 0) for group, key in deleted.items()}

        owner = (0, 1, 2)
        with patch.object(edr_sparse, "_signatures", collide):
            for positives, expected in ((((0,), (2,)), False), (((0,), (1,)), True)):
                sample = Sample(("a", "b", "c"), positives, ((0, 1),))
                result = discover_join(owner, sample, SearchBudget(), defaultdict(int), 5000, 65536)
                self.assertEqual(result is not None, expected)
                if expected:
                    verify_witness(self, sample, owner, result)

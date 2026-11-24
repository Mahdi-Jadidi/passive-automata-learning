import itertools
import random
import tracemalloc
import unittest
from dataclasses import replace
from selector_v2.core import Budget, PartitionRef, Sample, SymbolDSU
from selector_v2.sparse_analysis import discover_deletions, raw_check, singleton_check, singleton_forest


def literal(word, block):
    return tuple(a for a in word if a in block)


def compatible(sample, part):
    return all(any(all(literal(y, b) != literal(x, b) for x in sample.positive)
                   for b in part.blocks()) for y in sample.negative)


def obligations(sample, part):
    return {(i, g) for i, y in enumerate(sample.negative) for g in set(part.owner)
            if any(tuple(a for a in x if part.owner[a] != g) ==
                   tuple(a for a in y if part.owner[a] != g) for x in sample.positive)}


def partitions(n):
    def visit(owner):
        if len(owner) == n:
            yield PartitionRef(tuple(owner))
        else:
            for g in sorted(set(owner)) + [len(owner)]:
                yield from visit(owner + [g])
    return visit([])


class SparseTests(unittest.TestCase):
    def test_ids_and_validation(self):
        s = Sample.from_input({'alphabet': ['b', 'a', 'unused'], 'positive': [['a', 'a'], ['a', 'a']], 'negative': [['b']]})
        self.assertEqual(s.positive, ((1, 1), (1, 1)))
        self.assertEqual(s.sample_digest, Sample(s.alphabet, s.positive, s.negative).sample_digest)
        with self.assertRaises(ValueError):
            PartitionRef((0, 2, 2))
        with self.assertRaises(ValueError):
            Sample(('a',), ((True,),), ())
        d = SymbolDSU(4)
        self.assertTrue(d.union(3, 2))
        self.assertTrue(d.union(1, 3))
        self.assertFalse(d.union(1, 2))
        self.assertEqual(d.snapshot().owner, (0, 1, 1, 1))

    def test_degenerate_and_duplicates(self):
        for s in (Sample((), (), ((),)), Sample((), (), ()), Sample(('a',), (), ((),)),
                  Sample(('a',), ((0,),), ((),)), Sample(('a',), ((),), ((0,),))):
            p = PartitionRef.singletons(len(s.alphabet))
            self.assertEqual(raw_check(s, p).compatible, compatible(s, p))
            self.assertEqual(singleton_check(s).compatible, compatible(s, p))
        s = Sample(('a', 'b'), ((0,), (0,)), ((0,), (1,)))
        r = discover_deletions(s, PartitionRef.singletons(2))
        self.assertEqual(r.label_conflict, (0, 0))
        self.assertFalse(r.exhausted)

    def test_exhaustive_ordered_pairs_and_collisions(self):
        words = [w for k in range(4) for w in itertools.product(range(3), repeat=k)]
        for x in words:
            for y in words:
                if x == y:
                    continue
                s = Sample(('a', 'b', 'c'), (x,), (y,))
                for p in (PartitionRef((0, 1, 2)), PartitionRef((0, 0, 2))):
                    r = discover_deletions(s, p, hash_bits=0)
                    self.assertTrue(r.exhausted)
                    self.assertEqual({(f.negative, f.group) for f in r.facts}, obligations(s, p))
                    self.assertEqual(raw_check(s, p).compatible, compatible(s, p))

    def test_random_corpora_and_root_soundness(self):
        rng = random.Random(921)
        words = [w for k in range(4) for w in itertools.product(range(3), repeat=k)]
        for _ in range(250):
            xs = tuple(rng.choices(words, k=4))
            ys = tuple(rng.choices([w for w in words if w not in xs], k=4))
            s = Sample(('a', 'b', 'c'), xs, ys)
            p = PartitionRef.singletons(3)
            r = discover_deletions(s, p, hash_bits=1)
            self.assertEqual({(f.negative, f.group) for f in r.facts}, obligations(s, p))
            root, edges = singleton_forest(s, r)
            self.assertEqual(root.cost, len(edges))
            for q in partitions(3):
                self.assertEqual(raw_check(s, q).compatible, compatible(s, q))
                if compatible(s, q):
                    self.assertGreaterEqual(q.cost, root.cost)
                    for e in edges:
                        self.assertEqual(q.owner[e.a], q.owner[e.b])
            self.assertEqual(singleton_check(s).compatible, compatible(s, p))

    def test_budget_and_mutation(self):
        s = Sample(('a', 'b', 'c'), ((0,), (1,)), ((0, 1), (0, 1)))
        p = PartitionRef.singletons(3)
        full = discover_deletions(s, p)
        self.assertEqual({(f.negative, f.group) for f in full.facts}, {(0, 0), (0, 1), (1, 0), (1, 1)})
        for cap in range(45):
            r = discover_deletions(s, p, Budget(work=cap))
            self.assertTrue(set(r.facts) <= set(full.facts))
            self.assertEqual(r.cursor is None, r.exhausted)
            singleton_forest(s, r)
        self.assertFalse(discover_deletions(s, p, Budget(seconds=0)).exhausted)
        bad = replace(full, facts=(replace(full.facts[0], group=2),))
        with self.assertRaises(ValueError):
            singleton_forest(s, bad)

    def test_100k_sparse(self):
        tracemalloc.start()
        try:
            n = 100000
            s = Sample(tuple(map(str, range(n))), tuple((2*i, 2*i+1) for i in range(1000)),
                       tuple((2*i+1, 2*i) for i in range(1000)))
            p = PartitionRef.singletons(n)
            r = discover_deletions(s, p)
            root, edges = singleton_forest(s, r)
            self.assertEqual(len(edges), 1000)
            self.assertTrue(raw_check(s, root).compatible)
            _, peak = tracemalloc.get_traced_memory()
            self.assertLess(peak, 80 * 1024**2)
            print('100k peak traced bytes:', peak)
        finally:
            tracemalloc.stop()


if __name__ == '__main__':
    unittest.main()

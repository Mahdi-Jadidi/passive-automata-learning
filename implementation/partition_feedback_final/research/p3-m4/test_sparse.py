from itertools import product
from types import SimpleNamespace
import unittest

from selector_v2.edr_bb import SearchBudget, SearchCaps, SearchCapExceeded
from selector_v2.edr_sparse import DEFAULT_INDEX_BYTES, discover_join, sparse_compatible


def literal(owner, positives, negatives):
    def projection(word, group):
        return tuple(token for token in word if owner[token] == group)

    return all(any(all(projection(y, group) != projection(x, group) for x in positives)
                   for group in set(owner)) for y in negatives)


class SparseTests(unittest.TestCase):
    def test_literal_parity(self):
        for owner in ((), (0,), (0, 1), (0, 0), (0, 1, 2), (0, 1, 0), (0, 0, 0)):
            words = [word for length in range(3)
                     for word in product(range(len(owner)), repeat=length)]
            samples = [(), *((word,) for word in words), *product(words, repeat=2)]
            for positives, negatives in product(samples, repeat=2):
                value = sparse_compatible(owner, positives, negatives, SearchBudget(),
                                          DEFAULT_INDEX_BYTES, {})
                self.assertEqual(value, literal(owner, positives, negatives),
                                 (owner, positives, negatives))

    def test_caps_do_not_return_an_exact_answer(self):
        args = ((0, 1), ((0,),), ((1,),))
        for caps, index_bytes, expected in (
            (SearchCaps(work=1), DEFAULT_INDEX_BYTES, "work"),
            (SearchCaps(seconds=0), DEFAULT_INDEX_BYTES, "seconds"),
            (SearchCaps(), 0, "memory_bytes"),
        ):
            with self.subTest(cap=expected), self.assertRaises(SearchCapExceeded) as stopped:
                sparse_compatible(*args, SearchBudget(caps), index_bytes, {})
            self.assertEqual(stopped.exception.cap, expected)

    def test_singleton_join_vs_literal(self):
        for owner in ((0, 1, 2), (0, 0, 2), (0, 1, 0)):
            words = [word for n in range(3) for word in product(range(3), repeat=n)]
            for x1, x2, y in product(words, repeat=3):
                if y in (x1, x2):
                    continue
                sample = SimpleNamespace(positive=(x1, x2), negative=(y,))

                def drop(word, group):
                    return tuple(token for token in word if owner[token] != group)

                expected = {g for g in set(owner) if any(drop(x, g) == drop(y, g)
                                                        for x in sample.positive)}
                result = discover_join(owner, sample, SearchBudget(),
                                       dict(join_work=0, join_probes=0, join_local_caps=0),
                                       1000, DEFAULT_INDEX_BYTES)
                self.assertEqual(result is not None, len(expected) >= 2)
                if result:
                    self.assertEqual(result["negative_id"], "N0")
                    s, t = result["support_s"][0], result["support_t"][0]
                    self.assertLess(s, t)
                    for group, name in ((s, "positive_s_id"), (t, "positive_t_id")):
                        word = sample.positive[int(result[name][1:])]
                        self.assertEqual(drop(word, group), drop(y, group))

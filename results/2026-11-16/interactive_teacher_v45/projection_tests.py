"""Independent projection-oracle and DAG cache regression tests."""
import itertools
import unittest

from projections import ProjectionStore


def oracle(sigma, positives, negatives, mask):
    keep = {s for i, s in enumerate(sigma) if mask & (1 << i)}
    project = lambda w: tuple(s for s in w if s in keep)
    pos = [project(w) for w in positives]
    neg = [project(w) for w in negatives]
    first = {}
    for i, word in enumerate(pos):
        first.setdefault(word, i)
    rejection = sum(1 << i for i, word in enumerate(neg) if word not in first)
    return {"positive": pos, "negative": neg, "rejection_mask": rejection,
            "positive_witness": first}


class ProjectionTests(unittest.TestCase):
    def check_case(self, sigma, pos, neg):
        masks = list(range(1 << len(sigma)))
        # Different request orders exercise arbitrary cached supersets.
        for order in (masks, list(reversed(masks)), masks[::2] + masks[1::2]):
            calls = [0]
            def tick():
                calls[0] += 1
            store = ProjectionStore(sigma, pos, neg, tick)
            for mask in order:
                self.assertEqual(store.entry(mask), oracle(sigma, pos, neg, mask))
                before = store.stats["transformed_nodes"]
                store.entry(mask)
                self.assertEqual(store.stats["transformed_nodes"], before)
            self.assertGreater(calls[0], 0)
            print("projection stats", store.stats)

    def test_varied_samples(self):
        self.check_case(("a", "β", "🐈"),
                        [(), ("a",), ("a", "β"), ("a",), ("🐈", "β")],
                        [(), ("β",), ("a", "β", "🐈"), ("β",)])
        self.check_case((), [], [(), ()])
        self.check_case(("x", "y"), [], [("x",), ("y",)])
        self.check_case(("x", "y"), [("x",), ()], [])

    def test_long_trace(self):
        word = tuple(itertools.islice(itertools.cycle(("x", "y")), 5000))
        self.check_case(("x", "y"), [word, word[:-1]], [word, word[1:]])

    def test_tie_break_and_validation(self):
        store = ProjectionStore(("a", "b", "c"), [("a", "b", "c")], [], lambda: None)
        store.entry(6)
        store.entry(5)
        # For mask 4, equal-size supersets 5 and 6 both exist; 5 is selected.
        before = store.stats["transformed_nodes"]
        store.entry(4)
        self.assertEqual(store.stats["transformed_nodes"] - before, 2)
        with self.assertRaises(ValueError):
            store.entry(8)


if __name__ == "__main__":
    unittest.main()

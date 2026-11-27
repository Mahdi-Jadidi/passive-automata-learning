"""Finite literal checks for the proposed rule, isolated from both engines."""
import itertools
import unittest


def partitions(n):
    def extend(prefix):
        if len(prefix) == n:
            yield prefix
        else:
            for label in range(max(prefix, default=-1) + 2):
                yield from extend(prefix + (label,))
    return extend(())


def project(word, block):
    return tuple(a for a in word if a in block)


def feasible(p, positives, negatives):
    blocks = [{a for a, label in enumerate(p) if label == g} for g in set(p)]
    return all(any(all(project(y, block) != project(x, block) for x in positives)
                   for block in blocks) for y in negatives)


def cross_pairs(left, right):
    return sorted(tuple(sorted(pair)) for pair in itertools.product(left, right))


class CrossSupportTests(unittest.TestCase):
    def check_split(self, n, e, disequalities, left, right, x_s, x_t, y):
        left_symbols = {a for a in range(n) if e[a] in left}
        right_symbols = {a for a in range(n) if e[a] in right}
        universe = set(range(n))
        self.assertEqual(project(x_s, universe - left_symbols),
                         project(y, universe - left_symbols))
        self.assertEqual(project(x_t, universe - right_symbols),
                         project(y, universe - right_symbols))
        pairs = cross_pairs(left, right)
        self.assertEqual(len(pairs), len(left) * len(right))
        for p in partitions(n):
            if any(p[a] != p[e[a]] for a in range(n)):
                continue
            if any(p[a] == p[b] for a, b in disequalities):
                continue
            truths = [p[a] == p[b] for a, b in pairs]
            children = sum(truth and not any(truths[:j])
                           for j, truth in enumerate(truths))
            residual = not any(truths)
            self.assertEqual(children + residual, 1)
            if residual:
                self.assertFalse(feasible(p, [x_s, x_t], [y]))

    def test_all_disjoint_supports_through_n6(self):
        for n in range(2, 7):
            for membership in itertools.product(range(3), repeat=n):
                left = tuple(a for a, side in enumerate(membership) if side == 1)
                right = tuple(a for a, side in enumerate(membership) if side == 2)
                if left and right:
                    self.check_split(n, tuple(range(n)), (), left, right, left, right, ())

    def test_nonidentity_root_and_branch_disequalities(self):
        self.check_split(8, (0, 0, 2, 3, 3, 5, 6, 7), ((0, 3), (5, 7)),
                         (0, 6), (2, 3), (5, 0, 1, 1, 2), (5, 3, 4, 2, 2), (5, 2))

    def test_truncated_support_and_incomplete_families(self):
        positives = [(0, 1), (2,)]
        negatives = [()]
        p = (0, 1, 1)
        self.assertTrue(feasible(p, positives, negatives))
        self.assertNotEqual(project(positives[0], {1, 2}), ())
        self.assertFalse(any(p[a] == p[b] for a, b in [(0, 2)]))
        self.assertTrue(any(p[a] == p[b] for a, b in cross_pairs((0, 1), (2,))))
        ab = (0, 0, 1)
        self.assertFalse(any(ab[a] == ab[b] for a, b in cross_pairs((0, 1), (2,))))
        self.assertFalse(feasible(ab, positives, negatives))

    def test_different_negatives_can_use_different_blocks(self):
        self.assertTrue(feasible((0, 1), [()], [(0,), (1,)]))

    def test_local_ranks_share_a_merge(self):
        positive = (0, 0, 1, 2)
        negatives = [(0, 1, 0, 2), (1, 0, 0, 2)]
        for negative in negatives:
            for symbol in (0, 1):
                complement = set(range(3)) - {symbol}
                self.assertEqual(project(positive, complement), project(negative, complement))
        self.assertFalse(feasible(tuple(range(3)), [positive], negatives))
        self.assertTrue(feasible((0, 0, 1), [positive], negatives))

    def test_cross_prefix_cannot_use_all_pairs_threshold(self):
        p = (0, 1, 0, 1)
        pairs = cross_pairs((1,), (3,))
        self.assertEqual(pairs, [(1, 3)])
        self.assertEqual(p[1], p[3])
        self.assertEqual(p[0], p[2])
        self.assertLess((0, 2), pairs[0])


    def test_mixed_path_prefix_uses_original_endpoint_ids(self):
        for p in partitions(5):
            left = (1, 2)
            right = (0, 3, 4)
            ordered = cross_pairs(left, right)
            minima = []
            for label in set(p):
                s = [a for a in left if p[a] == label]
                t = [b for b in right if p[b] == label]
                if s and t:
                    minima.append(tuple(sorted((min(s), min(t)))))
            for end in range(len(ordered) + 1):
                explicit = any(p[a] == p[b] for a, b in ordered[:end])
                symbolic = bool(minima) if end == len(ordered) else any(
                    pair < ordered[end] for pair in minima)
                self.assertEqual(explicit, symbolic)

if __name__ == "__main__":
    unittest.main()

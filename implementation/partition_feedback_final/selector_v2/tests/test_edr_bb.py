import itertools
import unittest

from selector_v2.edr_bb import (
    RegionState,
    RollbackDSU,
    SearchBudget,
    SearchCapExceeded,
    SearchCaps,
    first_true_split,
    generic_fallback_alternatives,
    generic_fallback_split,
    should_prune,
)


def rgs(n):
    if n == 0:
        yield ()
        return
    labels = [0]
    def visit(max_label):
        if len(labels) == n:
            yield tuple(labels)
            return
        for label in range(max_label + 2):
            labels.append(label)
            yield from visit(max(max_label, label))
            labels.pop()
    yield from visit(0)


def owner_from_rgs(labels):
    minima = {}
    for symbol, label in enumerate(labels):
        minima.setdefault(label, symbol)
    return tuple(minima[label] for label in labels)


def partitions(n):
    return tuple(owner_from_rgs(labels) for labels in rgs(n))


def class_pairs(owner):
    classes = sorted(set(owner))
    return tuple(itertools.combinations(classes, 2))


class RollbackDSUTests(unittest.TestCase):
    def test_no_path_compression_and_nested_rollback(self):
        dsu = RollbackDSU(8)
        self.assertTrue(dsu.union(0, 1))
        self.assertTrue(dsu.union(2, 3))
        self.assertTrue(dsu.union(0, 2))
        self.assertTrue(dsu.union(4, 5))
        self.assertTrue(dsu.union(6, 7))
        marker = dsu.mark()
        self.assertTrue(dsu.union(4, 6))
        self.assertTrue(dsu.union(0, 4))
        before_find = tuple(dsu.parent)
        self.assertEqual(dsu.find(7), dsu.find(0))
        self.assertEqual(tuple(dsu.parent), before_find)
        self.assertEqual(dsu.snapshot(), (0, 0, 0, 0, 0, 0, 0, 0))
        dsu.rollback(marker)
        self.assertEqual(dsu.snapshot(), (0, 0, 0, 0, 4, 4, 6, 6))
        dsu.rollback(0)
        self.assertEqual(dsu.snapshot(), tuple(range(8)))
        self.assertEqual(dsu.class_count, 8)

    def test_deterministic_tie_break_and_initial_owner(self):
        dsu = RollbackDSU(5, (0, 0, 2, 2, 4))
        self.assertEqual(dsu.snapshot(), (0, 0, 2, 2, 4))
        dsu.union(4, 2)
        self.assertEqual(dsu.snapshot(), (0, 0, 2, 2, 2))
        self.assertEqual(dsu.representatives(), (0, 2))
        with self.assertRaises(ValueError):
            RollbackDSU(2).find(True)


class RegionAlgebraTests(unittest.TestCase):
    def test_region_validation_and_original_ids(self):
        region = RegionState.make((0, 0, 2, 3, 3), ((4, 2), (2, 4)))
        self.assertEqual(region.owner, (0, 0, 2, 3, 3))
        self.assertEqual(region.disequalities, ((2, 4),))
        self.assertEqual(region.alphabet_size, 5)
        self.assertEqual(region.class_count, 3)
        self.assertEqual(region.lower_bound, 2)
        self.assertTrue(region.contains((0, 0, 2, 3, 3)))
        self.assertFalse(region.contains((0, 0, 2, 3, 4)))
        self.assertEqual(region.representative, (0, 0, 2, 3, 3))
        self.assertEqual(RegionState.root(0).lower_bound, 0)
        with self.assertRaises(ValueError):
            RegionState.make((1, 1), ())
        self.assertTrue(RegionState.make((0, 0), ((0, 1),)).empty)
        with self.assertRaises(ValueError):
            RegionState.make((0, 0), ((0, 0),))

    def test_empty_region_and_branch_local_disequality(self):
        root = RegionState.root(4)
        left = root.with_equality(0, 1).with_disequality(0, 1)
        self.assertTrue(left.empty)
        self.assertFalse(left.contains((0, 0, 2, 3)))
        split = first_true_split(root, ((0, 1), (2, 3)))
        self.assertEqual(split.children[0].disequalities, ())
        self.assertEqual(split.children[1].disequalities, ((0, 1),))
        self.assertEqual(split.residual.disequalities, ((0, 1), (2, 3)))
        self.assertEqual(root.disequalities, ())

    def test_first_true_split_exhaustive_literal_coverage(self):
        # Exhaust all RGS partitions for n<=4, all ordered alternative lists
        # of length <=3 on four symbols, and several nontrivial parent regions.
        pair_universe = tuple(itertools.combinations(range(4), 2))
        ordered_lists = [()]
        for length in range(1, 4):
            ordered_lists.extend(itertools.permutations(pair_universe, length))
        parent_owners = (
            (0, 1, 2, 3),
            (0, 0, 2, 3),
            (0, 1, 1, 3),
        )
        d_contexts = ((), ((0, 1),), ((2, 3),))
        checked = 0
        for owner in parent_owners:
            for disequalities in d_contexts:
                parent = RegionState.make(owner, disequalities)
                for alternatives in ordered_lists:
                    split = first_true_split(parent, alternatives)
                    self.assertEqual(len(split.children), len(alternatives))
                    for candidate in partitions(4):
                        in_parent = parent.contains(candidate)
                        memberships = [child.contains(candidate) for child in split.children]
                        in_residual = split.residual.contains(candidate)
                        self.assertEqual(sum(memberships) + int(in_residual), int(in_parent))
                        true_indices = [j for j, (a, b) in enumerate(alternatives)
                                        if candidate[a] == candidate[b]]
                        if in_parent and true_indices:
                            self.assertEqual(sum(memberships), 1)
                            self.assertTrue(memberships[min(true_indices)])
                            self.assertFalse(in_residual)
                        elif in_parent:
                            self.assertFalse(any(memberships))
                            self.assertTrue(in_residual)
                        checked += 1
        self.assertEqual(checked, 21195)
        child_records = (sum(len(alternatives) for alternatives in ordered_lists)
                         * len(parent_owners) * len(d_contexts))
        residual_records = len(ordered_lists) * len(parent_owners) * len(d_contexts)
        self.assertEqual(child_records, 3834)
        self.assertEqual(residual_records, 1413)
        print("first-true exhaustive literal membership checks:", checked,
              "ordered lists:", len(ordered_lists),
              "child records:", child_records,
              "residual records:", residual_records)

    def test_generic_fallback_is_complete_and_has_exact_residual(self):
        for owner in ((0, 1, 2, 3), (0, 0, 2, 3), (0, 1, 1, 3), (0, 0, 2, 2)):
            parent = RegionState.make(owner)
            split = generic_fallback_split(parent)
            self.assertEqual(split.alternatives, class_pairs(owner))
            self.assertEqual(generic_fallback_alternatives(parent), class_pairs(owner))
            for candidate in partitions(4):
                if not parent.contains(candidate):
                    continue
                if candidate == owner:
                    self.assertTrue(split.residual.contains(candidate))
                    self.assertFalse(any(child.contains(candidate) for child in split.children))
                else:
                    self.assertFalse(split.residual.contains(candidate))
                    self.assertEqual(sum(child.contains(candidate) for child in split.children), 1)

    def test_base_lower_bound_and_optimum_cutoffs(self):
        for owner in partitions(4):
            region = RegionState.make(owner)
            for candidate in partitions(4):
                if region.contains(candidate):
                    self.assertGreaterEqual(4 - len(set(candidate)), region.lower_bound)
        equal = RegionState.make((0, 0, 2))
        self.assertTrue(should_prune(equal, 1, all_optima=False))
        self.assertFalse(should_prune(equal, 1, all_optima=True))
        self.assertTrue(should_prune(equal, 0, all_optima=True))


class SearchBudgetTests(unittest.TestCase):
    def test_work_entry_memory_and_time_caps(self):
        budget = SearchBudget(SearchCaps(work=3, entries=2, memory_bytes=10))
        budget.charge_work(1)
        budget.admit_frontier_entry(4)
        budget.admit_frontier_entry(6)
        self.assertEqual(budget.work, 3)
        self.assertEqual(budget.entries, 2)
        self.assertEqual(budget.memory_bytes, 10)
        before_rejected = (budget.work, budget.entries, budget.memory_bytes)
        with self.assertRaises(SearchCapExceeded) as work_error:
            budget.charge_work(1)
        self.assertEqual(work_error.exception.cap, "work")
        self.assertEqual((budget.work, budget.entries, budget.memory_bytes), before_rejected)
        with self.assertRaises(SearchCapExceeded) as entry_error:
            budget.admit_frontier_entry(0)
        self.assertEqual(entry_error.exception.cap, "entries")
        self.assertEqual((budget.work, budget.entries, budget.memory_bytes), before_rejected)
        memory = SearchBudget(SearchCaps(memory_bytes=1))
        with self.assertRaises(SearchCapExceeded) as memory_error:
            memory.admit_frontier_entry(2)
        self.assertEqual(memory_error.exception.cap, "memory_bytes")
        self.assertEqual((memory.work, memory.entries, memory.memory_bytes), (0, 0, 0))
        timed = SearchBudget(SearchCaps(seconds=0))
        with self.assertRaises(SearchCapExceeded) as time_error:
            timed.charge_work(0)
        self.assertEqual(time_error.exception.cap, "seconds")
        self.assertEqual(timed.counters()["work"], 0)
        print("cap accounting before rejection:", budget.work, budget.entries, budget.memory_bytes,
              "seconds cap:", timed.caps.seconds)


if __name__ == "__main__":
    unittest.main()

import itertools
import random
import unittest

from bounded_deletion import DeletionBudget, ReplayIncomplete, check_exhaustion
from independent_replay import InvalidProof


def literal_deletions(X, Y, owner):
    if set(X).intersection(Y):
        raise InvalidProof("duplicate conflict")
    return {
        (i, group)
        for i, negative in enumerate(Y)
        for group in set(owner)
        if any(
            tuple(a for a in positive if owner[a] != group)
            == tuple(a for a in negative if owner[a] != group)
            for positive in X
        )
    }


class BoundedDeletionTests(unittest.TestCase):
    def test_exhaustive_all_owners_and_forced_collisions(self):
        words = [
            word
            for length in range(3)
            for word in itertools.product(range(2), repeat=length)
        ]
        cases = checks = 0
        for labels in itertools.product(range(3), repeat=len(words)):
            positive = [w for w, label in zip(words, labels) if label == 1]
            negative = [w for w, label in zip(words, labels) if label == 2]
            for owner in ((0, 1), (0, 0)):
                claimed = literal_deletions(positive, negative, owner)
                for bits in (0, 2, 64):
                    check_exhaustion(
                        positive, negative, owner, claimed,
                        DeletionBudget(seconds=None), hash_bits=bits,
                    )
                    checks += 1
                cases += 1
        print("exhaustive_corpus_owner_cases=", cases, "filter_checks=", checks)

    def test_random_duplicate_positives_and_negative_conflicts(self):
        rng = random.Random(13452)
        words = [
            word
            for length in range(4)
            for word in itertools.product(range(3), repeat=length)
        ]
        for _ in range(500):
            positive = rng.choices(words, k=8)
            negative = rng.choices(words, k=7)
            owner = rng.choice(((0, 1, 2), (0, 0, 2), (0, 0, 0)))
            try:
                claimed = literal_deletions(positive, negative, owner)
            except InvalidProof:
                with self.assertRaises(InvalidProof):
                    check_exhaustion(
                        positive, negative, owner, set(),
                        DeletionBudget(), hash_bits=0,
                    )
            else:
                check_exhaustion(
                    positive, negative, owner, claimed,
                    DeletionBudget(seconds=None), hash_bits=0,
                )
        print("random_collision_cases=500")

    def test_duplicate_positive_index_is_deduplicated_and_bounded(self):
        positive = [(0,)] * 1000
        negative = [(1,)]
        owner = (0, 1)
        claimed = literal_deletions(positive, negative, owner)
        budget = DeletionBudget(entries=2, seconds=None)
        check_exhaustion(positive, negative, owner, claimed, budget, hash_bits=0)
        self.assertEqual(budget.peak_entries, 2)
        with self.assertRaises(ReplayIncomplete):
            check_exhaustion(
                positive, negative, owner, claimed,
                DeletionBudget(entries=1, seconds=None), hash_bits=0,
            )

    def test_work_entry_length_and_deadline_caps(self):
        positive = [(0, 1)]
        negative = [(1, 0)]
        owner = (0, 1)
        claimed = literal_deletions(positive, negative, owner)
        for limits in (
            dict(work=0), dict(entries=0), dict(word_length=1), dict(seconds=0),
        ):
            with self.subTest(limits=limits):
                with self.assertRaises(ReplayIncomplete):
                    check_exhaustion(
                        positive, negative, owner, claimed, DeletionBudget(**limits),
                    )

    def test_missing_extra_and_duplicate_conflict_rejected(self):
        positive = [(0, 1)]
        negative = [(1, 0)]
        owner = (0, 1)
        claimed = literal_deletions(positive, negative, owner)
        with self.assertRaises(InvalidProof):
            check_exhaustion(
                positive, negative, owner, claimed - {next(iter(claimed))},
                DeletionBudget(), hash_bits=0,
            )
        with self.assertRaises(InvalidProof):
            check_exhaustion(
                positive, negative, owner, claimed | {(1, 0)},
                DeletionBudget(), hash_bits=0,
            )
        with self.assertRaises(InvalidProof):
            check_exhaustion(
                positive, positive, owner, set(), DeletionBudget(), hash_bits=0,
            )

    def test_long_diverse_trace(self):
        size = 20_000
        owner = tuple(range(size))
        positive = [owner]
        negative = [(1, 0) + owner[2:]]
        claimed = {(0, 0), (0, 1)}
        budget = DeletionBudget(seconds=30, entries=size + 1)
        check_exhaustion(positive, negative, owner, claimed, budget)
        self.assertEqual(budget.peak_entries, size + 1)
        self.assertEqual(budget.exact_checks, 2)
        print(
            "long_diverse_symbols=", size,
            "index_entries=", budget.peak_entries,
            "exact_checks=", budget.exact_checks,
            "work=", budget.used,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

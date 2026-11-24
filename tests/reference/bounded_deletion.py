"""Independent exact deletion enumeration with resource caps.

Polynomial fingerprints are filters only. Every accepted hit is compared exactly
in streaming order. The positive index stores O(unique-positive * touched-groups)
references; no materialized deletion remainders or auxiliary trace-key sets.
Caps are cooperative enumeration limits, not hard process RSS limits.
"""
from array import array
from collections import defaultdict
from itertools import zip_longest
from time import monotonic

from independent_replay import require


class ReplayIncomplete(Exception):
    """No verified result when an enumeration budget is exhausted."""


class DeletionBudget:
    def __init__(self, *, work=200_000_000, entries=2_000_000,
                 word_length=2_000_000, seconds=30):
        for x in (work, entries, word_length):
            if type(x) is not int or x < 0:
                raise ValueError("nonnegative integer budget required")
        if seconds is not None and (
            type(seconds) not in (int, float) or not 0 <= seconds < float("inf")
        ):
            raise ValueError("invalid seconds")
        self.work = work
        self.entries = entries
        self.word_length = word_length
        self.deadline = None if seconds is None else monotonic() + seconds
        self.used = 0
        self.peak_entries = 0
        self.exact_checks = 0

    def debit(self, amount=1):
        self.used += amount
        if (self.used > self.work or
                (self.deadline is not None and monotonic() >= self.deadline)):
            raise ReplayIncomplete("deletion work/deadline cap")

    def index_size(self, entries):
        self.debit(0)
        self.peak_entries = max(self.peak_entries, entries)
        if entries > self.entries:
            raise ReplayIncomplete("deletion index entry cap")


def check_exhaustion(X, Y, p, claimed, budget, *, hash_bits=64):
    """Check every exact (negative index, deleted canonical group) obligation.

    Auxiliary index space is O(max_word_length + unique positive index entries
    + groups touched by one trace). The index never stores a remainder tuple.
    """
    if type(hash_bits) is not int or not 0 <= hash_bits <= 64:
        raise ValueError("hash bits")
    budget.debit(1 + len(X) + len(Y))
    longest = max((len(w) for words in (X, Y) for w in words), default=0)
    if longest > budget.word_length:
        raise ReplayIncomplete("deletion word length cap")
    budget.debit(longest)

    mask = (1 << hash_bits) - 1
    base = 0x9e3779b185ebca87
    powers = array("Q", [1 & mask])
    for i in range(longest):
        if i % 4096 == 0:
            budget.debit(0)
        powers.append((powers[-1] * base) & mask)

    def signatures(word):
        budget.debit(1 + 2 * len(word))
        h = 0
        states = {}
        for i, symbol in enumerate(word):
            if i % 4096 == 0:
                budget.debit(0)
            group = p[symbol]
            acc, previous, previous_hash, count = states.get(
                group, (0, 0, 0, 0)
            )
            factor = powers[i - previous]
            acc = (acc * factor + h - previous_hash * factor) & mask
            h = (h * base + symbol + 1) & mask
            states[group] = (acc, i + 1, h, count + 1)

        length = len(word)
        for group, (acc, previous, previous_hash, count) in states.items():
            factor = powers[length - previous]
            states[group] = (
                length - count,
                (acc * factor + h - previous_hash * factor) & mask,
            )
        return (length, h), states

    def equal_after_delete(x, y, group):
        budget.exact_checks += 1
        budget.debit(1 + len(x) + len(y))
        sentinel = object()

        def retained(word):
            for i, symbol in enumerate(word):
                if i % 4096 == 0:
                    budget.debit(0)
                if p[symbol] != group:
                    yield symbol

        return all(
            left == right
            for left, right in zip_longest(
                retained(x), retained(y), fillvalue=sentinel
            )
        )

    # Index only unique positive words. Exact duplicate detection uses the
    # full-word fingerprint bucket and streaming equality, not a second set
    # containing copies of every distinct positive trace.
    buckets = defaultdict(list)
    entry_count = 0
    for positive_id, word in enumerate(X):
        budget.debit(1 + len(word))
        full_key, groups = signatures(word)

        duplicate = False
        for marker, prior_id in buckets.get(full_key, ()):
            budget.debit()
            if marker == -1 and equal_after_delete(X[prior_id], word, -1):
                duplicate = True
                break
        if duplicate:
            continue

        entry_count += 1 + len(groups)
        budget.index_size(entry_count)
        buckets[full_key].append((-1, positive_id))
        for group, key in groups.items():
            buckets[key].append((group, positive_id))

    found_count = 0
    for negative_id, word in enumerate(Y):
        full_key, groups = signatures(word)

        # Cross-label equality is forbidden for an exhausted proof. Check
        # exact equality only in the full-word fingerprint bucket.
        for marker, positive_id in buckets.get(full_key, ()):
            budget.debit()
            if marker == -1:
                require(
                    not equal_after_delete(X[positive_id], word, -1),
                    "duplicate conflict precludes exhausted pass",
                )

        found = set()
        for group, key in groups.items():
            for marker, positive_id in buckets.get(key, ()):
                budget.debit()
                if (marker == -1 or marker == group) and equal_after_delete(
                    X[positive_id], word, group
                ):
                    require(
                        (negative_id, group) in claimed,
                        "missing exhausted deletion fact",
                    )
                    found.add(group)
                    break

        # A group absent from the negative word leaves that word unchanged.
        # Find positive traces whose deletion by that group equals it.
        for group, positive_id in buckets.get(full_key, ()):
            budget.debit()
            if (group != -1 and group not in groups and group not in found
                    and equal_after_delete(X[positive_id], word, group)):
                require(
                    (negative_id, group) in claimed,
                    "missing exhausted deletion fact",
                )
                found.add(group)

        found_count += len(found)

    budget.debit(0)
    require(found_count == len(claimed), "extra exhausted deletion fact")

"""Bounded literal deletion discovery and lazy cross-support families."""
from bisect import bisect_right
from dataclasses import dataclass
from heapq import merge
from itertools import combinations


ALL_PAIRS = "ALL_PAIRS_LEX_V1"
CROSS_SUPPORT = "CROSS_SUPPORT_LEX_V1"
DISCOVERY_WORK = 4096


@dataclass(frozen=True)
class CrossPairs:
    support_s: tuple[int, ...]
    support_t: tuple[int, ...]
    # Each row contains only an offset into the opposite support.
    rows: tuple[tuple[int, tuple[int, ...], int], ...]
    stops: tuple[int, ...]

    @classmethod
    def build(cls, s, t, budget):
        budget.charge_work(len(s) + len(t))
        members = merge(((a, t) for a in s), ((b, s) for b in t), key=lambda row: row[0])
        rows, stops = [], []
        total = 0
        for a, opposite in members:
            budget.charge_work(1 + len(opposite).bit_length())
            start = bisect_right(opposite, a)
            total += len(opposite) - start
            rows.append((a, opposite, start))
            stops.append(total)
        return cls(s, t, tuple(rows), tuple(stops))

    @property
    def count(self):
        return len(self.support_s) * len(self.support_t)

    def pair_at(self, index, budget):
        if type(index) is not int or not 0 <= index < self.count:
            raise ValueError("pair index")
        budget.charge_work(1 + len(self.rows).bit_length())
        row = bisect_right(self.stops, index)
        a, opposite, start = self.rows[row]
        offset = self.stops[row - 1] if row else 0
        return a, opposite[start + index - offset]


@dataclass(frozen=True)
class AllPairsPrefix:
    stop: tuple[int, int]

    def violated(self, dsu, merged, budget):
        budget.charge_work()
        # On a nonempty parent only newly internal pairs can violate this prefix.
        return merged < self.stop


@dataclass(frozen=True)
class CrossPrefix:
    family: CrossPairs
    stop: tuple[int, int]

    def violated(self, dsu, merged, budget):
        minima = {}
        for a in self.family.support_s:
            budget.charge_work()
            minima.setdefault(dsu.find(a), a)
        # Both supports are ascending. The first member of each side in a
        # current class gives that class's least normalized internal pair.
        for b in self.family.support_t:
            budget.charge_work()
            a = minima.pop(dsu.find(b), None)
            if a is not None and (min(a, b), max(a, b)) < self.stop:
                return True
        return False


class _DiscoveryLimit(Exception):
    pass


def discover(owner, sample, budget, counters):
    """Return the first completed disjoint pair in stable probe order."""
    used = 0

    def charge(units):
        nonlocal used
        if used + units > DISCOVERY_WORK:
            raise _DiscoveryLimit
        budget.charge_work(units)
        used += units
        counters["witness_work"] += units

    def complement(word, support):
        projected = []
        for token in word:
            charge(1)
            if owner[token] not in support:
                projected.append(token)
        return projected

    try:
        for i, y in enumerate(sample.negative):
            charge(1 + len(y))
            touched_y = {owner[token] for token in y}
            evidence = {}
            for j, x in enumerate(sample.positive):
                charge(1 + len(x) + len(touched_y))
                touched = sorted(touched_y | {owner[token] for token in x})
                for size in (1, 2):
                    for support in combinations(touched, size):
                        charge(1)
                        counters["witness_probes"] += 1
                        if complement(y, support) != complement(x, support):
                            continue
                        for previous, witness_j in evidence.items():
                            charge(1)
                            if any(a in previous for a in support):
                                continue
                            if previous < support:
                                s, t, js, jt = previous, support, witness_j, j
                            else:
                                s, t, js, jt = support, previous, j, witness_j
                            return dict(negative_id=f"N{i}", positive_s_id=f"P{js}",
                                        positive_t_id=f"P{jt}", support_s=list(s),
                                        support_t=list(t))
                        evidence.setdefault(support, j)
    except _DiscoveryLimit:
        counters["witness_local_caps"] += 1
    return None

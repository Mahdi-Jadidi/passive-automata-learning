
"""Immutable partition encoding, raw trace analysis, and complete query adapter."""
from collections import Counter, defaultdict
from itertools import combinations
from time import perf_counter

from sample import read_sample


def ordered(blocks):
    return tuple(sorted(blocks, key=lambda block: block & -block))


def union(blocks):
    result = 0
    for block in blocks:
        result |= block
    return result


def merge(partition, left, right):
    return ordered([left | right, *(b for b in partition if b not in (left, right))])


def image(word, block, tick):
    result = []
    for symbol in word:
        tick()
        if (1 << symbol) & block:
            result.append(symbol)
    return tuple(result)


class ProjectionOracle:
    """Bound to one sample. The selector receives only the callable interface."""

    def __init__(self, positives, negatives, tick):
        self.positives = positives
        self.negatives = negatives
        self.tick = tick
        self.cache = {}
        self.images = self.requests = self.misses = 0

    def row(self, block):
        self.requests += 1
        if block in self.cache:
            return self.cache[block]
        self.misses += 1
        positives = {}
        for j, word in enumerate(self.positives):
            self.images += 1
            positives.setdefault(image(word, block, self.tick), j)
        zeros, free = [], defaultdict(list)
        for i, word in enumerate(self.negatives):
            self.images += 1
            projected = image(word, block, self.tick)
            if projected in positives:
                zeros.append([i, positives[projected]])
            else:
                free[projected].append(i)
        result = {"block": block, "zeros": zeros, "free": list(free.values())}
        self.cache[block] = result
        return result

    def __call__(self, partition, purpose):
        tables = [self.row(block) for block in partition]
        covered = {i for table in tables for group in table["free"] for i in group}
        failed = next((i for i in range(len(self.negatives)) if i not in covered), None)
        return {
            "status": "ACCEPT" if failed is None else "NO",
            "blocks": list(partition),
            "tables": tables,
            "failed": failed,
        }


def deletion_candidates(x, y, counts_x, counts_y, tick, order_sensitive):
    different = {a for a in counts_x.keys() | counts_y.keys() if counts_x[a] != counts_y[a]}
    base = sum(1 << a for a in different)
    yield base
    if not order_sensitive:
        return
    common = sorted(counts_x.keys() - different)
    for a in common:
        tick()
    if tuple(a for a in x if a not in different) == tuple(a for a in y if a not in different):
        return
    graph = {a: set() for a in common}
    for a, b in combinations(common, 2):
        tick()
        pair = (1 << a) | (1 << b)
        if image(x, pair, tick) != image(y, pair, tick):
            graph[a].add(b)
            graph[b].add(a)

    nonisolated = [a for a in common if graph[a]]
    orders = [nonisolated, nonisolated[::-1]]
    orders += [[a, *(b for b in nonisolated if b != a)] for a in nonisolated[:3]]
    for order in orders:
        independent = set()
        for a in order:
            tick()
            if graph[a].isdisjoint(independent):
                independent.add(a)
        yield base | sum(1 << a for a in nonisolated if a not in independent)


def analyze(D, tick, *, enabled, order_sensitive, work_limit=None, encoded=None, covered=None):
    Sigma, positives, negatives = read_sample(D, tick) if encoded is None else encoded
    covered = {} if covered is None else covered
    full = (1 << len(Sigma)) - 1
    positive_ids = {}
    for j, x in enumerate(positives):
        tick()
        positive_ids.setdefault(x, j)
    for i, y in enumerate(negatives):
        tick()
        if y in positive_ids:
            return Sigma, positives, negatives, {"failure": {"kind": "A01", "i": i, "j": positive_ids[y]}}
    if not Sigma and negatives:
        return Sigma, positives, negatives, {"failure": {"kind": "A02", "i": 0}}

    observed = sum(1 << a for a in {a for word in (*positives, *negatives) for a in word})
    unused_mask = (full ^ observed) if enabled else 0
    if unused_mask == full and full:
        unused_mask ^= full & -full
    unused = [1 << a for a in range(len(Sigma)) if unused_mask & (1 << a)]
    active = full ^ unused_mask
    root = ordered(1 << a for a in range(len(Sigma)) if active & (1 << a))
    events = [{"rule": "A03", "blocks": unused}] if unused else []
    if len(positive_ids) < len(positives) or len(set(negatives)) < len(negatives):
        events.append({"rule": "A04", "positive_ids": list(positive_ids.values())})
    if any(not w for w in (*positives, *negatives)):
        events.append({"rule": "A05"})
    if not positives or not negatives:
        events.append({"rule": "A06"})
    facts = {}
    truncated = False

    if enabled and positives and negatives:
        negative_ids = {}
        for i, y in enumerate(negatives):
            if i not in covered:
                negative_ids.setdefault(y, []).append(i)
        counts = {word: Counter(word) for word in positive_ids.keys() | negative_ids.keys()}
        comparisons = 0
        for y, ids in negative_ids.items():
            if truncated:
                break
            for x, j in positive_ids.items():
                tick()
                if work_limit is not None and comparisons >= work_limit:
                    truncated = True
                    break
                comparisons += 1
                basic = next(deletion_candidates(x, y, counts[x], counts[y], tick, False))
                candidates = deletion_candidates(x, y, counts[x], counts[y], tick, order_sensitive)
                for deleted in dict.fromkeys(candidates):
                    region = active & ~deleted
                    if image(x, region, tick) == image(y, region, tick):
                        for i in ids:
                            facts.setdefault((i, region), {"i": i, "j": j, "region": region,
                                             "source": "raw", "rule": "A09" if deleted != basic else "A08"})
    contractions = []
    if facts:
        by_negative = defaultdict(list)
        for item in facts.values():
            by_negative[item["i"]].append(item)
        while True:
            changed = False
            for i, evidence in by_negative.items():
                required = {}
                for block in root:
                    tick()
                    complement = active & ~block
                    witness = next((item for item in evidence if complement & item["region"] == complement), None)
                    if witness:
                        required[block] = witness
                if len(required) >= 2:
                    contractions.append({"rule": "A07", "i": i, "items": [
                        {"block": block, "fact": item} for block, item in required.items()
                    ]})
                    root = ordered([union(required), *(b for b in root if b not in required)])
                    changed = True
                    break
            if not changed:
                break
    entry = {"unused": unused, "root": list(root), "contractions": contractions,
             "facts": list(facts.values()), "events": events, "truncated": truncated,
             "covered": covered}
    return Sigma, positives, negatives, entry

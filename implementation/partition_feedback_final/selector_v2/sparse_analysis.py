"""Raw evidence only. No external verdicts or learner dependencies."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import chain
from .core import Budget, BudgetExpired, PartitionRef, SymbolDSU


@dataclass(frozen=True)
class StructuralResult:
    compatible: bool
    separating_groups: tuple[int, ...] = ()
    failed_negative: int | None = None


def raw_check(sample, partition):
    partition.validate_sample(sample)
    owner = partition.owner
    def project(word):
        groups = defaultdict(list)
        for a in word:
            groups[owner[a]].append(a)
        return groups
    possible, presence = defaultdict(set), Counter()
    for word in sample.positive:
        for g, seq in project(word).items():
            possible[g].add(tuple(seq))
            presence[g] += 1
    universal = tuple(g for g, count in presence.items() if count == len(sample.positive))
    witnesses = []
    for i, word in enumerate(sample.negative):
        if not owner:
            return StructuralResult(False, failed_negative=i)
        if not sample.positive:
            witnesses.append(0)
            continue
        local = project(word)
        g = next((g for g, seq in local.items() if tuple(seq) not in possible.get(g, ())), None)
        if g is None:
            g = next((g for g in universal if g not in local), None)
        if g is None:
            return StructuralResult(False, failed_negative=i)
        witnesses.append(g)
    return StructuralResult(True, tuple(witnesses))


def singleton_check(sample):
    """Sparse count index; same result semantics as raw_check(singletons)."""
    possible, presence = defaultdict(set), Counter()
    for word in sample.positive:
        for a, count in Counter(word).items():
            possible[a].add(count)
            presence[a] += 1
    universal = tuple(a for a, count in presence.items() if count == len(sample.positive))
    witnesses = []
    for i, word in enumerate(sample.negative):
        if not sample.alphabet:
            return StructuralResult(False, failed_negative=i)
        if not sample.positive:
            witnesses.append(0)
            continue
        counts = Counter(word)
        a = next((a for a, c in counts.items() if c not in possible.get(a, ())), None)
        if a is None:
            a = next((a for a in universal if a not in counts), None)
        if a is None:
            return StructuralResult(False, failed_negative=i)
        witnesses.append(a)
    return StructuralResult(True, tuple(witnesses))


@dataclass(frozen=True)
class DeletionFact:
    negative: int
    group: int
    positive: int


@dataclass(frozen=True)
class DeletionResult:
    sample_digest: str
    owner_snapshot: PartitionRef
    facts: tuple[DeletionFact, ...]
    exhausted: bool
    cursor: tuple[str, int] | None
    label_conflict: tuple[int, int] | None = None


def _signatures(word, owner, mask):
    base = 1000003
    h, powers = [0], [1]
    positions = defaultdict(list)
    for k, a in enumerate(word):
        h.append((h[-1] * base + a + 1) & mask)
        powers.append((powers[-1] * base) & mask)
        positions[owner[a]].append(k)
    m = len(word)
    deleted = {}
    for g, pos in positions.items():
        value, left = 0, 0
        for right in chain(pos, (m,)):
            length = right - left
            value = (value * powers[length] + h[right] - h[left] * powers[length]) & mask
            left = right + 1
        deleted[g] = (m - len(pos), value)
    return (m, h[-1]), deleted


def _equal(x, y, owner, g):
    return tuple(a for a in x if owner[a] != g) == tuple(a for a in y if owner[a] != g)


def discover_deletions(sample, owner_snapshot, budget=None, *, hash_bits=64):
    """Three-way join, exact collision checks. Interrupted cursor is diagnostic;
    restart the frozen pass with a fresh budget (not a resumable index).
    """
    owner_snapshot.validate_sample(sample)
    if type(hash_bits) is not int or not 0 <= hash_bits <= 64:
        raise ValueError('invalid hash bits')
    owner = owner_snapshot.owner
    budget = budget if budget is not None else Budget()
    mask = (1 << hash_bits) - 1
    full, deletions, inverse = defaultdict(list), defaultdict(list), defaultdict(list)
    exact, facts = {}, []
    cursor = ('positive', 0)
    def result(exhausted, conflict=None):
        return DeletionResult(sample.sample_digest, owner_snapshot, tuple(facts), exhausted,
                              None if exhausted else cursor, conflict)
    try:
        for j, x in enumerate(sample.positive):
            cursor = ('positive', j)
            budget.debit(1 + len(x))
            if x in exact:
                continue
            exact[x] = j
            sig, ds = _signatures(x, owner, mask)
            full[sig].append(j)
            for g, key in ds.items():
                deletions[g, key].append(j)
                inverse[key].append((g, j))
        # Preflight duplicates before any deletion claims: absent-both case.
        for i, y in enumerate(sample.negative):
            cursor = ('conflict', i)
            budget.debit(1 + len(y))
            if y in exact:
                return result(False, (i, exact[y]))
        for i, y in enumerate(sample.negative):
            cursor = ('negative', i)
            budget.debit(1 + len(y))
            sig, ds = _signatures(y, owner, mask)
            found = set()
            for g, key in ds.items():
                for j in chain(deletions.get((g, key), ()), full.get(key, ())):
                    budget.debit(1 + len(y) + len(sample.positive[j]))
                    if _equal(sample.positive[j], y, owner, g):
                        facts.append(DeletionFact(i, g, j))
                        found.add(g)
                        break
            for g, j in inverse.get(sig, ()):
                budget.debit()
                if g not in ds and g not in found:
                    budget.debit(len(y) + len(sample.positive[j]))
                    if _equal(sample.positive[j], y, owner, g):
                        facts.append(DeletionFact(i, g, j))
                        found.add(g)
        return result(True)
    except BudgetExpired:
        return result(False)


@dataclass(frozen=True)
class ForcedEdge:
    negative: int
    a: int
    positive_a: int
    b: int
    positive_b: int


def singleton_forest(sample, result):
    """Replay singleton facts before contraction; no trust in hashes or cursor."""
    root = PartitionRef.singletons(len(sample.alphabet))
    if result.sample_digest != sample.sample_digest or result.owner_snapshot != root:
        raise ValueError('wrong sample or non-singleton snapshot')
    dsu, first, edges = SymbolDSU(len(root.owner)), {}, []
    for fact in result.facts:
        i, g, j = fact.negative, fact.group, fact.positive
        if (any(type(v) is not int for v in (i, g, j)) or not 0 <= i < len(sample.negative)
                or not 0 <= j < len(sample.positive) or not 0 <= g < len(root.owner)
                or not _equal(sample.positive[j], sample.negative[i], root.owner, g)):
            raise ValueError('invalid deletion fact')
        a = first.setdefault(i, fact)
        if dsu.union(a.group, g):
            edges.append(ForcedEdge(i, a.group, a.positive, g, j))
    return dsu.snapshot(), tuple(edges)

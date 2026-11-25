"""P3 EDR-BB region algebra and deterministic rollback union-find.

This module is the producer-side in-memory foundation only.  It deliberately
contains no wire serializer, certificate verifier, evaluator adapter, or
pruning rule beyond the mandatory-equality lower bound.
"""
from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from time import monotonic


def _valid_owner(owner):
    if type(owner) is not tuple:
        raise ValueError("owner must be a tuple")
    for symbol, representative in enumerate(owner):
        if (type(representative) is not int or representative < 0
                or representative > symbol or owner[representative] != representative):
            raise ValueError("owner is not a canonical original-alphabet owner array")
    return owner


def _pair(pair, n):
    if type(pair) is not tuple or len(pair) != 2:
        raise ValueError("pair must be a 2-tuple")
    a, b = pair
    if (type(a) is not int or type(b) is not int or a < 0 or b < 0
            or a >= n or b >= n or a == b):
        raise ValueError("pair endpoints must be distinct original IDs in range")
    return (a, b) if a < b else (b, a)


def _canonical_pairs(pairs, n):
    return tuple(sorted({_pair(pair, n) for pair in pairs}))


class RollbackDSU:
    """Deterministic union-by-size DSU; find never performs path compression."""

    def __init__(self, n, owner=None):
        if type(n) is not int or n < 0:
            raise ValueError("invalid alphabet size")
        self.parent = list(range(n))
        self.size = [1] * n
        self.minimum = list(range(n))
        self._history = []
        if owner is not None:
            owner = _valid_owner(owner)
            if len(owner) != n:
                raise ValueError("owner universe mismatch")
            for symbol, representative in enumerate(owner):
                if symbol != representative:
                    self._union(representative, symbol, record=False)
            self._history.clear()

    def _check_id(self, symbol):
        if type(symbol) is not int or not 0 <= symbol < len(self.parent):
            raise ValueError("symbol ID out of range")

    def find(self, symbol):
        self._check_id(symbol)
        while self.parent[symbol] != symbol:
            symbol = self.parent[symbol]
        return symbol

    def mark(self):
        return len(self._history)

    def _union(self, a, b, *, record):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        # Stable tie-break: larger tree wins; equal sizes choose lower minimum ID.
        if (self.size[root_a] < self.size[root_b]
                or (self.size[root_a] == self.size[root_b]
                    and self.minimum[root_a] > self.minimum[root_b])):
            root_a, root_b = root_b, root_a
        if record:
            self._history.append((root_b, root_a, self.size[root_a], self.minimum[root_a]))
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        self.minimum[root_a] = min(self.minimum[root_a], self.minimum[root_b])
        return True

    def union(self, a, b):
        self._check_id(a)
        self._check_id(b)
        return self._union(a, b, record=True)

    def rollback(self, marker):
        if type(marker) is not int or not 0 <= marker <= len(self._history):
            raise ValueError("invalid rollback marker")
        while len(self._history) > marker:
            child, parent, old_size, old_minimum = self._history.pop()
            self.parent[child] = child
            self.size[parent] = old_size
            self.minimum[parent] = old_minimum

    @property
    def class_count(self):
        return sum(1 for symbol, parent in enumerate(self.parent) if symbol == parent)

    def snapshot(self):
        return tuple(self.minimum[self.find(symbol)] for symbol in range(len(self.parent)))

    def representatives(self):
        return tuple(sorted({self.minimum[self.find(symbol)] for symbol in range(len(self.parent))}))


@dataclass(frozen=True)
class RegionState:
    """R(E,D): E is a canonical owner over all original IDs; D stores original pairs.

    The caller must construct a non-singleton root owner only from independently
    verified journal/2 evidence. root(n) is the no-contraction identity root.
    """
    owner: tuple[int, ...]
    disequalities: tuple[tuple[int, int], ...] = ()

    def __post_init__(self):
        _valid_owner(self.owner)
        expected = _canonical_pairs(self.disequalities, len(self.owner))
        if self.disequalities != expected:
            raise ValueError("disequalities must be sorted, unique original-ID pairs")

    @classmethod
    def make(cls, owner, disequalities=()):
        owner = _valid_owner(owner)
        return cls(owner, _canonical_pairs(tuple(disequalities), len(owner)))

    @classmethod
    def root(cls, n):
        if type(n) is not int or n < 0:
            raise ValueError("invalid alphabet size")
        return cls(tuple(range(n)), ())

    @property
    def alphabet_size(self):
        return len(self.owner)

    @property
    def class_count(self):
        return len(set(self.owner))

    @property
    def lower_bound(self):
        return self.alphabet_size - self.class_count

    @property
    def empty(self):
        return any(self.owner[a] == self.owner[b] for a, b in self.disequalities)

    @property
    def representative(self):
        """The minimum-cost member E, as a complete canonical owner array."""
        return self.owner

    def contains(self, candidate_owner):
        candidate_owner = _valid_owner(candidate_owner)
        if len(candidate_owner) != self.alphabet_size or self.empty:
            return False
        for symbol, representative in enumerate(self.owner):
            if candidate_owner[symbol] != candidate_owner[representative]:
                return False
        for a, b in self.disequalities:
            if candidate_owner[a] == candidate_owner[b]:
                return False
        return True

    def with_equality(self, a, b):
        pair = _pair((a, b), self.alphabet_size)
        dsu = RollbackDSU(self.alphabet_size, self.owner)
        dsu.union(*pair)
        return RegionState(self._owner_from_dsu(dsu), self.disequalities)

    def with_disequality(self, a, b):
        pair = _pair((a, b), self.alphabet_size)
        return RegionState.make(self.owner, self.disequalities + (pair,))

    @staticmethod
    def _owner_from_dsu(dsu):
        return dsu.snapshot()


@dataclass(frozen=True)
class FirstTrueSplit:
    """Ordered first-true children and the explicit all-false residual."""
    parent: RegionState
    alternatives: tuple[tuple[int, int], ...]
    children: tuple[RegionState, ...]
    residual: RegionState

    def __post_init__(self):
        if len(self.alternatives) != len(self.children):
            raise ValueError("one child is required for every ordered alternative")


def first_true_split(region, alternatives):
    """Split R(E,D) by the first true same-block predicate in ordered L.

    Child j adds equality e_j and all earlier disequalities.  The residual adds
    every alternative as a disequality.  Inconsistent regions are retained as
    explicit empty states; no child or residual is silently omitted.
    """
    if not isinstance(region, RegionState):
        raise ValueError("expected RegionState")
    normalized = tuple(_pair(pair, region.alphabet_size) for pair in alternatives)
    dsu = RollbackDSU(region.alphabet_size, region.owner)
    prefix = []
    children = []
    for pair in normalized:
        marker = dsu.mark()
        dsu.union(*pair)
        child_owner = dsu.snapshot()
        child = RegionState.make(child_owner, region.disequalities + tuple(prefix))
        children.append(child)
        dsu.rollback(marker)
        prefix.append(pair)
    residual = RegionState.make(region.owner, region.disequalities + normalized)
    return FirstTrueSplit(region, normalized, tuple(children), residual)


def generic_fallback_alternatives(region):
    """Every unordered pair of distinct current E-classes, in stable ID order."""
    if not isinstance(region, RegionState):
        raise ValueError("expected RegionState")
    representatives = tuple(sorted(set(region.owner)))
    return tuple(combinations(representatives, 2))


def generic_fallback_split(region):
    return first_true_split(region, generic_fallback_alternatives(region))


def should_prune(region, incumbent_cost, *, all_optima=False):
    """Apply only the authorized base-LB cutoff (one optimum vs all optima)."""
    if not isinstance(region, RegionState):
        raise ValueError("expected RegionState")
    if type(incumbent_cost) is not int or incumbent_cost < 0:
        raise ValueError("invalid incumbent cost")
    if type(all_optima) is not bool:
        raise ValueError("all_optima must be bool")
    if all_optima:
        return region.lower_bound > incumbent_cost
    return region.lower_bound >= incumbent_cost


class SearchCapExceeded(RuntimeError):
    def __init__(self, cap):
        super().__init__("search cap exceeded: " + cap)
        self.cap = cap


@dataclass(frozen=True)
class SearchCaps:
    """Cooperative caps; memory_bytes accounts retained frontier payload bytes."""
    seconds: float | None = None
    work: int | None = None
    entries: int | None = None
    memory_bytes: int | None = None

    def __post_init__(self):
        if self.seconds is not None and (type(self.seconds) not in (int, float)
                                         or not isfinite(self.seconds) or self.seconds < 0):
            raise ValueError("invalid seconds cap")
        for name in ("work", "entries", "memory_bytes"):
            value = getattr(self, name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("invalid " + name + " cap")


class SearchBudget:
    """Deterministic work/entry/frontier-byte accounting plus cooperative deadline."""
    def __init__(self, caps=None):
        self.caps = caps if caps is not None else SearchCaps()
        if not isinstance(self.caps, SearchCaps):
            raise ValueError("expected SearchCaps")
        self.started = monotonic()
        self.work = 0
        self.entries = 0
        self.memory_bytes = 0

    @property
    def elapsed_seconds(self):
        return monotonic() - self.started

    def _check_time(self):
        if self.caps.seconds is not None and self.elapsed_seconds >= self.caps.seconds:
            raise SearchCapExceeded("seconds")

    def charge_work(self, units=1):
        if type(units) is not int or units < 0:
            raise ValueError("invalid work units")
        self._check_time()
        if self.caps.work is not None and self.work + units > self.caps.work:
            raise SearchCapExceeded("work")
        self.work += units

    def admit_frontier_entry(self, encoded_bytes):
        if type(encoded_bytes) is not int or encoded_bytes < 0:
            raise ValueError("invalid encoded entry size")
        self._check_time()
        if self.caps.entries is not None and self.entries + 1 > self.caps.entries:
            raise SearchCapExceeded("entries")
        if (self.caps.memory_bytes is not None
                and self.memory_bytes + encoded_bytes > self.caps.memory_bytes):
            raise SearchCapExceeded("memory_bytes")
        if self.caps.work is not None and self.work + 1 > self.caps.work:
            raise SearchCapExceeded("work")
        # Admission is atomic: a rejected entry changes no counters.
        self.entries += 1
        self.memory_bytes += encoded_bytes
        self.work += 1

    def counters(self):
        return {
            "work": self.work,
            "entries": self.entries,
            "frontier_bytes": self.memory_bytes,
            "elapsed_seconds": self.elapsed_seconds,
        }

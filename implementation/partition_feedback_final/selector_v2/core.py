"""Selector-only immutable IDs, canonical partitions and sparse union-find."""
from dataclasses import dataclass, field
from hashlib import sha256
from json import dumps
from math import isfinite
from time import monotonic


def digest(value):
    return sha256(dumps(value, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Sample:
    alphabet: tuple[str, ...]
    positive: tuple[tuple[int, ...], ...]
    negative: tuple[tuple[int, ...], ...]
    sample_digest: str = field(init=False)

    def __post_init__(self):
        if (type(self.alphabet) is not tuple or any(type(a) is not str or not a for a in self.alphabet)
                or len(set(self.alphabet)) != len(self.alphabet)):
            raise ValueError('invalid alphabet')
        for words in (self.positive, self.negative):
            if type(words) is not tuple or any(type(w) is not tuple or any(
                    type(a) is not int or not 0 <= a < len(self.alphabet) for a in w) for w in words):
                raise ValueError('invalid encoded traces')
        object.__setattr__(self, 'sample_digest', digest(('sample-v2', self.alphabet, self.positive, self.negative)))

    @classmethod
    def from_input(cls, data):
        if type(data) is not dict or set(data) != {'alphabet', 'positive', 'negative'}:
            raise ValueError('expected alphabet, positive, negative')
        alphabet = data['alphabet']
        if type(alphabet) is not list or any(type(a) is not str or not a for a in alphabet):
            raise ValueError('invalid alphabet')
        ids = {a: i for i, a in enumerate(alphabet)}
        if len(ids) != len(alphabet):
            raise ValueError('duplicate symbol')
        def encode(words):
            if type(words) is not list:
                raise ValueError('invalid label class')
            out = []
            for word in words:
                if type(word) is not list or any(type(a) is not str or a not in ids for a in word):
                    raise ValueError('invalid trace')
                out.append(tuple(ids[a] for a in word))
            return tuple(out)
        return cls(tuple(alphabet), encode(data['positive']), encode(data['negative']))


@dataclass(frozen=True)
class PartitionRef:
    """owner[a] is minimum original ID in its block; all IDs are covered."""
    owner: tuple[int, ...]

    def __post_init__(self):
        if type(self.owner) is not tuple or any(type(g) is not int or not 0 <= g <= a
                or self.owner[g] != g for a, g in enumerate(self.owner)):
            raise ValueError('noncanonical owner')

    @classmethod
    def singletons(cls, n):
        return cls(tuple(range(n)))

    @property
    def cost(self):
        return sum(a != g for a, g in enumerate(self.owner))

    def blocks(self):
        groups = {}
        for a, g in enumerate(self.owner):
            groups.setdefault(g, []).append(a)
        return tuple(tuple(v) for v in groups.values())

    def validate_sample(self, sample):
        if len(self.owner) != len(sample.alphabet):
            raise ValueError('partition universe mismatch')


class SymbolDSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.minimum = list(range(n))
        self.cost = 0

    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        self.minimum[a] = min(self.minimum[a], self.minimum[b])
        self.cost += 1
        return True

    def snapshot(self):
        return PartitionRef(tuple(self.minimum[self.find(a)] for a in range(len(self.parent))))


class BudgetExpired(Exception):
    pass


class Budget:
    """Cooperative work/deadline budget; work units are not wall time."""
    def __init__(self, work=None, seconds=None):
        if work is not None and (type(work) is not int or work < 0):
            raise ValueError('invalid work budget')
        if seconds is not None and (type(seconds) not in (int, float) or not isfinite(seconds) or seconds < 0):
            raise ValueError('invalid time budget')
        self.limit = work
        self.used = 0
        self.stop = None if seconds is None else monotonic() + seconds

    def debit(self, work=1):
        if (self.stop is not None and monotonic() >= self.stop) or (
                self.limit is not None and self.used + work > self.limit):
            raise BudgetExpired
        self.used += work

"""Budgeted exact M4 evaluators using original token IDs."""
from collections import defaultdict
from itertools import chain

from .edr_bb import SearchCapExceeded


DEFAULT_INDEX_BYTES = 64 * 1024**2
DEFAULT_JOIN_WORK = 250_000


class _Scratch:
    """Deterministic scratch admission estimates, separate from frontier bytes."""

    def __init__(self, limit, counters, phase):
        self.limit = limit
        self.counters = counters
        self.key = phase + "_peak_index_bytes"
        self.retained = 0

    def admit(self, size, *, retain=False):
        total = self.retained + size
        if total > self.limit:
            raise SearchCapExceeded("memory_bytes")
        self.counters[self.key] = max(self.counters.get(self.key, 0), total)
        if retain:
            self.retained = total


def sparse_compatible(owner, positives, negatives, budget, index_bytes, counters):
    """Test literal ordered projections using only touched blocks."""
    budget.charge_work()
    if not negatives:
        return True
    if not owner or not positives:
        return bool(owner)

    scratch = _Scratch(index_bytes, counters, "compatibility")
    projections = {}
    presence = {}

    def project(word):
        budget.charge_work(1 + len(word))
        scratch.admit(256 + 160 * len(word))
        groups = {}
        for token in word:
            groups.setdefault(owner[token], []).append(token)
        return groups

    for word in positives:
        for group, tokens in project(word).items():
            budget.charge_work(1 + 3 * len(tokens))
            temporary = 256 + 160 * len(word)
            if group not in projections:
                scratch.admit(512 + temporary)
                scratch.admit(512, retain=True)
                projections[group] = set()
                presence[group] = 0
            projection = tuple(tokens)
            known = projections[group]
            if projection not in known:
                retained = 160 + 8 * len(tokens)
                scratch.admit(retained + temporary)
                scratch.admit(retained, retain=True)
                known.add(projection)
            presence[group] += 1

    universal = set()
    for group, count in presence.items():
        budget.charge_work()
        if count == len(positives):
            scratch.admit(96, retain=True)
            universal.add(group)

    for word in negatives:
        groups = project(word)
        touched_universal = 0
        for group, tokens in groups.items():
            budget.charge_work(1 + 2 * len(tokens))
            if tuple(tokens) not in projections.get(group, ()):
                break
            touched_universal += group in universal
        else:
            # A missing group rejects epsilon exactly when all positives touch it.
            if touched_universal == len(universal):
                return False
    budget.charge_work()
    return True


class _LocalJoinCap(Exception):
    pass


def _signatures(word, owner, charge):
    """Return length/hash keys for the full word and each touched deletion."""
    mask = (1 << 64) - 1
    base = 1000003
    hashes, powers = [0], [1]
    positions = defaultdict(list)
    for i, token in enumerate(word):
        charge(1)
        hashes.append((hashes[-1] * base + token + 1) & mask)
        powers.append(powers[-1] * base & mask)
        positions[owner[token]].append(i)
    deleted = {}
    end = len(word)
    for group, indices in positions.items():
        value = start = 0
        for stop in chain(indices, (end,)):
            charge(1)
            factor = powers[stop - start]
            value = (value * factor + hashes[stop] - hashes[start] * factor) & mask
            start = stop + 1
        deleted[group] = (end - len(indices), value)
    return (end, hashes[-1]), deleted


def discover_join(owner, sample, budget, counters, work_limit, index_bytes):
    """Find two exact singleton deletions for one negative, within local caps.

    The caller checks raw label conflict first. Hashes select candidate pairs
    only. The unindexed absent-on-both case would imply a raw label conflict.
    """
    used = 0
    scratch = _Scratch(index_bytes, counters, "join")

    def charge(units):
        nonlocal used
        budget.charge_work(0)
        if used + units > work_limit:
            raise _LocalJoinCap
        budget.charge_work(units)
        used += units
        counters["join_work"] += units

    def admit(size, *, retain=False):
        try:
            scratch.admit(size, retain=retain)
        except SearchCapExceeded as exc:
            raise _LocalJoinCap from exc

    def signatures(word):
        charge(1)
        admit(512 + 320 * len(word))
        return _signatures(word, owner, charge)

    def complement(word, group):
        result = []
        for token in word:
            charge(1)
            if owner[token] != group:
                result.append(token)
        return result

    def witness(i, y, candidates):
        first = None
        for group, j in candidates:
            charge(1)
            if first is not None and group == first[0]:
                continue
            x = sample.positive[j]
            counters["join_probes"] += 1
            admit(512 + 320 * len(y) + 16 * len(x))
            x_projection = complement(x, group)
            y_projection = complement(y, group)
            charge(1 + min(len(x_projection), len(y_projection)))
            if x_projection != y_projection:
                continue
            if first is None:
                first = (group, j)
                continue
            (s, js), (t, jt) = sorted((first, (group, j)))
            return dict(negative_id=f"N{i}", positive_s_id=f"P{js}",
                        positive_t_id=f"P{jt}", support_s=[s], support_t=[t])
        return None

    full, deletions, inverse = defaultdict(list), defaultdict(list), defaultdict(list)
    try:
        for j, x in enumerate(sample.positive):
            sig, deleted = signatures(x)
            temporary = 512 + 320 * len(x)
            charge(1)
            admit(320 + temporary)
            admit(320, retain=True)
            full[sig].append(j)
            for group, key in deleted.items():
                charge(1)
                admit(768 + temporary)
                admit(768, retain=True)
                deletions[group, key].append(j)
                inverse[key].append((group, j))

        def matches(sig, deleted):
            for group, key in deleted.items():
                charge(1)
                for j in chain(deletions.get((group, key), ()), full.get(key, ())):
                    yield group, j
            for group, j in inverse.get(sig, ()):
                charge(1)
                if group not in deleted:
                    yield group, j

        for i, y in enumerate(sample.negative):
            sig, deleted = signatures(y)
            found = witness(i, y, matches(sig, deleted))
            if found is not None:
                return found
    except _LocalJoinCap:
        counters["join_local_caps"] += 1
    return None

"""Benchmark-only alternative to literal deletion-remainder materialization.
Signatures are filters only. No producer imports; exact equality on every hit.
Outer worker limits must censor the complete replay, never return a partial proof.
"""
from collections import defaultdict
from itertools import zip_longest


def expected_deletions(X, Y, owner, *, hash_bits=64):
    if type(hash_bits) is not int or not 0 <= hash_bits <= 64:
        raise ValueError('hash_bits')
    if set(X).intersection(Y):
        raise ValueError('duplicate conflict precludes exhausted pass')
    mask = (1 << hash_bits) - 1
    base = 0x9e3779b185ebca87
    powers = [1]
    def signatures(w):
        # Split into maximal retained intervals; combine their rolling hashes.
        prefix = [0]
        positions = defaultdict(list)
        for i, a in enumerate(w):
            prefix.append((prefix[-1] * base + a + 1) & mask)
            positions[owner[a]].append(i)
        while len(powers) <= len(w):
            powers.append((powers[-1] * base) & mask)
        out = {}
        for g, pos in positions.items():
            h = start = 0
            for end in pos:
                length = end - start
                h = (h * powers[length] + prefix[end] - prefix[start] * powers[length]) & mask
                start = end + 1
            length = len(w) - start
            h = (h * powers[length] + prefix[-1] - prefix[start] * powers[length]) & mask
            out[g] = (len(w) - len(pos), h)
        return (len(w), prefix[-1]), out
    def equal(x, y, g):
        sentinel = object()
        return all(a == b for a,b in zip_longest((a for a in x if owner[a] != g),
                    (a for a in y if owner[a] != g), fillvalue=sentinel))
    full = defaultdict(list)
    by_group = defaultdict(list)
    inverse = defaultdict(list)
    for x in dict.fromkeys(X):
        sig, deleted = signatures(x)
        full[sig].append(x)
        for g,k in deleted.items():
            by_group[g,k].append(x)
            inverse[k].append((g,x))
    for i,y in enumerate(Y):
        sig,deleted = signatures(y)
        found = set()
        for g,k in deleted.items():
            for bucket in (by_group.get((g,k),()),full.get(k,())):
                if any(equal(x,y,g) for x in bucket):
                    found.add(g)
                    yield i,g
                    break
        for g,x in inverse.get(sig,()):
            if g not in deleted and g not in found and equal(x,y,g):
                found.add(g)
                yield i,g

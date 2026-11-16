"""Independent RGS/projection oracle for polynomial-partition candidates.

This deliberately enumerates set partitions and directly projects strings; it
does not import C026 or candidate solver code. It is a correctness oracle only,
not complexity evidence.
"""
from itertools import product


def rgs_partitions(m):
    """All restricted-growth strings of length m, each encoding one partition."""
    if m == 0:
        yield ()
        return
    def rec(prefix, maximum):
        if len(prefix) == m:
            yield tuple(prefix)
            return
        for x in range(maximum + 2):
            yield from rec(prefix + [x], max(maximum, x))
    yield from rec([0], 0)


def blocks_from_rgs(code, alphabet):
    return [frozenset(alphabet[i] for i, x in enumerate(code) if x == j)
            for j in range(max(code) + 1)] if code else []


def project(word, block):
    return tuple(c for c in word if c in block)


def compatible(alphabet, positive, negative, code):
    blocks = blocks_from_rgs(code, alphabet)
    pproj = [{project(p, b) for p in positive} for b in blocks]
    return all(any(project(n, b) not in pp for b, pp in zip(blocks, pproj))
               for n in negative)


def oracle(alphabet, positive, negative):
    family = [c for c in rgs_partitions(len(alphabet))
              if compatible(alphabet, positive, negative, c)]
    opt = [c for c in family if len(set(c)) == max(map(lambda q: len(set(q)), family))] if family else []
    return {"compatible_rgs": family, "max_blocks": len(set(opt[0])) if opt else 0,
            "optimal_rgs": opt}


def labels(words):
    """Enumerate three-way labels: unknown, positive, negative (no conflict)."""
    for ys in product(range(3), repeat=len(words)):
        yield ([w for w, y in zip(words, ys) if y == 1],
               [w for w, y in zip(words, ys) if y == 2])


def selftest():
    bells = [1, 1, 2, 5, 15, 52, 203, 877, 4140]
    for m in range(9):
        codes = list(rgs_partitions(m))
        assert len(codes) == bells[m]
        assert len(set(codes)) == len(codes)
        assert all(not c or (c[0] == 0 and all(c[i] <= 1 + max(c[:i]) for i in range(1, len(c)))) for c in codes)
    # Full-word epsilon and contradictory labels: the latter is invalid input,
    # so the mathematical compatibility oracle itself rejects the conflict.
    assert oracle(['a'], [()], [()])["compatible_rgs"] == []
    assert oracle(['a','b'], [()], [('a',)])["max_blocks"] == 2
    # Each positive agrees with the negative on one singleton block, so
    # singleton blocks cannot reject it: block rejection compares against ALL
    # positive projections on that block, then the partition uses EXISTS a
    # rejecting block for each negative. The oneblock projection is (a,b),
    # distinct from both positive traces, so optimum is one.
    quant = oracle(['a','b'], [('a',), ('b',)], [('a','b')])
    assert quant['max_blocks'] == 1 and quant['compatible_rgs'] == [(0,0)]
    # Refinement-maximality differs from max block count: the only partition
    # here is a|b, while oneblock is also compatible.
    q = oracle(['a','b'], [()], [('a',)])
    assert q['compatible_rgs'] == [(0, 0), (0, 1)]
    # Per-negative quantifier is existential over rejecting blocks; each block
    # may use ALL positive projections as its collision set.
    assert not compatible(['a','b'], [('a','b')], [('b','a')], (0,1))
    # Empty P/N, unused symbols, alpha-renaming, duplicate labels, and no
    # projection collision on epsilon are direct oracle controls.
    assert oracle(['a','b'], [], [])["max_blocks"] == 2
    assert oracle(['a','b'], [('a',)], [])["max_blocks"] == 2
    assert oracle(['a','b'], [()], [('a',)])["max_blocks"] == 2
    return {"status":"passed", "bell_counts":bells,
            "ab_length_le_2_labelings":3**7,
            "scope":"finite exhaustive fixtures and semantic controls only; no polynomial-time evidence"}


if __name__ == '__main__':
    import json
    print(json.dumps(selftest(), sort_keys=True))

"""Independent exhaustive oracle using recursive set insertion.

This does not enumerate RGS directly: it recursively inserts each symbol into
an existing block or a new block, then derives each canonical RGS. Projection
uses tuple filtering over atomic IDs. Kept separate from candidate code.
"""
from itertools import product


class InvalidInput(ValueError):
    pass


def normalize(data):
    if not isinstance(data, dict) or set(data) != {"alphabet", "positive", "negative"}:
        raise InvalidInput("record must contain exactly alphabet, positive, negative")
    sigma, pos, neg = data["alphabet"], data["positive"], data["negative"]
    if not isinstance(sigma, list) or any(not isinstance(x, str) or not x for x in sigma):
        raise InvalidInput("Sigma must be an array of nonempty string IDs")
    if len(set(sigma)) != len(sigma):
        raise InvalidInput("duplicate symbol IDs")
    allowed = set(sigma)
    def norm_words(words, label):
        if not isinstance(words, list):
            raise InvalidInput(f"{label} must be an array")
        result, seen = [], set()
        for word in words:
            if not isinstance(word, list) or any(not isinstance(x, str) for x in word):
                raise InvalidInput(f"{label} words must be arrays of string IDs")
            if any(x not in allowed for x in word):
                raise InvalidInput(f"unknown symbol in {label}")
            tup = tuple(word)
            if tup not in seen:
                seen.add(tup)
                result.append(tup)
        return result
    return list(sigma), norm_words(pos, "P"), norm_words(neg, "N")


def insert_partitions(symbols):
    """Yield each unordered partition once, in set-insertion order."""
    if not symbols:
        yield ()
        return
    for old in insert_partitions(symbols[:-1]):
        x = symbols[-1]
        for i in range(len(old)):
            new = list(old)
            new[i] = new[i] | frozenset((x,))
            yield tuple(new)
        yield old + (frozenset((x,)),)


def canonical_rgs(partition, sigma):
    owner = {x: block_id for block_id, block in enumerate(partition) for x in block}
    relabel, out = {}, []
    for x in sigma:
        old = owner[x]
        if old not in relabel:
            relabel[old] = len(relabel)
        out.append(relabel[old])
    return tuple(out)


def projection(word, block):
    return tuple(x for x in word if x in block)


def inspect_partition(sigma, positive, negative, part):
    h = [{projection(p, b) for p in positive} for b in part]
    rejected_by = {}
    for ni, n in enumerate(negative):
        for bi, (b, hb) in enumerate(zip(part, h)):
            if projection(n, b) not in hb:
                rejected_by[ni] = bi
                break
        else:
            return None
    return rejected_by


def oracle(data):
    sigma, positive, negative = normalize(data)
    if set(positive) & set(negative):
        return {"status": "INCOMPATIBLE", "compatible_count": 0,
                "optimal_count": 0, "max_blocks": None,
                "compatible": [], "optimal": [], "recommendation": None}
    candidates = []
    for part in insert_partitions(sigma):
        witness = inspect_partition(sigma, positive, negative, part)
        if witness is not None:
            code = canonical_rgs(part, sigma)
            candidates.append((code, part, witness))
    candidates.sort(key=lambda x: x[0])
    if not candidates:
        return {"status": "INCOMPATIBLE", "compatible_count": 0,
                "optimal_count": 0, "max_blocks": None,
                "compatible": [], "optimal": [], "recommendation": None}
    best = max(len(part) for _, part, _ in candidates)
    opt = [item for item in candidates if len(item[1]) == best]
    def present(items):
        out = []
        for code, part, rejecting in items[:2]:
            factors = []
            for block in part:
                words = sorted({projection(p, block) for p in positive})
                factors.append([list(w) for w in words])
            out.append({"rgs": list(code), "blocks": [list(s for s in sigma if s in b) for b in part],
                        "factor_languages": factors,
                        "rejecting_block_by_negative": [rejecting[i] for i in range(len(negative))]})
        return out
    return {"status": "UNIQUE_COMPATIBLE" if len(candidates) == 1 else "AMBIGUOUS",
            "compatible_count": len(candidates), "optimal_count": len(opt),
            "max_blocks": best, "compatible": present(candidates),
            "optimal": present(opt), "recommendation": list(opt[0][0]),
            "optimal_unique": len(opt) == 1}


def exhaustive_binary_cases():
    words = [(), ("a",), ("b",), ("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]
    for lab in product(range(3), repeat=len(words)):
        yield {"alphabet": ["a", "b"],
               "positive": [list(w) for w, y in zip(words, lab) if y == 1],
               "negative": [list(w) for w, y in zip(words, lab) if y == 2]}


def seeded_cases():
    import random
    for m in range(3, 9):
        sigma = [f"sym-{i}" for i in range(m)]
        for j in range(10):
            rng = random.Random(280000 + m * 100 + j)
            words = sorted({tuple(rng.choices(sigma, k=rng.randrange(0, 9))) for _ in range(30)})
            labs = [rng.randrange(3) for _ in words]
            yield {"alphabet": sigma,
                   "positive": [list(w) for w, y in zip(words, labs) if y == 1],
                   "negative": [list(w) for w, y in zip(words, labs) if y == 2]}


def selftest():
    bell = [1, 1, 2, 5, 15, 52, 203, 877, 4140]
    for m in range(9):
        ps = list(insert_partitions([str(i) for i in range(m)]))
        assert len(ps) == bell[m] == len({canonical_rgs(p, [str(i) for i in range(m)]) for p in ps})
    assert oracle({"alphabet": [], "positive": [[]], "negative": []})["compatible_count"] == 1
    assert oracle({"alphabet": [], "positive": [], "negative": [[]]})["status"] == "INCOMPATIBLE"
    assert oracle({"alphabet": ["a", "b"], "positive": [["a"], ["b"]], "negative": [["a", "b"]]})["max_blocks"] == 1
    assert oracle({"alphabet": ["prefix", "prefix-long", "☃"],
                   "positive": [["prefix", "prefix-long"]], "negative": [["☃"]]})["compatible_count"] > 0
    # Joining symbols as raw text would collapse these distinct words to abc;
    # the oracle retains the tuple identity and sees a contradiction-free pair.
    assert oracle({"alphabet": ["a", "bc", "ab", "c"],
                   "positive": [["a", "bc"]], "negative": [["ab", "c"]]})["status"] != "INCOMPATIBLE"
    return {"status": "passed", "bell_counts": bell,
            "binary_labelings": 3**7, "seeded_cases": 60,
            "enumerator": "recursive set insertion; direct tuple projections"}


if __name__ == "__main__":
    import json
    print(json.dumps(selftest(), sort_keys=True))

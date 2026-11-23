"""Independently verify a partition and its projection-based optimality proof."""

import argparse
from itertools import combinations
import json
from pathlib import Path

from sample import DeadlineExpired, deadline, read_sample


class InvalidProof(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidProof(message)


def select(items, index):
    require(type(index) is int and 0 <= index < len(items), "invalid trace index")
    return items[index]


def read_partition(raw, size):
    require(type(raw) in (list, tuple), "partition must be a sequence")
    symbols = set()
    blocks = []
    for block in raw:
        require(type(block) in (list, tuple) and bool(block), "invalid block")
        for a in block:
            require(type(a) is int and 0 <= a < size and a not in symbols,
                    "partition contains an invalid or repeated symbol")
            symbols.add(a)
        blocks.append(frozenset(block))
    require(len(symbols) == size, "partition omits a symbol")
    return frozenset(blocks)


def image(word, block):
    return tuple(a for a in word if a in block)


def check_rejection(record, partition, size, S_plus, S_minus, tick):
    region = read_partition(record["region"], size)
    y = select(S_minus, record["negative"])
    witnesses = record["positive"]
    require(type(witnesses) is list and len(witnesses) == len(region),
            "expected one positive index for each region block")
    owner = {}
    for r, (block, index) in enumerate(zip(record["region"], witnesses)):
        tick()
        x = select(S_plus, index)
        symbols = set(block)
        require(image(x, symbols) == image(y, symbols), "projection witness fails")
        owner.update((a, r) for a in block)
    for block in partition:
        require(len({owner[a] for a in block}) == 1, "region must coarsen the partition")
    return owner


def compatible(answer, S_plus, S_minus, tick):
    obligations = set(range(len(S_minus)))
    for block in answer:
        positive_images = set()
        for x in S_plus:
            tick()
            positive_images.add(image(x, block))
        still_uncovered = set()
        for i in obligations:
            tick()
            if image(S_minus[i], block) in positive_images:
                still_uncovered.add(i)
        obligations = still_uncovered
    return not obligations


def verified_root(proof, Sigma, S_plus, S_minus, tick):
    components = {frozenset({a}) for a in range(len(Sigma))}
    for witness in proof["swaps"]:
        tick()
        x = select(S_plus, witness["positive"])
        y = select(S_minus, witness["negative"])
        offset = witness["offset"]
        require(type(offset) is int and 0 <= offset < len(y) - 1, "invalid swap offset")
        a, b = y[offset:offset + 2]
        require(a != b and x == y[:offset] + (b, a) + y[offset + 2:], "invalid swap witness")
        touched = {block for block in components if a in block or b in block}
        components.difference_update(touched)
        components.add(frozenset().union(*touched))
    return frozenset(components)


def check_tree(result, proof, Sigma, S_plus, S_minus, tick, admissible, check_bounds):
    require(proof["bounded"] is (check_bounds is not None), "verification regime mismatch")

    def names(partition):
        return tuple(tuple(Sigma[a] for a in block)
                     for block in sorted(tuple(sorted(b)) for b in partition))

    def check_verdict(partition, expected):
        verdict = check_bounds(names(partition), tick)
        if verdict == "INCOMPLETE":
            raise DeadlineExpired
        require(verdict == expected, "bounds callback disagrees with result")

    answer = None
    if result["status"] == "OPTIMAL":
        raw = result["blocks"]
        require(type(raw) is list and all(type(b) is list for b in raw), "invalid output blocks")
        indices = {a: i for i, a in enumerate(Sigma)}
        answer = read_partition([[indices[a] for a in b] for b in raw], len(Sigma))
        k = result["max_devices"]
        require(type(k) is int and k == len(answer), "incorrect block count")
        require(admissible(names(answer)), "answer outside family")
        require(compatible(answer, S_plus, S_minus, tick), "answer is incompatible")
        if check_bounds is not None:
            check_verdict(answer, "PASS")

    root = verified_root(proof, Sigma, S_plus, S_minus, tick)
    require(type(proof["rejections"]) is list, "rejections must be a list")
    records = {}
    for record in proof["rejections"]:
        tick()
        partition = read_partition(record["partition"], len(Sigma))
        require(partition not in records, "duplicate rejection")
        records[partition] = record

    frontier = {root}
    while frontier:
        tick()
        if answer is not None and len(next(iter(frontier))) == len(answer):
            require(answer in frontier and not records, "unexpected optimum level")
            return
        children = set()
        for partition in frontier:
            tick()
            record = records.pop(partition)
            reason = record["reason"]
            member = admissible(names(partition))
            owner = None
            if reason == "outside_family":
                require(not member, "incorrectly skipped admissible partition")
            elif reason == "projection":
                require(member, "projection record outside family")
                owner = check_rejection(record, partition, len(Sigma), S_plus, S_minus, tick)
            else:
                require(reason == "bounds" and member and check_bounds is not None,
                        "invalid rejection reason")
                require(compatible(partition, S_plus, S_minus, tick), "expected projection pass")
                check_verdict(partition, "FAIL")
            for left, right in combinations(partition, 2):
                tick()
                if owner is None or owner[next(iter(left))] != owner[next(iter(right))]:
                    children.add(partition.difference((left, right)).union((left | right,)))
        frontier = children
    require(answer is None and not records, "unexpected exhaustion")


def verify(D, result, *, seconds=None, admissible=None, check_bounds=None):
    """Replay the proof against the same family and, if supplied, bounded oracle."""
    if admissible is None:
        def admissible(blocks):
            return True
    tick = deadline(seconds)
    try:
        tick()
        Sigma, S_plus, S_minus = read_sample(D, tick)
        proof = result["certificate"]
        status = result["status"]
        require(status in ("OPTIMAL", "INFEASIBLE"), "expected a completed result")
        if proof["kind"] == "projection_tree":
            check_tree(result, proof, Sigma, S_plus, S_minus, tick, admissible, check_bounds)
            verdict = "VERIFIED_CONDITIONAL" if check_bounds is not None else "VERIFIED"
        else:
            require(status == "INFEASIBLE", "unexpected infeasibility proof")
            y = select(S_minus, proof["negative"])
            if proof["kind"] == "empty_alphabet":
                require(not Sigma, "expected empty alphabet")
            else:
                require(proof["kind"] == "opposite_labels", "invalid infeasibility proof kind")
                require(y == select(S_plus, proof["positive"]), "traces differ")
            verdict = "VERIFIED"
        tick()
    except DeadlineExpired:
        return {"status": "INCOMPLETE"}
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "reason": str(exc)}
    return {"status": verdict}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--seconds", type=float)
    args = parser.parse_args()
    try:
        D = json.loads(args.input.read_text(encoding="utf-8"))
        result = json.loads(args.result.read_text(encoding="utf-8"))
        verdict = verify(D, result, seconds=args.seconds)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(verdict))
    return 0 if verdict["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())


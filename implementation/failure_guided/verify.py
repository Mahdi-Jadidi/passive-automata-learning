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


def check_optimal(result, proof, Sigma, S_plus, S_minus, tick):
    raw = result["blocks"]
    require(type(raw) is list and all(type(b) is list for b in raw), "invalid output blocks")
    indices = {a: i for i, a in enumerate(Sigma)}
    answer = read_partition([[indices[a] for a in b] for b in raw], len(Sigma))
    k = result["max_devices"]
    require(type(k) is int and k == len(answer), "incorrect block count")
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
    require(not obligations, "answer is incompatible")

    require(proof["kind"] == "projection_tree", "invalid optimality proof kind")
    require(type(proof["rejections"]) is list, "rejections must be a list")
    at_level = {}
    for record in proof["rejections"]:
        tick()
        partition = read_partition(record["partition"], len(Sigma))
        require(len(partition) >= k and partition != answer, "unexpected rejection")
        level = at_level.setdefault(len(partition), {})
        require(partition not in level, "duplicate rejection")
        level[partition] = record

    frontier = {frozenset(frozenset({a}) for a in range(len(Sigma)))}
    for count in range(len(Sigma), k - 1, -1):
        tick()
        level = at_level.get(count, {})
        if count == k:
            require(answer in frontier and level.keys() <= frontier, "unexpected optimum level")
            for partition, record in level.items():
                check_rejection(record, partition, len(Sigma), S_plus, S_minus, tick)
            return
        require(level.keys() == frontier, "missing or unexpected rejection at a cheaper level")
        children = set()
        for partition in frontier:
            owner = check_rejection(level[partition], partition, len(Sigma), S_plus, S_minus, tick)
            for left, right in combinations(partition, 2):
                tick()
                if owner[next(iter(left))] != owner[next(iter(right))]:
                    children.add(partition.difference((left, right)).union((left | right,)))
        frontier = children


def verify(D, result, *, seconds=None):
    tick = deadline(seconds)
    try:
        tick()
        Sigma, S_plus, S_minus = read_sample(D, tick)
        proof = result["certificate"]
        if result["status"] == "INFEASIBLE":
            y = select(S_minus, proof["negative"])
            if proof["kind"] == "empty_alphabet":
                require(not Sigma, "expected empty alphabet")
            else:
                require(proof["kind"] == "opposite_labels", "invalid infeasibility proof kind")
                require(y == select(S_plus, proof["positive"]), "traces differ")
        else:
            require(result["status"] == "OPTIMAL", "expected a completed result")
            check_optimal(result, proof, Sigma, S_plus, S_minus, tick)
        tick()
    except DeadlineExpired:
        return {"status": "INCOMPLETE"}
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "reason": str(exc)}
    return {"status": "VERIFIED"}


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


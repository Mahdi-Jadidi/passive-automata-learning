"""Certifying breadth-first partition search with projection feedback."""

import argparse
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

from sample import DeadlineExpired, deadline, read_sample


def merge(partition, left, right):
    joined = tuple(sorted(left + right))
    return tuple(sorted([b for b in partition if b not in (left, right)] + [joined]))


class ProjectionMatches:
    def __init__(self, S_plus, S_minus, tick):
        self.S_plus = S_plus
        self.S_minus = S_minus
        self.tick = tick
        self.cache = {}

    def project(self, word, symbols):
        image = []
        for symbol in word:
            self.tick()
            if symbol in symbols:
                image.append(symbol)
        return tuple(image)

    def row(self, block):
        if block not in self.cache:
            symbols = set(block)
            first_positive = {}
            for j, word in enumerate(self.S_plus):
                self.tick()
                first_positive.setdefault(self.project(word, symbols), j)
            matches = []
            for word in self.S_minus:
                self.tick()
                matches.append(first_positive.get(self.project(word, symbols)))
            self.cache[block] = tuple(matches)
        return self.cache[block]

    def first_failure(self, partition):
        if not self.S_minus:
            return None
        rows = [self.row(block) for block in partition]
        for i in range(len(self.S_minus)):
            self.tick()
            if all(row[i] is not None for row in rows):
                return i
        return None


def rejection_region(partition, i, matches, mode):
    region = partition
    while mode != "baseline":
        for left, right in combinations(region, 2):
            matches.tick()
            if matches.row(tuple(sorted(left + right)))[i] is not None:
                region = merge(region, left, right)
                break
        else:
            break
        if mode == "first":
            break
    witnesses = [matches.row(block)[i] for block in region]
    return region, witnesses


def search_levels(Sigma, matches, mode, order, stats):
    root = tuple((a,) for a in range(len(Sigma)))
    frontier = {root: 0}
    stats["generated"] = 1
    records = []
    while frontier:
        failures = []
        for partition in sorted(frontier, key=lambda p: (-frontier[p], p)):
            matches.tick()
            i = matches.first_failure(partition)
            stats["tested"] += 1
            if i is None:
                for failed, negative in failures:
                    matches.tick()
                    region, witnesses = rejection_region(failed, negative, matches, "baseline")
                    records.append({"partition": failed, "region": region,
                                    "negative": negative, "positive": witnesses})
                blocks = [[Sigma[a] for a in block] for block in partition]
                return {"status": "OPTIMAL", "blocks": blocks, "max_devices": len(blocks),
                        "certificate": {"kind": "projection_tree", "rejections": records}}

            failures.append((partition, i))

        next_frontier = {}
        for partition, i in failures:
            start = perf_counter()
            region, witnesses = rejection_region(partition, i, matches, mode)
            stats["region_seconds"] += perf_counter() - start
            records.append({"partition": partition, "region": region,
                            "negative": i, "positive": witnesses})
            owners = {a: r for r, block in enumerate(region) for a in block}
            uncovered = []
            if order == "gain":
                rows = [matches.row(block) for block in partition]
                for j in range(len(matches.S_minus)):
                    matches.tick()
                    if all(row[j] is not None for row in rows):
                        uncovered.append(j)
            for left, right in combinations(partition, 2):
                matches.tick()
                if owners[left[0]] == owners[right[0]]:
                    continue
                stats["child_edges"] += 1
                child = merge(partition, left, right)
                gain = 0
                if uncovered:
                    merged_row = matches.row(tuple(sorted(left + right)))
                    for j in uncovered:
                        matches.tick()
                        gain += merged_row[j] is None
                if child not in next_frontier:
                    stats["generated"] += 1
                    next_frontier[child] = gain
                else:
                    next_frontier[child] = max(next_frontier[child], gain)
        frontier = next_frontier
    raise AssertionError("disjoint sample with nonempty alphabet has a compatible partition")


def solve(D, *, mode="first", order="canonical", seconds=None):
    if mode not in {"baseline", "first", "maximal"} or order not in {"canonical", "gain"}:
        raise ValueError("unknown search mode or order")
    tick = deadline(seconds)
    stats = dict(generated=0, tested=0, child_edges=0, region_seconds=0.0)
    try:
        tick()
        Sigma, S_plus, S_minus = read_sample(D, tick)
        positives = {word: j for j, word in enumerate(S_plus)}
        for i, word in enumerate(S_minus):
            tick()
            if not Sigma or word in positives:
                kind = "empty_alphabet" if not Sigma else "opposite_labels"
                result = {"status": "INFEASIBLE", "certificate": {"kind": kind, "negative": i}}
                if Sigma:
                    result["certificate"]["positive"] = positives[word]
                break
        else:
            matches = ProjectionMatches(S_plus, S_minus, tick)
            result = search_levels(Sigma, matches, mode, order, stats)
        tick()
    except DeadlineExpired:
        result = {"status": "INCOMPLETE"}
    return {**result, "stats": stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=["baseline", "first", "maximal"], default="first")
    parser.add_argument("--order", choices=["canonical", "gain"], default="canonical")
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        D = json.loads(args.input.read_text(encoding="utf-8"))
        result = solve(D, mode=args.mode, order=args.order, seconds=args.seconds)
        payload = json.dumps(result, ensure_ascii=True, indent=2)
        if args.output:
            args.output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()


"""Certifying breadth-first partition search with projection feedback."""

import argparse
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

from analysis import analyze_traces, contract, exact_components
from packing import DeletionWitnesses, propose
from sample import DeadlineExpired, deadline


def merge(partition, left, right):
    joined = tuple(sorted(left + right))
    return tuple(sorted([b for b in partition if b not in (left, right)] + [joined]))


class ProjectionMatches:
    def __init__(self, S_plus, S_minus, tick):
        self.S_plus = S_plus
        self.S_minus = S_minus
        self.tick = tick
        self.cache = {}
        self.images = 0
        self.queries = 0
        self.cache_misses = 0

    def project(self, word, symbols):
        self.images += 1
        image = []
        for symbol in word:
            self.tick()
            if symbol in symbols:
                image.append(symbol)
        return tuple(image)

    def row(self, block):
        self.queries += 1
        if block not in self.cache:
            self.cache_misses += 1
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


def select_region(partition, first, matches, mode, policy):
    candidates = [first]
    if policy == "best-three" and mode != "baseline":
        rows = [matches.row(block) for block in partition]
        by_word = {}
        for i, word in enumerate(matches.S_minus):
            matches.tick()
            if all(row[i] is not None for row in rows):
                by_word.setdefault(word, i)
        candidates = [by_word[word] for word in sorted(by_word)[:3]]

    best = None
    best_hidden = -1
    for i in candidates:
        region, positives = rejection_region(partition, i, matches, mode)
        owners = {a: r for r, block in enumerate(region) for a in block}
        counts = [0] * len(region)
        for block in partition:
            counts[owners[block[0]]] += 1
        hidden = sum(t * (t - 1) // 2 for t in counts)
        if hidden > best_hidden:
            best = i, region, positives
            best_hidden = hidden
    return best


def optimal(Sigma, partition, proof):
    full = sorted((*partition, *((a,) for a in proof["unused"])))
    return {"status": "OPTIMAL", "blocks": [[Sigma[a] for a in b] for b in full],
            "max_devices": len(full), "certificate": proof}


def one_negative(Sigma, root, matches, proof, stats):
    for size in range(1, len(root) + 1):
        for chosen in combinations(root, size):
            matches.tick()
            block = tuple(sorted(a for b in chosen for a in b))
            stats["subsets_tested"] += 1
            if matches.row(block)[0] is None:
                proof.update(kind="one_negative", separating=block)
                return optimal(Sigma, sorted([b for b in root if b not in chosen] + [block]), proof)
    raise AssertionError("the full active alphabet separates disjoint traces")


def search_levels(Sigma, root, proof, matches, mode, order, stats, admissible, check_bounds, policy, mining, strength, incumbent, staged_root, root_failure):
    frontier = {root: 0}
    stats["generated"] = 1
    records = proof['rejections']
    while frontier:
        if incumbent is not None and len(next(iter(frontier))) <= len(incumbent):
            return optimal(Sigma, incumbent, proof)
        failures = []
        for partition in sorted(frontier, key=lambda p: (-frontier[p], p)):
            matches.tick()
            blocks = tuple(tuple(Sigma[a] for a in block) for block in partition)
            if not admissible(blocks):
                failures.append((partition, "outside_family", None))
                continue
            if partition == root and staged_root is not None:
                i = root_failure
            else:
                i = matches.first_failure(partition)
                stats["tested"] += 1
            if i is not None:
                failures.append((partition, "projection", i))
                continue
            if check_bounds is not None:
                verdict = check_bounds(blocks, matches.tick)
                if verdict == "INCOMPLETE":
                    raise DeadlineExpired
                if verdict == "FAIL":
                    failures.append((partition, "bounds", None))
                    continue
                if verdict != "PASS":
                    raise ValueError("bounds callback must return PASS, FAIL, or INCOMPLETE")
            return optimal(Sigma, partition, proof)

        next_frontier = {}
        for partition, kind, i in failures:
            record = {"partition": partition, "reason": kind}
            region = partition
            if mining is not None and strength == "nodes" and kind == "projection":
                bound, chosen = (staged_root if partition == root else
                                 measure_bound(mining, partition, matches, stats))
                if incumbent is not None and len(partition) - bound <= len(incumbent):
                    records.append({**record, "reason": "weighted",
                                    "bounds": [entry[3] for entry in chosen]})
                    stats["weighted_prunes"] += 1
                    continue
            if kind == "projection":
                start = perf_counter()
                i, region, positive = select_region(partition, i, matches, mode, policy)
                stats["region_seconds"] += perf_counter() - start
                record.update(region=region, negative=i, positive=positive)
            records.append(record)
            owners = {a: r for r, block in enumerate(region) for a in block}
            uncovered = []
            if order == "gain" and kind == "projection":
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
    if incumbent is not None:
        return optimal(Sigma, incumbent, proof)
    return {"status": "INFEASIBLE", "certificate": proof}


def measure_bound(mining, partition, matches, stats):
    started = perf_counter()
    try:
        return mining.bound(partition, matches)
    finally:
        stats["packing_seconds"] += perf_counter() - started


def solve(D, *, mode="first", order="canonical", seconds=None, preprocess=True,
          admissible=None, check_bounds=None, shortcuts=True, policy="first", exact_root=False, strength="nodes"):
    """Callbacks take canonical tuples of symbol names. Bind sample and bounds externally."""
    if mode not in {"baseline", "first", "maximal"} or order not in {"canonical", "gain"}:
        raise ValueError("unknown search mode or order")
    if policy not in {"first", "best-three"}:
        raise ValueError("unknown negative selection policy")
    unrestricted = admissible is None and check_bounds is None
    if strength not in {"off", "candidate", "root", "nodes"}:
        raise ValueError("unknown weighting mode")
    if not unrestricted:
        strength = "off"
    if exact_root and not unrestricted:
        raise ValueError("exact experimental root requires all partitions without bounds")
    if admissible is None:
        def admissible(blocks):
            return True
    tick = deadline(seconds)
    stats = dict(generated=0, tested=0, child_edges=0, region_seconds=0.0, analysis_seconds=0.0, subsets_tested=0, root_blocks=0)
    stats.update(packing_seconds=0.0, proposal_seconds=0.0, proposal_tests=0,
                 proposal_queries=0, root_lower=None, upper=None, weighted_prunes=0)
    matches = None
    start = perf_counter()
    try:
        tick()
        try:
            analysis = analyze_traces(D, tick)
            if not isinstance(analysis, dict):
                Sigma, S_plus, S_minus, root = analysis
                matches = ProjectionMatches(S_plus, S_minus, tick)
                unused = []
                if unrestricted and shortcuts:
                    observed = set()
                    for word in (*S_plus, *S_minus):
                        for a in word:
                            tick()
                            observed.add(a)
                    unused = [b[0] for b in root if b[0] not in observed]
                    if root and len(unused) == len(root):
                        unused = unused[1:]
                    unused_set = set(unused)
                    root = tuple(b for b in root if b[0] not in unused_set)
                steps = []
                if preprocess and S_plus and S_minus and len(root) > 1:
                    root, steps = contract(root, matches)
                if exact_root:
                    if len(root) > 10:
                        raise ValueError("experimental exact root is limited to ten components")
                    root = exact_components(root, matches)
                proof = {"kind": "projection_tree", "bounded": check_bounds is not None,
                         "contractions": steps, "unused": unused, "exact_root": exact_root,
                         "rejections": []}
                stats["root_blocks"] = len(root)
        finally:
            stats["analysis_seconds"] = perf_counter() - start
        if isinstance(analysis, dict):
            result = {"status": "INFEASIBLE", "certificate": analysis}
        else:
            incumbent = None
            mining = None
            staged_root = None
            root_failure = None
            result = None
            if strength != "off" and root and S_plus and S_minus:
                stats["generated"] = stats["tested"] = 1
                root_failure = matches.first_failure(root)
                if root_failure is None:
                    result = optimal(Sigma, root, proof)
                else:
                    mining = DeletionWitnesses(S_plus, S_minus, tick)
                    staged_root = measure_bound(mining, root, matches, stats)
                    bound, chosen = staged_root
                    began = perf_counter()
                    before_queries = matches.queries
                    try:
                        candidate = propose(root, chosen, matches)
                    finally:
                        stats["proposal_seconds"] += perf_counter() - began
                        stats["proposal_queries"] += matches.queries - before_queries
                    stats["proposal_tests"] = int(bool(chosen))
                    incumbent = candidate or (tuple(sorted(a for b in root for a in b)),)
                    base_cost = len(Sigma) - len(root) - len(proof["unused"])
                    stats["root_lower"] = base_cost + bound
                    stats["upper"] = base_cost + len(root) - len(incumbent)
                    proof["incumbent_search"] = True
                    if strength in {"root", "nodes"} and len(root) - bound <= len(incumbent):
                        proof.update(kind="weighted_root", bounds=[entry[3] for entry in chosen])
                        result = optimal(Sigma, incumbent, proof)
            if result is None and strength == "off" and unrestricted and shortcuts and len(S_minus) == 1:
                result = one_negative(Sigma, root, matches, proof, stats)
            if result is None:
                result = search_levels(Sigma, root, proof, matches, mode, order, stats,
                                       admissible, check_bounds, policy, mining, strength,
                                       incumbent, staged_root, root_failure)
        tick()
    except DeadlineExpired:
        result = {"status": "INCOMPLETE"}
    if matches is not None:
        stats.update(projection_queries=matches.queries, projection_cache_misses=matches.cache_misses,
                     projection_images=matches.images)
    return {**result, "stats": stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=["baseline", "first", "maximal"], default="maximal")
    parser.add_argument("--strength", choices=["off", "candidate", "root", "nodes"], default="nodes")
    parser.add_argument("--order", choices=["canonical", "gain"], default="canonical")
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--no-preprocess", action="store_true")
    parser.add_argument("--no-shortcuts", action="store_true")
    parser.add_argument("--policy", choices=["first", "best-three"], default="first")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        D = json.loads(args.input.read_text(encoding="utf-8"))
        result = solve(D, mode=args.mode, order=args.order, seconds=args.seconds,
                       preprocess=not args.no_preprocess, shortcuts=not args.no_shortcuts,
                       policy=args.policy, strength=args.strength)
        payload = json.dumps(result, ensure_ascii=True, indent=2)
        if args.output:
            args.output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()


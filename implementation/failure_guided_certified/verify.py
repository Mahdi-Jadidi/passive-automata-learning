"""Independently verify a partition and its projection-based optimality proof."""

import argparse
from collections import Counter
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


def read_partition(raw, alphabet):
    require(type(raw) in (list, tuple), "partition must be a sequence")
    symbols = set()
    blocks = []
    for block in raw:
        require(type(block) in (list, tuple) and bool(block), "invalid block")
        for a in block:
            require(type(a) is int and a in alphabet and a not in symbols,
                    "partition contains an invalid or repeated symbol")
            symbols.add(a)
        blocks.append(frozenset(block))
    require(symbols == alphabet, "partition omits a symbol")
    return frozenset(blocks)


def image(word, block):
    return tuple(a for a in word if a in block)


def check_rejection(record, partition, alphabet, S_plus, S_minus, tick):
    region = read_partition(record["region"], alphabet)
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


def verified_root(proof, alphabet, S_plus, S_minus, tick):
    components = {frozenset({a}) for a in alphabet}
    for step in proof["contractions"]:
        tick()
        y = select(S_minus, step["negative"])
        deleted = set()
        require(type(step["deleted"]) is list, "invalid deletion evidence")
        for witness in step["deleted"]:
            tick()
            raw = witness["block"]
            block = frozenset(raw)
            require(len(raw) == len(block) and all(type(a) is int for a in raw), "invalid symbol index")
            require(block in components and block not in deleted, "expected distinct current components")
            x = select(S_plus, witness["positive"])
            complement = alphabet - block
            require(image(x, complement) == image(y, complement), "invalid deletion witness")
            deleted.add(block)
        require(len(deleted) >= 2, "contraction must join two or more components")
        components.difference_update(deleted)
        components.add(frozenset().union(*deleted))
    if proof["exact_root"]:
        require(len(components) <= 10, "exact root exceeds ten components")
        base = list(components)
        groups = [frozenset(alphabet)] if alphabet else []
        for mask in range(1, 1 << len(base), 2):
            tick()
            left = frozenset().union(*(b for i, b in enumerate(base) if mask & (1 << i)))
            right = alphabet - left
            if right and compatible((left, right), S_plus, S_minus, tick):
                groups = [part for g in groups for part in (g & left, g & right) if part]
        components = groups
    return frozenset(components)


def weighted_bound(raw, partition, active, S_plus, S_minus, tick):
    require(type(raw) is list, "expected weighted witness list")
    atoms = sorted(tuple(sorted(block)) for block in partition)
    used = set()
    seen = set()
    bound = 0
    for record in raw:
        tick()
        i = record["negative"]
        y = select(S_minus, i)
        require(i not in seen, "repeated negative")
        seen.add(i)
        weights = Counter()
        loads = Counter()
        edges = {}
        rows = record["deletions"]
        require(type(rows) is list and bool(rows), "expected deletion records")
        for row in rows:
            tick()
            x = select(S_plus, row["positive"])
            indices = row["atoms"]
            require(type(indices) in (list, tuple) and bool(indices), "invalid deletion atoms")
            for k in indices:
                select(atoms, k)
            edge = frozenset(indices)
            require(len(edge) == len(indices) and edge not in weights, "duplicate deletion")
            weight = row["weight"]
            require(type(weight) is int and 1 <= weight <= 2, "invalid weight")
            deleted = {a for k in edge for a in atoms[k]}
            remaining = active - deleted
            require(image(x, remaining) == image(y, remaining), "invalid weighted projection")
            weights[edge] = weight
            for k in edge:
                loads[k] += weight
                require(loads[k] <= 2, "weighted load exceeds capacity")
                edges.setdefault(k, set()).add(edge)
        require(used.isdisjoint(loads), "overlapping weighted supports")
        used.update(loads)
        unseen = set(loads)
        d = 0
        while unseen:
            todo = [unseen.pop()]
            component = set()
            maximum = 0
            while todo:
                tick()
                k = todo.pop()
                maximum = max(maximum, loads[k])
                for edge in edges[k] - component:
                    component.add(edge)
                    added = unseen & edge
                    unseen.difference_update(added)
                    todo.extend(added)
            total = sum(weights[edge] for edge in component)
            d += (total + maximum - 1) // maximum
        bound += max(0, d - 1)
    return bound


def check_tree(result, proof, Sigma, S_plus, S_minus, tick, admissible, check_bounds, unrestricted):
    require(proof["bounded"] is (check_bounds is not None), "verification regime mismatch")
    require(type(proof["exact_root"]) is bool, "invalid root mode")
    raw_unused = proof["unused"]
    removed = set(raw_unused)
    require(len(raw_unused) == len(removed) and
            all(type(a) is int and 0 <= a < len(Sigma) for a in removed), "invalid unused symbols")
    require(unrestricted or (not removed and not proof["exact_root"]), "unsupported reduction")
    for word in (*S_plus, *S_minus):
        tick()
        require(removed.isdisjoint(word), "removed symbol occurs in sample")
    active = set(range(len(Sigma))) - removed
    require(active or not Sigma, "retain one symbol for a nonempty alphabet")
    root = verified_root(proof, active, S_plus, S_minus, tick)

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
        answer = read_partition([[indices[a] for a in b] for b in raw], set(range(len(Sigma))))
        k = result["max_devices"]
        require(type(k) is int and k == len(answer), "incorrect block count")
        require(admissible(names(answer)), "answer outside family")
        require(compatible(answer, S_plus, S_minus, tick), "answer is incompatible")
        if check_bounds is not None:
            check_verdict(answer, "PASS")

        for a in removed:
            require(frozenset({a}) in answer, "expected unused singleton")
        answer = answer - {frozenset({a}) for a in removed}

    incumbent_search = proof.get("incumbent_search", False)
    require(type(incumbent_search) is bool, "bad search regime")
    if incumbent_search or proof["kind"] == "weighted_root":
        require(unrestricted and answer is not None, "expected unrestricted feasible incumbent")
        require(all(any(atom <= b for b in answer) for atom in root),
                "incumbent must coarsen certified root")
    if proof["kind"] == "weighted_root":
        require(not proof["rejections"], "unexpected search records")
        bound = weighted_bound(proof["bounds"], root, active, S_plus, S_minus, tick)
        require(len(root) - bound <= len(answer), "root bound does not close the gap")
        return

    if proof["kind"] == "one_negative":
        require(unrestricted and answer is not None and len(S_minus) == 1,
                "invalid one-negative proof regime")
        raw = proof["separating"]
        block = frozenset(raw)
        require(len(raw) == len(block) and all(type(a) is int for a in raw), "invalid union symbols")
        chosen = {b for b in root if b <= block}
        require(chosen and frozenset().union(*chosen) == block, "invalid separating union")
        require(answer == (root - chosen) | {block}, "answer does not match separating union")
        require(compatible((block,), S_plus, S_minus, tick), "claimed union cannot separate")
        for size in range(1, len(chosen)):
            for subset in combinations(root, size):
                tick()
                union = frozenset().union(*subset)
                require(not compatible((union,), S_plus, S_minus, tick), "smaller separator exists")
        require(not proof["rejections"], "unexpected search records")
        return
    require(type(proof["rejections"]) is list, "rejections must be a list")
    records = {}
    for record in proof["rejections"]:
        tick()
        partition = read_partition(record["partition"], active)
        require(partition not in records, "duplicate rejection")
        records[partition] = record

    frontier = {root}
    while frontier:
        tick()
        if answer is not None and len(next(iter(frontier))) == len(answer):
            require((incumbent_search or answer in frontier) and not records, "unexpected optimum level")
            return
        children = set()
        for partition in frontier:
            tick()
            record = records.pop(partition)
            reason = record["reason"]
            member = admissible(names(partition))
            owner = None
            if reason == "weighted":
                require(incumbent_search, "weighted pruning requires a verified incumbent")
                bound = weighted_bound(record["bounds"], partition, active, S_plus, S_minus, tick)
                require(len(partition) - bound <= len(answer), "branch bound does not close the gap")
                continue
            if reason == "outside_family":
                require(not member, "incorrectly skipped admissible partition")
            elif reason == "projection":
                require(member, "projection record outside family")
                owner = check_rejection(record, partition, active, S_plus, S_minus, tick)
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
    require((answer is None or incumbent_search) and not records, "unexpected exhaustion")


def verify(D, result, *, seconds=None, admissible=None, check_bounds=None):
    """Replay the proof against the same family and, if supplied, bounded oracle."""
    unrestricted = admissible is None and check_bounds is None
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
        if proof["kind"] in ("projection_tree", "one_negative", "weighted_root"):
            check_tree(result, proof, Sigma, S_plus, S_minus, tick, admissible, check_bounds, unrestricted)
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
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
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



"""Exact alphabet partition selection using only certified facts and complete queries."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

from model import ProjectionOracle, analyze, merge, ordered, union
from sample import DeadlineExpired, deadline


def fingerprint(D):
    raw = json.dumps(D, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()


def within(block, region):
    return block & region == block


class Evidence:
    def __init__(self, negatives, tick):
        self.zeros = [dict() for _ in range(negatives)]
        self.ones = [set() for _ in range(negatives)]
        self.tick = tick

    def zero(self, item):
        i, region = item["i"], item["region"]
        known = self.zeros[i]
        for other in tuple(known):
            self.tick()
            if within(region, other):
                return
            if within(other, region):
                del known[other]
        known[region] = item

    def ingest(self, reply, query):
        for table in reply["tables"]:
            block = table["block"]
            for i, j in table["zeros"]:
                self.tick()
                self.zero({"i": i, "j": j, "region": block, "source": query, "rule": "S01"})
            for group in table["free"]:
                for i in group:
                    self.tick()
                    known = self.ones[i]
                    if any(within(other, block) for other in known):
                        continue
                    known.difference_update([other for other in known if within(block, other)])
                    known.add(block)

    def regions(self, partition, *, coarsen):
        for i, known in enumerate(self.zeros):
            self.tick()
            # The masks of covered atoms coincide with their symbol union.
            hits = {}
            for region, item in known.items():
                covered = 0
                for block in partition:
                    self.tick()
                    if within(block, region):
                        covered |= block
                if covered:
                    hits.setdefault(covered, item)
            if union(hits) != union(partition):
                continue
            remaining = list(partition)
            groups, witnesses = [], []
            while remaining:
                self.tick()
                first = remaining[0]
                options = [key for key in hits if within(first, key)]
                choice = max(options, key=lambda key: sum(within(b, key) for b in remaining)) if coarsen else options[0]
                take = [b for b in remaining if within(b, choice)] if coarsen else remaining[:1]
                groups.append(union(take))
                witnesses.append(hits[choice])
                remaining = [b for b in remaining if b not in take]
            yield {"i": i, "blocks": groups, "facts": witnesses}

    def accepted(self, partition):
        return all(any(within(z, block) for z in known for block in partition) for known in self.ones)


def hidden(partition, region):
    sizes = Counter(next(b for b in region if within(a, b)) for a in partition)
    return sum(n * (n - 1) // 2 for n in sizes.values())


def choose_region(partition, evidence, coarsen):
    choices = evidence.regions(partition, coarsen=coarsen)
    return max(choices, key=lambda r: hidden(partition, r["blocks"]), default=None)


def supports(partition, evidence):
    result = []
    for i, known in enumerate(evidence.zeros):
        minimal = {}
        for region, item in known.items():
            evidence.tick()
            atoms = frozenset(a for a in partition if not within(a, region))
            if atoms:
                minimal.setdefault(atoms, item)
        minimal = {atoms: minimal[atoms] for atoms in sorted(minimal, key=lambda a: (len(a), sorted(a)))
                   if not any(other < atoms for other in minimal)}
        components = []
        for atoms, item in minimal.items():
            evidence.tick()
            joined = [(atoms, item)]
            remaining = []
            for support, entries in components:
                if atoms & support:
                    joined.extend(entries)
                else:
                    remaining.append((support, entries))
            remaining.append((frozenset().union(*(a for a, _ in joined)), joined))
            components = remaining
        if components:
            support = frozenset().union(*(s for s, _ in components))
            d = 0
            for _, items in components:
                loads = Counter(atom for atoms, _ in items for atom in atoms)
                degree = max(loads.values())
                d += (len(items) + degree - 1) // degree
            if d > 1:
                result.append((support, d - 1, {"i": i, "facts": list(minimal.values())}))
    return sorted(result, key=lambda row: (-row[1], row[2]["i"]))


def lower_bound(primitives, overlapping, tick):
    used = frozenset()
    lower = 0
    records = []
    remaining = list(primitives)
    while remaining:
        tick()
        best = None
        for index, (support, cost, _) in enumerate(remaining):
            tick()
            overlap = len(used & support)
            gain = max(0, cost - lower, cost - max(0, overlap - 1)) if overlapping else (cost if not overlap else 0)
            if gain and (best is None or gain > best[0]):
                best = gain, index
        if best is None:
            break
        gain, index = best
        support, _, record = remaining.pop(index)
        used |= support
        lower += gain
        records.append(record)
    return lower, records


def disjoint_witness_pairs(partition, evidence):
    """Select two disjoint hitting obligations per negative on unused atoms."""
    used = 0
    proof = []
    for i, known in enumerate(evidence.zeros):
        evidence.tick()
        edges = {}
        for region, fact in known.items():
            edge = union(atom for atom in partition if not within(atom, region))
            if edge and not edge & used:
                edges.setdefault(edge, fact)
        ordered_edges = sorted(edges, key=lambda mask: (mask.bit_count(), mask))
        pair = None
        for left, right in combinations(ordered_edges, 2):
            evidence.tick()
            if not left & right:
                pair = left, right
                break
        if pair:
            left, right = pair
            used |= left | right
            proof.append({"i": i, "facts": [edges[left], edges[right]]})
    return proof


def repair(partition, evidence, primitives, tick):
    """Rank a complete candidate from known separating blocks and hitting obligations."""
    frequency = Counter(a for support, _, _ in primitives for a in support)
    obligations = {record["i"]: (support, cost, record) for support, cost, record in primitives}
    result = partition
    for i, known in enumerate(evidence.ones):
        tick()
        if any(within(b, block) for b in known for block in result):
            continue
        if known:
            def cost(block):
                return sum(bool(block & atom) for atom in result), block

            chosen = min(known, key=cost)
        elif i in obligations:
            support, lower, record = obligations[i]
            limit = min(len(support), lower + 2)
            chosen = 0
            for count in range(lower + 1, limit + 1):
                pool = sorted(support, key=lambda a: (frequency[a], a))
                for attempt, group in enumerate(combinations(pool, count)):
                    tick()
                    if attempt == 64:
                        break
                    candidate = union(group)
                    if all(not within(candidate, item["region"]) for item in record["facts"]):
                        chosen = candidate
                        break
                if chosen:
                    break
            if not chosen:
                continue
        else:
            continue
        parts = [b for b in result if b & chosen]
        result = ordered([union(parts), *(b for b in result if b not in parts)])
    return result


def diagnostic(partition, evidence, queried, tick):
    failed = list(evidence.regions(partition, coarsen=True))
    # A heuristic based on possible new, mutually disjoint unions.
    pool = []
    for region in failed:
        i = region["i"]
        by_positive = defaultdict(int)
        for atom in partition:
            tick()
            for region_mask, item in evidence.zeros[i].items():
                if within(atom, region_mask):
                    by_positive[item["j"]] |= atom
        gain = sum(1 for a, b in combinations(partition, 2)
                   if any(within(a | b, mask) for mask in by_positive.values())
                   and not any(within(a | b, z) for z in evidence.zeros[i]))
        pool.append((-gain, i, by_positive))
    choices = []
    for _, i, by_positive in sorted(pool, key=lambda row: row[:2])[:3]:
        for reverse in (False, True):
            tick()
            remaining = list(partition)
            groups = []
            masks = sorted(set(by_positive.values()), key=lambda mask: (-mask.bit_count(), mask))
            for mask in masks:
                suitable = [a for a in remaining if within(a, mask)]
                if reverse:
                    suitable.reverse()
                for left, right in zip(suitable[::2], suitable[1::2]):
                    tick()
                    block = left | right
                    if not any(within(block, z) for z in evidence.zeros[i]):
                        groups.append(block)
                        remaining.remove(left)
                        remaining.remove(right)
            candidate = ordered([*groups, *remaining])
            if len(groups) < 2 or candidate in queried:
                continue
            if evidence.accepted(candidate) or next(evidence.regions(candidate, coarsen=False), None):
                continue
            gain = sum(
                not evidence.accepted(child)
                and next(evidence.regions(child, coarsen=False), None) is None
                and child not in queried
                for a, b in combinations(partition, 2)
                if a | b in groups
                for child in [merge(partition, a, b)]
            )
            if gain >= 2:
                # Compare exact ratios and then use declared symbol order.
                choices.append((-Fraction(gain, len(groups)), candidate, i, gain))
    return min(choices, default=None)


def check_reply(reply, partition, negatives):
    if reply.get("status") == "INCOMPLETE":
        raise DeadlineExpired
    tables = reply["tables"]
    if tuple(reply["blocks"]) != partition or tuple(t["block"] for t in tables) != partition:
        raise ValueError("reply belongs to a different partition")
    covering = set()
    for table in tables:
        zeros = {i for i, j in table["zeros"] if type(j) is int and j >= 0}
        free = {i for group in table["free"] for i in group}
        size = len(table["zeros"]) + sum(map(len, table["free"]))
        if zeros & free or zeros | free != set(range(negatives)) or size != negatives:
            raise ValueError("incomplete or malformed table")
        covering |= free
    failed = reply["failed"]
    if reply["status"] == "ACCEPT" and len(covering) == negatives and failed is None:
        return
    if reply["status"] != "NO" or type(failed) is not int or not 0 <= failed < negatives or failed in covering:
        raise ValueError("verdict inconsistent with table")


def select(Sigma, negatives, analysis, query, tick, *, strategy, diagnostic_limit, overlapping,
           bound_enabled, incumbent_enabled, query_limit, stats):
    root = tuple(analysis["root"])
    unused = tuple(analysis["unused"])
    evidence = Evidence(negatives, tick)
    for item in analysis["facts"]:
        evidence.zero(item)

    for i, block in analysis.get("covered", {}).items():
        evidence.ones[i].add(block)

    accepted = (union(root),) if root else ()
    incumbent_reason = "A06" if not negatives else "A10"
    queried = {}
    records, replies, events = [], [], list(analysis["events"])
    events.extend(analysis["contractions"])
    events.extend(analysis["facts"])
    events.append({"rule": incumbent_reason, "initial_answer": accepted})
    seed = analysis.get("incumbent")
    if seed:
        # Removing unused singletons and coarsening to respect required atoms
        # both preserve compatibility.
        active = union(root)
        groups = list(ordered(b & active for b in seed if b & active))
        for atom in root:
            touch = [b for b in groups if b & atom]
            groups = [b for b in groups if not b & atom] + [union(touch)]
        seeded = ordered(groups)
        if len(seeded) > len(accepted):
            accepted, incumbent_reason = seeded, "A15"
            events.append({"rule": "A15", "blocks": ordered([*seeded, *unused])})
    counters = defaultdict(int)
    stats["selection"] = counters
    generated = {root}
    current = [root]
    waived = set()
    inferred = set()

    def use_query(partition, purpose):
        nonlocal accepted, incumbent_reason
        if partition in queried:
            return queried[partition]
        if query_limit is not None and len(queried) >= query_limit:
            raise DeadlineExpired
        tick()
        counters["diagnostic_calls" if purpose == "diagnostic" else "regular_calls"] += 1
        start = perf_counter()
        try:
            proposed = ordered([*partition, *unused])
            reply = query(proposed, purpose)
        finally:
            counters["oracle_seconds"] += perf_counter() - start
        check_reply(reply, proposed, negatives)
        label = len(replies)
        replies.append({"id": label, "purpose": purpose, **reply})
        queried[partition] = label
        evidence.ingest(reply, label)
        if reply["status"] == "NO":
            events.append({"rule": "S01", "query": label, "negative": reply["failed"]})
            if any(i != reply["failed"] for table in reply["tables"] for i, _ in table["zeros"]):
                events.append({"rule": "S03", "query": label})
        if any(len(group) > 1 for table in reply["tables"] for group in table["free"]):
            events.append({"rule": "S10", "query": label})
        if reply["status"] == "ACCEPT" and len(partition) >= len(accepted):
            accepted, incumbent_reason = partition, label
        return label

    if seed and bound_enabled and len(root) > len(accepted):
        began = perf_counter()
        packing = disjoint_witness_pairs(root, evidence)
        counters["witness_seconds"] += perf_counter() - began
        if len(root) - len(packing) <= len(accepted):
            records.append({"kind": "disjoint", "blocks": root, "facts": packing})
            events.append({"rule": "S12", "blocks": root, "lower": len(packing), "facts": packing})
            current = []

    initial_tried = False
    while current and len(current[0]) > len(accepted):
        following = {}
        for partition in current:
            tick()
            if len(partition) <= len(accepted):
                break
            counters["visited"] += 1
            region = choose_region(partition, evidence, coarsen=strategy != "pairs") if strategy != "pairs" else None
            if evidence.accepted(partition) and strategy != "pairs":
                accepted, incumbent_reason = partition, "S04"
                events.append({"rule": "S04", "blocks": partition})
                break
            if region:
                inferred.add(partition)
                events.append({"rule": "S02", "blocks": partition, "region": region})
            else:
                number = use_query(partition, "regular")
                if replies[number]["status"] == "ACCEPT":
                    break
                region = choose_region(partition, evidence, coarsen=strategy != "pairs")
            if not region:
                raise AssertionError("NO did not provide a common negative")

            closed = False
            if bound_enabled and len(partition) - 1 <= len(accepted):
                records.append({"kind": "unit", "blocks": partition, "region": region})
                events.append({"rule": "S08", "blocks": partition, "lower": 1})
                closed = True
            if closed:
                continue

            if strategy != "pairs":
                for _ in range(2):
                    if counters["diagnostic_calls"] >= diagnostic_limit:
                        break
                    start = perf_counter()
                    attempt = diagnostic(partition, evidence, queried, tick)
                    counters["ranking_seconds"] += perf_counter() - start
                    if not attempt:
                        break
                    _, target, i, gain = attempt
                    q = use_query(target, "diagnostic")
                    events.append({"rule": "S06", "query": q, "parent": partition, "negative": i,
                                   "estimated_children": gain})
                    region = choose_region(partition, evidence, coarsen=True)

            primitives = []
            if bound_enabled or (incumbent_enabled and not initial_tried):
                start = perf_counter()
                primitives = supports(partition, evidence)
                counters["witness_seconds"] += perf_counter() - start
            if incumbent_enabled and not initial_tried:
                initial_tried = True
                proposal = repair(partition, evidence, primitives, tick)
                if len(proposal) > len(accepted) and proposal != partition:
                    if evidence.accepted(proposal):
                        accepted, incumbent_reason = proposal, "S04"
                        events.append({"rule": "S04", "blocks": proposal})
                    elif next(evidence.regions(proposal, coarsen=False), None) is None:
                        q = use_query(proposal, "incumbent")
                        events.append({"rule": "S07", "query": q})
            if len(partition) <= len(accepted):
                break
            if bound_enabled:
                start = perf_counter()
                lower, proof = lower_bound(primitives, overlapping, tick)
                counters["witness_seconds"] += perf_counter() - start
                if lower and len(partition) - lower <= len(accepted):
                    records.append({"kind": "overlap" if overlapping else "disjoint", "blocks": partition,
                                    "facts": proof})
                    events.append({"rule": "S09", "blocks": partition, "lower": lower,
                                   "overlap": overlapping, "facts": proof})
                    continue

            group = {a: next(b for b in region["blocks"] if within(a, b)) for a in partition}
            records.append({"kind": "branch", "blocks": partition, "region": region})
            hidden_here = 0
            for a, b in combinations(partition, 2):
                tick()
                child = merge(partition, a, b)
                if group[a] == group[b]:
                    hidden_here += 1
                    waived.add(child)
                    continue
                counters["child_edges"] += 1
                following[child] = None
                generated.add(child)
            events.append({"rule": "S05", "blocks": partition, "region": region, "hidden_edges": hidden_here})
        counters["peak_frontier"] = max(counters["peak_frontier"], len(current), len(following))
        current = list(following)

    counters["generated"] = len(generated)
    counters["inferred_no"] = len(inferred - queried.keys())
    suppressed = waived - queried.keys()
    counters["unqueried_waived"] = len(suppressed)
    counters["unqueried_certified"] = len((inferred | waived) - queried.keys())
    certificate = {
        "unused": unused, "contractions": analysis["contractions"], "root": root,
        "records": [r for r in records if len(r["blocks"]) > len(accepted)],
    }
    return ordered([*accepted, *unused]), certificate, {
        "queries": replies, "events": events, "incumbent": incumbent_reason,
        "unqueried_waived": sorted(suppressed), "analysis_truncated": analysis["truncated"],
    }


def solve(D, *, seconds=None, strategy="table", diagnostic_limit=0, preprocess=True,
          order_sensitive=True, overlapping=True, bound_enabled=True, incumbent_enabled=True,
          query_limit=None, oracle=None, transcript=False, _encoded=None, _covered=None, _seed=None):
    if strategy not in ("table", "pairs"):
        raise ValueError("unknown strategy")
    if type(diagnostic_limit) is not int or diagnostic_limit < 0:
        raise ValueError("invalid diagnostic limit")
    tick = deadline(seconds)
    start = perf_counter()
    stats = {}
    adapter = None
    try:
        Sigma, positives, negatives, facts = analyze(D, tick, enabled=preprocess, order_sensitive=order_sensitive,
                                                    encoded=_encoded, covered=_covered)
        stats["analysis_seconds"] = perf_counter() - start
        digest = fingerprint(D)
        if "failure" in facts:
            result = {"status": "INFEASIBLE", "certificate": {"digest": digest, **facts["failure"]}}
            if transcript:
                result["transcript"] = {"queries": [], "events": [{"rule": facts["failure"]["kind"], **facts["failure"]}]}
        else:
            facts['incumbent'] = _seed
            adapter = ProjectionOracle(positives, negatives, tick)
            answer, proof, log = select(
                Sigma, len(negatives), facts, adapter if oracle is None else oracle, tick, strategy=strategy,
                diagnostic_limit=diagnostic_limit, overlapping=overlapping, bound_enabled=bound_enabled,
                incumbent_enabled=incumbent_enabled, query_limit=query_limit, stats=stats,
            )
            result = {"status": "OPTIMAL", "max_devices": len(answer),
                      "blocks": [[a for i, a in enumerate(Sigma) if (1 << i) & block] for block in answer],
                      "certificate": {"digest": digest, "kind": "partition-v1", **proof}}
            if transcript:
                result["transcript"] = log
        tick()
    except DeadlineExpired:
        result = {"status": "INCOMPLETE"}
        if transcript:
            result["transcript"] = {"queries": [], "events": [{"rule": "S11"}]}
    if adapter is not None:
        stats.update(row_requests=adapter.requests, new_rows=adapter.misses, projection_images=adapter.images)
    stats["producer_seconds"] = perf_counter() - start
    return {**result, "stats": stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--query-limit", type=int)
    parser.add_argument("--diagnostics", type=int, default=0)
    parser.add_argument("--mode", choices=["full", "passive", "feedback-only", "pairs"], default="full")
    parser.add_argument("--transcript", action="store_true")
    args = parser.parse_args()
    modes = {
        "full": {},
        "passive": dict(bound_enabled=False, incumbent_enabled=False),
        "feedback-only": dict(preprocess=False, bound_enabled=False, incumbent_enabled=False),
        "pairs": dict(strategy="pairs", preprocess=False, bound_enabled=False, incumbent_enabled=False),
    }
    D = json.loads(args.input.read_text(encoding="utf-8-sig"))
    print(json.dumps(solve(D, seconds=args.seconds, query_limit=args.query_limit,
                           diagnostic_limit=args.diagnostics, transcript=args.transcript, **modes[args.mode])))


if __name__ == "__main__":
    main()

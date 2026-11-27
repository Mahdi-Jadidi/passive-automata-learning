"""Replay exact Review08 roots with isolated evaluator and discovery arms."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import platform
from time import perf_counter

from selector_v2.core import Sample
from selector_v2.edr_bb import SearchBudget, SearchCaps, SearchCapExceeded
from selector_v2.edr_cross import discover
from selector_v2.edr_sparse import DEFAULT_INDEX_BYTES, DEFAULT_JOIN_WORK, discover_join, sparse_compatible
from selector_v2.scale_projections import CompactProjections
from selector_v2.scale_witness import TargetedDiscovery

FIXTURES = {
    "huge_choice_active": "0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba",
    "hdfs_1024": "7d076991e9ba118b98226a64d9551cd5c6df5d0797183d2e8a95ed896b057075",
    "hdfs_holdout_1024_uncapped": "238d37c4588f1a8506275859ede5cf6a5225630bb3454c016568ff7e2ae5ff6c",
}


def measured(call, budget):
    before = budget.work
    started = perf_counter()
    try:
        result = call()
        status = "complete"
    except SearchCapExceeded as exc:
        result = None
        status = "cap:" + str(exc)
    return dict(status=status, seconds=perf_counter() - started,
                work=budget.work - before, result=result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("arm", choices=("sparse", "compact", "join", "target", "literal"))
    parser.add_argument("--memory-mib", type=int, choices=(512, 1536))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.memory_mib:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    raw = args.fixture.read_bytes()
    source_hash = sha256(raw).hexdigest()
    if source_hash != FIXTURES[args.fixture.stem]:
        raise ValueError("fixture hash mismatch")
    sample = Sample.from_input(json.loads(raw))
    owner = tuple(range(len(sample.alphabet)))
    counters = defaultdict(int)
    budget = SearchBudget(SearchCaps(seconds=25, work=10_000_000))
    index = CompactProjections(sample)
    target = TargetedDiscovery(sample)
    failed = None

    def check():
        nonlocal failed
        if args.arm == "sparse":
            return sparse_compatible(owner, sample.positive, sample.negative, budget,
                                     DEFAULT_INDEX_BYTES, counters)
        failed = index.check(owner, budget, counters)
        return failed.compatible

    first = measured(check, budget)
    row = dict(arm=args.arm, case=args.fixture.stem, source_sha256=source_hash,
               alphabet=len(owner), positive=len(sample.positive), negative=len(sample.negative),
               memory_mib=args.memory_mib, index_bytes=DEFAULT_INDEX_BYTES,
               python=platform.python_version(), optimized=not __debug__, root=first)
    if failed is not None:
        row["failed_negative"] = failed.negative_id
    if first["result"] is False and args.arm in ("join", "target", "literal"):
        if args.arm == "join":
            find = lambda: discover_join(owner, sample, budget, counters,
                                         DEFAULT_JOIN_WORK, DEFAULT_INDEX_BYTES)
        elif args.arm == "target":
            find = lambda: target.find(failed, budget, counters)
        else:
            find = lambda: discover(owner, sample, budget, counters)
        row["discovery"] = measured(find, budget)
        found = row["discovery"]["result"]
        if found is not None:
            y = sample.negative[int(found["negative_id"][1:])]
            for side in ("s", "t"):
                x = sample.positive[int(found[f"positive_{side}_id"][1:])]
                support = found[f"support_{side}"]
                if tuple(a for a in x if owner[a] not in support) != tuple(
                        a for a in y if owner[a] not in support):
                    raise ValueError("invalid witness")
        elif args.arm != "literal":
            row["fallback"] = measured(lambda: discover(owner, sample, budget, counters), budget)
    if args.arm == "compact" and first["status"] == "complete":
        row["warm_same_owner"] = measured(check, budget)
    if args.memory_mib:
        row["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    row["counters"] = dict(counters)
    output = json.dumps(row, sort_keys=True)
    print(output)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    if args.fixture.stem == "huge_choice_active" and args.arm == "compact":
        if first["result"] is not False or row["warm_same_owner"]["result"] is not False:
            raise SystemExit("compact root did not complete as incompatible")


if __name__ == "__main__":
    main()

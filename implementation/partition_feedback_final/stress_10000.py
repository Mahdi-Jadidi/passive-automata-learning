"""Rebuild the 10,000-trace fixture and time the default exact solver."""
import argparse
from itertools import combinations, pairwise
import json
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import staged
from verify import verify


FIXTURE = Path(__file__).resolve().parent / "evidence/synthetic_10000_traces_1000_symbols.json"


def build_sample():
    alphabet = [f"s{i:04d}" for i in range(1000)]
    groups = []
    offset = 0
    for size in (22, *(75,) * 12, 78):
        groups.append(alphabet[offset:offset + size])
        offset += size
    edges = [edge for group in groups for edge in pairwise(group)]
    positives = dict.fromkeys(edges)
    for pair in combinations(alphabet, 2):
        positives.setdefault(pair, None)
        if len(positives) == 10000 - len(edges):
            break
    return {
        "alphabet": alphabet,
        "positive": [list(pair) for pair in positives],
        "negative": [[b, a] for a, b in edges],
    }, groups


def check_reference(sample, groups):
    positives = {tuple(word) for word in sample["positive"]}
    negatives = {tuple(word) for word in sample["negative"]}
    assert len(positives) == 9014 and len(negatives) == 986
    assert {a for group in groups for a in group} == set(sample["alphabet"])
    assert sum(map(len, groups)) == len(sample["alphabet"]) == 1000
    assert len(groups) == 14 and min(map(len, groups)) == 22
    assert all(a < b for a, b in positives)
    forced = {(b, a) for group in groups for a, b in pairwise(group) if (a, b) in positives}
    assert forced == negatives


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=30)
    args = parser.parse_args()
    sample, groups = build_sample()
    check_reference(sample, groups)
    assert sample == json.loads(FIXTURE.read_text(encoding="utf-8"))
    pair_scan = staged.pair_scan
    pair_seconds = None

    def timed_pair_scan(*args, **kwargs):
        nonlocal pair_seconds
        start = perf_counter()
        try:
            return pair_scan(*args, **kwargs)
        finally:
            pair_seconds = perf_counter() - start

    with patch.object(staged, "pair_scan", timed_pair_scan):
        result = staged.solve(sample, seconds=args.seconds)
    log = {"budget_seconds": args.seconds, "pair_scan_seconds": pair_seconds,
           "status": result["status"], "stats": result["stats"]}
    if result["status"] != "INCOMPLETE":
        start = perf_counter()
        verdict = verify(sample, result)
        log.update(verification=verdict["status"], verification_seconds=perf_counter() - start,
                   blocks=result.get("max_devices"))
        assert verdict["status"] == "VERIFIED" and result.get("max_devices") == len(groups)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()


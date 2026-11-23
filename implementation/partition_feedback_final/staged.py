"""Solve exactly using raw coverage, bounded witness rank and merge search."""
import argparse
import json
from pathlib import Path
from time import perf_counter

from hybrid import RANK_LIMIT, discrepancy_families, pair_scan, rank_answer, singleton_analysis
from sample import DeadlineExpired, deadline, read_sample
from search import fingerprint, solve as solve_feedback


def solve(D, *, seconds=None, transcript=False, mode="hybrid", rank_limit=RANK_LIMIT, **options):
    if mode not in ("hybrid", "targeted"):
        raise ValueError("unknown analysis mode")
    if type(rank_limit) is not int or not 0 <= rank_limit <= RANK_LIMIT:
        raise ValueError(f"rank_limit must be between 0 and {RANK_LIMIT}")
    start = perf_counter()
    tick = deadline(seconds)
    stats = {"selection": {"regular_calls": 0, "diagnostic_calls": 0}}
    try:
        encoded = read_sample(D, tick)
        sigma, positives, negatives = encoded
        root = tuple(1 << a for a in range(len(sigma)))
        covered = singleton_analysis(sigma, positives, negatives, tick)
        unresolved = [i for i in range(len(negatives)) if i not in covered]
        stats.update(unresolved_ids=len(unresolved),
                     unresolved_words=len({negatives[i] for i in unresolved}),
                     singleton_seconds=perf_counter() - start)
        coverage = [[i, block] for i, block in covered.items()]
        events = [{"rule": "A12", "coverage": coverage, "unresolved": unresolved}]
        result = None
        seed = None
        kind = None
        failures = []
        if not unresolved:
            answer, kind = root, "singleton"
        elif mode == "hybrid" and options.get("oracle") is None and root and set(positives).isdisjoint(negatives):
            began = perf_counter()
            scanned = pair_scan(root, positives, negatives, unresolved, tick)
            stats["pair_seconds"] = perf_counter() - began
            if scanned is not None:
                answer, kind, failures = scanned
                seed = answer
            if kind is None and rank_limit:
                began = perf_counter()
                rows = discrepancy_families(positives, negatives, unresolved, tick, rank_limit)
                if rows is not None:
                    answer, kind = rank_answer(root, rows, tick), "rank"
                stats["rank_seconds"] = perf_counter() - began
        if kind:
            proof = {"kind": kind, "digest": fingerprint(D)}
            if kind == "two-pairs":
                proof["failures"] = failures
            result = {"status": "OPTIMAL", "max_devices": len(answer), "certificate": proof,
                      "blocks": [[a for i, a in enumerate(sigma) if (1 << i) & b] for b in answer]}
            rule = {"singleton": "A11", "pair": "A13", "two-pairs": "A13", "rank": "A14"}[kind]
            events.append({"rule": rule, "blocks": answer, "certificate_kind": kind})
            if transcript:
                result["transcript"] = {"queries": [], "events": events}
        else:
            remaining = None if seconds is None else max(0, seconds - (perf_counter() - start))
            result = solve_feedback(D, seconds=remaining, transcript=transcript,
                                    _encoded=encoded, _covered=covered, _seed=seed, **options)
            stats.update(result["stats"])
            if transcript and result["status"] != "INCOMPLETE":
                result["transcript"]["events"][:0] = events
        tick()
    except DeadlineExpired:
        result = {"status": "INCOMPLETE"}
        if transcript:
            result["transcript"] = {"queries": [], "events": [{"rule": "S11"}]}
    stats["producer_seconds"] = perf_counter() - start
    return {**result, "stats": stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--query-limit", type=int)
    parser.add_argument("--diagnostics", type=int, default=0)
    parser.add_argument("--mode", choices=("hybrid", "targeted"), default="hybrid")
    parser.add_argument("--transcript", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.sample.read_text(encoding="utf-8-sig"))
    print(json.dumps(solve(data, seconds=args.seconds, diagnostic_limit=args.diagnostics,
                           query_limit=args.query_limit, transcript=args.transcript, mode=args.mode)))


if __name__ == "__main__":
    main()


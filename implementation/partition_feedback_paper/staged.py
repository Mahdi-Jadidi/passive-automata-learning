
"""Fast exact singleton certification before optional mining of deletion witnesses."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from sample import DeadlineExpired, deadline, read_sample
from search import fingerprint, solve as solve_feedback


def singleton_certificate(D, tick):
    Sigma, positives, negatives = read_sample(D, tick)
    observed = [set() for _ in Sigma]
    for x in dict.fromkeys(positives):
        tick()
        counts = Counter(x)
        for a, values in enumerate(observed):
            values.add(counts[a])

    witnesses = []
    for i, y in enumerate(negatives):
        tick()
        counts = Counter(y)
        a = next((a for a, values in enumerate(observed) if counts[a] not in values), None)
        if a is None:
            return None
        witnesses.append({"i": i, "symbol": a, "count": counts[a]})
    return Sigma, witnesses


def solve(D, *, seconds=None, transcript=False, **options):
    start = perf_counter()
    tick = deadline(seconds)
    try:
        fast = singleton_certificate(D, tick)
        examined = perf_counter() - start
        if fast is not None:
            Sigma, witnesses = fast
            root = [1 << a for a in range(len(Sigma))]
            result = {"status": "OPTIMAL", "blocks": [[a] for a in Sigma], "max_devices": len(Sigma),
                      "certificate": {"kind": "partition-v1", "digest": fingerprint(D), "root": root,
                                      "unused": [], "contractions": [], "records": []}}
            if transcript:
                result["transcript"] = {"queries": [], "events": [{"rule": "A11", "witnesses": witnesses}]}
            tick()
            result["stats"] = {"analysis_seconds": examined, "producer_seconds": perf_counter() - start,
                               "staged_singletons": True, "selection": {"regular_calls": 0, "diagnostic_calls": 0}}
            return result
        remaining = None if seconds is None else max(0, seconds - examined)
        result = solve_feedback(D, seconds=remaining, transcript=transcript, **options)
        result["stats"]["singleton_stage_seconds"] = examined
        result["stats"]["producer_seconds"] = perf_counter() - start
        return result
    except DeadlineExpired:
        return {"status": "INCOMPLETE", "stats": {"producer_seconds": perf_counter() - start}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sample", type=Path)
    p.add_argument("--seconds", type=float)
    p.add_argument("--diagnostics", type=int, default=0)
    p.add_argument("--query-limit", type=int)
    p.add_argument("--transcript", action="store_true")
    a = p.parse_args()
    D = json.loads(a.sample.read_text(encoding="utf-8-sig"))
    print(json.dumps(solve(D, seconds=a.seconds, diagnostic_limit=a.diagnostics,
                           query_limit=a.query_limit, transcript=a.transcript)))


if __name__ == "__main__":
    main()

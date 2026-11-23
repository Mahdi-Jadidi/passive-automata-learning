
"""Serial cold-cache comparisons, independent replay, and resumable trial records."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter
import tracemalloc

from audit import FEEDBACK, sample, triples
from search import solve
from verify import verify

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
VARIANTS = {
    "pairs": dict(FEEDBACK, strategy="pairs"),
    "passive": FEEDBACK,
    "diagnostics_1": dict(FEEDBACK, diagnostic_limit=1),
    "diagnostics_2": dict(FEEDBACK, diagnostic_limit=2),
    "full": {},
    "full_diagnostics": dict(diagnostic_limit=8),
    "disjoint_only": dict(overlapping=False),
    "without_order": dict(order_sensitive=False),
    "without_incumbent": dict(incumbent_enabled=False),
}


def cases():
    data = {
        "example": (sample("abcd", ["ab", "cd"], [""]), 3),
        "joint_obligations": (sample("abcd", ["a", "bc", "bd"], ["", "ac"]), 2),
    }
    for family in ("disjoint", "sunflower", "order"):
        for r in (4, 8, 16):
            for seed in range(3):
                D = triples(r, family, seed)
                data[f"{family}_{r}_{seed}"] = (D, len(D["alphabet"]) - r)
    for n in (6, 8):
        alphabet = list("abcdefghijklmnop"[:2*n])
        D = sample(alphabet, zip(alphabet[:n], alphabet[n:]),
                   zip(alphabet[:n-1], alphabet[1:n]))
        data[f"cover_path_{n}"] = (D, 2*n - n//2)
    hdfs = json.loads((EVIDENCE / "hdfs_cases.json").read_text(encoding="utf-8"))
    data.update({name: (D, 29 if name in ("hdfs_16", "hdfs_64") else None)
                 for name, D in hdfs.items()})
    return data


def trial(D, expected, variant, budget, limit, memory=False):
    if memory:
        tracemalloc.start()
    start = perf_counter()
    result = solve(D, seconds=budget, query_limit=limit, **VARIANTS[variant])
    encoded = json.dumps(result, separators=(",", ":"))
    result = json.loads(encoded)
    before_verify = perf_counter()
    if result["status"] == "INCOMPLETE" or before_verify - start >= budget:
        verdict = "INCOMPLETE"
    else:
        verdict = verify(D, result, seconds=max(0.0, budget - (before_verify - start)))["status"]
    if verdict == "VERIFIED" and expected is not None:
        assert result.get("max_devices") == expected, (expected, result)
    assert verdict != "INVALID", result
    elapsed = perf_counter() - start
    peak = None
    if memory:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return {
        "verdict": verdict, "blocks": result.get("max_devices") if verdict == "VERIFIED" else None,
        "certificate_bytes": len(json.dumps(result["certificate"])) if "certificate" in result else None,
        "verification_seconds": elapsed - (before_verify - start),
        "elapsed_seconds": elapsed, "peak_python_bytes": peak, **result["stats"],
    }


def summary(records):
    groups = {}
    for row in records:
        key = (row["case"], row["variant"], row["budget"], row["limit"], row["memory"])
        groups.setdefault(key, []).append(row)
    result = []
    for key, rows in sorted(groups.items(), key=lambda entry: str(entry[0])):
        completed = [r for r in rows if r["verdict"] == "VERIFIED"]
        calls = [r.get("selection", {}).get("regular_calls", 0)
                 + r.get("selection", {}).get("diagnostic_calls", 0) for r in rows]
        result.append({"case": key[0], "variant": key[1], "budget": key[2], "query_limit": key[3],
                       "memory_run": key[4], "verified": len(completed), "trials": len(rows),
                       "median_completed_ms": round(1000*median(r["elapsed_seconds"] for r in completed), 3)
                       if completed else None, "median_queries_all": median(calls)})
    return result


def run(profile):
    data = cases()
    out = EVIDENCE / f"trials_{profile}.jsonl"
    records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()] if out.exists() else []
    source_files = ("model.py", "search.py", "verify.py", "sample.py", "audit.py", "benchmark.py")
    digest = sha256()
    for name in source_files:
        digest.update((HERE / name).read_bytes())
    digest.update((EVIDENCE / "hdfs_cases.json").read_bytes())
    manifest = {"sha256": digest.hexdigest(), "platform": platform.platform(),
                "python": platform.python_version(), "repeat_order": "serial rotating"}
    manifest_file = EVIDENCE / f"manifest_{profile}.json"
    if records and json.loads(manifest_file.read_text(encoding="utf-8")) != manifest:
        raise ValueError("trial file belongs to a different code, data or machine")
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Main arms across representative cases. The scale profile uses theorem targets and
    # cheap query caps rather than running the hardest timed comparisons repeatedly.
    representative = ["example", "joint_obligations", "disjoint_4_0", "sunflower_4_0", "order_4_0",
                      "cover_path_6", "cover_path_8", "hdfs_16", "hdfs_64", "hdfs_128",
                      "hdfs_512", "hdfs_1024", "hdfs_holdout_128", "hdfs_holdout_512", "hdfs_holdout_1024"]
    variants = list(VARIANTS)
    if profile == "main":
        plan = [(case, budget, 32 if budget == 1 else None, False, repeat)
                for budget in (0.5, 5.0, 1.0) for repeat in range(3) for case in representative]
    elif profile == "scale":
        plan = [(case, 1.0, 32, False, 0) for case in data if case.startswith(("disjoint", "sunflower", "order"))]
        variants = ["full", "disjoint_only", "without_order", "full_diagnostics"]
    else:
        plan = [(case, 1.0, 32, True, 0) for case in representative]
        variants = ["passive", "full", "full_diagnostics"]

    already = {(r["case"], r["variant"], r["budget"], r["limit"], r["memory"], r["repeat"]) for r in records}
    with out.open("a", encoding="utf-8") as handle:
        for case, budget, limit, memory, repeat in plan:
            for variant in variants[repeat:] + variants[:repeat]:
                key = (case, variant, budget, limit, memory, repeat)
                if key in already:
                    continue
                D, expected = data[case]
                result = trial(D, expected, variant, budget, limit, memory)
                row = {"case": case, "variant": variant, "budget": budget, "limit": limit,
                       "memory": memory, "repeat": repeat, **result}
                handle.write(json.dumps(row) + "\n")
                handle.flush()
                records.append(row)
    info = summary(records)
    (EVIDENCE / f"summary_{profile}.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps({"profile": profile, "runs": len(records),
                      "verified": sum(r["verdict"] == "VERIFIED" for r in records)}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("profile", choices=("main", "scale", "memory"))
    run(p.parse_args().profile)

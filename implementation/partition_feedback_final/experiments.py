"""Reproduce the hybrid checks, hard certificates, and matched timing experiment."""
import argparse
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter

from audit import compatible, exhaustive_samples, optimum, sample
from model import ProjectionOracle, merge
from sample import read_sample
from search import Evidence, choose_region, solve as baseline
from staged import solve
from verify import verify

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence"


def save(name, data):
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def fixtures():
    data = json.loads((OUT / "hdfs_cases.json").read_text())
    alphabet = "abcdefghijklmnop"
    data["cover_path_8"] = sample(alphabet, zip(alphabet[:8], alphabet[8:]),
                                  zip(alphabet[:7], alphabet[1:8]))
    data["rank_order"] = sample("ab", ["aba"], ["aab"])
    data["rank_triple"] = sample("abc", ["a", "b", "c"], [""])
    data["exam_multi"] = sample("abc", ["ab"], ["aa", "ba", "ccc", "ba"])
    return data


def check(data):
    total = 0
    for D in exhaustive_samples():
        expected = optimum(D)
        for mode, limit in (("hybrid", 4096), ("targeted", 0), ("hybrid", 0)):
            result = solve(D, transcript=True, mode=mode, rank_limit=limit)
            assert result.get("max_devices") == expected and verify(D, result)["status"] == "VERIFIED"
            total += 1
    expected = {"hdfs_1024": 27, "cover_path_8": 12, "rank_order": 1, "rank_triple": 1, "exam_multi": 2}
    for name, count in expected.items():
        D = data[name]
        result = solve(D, transcript=True)
        assert result["max_devices"] == count and verify(D, result)["status"] == "VERIFIED"
        save(name, {"input": D, "result": result, "verdict": "VERIFIED"})
    assert solve(data["rank_triple"])["certificate"]["kind"] == "rank"
    assert solve(data["rank_triple"], rank_limit=0)["max_devices"] == 1
    hard = solve(data["hdfs_1024"])
    hard["certificate"]["failures"].pop()
    assert verify(data["hdfs_1024"], hard)["status"] == "INVALID"
    packing = solve(data["cover_path_8"])
    changed = deepcopy(packing)
    changed["certificate"]["records"][0]["facts"][0]["facts"][0]["i"] = 1
    assert verify(data["cover_path_8"], changed)["status"] == "INVALID"
    changed = deepcopy(packing)
    changed["certificate"]["records"].clear()
    assert verify(data["cover_path_8"], changed)["status"] == "INVALID"

    # Test the rank theorem above intermediate partitions with direct erasing projections.
    from audit import partitions
    from hybrid import discrepancy_families, rank_answer
    nodes = 0
    for D in exhaustive_samples():
        sigma, positives, negatives = read_sample(D, lambda: None)
        if not positives or not negatives or not set(positives).isdisjoint(negatives):
            continue
        rows = discrepancy_families(positives, negatives, range(len(negatives)), lambda: None, 4096)
        if rows is None:
            continue
        symbol_mask = {a: 1 << i for i, a in enumerate(sigma)}
        candidates = [
            tuple(sum(symbol_mask[a] for a in block) for block in partition)
            for partition in partitions(sigma) if compatible(D, partition)
        ]
        for partition in partitions(sigma):
            from model import ordered
            root = ordered(sum(symbol_mask[a] for a in block) for block in partition)
            expected = max(len(p) for p in candidates if all(any(a & b == a for b in p) for a in root))
            assert len(rank_answer(root, rows, lambda: None)) == expected
            nodes += 1
    save("hybrid_checks", {"historical_inputs_times_three": total, "rank_intermediate_nodes": nodes,
                           "hard_cases_verified": 2, "corruption_checks": 3})


def diagnostics():
    D = sample("abcde", ["abcde"], ["abced"])
    sigma, positives, negatives = read_sample(D, lambda: None)
    tick = lambda: None
    root = (1, 2, 4, 8, 16)
    a, b, c, d, e = root
    probes = [(a | b | c | d, e), (a | b | c | e, d)]
    from audit import partitions
    from model import ordered
    all_partitions = [ordered(sum(1 << sigma.index(s) for s in block) for block in p)
                      for p in partitions(sigma)]
    rows = []
    for budget in (-1, 0, 1, 2):
        ledger = Evidence(1, tick)
        oracle = ProjectionOracle(positives, negatives, tick)
        replies, skipped = [], []
        def query(blocks, purpose):
            response = oracle(blocks, purpose)
            index = len(replies)
            replies.append({"id": index, "purpose": purpose, **response})
            if budget >= 0:
                ledger.ingest(response, index)
            return response
        assert query(root, "regular")["status"] == "NO"
        for candidate in probes[:max(0, budget)]:
            assert query(candidate, "diagnostic")["status"] == "NO"
        excluded = {p for p in all_partitions if choose_region(p, ledger, False)}
        excluded.update(tuple(q["blocks"]) for q in replies)
        for left, right in combinations(root, 2):
            candidate = merge(root, left, right)
            proof = choose_region(candidate, ledger, False)
            if proof:
                skipped.append({"blocks": candidate, "proof": proof})
            elif query(candidate, "regular")["status"] == "ACCEPT":
                break
        from verify import Replay
        replay = Replay(positives, negatives, 31, tick)
        replay.transcript({"queries": replies})
        for event in skipped:
            replay.region(event["proof"], event["blocks"], 31)
        replay.answer(candidate)
        rows.append({"probe_budget": budget, "paid": len(replies),
                     "diagnostic_paid": max(0, budget), "excluded_before_scan": len(excluded),
                     "ordinary_skipped": len(skipped), "queries": replies, "skipped": skipped})
    assert [r["paid"] for r in rows] == [11, 11, 6, 4]
    save("diagnostics", {"input": D, "rows": rows})


def timing(data):
    # The frozen staged wrapper imports the locally copied merge core, whose
    # baseline path has no coverage or seeded incumbent.
    spec = spec_from_file_location("previous_staged", HERE.parent / "partition_feedback_paper" / "staged.py")
    previous = module_from_spec(spec)
    spec.loader.exec_module(previous)
    arms = {"core": baseline, "previous-singleton": previous.solve,
            "targeted": lambda D, **kw: solve(D, mode="targeted", **kw),
            "hybrid": solve,
            "hybrid-diagnostic": lambda D, **kw: solve(D, diagnostic_limit=2, **kw)}
    names = ("hdfs_128", "hdfs_512", "hdfs_1024", "hdfs_holdout_128",
             "hdfs_holdout_512", "hdfs_holdout_1024", "cover_path_8")
    rows = []
    for repeat in range(3):
        order = list(arms)[repeat:] + list(arms)[:repeat]
        for name in names:
            for arm in order:
                start = perf_counter()
                r = arms[arm](data[name], seconds=5)
                encoded = json.dumps(r, separators=(",", ":"))
                result = json.loads(encoded)
                check_start = perf_counter()
                remaining = 5 - (check_start - start)
                if result["status"] == "INCOMPLETE" or remaining <= 0:
                    verdict = "INCOMPLETE"
                else:
                    verdict = verify(data[name], result, seconds=remaining)["status"]
                elapsed = perf_counter() - start
                assert verdict != "INVALID"
                if elapsed > 5:
                    verdict = "INCOMPLETE"
                rows.append({"case": name, "repeat": repeat, "arm": arm, "verdict": verdict,
                             "blocks": r.get("max_devices") if verdict == "VERIFIED" else None,
                             "elapsed_seconds": elapsed, "verification_seconds": elapsed - (check_start - start),
                             "certificate_bytes": len(json.dumps(r["certificate"], separators=(",", ":")))
                             if "certificate" in r else None, "stats": r["stats"]})
    held = [(a, b) for a in rows for b in rows if a["case"].startswith("hdfs_holdout")
            and a["case"] == b["case"] and a["repeat"] == b["repeat"]
            and a["arm"] == "hybrid" and b["arm"] == "hybrid-diagnostic"]
    shared = [(a, b) for a, b in held if a["verdict"] == b["verdict"] == "VERIFIED"]
    def paid(row):
        stats = row["stats"].get("selection", {})
        return stats.get("regular_calls", 0) + stats.get("diagnostic_calls", 0)
    totals = [sum(paid(pair[index]) for pair in held) for index in (0, 1)]
    verified = [sum(pair[index]["verdict"] == "VERIFIED" for pair in held) for index in (0, 1)]
    common = [median(pair[index]["elapsed_seconds"] for pair in shared) for index in (0, 1)] if shared else []
    enable = totals[1] < totals[0] and verified[1] >= verified[0] and bool(common) and common[1] <= 1.05 * common[0]
    sources = sorted(HERE.glob("*.py")) + [OUT / "hdfs_cases.json"]
    save("timing", {"platform": platform.platform(), "python": platform.python_version(), "budget_seconds": 5,
                    "sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sources},
                    "rows": rows, "gate": {"paid": totals, "verified": verified, "common_median": common,
                                           "enable_default": enable}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timed", action="store_true")
    args = parser.parse_args()
    data = fixtures()
    if args.timed:
        timing(data)
    else:
        check(data)
        diagnostics()


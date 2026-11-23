
"""Paired serial comparisons of the singleton stage using the same total budget."""
from hashlib import sha256
import json
from time import perf_counter

from benchmark import EVIDENCE, HERE
from search import solve as core
from staged import solve as staged
from verify import verify


def run():
    data = json.loads((EVIDENCE / "hdfs_cases.json").read_text(encoding="utf-8"))
    names = ("hdfs_16", "hdfs_64", "hdfs_128", "hdfs_holdout_512")
    confirmed = {"hdfs_16": 29, "hdfs_64": 29, "hdfs_128": 28, "hdfs_holdout_512": 29}
    records = []
    for repeat in range(3):
        for name in names:
            D = data[name]
            solvers = [("core", core), ("staged", staged)]
            if repeat % 2:
                solvers.reverse()
            for label, solve in solvers:
                budget = 5
                start = perf_counter()
                result = json.loads(json.dumps(solve(D, seconds=budget)))
                remaining = max(0, budget - (perf_counter() - start))
                verdict = verify(D, result, seconds=remaining)["status"]
                elapsed = perf_counter() - start
                assert verdict in ("INCOMPLETE", "VERIFIED")
                if verdict == "VERIFIED":
                    assert result["max_devices"] == confirmed[name]
                record = {"case": name, "repeat": repeat, "variant": label, "budget": budget,
                          "verdict": verdict, "seconds": elapsed, "stats": result["stats"]}
                records.append(record)
    hash_files = ["staged.py", "search.py", "model.py", "verify.py", "sample.py", "benchmark_staged.py"]
    (EVIDENCE / "trials_staged.json").write_text(json.dumps({
        "code": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in hash_files},
        "trials": records,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()

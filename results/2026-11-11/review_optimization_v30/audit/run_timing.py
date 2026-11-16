"""Fixed 8-case x 2-solver x 3-repetition process-wall timing matrix."""
import importlib.util
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
RESULTS = WORKSPACE / "results" / "2026-11-11"
PYTHON = Path(sys.executable)
BASELINE = RESULTS / "exact_foundations_v28" / "implementation" / "reference.py"
COMBINED = RESULTS / "review_optimization_v30" / "optimization" / "candidate_v1.py"
WORKER = HERE / "timing_worker.py"
OUT = HERE / "timing_results.json"


def load_oracle():
    path = HERE / "reference_oracle_v28.py"
    spec = importlib.util.spec_from_file_location("oracle", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    oracle = load_oracle()
    rows = [json.loads(line) for line in (HERE / "timing_cases.jsonl").read_text(encoding="utf-8").splitlines()]
    output = {"status": "RUNNING", "repetitions": 3, "timeout_seconds": 20,
              "includes_process_startup": True, "observations": []}
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    solvers = [("baseline", BASELINE, "solve"), ("combined", COMBINED, "solve_combined")]
    for rep in range(1, 4):
        for row in rows:
            expected = oracle_to_source(row["input"], oracle)
            for label, module_path, function in solvers:
                start = time.perf_counter()
                observation = {"rep": rep, "case": row["case"], "solver": label,
                               "status": "NOT_RUN", "seconds": None, "result": None,
                               "stderr": ""}
                try:
                    completed = subprocess.run([str(PYTHON), str(WORKER), str(module_path), function],
                        input=json.dumps(row["input"], ensure_ascii=False), text=True,
                        capture_output=True, timeout=20, check=False)
                    observation["seconds"] = time.perf_counter() - start
                    observation["stderr"] = completed.stderr
                    if completed.returncode != 0:
                        observation["status"] = "PROCESS_ERROR"
                    else:
                        observed = json.loads(completed.stdout)
                        observation["status"] = "PASS" if observed == expected else "MISMATCH"
                        observation["result"] = observed
                except subprocess.TimeoutExpired as exc:
                    observation["seconds"] = time.perf_counter() - start
                    observation["status"] = "TIMEOUT"
                    observation["stderr"] = (exc.stderr or "") if isinstance(exc.stderr, str) else "timeout"
                output["observations"].append(observation)
                output["status"] = "RUNNING"
                OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
                if observation["status"] != "PASS":
                    output["status"] = "FAIL"
                    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
                    raise RuntimeError(f"timing observation failed: {observation['rep']} {observation['case']} {label} {observation['status']}")
    summary = {}
    for row in rows:
        for label, _, _ in solvers:
            samples = [x["seconds"] for x in output["observations"]
                       if x["case"] == row["case"] and x["solver"] == label]
            summary[f"{row['case']}::{label}"] = {"raw_seconds": samples,
                                                    "median_seconds": statistics.median(samples)}
    output["status"] = "PASS"
    output["summary"] = summary
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": output["status"], "observations": len(output["observations"]),
                      "summary": summary}, ensure_ascii=False, sort_keys=True))


def oracle_to_source(data, oracle):
    sigma, positives, negatives = oracle.normalize(data)
    raw = oracle.oracle(data)
    if raw["max_blocks"] is None:
        return {"status": "INCOMPATIBLE", "compatible_count": 0, "optimal_count": 0,
                "max_blocks": None, "recommendation": None, "optimal_unique": None,
                "compatible_witnesses": [], "optimal_witnesses": []}
    def convert(w):
        factors = []
        for block in w["blocks"]:
            seen, values = set(), []
            for p in positives:
                projected = oracle.projection(p, set(block))
                if projected not in seen:
                    seen.add(projected)
                    values.append(list(projected))
            factors.append(values)
        return {"rgs": w["rgs"], "blocks": w["blocks"], "factors": factors,
                "negative_rejected_by": w["rejecting_block_by_negative"]}
    all_w = [convert(w) for w in raw["compatible"]]
    opt_w = [convert(w) for w in raw["optimal"]]
    return {"status": raw["status"], "compatible_count": raw["compatible_count"],
            "optimal_count": raw["optimal_count"], "max_blocks": raw["max_blocks"],
            "recommendation": opt_w[0], "optimal_unique": raw["optimal_unique"],
            "compatible_witnesses": all_w, "optimal_witnesses": opt_w}


if __name__ == "__main__":
    main()

"""Postprocess already accepted benchmark captures; never starts solvers."""
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "results/2026-10-26/partition_discovery_v3/audit"
LEDGER = AUDIT / "performance_adopted/runs/serial_v1/ledger.jsonl"
OUT = AUDIT / "performance_case_analysis_v1"


def main():
    ledger = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line]
    assert len(ledger) == 1744
    by_case = defaultdict(list)
    for entry in ledger:
        if entry["mode"] != "timing":
            continue
        assert entry["execution_status"] == "success" and entry["child_reaped"] is True
        key = (entry["method"], int(entry["case_id"].rsplit("m", 1)[1].split("_", 1)[0]),
               entry["case_id"], entry["max_solutions"])
        by_case[key].append(entry["subprocess_seconds"])

    case_medians = {key: statistics.median(values) for key, values in by_case.items()}
    assert len(case_medians) == 100 * 2 * 2 + 18 * 2
    comparison = {}
    for size in (4, 6, 8, 10):
        for limit in (1, 2):
            ratios, gtimes, ftimes = [], [], []
            for i in range(25):
                case_id = f"performance_100_m{size}_{i:03d}"
                g = case_medians[("general", size, case_id, limit)]
                f = case_medians[("fair-reference", size, case_id, limit)]
                ratios.append(g / f)
                gtimes.append(g)
                ftimes.append(f)
            comparison[f"m{size}_limit{limit}"] = {
                "paired_cases": len(ratios),
                "median_per_case_general_seconds": statistics.median(gtimes),
                "median_per_case_fair_seconds": statistics.median(ftimes),
                "median_paired_general_over_fair_ratio": statistics.median(ratios),
                "general_faster_cases": sum(x < 1 for x in ratios),
                "fair_faster_cases": sum(x > 1 for x in ratios),
                "ties": sum(x == 1 for x in ratios),
            }

    fixed = {}
    for size in (2, 8, 16, 32, 64, 128):
        ids = [f"fixed_word_m{size}_{i:03d}" for i in (0, 9, 19)]
        for limit in (1, 2):
            values = [case_medians[("fixed-word", size, case_id, limit)] for case_id in ids]
            fixed[f"m{size}_limit{limit}"] = {
                "cases": len(values), "per_case_medians_seconds": values,
                "median_of_case_medians_seconds": statistics.median(values),
                "maximum_case_median_seconds": max(values),
            }
    result = {
        "status": "postprocessed_from_accepted_captures_only",
        "ledger_rows": len(ledger),
        "timing_per_case_medians": len(case_medians),
        "general_vs_fair": comparison,
        "fixed_word_by_size": fixed,
        "method_ordering": "general ran before fair-reference; method-block ordering bias remains",
        "timing_measurement": "fresh-process subprocess_seconds includes interpreter startup, input read, provider solve, serialization",
        "source_ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
    }
    OUT.mkdir(parents=True, exist_ok=False)
    target = OUT / "report.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

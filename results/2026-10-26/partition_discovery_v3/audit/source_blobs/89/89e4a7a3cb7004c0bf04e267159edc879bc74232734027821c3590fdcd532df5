"""Run a small, fixed set of structural controls against exact providers."""
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
C003 = ROOT / "results/2026-10-26/partition_discovery_v3"
SMOKE = C003 / "structural/smoke_inputs_v1.json"
BASELINE = ROOT / "results/2026-10-26/partition_constraints_v2/baseline/partition_solver.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    source = json.loads(SMOKE.read_text(encoding="utf-8"))
    selected = {
        "odd_cycle": "odd_cycle",
        "accepted_negative_conflict": "negative_conflict",
        "count_variation": "count_inconsistency",
        "absent_symbol": "absent_symbol",
        "single_positive": "one_positive_unique_but_no_certificate",
        "empty_positive": "no_positive",
        "duplicates_permuted": "normalize_duplicate_words",
        "deadline_expired": "limit_2",
    }
    cases = {r["case_id"]: r["input"] for r in source["cases"]}
    general = load("boundary_general", C003 / "general/general_solver.py")
    fair = load("boundary_fair", C003 / "general/fair_reference.py")
    baseline = load("boundary_baseline", BASELINE)
    for name, case_id in selected.items():
        data = cases[case_id]
        if name == "deadline_expired":
            deadline = time.perf_counter() - 1
            g = general.solve(data, deadline=deadline, max_solutions=None)
            f = fair.solve(data, deadline=deadline, max_solutions=None)
            expected = None
        else:
            g = general.solve(data, max_solutions=None)
            f = fair.solve(data, max_solutions=None)
            expected = baseline.solve(data)
        record = {"control": name, "source_case_id": case_id, "input": data,
                  "general": g, "fair_reference": f, "baseline": expected}
        sys.stdout.write(json.dumps(record, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
        sys.stdout.flush()
        if name == "duplicates_permuted":
            clean = {"alphabet": sorted(set(data["alphabet"])),
                     "positive": sorted(set(data["positive"])),
                     "negative": sorted(set(data["negative"]))}
            g2 = general.solve(clean, max_solutions=None)
            f2 = fair.solve(clean, max_solutions=None)
            expected2 = baseline.solve(clean)
            normalized = {"control": "permutation_deduplicated",
                          "source_case_id": case_id, "input": clean,
                          "general": g2, "fair_reference": f2,
                          "baseline": expected2}
            sys.stdout.write(json.dumps(normalized, ensure_ascii=False,
                                        separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

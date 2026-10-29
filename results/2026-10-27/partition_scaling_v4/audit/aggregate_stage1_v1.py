"""Reconcile the frozen C004 stage-1 measurement ledger and summarize it."""
from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
CORPUS = HERE / "corpora" / "stage1_v4"
RUN = HERE / "timed_runs" / "stage1_r1"
LEDGER = RUN / "ledger.jsonl"
PROTOCOL = HERE / "stage1_protocol_freeze_v4.json"
REPORT = HERE / "stage1_performance_report_v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    protocol = read_json(PROTOCOL)
    ledger = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = read_json(CORPUS / "manifest.json")
    case_meta = {row["id"]: row for row in manifest["cases"]}
    expected_groups = {
        "standard": protocol["ordering"]["standard_jobs"],
        "stress": protocol["ordering"]["stress_jobs"],
        "memory": protocol["ordering"]["memory_jobs"],
    }
    expected_ids = {job["job_id"] for group in expected_groups.values() for job in group}
    rows_by_id = {row["job_id"]: row for row in ledger}
    duplicate_ids = sorted(job_id for job_id, count in Counter(row["job_id"] for row in ledger).items() if count != 1)
    missing_ids = sorted(expected_ids - set(rows_by_id))
    unexpected_ids = sorted(set(rows_by_id) - expected_ids)
    expected_counts = {phase: len(jobs) for phase, jobs in expected_groups.items()}
    actual_counts = dict(Counter(row["phase"] for row in ledger))
    statuses = Counter(row["independent_check"]["status"] for row in ledger)
    permitted_statuses = {"pass", "censored_incomplete", "censored_external_timeout"}
    disallowed = [row["job_id"] for row in ledger if row["independent_check"]["status"] not in permitted_statuses]

    sums = defaultdict(float)
    phase_sums = defaultdict(float)
    for row in ledger:
        sec = row.get("subprocess_seconds") or 0.0
        if row["phase"] in ("standard", "stress"):
            sums[row["provider"]] += sec
        if row["phase"] == "stress":
            phase_sums[row["phase"]] += sec
    budget_ok = all(sec <= 900 for sec in sums.values()) and phase_sums["stress"] <= 180

    # Compare normalized first answers on the fixed-word bridge. This is a
    # post-capture semantic comparison and is intentionally outside timing.
    bridge_cases = sorted({row["case"] for row in ledger
                           if row["phase"] == "standard" and row["provider"] == "C003-fixed-word"})
    bridge = []
    bridge_match_ok = True
    for case_id in bridge_cases:
        case_rows = {row["provider"]: {row["repetition"]: row for row in ledger
                                      if row["phase"] == "standard" and row["case"] == case_id
                                      and row["provider"] in ("S001", "C003-fixed-word")}}
        pair_rows = []
        for repetition in sorted(case_rows.get("S001", {})):
            new_row = case_rows["S001"][repetition]
            old_row = case_rows["C003-fixed-word"].get(repetition)
            if old_row is None:
                bridge_match_ok = False
                pair_rows.append({"repetition": repetition, "status": "missing_pair"})
                continue
            status = "censored"
            if (new_row["independent_check"]["status"] == "pass"
                    and old_row["independent_check"]["status"] == "pass"):
                new_summary = read_json(Path(new_row["attempt_dir"]) / "stdout.bin")
                old_summary = read_json(Path(old_row["attempt_dir"]) / "stdout.bin")
                match = new_summary.get("solutions") == old_summary.get("solutions")
                status = "answer_match" if match else "answer_mismatch"
                bridge_match_ok = bridge_match_ok and match
            pair_rows.append({"repetition": repetition,
                              "s001_seconds": new_row.get("subprocess_seconds"),
                              "c003_seconds": old_row.get("subprocess_seconds"),
                              "s001_check": new_row["independent_check"]["status"],
                              "c003_check": old_row["independent_check"]["status"],
                              "status": status})
        bridge.append({"case": case_id, "alpha": case_meta[case_id]["alphabet_size"],
                       "k": case_meta[case_id]["k"], "length": case_meta[case_id]["length"],
                       "pairs": pair_rows})

    cell_summaries = []
    for provider in ("S001", "C003-fixed-word", "general-v3"):
        cases = sorted({row["case"] for row in ledger
                        if row["phase"] == "standard" and row["provider"] == provider})
        for case_id in cases:
            selected = [row for row in ledger if row["phase"] == "standard"
                        and row["provider"] == provider and row["case"] == case_id]
            times = [row["subprocess_seconds"] for row in selected]
            cell_summaries.append({
                "provider": provider, "case": case_id,
                "family": case_meta[case_id]["family"],
                "alphabet_size": case_meta[case_id]["alphabet_size"],
                "k": case_meta[case_id]["k"], "word_length": case_meta[case_id]["length"],
                "positive_count": case_meta[case_id]["positive_count"],
                "negative_count": case_meta[case_id]["negative_count"],
                "repetitions": [{"job_id": row["job_id"],
                                 "seconds": row.get("subprocess_seconds"),
                                 "status": row["scientific_status"],
                                 "check": row["independent_check"]["status"]}
                                for row in selected],
                "observed_median_seconds": statistics.median(times) if times else None,
                "completed_median_seconds": statistics.median(
                    [row["subprocess_seconds"] for row in selected
                     if row["independent_check"]["status"] == "pass"])
                    if any(row["independent_check"]["status"] == "pass" for row in selected) else None,
            })

    memory = []
    for row in ledger:
        if row["phase"] == "memory":
            memory.append({"job_id": row["job_id"], "provider": row["provider"],
                           "case": row["case"], "seconds": row.get("subprocess_seconds"),
                           "peak_traced_python_bytes": row["independent_check"].get("peak_traced_python_bytes"),
                           "scientific_status": row["scientific_status"],
                           "check": row["independent_check"]["status"]})

    gates = {
        "expected_counts_match": actual_counts == expected_counts,
        "all_expected_jobs_present_once": not missing_ids and not unexpected_ids and not duplicate_ids,
        "all_independent_checks_pass_or_censored": not disallowed,
        "bridge_completed_answers_match": bridge_match_ok,
        "provider_and_stress_budgets_respected": budget_ok,
        "ledger_rows": len(ledger),
        "missing_job_ids": missing_ids,
        "unexpected_job_ids": unexpected_ids,
        "duplicate_job_ids": duplicate_ids,
        "disallowed_check_job_ids": disallowed,
    }
    acceptance = all(value for key, value in gates.items() if isinstance(value, bool))
    result = {
        "schema": "C004-stage1-performance-report-v1",
        "acceptance": "accepted" if acceptance else "rejected",
        "protocol_sha256": sha(PROTOCOL),
        "corpus_manifest_sha256": sha(CORPUS / "manifest.json"),
        "corpus_freeze_record_sha256": sha(CORPUS / "corpus_freeze_v2.json"),
        "runtime_stage1_sha256": sha(PROJECT / "coordination" / "runtime_stage1.json"),
        "stage1_gate_report_sha256": sha(HERE / "stage1_gate_report_v1.json"),
        "run_manifest_sha256": sha(RUN / "run_manifest.json"),
        "ledger_sha256": sha(LEDGER),
        "runner_sha256": sha(HERE / "timed_provider_run_v1.py"),
        "aggregate_script_sha256": sha(Path(__file__)),
        "counts": {"expected": expected_counts, "actual": actual_counts,
                   "independent_check_statuses": dict(statuses)},
        "measured_seconds": {"standard_and_stress_by_provider": dict(sums),
                             "stress_total": phase_sums["stress"],
                             "limits_seconds": {"provider": 900, "stress_total": 180}},
        "gates": gates,
        "bridge": bridge,
        "standard_cells": cell_summaries,
        "stress_rows": [{"job_id": row["job_id"], "provider": row["provider"],
                         "case": row["case"], "seconds": row.get("subprocess_seconds"),
                         "scientific_status": row["scientific_status"],
                         "check": row["independent_check"]["status"]}
                        for row in ledger if row["phase"] == "stress"],
        "memory_rows": memory,
        "interpretation_limits": [
            "General-v3 rows are found first answers on finite samples; they do not establish global uniqueness.",
            "Context-regular rows are sample-compatible scaling cases, not full contextual-witness recovery certificates.",
            "The old fixed-word solver at alpha=128,length=4096 reached its internal deadline in all three repetitions; retain all as censored and do not compute a speed ratio for that cell.",
            "Allocation measurements are tracemalloc Python allocation peaks, not process RSS.",
            "General-v3 graph preprocessing has a worst-case quadratic negative-word materialization component; these measurements do not prove globally linear preprocessing.",
        ],
    }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"acceptance": result["acceptance"], "gates": gates,
                      "counts": result["counts"], "measured_seconds": result["measured_seconds"],
                      "report": str(REPORT), "sha256": sha(REPORT)}, ensure_ascii=False))
    if not acceptance:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

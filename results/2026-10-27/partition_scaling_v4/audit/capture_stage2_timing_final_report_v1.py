"""Capture creation of the compact Stage2 timing gate and Persian report."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
AGGREGATE_ATTEMPTS = [
    "20261029T085410.908640Z_165a89ef3d",
    "20261029T085455.184101Z_0ff6dc9062",
    "20261029T085528.010634Z_373cccb9da",
]

def main() -> int:
    sys.path.insert(0, str(HERE))
    from capture import capture
    protocol = json.loads((HERE / "stage2_timing_protocol_v1.json").read_text(encoding="utf-8-sig"))
    ledger = json.loads((HERE / "stage2_timing_execution_ledger_v1.json").read_text(encoding="utf-8-sig"))
    corpus = json.loads((HERE / "corpora" / "stage2_v1" / "manifest.json").read_text(encoding="utf-8-sig"))
    cases = {row["id"]: row for row in corpus["cases"]}
    sources = [
        Path(__file__).resolve(), HERE / "finalize_stage2_timing_report_v1.py",
        HERE / "stage2_timing_report_v1.json", HERE / "stage2_timing_protocol_v1.json",
        HERE / "stage2_timing_protocol_freeze_v1.json", HERE / "stage2_timing_execution_ledger_v1.json",
        HERE / "stage2_timing_preservation_inventory_v1.json", HERE / "stage2_timing_refreeze_erratum_01.json",
        HERE / "stage2_timing_wrapper_failure_v1.json",
        HERE / "stage2_timing_execution_ledger_pre_executor_fix_001.json",
        HERE / "stage1_performance_report_v2.json", HERE / "STAGE1_SCOPE_ERRATUM_01.md",
        HERE / "stage2_gate_report_v1.json", HERE / "capture.py",
        HERE / "timed_stage2_full_api_v1.py", HERE / "execute_stage2_timing_v1.py",
        HERE / "freeze_stage2_timing_protocol_v1.py",
        HERE / "aggregate_stage2_timing_v1.py", HERE / "capture_stage2_timing_aggregate_v1.py",
        HERE / "corpora" / "stage2_v1" / "manifest.json",
        HERE / "corpora" / "stage2_v1" / "freeze_v1.json",
        PROJECT / "coordination" / "runtime_stage2_r2.json",
        PROJECT / "solver_v2.py", PROJECT / "general" / "known_k_v3.py",
        PROJECT / "structural" / "singleton_solver_v1.py",
        PROJECT / "structural" / "singleton_solver_v2.py",
        PROJECT / "structural" / "singleton_solver_v4.py",
        PROJECT / "structural" / "bounded_certificate_v1.py",
    ]
    for case in protocol["cases"].values():
        sources.append(HERE / case["input_path"])
        sources.append(HERE / "corpora" / "stage2_v1" / cases[case["case_id"]]["truth"])
    for attempt_id in [row["attempt_id"] for row in ledger["jobs"]] + AGGREGATE_ATTEMPTS:
        attempt_dir = HERE / "attempts" / attempt_id
        for name in ("manifest.json", "result.json", "stdout.bin", "stderr.bin"):
            sources.append(attempt_dir / name)
    command = [sys.executable, "-B", "-X", "utf8", str(HERE / "finalize_stage2_timing_report_v1.py")]
    result = capture("stage2_timing_final_report_v1", command, cwd=HERE,
                     timeout_seconds=60.0, source_paths=sources)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if result["execution_status"] != "success" or result["exit_code"] != 0:
        raise SystemExit(2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

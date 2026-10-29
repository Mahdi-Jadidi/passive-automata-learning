"""Capture the read-only Stage2 timing validator and its complete evidence inputs."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

def main() -> int:
    sys.path.insert(0, str(HERE))
    from capture import capture

    protocol = json.loads((HERE / "stage2_timing_protocol_v1.json").read_text(encoding="utf-8-sig"))
    ledger = json.loads((HERE / "stage2_timing_execution_ledger_v1.json").read_text(encoding="utf-8-sig"))
    corpus = json.loads((HERE / "corpora" / "stage2_v1" / "manifest.json").read_text(encoding="utf-8-sig"))
    rows = {row["id"]: row for row in corpus["cases"]}
    sources = [
        Path(__file__).resolve(), HERE / "aggregate_stage2_timing_v1.py",
        HERE / "stage2_timing_protocol_v1.json", HERE / "stage2_timing_protocol_freeze_v1.json",
        HERE / "stage2_timing_execution_ledger_v1.json",
        HERE / "stage2_timing_preservation_inventory_v1.json",
        HERE / "stage2_timing_refreeze_erratum_01.json",
        HERE / "stage2_timing_wrapper_failure_v1.json",
        HERE / "stage2_timing_execution_ledger_pre_executor_fix_001.json",
        HERE / "timed_stage2_full_api_v1.py", HERE / "execute_stage2_timing_v1.py",
        HERE / "freeze_stage2_timing_protocol_v1.py", HERE / "capture.py",
        HERE / "stage2_gate_report_v1.json", HERE / "stage1_performance_report_v2.json",
        HERE / "STAGE1_SCOPE_ERRATUM_01.md",
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
        sources.append(HERE / "corpora" / "stage2_v1" / rows[case["case_id"]]["truth"])
    for job in ledger["jobs"]:
        attempt_dir = HERE / "attempts" / job["attempt_id"]
        for name in ("manifest.json", "result.json", "stdout.bin", "stderr.bin"):
            sources.append(attempt_dir / name)
    command = [sys.executable, "-B", "-X", "utf8", str(HERE / "aggregate_stage2_timing_v1.py")]
    result = capture("stage2_timing_aggregate_v1", command, cwd=HERE,
                     timeout_seconds=120.0, source_paths=sources)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if result["execution_status"] != "success" or result["exit_code"] != 0:
        raise SystemExit(2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

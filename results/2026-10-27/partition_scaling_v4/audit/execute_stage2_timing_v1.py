"""Serial execution wrapper for the frozen C004 Stage2 matched timing schedule."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
PROTOCOL = HERE / "stage2_timing_protocol_v1.json"
LEDGER = HERE / "stage2_timing_execution_ledger_v1.json"
PYTHON = Path(sys.executable)


def main() -> int:
    sys.path.insert(0, str(HERE))
    from capture import capture

    protocol_raw = PROTOCOL.read_bytes()
    protocol = json.loads(protocol_raw.decode("utf-8-sig"))
    protocol_sha256 = hashlib.sha256(protocol_raw).hexdigest()
    if protocol.get("status") != "frozen" or protocol.get("authorization") != "master_serial_timing_go":
        raise SystemExit("timing protocol is not frozen/authorized")
    for relpath, expected in protocol["source_bindings"].items():
        path = PROJECT / relpath
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"frozen source hash changed: {relpath}")
    for case in protocol["cases"].values():
        path = HERE / case["input_path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != case["input_sha256"]:
            raise SystemExit(f"frozen public input hash changed: {case['case_id']}")
    ledger = {"schema": "C004-stage2-timing-execution-ledger-v1",
              "protocol_sha256": protocol_sha256, "jobs": []}
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source_paths = [
        Path(__file__).resolve(), HERE / "timed_stage2_full_api_v1.py", PROTOCOL,
        HERE / "capture.py", HERE / "stage2_timing_wrapper_failure_v1.json",
        HERE / "stage2_timing_execution_ledger_pre_executor_fix_001.json",
        HERE / "freeze_stage2_timing_protocol_v1.py",
        HERE / "stage2_timing_protocol_freeze_v1.json",
        PROJECT / "coordination" / "runtime_stage2_r2.json",
        PROJECT / "solver_v2.py", PROJECT / "general" / "known_k_v3.py",
        PROJECT / "structural" / "singleton_solver_v1.py",
        PROJECT / "structural" / "singleton_solver_v2.py",
        PROJECT / "structural" / "singleton_solver_v4.py",
        PROJECT / "structural" / "bounded_certificate_v1.py",
        HERE / "stage2_gate_report_v1.json",
        HERE / "corpora" / "stage2_v1" / "manifest.json",
        HERE / "corpora" / "stage2_v1" / "freeze_v1.json",
        HERE / "stage1_performance_report_v2.json",
        HERE / "STAGE1_SCOPE_ERRATUM_01.md",
    ]
    corpus_manifest = json.loads((HERE / "corpora" / "stage2_v1" / "manifest.json").read_text(encoding="utf-8-sig"))
    corpus_cases = {row["id"]: row for row in corpus_manifest["cases"]}
    for case in protocol["cases"].values():
        source_paths.append(HERE / case["input_path"])
        truth_path = corpus_cases[case["case_id"]]["truth"]
        if truth_path:
            source_paths.append(HERE / "corpora" / "stage2_v1" / truth_path)

    for job in protocol["wall_schedule"] + protocol["memory_schedule"]:
        command = [str(PYTHON), "-B", "-X", "utf8",
                   str(HERE / "timed_stage2_full_api_v1.py"),
                   job["method"], job["case"]]
        if job["memory"]:
            command.append("--memory")
        attempt = capture(
            f"stage2_timing_{job['job_id']}", command, cwd=HERE,
            timeout_seconds=30.0, source_paths=source_paths)
        entry = {"protocol_sha256": protocol_sha256, **job, **{key: attempt.get(key) for key in
                           ("attempt_id", "execution_status", "exit_code", "duration_seconds",
                            "subprocess_seconds", "stdout_bytes", "stdout_sha256",
                            "stderr_bytes", "stderr_sha256", "attempt_dir")}}
        ledger["jobs"].append(entry)
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Captured integration smoke tests for the adopted runner and durable capture."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, f"unable to load {path}")
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    audit = root / "audit"
    support = audit / "benchmark_adopted"
    out = support / "smoke" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
                               + "_" + uuid4().hex[:8])
    out.mkdir(parents=True, exist_ok=False)

    runner = load_module(support / "runner.py", "adopted_benchmark_runner_smoke")
    spec = importlib.util.spec_from_file_location("adopted_durable_capture_smoke", audit / "capture.py")
    capture = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "unable to load adopted capture")
    spec.loader.exec_module(capture)
    cases, _, _ = runner.read_cases(root)
    case = next(item for item in cases if len(item["input"]["alphabet"]) == 4)
    input_path = out / "success_input.json"
    input_path.write_bytes(runner.canonical(case["input"]))
    worker = support / "worker.py"
    source_paths = [root / path for path in runner.EXPECTED]
    source_paths += [root / "coordination/runtime_manifest.json", support / "runner.py",
                     worker, Path(__file__).resolve(), input_path]

    success_sidecar = out / "success.worker.json"
    success_command = [sys.executable, "-B", "-X", "utf8", str(worker), str(root),
                       str(input_path), "baseline", "timing", str(success_sidecar), "30"]
    success_capture = capture.capture("benchmark-integration-smoke-success", success_command,
                                      cwd=root, timeout_seconds=10,
                                      source_paths=source_paths)
    success_attempt_dir = Path(success_capture["attempt_dir"])
    success_raw = (success_attempt_dir / "stdout.bin").read_bytes()
    success_result = json.loads(success_raw.decode("utf-8-sig"))
    success_meta = read_json(success_sidecar)
    success_status = runner.classify(success_capture, success_result, success_meta,
                                     {"method": "baseline", "mode": "timing"})
    require(success_capture["execution_status"] == "success" and success_capture["child_reaped"] is True,
            "success child was not captured and reaped")
    require(success_status == "complete", f"success status classified as {success_status}")
    require(isinstance(success_capture.get("subprocess_seconds"), (int, float))
            and not isinstance(success_capture.get("subprocess_seconds"), bool)
            and math.isfinite(success_capture["subprocess_seconds"])
            and success_capture["subprocess_seconds"] >= 0,
            "durable capture process clock is missing or invalid")

    timeout_child = out / "timeout_child.py"
    timeout_child.write_text(
        "import sys, time\n"
        "print('ready', flush=True)\n"
        "print('diagnostic', file=sys.stderr, flush=True)\n"
        "time.sleep(2)\n", encoding="utf-8")
    timeout_capture = capture.capture("benchmark-integration-smoke-timeout",
                                      [sys.executable, "-B", "-X", "utf8", str(timeout_child)],
                                      cwd=root, timeout_seconds=0.1,
                                      source_paths=[timeout_child])
    timeout_dir = Path(timeout_capture["attempt_dir"])
    timeout_stdout = (timeout_dir / "stdout.bin").read_bytes()
    timeout_stderr = (timeout_dir / "stderr.bin").read_bytes()
    timeout_status = runner.classify(timeout_capture, None, None,
                                     {"method": "baseline", "mode": "timing"})
    require(timeout_capture["execution_status"] == "timed_out" and timeout_status == "timed_out",
            "timeout was not preserved as authoritative")
    require(timeout_capture["child_reaped"] is True, "timed-out child was not reaped")
    require(b"ready" in timeout_stdout and b"diagnostic" in timeout_stderr,
            "flushed partial output was not preserved")

    incomplete_input = out / "incomplete_input.json"
    incomplete_input.write_bytes(runner.canonical({"alphabet": ["a", "b", "c"],
                                                    "positive": ["ab", "ac"],
                                                    "negative": ["abc"]}))
    incomplete_sidecar = out / "incomplete.worker.json"
    incomplete_command = [sys.executable, "-B", "-X", "utf8", str(worker), str(root),
                          str(incomplete_input), "baseline", "timing",
                          str(incomplete_sidecar), "0"]
    incomplete_capture = capture.capture("benchmark-integration-smoke-incomplete",
                                         incomplete_command, cwd=root, timeout_seconds=5,
                                         source_paths=[*source_paths, incomplete_input])
    incomplete_dir = Path(incomplete_capture["attempt_dir"])
    incomplete_result = json.loads((incomplete_dir / "stdout.bin").read_text(encoding="utf-8"))
    incomplete_meta = read_json(incomplete_sidecar)
    incomplete_status = runner.classify(incomplete_capture, incomplete_result, incomplete_meta,
                                        {"method": "baseline", "mode": "timing"})
    require(incomplete_capture["execution_status"] == "program_error"
            and incomplete_capture["exit_code"] == 3 and incomplete_status == "incomplete",
            "valid exit-3 incomplete output was misclassified")
    require(incomplete_result["complete"] is False
            and incomplete_result["feasible_partition_count"] is None
            and incomplete_result["found_partition_count"] == len(incomplete_result["feasible_partitions"]),
            "incomplete output contract is malformed")

    valid_complete_result = success_result
    valid_complete_sidecar = success_meta
    interrupted_fixture = {**success_capture, "execution_status": "interrupted"}
    interrupted_status = runner.classify(interrupted_fixture, valid_complete_result,
                                         valid_complete_sidecar,
                                         {"method": "baseline", "mode": "timing"})
    require(interrupted_status == "interrupted", "raw interrupted status was not authoritative")
    cleanup_fixture = {"execution_status": "capture_error", "cleanup_error": "simulated",
                       "child_reaped": False}
    cleanup_abort = runner.capture_abort_reason(cleanup_fixture, True, False)
    require(cleanup_abort == "capture_cleanup_failure_child_may_still_be_running",
            "unreaped child does not stop suite supervisor")
    invalid_clock_abort = runner.capture_abort_reason({"execution_status": "success", "child_reaped": True},
                                                      False, False)
    require(invalid_clock_abort == "capture_subprocess_clock_invalid_method_budget_unchargeable",
            "invalid process clock did not stop suite supervisor")

    report = {
        "smoke_id": out.name,
        "scientific_status": "harness_integration_smoke_passed",
        "execution_status": "success",
        "capture_backend": "B-CAPTURE-R1",
        "original_candidate_hashes": {
            "capture_candidate_sha256": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
            "benchmark_runner_sha256": "16876ce34ab9fe6f077e0925324770374a17964eadbb3b8bd97dfeca15b30d68",
            "benchmark_worker_sha256": "f1bb4866244587ff02c31dccd7e23e7ba7451cdba3cdd901cab0379b5ae5b801",
        },
        "checks": {
            "success_complete": {"status": success_status, "capture": success_capture,
                                  "solver_result": success_result, "worker": success_meta},
            "timeout_partial_output_and_reaping": {"status": timeout_status,
                "capture": timeout_capture, "stdout_sha256": sha(timeout_stdout),
                "stderr_sha256": sha(timeout_stderr), "stdout": timeout_stdout.decode("utf-8", "replace"),
                "stderr": timeout_stderr.decode("utf-8", "replace")},
            "incomplete_exit3": {"status": incomplete_status, "capture": incomplete_capture,
                                 "solver_result": incomplete_result, "worker": incomplete_meta},
            "interrupted_authoritative": {"status": interrupted_status},
            "cleanup_failure_aborts": {"abort_reason": cleanup_abort},
            "invalid_clock_aborts": {"abort_reason": invalid_clock_abort},
        },
        "limitations": ["Timeout and cleanup behavior controls the direct child only.",
                        "This smoke does not run the 1200-job performance suite or certify its outputs."],
    }
    report_path = out / "smoke_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report_path": str(report_path), "report_sha256": sha(report_path.read_bytes()),
                      "smoke_id": out.name, "checks": {name: value.get("status", "passed")
                                                           for name, value in report["checks"].items()}},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

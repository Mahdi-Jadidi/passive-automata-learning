"""Run the independent benchmark auditor through the durable capture backend."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, type=Path)
    args = parser.parse_args(argv)
    suite = args.suite.resolve(strict=True)
    capture_path = AUDIT / "capture.py"
    spec = importlib.util.spec_from_file_location("durable_capture_for_benchmark_audit", capture_path)
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)

    corpus_manifest = AUDIT / "corpus/frozen_v1/manifest.json"
    corpus = json.loads(corpus_manifest.read_text(encoding="utf-8"))
    dataset_path = AUDIT / "corpus/frozen_v1" / corpus["datasets"]["performance_100"]["path"]
    runtime_manifest = CYCLE / "coordination/runtime_manifest.json"
    runtime = json.loads(runtime_manifest.read_text(encoding="utf-8"))
    runner = AUDIT / "benchmark_adopted/runner.py"
    worker = AUDIT / "benchmark_adopted/worker.py"
    sources = [Path(__file__).resolve(), AUDIT / "validate_benchmark.py",
               AUDIT / "validate_saved_correctness.py", corpus_manifest, dataset_path,
               runtime_manifest, suite / "plan.json", suite / "jobs.jsonl",
               suite / "summary.json", suite / "support_sources_before.json",
               suite / "support_sources_after.json", runner, worker]
    sources.extend(CYCLE / item["path"] for item in runtime["files"])
    command = [sys.executable, "-B", "-X", "utf8",
               str(AUDIT / "validate_benchmark.py"), "--suite", str(suite)]
    attempt = capture.capture("independent_performance_output_validation", command,
                              cwd=CYCLE, timeout_seconds=600,
                              source_paths=sources)
    stdout_path = Path(attempt["attempt_dir"]) / "stdout.bin"
    stdout = stdout_path.read_bytes().decode("utf-8-sig", errors="replace")
    try:
        validator_result = json.loads(stdout.strip())
    except ValueError:
        validator_result = None
    print(json.dumps({"capture_attempt": attempt,
                      "validator_stdout": validator_result,
                      "validator_stdout_text": None if validator_result is not None else stdout},
                     ensure_ascii=False, sort_keys=True))
    if attempt.get("cleanup_error") is not None or attempt.get("child_reaped") is not True:
        return 4
    if attempt.get("execution_status") != "success":
        return 3
    return attempt.get("exit_code") if isinstance(attempt.get("exit_code"), int) else 5


if __name__ == "__main__":
    raise SystemExit(main())

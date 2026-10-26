"""Adopted serial benchmark harness for the durable B-CAPTURE-R1 backend.

Uses the capture API's subprocess_seconds clock directly. No correctness oracle
is implemented: an independent validator must verify every saved output.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import statistics
import sys
import time
from uuid import uuid4

CAPTURE_BACKEND = "B-CAPTURE-R1"

METHODS = ("baseline", "eager", "lazy")
EXPECTED = {
    "solver.py": "6801941c97ec0cd60200d01be540a357f0f16220c8c747289bd8dcbb44a37f36",
    "common/engine.py": "5bcd3459bf98efea499dd1edc2f60c2db21fd89f9b84a9950685aba1f00d8468",
    "common/helpers.py": "f9d905b79dea4740f7eecd3e586b1c8d7b093639f158b7b7757757da7b2904d1",
    "approaches/eager/eager_solver.py": "e4f0c0b5228cde9207fe30a94f7b5e0dea13aa49c2cff23d8c291ffa4064f069",
    "approaches/lazy/lazy_solver.py": "3445dfc281c23b3434b71081c2c01e11959b9589c4174aad91d3e29f35ce7c24",
    "baseline/partition_solver.py": "b0572bf8115d9188a6dbf20b6b6c8c70126cdf0cf9c7de4554ce2b36efdc702c",
}
RUNTIME_MANIFEST_HASH = "b7a5b30974500ea610689a7d6ca627437508d6cf63a59fd5e8b6c5a18206859b"
DATASET_HASH = "509928210c1075d502d7244f0c5a8f5f75d0b65b33298ddbe288995e0ef5ce20"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def append_record(path, value):
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(value).decode("utf-8") + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def runtime_check(root):
    checks = []
    for relative, expected in EXPECTED.items():
        path = root / relative
        actual = sha(path.read_bytes()) if path.is_file() else None
        checks.append({"path": relative, "expected": expected,
                       "actual": actual, "matches": actual == expected})
    manifest = root / "coordination/runtime_manifest.json"
    actual = sha(manifest.read_bytes()) if manifest.is_file() else None
    checks.append({"path": "coordination/runtime_manifest.json",
                   "expected": RUNTIME_MANIFEST_HASH, "actual": actual,
                   "matches": actual == RUNTIME_MANIFEST_HASH})
    return {"runtime_version": "C002-R1", "files": checks,
            "all_match": all(item["matches"] for item in checks)}


def read_cases(root):
    corpus = root / "audit/corpus/frozen_v1"
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    dataset = manifest["datasets"]["performance_100"]
    path = corpus / dataset["path"]
    raw = path.read_bytes()
    if sha(raw) != DATASET_HASH or dataset["sha256"] != DATASET_HASH:
        raise ValueError("performance_100 frozen hash mismatch")
    cases = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(cases) != 100 or dataset["count"] != 100:
        raise ValueError("expected exactly 100 performance cases")
    expected_inputs = {item["case_id"]: item["sha256"]
                       for item in dataset["case_input_hashes"]}
    if len({item["case_id"] for item in cases}) != 100:
        raise ValueError("duplicate case ID")
    for item in cases:
        if (set(item["input"]) != {"alphabet", "positive", "negative"}
                or item["dataset"] != "performance_100"
                or sha(canonical(item["input"])) != item["input_sha256"]
                or item["input_sha256"] != expected_inputs[item["case_id"]]):
            raise ValueError("case input contract/hash mismatch")
    # No generator truth sidecar is opened, loaded or passed to any process.
    return sorted(cases, key=lambda item: item["case_id"]), path, corpus / "manifest.json"


def job_plan(cases):
    jobs = []
    for mode, repetitions in (("timing", 3), ("memory", 1)):
        for repetition in range(repetitions):
            for index, case in enumerate(cases):
                offset = (index + repetition) % len(METHODS)
                order = METHODS[offset:] + METHODS[:offset]
                for method in order:
                    jobs.append({"job_id": f"{mode}_{repetition}_{case['case_id']}_{method}",
                                 "case_id": case["case_id"], "method": method,
                                 "mode": mode, "repetition": repetition,
                                 "alphabet_size": len(case["input"]["alphabet"])})
    return jobs


def classify(attempt, result, sidecar, job):
    raw_status = attempt["execution_status"]
    if raw_status == "interrupted":
        return "interrupted"
    if raw_status == "timed_out":
        return "timed_out"
    if raw_status in ("environment_error", "capture_error"):
        return raw_status
    code = attempt["exit_code"]
    if (not isinstance(result, dict) or not isinstance(sidecar, dict)
            or sidecar.get("exit_code") != code
            or sidecar.get("method") != job["method"]
            or sidecar.get("mode") != job["mode"]
            or result.get("method") != job["method"]
            or not isinstance(sidecar.get("pipeline_seconds"), (int, float))
            or not math.isfinite(sidecar["pipeline_seconds"])
            or sidecar["pipeline_seconds"] < 0):
        return "program_error"
    if job["mode"] == "memory":
        peak = sidecar.get("python_traced_peak_bytes")
        if type(peak) is not int or peak < 0:
            return "program_error"
    if (code == 0 and result.get("complete") is True
            and result.get("status") in ("unique", "ambiguous", "infeasible")):
        return "complete"
    if (code == 3 and result.get("complete") is False
            and result.get("status") == "incomplete"
            and result.get("feasible_partition_count") is None):
        return "incomplete"
    return "program_error"


def capture_abort_reason(attempt, clock_valid, interrupt_requested=False):
    if attempt.get("cleanup_error") is not None or attempt.get("child_reaped") is False:
        return "capture_cleanup_failure_child_may_still_be_running"
    if not clock_valid:
        return "capture_subprocess_clock_invalid_method_budget_unchargeable"
    if interrupt_requested or attempt.get("execution_status") == "interrupted":
        return "interrupted_after_active_subprocess_was_captured"
    return None


def distribution(values):
    return {"n": len(values), "min": min(values), "median": statistics.median(values),
            "max": max(values)} if values else {"n": 0}


def resource_value(record, field):
    if field in ("output_bytes", "found_partition_count", "process_elapsed_seconds"):
        return record.get(field)
    return record.get("solver_metrics", {}).get(field)


def summaries(records):
    summary = {"scientific_status": "independent_output_validation_required",
               "status_counts": {}, "paired_complete_only": [],
               "censoring_policy": "No replacement of incomplete/timeout/skipped by a time estimate; no instrumented speed comparisons."}
    for mode in ("timing", "memory"):
        for method in METHODS:
            selected = [r for r in records if r["mode"] == mode and r["method"] == method]
            summary["status_counts"][f"{mode}/{method}"] = dict(Counter(r["status"] for r in selected))
    by_key = {(r["mode"], r["case_id"], r["repetition"], r["method"]): r for r in records}
    for mode, repetitions, metric in (("timing", 3, "pipeline_seconds"),
                                       ("memory", 1, "python_traced_peak_bytes")):
        for method in ("eager", "lazy"):
            case_ids = sorted({r["case_id"] for r in records if r["mode"] == mode})
            comparable = []
            baseline_values, method_values, ratios = [], [], []
            resource_fields = ("nodes_visited", "complete_assignments", "constraints_stored",
                               "output_bytes", "found_partition_count", "process_elapsed_seconds",
                               "preprocessing_seconds", "separation_seconds", "cut_generation_seconds",
                               "lazy_cuts", "answer_blockers", "search_restarts")
            resources = {name: {field: [] for field in resource_fields}
                         for name in ("baseline", method)}
            for case_id in case_ids:
                pairs = [(by_key.get((mode, case_id, rep, "baseline")),
                          by_key.get((mode, case_id, rep, method))) for rep in range(repetitions)]
                if not all(a and b and a["status"] == b["status"] == "complete"
                           and isinstance(a.get("worker", {}).get(metric), (int, float))
                           and isinstance(b.get("worker", {}).get(metric), (int, float)) for a, b in pairs):
                    continue
                av = statistics.median(a["worker"][metric] for a, _ in pairs)
                bv = statistics.median(b["worker"][metric] for _, b in pairs)
                comparable.append(case_id)
                baseline_values.append(av)
                method_values.append(bv)
                if bv > 0:
                    ratios.append(av / bv)
                for name, rows in (("baseline", [a for a, _ in pairs]),
                                   (method, [b for _, b in pairs])):
                    for field in resource_fields:
                        values = [resource_value(row, field) for row in rows]
                        if all(isinstance(value, (int, float)) for value in values):
                            resources[name][field].append(statistics.median(values))
            summary["paired_complete_only"].append({
                "mode": mode, "method": method, "metric": metric,
                "requires_independent_output_validation_before_publication": True,
                "case_ids": comparable, "case_count": len(comparable),
                "per_case_aggregation": "median of all required complete repetitions",
                "baseline": distribution(baseline_values), "candidate": distribution(method_values),
                "baseline_over_candidate_ratio": distribution(ratios),
                "resource_distributions_per_case_medians": {
                    name: {field: distribution(values) for field, values in fields.items()}
                    for name, fields in resources.items()},
                "resource_note": "Missing metrics have n=0, not a zero measurement. Preprocessing/online phases have distinct scopes; memory-mode times are diagnostic only."})
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", required=True, type=Path,
                        help="New empty/nonexistent suite directory; never reuse an earlier run")
    args = parser.parse_args(argv)
    root, output = args.root.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    lock_path = Path(__file__).resolve().parent / ".benchmark.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        write_new(output / "blocked.json", {"status": "environment_error", "reason": "benchmark lock exists; verify owner before manual removal"})
        return 4
    os.write(lock_fd, f"{os.getpid()} {output}\n".encode("utf-8"))
    os.close(lock_fd)
    records = []
    spent = {method: 0.0 for method in METHODS}
    started = time.perf_counter()
    jobs = []
    abort_reason = None
    active = None
    source_paths = []
    capture = None
    support_before = None
    ledger = output / "jobs.jsonl"
    try:
        before = runtime_check(root)
        write_new(output / "runtime_before.json", before)
        if not before["all_match"]:
            raise ValueError("C002-R1 runtime differs from frozen sources")
        cases, dataset_path, corpus_manifest = read_cases(root)
        case_map = {item["case_id"]: item for item in cases}
        input_dir = output / "inputs"
        input_dir.mkdir()
        for case in cases:
            (input_dir / f"{case['case_id']}.json").write_bytes(canonical(case["input"]))
        jobs = job_plan(cases)
        write_new(output / "plan.json", {"suite_id": uuid4().hex,
                  "created_utc": datetime.now(timezone.utc).isoformat(),
                  "timing_jobs": 900, "memory_jobs": 300, "jobs": jobs,
                  "post_launch_wait_cap_seconds_per_input": 30.0, "shared_seconds_per_method": 900.0,
                  "capture_backend": CAPTURE_BACKEND,
                  "budget_scope": "sum of capture subprocess_seconds (Popen launch through direct-child reaping), timing+memory combined; capture snapshots and finalization excluded",
                  "order": "timing reps then memory; sorted cases, rotating Latin method order",
                  "correctness_checker": "none; auditor must validate all results independently"})
        spec = importlib.util.spec_from_file_location("c002_capture_for_benchmark", root / "audit/capture.py")
        capture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(capture)
        worker = Path(__file__).resolve().with_name("worker.py")
        source_paths = [root / path for path in EXPECTED] + [
            root / "coordination/runtime_manifest.json", dataset_path, corpus_manifest,
            Path(__file__).resolve(), worker]
        support_before = capture._source_manifest(source_paths)
        write_new(output / "support_sources_before.json", support_before)
        for job in jobs:
            active = job
            method = job["method"]
            remaining = max(0.0, 900.0 - spent[method])
            if remaining <= 0.001:
                record = {**job, "status": "budget_skipped", "remaining_method_seconds": remaining}
            else:
                pre = runtime_check(root)
                if not pre["all_match"]:
                    abort_reason = "runtime_source_drift_before_job"
                    break
                input_path = input_dir / f"{job['case_id']}.json"
                if sha(input_path.read_bytes()) != case_map[job["case_id"]]["input_sha256"]:
                    abort_reason = "input_source_drift_before_job"
                    break
                sidecar = output / f"{job['job_id']}.worker.json"
                hard_limit = min(30.0, remaining)
                command = [sys.executable, "-B", "-X", "utf8", str(worker), str(root),
                           str(input_path), method, job["mode"], str(sidecar), str(hard_limit)]
                interrupt_requested = []
                previous_handler = signal.signal(signal.SIGINT,
                    lambda signum, frame: interrupt_requested.append(signum))
                try:
                    # Defer ordinary Ctrl-C until capture has saved raw artifacts.
                    attempt = capture.capture(job["job_id"], command, cwd=root,
                                              timeout_seconds=hard_limit,
                                              source_paths=[*source_paths, input_path])
                finally:
                    signal.signal(signal.SIGINT, previous_handler)
                process_seconds = attempt.get("subprocess_seconds")
                clock_valid = (isinstance(process_seconds, (int, float))
                               and not isinstance(process_seconds, bool)
                               and math.isfinite(process_seconds) and process_seconds >= 0)
                if clock_valid:
                    spent[method] += process_seconds
                attempt_dir = Path(attempt["attempt_dir"])
                cleanup_failed = (attempt.get("cleanup_error") is not None
                                  or attempt.get("child_reaped") is False)
                raw = b"" if cleanup_failed else (attempt_dir / "stdout.bin").read_bytes()
                result = metadata = None
                errors = []
                if cleanup_failed:
                    errors.append("capture cleanup failed or direct child was not reaped; suite stopped")
                elif not clock_valid:
                    errors.append("capture subprocess_seconds missing or invalid; method budget cannot be charged")
                else:
                    try:
                        result = json.loads(raw.decode("utf-8-sig"))
                    except (ValueError, UnicodeError) as error:
                        errors.append(f"stdout_json: {error}")
                    if sidecar.is_file():
                        try:
                            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
                        except (OSError, ValueError) as error:
                            errors.append(f"sidecar_json: {error}")
                post = runtime_check(root) if not cleanup_failed else {"all_match": False,
                    "note": "not checked because capture reported unreaped child"}
                if cleanup_failed:
                    status = "cleanup_failure"
                elif not clock_valid:
                    status = "instrumentation_error"
                else:
                    status = classify(attempt, result, metadata, job)
                if (not cleanup_failed and
                        (interrupt_requested or attempt.get("execution_status") == "interrupted")):
                    status = "interrupted"
                record = {**job, "status": status, "capture": attempt,
                          "process_elapsed_seconds": process_seconds,
                          "capture_elapsed_including_overhead_seconds": attempt["duration_seconds"],
                          "capture_backend": CAPTURE_BACKEND,
                          "subprocess_clock_source": "capture.subprocess_seconds",
                          "hard_limit_seconds": hard_limit,
                          "cap_reason": "input_limit" if hard_limit == 30.0 else "method_budget_remaining",
                          "remaining_method_seconds_after": max(0.0, 900.0 - spent[method]),
                          "worker": metadata, "parse_errors": errors,
                          "runtime_before": pre, "runtime_after": post,
                          "output_bytes": len(raw) if not cleanup_failed else None,
                          "output_sha256": sha(raw) if not cleanup_failed else None,
                          "independent_correctness_checked": False}
                if isinstance(result, dict):
                    record["solver_status"] = result.get("status")
                    record["solver_metrics"] = result.get("metrics", {})
                    record["solver_search"] = result.get("search", {})
                    record["found_partition_count"] = result.get("found_partition_count")
                    # Full output is preserved verbatim by capture; never replace it.
                if sidecar.is_file() and not cleanup_failed:
                    record["sidecar_snapshot"] = capture._source_manifest([sidecar])
                abort_reason = capture_abort_reason(attempt, clock_valid,
                                                    bool(interrupt_requested))
                if abort_reason is None and not post["all_match"]:
                    abort_reason = "runtime_source_drift_after_job"
                    record["status"] = "invalidated_source_drift"
            append_record(ledger, record)
            records.append(record)
            active = None
            if abort_reason:
                break
    except KeyboardInterrupt:
        abort_reason = "interrupted"
    except BaseException as error:
        abort_reason = f"harness_error: {type(error).__name__}: {error}"
    finally:
        completed_ids = {record["job_id"] for record in records}
        for job in jobs:
            if job["job_id"] not in completed_ids:
                record = {**job, "status": "harness_interrupted" if active and job == active else "not_run_after_abort",
                          "reason": abort_reason or "aborted_before_record"}
                append_record(ledger, record)
                records.append(record)
        write_new(output / "runtime_after.json", runtime_check(root))
        if capture is not None and source_paths and support_before is not None:
            support_after = capture._source_manifest(source_paths)
            write_new(output / "support_sources_after.json", support_after)
            if support_before != support_after:
                abort_reason = abort_reason or "support_or_corpus_source_drift"
        write_new(output / "summary.json", {**summaries(records), "abort_reason": abort_reason,
                  "total_harness_seconds": time.perf_counter() - started,
                  "subprocess_seconds_by_method": spent,
                  "capture_backend": CAPTURE_BACKEND,
                  "warning": "capture raw exit3 program_error is reclassified as incomplete only with valid contract; no speed claim before independent correctness verification"})
        if abort_reason != "capture_cleanup_failure_child_may_still_be_running":
            lock_path.unlink()
    return 0 if abort_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())

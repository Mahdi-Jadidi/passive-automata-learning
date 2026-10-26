"""Independently validate every output captured by one adopted performance suite."""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent
EXPECTED_CORPUS_SHA = "a4ef5c7124b9852cb30c5eb8e86f6e8bd1fa53bf3d4e9ab5d89d70f9b48efd13"
EXPECTED_DATASET_SHA = "509928210c1075d502d7244f0c5a8f5f75d0b65b33298ddbe288995e0ef5ce20"
EXPECTED_RUNTIME_SHA = "b7a5b30974500ea610689a7d6ca627437508d6cf63a59fd5e8b6c5a18206859b"
EXPECTED_JOBS = 1200
METHODS = ("baseline", "eager", "lazy")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_correctness_checker():
    path = AUDIT / "validate_saved_correctness.py"
    spec = importlib.util.spec_from_file_location("partition_independent_f2_checker", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def finite_nonnegative(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def check_source_manifest(before, after):
    errors = []
    if before != after:
        errors.append("benchmark/corpus source manifest changed during suite")
    if not isinstance(before, list) or not before:
        errors.append("support source manifest is empty")
    for item in before if isinstance(before, list) else []:
        snapshot = AUDIT / item["snapshot"]
        if not snapshot.is_file() or sha(snapshot.read_bytes()) != item.get("sha256"):
            errors.append(f"missing or corrupt source snapshot: {item.get('path')}")
    return errors


def validate_output(checker, result, method, data, expected):
    if result.get("method") != method:
        raise RuntimeError("result method label mismatch")
    if result.get("alphabet") != data["alphabet"] or result.get("k") != 2:
        raise RuntimeError("result alphabet or block count mismatch")
    _, actual = checker.partition_set(result, data["alphabet"])
    witnesses = checker.verify_witnesses(result, data)
    if result.get("complete") is True:
        if result.get("status") not in {"unique", "ambiguous", "infeasible"}:
            raise RuntimeError("complete result has invalid status")
        if actual != expected:
            raise RuntimeError("complete F2 mismatch")
        if (result.get("feasible_partition_count") != len(expected)
                or result.get("found_partition_count") != len(expected)):
            raise RuntimeError("complete result count mismatch")
        expected_status = "infeasible" if not expected else "unique" if len(expected) == 1 else "ambiguous"
        if result.get("status") != expected_status:
            raise RuntimeError("complete result status disagrees with exact F2 set")
        return "complete", witnesses
    if result.get("complete") is not False or result.get("status") != "incomplete":
        raise RuntimeError("incomplete result contract flags disagree")
    if result.get("feasible_partition_count") is not None:
        raise RuntimeError("incomplete result claims a total count")
    if result.get("found_partition_count") != len(actual):
        raise RuntimeError("incomplete result found count mismatch")
    if not actual <= expected:
        raise RuntimeError("incomplete result contains an infeasible partition")
    return "incomplete", witnesses


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, type=Path)
    args = parser.parse_args(argv)
    suite = args.suite.resolve()
    checker, checker_path = import_correctness_checker()
    errors = []
    corpus_path = AUDIT / "corpus/frozen_v1/manifest.json"
    corpus_raw = corpus_path.read_bytes()
    if sha(corpus_raw) != EXPECTED_CORPUS_SHA:
        errors.append("frozen corpus manifest anchor mismatch")
    corpus = json.loads(corpus_raw)
    dataset = corpus["datasets"]["performance_100"]
    dataset_path = AUDIT / "corpus/frozen_v1" / dataset["path"]
    dataset_raw = dataset_path.read_bytes()
    if sha(dataset_raw) != EXPECTED_DATASET_SHA or dataset["sha256"] != EXPECTED_DATASET_SHA:
        errors.append("performance_100 dataset anchor mismatch")
    cases = [json.loads(line) for line in dataset_raw.splitlines() if line.strip()]
    case_by_id = {case["case_id"]: case for case in cases}
    if len(cases) != 100 or len(case_by_id) != 100:
        errors.append(f"expected 100 unique frozen performance cases; got {len(case_by_id)}")

    plan_path, ledger_path = suite / "plan.json", suite / "jobs.jsonl"
    plan_raw, ledger_raw = plan_path.read_bytes(), ledger_path.read_bytes()
    plan = json.loads(plan_raw)
    rows = [json.loads(line) for line in ledger_raw.decode("utf-8").splitlines() if line]
    planned = plan.get("jobs", [])
    planned_by_id = {job.get("job_id"): job for job in planned}
    row_by_id = {row.get("job_id"): row for row in rows}
    if len(planned) != EXPECTED_JOBS or len(planned_by_id) != EXPECTED_JOBS:
        errors.append(f"plan must contain {EXPECTED_JOBS} unique jobs")
    if (plan.get("timing_jobs") != 900 or plan.get("memory_jobs") != 300
            or sum(job.get("mode") == "timing" for job in planned) != 900
            or sum(job.get("mode") == "memory" for job in planned) != 300):
        errors.append("plan timing/memory job split differs from the registered protocol")
    if len(rows) != len(row_by_id):
        errors.append("duplicate job IDs in append-only ledger")
    if set(row_by_id) != set(planned_by_id):
        errors.append("ledger job coverage differs from the saved plan")
    for job_id, planned_job in planned_by_id.items():
        row = row_by_id.get(job_id)
        if row is None:
            continue
        for key in ("case_id", "method", "mode", "repetition", "alphabet_size"):
            if row.get(key) != planned_job.get(key):
                errors.append(f"{job_id}: ledger differs from plan for {key}")

    runtime_path = CYCLE / "coordination/runtime_manifest.json"
    runtime_raw = runtime_path.read_bytes()
    if sha(runtime_raw) != EXPECTED_RUNTIME_SHA:
        errors.append("frozen runtime manifest anchor mismatch")
    runtime = json.loads(runtime_raw)
    runtime_hashes = {}
    for item in runtime["files"]:
        path = CYCLE / item["path"]
        actual = sha(path.read_bytes()) if path.is_file() else None
        runtime_hashes[item["path"]] = actual
        if actual != item["sha256"]:
            errors.append(f"runtime source drift: {item['path']}")

    support_before = load_json(suite / "support_sources_before.json")
    support_after = load_json(suite / "support_sources_after.json")
    errors.extend(check_source_manifest(support_before, support_after))
    summary_path = suite / "summary.json"
    summary_raw = summary_path.read_bytes()
    summary = json.loads(summary_raw)
    if summary.get("abort_reason") is not None:
        errors.append(f"suite ended with abort reason: {summary.get('abort_reason')}")

    output_status_counts = collections.Counter()
    validation_counts = collections.Counter()
    method_mode_counts = collections.Counter()
    witness_total = 0
    checked_raw_bytes = 0
    valid_results = []
    failures = []
    result_cache = {}

    for row in rows:
        status = row.get("status")
        method_mode_counts[(row.get("mode"), row.get("method"), status)] += 1
        output_status_counts[status] += 1
        job_id = row.get("job_id", "<missing>")
        case_id = row.get("case_id")
        if row.get("method") not in METHODS or case_id not in case_by_id:
            failures.append({"job_id": job_id, "error": "unknown method or case"})
            continue
        case = case_by_id[case_id]
        data = checker.normalize_input(case["input"])
        input_path = suite / "inputs" / f"{case_id}.json"
        expected_input_bytes = checker.canonical_json(data)
        if not input_path.is_file() or input_path.read_bytes() != expected_input_bytes:
            failures.append({"job_id": job_id, "error": "saved solver input differs from frozen case"})
            continue
        if row.get("status") == "budget_skipped":
            validation_counts["budget_skipped"] += 1
            continue
        capture = row.get("capture")
        if not isinstance(capture, dict) or not capture.get("attempt_dir"):
            if status not in {"not_run_after_abort", "harness_interrupted"}:
                failures.append({"job_id": job_id, "error": "captured job lacks attempt metadata"})
            validation_counts[f"uncaptured/{status}"] += 1
            continue
        attempt_dir = Path(capture["attempt_dir"])
        stdout_path, stderr_path = attempt_dir / "stdout.bin", attempt_dir / "stderr.bin"
        if not stdout_path.is_file() or not stderr_path.is_file():
            failures.append({"job_id": job_id, "error": "durable capture lacks stdout/stderr files"})
            validation_counts["capture_files_missing"] += 1
            continue
        raw = stdout_path.read_bytes()
        checked_raw_bytes += len(raw)
        if (len(raw) != capture.get("stdout_bytes")
                or sha(raw) != capture.get("stdout_sha256")
                or len(raw) != row.get("output_bytes")
                or sha(raw) != row.get("output_sha256")):
            failures.append({"job_id": job_id, "error": "raw stdout bytes/hash disagree with capture and ledger"})
            validation_counts["capture_hash_mismatch"] += 1
            continue
        stderr_raw = stderr_path.read_bytes()
        if (len(stderr_raw) != capture.get("stderr_bytes")
                or sha(stderr_raw) != capture.get("stderr_sha256")):
            failures.append({"job_id": job_id, "error": "raw stderr bytes/hash disagree with capture"})
            validation_counts["stderr_hash_mismatch"] += 1
            continue
        if row.get("capture_backend") != "B-CAPTURE-R1":
            failures.append({"job_id": job_id, "error": "unexpected capture backend"})
        if capture.get("child_reaped") is not True:
            failures.append({"job_id": job_id, "error": "captured direct child was not confirmed reaped"})
        if not row.get("runtime_before", {}).get("all_match"):
            failures.append({"job_id": job_id, "error": "runtime did not match before solver launch"})
        if not row.get("runtime_after", {}).get("all_match"):
            failures.append({"job_id": job_id, "error": "runtime did not match after solver completion"})
        execution_status = capture.get("execution_status")
        if status in {"complete", "incomplete"} and execution_status != "success":
            failures.append({"job_id": job_id, "error": "solver result status disagrees with capture execution status"})
        if status == "timed_out" and execution_status != "timed_out":
            failures.append({"job_id": job_id, "error": "timeout row disagrees with capture execution status"})
        if row.get("process_elapsed_seconds") != capture.get("subprocess_seconds"):
            failures.append({"job_id": job_id, "error": "subprocess clock differs from captured attempt"})
        if not finite_nonnegative(capture.get("subprocess_seconds")):
            failures.append({"job_id": job_id, "error": "invalid subprocess_seconds"})

        expected_case_input_sha = case.get("input_sha256")
        canonical_case_sha = sha(checker.canonical_json(case["input"]))
        if expected_case_input_sha != canonical_case_sha:
            failures.append({"job_id": job_id, "error": "frozen case input hash mismatch"})

        try:
            result = json.loads(raw.decode("utf-8-sig"))
        except (ValueError, UnicodeError):
            result = None
        if result is None:
            validation_counts[f"unparseable/{status}"] += 1
            if status in {"complete", "incomplete"}:
                failures.append({"job_id": job_id, "error": "harness classified an unparseable output"})
            continue
        try:
            expected = checker.exact_f2(data)
            scientific_status, witnesses = validate_output(
                checker, result, row["method"], data, expected)
            if status == "complete" and scientific_status != "complete":
                raise RuntimeError("harness complete status disagrees with solver output")
            if status == "incomplete" and scientific_status != "incomplete":
                raise RuntimeError("harness incomplete status disagrees with solver output")
            worker = row.get("worker")
            if status in {"complete", "incomplete"}:
                if not isinstance(worker, dict):
                    raise RuntimeError("complete/incomplete job lacks worker sidecar")
                sidecar_path = suite / f"{job_id}.worker.json"
                if not sidecar_path.is_file():
                    raise RuntimeError("worker sidecar file missing")
                sidecar_raw = sidecar_path.read_bytes()
                sidecar = json.loads(sidecar_raw)
                if sidecar != worker:
                    raise RuntimeError("embedded worker metadata differs from saved sidecar")
                if sidecar.get("method") != row["method"] or sidecar.get("mode") != row["mode"]:
                    raise RuntimeError("worker sidecar method/mode mismatch")
                if not finite_nonnegative(sidecar.get("pipeline_seconds")):
                    raise RuntimeError("invalid pipeline_seconds")
                if row["mode"] == "memory":
                    peak = sidecar.get("python_traced_peak_bytes")
                    if type(peak) is not int or peak < 0:
                        raise RuntimeError("invalid Python tracemalloc peak")
                snap = row.get("sidecar_snapshot")
                if not isinstance(snap, list) or not any(
                        item.get("sha256") == sha(sidecar_raw) and item.get("path") == str(sidecar_path)
                        for item in snap):
                    raise RuntimeError("worker sidecar snapshot does not anchor saved sidecar")
            result_cache[job_id] = {"status": scientific_status,
                                    "witness_records": witnesses,
                                    "result": result,
                                    "data": data,
                                    "expected": expected}
            witness_total += witnesses
            validation_counts[f"valid_{scientific_status}"] += 1
            valid_results.append({"job_id": job_id, "case_id": case_id,
                                  "method": row["method"], "mode": row["mode"],
                                  "repetition": row["repetition"],
                                  "scientific_status": scientific_status,
                                  "witness_records": witnesses,
                                  "output_bytes": len(raw),
                                  "output_sha256": sha(raw)})
        except Exception as error:
            failures.append({"job_id": job_id,
                             "error": f"{type(error).__name__}: {error}"})
            validation_counts["validation_failure"] += 1

    # Recompute the three-repetition timing comparison coverage from independently
    # validated outputs; incomplete, timed-out, and skipped jobs never count.
    paired_coverage = []
    for candidate in ("eager", "lazy"):
        paired = []
        for case_id in sorted(case_by_id):
            keys = [("timing", case_id, rep) for rep in range(3)]
            triplets = []
            for mode, cid, rep in keys:
                triplet = [next((r for r in rows if r.get("mode") == mode
                                 and r.get("case_id") == cid and r.get("repetition") == rep
                                 and r.get("method") == method), None)
                           for method in ("baseline", candidate)]
                triplets.append(triplet)
            if all(all(r is not None and r.get("status") == "complete"
                       and (r.get("job_id") in result_cache)
                       and result_cache[r["job_id"]]["status"] == "complete"
                       for r in triplet) for triplet in triplets):
                paired.append(case_id)
        paired_coverage.append({"mode": "timing", "candidate": candidate,
                                "case_ids": paired, "case_count": len(paired)})

    # The measured process budgets include capture through reaping and combine
    # timing and memory jobs. Count only actual spawned jobs.
    spent = collections.Counter()
    for row in rows:
        seconds = row.get("process_elapsed_seconds")
        if finite_nonnegative(seconds):
            spent[row.get("method")] += seconds
    budget_overruns = {method: seconds - 900.0 for method, seconds in spent.items()
                       if seconds > 900.0}
    if any(amount > 1.0 for amount in budget_overruns.values()):
        errors.append(f"captured subprocess budget exceeded tolerance: {budget_overruns}")
    for method in METHODS:
        recorded = summary.get("subprocess_seconds_by_method", {}).get(method)
        if not finite_nonnegative(recorded) or abs(recorded - spent[method]) > 1e-6:
            errors.append(f"{method} subprocess budget summary differs from ledger")

    output_dir = AUDIT / "benchmark_validation" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:8])
    output_dir.mkdir(parents=True, exist_ok=False)
    report = {
        "validation_id": output_dir.name,
        "suite_id": plan.get("suite_id"),
        "scientific_status": "accepted" if not failures and not errors else "rejected_or_incomplete",
        "execution_status": "success" if summary.get("abort_reason") is None else "suite_aborted",
        "independent_checker": "direct exhaustive F2 enumeration and witness checks reused from saved-correctness auditor",
        "anchors": {
            "corpus_manifest_sha256": sha(corpus_raw),
            "performance_dataset_sha256": sha(dataset_raw),
            "runtime_manifest_sha256": sha(runtime_raw),
            "runtime_file_sha256": runtime_hashes,
            "correctness_checker_sha256": sha(checker_path.read_bytes()),
            "suite_plan_sha256": sha(plan_raw),
            "suite_ledger_sha256": sha(ledger_raw),
            "suite_summary_sha256": sha(summary_raw),
            "support_sources_before_sha256": sha((suite / "support_sources_before.json").read_bytes()),
            "support_sources_after_sha256": sha((suite / "support_sources_after.json").read_bytes()),
        },
        "coverage": {
            "planned_jobs": len(planned), "ledger_jobs": len(rows),
            "benchmark_status_counts": dict(output_status_counts),
            "validation_status_counts": dict(validation_counts),
            "witness_records_validated": witness_total,
            "raw_stdout_bytes_independently_hashed": checked_raw_bytes,
            "subprocess_seconds_by_method": dict(spent),
            "subprocess_budget_overrun_seconds": budget_overruns,
            "paired_timing_cases_after_output_validation": paired_coverage,
            "valid_scientific_outputs": len(valid_results),
        },
        "suite_summary": summary,
        "source_manifest_errors": check_source_manifest(support_before, support_after),
        "warnings": [
            (f"{method} exceeded the nominal 900s subprocess budget by {seconds:.6f}s; "
             "the capture cleanup/process-launch boundary can slightly overshoot a wait cap. "
             "The exact observed total is preserved and no time is imputed.")
            for method, seconds in budget_overruns.items()
        ],
        "errors": errors,
        "failures": failures,
        "validated_outputs": valid_results,
        "limitations": [
            "Only complete outputs support exact full-set equality; incomplete outputs are checked as nonempty feasible subsets with valid witnesses.",
            "Timeout and budget-skipped timing observations are censored and are not replaced by estimates.",
            "Python tracemalloc peaks exclude native allocations and process bootstrap, as stated by the worker contract.",
            "Performance results are descriptive for the frozen synthetic corpus and are not a general speedup guarantee.",
        ],
    }
    report_path = output_dir / "validation_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), "report_sha256": sha(report_path.read_bytes()),
                      "scientific_status": report["scientific_status"],
                      "execution_status": report["execution_status"],
                      "coverage": report["coverage"], "error_count": len(errors),
                      "failure_count": len(failures)}, ensure_ascii=False, sort_keys=True))
    return 0 if report["scientific_status"] == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())

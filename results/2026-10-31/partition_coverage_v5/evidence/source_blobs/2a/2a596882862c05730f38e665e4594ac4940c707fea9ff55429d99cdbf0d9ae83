"""Complete only the twelve exact jobs that failed before process launch in v1."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V5 = HERE.parent
COORD = V5 / "coordination"
ROOT = HERE / "frozen_corpus_v2"
PROPOSAL = HERE / "PERFORMANCE_PROPOSAL_V1.json"
PROTOCOL = HERE / "performance_execution_protocol_v1.json"
RECOVERY_PROTOCOL = HERE / "performance_recovery_protocol_v2.json"
FREEZE = HERE / "PERFORMANCE_FREEZE_V2.json"
OLD_FREEZE = HERE / "PERFORMANCE_FREEZE_V1.json"
TASK = HERE / "performance_task_v1.py"
OLD_REPORT = HERE / "PERFORMANCE_RUN_REPORT_V1.json"
REPORT = HERE / "PERFORMANCE_RUN_REPORT_V2.json"
ON_GATE = V5 / "evidence" / "attempts" / "20261101T053324.043566Z_c9b3c6ee88"
SCALE_AUDIT = V5 / "evidence" / "attempts" / "20261101T053559.626094Z_696f22aed1"
SCALE_FIXTURE = V5 / "structural" / "sparse_scaling_fixtures_v1.json"
EXACT = V5 / "general" / "known_k_qexact_v2.py"
SPARSE = V5 / "structural" / "sparse_certificate_v2.py"
CAPTURE_PATH = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE_PATH.parent))
import capture  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def result_partitions(result):
    return {canonical_partition(row["blocks"]) for row in result.get("solutions", [])}


def source_paths_for(corpus_row):
    paths = [
        Path(__file__), TASK, PROPOSAL, PROTOCOL, RECOVERY_PROTOCOL, FREEZE,
        OLD_FREEZE, OLD_REPORT, COORD / "PERFORMANCE_GO.json", CAPTURE_PATH,
        EXACT, SPARSE,
        ROOT / "manifest_v1.json", ROOT / "freeze_record_v1.json",
        ROOT / corpus_row["input"], ROOT / corpus_row["hidden"],
        ON_GATE / "stdout.bin", ON_GATE / "manifest.json", ON_GATE / "result.json",
        SCALE_FIXTURE, SCALE_AUDIT / "stdout.bin", SCALE_AUDIT / "manifest.json",
        SCALE_AUDIT / "result.json", HERE / "sparse_scaling_audit_v1.py",
        HERE / "SMALL_GATE_REPORT_V2.json", HERE / "EXACT_TOGGLE_GATE_REPORT_V1.json",
        HERE / "SPARSE_SCALING_AUDIT_REPORT_V1.json", HERE / "ROOT_CLI_AUDIT_REPORT_V1.json",
    ]
    legacy = json.loads(OLD_REPORT.read_text(encoding="utf-8"))
    for job in legacy["jobs"]:
        if job["kind"] == "exact":
            attempt_dir = V5 / job["attempt_dir"]
            paths.extend([attempt_dir / "manifest.json", attempt_dir / "result.json",
                          attempt_dir / "stdout.bin", attempt_dir / "stderr.bin"])
    return paths


def verify_frozen(proposal, protocol, recovery, freeze, old_report):
    if REPORT.exists():
        raise FileExistsError(f"refusing to overwrite recovery report: {REPORT}")
    prefix = "results/2026-10-31/partition_coverage_v5/"
    if sha(PROPOSAL) != freeze["sha256"][prefix + "audit/PERFORMANCE_PROPOSAL_V1.json"]:
        raise AssertionError("approved proposal changed")
    if sha(PROTOCOL) != freeze["sha256"][prefix + "audit/performance_execution_protocol_v1.json"]:
        raise AssertionError("approved execution protocol changed")
    if sha(RECOVERY_PROTOCOL) != freeze["sha256"][prefix + "audit/performance_recovery_protocol_v2.json"]:
        raise AssertionError("recovery protocol changed")
    if sha(COORD / "PERFORMANCE_GO.json") != freeze["sha256"][prefix + "coordination/PERFORMANCE_GO.json"]:
        raise AssertionError("master GO changed")
    for relative, expected in freeze["sha256"].items():
        if sha(REPO / relative) != expected:
            raise AssertionError(f"frozen source/input changed: {relative}")
    go = json.loads((COORD / "PERFORMANCE_GO.json").read_text(encoding="utf-8"))
    if go.get("protocol_sha256") != sha(PROPOSAL):
        raise AssertionError("GO does not approve frozen proposal")
    if protocol["schedule"]["total_jobs"] != 16 or recovery["recovery_scope"]["jobs"] != 12:
        raise AssertionError("frozen schedule cardinality changed")
    if old_report["counts"]["exact_jobs"] != 12:
        raise AssertionError("expected twelve original exact capture attempts")
    exact_failures = [j for j in old_report["jobs"] if j["kind"] == "exact"]
    if (len(exact_failures) != 12 or any(j["execution_status"] != "capture_error"
            or j["exit_code"] is not None or j["stdout_bytes"] != 0 for j in exact_failures)):
        raise AssertionError("original exact attempts were not capture-only failures")
    if any(j["execution_status"] != "success" for j in old_report["jobs"]
           if j["kind"] in ("sparse", "memory")):
        raise AssertionError("a passed sparse or memory job would be rerun")


def capture_exact(corpus_row, q, toggle, rep):
    input_path = ROOT / corpus_row["input"]
    command = [sys.executable, "-B", "-X", "utf8", str(TASK),
               "--mode", "exact", "--input", str(input_path), "--q", str(q),
               "--provider", str(EXACT), "--cooperative-seconds", "28", "--toggle", toggle]
    label = f"performance-exact-recovery-{corpus_row['id']}-{toggle}-rep{rep}"
    record = capture.capture(label, command, cwd=REPO, timeout_seconds=30,
                             source_paths=source_paths_for(corpus_row))
    attempt = Path(record["attempt_dir"])
    raw = (attempt / "stdout.bin").read_bytes()
    try:
        result = json.loads(raw.decode("utf-8")) if raw else None
    except Exception as exc:
        result = {"decode_error": repr(exc)}
    process_launched = record.get("child_pid") is not None
    prelaunch_capture_error = not process_launched
    runtime_censored = process_launched and (
        record["execution_status"] == "timed_out"
        or not isinstance(result, dict) or result.get("status") == "incomplete"
        or not result.get("search_exhausted") or not result.get("decision_complete")
    )
    execution_error = process_launched and (
        record["execution_status"] != "success" or record["exit_code"] != 0
    )
    measurement_eligible = process_launched and not runtime_censored and not execution_error
    return {
        "label": label, "kind": "exact", "case_id": corpus_row["id"], "q": q,
        "toggle": toggle, "rep": rep,
        "attempt_id": record["attempt_id"],
        "attempt_dir": str(attempt.relative_to(V5)),
        "execution_status": record["execution_status"], "exit_code": record["exit_code"],
        "child_pid": record.get("child_pid"), "process_launched": process_launched,
        "prelaunch_capture_error": prelaunch_capture_error,
        "runtime_censored": runtime_censored,
        "execution_error": execution_error,
        "measurement_eligible": measurement_eligible,
        "subprocess_seconds": record["subprocess_seconds"],
        "stdout_bytes": record["stdout_bytes"], "stdout_sha256": record["stdout_sha256"],
        "stderr_bytes": record["stderr_bytes"], "stderr_sha256": record["stderr_sha256"],
        "status": result.get("status") if isinstance(result, dict) else None,
        "search_exhausted": result.get("search_exhausted") if isinstance(result, dict) else None,
        "decision_complete": result.get("decision_complete") if isinstance(result, dict) else None,
        "solution_count": len(result.get("solutions", [])) if isinstance(result, dict) else None,
        "nodes": result.get("metrics", {}).get("nodes") if isinstance(result, dict) else None,
        "q_opposition_pruned_nodes": result.get("metrics", {}).get("cannot_link_pruned_nodes")
                                     if isinstance(result, dict) else None,
        "provider_seconds": result.get("metrics", {}).get("provider_seconds")
                            if isinstance(result, dict) else None,
        "censored": runtime_censored,
        "payload": result,
    }


def median_field(rows, name):
    values = [row[name] for row in rows if row["measurement_eligible"] and row.get(name) is not None]
    return statistics.median(values) if values else None


def main():
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY_PROTOCOL.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    old_report = json.loads(OLD_REPORT.read_text(encoding="utf-8"))
    verify_frozen(proposal, protocol, recovery, freeze, old_report)

    corpus = json.loads((ROOT / "manifest_v1.json").read_text(encoding="utf-8"))
    on_gate = json.loads((ON_GATE / "stdout.bin").read_text(encoding="utf-8"))
    reference_rows = {(row["id"], row["q"]): row["result"] for row in on_gate["exact_full_set_rows"]}
    jobs = []
    for case_id in protocol["schedule"]["exact"]["input_ids"]:
        row = next(item for item in corpus["small"]["cases"] if item["id"] == case_id)
        for rep, order in enumerate((("on", "off"), ("off", "on"), ("on", "off")), start=1):
            for toggle in order:
                job = capture_exact(row, 1, toggle, rep)
                expected = result_partitions(reference_rows[(case_id, 1)])
                actual = result_partitions(job["payload"]) if isinstance(job["payload"], dict) else set()
                job["reference_set_match"] = None if not job["measurement_eligible"] else actual == expected
                jobs.append(job)

    errors = []
    for job in jobs:
        if job["reference_set_match"] is False:
            errors.append({"label": job["label"], "error": "partition_set_differs_from_frozen_gate"})
    for case_id in protocol["schedule"]["exact"]["input_ids"]:
        for rep in range(1, 4):
            pair = [job for job in jobs if job["case_id"] == case_id and job["rep"] == rep]
            if len(pair) == 2 and all(job["measurement_eligible"] for job in pair):
                if result_partitions(pair[0]["payload"]) != result_partitions(pair[1]["payload"]):
                    errors.append({"case_id": case_id, "rep": rep, "error": "on_off_full_set_mismatch"})
    exact_summary = []
    for case_id in protocol["schedule"]["exact"]["input_ids"]:
        conditions = []
        for toggle in ("on", "off"):
            group = [j for j in jobs if j["case_id"] == case_id and j["toggle"] == toggle]
            conditions.append({
                "toggle": toggle, "jobs": len(group),
                "censored": sum(j["censored"] for j in group),
                "median_subprocess_seconds": median_field(group, "subprocess_seconds"),
                "median_provider_seconds": median_field(group, "provider_seconds"),
                "median_nodes": median_field(group, "nodes"),
                "median_q_opposition_pruned_nodes": median_field(group, "q_opposition_pruned_nodes"),
                "statuses": [j["status"] for j in group],
            })
        exact_summary.append({"case_id": case_id, "q": 1, "conditions": conditions})

    old_exact_failures = []
    for job in old_report["jobs"]:
        if job["kind"] == "exact":
            copied = {key: value for key, value in job.items() if key not in ("payload", "censored")}
            copied["prelaunch_capture_error"] = True
            copied["process_launched"] = False
            copied["runtime_censored"] = False
            copied["v1_censored_field_was_misclassified"] = True
            old_exact_failures.append(copied)
    old_completed = [job for job in old_report["jobs"] if job["kind"] in ("sparse", "memory")]
    sparse_summary = old_report["summary"]["sparse"]
    memory_summary = old_report["summary"]["memory"]
    compact_exact = [{key: value for key, value in job.items() if key != "payload"} for job in jobs]
    actual_processes = sum(job["process_launched"] for job in jobs) + len(old_completed)
    runtime_censored = sum(j["runtime_censored"] for j in jobs) + sum(j["censored"] for j in old_completed)
    recovery_capture_errors = sum(j["prelaunch_capture_error"] for j in jobs)
    recovery_execution_errors = sum(j["execution_error"] for j in jobs)
    report = {
        "schema": "C005-performance-run-report-v2",
        "scientific_status": ("completed" if actual_processes == 16 and not runtime_censored
                              and not recovery_capture_errors and not recovery_execution_errors and not errors
                              else "incomplete_or_censored"),
        "proposal_sha256": sha(PROPOSAL),
        "approved_execution_protocol_sha256": sha(PROTOCOL),
        "recovery_protocol_sha256": sha(RECOVERY_PROTOCOL),
        "freeze_manifest_sha256": sha(FREEZE),
        "master_go_sha256": sha(COORD / "PERFORMANCE_GO.json"),
        "driver_sha256": {"task": sha(TASK), "recovery_launcher": sha(Path(__file__))},
        "provider_sha256": {"exact": sha(EXACT), "sparse": sha(SPARSE)},
        "counts": {
            "capture_attempts_total": 28,
            "original_capture_only_errors": len(old_exact_failures),
            "actual_provider_processes": actual_processes,
            "exact_provider_processes": sum(j["process_launched"] for j in jobs),
            "sparse_provider_processes": sum(j["kind"] == "sparse" for j in old_completed),
            "memory_provider_processes": sum(j["kind"] == "memory" for j in old_completed),
            "runtime_censored_jobs": runtime_censored,
            "recovery_prelaunch_capture_errors": recovery_capture_errors,
            "recovery_execution_errors": recovery_execution_errors,
            "initial_prelaunch_capture_errors": len(old_exact_failures),
            "validation_errors": len(errors),
        },
        "exact_summary": exact_summary,
        "sparse_summary_from_completed_v1_jobs": sparse_summary,
        "memory_summary_from_completed_v1_job": memory_summary,
        "recovery_exact_jobs": compact_exact,
        "completed_sparse_and_memory_jobs": old_completed,
        "initial_exact_capture_errors": old_exact_failures,
        "errors": errors,
        "outputs": "Full exact, sparse, and memory JSON outputs remain in their per-job captured stdout.bin files referenced by attempt_dir and stdout_sha256.",
        "interpretation_limit": protocol["interpretation_limit"],
        "report_v1_classification_correction": "The v1 summary called all twelve capture_error attempts censored jobs. Those attempts had no child process, no exit code, and empty stdout; v2 reports them separately as prelaunch capture errors, not runtime-censored provider jobs.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"report": str(REPORT), "capture_attempts": 28,
                      "actual_provider_processes": actual_processes,
                      "exact_runtime_censored": sum(j["runtime_censored"] for j in jobs),
                      "recovery_prelaunch_capture_errors": recovery_capture_errors,
                      "recovery_execution_errors": recovery_execution_errors,
                      "sparse_censored": sparse_summary["censored"],
                      "memory_bytes": memory_summary["tracemalloc_peak_bytes"],
                      "errors": len(errors), "exact_summary": exact_summary},
                     ensure_ascii=False, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""Run the master-approved 16-job schedule serially through evidence/capture.py."""
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
FREEZE = HERE / "PERFORMANCE_FREEZE_V1.json"
TASK = HERE / "performance_task_v1.py"
REPORT = HERE / "PERFORMANCE_RUN_REPORT_V1.json"
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
    return {canonical_partition(solution["blocks"])
            for solution in result.get("solutions", [])}


def parse_attempt(record):
    attempt = Path(record["attempt_dir"])
    raw = (attempt / "stdout.bin").read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else None
    except Exception as exc:
        payload = {"decode_error": repr(exc)}
    return attempt, raw, payload


def source_paths_for(case):
    paths = [
        Path(__file__), TASK, PROPOSAL, PROTOCOL, FREEZE,
        COORD / "PERFORMANCE_GO.json", CAPTURE_PATH,
        EXACT, SPARSE,
        ROOT / "manifest_v1.json", ROOT / "freeze_record_v1.json",
        ON_GATE / "stdout.bin", ON_GATE / "manifest.json", ON_GATE / "result.json",
        SCALE_FIXTURE,
        SCALE_AUDIT / "stdout.bin", SCALE_AUDIT / "manifest.json", SCALE_AUDIT / "result.json",
        HERE / "sparse_scaling_audit_v1.py",
    ]
    if case["kind"] == "exact":
        paths.append(REPO / "results" / "2026-10-31" / "partition_coverage_v5" /
                     case["input"])
        paths.append(REPO / "results" / "2026-10-31" / "partition_coverage_v5" /
                     case["hidden_sidecar"])
    return paths


def verify_frozen_inputs(proposal, protocol, freeze):
    if REPORT.exists():
        raise FileExistsError(f"refusing to overwrite performance report: {REPORT}")
    prefix = "results/2026-10-31/partition_coverage_v5/"
    expected_go = freeze["sha256"][prefix + "coordination/PERFORMANCE_GO.json"]
    if sha(COORD / "PERFORMANCE_GO.json") != expected_go:
        raise AssertionError("master GO changed after freeze")
    if sha(PROPOSAL) != freeze["sha256"][prefix + "audit/PERFORMANCE_PROPOSAL_V1.json"]:
        raise AssertionError("approved timing proposal hash mismatch")
    if sha(PROTOCOL) != freeze["sha256"][prefix + "audit/performance_execution_protocol_v1.json"]:
        raise AssertionError("execution protocol changed after freeze")
    for relative, expected in freeze["sha256"].items():
        absolute = REPO / relative
        if sha(absolute) != expected:
            raise AssertionError(f"frozen source or input changed: {relative}")
    if proposal["status"] != "proposal_only_pending_master_GO":
        raise AssertionError("unexpected proposal state")
    if protocol["schedule"]["total_jobs"] != 16:
        raise AssertionError("approved schedule job count changed")
    go = json.loads((COORD / "PERFORMANCE_GO.json").read_text(encoding="utf-8"))
    if go.get("protocol_sha256") != sha(PROPOSAL):
        raise AssertionError("master GO does not approve this exact proposal")
    if protocol["correctness_prerequisites"]["errors"] != 0:
        raise AssertionError("correctness prerequisites have discrepancies")


def run_one(label, mode, input_path, q, *, toggle="on", case_id=None, provider=None, kind=None):
    command = [sys.executable, "-B", "-X", "utf8", str(TASK),
               "--mode", mode, "--input", str(input_path), "--q", str(q),
               "--provider", str(provider), "--cooperative-seconds", "28"]
    if case_id is not None:
        command.extend(["--case-id", case_id])
    if mode == "exact":
        command.extend(["--toggle", toggle])
    source_case = {"kind": kind or mode}
    if kind == "exact":
        case_id0 = case_id or ""
        rows = json.loads((ROOT / "manifest_v1.json").read_text(encoding="utf-8"))["small"]["cases"]
        corpus_row = next(row for row in rows if row["id"] == case_id0)
        source_case["input"] = corpus_row["input"]
        source_case["hidden_sidecar"] = corpus_row["hidden"]
    record = capture.capture(label, command, cwd=REPO, timeout_seconds=30,
                             source_paths=source_paths_for(source_case))
    attempt, raw, payload = parse_attempt(record)
    if mode == "memory" and isinstance(payload, dict):
        result = payload.get("result")
    else:
        result = payload
    metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
    return {
        "label": label,
        "kind": kind or mode,
        "case_id": case_id,
        "q": q,
        "toggle": toggle if mode == "exact" else None,
        "attempt_id": record["attempt_id"],
        "attempt_dir": str(attempt.relative_to(V5)),
        "execution_status": record["execution_status"],
        "exit_code": record["exit_code"],
        "subprocess_seconds": record["subprocess_seconds"],
        "stdout_bytes": record["stdout_bytes"],
        "stdout_sha256": record["stdout_sha256"],
        "stderr_bytes": record["stderr_bytes"],
        "stderr_sha256": record["stderr_sha256"],
        "status": result.get("status") if isinstance(result, dict) else None,
        "search_exhausted": result.get("search_exhausted") if isinstance(result, dict) else None,
        "decision_complete": result.get("decision_complete") if isinstance(result, dict) else None,
        "complete": result.get("complete") if isinstance(result, dict) else None,
        "uniqueness": result.get("uniqueness") if isinstance(result, dict) else None,
        "solution_count": len(result.get("solutions", [])) if isinstance(result, dict) else None,
        "nodes": metrics.get("nodes"),
        "q_opposition_pruned_nodes": metrics.get("cannot_link_pruned_nodes"),
        "provider_seconds": metrics.get("provider_seconds"),
        "tracemalloc_peak_bytes": (payload.get("memory", {}).get("traced_peak_bytes")
                                   if isinstance(payload, dict) and mode == "memory" else None),
        "payload": payload,
        "raw_stdout": raw,
    }


def summarize(jobs):
    exact_summary = []
    for case_id in ("small_m7_k3_planted_unequal_blocks_01",
                    "small_m7_k3_q_opposition_stress_07"):
        toggles = []
        for toggle in ("on", "off"):
            group = [job for job in jobs if job["kind"] == "exact" and
                     job["case_id"] == case_id and job["toggle"] == toggle]
            valid = [job for job in group if not job["censored"]]
            toggles.append({
                "toggle": toggle, "jobs": len(group), "censored": len(group) - len(valid),
                "median_subprocess_seconds": (statistics.median(j["subprocess_seconds"] for j in valid)
                                               if valid else None),
                "median_provider_seconds": (statistics.median(j["provider_seconds"] for j in valid
                                                               if j["provider_seconds"] is not None)
                                             if any(j["provider_seconds"] is not None for j in valid) else None),
                "median_nodes": (statistics.median(j["nodes"] for j in valid if j["nodes"] is not None)
                                 if any(j["nodes"] is not None for j in valid) else None),
                "median_q_opposition_pruned_nodes": (
                    statistics.median(j["q_opposition_pruned_nodes"] for j in valid
                                      if j["q_opposition_pruned_nodes"] is not None)
                    if any(j["q_opposition_pruned_nodes"] is not None for j in valid) else None),
                "statuses": [j["status"] for j in group],
            })
        exact_summary.append({"case_id": case_id, "q": 1, "conditions": toggles})
    sparse_jobs = [job for job in jobs if job["kind"] == "sparse" and not job["censored"]]
    memory_jobs = [job for job in jobs if job["kind"] == "memory"]
    return {
        "exact": exact_summary,
        "sparse": {
            "case_id": "sparse_m16_k6_r512_q4", "jobs": 3,
            "censored": 3 - len(sparse_jobs),
            "median_subprocess_seconds": (statistics.median(j["subprocess_seconds"] for j in sparse_jobs)
                                           if sparse_jobs else None),
            "median_provider_seconds": (statistics.median(j["provider_seconds"] for j in sparse_jobs
                                                           if j["provider_seconds"] is not None)
                                         if any(j["provider_seconds"] is not None for j in sparse_jobs) else None),
            "statuses": [j["status"] for j in jobs if j["kind"] == "sparse"],
        },
        "memory": {
            "jobs": len(memory_jobs),
            "status": memory_jobs[0]["status"] if memory_jobs else None,
            "tracemalloc_peak_bytes": memory_jobs[0]["tracemalloc_peak_bytes"] if memory_jobs else None,
        },
    }


def main():
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    verify_frozen_inputs(proposal, protocol, freeze)
    manifest = json.loads((ROOT / "manifest_v1.json").read_text(encoding="utf-8"))
    scale_fixture = json.loads(SCALE_FIXTURE.read_text(encoding="utf-8"))
    exact_cases = protocol["schedule"]["exact"]["input_ids"]
    jobs = []
    reference = json.loads((ON_GATE / "stdout.bin").read_text(encoding="utf-8"))
    reference_rows = {(row["id"], row["q"]): row for row in reference["exact_full_set_rows"]}
    for case_id in exact_cases:
        corpus_row = next(row for row in manifest["small"]["cases"] if row["id"] == case_id)
        input_path = ROOT / corpus_row["input"]
        for rep, order in enumerate((("on", "off"), ("off", "on"), ("on", "off")), start=1):
            for toggle in order:
                job = run_one(
                    f"performance-exact-{case_id}-{toggle}-rep{rep}", "exact", input_path, 1,
                    toggle=toggle, provider=EXACT, kind="exact", case_id=case_id,
                )
                result = job["payload"] if isinstance(job["payload"], dict) else {}
                job["censored"] = (
                    job["execution_status"] != "success" or job["exit_code"] != 0
                    or result.get("status") == "incomplete"
                    or not result.get("search_exhausted")
                    or not result.get("decision_complete")
                )
                job["reference_set_match"] = None
                if not job["censored"]:
                    ref = reference_rows[(case_id, 1)]["result"]
                    job["reference_set_match"] = result_partitions(result) == result_partitions(ref)
                jobs.append(job)
    cell = next(case for case in scale_fixture["cases"]
                if case["id"] == protocol["schedule"]["sparse"]["case_id"])
    for rep in range(1, 4):
        job = run_one(
            f"performance-sparse-{cell['id']}-rep{rep}", "sparse", SCALE_FIXTURE, 4,
            case_id=cell["id"], provider=SPARSE, kind="sparse",
        )
        result = job["payload"] if isinstance(job["payload"], dict) else {}
        job["censored"] = (
            job["execution_status"] != "success" or job["exit_code"] != 0
            or result.get("status") == "incomplete"
        )
        job["reference_set_match"] = (
            not job["censored"] and result_partitions(result) ==
            {canonical_partition(cell["expected_blocks"])}
        )
        jobs.append(job)
    memory = run_one(
        f"performance-memory-{cell['id']}", "memory", SCALE_FIXTURE, 4,
        case_id=cell["id"], provider=SPARSE, kind="memory",
    )
    memory_result = memory["payload"].get("result", {}) if isinstance(memory["payload"], dict) else {}
    memory["status"] = memory_result.get("status")
    memory["censored"] = (
        memory["execution_status"] != "success" or memory["exit_code"] != 0
        or memory_result.get("status") == "incomplete"
    )
    memory["reference_set_match"] = (
        not memory["censored"] and result_partitions(memory_result) ==
        {canonical_partition(cell["expected_blocks"])}
    )
    jobs.append(memory)

    errors = []
    for job in jobs:
        if job.get("reference_set_match") is False:
            errors.append({"label": job["label"], "error": "output_partition_differs_from_frozen_correctness_result"})
    for case_id in exact_cases:
        for rep in range(1, 4):
            pair = [job for job in jobs if job["kind"] == "exact" and
                    job["case_id"] == case_id and f"rep{rep}" in job["label"]]
            if len(pair) == 2 and not any(job["censored"] for job in pair):
                if result_partitions(pair[0]["payload"]) != result_partitions(pair[1]["payload"]):
                    errors.append({"case_id": case_id, "rep": rep, "error": "on_off_full_set_mismatch"})
    if len(jobs) != 16:
        errors.append({"error": "job_count_mismatch", "actual": len(jobs)})

    compact_jobs = [{key: value for key, value in job.items() if key not in ("payload", "raw_stdout")}
                    for job in jobs]
    report = {
        "schema": "C005-performance-run-report-v1",
        "scientific_status": "completed_with_censoring" if any(j["censored"] for j in jobs) else "completed",
        "proposal_sha256": sha(PROPOSAL),
        "execution_protocol_sha256": sha(PROTOCOL),
        "freeze_manifest_sha256": sha(FREEZE),
        "master_go_sha256": sha(COORD / "PERFORMANCE_GO.json"),
        "driver_sha256": {"task": sha(TASK), "launcher": sha(Path(__file__))},
        "provider_sha256": {"exact": sha(EXACT), "sparse": sha(SPARSE)},
        "counts": {"jobs": len(jobs), "exact_jobs": sum(j["kind"] == "exact" for j in jobs),
                   "sparse_jobs": sum(j["kind"] == "sparse" for j in jobs),
                   "memory_jobs": sum(j["kind"] == "memory" for j in jobs),
                   "censored_jobs": sum(j["censored"] for j in jobs), "errors": len(errors)},
        "summary": summarize(jobs),
        "errors": errors,
        "jobs": compact_jobs,
        "full_json_outputs": "Each job's unmodified full provider JSON is in its captured stdout.bin, linked by attempt_dir and stdout_sha256.",
        "interpretation_limit": protocol["interpretation_limit"],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"report": str(REPORT), "jobs": len(jobs),
                      "censored": report["counts"]["censored_jobs"],
                      "errors": len(errors), "summary": report["summary"]},
                     ensure_ascii=False, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

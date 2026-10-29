"""Freeze the authorized Stage2 full-API timing protocol and input/source hashes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    runtime_path = PROJECT / "coordination" / "runtime_stage2_r2.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8-sig"))
    gate_path = HERE / "stage2_gate_report_v1.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8-sig"))
    if gate.get("acceptance") != "accepted":
        raise SystemExit("Stage2 correctness gate is not accepted")

    manifest_path = HERE / "corpora" / "stage2_v1" / "manifest.json"
    freeze_path = HERE / "corpora" / "stage2_v1" / "freeze_v1.json"
    corpus = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    corpus_rows = {row["id"]: row for row in corpus["cases"]}
    chosen = {
        "m16_k4": "q2_positive_only_m16_k4",
        "m128_k8": "q2_positive_only_m128_k8",
    }
    cases = {}
    for cell, case_id in chosen.items():
        row = corpus_rows[case_id]
        input_path = HERE / "corpora" / "stage2_v1" / row["input"]
        if sha(input_path) != row["input_sha256"]:
            raise SystemExit(f"public input hash mismatch before freeze: {case_id}")
        if row["negative_count"] != 0 or row["positive_count"] != 4:
            raise SystemExit(f"unexpected q2 constructive input shape: {case_id}")
        cases[cell] = {
            "case_id": case_id,
            "input_path": str(Path("corpora") / "stage2_v1" / row["input"]),
            "input_sha256": row["input_sha256"],
            "input_bytes": input_path.stat().st_size,
            "alphabet_size": row["alphabet_size"],
            "k": row["k_input"],
            "positive_count": row["positive_count"],
            "negative_count": row["negative_count"],
            "positive_lengths": row["positive_lengths"],
            "negative_lengths": row["negative_lengths"],
        }

    wall_schedule = []
    def add(case: str, rep: int, method: str):
        index = len(wall_schedule) + 1
        wall_schedule.append({
            "job_id": f"wall_{index:02d}_{case}_{method}_r{rep}",
            "order": index, "phase": "wall", "case": case, "rep": rep,
            "method": method, "memory": False,
        })
    # Alternating order. Each method is first three times overall, with
    # alternating starts within both input cells.
    add("m16_k4", 1, "general_v3_q2")
    add("m16_k4", 1, "qop001_q2")
    add("m128_k8", 1, "qop001_q2")
    add("m128_k8", 1, "general_v3_q2")
    add("m128_k8", 2, "general_v3_q2")
    add("m128_k8", 2, "qop001_q2")
    add("m16_k4", 2, "qop001_q2")
    add("m16_k4", 2, "general_v3_q2")
    add("m16_k4", 3, "general_v3_q2")
    add("m16_k4", 3, "qop001_q2")
    add("m128_k8", 3, "qop001_q2")
    add("m128_k8", 3, "general_v3_q2")

    memory_schedule = []
    for index, (case, method) in enumerate([
        ("m16_k4", "general_v3_q2"),
        ("m16_k4", "qop001_q2"),
        ("m128_k8", "qop001_q2"),
    ], start=1):
        memory_schedule.append({
            "job_id": f"memory_{index:02d}_{case}_{method}",
            "order": len(wall_schedule) + index, "phase": "memory", "case": case,
            "rep": 1, "method": method, "memory": True,
        })

    audit_relative = [
        "audit/capture.py", "audit/stage2_timing_wrapper_failure_v1.json",
        "audit/stage2_timing_execution_ledger_pre_executor_fix_001.json",
        "audit/timed_stage2_full_api_v1.py",
        "audit/execute_stage2_timing_v1.py", "audit/freeze_stage2_timing_protocol_v1.py",
        "audit/stage2_gate_report_v1.json", "audit/stage1_performance_report_v2.json",
        "audit/STAGE1_SCOPE_ERRATUM_01.md", "audit/corpora/stage2_v1/manifest.json",
        "audit/corpora/stage2_v1/freeze_v1.json",
    ]
    source_paths = list(audit_relative)
    source_paths.append("coordination/runtime_stage2_r2.json")
    source_paths.extend(record["path"] for record in runtime["files"])
    source_bindings = {rel: sha(PROJECT / rel) for rel in sorted(set(source_paths))}
    if source_bindings["coordination/runtime_stage2_r2.json"] != sha(runtime_path):
        raise SystemExit("runtime source binding mismatch")

    schedule = wall_schedule + memory_schedule
    schedule_json = json.dumps(schedule, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
    protocol = {
        "schema": "C004-stage2-matched-full-api-timing-protocol-v1",
        "status": "frozen",
        "authorization": "master_serial_timing_go",
        "authorization_scope": "12 wall jobs + 3 separate tracemalloc jobs only",
        "pre_run_orchestration_event": {"path": "audit/stage2_timing_wrapper_failure_v1.json",
                                         "status": "provider_child_not_started; protocol refrozen after correction"},
        "runtime_manifest_sha256": sha(runtime_path),
        "stage2_gate_report_sha256": sha(gate_path),
        "stage2_corpus_manifest_sha256": sha(manifest_path),
        "stage2_corpus_freeze_sha256": sha(freeze_path),
        "protocol_generator_sha256": sha(Path(__file__)),
        "timing_driver_sha256": sha(HERE / "timed_stage2_full_api_v1.py"),
        "execution_wrapper_sha256": sha(HERE / "execute_stage2_timing_v1.py"),
        "capture_utility_sha256": sha(HERE / "capture.py"),
        "source_bindings": source_bindings,
        "cases": cases,
        "methods": {
            "general_v3_q2": {"provider": "general/known_k_v3.py", "local_word_cap": 2,
                               "k_source": "public input", "max_solutions": 2},
            "qop001_q2": {"provider": "structural/bounded_certificate_v1.py",
                           "support_dependency": "structural/singleton_solver_v1.py",
                           "local_word_cap": 2, "k_source": "public input", "max_solutions": 2},
        },
        "measured_scope": {
            "wall_metric": "capture subprocess_seconds",
            "wall_includes": ["child process startup", "protocol/input reads", "provider import",
                              "solve", "full API result JSON serialization", "stdout write and process exit"],
            "capture_source_snapshot_overhead_in_wall": False,
            "capture_timeout_seconds_hard": 30.0,
            "provider_deadline_seconds_soft": 29.0,
            "provider_deadline_origin": "timing driver entry after interpreter startup; before protocol/input reads and dynamic provider import",
            "serialized_output": "entire provider result object inside a small metadata envelope; no summary projection",
            "fresh_process_per_job": True,
            "execution_order": "strictly serial through audit/capture.py",
        },
        "memory_scope": {
            "jobs": "three listed memory jobs only; separate from all wall timings",
            "metric": "tracemalloc peak traced Python allocations in child",
            "tracing_begins": "timing driver main before protocol/input read and dynamic provider import",
            "peak_sampled_after": "full API result envelope has been JSON serialized",
            "is_rss": False,
        },
        "post_capture_validation": {
            "runs_after_raw_stdout_stderr_are_saved": True,
            "hidden_truth_sidecars_passed_to_timed_child": False,
            "independent_checks": ["full result JSON parse", "status/censor accounting",
                                   "target partition equality", "positive projection coverage",
                                   "q=2 local projection cap", "qop certificate edge evidence",
                                   "qop target/uniqueness certificate", "output size and metrics extraction"],
        },
        "censor_policy": {
            "capture_timeout_or_nonzero_exit": "preserve raw output and mark censored/error; do not discard or retry",
            "provider_status_incomplete_with_valid_first_answer": "retain answer and output; uniqueness/proof search is censored",
            "no_repeat_jobs": True,
        },
        "wall_schedule": wall_schedule,
        "memory_schedule": memory_schedule,
        "schedule_sha256": hashlib.sha256(schedule_json).hexdigest(),
        "provider_budget": {
            "per_provider_measured_limit_seconds": 900.0,
            "prior_stage1_general_v3_wall_seconds": 11.922917199786752,
            "stage1_memory_is_separate_and_not_added_to_wall_budget": True,
        },
    }
    protocol_path = HERE / "stage2_timing_protocol_v1.json"
    protocol_bytes = (json.dumps(protocol, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    protocol_path.write_bytes(protocol_bytes)
    freeze_record = {
        "schema": "C004-stage2-timing-protocol-freeze-v1",
        "protocol_path": str(protocol_path),
        "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "schedule_sha256": protocol["schedule_sha256"],
        "generator_sha256": sha(Path(__file__)),
        "wall_jobs": len(wall_schedule), "memory_jobs": len(memory_schedule),
        "source_bindings": source_bindings,
        "input_bindings": {case: {"path": record["input_path"], "sha256": record["input_sha256"]}
                           for case, record in cases.items()},
        "frozen_before_execution": True,
    }
    freeze_path = HERE / "stage2_timing_protocol_freeze_v1.json"
    freeze_path.write_text(json.dumps(freeze_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"protocol_sha256": freeze_record["protocol_sha256"],
                      "schedule_sha256": freeze_record["schedule_sha256"],
                      "wall_jobs": len(wall_schedule), "memory_jobs": len(memory_schedule),
                      "source_count": len(source_bindings),
                      "inputs": {case: info["sha256"] for case, info in freeze_record["input_bindings"].items()}},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()

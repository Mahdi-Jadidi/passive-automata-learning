"""Preflight the exact GO, source hashes, corpus and post-run auditor."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
BENCH = AUDIT / "benchmark_v1"
WORKSPACE = ROOT.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    freeze_path = BENCH / "BATCH_FREEZE_V1.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    batch_path = BENCH / "batch_v1.json"
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    go_path = ROOT / "coordination" / "PERFORMANCE_GO.json"
    go = json.loads(go_path.read_text(encoding="utf-8"))
    manifest_path = BENCH / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = []

    def check(name, okay, detail=None):
        checks.append({"name": name, "passed": bool(okay), "detail": detail})
        if not okay:
            raise AssertionError(f"{name}: {detail}")

    check("master_go_sha256", sha(go_path) == freeze["master_go_sha256"], sha(go_path))
    check("master_go_authorizes_exactly_six", go.get("decision") == "GO"
          and go.get("primary_provider_jobs") == 6 and go.get("repetitions") == 3)
    check("proposal_sha256", sha(ROOT / "audit" / "BENCHMARK_PROPOSAL_V2.md") == freeze["proposal_sha256"])
    check("protocol_sha256", sha(AUDIT / "PROTOCOL_BENCHMARK_V2.md") == freeze["protocol_sha256"])
    check("batch_sha256", sha(batch_path) == freeze["batch_sha256"])
    check("manifest_sha256", sha(manifest_path) == freeze["corpus_manifest_sha256"])
    check("manifest_provider_anchor", manifest.get("provider_sha256") == freeze["provider_sha256"])
    check("optional_cell_excluded", freeze["excluded_optional_input"] == "optional_decomposable_m64"
          and not any("optional" in job["label"] for job in batch["order"]))
    check("exact_job_count", len(batch["order"]) == freeze["authorized_jobs"] == 6)
    check("serial_order_matches", [j["label"] for j in batch["order"]] == freeze["jobs"])
    check("timing_policy_matches", batch["capture_policy"] == {
        "cooperative_seconds": 28, "hard_timeout_seconds": 30,
        "fresh_serial_process": True, "full_json_and_raw_streams": True})

    source_map = {
        ROOT / "implementation" / "solver_v5.py": freeze["provider_sha256"],
        ROOT / "implementation" / "cli_v4.py": freeze["cli_sha256"],
        ROOT / "solver.py": freeze["root_wrapper_sha256"],
        WORKSPACE / "results" / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py": freeze["parent_helper_sha256"],
        AUDIT / "gate_solver_v5_v6.py": freeze["independent_certificate_auditor_sha256"],
        BENCH / "validate_and_summarize_runs_v1.py": freeze["post_run_validator_sha256"],
        AUDIT / "PROTOCOL_BENCHMARK_V2.md": freeze["protocol_sha256"],
        ROOT / "coordination" / "PERFORMANCE_GO.json": freeze["master_go_sha256"],
    }
    for path, wanted in source_map.items():
        check("source_anchor:" + str(path.relative_to(WORKSPACE)), sha(path) == wanted, sha(path))

    visible = [json.loads(line) for line in (BENCH / "inputs.jsonl").read_text(encoding="utf-8").splitlines() if line]
    check("frozen_input_sidecar_hash", sha(BENCH / "inputs.jsonl") == manifest["inputs_sha256"])
    check("truth_sidecar_hash", sha(BENCH / "truth_sidecars.jsonl") == manifest["truth_sidecars_sha256"])
    check("expected_obstruction_hash", sha(BENCH / "expected_obstructions.jsonl") == manifest["expected_obstructions_sha256"])
    for job in batch["order"]:
        input_path = BENCH / "inputs" / job["input"]
        data = json.loads(input_path.read_text(encoding="utf-8"))
        check("input_hash:" + job["input"], sha(input_path) == job["input_sha256"])
        check("no_hidden_k_q:" + job["input"], set(data) == {"alphabet", "positive", "negative"})
    check("two_primary_and_one_optional_record", len(visible) == 3 and
          {row["case_id"] for row in visible} == {"large_connected_m64", "small_full_cover_m4", "optional_decomposable_m64"})

    driver_paths = [BENCH / "validate_and_summarize_runs_v1.py", AUDIT / "gate_solver_v5_v6.py"]
    for path in driver_paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    check("post_run_drivers_parse", True, [str(path.relative_to(ROOT)) for path in driver_paths])
    check("post_run_validator_sha256", sha(BENCH / "validate_and_summarize_runs_v1.py")
          == freeze["post_run_validator_sha256"], sha(BENCH / "validate_and_summarize_runs_v1.py"))
    check("prelaunch_checker_sha256", sha(Path(__file__).resolve())
          == freeze["prelaunch_freeze_checker_sha256"], sha(Path(__file__).resolve()))
    check("expected_reference_validation_exists", sha(BENCH / "freeze_validation.json")
          == "c2aa7a769777f189fdb5d562bb4666c72227756fb7887089c4c8ec940f49e506")

    report = {
        "scientific_status": "passed_prelaunch_source_and_schedule_freeze",
        "execution_status": "success",
        "provider_jobs_run": 0,
        "freeze_sha256": sha(freeze_path),
        "batch_sha256": sha(batch_path),
        "post_run_validator_sha256": sha(BENCH / "validate_and_summarize_runs_v1.py"),
        "check_count": len(checks),
        "checks_passed": sum(c["passed"] for c in checks),
        "checks": checks,
        "jobs": [job["label"] for job in batch["order"]]
    }
    out = BENCH / "batch_preflight_v1.json"
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

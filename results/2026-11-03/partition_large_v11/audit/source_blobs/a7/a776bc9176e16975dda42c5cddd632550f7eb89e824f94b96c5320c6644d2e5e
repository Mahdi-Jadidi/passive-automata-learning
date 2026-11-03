#!/usr/bin/env python3
"""Balanced frozen baseline/candidate CLI benchmark; refuses launch without two GO bindings."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
RESULTS = ROOT.parent.parent
C010 = RESULTS / "2026-11-02" / "partition_unrestricted_v10"
C010_IMPL = C010 / "implementation"
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def resolve_binding(row: dict) -> tuple[Path, str]:
    path = (ROOT / row["path"]).resolve()
    if not path.is_file() or sha(path) != row["sha256"]:
        raise SystemExit(f"candidate binding hash/path mismatch: {row.get('path')}")
    return path, row["sha256"]

go_path = AUDIT / "MASTER_GO_V1.json"
binding_path = AUDIT / "CANDIDATE_BINDING_V1.json"
if not go_path.is_file() or not binding_path.is_file():
    raise SystemExit("master GO or candidate source binding missing; refusing benchmark")
go = json.loads(go_path.read_text(encoding="utf-8"))
if (go.get("status") != "GO" or go.get("baseline_runs_authorized") is not True
        or go.get("candidate_runs_authorized") is not True):
    raise SystemExit("master GO does not authorize both methods")
binding = json.loads(binding_path.read_text(encoding="utf-8"))
if binding.get("status") != "static_review_passed":
    raise SystemExit("candidate static review is not accepted")
candidate_solver, _ = resolve_binding(binding["solver"])
candidate_cli, _ = resolve_binding(binding["cli"])
candidate_readiness, _ = resolve_binding(binding["readiness"])
candidate_static_review, _ = resolve_binding(binding["static_review"])

if not (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").is_file():
    raise SystemExit("independent oracle receipt missing")
manifest = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
baseline_readiness = C010_IMPL / "READINESS_V3.json"
baseline_solver = C010_IMPL / "unrestricted_solver_v2.py"
baseline_cli = C010_IMPL / "unrestricted_cli_v2.py"
base_ready = json.loads(baseline_readiness.read_text(encoding="utf-8"))["files"]
for path in (baseline_solver, baseline_cli):
    if sha(path) != base_ready[path.name]["sha256"]:
        raise SystemExit(f"baseline source drift: {path.name}")

used = {"baseline": 0.0, "candidate": 0.0}
for result_path in (AUDIT / "attempts").glob("*/result.json"):
    result = json.loads(result_path.read_text(encoding="utf-8"))
    label = str(result.get("label", ""))
    if label.startswith("c011_baseline_cli_") or label.startswith("c011_memory_baseline_"):
        used["baseline"] += float(result.get("duration_seconds", 0.0))
    elif label.startswith("c011_candidate_cli_") or label.startswith("c011_memory_candidate_"):
        used["candidate"] += float(result.get("duration_seconds", 0.0))

base_sources = [
    Path(__file__).resolve(), (AUDIT / "capture.py").resolve(),
    (AUDIT / "PROTOCOL_V1.md").resolve(), (AUDIT / "CORRECTNESS_MANIFEST_V2.json").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V2.json").resolve(),
    (AUDIT / "FULL_CORRECTNESS_ORACLE_V2.jsonl").resolve(),
    (AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V2.json").resolve(),
    (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").resolve(),
    (AUDIT / "STATIC_REVIEW_INTERVAL_V1.md").resolve(),
    go_path.resolve(), binding_path.resolve(), candidate_static_review.resolve(),
    candidate_readiness.resolve(), candidate_solver.resolve(), candidate_cli.resolve(),
    baseline_readiness.resolve(), baseline_solver.resolve(), baseline_cli.resolve(),
    (C010 / "audit" / "PROTOCOL_PROVIDER_GATE_V2.md").resolve(),
    (ROOT / "coordination" / "CONTRACT.md").resolve(),
    (ROOT / "coordination" / "parent_manifest.json").resolve(),
]
rows = []
started = time.perf_counter()
for rep in range(1, 4):
    method_order = ("baseline", "candidate") if rep in (1, 3) else ("candidate", "baseline")
    for case in manifest["cells"]:
        input_path = AUDIT / case["path"]
        if sha(input_path) != case["input_sha256"]:
            raise SystemExit(f"frozen input hash drift: {case['case_id']}")
        for method in method_order:
            if used[method] + 30.0 > 760.0:
                rows.append({"method": method, "case_id": case["case_id"], "rep": rep,
                             "status": "not_started_method_timing_budget_censoring"})
                continue
            cli = baseline_cli if method == "baseline" else candidate_cli
            label = f"c011_{method}_cli_{case['case_id']}_rep{rep}"
            record = capture.capture(
                label,
                [sys.executable, "-B", "-X", "utf8", str(cli), str(input_path), "--seconds", "28"],
                cwd=ROOT,
                timeout_seconds=30.0,
                source_paths=base_sources + [input_path.resolve()],
            )
            duration = float(record.get("duration_seconds", 0.0))
            used[method] += duration
            rows.append({"method": method, "case_id": case["case_id"], "rep": rep,
                         "attempt_id": record["attempt_id"],
                         "execution_status": record["execution_status"],
                         "exit_code": record["exit_code"],
                         "child_reaped": record["child_reaped"],
                         "subprocess_seconds": record["subprocess_seconds"],
                         "capture_duration_seconds": duration,
                         "stdout_bytes": record["stdout_bytes"],
                         "stdout_sha256": record["stdout_sha256"]})
            if record.get("child_pid") is not None and record.get("child_reaped") is not True:
                print(json.dumps({"status": "aborted_unreaped_child", "used_seconds": used, "rows": rows}, sort_keys=True))
                return 2
            if record.get("cleanup_error") or record.get("capture_error"):
                print(json.dumps({"status": "aborted_capture_or_cleanup_error", "used_seconds": used, "rows": rows}, sort_keys=True))
                return 2
print(json.dumps({"status": "completed_or_budget_censored", "planned_cells": len(manifest["cells"]),
                  "planned_reps": 3, "used_method_capture_seconds": used,
                  "wall_elapsed_seconds": time.perf_counter() - started,
                  "launched": sum("attempt_id" in row for row in rows),
                  "censored_before_launch": sum(row.get("status") == "not_started_method_timing_budget_censoring" for row in rows),
                  "rows": rows}, ensure_ascii=False, sort_keys=True))
#!/usr/bin/env python3
"""Run the frozen C010 baseline CLI cells through the local copy of C010 capture."""
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

go_path = AUDIT / "MASTER_GO_V1.json"
if not go_path.is_file():
    raise SystemExit("master GO receipt absent; refusing baseline execution")
go = json.loads(go_path.read_text(encoding="utf-8"))
if go.get("status") != "GO" or go.get("baseline_runs_authorized") is not True:
    raise SystemExit("master GO receipt does not authorize baseline execution")
if not (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").is_file():
    raise SystemExit("oracle/freeze receipt absent; refusing baseline execution")
manifest = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
readiness = json.loads((C010_IMPL / "READINESS_V3.json").read_text(encoding="utf-8"))
solver = C010_IMPL / "unrestricted_solver_v2.py"
cli = C010_IMPL / "unrestricted_cli_v2.py"
for path in (solver, cli):
    expected = readiness["files"][path.name]
    if sha(path) != expected["sha256"]:
        raise SystemExit(f"baseline source drift: {path.name}")

prior_seconds = 0.0
for result_path in (AUDIT / "attempts").glob("*/result.json"):
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if str(result.get("label", "")).startswith(("c011_baseline_cli_", "c011_memory_baseline_")):
        prior_seconds += float(result.get("duration_seconds", 0.0))
start = time.perf_counter()
rows = []
for rep in range(1, 4):
    for case in manifest["cells"]:
        elapsed = prior_seconds + (time.perf_counter() - start)
        if elapsed + 30.0 > 760.0:
            rows.append({"case_id": case["case_id"], "rep": rep, "status": "not_started_budget_censoring"})
            continue
        input_path = AUDIT / case["path"]
        if sha(input_path) != case["input_sha256"]:
            raise SystemExit(f"input hash drift: {case['case_id']}")
        sources = [
            Path(__file__).resolve(),
            (AUDIT / "capture.py").resolve(),
            (AUDIT / "PROTOCOL_V1.md").resolve(),
            (AUDIT / "CORRECTNESS_MANIFEST_V2.json").resolve(),
            (AUDIT / "PERFORMANCE_MANIFEST_V2.json").resolve(),
            (AUDIT / "FULL_CORRECTNESS_ORACLE_V2.jsonl").resolve(),
            (AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V2.json").resolve(),
            (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").resolve(),
            (AUDIT / "STATIC_REVIEW_INTERVAL_V1.md").resolve(),
            go_path.resolve(), input_path.resolve(), solver.resolve(), cli.resolve(),
            (C010_IMPL / "READINESS_V3.json").resolve(),
            (C010 / "audit" / "PROTOCOL_PROVIDER_GATE_V2.md").resolve(),
            (ROOT / "coordination" / "CONTRACT.md").resolve(),
            (ROOT / "coordination" / "parent_manifest.json").resolve(),
        ]
        label = f"c011_baseline_cli_{case['case_id']}_rep{rep}"
        record = capture.capture(
            label,
            [sys.executable, "-B", "-X", "utf8", str(cli), str(input_path), "--seconds", "28"],
            cwd=ROOT,
            timeout_seconds=30.0,
            source_paths=sources,
        )
        rows.append({"case_id": case["case_id"], "rep": rep,
                     "attempt_id": record["attempt_id"],
                     "execution_status": record["execution_status"],
                     "exit_code": record["exit_code"],
                     "child_reaped": record["child_reaped"],
                     "subprocess_seconds": record["subprocess_seconds"],
                     "capture_duration_seconds": record["duration_seconds"]})
        if record.get("child_pid") is not None and record.get("child_reaped") is not True:
            print(json.dumps({"status": "aborted_unreaped_child", "rows": rows}, sort_keys=True))
            return 2
        if record.get("cleanup_error") or record.get("capture_error"):
            print(json.dumps({"status": "aborted_capture_or_cleanup_error", "rows": rows}, sort_keys=True))
            return 2
print(json.dumps({"status": "completed_or_budget_censored", "method": "C010 baseline v2",
                  "planned_cells": len(manifest["cells"]), "planned_reps": 3,
                  "attempts": sum("attempt_id" in row for row in rows),
                  "not_started": sum(row.get("status") == "not_started_budget_censoring" for row in rows),
                  "rows": rows}, ensure_ascii=False, sort_keys=True))
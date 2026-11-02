#!/usr/bin/env python3
"""Run four preregistered correctness-only scale cells once each with captures."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import capture


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
SCALE_DIR = ROOT / "scale_v1"
MANIFEST = SCALE_DIR / "manifest.json"
ORACLE = SCALE_DIR / "oracle_v1.jsonl"
PROTOCOL = ROOT / "SCALE_PROTOCOL_V1.md"
CONTRACT = ROOT.parent / "coordination" / "CONTRACT.md"
IMPLEMENTATION = WORKSPACE / "results/2026-11-02/partition_coverage_v9/implementation"
CLI = IMPLEMENTATION / "ownership_cli_v1.py"
SOLVER = IMPLEMENTATION / "ownership_solver_v1.py"
API_PROTOCOL = IMPLEMENTATION / "API_PROTOCOL_V1.md"
READINESS = IMPLEMENTATION / "READINESS_V1.json"
GATE_REPORT = ROOT / "provider_gate_validation_v1.json"
CONTROLS_REPORT = ROOT / "controls_validation_v3.json"
WRAPPER_REPORT = ROOT / "root_wrapper_validation_v1.json"
LEDGER = ROOT / "scale_provider_ledger_v1.jsonl"
SUMMARY = ROOT / "scale_provider_run_v1.json"

EXPECTED = {
    CLI: "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507",
    SOLVER: "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7",
    API_PROTOCOL: "111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b",
    READINESS: "e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087",
    MANIFEST: "bfe267967d6c759725cbdee77a93aa71edaef15ee8319695f7ae22f0f48bbd40",
    ORACLE: "5d23984b5c502a883b76761cf430ab2495555c3282cdc99e650019c0e473161a",
    PROTOCOL: "114a96eef1cb8bc38014cda16b72c209236b92d9071d3bbfd0efbbcb5af1960c",
    CONTRACT: "c3f5fddc4e8356e57c01870648234cfbb02a0a6e893bd78484661df7426b1521",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"scale source/input hash drift: {path}")
    if sha(ROOT / "capture.py") != "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf":
        raise SystemExit("scale capture helper hash drift")
    for report_path, expected_status in (
        (GATE_REPORT, "accepted_independent_provider_gate"),
        (CONTROLS_REPORT, "accepted_independent_controls_audit"),
        (WRAPPER_REPORT, "accepted_root_wrapper_control"),
    ):
        if json.loads(report_path.read_text(encoding="utf-8"))["status"] != expected_status:
            raise SystemExit(f"scale prereq is not accepted: {report_path}")
    if LEDGER.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite scale provider results")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    oracle_rows = [json.loads(line) for line in ORACLE.read_text(encoding="utf-8").splitlines()]
    if len(manifest["cases"]) != 4 or [row["case_id"] for row in manifest["cases"]] != [row["case_id"] for row in oracle_rows]:
        raise SystemExit("scale input/oracle cell order mismatch")
    oracle_by_id = {row["case_id"]: row for row in oracle_rows}
    frozen = dict(EXPECTED)
    frozen[ROOT / "capture.py"] = sha(ROOT / "capture.py")
    frozen[Path(__file__)] = sha(Path(__file__))
    counts: dict[str, int] = {}
    rows = []
    python = sys.executable
    for case in manifest["cases"]:
        input_path = SCALE_DIR / case["path"]
        if sha(input_path) != case["input_sha256"]:
            raise SystemExit(f"scale input hash mismatch: {case['case_id']}")
        command = [python, "-B", "-X", "utf8", str(CLI), str(input_path), "--seconds", "27", "--enumerate"]
        record = capture.capture(
            f"scale-correctness-{case['case_id']}", command, cwd=WORKSPACE, timeout_seconds=30.0,
            source_paths=[Path(__file__), CLI, SOLVER, API_PROTOCOL, READINESS, input_path, MANIFEST, ORACLE,
                          PROTOCOL, CONTRACT, GATE_REPORT, CONTROLS_REPORT, WRAPPER_REPORT],
        )
        counts[record["execution_status"]] = counts.get(record["execution_status"], 0) + 1
        payload = None
        error = None
        try:
            payload = json.loads((Path(record["attempt_dir"]) / "stdout.bin").read_bytes())
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            error = repr(exc)
        cap_manifest = json.loads((Path(record["attempt_dir"]) / "manifest.json").read_text(encoding="utf-8"))
        source_hashes = {str(Path(item["path"]).resolve()): item["sha256"] for item in cap_manifest["sources"]}
        expected_sources = dict(frozen)
        expected_sources[input_path] = case["input_sha256"]
        source_match = all(source_hashes.get(str(path.resolve())) == digest for path, digest in expected_sources.items())
        row = {
            "case_id": case["case_id"],
            "input_sha256": case["input_sha256"],
            "expected_partition_count": case["expected_partition_count"],
            "attempt_id": record["attempt_id"],
            "attempt_dir": str(Path(record["attempt_dir"]).relative_to(ROOT)),
            "execution_status": record["execution_status"],
            "exit_code": record["exit_code"],
            "child_reaped": record["child_reaped"],
            "provider_status": payload.get("status") if isinstance(payload, dict) else None,
            "provider_complete": payload.get("complete") if isinstance(payload, dict) else None,
            "provider_partition_count": payload.get("partition_count") if isinstance(payload, dict) else None,
            "provider_json_error": error,
            "source_snapshot_match": source_match,
            "stdout_bytes": record["stdout_bytes"],
            "stdout_sha256": record["stdout_sha256"],
            "stderr_bytes": record["stderr_bytes"],
            "stderr_sha256": record["stderr_sha256"],
            "subprocess_seconds": record["subprocess_seconds"],
            "oracle_partition_count": oracle_by_id[case["case_id"]]["partition_count"],
        }
        rows.append(row)
        if not source_match or record["child_reaped"] is not True:
            break
    with LEDGER.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))
        handle.flush()
    summary = {
        "schema_version": 1,
        "status": "captured_all_scale_cells" if len(rows) == 4 else "stopped_on_source_or_reap_failure",
        "planned_cells": 4,
        "captured_cells": len(rows),
        "execution_status_counts": counts,
        "all_child_processes_reaped": all(row["child_reaped"] is True for row in rows),
        "protocol_sha256": sha(PROTOCOL),
        "manifest_sha256": sha(MANIFEST),
        "oracle_sha256": sha(ORACLE),
        "provider_solver_sha256": sha(SOLVER),
        "provider_cli_sha256": sha(CLI),
        "runner_sha256": sha(Path(__file__)),
        "ledger_sha256": sha(LEDGER),
    }
    with SUMMARY.open("xb") as handle:
        handle.write((json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if len(rows) == 4 and summary["all_child_processes_reaped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

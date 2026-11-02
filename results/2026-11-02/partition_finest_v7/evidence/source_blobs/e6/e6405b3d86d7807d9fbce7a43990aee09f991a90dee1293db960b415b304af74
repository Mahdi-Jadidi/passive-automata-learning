#!/usr/bin/env python3
"""Independently replay the master-owned root wrapper CLI smoke."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import validate_scale_v3 as scale_replay


ROOT = Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_root_cli_smoke_v1.py ROOT_CLI_ATTEMPT_ID")
    attempt_id = sys.argv[1]
    attempt = ROOT / "evidence" / "attempts" / attempt_id
    case_rows = {row["case_id"]: row for row in scale_replay.read_jsonl(ROOT / "audit" / "scale_v1" / "inputs.jsonl")}
    sidecars = {row["case_id"]: row for row in scale_replay.read_jsonl(ROOT / "audit" / "scale_v1" / "truth_sidecars.jsonl")}
    case_id = "scale_m64_equal8"
    result = scale_replay.verify_case(
        case_rows[case_id], sidecars[case_id],
        ROOT / "audit" / "scale_v1" / "cli_inputs" / f"{case_id}.json",
        attempt / "stdout.bin", attempt / "manifest.json", attempt / "result.json")
    manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    wrapper = str((ROOT / "solver.py").resolve())
    source_map = {source["path"]: source["sha256"] for source in manifest.get("sources", [])}
    wrapper_sha = hashlib.sha256((ROOT / "solver.py").read_bytes()).hexdigest()
    failures = list(result["failures"])
    if source_map.get(wrapper) != wrapper_sha:
        failures.append("root_wrapper_not_bound_to_capture")
    if not manifest.get("command_argv") or not manifest["command_argv"][0].lower().endswith("python.exe"):
        failures.append("unexpected_root_cli_command")
    report = {
        "schema_version": 1,
        "status": "accepted" if not failures and result["scientific_status"] == "accepted_unique_finest_by_forced_path_edges" else "rejected",
        "case_id": case_id,
        "root_wrapper": str(ROOT / "solver.py"),
        "root_wrapper_sha256": wrapper_sha,
        "capture_attempt_id": attempt_id,
        "execution_status": result["capture_execution_status"],
        "scientific_status": result["scientific_status"],
        "alphabet_size": result.get("alphabet_size"),
        "blocks": result.get("expected_blocks"),
        "forced_edges": result.get("edge_witnesses"),
        "stdout_sha256": result.get("stdout_sha256"),
        "failures": failures,
    }
    out = ROOT / "audit" / "root_cli_v1.json"
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())

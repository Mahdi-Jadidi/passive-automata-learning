#!/usr/bin/env python3
"""Execute the explicitly approved C007 v4 V2 timing schedule with per-run replay."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
EVIDENCE = ROOT / "evidence"
TIMING = AUDIT / "timing_v2"
MANIFEST_PATH = TIMING / "input_manifest_v2.json"
PROPOSAL_PATH = TIMING / "PROPOSAL_V2.md"
INTEGRITY_PATH = TIMING / "proposal_integrity_v2.json"
GO_PATH = ROOT / "coordination" / "PERFORMANCE_GO_V2.json"
PROVIDER = ROOT / "implementation" / "finest_solver_v4.py"
CLI = ROOT / "implementation" / "finest_cli_v2.py"
PROTOCOL = ROOT / "implementation" / "PROTOCOL_V5.md"
READINESS = ROOT / "implementation" / "READINESS_V4.json"
WRAPPER = ROOT / "solver.py"
CAPTURE_PATH = EVIDENCE / "capture.py"
VALIDATOR = AUDIT / "validate_v4_timing_capture_v2.py"
REPLAY_HELPER = AUDIT / "validate_provider_gate_v3.py"
C006 = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
C005 = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"
LEDGER_PATH = TIMING / "run_ledger_v1.jsonl"
SUMMARY_PATH = TIMING / "suite_summary_v1.json"

EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "readiness": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "wrapper": "d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de",
    "capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
    "validator": "b85467c83b28752286711f653c079187ff1163bc70810c9adb04548d4579668e",
    "replay_helper": "f49e4822ed1f6c50a603024c42989792e2deb2b0669d3bf3a82858edbb61e4e6",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
    "manifest": "e07b0a15559becc5b13a44a5baee978b7ccefb86f06a0a4034aaa668b4625737",
    "proposal": "fcf908fd7b32d445d256b3cd75d20be970001c86a4c1a6a3bf75e9cf0b6b3f89",
    "integrity": "1a78f2a2ed731d388ebef5a74567445ace0636489a3140a5103c08e333d46132",
    "go": "d7b51ff312396599255c0b0ca0dc69d720d7567e6769b2e3d20b23351d75ded6",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def load_capture_module():
    spec = importlib.util.spec_from_file_location("c007_capture_v1", CAPTURE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen capture helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_frozen(manifest, integrity, go):
    paths = {
        "provider": PROVIDER, "cli": CLI, "protocol": PROTOCOL,
        "readiness": READINESS, "wrapper": WRAPPER, "capture": CAPTURE_PATH,
        "validator": VALIDATOR, "replay_helper": REPLAY_HELPER,
        "c006": C006, "c005": C005, "manifest": MANIFEST_PATH,
        "proposal": PROPOSAL_PATH, "integrity": INTEGRITY_PATH, "go": GO_PATH,
    }
    for key, path in paths.items():
        actual = file_sha(path)
        if actual != EXPECTED[key]:
            raise RuntimeError(f"frozen {key} source drift: {actual}")
    if (go.get("decision") != "GO" or go.get("proposal_sha256") != EXPECTED["proposal"]
            or go.get("input_manifest_sha256") != EXPECTED["manifest"]
            or go.get("validator_sha256") != EXPECTED["validator"]
            or go.get("max_provider_processes") != 18 or go.get("cooperative_seconds") != 28
            or go.get("hard_seconds") != 30 or go.get("subprocess_budget_seconds_per_mode") != 300
            or go.get("source_changes") != "not authorized"):
        raise RuntimeError("master GO record does not authorize this exact frozen schedule")
    if manifest.get("status") != "frozen_inputs_prepared_no_timing_run" or len(manifest.get("cases", {})) != 3:
        raise RuntimeError("V2 timing input manifest is not frozen as proposed")
    if integrity.get("state") != "frozen_proposal_waiting_for_explicit_master_go":
        raise RuntimeError("proposal integrity record changed unexpectedly")


def build_schedule():
    rows = []
    for case_id, mode_order in (
        ("c007_gen_m04_013", (("adaptive", "reference"), ("reference", "adaptive"), ("adaptive", "reference"))),
        ("ctrl_empty_must_link_unique_3", (("reference", "adaptive"), ("adaptive", "reference"), ("reference", "adaptive"))),
        ("c007_gen_m08_000", (("adaptive", "reference"), ("reference", "adaptive"), ("adaptive", "reference"))),
    ):
        for repetition, pair in enumerate(mode_order, start=1):
            for mode in pair:
                rows.append({"case_id": case_id, "repetition": repetition, "mode": mode})
    if len(rows) != 18:
        raise AssertionError("frozen run schedule should have 18 jobs")
    return rows


def source_paths(case_info):
    rgs = AUDIT / case_info["rgs_oracle_path"]
    independent = AUDIT / case_info["independent_oracle_path"]
    input_path = TIMING / case_info["path"]
    return [
        Path(__file__), VALIDATOR, REPLAY_HELPER, WRAPPER, PROVIDER, CLI, PROTOCOL,
        READINESS, CAPTURE_PATH, C005, C006, MANIFEST_PATH, PROPOSAL_PATH, INTEGRITY_PATH,
        GO_PATH, input_path, rgs, independent,
        AUDIT / "corpus_v1" / "all_valid_inputs.jsonl",
    ]


def main() -> int:
    if LEDGER_PATH.exists() or SUMMARY_PATH.exists():
        raise SystemExit("timing ledger already exists; refusing duplicate provider runs")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    integrity = json.loads(INTEGRITY_PATH.read_text(encoding="utf-8"))
    go = json.loads(GO_PATH.read_text(encoding="utf-8"))
    assert_frozen(manifest, integrity, go)
    capture = load_capture_module()
    jobs = build_schedule()
    time_by_mode = {"adaptive": 0.0, "reference": 0.0}
    execution_rows = []
    stop_reason = None
    ledger_path = LEDGER_PATH
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("x", encoding="utf-8", newline="\n") as ledger:
        for index, job in enumerate(jobs, start=1):
            mode = job["mode"]
            case_id = job["case_id"]
            case_info = manifest["cases"][case_id]
            input_path = TIMING / case_info["path"]
            sources = source_paths(case_info)
            if time_by_mode[mode] >= 300.0:
                stop_reason = f"{mode}_cumulative_subprocess_budget_reached"
                break
            provider_label = f"c007_v4_timing_{case_id}_r{job['repetition']}_{mode}"
            provider_command = [sys.executable, "-B", "-X", "utf8", str(WRAPPER),
                                str(input_path), "--mode", mode, "--seconds", "28"]
            provider_capture = capture.capture(
                provider_label, provider_command, cwd=ROOT, timeout_seconds=30.0,
                source_paths=sources)
            provider_attempt_id = provider_capture["attempt_id"]
            provider_dir = Path(provider_capture["attempt_dir"])
            time_by_mode[mode] += float(provider_capture.get("subprocess_seconds", 0.0))

            validator_sources = sources + [
                provider_dir / "manifest.json", provider_dir / "result.json",
                provider_dir / "stdout.bin", provider_dir / "stderr.bin",
            ]
            validator_label = f"c007_v4_timing_validation_{case_id}_r{job['repetition']}_{mode}"
            validator_command = [sys.executable, "-B", "-X", "utf8", str(VALIDATOR),
                                 provider_attempt_id, mode, case_id]
            validator_capture = capture.capture(
                validator_label, validator_command, cwd=ROOT, timeout_seconds=60.0,
                source_paths=validator_sources)
            report_path = TIMING / "validations" / f"{provider_attempt_id}.json"
            validation_report = (json.loads(report_path.read_text(encoding="utf-8"))
                                 if report_path.is_file() else None)
            validation_status = validation_report.get("status") if validation_report else "missing_report"
            row = {
                "schedule_index": index,
                "case_id": case_id,
                "repetition": job["repetition"],
                "mode": mode,
                "provider_attempt_id": provider_attempt_id,
                "provider_execution_status": provider_capture.get("execution_status"),
                "provider_exit_code": provider_capture.get("exit_code"),
                "provider_child_reaped": provider_capture.get("child_reaped"),
                "provider_subprocess_seconds": provider_capture.get("subprocess_seconds"),
                "provider_stdout_bytes": provider_capture.get("stdout_bytes"),
                "provider_stdout_sha256": provider_capture.get("stdout_sha256"),
                "validator_attempt_id": validator_capture.get("attempt_id"),
                "validator_execution_status": validator_capture.get("execution_status"),
                "validator_exit_code": validator_capture.get("exit_code"),
                "validation_status": validation_status,
                "scientific_status": validation_report.get("scientific_status") if validation_report else None,
                "provider_status": validation_report.get("provider_status") if validation_report else None,
                "validation_report_path": str(report_path.relative_to(ROOT)),
                "validation_report_sha256": file_sha(report_path) if report_path.is_file() else None,
                "internal_metrics": validation_report.get("provider_metrics") if validation_report else None,
            }
            ledger.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            ledger.flush()
            import os
            os.fsync(ledger.fileno())
            execution_rows.append(row)

            # Any independent rejection or capture infrastructure failure pauses the suite.
            if (validation_status != "accepted"
                    or validator_capture.get("execution_status") != "success"
                    or provider_capture.get("child_reaped") is not True
                    or provider_capture.get("execution_status") in ("capture_error", "environment_error", "interrupted")):
                stop_reason = f"independent_validation_or_capture_failure_at_schedule_index_{index}"
                break

    complete_schedule = len(execution_rows) == len(jobs)
    summary = {
        "schema_version": 1,
        "status": "complete" if complete_schedule and all(row["validation_status"] == "accepted" for row in execution_rows) else "paused_or_incomplete",
        "proposal_sha256": EXPECTED["proposal"],
        "input_manifest_sha256": EXPECTED["manifest"],
        "master_go_sha256": EXPECTED["go"],
        "planned_jobs": len(jobs),
        "provider_jobs_run": len(execution_rows),
        "provider_jobs_independently_accepted_or_censored": sum(row["validation_status"] == "accepted" for row in execution_rows),
        "stop_reason": stop_reason,
        "subprocess_seconds_by_mode": time_by_mode,
        "run_ledger_path": str(ledger_path.relative_to(ROOT)),
        "run_ledger_sha256": file_sha(ledger_path),
        "execution_rows": execution_rows,
        "timing_caveat": "subprocess_seconds is primary; v4 internal fields do not partition fallback elapsed time",
    }
    write_json(SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Capture one full-enumeration CLI process for each frozen Stage-A valid case."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import capture


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
CORPUS = ROOT / "corpus_v1"
MANIFEST_PATH = CORPUS / "manifest.json"
ORACLE_PATH = ROOT / "oracle_v1.jsonl"
PROTOCOL_PATH = ROOT / "PROTOCOL_AUDIT_V1.md"
AMENDMENT_PATH = ROOT / "PROTOCOL_AUDIT_AMENDMENT_V2.md"
GATE_PROTOCOL_PATH = ROOT / "PROVIDER_GATE_PROTOCOL_V1.md"
CONTRACT_PATH = ROOT.parent / "coordination" / "CONTRACT.md"
IMPLEMENTATION = WORKSPACE / "results/2026-11-02/partition_coverage_v9/implementation"
CLI_PATH = IMPLEMENTATION / "ownership_cli_v1.py"
SOLVER_PATH = IMPLEMENTATION / "ownership_solver_v1.py"
API_PROTOCOL_PATH = IMPLEMENTATION / "API_PROTOCOL_V1.md"
READINESS_PATH = IMPLEMENTATION / "READINESS_V1.json"
LEDGER_PATH = ROOT / "provider_gate_ledger_v2.jsonl"
SUMMARY_PATH = ROOT / "provider_gate_run_v2.json"
RECOVERED_FIRST_ATTEMPT = "20261102T105532.160951Z_4e6a888f5d"
PREVIOUS_RUNNER_SHA = "fb831300d5f4c8360f904d779d58ed57e88dea0495d6653bdc1b19dc9c757f52"

EXPECTED = {
    SOLVER_PATH: "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7",
    CLI_PATH: "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507",
    API_PROTOCOL_PATH: "111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b",
    READINESS_PATH: "e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087",
    MANIFEST_PATH: "bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1",
    ORACLE_PATH: "01f7973358400f6e17d0b60ed6646e75f2244bfcba92d262d6149b5e0e9d35d2",
    PROTOCOL_PATH: "e02d3a4a210fdff1197b778d913a6ba36c809512a114ef6f3bffc5606e40f85d",
    AMENDMENT_PATH: "444b613f51e9b2a2b150d6138815008d84e6e8610c39f145b4d5252e937ec4c4",
    GATE_PROTOCOL_PATH: "eeec7267dcb2f52bd20634176027bc71306facb05d18f0cc0cc54c8e7311bc23",
    CONTRACT_PATH: "c3f5fddc4e8356e57c01870648234cfbb02a0a6e893bd78484661df7426b1521",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"frozen source/data hash mismatch: {path} {actual} != {expected}")
    if sha(ROOT / "capture.py") != "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf":
        raise SystemExit("copied capture helper hash mismatch")
    frozen_capture_sources = dict(EXPECTED)
    frozen_capture_sources.update({
        Path(__file__): sha(Path(__file__)),
        ROOT / "capture.py": sha(ROOT / "capture.py"),
        PROTOCOL_PATH: sha(PROTOCOL_PATH),
        AMENDMENT_PATH: sha(AMENDMENT_PATH),
        GATE_PROTOCOL_PATH: sha(GATE_PROTOCOL_PATH),
        CONTRACT_PATH: sha(CONTRACT_PATH),
    })
    runner_sha = sha(Path(__file__))
    if LEDGER_PATH.exists() or SUMMARY_PATH.exists():
        raise SystemExit("refusing to overwrite an existing provider gate run")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    oracle_rows = [json.loads(line) for line in ORACLE_PATH.read_text(encoding="utf-8").splitlines()]
    if len(manifest["valid_cases"]) != 129 or len(oracle_rows) != 129:
        raise SystemExit("unexpected frozen Stage-A case count")
    oracle_by_id = {row["case_id"]: row for row in oracle_rows}
    if [row["case_id"] for row in manifest["valid_cases"]] != [row["case_id"] for row in oracle_rows]:
        raise SystemExit("manifest/oracle case order mismatch")

    python = sys.executable
    counts: dict[str, int] = {"success": 1}
    status = "accepted_capture_batch"
    stop_case = None
    first_case = manifest["valid_cases"][0]
    recovery_dir = ROOT / "attempts" / RECOVERED_FIRST_ATTEMPT
    recovery_manifest = json.loads((recovery_dir / "manifest.json").read_text(encoding="utf-8"))
    recovery_result = json.loads((recovery_dir / "result.json").read_text(encoding="utf-8"))
    recovery_payload = json.loads((recovery_dir / "stdout.bin").read_bytes())
    recovery_hashes = {str(Path(item["path"]).resolve()): item["sha256"] for item in recovery_manifest["sources"]}
    expected_recovery_sources = dict(frozen_capture_sources)
    expected_recovery_sources.pop(Path(__file__))
    expected_recovery_sources[ROOT / "run_provider_gate_v1.py"] = PREVIOUS_RUNNER_SHA
    first_input = CORPUS / first_case["path"]
    expected_recovery_sources[first_input] = first_case["input_sha256"]
    if (recovery_manifest.get("label") != f"provider-full-enumeration-{first_case['case_id']}"
            or recovery_result.get("execution_status") != "success"
            or recovery_result.get("exit_code") != 0
            or recovery_result.get("child_reaped") is not True
            or not all(recovery_hashes.get(str(path.resolve())) == digest for path, digest in expected_recovery_sources.items())
            or recovery_payload.get("complete") is not True
            or recovery_payload.get("status") not in {"model_inconsistent", "identified_unique_partition", "partial_ownership_identification"}):
        raise SystemExit("the saved first provider capture failed recovery validation; stopping without rerun")
    with LEDGER_PATH.open("x", encoding="utf-8", newline="\n") as ledger:
        recovered_row = {
            "case_id": first_case["case_id"],
            "input_sha256": first_case["input_sha256"],
            "oracle_partition_count": oracle_by_id[first_case["case_id"]]["partition_count"],
            "attempt_id": RECOVERED_FIRST_ATTEMPT,
            "attempt_dir": str(recovery_dir.relative_to(ROOT)),
            "execution_status": recovery_result["execution_status"],
            "exit_code": recovery_result["exit_code"],
            "child_reaped": recovery_result["child_reaped"],
            "provider_status": recovery_payload.get("status"),
            "provider_complete": recovery_payload.get("complete"),
            "provider_json_error": None,
            "source_snapshot_match": True,
            "stdout_bytes": recovery_result["stdout_bytes"],
            "stdout_sha256": recovery_result["stdout_sha256"],
            "stderr_bytes": recovery_result["stderr_bytes"],
            "stderr_sha256": recovery_result["stderr_sha256"],
            "subprocess_seconds": recovery_result["subprocess_seconds"],
            "recovered_from_orchestration_failure": True,
        }
        ledger.write(json.dumps(recovered_row, ensure_ascii=False, sort_keys=True) + "\n")
        ledger.flush()
        for case in manifest["valid_cases"][1:]:
            input_path = CORPUS / case["path"]
            if sha(input_path) != case["input_sha256"]:
                status, stop_case = "aborted_input_hash_mismatch", case["case_id"]
                break
            command = [python, "-B", "-X", "utf8", str(CLI_PATH), str(input_path), "--seconds", "20", "--enumerate"]
            record = capture.capture(
                f"provider-full-enumeration-{case['case_id']}",
                command,
                cwd=WORKSPACE,
                timeout_seconds=25.0,
                source_paths=[
                    Path(__file__), CLI_PATH, SOLVER_PATH, API_PROTOCOL_PATH, READINESS_PATH,
                    input_path, MANIFEST_PATH, ORACLE_PATH, PROTOCOL_PATH, AMENDMENT_PATH, GATE_PROTOCOL_PATH, CONTRACT_PATH,
                ],
            )
            counts[record["execution_status"]] = counts.get(record["execution_status"], 0) + 1
            payload = None
            payload_error = None
            try:
                payload = json.loads((Path(record["attempt_dir"]) / "stdout.bin").read_bytes())
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                payload_error = repr(exc)
            attempt_manifest = json.loads((Path(record["attempt_dir"]) / "manifest.json").read_text(encoding="utf-8"))
            snapshot_hashes = {str(Path(item["path"]).resolve()): item["sha256"] for item in attempt_manifest["sources"]}
            expected_case_sources = dict(frozen_capture_sources)
            expected_case_sources[input_path] = case["input_sha256"]
            source_snapshot_match = all(snapshot_hashes.get(str(path.resolve())) == expected for path, expected in expected_case_sources.items())
            row = {
                "case_id": case["case_id"],
                "input_sha256": case["input_sha256"],
                "oracle_partition_count": oracle_by_id[case["case_id"]]["partition_count"],
                "attempt_id": record["attempt_id"],
                "attempt_dir": str(Path(record["attempt_dir"]).relative_to(ROOT)),
                "execution_status": record["execution_status"],
                "exit_code": record["exit_code"],
                "child_reaped": record["child_reaped"],
                "provider_status": payload.get("status") if isinstance(payload, dict) else None,
                "provider_complete": payload.get("complete") if isinstance(payload, dict) else None,
                "provider_json_error": payload_error,
                "source_snapshot_match": source_snapshot_match,
                "stdout_bytes": record["stdout_bytes"],
                "stdout_sha256": record["stdout_sha256"],
                "stderr_bytes": record["stderr_bytes"],
                "stderr_sha256": record["stderr_sha256"],
                "subprocess_seconds": record["subprocess_seconds"],
            }
            ledger.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            ledger.flush()
            if not source_snapshot_match:
                status, stop_case = "stopped_source_snapshot_drift", case["case_id"]
                break
            if record["execution_status"] != "success" or record["exit_code"] != 0 or record["child_reaped"] is not True:
                status, stop_case = "stopped_provider_capture_or_cli_failure", case["case_id"]
                break
            if not isinstance(payload, dict) or payload.get("complete") is not True or payload.get("status") not in {
                "model_inconsistent", "identified_unique_partition", "partial_ownership_identification"
            }:
                status, stop_case = "stopped_incomplete_or_malformed_provider_result", case["case_id"]
                break
    summary = {
        "schema_version": 1,
        "status": status,
        "planned_cases": 129,
        "captured_cases": sum(counts.values()),
        "recovered_prior_case_ids": [first_case["case_id"]],
        "execution_status_counts": counts,
        "stop_case": stop_case,
        "provider_cli_sha256": sha(CLI_PATH),
        "provider_solver_sha256": sha(SOLVER_PATH),
        "corpus_manifest_sha256": sha(MANIFEST_PATH),
        "oracle_sha256": sha(ORACLE_PATH),
        "stage_a_protocol_sha256": sha(PROTOCOL_PATH),
        "protocol_amendment_sha256": sha(AMENDMENT_PATH),
        "gate_protocol_sha256": sha(GATE_PROTOCOL_PATH),
        "contract_sha256": sha(CONTRACT_PATH),
        "runner_sha256": runner_sha,
        "ledger_sha256": sha(LEDGER_PATH),
    }
    with SUMMARY_PATH.open("xb") as handle:
        handle.write((json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if status == "accepted_capture_batch" and sum(counts.values()) == 129 else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independently validate the saved malformed, deadline, and interruption captures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import run_controls_v1 as run


ROOT = run.ROOT
REPORT = ROOT / "controls_validation_v1.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    ledger = [json.loads(line) for line in run.LEDGER.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(run.SUMMARY.read_text(encoding="utf-8"))
    preflight = json.loads((ROOT / "controls_preflight_v1.json").read_text(encoding="utf-8"))
    require(len(ledger) == 9, "expected seven invalid plus deadline and interruption rows")
    require(summary["status"] == "accepted_controls" and summary["all_completed_controls_accepted"], "control runner summary failed")
    require(preflight["status"] == "frozen_control_preflight_passed" and preflight["failure_count"] == 0,
            "control preflight was not clean")
    require(summary["runner_sha256"] == sha(Path(run.__file__).read_bytes()), "control runner source hash mismatch")
    require(summary["runner_sha256"] == preflight["control_runner_sha256"], "runner changed after preflight")
    require(sha(run.LEDGER.read_bytes()) == summary["ledger_sha256"], "control ledger hash mismatch")
    valid_ids = {json.loads(line)["case_id"] for line in run.INVALID_MANIFEST.read_text(encoding="utf-8").splitlines()}
    invalid_rows = [row for row in ledger if row["kind"] == "invalid_input"]
    require(len(invalid_rows) == 7 and {row["case_id"] for row in invalid_rows} == valid_ids, "invalid control case set mismatch")
    checks = []
    for row in ledger:
        attempt_dir = ROOT / row["attempt_dir"] if row.get("attempt_dir") else None
        if attempt_dir is None:
            # The compact control ledger intentionally stores attempt IDs; resolve the unique capture directory.
            matches = []
            for folder in (ROOT / "attempts").iterdir():
                manifest_path = folder / "manifest.json"
                if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8"))["attempt_id"] == row["attempt_id"]:
                    matches.append(folder)
            require(len(matches) == 1, f"capture attempt not uniquely found: {row['attempt_id']}")
            attempt_dir = matches[0]
        capture_manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
        capture_result = json.loads((attempt_dir / "result.json").read_text(encoding="utf-8"))
        stdout = (attempt_dir / "stdout.bin").read_bytes()
        stderr = (attempt_dir / "stderr.bin").read_bytes()
        require(capture_result["stdout_sha256"] == sha(stdout) == row["stdout_sha256"], f"stdout stream hash mismatch: {row['case_id']}")
        require(capture_result["stderr_sha256"] == sha(stderr) == row["stderr_sha256"], f"stderr stream hash mismatch: {row['case_id']}")
        require(capture_result["child_reaped"] is True and row["child_reaped"] is True, f"unreaped control child: {row['case_id']}")
        payload = json.loads(stdout)
        source_hashes = {str(Path(item["path"]).resolve()): item["sha256"] for item in capture_manifest["sources"]}
        expected_sources = {
            run.ROOT / "capture.py": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
            run.CLI: "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507",
            run.SOLVER: "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7",
            run.API_PROTOCOL: "111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b",
            run.READINESS: "e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087",
            run.CORPUS_MANIFEST: run.EXPECTED[run.CORPUS_MANIFEST],
            run.INVALID_MANIFEST: run.EXPECTED[run.INVALID_MANIFEST],
            run.CONTROLS_PROTOCOL: run.EXPECTED[run.CONTROLS_PROTOCOL],
            run.CONTRACT: run.EXPECTED[run.CONTRACT],
        }
        if row["kind"] == "invalid_input":
            invalid_meta = next(item for item in [json.loads(line) for line in run.INVALID_MANIFEST.read_text(encoding="utf-8").splitlines()]
                                if item["case_id"] == row["case_id"])
            expected_sources[run.CORPUS / invalid_meta["path"]] = invalid_meta["input_sha256"]
        elif row["kind"] == "expired_deadline":
            expected_sources[run.ADDENDUM_INPUT] = run.EXPECTED[run.ADDENDUM_INPUT]
            expected_sources[run.ROOT / "addenda" / "oracle_v1.jsonl"] = run.EXPECTED[run.ROOT / "addenda" / "oracle_v1.jsonl"]
            expected_sources[run.ROOT / "addenda" / "PROTOCOL_ADDENDUM_V1.md"] = "fc6aef5f5a632ef0a97383cf4c7547c94a30a3b5603bfe64486d765f6d2e1fce"
        else:
            expected_sources[run.INTERRUPT_WRAPPER] = run.EXPECTED[run.INTERRUPT_WRAPPER]
            expected_sources[run.INTERRUPT_INPUT] = run.EXPECTED[run.INTERRUPT_INPUT]
        require(all(source_hashes.get(str(path.resolve())) == digest for path, digest in expected_sources.items()),
                f"captured control source/input mismatch: {row['case_id']}")
        label = capture_manifest["label"]
        if row["kind"] == "invalid_input":
            require(capture_result["execution_status"] == "program_error" and capture_result["exit_code"] == 2,
                    f"invalid CLI exit contract mismatch: {row['case_id']}")
            require(payload.get("status") == "invalid_input" and payload.get("complete") is True,
                    f"invalid input accepted by provider: {row['case_id']}")
            require("partition_count" not in payload and payload.get("pair_relations") is None
                    and payload.get("representative") is None, f"invalid input produced exact claim: {row['case_id']}")
            require(label == f"invalid-input-{row['case_id']}", f"invalid control label mismatch: {row['case_id']}")
        elif row["kind"] == "expired_deadline":
            require(capture_result["execution_status"] == "program_error" and capture_result["exit_code"] == 3,
                    "deadline CLI exit contract mismatch")
            require(payload.get("status") == "unknown" and payload.get("complete") is False,
                    "expired deadline did not return unknown")
            require(payload.get("partition_count") is None and payload.get("pair_relations") is None
                    and payload.get("representative") is None and payload.get("enumerated_partitions") is None,
                    "expired deadline returned an exact claim")
            require(label == "expired-cooperative-deadline-v1", "deadline capture label mismatch")
        else:
            require(row["kind"] == "interruption_after_partial_work", f"unknown control kind: {row['kind']}")
            result = payload["result"]
            require(capture_result["execution_status"] == "success" and capture_result["exit_code"] == 0,
                    "interruption wrapper failed")
            require(payload["interrupt_triggered"] is True and payload["projection_calls_completed_before_interrupt"] == 3,
                    "interrupt was not injected after three completed projections")
            require(result.get("status") == "unknown" and result.get("complete") is False,
                    "interruption did not produce unknown")
            require(result.get("partition_count") is None and result.get("pair_relations") is None
                    and result.get("representative") is None and result.get("enumerated_partitions") is None,
                    "interruption returned exact ownership claims")
            require(result["metrics"]["block_masks_precomputed"] >= 1,
                    "interruption occurred before confirmed partial provider work")
            require(label == "interrupt-after-three-projections-v1", "interrupt capture label mismatch")
        checks.append({"case_id": row["case_id"], "kind": row["kind"], "attempt_id": row["attempt_id"], "accepted": True})
    report = {
        "schema_version": 1,
        "status": "accepted_independent_controls_audit",
        "controls_replayed": len(checks),
        "invalid_controls": len(invalid_rows),
        "deadline_controls": sum(row["kind"] == "expired_deadline" for row in ledger),
        "partial_interrupt_controls": sum(row["kind"] == "interruption_after_partial_work" for row in ledger),
        "child_stream_and_contract_checks": checks,
        "ledger_sha256": sha(run.LEDGER.read_bytes()),
        "summary_sha256": sha(run.SUMMARY.read_bytes()),
        "preflight_sha256": sha((ROOT / "controls_preflight_v1.json").read_bytes()),
        "provider_cli_sha256": sha(run.CLI),
        "provider_solver_sha256": sha(run.SOLVER),
    }
    with REPORT.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

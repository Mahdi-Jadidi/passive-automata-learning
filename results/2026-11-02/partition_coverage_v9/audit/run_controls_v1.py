#!/usr/bin/env python3
"""Capture invalid-input, expired-deadline, and deterministic interrupt controls."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import capture


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
CORPUS = ROOT / "corpus_v1"
CORPUS_MANIFEST = CORPUS / "manifest.json"
INVALID_MANIFEST = CORPUS / "invalid_cases.jsonl"
ADDENDUM_INPUT = ROOT / "addenda" / "feasible_count_not_unique_ownership_v1.json"
INTERRUPT_INPUT = ROOT / "controls" / "interruption_input_v1.json"
CONTROLS_PROTOCOL = ROOT / "CONTROLS_PROTOCOL_V1.md"
INTERRUPT_WRAPPER = ROOT / "interrupt_api_wrapper_v1.py"
CONTRACT = ROOT.parent / "coordination" / "CONTRACT.md"
IMPLEMENTATION = WORKSPACE / "results/2026-11-02/partition_coverage_v9/implementation"
CLI = IMPLEMENTATION / "ownership_cli_v1.py"
SOLVER = IMPLEMENTATION / "ownership_solver_v1.py"
API_PROTOCOL = IMPLEMENTATION / "API_PROTOCOL_V1.md"
READINESS = IMPLEMENTATION / "READINESS_V1.json"
LEDGER = ROOT / "controls_ledger_v1.jsonl"
SUMMARY = ROOT / "controls_run_v1.json"

EXPECTED = {
    CLI: "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507",
    SOLVER: "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7",
    API_PROTOCOL: "111226b52eef31fd67dc599082e10ca53ae941f4527e8db48063809a85fd761b",
    READINESS: "e0c362047b3c63a1a0e25be52396357a900add60e37dde91c025a3c8fa2d0087",
    CONTRACT: "c3f5fddc4e8356e57c01870648234cfbb02a0a6e893bd78484661df7426b1521",
    INTERRUPT_INPUT: "68e9e9cb3e62f583a6ea58bcc76035742df5dc297c4b72fbbd9e164b0874b6d8",
    CORPUS_MANIFEST: "bd4c76b389d87887504f624248940d9bb1d65d69542bca4c01da0714f5200fa1",
    INVALID_MANIFEST: "ece2a61a5e3dd56dd84c318a147f7641f39aa8a3669b717fb0d1d035d2519555",
    ADDENDUM_INPUT: "cc7fb05a6069f10dc4f36e8f9b1c80a81bb2f2d616f7153a687589cfcf93c0f1",
    ROOT / "addenda" / "oracle_v1.jsonl": "3b92eee5de17a24df27dfd3c19ca3666d9e328818ec09fb1eb1fe80ede1be9f3",
    CONTROLS_PROTOCOL: "e76c7dec7f9e05b05a91ecca3aca363c4dbabd03c8cffc3a0b146c94786dba01",
    INTERRUPT_WRAPPER: "a61ad3cfa861097fc5ab1965eaabc2c485a9bb2893b7e7a9c0808ebf2729f38d",
    ROOT / "capture.py": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_capture(record: dict) -> dict | None:
    try:
        return json.loads((Path(record["attempt_dir"]) / "stdout.bin").read_bytes())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def main() -> int:
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen control source/input hash mismatch: {path}")
    for path in (LEDGER, SUMMARY):
        if path.exists():
            raise SystemExit(f"refusing to overwrite control run: {path}")
    manifest = json.loads(CORPUS_MANIFEST.read_text(encoding="utf-8"))
    invalid_rows = [json.loads(line) for line in INVALID_MANIFEST.read_text(encoding="utf-8").splitlines()]
    ledger_rows = []
    status = "accepted_controls"

    def run_one(label: str, command: list[str], sources: list[Path]) -> tuple[dict, dict | None]:
        record = capture.capture(label, command, cwd=WORKSPACE, timeout_seconds=25.0, source_paths=sources)
        return record, parse_capture(record)

    python = sys.executable
    common = [CLI, SOLVER, API_PROTOCOL, READINESS, CORPUS_MANIFEST, CONTROLS_PROTOCOL, CONTRACT]
    for invalid in invalid_rows:
        input_path = CORPUS / invalid["path"]
        if sha(input_path) != invalid["input_sha256"]:
            status = "stopped_invalid_control_input_hash_mismatch"
            break
        record, payload = run_one(
            f"invalid-input-{invalid['case_id']}",
            [python, "-B", "-X", "utf8", str(CLI), str(input_path)],
            common + [INVALID_MANIFEST, input_path],
        )
        ok = (record["execution_status"] == "program_error" and record["exit_code"] == 2
              and record["child_reaped"] is True and isinstance(payload, dict)
              and payload.get("status") == "invalid_input" and payload.get("complete") is True
              and "partition_count" not in payload and payload.get("pair_relations") is None
              and payload.get("representative") is None)
        ledger_rows.append({"kind": "invalid_input", "case_id": invalid["case_id"], "expected_rejection": invalid["expected_input_classification"],
                            "attempt_id": record["attempt_id"], "execution_status": record["execution_status"],
                            "exit_code": record["exit_code"], "child_reaped": record["child_reaped"],
                            "stdout_sha256": record["stdout_sha256"], "stderr_sha256": record["stderr_sha256"], "accepted": ok})
        if not ok:
            status = "stopped_invalid_input_contract_mismatch"
            break

    if status == "accepted_controls":
        record, payload = run_one(
            "expired-cooperative-deadline-v1",
            [python, "-B", "-X", "utf8", str(CLI), str(ADDENDUM_INPUT), "--seconds", "0", "--enumerate"],
            common + [ADDENDUM_INPUT, ROOT / "addenda" / "PROTOCOL_ADDENDUM_V1.md", ROOT / "addenda" / "oracle_v1.jsonl"],
        )
        ok = (record["execution_status"] == "program_error" and record["exit_code"] == 3
              and record["child_reaped"] is True and isinstance(payload, dict)
              and payload.get("status") == "unknown" and payload.get("complete") is False
              and payload.get("partition_count") is None and payload.get("pair_relations") is None
              and payload.get("representative") is None and payload.get("enumerated_partitions") is None)
        ledger_rows.append({"kind": "expired_deadline", "case_id": "feasible_count_not_unique_ownership_v1",
                            "attempt_id": record["attempt_id"], "execution_status": record["execution_status"],
                            "exit_code": record["exit_code"], "child_reaped": record["child_reaped"],
                            "provider_status": payload.get("status") if isinstance(payload, dict) else None,
                            "provider_complete": payload.get("complete") if isinstance(payload, dict) else None,
                            "stdout_sha256": record["stdout_sha256"], "stderr_sha256": record["stderr_sha256"], "accepted": ok})
        if not ok:
            status = "stopped_deadline_contract_mismatch"

    if status == "accepted_controls":
        record, payload = run_one(
            "interrupt-after-three-projections-v1",
            [python, "-B", "-X", "utf8", str(INTERRUPT_WRAPPER), str(INTERRUPT_INPUT)],
            common + [INTERRUPT_WRAPPER, INTERRUPT_INPUT],
        )
        result = payload.get("result") if isinstance(payload, dict) else None
        metrics = result.get("metrics") if isinstance(result, dict) else None
        ok = (record["execution_status"] == "success" and record["exit_code"] == 0
              and record["child_reaped"] is True and isinstance(payload, dict)
              and payload.get("interrupt_triggered") is True
              and payload.get("projection_calls_completed_before_interrupt") == 3
              and isinstance(result, dict) and result.get("status") == "unknown" and result.get("complete") is False
              and result.get("partition_count") is None and result.get("pair_relations") is None
              and result.get("representative") is None and result.get("enumerated_partitions") is None
              and isinstance(metrics, dict) and metrics.get("block_masks_precomputed", 0) >= 1)
        ledger_rows.append({"kind": "interruption_after_partial_work", "case_id": "interruption_after_three_projection_calls_v1",
                            "attempt_id": record["attempt_id"], "execution_status": record["execution_status"],
                            "exit_code": record["exit_code"], "child_reaped": record["child_reaped"],
                            "provider_status": result.get("status") if isinstance(result, dict) else None,
                            "provider_complete": result.get("complete") if isinstance(result, dict) else None,
                            "projection_calls": payload.get("projection_calls_completed_before_interrupt") if isinstance(payload, dict) else None,
                            "block_masks_precomputed": metrics.get("block_masks_precomputed") if isinstance(metrics, dict) else None,
                            "stdout_sha256": record["stdout_sha256"], "stderr_sha256": record["stderr_sha256"], "accepted": ok})
        if not ok:
            status = "stopped_interruption_contract_mismatch"

    with LEDGER.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in ledger_rows))
        handle.flush()
    summary = {
        "schema_version": 1,
        "status": status,
        "invalid_controls_planned": len(invalid_rows),
        "invalid_controls_completed": sum(row["kind"] == "invalid_input" for row in ledger_rows),
        "deadline_controls_completed": sum(row["kind"] == "expired_deadline" for row in ledger_rows),
        "interruption_controls_completed": sum(row["kind"] == "interruption_after_partial_work" for row in ledger_rows),
        "all_completed_controls_accepted": all(row["accepted"] for row in ledger_rows),
        "ledger_sha256": sha(LEDGER),
        "provider_cli_sha256": sha(CLI),
        "provider_solver_sha256": sha(SOLVER),
        "controls_protocol_sha256": sha(CONTROLS_PROTOCOL),
        "runner_sha256": sha(Path(__file__)),
    }
    with SUMMARY.open("xb") as handle:
        handle.write((json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if status == "accepted_controls" and all(row["accepted"] for row in ledger_rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

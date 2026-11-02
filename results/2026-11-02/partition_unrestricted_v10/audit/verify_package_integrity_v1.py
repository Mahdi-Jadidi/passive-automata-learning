#!/usr/bin/env python3
"""Read-only byte/source-closure audit for the completed C010 package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def verify_source_rows(source_rows: list[dict], errors: list[str], attempt: str) -> int:
    checked = 0
    for row in source_rows:
        blob = AUDIT / row["snapshot"]
        if not blob.is_file():
            errors.append(f"{attempt}: missing immutable source blob {row.get('snapshot')}")
            continue
        raw = blob.read_bytes()
        if sha(raw) != row["sha256"] or len(raw) != int(row["bytes"]):
            errors.append(f"{attempt}: source blob hash/size mismatch {row.get('path')}")
        checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-label", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    errors: list[str] = []

    ledger_path = AUDIT / "ATTEMPT_LEDGER_V2.json"
    ledger_raw = ledger_path.read_bytes()
    ledger = json.loads(ledger_raw.decode("utf-8"))
    ledger_by_id = {row["attempt_id"]: row for row in ledger["attempts"]}
    attempts_root = AUDIT / "attempts"
    current_self = None
    completed_ids = set()
    attempts_checked = 0
    source_blobs_checked = 0
    raw_streams_checked = 0
    capture_errors = []

    for attempt_dir in sorted(attempts_root.iterdir()):
        manifest_path = attempt_dir / "manifest.json"
        result_path = attempt_dir / "result.json"
        if not manifest_path.exists():
            errors.append(f"attempt folder missing manifest: {attempt_dir.name}")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("label") == args.current_label and not result_path.exists():
            current_self = {
                "attempt_id": manifest.get("attempt_id"), "label": args.current_label,
                "manifest_sha256": sha(manifest_path.read_bytes()),
                "source_count": len(manifest.get("sources", [])),
            }
            source_blobs_checked += verify_source_rows(manifest.get("sources", []), errors, attempt_dir.name + "/self")
            if manifest.get("source_snapshot_error") is not None:
                errors.append("integrity capture itself has source snapshot error")
            continue
        if not result_path.exists():
            errors.append(f"completed research attempt has no result: {attempt_dir.name}")
            continue
        result_raw = result_path.read_bytes()
        result = json.loads(result_raw.decode("utf-8"))
        stdout_path, stderr_path = attempt_dir / "stdout.bin", attempt_dir / "stderr.bin"
        if not stdout_path.is_file() or not stderr_path.is_file():
            errors.append(f"attempt missing raw stream file: {attempt_dir.name}")
            continue
        stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
        if result.get("attempt_id") != manifest.get("attempt_id") or result.get("attempt_id") != attempt_dir.name:
            errors.append(f"attempt identity mismatch: {attempt_dir.name}")
        if result.get("label") != manifest.get("label"):
            errors.append(f"attempt label mismatch: {attempt_dir.name}")
        if len(stdout) != result.get("stdout_bytes") or sha(stdout) != result.get("stdout_sha256"):
            errors.append(f"stdout raw hash/size mismatch: {attempt_dir.name}")
        if len(stderr) != result.get("stderr_bytes") or sha(stderr) != result.get("stderr_sha256"):
            errors.append(f"stderr raw hash/size mismatch: {attempt_dir.name}")
        if result.get("child_pid") is not None and result.get("child_reaped") is not True:
            errors.append(f"child is not confirmed reaped: {attempt_dir.name}")
        if manifest.get("source_snapshot_error") is None:
            source_blobs_checked += verify_source_rows(manifest.get("sources", []), errors, attempt_dir.name)
        else:
            capture_errors.append({"attempt_id": result.get("attempt_id"),
                                   "label": result.get("label"),
                                   "source_snapshot_error": manifest["source_snapshot_error"],
                                   "child_pid": result.get("child_pid")})
            if result.get("child_pid") is not None:
                errors.append(f"source-snapshot error occurred after child start: {attempt_dir.name}")
        ledger_row = ledger_by_id.get(result["attempt_id"])
        if ledger_row is None:
            errors.append(f"attempt absent from frozen ledger: {attempt_dir.name}")
        else:
            if ledger_row.get("result_sha256") != sha(result_raw):
                errors.append(f"ledger result hash mismatch: {attempt_dir.name}")
            if ledger_row.get("manifest_sha256") != sha(manifest_path.read_bytes()):
                errors.append(f"ledger manifest hash mismatch: {attempt_dir.name}")
            if ledger_row.get("stdout_sha256") != sha(stdout) or ledger_row.get("stderr_sha256") != sha(stderr):
                errors.append(f"ledger raw stream hash mismatch: {attempt_dir.name}")
            if ledger_row.get("sources") != manifest.get("sources", []):
                errors.append(f"ledger source list differs from attempt manifest: {attempt_dir.name}")
        attempts_checked += 1
        raw_streams_checked += 2
        completed_ids.add(result["attempt_id"])

    if current_self is None:
        errors.append("current integrity capture label not found or already has a result")
    if completed_ids != set(ledger_by_id):
        errors.append(f"attempt/ledger ID set mismatch: observed {len(completed_ids)}, ledger {len(ledger_by_id)}")
    if attempts_checked != ledger.get("attempt_count"):
        errors.append("attempt count differs from ATTEMPT_LEDGER_V2")

    # Recheck every frozen corpus input and all summary/acceptance reports.
    corpus_manifest_raw = (AUDIT / "corpus_v1" / "manifest.json").read_bytes()
    corpus_manifest = json.loads(corpus_manifest_raw.decode("utf-8"))
    corpus_files_checked = 0
    for item in corpus_manifest["files"]:
        raw = (AUDIT / "corpus_v1" / item["path"]).read_bytes()
        if len(raw) != item["bytes"] or sha(raw) != item["sha256"]:
            errors.append(f"frozen C009-derived corpus file mismatch: {item['path']}")
        corpus_files_checked += 1
    for row in corpus_manifest["valid_cases"]:
        raw = (AUDIT / "corpus_v1" / row["path"]).read_bytes()
        if sha(raw) != row["sha256"]:
            errors.append(f"frozen valid input mismatch: {row['case_id']}")
        corpus_files_checked += 1
    for row in json.loads((AUDIT / "scale_v1" / "manifest.json").read_text(encoding="utf-8"))["cells"]:
        raw = (AUDIT / "scale_v1" / row["input"]["path"]).read_bytes()
        if len(raw) != row["input"]["bytes"] or sha(raw) != row["input"]["sha256"]:
            errors.append(f"scale input mismatch: {row['case_id']}")
        corpus_files_checked += 1

    readiness = json.loads((ROOT / "implementation" / "READINESS_V3.json").read_text(encoding="utf-8"))
    runtime_files_checked = 0
    for name, row in readiness["files"].items():
        raw = (ROOT / "implementation" / name).read_bytes()
        if len(raw) != row["bytes"] or sha(raw) != row["sha256"]:
            errors.append(f"implementation readiness hash mismatch: {name}")
        runtime_files_checked += 1
    reports = {
        "audit/oracle_validation_v1.json": "accepted_independent_unrestricted_oracle",
        "audit/provider_validation_v2.json": "accepted_exact_full_set_gate",
        "audit/provider_controls_validation_v2.json": "accepted_invalid_deadline_interrupt_controls",
        "audit/cli_smoke_validation_v2.json": "accepted_cli_smoke",
        "audit/scale_v1/oracle_validation_v1.json": "accepted_independent_scale_oracle",
        "audit/scale_v1/preflight_v1.json": "ready_for_exactly_four_one_run_scale_cells",
        "audit/scale_v1/provider_validation_v1.json": "accepted_four_complete_scale_cells",
    }
    report_hashes = {}
    for path, status in reports.items():
        p = ROOT / path
        raw = p.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        if payload.get("status") != status:
            errors.append(f"acceptance report status mismatch: {path}")
        report_hashes[path] = sha(raw)
    final_report_raw = (AUDIT / "AUDIT_FINAL_V1.md").read_bytes()
    summary_raw = (AUDIT / "FINAL_SUMMARY_V1.json").read_bytes()
    summary = json.loads(summary_raw.decode("utf-8"))
    if summary.get("status") != "accepted_bounded_correctness_no_performance_claim":
        errors.append("final machine summary status mismatch")
    if summary.get("attempt_ledger", {}).get("sha256") != sha(ledger_raw):
        errors.append("machine summary does not anchor the frozen attempt ledger")
    if not final_report_raw:
        errors.append("final Persian report is empty")

    # Explicit failure classes remain evidence; none is silently replaced.
    required_failures = {
        "unrestricted_provider_full_set_gate_v1": "capture_error",
        "c010_scale_corpus_generation_v1": "program_error",
        "c010_independent_scale_oracle_v1": "program_error",
    }
    for label, status in required_failures.items():
        matches = [row for row in ledger["attempts"] if row.get("label") == label]
        if len(matches) != 1 or matches[0].get("execution_status") != status:
            errors.append(f"required preserved failed attempt missing/changed: {label}")
    v1_attempt = next((row for row in ledger["attempts"] if row.get("label") == "unrestricted_provider_full_set_gate_v1"), {})
    if v1_attempt.get("child_pid") is not None:
        errors.append("v1 provider should not have started")

    status = "passed" if not errors else "failed"
    report = {
        "schema_version": 1,
        "status": status,
        "scope": "all completed research/audit captures before this closure capture; current capture source snapshots are verified separately",
        "integrity_capture": current_self,
        "research_attempts_checked": attempts_checked,
        "capture_errors_preserved": capture_errors,
        "raw_stream_files_hash_checked": raw_streams_checked,
        "immutable_source_blobs_checked": source_blobs_checked,
        "frozen_input_files_checked": corpus_files_checked,
        "provider_readiness_files_checked": runtime_files_checked,
        "acceptance_report_hashes": report_hashes,
        "final_report_sha256": sha(final_report_raw),
        "machine_summary_sha256": sha(summary_raw),
        "attempt_ledger_sha256": sha(ledger_raw),
        "errors": errors,
    }
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

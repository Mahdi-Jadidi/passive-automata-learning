#!/usr/bin/env python3
"""Check captured no-K invalid/deadline/interruption control responses."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider_stdout", type=Path)
    parser.add_argument("capture_result", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    cap = json.loads(args.capture_result.read_text(encoding="utf-8"))
    raw = args.provider_stdout.read_bytes()
    errors = []
    if cap.get("execution_status") != "success" or cap.get("exit_code") != 0 or cap.get("child_reaped") is not True:
        errors.append("capture status/exit/reap invalid")
    if cap.get("stdout_sha256") != sha(raw) or cap.get("stdout_bytes") != len(raw):
        errors.append("stdout capture hash/size mismatch")
    try:
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    except Exception as exc:
        rows = []
        errors.append(f"stdout is not valid UTF-8 JSONL: {exc!r}")
    by_id = {row.get("case_id"): row for row in rows}
    wanted_ids = {"stale_allowed_k", "stale_legacy_k", "empty_alphabet",
                  "duplicate_alphabet_symbol", "conflicting_labels",
                  "word_outside_alphabet", "already_expired_deadline",
                  "synthetic_keyboard_interrupt_at_extraction_guard"}
    if len(rows) != len(wanted_ids) or set(by_id) != wanted_ids:
        errors.append("control ID set is not exactly six invalid plus deadline plus interruption")
    invalid_ids = sorted(wanted_ids - {"already_expired_deadline", "synthetic_keyboard_interrupt_at_extraction_guard"})
    for case_id in invalid_ids:
        row = by_id.get(case_id, {})
        result = row.get("result", {})
        if row.get("kind") != "invalid_input" or result.get("status") != "invalid_input" or result.get("complete") is not True:
            errors.append(f"invalid control not rejected: {case_id}")
    for case_id in ("already_expired_deadline", "synthetic_keyboard_interrupt_at_extraction_guard"):
        row = by_id.get(case_id, {})
        result = row.get("result", {})
        if row.get("kind") not in ("expired_deadline", "guarded_interrupt"):
            errors.append(f"wrong control kind: {case_id}")
        if result.get("status") != "unknown" or result.get("complete") is not False:
            errors.append(f"control returned final status: {case_id}")
        for field in ("partition_count", "partition_count_by_k", "pair_relations",
                      "representative", "enumerated_partitions"):
            if result.get(field) is not None:
                errors.append(f"incomplete control retained final field {field}: {case_id}")
    report = {
        "schema_version": 1,
        "status": "accepted_invalid_deadline_interrupt_controls" if not errors else "rejected_controls",
        "capture_attempt_id": cap.get("attempt_id"),
        "capture_execution_status": cap.get("execution_status"),
        "invalid_controls_expected": len(invalid_ids),
        "invalid_controls_rejected": sum(by_id.get(case_id, {}).get("result", {}).get("status") == "invalid_input" for case_id in invalid_ids),
        "deadline_control_incomplete_no_finality": by_id.get("already_expired_deadline", {}).get("result", {}).get("status") == "unknown" and by_id.get("already_expired_deadline", {}).get("result", {}).get("complete") is False,
        "guarded_interrupt_incomplete_no_finality": by_id.get("synthetic_keyboard_interrupt_at_extraction_guard", {}).get("result", {}).get("status") == "unknown" and by_id.get("synthetic_keyboard_interrupt_at_extraction_guard", {}).get("result", {}).get("complete") is False,
        "control_rows": len(rows),
        "errors": errors,
        "stdout_sha256": sha(raw),
        "stdout_bytes": len(raw),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check captured invalid/deadline/interruption outputs without solver code."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_provider_controls_v1.py CAPTURED_STDOUT REPORT")
    captured, report_path = map(Path, sys.argv[1:])
    rows = [json.loads(line) for line in captured.read_text(encoding="utf-8").splitlines() if line]
    summary = rows[-1]
    controls = rows[:-1]
    failures = []
    invalid = [row for row in controls if row["control"] == "invalid_input"]
    if len(invalid) != 6:
        failures.append("expected_six_invalid_mode_runs")
    for row in invalid:
        if row["result"].get("status") != "invalid_input" or row["result"].get("complete") is not True:
            failures.append("invalid_input_not_rejected:" + row["case_id"] + ":" + str(row.get("mode")))
    expected = {
        "ctrl_expired_deadline": ("incomplete", 0),
        "ctrl_cheap_path_cooperative_stop": ("incomplete", 0),
        "ctrl_post_separator_stop": ("incomplete", 1),
        "ctrl_interrupt_after_partial_separator": ("incomplete", 1),
    }
    for row in controls:
        if row["control"] not in expected:
            continue
        status, history_count = expected[row["control"]]
        result = row.get("result") or {}
        history = result.get("successful_separators", [])
        if result.get("status") != status or result.get("complete") is not False:
            failures.append("control_not_incomplete:" + row["control"])
        if result.get("decision_complete") is not False or result.get("finality_certificate") is not None:
            failures.append("incomplete_control_has_finality_claim:" + row["control"])
        if len(history) != history_count:
            failures.append("unexpected_partial_history:" + row["control"])
        if row["control"] == "ctrl_expired_deadline" and result.get("reason") not in (
                "deadline_or_interruption", "reference_truncated"):
            failures.append("expired_deadline_reason_mismatch")
        if row["control"] == "ctrl_cheap_path_cooperative_stop" and row.get("injected_check_calls") != 2:
            failures.append("cheap_path_stop_injection_boundary_mismatch")
        if row["control"] in ("ctrl_post_separator_stop", "ctrl_interrupt_after_partial_separator"):
            if row.get("injected_direct_calls") != 4:
                failures.append("post_separator_injection_boundary_mismatch:" + row["control"])
            if not result.get("partial_meet"):
                failures.append("partial_meet_not_retained:" + row["control"])
    if summary.get("errors") != 0 or summary.get("invalid_inputs") != 3:
        failures.append("control_runner_summary_mismatch")
    report = {
        "schema_version": 1,
        "status": "accepted" if not failures else "rejected",
        "invalid_mode_runs": len(invalid),
        "expired_deadline": "incomplete; no finality",
        "cheap_path_stop": "incomplete; no finality",
        "post_separator_stop": "incomplete with one retained separator; no finality",
        "injected_keyboardinterrupt": "incomplete with one retained separator; no finality",
        "capture_attempt_id": captured.parent.name,
        "captured_stdout_sha256": hashlib.sha256(captured.read_bytes()).hexdigest(),
        "failures": failures,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze-check the provider gate without launching a provider process."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import run_provider_gate_v1 as gate


REPORT_PATH = gate.ROOT / "provider_gate_preflight_v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = []
    for path, expected in gate.EXPECTED.items():
        actual = sha(path)
        checks.append({"check": f"frozen:{path.name}", "ok": actual == expected, "sha256": actual})
    expected_capture = "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf"
    checks.append({"check": "capture_helper", "ok": sha(gate.ROOT / "capture.py") == expected_capture,
                   "sha256": sha(gate.ROOT / "capture.py")})
    source = gate.Path(__file__).read_text(encoding="utf-8")
    ast.parse(source)
    ast.parse(gate.Path(gate.__file__).read_text(encoding="utf-8"))
    checks.append({"check": "python_syntax", "ok": True})
    manifest = json.loads(gate.MANIFEST_PATH.read_text(encoding="utf-8"))
    oracle = [json.loads(line) for line in gate.ORACLE_PATH.read_text(encoding="utf-8").splitlines()]
    checks.append({"check": "exact_129_case_order", "ok": len(manifest["valid_cases"]) == 129
                   and [row["case_id"] for row in manifest["valid_cases"]] == [row["case_id"] for row in oracle]})
    by_id = {row["case_id"]: row for row in oracle}
    for case in manifest["valid_cases"]:
        raw = (gate.CORPUS / case["path"]).read_bytes()
        checks.append({"check": f"input:{case['case_id']}", "ok": sha(gate.CORPUS / case["path"]) == case["input_sha256"]
                       and case["case_id"] in by_id})
    prior_labels = []
    attempts_dir = gate.ROOT / "attempts"
    if attempts_dir.exists():
        for attempt_dir in attempts_dir.iterdir():
            manifest_path = attempt_dir / "manifest.json"
            if manifest_path.exists():
                attempt_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if str(attempt_manifest.get("label", "")).startswith("provider-full-enumeration-"):
                    prior_labels.append(attempt_manifest["label"])
    checks.append({"check": "no_prior_gate_run", "ok": not gate.LEDGER_PATH.exists() and not gate.SUMMARY_PATH.exists()
                   and not prior_labels, "prior_labels": prior_labels})
    failed = [check for check in checks if not check["ok"]]
    report = {
        "schema_version": 1,
        "status": "frozen_preflight_passed" if not failed else "preflight_failed",
        "provider_jobs": 0,
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
        "gate_protocol_sha256": sha(gate.GATE_PROTOCOL_PATH),
        "protocol_amendment_sha256": sha(gate.AMENDMENT_PATH),
        "runner_sha256": sha(gate.Path(gate.__file__)),
        "preflight_source_sha256": sha(gate.Path(__file__)),
    }
    with REPORT_PATH.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

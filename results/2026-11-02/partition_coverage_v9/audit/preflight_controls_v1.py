#!/usr/bin/env python3
"""Check control protocol/source/input freeze before any control provider calls."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import run_controls_v1 as controls


REPORT = controls.ROOT / "controls_preflight_v1.json"


def main() -> int:
    checks = []
    for path, expected in controls.EXPECTED.items():
        actual = controls.sha(path)
        checks.append({"check": f"frozen:{path.name}", "ok": actual == expected, "sha256": actual})
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    ast.parse(Path(controls.__file__).read_text(encoding="utf-8"))
    ast.parse(controls.INTERRUPT_WRAPPER.read_text(encoding="utf-8"))
    checks.append({"check": "python_syntax", "ok": True})
    invalid_rows = [json.loads(line) for line in controls.INVALID_MANIFEST.read_text(encoding="utf-8").splitlines()]
    checks.append({"check": "seven_invalid_cases", "ok": len(invalid_rows) == 7})
    data = json.loads(controls.INTERRUPT_INPUT.read_text(encoding="utf-8"))
    lengths = [len(word) for word in data["positive"] + data["negative"]]
    checks.append({"check": "long_interruption_input", "ok": data["alphabet"] == list("abcdefgh") and lengths == [4096, 4096]})
    checks.append({"check": "no_prior_control_outputs", "ok": not controls.LEDGER.exists() and not controls.SUMMARY.exists() and not REPORT.exists()})
    failed = [row for row in checks if not row["ok"]]
    report = {
        "schema_version": 1,
        "status": "frozen_control_preflight_passed" if not failed else "preflight_failed",
        "provider_jobs": 0,
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
        "control_protocol_sha256": controls.sha(controls.CONTROLS_PROTOCOL),
        "control_runner_sha256": controls.sha(Path(controls.__file__)),
        "interrupt_wrapper_sha256": controls.sha(controls.INTERRUPT_WRAPPER),
        "preflight_sha256": controls.sha(Path(__file__)),
    }
    with REPORT.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

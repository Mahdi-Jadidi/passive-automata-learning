#!/usr/bin/env python3
"""Check the frozen scale corpus and all-oracle answer before provider execution."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import run_scale_provider_v1 as run


REPORT = run.ROOT / "scale_preflight_v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = []
    for path, expected in run.EXPECTED.items():
        checks.append({"check": f"frozen:{path.name}", "ok": sha(path) == expected, "sha256": sha(path)})
    checks.append({"check": "capture_helper", "ok": sha(run.ROOT / "capture.py") == "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf"})
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    ast.parse(Path(run.__file__).read_text(encoding="utf-8"))
    checks.append({"check": "python_syntax", "ok": True})
    manifest = json.loads(run.MANIFEST.read_text(encoding="utf-8"))
    oracle = [json.loads(line) for line in run.ORACLE.read_text(encoding="utf-8").splitlines()]
    counts = {row["case_id"]: row["partition_count"] for row in oracle}
    expected = {"pair_atoms_m10_k2_4": 25, "pair_atoms_m12_k3_5": 105,
                "pair_atoms_m14_k2_4": 413, "long_word_m4_len4096_k2": 3}
    checks.append({"check": "four_exact_scale_answers", "ok": counts == expected and len(manifest["cases"]) == 4,
                   "partition_counts": counts})
    for case in manifest["cases"]:
        path = run.SCALE_DIR / case["path"]
        checks.append({"check": f"input:{case['case_id']}", "ok": sha(path) == case["input_sha256"]})
        oracle_row = next(row for row in oracle if row["case_id"] == case["case_id"])
        checks.append({"check": f"oracle:{case['case_id']}", "ok": oracle_row["complete"] is True
                       and oracle_row["partition_count"] == case["expected_partition_count"]})
    checks.append({"check": "prerequisites_accepted", "ok":
                   json.loads(run.GATE_REPORT.read_text(encoding="utf-8"))["status"] == "accepted_independent_provider_gate"
                   and json.loads(run.CONTROLS_REPORT.read_text(encoding="utf-8"))["status"] == "accepted_independent_controls_audit"
                   and json.loads(run.WRAPPER_REPORT.read_text(encoding="utf-8"))["status"] == "accepted_root_wrapper_control"})
    checks.append({"check": "no_prior_scale_provider_run", "ok": not run.LEDGER.exists() and not run.SUMMARY.exists()})
    failed = [row for row in checks if not row["ok"]]
    report = {
        "schema_version": 1,
        "status": "scale_preflight_passed" if not failed else "preflight_failed",
        "provider_jobs": 0,
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
        "protocol_sha256": sha(run.PROTOCOL),
        "manifest_sha256": sha(run.MANIFEST),
        "oracle_sha256": sha(run.ORACLE),
        "runner_sha256": sha(Path(run.__file__)),
        "preflight_sha256": sha(Path(__file__)),
    }
    with REPORT.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

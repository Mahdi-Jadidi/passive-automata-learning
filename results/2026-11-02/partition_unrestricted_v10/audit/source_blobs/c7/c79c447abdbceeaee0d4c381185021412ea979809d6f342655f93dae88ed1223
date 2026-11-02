#!/usr/bin/env python3
"""Validate one captured v2 CLI full-enumeration smoke independently."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
from validate_provider_v2 import check_witness, direct_expected, partition_rgs  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider_stdout", type=Path)
    parser.add_argument("capture_result", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    capture = json.loads(args.capture_result.read_text(encoding="utf-8"))
    raw = args.provider_stdout.read_bytes()
    input_raw = args.input.read_bytes()
    data = json.loads(input_raw.decode("utf-8"))
    errors = []
    if capture.get("execution_status") != "success" or capture.get("exit_code") != 0 or capture.get("child_reaped") is not True:
        errors.append("CLI capture status/exit/reap invalid")
    if capture.get("stdout_sha256") != sha(raw) or capture.get("stdout_bytes") != len(raw):
        errors.append("CLI stdout hash/size mismatch")
    try:
        result = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        result = {}
        errors.append(f"CLI stdout is not a single JSON document: {exc!r}")
    expected = direct_expected(data)
    wanted_spectrum = {str(k): sum(1 for rgs in expected if max(rgs) + 1 == k)
                       for k in range(1, len(data["alphabet"]) + 1)}
    if result.get("complete") is not True or result.get("partition_count") != 5:
        errors.append("CLI result is not complete with five answers")
    if result.get("partition_count_by_k") != wanted_spectrum or wanted_spectrum != {"1": 1, "2": 3, "3": 1}:
        errors.append("CLI exact-k spectrum mismatch")
    family = result.get("enumerated_partitions")
    observed = set()
    if not isinstance(family, list):
        errors.append("CLI did not return full enumeration")
    else:
        try:
            for witness in family:
                check_witness(data, witness)
            observed = {partition_rgs(row["partition"], data["alphabet"]) for row in family}
        except Exception as exc:
            errors.append(f"CLI partition list malformed: {exc!r}")
    if observed != expected or len(family or []) != len(expected):
        errors.append("CLI exact family differs from direct set-insertion oracle")
    try:
        check_witness(data, result.get("representative"))
    except Exception as exc:
        errors.append(f"CLI representative witness does not replay: {exc!r}")
    report = {
        "schema_version": 1,
        "status": "accepted_cli_smoke" if not errors else "rejected_cli_smoke",
        "capture_attempt_id": capture.get("attempt_id"),
        "capture_execution_status": capture.get("execution_status"),
        "input_sha256": sha(input_raw),
        "provider_stdout_sha256": sha(raw),
        "exact_partitions_expected": len(expected),
        "exact_partitions_observed": len(observed),
        "spectrum": result.get("partition_count_by_k"),
        "errors": errors,
    }
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

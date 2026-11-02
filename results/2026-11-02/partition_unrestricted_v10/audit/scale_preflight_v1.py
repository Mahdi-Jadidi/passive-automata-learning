#!/usr/bin/env python3
"""Read-only freeze check immediately before four one-run scale cells."""
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scale_oracle_stdout", type=Path)
    parser.add_argument("scale_oracle_result", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    errors = []
    manifest_raw = (AUDIT / "scale_v1" / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    protocol = (AUDIT / "PROTOCOL_SCALE_V1.md").read_text(encoding="utf-8")
    if sha(manifest_raw) != "cd140f1e2d3b3976febd5c277c7aa3a045f94d658c9f5674084f2abd2f1eba2f":
        errors.append("scale manifest differs from protocol anchor")
    if "Bell(64)" not in protocol or "once" not in protocol:
        errors.append("scale protocol lost no-Bell64 or no-rerun constraint")
    input_count = 0
    for case in manifest["cells"]:
        path = AUDIT / "scale_v1" / case["input"]["path"]
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
        if sha(raw) != case["input"]["sha256"] or len(raw) != case["input"]["bytes"]:
            errors.append(f"input bytes/hash mismatch: {case['case_id']}")
        if sha(canonical(data)) != case["input"]["canonical_payload_sha256"]:
            errors.append(f"canonical input hash mismatch: {case['case_id']}")
        if len(data["alphabet"]) != case["input"]["alphabet_size"]:
            errors.append(f"alphabet-size mismatch: {case['case_id']}")
        if "k" in data or "allowed_k" in data:
            errors.append(f"external K found: {case['case_id']}")
        input_count += 1
    readiness = json.loads((ROOT / "implementation" / "READINESS_V3.json").read_text(encoding="utf-8"))
    for name, row in readiness["files"].items():
        p = ROOT / "implementation" / name
        if not p.exists() or sha(p.read_bytes()) != row["sha256"] or p.stat().st_size != row["bytes"]:
            errors.append(f"provider readiness mismatch: {name}")
    wrapper_sha = sha((ROOT / "solve.py").read_bytes())
    if wrapper_sha != "533bcbffe39fa18648567abcaeb1fd775d75d05561f42be007c03c849f41a989":
        errors.append("root solve.py wrapper changed after preregistration")

    oracle_raw = args.scale_oracle_stdout.read_bytes()
    oracle_result = json.loads(args.scale_oracle_result.read_text(encoding="utf-8"))
    oracle_validation = json.loads((AUDIT / "scale_v1" / "oracle_validation_v1.json").read_text(encoding="utf-8"))
    if oracle_result.get("execution_status") != "success" or oracle_result.get("child_reaped") is not True:
        errors.append("scale oracle capture not successful/reaped")
    if oracle_result.get("stdout_sha256") != sha(oracle_raw):
        errors.append("scale oracle capture stdout hash mismatch")
    if oracle_validation.get("status") != "accepted_independent_scale_oracle" or oracle_validation.get("oracle_stdout_sha256") != sha(oracle_raw):
        errors.append("independent scale oracle validation mismatch")
    oracle = json.loads(oracle_raw.decode("utf-8"))
    if oracle.get("scale_manifest_sha256") != sha(manifest_raw) or len(oracle.get("cells", [])) != 4:
        errors.append("scale oracle not anchored to frozen four-cell manifest")
    by_id = {row["case_id"]: row for row in oracle.get("cells", [])}
    for case in manifest["cells"]:
        row = by_id.get(case["case_id"], {})
        if row.get("compatible_partition_count") != case["expected_count"]:
            errors.append(f"oracle count differs from preregistration: {case['case_id']}")
        if row.get("compatible_partition_count_by_k") != case["expected_spectrum"]:
            errors.append(f"oracle spectrum differs from preregistration: {case['case_id']}")
    m64 = by_id.get("m64_eight_connected_groups", {})
    if m64.get("symbol_partitions_enumerated") != 0 or m64.get("atom_or_semantic_partitions_enumerated") != 4140:
        errors.append("m64 oracle did not use exactly Bell(8) quotient domain")

    existing_cells = []
    for attempt in (AUDIT / "attempts").iterdir():
        result_path = attempt / "result.json"
        if not result_path.exists():
            continue
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("label", "").startswith("c010_scale_rootcli_"):
            existing_cells.append(result["label"])
    if existing_cells:
        errors.append(f"scale provider cells already exist; prevent duplicate run: {existing_cells}")

    report = {
        "schema_version": 1,
        "status": "ready_for_exactly_four_one_run_scale_cells" if not errors else "blocked_preflight",
        "scale_manifest_sha256": sha(manifest_raw),
        "scale_oracle_stdout_sha256": sha(oracle_raw),
        "input_files_hash_checked": input_count,
        "provider_readiness_files_checked": len(readiness["files"]),
        "root_wrapper_sha256": wrapper_sha,
        "prior_provider_scale_cells": existing_cells,
        "errors": errors,
    }
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

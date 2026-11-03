#!/usr/bin/env python3
"""Versioned C011 oracle audit fixing the V2 fallback-case lookup."""
from __future__ import annotations

import json
from pathlib import Path
import oracle_audit_v2 as base

AUDIT = Path(__file__).resolve().parent


def main() -> int:
    correctness = json.loads((AUDIT / "CORRECTNESS_MANIFEST_V2.json").read_text(encoding="utf-8"))
    base_rows = [row for row in correctness["cases"] if row["expected_source"] == "c010_direct_rgs_v1"]
    base_oracle_path = AUDIT / "c010_oracle_v1.jsonl"
    base_oracle = [json.loads(line) for line in base_oracle_path.read_text(encoding="utf-8").splitlines()]
    if len(base_oracle) != len(base_rows) or {r["case_id"] for r in base_oracle} != {r["case_id"] for r in base_rows}:
        raise AssertionError("copied C010 oracle rows do not match the 125 frozen input IDs")
    by_base_id = {row["case_id"]: row for row in base_oracle}
    for row in base_rows:
        data = json.loads((AUDIT / row["path"]).read_text(encoding="utf-8"))
        if base.sha(base.canonical(data)) != by_base_id[row["case_id"]]["input_sha256"]:
            raise AssertionError(f"C010 oracle/input canonical hash mismatch: {row['case_id']}")

    new_rows = [row for row in correctness["cases"]
                if row["expected_source"] in {"c011_direct_rgs_v1", "c011_direct_rgs_v2"}]
    rgs_outputs = []
    for row in new_rows:
        path = AUDIT / row["path"]
        raw = path.read_bytes()
        if base.sha(raw) != row["input_sha256"]:
            raise AssertionError(f"new input hash mismatch: {row['case_id']}")
        data = json.loads(raw.decode("utf-8"))
        rgs_outputs.append(base.make_rgs_result(row, raw, data))
    rgs_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                      for row in rgs_outputs).encode("utf-8")
    base.write_once(AUDIT / "C011_RGS_ORACLE_V3.jsonl", rgs_raw)
    combined_raw = base_oracle_path.read_bytes() + rgs_raw
    base.write_once(AUDIT / "FULL_CORRECTNESS_ORACLE_V3.jsonl", combined_raw)

    rgs_by_id = {row["case_id"]: row for row in rgs_outputs}
    performance = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
    certs = []
    for case in performance["cells"]:
        if case["family_kind"] == "direct_rgs_fallback":
            path = AUDIT / case["path"]
            raw = path.read_bytes()
            if base.sha(raw) != case["input_sha256"]:
                raise AssertionError(f"fallback input hash mismatch: {case['case_id']}")
            data = json.loads(raw.decode("utf-8"))
            output = rgs_by_id.get(case["case_id"])
            if output is None:
                # The performance control is not a correctness-manifest row.
                # Compute its direct-RGS result separately; do not silently add
                # it to the frozen 138-case correctness family.
                output = base.make_rgs_result(case, raw, data)
            alphabet, positives, negatives = base.normalize(data)
            if any(base.adjacent_swap(p, n) is not None for p in positives for n in negatives):
                raise AssertionError("fallback control unexpectedly has adjacent-swap edges")
            if base.feasible(alphabet, positives, negatives, tuple(range(len(alphabet)))):
                raise AssertionError("fallback singleton atoms unexpectedly feasible")
            certs.append({
                "case_id": case["case_id"],
                "proof_method": "full direct RGS oracle, m<=8; exact empty swap graph and singleton infeasibility replayed",
                "input_sha256": case["input_sha256"],
                "partition_count": output["partition_count"],
                "partition_count_by_k": output["partition_count_by_k"],
                "compatible_rgs": output["compatible_rgs"],
                "graph_empty_expected": True,
                "atom_partition_feasible_expected": False,
            })
        else:
            path = AUDIT / case["path"]
            data = json.loads(path.read_text(encoding="utf-8"))
            certs.append(base.certify_family(case, data))
    cert_raw = (json.dumps({
        "schema_version": 1,
        "method": "independent structural proof certificates; no Bell(alphabet-size) enumeration",
        "certificates": certs,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    base.write_once(AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V3.json", cert_raw)
    receipt = {
        "schema_version": 1,
        "status": "oracle_and_family_certificates_frozen",
        "rgs_new_case_count": len(rgs_outputs),
        "rgs_new_case_ids": [row["case_id"] for row in rgs_outputs],
        "base_c010_oracle_case_count": len(base_oracle),
        "full_correctness_oracle_case_count": len(base_oracle) + len(rgs_outputs),
        "full_oracle_sha256": base.sha(combined_raw),
        "rgs_extension_sha256": base.sha(rgs_raw),
        "family_certificate_count": len(certs),
        "family_certificate_sha256": base.sha(cert_raw),
        "direct_rgs_method": "canonical restricted-growth strings plus direct projection feasibility; duplicate labels normalized as set-valued finite samples",
        "provider_imports": False,
        "bell_large_m_enumeration": False,
        "v2_harness_issue": "performance fallback input was not a correctness-manifest row; v3 computes its direct-RGS result separately",
    }
    receipt_raw = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    base.write_once(AUDIT / "ORACLE_FREEZE_RECEIPT_V3.json", receipt_raw)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

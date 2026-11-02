#!/usr/bin/env python3
"""Cross-check the supplemental count-vs-ownership case independently."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from validate_provider_gate_v1 import compatible_set


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "feasible_count_not_unique_ownership_v1.json"
MANIFEST_PATH = ROOT / "manifest_v1.json"
ORACLE_PATH = ROOT / "oracle_v1.jsonl"
REPORT_PATH = ROOT / "validation_v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    row = json.loads(ORACLE_PATH.read_text(encoding="utf-8").strip())
    expected = {((0, 0, 1)), ((0, 1, 0))}
    observed = compatible_set(data)
    if observed != expected:
        raise AssertionError(f"alternate set-insertion output mismatch: {observed!r}")
    if row["partition_count"] != 2 or {tuple(rgs) for rgs in row["compatible_rgs"]} != expected:
        raise AssertionError("direct-RGS oracle output mismatch")
    relation = {"".join(item["symbols"]): item["relation"] for item in row["pair_relations"]}
    if relation != {"ab": "ambiguous", "ac": "ambiguous", "bc": "forced_different"}:
        raise AssertionError(f"pair relation mismatch: {relation!r}")
    if sha(INPUT_PATH) != manifest["valid_cases"][0]["input_sha256"]:
        raise AssertionError("addendum input hash mismatch")
    report = {
        "schema_version": 1,
        "status": "accepted_supplemental_mathematical_control",
        "case_id": manifest["valid_cases"][0]["case_id"],
        "direct_rgs_partition_count": row["partition_count"],
        "independent_set_insertion_count": len(observed),
        "compatible_partitions": row["compatible_partitions"],
        "pair_relations": relation,
        "input_sha256": sha(INPUT_PATH),
        "oracle_sha256": sha(ORACLE_PATH),
    }
    with REPORT_PATH.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

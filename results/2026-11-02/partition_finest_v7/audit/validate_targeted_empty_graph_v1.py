#!/usr/bin/env python3
"""Independent gate for the frozen empty-must-link/three-block addendum."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import validate_provider_gate_v2 as replay


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def main():
    if len(sys.argv) != 6:
        raise SystemExit("usage: validate_targeted_empty_graph_v1.py ADAPTIVE REFERENCE INPUT PRIMARY INDEPENDENT")
    adaptive_path, reference_path, input_path, primary_path, independent_path = map(Path, sys.argv[1:])
    row = read_jsonl(input_path)[0]
    primary = read_jsonl(primary_path)[0]
    independent = read_jsonl(independent_path)[0]
    adaptive_records = read_jsonl(adaptive_path)
    reference_records = read_jsonl(reference_path)
    adaptive = next(record for record in adaptive_records if record.get("record_type") == "case_result")
    reference = next(record for record in reference_records if record.get("record_type") == "case_result")
    failures = []
    expected = [["a", "b"], ["c", "d"], ["e", "f"]]
    if not primary["meet_compatible"] or primary["meet"] != expected:
        failures.append("RGS_target_not_unique_ab_cd_ef")
    if not independent["unique_finest_by_direct_poset"] or independent["meet"] != expected:
        failures.append("direct_poset_target_mismatch")
    for mode, record in (("adaptive", adaptive), ("reference", reference)):
        result = record["result"]
        if (record.get("case_id") != row["case_id"] or record.get("mode") != mode
                or result.get("status") != "finest_unique" or result.get("complete") is not True):
            failures.append(f"{mode}_status_or_binding_mismatch")
        if result.get("finality_certificate", {}).get("kind") != "complete_separator_cover":
            failures.append(f"{mode}_did_not_use_exhaustive_finality_path")
        if result.get("finality_certificate", {}).get("must_link_edges") != []:
            failures.append(f"{mode}_must_link_graph_not_empty")
        if result.get("finest_witness", {}).get("partition") != expected:
            failures.append(f"{mode}_partition_mismatch")
        valid, reason = replay.replay_result(replay.api_data(row["input"]), result, primary)
        if not valid:
            failures.append(f"{mode}_certificate_replay:{reason}")
    expected_binary = replay.normalized_set(primary["compatible_binary_partitions"])
    observed_binary = replay.normalized_set(reference["result"].get("reference_bipartitions", []))
    if expected_binary != observed_binary:
        failures.append("reference_binary_set_mismatch")
    result = {
        "schema_version": 1,
        "status": "accepted" if not failures else "rejected",
        "case_id": row["case_id"],
        "payload_sha256": primary["payload_sha256"],
        "compatible_all_k_partitions": primary["compatible_partition_count"],
        "compatible_binary_partitions": len(primary["compatible_binary_partitions"]),
        "maximal_refinement_frontier": len(primary["maximal_refinement_frontier"]),
        "unique_finest_partition": expected,
        "must_link_edges": 0,
        "adaptive_separator_rounds": adaptive["result"]["metrics"]["separator_rounds"],
        "adaptive_binary_cuts_checked": adaptive["result"]["metrics"]["binary_cuts_checked"],
        "adaptive_certificate_cut_records": len(adaptive["result"]["finality_certificate"]["cut_records"]),
        "adaptive_successful_separators": len(adaptive["result"]["finality_certificate"]["successful_separators"]),
        "provider_attempt_ids": {"adaptive": adaptive_path.parent.name,
                                  "reference": reference_path.parent.name},
        "all_k_sha256": hashlib.sha256(Path(primary_path).read_bytes()).hexdigest(),
        "direct_poset_sha256": hashlib.sha256(Path(independent_path).read_bytes()).hexdigest(),
        "failures": failures,
    }
    out = Path(__file__).resolve().parent / "targeted_empty_graph" / "provider_gate_v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

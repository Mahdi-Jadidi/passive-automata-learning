#!/usr/bin/env python3
"""Independent v4 replay of adaptive and reference on the empty-graph control."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
import validate_provider_gate_v3 as replay  # noqa: E402


EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "input": "50700da2538c66552014ee993210006f7b9ef5df706bdbeae1b04ccb4ca69f17",
    "oracle_rgs": "5a4892243d6b90a40edf8052d18eeb91976f630f61507e8a611366b88e6bbe93",
    "oracle_poset": "303eb4faef79ee58c62551ee9f79bda906f735ad1882358b7ef5592f3cfea63c",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_targeted_empty_graph_v2.py ADAPTIVE_ATTEMPT REFERENCE_ATTEMPT")
    adaptive_dir, reference_dir = (Path(value).resolve() for value in sys.argv[1:])
    input_path = ROOT / "audit" / "targeted_empty_graph_v1.jsonl"
    rgs_path = ROOT / "audit" / "targeted_empty_graph" / "oracle_rgs_v1.jsonl"
    poset_path = ROOT / "audit" / "targeted_empty_graph" / "oracle_poset_v1.jsonl"
    provider = ROOT / "implementation" / "finest_solver_v4.py"
    cli = ROOT / "implementation" / "finest_cli_v2.py"
    protocol = ROOT / "implementation" / "PROTOCOL_V5.md"
    readiness = ROOT / "implementation" / "READINESS_V4.json"
    c006 = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005 = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"
    required_sources = {
        ROOT / "evidence" / "capture.py": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
        ROOT / "audit" / "run_targeted_empty_graph_v1.py": sha(ROOT / "audit" / "run_targeted_empty_graph_v1.py"),
        provider: EXPECTED["provider"], cli: EXPECTED["cli"], protocol: EXPECTED["protocol"],
        readiness: sha(readiness), input_path: EXPECTED["input"],
        rgs_path: EXPECTED["oracle_rgs"], poset_path: EXPECTED["oracle_poset"],
        c006: EXPECTED["c006"], c005: EXPECTED["c005"],
    }
    capture_adaptive, failures_adaptive = replay.verify_capture_bundle(adaptive_dir, "adaptive", required_sources)
    capture_reference, failures_reference = replay.verify_capture_bundle(reference_dir, "reference", required_sources)
    rows = replay.read_jsonl(input_path)
    primary_rows = replay.read_jsonl(rgs_path)
    poset_rows = replay.read_jsonl(poset_path)
    failures = ([{"mode": "adaptive", "scope": "capture", "reason": item} for item in failures_adaptive]
                + [{"mode": "reference", "scope": "capture", "reason": item} for item in failures_reference])
    if len(rows) != 1 or len(primary_rows) != 1 or len(poset_rows) != 1:
        raise AssertionError("targeted input or oracle row cardinality changed")
    row, oracle, poset = rows[0], primary_rows[0], poset_rows[0]
    if row["case_id"] != "ctrl_empty_must_link_unique_3":
        failures.append({"scope": "input", "reason": "wrong_case_id"})
    if sha(input_path) != EXPECTED["input"] or sha(rgs_path) != EXPECTED["oracle_rgs"] or sha(poset_path) != EXPECTED["oracle_poset"]:
        failures.append({"scope": "input", "reason": "frozen_input_or_oracle_hash_mismatch"})
    data = replay.api_data(row["input"])
    if oracle.get("payload_sha256") != poset.get("payload_sha256"):
        failures.append({"scope": "oracle", "reason": "oracle_payload_hash_mismatch"})
    if (oracle.get("meet_compatible") != poset.get("unique_finest_by_direct_poset")
            or replay.normalized_partition(oracle.get("meet", [])) != replay.normalized_partition(poset.get("meet", []))
            or oracle.get("compatible_partition_count") != poset.get("compatible_partition_count")):
        failures.append({"scope": "oracle", "reason": "RGS_vs_direct_poset_disagreement"})

    batches = {}
    summaries = {}
    for mode, directory in (("adaptive", adaptive_dir), ("reference", reference_dir)):
        records, summary, _ = replay.parse_batch(directory / "stdout.bin", mode)
        batches[mode], summaries[mode] = records, summary
        if set(records) != {row["case_id"]}:
            failures.append({"mode": mode, "scope": "batch", "reason": "case_set_mismatch"})
        if summary.get("rows") != 1 or summary.get("provider_sha256") != EXPECTED["provider"]:
            failures.append({"mode": mode, "scope": "batch", "reason": "summary_anchor_mismatch"})
        record = records.get(row["case_id"])
        if record is None:
            continue
        expected_payload_hash = hashlib.sha256(replay.canonical(row["input"]).encode("utf-8")).hexdigest()
        if record.get("payload_sha256") != expected_payload_hash:
            failures.append({"mode": mode, "scope": "binding", "reason": "payload_hash_mismatch"})
        valid, reason = replay.replay_result(data, record["result"], oracle)
        if not valid:
            failures.append({"mode": mode, "scope": "certificate", "reason": reason})
        result = record["result"]
        if result.get("status") != "finest_unique":
            failures.append({"mode": mode, "scope": "target", "reason": "not_unique_finest"})
        certificate = result.get("finality_certificate", {})
        if certificate.get("kind") != "complete_separator_cover":
            failures.append({"mode": mode, "scope": "target", "reason": "empty_graph_did_not_reach_complete_cover"})
        if certificate.get("must_link_edges") != []:
            failures.append({"mode": mode, "scope": "target", "reason": "must_link_graph_not_empty"})
        if len(result.get("finest_witness", {}).get("partition", [])) != 3:
            failures.append({"mode": mode, "scope": "target", "reason": "three_block_finest_missing"})
        if mode == "reference":
            observed = replay.normalized_set(result.get("reference_bipartitions", []))
            expected = replay.normalized_set(oracle.get("compatible_binary_partitions", []))
            if observed != expected:
                failures.append({"mode": mode, "scope": "binary_reference", "reason": "binary_set_mismatch"})

    report = {
        "schema_version": 2,
        "status": "accepted" if not failures else "rejected",
        "case_id": row["case_id"],
        "input_sha256": sha(input_path),
        "rgs_oracle_sha256": sha(rgs_path),
        "direct_poset_oracle_sha256": sha(poset_path),
        "rgs_all_k_compatible_count": oracle.get("compatible_partition_count"),
        "rgs_compatible_bipartition_count": len(oracle.get("compatible_binary_partitions", [])),
        "rgs_finest": oracle.get("meet"),
        "adaptive_attempt_id": capture_adaptive.get("attempt_id"),
        "reference_attempt_id": capture_reference.get("attempt_id"),
        "adaptive_capture_stdout_sha256": capture_adaptive.get("stdout_sha256"),
        "reference_capture_stdout_sha256": capture_reference.get("stdout_sha256"),
        "adaptive_certificate_kind": batches.get("adaptive", {}).get(row["case_id"], {}).get("result", {}).get("finality_certificate", {}).get("kind"),
        "reference_certificate_kind": batches.get("reference", {}).get(row["case_id"], {}).get("result", {}).get("finality_certificate", {}).get("kind"),
        "independent_certificate_replays": 2,
        "failures": failures,
    }
    report_path = ROOT / "audit" / "targeted_empty_graph" / "provider_gate_v2.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze V2 timing inputs, replacing the m6 singleton case with the accepted empty-graph control."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "timing_v2"
TARGET_CASE = "ctrl_empty_must_link_unique_3"
TARGET_INPUT_SHA = "50700da2538c66552014ee993210006f7b9ef5df706bdbeae1b04ccb4ca69f17"
TARGET_RGS_SHA = "5a4892243d6b90a40edf8052d18eeb91976f630f61507e8a611366b88e6bbe93"
TARGET_POSET_SHA = "303eb4faef79ee58c62551ee9f79bda906f735ad1882358b7ef5592f3cfea63c"
TARGET_GATE_SHA = "aa87929527cb843b2851a7f6a11b5c6cc8b1a88fa02e38f8f101a4fba5dbd999"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    v1_manifest_path = AUDIT / "timing_v1" / "input_manifest_v1.json"
    v1_manifest = json.loads(v1_manifest_path.read_text(encoding="utf-8"))
    if v1_manifest.get("status") != "frozen_inputs_prepared_no_timing_run":
        raise RuntimeError("V1 input manifest is not frozen")
    target_source = AUDIT / "targeted_empty_graph_v1.jsonl"
    target_rgs_path = AUDIT / "targeted_empty_graph" / "oracle_rgs_v1.jsonl"
    target_poset_path = AUDIT / "targeted_empty_graph" / "oracle_poset_v1.jsonl"
    target_gate_path = AUDIT / "targeted_empty_graph" / "provider_gate_v2.json"
    if (digest(target_source.read_bytes()) != TARGET_INPUT_SHA
            or digest(target_rgs_path.read_bytes()) != TARGET_RGS_SHA
            or digest(target_poset_path.read_bytes()) != TARGET_POSET_SHA
            or digest(target_gate_path.read_bytes()) != TARGET_GATE_SHA):
        raise RuntimeError("accepted targeted-control input/oracle/gate hash changed")
    gate = json.loads(target_gate_path.read_text(encoding="utf-8"))
    if gate.get("status") != "accepted" or gate.get("case_id") != TARGET_CASE:
        raise RuntimeError("V4 targeted empty-graph correctness gate is not accepted")

    out_inputs = OUT / "inputs"
    out_inputs.mkdir(parents=True, exist_ok=True)
    cases = {}
    for case_id in ("c007_gen_m04_013", "c007_gen_m08_000"):
        info = v1_manifest["cases"][case_id]
        old_path = AUDIT / "timing_v1" / info["path"]
        new_path = out_inputs / f"{case_id}.json"
        shutil.copyfile(old_path, new_path)
        cases[case_id] = dict(info)
        cases[case_id]["path"] = f"inputs/{case_id}.json"
        cases[case_id]["rgs_oracle_path"] = "audit/oracle_v1/all_k_rgs.jsonl"
        cases[case_id]["rgs_oracle_sha256"] = v1_manifest["all_k_rgs_sha256"]
        cases[case_id]["independent_oracle_path"] = "audit/oracle_v1/all_k_independent_v3.jsonl"
        cases[case_id]["independent_oracle_sha256"] = "290a82bd7fd1cae7d4e0aebb27a6ea90b91148ee47d0963012319d6339680d25"
        cases[case_id]["source_payload_sha256"] = info["payload_sha256"]
        cases[case_id]["input_file_sha256"] = digest(new_path.read_bytes())
        cases[case_id]["rgs_oracle_path"] = "oracle_v1/all_k_rgs.jsonl"
        cases[case_id]["independent_oracle_path"] = "oracle_v1/all_k_independent_v3.jsonl"

    target_row = read_jsonl(target_source)[0]
    target_data = target_row["input"]
    cli_data = {
        "alphabet": list(target_data["alphabet"]),
        "positive": ["".join(word) for word in target_data["positive"]],
        "negative": ["".join(word) for word in target_data["negative"]],
    }
    target_path = out_inputs / f"{TARGET_CASE}.json"
    target_bytes = (json.dumps(cli_data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    target_path.write_bytes(target_bytes)
    rgs_target = read_jsonl(target_rgs_path)[0]
    poset_target = read_jsonl(target_poset_path)[0]
    cases[TARGET_CASE] = {
        "path": f"inputs/{TARGET_CASE}.json",
        "sha256": digest(target_bytes),
        "input_file_sha256": digest(target_bytes),
        "bytes": len(target_bytes),
        "payload_sha256": digest(canonical(target_data)),
        "source_payload_sha256": digest(canonical(target_data)),
        "alphabet_size": len(target_data["alphabet"]),
        "max_word_length": max((len(word) for group in (target_data["positive"], target_data["negative"])
                                for word in group), default=0),
        "positive_count": len(target_data["positive"]),
        "negative_count": len(target_data["negative"]),
        "all_k_compatible_bipartitions": len(rgs_target["compatible_binary_partitions"]),
        "all_k_compatible_partition_count": rgs_target["compatible_partition_count"],
        "all_k_expected_status": "finest_unique" if rgs_target["meet_compatible"] else "multiple_maximal_exist",
        "all_k_expected_meet": rgs_target["meet"],
        "validated_v4_adaptive_path": "complete_separator_cover",
        "validated_v4_adaptive_fallback": True,
        "validated_v4_adaptive_status": "finest_unique",
        "rgs_oracle_path": "targeted_empty_graph/oracle_rgs_v1.jsonl",
        "rgs_oracle_sha256": TARGET_RGS_SHA,
        "independent_oracle_path": "targeted_empty_graph/oracle_poset_v1.jsonl",
        "independent_oracle_sha256": TARGET_POSET_SHA,
        "v4_correctness_gate_path": "targeted_empty_graph/provider_gate_v2.json",
        "v4_correctness_gate_sha256": TARGET_GATE_SHA,
        "forced_edge_count": 0,
        "purpose": "unique three-block finest partition with empty forced graph; requires separator search and complete cover",
    }
    manifest = {
        "schema_version": 2,
        "status": "frozen_inputs_prepared_no_timing_run",
        "supersedes_for_planned_timing_only": "timing_v1/input_manifest_v1.json",
        "v1_preserved_unrun": True,
        "selection_rule": "retain V1 m4 fallback/multiple-maximal and m8 singleton fast path; replace V1 m6 singleton fast path with independently accepted empty-must-link unique-three-block case; this broadens path coverage without timing-based selection",
        "source_corpus_sha256": "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b",
        "all_k_rgs_sha256": "a4216c69d0328419086096ff7b28f7efc39f98fb85ff904d798c5a6f54421281",
        "all_k_independent_sha256": "290a82bd7fd1cae7d4e0aebb27a6ea90b91148ee47d0963012319d6339680d25",
        "targeted_empty_graph_source_sha256": TARGET_INPUT_SHA,
        "targeted_v4_gate_sha256": TARGET_GATE_SHA,
        "timing_measurement_observations_used_for_selection": False,
        "cases": cases,
    }
    manifest_path = OUT / "input_manifest_v2.json"
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    print(json.dumps({"status": manifest["status"], "manifest_path": str(manifest_path),
                      "manifest_sha256": digest(manifest_bytes), "cases": cases},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

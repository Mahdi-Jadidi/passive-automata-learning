#!/usr/bin/env python3
"""Independent replay of five adaptive-only structured scale CLI outputs."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import validate_provider_gate_v2 as replay


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_case(case, sidecar, input_path, stdout_path, capture_manifest_path, capture_result_path):
    failures = []
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    capture_manifest = json.loads(Path(capture_manifest_path).read_text(encoding="utf-8"))
    capture_result = json.loads(Path(capture_result_path).read_text(encoding="utf-8"))
    if sidecar["case_id"] != case["case_id"]:
        failures.append("sidecar_case_id_mismatch")
    payload_hash = hashlib.sha256(replay.canonical(data).encode("utf-8")).hexdigest()
    if payload_hash != sidecar["payload_sha256"]:
        failures.append("sidecar_payload_binding_mismatch")
    if len(data["positive"]) != 1 or data["positive"][0] != sidecar["base_positive_word"]:
        failures.append("positive_base_mismatch")
    base = sidecar["base_positive_word"]
    edges = sidecar["swap_edges"]
    if len(edges) != len(data["negative"]):
        failures.append("swap_edge_count_mismatch")
    for index, edge in enumerate(edges):
        position = edge["position"]
        if (edge["negative_index"] != index or not 0 <= position < len(base) - 1
                or edge["symbols"] != [base[position], base[position + 1]]
                or data["negative"][index] != base[:position] + base[position + 1]
                    + base[position] + base[position + 2:]):
            failures.append(f"bad_constructed_swap_{index}")
            break
    if len(set(data["negative"])) != len(data["negative"]):
        failures.append("negative_words_not_unique")

    expected = sidecar["expected_finest_partition"]
    alphabet = data["alphabet"]
    if not replay.is_valid_partition(expected, alphabet):
        failures.append("invalid_sidecar_partition")
    witness, collision = replay.direct_witness(data, expected)
    if witness is None:
        failures.append("sidecar_partition_not_directly_compatible")

    source_hashes = {source["path"]: source["sha256"] for source in capture_manifest.get("sources", [])}
    readiness_path = ROOT / "implementation" / "READINESS_V1.json"
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    for item in readiness.get("runtime_dependencies", []) + readiness.get("versioned_artifacts", []):
        absolute = str((ROOT / "implementation" / item["path"]).resolve())
        if source_hashes.get(absolute) != item["sha256"]:
            failures.append("frozen_source_not_captured:" + item["path"])
    if capture_result.get("stdout_sha256") != sha256(stdout_path):
        failures.append("captured_stdout_hash_mismatch")
    if capture_result.get("child_reaped") is not True:
        failures.append("capture_child_not_reaped")
    if "--mode" not in capture_manifest.get("command_argv", []) or "adaptive" not in capture_manifest.get("command_argv", []):
        failures.append("wrong_cli_mode")
    if "--seconds" not in capture_manifest.get("command_argv", []) or "28" not in capture_manifest.get("command_argv", []):
        failures.append("wrong_cooperative_deadline")

    stdout = Path(stdout_path).read_text(encoding="utf-8").strip()
    if not stdout:
        if capture_result.get("execution_status") == "timed_out":
            scientific = "hard_censored_empty_output"
        else:
            failures.append("empty_provider_output_without_hard_timeout")
            scientific = "invalid_empty_output"
        return {"case_id": case["case_id"], "scientific_status": scientific,
                "capture_execution_status": capture_result.get("execution_status"),
                "stdout_bytes": capture_result.get("stdout_bytes"), "failures": failures}
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        return {"case_id": case["case_id"], "scientific_status": "invalid_json_output",
                "capture_execution_status": capture_result.get("execution_status"),
                "stdout_bytes": capture_result.get("stdout_bytes"),
                "failures": failures + ["cli_output_not_single_json_object"]}

    if result.get("status") == "incomplete":
        if result.get("complete") is not False or result.get("decision_complete") is not False:
            failures.append("incomplete_result_claimed_completeness")
        if result.get("finality_certificate") is not None or result.get("finest_witness") is not None:
            failures.append("incomplete_result_contains_final_claim")
        scientific = "cooperative_censored_no_finality"
    elif result.get("status") == "finest_unique" and result.get("complete") is True:
        certificate = result.get("finality_certificate", {})
        if certificate.get("kind") != "must_link_components_compatible":
            failures.append("scale_result_did_not_use_must_link_shortcut")
        provider_edges = certificate.get("must_link_edges")
        if not isinstance(provider_edges, list):
            failures.append("missing_must_link_edge_records")
            provider_edges = []
        if any(not replay.valid_edge(edge, data) for edge in provider_edges):
            failures.append("invalid_provider_edge_witness")
        expected_pair_set = {tuple(edge["symbols"]) for edge in edges}
        observed_pair_set = {tuple(edge.get("symbols", [])) for edge in provider_edges
                             if isinstance(edge, dict)}
        if observed_pair_set != expected_pair_set:
            failures.append("provider_must_link_edges_not_exact_path_edges")
        components = replay.dsu_components(alphabet, provider_edges)
        if replay.normalized_partition(components) != replay.normalized_partition(expected):
            failures.append("provider_edge_components_not_expected_partition")
        if replay.normalized_partition(certificate.get("components", [])) != replay.normalized_partition(expected):
            failures.append("certificate_components_not_expected_partition")
        if replay.normalized_partition(result.get("finest_witness", {}).get("partition", [])) != replay.normalized_partition(expected):
            failures.append("provider_finest_partition_mismatch")
        if result.get("finest_witness") != witness:
            failures.append("provider_projection_witness_replay_mismatch")
        if result.get("uniqueness_scope") != "finest_sample_compatible_partition_not_hidden_architecture":
            failures.append("wrong_uniqueness_scope")
        scientific = "accepted_unique_finest_by_forced_path_edges"
    else:
        failures.append("unexpected_scale_status:" + str(result.get("status")))
        scientific = "provider_error_or_unexpected_status"

    return {
        "case_id": case["case_id"],
        "scientific_status": scientific,
        "capture_execution_status": capture_result.get("execution_status"),
        "exit_code": capture_result.get("exit_code"),
        "child_reaped": capture_result.get("child_reaped"),
        "alphabet_size": len(alphabet),
        "context_length": len(base),
        "negative_count": len(data["negative"]),
        "expected_blocks": len(expected),
        "edge_witnesses": len(result.get("finality_certificate", {}).get("must_link_edges", [])),
        "stdout_bytes": capture_result.get("stdout_bytes"),
        "capture_attempt_id": capture_result.get("attempt_id"),
        "stdout_sha256": capture_result.get("stdout_sha256"),
        "failures": failures,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_scale_v1.py SCALE_CAPTURE_MAP.json")
    capture_map_path = Path(sys.argv[1])
    capture_map = json.loads(capture_map_path.read_text(encoding="utf-8"))
    scale_manifest_path = ROOT / "audit" / "scale_v1" / "manifest.json"
    manifest = json.loads(scale_manifest_path.read_text(encoding="utf-8"))
    inputs = {row["case_id"]: row for row in read_jsonl(ROOT / "audit" / "scale_v1" / "inputs.jsonl")}
    sidecars = {row["case_id"]: row for row in read_jsonl(ROOT / "audit" / "scale_v1" / "truth_sidecars.jsonl")}
    reports = []
    for case_spec in manifest["cells"]:
        case_id = case_spec["case_id"]
        attempt_id = capture_map["attempts"][case_id]
        attempt_dir = ROOT / "evidence" / "attempts" / attempt_id
        reports.append(verify_case(case_spec, sidecars[case_id],
                                   ROOT / "audit" / "scale_v1" / "cli_inputs" / f"{case_id}.json",
                                   attempt_dir / "stdout.bin", attempt_dir / "manifest.json",
                                   attempt_dir / "result.json"))
    accepted = all(not report["failures"] and report["scientific_status"] == "accepted_unique_finest_by_forced_path_edges"
                   for report in reports if report["scientific_status"] != "cooperative_censored_no_finality")
    report = {
        "schema_version": 1,
        "status": "accepted_with_censoring" if accepted else "rejected",
        "cell_count": len(reports),
        "accepted_cells": sum(report["scientific_status"] == "accepted_unique_finest_by_forced_path_edges"
                               and not report["failures"] for report in reports),
        "censored_cells": sum(report["scientific_status"] == "cooperative_censored_no_finality"
                               and not report["failures"] for report in reports),
        "scale_input_manifest_sha256": sha256(scale_manifest_path),
        "scale_cells": reports,
    }
    out = ROOT / "audit" / "scale_v1" / "scale_validation_v1.json"
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())

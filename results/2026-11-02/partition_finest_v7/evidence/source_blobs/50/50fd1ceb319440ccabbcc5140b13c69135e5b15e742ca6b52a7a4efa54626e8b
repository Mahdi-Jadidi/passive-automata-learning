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


def source_map(manifest):
    return {source["path"]: source["sha256"] for source in manifest.get("sources", [])}


def has_source(manifest, path, expected_sha):
    absolute = str(Path(path).resolve())
    return source_map(manifest).get(absolute) == expected_sha


def source_closure_failures(case_id, capture_manifest, readiness, scale_manifest, cli_manifest):
    failures = []
    fixed_paths = [
        ROOT / "audit" / "PROTOCOL_SCALE_V1.md",
        ROOT / "audit" / "PROTOCOL_SCALE_V2.md",
        ROOT / "audit" / "scale_v1" / "manifest.json",
        ROOT / "audit" / "scale_v1" / "inputs.jsonl",
        ROOT / "audit" / "scale_v1" / "truth_sidecars.jsonl",
        ROOT / "audit" / "scale_v1" / "cli_input_manifest_v1.json",
        ROOT / "audit" / "scale_v1" / "cli_inputs" / f"{case_id}.json",
        ROOT / "evidence" / "capture.py",
        ROOT / "implementation" / "READINESS_V1.json",
        ROOT / "implementation" / "finest_solver_v3.py",
        ROOT / "implementation" / "finest_cli_v1.py",
    ]
    declared = {
        ROOT / "audit" / "PROTOCOL_SCALE_V1.md": scale_manifest["protocol_sha256"],
        ROOT / "audit" / "scale_v1" / "inputs.jsonl": scale_manifest["files"]["inputs.jsonl"]["sha256"],
        ROOT / "audit" / "scale_v1" / "truth_sidecars.jsonl": scale_manifest["files"]["truth_sidecars.jsonl"]["sha256"],
    }
    cli_entry = cli_manifest["files"][case_id]
    cli_path = ROOT / "audit" / "scale_v1" / "cli_inputs" / f"{case_id}.json"
    declared[cli_path] = cli_entry["sha256"]
    for path in fixed_paths:
        expected_sha = declared.get(path, sha256(path))
        if not has_source(capture_manifest, path, expected_sha):
            failures.append("required_scale_source_missing_or_drifted:" + str(path.relative_to(ROOT)))
    if cli_entry.get("path") != f"cli_inputs/{case_id}.json" or sha256(cli_path) != cli_entry["sha256"]:
        failures.append("cli_input_manifest_does_not_bind_input_file")
    for item in readiness.get("runtime_dependencies", []):
        path = (ROOT / "implementation" / item["path"]).resolve()
        if not has_source(capture_manifest, path, item["sha256"]):
            failures.append("runtime_dependency_not_captured:" + item["path"])
    argv = capture_manifest.get("command_argv", [])
    if not any(arg.endswith("finest_cli_v1.py") for arg in argv):
        failures.append("versioned_cli_not_invoked")
    if not any(arg.endswith(f"{case_id}.json") for arg in argv):
        failures.append("wrong_scale_case_input_argv")
    return failures


def check_generator_and_cli_derivation(closure_map, scale_manifest, cli_manifest):
    failures = []
    details = {}
    for role, key, expected_label in (
        ("corpus_freeze", "scale_corpus_freeze_attempt", "c007_scale_corpus_freeze_v1"),
        ("cli_input_derivation", "scale_cli_input_derivation_attempt", "c007_scale_cli_input_derivation_v1"),
    ):
        attempt_id = closure_map[key]
        attempt = ROOT / "evidence" / "attempts" / attempt_id
        manifest_path, result_path = attempt / "manifest.json", attempt / "result.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if manifest.get("label") != expected_label or result.get("execution_status") != "success" or result.get("exit_code") != 0:
            failures.append(role + "_capture_not_successful")
        if result.get("stdout_sha256") != sha256(attempt / "stdout.bin"):
            failures.append(role + "_stdout_hash_mismatch")
        captured_summary = json.loads((attempt / "stdout.bin").read_text(encoding="utf-8").strip())
        if role == "corpus_freeze":
            generator = ROOT / "audit" / "generate_scale_v1.py"
            protocol = ROOT / "audit" / "PROTOCOL_SCALE_V1.md"
            if not has_source(manifest, generator, scale_manifest["generator_sha256"]):
                failures.append("scale_generator_not_bound_to_freeze")
            if not has_source(manifest, protocol, scale_manifest["protocol_sha256"]):
                failures.append("scale_v1_protocol_not_bound_to_freeze")
            if captured_summary.get("manifest_sha256") != sha256(ROOT / "audit" / "scale_v1" / "manifest.json"):
                failures.append("scale_freeze_output_manifest_hash_mismatch")
        else:
            prep = ROOT / "audit" / "prepare_scale_cli_inputs_v1.py"
            inputs = ROOT / "audit" / "scale_v1" / "inputs.jsonl"
            if not has_source(manifest, prep, sha256(prep)):
                failures.append("cli_derivation_script_not_bound")
            if not has_source(manifest, inputs, scale_manifest["files"]["inputs.jsonl"]["sha256"]):
                failures.append("cli_derivation_source_inputs_not_bound")
            if cli_manifest["source_inputs_sha256"] != scale_manifest["files"]["inputs.jsonl"]["sha256"]:
                failures.append("cli_manifest_source_inputs_mismatch")
            if captured_summary.get("manifest_sha256") != sha256(ROOT / "audit" / "scale_v1" / "cli_input_manifest_v1.json"):
                failures.append("cli_derivation_output_manifest_hash_mismatch")
        details[role] = {"attempt_id": attempt_id, "capture_label": manifest.get("label"),
                         "capture_stdout_sha256": result.get("stdout_sha256")}
    return failures, details


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
    for item in readiness.get("runtime_dependencies", []):
        absolute = str((ROOT / "implementation" / item["path"]).resolve())
        if source_hashes.get(absolute) != item["sha256"]:
            failures.append("frozen_source_not_captured:" + item["path"])
    for item in readiness.get("versioned_artifacts", []):
        if item["path"] == "finest_cli_v1.py":
            absolute = str((ROOT / "implementation" / item["path"]).resolve())
            if source_hashes.get(absolute) != item["sha256"]:
                failures.append("frozen_cli_not_captured")
    if capture_result.get("stdout_sha256") != sha256(stdout_path):
        failures.append("captured_stdout_hash_mismatch")
    if capture_result.get("child_reaped") is not True:
        failures.append("capture_child_not_reaped")
    if "--mode" not in capture_manifest.get("command_argv", []) or "adaptive" not in capture_manifest.get("command_argv", []):
        failures.append("wrong_cli_mode")
    if "--seconds" not in capture_manifest.get("command_argv", []) or "28" not in capture_manifest.get("command_argv", []):
        failures.append("wrong_cooperative_deadline")
    scale_manifest = json.loads((ROOT / "audit" / "scale_v1" / "manifest.json").read_text(encoding="utf-8"))
    cli_manifest = json.loads((ROOT / "audit" / "scale_v1" / "cli_input_manifest_v1.json").read_text(encoding="utf-8"))
    failures.extend(source_closure_failures(case["case_id"], capture_manifest, readiness,
                                            scale_manifest, cli_manifest))

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
    closure_map_path = capture_map_path.with_name("closure_map_v1.json")
    closure_map = json.loads(closure_map_path.read_text(encoding="utf-8"))
    scale_manifest_path = ROOT / "audit" / "scale_v1" / "manifest.json"
    manifest = json.loads(scale_manifest_path.read_text(encoding="utf-8"))
    cli_manifest_path = ROOT / "audit" / "scale_v1" / "cli_input_manifest_v1.json"
    cli_manifest = json.loads(cli_manifest_path.read_text(encoding="utf-8"))
    closure_failures, closure_details = check_generator_and_cli_derivation(closure_map, manifest, cli_manifest)
    for name in ("inputs.jsonl", "truth_sidecars.jsonl"):
        path = ROOT / "audit" / "scale_v1" / name
        if sha256(path) != manifest["files"][name]["sha256"]:
            closure_failures.append("frozen_scale_file_hash_mismatch:" + name)
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
    readiness = json.loads((ROOT / "implementation" / "READINESS_V1.json").read_text(encoding="utf-8"))
    protocol_expected = next(item["sha256"] for item in readiness["versioned_artifacts"]
                             if item["path"] == "PROTOCOL_V1.md")
    protocol_actual = sha256(ROOT / "implementation" / "PROTOCOL_V1.md")
    accepted_statuses = {"accepted_unique_finest_by_forced_path_edges",
                         "cooperative_censored_no_finality"}
    accepted = (not closure_failures and all(not report["failures"] for report in reports)
                and all(report["scientific_status"] in accepted_statuses for report in reports)
                and protocol_actual == protocol_expected)
    report = {
        "schema_version": 1,
        "status": "accepted_with_censoring" if accepted else "rejected",
        "cell_count": len(reports),
        "accepted_cells": sum(report["scientific_status"] == "accepted_unique_finest_by_forced_path_edges"
                               and not report["failures"] for report in reports),
        "censored_cells": sum(report["scientific_status"] == "cooperative_censored_no_finality"
                               and not report["failures"] for report in reports),
        "scale_input_manifest_sha256": sha256(scale_manifest_path),
        "source_closure": {"failures": closure_failures, "captures": closure_details,
                           "provider_capture_required_sources_checked": True,
                           "generator_and_cli_derivation_captures_checked": True},
        "implementation_protocol_hash_anchor": {
            "path": "implementation/PROTOCOL_V1.md",
            "readiness_sha256": protocol_expected,
            "directly_snapshotted_by_scale_cli_captures": False,
            "current_file_matches_readiness": protocol_actual == protocol_expected,
        },
        "scale_cells": reports,
    }
    out = ROOT / "audit" / "scale_v1" / "scale_validation_v4.json"
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())

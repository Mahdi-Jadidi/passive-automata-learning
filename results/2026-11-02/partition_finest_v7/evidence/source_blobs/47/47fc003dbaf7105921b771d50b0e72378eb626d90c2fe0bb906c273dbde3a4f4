#!/usr/bin/env python3
"""Independently replay the already captured C007 v4 65,536-symbol case."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
import validate_provider_gate_v3 as replay  # noqa: E402


ATTEMPT_ID = "20261101T213654.444396Z_b24663495c"
EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol_v5": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "readiness_v4": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "scale_protocol_v1": "5d46fe473e55e39f337b2daca1c9b07d654776b38053b0536922803000c0f027",
    "scale_manifest": "1a79aba073c61148948ef21451e3b043be733e0ef5b447f0da5954ac602a9012",
    "scale_case": "680a589332d327f07eb5d567db262409b874cf7703e18e3e987f43e90fca8dde",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
    "capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
    "stdout": "6685437521f425168c7aa9676a5bc2fea964be61032586ee013623e32c8ceaf9",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    attempt = ROOT / "evidence" / "attempts" / ATTEMPT_ID
    input_path = ROOT / "audit" / "scale_v1" / "cli_inputs" / "scale_m16_len65536.json"
    manifest_path = ROOT / "audit" / "scale_v1" / "manifest.json"
    sidecars_path = ROOT / "audit" / "scale_v1" / "truth_sidecars.jsonl"
    cli_manifest_path = ROOT / "audit" / "scale_v1" / "cli_input_manifest_v1.json"
    protocol_v1_path = ROOT / "audit" / "PROTOCOL_SCALE_V1.md"
    attempt_manifest_path = attempt / "manifest.json"
    attempt_result_path = attempt / "result.json"
    stdout_path = attempt / "stdout.bin"
    stderr_path = attempt / "stderr.bin"
    readiness_v4_path = ROOT / "implementation" / "READINESS_V4.json"
    readiness_v5_path = ROOT / "implementation" / "READINESS_V5.json"
    provider_path = ROOT / "implementation" / "finest_solver_v4.py"
    cli_path = ROOT / "implementation" / "finest_cli_v2.py"
    protocol_v5_path = ROOT / "implementation" / "PROTOCOL_V5.md"
    c006_path = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005_path = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"
    capture_path = ROOT / "evidence" / "capture.py"

    scale_manifest = read_json(manifest_path)
    cli_manifest = read_json(cli_manifest_path)
    sidecar_rows = [json.loads(line) for line in sidecars_path.read_text(encoding="utf-8").splitlines() if line]
    case_id = "scale_m16_len65536"
    case = next(row for row in replay.read_jsonl(ROOT / "audit" / "scale_v1" / "inputs.jsonl")
                if row["case_id"] == case_id)
    sidecar = next(row for row in sidecar_rows if row["case_id"] == case_id)
    data = read_json(input_path)
    capture_manifest = read_json(attempt_manifest_path)
    capture_result = read_json(attempt_result_path)
    readiness_v5 = read_json(readiness_v5_path)

    required_sources = {
        capture_path: EXPECTED["capture"],
        provider_path: EXPECTED["provider"],
        cli_path: EXPECTED["cli"],
        protocol_v5_path: EXPECTED["protocol_v5"],
        readiness_v4_path: EXPECTED["readiness_v4"],
        protocol_v1_path: EXPECTED["scale_protocol_v1"],
        manifest_path: EXPECTED["scale_manifest"],
        input_path: EXPECTED["scale_case"],
        c006_path: EXPECTED["c006"],
        c005_path: EXPECTED["c005"],
    }
    failures = []
    for path, expected_hash in required_sources.items():
        absolute = str(path.resolve())
        if not any(source.get("path") == absolute and source.get("sha256") == expected_hash
                   for source in capture_manifest.get("sources", [])):
            failures.append("required_runtime_source_missing_or_drifted:" + path.name)
    for source in capture_manifest.get("sources", []):
        blob = ROOT / "evidence" / source.get("snapshot", "")
        if not blob.is_file() or sha_path(blob) != source.get("sha256"):
            failures.append("invalid_captured_source_blob:" + Path(source.get("path", "unknown")).name)

    if capture_manifest.get("attempt_id") != ATTEMPT_ID or capture_result.get("attempt_id") != ATTEMPT_ID:
        failures.append("capture_attempt_id_mismatch")
    if capture_manifest.get("label") != "c007_v4_single_historical_long_cell":
        failures.append("unexpected_historical_run_label")
    if capture_result.get("execution_status") != "success" or capture_result.get("exit_code") != 0:
        failures.append("historical_capture_not_successful")
    if capture_result.get("child_reaped") is not True:
        failures.append("historical_child_not_reaped")
    if capture_result.get("stdout_sha256") != EXPECTED["stdout"] or sha_path(stdout_path) != EXPECTED["stdout"]:
        failures.append("historical_stdout_hash_mismatch")
    if capture_result.get("stderr_bytes") != 0 or stderr_path.stat().st_size != 0:
        failures.append("historical_stderr_not_empty")
    if capture_result.get("stdout_bytes") != stdout_path.stat().st_size:
        failures.append("historical_stdout_byte_count_mismatch")

    cli_entry = cli_manifest.get("files", {}).get(case_id, {})
    if sha_path(input_path) != EXPECTED["scale_case"]:
        failures.append("long_case_input_hash_mismatch")
    if cli_entry.get("path") != "cli_inputs/scale_m16_len65536.json" or cli_entry.get("sha256") != EXPECTED["scale_case"]:
        failures.append("cli_manifest_does_not_bind_long_case")
    if scale_manifest.get("protocol_sha256") != EXPECTED["scale_protocol_v1"]:
        failures.append("scale_manifest_protocol_anchor_mismatch")
    if scale_manifest.get("files", {}).get("truth_sidecars.jsonl", {}).get("sha256") != sha_path(sidecars_path):
        failures.append("scale_sidecar_manifest_mismatch")
    if case.get("case_id") != case_id or sidecar.get("case_id") != case_id:
        failures.append("long_case_or_sidecar_id_mismatch")
    if sidecar.get("payload_sha256") != sha_bytes(canonical(data).encode("utf-8")):
        failures.append("sidecar_payload_hash_mismatch")
    base_word = data.get("positive", [""])[0]
    derived_swaps = []
    for negative_index, negative_word in enumerate(data.get("negative", [])):
        differences = [index for index, (left, right) in enumerate(zip(base_word, negative_word))
                       if left != right]
        if (len(negative_word) != len(base_word) or len(differences) != 2
                or differences[1] != differences[0] + 1
                or base_word[differences[0]] != negative_word[differences[1]]
                or base_word[differences[1]] != negative_word[differences[0]]):
            failures.append("negative_not_a_unique_adjacent_swap:" + str(negative_index))
            continue
        position = differences[0]
        derived_swaps.append({"negative_index": negative_index, "position": position,
                              "symbols": [base_word[position], base_word[position + 1]]})
    normalized_sidecar_swaps = [
        {"negative_index": edge.get("negative_index"), "position": edge.get("position"),
         "symbols": edge.get("symbols")}
        for edge in sidecar.get("swap_edges", [])
    ]
    if derived_swaps != normalized_sidecar_swaps:
        failures.append("sidecar_swap_edges_do_not_rederive_from_frozen_input")
    if (readiness_v5.get("attempts", {}).get("single_historical_long_cell", {}).get("id") != ATTEMPT_ID
            or readiness_v5.get("attempts", {}).get("single_historical_long_cell", {}).get("result_status") != "finest_unique"):
        failures.append("readiness_v5_does_not_reference_historical_long_result")

    argv = capture_manifest.get("command_argv", [])
    if not any(arg.endswith("finest_cli_v2.py") for arg in argv):
        failures.append("v4_cli_not_invoked")
    if not any(arg.endswith("scale_m16_len65536.json") for arg in argv):
        failures.append("wrong_long_case_input_argv")
    if not ("--mode" in argv and "adaptive" in argv and "--seconds" in argv and "28" in argv):
        failures.append("wrong_mode_or_cooperative_deadline")

    output = stdout_path.read_text(encoding="utf-8").strip()
    try:
        result = json.loads(output)
    except json.JSONDecodeError as error:
        result = None
        failures.append("historical_stdout_not_single_json:" + str(error))

    direct_witness = None
    expected_partition = sidecar.get("expected_finest_partition", [])
    if not isinstance(result, dict):
        scientific_status = "invalid_json_output"
    else:
        if result.get("status") != "finest_unique" or result.get("complete") is not True or result.get("decision_complete") is not True:
            failures.append("historical_result_not_complete_unique_finest")
        certificate = result.get("finality_certificate", {})
        edges = certificate.get("must_link_edges", [])
        expected_edges = {tuple(edge["symbols"]) for edge in sidecar.get("swap_edges", [])}
        observed_edges = {tuple(edge.get("symbols", [])) for edge in edges if isinstance(edge, dict)}
        if certificate.get("kind") != "must_link_components_compatible":
            failures.append("long_result_missing_forced_component_certificate")
        if len(edges) != len(sidecar.get("swap_edges", [])) or observed_edges != expected_edges:
            failures.append("long_result_forced_edge_set_mismatch")
        if any(not replay.valid_edge(edge, data) for edge in edges):
            failures.append("long_result_contains_invalid_swap_witness")
        components = replay.dsu_components(data["alphabet"], edges)
        if replay.normalized_partition(components) != replay.normalized_partition(expected_partition):
            failures.append("replayed_forced_components_differ_from_frozen_partition")
        if replay.normalized_partition(certificate.get("components", [])) != replay.normalized_partition(expected_partition):
            failures.append("certificate_components_differ_from_frozen_partition")
        if replay.normalized_partition(result.get("meet_partition", [])) != replay.normalized_partition(expected_partition):
            failures.append("claimed_meet_differs_from_frozen_partition")
        if result.get("uniqueness_scope") != "finest_sample_compatible_partition_not_hidden_architecture":
            failures.append("wrong_uniqueness_scope")
        direct_witness, collision = replay.direct_witness(data, expected_partition)
        if direct_witness is None:
            failures.append("frozen_partition_fails_direct_projection_check")
        elif result.get("finest_witness") != direct_witness:
            failures.append("long_result_projection_witness_replay_mismatch")
        if (len(data.get("alphabet", [])) != 16 or len(data.get("positive", [])) != 1
                or len(data["positive"][0]) != 65536 or len(data.get("negative", [])) != 12
                or len(expected_partition) != 4 or len(edges) != 12):
            failures.append("long_case_shape_not_as_registered")
        stage = result.get("staged_preprocessing", {})
        if stage.get("fallback_used") is not False:
            failures.append("historical_long_run_did_not_use_swap_only_path")
        scientific_status = "accepted_unique_finest_by_replayed_forced_edges" if not failures else "rejected"

    report = {
        "schema_version": 1,
        "status": "accepted" if scientific_status == "accepted_unique_finest_by_replayed_forced_edges" and not failures else "rejected",
        "scientific_status": scientific_status,
        "capture_execution_status": capture_result.get("execution_status"),
        "capture_attempt_id": ATTEMPT_ID,
        "v3_predecessor_censored_attempt_id": "20261101T212905.949382Z_a269d7d6d7",
        "input_sha256": sha_path(input_path),
        "sidecars_sha256": sha_path(sidecars_path),
        "stdout_bytes": stdout_path.stat().st_size,
        "stdout_sha256": sha_path(stdout_path),
        "alphabet_size": len(data.get("alphabet", [])),
        "context_length": len(data.get("positive", [""])[0]),
        "positive_count": len(data.get("positive", [])),
        "negative_count": len(data.get("negative", [])),
        "blocks": len(expected_partition),
        "replayed_forced_edges": len(result.get("finality_certificate", {}).get("must_link_edges", [])) if isinstance(result, dict) else None,
        "provider_seconds_recorded": result.get("metrics", {}).get("provider_seconds") if isinstance(result, dict) else None,
        "subprocess_seconds_recorded": capture_result.get("subprocess_seconds"),
        "official_timing_claim": False,
        "source_checks": len(required_sources),
        "failures": failures,
    }
    report_path = ROOT / "audit" / "scale_v1" / "long_v4_replay_v1.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())

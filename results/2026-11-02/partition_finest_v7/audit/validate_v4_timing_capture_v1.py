#!/usr/bin/env python3
"""Independent post-run validation for one captured C007 v4 timing cell."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
import validate_provider_gate_v3 as replay  # noqa: E402


EXPECTED = {
    "wrapper": "d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de",
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "readiness": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
    "inputs_manifest": "0ff7527b1762105971e6883062ab430f2e29203af50f8cf03d4b1eb2579fff17",
    "corpus": "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b",
    "rgs": "a4216c69d0328419086096ff7b28f7efc39f98fb85ff904d798c5a6f54421281",
    "independent": "290a82bd7fd1cae7d4e0aebb27a6ea90b91148ee47d0963012319d6339680d25",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[2] not in ("adaptive", "reference"):
        raise SystemExit("usage: validate_v4_timing_capture_v1.py ATTEMPT_ID adaptive|reference CASE_ID")
    attempt_id, mode, case_id = sys.argv[1:]
    attempt = ROOT / "evidence" / "attempts" / attempt_id
    input_manifest_path = ROOT / "audit" / "timing_v1" / "input_manifest_v1.json"
    input_manifest = json.loads(input_manifest_path.read_text(encoding="utf-8"))
    case_info = input_manifest["cases"][case_id]
    input_path = ROOT / "audit" / "timing_v1" / case_info["path"]
    rgs_path = ROOT / "audit" / "oracle_v1" / "all_k_rgs.jsonl"
    independent_path = ROOT / "audit" / "oracle_v1" / "all_k_independent_v3.jsonl"
    wrapper = ROOT / "solver.py"
    provider = ROOT / "implementation" / "finest_solver_v4.py"
    cli = ROOT / "implementation" / "finest_cli_v2.py"
    protocol = ROOT / "implementation" / "PROTOCOL_V5.md"
    readiness = ROOT / "implementation" / "READINESS_V4.json"
    capture = ROOT / "evidence" / "capture.py"
    c006 = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005 = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"

    manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    capture_result = json.loads((attempt / "result.json").read_text(encoding="utf-8"))
    stdout_path, stderr_path = attempt / "stdout.bin", attempt / "stderr.bin"
    sources = {
        capture: EXPECTED["capture"], wrapper: EXPECTED["wrapper"],
        provider: EXPECTED["provider"], cli: EXPECTED["cli"],
        protocol: EXPECTED["protocol"], readiness: EXPECTED["readiness"],
        input_path: case_info["sha256"], rgs_path: EXPECTED["rgs"],
        independent_path: EXPECTED["independent"], c006: EXPECTED["c006"], c005: EXPECTED["c005"],
    }
    failures = []
    if file_sha(input_manifest_path) != EXPECTED["inputs_manifest"]:
        failures.append("timing_input_manifest_hash_mismatch")
    corpus_path = ROOT / "audit" / "corpus_v1" / "all_valid_inputs.jsonl"
    if file_sha(corpus_path) != EXPECTED["corpus"]:
        failures.append("source_corpus_hash_mismatch")
    source_map = {entry["path"]: entry for entry in manifest.get("sources", [])}
    for path, expected_sha in sources.items():
        entry = source_map.get(str(path.resolve()))
        if entry is None or entry.get("sha256") != expected_sha:
            failures.append("required_runtime_source_missing_or_drifted:" + path.name)
    for entry in manifest.get("sources", []):
        blob = ROOT / "evidence" / entry.get("snapshot", "")
        if not blob.is_file() or file_sha(blob) != entry.get("sha256"):
            failures.append("captured_source_blob_invalid:" + Path(entry.get("path", "unknown")).name)
    if capture_result.get("attempt_id") != attempt_id or manifest.get("attempt_id") != attempt_id:
        failures.append("attempt_id_mismatch")
    if capture_result.get("execution_status") not in ("success", "program_error", "timed_out"):
        failures.append("unrecognized_capture_execution_status")
    if capture_result.get("child_reaped") is not True:
        failures.append("child_not_reaped")
    if capture_result.get("stdout_sha256") != file_sha(stdout_path):
        failures.append("stdout_hash_mismatch")
    if capture_result.get("stderr_sha256") != file_sha(stderr_path):
        failures.append("stderr_hash_mismatch")
    argv = manifest.get("command_argv", [])
    if (not any(arg.endswith("solver.py") for arg in argv)
            or not any(arg.endswith(Path(case_info["path"]).name) for arg in argv)
            or "--mode" not in argv or mode not in argv
            or "--seconds" not in argv or "28" not in argv):
        failures.append("command_does_not_match_frozen_protocol")

    input_data = json.loads(input_path.read_text(encoding="utf-8"))
    data = {"alphabet": list(input_data["alphabet"]),
            "positive": list(input_data["positive"]), "negative": list(input_data["negative"])}
    oracle_rows = {row["case_id"]: row for row in replay.read_jsonl(rgs_path)}
    independent_rows = {row["case_id"]: row for row in replay.read_jsonl(independent_path)}
    oracle = oracle_rows[case_id]
    direct = independent_rows[case_id]
    if direct.get("unique_finest_by_direct_poset") != oracle.get("meet_compatible"):
        failures.append("rgs_vs_direct_poset_status_mismatch")
    if direct.get("direct_finest_candidates") and replay.normalized_partition(direct["direct_finest_candidates"][0]) != replay.normalized_partition(oracle["meet"]):
        failures.append("rgs_vs_direct_poset_meet_mismatch")

    result = None
    output_text = stdout_path.read_text(encoding="utf-8", errors="replace").strip()
    if output_text:
        try:
            result = json.loads(output_text)
        except json.JSONDecodeError:
            failures.append("stdout_not_one_complete_json_result")
    if result is None:
        scientific_status = "censored_no_parseable_result" if capture_result.get("execution_status") == "timed_out" else "invalid_output"
    elif result.get("status") == "incomplete":
        if result.get("complete") is not False or result.get("decision_complete") is not False:
            failures.append("incomplete_result_claims_finality")
        if result.get("finality_certificate") is not None or result.get("finest_witness") is not None:
            failures.append("incomplete_result_has_final_claim")
        scientific_status = "cooperative_censored_no_finality"
    else:
        valid, reason = replay.replay_result(data, result, oracle)
        if not valid:
            failures.append("independent_result_replay_failed:" + reason)
        if result.get("status") != case_info["all_k_expected_status"]:
            failures.append("result_status_differs_from_frozen_expected_status")
        scientific_status = "accepted_complete_result" if not failures else "rejected"

    report = {
        "schema_version": 1,
        "status": "accepted" if not failures else "rejected",
        "scientific_status": scientific_status,
        "attempt_id": attempt_id,
        "case_id": case_id,
        "mode": mode,
        "capture_execution_status": capture_result.get("execution_status"),
        "exit_code": capture_result.get("exit_code"),
        "child_reaped": capture_result.get("child_reaped"),
        "subprocess_seconds": capture_result.get("subprocess_seconds"),
        "stdout_bytes": capture_result.get("stdout_bytes"),
        "stdout_sha256": capture_result.get("stdout_sha256"),
        "provider_status": result.get("status") if isinstance(result, dict) else None,
        "provider_metrics": result.get("metrics") if isinstance(result, dict) else None,
        "timing_note": "Capture subprocess_seconds is primary; v4 internal stage metrics are diagnostic only and do not partition fallback elapsed time.",
        "failures": failures,
    }
    output_dir = ROOT / "audit" / "timing_v1" / "validations"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{attempt_id}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())

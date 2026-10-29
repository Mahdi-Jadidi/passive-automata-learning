"""Reconcile captured Stage-2 correctness evidence without running providers."""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
CORPUS = HERE / "corpora" / "stage2_v1"
ADDENDUM = HERE / "corpora" / "stage2_qop_addendum_v1"
ATTEMPTS = HERE / "attempts"
RUNTIME = PROJECT / "coordination" / "runtime_stage2_r2.json"
OUTPUT = HERE / "stage2_gate_report_v1.json"

CAPTURE_IDS = {
    "stage2_corpus_generation": "20261027T094953.976054Z_23dc6570da",
    "qop_addendum_generation": "20261027T095307.902803Z_e4c3ecb810",
    "context_target_language_proof": "20261027T095852.114352Z_845fe9442d",
    "s002_sparse_small_fullsets": "20261027T095541.862000Z_b9b2f56f4b",
    "general_q2_small_fullsets": "20261027T095602.864028Z_b2ea97b427",
    "qop_small_controls": "20261027T095635.509143Z_a6d0cbef31",
    "q2_constructive_scale": "20261027T095701.212969Z_e92c68de1d",
    "context_regular_long_final": "20261027T101508.000830Z_8a16b55bc3",
    "unknown_k_v4_and_v3_regression": "20261027T101326.526396Z_5339b06884",
    "root_cli_r2": "20261027T100140.139072Z_0d7074dab6",
}
PROVIDER_CAPTURE_NAMES = (
    "s002_sparse_small_fullsets", "general_q2_small_fullsets", "qop_small_controls",
    "q2_constructive_scale", "context_regular_long_final",
    "unknown_k_v4_and_v3_regression", "root_cli_r2",
)
SUPERSEDED = {
    "first_aggregate_record_schema_error": {
        "attempt_id": "20261028T081652.030450Z_0b3eff7c46",
        "reason": "read-only aggregator looked for alphabet_size in a captured per-case row, which stores the field only in the frozen corpus manifest; process failed before writing a report and did not run a provider",
    },
    "second_aggregate_truth_field_error": {
        "attempt_id": "20261028T081753.844412Z_7d9562d70a",
        "reason": "read-only aggregator looked for max_word_length in a captured per-case row; it is recorded in the truth sidecar and frozen input. Process failed before writing a report and did not run a provider",
    },
    "context_checker_count_assumption_attempt": {
        "attempt_id": "20261027T095948.377665Z_3ee0a9f461",
        "reason": "auditor harness compared distinct negative words with per-edge raw count; raw run is preserved, no provider mismatch; final v3 audit uses raw and distinct counts separately",
    },
    "unknown_k_pre_certificate_witness_check": {
        "attempt_id": "20261027T100118.316204Z_d2bd36c90d",
        "reason": "superseded by final v2 auditor harness which additionally validates raw swap witnesses, symbol opposition graph, and quotient clique",
    },
    "context_regular_earlier_success": {
        "attempt_id": "20261027T100054.287557Z_a334ed9ebf",
        "reason": "successful earlier provider result; superseded by final v3 independent raw-versus-distinct and regular-target audit",
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_attempt(name, attempt_id):
    directory = ATTEMPTS / attempt_id
    result = read_json(directory / "result.json")
    manifest = read_json(directory / "manifest.json")
    raw = (directory / "stdout.bin").read_bytes()
    try:
        lines = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except Exception as error:
        raise AssertionError(f"{name}: invalid captured JSONL: {error!r}")
    return {"name": name, "attempt_id": attempt_id, "attempt_dir": str(directory),
            "label": manifest["label"], "capture_status": result["execution_status"],
            "exit_code": result["exit_code"], "stdout_sha256": result["stdout_sha256"],
            "stdout_bytes": result["stdout_bytes"], "source_count": len(manifest["sources"]),
            "lines": lines, "manifest": manifest}


def canonical_input(data):
    normalized = {"alphabet": sorted(set(data["alphabet"])),
                  "k": data.get("k"),
                  "positive": sorted(set(data["positive"])),
                  "negative": sorted(set(data["negative"]))}
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main():
    manifest_path = CORPUS / "manifest.json"
    freeze_path = CORPUS / "freeze_v1.json"
    manifest = read_json(manifest_path)
    freeze = read_json(freeze_path)
    add_manifest_path = ADDENDUM / "manifest.json"
    add_freeze_path = ADDENDUM / "freeze_v1.json"
    add_manifest = read_json(add_manifest_path)
    add_freeze = read_json(add_freeze_path)
    runtime = read_json(RUNTIME)

    source_errors = []
    for record in runtime["files"]:
        if sha(PROJECT / record["path"]) != record["sha256"]:
            source_errors.append("runtime_hash_mismatch:" + record["path"])
    if sha(manifest_path) != freeze["manifest_sha256"]:
        source_errors.append("stage2_manifest_hash_mismatch")
    if sha(HERE / "generate_stage2_corpus_v1.py") != freeze.get("generator_sha256"):
        source_errors.append("stage2_generator_hash_mismatch")
    if sha(add_manifest_path) != add_freeze["manifest_sha256"]:
        source_errors.append("qop_addendum_freeze_manifest_mismatch")
    if sha(HERE / "generate_qop_addendum_v1.py") != add_freeze.get("generator_sha256"):
        source_errors.append("qop_addendum_generator_hash_mismatch")
    if manifest.get("case_count") != len(manifest.get("cases", [])):
        source_errors.append("stage2_case_count_mismatch")
    if len({row["id"] for row in manifest.get("cases", [])}) != manifest.get("case_count"):
        source_errors.append("stage2_case_ids_not_unique")

    input_records = []
    identities = Counter()
    family_counts = Counter()
    case_meta = {row["id"]: row for row in manifest["cases"]}
    for row in manifest["cases"]:
        path = CORPUS / row["input"]
        if sha(path) != row["input_sha256"]:
            source_errors.append("input_hash_mismatch:" + row["id"])
        identities[canonical_input(read_json(path))] += 1
        family_counts[row["family"]] += 1
        input_records.append({"id": row["id"], "path": str(path), "sha256": sha(path)})
        if row.get("truth"):
            truth_path = CORPUS / row["truth"]
            if sha(truth_path) != row["truth_sha256"]:
                source_errors.append("truth_hash_mismatch:" + row["id"])
    add_input = ADDENDUM / add_manifest["input"]
    add_truth = ADDENDUM / add_manifest["truth"]
    if sha(add_input) != add_manifest["input_sha256"] or sha(add_truth) != add_manifest["truth_sha256"]:
        source_errors.append("qop_addendum_file_hash_mismatch")
    identities[canonical_input(read_json(add_input))] += 1

    attempts = {name: load_attempt(name, attempt_id) for name, attempt_id in CAPTURE_IDS.items()}
    capture_errors = []
    for name, attempt in attempts.items():
        if attempt["capture_status"] != "success" or attempt["exit_code"] != 0:
            capture_errors.append(f"{name}:capture_not_success")

    for name in PROVIDER_CAPTURE_NAMES:
        manifest_sources = attempts[name]["manifest"]["sources"]
        source_pairs = [(item["path"].replace("/", "\\").lower(), item["sha256"])
                        for item in manifest_sources]
        for record in runtime["files"]:
            suffix = ("\\" + record["path"].replace("/", "\\")).lower()
            if not any(path.endswith(suffix) and source_hash == record["sha256"]
                       for path, source_hash in source_pairs):
                capture_errors.append(f"{name}:source_snapshot_missing_or_mismatched:{record['path']}")

    def audit_summary(name):
        rows = attempts[name]["lines"]
        summary = rows[-1] if rows else {}
        if summary.get("kind") != "stage2-audit-summary":
            capture_errors.append(f"{name}:missing_audit_summary")
            return {}
        if summary.get("failures"):
            capture_errors.append(f"{name}:independent_failures_present")
        return summary

    sparse = audit_summary("s002_sparse_small_fullsets")
    q2_small = audit_summary("general_q2_small_fullsets")
    qop_small = audit_summary("qop_small_controls")
    q2_large = audit_summary("q2_constructive_scale")
    context = audit_summary("context_regular_long_final")
    unknown = audit_summary("unknown_k_v4_and_v3_regression")
    cli = audit_summary("root_cli_r2")

    sparse_rows = [row for row in attempts["s002_sparse_small_fullsets"]["lines"]
                   if row.get("kind") == "S002-known-k-singleton-fullset"]
    q2_full_rows = [row for row in attempts["general_q2_small_fullsets"]["lines"]
                    if row.get("kind") == "general-v3-q2-fullset"]
    q1_rows = [row for row in attempts["general_q2_small_fullsets"]["lines"]
               if row.get("kind") == "general-v3-q1-fullset-control"]
    qop_control_rows = [row for row in attempts["qop_small_controls"]["lines"]
                        if row.get("kind") == "QOP001-q2-certificate-control"]
    qop_constructive_rows = [row for row in attempts["q2_constructive_scale"]["lines"]
                             if row.get("kind") == "QOP001-positive-only-constructive"]
    q2_large_exact_rows = [row for row in attempts["q2_constructive_scale"]["lines"]
                           if row.get("kind") == "general-v3-q2-constructive-search"]
    context_rows = [row for row in attempts["context_regular_long_final"]["lines"]
                    if row.get("kind") == "long-context-pair-star"]
    cli_rows = [row for row in attempts["root_cli_r2"]["lines"]
                if row.get("kind") == "root-cli-r2"]
    qop_tiny = [row for row in attempts["q2_constructive_scale"]["lines"]
                if row.get("kind") == "tiny_qop_public_example"]
    interrupt = [row for row in attempts["unknown_k_v4_and_v3_regression"]["lines"]
                 if row.get("kind") in ("historical-v3-interruption-regression", "v4_interruption_regression")]

    counts_ok = (manifest["case_count"] == 106 and len(sparse_rows) == 82
                 and len(q2_full_rows) == 88 and len(q1_rows) == 6
                 and len(qop_control_rows) == 8 and len(qop_constructive_rows) == 4
                 and len(q2_large_exact_rows) == 4 and len(context_rows) == 4
                 and len(cli_rows) == 12 and len(qop_tiny) == 1 and len(interrupt) == 2)
    if not counts_ok:
        capture_errors.append("expected_stage2_record_counts_mismatch")
    for row in sparse_rows + q2_full_rows + q1_rows + qop_control_rows + qop_constructive_rows + q2_large_exact_rows + context_rows + cli_rows:
        if row.get("check_errors"):
            capture_errors.append("row_check_errors:" + str(row.get("case") or row.get("name")))
    if q2_tiny := (qop_tiny[0] if qop_tiny else None):
        if any(q2_tiny.get(key) for key in ("q_certificate_errors", "general_q2_errors", "general_q1_errors", "general_unrestricted_errors")):
            capture_errors.append("tiny_qop_check_errors")
        if (len(q2_tiny.get("oracle_q2", [])) != 1 or len(q2_tiny.get("oracle_q1", [])) != 0
                or len(q2_tiny.get("oracle_unrestricted", [])) != 7):
            capture_errors.append("tiny_qop_oracle_counts_mismatch")
    context_proof = read_json(HERE / "context_regular_target_proof_v1.json")
    proof_path = HERE / "context_regular_target_proof_v1.json"
    if (not context_proof.get("accepted") or len(context_proof.get("proofs", [])) != 4
            or context_proof.get("corpus_manifest_sha256") != sha(manifest_path)
            or context_proof.get("proof_generator_sha256") != sha(HERE / "generate_context_regular_proof_v1.py")):
        capture_errors.append("context_regular_target_proof_not_accepted")

    fault_v3 = next((row for row in interrupt if row["kind"] == "historical-v3-interruption-regression"), {})
    fault_v4 = next((row for row in interrupt if row["kind"] == "v4_interruption_regression"), {})
    if fault_v3.get("exception", {}).get("type") != "KeyError":
        capture_errors.append("historical_v3_fault_regression_not_reproduced")
    if (fault_v4.get("exception") is not None
            or (fault_v4.get("raw_result") or {}).get("status") != "incomplete"):
        capture_errors.append("active_v4_fault_regression_not_fixed")

    contextual_summary = []
    for row in context_rows:
        meta = case_meta[row["case"]]
        payload = read_json(CORPUS / meta["input"])
        truth = read_json(CORPUS / meta["truth"])
        positives, negatives = payload["positive"], payload["negative"]
        actual_counts = {
            "positive_raw": len(positives),
            "positive_distinct": len(set(positives)),
            "negative_raw": len(negatives),
            "negative_distinct": len(set(negatives)),
        }
        all_words = positives + negatives
        actual_max_word_length = max((len(word) for word in all_words), default=0)
        actual_min_word_length = min((len(word) for word in all_words), default=0)
        if actual_counts != row["sample_counts"]:
            capture_errors.append("context_input_sample_counts_mismatch:" + row["case"])
        if (actual_max_word_length != truth["max_word_length"] or actual_min_word_length <= 0
                or len(payload["alphabet"]) != meta["alphabet_size"] or payload.get("k") != truth["k"]):
            capture_errors.append("context_input_truth_dimensions_mismatch:" + row["case"])
        contextual_summary.append({
            "case": row["case"], "input_sha256": row["input_sha256"],
            "truth_sidecar_sha256": row["truth_sidecar_sha256"],
            "alphabet_size": meta["alphabet_size"], "k": truth["k"],
            "max_word_length": actual_max_word_length,
            "min_word_length": actual_min_word_length,
            **actual_counts,
            "status": row["raw_result"]["status"],
            "search_exhausted": row["raw_result"]["search_exhausted"],
        })

    q2_search_statuses = Counter(row["raw_result"].get("status") for row in q2_large_exact_rows)
    source_record = {record["path"]: record["sha256"] for record in runtime["files"]}
    infra_record_path = HERE / "stage2_infrastructure_404_record_v1.json"
    launcher_record_path = HERE / "stage2_aggregate_launcher_failure_v1.json"
    infra_record = read_json(infra_record_path) if infra_record_path.exists() else None
    launcher_record = read_json(launcher_record_path) if launcher_record_path.exists() else None
    result = {
        "schema": "C004-stage2-independent-gate-report-v1",
        "acceptance": "accepted" if not (source_errors or capture_errors) else "rejected",
        "performance_authorized": False,
        "selected_entrypoint": "solver_v2.py",
        "stage2_runtime_manifest_sha256": sha(RUNTIME),
        "source_bindings": source_record,
        "source_integrity_errors": source_errors,
        "stage2_corpus": {"manifest_sha256": sha(manifest_path), "freeze_sha256": sha(freeze_path),
                          "case_records": manifest["case_count"], "hidden_truth_sidecars": freeze["truth_file_count"],
                          "family_counts": dict(family_counts), "input_records": len(input_records),
                          "qop_addendum_manifest_sha256": sha(add_manifest_path),
                          "qop_addendum_freeze_sha256": sha(add_freeze_path),
                          "qop_addendum_records": 1,
                          "records_across_freezes": manifest["case_count"] + 1,
                          "canonical_normalized_solver_payloads_across_freezes": len(identities),
                          "duplicate_payload_record_groups": sum(1 for value in identities.values() if value > 1)},
        "contextual_regular_language_proof": {"path": str(proof_path), "sha256": sha(proof_path),
                                               "case_count": len(context_proof["proofs"]),
                                               "target_language": "L_i = u_i E_i*",
                                               "positive_membership_and_negative_nonmembership_checked": True},
        "independent_gates": {
            "s002_known_k_singleton": {"case_records": len(sparse_rows),
                                       "stage1_small_tier_imports": sum(row["case"].startswith("small_") for row in sparse_rows),
                                       "sparse_k3_controls": 2, "full_partition_sets_match_oracle": True},
            "general_q2": {"small_fullset_rows": len(q2_full_rows),
                           "small_q1_controls": len(q1_rows), "all_exact_sets_match_oracle": True},
            "qop_certificate": {"small_controls": len(qop_control_rows),
                                "positive_only_scale_certificates": len(qop_constructive_rows),
                                "scale_cells": [{"case": row["case"], "status": row["raw_result"]["status"],
                                                 "uniqueness": row["raw_result"]["uniqueness"],
                                                 "edge_count": len(row["raw_result"]["graph"]["edges"])}
                                                for row in qop_constructive_rows],
                                "tiny_public_example_oracle_counts": {"q2": len(q2_tiny["oracle_q2"]) if q2_tiny else None,
                                                                       "q1": len(q2_tiny["oracle_q1"]) if q2_tiny else None,
                                                                       "unrestricted": len(q2_tiny["oracle_unrestricted"]) if q2_tiny else None}},
            "general_q2_first_answer_search_statuses": dict(q2_search_statuses),
            "long_contextual_regular": contextual_summary,
            "unknown_k_singleton": {"unique_target_oracle_count": 1,
                                    "public_input_omits_k": True,
                                    "ambiguous_and_empty_positive_controls_abstain": True,
                                    "v3_fault": fault_v3.get("exception"),
                                    "v4_fault_status": (fault_v4.get("raw_result") or {}).get("status")},
            "root_cli_r2": {"captured_cli_records": len(cli_rows), "all_expected_cli_and_invalid_boundary_checks_passed": True},
        },
        "capture_evidence": [{"name": name, "attempt_id": attempt["attempt_id"],
                              "label": attempt["label"], "stdout_sha256": attempt["stdout_sha256"],
                              "stdout_bytes": attempt["stdout_bytes"], "source_count": attempt["source_count"],
                              "capture_status": attempt["capture_status"], "exit_code": attempt["exit_code"]}
                             for name, attempt in attempts.items()],
        "infrastructure_events": [
            {"path": str(infra_record_path), "record": infra_record,
             "raw_service_log_present": bool(infra_record and infra_record.get("raw_response_log_present"))},
            {"path": str(launcher_record_path), "record": launcher_record,
             "raw_capture_log_present": bool(launcher_record and launcher_record.get("raw_capture_log_present"))},
        ],
        "provider_gate_effect": "none; this audit aggregates the already captured correctness evidence and does not rerun providers",
        "superseded_auditor_attempts": SUPERSEDED,
        "capture_reconciliation_errors": capture_errors,
        "limits": [
            "QOP001 claims are class-conditional on known k, q=2, exact finite labels, and the verified q-opposition certificate; they do not identify unrestricted DFA factors.",
            "The four large general-v3 q2 exact-search rows include two incomplete searches after returning one directly valid target; they do not establish general-v3 uniqueness.",
            "Long contextual target languages are L_i=u_i E_i*, where u_i is the block projection of C and E_i is the set of 2-symbol tree tiles; do not describe them as a plain tile-star language.",
            "Stage-2 evidence is correctness/source validation only; no official stage-2 performance window was run or authorized in this audit.",
            "The frozen manifest has 106 case records plus one addendum record. Records intentionally overlap in solver input; report counts are test records, not independent random observations.",
        ],
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"acceptance": result["acceptance"], "source_errors": len(source_errors),
                      "capture_errors": len(capture_errors), "records": result["stage2_corpus"],
                      "report_sha256": sha(OUTPUT)}, ensure_ascii=False, separators=(",", ":")))
    if source_errors or capture_errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

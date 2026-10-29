"""Independently validate and reconcile the already captured Stage2 timing outputs."""
from __future__ import annotations
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ATTEMPTS = HERE / "attempts"
PROTO_PATH = HERE / "stage2_timing_protocol_v1.json"
FREEZE_PATH = HERE / "stage2_timing_protocol_freeze_v1.json"
LEDGER_PATH = HERE / "stage2_timing_execution_ledger_v1.json"
REPORT_PATH = HERE / "stage2_timing_report_v1.json"
CORPUS_DIR = HERE / "corpora" / "stage2_v1"

def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def canon_blocks(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))

def project(word: str, block: set[str]) -> str:
    return "".join(ch for ch in word if ch in block)

def check_partition(blocks, alphabet, k):
    errors = []
    if not isinstance(blocks, list) or len(blocks) != k:
        return ["partition_block_count"]
    flat = [ch for block in blocks for ch in block]
    if any(not block for block in blocks):
        errors.append("empty_block")
    if len(flat) != len(set(flat)):
        errors.append("overlapping_blocks")
    if set(flat) != set(alphabet):
        errors.append("partition_alphabet_coverage")
    return errors

def expected_q2_edges(data, target_blocks):
    alphabet = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    target_owner = {symbol: i for i, block in enumerate(target_blocks) for symbol in block}
    edges = set()
    target_cross = set()
    exact_projection_counts = {}
    for i, a in enumerate(alphabet):
        for b in alphabet[i + 1:]:
            pair = {a, b}
            projections = {project(word, pair) for word in positives}
            key = (a, b)
            exact_projection_counts[key] = projections
            if len(projections) > 2:
                edges.add(key)
            if target_owner[a] != target_owner[b]:
                target_cross.add(key)
    return edges, target_cross, exact_projection_counts

def main() -> None:
    protocol_raw = PROTO_PATH.read_bytes()
    protocol_hash = sha_bytes(protocol_raw)
    protocol = json.loads(protocol_raw.decode("utf-8-sig"))
    freeze = read_json(FREEZE_PATH)
    ledger = read_json(LEDGER_PATH)
    corpus_manifest_path = CORPUS_DIR / "manifest.json"
    corpus_freeze_path = CORPUS_DIR / "freeze_v1.json"
    corpus_manifest = read_json(corpus_manifest_path)
    corpus_freeze = read_json(corpus_freeze_path)
    corpus_by_id = {row["id"]: row for row in corpus_manifest["cases"]}

    errors = []
    if freeze.get("protocol_sha256") != protocol_hash:
        errors.append("active_protocol_freeze_hash_mismatch")
    if ledger.get("protocol_sha256") != protocol_hash:
        errors.append("ledger_protocol_hash_mismatch")
    if protocol.get("status") != "frozen" or protocol.get("authorization") != "master_serial_timing_go":
        errors.append("active_protocol_not_authorized_frozen")
    if protocol.get("wall_schedule") is None or protocol.get("memory_schedule") is None:
        errors.append("schedule_missing")
    expected_jobs = protocol.get("wall_schedule", []) + protocol.get("memory_schedule", [])
    ledger_jobs = ledger.get("jobs", [])
    if len(ledger_jobs) != 15 or len(expected_jobs) != 15:
        errors.append("scheduled_job_count_mismatch")
    if [row.get("job_id") for row in ledger_jobs] != [row.get("job_id") for row in expected_jobs]:
        errors.append("ledger_schedule_order_mismatch")

    for rel, expected in protocol["source_bindings"].items():
        path = PROJECT / rel
        if not path.is_file() or sha(path) != expected:
            errors.append("current_source_binding_mismatch:" + rel)
    if sha(corpus_manifest_path) != protocol["stage2_corpus_manifest_sha256"]:
        errors.append("stage2_corpus_manifest_hash_mismatch")
    if sha(corpus_freeze_path) != protocol["stage2_corpus_freeze_sha256"]:
        errors.append("stage2_corpus_freeze_hash_mismatch")

    parsed = []
    source_snapshot_records = []
    child_pids = set()
    measured_by_provider = defaultdict(float)
    grouped_wall = defaultdict(list)
    memory_rows = []
    qop_oracles = {}
    qop_edge_counts = {}

    for expected, entry in zip(expected_jobs, ledger_jobs):
        job_errors = []
        for key in ("job_id", "order", "phase", "case", "rep", "method", "memory"):
            if entry.get(key) != expected.get(key):
                job_errors.append("ledger_field_mismatch:" + key)
        if entry.get("protocol_sha256") != protocol_hash:
            job_errors.append("job_protocol_hash_mismatch")
        attempt_id = entry.get("attempt_id")
        attempt_dir = ATTEMPTS / str(attempt_id)
        try:
            capture_result = read_json(attempt_dir / "result.json")
            capture_manifest = read_json(attempt_dir / "manifest.json")
            raw_stdout = (attempt_dir / "stdout.bin").read_bytes()
            raw_stderr = (attempt_dir / "stderr.bin").read_bytes()
        except Exception as exc:
            errors.append(f"{entry.get('job_id')}:capture_artifact_unreadable:{type(exc).__name__}")
            continue
        if capture_result.get("attempt_id") != attempt_id or capture_manifest.get("attempt_id") != attempt_id:
            job_errors.append("capture_attempt_id_mismatch")
        if capture_result.get("execution_status") != "success" or capture_result.get("exit_code") != 0:
            job_errors.append("capture_not_success")
        if entry.get("execution_status") != capture_result.get("execution_status") or entry.get("exit_code") != capture_result.get("exit_code"):
            job_errors.append("ledger_capture_status_mismatch")
        if capture_result.get("stdout_sha256") != sha_bytes(raw_stdout) or capture_result.get("stderr_sha256") != sha_bytes(raw_stderr):
            job_errors.append("captured_stream_hash_mismatch")
        if capture_result.get("stdout_bytes") != len(raw_stdout) or capture_result.get("stderr_bytes") != len(raw_stderr):
            job_errors.append("captured_stream_byte_count_mismatch")
        if (entry.get("stdout_sha256") != capture_result.get("stdout_sha256")
                or entry.get("stderr_sha256") != capture_result.get("stderr_sha256")
                or entry.get("stdout_bytes") != capture_result.get("stdout_bytes")
                or entry.get("stderr_bytes") != capture_result.get("stderr_bytes")):
            job_errors.append("ledger_capture_stream_mismatch")
        wall = capture_result.get("subprocess_seconds")
        if not isinstance(wall, (int, float)) or wall < 0 or wall > 30.0:
            job_errors.append("hard_timeout_wall_violation")
        if capture_manifest.get("timeout_seconds") != 30.0:
            job_errors.append("capture_hard_timeout_not_30s")
        child_pid = capture_result.get("child_pid")
        if child_pid in child_pids:
            job_errors.append("child_process_not_fresh")
        child_pids.add(child_pid)
        measured_by_provider[entry["method"]] += float(wall or 0.0)

        source_map = {}
        for source in capture_manifest.get("sources", []):
            source_map[str(Path(source["path"]).resolve()).lower()] = source["sha256"]
        for rel, digest in protocol["source_bindings"].items():
            expected_path = str((PROJECT / rel).resolve()).lower()
            if source_map.get(expected_path) != digest:
                job_errors.append("source_snapshot_missing_or_mismatch:" + rel)
        case_meta = protocol["cases"][entry["case"]]
        input_path = HERE / case_meta["input_path"]
        input_digest = case_meta["input_sha256"]
        if sha(input_path) != input_digest:
            job_errors.append("public_input_hash_changed")
        if source_map.get(str(input_path.resolve()).lower()) != input_digest:
            job_errors.append("public_input_snapshot_missing_or_mismatch")
        corpus_row = corpus_by_id[case_meta["case_id"]]
        truth_path = CORPUS_DIR / corpus_row["truth"]
        truth_digest = corpus_row["truth_sha256"]
        if sha(truth_path) != truth_digest:
            job_errors.append("hidden_truth_hash_changed_after_capture")
        if source_map.get(str(truth_path.resolve()).lower()) != truth_digest:
            job_errors.append("hidden_truth_snapshot_missing_or_mismatch")
        command_argv = capture_manifest.get("command_argv", [])
        if any(corpus_row["truth"].lower() in arg.lower() for arg in command_argv):
            job_errors.append("hidden_truth_path_passed_to_timed_child")
        if any(case_meta["input_path"].lower() in arg.lower() for arg in command_argv):
            job_errors.append("input_path_not_loaded_from_frozen_protocol")

        try:
            envelope = json.loads(raw_stdout.decode("utf-8"))
        except Exception as exc:
            job_errors.append("full_result_json_parse_error:" + type(exc).__name__)
            envelope = None
        if not envelope:
            errors.extend(entry["job_id"] + ":" + e for e in job_errors)
            continue
        if envelope.get("schema") != "C004-stage2-full-api-timing-v1":
            job_errors.append("timed_envelope_schema_mismatch")
        if envelope.get("protocol_sha256") != protocol_hash:
            job_errors.append("child_protocol_hash_mismatch")
        if (envelope.get("method") != entry["method"] or envelope.get("case") != entry["case"]
                or envelope.get("max_solutions") != 2 or envelope.get("local_word_cap") != 2
                or envelope.get("soft_deadline_seconds_from_child_entry") != 29.0):
            job_errors.append("timed_envelope_call_parameters_mismatch")

        payload = read_json(input_path)
        truth = read_json(truth_path)
        target = canon_blocks(truth["target_blocks"])
        result = envelope.get("result") or {}
        if not result or not isinstance(result.get("solutions"), list):
            job_errors.append("full_api_result_missing_solutions")
            solutions = []
        else:
            solutions = result["solutions"]
        if len(solutions) != 1:
            job_errors.append("expected_one_valid_first_answer")
        k = int(payload["k"])
        alphabet = payload["alphabet"]
        positives = sorted(set(payload["positive"]))
        if envelope.get("k") != k or result.get("k") != k or result.get("local_word_cap") != 2:
            job_errors.append("provider_k_or_cap_mismatch")
        for sol_idx, solution in enumerate(solutions):
            blocks = solution.get("blocks", [])
            job_errors.extend(f"solution{sol_idx}:{e}" for e in check_partition(blocks, alphabet, k))
            if canon_blocks(blocks) != target:
                job_errors.append(f"solution{sol_idx}:target_partition_mismatch")
            languages = solution.get("positive_projection_languages")
            if not isinstance(languages, list) or len(languages) != len(blocks):
                job_errors.append(f"solution{sol_idx}:local_language_count_mismatch")
            else:
                for block_idx, block in enumerate(blocks):
                    block_set = set(block)
                    expected_language = sorted({project(word, block_set) for word in positives})
                    emitted_language = sorted(set(languages[block_idx]))
                    if emitted_language != expected_language:
                        job_errors.append(f"solution{sol_idx}:projection_language_mismatch:{block_idx}")
                    if len(emitted_language) > 2:
                        job_errors.append(f"solution{sol_idx}:q2_cap_violation:{block_idx}")
                    if any(project(word, block_set) not in set(emitted_language) for word in positives):
                        job_errors.append(f"solution{sol_idx}:positive_projection_not_accepted:{block_idx}")
            if solution.get("negative_witnesses", []) != []:
                job_errors.append(f"solution{sol_idx}:unexpected_negative_witnesses")

        status = result.get("status")
        exhausted = result.get("search_exhausted")
        uniqueness = result.get("uniqueness")
        if entry["method"] == "general_v3_q2":
            if status == "found":
                if not exhausted or uniqueness != "unique":
                    job_errors.append("general_found_not_exhausted_unique")
            elif status == "incomplete":
                if exhausted or uniqueness != "unknown":
                    job_errors.append("general_incomplete_state_mismatch")
            else:
                job_errors.append("general_unexpected_status")
        else:
            if status != "found" or not exhausted or uniqueness != "unique":
                job_errors.append("qop_certificate_not_unique_found")
            graph = result.get("graph") or {}
            certificate = result.get("certificate") or {}
            target_edges, target_cross_edges, projection_map = qop_oracles.get(entry["case"], (None, None, None))
            if target_edges is None:
                target_edges, target_cross_edges, projection_map = expected_q2_edges(payload, truth["target_blocks"])
                qop_oracles[entry["case"]] = (target_edges, target_cross_edges, projection_map)
            emitted_edges = {tuple(sorted(edge)) for edge in graph.get("edges", [])}
            if emitted_edges != target_edges or target_edges != target_cross_edges:
                job_errors.append("qop_opposition_graph_not_exact_target_complete_multipartite")
            if len(emitted_edges) != len(graph.get("edges", [])):
                job_errors.append("qop_duplicate_graph_edge")
            if graph.get("construction_complete") is not True or graph.get("q") != 2:
                job_errors.append("qop_graph_incomplete_or_wrong_q")
            witnesses = graph.get("edge_witnesses", [])
            if len(witnesses) != len(emitted_edges):
                job_errors.append("qop_edge_witness_count_mismatch")
            pos_order = sorted(set(payload["positive"]))
            for witness in witnesses:
                pair = tuple(sorted(witness.get("symbols", [])))
                indices = witness.get("positive_indices", [])
                pair_projections = witness.get("pair_projections", [])
                if pair not in emitted_edges or len(indices) != len(pair_projections) or len(set(pair_projections)) <= 2:
                    job_errors.append("qop_edge_witness_shape_or_threshold_error")
                    continue
                if any(not isinstance(idx, int) or idx < 0 or idx >= len(pos_order) for idx in indices):
                    job_errors.append("qop_edge_witness_index_invalid")
                    continue
                for idx, witness_projection in zip(indices, pair_projections):
                    if project(pos_order[idx], set(pair)) != witness_projection:
                        job_errors.append("qop_edge_witness_projection_mismatch")
                        break
            if (certificate.get("q") != 2 or certificate.get("unique_q_opposition_coloring") is not True
                    or certificate.get("kind") != "q_complete_k_partite_opposition"
                    or canon_blocks(certificate.get("blocks", [])) != target):
                job_errors.append("qop_unique_coloring_certificate_mismatch")
            qop_edge_counts[entry["case"]] = len(emitted_edges)

        metrics = result.get("metrics") or {}
        provider_seconds = metrics.get("provider_seconds")
        if not isinstance(provider_seconds, (int, float)) or provider_seconds < 0 or provider_seconds > 29.0:
            job_errors.append("provider_soft_deadline_metric_invalid")
        if entry["method"] == "general_v3_q2":
            nodes = metrics.get("nodes")
            if not isinstance(nodes, int) or nodes < 0:
                job_errors.append("general_search_nodes_missing")
        if entry["phase"] == "wall":
            grouped_wall[(entry["case"], entry["method"])].append({
                "rep": entry["rep"], "wall_seconds": float(wall),
                "provider_seconds": float(provider_seconds),
                "stdout_bytes": len(raw_stdout), "status": status,
                "uniqueness": uniqueness, "search_exhausted": exhausted,
                "solution_count": len(solutions), "search_nodes": metrics.get("nodes"),
                "pair_tests": metrics.get("pair_tests"), "output_sha256": sha_bytes(raw_stdout),
                "attempt_id": attempt_id,
            })
        else:
            if not entry["memory"]:
                job_errors.append("memory_phase_flag_mismatch")
            try:
                stderr_obj = json.loads(raw_stderr.decode("utf-8").strip())
            except Exception:
                stderr_obj = {}
                job_errors.append("memory_stderr_json_invalid")
            if (stderr_obj.get("schema") != "C004-python-tracemalloc-v1"
                    or not isinstance(stderr_obj.get("peak_traced_python_bytes"), int)
                    or stderr_obj["peak_traced_python_bytes"] <= 0):
                job_errors.append("memory_tracemalloc_metric_missing")
            memory_rows.append({
                "job_id": entry["job_id"], "case": entry["case"], "method": entry["method"],
                "wall_seconds_separate_memory_run": float(wall),
                "peak_traced_python_bytes": stderr_obj.get("peak_traced_python_bytes"),
                "not_rss": True, "provider_seconds": provider_seconds,
                "stdout_bytes": len(raw_stdout), "status": status,
                "search_exhausted": exhausted, "uniqueness": uniqueness,
                "search_nodes": metrics.get("nodes"), "attempt_id": attempt_id,
            })
        errors.extend(entry["job_id"] + ":" + e for e in job_errors)
        parsed.append({"job_id": entry["job_id"], "attempt_id": attempt_id,
                       "method": entry["method"], "case": entry["case"], "phase": entry["phase"],
                       "wall_seconds": float(wall), "stdout_bytes": len(raw_stdout),
                       "stdout_sha256": sha_bytes(raw_stdout), "status": status,
                       "uniqueness": uniqueness, "search_exhausted": exhausted,
                       "solutions": len(solutions), "provider_seconds": provider_seconds,
                       "search_nodes": metrics.get("nodes"), "pair_tests": metrics.get("pair_tests"),
                       "tracemalloc_peak_bytes": (json.loads(raw_stderr.decode("utf-8").strip()).get("peak_traced_python_bytes") if entry["memory"] and raw_stderr else None)})
        source_snapshot_records.append({"attempt_id": attempt_id, "count": len(capture_manifest.get("sources", [])),
                                        "source_manifest_sha256": sha(attempt_dir / "manifest.json")})

    expected_group_keys = {(case, method) for case in protocol["cases"]
                           for method in protocol["methods"]}
    for key in sorted(expected_group_keys):
        rows = grouped_wall.get(key, [])
        if len(rows) != 3 or [row["rep"] for row in rows] != [1, 2, 3]:
            errors.append(f"wall_repetition_count_or_order_mismatch:{key[0]}:{key[1]}")
    if len(memory_rows) != 3:
        errors.append("memory_job_count_mismatch")

    summary = {}
    for (case, method), rows in grouped_wall.items():
        times = [row["wall_seconds"] for row in rows]
        summary.setdefault(case, {})[method] = {
            "wall_seconds_by_rep": times,
            "median_wall_seconds": statistics.median(times),
            "min_wall_seconds": min(times), "max_wall_seconds": max(times),
            "provider_seconds_by_rep": [row["provider_seconds"] for row in rows],
            "median_provider_seconds": statistics.median(row["provider_seconds"] for row in rows),
            "output_bytes_by_rep": [row["stdout_bytes"] for row in rows],
            "median_output_bytes": statistics.median(row["stdout_bytes"] for row in rows),
            "search_statuses": dict(Counter(row["status"] for row in rows)),
            "uniqueness_statuses": dict(Counter(row["uniqueness"] for row in rows)),
            "search_exhausted_by_rep": [row["search_exhausted"] for row in rows],
            "solution_count_by_rep": [row["solution_count"] for row in rows],
            "search_nodes_by_rep": [row["search_nodes"] for row in rows],
            "pair_tests_by_rep": [row["pair_tests"] for row in rows],
            "attempt_ids": [row["attempt_id"] for row in rows],
        }

    stage1_report_path = HERE / "stage1_performance_report_v2.json"
    stage1_report = read_json(stage1_report_path)
    stage1_general = stage1_report["measured_seconds"]["standard_and_stress_by_provider"]["general-v3"]
    stage2_wall_by_method = {
        method: sum(row["wall_seconds"] for (case_name, row_method), rows in grouped_wall.items()
                    for row in rows if row_method == method)
        for method in protocol["methods"]
    }
    stage2_mem_wall_by_method = {
        method: sum(row["wall_seconds_separate_memory_run"] for row in memory_rows
                    if row["method"] == method)
        for method in protocol["methods"]
    }
    stage2_general_total = stage2_wall_by_method["general_v3_q2"] + stage2_mem_wall_by_method["general_v3_q2"]
    budget = {
        "limit_per_provider_seconds": 900.0,
        "general_v3": {
            "stage1_standard_and_stress_seconds": stage1_general,
            "stage1_memory_runs_excluded_from_wall_budget": True,
            "stage2_wall_jobs_seconds": stage2_wall_by_method["general_v3_q2"],
            "stage2_separate_memory_job_wall_seconds": stage2_mem_wall_by_method["general_v3_q2"],
            "combined_measured_invocation_seconds": stage1_general + stage2_general_total,
            "within_limit": stage1_general + stage2_general_total <= 900.0,
        },
        "qop001": {
            "prior_stage1_budget_seconds": 0.0,
            "stage2_wall_jobs_seconds": stage2_wall_by_method["qop001_q2"],
            "stage2_separate_memory_job_wall_seconds": stage2_mem_wall_by_method["qop001_q2"],
            "combined_measured_invocation_seconds": stage2_wall_by_method["qop001_q2"] + stage2_mem_wall_by_method["qop001_q2"],
            "within_limit": stage2_wall_by_method["qop001_q2"] + stage2_mem_wall_by_method["qop001_q2"] <= 900.0,
        },
    }

    preserve_path = HERE / "stage2_timing_preservation_inventory_v1.json"
    refreeze_erratum_path = HERE / "stage2_timing_refreeze_erratum_01.json"
    preservation = read_json(preserve_path)
    refreeze_erratum = read_json(refreeze_erratum_path)
    result_report = {
        "schema": "C004-stage2-matched-timing-report-v1",
        "acceptance": "accepted" if not errors else "rejected",
        "protocol_sha256": protocol_hash,
        "protocol_freeze_record_sha256": sha(FREEZE_PATH),
        "schedule_sha256": protocol["schedule_sha256"],
        "stage2_gate_report_sha256": protocol["stage2_gate_report_sha256"],
        "runtime_manifest_sha256": protocol["runtime_manifest_sha256"],
        "source_bindings": protocol["source_bindings"],
        "input_bindings": {case: {"case_id": row["case_id"], "input_path": row["input_path"],
                                   "sha256": row["input_sha256"], "bytes": row["input_bytes"],
                                   "alphabet_size": row["alphabet_size"], "k": row["k"],
                                   "positive_count": row["positive_count"],
                                   "negative_count": row["negative_count"]}
                            for case, row in protocol["cases"].items()},
        "scheduled_counts": {"expected_wall": 12, "actual_wall": sum(1 for row in parsed if row["phase"] == "wall"),
                             "expected_memory": 3, "actual_memory": len(memory_rows),
                             "fresh_child_processes": len(child_pids), "attempts": len(parsed)},
        "wall_results": summary,
        "memory_results": memory_rows,
        "qop_exact_edge_counts": qop_edge_counts,
        "budget_accounting": budget,
        "per_job_records": parsed,
        "capture_source_snapshot_reconciliation": source_snapshot_records,
        "preservation_inventory_sha256": sha(preserve_path),
        "refreeze_erratum_sha256": sha(refreeze_erratum_path),
        "refreeze_history": refreeze_erratum,
        "timing_scope": protocol["measured_scope"],
        "memory_scope": protocol["memory_scope"],
        "limits": [
            "The general-v3 q2 m128/k8 jobs that returned incomplete retain one independently validated target answer but do not prove uniqueness or exhaustive search.",
            "QOP001 results are conditional on known k, q=2, exact finite labels, and the verified q-opposition certificate; they do not establish unrestricted-DFA factor recovery.",
            "Tracemalloc values are peak traced Python allocations, not process RSS; the allocation jobs are separate from wall comparisons.",
            "Full API results were serialized, including the QOP opposition graph and edge witnesses; output byte differences are part of the measured cost.",
            "The original pre-correction protocol, freeze record, and executor source bytes were unavailable in content-addressed storage; trusted hashes and the zero-child event are preserved without reconstructing historical bytes.",
        ],
        "validation_errors": errors,
    }
    report_bytes = (json.dumps(result_report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    REPORT_PATH.write_bytes(report_bytes)
    print(json.dumps({"acceptance": result_report["acceptance"], "errors": len(errors),
                      "wall_jobs": result_report["scheduled_counts"]["actual_wall"],
                      "memory_jobs": result_report["scheduled_counts"]["actual_memory"],
                      "report_sha256": sha(REPORT_PATH),
                      "wall_medians": {case: {method: values["median_wall_seconds"] for method, values in methods.items()}
                                       for case, methods in summary.items()},
                      "memory_peaks": {row["job_id"]: row["peak_traced_python_bytes"] for row in memory_rows}},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if errors:
        raise SystemExit(2)

if __name__ == "__main__":
    main()

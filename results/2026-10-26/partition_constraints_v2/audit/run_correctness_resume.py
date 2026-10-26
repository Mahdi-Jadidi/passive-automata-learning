"""Resume C002 correctness from captured full outputs and save every result first."""
from __future__ import annotations

import gzip
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import run_correctness as rc


AUDIT = rc.AUDIT
CYCLE = rc.CYCLE
CORPUS = rc.CORPUS
PREVIOUS_RUN_ID = "20261026T123752.173646Z_dd9ca0cd"
PREVIOUS_CAPTURE_ID = "20261026T123751.304862Z_11599e4f62"


def read_result_map(path: Path) -> dict[tuple[str, str], dict]:
    result = {}
    if not path.exists():
        return result
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            key = (item["dataset"], item["case_id"])
            assert key not in result, (path, key)
            result[key] = item
    return result


def write_record(handle, case_id, dataset, input_hash, data, result,
                 execution: dict) -> None:
    item = {"case_id": case_id, "dataset": dataset,
            "input_sha256": input_hash, "input": data,
            "execution": execution, "result": result}
    handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def write_reference(handle, record: dict) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    runtime, runtime_hash_before = rc.runtime_snapshot()
    manifest_path = CORPUS / "manifest.json"
    manifest_raw = manifest_path.read_bytes()
    corpus_manifest = json.loads(manifest_raw)
    assert corpus_manifest["frozen_before_solver_runs"] is True
    frozen_paths = [spec["path"] for spec in corpus_manifest["datasets"].values()]
    frozen_paths += [spec["path"] for spec in corpus_manifest["truth_sidecars"].values()]
    frozen_hashes_before = {name: rc.sha((CORPUS / name).read_bytes())
                            for name in frozen_paths}

    legacy = AUDIT / "corpus" / "legacy_generator_extension_v1"
    legacy_manifest_path = legacy / "manifest.json"
    legacy_manifest_raw = legacy_manifest_path.read_bytes()
    legacy_manifest = json.loads(legacy_manifest_raw)
    legacy_hashes_before = {name: rc.sha((legacy / name).read_bytes())
                            for name in ["manifest.json", *legacy_manifest["files"]]}
    assert legacy_manifest["count"] == 3072
    assert legacy_manifest["duplicate_solver_inputs"] == 2502
    assert legacy_manifest["unique_solver_inputs"] == 570

    previous = AUDIT / "correctness_runs" / PREVIOUS_RUN_ID
    previous_capture = AUDIT / "attempts" / PREVIOUS_CAPTURE_ID
    previous_failure = json.loads((previous / "mismatches.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert previous_failure["error_type"] == "TimeoutError"
    assert previous_failure["case_id"] == "finite_generator_140_m10_002"
    previous_result = json.loads((previous_capture / "result.json").read_text(encoding="utf-8"))
    assert previous_result["execution_status"] == "program_error"

    old_outputs = {method: read_result_map(previous / f"{method}.jsonl.gz")
                   for method in ("baseline", "baseline_unpruned", "eager", "lazy")}
    old_mismatch_hash = rc.sha((previous / "mismatches.jsonl").read_bytes())

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:8]
    run_dir = AUDIT / "correctness_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    if str(CYCLE) not in rc.sys.path:
        rc.sys.path.insert(0, str(CYCLE))
    driver = rc.load_module(CYCLE / "solver.py", "c002_audit_driver_resume")
    baseline = rc.load_module(CYCLE / "baseline" / "partition_solver.py", "c002_audit_baseline_resume")
    eager = rc.load_module(CYCLE / "approaches" / "eager" / "eager_solver.py", "c002_audit_eager_resume")
    lazy = rc.load_module(CYCLE / "approaches" / "lazy" / "lazy_solver.py", "c002_audit_lazy_resume")
    providers = {"baseline": lambda data, deadline=None: driver.baseline_result(data, deadline=deadline),
                 "eager": eager.solve, "lazy": lazy.solve}

    datasets = []
    for name, spec in corpus_manifest["datasets"].items():
        records = rc.load_jsonl(CORPUS / spec["path"])
        assert len(records) == spec["count"]
        datasets.extend(records)
    legacy_inputs = rc.load_jsonl(legacy / "solver_inputs.jsonl")
    legacy_truth = rc.load_jsonl(legacy / "truth_sidecars.jsonl")
    assert len(legacy_inputs) == len(legacy_truth) == 3072
    datasets.extend(legacy_inputs)
    same_side_data = {"alphabet": list("abc"), "positive": ["a", "c"], "negative": ["ac"]}
    datasets.append({"case_id": "same_rejecting_side_regression",
                     "dataset": "supplemental_controls", "input": same_side_data,
                     "input_sha256": rc.sha(rc.canonical_json(same_side_data))})

    truth_by_dataset = {}
    for name, spec in corpus_manifest["truth_sidecars"].items():
        truth_by_dataset[name] = {item["case_id"]: item
                                  for item in rc.load_jsonl(CORPUS / spec["path"])}
    truth_by_dataset["legacy_generator_extension_v1"] = {
        item["case_id"]: item for item in legacy_truth}

    output_handles = {}
    result_paths: dict[str, Path] = {}
    for method in ("baseline", "baseline_unpruned", "eager", "lazy"):
        path = run_dir / f"{method}.jsonl.gz"
        output_handles[method] = gzip.open(path, "wt", encoding="utf-8", newline="\n", compresslevel=6)
        result_paths[method] = path

    summary_counts = {
        "case_count": len(datasets), "resumed_records": {name: len(rows) for name, rows in old_outputs.items()},
        "replayed_cases": 0, "executed_provider_calls": 0,
        "by_dataset": {}, "reference_counts": {}, "status_counts": {name: {} for name in providers},
        "complete_set_comparisons": {name: 0 for name in providers},
        "incomplete_results": [], "over_30_second_results": [],
        "witness_records_validated": 0, "true_partition_checks": 0,
        "boolean_oracle_cases": 0, "direct_projection_crosschecks": 0,
        "mismatch_count": 0, "provider_error_count": 0,
    }
    mismatches = []
    provider_errors = []
    started = time.perf_counter()

    try:
        for ordinal, item in enumerate(datasets):
            case_id, dataset_name, data = item["case_id"], item["dataset"], item["input"]
            input_hash = item.get("input_sha256", rc.sha(rc.canonical_json(data)))
            alphabet = sorted(data["alphabet"])
            case_key = (dataset_name, case_id)
            summary_counts["by_dataset"][dataset_name] = summary_counts["by_dataset"].get(dataset_name, 0) + 1

            if dataset_name in {"prior_binary_2187", "prior_abc_81",
                                "targeted_controls", "supplemental_controls"}:
                expected = rc.boolean_oracle(data)
                assert expected == rc.direct_oracle(data)
                summary_counts["boolean_oracle_cases"] += 1
                summary_counts["direct_projection_crosschecks"] += 1
                summary_counts["reference_counts"]["boolean_oracle"] = summary_counts["reference_counts"].get("boolean_oracle", 0) + 1
                unpruned = None
            else:
                old_ref = old_outputs["baseline_unpruned"].get(case_key)
                if old_ref is not None:
                    assert old_ref["input_sha256"] == input_hash, (case_id, "reused reference input hash")
                    unpruned = old_ref["result"]
                    summary_counts["replayed_cases"] += 1
                else:
                    unpruned = baseline.solve(data, prune=False)
                _, expected = rc.normalize_partitions(unpruned, alphabet)
                assert expected == rc.direct_oracle(data)
                summary_counts["direct_projection_crosschecks"] += 1
                summary_counts["reference_counts"]["baseline_unpruned"] = summary_counts["reference_counts"].get("baseline_unpruned", 0) + 1
                write_reference(output_handles["baseline_unpruned"],
                                {"case_id": case_id, "dataset": dataset_name,
                                 "input_sha256": input_hash, "input": data,
                                 "result": unpruned,
                                 "execution": {"source": "reused" if old_ref else "executed"}})

            # Reuse complete audited outputs from the preserved partial run;
            # execute only absent method records. Every new raw result is
            # persisted before it is interpreted or compared.
            case_results = {}
            case_exec = {}
            case_errors = {}
            for method, solve in providers.items():
                old = old_outputs[method].get(case_key)
                if old is not None:
                    assert old["input_sha256"] == input_hash, (method, case_id, "reused input hash")
                    result = old["result"]
                    execution = {"source": "reused_verified_result",
                                 "previous_run": PREVIOUS_RUN_ID}
                    summary_counts["replayed_cases"] += 1
                else:
                    call_started = time.perf_counter()
                    try:
                        result = solve(data, deadline=call_started + 30.0)
                        elapsed = time.perf_counter() - call_started
                        execution = {"source": "fresh_call", "elapsed_seconds": elapsed,
                                     "cooperative_limit_seconds": 30.0,
                                     "over_30_seconds": elapsed > 30.0}
                        summary_counts["executed_provider_calls"] += 1
                        if elapsed > 30.0:
                            summary_counts["over_30_second_results"].append(
                                {"case_id": case_id, "dataset": dataset_name,
                                 "method": method, "elapsed_seconds": elapsed})
                    except Exception as error:
                        case_errors[method] = {"error_type": type(error).__name__,
                                               "error": str(error),
                                               "traceback": traceback.format_exc()}
                        continue
                case_results[method] = result
                case_exec[method] = execution
                write_record(output_handles[method], case_id, dataset_name,
                             input_hash, data, result, execution)

            case_mismatch = None
            for method, result in case_results.items():
                summary_counts["status_counts"][method][result["status"]] = summary_counts["status_counts"][method].get(result["status"], 0) + 1
                if result["complete"]:
                    try:
                        rc.check_complete_contract(result, expected, method, alphabet, data)
                        summary_counts["complete_set_comparisons"][method] += 1
                    except Exception as error:
                        case_mismatch = {"method": method, "error_type": type(error).__name__,
                                         "error": str(error), "traceback": traceback.format_exc()}
                    summary_counts["witness_records_validated"] += len(result["feasible_partitions"])
                else:
                    try:
                        rc.status_result(result)
                        _, partial_set = rc.normalize_partitions(result, alphabet)
                        assert partial_set <= expected, (method, case_id,
                                                        "incomplete result contains a non-feasible partition")
                        rc.check_witnesses(result, data)
                        summary_counts["witness_records_validated"] += len(result["feasible_partitions"])
                    except Exception as error:
                        case_mismatch = {"method": method, "error_type": type(error).__name__,
                                         "error": str(error), "traceback": traceback.format_exc()}
                    summary_counts["incomplete_results"].append(
                        {"case_id": case_id, "dataset": dataset_name, "method": method,
                         "found_partition_count": result.get("found_partition_count"),
                         "elapsed_seconds": case_exec.get(method, {}).get("elapsed_seconds")})

            if case_errors:
                summary_counts["provider_error_count"] += len(case_errors)
                provider_error = {"ordinal": ordinal, "case_id": case_id,
                                  "dataset": dataset_name, "input_sha256": input_hash,
                                  "input": data, "provider_errors": case_errors,
                                  "returned_results": case_results}
                provider_errors.append(provider_error)
                (run_dir / "provider_errors.jsonl").open("a", encoding="utf-8").write(
                    json.dumps(provider_error, ensure_ascii=False, sort_keys=True) + "\n")
                break

            if dataset_name in truth_by_dataset:
                truth = truth_by_dataset[dataset_name][case_id]
                true_partition = tuple(sorted(tuple(sorted(block))
                                               for block in truth["true_partition"]))
                assert true_partition in expected, (case_id, "true generator partition absent from F2")
                summary_counts["true_partition_checks"] += 1
            if case_id == "same_rejecting_side_regression":
                target = (("a",), ("b", "c"))
                assert target not in expected

            if case_mismatch is not None:
                summary_counts["mismatch_count"] += 1
                mismatch = {"ordinal": ordinal, "case_id": case_id,
                            "dataset": dataset_name, "input_sha256": input_hash,
                            "input": data, "expected_partition_set": sorted(expected),
                            "case_results": case_results, "execution": case_exec,
                            **case_mismatch}
                mismatches.append(mismatch)
                (run_dir / "mismatches.jsonl").open("a", encoding="utf-8").write(
                    json.dumps(mismatch, ensure_ascii=False, sort_keys=True) + "\n")
                # Preserve all three method results for the first discrepancy,
                # then stop the acceptance audit until the defect is reviewed.
                break
    finally:
        for handle in output_handles.values():
            handle.close()

    # Capture the externally visible incomplete/exit-3 and invalid-input
    # contract even when a prior provider timeout occurred.
    interruption_data = {"alphabet": list("abc"), "positive": ["ab", "ac"], "negative": ["abc"]}
    cooperative = {}
    for method, solve in providers.items():
        result = solve(interruption_data, deadline=time.perf_counter() - 1.0)
        rc.status_result(result)
        cooperative[method] = {"result": result, "interpreted_status": "incomplete"}
    invalid_results = rc.cli_invalid_checks(driver, run_dir)
    (run_dir / "invalid_input_results.json").write_text(
        json.dumps(invalid_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cli_deadlines = rc.cli_deadline_checks(driver, run_dir)
    (run_dir / "cli_deadline_results.json").write_text(
        json.dumps(cli_deadlines, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runtime_after, runtime_hash_after = rc.runtime_snapshot()
    assert runtime_hash_before == runtime_hash_after and runtime == runtime_after
    assert frozen_hashes_before == {name: rc.sha((CORPUS / name).read_bytes()) for name in frozen_paths}
    assert rc.sha(manifest_path.read_bytes()) == rc.sha(manifest_raw)
    assert legacy_hashes_before == {name: rc.sha((legacy / name).read_bytes()) for name in legacy_hashes_before}

    all_methods_complete = (not summary_counts["incomplete_results"]
                            and all(summary_counts["complete_set_comparisons"][method]
                                    == len(datasets) for method in providers))
    no_errors = not provider_errors and not mismatches
    scientific_status = ("accepted_for_all_cases" if all_methods_complete and no_errors
                         else "incomplete_due_to_provider_timeout" if no_errors
                         else "mismatch_or_provider_error")
    summary = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "scientific_status": scientific_status,
        "execution_status": "success" if no_errors else "program_error",
        "runtime_version": "C002-R1",
        "runtime_manifest_sha256": runtime_hash_before,
        "corpus_manifest_sha256": rc.sha(manifest_raw),
        "legacy_extension_manifest_sha256": rc.sha(legacy_manifest_raw),
        "legacy_extension_inputs_sha256": legacy_manifest["files"]["solver_inputs.jsonl"]["sha256"],
        "previous_run_id": PREVIOUS_RUN_ID,
        "previous_capture_attempt_id": PREVIOUS_CAPTURE_ID,
        "previous_failure_artifact_sha256": old_mismatch_hash,
        "previous_capture_execution_status": previous_result["execution_status"],
        "elapsed_seconds": time.perf_counter() - started,
        "counts": summary_counts,
        "cooperative_deadline_results": cooperative,
        "invalid_cli_results": invalid_results,
        "cli_deadline_results": cli_deadlines,
        "result_files": {name: path.name for name, path in result_paths.items()},
        "result_file_sha256": {name: rc.sha(path.read_bytes()) for name, path in result_paths.items()},
        "mismatches": mismatches,
        "provider_errors": provider_errors,
        "limitations": ["Correctness executes providers in one process and is not timing evidence.",
                        "A provider result with complete=false is preserved and does not count as a complete-set comparison.",
                        "Hard 30-second per-process limits are measured in the separate fresh-process benchmark."]
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False,
                                                    indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "scientific_status": scientific_status,
                      "elapsed_seconds": summary["elapsed_seconds"],
                      "counts": summary_counts,
                      "runtime_manifest_sha256": runtime_hash_before,
                      "corpus_manifest_sha256": rc.sha(manifest_raw),
                      "legacy_extension_manifest_sha256": rc.sha(legacy_manifest_raw),
                      "result_file_sha256": summary["result_file_sha256"]},
                     ensure_ascii=False, sort_keys=True))
    return 0 if no_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

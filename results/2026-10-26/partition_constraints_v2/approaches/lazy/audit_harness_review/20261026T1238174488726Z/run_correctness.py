"""One-process exact F2 differential audit with complete captured result files."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent
CORPUS = AUDIT / "corpus" / "frozen_v1"
RUNTIME_MANIFEST_PATH = CYCLE / "coordination" / "runtime_manifest.json"
EXPECTED_RUNTIME = "C002-R1"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def runtime_snapshot() -> tuple[dict, str]:
    raw = RUNTIME_MANIFEST_PATH.read_bytes()
    manifest = json.loads(raw)
    assert manifest["runtime_version"] == EXPECTED_RUNTIME
    for item in manifest["files"]:
        path = CYCLE / item["path"]
        assert sha(path.read_bytes()) == item["sha256"], item["path"]
    return manifest, sha(raw)


def normalize_partitions(result: dict, alphabet: list[str]) -> tuple[list, set]:
    records = result.get("feasible_partitions", [])
    normalized = []
    for item in records:
        blocks = item["blocks"]
        assert len(blocks) == 2
        assert all(block for block in blocks)
        canonical = tuple(sorted(tuple(sorted(block)) for block in blocks))
        assert sorted(symbol for block in canonical for symbol in block) == sorted(alphabet)
        assert len(set(symbol for block in canonical for symbol in block)) == len(alphabet)
        normalized.append(canonical)
    assert len(normalized) == len(set(normalized)), "duplicate ownership result"
    return sorted(normalized), set(normalized)


def project(word: str, block: list[str] | tuple[str, ...]) -> str:
    allowed = set(block)
    return "".join(symbol for symbol in word if symbol in allowed)


def check_witnesses(result: dict, data: dict) -> None:
    positive, negative = data["positive"], data["negative"]
    for record in result["feasible_partitions"]:
        blocks = record["blocks"]
        assert len(record["positive_projection_languages"]) == 2
        projected = [{project(p, block) for p in positive} for block in blocks]
        assert record["positive_projection_languages"] == [sorted(values) for values in projected]
        witnesses = record["negative_witnesses"]
        assert len(witnesses) == len(negative)
        assert [w["negative"] for w in witnesses] == negative
        for witness in witnesses:
            word = witness["negative"]
            unseen = [side for side, block in enumerate(blocks)
                      if project(word, block) not in projected[side]]
            assert unseen
            assert witness["all_unseen_block_indices"] == unseen
            side = witness["block_index"]
            assert side in unseen
            assert witness["projection"] == project(word, blocks[side])
            assert witness["projection"] not in projected[side]


def check_complete_contract(result: dict, expected: set, method: str,
                            alphabet: list[str], data: dict) -> None:
    assert result["method"] == method
    assert result["complete"] is True
    normalized, actual = normalize_partitions(result, alphabet)
    assert actual == expected, (method, "full F2 set differs", actual, expected)
    assert result["feasible_partition_count"] == len(expected)
    assert result["found_partition_count"] == len(expected)
    expected_status = "infeasible" if not expected else "unique" if len(expected) == 1 else "ambiguous"
    assert result["status"] == expected_status
    check_witnesses(result, data)


def canonical_models(alphabet: list[str]):
    for suffix in itertools.product((0, 1), repeat=len(alphabet) - 1):
        owners = (0,) + suffix
        if 1 not in owners:
            continue
        yield [{symbol for symbol, owner in zip(alphabet, owners) if owner == side}
               for side in (0, 1)]


def boolean_partition_feasible(blocks: list[set[str]], positive: list[str],
                               negative: list[str]) -> bool:
    positive_projections = [{project(word, block) for word in positive}
                            for block in blocks]
    free_values = sorted({(side, project(word, blocks[side]))
                          for word in negative for side in (0, 1)
                          if project(word, blocks[side]) not in positive_projections[side]})
    index = {value: i for i, value in enumerate(free_values)}
    for bits in itertools.product((False, True), repeat=len(free_values)):
        feasible = True
        for word in negative:
            local_accepts = []
            for side in (0, 1):
                projected = project(word, blocks[side])
                if projected in positive_projections[side]:
                    local_accepts.append(True)
                else:
                    local_accepts.append(bits[index[(side, projected)]])
            if all(local_accepts):
                feasible = False
                break
        if feasible:
            return True
    return False


def boolean_oracle(data: dict) -> set:
    alpha = data["alphabet"]
    result = set()
    for blocks in canonical_models(alpha):
        if boolean_partition_feasible(blocks, data["positive"], data["negative"]):
            result.add(tuple(sorted(tuple(sorted(block)) for block in blocks)))
    return result


def direct_oracle(data: dict) -> set:
    alpha = data["alphabet"]
    result = set()
    for blocks in canonical_models(alpha):
        projections = [{project(word, block) for word in data["positive"]}
                       for block in blocks]
        if all(any(project(word, blocks[side]) not in projections[side]
                   for side in (0, 1)) for word in data["negative"]):
            result.add(tuple(sorted(tuple(sorted(block)) for block in blocks)))
    return result


def status_result(result: dict) -> None:
    assert result["complete"] is False
    assert result["status"] == "incomplete"
    assert result["feasible_partition_count"] is None
    assert result["found_partition_count"] == len(result["feasible_partitions"])
    assert result["status"] not in ("unique", "infeasible")


def cli_invalid_checks(driver, run_dir: Path) -> list[dict]:
    invalid_data = [
        {"alphabet": ["a", "b"], "positive": ["ab"], "negative": ["ab"]},
        {"alphabet": ["a", "b"], "positive": ["ac"], "negative": []},
        {"alphabet": ["a", "a"], "positive": [], "negative": []},
        {"alphabet": ["a"], "positive": [], "negative": []},
        {"alphabet": ["a", "b"], "positive": "ab", "negative": []},
    ]
    outcomes = []
    for index, data in enumerate(invalid_data):
        path = run_dir / f"invalid_{index}.json"
        path.write_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        for method in ("baseline", "eager", "lazy"):
            from contextlib import redirect_stdout
            from io import StringIO
            buffer = StringIO()
            with redirect_stdout(buffer):
                code = driver.main([str(path), "--method", method])
            stdout = buffer.getvalue()
            payload = json.loads(stdout)
            assert code == 2 and payload["status"] == "invalid_input"
            outcomes.append({"case_id": f"invalid_{index}", "method": method,
                             "input": data, "input_sha256": sha(canonical_json(data)),
                             "exit_code": code, "stdout": payload})
    return outcomes


def cli_deadline_checks(driver, run_dir: Path) -> list[dict]:
    data = {"alphabet": list("abc"), "positive": ["ab", "ac"], "negative": ["abc"]}
    path = run_dir / "cooperative_deadline.json"
    path.write_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    outcomes = []
    for method in ("baseline", "eager", "lazy"):
        from contextlib import redirect_stdout
        from io import StringIO
        buffer = StringIO()
        with redirect_stdout(buffer):
            raw_exit_code = driver.main([str(path), "--method", method,
                                         "--timeout-seconds", "0"])
        payload = json.loads(buffer.getvalue())
        assert raw_exit_code == 3
        status_result(payload)
        outcomes.append({"method": method, "raw_exit_code": raw_exit_code,
                         "raw_process_status": "program_error",
                         "interpreted_solver_status": "incomplete",
                         "result": payload})
    return outcomes


def main() -> int:
    runtime, runtime_hash_before = runtime_snapshot()
    corpus_manifest_path = CORPUS / "manifest.json"
    corpus_manifest_raw = corpus_manifest_path.read_bytes()
    corpus_manifest = json.loads(corpus_manifest_raw)
    assert corpus_manifest["frozen_before_solver_runs"] is True
    corpus_hashes_before = {
        item["path"]: sha((CORPUS / item["path"]).read_bytes())
        for item in corpus_manifest["datasets"].values()
    }
    corpus_hashes_before.update({
        item["path"]: sha((CORPUS / item["path"]).read_bytes())
        for item in corpus_manifest["truth_sidecars"].values()
    })

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:8]
    run_dir = AUDIT / "correctness_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    if str(CYCLE) not in sys.path:
        sys.path.insert(0, str(CYCLE))
    driver = load_module(CYCLE / "solver.py", "c002_audit_driver")
    baseline = load_module(CYCLE / "baseline" / "partition_solver.py", "c002_audit_baseline")
    eager = load_module(CYCLE / "approaches" / "eager" / "eager_solver.py", "c002_audit_eager")
    lazy = load_module(CYCLE / "approaches" / "lazy" / "lazy_solver.py", "c002_audit_lazy")
    providers = {"baseline": lambda data, deadline=None: driver.baseline_result(data, deadline=deadline),
                 "eager": eager.solve, "lazy": lazy.solve}

    datasets = []
    for dataset_name, spec in corpus_manifest["datasets"].items():
        records = load_jsonl(CORPUS / spec["path"])
        assert len(records) == spec["count"]
        datasets.extend(records)
    legacy_extension = AUDIT / "corpus" / "legacy_generator_extension_v1"
    legacy_manifest_path = legacy_extension / "manifest.json"
    legacy_manifest_raw = legacy_manifest_path.read_bytes()
    legacy_manifest = json.loads(legacy_manifest_raw)
    assert legacy_manifest["count"] == 3072
    for filename, spec in legacy_manifest["files"].items():
        assert sha((legacy_extension / filename).read_bytes()) == spec["sha256"]
    legacy_inputs = load_jsonl(legacy_extension / "solver_inputs.jsonl")
    assert len(legacy_inputs) == 3072
    assert len({item["case_id"] for item in legacy_inputs}) == 3072
    datasets.extend(legacy_inputs)
    # Add the regression that specifically rejects per-positive side switching.
    side_data = {"alphabet": list("abc"), "positive": ["a", "c"], "negative": ["ac"]}
    side_record = {"case_id": "same_rejecting_side_regression",
                   "dataset": "supplemental_controls",
                   "input": side_data,
                   "input_sha256": sha(canonical_json(side_data))}
    datasets.append(side_record)

    truth_by_dataset = {}
    for dataset_name, spec in corpus_manifest["truth_sidecars"].items():
        sidecar = CORPUS / spec["path"]
        truth_by_dataset[dataset_name] = {
            item["case_id"]: item for item in load_jsonl(sidecar)}
    legacy_truth = load_jsonl(legacy_extension / "truth_sidecars.jsonl")
    truth_by_dataset["legacy_generator_extension_v1"] = {
        item["case_id"]: item for item in legacy_truth}
    assert len(legacy_truth) == 3072
    assert legacy_manifest["partition_group_counts"] == {"ab|c": 1024, "ac|b": 1024, "a|bc": 1024}
    assert legacy_manifest["duplicate_solver_inputs"] == 2502
    assert legacy_manifest["unique_solver_inputs"] == 570
    for record, truth in zip(legacy_inputs, legacy_truth):
        assert record["case_id"] == truth["case_id"]
        assert record["dataset"] == "legacy_generator_extension_v1"
        assert set(record) == {"case_id", "dataset", "input", "input_sha256"}
        data = record["input"]
        assert sha(canonical_json(data)) == record["input_sha256"]
        assert data["alphabet"] == list("abc")
        assert data["positive"] == sorted(set(data["positive"]))
        assert data["negative"] == sorted(set(data["negative"]))
        assert not (set(data["positive"]) & set(data["negative"]))
        blocks = truth["true_partition"]
        languages = [set(item["language"]) for item in truth["local_languages"]]
        assert len(blocks) == len(languages) == 2
        assert all(item["block"] == blocks[i] for i, item in enumerate(truth["local_languages"]))
        assert sorted(blocks[0] + blocks[1]) == list("abc")
        for i, item in enumerate(truth["local_languages"]):
            assert all(len(word) <= 2 and set(word) <= set(blocks[i])
                       for word in item["language"])
        assert len(data["positive"]) + len(data["negative"]) == truth["sample_word_count"]
        for word in data["positive"]:
            assert len(word) <= 4 and all(any(symbol in word for symbol in block) for block in blocks)
            assert all(project(word, block) in languages[i]
                       for i, block in enumerate(blocks))
        for word in data["negative"]:
            assert len(word) <= 4 and all(any(symbol in word for symbol in block) for block in blocks)
            assert not all(project(word, block) in languages[i]
                           for i, block in enumerate(blocks))

    output_handles = {}
    result_paths = {}
    for method in ("baseline", "baseline_unpruned", "eager", "lazy"):
        path = run_dir / f"{method}.jsonl.gz"
        handle = gzip.open(path, "wt", encoding="utf-8", newline="\n", compresslevel=6)
        output_handles[method] = handle
        result_paths[method] = path.name

    counters = {"cases": len(datasets), "by_dataset": {}, "reference": {},
                "mismatch_count": 0, "provider_error_count": 0,
                "witness_records_checked": 0, "true_partition_checks": 0,
                "boolean_oracle_cases": 0, "unpruned_baseline_cases": 0}
    mismatches = []
    provider_errors = []
    status_counts = {method: {} for method in providers}
    started = time.perf_counter()
    try:
        for ordinal, item in enumerate(datasets):
            case_id, dataset_name = item["case_id"], item["dataset"]
            data = item["input"]
            input_hash = item.get("input_sha256", sha(canonical_json(data)))
            alphabet = sorted(data["alphabet"])
            counters["by_dataset"][dataset_name] = counters["by_dataset"].get(dataset_name, 0) + 1
            try:
                if dataset_name in {"prior_binary_2187", "prior_abc_81",
                                    "targeted_controls", "supplemental_controls"}:
                    expected = boolean_oracle(data)
                    counters["boolean_oracle_cases"] += 1
                    counters["reference"]["boolean_oracle"] = counters["reference"].get("boolean_oracle", 0) + 1
                    assert expected == direct_oracle(data)
                    counters["reference"]["boolean_vs_projection_oracle_cases"] = counters["reference"].get("boolean_vs_projection_oracle_cases", 0) + 1
                else:
                    unpruned = baseline.solve(data, prune=False)
                    _, expected = normalize_partitions(unpruned, alphabet)
                    assert expected == direct_oracle(data)
                    counters["unpruned_baseline_cases"] += 1
                    counters["reference"]["baseline_unpruned"] = counters["reference"].get("baseline_unpruned", 0) + 1
                    output_handles["baseline_unpruned"].write(json.dumps(
                        {"case_id": case_id, "dataset": dataset_name,
                         "input_sha256": input_hash, "input": data,
                         "result": unpruned}, ensure_ascii=False, sort_keys=True) + "\n")
                    counters["reference"]["baseline_unpruned_outputs"] = counters["reference"].get("baseline_unpruned_outputs", 0) + 1

                case_results = {}
                for method, solve in providers.items():
                    call_started = time.perf_counter()
                    deadline = call_started + 30.0
                    result = solve(data, deadline=deadline)
                    elapsed = time.perf_counter() - call_started
                    if elapsed > 30.0:
                        raise TimeoutError(f"{method} exceeded 30 seconds on {case_id}: {elapsed:.6f}")
                    check_complete_contract(result, expected, method, alphabet, data)
                    case_results[method] = result
                    status_counts[method][result["status"]] = status_counts[method].get(result["status"], 0) + 1
                    counters["witness_records_checked"] += len(result["feasible_partitions"])
                    output_handles[method].write(json.dumps(
                        {"case_id": case_id, "dataset": dataset_name,
                         "input_sha256": input_hash, "input": data,
                         "result": result}, ensure_ascii=False, sort_keys=True) + "\n")

                if dataset_name in truth_by_dataset:
                    truth = truth_by_dataset[dataset_name][case_id]
                    true_partition = tuple(sorted(tuple(sorted(block))
                                                   for block in truth["true_partition"]))
                    assert true_partition in expected, (case_id, "true generator partition absent from F2")
                    counters["true_partition_checks"] += 1
                if case_id == "same_rejecting_side_regression":
                    target = (tuple(("a",)), tuple(("b", "c")))
                    assert target not in expected, "regression target should fail shared-side feasibility"
                    counters["same_rejecting_side_partition_excluded"] = True

            except Exception as error:
                counters["mismatch_count"] += 1
                mismatch = {"ordinal": ordinal, "case_id": case_id, "dataset": dataset_name,
                            "input_sha256": input_hash, "input": data,
                            "error_type": type(error).__name__, "error": str(error),
                            "traceback": traceback.format_exc()}
                mismatches.append(mismatch)
                provider_errors.append(mismatch)
                (run_dir / "mismatches.jsonl").open("a", encoding="utf-8").write(
                    json.dumps(mismatch, ensure_ascii=False, sort_keys=True) + "\n")
                # Stop at the first discrepancy; complete outputs for this case
                # have already been saved for every provider that returned.
                break
    finally:
        for handle in output_handles.values():
            handle.close()

    # Verify cooperative interruption cannot claim a complete unique/empty set.
    deadline_data = {"alphabet": list("abc"), "positive": ["ab", "ac"], "negative": ["abc"]}
    interruption = {}
    for method, solve in providers.items():
        result = solve(deadline_data, deadline=time.perf_counter() - 1.0)
        status_result(result)
        interruption[method] = {"complete": result["complete"], "status": result["status"],
                                "feasible_partition_count": result["feasible_partition_count"],
                                "found_partition_count": result["found_partition_count"]}

    invalid_results = cli_invalid_checks(driver, run_dir)
    (run_dir / "invalid_input_results.json").write_text(
        json.dumps(invalid_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert len(invalid_results) == 15
    cli_deadlines = cli_deadline_checks(driver, run_dir)
    (run_dir / "cli_deadline_results.json").write_text(
        json.dumps(cli_deadlines, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runtime_after, runtime_hash_after = runtime_snapshot()
    assert runtime_hash_before == runtime_hash_after
    assert runtime == runtime_after
    corpus_hashes_after = {
        item["path"]: sha((CORPUS / item["path"]).read_bytes())
        for item in corpus_manifest["datasets"].values()
    }
    corpus_hashes_after.update({
        item["path"]: sha((CORPUS / item["path"]).read_bytes())
        for item in corpus_manifest["truth_sidecars"].values()
    })
    assert corpus_hashes_before == corpus_hashes_after
    assert sha(corpus_manifest_path.read_bytes()) == sha(corpus_manifest_raw)
    assert sha(legacy_manifest_path.read_bytes()) == sha(legacy_manifest_raw)
    for filename, spec in legacy_manifest["files"].items():
        assert sha((legacy_extension / filename).read_bytes()) == spec["sha256"]

    complete = counters["mismatch_count"] == 0
    summary = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "scientific_status": "accepted_for_this_corpus" if complete else "mismatch_or_provider_error",
        "execution_status": "success" if complete else "program_error",
        "runtime_version": EXPECTED_RUNTIME,
        "runtime_manifest_sha256": runtime_hash_before,
        "corpus_manifest_sha256": sha(corpus_manifest_raw),
        "legacy_extension_manifest_sha256": sha(legacy_manifest_raw),
        "legacy_extension_input_sha256": legacy_manifest["files"]["solver_inputs.jsonl"]["sha256"],
        "elapsed_seconds": time.perf_counter() - started,
        "counters": counters,
        "status_counts": status_counts,
        "cooperative_deadline_results": interruption,
        "invalid_cli_cases": invalid_results,
        "cli_deadline_interpretation": cli_deadlines,
        "result_files": result_paths,
        "result_file_sha256": {name: sha(path.read_bytes()) for name, path in result_paths.items()},
        "mismatches": mismatches,
        "limitations": ["Correctness batch runs in one process; it is not performance timing.",
                        "Per-call cooperative deadlines are checked by providers; hard process limits are validated separately by the capture runner."]
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False,
                                                    indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "scientific_status": summary["scientific_status"],
                      "elapsed_seconds": summary["elapsed_seconds"], "counters": counters,
                      "status_counts": status_counts, "runtime_manifest_sha256": runtime_hash_before,
                      "corpus_manifest_sha256": sha(corpus_manifest_raw),
                      "legacy_extension_manifest_sha256": sha(legacy_manifest_raw),
                      "result_file_sha256": summary["result_file_sha256"]},
                     ensure_ascii=False, sort_keys=True))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())

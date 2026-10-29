"""Serial stage-1 benchmark executor with post-capture independent checks."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
CORPUS = HERE / "corpora" / "stage1_v4"
PROTOCOL = HERE / "stage1_protocol_freeze_v4.json"
GATE = HERE / "stage1_gate_report_v1.json"
RUNTIME = PROJECT / "coordination" / "runtime_stage1.json"
RUNNER = HERE / "timed_provider_run_v1.py"
RUN_ROOT = HERE / "timed_runs" / "stage1_r1"
LEDGER = RUN_ROOT / "ledger.jsonl"
RUN_MANIFEST = RUN_ROOT / "run_manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pkey(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def project(word, block):
    members = set(block)
    return "".join(ch for ch in word if ch in members)


def validate_solution(data, solution):
    problems = []
    blocks = solution.get("blocks")
    if not isinstance(blocks, list) or len(blocks) != data["k"] or any(not b for b in blocks):
        return ["malformed_or_wrong_block_count"]
    alphabet = set(data["alphabet"])
    if sorted(ch for block in blocks for ch in block) != sorted(alphabet):
        problems.append("blocks_do_not_partition_alphabet")
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    languages = [{project(word, block) for word in positives} for block in blocks]
    if solution.get("positive_projection_languages") != [sorted(lang) for lang in languages]:
        problems.append("reported_projection_languages_mismatch")
    witnesses = {}
    for witness in solution.get("negative_witnesses", []):
        word = witness.get("negative")
        if word in witnesses:
            problems.append("duplicate_negative_witness")
        witnesses[word] = witness
    if set(witnesses) != set(negatives):
        problems.append("negative_witness_coverage_mismatch")
    for word in negatives:
        unseen = [i for i, block in enumerate(blocks) if project(word, block) not in languages[i]]
        if not unseen:
            problems.append("negative_accepted_by_partition")
            continue
        witness = witnesses.get(word)
        if witness is not None:
            idx = witness.get("block_index")
            if not isinstance(idx, int) or idx not in range(len(blocks)):
                problems.append("negative_witness_bad_block_index")
            elif idx not in unseen or witness.get("projection") != project(word, blocks[idx]):
                problems.append("negative_witness_projection_invalid")
            if sorted(witness.get("all_unseen_block_indices", [])) != unseen:
                problems.append("negative_witness_unseen_set_invalid")
    return problems


def independently_check(provider, summary, data, truth, capture_result):
    if capture_result["execution_status"] == "timed_out":
        return {"status": "censored_external_timeout", "problems": []}
    if capture_result["execution_status"] != "success":
        return {"status": "execution_error", "problems": [capture_result["execution_status"]]}
    if not isinstance(summary, dict) or summary.get("schema") != "C004-timed-provider-summary-v1":
        return {"status": "invalid_raw_summary", "problems": ["summary_missing_or_malformed"]}
    status = summary.get("status")
    answers = summary.get("solutions", [])
    if status == "incomplete" and not answers:
        return {"status": "censored_incomplete", "problems": []}
    if provider in ("S001", "C003-fixed-word"):
        if status != "found" or len(answers) != 1:
            return {"status": "unexpected_singleton_status", "problems": [status or "missing_status"]}
        problems = validate_solution(data, answers[0])
        if pkey(answers[0]["blocks"]) != pkey(truth["blocks"]):
            problems.append("not_hidden_singleton_truth_partition")
        expected_langs = sorted(zip([sorted(b) for b in truth["blocks"]],
                                    [sorted(set(x)) for x in truth["local_languages"]]))
        actual_pairs = sorted((sorted(block), lang) for block, lang in
                              zip(answers[0]["blocks"], answers[0]["positive_projection_languages"]))
        if actual_pairs != expected_langs:
            problems.append("not_hidden_singleton_truth_languages")
        return {"status": "pass" if not problems else "mismatch", "problems": problems}
    if provider == "general-v3":
        truth_blocks = truth["blocks"]
        truth_langs = [{project(w, block) for w in data["positive"]} for block in truth_blocks]
        if any(all(project(w, truth_blocks[i]) in truth_langs[i]
                   for i in range(data["k"])) for w in data["negative"]):
            return {"status": "corpus_oracle_error", "problems": ["planted_partition_does_not_fit_finite_positive_projection_model"]}
        if status == "infeasible" and summary.get("search_exhausted"):
            return {"status": "mismatch", "problems": ["reported_infeasible_despite_planted_finite_solution"]}
        if status != "found" or len(answers) != 1:
            return {"status": "unexpected_general_status", "problems": [status or "missing_status"]}
        problems = validate_solution(data, answers[0])
        return {"status": "pass" if not problems else "mismatch", "problems": problems}
    return {"status": "unknown_provider", "problems": [provider]}


def load_ledger():
    if not LEDGER.exists():
        return []
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("standard", "stress", "memory"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    args = parser.parse_args()
    import sys as _sys
    sys.path.insert(0, str(HERE))
    from capture import capture

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in manifest["cases"]}
    protocol_sha = sha(PROTOCOL)
    if protocol.get("schema") != "C004-stage1-performance-protocol-v1":
        raise ValueError("unexpected protocol schema")
    if protocol["created_from"]["runtime_stage1_sha256"] != sha(RUNTIME):
        raise ValueError("runtime source freeze changed")
    if protocol["created_from"]["corpus_manifest_sha256"] != sha(CORPUS / "manifest.json"):
        raise ValueError("corpus manifest changed")
    if protocol["created_from"]["stage1_gate_report_sha256"] != sha(GATE):
        raise ValueError("stage1 gate report changed")
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    if not RUN_MANIFEST.exists():
        record = {"schema": "C004-stage1-benchmark-run-v1", "run_id": "stage1_r1",
                  "protocol_path": str(PROTOCOL), "protocol_sha256": protocol_sha,
                  "started_utc": datetime.now(timezone.utc).isoformat(),
                  "runner_path": str(RUNNER), "runner_sha256": sha(RUNNER),
                  "timed_scope": protocol["measured_budget"]["measured_scope"]}
        with RUN_MANIFEST.open("xb") as handle:
            handle.write((json.dumps(record, ensure_ascii=False, indent=2)+"\n").encode("utf-8"))
            handle.flush(); os.fsync(handle.fileno())
    else:
        saved = json.loads(RUN_MANIFEST.read_text(encoding="utf-8"))
        if saved.get("protocol_sha256") != protocol_sha:
            raise ValueError("existing run belongs to a different frozen protocol")
    ledger = load_ledger()
    done = {row["job_id"] for row in ledger}
    if args.phase == "standard":
        all_jobs = protocol["ordering"]["standard_jobs"]
        stop = len(all_jobs) if args.stop is None else args.stop
        jobs = all_jobs[args.start:stop]
        if args.start < 0 or stop > len(all_jobs) or args.start > stop:
            raise ValueError("invalid standard job range")
    elif args.phase == "stress":
        standard_ids = {job["job_id"] for job in protocol["ordering"]["standard_jobs"]}
        if not standard_ids.issubset(done):
            raise ValueError("stress phase requires every standard timed job recorded")
        jobs = protocol["ordering"]["stress_jobs"]
    else:
        required = {job["job_id"] for job in protocol["ordering"]["standard_jobs"] + protocol["ordering"]["stress_jobs"]}
        if not required.issubset(done):
            raise ValueError("memory phase requires all timed and stress jobs recorded")
        jobs = protocol["ordering"]["memory_jobs"]
    appended, summaries = [], []
    for job in jobs:
        if job["job_id"] in done:
            continue
        provider, case_id = job["provider"], job["case"]
        row = rows[case_id]
        input_path = (CORPUS / row["input"]).resolve()
        truth_path = (CORPUS / row["truth"]).resolve()
        if sha(input_path) != next(x["input_sha256"] for x in protocol["selected_inputs"] if x["id"] == case_id):
            raise ValueError(f"selected input hash changed: {case_id}")
        if sha(truth_path) != next(x["truth_sha256"] for x in protocol["selected_inputs"] if x["id"] == case_id):
            raise ValueError(f"selected truth hash changed: {case_id}")
        data = json.loads(input_path.read_text(encoding="utf-8"))
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        if args.phase == "memory":
            label = f"allocation_{job['provider']}_{case_id}"
        else:
            label = f"timing_{job['provider']}_{case_id}_r{job.get('repetition',1)}"
        command = [sys.executable, "-B", "-X", "utf8", str(RUNNER), provider,
                   case_id, str(input_path)]
        if args.phase == "memory":
            command.append("--memory")
        provider_source = {
            "S001": PROJECT / "structural" / "singleton_solver_v1.py",
            "general-v3": PROJECT / "general" / "known_k_v3.py",
            "C003-fixed-word": WORKSPACE_C003_FIXED,
        }[provider]
        source_paths = [RUNNER, PROTOCOL, input_path, provider_source, RUNTIME,
                        GATE, CORPUS / "corpus_freeze_v2.json"]
        capture_record = capture(label, command, cwd=HERE, timeout_seconds=30.0,
                                 source_paths=source_paths)
        raw_summary, validation = None, {"status": "unavailable", "problems": []}
        if capture_record["stdout_bytes"]:
            raw_path = Path(capture_record["attempt_dir"]) / "stdout.bin"
            try:
                raw_value = json.loads(raw_path.read_text(encoding="utf-8"))
                if args.phase == "memory":
                    raw_summary = raw_value.get("summary")
                    peak = raw_value.get("peak_traced_python_bytes")
                    validation = independently_check(provider, raw_summary, data, truth,
                                                     capture_record)
                    validation["peak_traced_python_bytes"] = peak
                else:
                    raw_summary = raw_value
                    validation = independently_check(provider, raw_summary, data, truth,
                                                     capture_record)
            except Exception as error:
                validation = {"status": "raw_parse_error", "problems": [repr(error)]}
        record = {"job_id": job["job_id"], "phase": args.phase,
                  "provider": provider, "case": case_id,
                  "repetition": job.get("repetition"),
                  "attempt_id": capture_record.get("attempt_id"),
                  "attempt_dir": capture_record.get("attempt_dir"),
                  "capture_execution_status": capture_record.get("execution_status"),
                  "exit_code": capture_record.get("exit_code"),
                  "subprocess_seconds": capture_record.get("subprocess_seconds"),
                  "stdout_bytes": capture_record.get("stdout_bytes"),
                  "stdout_sha256": capture_record.get("stdout_sha256"),
                  "stderr_bytes": capture_record.get("stderr_bytes"),
                  "stderr_sha256": capture_record.get("stderr_sha256"),
                  "scientific_status": raw_summary.get("status") if raw_summary else None,
                  "search_exhausted": raw_summary.get("search_exhausted") if raw_summary else None,
                  "uniqueness": raw_summary.get("uniqueness") if raw_summary else None,
                  "independent_check": validation,
                  "protocol_sha256": protocol_sha}
        with LEDGER.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        done.add(job["job_id"]); ledger.append(record); appended.append(record)
        summaries.append({"job_id": job["job_id"], "provider": provider,
                          "case": case_id, "capture_status": capture_record["execution_status"],
                          "seconds": capture_record.get("subprocess_seconds"),
                          "scientific_status": record["scientific_status"],
                          "check": validation["status"]})
        sys.stdout.write(json.dumps({"completed": summaries[-1]}, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
        sys.stdout.flush()
        sums = {}
        stress_sum = 0.0
        for prev in ledger:
            if prev["phase"] in ("standard", "stress"):
                sums[prev["provider"]] = sums.get(prev["provider"], 0.0) + (prev.get("subprocess_seconds") or 0.0)
            if prev["phase"] == "stress":
                stress_sum += prev.get("subprocess_seconds") or 0.0
        if any(value > 900.0 for value in sums.values()) or stress_sum > 180.0:
            raise RuntimeError("frozen measured budget exceeded after job was preserved")
    batch = {"phase": args.phase, "requested_jobs": len(jobs),
             "new_jobs": len(appended), "summaries": summaries}
    sys.stdout.write(json.dumps({"batch_complete": batch}, ensure_ascii=False,
                                separators=(",", ":")) + "\n")
    sys.stdout.flush()
    return 0


WORKSPACE_C003_FIXED = PROJECT.parents[2] / "results" / "2026-10-26" / "partition_discovery_v3" / "structural" / "fixed_word_solver.py"


if __name__ == "__main__":
    raise SystemExit(main())


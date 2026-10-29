"""Freeze exact stage-1 measurement schedule and input/source hashes."""
from __future__ import annotations
import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
CORPUS = HERE / "corpora" / "stage1_v4"
ROOT_MANIFEST = CORPUS / "manifest.json"
FREEZE = CORPUS / "corpus_freeze_v2.json"
RUNTIME = PROJECT / "coordination" / "runtime_stage1.json"
GATE = HERE / "stage1_gate_report_v1.json"
PROTOCOL = HERE / "PROTOCOL_STAGE1_FA_v2.md"
OUT = HERE / "stage1_protocol_freeze_v4.json"

S001 = PROJECT / "structural" / "singleton_solver_v1.py"
GENERAL = PROJECT / "general" / "known_k_v3.py"
WORKSPACE = PROJECT.parents[2]
C003_FIXED = WORKSPACE / "results" / "2026-10-26" / "partition_discovery_v3" / "structural" / "fixed_word_solver.py"
C003_GENERAL = WORKSPACE / "results" / "2026-10-26" / "partition_discovery_v3" / "general" / "general_solver.py"
C003_SUPPORT = WORKSPACE / "results" / "2026-10-26" / "partition_discovery_v3" / "general" / "support.py"
C002_BASELINE = WORKSPACE / "results" / "2026-10-26" / "partition_constraints_v2" / "baseline" / "partition_solver.py"
CAPTURE = HERE / "capture.py"

S001_CASES = [
    "long_singleton_a32_k2_l1024",
    "long_singleton_a128_k2_l1024",
    "long_singleton_a128_k2_l4096",
    "long_singleton_a32_k2_l4096",
    "long_singleton_a32_k3_l4096",
    "long_singleton_a32_k4_l4096",
    "long_singleton_a32_k6_l4096",
    "long_singleton_a32_k8_l4096",
    "long_singleton_a32_k2_l128",
]
BRIDGE_CASES = [
    "long_singleton_a32_k2_l1024",
    "long_singleton_a128_k2_l1024",
    "long_singleton_a128_k2_l4096",
]
GENERAL_CASES = [
    "random_dfa_a8_k2_l4096_s88296",
    "random_dfa_a32_k4_l1024_s109424",
    "random_dfa_a128_k8_l128_s204928",
    "context_regular_a32_k2_l4096_s127296",
    "context_regular_a32_k8_l1024_s124824",
    "context_regular_a128_k4_l4096_s223496",
]
STRESS_A = ["stress_a128_k2_l16384", "stress_a128_k4_l16384", "stress_a128_k8_l16384"]
STRESS_B = ["stress_a128_k2_l16384"]
ALLOCATION = [
    ("S001", "long_singleton_a32_k2_l1024"),
    ("C003-fixed-word", "long_singleton_a32_k2_l1024"),
    ("S001", "long_singleton_a128_k2_l1024"),
    ("C003-fixed-word", "long_singleton_a128_k2_l1024"),
    ("general-v3", "random_dfa_a32_k4_l1024_s109424"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(f"refusing to replace frozen protocol: {OUT}")
    manifest = json.loads(ROOT_MANIFEST.read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in manifest["cases"]}
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    corpus_freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    source_paths = [
        (S001, "structural/singleton_solver_v1.py"),
        (GENERAL, "general/known_k_v3.py"),
        (CAPTURE, "audit/capture.py"),
        (C003_FIXED, str(C003_FIXED.relative_to(WORKSPACE)).replace("\\", "/")),
        (C003_GENERAL, str(C003_GENERAL.relative_to(WORKSPACE)).replace("\\", "/")),
        (C003_SUPPORT, str(C003_SUPPORT.relative_to(WORKSPACE)).replace("\\", "/")),
        (C002_BASELINE, str(C002_BASELINE.relative_to(WORKSPACE)).replace("\\", "/")),
    ]
    sources = [{"path": relative, "sha256": sha(path), "bytes": path.stat().st_size}
               for path, relative in source_paths]
    runtime_sources = {entry["path"]: entry["sha256"] for entry in runtime["files"]}
    for entry in sources:
        name = entry["path"].replace("\\", "/")
        if name in runtime_sources and runtime_sources[name] != entry["sha256"]:
            raise ValueError(f"source hash differs from master runtime freeze: {name}")
    input_cases = sorted(set(S001_CASES + GENERAL_CASES + STRESS_A + STRESS_B +
                             [case for _, case in ALLOCATION]))
    inputs = []
    for case_id in input_cases:
        row = rows[case_id]
        item = {"id": case_id, "family": row["family"], "k": row["k"],
                "alphabet_size": row["alphabet_size"],
                "positive_count": row["positive_count"], "negative_count": row["negative_count"],
                "positive_lengths": row["positive_lengths"], "negative_lengths": row["negative_lengths"],
                "input_path": row["input"], "input_sha256": sha(CORPUS / row["input"]),
                "truth_path": row["truth"], "truth_sha256": sha(CORPUS / row["truth"])}
        inputs.append(item)
    rng = random.Random(20261027)
    bridge_jobs = []
    for repetition in (1, 2, 3):
        cells = BRIDGE_CASES[:]
        rng.shuffle(cells)
        for cell in cells:
            methods = ["S001", "C003-fixed-word"]
            if rng.random() < 0.5:
                methods.reverse()
            for method in methods:
                bridge_jobs.append({"provider": method, "case": cell, "repetition": repetition,
                                    "job_id": f"{method}--{cell}--r{repetition}"})
    remaining_a = sorted(set(S001_CASES) - set(BRIDGE_CASES))
    other_jobs = []
    for repetition in (1, 2, 3):
        for case_id in remaining_a:
            other_jobs.append({"provider": "S001", "case": case_id, "repetition": repetition,
                               "job_id": f"S001--{case_id}--r{repetition}"})
        for case_id in GENERAL_CASES:
            other_jobs.append({"provider": "general-v3", "case": case_id, "repetition": repetition,
                               "job_id": f"general-v3--{case_id}--r{repetition}"})
    rng.shuffle(other_jobs)
    standard_jobs = bridge_jobs + other_jobs
    stress_jobs = []
    for case_id in STRESS_A:
        stress_jobs.append({"provider": "S001", "case": case_id, "repetition": 1,
                            "job_id": f"S001--{case_id}--stress-r1"})
    for case_id in STRESS_B:
        stress_jobs.append({"provider": "general-v3", "case": case_id, "repetition": 1,
                            "job_id": f"general-v3--{case_id}--stress-r1"})
    memory_jobs = [{"job_id": f"allocation--{provider}--{case_id}", "provider": provider, "case": case_id, "measurement": "tracemalloc_peak_bytes"}
                   for provider, case_id in ALLOCATION]
    rng_memory = random.Random(20261028)
    rng_memory.shuffle(memory_jobs)
    record = {
        "schema": "C004-stage1-performance-protocol-v1",
        "status": "frozen_pending_master_start",
        "created_from": {
            "corpus_manifest_sha256": sha(ROOT_MANIFEST),
            "corpus_freeze_record_sha256": sha(FREEZE),
            "runtime_stage1_sha256": sha(RUNTIME),
            "stage1_gate_report_sha256": sha(GATE),
            "protocol_text_sha256": sha(PROTOCOL),
            "capture_sha256": sha(CAPTURE),
        },
        "candidate_source_hashes": sources,
        "source_dependencies_included_in_capture": [x["path"] for x in sources],
        "selected_inputs": inputs,
        "measured_budget": {
            "hard_seconds_per_child": 30,
            "provider_seconds_ceiling": 900,
            "stress_seconds_ceiling": 180,
            "measured_scope": "whole fresh child from Python startup through input read, provider import, solve and normalized summary serialization; capture source snapshots excluded; no concurrent provider jobs",
            "internal_deadline_seconds": 29,
            "standard_job_counts": {"S001": 27, "C003-fixed-word": 9, "general-v3": 18},
            "stress_job_counts": {"S001": 3, "general-v3": 1},
            "memory_jobs_separate_from_timing": 5,
            "memory_note": "tracemalloc peak is Python allocation data, not RSS",
            "full_provider_outputs_and_independent_checks": "separate correctness captures; timed stdout contains identical normalized summary schema for compared methods"
        },
        "ordering": {
            "seed": 20261027,
            "common_pair_policy": "for each k=2 bridge cell and repetition, S001/C003 order is selected by deterministic seeded coin flip; all other standard jobs are deterministically shuffled after paired jobs",
            "stress_order": "after every standard timed job",
            "memory_seed": 20261028,
            "standard_jobs": standard_jobs,
            "stress_jobs": stress_jobs,
            "memory_jobs": memory_jobs
        }
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps({"protocol_freeze": str(OUT), "standard_jobs": len(standard_jobs),
                      "stress_jobs": len(stress_jobs), "memory_jobs": len(memory_jobs),
                      "source_count": len(sources), "selected_input_count": len(inputs),
                      "protocol_text_sha256": record["created_from"]["protocol_text_sha256"]},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()




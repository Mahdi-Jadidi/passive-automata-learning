"""Freeze v2 correctness argv, corrected diagnostic, unchanged corpus, and provenance."""
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
RESULTS = WORKSPACE / "results" / "2026-11-11"
FILES = [
    RESULTS / "review_optimization_v30" / "optimization" / "candidate_v1.py",
    RESULTS / "exact_foundations_v28" / "implementation" / "reference.py",
    RESULTS / "review_optimization_v30" / "review" / "CANDIDATE_SOURCE_VERDICT.md",
    RESULTS / "review_optimization_v30" / "optimization" / "PROPOSAL_PROOFS_V1.md",
    RESULTS / "review_optimization_v30" / "review" / "OPTIMIZATION_PROOF_VERDICT.md",
    RESULTS / "review_optimization_v30" / "review" / "DIAGNOSTIC_V2_VERDICT.md",
    HERE / "reference_oracle_v28.py", HERE / "verify_v28_oracle_v2.py",
    HERE / "freeze_suite.py", HERE / "benchmark_protocol.md",
    HERE / "fixed_cases.jsonl", HERE / "timing_cases.jsonl",
    HERE / "timing_worker.py", HERE / "run_timing.py",
    HERE / "verify_v28_oracle_v1_frozen.py", HERE / "FROZEN_MANIFEST_V1.json",
    HERE / "candidate_correctness_v1_stdout.txt", HERE / "candidate_correctness_v1_stderr.txt",
    HERE / "baseline_oracle_v2_stdout.txt", HERE / "baseline_oracle_v2_stderr.txt",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = {
    "status": "FROZEN_BEFORE_V2_CANDIDATE_RUN",
    "python_executable": sys.executable,
    "python_version": sys.version,
    "platform": platform.platform(),
    "candidate_expected_sha256": "7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b",
    "baseline_expected_sha256": "5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94",
    "v2_harness_expected_sha256": "de3ff0e7e355396376b13dbc6f855edf22e995034b7ff858da04deb6efafabbb",
    "diagnostic": {"alphabet": ["a", "b"], "positive": [["a"], ["b"]],
                   "negative": [["a", "b"], ["b", "b"], ["a", "b", "b"]],
                   "tested_rgs": [0, 1], "expected_rejection_vectors":
                   {"a": [False, False, False], "b": [False, True, True]}},
    "argv": [sys.executable,
             str(HERE / "verify_v28_oracle_v2.py"), "--go"],
    "corpus": {"fixed": 24, "exhaustive_binary": 2187, "seeded_generic": 60,
               "unlimited_cases": 2271, "budget_pairs_per_variant": 8,
               "invalid_pairs_per_variant": 9,
               "timing": {"cases": 8, "solvers": ["baseline", "combined"],
                          "repetitions": 3, "maximum_calls": 48, "budget": None}},
    "files": {str(p.relative_to(WORKSPACE)): sha(p) for p in FILES},
}
dest = HERE / "FROZEN_MANIFEST_V2.json"
dest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": manifest["status"], "manifest": str(dest),
                  "candidate_sha256": sha(FILES[0]), "baseline_sha256": sha(FILES[1]),
                  "harness_sha256": sha(FILES[7]), "files": len(FILES)}, sort_keys=True))

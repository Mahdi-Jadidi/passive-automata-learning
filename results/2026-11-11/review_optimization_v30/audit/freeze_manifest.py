"""Write the frozen pre-candidate audit manifest and environment receipt."""
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
    HERE / "reference_oracle_v28.py", HERE / "verify_v28_oracle.py",
    HERE / "freeze_suite.py", HERE / "benchmark_protocol.md",
    HERE / "fixed_cases.jsonl", HERE / "timing_cases.jsonl",
    HERE / "timing_worker.py", HERE / "run_timing.py",
    HERE / "final_baseline_stdout.txt", HERE / "final_baseline_stderr.txt",
]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


manifest = {
    "status": "FROZEN_BEFORE_CANDIDATE_RUNS",
    "created_utc_local_clock_not_available": True,
    "python_executable": sys.executable,
    "python_version": sys.version,
    "platform": platform.platform(),
    "candidate_expected_sha256": "7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b",
    "baseline_expected_sha256": "5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94",
    "proposal_proof_sha256": "4a11b61337b0a1dda5e9969fdb1741e5d87d43a03ec74f5afbddbb712955ef79",
    "commands": [
        "python freeze_suite.py",
        "python verify_v28_oracle.py",
        "python verify_v28_oracle.py --go",
        "python run_timing.py",
    ],
    "correctness_corpus": {"fixed": 24, "exhaustive_binary": 2187, "seeded_generic": 60,
                           "total_unlimited": 2271, "budgets_per_variant": 8,
                           "invalid_per_variant": 9},
    "timing_matrix": {"cases": 8, "solvers": ["baseline", "combined"],
                      "repetitions": 3, "max_observations": 48,
                      "budget": None, "subprocess_timeout_seconds": 20},
    "files": {str(path.relative_to(WORKSPACE)): sha(path) for path in FILES},
}
(HERE / "FROZEN_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
print(json.dumps({"status": manifest["status"], "manifest": str(HERE / "FROZEN_MANIFEST.json"),
                  "candidate_sha256": sha(FILES[0]), "baseline_sha256": sha(FILES[1]),
                  "hashed_files": len(FILES)}, sort_keys=True))

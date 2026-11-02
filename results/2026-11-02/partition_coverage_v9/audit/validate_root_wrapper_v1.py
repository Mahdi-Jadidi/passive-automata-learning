#!/usr/bin/env python3
"""Independently replay one frozen C009 public-root-wrapper capture."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
sys.path.insert(0, str(ROOT))
from validate_provider_gate_v1 import blocks_to_rgs, compatible_set, project, replay_projection_witness

ATTEMPT_ID = "20261102T110302.722584Z_0d74867d73"
ADDENDUM_DIR = ROOT / "addenda"
INPUT_PATH = ADDENDUM_DIR / "feasible_count_not_unique_ownership_v1.json"
ORACLE_PATH = ADDENDUM_DIR / "oracle_v1.jsonl"
WRAPPER_PATH = WORKSPACE / "results/2026-11-02/partition_coverage_v9/solver.py"
SOLVER_PATH = WORKSPACE / "results/2026-11-02/partition_coverage_v9/implementation/ownership_solver_v1.py"
CLI_PATH = WORKSPACE / "results/2026-11-02/partition_coverage_v9/implementation/ownership_cli_v1.py"
REPORT_PATH = ROOT / "root_wrapper_validation_v1.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", default=ATTEMPT_ID)
    args = parser.parse_args()
    attempt = ROOT / "attempts" / args.attempt_id
    capture_manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    capture_result = json.loads((attempt / "result.json").read_text(encoding="utf-8"))
    raw_stdout = (attempt / "stdout.bin").read_bytes()
    raw_stderr = (attempt / "stderr.bin").read_bytes()
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8").strip())
    provider = json.loads(raw_stdout)
    expected = compatible_set(data)
    expected_sources = {
        WRAPPER_PATH: "543a020f690e0403f21799f2875df08aa9546688bccb65119499bff09a9b57a2",
        SOLVER_PATH: "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7",
        CLI_PATH: "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507",
        INPUT_PATH: "cc7fb05a6069f10dc4f36e8f9b1c80a81bb2f2d616f7153a687589cfcf93c0f1",
        ORACLE_PATH: "3b92eee5de17a24df27dfd3c19ca3666d9e328818ec09fb1eb1fe80ede1be9f3",
    }
    observed_sources = {str(Path(row["path"]).resolve()): row["sha256"] for row in capture_manifest["sources"]}
    if capture_manifest["label"] != "root-wrapper-count-ownership-addendum-v1":
        raise AssertionError("root wrapper capture label mismatch")
    if capture_result["execution_status"] != "success" or capture_result["exit_code"] != 0 or capture_result["child_reaped"] is not True:
        raise AssertionError("root wrapper capture was not a clean success/reaped process")
    if capture_result["stdout_sha256"] != sha(raw_stdout) or raw_stderr or capture_result["stderr_bytes"] != 0:
        raise AssertionError("root wrapper captured stream integrity failure")
    if not all(observed_sources.get(str(path.resolve())) == digest for path, digest in expected_sources.items()):
        raise AssertionError("root wrapper capture source snapshot mismatch")
    if provider.get("complete") is not True or provider.get("status") != "partial_ownership_identification":
        raise AssertionError("root wrapper status/completeness mismatch")
    provider_set = set()
    if len(provider["enumerated_partitions"]) != len(expected):
        raise AssertionError("root wrapper enumeration length mismatch")
    for witness in provider["enumerated_partitions"]:
        blocks = replay_projection_witness(witness, data)
        provider_set.add(blocks_to_rgs([list(block) for block in blocks], sorted(data["alphabet"])))
    if provider_set != expected or provider_set != {tuple(row) for row in oracle["compatible_rgs"]}:
        raise AssertionError("root wrapper full set differs from independent oracle")
    if provider.get("partition_count") != 2 or provider.get("partition_count_by_k") != {"2": 2}:
        raise AssertionError("root wrapper exact count mismatch")
    relations = {"".join(row["symbols"]): row for row in provider["pair_relations"]}
    expected_relations = {"ab": ("ambiguous", 1, 1), "ac": ("ambiguous", 1, 1), "bc": ("forced_different", 0, 2)}
    if set(relations) != set(expected_relations):
        raise AssertionError("root wrapper pair set mismatch")
    for pair, (relation, same_count, different_count) in expected_relations.items():
        row = relations[pair]
        if (row["relation"], row["same_partition_count"], row["different_partition_count"]) != (relation, same_count, different_count):
            raise AssertionError(f"root wrapper pair relation/count mismatch: {pair}")
        for side, key, should_same in (("same", "same_partition_witness", True), ("different", "different_partition_witness", False)):
            witness = row[key]
            exists = same_count > 0 if should_same else different_count > 0
            if (witness is not None) != exists:
                raise AssertionError(f"root wrapper pair witness existence mismatch: {pair} {side}")
            if witness is not None:
                blocks = [list(block) for block in witness]
                if not any(project("a", set(block)) not in {project(p, set(block)) for p in data["positive"]}
                           for block in blocks) and data["negative"]:
                    raise AssertionError(f"root wrapper pair witness does not reject negative: {pair} {side}")
                labels = {symbol: i for i, block in enumerate(blocks) for symbol in block}
                if ((labels[pair[0]] == labels[pair[1]]) is not should_same) or blocks_to_rgs(blocks, sorted(data["alphabet"])) not in expected:
                    raise AssertionError(f"root wrapper pair witness ownership/feasibility mismatch: {pair} {side}")
    report = {
        "schema_version": 1,
        "status": "accepted_root_wrapper_control",
        "attempt_id": args.attempt_id,
        "case_id": oracle["case_id"],
        "provider_partition_count": provider["partition_count"],
        "independent_partition_count": len(expected),
        "provider_pair_relations": {pair: row["relation"] for pair, row in relations.items()},
        "provider_sha256": sha(raw_stdout),
        "capture_stdout_sha256": capture_result["stdout_sha256"],
        "wrapper_sha256": sha(WRAPPER_PATH.read_bytes()),
        "solver_sha256": sha(SOLVER_PATH.read_bytes()),
    }
    with REPORT_PATH.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

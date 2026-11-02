#!/usr/bin/env python3
"""Independently validate complete scale cells and censor the cooperative-incomplete cell."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import run_scale_provider_v1 as run
from validate_provider_gate_v1 import blocks_to_rgs, feasible, replay_projection_witness


ROOT = run.ROOT
REPORT = ROOT / "scale_validation_v1.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads(run.MANIFEST.read_text(encoding="utf-8"))
    oracle_rows = [json.loads(line) for line in run.ORACLE.read_text(encoding="utf-8").splitlines()]
    oracle_by_id = {row["case_id"]: row for row in oracle_rows}
    ledger = [json.loads(line) for line in run.LEDGER.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(run.SUMMARY.read_text(encoding="utf-8"))
    preflight = json.loads((ROOT / "scale_preflight_v1.json").read_text(encoding="utf-8"))
    require(len(ledger) == len(manifest["cases"]) == len(oracle_rows) == 4, "scale cell count mismatch")
    require(summary["captured_cells"] == 4 and summary["all_child_processes_reaped"] is True,
            "scale batch did not capture/reap all four cells")
    require(preflight["status"] == "scale_preflight_passed" and preflight["failure_count"] == 0,
            "scale preflight failed")
    require(sha(run.LEDGER.read_bytes()) == summary["ledger_sha256"], "scale ledger hash mismatch")
    require(sha(run.ORACLE.read_bytes()) == summary["oracle_sha256"], "scale oracle hash mismatch")
    expected_sources = dict(run.EXPECTED)
    expected_sources.update({
        ROOT / "capture.py": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
        ROOT / "run_scale_provider_v1.py": sha(Path(run.__file__).read_bytes()),
    })
    complete_cases = []
    censored_cases = []
    for case, ledger_row in zip(manifest["cases"], ledger):
        case_id = case["case_id"]
        require(ledger_row["case_id"] == case_id, f"scale ledger order mismatch: {case_id}")
        require(ledger_row["input_sha256"] == case["input_sha256"], f"scale input hash mismatch: {case_id}")
        attempt_dir = ROOT / ledger_row["attempt_dir"]
        cap_manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
        cap_result = json.loads((attempt_dir / "result.json").read_text(encoding="utf-8"))
        raw_out = (attempt_dir / "stdout.bin").read_bytes()
        raw_err = (attempt_dir / "stderr.bin").read_bytes()
        require(cap_result["stdout_sha256"] == sha(raw_out) == ledger_row["stdout_sha256"], f"stdout hash mismatch: {case_id}")
        require(cap_result["stderr_sha256"] == sha(raw_err) == ledger_row["stderr_sha256"], f"stderr hash mismatch: {case_id}")
        require(cap_result["child_reaped"] is True and ledger_row["child_reaped"] is True, f"unreaped scale child: {case_id}")
        require(cap_manifest["label"] == f"scale-correctness-{case_id}", f"scale capture label mismatch: {case_id}")
        input_path = run.SCALE_DIR / case["path"]
        case_sources = dict(expected_sources)
        case_sources[input_path] = case["input_sha256"]
        observed_sources = {str(Path(item["path"]).resolve()): item["sha256"] for item in cap_manifest["sources"]}
        require(all(observed_sources.get(str(path.resolve())) == digest for path, digest in case_sources.items()),
                f"scale source snapshot mismatch: {case_id}")
        require(ledger_row["source_snapshot_match"] is True, f"runner marked source drift: {case_id}")
        oracle = oracle_by_id[case_id]
        data = json.loads(input_path.read_text(encoding="utf-8"))
        try:
            provider = json.loads(raw_out)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AssertionError(f"invalid provider JSON: {case_id}: {exc!r}") from exc
        if provider.get("complete") is False:
            require(provider.get("status") == "unknown", f"incomplete result not unknown: {case_id}")
            require(provider.get("partition_count") is None and provider.get("pair_relations") is None
                    and provider.get("representative") is None and provider.get("enumerated_partitions") is None,
                    f"incomplete result contains an exact claim: {case_id}")
            require(cap_result["exit_code"] == 3 and cap_result["execution_status"] == "program_error",
                    f"incomplete CLI status/exit mismatch: {case_id}")
            require(ledger_row["provider_status"] == "unknown" and ledger_row["provider_partition_count"] is None,
                    f"incomplete ledger row inconsistent: {case_id}")
            censored_cases.append({"case_id": case_id, "reason": provider.get("reason"),
                                   "dp_states": provider.get("metrics", {}).get("dp_states"),
                                   "dp_branches": provider.get("metrics", {}).get("dp_branches"),
                                   "block_masks_precomputed": provider.get("metrics", {}).get("block_masks_precomputed")})
            continue

        require(provider.get("complete") is True, f"complete status malformed: {case_id}")
        require(cap_result["execution_status"] == "success" and cap_result["exit_code"] == 0,
                f"completed cell process failed: {case_id}")
        expected_rgs = {tuple(rgs) for rgs in oracle["compatible_rgs"]}
        provider_set = set()
        for witness in provider["enumerated_partitions"]:
            normalized = replay_projection_witness(witness, data)
            provider_set.add(blocks_to_rgs([list(block) for block in normalized], sorted(data["alphabet"])))
        require(len(provider["enumerated_partitions"]) == len(expected_rgs), f"enumerated count mismatch: {case_id}")
        require(len(provider_set) == len(provider["enumerated_partitions"]), f"duplicate scale partitions: {case_id}")
        require(provider_set == expected_rgs, f"complete scale partition set mismatch: {case_id}")
        require(provider.get("partition_count") == oracle["partition_count"] == len(expected_rgs),
                f"total count mismatch: {case_id}")
        require(provider.get("partition_count_by_k") == oracle["k_histogram"], f"per-k count mismatch: {case_id}")
        require(provider.get("status") == "partial_ownership_identification", f"scale status mismatch: {case_id}")
        replay_projection_witness(provider.get("representative"), data)
        oracle_pairs = {tuple(row["symbols"]): row for row in oracle["pair_relations"]}
        provider_pairs = {tuple(row["symbols"]): row for row in provider["pair_relations"]}
        require(set(provider_pairs) == set(oracle_pairs), f"pair set mismatch: {case_id}")
        for symbols, expected_pair in oracle_pairs.items():
            row = provider_pairs[symbols]
            require(row["relation"] == expected_pair["relation"], f"pair relation mismatch: {case_id} {symbols}")
            require(row["same_partition_count"] == expected_pair["coown_count"]
                    and row["different_partition_count"] == expected_pair["different_count"],
                    f"pair count mismatch: {case_id} {symbols}")
            for side, should_same in (("same", True), ("different", False)):
                witness = row[f"{side}_partition_witness"]
                expected_rgs_witness = expected_pair[f"{side}_witness_rgs"]
                require((witness is not None) == (expected_rgs_witness is not None),
                        f"pair witness existence mismatch: {case_id} {symbols} {side}")
                if witness is not None:
                    blocks = [list(block) for block in witness]
                    require(feasible(data, blocks), f"pair witness infeasible: {case_id} {symbols} {side}")
                    rgs = blocks_to_rgs(blocks, sorted(data["alphabet"]))
                    i, j = (sorted(data["alphabet"]).index(symbol) for symbol in symbols)
                    require(rgs in expected_rgs and ((rgs[i] == rgs[j]) is should_same),
                            f"pair witness ownership mismatch: {case_id} {symbols} {side}")
        complete_cases.append(case_id)

    require(censored_cases == [{"case_id": "pair_atoms_m14_k2_4", "reason": "deadline_or_interruption",
                               "dp_states": 61664, "dp_branches": 1468414, "block_masks_precomputed": 16383}],
            f"unexpected scale censoring set: {censored_cases!r}")
    report = {
        "schema_version": 1,
        "status": "accepted_with_censoring" if len(complete_cases) == 3 and len(censored_cases) == 1 else "scale_gate_failed",
        "planned_cells": 4,
        "complete_cells_exact": complete_cases,
        "censored_cells": censored_cases,
        "mismatches": [],
        "oracle_sha256": sha(run.ORACLE.read_bytes()),
        "provider_ledger_sha256": sha(run.LEDGER.read_bytes()),
        "provider_run_summary_sha256": sha(run.SUMMARY.read_bytes()),
        "provider_solver_sha256": sha(run.SOLVER.read_bytes()),
        "provider_cli_sha256": sha(run.CLI.read_bytes()),
        "interpretation": "correctness-only bounded cells; no speed comparison; m14 output is incomplete and yields no ownership/count conclusion",
    }
    with REPORT.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted_with_censoring" else 1


if __name__ == "__main__":
    raise SystemExit(main())

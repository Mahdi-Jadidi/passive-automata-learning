#!/usr/bin/env python3
"""Independently validate the four captured C010 root-CLI scale results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SCALE = AUDIT / "scale_v1"
sys.path.insert(0, str(AUDIT))
from validate_provider_v2 import check_witness, feasible, partition_rgs, validate_edges_and_atoms  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check_source_closure(attempt_dir: Path) -> tuple[int, list[str]]:
    errors = []
    manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("source_snapshot_error") is not None:
        errors.append("capture source snapshot error")
    sources = manifest.get("sources", [])
    for row in sources:
        snapshot = AUDIT / row["snapshot"]
        if not snapshot.is_file():
            errors.append(f"missing captured source blob: {row.get('snapshot')}")
            continue
        raw = snapshot.read_bytes()
        if sha(raw) != row["sha256"] or len(raw) != int(row["bytes"]):
            errors.append(f"captured source blob hash/size mismatch: {row.get('path')}")
    return len(sources), errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    errors: list[str] = []
    manifest_raw = (SCALE / "manifest.json").read_bytes()
    scale_manifest = json.loads(manifest_raw.decode("utf-8"))
    oracle_raw = next((AUDIT / "attempts" / name / "stdout.bin").read_bytes()
                      for name in ("20261102T191543.345590Z_859ae8cc90",))
    oracle = json.loads(oracle_raw.decode("utf-8"))
    oracle_validation = json.loads((SCALE / "oracle_validation_v1.json").read_text(encoding="utf-8"))
    if oracle_validation.get("status") != "accepted_independent_scale_oracle" or oracle_validation.get("oracle_stdout_sha256") != sha(oracle_raw):
        errors.append("independent scale oracle is not accepted or its bytes changed")
    oracle_by_id = {row["case_id"]: row for row in oracle["cells"]}
    attempt_index = json.loads((SCALE / "provider_attempts_v1.json").read_text(encoding="utf-8"))
    if len(attempt_index.get("cells", [])) != 4:
        errors.append("provider attempt index is not exactly four cells")
    if len({row["attempt_id"] for row in attempt_index["cells"]}) != 4:
        errors.append("provider attempt IDs are not unique")

    cell_reports = []
    total_source_blobs_checked = 0
    complete_cells = 0
    censored_cells = 0
    for attempt_row in attempt_index["cells"]:
        case_id = attempt_row["case_id"]
        case = next((row for row in scale_manifest["cells"] if row["case_id"] == case_id), None)
        oracle_row = oracle_by_id.get(case_id)
        case_errors: list[str] = []
        if case is None or oracle_row is None:
            errors.append(f"unknown scale cell in attempt index: {case_id}")
            continue
        attempt_dir = AUDIT / attempt_row["attempt_dir"]
        result_raw = (attempt_dir / "result.json").read_bytes()
        cap = json.loads(result_raw.decode("utf-8"))
        stdout_raw = (attempt_dir / "stdout.bin").read_bytes()
        source_count, source_errors = check_source_closure(attempt_dir)
        total_source_blobs_checked += source_count
        case_errors.extend(f"source-closure: {item}" for item in source_errors)
        attempt_manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
        argv = attempt_manifest.get("command_argv", [])
        if attempt_manifest.get("timeout_seconds") != 30.0:
            case_errors.append("capture hard deadline differs from preregistered 30 seconds")
        if argv[-4:] != ["solve.py", f"audit/scale_v1/{case['input']['path']}", "--seconds", "28"]:
            case_errors.append("captured command does not match frozen root-wrapper invocation")
        if cap.get("attempt_id") != attempt_row["attempt_id"] or cap.get("label") != attempt_row["label"]:
            case_errors.append("attempt metadata differs from frozen provider_attempts index")
        if cap.get("stdout_sha256") != sha(stdout_raw) or cap.get("stdout_bytes") != len(stdout_raw):
            case_errors.append("captured stdout hash/size differs from attempt metadata")
        if attempt_row.get("stdout_sha256") != sha(stdout_raw) or attempt_row.get("stderr_sha256") != cap.get("stderr_sha256"):
            case_errors.append("attempt index raw stream hash differs")
        if cap.get("child_reaped") is not True:
            case_errors.append("provider child not confirmed reaped")

        input_path = SCALE / case["input"]["path"]
        input_raw = input_path.read_bytes()
        data = json.loads(input_raw.decode("utf-8"))
        if sha(input_raw) != case["input"]["sha256"]:
            case_errors.append("scale input hash differs from frozen manifest")
        source_rows = attempt_manifest.get("sources", [])
        source_hashes = {row["sha256"] for row in source_rows}
        if case["input"]["sha256"] not in source_hashes:
            case_errors.append("exact cell input was not included in captured source closure")
        readiness = json.loads((ROOT / "implementation" / "READINESS_V3.json").read_text(encoding="utf-8"))
        required_hashes = {
            "unrestricted_solver_v2.py": readiness["files"]["unrestricted_solver_v2.py"]["sha256"],
            "unrestricted_cli_v2.py": readiness["files"]["unrestricted_cli_v2.py"]["sha256"],
        }
        for suffix, digest in required_hashes.items():
            if not any(row["path"].replace("\\", "/").endswith("/" + suffix) and row["sha256"] == digest for row in source_rows):
                case_errors.append(f"frozen runtime hash absent from source closure: {suffix}")
        if not any(row["path"].replace("\\", "/").endswith("/solve.py") and row["sha256"] == "533bcbffe39fa18648567abcaeb1fd775d75d05561f42be007c03c849f41a989" for row in source_rows):
            case_errors.append("frozen root wrapper hash absent from source closure")
        errors.extend(f"{case_id}: {item}" for item in case_errors)

        if cap.get("execution_status") != "success" or cap.get("exit_code") != 0:
            censored_cells += 1
            cell_reports.append({
                "case_id": case_id, "attempt_id": cap.get("attempt_id"),
                "execution_status": cap.get("execution_status"),
                "scientific_status": "censored_incomplete_execution",
                "stdout_sha256": sha(stdout_raw), "stdout_bytes": len(stdout_raw),
                "external_duration_seconds": cap.get("duration_seconds"),
                "subprocess_seconds": cap.get("subprocess_seconds"),
                "source_snapshots_checked": source_count,
                "errors": case_errors,
            })
            errors.extend(f"{case_id}: {item}" for item in case_errors)
            continue
        try:
            result = json.loads(stdout_raw.decode("utf-8"))
        except Exception as exc:
            censored_cells += 1
            cell_reports.append({"case_id": case_id, "attempt_id": cap.get("attempt_id"),
                                 "scientific_status": "censored_unparseable_output",
                                 "stdout_sha256": sha(stdout_raw), "stdout_bytes": len(stdout_raw),
                                 "external_duration_seconds": cap.get("duration_seconds"),
                                 "subprocess_seconds": cap.get("subprocess_seconds"),
                                 "source_snapshots_checked": source_count,
                                 "errors": [f"stdout JSON parse failed: {exc!r}", *case_errors]})
            continue
        if result.get("complete") is not True or result.get("status") == "unknown":
            censored_cells += 1
            final_fields = ("partition_count", "partition_count_by_k", "k_max_compatible", "pair_relations", "representative")
            for field in final_fields:
                if result.get(field) is not None:
                    case_errors.append(f"incomplete provider result retained final field {field}")
            cell_reports.append({
                "case_id": case_id, "attempt_id": cap.get("attempt_id"),
                "execution_status": cap.get("execution_status"), "provider_status": result.get("status"),
                "scientific_status": "censored_provider_incomplete",
                "stdout_sha256": sha(stdout_raw), "stdout_bytes": len(stdout_raw),
                "external_duration_seconds": cap.get("duration_seconds"),
                "subprocess_seconds": cap.get("subprocess_seconds"),
                "source_snapshots_checked": source_count,
                "metrics": result.get("metrics"), "errors": case_errors,
            })
            errors.extend(f"{case_id}: {item}" for item in case_errors)
            continue

        try:
            expected_family = {tuple(rgs) for rgs in oracle_row["compatible_rgs"]}
            alphabet = sorted(data["alphabet"])
            expected_atoms = oracle_row["provider_atoms"]
            if result.get("status") != "partial_ownership_identification":
                raise ValueError("complete scale family should have multiple compatible partitions")
            if result.get("partition_count") != oracle_row["compatible_partition_count"]:
                raise ValueError("partition_count differs from independent oracle")
            if result.get("partition_count_by_k") != oracle_row["compatible_partition_count_by_k"]:
                raise ValueError("exact per-k spectrum differs from independent oracle")
            if result.get("k_max_compatible") != oracle_row["k_max_compatible"]:
                raise ValueError("exact k_max_compatible differs from oracle")
            atoms = validate_edges_and_atoms(data, result)
            if atoms != expected_atoms or result.get("k_max_upper_bound") != len(expected_atoms):
                raise ValueError("provider atom partition or certified upper bound differs")
            if result.get("swap_edge_witnesses") != oracle_row["swap_edges"]:
                raise ValueError("provider swap-edge certificates differ from independently replayed edges")
            if result.get("atom_projection_feasible") is not oracle_row["atom_partition_feasible"]:
                raise ValueError("atom feasibility flag differs from direct criterion")
            if result.get("enumerated_partitions") is not None:
                raise ValueError("default scale mode unexpectedly materialized the full family")

            representative = result.get("representative")
            check_witness(data, representative)
            rep_rgs = tuple(partition_rgs(representative["partition"], alphabet))
            if rep_rgs not in expected_family:
                raise ValueError("representative not in independently enumerated family")

            pair_expected = {tuple(row["symbols"]): row for row in oracle_row["pair_relations"]}
            provider_pairs = result.get("pair_relations")
            pair_actual = {tuple(row.get("symbols", [])): row for row in provider_pairs or []}
            if len(pair_actual) != len(pair_expected):
                raise ValueError("provider pair table incomplete")
            pair_witnesses_checked = 0
            for pair, expected in pair_expected.items():
                actual = pair_actual.get(pair)
                if actual is None:
                    raise ValueError(f"missing pair output {pair}")
                for field in ("relation", "same_partition_count", "different_partition_count"):
                    if actual.get(field) != expected[field]:
                        raise ValueError(f"pair {pair} {field} differs from independent oracle")
                for field, want_same in (("same_partition_witness", True), ("different_partition_witness", False)):
                    witness = actual.get(field)
                    witness_expected = expected["same_witness_rgs" if want_same else "different_witness_rgs"]
                    if (witness is not None) != (witness_expected is not None):
                        raise ValueError(f"pair {pair} {field} existence differs")
                    if witness is not None:
                        if not feasible(data, witness):
                            raise ValueError(f"pair {pair} {field} is infeasible")
                        observed_rgs = tuple(partition_rgs(witness, alphabet))
                        if observed_rgs not in expected_family:
                            raise ValueError(f"pair {pair} {field} is outside the independent family")
                        positions = [alphabet.index(pair[0]), alphabet.index(pair[1])]
                        together = observed_rgs[positions[0]] == observed_rgs[positions[1]]
                        if together is not want_same:
                            raise ValueError(f"pair {pair} {field} contradicts its relation")
                        pair_witnesses_checked += 1

            if result.get("partition_count") != len(expected_family):
                raise ValueError("oracle family size and total disagree")
            metrics = result.get("metrics", {})
            metric_fields = ("swap_pairs_tested", "swap_edges", "atoms", "atom_projection_checks",
                             "block_masks_computed", "dp_states", "dp_branches", "enumerated_partitions",
                             "preprocessing_seconds", "search_seconds", "provider_seconds")
            metrics_summary = {field: metrics.get(field) for field in metric_fields}
            complete_cells += 1
            cell_reports.append({
                "case_id": case_id, "attempt_id": cap.get("attempt_id"),
                "provider_status": result.get("status"), "scientific_status": "complete_exact_match",
                "partition_count": result["partition_count"],
                "partition_count_by_k": result["partition_count_by_k"],
                "k_max_upper_bound": result["k_max_upper_bound"],
                "k_max_compatible": result["k_max_compatible"],
                "pair_relations_checked": len(pair_expected),
                "pair_witnesses_replayed": pair_witnesses_checked,
                "representative_witness_replayed": True,
                "swap_edges": len(result["swap_edge_witnesses"]),
                "atoms": len(atoms),
                "stdout_bytes": len(stdout_raw), "stdout_sha256": sha(stdout_raw),
                "external_duration_seconds": cap.get("duration_seconds"),
                "subprocess_seconds": cap.get("subprocess_seconds"),
                "provider_seconds": metrics.get("provider_seconds"),
                "source_snapshots_checked": source_count,
                "metrics": metrics_summary,
                "errors": case_errors,
            })
        except Exception as exc:
            case_errors.append(str(exc))
            cell_reports.append({
                "case_id": case_id, "attempt_id": cap.get("attempt_id"),
                "provider_status": result.get("status"), "scientific_status": "completed_but_mismatch",
                "stdout_bytes": len(stdout_raw), "stdout_sha256": sha(stdout_raw),
                "external_duration_seconds": cap.get("duration_seconds"),
                "subprocess_seconds": cap.get("subprocess_seconds"),
                "source_snapshots_checked": source_count,
                "errors": case_errors,
            })
            errors.extend(f"{case_id}: {item}" for item in case_errors)

    status = "accepted_four_complete_scale_cells" if not errors and complete_cells == 4 and censored_cells == 0 else (
        "accepted_with_censoring" if not errors and complete_cells + censored_cells == 4 else "rejected_or_incomplete")
    report = {
        "schema_version": 1,
        "status": status,
        "scale_manifest_sha256": sha(manifest_raw),
        "scale_oracle_sha256": sha(oracle_raw),
        "attempt_index_sha256": sha((SCALE / "provider_attempts_v1.json").read_bytes()),
        "cells_planned": 4,
        "cells_complete_exact": complete_cells,
        "cells_censored": censored_cells,
        "source_snapshots_checked": total_source_blobs_checked,
        "errors": errors,
        "cells": cell_reports,
    }
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if status == "accepted_four_complete_scale_cells" else 1


if __name__ == "__main__":
    raise SystemExit(main())

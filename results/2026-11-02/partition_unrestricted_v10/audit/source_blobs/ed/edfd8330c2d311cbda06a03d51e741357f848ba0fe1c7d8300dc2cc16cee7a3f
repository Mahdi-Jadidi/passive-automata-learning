#!/usr/bin/env python3
"""Assemble the C010 machine-readable final research summary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CYCLE = ROOT.parent


def read(path: str):
    return json.loads((CYCLE / path).read_text(encoding="utf-8"))


def sha(path: str) -> str:
    return hashlib.sha256((CYCLE / path).read_bytes()).hexdigest()


main = read("audit/provider_validation_v2.json")
controls = read("audit/provider_controls_validation_v2.json")
cli = read("audit/cli_smoke_validation_v2.json")
scale_oracle = read("audit/scale_v1/oracle_validation_v1.json")
scale = read("audit/scale_v1/provider_validation_v1.json")
ledger = read("audit/ATTEMPT_LEDGER_V2.json")
attempt_by_label = {row.get("label"): row for row in ledger["attempts"]}

scale_cells = []
for cell in scale["cells"]:
    scale_cells.append({
        "case_id": cell["case_id"], "attempt_id": cell["attempt_id"],
        "scientific_status": cell["scientific_status"],
        "count": cell.get("partition_count"),
        "count_by_k": cell.get("partition_count_by_k"),
        "k_max_upper_bound": cell.get("k_max_upper_bound"),
        "k_max_compatible": cell.get("k_max_compatible"),
        "pair_relations_checked": cell.get("pair_relations_checked"),
        "pair_witnesses_replayed": cell.get("pair_witnesses_replayed"),
        "swap_edges": cell.get("swap_edges"), "atoms": cell.get("atoms"),
        "metrics": cell.get("metrics"),
        "external_subprocess_seconds": cell.get("subprocess_seconds"),
        "capture_duration_seconds": cell.get("external_duration_seconds"),
        "stdout_bytes": cell.get("stdout_bytes"), "stdout_sha256": cell.get("stdout_sha256"),
        "source_snapshots_checked": cell.get("source_snapshots_checked"),
    })

failed_attempts = []
for label in ("unrestricted_provider_full_set_gate_v1",
              "c010_scale_corpus_generation_v1",
              "c010_independent_scale_oracle_v1"):
    row = attempt_by_label[label]
    failed_attempts.append({
        "attempt_id": row["attempt_id"], "label": label,
        "execution_status": row["execution_status"],
        "scientific_status": row["scientific_status"],
        "note": row["scientific_note"],
        "stdout_sha256": row["stdout_sha256"], "stderr_sha256": row["stderr_sha256"],
    })

summary = {
    "schema_version": 1,
    "cycle": "C010",
    "status": "accepted_bounded_correctness_no_performance_claim",
    "model_assumptions": [
        "known nonempty alphabet", "disjoint component alphabets", "independent arbitrary regular factors",
        "exact finite complete-word labels", "no noise", "no externally supplied K", "no state bound or prime restriction"
    ],
    "identifiability_theorem": {
        "one_block_model_always_fits_consistent_finite_labels": True,
        "guaranteed_nontrivial_ownership_identification_without_K": False,
        "singleton_version_space_can_only_be_one_block": True,
        "forced_different_pair_possible": False,
    },
    "provider_v1": {
        "source_sha256": "e2d3e0df3e59acb7b359b4be7a41243d99e7c71f4743a2bb76192cbbebdded1c",
        "scientific_status": "rejected_by_static_spectrum_counterexample; no provider call",
        "finding": "Bell(k) was substituted for S(r,k) in fast-path spectrum",
        "record": "audit/PROVIDER_V1_STATIC_FINDINGS.json",
    },
    "provider_v2": {
        "source_sha256": "4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502",
        "readiness_sha256": "13733c49a331a05dd1b6e59dbb73cd2323d869b17d50bed88f9997ae855b420e",
        "static_review": "audit/PROVIDER_V2_STATIC_REVIEW_V1.md",
        "main_gate": {
            "status": main["status"],
            "provider_attempt_id": main["capture_attempt_id"],
            "rows": main["exact_full_sets_matched"],
            "expected_rows": main["expected_rows"],
            "compatible_partition_rows": main["total_compatible_partition_rows"],
            "projection_witnesses_replayed": main["enumerated_partition_witnesses_replayed"],
            "swap_edge_witnesses_replayed": main["swap_edge_witnesses_replayed"],
            "oracle_sha256": main["oracle_sha256"],
            "corpus_manifest_sha256": main["corpus_manifest_sha256"],
            "validation_report": "audit/provider_validation_v2.json",
        },
        "controls": {
            "status": controls["status"],
            "capture_attempt_id": controls["capture_attempt_id"],
            "invalid_rejected": controls["invalid_controls_rejected"],
            "invalid_expected": controls["invalid_controls_expected"],
            "expired_deadline_no_finality": controls["deadline_control_incomplete_no_finality"],
            "guarded_synthetic_interrupt_no_finality": controls["guarded_interrupt_incomplete_no_finality"],
            "validation_report": "audit/provider_controls_validation_v2.json",
        },
        "cli_smoke": {
            "status": cli["status"],
            "capture_attempt_id": cli["capture_attempt_id"],
            "count": cli["exact_partitions_observed"],
            "spectrum": cli["spectrum"],
            "validation_report": "audit/cli_smoke_validation_v2.json",
            "root_wrapper_help_attempt_id": attempt_by_label["c010_v2_root_wrapper_help_smoke_a1"]["attempt_id"],
        },
    },
    "scale_oracle": {
        "status": scale_oracle["status"],
        "validation_report": "audit/scale_v1/oracle_validation_v1.json",
        "symbol_partitions_enumerated": scale_oracle["symbol_partition_domains_enumerated"],
        "quotient_partitions_enumerated": scale_oracle["quotient_partition_domains_enumerated"],
        "pair_witnesses_replayed": scale_oracle["pair_witnesses_replayed"],
        "manifest_sha256": scale_oracle["scale_manifest_sha256"],
    },
    "scale_provider_gate": {
        "status": scale["status"], "cells_complete": scale["cells_complete_exact"],
        "cells_planned": scale["cells_planned"], "cells_censored": scale["cells_censored"],
        "source_snapshots_checked": scale["source_snapshots_checked"],
        "validation_report": "audit/scale_v1/provider_validation_v1.json",
        "cells": scale_cells,
    },
    "limitations": [
        "No comparative performance benchmark, memory benchmark, or universal speed claim.",
        "The four scale cells are structured correctness instances, not general m=14 or m=64 coverage.",
        "The m=10 and length-4096 fallback cells computed all nonempty block masks plus the empty mask; no reduction in the full mask universe was evidenced there.",
        "KeyboardInterrupt control was a deterministic injected exception at a protected call, not an operating-system signal race.",
        "Input validation precedes cooperative deadline protection; unknown non-K fields are ignored by the current API."
    ],
    "preserved_failed_attempts": failed_attempts,
    "attempt_ledger": {"path": "audit/ATTEMPT_LEDGER_V2.json", "sha256": sha("audit/ATTEMPT_LEDGER_V2.json"), "attempt_count": ledger["attempt_count"]},
    "integrity_result_path": "audit/INTEGRITY_FINAL.json",
    "final_report_path": "audit/AUDIT_FINAL_V1.md",
}

path = ROOT / "FINAL_SUMMARY_V1.json"
raw = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
with path.open("xb") as handle:
    handle.write(raw)
print(json.dumps({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                  "status": summary["status"], "scale_cells": len(scale_cells)}, sort_keys=True))

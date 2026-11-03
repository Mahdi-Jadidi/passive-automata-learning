#!/usr/bin/env python3
"""Capture the frozen C011 direct-RGS/family oracle exactly once."""
from __future__ import annotations
import json
from pathlib import Path
import sys
AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
RESULTS = ROOT.parent.parent
C010 = RESULTS / "2026-11-02" / "partition_unrestricted_v10"
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402
sources = {
    Path(__file__).resolve(),
    (AUDIT / "oracle_audit_v2.py").resolve(),
    (AUDIT / "oracle_audit_v1.py").resolve(),
    (AUDIT / "build_suite_v1.py").resolve(),
    (AUDIT / "build_performance_suite_v2.py").resolve(),
    (AUDIT / "CORRECTNESS_MANIFEST_V1.json").resolve(),
    (AUDIT / "CORRECTNESS_MANIFEST_V2.json").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V1.json").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V2.json").resolve(),
    (AUDIT / "COLLISION_CONTROLS_V2.json").resolve(),
    (AUDIT / "STATIC_REVIEW_INTERVAL_V1.md").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V1.json").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V2.json").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V3.json").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V4.json").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V5.json").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V6.json").resolve(),
    (AUDIT / "run_oracle_capture_v2_broken_literal_newline.py").resolve(),
    (AUDIT / "PERFORMANCE_BUILD_RECEIPT_V2.json").resolve(),
    (AUDIT / "CORPUS_BUILD_RECEIPT_V1.json").resolve(),
    (AUDIT / "capture.py").resolve(),
    (AUDIT / "PROTOCOL_V1.md").resolve(),
    (AUDIT / "PROTOCOL_V2.md").resolve(),
    (AUDIT / "PROTOCOL_PREFREEZE_DRAFT_V1.md").resolve(),
    (AUDIT / "run_pairwise_benchmark_v1.py").resolve(),
    (AUDIT / "run_memory_probe_capture_v1.py").resolve(),
    (AUDIT / "memory_probe_v1.py").resolve(),
    (AUDIT / "run_baseline_suite_capture_v1.py").resolve(),
    (AUDIT / "PROTOCOL_PREFREEZE_DRAFT_V1.md").resolve(),
    (AUDIT / "C011_RGS_ORACLE_V1.jsonl").resolve(),
    (AUDIT / "FULL_CORRECTNESS_ORACLE_V1.jsonl").resolve(),
    (AUDIT / "c010_oracle_v1.jsonl").resolve(),
    (C010 / "audit" / "corpus_v1" / "manifest.json").resolve(),
    (C010 / "audit" / "corpus_v1" / "oracle_v1.jsonl").resolve(),
    (C010 / "audit" / "oracle_independent_v1.py").resolve(),
    (C010 / "audit" / "validate_oracle_v1.py").resolve(),
    (C010 / "audit" / "PROTOCOL_PROVIDER_GATE_V2.md").resolve(),
    (C010 / "audit" / "THEOREM_BOUNDARIES_V1.md").resolve(),
    (C010 / "theory" / "PROOFS_v1.md").resolve(),
    (C010 / "implementation" / "unrestricted_solver_v2.py").resolve(),
    (C010 / "implementation" / "unrestricted_cli_v2.py").resolve(),
    (C010 / "implementation" / "READINESS_V3.json").resolve(),
    (ROOT / "coordination" / "CONTRACT.md").resolve(),
    (ROOT / "coordination" / "parent_manifest.json").resolve(),
}
for base in (AUDIT / "cases", AUDIT / "controls"):
    sources.update(path.resolve() for path in base.rglob("*") if path.is_file())
record = capture.capture(
    "c011_direct_rgs_and_family_oracle_v2",
    [sys.executable, "-B", "-X", "utf8", str(AUDIT / "oracle_audit_v2.py")],
    cwd=ROOT,
    timeout_seconds=180.0,
    source_paths=sorted(sources),
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
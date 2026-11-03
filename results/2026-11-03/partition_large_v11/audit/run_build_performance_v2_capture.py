#!/usr/bin/env python3
"""Durably capture the one justified C011 performance corpus correction."""
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
sources = [
    Path(__file__).resolve(),
    (AUDIT / "build_performance_suite_v2.py").resolve(),
    (AUDIT / "build_suite_v1.py").resolve(),
    (AUDIT / "oracle_audit_v1.py").resolve(),
    (AUDIT / "MANUAL_ATTEMPTS_V1.json").resolve(),
    (AUDIT / "CORRECTNESS_MANIFEST_V1.json").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V1.json").resolve(),
    (AUDIT / "CORPUS_BUILD_RECEIPT_V1.json").resolve(),
    (AUDIT / "capture.py").resolve(),
    (C010 / "audit" / "corpus_v1" / "manifest.json").resolve(),
    (C010 / "audit" / "corpus_v1" / "oracle_v1.jsonl").resolve(),
    (C010 / "audit" / "oracle_independent_v1.py").resolve(),
    (C010 / "implementation" / "unrestricted_solver_v2.py").resolve(),
    (C010 / "implementation" / "unrestricted_cli_v2.py").resolve(),
    (C010 / "audit" / "capture.py").resolve(),
    (ROOT / "coordination" / "CONTRACT.md").resolve(),
    (ROOT / "coordination" / "parent_manifest.json").resolve(),
]
record = capture.capture(
    "c011_build_performance_corpus_v2",
    [sys.executable, "-B", "-X", "utf8", str(AUDIT / "build_performance_suite_v2.py")],
    cwd=ROOT,
    timeout_seconds=30.0,
    source_paths=sources,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
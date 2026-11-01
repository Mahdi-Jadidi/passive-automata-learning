"""Capture and run the independent sparse scaling/proof-boundary audit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V5 = HERE.parent
CAPTURE = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE.parent))
import capture  # noqa: E402

source_paths = [
    Path(__file__), CAPTURE,
    HERE / "sparse_scaling_audit_v1.py",
    HERE / "sparse_scaling_audit_protocol_v1.json",
    V5 / "structural" / "sparse_certificate_v2.py",
    V5 / "structural" / "sparse_scaling_v1.py",
    V5 / "structural" / "sparse_scaling_protocol_v1.json",
    V5 / "structural" / "sparse_scaling_fixtures_v1.json",
    V5 / "structural" / "PROOF_SPARSE_SCALING_ADDENDUM_V1.md",
    V5 / "structural" / "PROOFS_SPARSE_Q_V2.md",
    V5 / "structural" / "minimization_result_v1.json",
    V5 / "structural" / "lockstep_unequal_counterexample_original_v1.json",
]
record = capture.capture(
    "audit-sparse-scaling-and-proof-boundaries-v1",
    [sys.executable, "-B", "-X", "utf8", str(HERE / "sparse_scaling_audit_v1.py")],
    cwd=REPO,
    timeout_seconds=120,
    source_paths=source_paths,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if record["execution_status"] == "success" else 1)

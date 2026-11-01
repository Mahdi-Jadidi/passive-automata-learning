"""Capture and run the v2 independent full-set gate from the frozen v2 corpus."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = HERE / "frozen_corpus_v2"
CAPTURE = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE.parent))
import capture  # noqa: E402

V5 = HERE.parent
source_paths = [
    Path(__file__), CAPTURE,
    HERE / "small_gate_driver_v1.py", HERE / "small_gate_driver_v2.py",
    HERE / "generate_corpus_v1.py", HERE / "generate_corpus_v2.py",
    HERE / "corpus_protocol_v1.json", HERE / "proof_gate_protocol_v1.json",
    HERE / "proof_gate_protocol_v2.json", HERE / "corpus_v2_generation_note.md",
    HERE / "graph_unit_controls_v1.json",
    V5 / "general" / "known_k_qexact_v2.py",
    V5 / "structural" / "sparse_certificate_v2.py",
    V5 / "structural" / "sparse_trace_fixtures_v1.json",
    V5 / "structural" / "PROOFS_SPARSE_Q_V2.md",
    V5 / "structural" / "PROOF_SPARSE_SCALING_ADDENDUM_V1.md",
    V5 / "structural" / "minimization_result_v1.json",
    V5 / "general" / "public_cli_v1.py",
    V5 / "solver.py",
    ROOT / "manifest_v1.json", ROOT / "freeze_record_v1.json",
]
for folder in (ROOT / "small" / "inputs", ROOT / "small" / "hidden",
               ROOT / "stage2" / "inputs", ROOT / "stage2" / "hidden"):
    source_paths.extend(sorted(folder.glob("*.json")))

record = capture.capture(
    "audit-small-full-set-gate-v2",
    [sys.executable, "-B", "-X", "utf8", str(HERE / "small_gate_driver_v2.py")],
    cwd=REPO,
    timeout_seconds=300,
    source_paths=source_paths,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if record["execution_status"] == "success" else 1)

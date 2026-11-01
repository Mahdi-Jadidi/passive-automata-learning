"""Launch the independent gate only through the shared immutable capture API."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CAPTURE = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE.parent))
import capture  # noqa: E402

CORPUS = HERE / "frozen_corpus_v1"
source_paths = [
    Path(__file__), HERE / "small_gate_driver_v1.py",
    HERE / "corpus_protocol_v1.json", HERE / "proof_gate_protocol_v1.json",
    HERE / "graph_unit_controls_v1.json",
    HERE.parent / "general" / "known_k_qexact_v2.py",
    HERE.parent / "structural" / "sparse_certificate_v2.py",
    HERE.parent / "structural" / "sparse_trace_fixtures_v1.json",
    CORPUS / "manifest_v1.json", CORPUS / "freeze_record_v1.json",
]
for folder in (CORPUS / "small" / "inputs", CORPUS / "small" / "hidden",
               CORPUS / "stage2" / "inputs", CORPUS / "stage2" / "hidden"):
    source_paths.extend(sorted(folder.glob("*.json")))

record = capture.capture(
    "audit-small-full-set-gate-v1",
    [sys.executable, "-B", "-X", "utf8", str(HERE / "small_gate_driver_v1.py")],
    cwd=REPO,
    timeout_seconds=300,
    source_paths=source_paths,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if record["execution_status"] == "success" else 1)

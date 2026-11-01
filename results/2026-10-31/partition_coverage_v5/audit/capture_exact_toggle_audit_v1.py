"""Capture and run the independent exact q-opposition toggle parity audit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V5 = HERE.parent
ROOT = HERE / "frozen_corpus_v2"
ON_GATE = V5 / "evidence" / "attempts" / "20261101T053324.043566Z_c9b3c6ee88"
CAPTURE = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE.parent))
import capture  # noqa: E402

source_paths = [
    Path(__file__), CAPTURE,
    HERE / "exact_toggle_audit_v1.py", HERE / "exact_toggle_audit_protocol_v1.json",
    HERE / "small_gate_driver_v2.py", HERE / "proof_gate_protocol_v2.json",
    V5 / "general" / "known_k_qexact_v2.py",
    ROOT / "manifest_v1.json", ROOT / "freeze_record_v1.json",
    ON_GATE / "stdout.bin", ON_GATE / "manifest.json", ON_GATE / "result.json",
]
for folder in (ROOT / "small" / "inputs", ROOT / "small" / "hidden",
               ROOT / "stage2" / "inputs", ROOT / "stage2" / "hidden"):
    source_paths.extend(sorted(folder.glob("*.json")))
record = capture.capture(
    "audit-exact-q-opposition-toggle-v1",
    [sys.executable, "-B", "-X", "utf8", str(HERE / "exact_toggle_audit_v1.py")],
    cwd=REPO,
    timeout_seconds=120,
    source_paths=source_paths,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if record["execution_status"] == "success" else 1)

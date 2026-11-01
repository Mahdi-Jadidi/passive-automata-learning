"""Capture and run independent tests against the workspace root CLI wrapper."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V5 = HERE.parent
GENERAL = V5 / "general"
CAPTURE = REPO / "results" / "2026-10-31" / "partition_coverage_v5" / "evidence" / "capture.py"
sys.path.insert(0, str(CAPTURE.parent))
import capture  # noqa: E402

source_paths = [
    Path(__file__), CAPTURE,
    HERE / "public_cli_root_audit_v1.py",
    HERE / "public_cli_root_audit_protocol_v1.json",
    V5 / "solver.py",
    GENERAL / "public_cli_v1.py",
    GENERAL / "known_k_qexact_v2.py",
    V5 / "structural" / "sparse_certificate_v2.py",
    GENERAL / "sanity_inputs_v1.json",
    GENERAL / "public_cli_certificate_input_v1.json",
    GENERAL / "sanity_invalid_v1.json",
]
record = capture.capture(
    "audit-root-cli-independent-v1",
    [sys.executable, "-B", "-X", "utf8", str(HERE / "public_cli_root_audit_v1.py")],
    cwd=REPO,
    timeout_seconds=120,
    source_paths=source_paths,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if record["execution_status"] == "success" else 1)

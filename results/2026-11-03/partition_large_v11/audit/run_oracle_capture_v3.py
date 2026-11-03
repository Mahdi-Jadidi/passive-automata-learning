#!/usr/bin/env python3
"""Minimal durable capture driver for the independent C011 oracle audit."""
from __future__ import annotations

import json
from pathlib import Path
import sys

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402

correctness_path = AUDIT / "CORRECTNESS_MANIFEST_V2.json"
performance_path = AUDIT / "PERFORMANCE_MANIFEST_V2.json"
correctness = json.loads(correctness_path.read_text(encoding="utf-8"))
performance = json.loads(performance_path.read_text(encoding="utf-8"))
sources = {
    Path(__file__).resolve(),
    (AUDIT / "capture.py").resolve(),
    (AUDIT / "oracle_audit_v2.py").resolve(),
    (AUDIT / "oracle_audit_v3.py").resolve(),
    correctness_path.resolve(),
    performance_path.resolve(),
    (AUDIT / "c010_oracle_v1.jsonl").resolve(),
    (AUDIT / "PROTOCOL_V2.md").resolve(),
}
for row in correctness["cases"]:
    sources.add((AUDIT / row["path"]).resolve())
for row in performance["cells"]:
    sources.add((AUDIT / row["path"]).resolve())

record = capture.capture(
    "c011_direct_rgs_and_family_oracle_v3",
    [sys.executable, "-B", "-X", "utf8", str(AUDIT / "oracle_audit_v3.py")],
    cwd=ROOT,
    timeout_seconds=180.0,
    source_paths=sorted(sources),
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))

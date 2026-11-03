#!/usr/bin/env python3
"""Durably capture the independent read-only C011 oracle validation."""
from __future__ import annotations

import json
from pathlib import Path
import sys

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402

correctness = json.loads((AUDIT / "CORRECTNESS_MANIFEST_V2.json").read_text(encoding="utf-8"))
performance = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
sources = {
    Path(__file__).resolve(),
    (AUDIT / "capture.py").resolve(),
    (AUDIT / "validate_oracle_v3.py").resolve(),
    (AUDIT / "CORRECTNESS_MANIFEST_V2.json").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V2.json").resolve(),
    (AUDIT / "c010_oracle_v1.jsonl").resolve(),
    (AUDIT / "C011_RGS_ORACLE_V3.jsonl").resolve(),
    (AUDIT / "FULL_CORRECTNESS_ORACLE_V3.jsonl").resolve(),
    (AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V3.json").resolve(),
    (AUDIT / "ORACLE_FREEZE_RECEIPT_V3.json").resolve(),
    (AUDIT / "PROTOCOL_V2.md").resolve(),
}
for row in correctness["cases"]:
    sources.add((AUDIT / row["path"]).resolve())
for row in performance["cells"]:
    sources.add((AUDIT / row["path"]).resolve())

record = capture.capture(
    "c011_independent_oracle_validation_v1",
    [sys.executable, "-B", "-X", "utf8", str(AUDIT / "validate_oracle_v3.py")],
    cwd=ROOT,
    timeout_seconds=180.0,
    source_paths=sorted(sources),
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))

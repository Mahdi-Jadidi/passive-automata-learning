#!/usr/bin/env python3
"""Run the frozen C010 provider once per frozen valid case, full enumeration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
sys.path.insert(0, str(ROOT / "implementation"))
import unrestricted_solver_v1  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


manifest_raw = (AUDIT / "corpus_v1" / "manifest.json").read_bytes()
manifest = json.loads(manifest_raw.decode("utf-8"))
for case in manifest["valid_cases"]:
    input_raw = (AUDIT / "corpus_v1" / case["path"]).read_bytes()
    data = json.loads(input_raw.decode("utf-8"))
    result = unrestricted_solver_v1.solve(data, deadline=None, enumerate_partitions=True)
    print(json.dumps({
        "case_id": case["case_id"],
        "input_sha256": sha(input_raw),
        "canonical_payload_sha256": case["canonical_payload_sha256"],
        "result": result,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")), flush=True)

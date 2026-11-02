#!/usr/bin/env python3
"""Captured full-family C010 v2 provider pass over frozen cases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
IMPLEMENTATION = ROOT / "implementation"
sys.path.insert(0, str(IMPLEMENTATION))
import unrestricted_solver_v2  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def run_case(case_id: str, kind: str, input_path: Path, data: dict) -> None:
    raw = input_path.read_bytes()
    result = unrestricted_solver_v2.solve(data, deadline=None, enumerate_partitions=True)
    print(json.dumps({
        "case_id": case_id,
        "kind": kind,
        "input_sha256": sha(raw),
        "canonical_payload_sha256": sha(json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")),
        "result": result,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")), flush=True)


manifest = json.loads((AUDIT / "corpus_v1" / "manifest.json").read_text(encoding="utf-8"))
for case in manifest["valid_cases"]:
    input_path = AUDIT / "corpus_v1" / case["path"]
    run_case(case["case_id"], "frozen_corpus", input_path,
             json.loads(input_path.read_text(encoding="utf-8")))

preflight = json.loads((IMPLEMENTATION / "PREFLIGHT_CASES_V1.json").read_text(encoding="utf-8"))
for case in preflight["cases"]:
    input_path = IMPLEMENTATION / case["input"]
    run_case(case["id"], "analytic_preflight", input_path,
             json.loads(input_path.read_text(encoding="utf-8")))

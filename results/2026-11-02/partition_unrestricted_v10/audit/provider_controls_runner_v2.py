#!/usr/bin/env python3
"""Captured C010 v2 invalid/deadline/guarded-interruption controls."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
IMPLEMENTATION = ROOT / "implementation"
sys.path.insert(0, str(IMPLEMENTATION))
import unrestricted_solver_v2  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def emit(case_id: str, kind: str, raw: bytes, result: dict) -> None:
    print(json.dumps({"case_id": case_id, "kind": kind,
                      "input_sha256": sha(raw), "result": result},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":")), flush=True)


invalid_manifest = AUDIT / "corpus_v1" / "invalid_cases.jsonl"
for line in invalid_manifest.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    input_path = AUDIT / "corpus_v1" / row["path"]
    raw = input_path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    emit(row["case_id"], "invalid_input", raw,
         unrestricted_solver_v2.solve(data, enumerate_partitions=True))

deadline_data = {"alphabet": ["a", "b"], "positive": [], "negative": []}
deadline_raw = json.dumps(deadline_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
emit("already_expired_deadline", "expired_deadline", deadline_raw,
     unrestricted_solver_v2.solve(deadline_data, deadline=time.perf_counter() - 1,
                                  enumerate_partitions=True))

interrupt_data = {"alphabet": ["a", "b"], "positive": [], "negative": []}
interrupt_raw = json.dumps(interrupt_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
original_extract_atoms = unrestricted_solver_v2._extract_atoms

def inject_guarded_keyboard_interrupt(*args, **kwargs):
    raise KeyboardInterrupt("auditor injected interruption at protected atom-extraction call")

unrestricted_solver_v2._extract_atoms = inject_guarded_keyboard_interrupt
try:
    result = unrestricted_solver_v2.solve(interrupt_data, enumerate_partitions=True)
finally:
    unrestricted_solver_v2._extract_atoms = original_extract_atoms
emit("synthetic_keyboard_interrupt_at_extraction_guard", "guarded_interrupt",
     interrupt_raw, result)

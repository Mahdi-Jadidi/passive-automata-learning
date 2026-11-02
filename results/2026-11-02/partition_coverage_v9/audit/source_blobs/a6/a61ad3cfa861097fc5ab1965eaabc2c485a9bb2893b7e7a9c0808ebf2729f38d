#!/usr/bin/env python3
"""Inject one deterministic SIGINT after three completed provider projections."""
from __future__ import annotations

import hashlib
import json
import signal
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IMPLEMENTATION = ROOT.parent / "implementation"
sys.path.insert(0, str(IMPLEMENTATION))
import ownership_solver_v1


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: interrupt_api_wrapper_v1.py INPUT.json")
    input_path = Path(sys.argv[1]).resolve()
    raw = input_path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    original_project = ownership_solver_v1._project
    projection_calls = 0
    triggered = False

    def interrupt_after_three(word, block, deadline=None):
        nonlocal projection_calls, triggered
        result = original_project(word, block, deadline)
        projection_calls += 1
        if projection_calls == 3:
            triggered = True
            signal.raise_signal(signal.SIGINT)
        return result

    ownership_solver_v1._project = interrupt_after_three
    result = ownership_solver_v1.solve(data, enumerate_partitions=True)
    envelope = {
        "schema_version": 1,
        "case_id": "interruption_after_three_projection_calls_v1",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "interrupt_triggered": triggered,
        "projection_calls_completed_before_interrupt": projection_calls,
        "result": result,
    }
    print(json.dumps(envelope, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

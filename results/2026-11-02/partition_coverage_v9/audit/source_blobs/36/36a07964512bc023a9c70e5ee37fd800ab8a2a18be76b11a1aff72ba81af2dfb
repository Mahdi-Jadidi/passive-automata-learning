#!/usr/bin/env python3
"""Create one deterministic non-planted long-word input for interruption control."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "controls"
OUT_PATH = OUT_DIR / "interruption_input_v1.json"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=False)
    left = "a" * 2048 + "b" * 2048
    right = "b" * 2048 + "a" * 2048
    payload = {"alphabet": list("abcdefgh"), "positive": [left], "negative": [right]}
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with OUT_PATH.open("xb") as handle:
        handle.write(raw)
    print(json.dumps({
        "status": "frozen_interruption_control_input",
        "case_id": "interruption_after_three_projection_calls_v1",
        "alphabet_size": 8,
        "word_length": 4096,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

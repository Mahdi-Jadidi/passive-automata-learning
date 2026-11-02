#!/usr/bin/env python3
"""Run the hash-frozen C007 provider once per case and emit durable JSONL."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
READINESS = IMPLEMENTATION / "READINESS_V1.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_readiness_hashes():
    ready = json.loads(READINESS.read_text(encoding="utf-8"))
    checked = []
    for field in ("runtime_dependencies", "versioned_artifacts"):
        for item in ready.get(field, []):
            path = (IMPLEMENTATION / item["path"]).resolve()
            actual = sha256(path)
            if actual != item["sha256"]:
                raise RuntimeError(f"readiness hash mismatch for {item['path']}: {actual}")
            checked.append(item["path"])
    return sha256(READINESS), checked


READINESS_SHA256, FROZEN_HASHES = verify_readiness_hashes()
sys.path.insert(0, str(IMPLEMENTATION))
import finest_solver_v3  # noqa: E402


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def api_input(data):
    return {
        "alphabet": list(data["alphabet"]),
        "positive": ["".join(word) for word in data["positive"]],
        "negative": ["".join(word) for word in data["negative"]],
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("adaptive", "reference"):
        raise SystemExit("usage: run_provider_batch_v1.py adaptive|reference INPUTS.jsonl")
    mode, path = sys.argv[1], Path(sys.argv[2])
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    statuses = Counter()
    errors = 0
    for row in rows:
        data = api_input(row["input"])
        payload_hash = hashlib.sha256(canonical(row["input"]).encode("utf-8")).hexdigest()
        try:
            result = finest_solver_v3.solve(data, mode=mode)
            statuses[result.get("status", "missing_status")] += 1
            record = {"record_type": "case_result", "case_id": row["case_id"],
                      "payload_sha256": payload_hash, "mode": mode, "result": result}
        except BaseException as error:
            errors += 1
            record = {"record_type": "case_error", "case_id": row["case_id"],
                      "payload_sha256": payload_hash, "mode": mode,
                      "exception_type": type(error).__name__, "exception": repr(error)}
        print(json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)
    summary = {"record_type": "batch_summary", "mode": mode, "rows": len(rows),
               "errors": errors, "statuses": dict(sorted(statuses.items())),
               "provider": "finest_solver_v3.py", "readiness_sha256": READINESS_SHA256,
               "frozen_dependency_hashes_checked": FROZEN_HASHES}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

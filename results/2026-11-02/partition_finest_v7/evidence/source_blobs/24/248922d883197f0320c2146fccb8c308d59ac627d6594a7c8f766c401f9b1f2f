#!/usr/bin/env python3
"""Run immutable C007 v4 on the frozen 218-row corpus, emitting JSONL."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"
INPUTS = ROOT / "audit" / "corpus_v1" / "all_valid_inputs.jsonl"
READINESS = IMPLEMENTATION / "READINESS_V4.json"
EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "inputs": "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b",
    "primary_oracle": "a4216c69d0328419086096ff7b28f7efc39f98fb85ff904d798c5a6f54421281",
    "independent_oracle": "290a82bd7fd1cae7d4e0aebb27a6ea90b91148ee47d0963012319d6339680d25",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require_hash(path: Path, expected: str, label: str) -> str:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} hash mismatch: {actual}")
    return actual


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("adaptive", "reference"):
        raise SystemExit("usage: run_provider_batch_v2.py adaptive|reference INPUTS.jsonl")
    mode, inputs_path = sys.argv[1], Path(sys.argv[2]).resolve(strict=True)
    provider_path = IMPLEMENTATION / "finest_solver_v4.py"
    cli_path = IMPLEMENTATION / "finest_cli_v2.py"
    protocol_path = IMPLEMENTATION / "PROTOCOL_V5.md"
    primary_path = ROOT / "audit" / "oracle_v1" / "all_k_rgs.jsonl"
    independent_path = ROOT / "audit" / "oracle_v1" / "all_k_independent_v3.jsonl"
    c006_path = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005_path = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"

    checks = {
        "provider": require_hash(provider_path, EXPECTED["provider"], "provider"),
        "cli": require_hash(cli_path, EXPECTED["cli"], "cli"),
        "protocol": require_hash(protocol_path, EXPECTED["protocol"], "protocol"),
        "inputs": require_hash(inputs_path, EXPECTED["inputs"], "inputs"),
        "primary_oracle": require_hash(primary_path, EXPECTED["primary_oracle"], "primary oracle"),
        "independent_oracle": require_hash(independent_path, EXPECTED["independent_oracle"], "independent oracle"),
        "c006": require_hash(c006_path, EXPECTED["c006"], "C006 dependency"),
        "c005": require_hash(c005_path, EXPECTED["c005"], "C005 dependency"),
    }
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    if readiness.get("provider_sha256") != checks["provider"]:
        raise RuntimeError("READINESS_V4 provider anchor mismatch")
    if readiness.get("cli_sha256") != checks["cli"]:
        raise RuntimeError("READINESS_V4 CLI anchor mismatch")
    if readiness.get("protocol_sha256") != checks["protocol"]:
        raise RuntimeError("READINESS_V4 protocol anchor mismatch")
    if readiness.get("parent_dependencies") != {
        "C006_solver_v5.py": checks["c006"],
        "C005_graph_helper_v2.py": checks["c005"],
    }:
        raise RuntimeError("READINESS_V4 parent dependency anchors mismatch")

    sys.path.insert(0, str(IMPLEMENTATION))
    import finest_solver_v4  # noqa: E402

    rows = [json.loads(line) for line in inputs_path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 218 or len({row["case_id"] for row in rows}) != 218:
        raise RuntimeError(f"expected 218 distinct rows, found {len(rows)}")
    statuses: Counter[str] = Counter()
    errors = 0
    for row in rows:
        data = {
            "alphabet": list(row["input"]["alphabet"]),
            "positive": ["".join(word) for word in row["input"]["positive"]],
            "negative": ["".join(word) for word in row["input"]["negative"]],
        }
        payload_hash = hashlib.sha256(canonical(row["input"]).encode("utf-8")).hexdigest()
        try:
            result = finest_solver_v4.solve(data, mode=mode)
            statuses[result.get("status", "missing_status")] += 1
            record = {"record_type": "case_result", "case_id": row["case_id"],
                      "payload_sha256": payload_hash, "mode": mode, "result": result}
        except BaseException as error:  # persist any provider failure as a row
            errors += 1
            record = {"record_type": "case_error", "case_id": row["case_id"],
                      "payload_sha256": payload_hash, "mode": mode,
                      "exception_type": type(error).__name__, "exception": repr(error)}
        print(json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)
    summary = {
        "record_type": "batch_summary", "mode": mode, "rows": len(rows),
        "errors": errors, "statuses": dict(sorted(statuses.items())),
        "provider": provider_path.name, "provider_sha256": checks["provider"],
        "readiness_sha256": sha256(READINESS), "source_hashes": checks,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

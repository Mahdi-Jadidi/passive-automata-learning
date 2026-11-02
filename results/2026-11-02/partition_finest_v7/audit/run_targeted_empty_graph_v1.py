#!/usr/bin/env python3
"""Run one frozen C007 empty-must-link control with the immutable v4 provider."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "input": "50700da2538c66552014ee993210006f7b9ef5df706bdbeae1b04ccb4ca69f17",
    "oracle_rgs": "5a4892243d6b90a40edf8052d18eeb91976f630f61507e8a611366b88e6bbe93",
    "oracle_poset": "303eb4faef79ee58c62551ee9f79bda906f735ad1882358b7ef5592f3cfea63c",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("adaptive", "reference"):
        raise SystemExit("usage: run_targeted_empty_graph_v1.py adaptive|reference INPUTS.jsonl")
    mode, input_path = sys.argv[1], Path(sys.argv[2]).resolve(strict=True)
    impl = ROOT / "implementation"
    provider = impl / "finest_solver_v4.py"
    cli = impl / "finest_cli_v2.py"
    protocol = impl / "PROTOCOL_V5.md"
    rgs_path = ROOT / "audit" / "targeted_empty_graph" / "oracle_rgs_v1.jsonl"
    poset_path = ROOT / "audit" / "targeted_empty_graph" / "oracle_poset_v1.jsonl"
    c006 = ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py"
    c005 = ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py"
    checks = {"provider": sha256(provider), "cli": sha256(cli), "protocol": sha256(protocol),
              "input": sha256(input_path), "oracle_rgs": sha256(rgs_path),
              "oracle_poset": sha256(poset_path), "c006": sha256(c006), "c005": sha256(c005)}
    if checks != EXPECTED:
        raise RuntimeError("frozen v4 target-control source/input hash mismatch: " + repr(checks))
    sys.path.insert(0, str(impl))
    import finest_solver_v4  # noqa: E402

    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 1 or rows[0].get("case_id") != "ctrl_empty_must_link_unique_3":
        raise RuntimeError("frozen targeted empty-graph corpus row changed")
    row = rows[0]
    source_data = row["input"]
    data = {"alphabet": list(source_data["alphabet"]),
            "positive": ["".join(word) for word in source_data["positive"]],
            "negative": ["".join(word) for word in source_data["negative"]]}
    payload_hash = hashlib.sha256(canonical(source_data).encode("utf-8")).hexdigest()
    result = finest_solver_v4.solve(data, mode=mode)
    record = {"record_type": "case_result", "case_id": row["case_id"],
              "payload_sha256": payload_hash, "mode": mode, "result": result}
    summary = {"record_type": "batch_summary", "mode": mode, "rows": 1,
               "provider": provider.name, "provider_sha256": checks["provider"],
               "source_hashes": checks}
    print(json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

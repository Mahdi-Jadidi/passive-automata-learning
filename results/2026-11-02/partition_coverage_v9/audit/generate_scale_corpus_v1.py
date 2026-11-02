#!/usr/bin/env python3
"""Freeze the four preregistered C009 correctness-only scale inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "scale_v1"
PROTOCOL = ROOT / "SCALE_PROTOCOL_V1.md"
GATE_REPORT = ROOT / "provider_gate_validation_v1.json"
CONTROL_REPORT = ROOT / "controls_validation_v3.json"
WRAPPER_REPORT = ROOT / "root_wrapper_validation_v1.json"
SOLVER = ROOT.parent / "implementation" / "ownership_solver_v1.py"
CLI = ROOT.parent / "implementation" / "ownership_cli_v1.py"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
    return raw


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite scale corpus: {OUT}")
    gate = json.loads(GATE_REPORT.read_text(encoding="utf-8"))
    controls = json.loads(CONTROL_REPORT.read_text(encoding="utf-8"))
    wrapper = json.loads(WRAPPER_REPORT.read_text(encoding="utf-8"))
    if gate.get("status") != "accepted_independent_provider_gate" or gate.get("mismatch_count") != 0:
        raise SystemExit("primary correctness gate not accepted")
    if controls.get("status") != "accepted_independent_controls_audit":
        raise SystemExit("controls not accepted")
    if wrapper.get("status") != "accepted_root_wrapper_control":
        raise SystemExit("root wrapper control not accepted")
    if sha(SOLVER.read_bytes()) != "79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7":
        raise SystemExit("provider solver hash drift")
    if sha(CLI.read_bytes()) != "356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507":
        raise SystemExit("provider CLI hash drift")

    (OUT / "inputs").mkdir(parents=True)
    specs = [
        (10, [2, 4]),
        (12, [3, 5]),
        (14, [2, 4]),
    ]
    cases = []
    for m, allowed_k in specs:
        alphabet = [chr(ord("a") + i) for i in range(m)]
        positive = "".join(alphabet)
        negative = []
        for i in range(0, m, 2):
            chars = list(positive)
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
            negative.append("".join(chars))
        case_id = f"pair_atoms_m{m}_k" + "_".join(str(k) for k in allowed_k)
        payload = {"alphabet": alphabet, "positive": [positive], "negative": negative, "allowed_k": allowed_k}
        path = OUT / "inputs" / f"{case_id}.json"
        raw = write_json(path, payload)
        cases.append({"case_id": case_id, "origin": "proved_pair_atom_coarsening_family", "path": f"inputs/{path.name}",
                      "input_sha256": sha(raw), "alphabet_size": m, "atom_count": m // 2,
                      "allowed_k": allowed_k, "positive_count": 1, "negative_count": m // 2,
                      "expected_partition_count": {10: 25, 12: 105, 14: 413}[m],
                      "expected_cross_atom_coown_count": {10: 8, 12: 26, 14: 96}[m]})

    alphabet = list("abcd")
    long_payload = {
        "alphabet": alphabet,
        "positive": ["a" * 2048 + "b" * 2048],
        "negative": ["b" * 2048 + "a" * 2048],
        "allowed_k": [2],
    }
    long_id = "long_word_m4_len4096_k2"
    long_path = OUT / "inputs" / f"{long_id}.json"
    long_raw = write_json(long_path, long_payload)
    cases.append({"case_id": long_id, "origin": "proved_adjacent_swap_long_word", "path": f"inputs/{long_path.name}",
                  "input_sha256": sha(long_raw), "alphabet_size": 4, "word_length": 4096,
                  "allowed_k": [2], "positive_count": 1, "negative_count": 1,
                  "expected_partition_count": 3})

    cases_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in cases).encode("utf-8")
    with (OUT / "cases.jsonl").open("xb") as handle:
        handle.write(cases_raw)
    file_rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "manifest.json"):
        raw = path.read_bytes()
        file_rows.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha(raw), "bytes": len(raw)})
    manifest = {
        "schema_version": 1,
        "status": "frozen_pending_scale_oracle_and_provider",
        "case_count": len(cases),
        "protocol_sha256": sha(PROTOCOL.read_bytes()),
        "primary_gate_validation_sha256": sha(GATE_REPORT.read_bytes()),
        "controls_validation_sha256": sha(CONTROL_REPORT.read_bytes()),
        "root_wrapper_validation_sha256": sha(WRAPPER_REPORT.read_bytes()),
        "provider_solver_sha256": sha(SOLVER.read_bytes()),
        "provider_cli_sha256": sha(CLI.read_bytes()),
        "cases": cases,
        "files": file_rows,
    }
    write_json(OUT / "manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "case_count": len(cases),
                      "cases": cases, "manifest_sha256": sha((OUT / "manifest.json").read_bytes())}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

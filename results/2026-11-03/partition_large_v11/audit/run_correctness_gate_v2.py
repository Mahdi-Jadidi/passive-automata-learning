#!/usr/bin/env python3
"""Captured C011 correctness and controls only; no performance launch."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
C010 = ROOT.parent.parent / "2026-11-02" / "partition_unrestricted_v10"
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402

FIXED = {
    "implementation/unrestricted_solver_v3.py": "42726e740198787645783acefd1fa06f6490ec16d609ef07d22cbfafd34a00fa",
    "implementation/unrestricted_cli_v3.py": "169d7d468a5e3d8a0ba93b686ccb2b058ba231fa1b8e85150d5840df4fec563c",
    "implementation/READINESS_V6.json": "da444c56ce7fe33174ec5efd7b51b622f583af38fc4b13b30baf9936cdb7aec8",
    "audit/capture.py": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
    "audit/CORRECTNESS_MANIFEST_V2.json": "33d4054fbea394084e32fae3aa8f3a6cdfce62789b7856a7ae8fda21c81fd6b9",
    "audit/FULL_CORRECTNESS_ORACLE_V3.jsonl": "ee1992079e2565c2ebfb9e71a0fdbfed30a9d1e81c0ce369548d24e96fbd89cc",
    "audit/ORACLE_VALIDATION_REPORT_V4.json": "ea752b2be1a1965835b72825f67c02a03a025800334392d9369c769ff41bc6a8",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normal(data):
    return {"alphabet": sorted(data["alphabet"]), "positive": sorted(set(data["positive"])),
            "negative": sorted(set(data["negative"]))}


def preflight():
    for relative, digest in FIXED.items():
        if sha(ROOT / relative) != digest:
            raise SystemExit(f"frozen source/input drift: {relative}")
    go_path = ROOT / "coordination" / "MASTER_CORRECTNESS_GO_V1.json"
    go = json.loads(go_path.read_text(encoding="utf-8"))
    if go.get("status") != "GO" or go.get("phase") != "correctness_and_controls_only" or go.get("candidate_runs_authorized") is not True:
        raise SystemExit("master correctness/control GO missing or wrong phase")
    for row in go["bindings"].values():
        if sha(ROOT / row["path"]) != row["sha256"]:
            raise SystemExit(f"GO binding drift: {row['path']}")
    readiness = json.loads((ROOT / "implementation" / "READINESS_V6.json").read_text(encoding="utf-8"))
    if readiness.get("status") != "ready_for_preregistered_correctness_gate":
        raise SystemExit("candidate readiness is not approved for correctness")
    for name, row in readiness["implementation"].items():
        path = ROOT / "implementation" / row.get("path", name)
        if sha(path) != row["sha256"]:
            raise SystemExit(f"readiness binding drift: {name}")
    receipt = json.loads((AUDIT / "ORACLE_FREEZE_RECEIPT_V3.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "ORACLE_VALIDATION_REPORT_V4.json").read_text(encoding="utf-8"))
    if receipt.get("full_correctness_oracle_case_count") != 138 or validation.get("status") != "independent_oracle_validation_passed":
        raise SystemExit("independent oracle receipt/validation not accepted")
    if receipt["full_oracle_sha256"] != FIXED["audit/FULL_CORRECTNESS_ORACLE_V3.jsonl"]:
        raise SystemExit("oracle receipt source mismatch")
    manifest = json.loads((AUDIT / "CORRECTNESS_MANIFEST_V2.json").read_text(encoding="utf-8"))
    if len(manifest["cases"]) != 138 or len({x["case_id"] for x in manifest["cases"]}) != 138:
        raise SystemExit("frozen correctness job count/IDs mismatch")
    specs = []
    for row in manifest["cases"]:
        path = (AUDIT / row["path"]).resolve()
        if sha(path) != row["input_sha256"]:
            raise SystemExit(f"correctness input drift: {row['case_id']}")
        specs.append({"case_id": row["case_id"], "kind": "full", "input": str(path),
                      "input_sha256": sha(path), "mode": "constant" if row["case_id"].startswith("hash_collision_") else "normal"})
    regression = normal({"alphabet": ["a", "b", "c"], "positive": ["", "abc"], "negative": ["a"]})
    aliases = [x["case_id"] for x in specs if normal(json.loads(Path(x["input"]).read_text(encoding="utf-8"))) == regression]
    if not aliases:
        path = (AUDIT / "controls" / "none_witness_regression_v1.json").resolve()
        if normal(json.loads(path.read_text(encoding="utf-8"))) != regression:
            raise SystemExit("supplemental None witness input drift")
        specs.append({"case_id": "none_witness_regression_v1", "kind": "full", "input": str(path),
                      "input_sha256": sha(path), "mode": "normal"})
    invalid_manifest = C010 / "audit" / "corpus_v1" / "invalid_cases.jsonl"
    for line in invalid_manifest.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        path = (invalid_manifest.parent / row["path"]).resolve()
        if sha(path) != row["input_sha256"]:
            raise SystemExit(f"invalid control source drift: {row['case_id']}")
        specs.append({"case_id": "invalid_" + row["case_id"], "kind": "invalid", "input": str(path),
                      "input_sha256": sha(path), "mode": "normal"})
    control = next(x for x in specs if x["case_id"] == "no_labels_all_partitions")
    for mode in ("expired", "interrupt"):
        control_input = control if mode == "expired" else next(x for x in specs if x["case_id"] == "interval_two_symbol_nonadjacent")
        specs.append({"case_id": "control_" + mode, "kind": mode, "input": control_input["input"],
                      "input_sha256": control_input["input_sha256"], "mode": mode})
    specs.append({"case_id": "cli_smoke_no_labels", "kind": "cli", "input": control["input"],
                  "input_sha256": control["input_sha256"], "mode": "normal", "oracle_case_id": control["case_id"]})
    sources = {Path(__file__).resolve(), (AUDIT / "correctness_case_v2.py").resolve(),
               (AUDIT / "validate_correctness_gate_v2.py").resolve(), go_path.resolve(),
               (AUDIT / "PROTOCOL_V2.md").resolve(), (AUDIT / "ORACLE_FREEZE_RECEIPT_V3.json").resolve(),
               (ROOT / "implementation" / "API_PROTOCOL_V3.md").resolve(), invalid_manifest.resolve(),
               (AUDIT / "controls" / "execution_controls_v1.json").resolve(),
               (C010 / "audit" / "validate_provider_v2.py").resolve()}
    sources.add((C010 / "audit" / "corpus_v1" / "execution_controls_v1.json").resolve())
    sources.update(Path(x["input"]).resolve() for x in specs if x["kind"] in {"invalid", "expired", "interrupt"})
    sources.update((ROOT / path).resolve() for path in FIXED)
    sources.update((ROOT / row["path"]).resolve() for row in go["bindings"].values())
    source_hashes = {str(path): sha(path) for path in sorted(sources)}
    return specs, sorted(sources), source_hashes, aliases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    specs, sources, source_hashes, aliases = preflight()
    if args.preflight:
        print(json.dumps({"status": "preflight_ready_no_provider_executed", "planned_jobs": len(specs),
                          "full_corpus": 138, "none_regression_existing_aliases": aliases,
                          "source_hashes": source_hashes}, sort_keys=True))
        return 0
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:10]
    run = AUDIT / "correctness_runs_v2" / run_id
    run.mkdir(parents=True, exist_ok=False)
    plan = {"schema_version": 1, "run_id": run_id, "phase": "correctness_and_controls_only",
            "specs": specs, "source_hashes": source_hashes, "none_regression_existing_aliases": aliases}
    (run / "run_manifest.json").write_text(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with (run / "ledger.jsonl").open("x", encoding="utf-8", newline="\n") as ledger:
        for item in specs:
            for path, digest in source_hashes.items():
                if sha(Path(path)) != digest:
                    raise SystemExit(f"source changed during gate: {path}")
            path = Path(item["input"])
            if sha(path) != item["input_sha256"]:
                raise SystemExit(f"input changed during gate: {path}")
            command = ([sys.executable, "-B", "-X", "utf8", str(ROOT / "implementation" / "unrestricted_cli_v3.py"), str(path), "--enumerate", "--seconds", "28"]
                       if item["kind"] == "cli" else
                       [sys.executable, "-B", "-X", "utf8", str(AUDIT / "correctness_case_v2.py"), str(path), "--mode", item["mode"]])
            result = capture.capture("c011_correctness_" + item["case_id"], command,
                                     cwd=ROOT, timeout_seconds=30, source_paths=[*sources, path])
            row = {**item, "attempt_id": result["attempt_id"], "execution_status": result["execution_status"]}
            ledger.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            ledger.flush()
            os.fsync(ledger.fileno())
            if result.get("child_reaped") is not True or result.get("cleanup_error") or result["execution_status"] in {"capture_error", "environment_error", "interrupted"}:
                raise SystemExit("capture supervision failed; remaining gate jobs not launched")
    validator_sources = {*sources, (run / "run_manifest.json").resolve(), (run / "ledger.jsonl").resolve()}
    for row in (json.loads(x) for x in (run / "ledger.jsonl").read_text(encoding="utf-8").splitlines()):
        attempt = AUDIT / "attempts" / row["attempt_id"]
        validator_sources.update((attempt / name).resolve() for name in ("manifest.json", "result.json", "stdout.bin", "stderr.bin"))
        validator_sources.add(Path(row["input"]))
    checked = capture.capture("c011_correctness_independent_validation_v1",
                              [sys.executable, "-B", "-X", "utf8", str(AUDIT / "validate_correctness_gate_v2.py"), str(run)],
                              cwd=ROOT, timeout_seconds=180, source_paths=sorted(validator_sources))
    (run / "validation_capture.json").write_text(json.dumps(checked, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": str(run), "validation_capture": checked}, sort_keys=True))
    return 0 if checked["execution_status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

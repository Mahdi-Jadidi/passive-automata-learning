"""Independently replay one captured invocation through the project root CLI."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
ATTEMPT_ID = "20261101T155408.832648Z_59e21f537e"
ATTEMPT = ROOT / "evidence" / "attempts" / ATTEMPT_ID
INPUT_PATH = ROOT / "implementation" / "example_manager_candidate_v1.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_gate_auditor():
    path = AUDIT / "gate_solver_v5_v6.py"
    spec = importlib.util.spec_from_file_location("c006_independent_gate_auditor_v6", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    capture_result = json.loads((ATTEMPT / "result.json").read_text(encoding="utf-8"))
    assert capture_result["execution_status"] == "success"
    assert capture_result["exit_code"] == 0 and capture_result["child_reaped"] is True
    raw = (ATTEMPT / "stdout.bin").read_bytes()
    assert len(raw) == capture_result["stdout_bytes"]
    assert sha(raw) == capture_result["stdout_sha256"]
    assert raw.endswith(b"\n")
    lines = raw.splitlines()
    assert len(lines) == 1, len(lines)
    result = json.loads(lines[0].decode("utf-8"))
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert result.get("status") == "not_decomposable"
    assert result.get("complete") is True and result.get("decision_complete") is True
    assert result.get("solutions") == []
    auditor = load_gate_auditor()
    valid, reason, cuts = auditor.replay_certificate_independently(data, result.get("certificate"))
    assert valid, (reason, cuts)
    assert result["certificate"].get("obstruction") == "complete_cut_collision_cover"
    assert cuts == 7
    assert result.get("certificate_check", {}).get("valid") is True
    report = {
        "scientific_status": "passed",
        "execution_status": "success",
        "attempt_id": ATTEMPT_ID,
        "cli_entry": "root solver.py -> implementation/cli_v4.py -> solver_v5.py",
        "capture_stdout_sha256": sha(raw),
        "cli_status": result["status"],
        "complete": result["complete"],
        "independent_certificate_replay": True,
        "certificate_kind": result["certificate"]["obstruction"],
        "canonical_cuts_checked": cuts,
        "input_sha256": sha(INPUT_PATH.read_bytes()),
        "provider_sha256": sha((ROOT / "implementation" / "solver_v5.py").read_bytes()),
        "cli_sha256": sha((ROOT / "implementation" / "cli_v4.py").read_bytes()),
        "root_wrapper_sha256": sha((ROOT / "solver.py").read_bytes()),
    }
    output = AUDIT / "validation_v2" / "root_cli_v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

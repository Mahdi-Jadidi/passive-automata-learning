"""Captured root-CLI integration gate; saves each raw child output before checks."""
import json
import sys
from pathlib import Path

from capture import capture

ROOT = Path(__file__).resolve().parents[4]
C003 = ROOT / "results/2026-10-26/partition_discovery_v3"
AUDIT = C003 / "audit"
GATE = AUDIT / "integration_gate_v2"
CLI = C003 / "solver.py"
RUNTIME = json.loads((C003 / "coordination/runtime_manifest.json").read_text(encoding="utf-8"))

CASES = {
    "valid": {"alphabet": ["a", "b"], "positive": ["ab", "ba"], "negative": ["aa"]},
    "coverage": {"alphabet": ["a", "b", "c"], "positive": ["abc"], "negative": []},
    "assumption": {"alphabet": ["a", "b"], "positive": ["ab", "aab"], "negative": []},
    "invalid": {"alphabet": ["a", "b"], "positive": ["ab"], "negative": ["ab"]},
}

def put(path, value):
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as f:
        f.write(raw)

def main():
    GATE.mkdir(parents=True, exist_ok=False)
    for name, data in CASES.items():
        put(GATE / f"{name}.json", data)
    rows = []
    source_paths = [CLI, Path(__file__), C003 / "coordination/runtime_manifest.json"]
    source_paths += [C003 / item["path"] for item in RUNTIME["files"]]
    for name in ("valid", "coverage", "assumption", "invalid"):
        methods = ("general", "fair-reference", "fixed-word") if name == "valid" else (
            ("fixed-word",) if name in ("coverage", "assumption") else ("general",))
        for method in methods:
            path = GATE / f"{name}.json"
            result = capture(f"C003_CLI_GATE_{name}_{method}",
                [sys.executable, "-B", "-X", "utf8", str(CLI), str(path),
                 "--method", method, "--max-solutions", "1", "--timeout-seconds", "30"],
                cwd=ROOT, timeout_seconds=35,
                source_paths=source_paths + [path])
            raw = (Path(result["attempt_dir"]) / "stdout.bin").read_bytes()
            decoded = json.loads(raw.decode("utf-8")) if raw.strip() else None
            expected_exit = {"valid": 0, "coverage": 4,
                             "assumption": 5, "invalid": 2}[name]
            expected_status = {"valid": "found", "coverage": "insufficient_coverage",
                               "assumption": "assumption_violation",
                               "invalid": "invalid_input"}[name]
            row = {"case": name, "method": method, "capture": result,
                   "json_status": decoded.get("status") if decoded else None}
            rows.append(row)
            (GATE / "results.jsonl").open("ab").write(
                (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
            expected_execution = "success" if expected_exit == 0 else "program_error"
            if result["execution_status"] != expected_execution or result["exit_code"] != expected_exit:
                raise AssertionError(f"CLI capture/exit mismatch after raw save: {row}")
            if decoded is None or decoded.get("status") != expected_status:
                raise AssertionError(f"CLI status mismatch after raw save: {row}")
    timeout_input = GATE / "valid.json"
    result = capture("C003_CLI_GATE_zero_deadline", [
        sys.executable, "-B", "-X", "utf8", str(CLI), str(timeout_input),
        "--method", "fixed-word", "--max-solutions", "1", "--timeout-seconds", "0"],
        cwd=ROOT, timeout_seconds=10, source_paths=source_paths + [timeout_input])
    raw = (Path(result["attempt_dir"]) / "stdout.bin").read_bytes()
    decoded = json.loads(raw.decode("utf-8")) if raw.strip() else None
    row = {"case": "zero_deadline", "method": "fixed-word", "capture": result,
           "json_status": decoded.get("status") if decoded else None}
    rows.append(row)
    with (GATE / "results.jsonl").open("ab") as f:
        f.write((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    if result["execution_status"] != "program_error" or result["exit_code"] != 3 or not decoded or decoded.get("status") != "incomplete":
        raise AssertionError(f"CLI incomplete mapping mismatch after raw save: {row}")
    print(json.dumps({"case_count": len(rows), "results_file": str(GATE / "results.jsonl"),
                      "outcomes": [{"case": r["case"], "method": r["method"],
                                    "exit": r["capture"]["exit_code"], "status": r["json_status"]}
                                   for r in rows]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""Hash frozen inputs, oracle, fixtures, and audit captures for report."""
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FILES = [
    ROOT / "implementation" / "reference.py",
    ROOT / "implementation" / "FREEZE.md",
    ROOT / "theory" / "SPEC.md",
    ROOT / "theory" / "PROOFS.md",
    ROOT / "theory" / "AMENDMENT_1.md",
    ROOT / "review" / "REVIEW_VERDICT.md",
    HERE / "reference_oracle_v28.py",
    HERE / "build_fixtures_v1.py",
    HERE / "run_independent_audit_v1.py",
    HERE / "binary_ternary_length2_v1.jsonl",
    HERE / "seeded_m3_to_m8_v1.jsonl",
    HERE / "edge_cases_v1.jsonl",
    HERE / "invalid_cases_v1.jsonl",
    HERE / "FIXTURE_MANIFEST_V1.json",
    HERE / "INDEPENDENT_AUDIT_RESULTS_V1.json",
    HERE / "audit_stdout_v2.txt",
    HERE / "audit_stderr_v2.txt",
    HERE / "audit_stderr_v1.txt",
    HERE / "AUDIT_REPORT_V1.md",
]

def entry(path):
    data = path.read_bytes()
    try:
        shown = str(path.relative_to(ROOT))
    except ValueError:
        shown = str(path.relative_to(HERE))
    return {"path": shown.replace("\\", "/"), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}

out = {
    "audit": "C028 independent finite correctness audit v1",
    "python": sys.version,
    "platform": platform.platform(),
    "commands": [
        "& 'C:\\Users\\Mahdi\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe' build_fixtures_v1.py",
        "& 'C:\\Users\\Mahdi\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe' run_independent_audit_v1.py 1> audit_stdout_v2.txt 2> audit_stderr_v2.txt",
    ],
    "results": json.loads((HERE / "INDEPENDENT_AUDIT_RESULTS_V1.json").read_text(encoding="utf-8")),
    "files": [entry(path) for path in FILES],
}
(HERE / "AUDIT_MANIFEST_V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"files": len(FILES), "manifest": "AUDIT_MANIFEST_V1.json",
                  "status": out["results"]["status"]}, sort_keys=True))

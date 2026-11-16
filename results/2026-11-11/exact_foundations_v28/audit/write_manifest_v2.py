"""Emit the final C028 audit evidence manifest."""
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
    ROOT / "theory" / "AMENDMENT_2.md",
    ROOT / "review" / "REVIEW_VERDICT.md",
    ROOT / "review" / "AMENDMENT_2_VERDICT.md",
    HERE / "reference_oracle_v28.py",
    HERE / "build_fixtures_v1.py",
    HERE / "run_independent_audit_v1.py",
    HERE / "write_manifest_v2.py",
    HERE / "binary_ternary_length2_v1.jsonl",
    HERE / "seeded_m3_to_m8_v1.jsonl",
    HERE / "edge_cases_v1.jsonl",
    HERE / "invalid_cases_v1.jsonl",
    HERE / "FIXTURE_MANIFEST_V1.json",
    HERE / "INDEPENDENT_AUDIT_RESULTS_V1.json",
    HERE / "INDEPENDENT_AUDIT_RESULTS_V2.json",
    HERE / "audit_stdout_v1.txt",
    HERE / "audit_stderr_v1.txt",
    HERE / "audit_stdout_v2.txt",
    HERE / "audit_stderr_v2.txt",
    HERE / "audit_stdout_v3.txt",
    HERE / "audit_stderr_v3.txt",
    HERE / "audit_stdout_v4.txt",
    HERE / "audit_stderr_v4.txt",
    HERE / "build_stdout_v2.txt",
    HERE / "build_stderr_v2.txt",
    HERE / "AUDIT_REPORT_V1.md",
    HERE / "AUDIT_REPORT_V2.md",
]

def item(path):
    raw = path.read_bytes()
    try:
        name = str(path.relative_to(ROOT))
    except ValueError:
        name = str(path.relative_to(HERE))
    return {"path": name.replace("\\", "/"), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}

out = {
    "audit": "C028 independent finite correctness audit v2 (Amendment 2 approved)",
    "python": sys.version,
    "platform": platform.platform(),
    "commands": [
        "& 'C:\\Users\\Mahdi\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe' build_fixtures_v1.py",
        "& 'C:\\Users\\Mahdi\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe' run_independent_audit_v1.py 1> audit_stdout_v4.txt 2> audit_stderr_v4.txt",
    ],
    "results": json.loads((HERE / "INDEPENDENT_AUDIT_RESULTS_V2.json").read_text(encoding="utf-8")),
    "files": [item(p) for p in FILES],
}
(HERE / "AUDIT_MANIFEST_V2.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"files": len(FILES), "status": out["results"]["status"],
                  "manifest": "AUDIT_MANIFEST_V2.json"}, sort_keys=True))

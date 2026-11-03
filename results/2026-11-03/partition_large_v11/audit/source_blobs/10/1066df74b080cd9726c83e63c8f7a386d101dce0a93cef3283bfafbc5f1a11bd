#!/usr/bin/env python3
"""Durably capture one separate baseline tracemalloc probe after the freeze/GO gate."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
RESULTS = ROOT.parent.parent
C010 = RESULTS / "2026-11-02" / "partition_unrestricted_v10"
C010_IMPL = C010 / "implementation"
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("--case-id", required=True)
args = parser.parse_args()
go_path = AUDIT / "MASTER_GO_V1.json"
if not go_path.is_file():
    raise SystemExit("master GO receipt absent; refusing memory probe")
go = json.loads(go_path.read_text(encoding="utf-8"))
if go.get("status") != "GO" or go.get("baseline_runs_authorized") is not True:
    raise SystemExit("master GO receipt does not authorize baseline probe")
manifest = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
case = next((row for row in manifest["cells"] if row["case_id"] == args.case_id), None)
if case is None:
    raise SystemExit("unknown performance cell")
if (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").exists() is False:
    raise SystemExit("oracle/freeze receipt absent; refusing memory probe")
input_path = AUDIT / case["path"]
if sha(input_path) != case["input_sha256"]:
    raise SystemExit("input hash drift")
solver = C010_IMPL / "unrestricted_solver_v2.py"
cli = C010_IMPL / "unrestricted_cli_v2.py"
readiness = C010_IMPL / "READINESS_V3.json"
expected = json.loads(readiness.read_text(encoding="utf-8"))["files"]
for path in (solver, cli):
    row = expected[path.name]
    if sha(path) != row["sha256"]:
        raise SystemExit("baseline readiness hash drift")
prior_seconds = 0.0
for result_path in (AUDIT / "attempts").glob("*/result.json"):
    prior_result = json.loads(result_path.read_text(encoding="utf-8"))
    label = str(prior_result.get("label", ""))
    if label.startswith(("c011_baseline_cli_", "c011_memory_baseline_")):
        prior_seconds += float(prior_result.get("duration_seconds", 0.0))
if prior_seconds + 14.0 > 900.0:
    raise SystemExit("method all-in budget would be exceeded; probe censored before launch")

sources = [
    Path(__file__).resolve(),
    (AUDIT / "memory_probe_v1.py").resolve(),
    (AUDIT / "PERFORMANCE_MANIFEST_V2.json").resolve(),
    (AUDIT / "CORRECTNESS_MANIFEST_V2.json").resolve(),
    (AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json").resolve(),
    (AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V2.json").resolve(),
    (AUDIT / "STATIC_REVIEW_INTERVAL_V1.md").resolve(),
    (AUDIT / "PROTOCOL_V1.md").resolve(),
    go_path.resolve(),
    (AUDIT / "capture.py").resolve(),
    input_path.resolve(), solver.resolve(), cli.resolve(), readiness.resolve(),
    (C010 / "audit" / "PROTOCOL_PROVIDER_GATE_V2.md").resolve(),
    (ROOT / "coordination" / "CONTRACT.md").resolve(),
    (ROOT / "coordination" / "parent_manifest.json").resolve(),
]
record = capture.capture(
    f"c011_memory_baseline_{args.case_id}",
    [sys.executable, "-B", "-X", "utf8", str(AUDIT / "memory_probe_v1.py"),
     "--input", str(input_path), "--solver", str(solver),
     "--module-name", "c010_unrestricted_solver_v2"],
    cwd=ROOT,
    timeout_seconds=12.0,
    source_paths=sources,
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))
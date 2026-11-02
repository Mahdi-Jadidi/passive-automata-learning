#!/usr/bin/env python3
"""Take one durable capture of the final read-only package integrity check."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
sys.path.insert(0, str(AUDIT))
import capture  # noqa: E402


source_paths: set[Path] = {
    Path(__file__).resolve(),
    (AUDIT / "verify_package_integrity_v1.py").resolve(),
    (AUDIT / "AUDIT_FINAL_V1.md").resolve(),
    (AUDIT / "FINAL_SUMMARY_V1.json").resolve(),
    (AUDIT / "ATTEMPT_LEDGER_V2.json").resolve(),
}

# Snapshot each durable capture record, raw stream, and every source blob those
# captures referenced. The verifier independently checks all of these bytes.
for attempt_dir in (AUDIT / "attempts").iterdir():
    manifest_path = attempt_dir / "manifest.json"
    result_path = attempt_dir / "result.json"
    if not manifest_path.is_file() or not result_path.is_file():
        continue
    source_paths.update((manifest_path.resolve(), result_path.resolve(),
                         (attempt_dir / "stdout.bin").resolve(),
                         (attempt_dir / "stderr.bin").resolve()))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for source in manifest.get("sources", []):
        source_paths.add((AUDIT / source["snapshot"]).resolve())

# Frozen corpus and scale data, protocols, reviewers, runtime and acceptance
# reports are also in the final checker capture's own source closure.
for base in (AUDIT / "corpus_v1", AUDIT / "scale_v1", AUDIT / "source_blobs"):
    source_paths.update(path.resolve() for path in base.rglob("*") if path.is_file())
for base in (AUDIT, ROOT / "implementation", ROOT / "theory", ROOT / "coordination"):
    for path in base.iterdir():
        if path.is_file() and path.name not in ("INTEGRITY_FINAL.json",):
            source_paths.add(path.resolve())
for name in ("solve.py",):
    source_paths.add((ROOT / name).resolve())

record = capture.capture(
    "c010_final_package_integrity_v1",
    [sys.executable, "-B", "-X", "utf8",
     str(AUDIT / "verify_package_integrity_v1.py"),
     "--current-label", "c010_final_package_integrity_v1",
     "--report", "audit/INTEGRITY_FINAL.json"],
    cwd=ROOT,
    timeout_seconds=180.0,
    source_paths=sorted(source_paths),
)
print(json.dumps(record, ensure_ascii=False, sort_keys=True))

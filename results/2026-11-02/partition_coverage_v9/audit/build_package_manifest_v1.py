#!/usr/bin/env python3
"""Close the audit package with a byte manifest and capture-stream integrity checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "PACKAGE_MANIFEST_V1.json"
FINAL_REPORT = ROOT / "FINAL_AUDIT_REPORT_FA.md"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite package manifest: {OUTPUT}")
    errors = []
    stream_checks = 0
    source_blob_checks = 0
    attempt_dirs = sorted(path for path in (ROOT / "attempts").iterdir() if path.is_dir())
    for attempt in attempt_dirs:
        manifest_path = attempt / "manifest.json"
        result_path = attempt / "result.json"
        stdout_path = attempt / "stdout.bin"
        stderr_path = attempt / "stderr.bin"
        if not all(path.exists() for path in (manifest_path, result_path, stdout_path, stderr_path)):
            errors.append({"path": str(attempt.relative_to(ROOT)), "error": "capture attempt missing manifest/result/stream"})
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
        if result.get("stdout_sha256") != digest(stdout) or result.get("stdout_bytes") != len(stdout):
            errors.append({"path": str(stdout_path.relative_to(ROOT)), "error": "stdout hash/length mismatch"})
        if result.get("stderr_sha256") != digest(stderr) or result.get("stderr_bytes") != len(stderr):
            errors.append({"path": str(stderr_path.relative_to(ROOT)), "error": "stderr hash/length mismatch"})
        stream_checks += 2
        for source in manifest.get("sources", []):
            blob_path = ROOT / source["snapshot"]
            if not blob_path.exists() or digest(blob_path.read_bytes()) != source["sha256"]:
                errors.append({"path": str(blob_path.relative_to(ROOT)), "error": "missing or mismatched source blob"})
            source_blob_checks += 1
    blob_files = sorted((ROOT / "source_blobs").rglob("*")) if (ROOT / "source_blobs").exists() else []
    for blob in blob_files:
        if not blob.is_file():
            continue
        expected = blob.name
        if len(expected) != 64 or digest(blob.read_bytes()) != expected:
            errors.append({"path": str(blob.relative_to(ROOT)), "error": "content-addressed blob hash mismatch"})
    files = []
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and p != OUTPUT):
        raw = path.read_bytes()
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(raw), "bytes": len(raw)})
    report_hash = digest(FINAL_REPORT.read_bytes())
    package = {
        "schema_version": 1,
        "status": "integrity_passed" if not errors else "integrity_errors",
        "final_report": {"path": FINAL_REPORT.name, "sha256": report_hash},
        "file_count_excluding_manifest": len(files),
        "capture_attempt_count": len(attempt_dirs),
        "captured_stream_checks": stream_checks,
        "source_blob_references_checked": source_blob_checks,
        "content_addressed_blobs_checked": sum(1 for p in blob_files if p.is_file()),
        "error_count": len(errors),
        "errors": errors,
        "files": files,
    }
    with OUTPUT.open("xb") as handle:
        handle.write((json.dumps(package, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({key: package[key] for key in (
        "status", "file_count_excluding_manifest", "capture_attempt_count", "captured_stream_checks",
        "source_blob_references_checked", "content_addressed_blobs_checked", "error_count", "final_report",
    )}, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

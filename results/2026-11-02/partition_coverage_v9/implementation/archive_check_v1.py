"""Read-only integrity checker for the C009 research archive.

Run from anywhere with the bundled or system Python (standard library only)::

    python -B -X utf8 results/2026-11-02/partition_coverage_v9/implementation/archive_check_v1.py \
        --report coordination/ARCHIVE_CHECK_V1.json

The report argument is a unique path relative to the C009 root. The checker
first snapshots its own exact source under implementation/.checker_snapshots,
then verifies manifests and archived bytes. It never launches research code.

The required coordination/runtime_final.json schema is a JSON object with a
nonempty ``files`` list. Each entry has ``path`` (absolute, or workspace-root
relative), ``sha256`` and ``bytes``. Paths are checked as supplied; no
basename/hash guessing is performed. An optional implementation/READINESS_V1.json
is checked only against the explicit known-file map below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
AUDIT = ROOT / "audit"
BORROWED_CAPTURE = (WORKSPACE / "results" / "2026-11-02" /
                    "partition_identification_v8" / "audit" / "evidence" / "capture.py")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def confined(path: Path, base: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(base.resolve(strict=True))
        return True
    except (OSError, ValueError):
        return False


def snapshot_self() -> dict[str, Any]:
    source = Path(__file__).resolve(strict=True)
    raw = source.read_bytes()
    digest = sha256_bytes(raw)
    snapshot_dir = ROOT / "implementation" / ".checker_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = snapshot_dir / f"archive_check_v1_{stamp}_{digest[:12]}.py"
    with target.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "source_path": source.relative_to(ROOT).as_posix(),
        "snapshot_path": target.relative_to(ROOT).as_posix(),
        "sha256": digest,
        "bytes": len(raw),
    }


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.parent_files = 0
        self.runtime_files = 0
        self.attempt_count = 0
        self.source_references = 0
        self.source_blobs = 0
        self.execution_status_counts: dict[str, int] = {}
        self.scientific_status_counts: dict[str, int] = {}
        self.attempt_rows: list[dict[str, Any]] = []
        self.borrowed_capture_provenance: dict[str, Any] | None = None

    def error(self, message: str) -> None:
        self.errors.append(message)

    def check_bytes(self, path: Path, expected_hash: Any, expected_bytes: Any,
                    label: str) -> bool:
        if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
            self.error(f"{label}: invalid sha256")
            return False
        if not is_int(expected_bytes) and not (
            isinstance(expected_bytes, str) and expected_bytes.isdigit()
        ):
            self.error(f"{label}: invalid byte count")
            return False
        if not path.is_file():
            self.error(f"{label}: missing file {path}")
            return False
        size = path.stat().st_size
        if size != int(expected_bytes):
            self.error(f"{label}: byte count mismatch {path}")
            return False
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            self.error(f"{label}: sha256 mismatch {path}")
            return False
        return True

    def check_parent_manifest(self) -> None:
        manifest_path = ROOT / "coordination" / "parent_manifest.json"
        try:
            manifest = read_json(manifest_path)
        except Exception as exc:
            self.error(f"parent manifest unreadable: {exc!r}")
            return
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if not isinstance(files, list):
            self.error("parent manifest files must be a list")
            return
        for index, entry in enumerate(files):
            self.parent_files += 1
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                self.error(f"parent manifest entry {index}: malformed")
                continue
            rel = Path(entry["path"])
            if rel.is_absolute():
                self.error(f"parent manifest entry {index}: expected workspace-relative path")
                continue
            path = (WORKSPACE / rel).resolve(strict=False)
            if not confined(path, WORKSPACE):
                self.error(f"parent manifest entry {index}: path escapes workspace")
                continue
            self.check_bytes(path, entry.get("sha256"), entry.get("bytes", path.stat().st_size if path.is_file() else None),
                             f"parent[{index}]")
        if self.parent_files == 0:
            self.error("parent manifest contains no files")

    def check_runtime_final(self) -> None:
        manifest_path = ROOT / "coordination" / "runtime_final.json"
        try:
            manifest = read_json(manifest_path)
        except Exception as exc:
            self.error(f"required runtime_final.json missing/unreadable: {exc!r}")
            return
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if not isinstance(files, list) or not files:
            self.error("runtime_final.json must contain a nonempty files list")
            return
        for index, entry in enumerate(files):
            self.runtime_files += 1
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                self.error(f"runtime_final entry {index}: malformed actual path entry")
                continue
            raw_path = Path(entry["path"])
            actual = raw_path if raw_path.is_absolute() else WORKSPACE / raw_path
            actual = actual.resolve(strict=False)
            if not confined(actual, WORKSPACE):
                self.error(f"runtime_final entry {index}: path escapes workspace")
                continue
            self.check_bytes(actual, entry.get("sha256"), entry.get("bytes"),
                             f"runtime_final[{index}]")

    def check_optional_readiness(self) -> None:
        readiness_path = ROOT / "implementation" / "READINESS_V1.json"
        if not readiness_path.exists():
            return
        try:
            readiness = read_json(readiness_path)
        except Exception as exc:
            self.error(f"optional READINESS_V1.json unreadable: {exc!r}")
            return
        expected = readiness.get("files") if isinstance(readiness, dict) else None
        if not isinstance(expected, dict):
            self.error("READINESS_V1.json files must be an object")
            return
        known = {
            "ownership_solver_v1.py": ROOT / "implementation" / "ownership_solver_v1.py",
            "ownership_cli_v1.py": ROOT / "implementation" / "ownership_cli_v1.py",
            "ownership_example_v1.json": ROOT / "implementation" / "ownership_example_v1.json",
            "API_PROTOCOL_V1.md": ROOT / "implementation" / "API_PROTOCOL_V1.md",
        }
        for key, path in known.items():
            if key not in expected:
                continue
            expected_hash = expected[key]
            if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
                self.error(f"readiness[{key}]: invalid sha256")
            elif not path.is_file() or sha256_file(path) != expected_hash:
                self.error(f"readiness[{key}]: known file hash mismatch {path}")

    def check_attempts(self) -> None:
        attempts_root = AUDIT / "attempts"
        if not attempts_root.is_dir():
            self.error("audit/attempts directory missing")
            return
        for directory in sorted(p for p in attempts_root.iterdir() if p.is_dir()):
            self.attempt_count += 1
            attempt_id = directory.name
            manifest_path = directory / "manifest.json"
            result_path = directory / "result.json"
            try:
                manifest = read_json(manifest_path)
            except Exception as exc:
                self.error(f"attempt {attempt_id}: manifest unreadable: {exc!r}")
                continue
            try:
                result = read_json(result_path)
            except Exception as exc:
                self.error(f"attempt {attempt_id}: result unreadable: {exc!r}")
                continue
            if not isinstance(manifest, dict) or not isinstance(result, dict):
                self.error(f"attempt {attempt_id}: manifest/result must be objects")
                continue
            if manifest.get("attempt_id") != attempt_id or result.get("attempt_id") != attempt_id:
                self.error(f"attempt {attempt_id}: attempt ID mismatch")

            execution = result.get("execution_status")
            scientific = result.get("scientific_status")
            if not isinstance(execution, str) or not execution:
                self.error(f"attempt {attempt_id}: missing execution_status")
                execution = "<missing>"
            if not isinstance(scientific, str) or not scientific:
                self.error(f"attempt {attempt_id}: missing scientific_status")
                scientific = "<missing>"
            self.execution_status_counts[execution] = self.execution_status_counts.get(execution, 0) + 1
            self.scientific_status_counts[scientific] = self.scientific_status_counts.get(scientific, 0) + 1

            sources = manifest.get("sources")
            snapshot_error = manifest.get("source_snapshot_error")
            if not isinstance(sources, list):
                self.error(f"attempt {attempt_id}: sources must be a list")
                sources = []
            if not sources:
                prelaunch_ok = (
                    isinstance(snapshot_error, str) and bool(snapshot_error.strip())
                    and execution == "capture_error"
                    and result.get("child_pid") is None
                    and result.get("child_reaped") is None
                    and result.get("exit_code") is None
                    and result.get("subprocess_seconds") == 0
                )
                if not prelaunch_ok:
                    self.error(f"attempt {attempt_id}: empty sources without proven prelaunch capture error")
            else:
                if snapshot_error is not None:
                    self.error(f"attempt {attempt_id}: sources present with source_snapshot_error")
                found_capture = False
                seen_paths: set[str] = set()
                for source_index, item in enumerate(sources):
                    self.source_references += 1
                    if not isinstance(item, dict):
                        self.error(f"attempt {attempt_id}: source {source_index} malformed")
                        continue
                    source_path = item.get("path")
                    digest = item.get("sha256")
                    byte_count = item.get("bytes")
                    snapshot = item.get("snapshot")
                    if not isinstance(source_path, str) or not Path(source_path).is_absolute():
                        self.error(f"attempt {attempt_id}: source {source_index} path must be absolute")
                    else:
                        normalized = os.path.normcase(os.path.normpath(source_path))
                        if normalized in seen_paths:
                            self.error(f"attempt {attempt_id}: duplicate source path {source_path}")
                        seen_paths.add(normalized)
                        if Path(source_path).resolve(strict=False) == (AUDIT / "capture.py").resolve():
                            found_capture = True
                        self.check_bytes(Path(source_path), digest, byte_count,
                                         f"attempt {attempt_id} current source {source_index}")
                    if not isinstance(snapshot, str):
                        self.error(f"attempt {attempt_id}: source {source_index} missing snapshot path")
                    else:
                        posix = PurePosixPath(snapshot)
                        if posix.is_absolute() or ".." in posix.parts:
                            self.error(f"attempt {attempt_id}: source snapshot path escapes audit root")
                        else:
                            snap_path = AUDIT.joinpath(*posix.parts)
                            if not confined(snap_path, AUDIT):
                                self.error(f"attempt {attempt_id}: source snapshot escapes audit root")
                            else:
                                self.check_bytes(snap_path, digest, byte_count,
                                                 f"attempt {attempt_id} snapshot {source_index}")
                if not found_capture:
                    self.error(f"attempt {attempt_id}: capture helper audit/capture.py not snapshotted")

            # Raw streams are authoritative bytes even for failed science or a timeout.
            for name in ("stdout", "stderr"):
                raw_path = directory / f"{name}.bin"
                self.check_bytes(raw_path, result.get(f"{name}_sha256"),
                                 result.get(f"{name}_bytes"), f"attempt {attempt_id} {name}")

            child_pid = result.get("child_pid")
            child_reaped = result.get("child_reaped")
            if execution in {"success", "program_error", "timed_out", "interrupted"} and child_pid is None:
                self.error(f"attempt {attempt_id}: execution status requires a launched child")
            if child_pid is not None:
                if not is_int(child_pid):
                    self.error(f"attempt {attempt_id}: child_pid must be integer or null")
                if child_reaped is not True:
                    self.error(f"attempt {attempt_id}: launched child was not confirmed reaped")
                if result.get("cleanup_scope") != "direct_child_only":
                    self.error(f"attempt {attempt_id}: unexpected child cleanup scope")
            elif child_reaped is not None:
                self.error(f"attempt {attempt_id}: child_reaped must be null when no child was launched")

            if not isinstance(result.get("subprocess_seconds"), (int, float)):
                self.error(f"attempt {attempt_id}: missing subprocess_seconds")
            if not isinstance(result.get("exit_code"), (int, type(None))):
                self.error(f"attempt {attempt_id}: invalid exit_code")
            self.attempt_rows.append({
                "attempt_id": attempt_id,
                "execution_status": execution,
                "scientific_status": scientific,
                "exit_code": result.get("exit_code"),
                "source_references": len(sources),
                "child_launched": child_pid is not None,
                "child_reaped": child_reaped,
            })
        if self.attempt_count == 0:
            self.error("no audit attempts found")

    def check_source_blobs(self) -> None:
        blob_root = AUDIT / "source_blobs"
        if not blob_root.is_dir():
            self.error("audit/source_blobs directory missing")
            return
        for blob in sorted(p for p in blob_root.rglob("*") if p.is_file()):
            self.source_blobs += 1
            digest = blob.name
            if not HEX64.fullmatch(digest):
                self.error(f"source blob has non-digest filename: {blob}")
                continue
            if blob.parent.name != digest[:2]:
                self.error(f"source blob prefix directory mismatch: {blob}")
            if sha256_file(blob) != digest:
                self.error(f"source blob content hash mismatch: {blob}")
        if self.source_blobs == 0:
            self.error("no content-addressed source blobs found")
        borrowed = AUDIT / "capture.py"
        if not borrowed.is_file() or not BORROWED_CAPTURE.is_file():
            self.error("borrowed C008/C009 capture helper missing")
        else:
            current_hash = sha256_file(borrowed)
            current_bytes = borrowed.stat().st_size
            origin_hash = sha256_file(BORROWED_CAPTURE)
            origin_bytes = BORROWED_CAPTURE.stat().st_size
            same = current_hash == origin_hash and current_bytes == origin_bytes
            if not same:
                self.error("C009 audit/capture.py no longer matches its borrowed C008 source")
            self.borrowed_capture_provenance = {
                "c009_path": borrowed.relative_to(ROOT).as_posix(),
                "origin_path": BORROWED_CAPTURE.relative_to(WORKSPACE).as_posix(),
                "sha256": current_hash,
                "bytes": current_bytes,
                "matches_origin": same,
            }

    def report(self, checker_snapshot: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "archive": "C009 partition_coverage_v9",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "status": "pass" if not self.errors else "fail",
            "error_count": len(self.errors),
            "errors": self.errors,
            "counts": {
                "parent_files_checked": self.parent_files,
                "runtime_final_files_checked": self.runtime_files,
                "attempts": self.attempt_count,
                "source_references": self.source_references,
                "content_addressed_source_blobs": self.source_blobs,
            },
            "execution_status_counts": self.execution_status_counts,
            "scientific_status_counts": self.scientific_status_counts,
            "attempts": self.attempt_rows,
            "borrowed_capture_provenance": self.borrowed_capture_provenance,
            "checker_snapshot": checker_snapshot,
            "scope": (
                "Archive byte/hash/manifest integrity only. Scientific failures, "
                "timeouts, and incomplete results are preserved as statuses and "
                "do not fail integrity when their recorded raw artifacts validate."
            ),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True,
                        help="unique output path relative to the C009 root")
    args = parser.parse_args(argv)

    # Preserve exact checker source before running any archive checks.
    checker_snapshot = snapshot_self()
    report_rel = Path(args.report)
    if report_rel.is_absolute():
        parser.error("--report must be relative to the C009 root")
    report_path = (ROOT / report_rel).resolve(strict=False)
    if not confined(report_path, ROOT):
        parser.error("--report escapes the C009 root")
    if report_path.exists():
        parser.error("--report must be a unique, not-yet-existing path")

    audit = Audit()
    audit.check_parent_manifest()
    audit.check_runtime_final()
    audit.check_optional_readiness()
    audit.check_attempts()
    audit.check_source_blobs()
    report = audit.report(checker_snapshot)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with report_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        parser.error("--report became non-unique; refusing to overwrite")
    print(json.dumps({"status": report["status"], "report": str(report_path),
                      "error_count": report["error_count"]}, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

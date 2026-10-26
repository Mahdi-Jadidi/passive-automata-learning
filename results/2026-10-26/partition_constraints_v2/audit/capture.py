"""Immutable, standard-library-only subprocess capture for C002 audit runs.

Usage::

    python -B -X utf8 capture.py LABEL [--cwd PATH] [--timeout-seconds N]
        [--source PATH ...] -- COMMAND [ARG ...]

The source paths are resolved from the caller's current directory. The capture
script is always snapshotted. Attempt folders are unique and never overwritten;
source snapshots are stored in content-addressed blobs. stdout/stderr are saved
as raw bytes so output is lossless. Environment values are recorded only from a
small allowlist; other environment values are omitted. The direct child only is
terminated/reaped on timeout or cooperative interruption. Abrupt capture-process
kills may leave a started attempt without final metadata. Child-buffered bytes
not yet flushed by the child cannot be recovered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import locale
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


AUDIT_DIR = Path(__file__).resolve().parent
ATTEMPTS_DIR = AUDIT_DIR / "attempts"
SOURCE_BLOBS_DIR = AUDIT_DIR / "source_blobs"
SAFE_ENV_VALUES = (
    "PYTHONUTF8", "PYTHONDONTWRITEBYTECODE", "PYTHONPATH", "VIRTUAL_ENV",
    "CONDA_PREFIX", "TZ", "LANG", "LC_ALL", "PROCESSOR_ARCHITECTURE",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _store_blob(data: bytes) -> tuple[str, str]:
    digest = _sha256(data)
    blob_dir = SOURCE_BLOBS_DIR / digest[:2]
    blob_dir.mkdir(parents=True, exist_ok=True)
    blob_path = blob_dir / digest
    try:
        with blob_path.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        if blob_path.read_bytes() != data:
            raise RuntimeError(f"content-addressed source collision: {digest}")
    return digest, str(blob_path.relative_to(AUDIT_DIR))


def _source_manifest(source_paths: list[Path]) -> list[dict[str, str]]:
    unique: dict[str, Path] = {}
    for path in [Path(__file__), *source_paths]:
        resolved = path.expanduser().resolve(strict=True)
        unique[str(resolved)] = resolved
    result = []
    for absolute, path in sorted(unique.items()):
        raw = path.read_bytes()
        digest, blob = _store_blob(raw)
        result.append({"path": absolute, "sha256": digest, "snapshot": blob,
                       "bytes": str(len(raw))})
    return result


def _environment_snapshot(cwd: Path) -> dict[str, object]:
    values = {key: os.environ[key] for key in SAFE_ENV_VALUES if key in os.environ}
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "python_flags": repr(sys.flags),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "preferred_encoding": locale.getpreferredencoding(False),
        "cwd": str(cwd),
        "allowlisted_environment_values": values,
        "omitted_environment_variable_count": sum(
            1 for key in os.environ if key not in SAFE_ENV_VALUES),
        "environment_policy": "allowlisted values only; remaining values omitted",
    }


def capture(label: str, command: list[str], *, cwd: Path | str | None = None,
            timeout_seconds: float = 30.0,
            source_paths: list[Path | str] | None = None) -> dict[str, object]:
    """Run one command and persist its complete execution record before return."""
    if not isinstance(label, str) or not label.strip():
        raise ValueError("label must be a nonempty string")
    if not command or any(not isinstance(part, str) for part in command):
        raise ValueError("command must be a nonempty list of strings")
    if timeout_seconds < 0 or timeout_seconds != timeout_seconds or timeout_seconds == float("inf"):
        raise ValueError("timeout_seconds must be finite and nonnegative")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "_" + uuid4().hex[:10]
    run_dir = ATTEMPTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    workdir = Path(cwd).expanduser().resolve() if cwd is not None else Path.cwd().resolve()
    args = [str(part) for part in command]
    started_clock = time.perf_counter()
    manifest: dict[str, object] = {
        "schema_version": 1,
        "attempt_id": run_id,
        "label": label,
        "started_utc": utc_now(),
        "command_argv": args,
        "cwd": str(workdir),
        "timeout_seconds": timeout_seconds,
        "environment": _environment_snapshot(workdir),
        "sources": [],
        "source_snapshot_error": None,
    }
    _write_json(run_dir / "manifest.json", manifest)

    exit_code: int | None = None
    execution_status = "capture_error"
    capture_error = None
    cleanup_error = None
    process = None
    process_started = None
    subprocess_seconds = 0.0
    stdout_path, stderr_path = run_dir / "stdout.bin", run_dir / "stderr.bin"
    # Create durable destinations before launching; no parent PIPE buffers.
    stdout_path.touch(exist_ok=False)
    stderr_path.touch(exist_ok=False)
    try:
        manifest["sources"] = _source_manifest(
            [Path(path) for path in (source_paths or [])])
        _write_json(run_dir / "manifest.json", manifest)
        child_env = os.environ.copy()
        child_env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
        child_env.setdefault("PYTHONUTF8", "1")
        with stdout_path.open("ab", buffering=0) as out, stderr_path.open("ab", buffering=0) as err:
            process_started = time.perf_counter()
            try:
                try:
                    process = subprocess.Popen(args, cwd=workdir, env=child_env,
                                               stdout=out, stderr=err, shell=False)
                except OSError as error:
                    execution_status = "environment_error"
                    capture_error = repr(error)
                    err.write(repr(error).encode("utf-8", errors="replace"))
                else:
                    try:
                        exit_code = process.wait(timeout=timeout_seconds)
                        execution_status = "success" if exit_code == 0 else "program_error"
                    except subprocess.TimeoutExpired:
                        execution_status = "timed_out"
                    except KeyboardInterrupt:
                        execution_status = "interrupted"
            finally:
                if process is not None:
                    try:
                        _terminate_and_reap(process)
                        exit_code = process.returncode
                    except Exception as error:
                        cleanup_error = repr(error)
                subprocess_seconds = time.perf_counter() - process_started
                os.fsync(out.fileno())
                os.fsync(err.fileno())
    except KeyboardInterrupt:
        execution_status = "interrupted"
    except Exception as error:
        execution_status = "capture_error"
        capture_error = repr(error)
        if not manifest["sources"]:
            manifest["source_snapshot_error"] = capture_error
        with stderr_path.open("ab", buffering=0) as err:
            err.write(repr(error).encode("utf-8", errors="replace"))
            os.fsync(err.fileno())

    _write_json(run_dir / "manifest.json", manifest)
    stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
    result: dict[str, object] = {
        "schema_version": 1,
        "attempt_id": run_id,
        "label": label,
        "execution_status": execution_status,
        "scientific_status": "not_assessed",
        "exit_code": exit_code,
        "duration_seconds": time.perf_counter() - started_clock,
        "subprocess_seconds": subprocess_seconds,
        "child_pid": process.pid if process is not None else None,
        "child_reaped": process.returncode is not None if process is not None else None,
        "cleanup_scope": "direct_child_only",
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": _sha256(stdout),
        "stderr_sha256": _sha256(stderr),
        "finished_utc": utc_now(),
    }
    if capture_error is not None:
        result["capture_error"] = capture_error
    if cleanup_error is not None:
        result["cleanup_error"] = cleanup_error
        result["primary_execution_status"] = execution_status
        result["execution_status"] = "capture_error"
    _write_json(run_dir / "result.json", result)
    return {"attempt_dir": str(run_dir), **result}


def _terminate_and_reap(process: subprocess.Popen) -> None:
    """Clean up only this capture's direct child; retry cooperative interrupts."""
    while True:
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            else:
                process.wait()
            return
        except KeyboardInterrupt:
            # A repeated Ctrl-C must not abandon a still-running owned child.
            continue


def _cli() -> int:
    argv = sys.argv[1:]
    if "--" not in argv:
        raise SystemExit("usage: capture.py LABEL [OPTIONS] -- COMMAND [ARG ...]")
    separator = argv.index("--")
    option_argv, command = argv[:separator], argv[separator + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("label")
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--source", action="append", type=Path, default=[])
    args = parser.parse_args(option_argv)
    record = capture(args.label, command, cwd=args.cwd,
                     timeout_seconds=args.timeout_seconds,
                     source_paths=args.source)
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return {"success": 0, "program_error": 1, "timed_out": 3,
            "environment_error": 4, "capture_error": 5,
            "interrupted": 130}[record["execution_status"]]


if __name__ == "__main__":
    raise SystemExit(_cli())

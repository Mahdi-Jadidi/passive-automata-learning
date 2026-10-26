"""Temporary branch-local capture until the auditor's capture runner is ready.

Usage: python record_attempt.py LABEL -- EXECUTABLE ARG...
Never overwrites a previous attempt; stores source bytes by SHA-256.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def main():
    label, marker, *command = sys.argv[1:]
    if marker != "--" or not command:
        raise SystemExit("expected LABEL -- COMMAND...")
    owned = Path(__file__).resolve().parent
    root = owned.parents[1]
    attempts = owned / "attempts"
    blobs = attempts / "source_blobs"
    blobs.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid4().hex[:8]
    run_dir = attempts / run_id
    run_dir.mkdir()
    paths = list(owned.glob("*.py")) + list(owned.glob("*.md"))
    paths += list((root / "common").glob("*.py"))
    paths += list((root / "baseline").glob("theory_*.json"))
    paths += [root / "baseline" / "partition_solver.py"]
    sources = []
    for path in sorted(set(paths)):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        blob = blobs / digest
        if not blob.exists():
            blob.write_bytes(raw)
        sources.append({"path": str(path.relative_to(root)), "sha256": digest,
                        "blob": str(blob.relative_to(root))})
    start = {"id": run_id, "label": label, "command": command,
             "cwd": str(owned), "environment": {"python": sys.version,
             "platform": sys.platform, "PYTHONDONTWRITEBYTECODE": "1"},
             "sources": sources,
             "started_utc": datetime.now(timezone.utc).isoformat()}
    (run_dir / "started.json").write_text(json.dumps(start, indent=2), encoding="utf-8")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    try:
        completed = subprocess.run(command, cwd=owned, env=env, capture_output=True,
                                   timeout=120)
        stdout, stderr = completed.stdout, completed.stderr
        code = completed.returncode
        execution = "success" if code == 0 else "program_error"
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b"", error.stderr or b""
        code, execution = None, "timed_out"
    except OSError as error:
        stdout, stderr = b"", repr(error).encode("utf-8")
        code, execution = None, "environment_error"
    (run_dir / "stdout.txt").write_bytes(stdout)
    (run_dir / "stderr.txt").write_bytes(stderr)
    result = {"id": run_id, "label": label, "execution_status": execution,
              "scientific_status": "not_decided_by_capture",
              "exit_code": code, "finished_utc": datetime.now(timezone.utc).isoformat()}
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (attempts / "journal.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result) + "\n")
    print(json.dumps({"attempt": str(run_dir), **result}))
    if stdout:
        print(stdout.decode("utf-8", errors="replace"))
    if stderr:
        print(stderr.decode("utf-8", errors="replace"), file=sys.stderr)
    return code if code is not None else 3


if __name__ == "__main__":
    sys.exit(main())

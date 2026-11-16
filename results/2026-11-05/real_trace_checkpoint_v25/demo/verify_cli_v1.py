"""Record five bounded, explanatory CLI runs; no timing comparison."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASES = [
    ("finite_memory_boundary.json", "0", "incompatible"),
    ("finite_memory_boundary.json", "1", "certified_unique"),
    ("finite_memory_boundary.json", "full", "ambiguous"),
    ("last_event_obstruction.json", "0", "ambiguous"),
    ("last_event_obstruction.json", "full", "ambiguous"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    results = []
    for filename, depth, expected in CASES:
        argv = [sys.executable, str(ROOT / "partition_events.py"), str(HERE / filename),
                "--model-version", "selected-output-v1", "--depth", depth, "--seconds", "5"]
        stem = f"{Path(filename).stem}_depth_{depth}"
        record = dict(argv=argv, input_sha256=sha(HERE / filename), expected=expected)
        try:
            p = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=25)
            (HERE / f"{stem}.stdout.json").write_bytes(p.stdout)
            (HERE / f"{stem}.stderr.txt").write_bytes(p.stderr)
            record.update(exit_code=p.returncode, stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
            out = json.loads(p.stdout)
            record.update(actual=out.get("status"), complete=out.get("complete"))
            valid = p.returncode == 0 and out.get("status") == expected and out.get("complete") is True
            if expected == "certified_unique":
                valid = valid and sorted(sorted(b) for b in out["partition"]) == [["x"], ["y"]]
            if expected == "ambiguous":
                valid = valid and len(out["alternatives"]) == 2
            record["passed"] = valid
        except (subprocess.TimeoutExpired, ValueError, OSError) as exc:
            record.update(passed=False, error=repr(exc))
        results.append(record)
    report = dict(scope="Five constructed advisor CLI demos, not real-data runs or a speed benchmark",
                  entrypoint_sha256=sha(ROOT / "partition_events.py"),
                  script_sha256=sha(Path(__file__)), results=results,
                  passed=all(r["passed"] for r in results))
    (HERE / "CLI_VERIFICATION_V1.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=report["passed"], calls=len(results))))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""One actual-data CLI smoke; compare the two witnesses with frozen audit output."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    path = HERE / "cage2_raw_qualified_train.json"
    argv = [sys.executable, str(ROOT / "partition_events.py"), str(path),
            "--model-version", "selected-output-v1", "--depth", "4", "--seconds", "20"]
    record = dict(scope="One manager CLI integration smoke, outside the 42-cell scientific sweep",
                  argv=argv, input_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    try:
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=25)
        (HERE / "real_cli.stdout.json").write_bytes(p.stdout)
        (HERE / "real_cli.stderr.txt").write_bytes(p.stderr)
        actual = json.loads(p.stdout)
        prior = json.loads((HERE.parent / "audit/ACTUAL_cage2_raw_qualified_V1.json").read_text())
        expected = next(r["result"] for r in prior["rows"] if r["depth"] == 4)
        equal = [w["blocks"] for w in actual["alternatives"]] == [w["blocks"] for w in expected["alternatives"]]
        record.update(exit_code=p.returncode, status=actual["status"],
                      witnesses_match_frozen_audit=equal,
                      passed=p.returncode == 0 and actual["complete"] is True
                             and actual["status"] == "ambiguous" and equal,
                      stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
    except (subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
        record.update(passed=False, error=repr(exc))
    (HERE / "REAL_CLI_VERIFICATION_V1.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=record["passed"], calls=1)))
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run a frozen infinite-target fixture set through one C003 provider.

Every case is emitted as JSONL immediately, before any audit assertions.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
C003 = ROOT / "results/2026-10-26/partition_discovery_v3"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--method", choices=("general", "fair-reference"), required=True)
    parser.add_argument("--limit", type=int, choices=(1, 2), required=True)
    parser.add_argument("--deadline-seconds", type=float, default=30)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("c003_cli", C003 / "solver.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    provider = cli.provider(args.method)
    for line in args.inputs.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        visible = json.loads(line)
        canonical = (json.dumps(visible["input"], ensure_ascii=False,
                                sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        started = time.perf_counter()
        try:
            result = provider.solve(visible["input"],
                                   deadline=started + args.deadline_seconds,
                                   max_solutions=args.limit)
            error = None
        except BaseException as exc:
            result = None
            error = repr(exc)
        record = {"case_id": visible["case_id"], "method": args.method,
                  "input_sha256": hashlib.sha256(canonical).hexdigest(),
                  "max_solutions": args.limit, "result": result,
                  "runner_error": error,
                  "runner_elapsed_seconds": time.perf_counter() - started}
        sys.stdout.write(json.dumps(record, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

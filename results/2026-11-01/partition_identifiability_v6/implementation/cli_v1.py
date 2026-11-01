"""Versioned JSON CLI for C006 implementation solver_v2."""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import solver_v2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with alphabet, positive, negative")
    parser.add_argument("--seconds", type=float, default=None,
                        help="cooperative wall duration from provider-call start")
    parser.add_argument("--max-solutions", type=int, default=1,
                        help="positive limit; use --all to enumerate all")
    parser.add_argument("--all", action="store_true", help="enumerate all compatible bipartitions")
    args = parser.parse_args(argv)
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds < 0):
        print(json.dumps({"status":"invalid_input", "error":"seconds must be finite and nonnegative"}))
        return 2
    if args.all and args.max_solutions != 1:
        print(json.dumps({"status":"invalid_input", "error":"--all cannot be combined with --max-solutions"}))
        return 2
    try:
        with args.input.open("r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"invalid_input", "error":str(exc)}, ensure_ascii=False))
        return 2
    deadline = None if args.seconds is None else time.perf_counter() + args.seconds
    try:
        result = solver_v2.solve(data, deadline=deadline,
                                 max_solutions=None if args.all else args.max_solutions)
    except ValueError as exc:
        print(json.dumps({"status":"invalid_input", "error":str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"found":0, "not_decomposable":0, "incomplete":3,
            "invalid_input":2, "runtime_error":4}.get(result["status"], 4)


if __name__ == "__main__":
    raise SystemExit(main())

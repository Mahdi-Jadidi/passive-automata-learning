"""JSON CLI for exact C011 ownership inference with RLE interval indexing."""
import argparse
import json
import math
import time
from pathlib import Path
import unrestricted_solver_v2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON containing alphabet, positive, negative")
    parser.add_argument("--seconds", type=float, default=None,
                        help="cooperative computation deadline in seconds")
    parser.add_argument("--enumerate", action="store_true",
                        help="export every compatible partition; no truncation")
    args = parser.parse_args(argv)
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds < 0):
        print(json.dumps({"status": "invalid_input", "error": "seconds must be finite and nonnegative"}))
        return 2
    try:
        with args.input.open("r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)}, ensure_ascii=False))
        return 2
    deadline = None if args.seconds is None else time.perf_counter() + args.seconds
    result = unrestricted_solver_v2.solve(data, deadline=deadline,
                                          enumerate_partitions=args.enumerate)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"invalid_input": 2, "incomplete": 3}.get(result["status"], 0)


if __name__ == "__main__":
    raise SystemExit(main())

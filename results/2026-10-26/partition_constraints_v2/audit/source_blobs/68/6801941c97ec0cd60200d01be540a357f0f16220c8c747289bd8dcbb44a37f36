"""Coordinator-promotable CLI: default frozen baseline, optional eager/lazy."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path


def locate_root():
    for parent in (Path(__file__).resolve().parent, *Path(__file__).resolve().parents):
        if (parent / "coordination" / "CONTRACT.md").is_file():
            return parent
    raise RuntimeError("cannot locate C002 root")


def load_provider(root, method):
    path = root / "approaches" / method / f"{method}_solver.py"
    spec = importlib.util.spec_from_file_location(f"c002_{method}_provider", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def baseline_result(data, *, deadline=None):
    from common.engine import SearchInterrupted, check_deadline
    from common.helpers import load_baseline, result_from_records, validate
    started = time.perf_counter()
    alphabet, positive, negative = validate(data)
    components, edges, records = [[a] for a in alphabet], [], []
    complete = True
    stats = {}
    try:
        check_deadline(deadline)
        old = load_baseline().solve(data, prune=True)
        components, edges = old["graph"]["components"], old["graph"]["edges"]
        records = old["feasible_partitions"]
        stats["complete_assignments"] = old["search"]["candidates_checked"]
        check_deadline(deadline)
    except (SearchInterrupted, KeyboardInterrupt):
        complete = False
    return result_from_records(alphabet, positive, negative, records,
                               method="baseline", components=components, edges=edges,
                               stats=stats, complete=complete,
                               metrics={"provider_seconds": time.perf_counter() - started,
                                        "baseline_engine": "immutable_v1",
                                        "deadline_granularity": "before_and_after_v1_call"})


def main(argv=None):
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--method", choices=("baseline", "eager", "lazy"), default="baseline")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args(argv)
    root = locate_root()
    sys.path.insert(0, str(root))
    if args.timeout_seconds < 0 or not args.timeout_seconds < float("inf"):
        parser.error("--timeout-seconds must be finite and nonnegative")
    deadline = started + args.timeout_seconds
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        if args.method == "baseline":
            result = baseline_result(data, deadline=deadline)
        else:
            result = load_provider(root, args.method).solve(data, deadline=deadline)
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}, ensure_ascii=False))
        return 2
    result.setdefault("metrics", {})["cli_seconds_before_serialization"] = time.perf_counter() - started
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["complete"] else 3


if __name__ == "__main__":
    sys.exit(main())

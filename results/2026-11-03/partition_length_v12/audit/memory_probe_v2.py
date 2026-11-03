#!/usr/bin/env python3
"""Separate tracemalloc probe for the same default result API; not a timing CLI."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import time
import tracemalloc
from pathlib import Path


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--module-name", default="measured_solver")
    parser.add_argument("--result-output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    tracemalloc.start()
    input_raw = args.input.read_bytes()
    data = json.loads(input_raw.decode("utf-8"))
    spec = importlib.util.spec_from_file_location(args.module_name, args.solver)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen solver source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.solve(data, deadline=None, enumerate_partitions=False)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with args.result_output.open("xb") as output:
        output.write(encoded)
    print(json.dumps({
        "result_sha256": sha(encoded),
        "status": result.get("status"),
        "complete": result.get("complete"),
        "partition_count": result.get("partition_count"),
        "k_max_compatible": result.get("k_max_compatible"),
        "input_sha256": sha(input_raw),
        "solver_sha256": sha(args.solver.read_bytes()),
        "serialized_default_output_bytes": len(encoded),
        "tracemalloc_current_bytes": current,
        "tracemalloc_peak_bytes": peak,
        "probe_elapsed_seconds": time.perf_counter() - started,
        "scope": "Python allocations after tracemalloc.start through solve and default JSON serialization; excludes OS/native allocations and untraced interpreter startup",
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""One fresh-process C005 timing or tracemalloc job; stdout preserves full JSON."""
from __future__ import annotations

import argparse
import importlib.util
import json
import time
import tracemalloc
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load provider {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_input(mode: str, path: Path, case_id: str | None):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if mode == "exact":
        return payload
    matches = [case for case in payload["cases"] if case["id"] == case_id]
    if len(matches) != 1:
        raise ValueError(f"expected one fixture row for {case_id}, got {len(matches)}")
    return matches[0]["data"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("exact", "sparse", "memory"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--case-id")
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--toggle", choices=("on", "off"), default="on")
    parser.add_argument("--provider", type=Path, required=True)
    parser.add_argument("--cooperative-seconds", type=float, default=28.0)
    args = parser.parse_args()
    data = read_input(args.mode, args.input, args.case_id)
    tracing = args.mode == "memory"
    if tracing:
        tracemalloc.start()
    if args.mode == "exact":
        provider = load_module("timed_exact_v2", args.provider)
        deadline = time.perf_counter() + args.cooperative_seconds
        result = provider.solve(
            data, k=data["k"], local_word_cap=args.q, deadline=deadline,
            max_solutions=None, use_q_opposition=args.toggle == "on",
            use_contextual_must_links=True,
        )
        output = result
    else:
        provider = load_module("timed_sparse_v2", args.provider)
        deadline = time.perf_counter() + args.cooperative_seconds
        result = provider.solve(
            data, k=data["k"], local_word_cap=args.q, deadline=deadline,
            max_solutions=1,
        )
        if tracing:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            output = {
                "memory": {
                    "traced_current_bytes": current,
                    "traced_peak_bytes": peak,
                    "scope": "after input parsing; includes sparse provider import and solve; excludes Python startup, input object, and outer JSON serialization; not RSS",
                },
                "result": result,
            }
        else:
            output = result
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

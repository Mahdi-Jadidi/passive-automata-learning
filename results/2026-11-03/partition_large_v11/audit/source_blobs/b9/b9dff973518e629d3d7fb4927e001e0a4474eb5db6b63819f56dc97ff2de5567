#!/usr/bin/env python3
"""One frozen C011 API call; used only by the captured correctness gate."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
SOLVER = ROOT / "implementation" / "unrestricted_solver_v3.py"
EXPECTED = "42726e740198787645783acefd1fa06f6490ec16d609ef07d22cbfafd34a00fa"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=("normal", "constant", "expired", "interrupt"), default="normal")
    args = parser.parse_args()
    if hashlib.sha256(SOLVER.read_bytes()).hexdigest() != EXPECTED:
        raise SystemExit("frozen solver source drift")
    spec = importlib.util.spec_from_file_location("c011_frozen_candidate", SOLVER)
    provider = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(provider)
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if args.mode == "constant":
        provider._fingerprint_range = lambda *unused: 0
    elif args.mode == "interrupt":
        original_extract = provider._extract_contractions
        original_check = provider._check
        progress = {}
        def injected(alphabet, positive, negative, deadline, metrics):
            def guarded_check(value):
                original_check(value)
                if metrics["positive_interval_records"] >= 1:
                    progress.update({"injected": True, "positive_interval_records": metrics["positive_interval_records"]})
                    raise KeyboardInterrupt("audit interruption after interval record")
            provider._check = guarded_check
            return original_extract(alphabet, positive, negative, deadline, metrics)
        provider._extract_contractions = injected
    deadline = time.perf_counter() - 1 if args.mode == "expired" else time.perf_counter() + 28
    result = provider.solve(data, deadline=deadline, enumerate_partitions=True)
    if args.mode == "interrupt":
        assert progress.get("injected") and progress["positive_interval_records"] >= 1
        result["audit_injection"] = progress
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return {"invalid_input": 2, "incomplete": 3}.get(result.get("status"), 0)


if __name__ == "__main__":
    raise SystemExit(main())

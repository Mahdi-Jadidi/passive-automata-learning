"""Fresh-process full-result timing runner for the frozen C004 Stage2 q2 comparison."""
from __future__ import annotations
import argparse
import hashlib
import importlib
import importlib.util
import json
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
PROTOCOL = HERE / "stage2_timing_protocol_v1.json"


def load_file_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load provider module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("method", choices=("general_v3_q2", "qop001_q2"))
    parser.add_argument("case")
    parser.add_argument("--memory", action="store_true")
    args = parser.parse_args()

    # Memory capture begins before protocol/input reads and provider imports.
    if args.memory:
        tracemalloc.start()
    child_start = time.perf_counter()
    deadline = child_start + 29.0
    protocol_raw = PROTOCOL.read_bytes()
    protocol = json.loads(protocol_raw.decode("utf-8-sig"))
    case_record = protocol["cases"][args.case]
    input_path = HERE / case_record["input_path"]
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))

    if args.method == "general_v3_q2":
        provider_path = PROJECT / "general" / "known_k_v3.py"
        provider = load_file_module("c004_timing_known_k_v3", provider_path)
        result = provider.solve(data, k=data["k"], local_word_cap=2,
                                max_solutions=2, deadline=deadline)
    else:
        structural_dir = str(PROJECT / "structural")
        if structural_dir not in sys.path:
            sys.path.insert(0, structural_dir)
        provider = importlib.import_module("bounded_certificate_v1")
        result = provider.solve(data, k=data["k"], local_word_cap=2,
                                max_solutions=2, deadline=deadline)

    envelope = {
        "schema": "C004-stage2-full-api-timing-v1",
        "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
        "case": args.case,
        "method": args.method,
        "k": data["k"],
        "local_word_cap": 2,
        "max_solutions": 2,
        "soft_deadline_seconds_from_child_entry": 29.0,
        "result": result,
    }
    serialized = json.dumps(envelope, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":"))
    if args.memory:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.stderr.write(json.dumps({"schema": "C004-python-tracemalloc-v1",
                                     "peak_traced_python_bytes": peak},
                                    sort_keys=True, separators=(",", ":")) + "\n")
        sys.stderr.flush()
    sys.stdout.write(serialized)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

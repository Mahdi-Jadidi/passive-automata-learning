"""Run one frozen dataset/method sequentially; stdout is durable JSONL evidence."""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
C003 = ROOT / "results/2026-10-26/partition_discovery_v3"

def load_provider(method):
    cli_spec = importlib.util.spec_from_file_location("c003_root_cli", C003 / "solver.py")
    cli = importlib.util.module_from_spec(cli_spec)
    cli_spec.loader.exec_module(cli)
    return cli.provider(method)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", required=True, type=Path)
    parser.add_argument("--method", required=True, choices=("general", "fair-reference", "fixed-word"))
    parser.add_argument("--max-solutions", default="auto", choices=("auto", "all", "1", "2"))
    parser.add_argument("--deadline-seconds", default=30, type=float)
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    provider = load_provider(args.method)
    for raw in args.input_file.read_text(encoding="utf-8").splitlines():
        if not raw: continue
        row = json.loads(raw)
        if row.get("dataset", args.dataset) != args.dataset and args.dataset != "all":
            continue
        if args.max_solutions == "auto":
            size = len(row["input"]["alphabet"])
            limit = None if size <= 10 else 1
        else:
            limit = None if args.max_solutions == "all" else int(args.max_solutions)
        started = time.perf_counter()
        deadline = started + args.deadline_seconds
        try:
            result = provider.solve(row["input"], deadline=deadline, max_solutions=limit)
            record = {"case_id": row["case_id"], "method": args.method,
                      "dataset": row.get("dataset", args.dataset),
                      "input_sha256": row.get("input_sha256"), "max_solutions": limit,
                      "result": result, "runner_elapsed_seconds": time.perf_counter() - started,
                      "runner_error": None}
        except BaseException as error:
            record = {"case_id": row.get("case_id"), "method": args.method,
                      "dataset": row.get("dataset", args.dataset),
                      "input_sha256": row.get("input_sha256"), "max_solutions": limit,
                      "result": None, "runner_elapsed_seconds": time.perf_counter() - started,
                      "runner_error": repr(error)}
        sys.stdout.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()

if __name__ == "__main__": main()

"""Fresh-process provider runner; stdout is a normalized full first-answer record."""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_solution(solution):
    raw_blocks = solution.get("blocks", [])
    order = sorted(range(len(raw_blocks)), key=lambda i: tuple(sorted(raw_blocks[i])))
    old_to_new = {old: new for new, old in enumerate(order)}
    blocks = [sorted(raw_blocks[i]) for i in order]
    languages = solution.get("positive_projection_languages")
    if languages is None and solution.get("local_words") is not None:
        languages = [[word] for word in solution["local_words"]]
    if languages is not None:
        languages = [sorted(set(languages[i])) for i in order]
    witnesses = []
    for witness in solution.get("negative_witnesses", []):
        copied = dict(witness)
        if isinstance(copied.get("block_index"), int):
            copied["block_index"] = old_to_new[copied["block_index"]]
        if isinstance(copied.get("all_unseen_block_indices"), list):
            copied["all_unseen_block_indices"] = sorted(
                old_to_new[i] for i in copied["all_unseen_block_indices"])
        witnesses.append(copied)
    witnesses.sort(key=lambda x: (x.get("negative", ""), x.get("block_index", -1)))
    answer = {"blocks": blocks}
    if languages is not None:
        answer["positive_projection_languages"] = languages
    if witnesses or "negative_witnesses" in solution:
        answer["negative_witnesses"] = witnesses
    return answer


def run(provider, case_id, input_path, memory):
    if memory:
        tracemalloc.start()
    start = time.perf_counter()
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    deadline = start + 29.0
    if provider == "S001":
        path = PROJECT / "structural" / "singleton_solver_v1.py"
        mod = load_module("timed_s001", path)
        result = mod.solve(data, k=data["k"], deadline=deadline, max_solutions=1)
    elif provider == "general-v3":
        path = PROJECT / "general" / "known_k_v3.py"
        mod = load_module("timed_general_v3", path)
        result = mod.solve(data, k=data["k"], deadline=deadline,
                           max_solutions=1, local_word_cap=None)
    elif provider == "C003-fixed-word":
        path = PROJECT.parents[2] / "results" / "2026-10-26" / "partition_discovery_v3" / "structural" / "fixed_word_solver.py"
        mod = load_module("timed_c003_fixed", path)
        result = mod.solve(data, deadline=deadline, max_solutions=1)
    else:
        raise ValueError(f"unknown provider: {provider}")
    summary = {"schema": "C004-timed-provider-summary-v1", "case": case_id,
               "k": data["k"], "status": result.get("status"),
               "search_exhausted": result.get("search_exhausted"),
               "decision_complete": result.get("decision_complete"),
               "uniqueness": result.get("uniqueness"),
               "solution_count": len(result.get("solutions", [])),
               "solutions": [canonical_solution(s) for s in result.get("solutions", [])]}
    if memory:
        encoded = json.dumps(summary, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        output = {"peak_traced_python_bytes": peak, "summary": summary}
        sys.stdout.write(json.dumps(output, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")))
    else:
        sys.stdout.write(json.dumps(summary, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")))
    sys.stdout.flush()
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("S001", "C003-fixed-word", "general-v3"))
    parser.add_argument("case")
    parser.add_argument("input")
    parser.add_argument("--memory", action="store_true")
    args = parser.parse_args()
    return run(args.provider, args.case, args.input, args.memory)


if __name__ == "__main__":
    raise SystemExit(main())

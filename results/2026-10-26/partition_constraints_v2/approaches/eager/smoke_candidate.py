"""Archived candidate-only smoke checks; does not modify shared modules."""
from __future__ import annotations

import importlib.util
import itertools
import json
import random
import sys
import time
import types
from pathlib import Path


OWNED = Path(__file__).resolve().parent
ROOT = OWNED.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


common = types.ModuleType("common")
common.__path__ = []
sys.modules["common"] = common
engine = load("common.engine", OWNED / "engine_candidate.py")
helpers = load("common.helpers", OWNED / "common_helpers_candidate.py")
eager = load("candidate_eager", OWNED / "eager_solver.py")


def normalized(result):
    return {tuple(tuple(block) for block in record["blocks"])
            for record in result["feasible_partitions"]}


def direct_full_set(data):
    alphabet, positive, negative = helpers.validate(data)
    result = set()
    for rest in itertools.product((0, 1), repeat=len(alphabet) - 1):
        assignment = (0,) + rest
        if 1 not in assignment:
            continue
        record = helpers.partition_record(alphabet, positive, negative, assignment)
        if record is not None:
            result.add(tuple(tuple(block) for block in record["blocks"]))
    return result


def main():
    summaries = []
    for path in sorted((ROOT / "baseline").glob("theory_*.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        result = eager.solve(data)
        assert result["complete"]
        assert normalized(result) == direct_full_set(data)
        assert normalized(result) == normalized(helpers.load_baseline().solve(data))
        summaries.append({"input": path.name, "status": result["status"],
                          "count": result["feasible_partition_count"]})
    rng = random.Random(20261026)
    alphabet = list("abc")
    words = [""] + list("abc") + ["".join(p) for p in itertools.product("abc", repeat=2)]
    for _ in range(100):
        labels = [rng.randrange(3) for _ in words]
        data = {"alphabet": alphabet,
                "positive": [w for w, label in zip(words, labels) if label == 1],
                "negative": [w for w, label in zip(words, labels) if label == 2]}
        assert normalized(eager.solve(data)) == direct_full_set(data)
    for positive, negative in (([], []), (["ab"], []), ([], ["ab"])):
        data = {"alphabet": alphabet, "positive": positive, "negative": negative}
        result = eager.solve(data)
        assert result["feasible_partition_count"] == 3
    data = {"alphabet": alphabet, "positive": ["ab", "ac", "bc"], "negative": ["abc"]}
    assert eager.solve(data)["status"] == "infeasible"
    interrupted = eager.solve(data, deadline=time.perf_counter() - 1)
    assert interrupted["complete"] is False and interrupted["status"] == "incomplete"
    assert interrupted["feasible_partition_count"] is None
    assert interrupted["found_partition_count"] == 0
    assert engine.eval_expr(("and", ()), [-1]) is True
    assert engine.eval_expr(("or", ()), [-1]) is False
    exprs = [("lit", 1, 0), ("lit", 2, 1),
             ("or", (("lit", 1, 1), ("lit", 2, 0))),
             ("and", (("lit", 0, 0), ("lit", 2, 1)))]
    for expr in exprs:
        actual = set(engine.iter_models(3, [expr]))
        expected = {bits for bits in itertools.product((0, 1), repeat=3)
                    if bits[0] == 0 and 1 in bits and engine.eval_expr(expr, bits)}
        assert actual == expected
        for partial in itertools.product((-1, 0, 1), repeat=3):
            value = engine.eval_expr(expr, partial)
            completions = [bits for bits in itertools.product((0, 1), repeat=3)
                           if all(p == -1 or p == b for p, b in zip(partial, bits))]
            if value is not None:
                assert all(engine.eval_expr(expr, bits) == value for bits in completions)
    for n in words:
        for p in words:
            family = helpers.distinguishers(alphabet, n, p)
            for mask in range(8):
                indices = {i for i in range(3) if mask & (1 << i)}
                block = {alphabet[i] for i in indices}
                direct = helpers.project(n, block) != helpers.project(p, block)
                assert direct == any(set(subset) <= indices for subset in family)
    print(json.dumps({"result": "all_candidate_smoke_checks_passed", "examples": summaries,
                      "seeded_samples": 100, "distinguisher_word_pairs": len(words) ** 2,
                      "distinguisher_blocks_per_pair": 8,
                      "note": "Independent auditor owns broader correctness/performance claims."}, indent=2))


if __name__ == "__main__":
    main()

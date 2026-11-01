"""Captured small independent-oracle checks for solver_v1.py."""
import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c006_solver_v1", ROOT / "solver_v1.py")
solver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(solver)


def canonical(blocks):
    return tuple(sorted(tuple(sorted(x)) for x in blocks))


def oracle(data):
    alpha = sorted(data["alphabet"])
    p, n = sorted(set(data["positive"])), sorted(set(data["negative"]))
    answers = set()
    for mask in range(1, (1 << len(alpha)) - 1):
        if not mask & 1:
            continue
        blocks = [set(a for i, a in enumerate(alpha) if mask >> i & 1),
                  set(a for i, a in enumerate(alpha) if not (mask >> i & 1))]
        langs = [{"".join(c for c in w if c in b) for w in p} for b in blocks]
        if all(any("".join(c for c in w if c in b) not in langs[i]
                   for i, b in enumerate(blocks)) for w in n):
            answers.add(canonical(blocks))
    return answers


CASES = [
    {"name":"manager_unknown_candidate", "data":{"alphabet":list("abcd"),
     "positive":["acdb","cabd","bcda","dabc"], "negative":["abcd"]}},
    {"name":"unconstrained_three_symbols", "data":{"alphabet":list("abc"),
     "positive":["abc"], "negative":[]}},
    {"name":"no_positive_nonempty_negative", "data":{"alphabet":list("abc"),
     "positive":[], "negative":["","a","bc"]}},
    {"name":"epsilon_positive_unused_symbol", "data":{"alphabet":list("abcd"),
     "positive":[""], "negative":["a","bb"]}},
    {"name":"all_positive_labels", "data":{"alphabet":list("ab"),
     "positive":["a","b","ab"], "negative":[]}},
    {"name":"cut_collision_cover", "data":{"alphabet":list("ab"),
     "positive":["a","b"], "negative":["ab"]}},
]

records = []
for case in CASES:
    data = case["data"]
    result = solver.solve(data, max_solutions=None)
    expected = oracle(data)
    actual = {canonical(s["blocks"]) for s in result["solutions"]}
    assert result["complete"] is True, (case["name"], result)
    assert actual == expected, (case["name"], sorted(actual), sorted(expected), result)
    for solution in result["solutions"]:
        assert solver.verify_solution(data, solution)["valid"], case["name"]
    if expected:
        assert result["status"] == "found", (case["name"], result)
    else:
        assert result["status"] == "not_decomposable" and result["certificate"], (case["name"], result)
        assert solver.verify_certificate(data, result["certificate"])["valid"], case["name"]
    records.append({"name":case["name"], "expected_partitions":len(expected),
                    "actual_partitions":len(actual), "status":result["status"],
                    "certificate_kind":(result["certificate"] or {}).get("obstruction"),
                    "result":result})

# The manager's proposed sample is specifically checked with a fresh direct oracle.
limited = solver.solve(CASES[1]["data"], max_solutions=1)
assert limited["status"] == "found" and limited["decision_complete"]
assert limited["complete"] is False and limited["uniqueness"] == "unknown"
expired = solver.solve(CASES[1]["data"], deadline=time.perf_counter()-1)
assert expired["status"] == "incomplete" and not expired["complete"]
invalid = solver.solve({"alphabet":["a","b"], "positive":["a"], "negative":["a"]})
assert invalid["status"] == "invalid_input"
unknown_k = solver.solve({"alphabet":["a","b"], "positive":[], "negative":[], "k":2})
assert unknown_k["status"] == "invalid_input"
singleton = solver.solve({"alphabet":["a"], "positive":[], "negative":[]})
assert singleton["status"] == "not_decomposable"
assert solver.verify_certificate({"alphabet":["a"], "positive":[], "negative":[]},
                                  singleton["certificate"])["valid"]

print(json.dumps({"scientific_status":"passed", "execution_scope":"small_smoke_only",
                  "cases":records, "additional_checks":["max_solutions_truncation",
                  "immediate_deadline", "contradictory_labels", "rejected_input_k",
                  "singleton_alphabet_control"]}, ensure_ascii=False, sort_keys=True))

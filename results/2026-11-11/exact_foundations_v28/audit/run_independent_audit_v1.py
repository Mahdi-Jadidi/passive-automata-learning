"""Compare frozen C028 implementation with the independent set-insertion oracle."""
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from itertools import product
from pathlib import Path

from reference_oracle_v28 import (oracle, exhaustive_binary_cases, seeded_cases,
                                  insert_partitions)
from build_fixtures_v1 import edge_cases, invalid_cases

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "implementation" / "reference.py"
SPEC = HERE.parent / "theory" / "SPEC.md"
PROOFS = HERE.parent / "theory" / "PROOFS.md"
AMEND = HERE.parent / "theory" / "AMENDMENT_1.md"
AMEND2 = HERE.parent / "theory" / "AMENDMENT_2.md"
AMEND2_VERDICT = HERE.parent / "review" / "AMENDMENT_2_VERDICT.md"


def load_solver():
    spec = importlib.util.spec_from_file_location("c028_frozen_reference", SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_witness(w, record, expected_w):
    """Directly replay one candidate witness; independent of its verifier."""
    sigma = record["alphabet"]
    pos = list(dict.fromkeys(tuple(w) for w in record["positive"]))
    neg = list(dict.fromkeys(tuple(w) for w in record["negative"]))
    blocks = w["blocks"]
    assert len(blocks) <= len(w["rgs"])
    assert all(isinstance(b, list) and b for b in blocks) if sigma else blocks == []
    flat = [x for b in blocks for x in b]
    assert len(flat) == len(sigma) and set(flat) == set(sigma)
    assert blocks == [[x for x in sigma if x in set(b)] for b in blocks]
    owners = {x: i for i, b in enumerate(blocks) for x in b}
    labels = {}
    code = []
    for x in sigma:
        old = owners[x]
        if old not in labels:
            labels[old] = len(labels)
        code.append(labels[old])
    assert code == w["rgs"]
    assert len(w["factors"]) == len(blocks)
    langs = [set(tuple(x) for x in f) for f in w["factors"]]
    def proj(word, block):
        bs = set(block)
        return tuple(x for x in word if x in bs)
    for j, b in enumerate(blocks):
        assert langs[j] == {proj(p, b) for p in pos}
        expected_factor = []
        seen = set()
        for p in pos:
            value = proj(p, b)
            if value not in seen:
                seen.add(value)
                expected_factor.append(list(value))
        assert w["factors"][j] == expected_factor
    assert len(w["negative_rejected_by"]) == len(neg), (w, record)
    expected_rejectors = []
    for n in neg:
        expected_rejectors.append(next(j for j, b in enumerate(blocks)
                                       if proj(n, b) not in langs[j]))
    assert w["negative_rejected_by"] == expected_rejectors
    for n, j in zip(neg, w["negative_rejected_by"]):
        assert type(j) is int and 0 <= j < len(blocks)
        assert proj(n, blocks[j]) not in langs[j]
    if expected_w is not None:
        assert tuple(w["rgs"]) == tuple(expected_w["rgs"])


def compare_one(solver, record):
    expected = oracle(record)
    got = solver.solve(record)
    for key in ("status", "compatible_count", "optimal_count", "max_blocks",
                "recommendation", "optimal_unique"):
        if got.get(key) != expected.get(key):
            # recommendation includes witness details, while oracle returns only
            # the canonical RGS. Compare that field separately below.
            if key == "recommendation" and isinstance(got.get(key), dict):
                if got[key].get("rgs") == expected.get(key):
                    continue
            raise AssertionError((key, got.get(key), expected.get(key), record))
    if expected["compatible_count"] == 0:
        assert got["compatible_witnesses"] == [] and got["optimal_witnesses"] == []
        return got
    assert got["recommendation"]["rgs"] == expected["recommendation"]
    assert got["recommendation"] == got["optimal_witnesses"][0]
    check_witness(got["recommendation"], record, expected["optimal"][0])
    for list_key, expected_key in (("compatible_witnesses", "compatible"),
                                   ("optimal_witnesses", "optimal")):
        got_list = got[list_key]
        exp_list = expected[expected_key]
        assert len(got_list) == min(2, expected["compatible_count"] if expected_key == "compatible" else expected["optimal_count"])
        assert [tuple(x["rgs"]) for x in got_list] == [tuple(x["rgs"]) for x in exp_list]
        for w, ew in zip(got_list, exp_list):
            check_witness(w, record, ew)
            assert len(w["blocks"]) == len(ew["blocks"])
            assert [set(b) for b in w["blocks"]] == [set(b) for b in ew["blocks"]]
    return got


def transformed(record, mapping):
    return {"alphabet": [mapping[x] for x in record["alphabet"]],
            "positive": [[mapping[x] for x in w] for w in record["positive"]],
            "negative": [[mapping[x] for x in w] for w in record["negative"]]}


def dfa_labels(alphabet, partition, dfa_specs, max_length=3):
    """Generate finite sample from explicitly specified independent DFA factors."""
    words = [w for k in range(max_length + 1) for w in product(alphabet, repeat=k)]
    positive, negative = [], []
    for word in words:
        accepted = True
        for block, (start, finals, transitions) in zip(partition, dfa_specs):
            q = start
            for symbol in word:
                if symbol in block:
                    q = transitions[q][symbol]
            if q not in finals:
                accepted = False
                break
        (positive if accepted else negative).append(list(word))
    return {"alphabet": list(alphabet), "positive": positive, "negative": negative}


def dfa_controls(solver):
    # The target automata below are audit-only metadata and are never passed to
    # the learner. Factors have mixed state counts; checks test fit, not recovery.
    a, b, c = "a", "b", "c"
    cases = [
        ([a, b, c], [{a}, {b, c}],
         [(0, {0}, {0: {a: 1, b: 0, c: 0}, 1: {a: 0, b: 1, c: 1}}),
          (0, {2}, {0: {a: 0, b: 1, c: 0}, 1: {a: 1, b: 2, c: 1}, 2: {a: 2, b: 2, c: 2}})]),
        ([a, b, c], [{a, b}, {c}],
         [(0, {0}, {0: {a: 1, b: 0, c: 0}, 1: {a: 0, b: 1, c: 1}}),
          (0, {0, 1}, {0: {a: 0, b: 0, c: 1}, 1: {a: 1, b: 1, c: 0}})]),
        ([a, b, c], [{a}, {b}, {c}],
         [(0, {0}, {0: {a: 1, b: 0, c: 0}, 1: {a: 0, b: 1, c: 1}}),
          (0, {0}, {0: {a: 0, b: 1, c: 0}, 1: {a: 1, b: 0, c: 1}}),
          (0, {0}, {0: {a: 0, b: 0, c: 1}, 1: {a: 1, b: 1, c: 0}})]),
    ]
    for alphabet, part, specs in cases:
        record = dfa_labels(alphabet, part, specs)
        # Assert the generating partition fits the observed labels. The oracle
        # and solver receive only record; no target metadata enters solve().
        from reference_oracle_v28 import inspect_partition
        assert inspect_partition(alphabet, [tuple(w) for w in record["positive"]],
                                 [tuple(w) for w in record["negative"]],
                                 tuple(frozenset(b) for b in part)) is not None
        compare_one(solver, record)
    return {"status": "passed", "withheld_target_cases": len(cases),
            "input_word_max_length": 3, "physical_recovery_asserted": False}


def controls(solver):
    # Validation/error classes and normalization invariances.
    invalids = invalid_cases()
    for x in invalids:
        bad = solver.solve(x)
        assert bad["status"] == "INVALID_INPUT"
        assert all(bad[k] is None for k in ("compatible_count", "optimal_count", "max_blocks",
                                            "recommendation", "optimal_unique", "compatible_witnesses",
                                            "optimal_witnesses"))
    base = {"alphabet": ["a", "bc", "ab", "c"],
            "positive": [["a", "bc"]], "negative": [["ab", "c"]]}
    base_out = solver.solve(base)
    assert base_out["status"] != "INCOMPATIBLE"
    renamed = transformed(base, {"a":"A:one", "bc":"B two", "ab":"☃", "c":"ε"})
    renamed_out = solver.solve(renamed)
    assert (base_out["compatible_count"], base_out["optimal_count"], base_out["max_blocks"],
            base_out["recommendation"]["rgs"]) == (renamed_out["compatible_count"],
            renamed_out["optimal_count"], renamed_out["max_blocks"], renamed_out["recommendation"]["rgs"])
    reordered = {"alphabet": base["alphabet"], "positive": list(reversed(base["positive"])),
                 "negative": list(reversed(base["negative"]))}
    order_out = solver.solve(reordered)
    assert (base_out["compatible_count"], base_out["optimal_count"], base_out["max_blocks"],
            base_out["recommendation"]["rgs"]) == (order_out["compatible_count"],
            order_out["optimal_count"], order_out["max_blocks"], order_out["recommendation"]["rgs"])
    dup = {"alphabet": ["a", "b"], "positive": [[], [], ["a"], ["a"]],
           "negative": [["b"], ["b"]]}
    dedup = {"alphabet": ["a", "b"], "positive": [[], ["a"]], "negative": [["b"]]}
    a, b = solver.solve(dup), solver.solve(dedup)
    assert all(a[k] == b[k] for k in ("status", "compatible_count", "optimal_count", "max_blocks", "recommendation"))
    # The budget is an optional implementation control; no partial count/status.
    partial = solver.solve({"alphabet": ["a", "b", "c"], "positive": [], "negative": []}, max_candidates=1)
    assert partial["status"] == "INCOMPLETE"
    assert all(partial[k] is None for k in ("compatible_count", "optimal_count", "max_blocks", "recommendation", "optimal_unique", "compatible_witnesses", "optimal_witnesses"))
    exact = solver.solve({"alphabet": ["a", "b", "c"], "positive": [], "negative": []}, max_candidates=5)
    assert exact["status"] == "AMBIGUOUS" and exact["compatible_count"] == 5
    return {"status":"passed", "invalid_cases":len(invalids), "rename_and_order":"passed", "dedup":"passed"}


def main():
    solver = load_solver()
    results = {"source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "spec_sha256": hashlib.sha256(SPEC.read_bytes()).hexdigest(),
               "proofs_sha256": hashlib.sha256(PROOFS.read_bytes()).hexdigest(),
               "amendment_sha256": hashlib.sha256(AMEND.read_bytes()).hexdigest(),
               "amendment2_sha256": hashlib.sha256(AMEND2.read_bytes()).hexdigest(),
               "amendment2_verdict_sha256": hashlib.sha256(AMEND2_VERDICT.read_bytes()).hexdigest(),
               "python": sys.version, "platform": platform.platform(),
               "exhaustive_cases": 0, "seeded_cases": 0, "edge_cases": 0,
               "failures": []}
    t0 = time.perf_counter()
    for record in exhaustive_binary_cases():
        compare_one(solver, record)
        results["exhaustive_cases"] += 1
    for record in seeded_cases():
        compare_one(solver, record)
        results["seeded_cases"] += 1
    for record in edge_cases():
        if not any(not isinstance(x, str) or not x for x in record["alphabet"]):
            compare_one(solver, record)
            results["edge_cases"] += 1
        else:
            assert solver.solve(record)["status"] == "INVALID_INPUT"
            results["edge_cases"] += 1
    results["invalid_schema_cases"] = len(invalids := invalid_cases())
    results["controls"] = controls(solver)
    # Explicit arbitrary alphabet-size budget control: iterative candidate
    # generation must not recurse once per symbol before returning INCOMPLETE.
    huge_alphabet = [f"opaque-{i}" for i in range(1200)]
    huge = solver.solve({"alphabet": huge_alphabet, "positive": [], "negative": []}, max_candidates=1)
    assert huge["status"] == "INCOMPLETE" and all(huge[k] is None for k in
            ("compatible_count", "optimal_count", "max_blocks", "recommendation", "optimal_unique",
             "compatible_witnesses", "optimal_witnesses"))
    results["large_alphabet_budget_control"] = "passed (1200 IDs, one candidate budget)"
    results["dfa_controls"] = dfa_controls(solver)
    # Prefix extension: the maximum does not increase, while the canonical
    # optimum can switch between incomparable cuts.
    old = {"alphabet": ["a", "b", "c"], "positive": [[], ["a", "b", "c"]],
           "negative": [["a"]]}
    extended = {**old, "negative": [["a"], ["c"]]}
    o, e = solver.solve(old), solver.solve(extended)
    assert o["max_blocks"] == e["max_blocks"] == 2
    assert o["recommendation"]["rgs"] != e["recommendation"]["rgs"]
    results["sample_extension"] = {"old_max": o["max_blocks"], "extended_max": e["max_blocks"],
                                   "old_rgs": o["recommendation"]["rgs"],
                                   "extended_rgs": e["recommendation"]["rgs"]}
    results["elapsed_seconds"] = time.perf_counter() - t0
    results["status"] = "passed"
    dest = HERE / "INDEPENDENT_AUDIT_RESULTS_V2.json"
    dest.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

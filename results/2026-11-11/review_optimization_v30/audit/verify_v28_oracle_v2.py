"""Independent oracle/source cross-check; candidate mode enabled only by GO."""
import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
RESULTS = WORKSPACE / "results" / "2026-11-11"
V28 = RESULTS / "exact_foundations_v28"
sys.path.insert(0, str(HERE))
import reference_oracle_v28 as oracle_mod


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def oracle_to_source(data):
    sigma, positives, negatives = oracle_mod.normalize(data)
    raw = oracle_mod.oracle(data)

    def convert(w):
        blocks = w["blocks"]
        # Match C028's first-occurrence positive projection order, while retaining
        # the independent oracle's own partition and rejecting-block choice.
        factors = []
        for block in blocks:
            seen, local = set(), []
            for p in positives:
                projected = oracle_mod.projection(p, set(block))
                if projected not in seen:
                    seen.add(projected)
                    local.append(list(projected))
            factors.append(local)
        rejecting = w["rejecting_block_by_negative"]
        return {"rgs": w["rgs"], "blocks": blocks, "factors": factors,
                "negative_rejected_by": rejecting}

    if raw["max_blocks"] is None:
        return {"status": "INCOMPATIBLE", "compatible_count": 0,
                "optimal_count": 0, "max_blocks": None, "recommendation": None,
                "optimal_unique": None, "compatible_witnesses": [], "optimal_witnesses": []}
    compatible = [convert(w) for w in raw["compatible"]]
    optimal = [convert(w) for w in raw["optimal"]]
    return {"status": raw["status"], "compatible_count": raw["compatible_count"],
            "optimal_count": raw["optimal_count"], "max_blocks": raw["max_blocks"],
            "recommendation": optimal[0], "optimal_unique": raw["optimal_unique"],
            "compatible_witnesses": compatible, "optimal_witnesses": optimal}


def check_replay(data, result):
    sigma, positives, negatives = oracle_mod.normalize(data)
    for family in (result["compatible_witnesses"], result["optimal_witnesses"]):
        for w in family:
            assert tuple(w["rgs"]) == tuple(oracle_mod.canonical_rgs(
                tuple(frozenset(b) for b in w["blocks"]), sigma))
            flat = [x for block in w["blocks"] for x in block]
            assert len(flat) == len(sigma) and set(flat) == set(sigma)
            assert all(w["blocks"]) if sigma else w["blocks"] == []
            for i, block in enumerate(w["blocks"]):
                seen = []
                for p in positives:
                    projected = list(oracle_mod.projection(p, set(block)))
                    if projected not in seen:
                        seen.append(projected)
                assert w["factors"][i] == seen
            assert len(w["negative_rejected_by"]) == len(negatives)
            for n, bi in zip(negatives, w["negative_rejected_by"]):
                assert 0 <= bi < len(w["blocks"])
                projected = oracle_mod.projection(n, set(w["blocks"][bi]))
                assert projected not in {oracle_mod.projection(p, set(w["blocks"][bi])) for p in positives}
                assert all(oracle_mod.projection(n, set(w["blocks"][j])) in
                           {oracle_mod.projection(p, set(w["blocks"][j])) for p in positives}
                           for j in range(bi))


def cases():
    yield from (x for _, x in ((row["case"], row["input"]) for row in
                              map(json.loads, (HERE / "fixed_cases.jsonl").read_text(encoding="utf-8").splitlines())))
    yield from oracle_mod.exhaustive_binary_cases()
    yield from oracle_mod.seeded_cases()


def budget_cases():
    singleton = {"alphabet": ["a", "b", "c", "d"], "positive": [], "negative": []}
    bell4 = 15
    yield "singleton_budget_0", singleton, 0
    yield "singleton_budget_1", singleton, 1
    yield "singleton_budget_bell_minus_1", singleton, bell4 - 1
    yield "singleton_budget_bell", singleton, bell4
    yield "empty_alphabet_budget_0", {"alphabet": [], "positive": [], "negative": []}, 0
    yield "singleton_budget_0_m1", {"alphabet": ["a"], "positive": [], "negative": []}, 0
    yield "singleton_budget_1_m1", {"alphabet": ["a"], "positive": [], "negative": []}, 1
    yield "contradiction_budget_0", {"alphabet": ["a"], "positive": [["a"]],
                                      "negative": [["a"]]}, 0


def invalid_cases():
    good = {"alphabet": ["a"], "positive": [], "negative": []}
    yield "extra_schema_key", {**good, "ignored": 0}, None
    yield "missing_schema_key", {"alphabet": ["a"], "positive": []}, None
    yield "empty_id", {"alphabet": [""], "positive": [], "negative": []}, None
    yield "duplicate_id", {"alphabet": ["a", "a"], "positive": [], "negative": []}, None
    yield "unknown_word_id", {"alphabet": ["a"], "positive": [["b"]], "negative": []}, None
    yield "word_not_array", {"alphabet": ["a"], "positive": ["a"], "negative": []}, None
    yield "invalid_budget_negative", good, -1
    yield "invalid_budget_bool", good, True
    yield "invalid_budget_float", good, 1.0


def lru_and_early_failure_checks(candidate):
    from collections import OrderedDict
    original_od = candidate.OrderedDict

    class TrackingLRU(OrderedDict):
        evictions = 0
        evicted_keys = set()
        reinsertions = 0
        def popitem(self, *args, **kwargs):
            type(self).evictions += 1
            pair = super().popitem(*args, **kwargs)
            type(self).evicted_keys.add(pair[0])
            return pair
        def __setitem__(self, key, value):
            if key in type(self).evicted_keys:
                type(self).reinsertions += 1
                type(self).evicted_keys.remove(key)
            return super().__setitem__(key, value)

    proj = candidate._projection
    candidate.OrderedDict = TrackingLRU
    try:
        # 9 IDs have 511 nonempty subsets; full enumeration must cross 256 keys.
        evict_data = {"alphabet": [f"e{i}" for i in range(9)], "positive": [], "negative": []}
        observed = candidate.solve_b(evict_data)
        expected = oracle_to_source(evict_data)
        assert observed == expected
        assert TrackingLRU.evictions > 0
        evictions = TrackingLRU.evictions
        reinsertions = TrackingLRU.reinsertions
        assert reinsertions > 0

        # Sequential invocations must not carry local rejection vectors forward.
        pair = [
            {"alphabet": ["a", "b"], "positive": [["a"]], "negative": [["b"]]},
            {"alphabet": ["a", "b"], "positive": [["b"]], "negative": [["a"]]},
        ]
        for record in pair:
            assert candidate.solve_b(record) == oracle_to_source(record)

        # An early rejecting negative makes the baseline stop before later negatives;
        # B is required by its proposal to materialize the whole vector on a miss.
        alpha, pos, neg = candidate._normalize({"alphabet": ["a", "b"],
            "positive": [["a"], ["b"]],
            "negative": [["a", "b"], ["b", "b"], ["a", "b", "b"]]})
        # One two-symbol negative is locally present in both singleton factors,
        # but is distinct as a whole word from either positive (no contradiction).
        rgs = (0, 1)
        calls = {"baseline": 0, "memo": 0}
        def counted(which):
            def f(word, symbols):
                calls[which] += 1
                return proj(word, symbols)
            return f
        candidate._projection = counted("baseline")
        assert candidate._candidate(alpha, pos, neg, rgs) is None
        baseline_calls = calls["baseline"]
        candidate._projection = counted("memo")
        assert candidate._cached_candidate(alpha, pos, neg, rgs, OrderedDict()) is False
        memo_calls = calls["memo"]
        assert memo_calls > baseline_calls
        return {"lru_evictions_observed": evictions,
                "lru_reinsertions_after_eviction": reinsertions,
                "early_failure_projection_calls_baseline": baseline_calls,
                "early_failure_projection_calls_memo": memo_calls}
    finally:
        candidate.OrderedDict = original_od
        candidate._projection = proj


def checker_mutation_sanity():
    data = {"alphabet": ["a", "b", "c"], "positive": [[], ["a", "b", "c"]],
            "negative": [["a"]]}
    good = oracle_to_source(data)
    mutations = []
    for field in ("compatible_count", "optimal_count"):
        bad = copy.deepcopy(good)
        bad[field] += 1
        mutations.append(bad)
    if len(good["compatible_witnesses"]) > 1:
        bad = copy.deepcopy(good)
        bad["compatible_witnesses"].reverse()
        mutations.append(bad)
    bad = copy.deepcopy(good)
    bad["compatible_witnesses"][0]["rgs"][0] += 1
    mutations.append(bad)
    bad = copy.deepcopy(good)
    bad["compatible_witnesses"][0]["negative_rejected_by"][0] = 1
    mutations.append(bad)
    collision = {"alphabet": ["a", "bc", "ab", "c"],
                 "positive": [["a", "bc"]], "negative": [["ab", "c"]]}
    collision_expected = oracle_to_source(collision)
    assert collision_expected["status"] != "INCOMPATIBLE"
    assert len(mutations) == 5 and all(bad != good for bad in mutations)
    return {"synthetic_mutations_rejected_by_exact_comparison": len(mutations),
            "raw_join_collision_distinguished": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="manager GO required before candidate calls")
    args = ap.parse_args()
    # Always self-test the independently implemented partition generator.
    oracle_selftest = oracle_mod.selftest()
    mutation_selftest = checker_mutation_sanity()
    baseline = load(V28 / "implementation" / "reference.py", "v28baseline")
    n = 0
    for data in cases():
        expected = oracle_to_source(data)
        actual = baseline.solve(data)
        if actual != expected:
            raise AssertionError({"case": n, "input": data, "expected": expected, "actual": actual})
        check_replay(data, actual)
        n += 1
    result = {"status": "PASS", "oracle_selftest": oracle_selftest,
              "checker_mutation_selftest": mutation_selftest,
              "baseline_oracle_cases": n, "candidate_calls": 0}
    if args.go:
        candidate_path = RESULTS / "review_optimization_v30" / "optimization" / "candidate_v1.py"
        candidate = load(candidate_path, "c030candidate")
        for name in ("solve_a", "solve_b", "solve_combined"):
            checked = 0
            for data in cases():
                expected = oracle_to_source(data)
                actual = getattr(candidate, name)(data)
                if actual != expected:
                    raise AssertionError({"variant": name, "case": checked,
                                          "input": data, "expected": expected, "actual": actual})
                check_replay(data, actual)
                checked += 1
            result[name + "_cases"] = checked
            budget_checked = 0
            for case_name, data, budget in budget_cases():
                expected = baseline.solve(data, max_candidates=budget)
                actual = getattr(candidate, name)(data, max_candidates=budget)
                if actual != expected:
                    raise AssertionError({"variant": name, "budget_case": case_name,
                                          "budget": budget, "expected": expected, "actual": actual})
                budget_checked += 1
            result[name + "_budget_cases"] = budget_checked
            invalid_checked = 0
            for case_name, data, budget in invalid_cases():
                expected = baseline.solve(data, max_candidates=budget)
                actual = getattr(candidate, name)(data, max_candidates=budget)
                if actual != expected:
                    raise AssertionError({"variant": name, "invalid_case": case_name,
                                          "budget": budget, "expected": expected, "actual": actual})
                if expected["status"] == "INVALID_INPUT":
                    assert all(expected[key] is None for key in
                               ("compatible_count", "optimal_count", "max_blocks", "recommendation",
                                "optimal_unique", "compatible_witnesses", "optimal_witnesses"))
                invalid_checked += 1
            result[name + "_invalid_cases"] = invalid_checked
        result["candidate_B_internal_regressions"] = lru_and_early_failure_checks(candidate)
        result["candidate_variants"] = 3
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

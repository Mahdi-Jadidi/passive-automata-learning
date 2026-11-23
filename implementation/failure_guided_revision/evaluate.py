"""Reproduce correctness checks and matched synthetic benchmarks."""

import argparse
from collections import Counter
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
from random import Random
from statistics import median
from time import perf_counter

from search import ProjectionMatches, solve
from verify import verify


METHODS = (("baseline", "canonical"), ("first", "canonical"),
           ("maximal", "canonical"), ("maximal", "gain"))


HISTORICAL_METHODS = {
    "no_analysis_all_pairs": dict(preprocess=False, shortcuts=False, mode="baseline"),
    "fixed_point_all_pairs": dict(shortcuts=False, mode="baseline"),
    "fixed_point_guided": dict(shortcuts=False, mode="maximal"),
    "full_analysis": dict(mode="maximal"),
}
RESIDUAL_METHODS = {
    "all_pairs": dict(mode="baseline", exact_root=True),
    "first_failure": dict(mode="maximal", exact_root=True),
    "best_three": dict(mode="maximal", exact_root=True, policy="best-three"),
}

def sample(alphabet, positive, negative):
    return {"alphabet": list(alphabet), "positive": [list(x) for x in positive],
            "negative": [list(y) for y in negative]}


def partitions(alphabet):
    if not alphabet:
        yield []
        return
    a, *remaining = alphabet
    for partition in partitions(remaining):
        yield [{a}, *partition]
        for i, block in enumerate(partition):
            yield partition[:i] + [block | {a}] + partition[i + 1:]


def exhaustive_optimum(D):
    def projection(word, block):
        return tuple(filter(block.__contains__, word))

    def compatible(partition):
        return all(any(all(projection(x, block) != projection(y, block)
                           for x in D["positive"]) for block in partition)
                   for y in D["negative"])

    return max((len(p) for p in partitions(D["alphabet"]) if compatible(p)), default=None)


def group_sample(groups):
    alphabet = "".join(groups)
    positive = [""]
    for group in groups:
        positive.extend(group[:i] + group[i + 1:] for i in range(len(group)))
    return sample(alphabet, positive, groups)


def random_sample(rng, n):
    alphabet = "abcdef"[:n]
    words = sorted({"".join(rng.choices(alphabet, k=rng.randrange(9))) for _ in range(22)})
    rng.shuffle(words)
    cut = rng.randrange(len(words) + 1)
    return sample(alphabet, words[:cut], words[cut:])


def correctness():
    cases = [
        ("example", sample("abc", ["ac", "bc"], ["abc"]), 2),
        ("tied", sample("abc", ["ab", "ac", "bc"], [""]), 2),
        ("greedy_counterexample", sample("abcd", ["", "ab", "cd"], ["ac", "dc"]), 3),
        ("multiple_merges", group_sample(["abc"]), 1),
        ("empty_alphabet", sample("", [""], []), 0),
        ("empty_alphabet_negative", sample("", [], [""]), None),
        ("empty_sample", sample("abc", [], []), 3),
        ("unused_symbol", sample("abcd", ["ac", "bc"], ["abc"]), 3),
        ("duplicates", sample("abc", ["ac", "ac", "bc"], ["abc", "abc"]), 2),
        ("opposite_labels", sample("ab", ["a"], ["a"]), None),
        ("order_matters", sample("ab", ["ab"], ["ba"]), 1),
        ("multi_character_symbols", sample(["open", "close"], [["open", "close"]],
                                           [["close", "open"]]), 1),
    ]
    for n in range(3):
        alphabet = "ab"[:n]
        words = [w for size in range(3) for w in product(alphabet, repeat=size)]
        for labels in product(range(3), repeat=len(words)):
            D = sample(alphabet, [w for w, label in zip(words, labels) if label == 1],
                       [w for w, label in zip(words, labels) if label == 2])
            cases.append(("exhaustive", D, exhaustive_optimum(D)))
    rng = Random(22112026)
    for i in range(300):
        D = random_sample(rng, i % 4 + 3)
        cases.append(("seeded", D, exhaustive_optimum(D)))

    for name, D, k in cases:
        assert exhaustive_optimum(D) == k, name
        for mode, order in METHODS:
            for enabled in (False, True):
                result = solve(D, mode=mode, order=order, preprocess=enabled)
                assert result["status"] == ("INFEASIBLE" if k is None else "OPTIMAL"), (name, result)
                assert result.get("max_devices") == k, (name, mode, order, result)
                wire_result = json.loads(json.dumps(result))
                assert verify(D, wire_result)["status"] == "VERIFIED", (name, mode, order)

    D = group_sample(["abc"])
    result = solve(D, preprocess=False, shortcuts=False)
    missing = deepcopy(result)
    del missing["certificate"]["rejections"][1]
    assert verify(D, missing)["status"] == "INVALID"
    wrong = deepcopy(result)
    wrong["certificate"]["rejections"][0]["positive"][0] = 0
    assert verify(D, wrong)["status"] == "INVALID"
    assert solve(D, seconds=0)["status"] == "INCOMPLETE"
    assert verify(D, result, seconds=0)["status"] == "INCOMPLETE"
    targeted_checks()
    return {"samples": len(cases), "method_comparisons_and_replays": len(cases) * len(METHODS) * 2,
            "targeted_checks": "passed",
            "negative_proof_checks": 2, "deadline_checks": 2}


def targeted_checks():
    D = sample("abc", ["abc"], ["bac", "acb"])
    result = solve(D)
    assert result["blocks"] == [["a", "b", "c"]]
    assert len(result["certificate"]["contractions"][0]["deleted"]) >= 2
    assert verify(D, result)["status"] == "VERIFIED"
    tampered = deepcopy(result)
    tampered["certificate"]["contractions"][0]["deleted"][0]["positive"] = 99
    assert verify(D, tampered)["status"] == "INVALID"

    multi = sample("abc", ["a", "b", "ac"], ["", "bc"])
    result = solve(multi)
    assert result["max_devices"] == 1
    assert len(result["certificate"]["contractions"]) == 2
    assert verify(multi, result)["status"] == "VERIFIED"
    del result["certificate"]["contractions"][0]
    assert verify(multi, result)["status"] == "INVALID"

    single = sample("abcdefxy", ["ab", "cd", "ef"], [""])
    result = solve(single)
    assert result["max_devices"] == 6 and result["certificate"]["unused"] == [6, 7]
    assert verify(single, result)["status"] == "VERIFIED"
    bad = deepcopy(result)
    kept = next(b for b in bad["blocks"] if len(b) > 1)
    extra = next(b for b in bad["blocks"] if len(b) == 1 and b[0] not in "xy")
    kept.extend(extra)
    bad["blocks"].remove(extra)
    bad["max_devices"] -= 1
    bad["certificate"]["separating"] += (single["alphabet"].index(extra[0]),)
    assert verify(single, bad)["status"] == "INVALID"
    for traces in (([], [""]), ([""], []), ([], [])):
        empty = sample("abcd", *traces)
        result = solve(empty)
        assert result["max_devices"] == 4 and verify(empty, result)["status"] == "VERIFIED"

    pair_words = ["ab", "cd", "ef", "gh", "ij"]
    for extra in ("", "xy"):
        stress = sample("abcdefghij" + extra, pair_words, [""])
        result = solve(stress)
        assert result["max_devices"] == 6 + len(extra)
        assert result["stats"]["subsets_tested"] == 462
        assert verify(stress, result)["status"] == "VERIFIED"

    order_case = sample("abcd", ["ac", "cd", "b", "ad"], ["bd", "ba"])
    def counters(result):
        return tuple(result["stats"][k] for k in ("generated", "tested"))
    reversed_case = {**order_case, "negative": order_case["negative"][::-1]}
    orders = [solve(D, mode="maximal", policy="best-three") for D in (order_case, reversed_case)]
    assert counters(orders[0]) == counters(orders[1])
    assert all(result["max_devices"] == 2 for result in orders)

    baseline_orders = [solve(D, mode="maximal") for D in (order_case, reversed_case)]
    assert [r["stats"]["tested"] for r in baseline_orders] == [6, 9]
    assert [r["stats"]["tested"] for r in orders] == [7, 7]

    words = ((1, 0, 2), (0, 2, 1))
    matches = ProjectionMatches(((0, 1, 2),), words, lambda: None)
    assert [matches.row((a,)) for a in range(3)] == [(0, 0)] * 3
    assert matches.row((0, 1)) == (None, 0)
    assert matches.row((1, 2)) == (0, None)

    D = sample("abcd", ["", "ab", "cd"], ["ac", "dc"])
    result = solve(D)
    assert result["blocks"] == [["a"], ["b"], ["c", "d"]]
    assert len(result["certificate"]["contractions"]) == 1

    D = sample("abc", ["ac", "bc"], ["abc"])
    def one_block(blocks):
        return len(blocks) == 1
    result = solve(D, admissible=one_block)
    assert result["max_devices"] == 1
    assert verify(D, result, admissible=one_block)["status"] == "VERIFIED"
    assert verify(D, result)["status"] == "INVALID"

    def no_member(blocks):
        return False
    result = solve(D, admissible=no_member)
    assert result["status"] == "INFEASIBLE"
    assert verify(D, result, admissible=no_member)["status"] == "VERIFIED"
    tampered = deepcopy(result)
    tampered["certificate"]["rejections"].pop()
    assert verify(D, tampered, admissible=no_member)["status"] == "INVALID"

    D = sample("abc", ["bc", "bac"], ["aabc", "acb"])
    seen = []
    def bounded_example(blocks, tick):
        tick()
        seen.append(blocks)
        return "PASS" if blocks == (("a", "b"), ("c",)) else "FAIL"
    result = solve(D, check_bounds=bounded_example)
    assert seen == [(("a",), ("b", "c")), (("a", "b"), ("c",))]
    assert result["blocks"] == [["a", "b"], ["c"]]
    assert verify(D, result, check_bounds=bounded_example)["status"] == "VERIFIED_CONDITIONAL"
    assert verify(D, result)["status"] == "INVALID"

    def only_full_has_capacity(blocks, tick):
        tick()
        return "PASS" if len(blocks) == 1 else "FAIL"
    bounded = solve(D, check_bounds=only_full_has_capacity)
    assert bounded["max_devices"] == 1
    assert any(r["reason"] == "bounds" for r in bounded["certificate"]["rejections"])
    seen_replay = []
    def replay_bounds(blocks, tick):
        seen_replay.append(blocks)
        return only_full_has_capacity(blocks, tick)
    assert verify(D, bounded, check_bounds=replay_bounds)["status"] == "VERIFIED_CONDITIONAL"
    assert any(len(blocks) == 2 for blocks in seen_replay)

    def interrupted(blocks, tick):
        return "INCOMPLETE"
    assert solve(D, check_bounds=interrupted)["status"] == "INCOMPLETE"
    assert verify(D, result, check_bounds=interrupted)["status"] == "INCOMPLETE"


def compatible(D, partition):
    def project(w, B):
        return tuple(a for a in w if a in B)
    return all(any(all(project(y, B) != project(x, B) for x in D["positive"])
                   for B in partition) for y in D["negative"])


def exact_reference(D):
    alphabet = D["alphabet"]
    feasible = [P for P in partitions(alphabet) if compatible(D, P)]
    remaining = set(alphabet)
    meet = []
    while remaining:
        a = min(remaining)
        block = {b for b in remaining if all(any({a, b} <= B for B in P) for P in feasible)}
        meet.append(block)
        remaining -= block
    return meet, max(map(len, feasible))


def freeze_residual_inputs():
    rng = Random(22112027)
    cases = {"joint_obligations": sample("abcd", ["a", "bc", "bd"], ["", "ac"]),
             "negative_order": sample("abcd", ["ac", "cd", "b", "ad"], ["bd", "ba"])}
    for n in (5, 6, 7, 8):
        alphabet = "abcdefgh"[:n]
        kept = 0
        for _ in range(250):
            words = sorted({"".join(rng.choices(alphabet, k=rng.randrange(5))) for _ in range(16)})
            rng.shuffle(words)
            D = sample(alphabet, words[:5], words[5:9])
            if len(D["negative"]) < 2:
                continue
            if set().union(*(set(w) for w in D["positive"] + D["negative"])) != set(alphabet):
                continue
            meet, _ = exact_reference(D)
            if not compatible(D, meet):
                kept += 1
                cases[f"residual_{n}_{kept}"] = D
                if kept == 2:
                    break
        assert kept == 2, n
    return cases


def benchmark_trial(name, D, method, options, repetition, seconds):
    t0 = perf_counter()
    result = solve(D, seconds=seconds, **options)
    t1 = perf_counter()
    record = dict(case=name, method=method, repetition=repetition, outcome=result["status"],
                  search_seconds=t1 - t0 - result["stats"]["analysis_seconds"], **result["stats"])
    if result["status"] == "INCOMPLETE":
        return dict(record, stopped_at="solve", total_seconds=t1 - t0)
    wire = json.dumps(result, separators=(",", ":"))
    certificate_bytes = len(json.dumps(result["certificate"], separators=(",", ":")).encode())
    decoded = json.loads(wire)
    t2 = perf_counter()
    verdict = verify(D, decoded, seconds=max(0, seconds - (t2 - t0)))
    end = perf_counter()
    assert verdict["status"] != "INVALID", verdict
    return dict(record, outcome=verdict["status"], max_devices=result.get("max_devices"),
                stopped_at=None if verdict["status"] == "VERIFIED" else
                ("serialization" if t2 - t0 >= seconds else "replay"),
                serialization_seconds=t2 - t1, replay_seconds=end - t2,
                certificate_bytes=certificate_bytes, total_seconds=end - t0)


def benchmark(seconds, repeats):
    fixtures = json.loads(Path(__file__).with_name("fixtures.json").read_text())
    records = []
    roots = {}
    for cohort, methods in (("historical", HISTORICAL_METHODS), ("residual", RESIDUAL_METHODS)):
        for name, D in fixtures[cohort].items():
            expected = None
            cheap = solve(D)
            if cohort == "residual":
                meet, expected = exact_reference(D)
                assert not compatible(D, meet)
                roots[name] = dict(cheap_root=cheap["stats"]["root_blocks"],
                                   exact_root=len(meet), optimum=expected)
            else:
                expected = cheap["max_devices"]
                roots[name] = dict(cheap_root=cheap["stats"]["root_blocks"], optimum=expected)
            names = list(methods)
            for repetition in range(repeats):
                offset = repetition % len(names)
                for method in names[offset:] + names[:offset]:
                    record = benchmark_trial(name, D, method, methods[method], repetition, seconds)
                    records.append(dict(record, cohort=cohort))
                    if record["outcome"] == "VERIFIED":
                        assert record["max_devices"] == expected, (name, record)
                        if cohort == "residual":
                            assert record["root_blocks"] == roots[name]["exact_root"]
    return roots, records


def summarize(records):
    summary = []
    for case, method in dict.fromkeys((r["case"], r["method"]) for r in records):
        trials = [r for r in records if r["case"] == case and r["method"] == method]
        completed = [r for r in trials if r["outcome"] == "VERIFIED"]
        metrics = ("generated", "tested", "subsets_tested", "analysis_seconds",
                   "region_seconds", "search_seconds", "serialization_seconds",
                   "total_seconds", "certificate_bytes", "replay_seconds")
        summary.append(dict(case=case, method=method,
                            outcomes=dict(Counter(r["outcome"] for r in trials)),
                            medians={k: median(r[k] for r in completed) for k in metrics}
                            if completed else {}))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=0.5)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    checks = correctness()
    roots, records = benchmark(args.seconds, args.repeats)
    report = dict(checks=checks, seconds=args.seconds, repeats=args.repeats,
                  roots=roots, trials=records, summary=summarize(records))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    main()

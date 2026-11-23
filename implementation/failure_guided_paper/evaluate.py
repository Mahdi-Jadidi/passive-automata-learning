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


BENCHMARK_METHODS = tuple((mode, "canonical", enabled)
                          for enabled in (False, True) for mode in ("baseline", "maximal"))


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
    result = solve(D)
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
    assert len(result["certificate"]["swaps"]) == 2
    assert verify(D, result)["status"] == "VERIFIED"
    for bad in ({"negative": 0, "positive": 0, "offset": 1},
                {"negative": 1, "positive": 0, "offset": True}):
        tampered = deepcopy(result)
        tampered["certificate"]["swaps"].append(bad)
        assert verify(D, tampered)["status"] == "INVALID"

    words = ((1, 0, 2), (0, 2, 1))
    matches = ProjectionMatches(((0, 1, 2),), words, lambda: None)
    assert [matches.row((a,)) for a in range(3)] == [(0, 0)] * 3
    assert matches.row((0, 1)) == (None, 0)
    assert matches.row((1, 2)) == (0, None)

    D = sample("abcd", ["", "ab", "cd"], ["ac", "dc"])
    result = solve(D)
    assert result["blocks"] == [["a"], ["b"], ["c", "d"]]
    assert len(result["certificate"]["swaps"]) == 1

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

    def interrupted(blocks, tick):
        return "INCOMPLETE"
    assert solve(D, check_bounds=interrupted)["status"] == "INCOMPLETE"
    assert verify(D, result, check_bounds=interrupted)["status"] == "INCOMPLETE"


def benchmark_trial(name, D, method, repetition, seconds):
    mode, order, preprocess = method
    t0 = perf_counter()
    result = solve(D, mode=mode, order=order, seconds=seconds, preprocess=preprocess)
    t1 = perf_counter()
    record = dict(case=name, mode=mode, order=order, preprocess=preprocess, repetition=repetition,
                  outcome=result["status"], search_seconds=t1 - t0, **result["stats"])
    if result["status"] != "INCOMPLETE":
        certificate = json.dumps(result["certificate"], separators=(",", ":")).encode()
        t2 = perf_counter()
        wire_result = json.loads(json.dumps(result))
        replay = verify(D, wire_result, seconds=max(0, seconds - (perf_counter() - t0)))
        end = perf_counter()
        assert replay["status"] != "INVALID", replay
        record.update(max_devices=result.get("max_devices"), certificate_bytes=len(certificate),
                      replay_seconds=end - t2, outcome=replay["status"], total_seconds=end - t0)
    else:
        record["total_seconds"] = t1 - t0
    return record


def benchmark(seconds, repeats):
    cases = {
        "example": sample("abc", ["ac", "bc"], ["abc"]),
        "singletons_12": sample("abcdefghijkl", [], ["abc"]),
        "greedy_counterexample": sample("abcd", ["", "ab", "cd"], ["ac", "dc"]),
        "one_group_6": group_sample(["abcdef"]),
        "two_groups_6": group_sample(["abc", "def"]),
        "two_groups_8": group_sample(["abcd", "efgh"]),
        "three_groups_9": group_sample(["abc", "def", "ghi"]),
        "three_groups_12": group_sample(["abcd", "efgh", "ijkl"]),
    }
    records = []
    for name, D in cases.items():
        completed_k = set()
        for repetition in range(repeats):
            start = repetition % len(BENCHMARK_METHODS)
            for method in BENCHMARK_METHODS[start:] + BENCHMARK_METHODS[:start]:
                record = benchmark_trial(name, D, method, repetition, seconds)
                records.append(record)
                if record["outcome"] == "VERIFIED":
                    completed_k.add(record["max_devices"])
        assert len(completed_k) <= 1, name
    return cases, records


def summarize(records):
    summary = []
    for case in dict.fromkeys(record["case"] for record in records):
        for mode, order, preprocess in BENCHMARK_METHODS:
            trials = [r for r in records if r["case"] == case and
                      (r["mode"], r["order"], r["preprocess"]) == (mode, order, preprocess)]
            completed = [r for r in trials if r["outcome"] == "VERIFIED"]
            timings = ("generated", "tested", "analysis_seconds", "region_seconds", "search_seconds",
                       "total_seconds", "certificate_bytes", "replay_seconds")
            summary.append(dict(case=case, mode=mode, order=order, preprocess=preprocess,
                                outcomes=dict(Counter(r["outcome"] for r in trials)),
                                medians={k: median(r[k] for r in completed) for k in timings}
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
    cases, records = benchmark(args.seconds, args.repeats)
    report = dict(checks=checks, seconds=args.seconds, repeats=args.repeats,
                  inputs=cases, trials=records, summary=summarize(records))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks))


if __name__ == "__main__":
    main()


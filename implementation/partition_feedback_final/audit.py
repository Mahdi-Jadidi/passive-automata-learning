
"""Logical regressions, exhaustive optimum checks, and documented replay examples."""
from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path
from random import Random

from model import ProjectionOracle, analyze, image, ordered
from search import Evidence, choose_region, fingerprint, lower_bound, solve, supports
from verify import verify

HERE = Path(__file__).resolve().parent
FEEDBACK = dict(preprocess=False, bound_enabled=False, incumbent_enabled=False)


def sample(alphabet, positives, negatives):
    return {"alphabet": list(alphabet), "positive": list(map(list, positives)), "negative": list(map(list, negatives))}


def partitions(symbols):
    if not symbols:
        yield ()
        return
    a, *rest = symbols
    for base in partitions(rest):
        yield (frozenset({a}), *base)
        for j, block in enumerate(base):
            yield (*base[:j], block | {a}, *base[j + 1:])


def compatible(D, P):
    def project(word, block):
        return tuple(a for a in word if a in block)
    return all(any(project(y, b) not in {project(x, b) for x in D["positive"]} for b in P)
               for y in D["negative"])


def optimum(D):
    return max((len(P) for P in partitions(D["alphabet"]) if compatible(D, P)), default=None)


def triples(r, kind, seed=0):
    letters = list(range(3 * r if kind != "sunflower" else 2 * r + 1))
    labels = [f"s{i:02}" for i in letters]
    if kind == "sunflower":
        groups = [(0, 2*i+1, 2*i+2) for i in range(r)]
    else:
        groups = [tuple(letters[k:k+3]) for k in range(0, len(letters), 3)]
    rng = Random(seed)
    W = [a for triple in groups for a in triple] if kind == "order" else rng.sample(letters, len(letters))
    if kind == "order":
        positives = [W]
        negatives = [W[:k] + list(reversed(W[k:k+3])) + W[k+3:] for k in range(0, len(W), 3)]
    else:
        positives = [[a for a in W if a != b] for b in W]
        negatives = [[a for a in W if a not in g] for g in groups]
    rng.shuffle(letters)
    rng.shuffle(positives)
    rng.shuffle(negatives)
    return sample([labels[a] for a in letters], [[labels[a] for a in w] for w in positives],
                  [[labels[a] for a in w] for w in negatives])


def exhaustive_samples():
    yield from (
        sample(alphabet, positives, negatives)
        for alphabet, positives, negatives in (
            ("abc", ["ac", "bc"], ["abc"]), ("abc", ["ab", "ac", "bc"], [""]),
            ("abcd", ["", "ab", "cd"], ["ac", "dc"]), ("abc", ["", "bc", "ac", "ab"], ["abc"]),
            ("", [""], []), ("", [], [""]), ("abc", [], []),
            ("abcd", ["ac", "bc"], ["abc"]), ("abc", ["ac", "ac", "bc"], ["abc", "abc"]),
            ("ab", ["a"], ["a"]), ("ab", ["ab"], ["ba"]),
            (["open", "close"], [["open", "close"]], [["close", "open"]]),
        )
    )
    for n in range(3):
        alphabet = "ab"[:n]
        words = [w for length in range(3) for w in product(alphabet, repeat=length)]
        for labels in product(range(3), repeat=len(words)):
            yield sample(alphabet, [w for w, label in zip(words, labels) if label == 1],
                         [w for w, label in zip(words, labels) if label == 2])
    rng = Random(22112026)
    for i in range(300):
        alphabet = "abcdef"[:i % 4 + 3]
        words = sorted({"".join(rng.choices(alphabet, k=rng.randrange(9))) for _ in range(22)})
        rng.shuffle(words)
        stop = rng.randrange(len(words) + 1)
        yield sample(alphabet, words[:stop], words[stop:])


def node_checks():
    checked = 0
    rng = Random(731)
    for case in range(224):
        n = 4 + case % 2
        D = sample("abcde"[:n],
                   [rng.choices("abcde"[:n], k=rng.randrange(5)) for _ in range(3)],
                   [rng.choices("abcde"[:n], k=rng.randrange(5)) for _ in range(2)])
        Sigma, pos, neg, analysis = analyze(D, lambda: None, enabled=True, order_sensitive=True)
        if "failure" in analysis:
            continue
        masks = {a: 1 << i for i, a in enumerate(Sigma)}
        all_parts = [ordered(sum(masks[a] for a in b) for b in P) for P in partitions(Sigma)]
        adapter = ProjectionOracle(pos, neg, lambda: None)
        solutions = [P for P in all_parts if adapter(P, "test")["status"] == "ACCEPT"]
        facts = Evidence(len(neg), lambda: None)
        for item in analysis["facts"]:
            facts.zero(item)
        for number, P in enumerate(all_parts):
            reply = adapter(P, "test")
            facts.ingest(reply, number)
            descendants = [Q for Q in solutions if all(any(a & b == a for b in Q) for a in P)]
            checks = lower_bound(supports(P, facts), True, lambda: None)[0]
            assert descendants and checks <= len(P) - max(map(len, descendants))
            if reply["status"] == "NO":
                R = choose_region(P, facts, True)
                assert R
                assert all(any(not any(a & r == a and b & r == b for r in R["blocks"])
                               for block in Q for a, b in combinations(P, 2) if a & block == a and b & block == b)
                           for Q in descendants)
                for candidate in all_parts:
                    if all(any(a & b == a for b in R["blocks"]) for a in candidate):
                        assert candidate not in solutions
            checked += 1
    return checked


def run():
    out = HERE / "evidence"
    out.mkdir(exist_ok=True)
    modes = [{}, {"diagnostic_limit": 8}, {**FEEDBACK, "diagnostic_limit": 2},
             {**FEEDBACK, "strategy": "pairs"}]
    former = list(exhaustive_samples())
    targeted = [
        sample("", [], []), sample("", [], [""]), sample("ab", [], [""]),
        sample("abc", ["ab"], []), sample("abc", ["a", "a"], ["", ""]),
        sample("abcd", ["abcd"], ["bacd", "abdc"]),
        sample("abcdef", ["ab", "cd", "ef"], [""]),
        sample("abcd", ["ab", "ac", "bc", "abd", "acd", "bcd"], ["", "d"]),
        sample("abcd", ["a", "bc", "bd"], ["", "ac"]),
        sample("abc", ["abc"], ["bac"]), sample("abc", ["abc"], ["acb"]),
        sample("ab", ["a"], ["a"]), sample("abcd", ["ab", "cd"], [""]),
        sample("abc", ["ab"], ["ba", "baa", "aba"]),
        sample("abz", ["ab"], ["ba"]), sample("abcdef", ["abc", "def"], [""]),
        sample("abcdef", ["abc", "cde", "efa"], [""]),
    ]
    targeted.extend(triples(r, family) for r in (1, 2, 3) for family in ("order", "disjoint", "sunflower"))
    assert optimum(targeted[5]) == 2 and optimum(targeted[6]) == 4
    assert optimum(targeted[9]) == optimum(targeted[10]) == 2
    tests = 0
    for D in former + targeted:
        expected = optimum(D)
        for mode in modes:
            if len(D["alphabet"]) > 6 and mode:
                continue
            result = solve(D, transcript=True, **mode)
            assert result.get("max_devices") == expected, (D, result, expected)
            assert verify(D, result)["status"] == "VERIFIED", (D, result, verify(D, result))
            tests += 1

    D = targeted[12]
    _, pos, neg, _ = analyze(D, lambda: None, enabled=False, order_sensitive=False)
    adapter = ProjectionOracle(pos, neg, lambda: None)
    calls = []
    def spy(P, purpose):
        assert sum(P) == 15 and P not in [prior for prior, _ in calls]
        calls.append((P, purpose))
        return adapter(P, purpose)

    example = solve(D, transcript=True, diagnostic_limit=8, oracle=spy, **FEEDBACK)
    assert calls == [((1, 2, 4, 8), "regular"), ((3, 12), "diagnostic"), ((5, 2, 8), "regular")]
    assert example["transcript"]["unqueried_waived"] == [(1, 2, 12), (3, 4, 8)]
    assert verify(D, example)["status"] == "VERIFIED"
    full_example = solve(D, transcript=True)
    assert verify(D, full_example)["status"] == "VERIFIED"
    assert solve(targeted[9], transcript=True)["blocks"] == [["a", "b"], ["c"]]
    assert solve(targeted[10], transcript=True)["blocks"] == [["a"], ["b", "c"]]
    for family in ("order", "disjoint", "sunflower"):
        fixed = triples(3, family)
        r = solve(fixed, transcript=True)
        assert r["certificate"]["records"][0]["kind"] == "overlap", (family, r)
        assert any(event.get("lower") == 3 for event in r["transcript"]["events"] if event["rule"] == "S09")
    weaker = solve(triples(3, "sunflower"), overlapping=False, transcript=True)
    assert weaker["stats"]["selection"]["visited"] > 1

    # Learn two complementary all-zero regions from two separate full queries.
    antichain = Evidence(1, lambda: None)
    left, right = adapter((3, 4, 8), "test"), adapter((1, 2, 12), "test")
    for response in (left, right):
        separate = Evidence(1, lambda: None)
        separate.ingest(response, 0)
        assert choose_region((3, 12), separate, True) is None
    antichain.ingest(left, 0)
    antichain.ingest(right, 1)
    assert {f["source"] for f in choose_region((3, 12), antichain, True)["facts"]} == {0, 1}
    assert verify(D, solve(D, query_limit=0, **FEEDBACK))["status"] == "INCOMPLETE"

    corrupted = []
    broken = deepcopy(example)
    broken["certificate"]["records"].clear()
    corrupted.append((D, broken))
    broken = deepcopy(example)
    broken["certificate"]["records"][0]["region"]["facts"][0]["j"] = 0
    corrupted.append((D, broken))
    broken = deepcopy(example)
    broken["blocks"] = [["a", "b", "c", "d"], ["ghost"]]
    corrupted.append((D, broken))
    broken = solve(targeted[11])
    broken.update(max_devices=999, blocks=[["ghost"]])
    corrupted.append((targeted[11], broken))
    broken = solve(targeted[13], transcript=True, strategy="pairs", **FEEDBACK)
    broken["transcript"]["queries"][0]["tables"][0]["free"] = [[1], [2]]
    corrupted.append((targeted[13], broken))
    corrupted.append((D, {"status": "INCOMPLETE", "max_devices": 999}))
    corrupted.append((targeted[11], example))
    assert all(verify(d, r)["status"] == "INVALID" for d, r in corrupted)

    logs = {"example": example, "example_full": full_example,
            "empty_alphabet": solve(targeted[1], transcript=True),
            "opposite_labels": solve(targeted[11], transcript=True),
            "unused_and_contraction": solve(targeted[14], transcript=True),
            "duplicate": solve(targeted[4], transcript=True),
            "no_positive": solve(targeted[2], transcript=True),
            "held_together": solve(targeted[13], transcript=True, strategy="pairs", **FEEDBACK),
            "order_triples": solve(triples(3, "order"), transcript=True),
            "sunflower": solve(triples(3, "sunflower"), transcript=True),
            "unit": solve(sample("ab", ["ab"], ["ba"]), transcript=True, preprocess=False),
            "unknown": solve(D, query_limit=0, transcript=True, **FEEDBACK)}
    for name, result in logs.items():
        (out / (name + ".json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    stats = {"exhaustive_cases": len(former), "targeted": len(targeted), "solver_replays": tests,
             "node_checks": node_checks(), "invalid_certificates_rejected": len(corrupted),
             "spy_queries": len(calls), "mixed_source_regions": 2}
    (out / "checks.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats))


if __name__ == "__main__":
    run()

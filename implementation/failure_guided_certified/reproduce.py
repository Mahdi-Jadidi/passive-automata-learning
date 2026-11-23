"""Verify, benchmark and summarize the portable partition selection package."""
import argparse
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
from random import Random
from statistics import median
import sys
from time import perf_counter

import evaluate
from packing import DeletionWitnesses
from search import ProjectionMatches, merge, rejection_region, solve
from verify import verify

HERE = Path(__file__).resolve().parent
METHODS = {
    "all_pairs": ("baseline", False, "off"),
    "contract": ("baseline", True, "off"),
    "feedback": ("maximal", True, "off"),
    "candidate": ("maximal", True, "candidate"),
    "root": ("maximal", True, "root"),
    "nodes": ("maximal", True, "nodes"),
}


def triples(r, seed=None):
    alphabet = [chr(97 + i) if 3 * r <= 26 else f"s{i:02}" for i in range(3 * r)]
    groups = [set(alphabet[i:i+3]) for i in range(0, len(alphabet), 3)]
    word = alphabet[:]
    if seed is not None:
        rng = Random(seed)
        rng.shuffle(word)
        rng.shuffle(alphabet)
    positive = [[a for a in word if a != b] for b in word]
    negative = [[a for a in word if a not in group] for group in groups]
    if seed is not None:
        rng.shuffle(positive)
        rng.shuffle(negative)
    return dict(alphabet=alphabet, positive=positive, negative=negative), groups


def graph_cases():
    for n in (4, 6, 8, 12, 18):
        rng = Random(3810 + n)
        pairs = list(combinations(range(n), 2))
        for label, edges in (
            ("path", [(i, i+1) for i in range(n-1)]),
            ("random", [edge for edge in pairs if rng.random() < 0.36]),
        ):
            vertices = [f"v{i}" for i in range(n)]
            mates = [f"m{i}" for i in range(n)]
            cost = next(k for k in range(n + 1)
                        if any(all(u in X or v in X for u, v in edges)
                               for X in map(set, combinations(range(n), k))))
            yield f"cover_{label}_{n}", dict(alphabet=vertices+mates,
                positive=[[a, b] for a, b in zip(vertices, mates)],
                negative=[[vertices[u], vertices[v]] for u, v in edges]), 2*n-cost


def run_method(D, method, seconds=None):
    mode, preprocess, strength = METHODS[method]
    return solve(D, mode=mode, preprocess=preprocess, strength=strength, shortcuts=False,
                 seconds=seconds)


def check_result(D, result, expected):
    assert result["status"] == ("OPTIMAL" if expected is not None else "INFEASIBLE"), result
    assert result.get("max_devices") == expected, (expected, result)
    assert verify(D, json.loads(json.dumps(result)))["status"] == "VERIFIED", result


def lattice_checks(D):
    alphabet = D["alphabet"]
    ids = {a: i for i, a in enumerate(alphabet)}
    S_plus = [tuple(ids[a] for a in x) for x in D["positive"]]
    S_minus = [tuple(ids[a] for a in y) for y in D["negative"]]
    tick = lambda: None
    policies = DeletionWitnesses(S_plus, S_minus, tick)
    matches = ProjectionMatches(S_plus, S_minus, tick)
    partitions = list(evaluate.partitions(alphabet))
    feasible = [q for q in partitions if evaluate.compatible(D, q)]
    checked = 0
    for p in partitions:
        if evaluate.compatible(D, p):
            continue
        children_of_p = [q for q in feasible if all(any(b <= c for c in q) for b in p)]
        P = tuple(sorted(tuple(sorted(ids[a] for a in b)) for b in p))
        bound, _ = policies.bound(P, matches)
        if children_of_p:
            assert bound <= len(p) - max(map(len, children_of_p))
        i = matches.first_failure(P)
        assert i is not None
        R, positives = rejection_region(P, i, matches, "maximal")
        owners = {a: k for k, b in enumerate(R) for a in b}
        retained = [merge(P, a, b) for a, b in combinations(P, 2)
                    if owners[a[0]] != owners[b[0]]]
        for q in children_of_p:
            assert any(all(any({alphabet[a] for a in b} <= c for c in q)
                           for b in child) for child in retained)
        checked += 1
    return checked


def targeted():
    weighted = evaluate.sample("abcde", ["ab", "ac", "bc", "de"], [""])
    split = evaluate.sample("abcdef", ["ab", "ac", "bc", "de", "df", "ef"], [""])
    overlap = evaluate.sample("abcd", ["ab", "ac", "bc", "abd", "acd", "bcd"], ["", "d"])
    example, _ = triples(3)
    for D, n in [(weighted, 3), (split, 3), (overlap, 3), (example, 6)]:
        result = run_method(D, "nodes")
        check_result(D, result, n)
        assert result["certificate"]["kind"] == "weighted_root"
        assert len(D["alphabet"]) - n == result["stats"]["root_lower"]
    proof = run_method(example, "nodes")
    for change in ("projection", "load", "answer", "missing"):
        wrong = deepcopy(proof)
        rows = wrong["certificate"]["bounds"][0]["deletions"]
        if change == "projection":
            rows[0]["positive"] = next(j for j in range(len(example["positive"]))
                                       if j != rows[0]["positive"] and
                                       any(example["alphabet"][k] not in example["positive"][j]
                                           for k in rows[0]["atoms"]))
        elif change == "load":
            rows[0]["weight"] = 2
        elif change == "answer":
            wrong["blocks"][0].append(wrong["blocks"][1][0])
        else:
            rows.pop(0)
        assert verify(example, wrong)["status"] == "INVALID", change
    wrong = run_method(overlap, "nodes")
    evidence = wrong["certificate"]["bounds"]
    duplicate = deepcopy(evidence[0])
    duplicate["negative"] = 1
    for row in duplicate["deletions"]:
        row["positive"] += 3
    evidence.append(duplicate)
    assert verify(overlap, wrong)["reason"] == "overlapping weighted supports"
    assert run_method(example, "nodes", 0)["status"] == "INCOMPLETE"
    assert verify(example, proof, seconds=0)["status"] == "INCOMPLETE"
    for r in (1, 2, 3):
        D, groups = triples(r)
        pairs = list(combinations(D["alphabet"], 2))
        forced = set(pairs)
        cheaper = 0
        for P in evaluate.partitions(D["alphabet"]):
            compatible = evaluate.compatible(D, P)
            assert compatible == all(any(len(g & b) >= 2 for b in P) for g in groups)
            if compatible:
                forced.intersection_update(pair for pair in pairs if any(set(pair) <= b for b in P))
            cheaper += len(P) > 2*r
        assert not forced and cheaper == {1: 1, 2: 16, 3: 499}[r]
        check_result(D, run_method(D, "nodes"), 2*r)


def correctness():
    rng = Random(88712)
    nodes = 0
    count = 0

    def check(D, k):
        nonlocal nodes, count
        for method in ("candidate", "root", "nodes"):
            check_result(D, run_method(D, method), k)
            count += 1
        if len(D["alphabet"]) <= 5:
            nodes += lattice_checks(D)

    previous = evaluate.correctness(on_case=check)
    evaluate.targeted_checks()
    targeted()
    for _ in range(40):
        nodes += lattice_checks(evaluate.random_sample(rng, 5))
    return {"historical_checks": previous, "weighted_replays": count, "lattice_nodes": nodes}


def fixtures():
    raw = json.loads((HERE / "fixtures.json").read_text())
    for group, inputs in raw.items():
        for name, D in inputs.items():
            expected = evaluate.exhaustive_optimum(D) if len(D["alphabet"]) <= 9 else None
            if name == "singletons_12":
                expected = 12
            if name == "three_groups_12":
                expected = 3
            yield group, name, D, expected
    for r in (1, 2, 3, 4, 8, 16):
        for i in range(6 if r >= 4 else 1):
            D, _ = triples(r, 810000 + i if r >= 4 else None)
            yield "triples", f"triples{r}_{i}", D, 2*r
    for name, D, k in graph_cases():
        yield "vertex_cover", name, D, k
    external = HERE / "hdfs_cases.json"
    if external.is_file():
        for name, D in json.loads(external.read_text()).items():
            yield "hdfs", name, D, None


def trial(D, method, seconds):
    start = perf_counter()
    result = run_method(D, method, seconds)
    solved = perf_counter()
    record = dict(**result["stats"], solve_seconds=solved-start, outcome=result["status"],
                  search_seconds=max(0, solved-start-result["stats"]["analysis_seconds"]
                                     -result["stats"]["packing_seconds"]-result["stats"]["proposal_seconds"]),
                  max_devices=result.get("max_devices"), certificate_kind=result.get("certificate", {}).get("kind"),
                  stopped_at="solve", total_seconds=solved-start)
    if result["status"] == "INCOMPLETE":
        return record
    wire = json.dumps(result, separators=(",", ":"))
    payload = json.loads(wire)
    size = len(json.dumps(result["certificate"], separators=(",", ":")).encode())
    serialized = perf_counter()
    verdict = verify(D, payload, seconds=max(0, seconds-(serialized-start)))
    end = perf_counter()
    assert verdict["status"] in {"VERIFIED", "INCOMPLETE"}, verdict
    return dict(record, outcome=verdict["status"], total_seconds=end-start, certificate_bytes=size,
                serialization_seconds=serialized-solved, replay_seconds=end-serialized,
                stopped_at=None if verdict["status"] == "VERIFIED" else
                ("serialization" if serialized-start >= seconds else "replay"))


def benchmark(path, cases):
    names = list(METHODS)
    # One serial benchmark process. Flush each row for audit after interruption.
    with path.open("w", encoding="utf-8") as output:
        for group, name, D, expected in cases:
            print(f"Benchmark {name}", flush=True)
            actual = set()
            for seconds in (0.5, 5.0):
                for repeat in range(3):
                    shift = repeat + (3 if seconds == 5 else 0)
                    for method in names[shift:] + names[:shift]:
                        row = trial(D, method, seconds)
                        if row["outcome"] == "VERIFIED":
                            actual.add(row["max_devices"])
                            if expected is not None:
                                assert row["max_devices"] == expected, (name, row)
                        output.write(json.dumps(dict(row, cohort=group, case=name, method=method,
                            budget=seconds, repeat=repeat, expected=expected))+"\n")
                        output.flush()
            assert len(actual) <= 1, (name, actual)


def summarize(raw, output):
    buckets = defaultdict(list)
    for line in raw.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        case = row["case"].split("_")[0] if row["cohort"] == "triples" else row["case"]
        buckets[case, row["budget"], row["method"]].append(row)
    fields = ["generated", "tested", "projection_images", "packing_seconds",
              "replay_seconds", "total_seconds", "certificate_bytes"]
    with output.open("w", encoding="utf-8") as stream:
        stream.write("| Case | Budget (s) | Method | Verified / runs | Generated | Tested | Images | Witness (ms) | Replay (ms) | Total (ms) | Certificate (B) |\n")
        stream.write("|" + "---|"*11 + "\n")
        for (case, budget, method), rows in sorted(buckets.items()):
            complete = [row for row in rows if row["outcome"] == "VERIFIED"]
            values = []
            for field in fields:
                factor = 1000 if field.endswith("_seconds") else 1
                values.append(f"{factor*median(r.get(field, 0) for r in complete):.3g}" if complete else "—")
            stream.write("| " + " | ".join([case, str(budget), method,
                f"{len(complete)}/{len(rows)}", *values]) + " |\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--checks-only", action="store_true")
    parser.add_argument("--benchmark-only", action="store_true")
    parser.add_argument("--external-only", action="store_true")
    parser.add_argument("--summarize", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reproduced"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.summarize:
        summarize(args.summarize, args.output / "table.md")
        return
    if not args.benchmark_only and not args.external_only:
        checks = correctness()
        print(checks, flush=True)
        (args.output / "checks.json").write_text(json.dumps(checks, indent=2))
    if not args.checks_only:
        raw = args.output / "trials.jsonl"
        inputs = [entry for entry in fixtures() if
                  (entry[0] == "hdfs" if args.external_only else args.full or entry[1] == "triples3_0")]
        (args.output / "inputs.json").write_text(json.dumps(inputs, indent=2))
        (args.output / "manifest.json").write_text(json.dumps(
            dict(python=sys.version, platform=platform.platform(), processor=platform.processor(),
            source={p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))},
            inputs_sha256=sha256((args.output / "inputs.json").read_bytes()).hexdigest()), indent=2))
        benchmark(raw, inputs)
        summarize(raw, args.output / "table.md")


if __name__ == "__main__":
    main()

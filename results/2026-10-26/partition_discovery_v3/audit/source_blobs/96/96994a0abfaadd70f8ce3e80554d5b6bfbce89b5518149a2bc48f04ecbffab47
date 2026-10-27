"""Build deterministic, immutable local fixtures; execute only through capture."""
import hashlib
import json
from pathlib import Path
import random


def main():
    root = Path(__file__).resolve().parent
    cases = []

    def add(name, data, expected, **extra):
        cases.append({"case_id": name, "input": data, "expected_status": expected, **extra})

    def data(alphabet, positive, negative=()):
        return {"alphabet": list(alphabet), "positive": list(positive), "negative": list(negative)}

    add("repeated_small", data("abc", ["aabbcc", "ccaabb"], ["aabcc", "abacbc"]), "found")
    add("singleton_blocks", data("ab", ["aabbb", "bbbaa"], ["ab"]), "found")
    add("class_unique_not_general", data("abc", ["abc", "cab"]), "found", general_count=3)
    add("no_positive", data("abc", [], [""]), "insufficient_coverage")
    add("one_positive_unique_but_no_certificate", data("ab", ["ab"]), "insufficient_coverage", fixed_count=1)
    add("duplicates_add_no_coverage", data("abc", ["abc", "abc"]), "insufficient_coverage")
    add("absent_symbol", data("abc", ["ab", "ba"]), "insufficient_coverage")
    add("empty_local_words", data("abc", [""], ["a"]), "insufficient_coverage")
    add("count_inconsistency", data("abc", ["a", "aa"]), "assumption_violation", fixed_count=0)
    add("odd_cycle", data("abc", ["abc", "bca", "cab"]), "assumption_violation", fixed_count=0)
    add("negative_conflict", data("abc", ["abc", "cab"], ["acb"]), "assumption_violation", fixed_count=0)
    add("normalize_duplicate_words", data("cba", ["cab", "abc", "cab"], ["aa", "", "aa"]), "found")
    for limit in (2, None):
        add(f"limit_{limit}", data("abc", ["abc", "cab"]), "found", max_solutions=limit)
    add("expired_deadline", data("abc", ["abc", "cab"]), "incomplete", expired_deadline=True)
    malformed = [data("aab", ["ab"]), data("ab", ["ac"]),
                 data("ab", ["ab"], ["ab"]), data("a", ["a"]),
                 {"alphabet": ["a", "b"], "positive": "ab", "negative": []},
                 None]
    for i, item in enumerate(malformed):
        add(f"malformed_{i}", item, "ValueError")
    add("invalid_limit_bool", data("ab", ["ab"]), "ValueError", max_solutions=True)
    add("invalid_limit_zero", data("ab", ["ab"]), "ValueError", max_solutions=0)
    rng = random.Random(20261026)
    for i in range(32):
        size = rng.randrange(2, 7)
        alphabet = [chr(97 + j) for j in range(size)]
        order = alphabet[:]
        rng.shuffle(order)
        cut = rng.randrange(1, size)
        block0, block1 = order[:cut], order[cut:]
        u = "".join(a * rng.randrange(1, 4) for a in block0)
        v = "".join(a * rng.randrange(1, 4) for a in block1)
        add(f"constructive_small_{i:02d}", data(alphabet, [u + v, v + u], [(u + v)[:-1]]),
            "found", target_blocks=[sorted(block0), sorted(block1)])
    alphabet = [chr(0x400 + i) for i in range(128)]
    for name, split in (("balanced_128", 64), ("singleton_128", 1)):
        block0, block1 = alphabet[:split], alphabet[split:]
        u = "".join(block0) + "".join(reversed(block0))
        v = "".join(block1) * 3
        add(name, data(alphabet, [u + v, v + u], [(u + v)[:-1]]), "found",
            target_blocks=[block0, block1])
    payload = {"fixture_id": "C003-S001-SMOKE-v1", "seed": 20261026,
               "cases": cases, "solver_input_policy": "Only case.input is passed to solve."}
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    path = root / "smoke_inputs_v1.json"
    with path.open("xb") as handle:
        handle.write(raw)
    example = cases[0]["input"]
    example_raw = json.dumps(example, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    with (root / "example_input.json").open("xb") as handle:
        handle.write(example_raw)
    print(json.dumps({"fixture_id": payload["fixture_id"], "case_count": len(cases),
                      "fixture_sha256": hashlib.sha256(raw).hexdigest(),
                      "example_sha256": hashlib.sha256(example_raw).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    main()

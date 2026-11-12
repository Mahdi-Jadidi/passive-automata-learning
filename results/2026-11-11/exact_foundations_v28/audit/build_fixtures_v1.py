"""Create frozen, deterministic C028 auditor/provider input fixtures."""
import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def exhaustive_ab():
    words = [[], ["a"], ["b"], ["a", "a"], ["a", "b"], ["b", "a"], ["b", "b"]]
    for labels in __import__('itertools').product(range(3), repeat=7):
        yield {"alphabet": ["a", "b"],
               "positive": [w for w, y in zip(words, labels) if y == 1],
               "negative": [w for w, y in zip(words, labels) if y == 2]}


def seeded():
    for m in range(3, 9):
        alphabet = [f"sym-{i}" for i in range(m)]
        for j in range(10):
            rng = random.Random(280000 + m * 100 + j)
            words = sorted({tuple(rng.choices(alphabet, k=rng.randrange(0, 9))) for _ in range(30)})
            ys = [rng.randrange(3) for _ in words]
            yield {"alphabet": alphabet,
                   "positive": [list(w) for w, y in zip(words, ys) if y == 1],
                   "negative": [list(w) for w, y in zip(words, ys) if y == 2]}


def edge_cases():
    A = "alphabet"; P = "positive"; N = "negative"
    return [
        {A: [], P: [], N: []},                         # empty product, no labels
        {A: [], P: [[]], N: []},                       # epsilon positive, empty partition
        {A: [], P: [], N: [[]]},                       # impossible epsilon negative
        {A: ["a"], P: [], N: []},                      # empty/empty labels, unused symbol
        {A: ["a", "b"], P: [], N: [["a", "b"]]},    # empty P
        {A: ["a", "b"], P: [["a"]], N: []},          # empty N, unused symbol
        {A: ["a", "b"], P: [[]], N: [["a"]]},        # unique optimum vs all-K ambiguity
        {A: ["a", "b"], P: [["a"], ["b"]], N: [["a", "b"]]}, # quantifier order
        {A: ["a", "b"], P: [["a", "b"]], N: [["b", "a"]]},
        {A: ["a", "b", "c"], P: [[], ["a", "b", "c"]], N: [["a"]]},
        {A: ["a", "b", "c"], P: [[], ["a", "b", "c"]], N: [["a"], ["b"]]},
        {A: ["a", "b"], P: [["a", "b"]], N: [["b", "a"]]},
        # Multi-ID concatenation collision trap; these are distinct words.
        {A: ["a", "bc", "ab", "c"], P: [["a", "bc"]], N: [["ab", "c"]]},
        {A: ["x y", "ε", "!", "☃"], P: [["x y", "ε"]], N: [["!", "☃"]]},
        # Literal epsilon-looking ID is a symbol; empty word is [] only.
        {A: ["ε", "literal"], P: [[]], N: [["ε"]]},
        {A: ["same", "other"], P: [["same"], ["same"]], N: [["other"], ["other"]]},
        {A: ["same", "other"], P: [["same"]], N: [["same"]]}, # contradiction
        # Long traces on a small alphabet.
        {A: ["u", "v"], P: [["u", "v"] * 5000], N: [["v", "u"] * 5000]},
        # Sparse observations over a larger alphabet (still exhaustively solvable).
        {A: [f"id-{i}" for i in range(8)], P: [["id-0", "id-7"]], N: [["id-1", "id-6"]]},
    ]


def invalid_cases():
    base = {"alphabet": ["a"], "positive": [], "negative": []}
    return [
        {}, {**base, "extra": 1}, {k: v for k, v in base.items() if k != "positive"},
        {"alphabet": ["a", "a"], "positive": [], "negative": []},
        {"alphabet": [""], "positive": [], "negative": []},
        {"alphabet": [1], "positive": [], "negative": []},
        {"alphabet": ["a"], "positive": ["a"], "negative": []},
        {"alphabet": ["a"], "positive": [["b"]], "negative": []},
        {"alphabet": ["a"], "positive": [[1]], "negative": []},
        {"alphabet": ["a"], "positive": [None], "negative": []},
        {"alphabet": "a", "positive": [], "negative": []},
    ]


def write_jsonl(path, entries):
    path.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n" for x in entries), encoding="utf-8")
    data = path.read_bytes()
    return {"file": path.name, "records": len(entries), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


if __name__ == "__main__":
    sets = {
        "binary_ternary_length2_v1.jsonl": list(exhaustive_ab()),
        "seeded_m3_to_m8_v1.jsonl": list(seeded()),
        "edge_cases_v1.jsonl": edge_cases(),
        "invalid_cases_v1.jsonl": invalid_cases(),
    }
    manifest = [write_jsonl(HERE / name, records) for name, records in sets.items()]
    out = HERE / "FIXTURE_MANIFEST_V1.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))

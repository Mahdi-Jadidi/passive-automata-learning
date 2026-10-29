"""Small independent full-set oracle for known-k generalized partitions."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "known_k_v3.py"
spec = importlib.util.spec_from_file_location("known_k_smoke", SOURCE)
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)


def brute(data, k, cap=None):
    alphabet = sorted(data["alphabet"])
    positive, negative = sorted(set(data["positive"])), sorted(set(data["negative"]))
    found = set()
    # Canonical restricted-growth assignment on the actual sorted alphabet.
    def rec(prefix):
        if len(prefix) == len(alphabet):
            if max(prefix) + 1 != k:
                return
            blocks = [{a for a, owner in zip(alphabet, prefix) if owner == side}
                      for side in range(k)]
            languages = [{solver._project(word, block) for word in positive}
                         for block in blocks]
            if cap is not None and any(len(lang) > cap for lang in languages):
                return
            if all(any(solver._project(word, block) not in languages[i]
                       for i, block in enumerate(blocks)) for word in negative):
                found.add(tuple(tuple(sorted(block)) for block in blocks))
            return
        used = max(prefix) + 1 if prefix else 0
        for side in range(min(used, k - 1) + 1):
            rec(prefix + (side,))
    rec(())
    return found


cases = json.loads((HERE / "fixtures" / "smoke_inputs.json").read_text(encoding="utf-8"))
comparisons = []
for data in cases:
    for k in range(2, min(4, len(data["alphabet"])) + 1):
        for cap in (None, 1, 2):
            expected = brute(data, k, cap)
            result = solver.solve(data, k=k, max_solutions=None, local_word_cap=cap)
            actual = {tuple(tuple(block) for block in row["blocks"])
                      for row in result["solutions"]}
            comparisons.append({"alphabet": data["alphabet"], "k": k, "cap": cap,
                                "expected": sorted(map(str, expected)),
                                "actual": sorted(map(str, actual)),
                                "status": result["status"],
                                "search_exhausted": result["search_exhausted"]})
print(json.dumps(comparisons, ensure_ascii=False, sort_keys=True))
assert all(item["expected"] == item["actual"] for item in comparisons)
assert all(item["search_exhausted"] for item in comparisons)

# Distinguish a one-solution prefix from a completed uniqueness result.
res = solver.solve({"alphabet": list("abcd"), "positive": [], "negative": []}, k=2,
                   max_solutions=1)
print(json.dumps({"limited": {k: res[k] for k in
                              ("status", "search_exhausted", "uniqueness")}}))
assert res["status"] == "found" and res["uniqueness"] == "unknown"

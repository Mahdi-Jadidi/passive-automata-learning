"""Tiny frozen branch sanity check. Run only through evidence/capture.py."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
legacy_path = ROOT / "results/2026-10-27/partition_scaling_v4/general/known_k_v3.py"
legacy_spec = importlib.util.spec_from_file_location("legacy_known_k_v3", legacy_path)
legacy = importlib.util.module_from_spec(legacy_spec)
legacy_spec.loader.exec_module(legacy)

spec = importlib.util.spec_from_file_location("candidate_qexact_v1", HERE / "known_k_qexact_v1.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
data = json.loads((HERE / "sanity_inputs_v1.json").read_text(encoding="utf-8"))

unrestricted = candidate.solve(data, max_solutions=None)
legacy_result = legacy.solve(data, max_solutions=None)
q2_pruned = candidate.solve(data, local_word_cap=2, max_solutions=None)
q2_baseline = candidate.solve(data, local_word_cap=2, max_solutions=None,
                              use_q_opposition=False, use_contextual_must_links=False)

def parts(result):
    return sorted(tuple(tuple(block) for block in solution["blocks"])
                  for solution in result["solutions"])

def verify(result):
    for solution in result["solutions"]:
        blocks = [set(block) for block in solution["blocks"]]
        languages = [set(words) for words in solution["positive_projection_languages"]]
        for witness in solution["negative_witnesses"]:
            side = witness["block_index"]
            assert witness["projection"] not in languages[side]
            word = witness["negative"]
            assert "".join(ch for ch in word if ch in blocks[side]) == witness["projection"]

assert unrestricted["search_exhausted"] and legacy_result["search_exhausted"]
assert parts(unrestricted) == parts(legacy_result)
assert q2_pruned["search_exhausted"] and q2_baseline["search_exhausted"]
assert parts(q2_pruned) == parts(q2_baseline)
verify(unrestricted)
verify(q2_pruned)
print(json.dumps({"unrestricted": {"status": unrestricted["status"],
                                   "uniqueness": unrestricted["uniqueness"],
                                   "count": len(unrestricted["solutions"]),
                                   "partitions": parts(unrestricted)},
                  "legacy_unrestricted_count": len(legacy_result["solutions"]),
                  "q2_pruned": {"status": q2_pruned["status"],
                                "uniqueness": q2_pruned["uniqueness"],
                                "count": len(q2_pruned["solutions"]),
                                "nodes": q2_pruned["metrics"]["nodes"],
                                "partitions": parts(q2_pruned)},
                  "q2_baseline_count": len(q2_baseline["solutions"]),
                  "witness_checks": "passed"}, ensure_ascii=False, sort_keys=True))

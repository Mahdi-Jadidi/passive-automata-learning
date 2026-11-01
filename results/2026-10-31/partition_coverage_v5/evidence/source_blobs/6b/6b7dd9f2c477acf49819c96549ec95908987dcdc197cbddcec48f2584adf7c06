"""Exhaustive same-input declared-class frontier; no hidden q inference."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("candidate_qexact_v2", HERE / "known_k_qexact_v2.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
data = json.loads((HERE / "sanity_inputs_v1.json").read_text(encoding="utf-8"))
rows = []
for q in (1, 2, 3, 4, None):
    result = provider.solve(data, local_word_cap=q, max_solutions=None)
    rows.append({"declared_q": q, "status": result["status"],
                 "complete": result["complete"], "search_exhausted": result["search_exhausted"],
                 "uniqueness": result["uniqueness"],
                 "compatible_partition_count": len(result["solutions"])})
assert all(row["complete"] for row in rows)
print(json.dumps({"note": "Each row is a separate declared model class; no hidden q is inferred.",
                  "frontier": rows}, ensure_ascii=False, sort_keys=True))

"""Run a declared q-class frontier on one frozen input; infer no hidden q."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "candidate_qexact_v1", HERE / "known_k_qexact_v1.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
data = json.loads((HERE / "sanity_inputs_v1.json").read_text(encoding="utf-8"))
frontier = []
for q in (1, 2, 3, 4, None):
    result = provider.solve(data, local_word_cap=q, max_solutions=None)
    frontier.append({"declared_q": q, "status": result["status"],
                     "search_exhausted": result["search_exhausted"],
                     "uniqueness": result["uniqueness"],
                     "compatible_partition_count": len(result["solutions"]),
                     "cannot_link_count": len(result["constraints"]["cannot_link_edges"]),
                     "unary_conflict_count": len(result["constraints"]["unary_conflicts"])})
assert all(row["search_exhausted"] for row in frontier)
print(json.dumps({"note": "Each row is a separate declared model class; no hidden q is inferred.",
                  "frontier": frontier}, ensure_ascii=False, sort_keys=True))

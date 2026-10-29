"""Preserve output checking a proposed but invalid rescue counterexample."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OLD_HELPER = ROOT / "results" / "2026-10-26" / "partition_constraints_v2" / "baseline" / "partition_solver.py"
spec = importlib.util.spec_from_file_location("readonly_old_partition_helper", OLD_HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

cases = {
    "omits_required_rescue": {"alphabet": ["a", "b"], "positive": ["", "b"], "negative": ["a"]},
    "includes_required_rescue": {"alphabet": ["a", "b"], "positive": ["", "b", "ab"], "negative": ["a"]},
}
outputs = {}
for label, data in cases.items():
    alphabet, positive, negative = helper.validate(data)
    components, edges = helper.witness_graph(alphabet, positive, negative)
    outputs[label] = {"components": components, "edges": edges,
                      "partition_search": helper.solve(data)}
print(json.dumps(outputs, ensure_ascii=False, sort_keys=True))
assert all(edge["witness"]["rule"] != "insertion_rescue"
           for edge in outputs["omits_required_rescue"]["edges"])
assert any(edge["witness"]["rule"] == "insertion_rescue"
           for edge in outputs["includes_required_rescue"]["edges"])
assert outputs["omits_required_rescue"]["partition_search"]["feasible_partition_count"] == 1
assert outputs["includes_required_rescue"]["partition_search"]["feasible_partition_count"] == 0

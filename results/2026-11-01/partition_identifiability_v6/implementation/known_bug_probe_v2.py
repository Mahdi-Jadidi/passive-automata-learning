"""Reproduce the sorted-pair insertion-rescue verifier defect in solver_v3."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c006_solver_v3_probe", ROOT / "solver_v3.py")
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)
data = json.loads((ROOT / "known_bug_probe_v1.json").read_text(encoding="utf-8"))
result = solver.solve(data, max_solutions=None)
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
assert result["status"] == "not_decomposable", "expected a replayed connected-graph obstruction"



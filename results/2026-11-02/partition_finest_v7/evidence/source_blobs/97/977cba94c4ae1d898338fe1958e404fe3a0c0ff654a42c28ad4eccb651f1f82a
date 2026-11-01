"""Capture the v1 initialization defect on a certified multiple-maximal sample."""
import importlib.util
import json
from pathlib import Path

root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("c007_finest_v1_failure",root/"finest_solver_v1.py")
solver=importlib.util.module_from_spec(spec); spec.loader.exec_module(solver)
data=json.loads((root/"v1_meet_init_counterexample.json").read_text(encoding="utf-8"))
result=solver.solve(data,mode="adaptive")
print(json.dumps(result,ensure_ascii=False,sort_keys=True))
assert result["status"]=="multiple_maximal_exist", "v1 must not treat the forced-component partition as the meet"

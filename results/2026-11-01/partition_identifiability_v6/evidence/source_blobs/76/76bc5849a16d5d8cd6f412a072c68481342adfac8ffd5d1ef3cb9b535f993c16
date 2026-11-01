"""Reproduce solver_v3 status bug with a deterministic interruption."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c006_solver_v3_interrupt_probe", ROOT / "solver_v3.py")
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)
data = {"alphabet":["a","b","c"], "positive":["abc"], "negative":[]}
original = solver._compatibility
calls = 0
def interrupt_on_second_cut(*args, **kwargs):
    global calls
    calls += 1
    if calls == 2:
        raise KeyboardInterrupt
    return original(*args, **kwargs)
solver._compatibility = interrupt_on_second_cut
result = solver.solve(data, max_solutions=None)
print(json.dumps({"compatibility_calls":calls, "result":result}, ensure_ascii=False, sort_keys=True))
assert result["status"] == "incomplete", "interruption after an answer must stay explicitly incomplete"

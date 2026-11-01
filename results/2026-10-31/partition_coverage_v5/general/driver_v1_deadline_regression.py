"""Reproduce the reviewed v1 immediate-deadline exception; capture only."""
import importlib.util
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("candidate_qexact_v1", HERE / "known_k_qexact_v1.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
data = json.loads((HERE / "sanity_inputs_v1.json").read_text(encoding="utf-8"))
print(json.dumps(provider.solve(data, deadline=time.perf_counter() - 1), sort_keys=True))

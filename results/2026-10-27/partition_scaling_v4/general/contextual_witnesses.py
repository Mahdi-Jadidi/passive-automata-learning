"""Exercise long nonempty-context swap and insertion-rescue witnesses."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("known_k_contextual", HERE / "known_k_v3.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
cases = json.loads((HERE / "fixtures" / "contextual_witnesses.json").read_text(encoding="utf-8"))
records = {}
for family, data in cases.items():
    alphabet, positive, negative, k = provider._validate(data, 2)
    components, edges = provider._components(alphabet, positive, negative, None)
    result = provider.solve(data, k=2, max_solutions=None)
    records[family] = {"positive_lengths": list(map(len, positive)),
                       "negative_lengths": list(map(len, negative)),
                       "components": components, "edges": edges,
                       "status": result["status"],
                       "search_exhausted": result["search_exhausted"],
                       "solutions": result["solutions"]}
print(json.dumps(records, ensure_ascii=False, sort_keys=True))
assert any(e["witness"]["rule"] == "adjacent_swap" for e in records["swap"]["edges"])
assert any(e["witness"]["rule"] == "insertion_rescue" for e in records["rescue"]["edges"])
assert all(len(cases[name]["positive"][0]) > 20 and len(cases[name]["negative"][0]) > 20
           for name in cases)
assert all(record["search_exhausted"] for record in records.values())

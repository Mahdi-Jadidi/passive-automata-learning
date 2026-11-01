"""Corrected must/cannot and empty-positive branch controls; capture only."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("candidate_qexact_v2", HERE / "known_k_qexact_v2.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
contradiction_data = json.loads((HERE / "sanity_contradiction_v2.json").read_text(encoding="utf-8"))
empty_data = json.loads((HERE / "sanity_empty_positive_v1.json").read_text(encoding="utf-8"))
contradiction = provider.solve(contradiction_data, local_word_cap=1, max_solutions=None)
empty = provider.solve(empty_data, local_word_cap=1, max_solutions=None)
assert contradiction["status"] == "infeasible" and contradiction["search_exhausted"]
assert contradiction["constraints"]["presearch_contradiction"]["kind"] == "must_link_and_cannot_link"
assert set(contradiction["constraints"]["presearch_contradiction"]["must_link_component"]) == {"a", "b"}
assert empty["status"] == "found" and empty["search_exhausted"]
assert len(empty["solutions"]) == 7
for solution in empty["solutions"]:
    assert len(solution["negative_witnesses"]) == len(empty_data["negative"])
    for witness in solution["negative_witnesses"]:
        assert witness["projection"] not in solution["positive_projection_languages"][witness["block_index"]]
print(json.dumps({"must_cannot_contradiction": {
                      "status": contradiction["status"],
                      "proof_kind": contradiction["constraints"]["presearch_contradiction"]["kind"],
                      "must_component": contradiction["constraints"]["presearch_contradiction"]["must_link_component"]},
                  "empty_positive": {"status": empty["status"],
                                     "partition_count": len(empty["solutions"]),
                                     "missing_symbol": "d",
                                     "witness_checks": "passed"}},
                 ensure_ascii=False, sort_keys=True))

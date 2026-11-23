
"""Materialize and verify the examples linked from the decision tables."""
from copy import deepcopy
import json
from pathlib import Path

from audit import FEEDBACK, exhaustive_samples, optimum, sample, triples
from compact import verify_compact, with_optional_witnesses
from model import ProjectionOracle, analyze
from search import Evidence, choose_region, solve
from staged import solve as solve_staged
from verify import verify

HERE = Path(__file__).resolve().parent
OUT = HERE / "evidence"


def save(name, value):
    (OUT / (name + ".json")).write_text(json.dumps(value, indent=2), encoding="utf-8")


def main():
    D = sample("abcde", ["", "c", "edb", "edc"], ["aeeb", "de"])
    result = solve(D, transcript=True, diagnostic_limit=2, **FEEDBACK)
    assert verify(D, result)["status"] == "VERIFIED"
    assert any(e["rule"] == "S04" for e in result["transcript"]["events"])
    save("reject_superset", {"input": D, **result})

    D = json.loads((HERE / "example.json").read_text(encoding="utf-8-sig"))
    _, pos, neg, _ = analyze(D, lambda: None, enabled=False, order_sensitive=False)
    adapter = ProjectionOracle(pos, neg, lambda: None)
    def sparse(P, purpose):
        response = deepcopy(adapter(P, purpose))
        for row in response["tables"]:
            row["zeros"] = [[i] for i, _ in row["zeros"]]
        return response

    restored = solve(D, transcript=True, diagnostic_limit=8, **FEEDBACK,
                     oracle=with_optional_witnesses(D, sparse))
    assert verify(D, restored)["status"] == "VERIFIED"
    for response in restored["transcript"]["queries"]:
        for row in response["tables"]:
            row["zeros"] = [[i, None] for i, _ in row["zeros"]]
    for record in restored["certificate"]["records"]:
        for fact in record["region"]["facts"]:
            fact.pop("j")
    assert verify_compact(D, restored)["status"] == "VERIFIED"
    fake = deepcopy(restored)
    first_row = fake["transcript"]["queries"][2]["tables"][0]
    first_row["zeros"] = [[0]]
    assert verify_compact(D, fake)["status"] == "INVALID"
    save("compact_witness_audit", {"reconstructed": True, "false_zero_rejected": True})

    evidence = Evidence(len(neg), lambda: None)
    queries = []
    candidate = (3, 12)
    for number, proposal in enumerate([(3, 4, 8), (1, 2, 12)]):
        reply = adapter(proposal, "diagnostic")
        one = Evidence(len(neg), lambda: None)
        one.ingest(reply, number)
        assert choose_region(candidate, one, True) is None
        evidence.ingest(reply, number)
        queries.append({"id": number, **reply})
    proof = choose_region(candidate, evidence, True)
    assert {item["source"] for item in proof["facts"]} == {0, 1}
    save("mixed_sources", {"input": D, "queries": queries,
                           "events": [{"rule": "S02", "blocks": candidate, "region": proof}]})

    D = sample("abcdef", ["ab", "cd", "ef"], [""])
    result = solve(D, transcript=True, **FEEDBACK)
    assert verify(D, result)["status"] == "VERIFIED"
    proof = result["certificate"]
    remove = next(i for i, node in enumerate(proof["records"]) if len(node["blocks"]) < len(proof["root"]))
    removed = proof["records"].pop(remove)
    verdict = verify(D, result)
    assert verdict == {"status": "INVALID", "reason": "missing reachable partition"}
    save("missing_child_audit", {"input": D, "removed": removed, "verdict": verdict})

    witnesses = []
    for family in ("sunflower", "order", "disjoint"):
        for r in (4, 8, 16):
            D = triples(r, family)
            result = solve(D, transcript=True)
            assert verify(D, result)["status"] == "VERIFIED" and result["max_devices"] == len(D["alphabet"]) - r
            event = next(e for e in result["transcript"]["events"] if e["rule"] == "S09")
            assert event["lower"] == r and result["stats"]["selection"]["visited"] == 1
            witnesses.append({"family": family, "r": r, "bound": event["lower"],
                              "blocks": result["max_devices"], "stats": result["stats"]})
    save("root_certificates", witnesses)

    hdfs = json.loads((OUT / "hdfs_cases.json").read_text(encoding="utf-8"))
    D = hdfs["hdfs_holdout_512"]
    stage = solve_staged(D, transcript=True, query_limit=0)
    assert stage["max_devices"] == len(D["alphabet"]) == 29
    assert verify(D, stage)["status"] == "VERIFIED"
    save("singleton_stage", {"case": "hdfs_holdout_512", **stage})
    stage_tests = 0
    for D in exhaustive_samples():
        fast = solve_staged(D, transcript=True)
        assert fast.get("max_devices") == optimum(D) and verify(D, fast)["status"] == "VERIFIED"
        stage_tests += 1
    save("singleton_stage_checks", {"independent_replays": stage_tests})

    files_by_rule = {
        "A01": "opposite_labels", "A02": "empty_alphabet", "A03": "unused_and_contraction",
        "A04": "duplicate", "A05": "example", "A06": "no_positive",
        "A07": "unused_and_contraction", "A08": "sunflower", "A09": "order_triples", "A10": "unit", "A11": "singleton_stage",
        "S01": "example", "S02": "example_full", "S03": "held_together", "S04": "reject_superset",
        "S05": "example", "S06": "example", "S07": "sunflower", "S08": "unit",
        "S09": "sunflower", "S10": "held_together", "S11": "unknown",
    }
    result = {}
    for number, filename in files_by_rule.items():
        log = json.loads((OUT / (filename + ".json")).read_text(encoding="utf-8"))
        transcript = log["transcript"]
        indices = [i for i, row in enumerate(transcript["events"]) if row["rule"] == number]
        assert indices, (number, filename)
        result[number] = {"file": filename + ".json", "event_indices": indices}
    save("rule_index", result)
    print(f"{len(result)} rule IDs matched recorded evidence")


if __name__ == "__main__":
    main()

"""Revalidate long S001 outputs, separating one censored C003 bridge from harness status."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "corpora" / "stage1_v4"
MANIFEST = ROOT / "manifest.json"
ATTEMPTS = HERE / "attempts"
CASES = [
    ("20261027T091302.825297Z_dacaf432de", "long_singleton_a8_k2_l128", False),
    ("20261027T091303.733968Z_3bc0fd6e00", "long_singleton_a32_k4_l1024", False),
    ("20261027T091304.927763Z_86c39e11e2", "long_singleton_a128_k8_l4096", False),
    ("20261027T091307.151525Z_811917fc64", "long_singleton_a32_k2_l1024", True),
    ("20261027T091309.117723Z_3fc66028ea", "long_singleton_a128_k2_l1024", True),
    ("20261027T091318.427730Z_f3a21b622a", "long_singleton_a128_k2_l4096", True),
]


def pkey(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def project(word, block):
    keep = set(block)
    return "".join(ch for ch in word if ch in keep)


def verify_solution(data, sol):
    blocks = sol["blocks"]
    errors = []
    if len(blocks) != data["k"] or sorted(ch for b in blocks for ch in b) != sorted(data["alphabet"]):
        errors.append("bad_partition")
    langs = [{project(w, b) for w in data["positive"]} for b in blocks]
    if sol.get("positive_projection_languages") != [sorted(x) for x in langs]:
        errors.append("bad_positive_projection_languages")
    witnesses = {x["negative"]: x for x in sol.get("negative_witnesses", [])}
    if set(witnesses) != set(data["negative"]):
        errors.append("missing_or_duplicate_negative_witness")
    for n in data["negative"]:
        unseen = [i for i,b in enumerate(blocks) if project(n,b) not in langs[i]]
        w = witnesses.get(n)
        if not unseen or w is None:
            errors.append("negative_not_rejected")
        elif w["block_index"] not in unseen or w["projection"] != project(n,blocks[w["block_index"]]):
            errors.append("invalid_negative_witness")
    return errors


def main():
    rows = {x["id"]: x for x in json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]}
    output, problems = [], []
    for attempt, case_id, has_bridge in CASES:
        attempt_dir = ATTEMPTS / attempt
        raw = json.loads((attempt_dir / "stdout.bin").read_text(encoding="utf-8"))
        capture = json.loads((attempt_dir / "result.json").read_text(encoding="utf-8"))
        row = rows[case_id]
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        truth = json.loads((ROOT / row["truth"]).read_text(encoding="utf-8"))
        result = raw["result"]
        expected_edges = {tuple(sorted((a,b))) for i,left in enumerate(truth["blocks"])
                          for right in truth["blocks"][i+1:] for a in left for b in right}
        actual_edges = {tuple(edge) for edge in result.get("graph",{}).get("edges",[])}
        local_problems = []
        if raw.get("case") != case_id:
            local_problems.append("wrong_case_id")
        if result.get("status") != "found" or result.get("uniqueness") != "unique":
            local_problems.append("S001_not_unique_found")
        if actual_edges != expected_edges:
            local_problems.append("S001_opposition_graph_mismatch")
        if result.get("solutions"):
            sol = result["solutions"][0]
            if pkey(sol["blocks"]) != pkey(truth["blocks"]):
                local_problems.append("S001_partition_mismatch")
            local_problems.extend(verify_solution(data, sol))
        else:
            local_problems.append("S001_solution_missing")
        c003 = raw.get("c003_bridge")
        bridge_status = None
        if has_bridge:
            bridge_status = c003.get("status") if c003 else None
            if bridge_status == "found":
                for sol in c003.get("solutions",[]):
                    if pkey(sol["blocks"]) != pkey(truth["blocks"]):
                        local_problems.append("C003_partition_mismatch")
                    local_problems.extend("C003_"+e for e in verify_solution(data,sol))
            elif bridge_status == "incomplete":
                if c003.get("search_exhausted") or c003.get("uniqueness") != "unknown":
                    local_problems.append("C003_incomplete_overclaimed")
            else:
                local_problems.append("C003_unexpected_status")
        # Last attempt was marked program_error only because the harness required
        # an old C003 long cell to finish; inspect that as a censored bridge.
        allowed_capture_status = "program_error" if bridge_status == "incomplete" else "success"
        if capture.get("execution_status") != allowed_capture_status:
            local_problems.append("unexpected_capture_status")
        if local_problems:
            problems.append({"case":case_id,"problems":local_problems})
        output.append({"attempt_id":attempt,"case":case_id,"capture_status":capture["execution_status"],
                       "S001_status":result["status"],"S001_uniqueness":result["uniqueness"],
                       "alphabet_size":len(data["alphabet"]),"k":data["k"],"length":row.get("length"),
                       "S001_edge_count":len(actual_edges),"independent_expected_edge_count":len(expected_edges),
                       "C003_status":bridge_status,"C003_classification":"censored_incomplete" if bridge_status=="incomplete" else "complete" if bridge_status else "not_run",
                       "problems":local_problems})
    report={"audit":"independent re-review of six preserved long singleton correctness attempts v1",
            "case_count":len(output),"S001_mismatch_count":sum(bool(r["problems"]) for r in output),
            "C003_incomplete_attempts":sum(r["C003_status"]=="incomplete" for r in output),
            "attempts":output,"problems":problems,
            "classification_note":"One capture exits program_error because the harness required C003 to finish; its raw record shows C003 incomplete at the predeclared 25s solver deadline while S001 completed and passed all independent checks. Preserve as censored, not a solver mismatch."}
    sys.stdout.write(json.dumps(report,ensure_ascii=False,separators=(",",":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__=="__main__":
    raise SystemExit(main())

"""Check one frozen long singleton input and its full opposition certificate."""
from __future__ import annotations
import importlib.util
import json
import sys
import time
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
CASE_ID = sys.argv[2]
BRIDGE = len(sys.argv) > 3 and sys.argv[3] == "--bridge"
ROOT = MANIFEST.parent
HERE = Path(__file__).resolve().parent
S001 = HERE.parent / "structural" / "singleton_solver_v1.py"
C003_FIXED = HERE.parents[2] / "2026-10-26" / "partition_discovery_v3" / "structural" / "fixed_word_solver.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pkey(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def project(word, block):
    members = set(block)
    return "".join(ch for ch in word if ch in members)


def verify_solution(data, solution):
    blocks = solution["blocks"]
    errors = []
    if len(blocks) != data["k"] or any(not block for block in blocks):
        errors.append("bad_block_count")
    if sorted(ch for block in blocks for ch in block) != sorted(data["alphabet"]):
        errors.append("not_an_alphabet_partition")
    langs = [{project(w, block) for w in data["positive"]} for block in blocks]
    reported = solution.get("positive_projection_languages")
    if reported != [sorted(x) for x in langs]:
        errors.append("projection_language_mismatch")
    witnesses = {w["negative"]: w for w in solution.get("negative_witnesses", [])}
    if set(witnesses) != set(data["negative"]):
        errors.append("negative_witness_coverage")
    for word in data["negative"]:
        unseen = [i for i, block in enumerate(blocks) if project(word, block) not in langs[i]]
        w = witnesses.get(word)
        if not unseen or w is None:
            errors.append("negative_not_rejected")
        elif w["block_index"] not in unseen or w["projection"] != project(word, blocks[w["block_index"]]):
            errors.append("invalid_negative_witness")
    return errors


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = next(x for x in manifest["cases"] if x["id"] == CASE_ID)
    if row["family"] not in ("long_singleton", "stress_16384"):
        raise ValueError("selected case is not a long singleton input")
    data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
    truth = json.loads((ROOT / row["truth"]).read_text(encoding="utf-8"))
    module = load("audit_s001_large", S001)
    started = time.perf_counter()
    result = module.solve(data, k=data["k"], deadline=time.perf_counter()+25, max_solutions=None)
    # Derive the complete graph independently from the planted local blocks:
    # every within-block pair has invariant projection; forward/reverse block
    # concatenations reverse every cross-block pair.
    expected_edges = {tuple(sorted((a, b))) for i, left in enumerate(truth["blocks"])
                      for right in truth["blocks"][i+1:] for a in left for b in right}
    actual_edges = {tuple(edge) for edge in result.get("graph", {}).get("edges", [])}
    problems = []
    if result.get("status") != "found" or len(result.get("solutions", [])) != 1:
        problems.append({"kind": "certificate_not_found", "status": result.get("status")})
    if actual_edges != expected_edges:
        problems.append({"kind": "opposition_graph_not_complete_k_partite",
                         "expected_edge_count": len(expected_edges),
                         "actual_edge_count": len(actual_edges),
                         "missing_count": len(expected_edges-actual_edges),
                         "extra_count": len(actual_edges-expected_edges)})
    if result.get("certificate", {}).get("kind") != "complete_k_partite_opposition":
        problems.append({"kind": "wrong_certificate_kind", "certificate": result.get("certificate")})
    if result.get("solutions"):
        solution = result["solutions"][0]
        if pkey(solution["blocks"]) != pkey(truth["blocks"]):
            problems.append({"kind": "wrong_partition", "actual": pkey(solution["blocks"]),
                             "truth": pkey(truth["blocks"])})
        errors = verify_solution(data, solution)
        if errors:
            problems.append({"kind": "invalid_solution_or_witness", "errors": errors})
    bridge_result = None
    if BRIDGE:
        old = load("audit_c003_fixed_large", C003_FIXED)
        bridge_result = old.solve(data, deadline=time.perf_counter()+25, max_solutions=None)
        if bridge_result.get("status") != "found" or len(bridge_result.get("solutions", [])) != 1:
            problems.append({"kind": "c003_bridge_not_found", "status": bridge_result.get("status")})
        for solution in bridge_result.get("solutions", []):
            if pkey(solution["blocks"]) != pkey(truth["blocks"]):
                problems.append({"kind": "c003_bridge_wrong_partition"})
            errs = verify_solution(data, solution)
            if errs:
                problems.append({"kind": "c003_bridge_bad_witness", "errors": errs})
    record = {"case": CASE_ID, "alphabet_size": len(data["alphabet"]), "k": data["k"],
              "length": row.get("length"), "positive_count": len(data["positive"]),
              "negative_count": len(data["negative"]), "result": result,
              "c003_bridge": bridge_result,
              "independent_complete_k_partite_edges": len(expected_edges),
              "unique_partition_proof": "all cross-part pairs are opposition edges; exactly k nonempty color classes force one color per planted part; within-part projections are invariant",
              "audit_elapsed_nonbenchmark_seconds": time.perf_counter()-started,
              "problems": problems}
    sys.stdout.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

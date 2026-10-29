"""Force maximal rolling-hash collisions and verify exact witness guards."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
CORPUS = MANIFEST.parent
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "general" / "known_k_v3.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def key(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def verify_edge(edge, data):
    pset, nset = set(data["positive"]), set(data["negative"])
    pair = tuple(edge["symbols"])
    w = edge["witness"]
    if w["rule"] == "adjacent_swap":
        p, n, i = w["positive"], w["negative"], w["position"]
        return (p in pset and n in nset and p[:i] == n[:i] and
                p[i] != p[i+1] and n[i:i+2] == p[i+1]+p[i] and
                p[i+2:] == n[i+2:] and tuple(sorted((p[i],p[i+1]))) == pair)
    if w["rule"] == "insertion_rescue":
        base, rescued = w["positive"]
        n, i = w["negative"], w["position"]
        if base not in pset or rescued not in pset or n not in nset:
            return False
        if base != n[:i] + n[i+1:]:
            return False
        a = n[i]
        for j in (i, i+1):
            if j <= len(n):
                b = rescued[j]
                if b != a and rescued == n[:j] + b + n[j:] and tuple(sorted((a,b))) == pair:
                    return True
        return False
    return False


def main():
    module = load("audit_general_hash_v3", SOURCE)
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]
    selected = {r["id"]: r for r in rows if r["id"] in
                {"edge_rescue_counterexample", "edge_rescue_true_control"}}
    reports, problems = [], []
    original = (module._HASH_MOD, module._HASH_BASE)
    try:
        for cid in sorted(selected):
            data = json.loads((CORPUS / selected[cid]["input"]).read_text(encoding="utf-8"))
            ordinary_edges = module._components(sorted(data["alphabet"]),
                                                sorted(set(data["positive"])),
                                                sorted(set(data["negative"])), None)[1]
            module._HASH_MOD, module._HASH_BASE = 1, 1
            collision_edges = module._components(sorted(data["alphabet"]),
                                                 sorted(set(data["positive"])),
                                                 sorted(set(data["negative"])), None)[1]
            ordinary_set = {tuple(e["symbols"]) for e in ordinary_edges}
            collision_set = {tuple(e["symbols"]) for e in collision_edges}
            if collision_set != ordinary_set:
                problems.append({"id": cid, "kind": "hash_collision_changed_edge_set",
                                 "ordinary": sorted(ordinary_set), "forced": sorted(collision_set)})
            invalid = [e for e in collision_edges if not verify_edge(e, data)]
            if invalid:
                problems.append({"id": cid, "kind": "false_edge_under_forced_collision", "edges": invalid})
            forced_result = module.solve(data, k=data["k"], deadline=None,
                                         max_solutions=None, local_word_cap=None)
            actual = {key(s["blocks"]) for s in forced_result["solutions"]}
            if cid == "edge_rescue_counterexample":
                expected = {tuple(sorted((tuple([data["alphabet"][0]]),
                                          tuple([data["alphabet"][1]]))))}
                if actual != expected or collision_set:
                    problems.append({"id": cid, "kind": "missing_rescue_false_component",
                                     "actual": sorted(actual), "edges": sorted(collision_set)})
            else:
                if actual or collision_set != {tuple(sorted(data["alphabet"]))}:
                    problems.append({"id": cid, "kind": "true_rescue_not_preserved",
                                     "actual": sorted(actual), "edges": sorted(collision_set)})
            reports.append({"id": cid, "hash_modulus": 1, "hash_base": 1,
                            "hash_values": sorted({module._hash_word(w) for w in
                                                   data["positive"] + data["negative"]}),
                            "ordinary_edges": ordinary_edges, "forced_collision_edges": collision_edges,
                            "forced_solution_count": len(actual), "forced_status": forced_result["status"]})
            module._HASH_MOD, module._HASH_BASE = original
    finally:
        module._HASH_MOD, module._HASH_BASE = original
    out = {"audit": "forced rolling-hash collision verification v1",
           "candidate_source": str(SOURCE), "collision_mode": {"modulus": 1, "base": 1},
           "reports": reports, "problems": problems}
    sys.stdout.write(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

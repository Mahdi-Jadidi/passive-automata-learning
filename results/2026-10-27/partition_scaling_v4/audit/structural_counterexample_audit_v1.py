"""Independently certify the connected k=3 non-unique opposition control."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
ROOT = MANIFEST.parent
HERE = Path(__file__).resolve().parent
SMALL_AUDIT = HERE / "stage1_small_audit_v1.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def project(word, pair):
    keep = set(pair)
    return "".join(ch for ch in word if ch in keep)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = next(x for x in manifest["cases"] if x["id"] == "three_color_connected_nonunique")
    data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
    alpha = sorted(data["alphabet"])
    base = data["positive"][0]
    edges = []
    for i, a in enumerate(alpha):
        for b in alpha[i+1:]:
            if any(project(w, (a,b)) != project(base, (a,b)) for w in data["positive"][1:]):
                edges.append([a,b])
    adjacency = {a:set() for a in alpha}
    for a,b in edges:
        adjacency[a].add(b); adjacency[b].add(a)
    seen, components = set(), []
    for root in alpha:
        if root in seen: continue
        comp, stack = set(), [root]
        while stack:
            cur = stack.pop()
            if cur in comp: continue
            comp.add(cur); stack.extend(adjacency[cur]-comp)
        seen.update(comp); components.append(sorted(comp))
    helper = load("audit_small_oracle", SMALL_AUDIT)
    general = helper.oracle(data, 3)
    capped = helper.oracle(data, 3, cap=1)
    empty_row = next(x for x in manifest["cases"] if x["id"] == "empty_positive_negative")
    empty = json.loads((ROOT / empty_row["input"]).read_text(encoding="utf-8"))
    empty_general = helper.oracle(empty, 2)
    empty_q1 = helper.oracle(empty, 2, cap=1)
    empty_singleton = helper.oracle(empty, 2, exact_singleton=True)
    # Construct actual singleton languages beyond all finite negative projections.
    bound = 1 + max((len(w) for w in empty["negative"]), default=0)
    empty_constructive_witnesses = []
    for partition in sorted(empty_singleton):
        words = [block[0] * bound for block in partition]
        for n in empty["negative"]:
            if all(project(n, block) == word for block, word in zip(partition, words)):
                raise AssertionError("constructed singleton factorization accepts a negative")
        empty_constructive_witnesses.append({"blocks": partition, "local_words": words})
    problems = []
    expected_path = [[alpha[i], alpha[i+1]] for i in range(len(alpha)-1)]
    if edges != expected_path:
        problems.append("opposition_graph_is_not_expected_path_P4")
    if len(components) != 1:
        problems.append("opposition_graph_is_not_connected")
    if len(general) <= 1 or len(capped) <= 1:
        problems.append("control_does_not_demonstrate_multiple_k3_partitions")
    if not (len(empty_general) == len(empty_q1) == len(empty_singleton) == 3):
        problems.append("empty_positive_semantics_partition_count_mismatch")
    result = {"audit": "connected k=3 non-unique and empty-positive controls v1",
              "case": row["id"], "alphabet": alpha, "positive_count": len(data["positive"]),
              "opposition_edges": edges, "opposition_components": components,
              "general_unordered_partitions": len(general),
              "q1_unordered_partitions": len(capped),
              "q3_claim_rejected": "connected P4 opposition alone is not a k=3 unique-coloring certificate",
              "empty_positive_case": empty_row["id"],
              "general_cap1_partition_count": len(empty_q1),
              "singleton_exactly_one_partition_count": len(empty_singleton),
              "empty_positive_semantics": "cap-1 finite projection model uses empty observed projection sets; exact-one singleton class instead chooses arbitrary nonempty local words of length greater than every negative projection",
              "constructive_empty_positive_witnesses": empty_constructive_witnesses,
              "problems": problems}
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

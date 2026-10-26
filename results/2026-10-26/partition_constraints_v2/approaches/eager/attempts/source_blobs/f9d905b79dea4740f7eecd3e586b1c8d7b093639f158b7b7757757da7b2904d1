"""C002 shared helpers candidate; derives paths rather than relying on cwd."""
from __future__ import annotations

import importlib.util
from functools import lru_cache
from itertools import combinations
from pathlib import Path


def cycle_root():
    for parent in Path(__file__).resolve().parents:
        if ((parent / "coordination" / "CONTRACT.md").is_file()
                and (parent / "baseline" / "partition_solver.py").is_file()):
            return parent
    raise RuntimeError("cannot locate the C002 cycle root")


@lru_cache(maxsize=1)
def load_baseline():
    path = cycle_root() / "baseline" / "partition_solver.py"
    spec = importlib.util.spec_from_file_location("c002_frozen_baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    return load_baseline().validate(data)


def project(word, block):
    return load_baseline().project(word, block)


def witness_graph(alphabet, positive, negative):
    return load_baseline().witness_graph(alphabet, positive, negative)


def distinguishers(alphabet, n, p):
    """Inclusion-minimal distinguishing singleton/pair index sets."""
    singles = tuple((i,) for i, a in enumerate(alphabet) if n.count(a) != p.count(a))
    singleton_indices = {item[0] for item in singles}
    pairs = []
    for i, j in combinations(range(len(alphabet)), 2):
        if i in singleton_indices or j in singleton_indices:
            continue
        block = {alphabet[i], alphabet[j]}
        if project(n, block) != project(p, block):
            pairs.append((i, j))
    return singles + tuple(pairs)


def graph_constraints(alphabet, edges):
    indices = {a: i for i, a in enumerate(alphabet)}
    result = []
    for edge in edges:
        a, b = (indices[symbol] for symbol in edge["symbols"])
        result.append(("or", tuple(
            ("and", (("lit", a, side), ("lit", b, side)))
            for side in (0, 1))))
    return result


def partition_record(alphabet, positive, negative, assignment):
    """Return a direct-criterion witness record, or None if infeasible."""
    if (len(assignment) != len(alphabet) or assignment[0] != 0
            or any(side not in (0, 1) for side in assignment)
            or 1 not in assignment):
        raise ValueError("assignment must be a canonical nonempty bipartition")
    blocks = [{a for a, side in zip(alphabet, assignment) if side == s}
              for s in (0, 1)]
    projections = [{project(p, block) for p in positive} for block in blocks]
    witnesses = []
    for n in negative:
        unseen = [s for s in (0, 1) if project(n, blocks[s]) not in projections[s]]
        if not unseen:
            return None
        side = unseen[0]
        witnesses.append({"negative": n, "block_index": side,
                          "projection": project(n, blocks[side]),
                          "all_unseen_block_indices": unseen})
    return {"blocks": [sorted(block) for block in blocks],
            "positive_projection_languages": [sorted(p) for p in projections],
            "negative_witnesses": witnesses}


def result_from_records(alphabet, positive, negative, records, *, method,
                        components, edges, stats=None, complete=True, metrics=None):
    """Build the common complete/incomplete JSON result contract."""
    ordered = sorted(records, key=lambda r: tuple(tuple(b) for b in r["blocks"]))
    count = len(ordered)
    if not complete:
        status = "incomplete"
        interpretation = "Interrupted enumeration: stored partitions are only a lower-bound set."
    elif not count:
        status = "infeasible"
        interpretation = "No regular product model with two nonempty disjoint blocks fits these labels."
    elif count == 1:
        status = "unique"
        interpretation = ("Unique sample-feasible partition; equals the true declared partition "
                          "if a noise-free two-block target of this model exists.")
    else:
        status = "ambiguous"
        interpretation = "Several two-block partitions fit; the sample does not identify a unique declared partition."
    stats = dict(stats or {})
    metric_data = dict(metrics or {})
    metric_data.update(stats)
    return {
        "alphabet": alphabet, "k": 2, "method": method, "complete": bool(complete),
        "status": status, "interpretation": interpretation,
        "sample_size": {"positive": len(positive), "negative": len(negative)},
        "graph": {"edges": edges, "components": components,
                  "component_count": len(components),
                  "known_k_certificate": bool(complete and len(components) == 2 and count == 1),
                  "certificate_condition": "Requires a true noise-free two-block disjoint-alphabet target."},
        "search": {"graph_pruning": True,
                   "candidates_checked": stats.get("complete_assignments", 0),
                   "all_symbol_bipartitions": (1 << (len(alphabet) - 1)) - 1},
        "feasible_partition_count": count if complete else None,
        "found_partition_count": count, "feasible_partitions": ordered,
        "metrics": metric_data,
        "limitations": ("Unbounded regular local factors; no local DFA recovery, "
                        "distribution-free recovery, novelty, or efficiency guarantee.")}

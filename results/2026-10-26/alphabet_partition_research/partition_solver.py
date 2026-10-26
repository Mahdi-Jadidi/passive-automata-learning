"""Small exact two-block passive partition demonstrator (Python standard library).

Usage: python partition_solver.py input.json [--no-graph-pruning]
Alphabet: 2..10 distinct one-character strings. Empty word: "".
Worst case: 2**(m-1)-1 unordered bipartitions; no efficiency claim.
"""

import argparse
import json
import sys
from pathlib import Path


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    alphabet = data.get("alphabet")
    if (not isinstance(alphabet, list) or not 2 <= len(alphabet) <= 10
            or any(not isinstance(a, str) or len(a) != 1 for a in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError("alphabet must list 2..10 distinct one-character strings")
    sigma = set(alphabet)
    samples = []
    for name in ("positive", "negative"):
        words = data.get(name)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(f"{name} must be a list of strings")
        if any(set(w) - sigma for w in words):
            raise ValueError(f"{name} contains a symbol outside alphabet")
        samples.append(sorted(set(words)))
    positive, negative = samples
    if set(positive) & set(negative):
        raise ValueError("A word cannot have both labels")
    return sorted(alphabet), positive, negative


def project(word, block):
    return "".join(a for a in word if a in block)


def witness_graph(alphabet, positive, negative):
    pos, neg = set(positive), set(negative)
    edges = {}

    def record(a, b, witness):
        if a != b:
            edges.setdefault(tuple(sorted((a, b))), witness)

    for word in positive:
        for i in range(len(word) - 1):
            a, b = word[i:i + 2]
            swapped = word[:i] + b + a + word[i + 2:]
            if a != b and swapped in neg:
                record(a, b, {"rule": "swap", "positive": [word],
                              "negative": swapped, "position": i})
    for word in negative:
        for i, a in enumerate(word):
            base = word[:i] + word[i + 1:]
            if base not in pos:
                continue
            for b in alphabet:
                if a == b:
                    continue
                for insertion in (i, i + 1):
                    rescued = word[:insertion] + b + word[insertion:]
                    if rescued in pos:
                        record(a, b, {"rule": "insertion_rescue",
                                      "positive": [base, rescued],
                                      "negative": word, "position": i})
    neighbors = {a: set() for a in alphabet}
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    components, seen = [], set()
    for a in alphabet:
        if a in seen:
            continue
        stack, component = [a], set()
        while stack:
            v = stack.pop()
            if v not in component:
                component.add(v)
                stack.extend(neighbors[v] - component)
        seen.update(component)
        components.append(sorted(component))
    return components, [{"symbols": list(pair), "witness": edges[pair]}
                        for pair in sorted(edges)]


def solve(data, prune=True):
    alphabet, positive, negative = validate(data)
    components, edges = witness_graph(alphabet, positive, negative)
    atoms = components if prune else [[a] for a in alphabet]
    feasible, checked = [], 0
    # The atom containing the smallest symbol is fixed in block zero.
    for mask in range(1, 1 << (len(atoms) - 1)):
        left, right = set(atoms[0]), set()
        for i, atom in enumerate(atoms[1:]):
            (right if mask & (1 << i) else left).update(atom)
        blocks = [left, right]
        projections = [{project(p, b) for p in positive} for b in blocks]
        checked += 1
        witnesses = []
        for n in negative:
            rejecting = [i for i, b in enumerate(blocks)
                         if project(n, b) not in projections[i]]
            if not rejecting:
                break
            i = rejecting[0]
            witnesses.append({"negative": n, "block_index": i,
                              "projection": project(n, blocks[i]),
                              "all_unseen_block_indices": rejecting})
        else:
            feasible.append({"blocks": [sorted(b) for b in blocks],
                             "positive_projection_languages":
                                 [sorted(p) for p in projections],
                             "negative_witnesses": witnesses})
    count = len(feasible)
    status = "infeasible" if count == 0 else "unique" if count == 1 else "ambiguous"
    meanings = {
        "infeasible": "No regular product model with two nonempty disjoint blocks fits these labels.",
        "unique": "Unique sample-feasible partition; equals the true declared partition if a noise-free two-block target of this model exists.",
        "ambiguous": "Several two-block partitions fit; this sample alone cannot guarantee the true declared partition."
    }
    return {
        "alphabet": alphabet, "k": 2, "status": status,
        "interpretation": meanings[status],
        "sample_size": {"positive": len(positive), "negative": len(negative)},
        "graph": {"edges": edges, "components": components,
                  "component_count": len(components),
                  "known_k_certificate": len(components) == 2 and count == 1,
                  "certificate_condition": "Requires existence of a true noise-free two-block disjoint-alphabet target."},
        "search": {"graph_pruning": prune, "candidates_checked": checked,
                   "all_symbol_bipartitions": (1 << (len(alphabet) - 1)) - 1},
        "feasible_partition_count": count, "feasible_partitions": feasible,
        "limitations": "Unbounded regular local factors; finite-sample partition consistency only. No local DFA recovery or distribution-free recovery guarantee."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--no-graph-pruning", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = solve(data, prune=not args.no_graph_pruning)
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

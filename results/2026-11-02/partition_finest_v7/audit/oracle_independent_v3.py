#!/usr/bin/env python3
"""Second independent all-k oracle and frozen-corpus/DFA-sidecar auditor."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_payload(data):
    return hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def validate(data):
    alphabet = data.get("alphabet")
    positive = data.get("positive")
    negative = data.get("negative")
    if not isinstance(alphabet, list) or any(not isinstance(s, str) for s in alphabet):
        raise ValueError("alphabet must be a list of symbols")
    if len(set(alphabet)) != len(alphabet):
        raise ValueError("duplicate alphabet symbol")
    if not isinstance(positive, list) or not isinstance(negative, list):
        raise ValueError("labels must be word lists")
    allowed = set(alphabet)
    for words in (positive, negative):
        if any(not isinstance(w, list) or any(not isinstance(s, str) or s not in allowed for s in w)
               for w in words):
            raise ValueError("word outside alphabet or malformed word")
        if len(set(map(tuple, words))) != len(words):
            raise ValueError("duplicate word within label")
    if set(map(tuple, positive)) & set(map(tuple, negative)):
        raise ValueError("label conflict")
    return alphabet, positive, negative


def partitions_by_insertion(size):
    """Enumerate each set partition once by inserting ordered elements."""
    if size == 0:
        yield ()
        return

    def extend(next_symbol, blocks):
        if next_symbol == size:
            yield tuple(tuple(block) for block in blocks)
            return
        for position in range(len(blocks)):
            changed = [list(block) for block in blocks]
            changed[position].append(next_symbol)
            yield from extend(next_symbol + 1, changed)
        yield from extend(next_symbol + 1, blocks + [[next_symbol]])

    yield from extend(1, [[0]])


def encode(partition, alphabet):
    return [list(alphabet[index] for index in block) for block in partition]


def block_mask(block):
    result = 0
    for index in block:
        result |= 1 << index
    return result


def block_projection(word, alphabet, mask):
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    return tuple(symbol for symbol in word if mask & (1 << index[symbol]))


def compatible_direct(partition, alphabet, positives, negatives):
    for negative in negatives:
        rejected = False
        for block in partition:
            mask = block_mask(block)
            projection = block_projection(negative, alphabet, mask)
            matched = False
            for positive in positives:
                if block_projection(positive, alphabet, mask) == projection:
                    matched = True
                    break
            if not matched:
                rejected = True
                break
        if not rejected:
            return False
    return True


def binary_reference(alphabet_size, alphabet, positives, negatives):
    result = []
    if alphabet_size < 2:
        return result
    full = (1 << alphabet_size) - 1
    # Fix symbol zero on the left to avoid complement duplicates.
    for left in range(1, full):
        if not (left & 1):
            continue
        right = full ^ left
        if not right:
            continue
        partition = (tuple(i for i in range(alphabet_size) if left & (1 << i)),
                     tuple(i for i in range(alphabet_size) if right & (1 << i)))
        if compatible_direct(partition, alphabet, positives, negatives):
            result.append(partition)
    return result


def strict_split_exists(partition, alphabet, positives, negatives):
    """A coarsening-monotonicity characterization of a maximal refinement."""
    for position, block in enumerate(partition):
        if len(block) < 2:
            continue
        first = block[0]
        remainder = block[1:]
        size = len(block)
        # Subsets containing first canonically represent every unordered split.
        for selector in range(1 << (size - 1)):
            left = [first]
            right = []
            for offset, symbol_index in enumerate(remainder):
                (left if selector & (1 << offset) else right).append(symbol_index)
            if not right:
                continue
            split = [list(piece) for j, piece in enumerate(partition) if j != position]
            split.extend((left, right))
            split.sort(key=lambda block_: block_[0])
            if compatible_direct(tuple(tuple(x) for x in split), alphabet, positives, negatives):
                return True
    return False


def independent_meet(partitions, size):
    def coowned_everywhere(i, j):
        for partition in partitions:
            if not any(i in block and j in block for block in partition):
                return False
        return True

    # Build each equivalence class symmetrically; this avoids relying on the
    # primary oracle's DSU implementation or its partition encoding.
    classes = {tuple(j for j in range(size) if coowned_everywhere(i, j))
               for i in range(size)}
    return tuple(sorted(classes, key=lambda group: group[0]))


def refines(fine, coarse):
    coarse_blocks = [set(block) for block in coarse]
    return all(any(set(block) <= coarse_block for coarse_block in coarse_blocks)
               for block in fine)


def finest_by_direct_poset(compatible):
    """Use the target definition directly, without inferring it from the meet."""
    candidates = []
    for candidate in compatible:
        if all(refines(candidate, other) for other in compatible):
            candidates.append(candidate)
    return candidates


def maximal_frontier(partitions, alphabet, positives, negatives):
    return [partition for partition in partitions
            if not strict_split_exists(partition, alphabet, positives, negatives)]


def analyze(data):
    alphabet, positives, negatives = validate(data)
    compatible = [partition for partition in partitions_by_insertion(len(alphabet))
                  if compatible_direct(partition, alphabet, positives, negatives)]
    meet = independent_meet(compatible, len(alphabet))
    frontier = maximal_frontier(compatible, alphabet, positives, negatives)
    binary = binary_reference(len(alphabet), alphabet, positives, negatives)
    direct_finest = finest_by_direct_poset(compatible)
    if (len(direct_finest) == 1) != (meet in compatible):
        raise AssertionError("direct finest definition disagrees with meet feasibility")
    if direct_finest and direct_finest[0] != meet:
        raise AssertionError("direct finest candidate differs from computed meet")
    if (len(frontier) == 1) != (len(direct_finest) == 1):
        raise AssertionError("frontier uniqueness differs from direct finest definition")
    return {
        "payload_sha256": digest_payload(data),
        "compatible_partition_count": len(compatible),
        "compatible_by_k": {str(k): sum(len(p) == k for p in compatible)
                             for k in range(1, len(alphabet) + 1)},
        "compatible_partitions": [encode(p, alphabet) for p in compatible],
        "compatible_binary_partitions": [encode(p, alphabet) for p in binary],
        "meet": encode(meet, alphabet),
        "meet_compatible": any(meet == p for p in compatible),
        "direct_finest_candidates": [encode(p, alphabet) for p in direct_finest],
        "unique_finest_by_direct_poset": len(direct_finest) == 1,
        "maximal_refinement_frontier": [encode(p, alphabet) for p in frontier],
    }


def reachable(states, start, transitions):
    seen = {start}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for target in transitions[str(state)].values():
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def has_cycle_in_subgraph(nodes, transitions):
    color = {node: 0 for node in nodes}

    def visit(node):
        color[node] = 1
        for target in transitions[str(node)].values():
            if target not in nodes:
                continue
            if color[target] == 1:
                return True
            if color[target] == 0 and visit(target):
                return True
        color[node] = 2
        return False

    return any(color[node] == 0 and visit(node) for node in nodes)


def dfa_is_infinite(component):
    states = set(component["states"])
    transitions = component["transitions"]
    if set(transitions) != {str(state) for state in states}:
        return False
    if any(set(row) != set(component["alphabet"]) for row in transitions.values()):
        return False
    if any(target not in states for row in transitions.values() for target in row.values()):
        return False
    start_reachable = reachable(states, component["start"], transitions)
    reverse = {state: set() for state in states}
    for source, row in transitions.items():
        for target in row.values():
            reverse[target].add(int(source))
    coaccessible = set(component["accepting"])
    queue = deque(coaccessible)
    while queue:
        state = queue.popleft()
        for predecessor in reverse[state]:
            if predecessor not in coaccessible:
                coaccessible.add(predecessor)
                queue.append(predecessor)
    productive_reachable = start_reachable & coaccessible
    return has_cycle_in_subgraph(productive_reachable, transitions)


def dfa_accepts(component, word):
    state = component["start"]
    for symbol in word:
        state = component["transitions"][str(state)][symbol]
    return state in component["accepting"]


def verify_sidecars(inputs, sidecars):
    if len(inputs) != len(sidecars):
        raise AssertionError("sidecar/input row count mismatch")
    checked_components = 0
    for row, sidecar in zip(inputs, sidecars):
        data = row["input"]
        if sidecar["case_id"] != row["case_id"] or sidecar["payload_sha256"] != digest_payload(data):
            raise AssertionError(f"hidden sidecar is not bound to {row['case_id']}")
        blocks = sidecar["planted_partition"]
        if {s for block in blocks for s in block} != set(data["alphabet"]):
            raise AssertionError(f"planted partition coverage failure: {row['case_id']}")
        if sum(len(block) for block in blocks) != len(data["alphabet"]):
            raise AssertionError(f"planted partition duplicate: {row['case_id']}")
        components = sidecar["components"]
        if len(components) != len(blocks):
            raise AssertionError(f"component count mismatch: {row['case_id']}")
        for block, component in zip(blocks, components):
            if set(block) != set(component["alphabet"]):
                raise AssertionError(f"component alphabet mismatch: {row['case_id']}")
            if not dfa_is_infinite(component):
                raise AssertionError(f"component language not verified infinite: {row['case_id']}")
            checked_components += 1
        def in_product(word):
            return all(dfa_accepts(component,
                       [symbol for symbol in word if symbol in set(component["alphabet"])])
                       for component in components)
        if any(not in_product(word) for word in data["positive"]):
            raise AssertionError(f"positive violates hidden product: {row['case_id']}")
        if any(in_product(word) for word in data["negative"]):
            raise AssertionError(f"negative violates hidden product: {row['case_id']}")
    return checked_components


def normalized_set(values):
    return sorted(canonical(value) for value in values)


def main():
    if len(sys.argv) != 6:
        raise SystemExit("usage: oracle_independent_v1.py INPUTS PRIMARY SIDECARS REPORT SUMMARY")
    input_path, primary_path, sidecar_path, report_path, summary_path = map(Path, sys.argv[1:])
    rows = read_jsonl(input_path)
    primary_rows = read_jsonl(primary_path)
    sidecars = read_jsonl(sidecar_path)
    if not (len(rows) == len(primary_rows)):
        raise AssertionError("primary oracle row count mismatch")
    dfa_components = verify_sidecars(rows[:len(sidecars)], sidecars)
    independent_rows = []
    for row, primary in zip(rows, primary_rows):
        result = analyze(row["input"])
        if result["payload_sha256"] != primary["payload_sha256"]:
            raise AssertionError(f"payload digest disagreement: {row['case_id']}")
        for key in ("compatible_partition_count", "compatible_by_k", "meet",
                    "meet_compatible", "maximal_refinement_frontier",
                    "compatible_binary_partitions"):
            if key in ("maximal_refinement_frontier", "compatible_binary_partitions"):
                a = normalized_set(result[key])
                b = normalized_set(primary[key])
            else:
                a, b = result[key], primary[key]
            if a != b:
                raise AssertionError(f"independent oracle mismatch on {row['case_id']} field {key}")
        # Full compatible all-k set equality is the exact sample oracle contract.
        if normalized_set(result["compatible_partitions"]) != normalized_set(primary["compatible_partitions"]):
            raise AssertionError(f"all-k set mismatch: {row['case_id']}")
        result["case_id"] = row["case_id"]
        independent_rows.append(result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("".join(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n"
                                   for result in independent_rows), encoding="utf-8", newline="\n")
    summary = {
        "status": "accepted",
        "rows_compared": len(rows),
        "all_k_exact_set_matches": len(rows),
        "binary_reference_exact_set_matches": len(rows),
        "frontier_matches": len(rows),
        "hidden_infinite_dfa_components_verified": dfa_components,
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "primary_sha256": hashlib.sha256(primary_path.read_bytes()).hexdigest(),
        "sidecar_sha256": hashlib.sha256(sidecar_path.read_bytes()).hexdigest(),
        "independent_output_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                            encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

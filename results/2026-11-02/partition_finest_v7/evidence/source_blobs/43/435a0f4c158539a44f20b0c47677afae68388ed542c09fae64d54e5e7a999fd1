#!/usr/bin/env python3
"""Direct-projection all-k oracle using restricted-growth-string partitions."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def partitions_rgs(size: int):
    if size < 0:
        raise ValueError("negative alphabet size")
    if size == 0:
        yield ()
        return
    labels = [0] * size

    def visit(index: int, maximum: int):
        if index == size:
            count = maximum + 1
            blocks = [[] for _ in range(count)]
            for symbol_index, label in enumerate(labels):
                blocks[label].append(symbol_index)
            yield tuple(tuple(block) for block in blocks)
            return
        for label in range(maximum + 2):
            labels[index] = label
            yield from visit(index + 1, max(maximum, label))

    labels[0] = 0
    yield from visit(1, 0)


def compatible(partition, alphabet, positives, negatives) -> bool:
    projection_sets = []
    for block in partition:
        symbols = {alphabet[i] for i in block}
        projection_sets.append({tuple(symbol for symbol in word if symbol in symbols)
                                for word in positives})
    for negative in negatives:
        separated = False
        for block, observed in zip(partition, projection_sets):
            symbols = {alphabet[i] for i in block}
            projection = tuple(symbol for symbol in negative if symbol in symbols)
            if projection not in observed:
                separated = True
                break
        if not separated:
            return False
    return True


def encode_partition(partition, alphabet):
    return [list(alphabet[i] for i in block) for block in partition]


def refines(fine, coarse) -> bool:
    coarse_sets = [set(block) for block in coarse]
    return all(any(set(block) <= target for target in coarse_sets) for block in fine)


def maximal_refinements(compatible_partitions):
    compatible_set = set(compatible_partitions)
    result = []
    for candidate in compatible_partitions:
        has_compatible_binary_split = False
        for block_index, block in enumerate(candidate):
            if len(block) < 2:
                continue
            first, remainder = block[0], block[1:]
            for selector in range(1 << len(remainder)):
                left, right = [first], []
                for offset, symbol_index in enumerate(remainder):
                    (left if selector & (1 << offset) else right).append(symbol_index)
                if not right:
                    continue
                split = [list(piece) for i, piece in enumerate(candidate) if i != block_index]
                split.extend((left, right))
                normalized = tuple(tuple(piece) for piece in sorted(split, key=lambda part: part[0]))
                if normalized in compatible_set:
                    has_compatible_binary_split = True
                    break
            if has_compatible_binary_split:
                break
        if not has_compatible_binary_split:
            result.append(candidate)
    return result


def meet_of(partitions, alphabet_size):
    if not partitions:
        return tuple((i,) for i in range(alphabet_size))
    labels = []
    for i in range(alphabet_size):
        labels.append(i)
    # Two symbols are equivalent only if every compatible partition co-owns them.
    parent = list(range(alphabet_size))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(alphabet_size):
        for j in range(i + 1, alphabet_size):
            if all(any(i in block and j in block for block in part)
                   for part in partitions):
                union(i, j)
    groups = {}
    for i in range(alphabet_size):
        groups.setdefault(find(i), []).append(i)
    return tuple(tuple(group) for group in sorted(groups.values(), key=lambda g: g[0]))


def validate_input(record):
    data = record["input"] if "input" in record else record
    alphabet = data["alphabet"]
    positives = data["positive"]
    negatives = data["negative"]
    if not isinstance(alphabet, list) or any(not isinstance(s, str) for s in alphabet):
        raise ValueError("alphabet must be a list of strings")
    if len(alphabet) != len(set(alphabet)):
        raise ValueError("alphabet symbols must be unique")
    allowed = set(alphabet)
    for label, words in (("positive", positives), ("negative", negatives)):
        if not isinstance(words, list):
            raise ValueError(f"{label} must be a list")
        if any(not isinstance(w, list) or any(not isinstance(s, str) or s not in allowed for s in w)
               for w in words):
            raise ValueError(f"invalid {label} word")
        if len({tuple(w) for w in words}) != len(words):
            raise ValueError(f"duplicate {label} word")
    if {tuple(w) for w in positives} & {tuple(w) for w in negatives}:
        raise ValueError("positive/negative conflict")
    return alphabet, positives, negatives


def analyze(record):
    alphabet, positives, negatives = validate_input(record)
    compatible_parts = [p for p in partitions_rgs(len(alphabet))
                        if compatible(p, alphabet, positives, negatives)]
    meet = meet_of(compatible_parts, len(alphabet))
    frontier = maximal_refinements(compatible_parts)
    binaries = [p for p in compatible_parts if len(p) == 2]
    meet_compatible = meet in compatible_parts
    return {
        "case_id": record.get("case_id", "unnamed"),
        "payload_sha256": hashlib.sha256(canonical_json(record.get("input", record)).encode("utf-8")).hexdigest(),
        "alphabet_size": len(alphabet),
        "compatible_partition_count": len(compatible_parts),
        "compatible_by_k": {str(k): sum(len(p) == k for p in compatible_parts)
                             for k in range(1, len(alphabet) + 1)},
        "compatible_partitions": [encode_partition(p, alphabet) for p in compatible_parts],
        "compatible_binary_partitions": [encode_partition(p, alphabet) for p in binaries],
        "meet": encode_partition(meet, alphabet),
        "meet_compatible": meet_compatible,
        "unique_finest": meet_compatible,
        "maximal_refinement_frontier": [encode_partition(p, alphabet) for p in frontier],
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: oracle_direct_v1.py INPUTS.jsonl OUTPUT.jsonl")
    input_path, output_path = map(Path, sys.argv[1:])
    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = [analyze(row) for row in rows]
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for result in results:
            stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {"rows": len(rows), "unique_payloads": len({
        result["payload_sha256"] for result in results}),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest()}
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

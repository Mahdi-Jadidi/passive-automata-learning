#!/usr/bin/env python3
"""Independent exact oracles for the four frozen C010 scale inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCALE = ROOT / "scale_v1"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def partitions(items: list) -> object:
    """Yield each set partition once by inserting the first item canonically."""
    if not items:
        yield []
        return
    head, *tail = items
    for part in partitions(tail):
        for index in range(len(part)):
            candidate = [block.copy() for block in part]
            candidate[index].append(head)
            yield candidate
        yield [[head], *[block.copy() for block in part]]


def project(word: str, block: set[str]) -> str:
    return "".join(ch for ch in word if ch in block)


def feasible(data: dict, part: list[list[str]]) -> bool:
    languages = [{project(p, set(block)) for p in data["positive"]}
                 for block in part]
    return all(any(project(n, set(block)) not in language
                   for block, language in zip(part, languages))
               for n in data["negative"])


def rgs(part: list[list[str]], alphabet: list[str]) -> list[int]:
    owner = {ch: index for index, block in enumerate(part) for ch in block}
    renaming: dict[int, int] = {}
    result = []
    for ch in alphabet:
        raw = owner[ch]
        renaming.setdefault(raw, len(renaming))
        result.append(renaming[raw])
    return result


def lift_atom_partition(part: list[list[int]], atoms: list[list[str]]) -> list[list[str]]:
    return [sorted(ch for atom_index in block for ch in atoms[atom_index])
            for block in part]


def adjacent_swap_edges(data: dict) -> list[dict]:
    edges = []
    for positive in data["positive"]:
        for negative in data["negative"]:
            if len(positive) != len(negative):
                continue
            mismatch = [i for i, (left, right) in enumerate(zip(positive, negative))
                        if left != right]
            if len(mismatch) != 2 or mismatch[1] != mismatch[0] + 1:
                continue
            i, j = mismatch
            if positive[i] != positive[j] and positive[i] == negative[j] and positive[j] == negative[i]:
                edges.append({"positive": positive, "negative": negative,
                              "positions": [i, j], "symbols": [positive[i], positive[j]]})
    return edges


def components(alphabet: list[str], edges: list[dict]) -> list[list[str]]:
    parent = {ch: ch for ch in alphabet}

    def find(ch: str) -> str:
        if parent[ch] != ch:
            parent[ch] = find(parent[ch])
        return parent[ch]

    for edge in edges:
        a, b = edge["symbols"]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    groups: dict[str, list[str]] = {}
    for ch in alphabet:
        groups.setdefault(find(ch), []).append(ch)
    return sorted((sorted(group) for group in groups.values()), key=lambda group: group[0])


def stirling_spectrum(atom_count: int, max_k: int) -> dict[str, int]:
    row = [1] + [0] * atom_count
    for n in range(1, atom_count + 1):
        nxt = [0] * (atom_count + 1)
        for k in range(1, n + 1):
            nxt[k] = row[k - 1] + k * row[k]
        row = nxt
    return {str(k): (row[k] if k <= atom_count else 0)
            for k in range(1, max_k + 1)}


def expected_family(case: dict, data: dict, provider_atoms: list[list[str]], edges: list[dict]):
    alphabet = sorted(data["alphabet"])
    cell = case["case_id"]
    if cell in ("m14_seven_pair_atoms", "m64_eight_connected_groups"):
        if provider_atoms != case["expected_atoms"]:
            raise AssertionError(f"{cell}: edge component partition mismatch")
        if len(edges) != case["expected_edge_count"]:
            raise AssertionError(f"{cell}: swap edge count mismatch")
        if not feasible(data, provider_atoms):
            raise AssertionError(f"{cell}: quotient atom partition is not feasible")
        quotient_count = 0
        family = []
        for quotient_part in partitions(list(range(len(provider_atoms)))):
            quotient_count += 1
            lifted = lift_atom_partition(quotient_part, provider_atoms)
            if not feasible(data, lifted):
                raise AssertionError(f"{cell}: a coarsening of feasible atom partition failed")
            family.append(rgs(lifted, alphabet))
        domain = "all quotient partitions; adjacent-swap theorem proves completeness"
        symbol_partitions_enumerated = 0
        atom_partitions_enumerated = quotient_count
    else:
        direct_count = 0
        family = []
        for part in partitions(alphabet):
            direct_count += 1
            if feasible(data, part):
                family.append(rgs(part, alphabet))
        if cell == "m10_graph_empty_five_semantic_pairs":
            semantic_atoms = case["expected_semantic_atoms"]
            if provider_atoms != case["expected_provider_atoms"] or edges:
                raise AssertionError("m10 provider graph should remain empty with singleton graph-atoms")
        else:
            semantic_atoms = case["expected_semantic_atoms"]
            if provider_atoms != case["expected_provider_atoms"] or edges:
                raise AssertionError("long-word input should have no swap edges and singleton graph-atoms")
        quotient = []
        for part in partitions(list(range(len(semantic_atoms)))):
            quotient.append(rgs(lift_atom_partition(part, semantic_atoms), alphabet))
        if set(family) != set(quotient):
            raise AssertionError(f"{cell}: direct full-family result differs from claimed semantic coarsenings")
        domain = "all symbol partitions; compare to claimed semantic-atom coarsenings"
        symbol_partitions_enumerated = direct_count
        atom_partitions_enumerated = len(quotient)

    if len(set(tuple(row) for row in family)) != len(family):
        raise AssertionError(f"{cell}: duplicate canonical RGS partitions")
    family.sort()
    expected_count = case["expected_count"]
    if len(family) != expected_count:
        raise AssertionError(f"{cell}: expected {expected_count} compatible partitions, got {len(family)}")
    spectrum = {str(k): 0 for k in range(1, len(alphabet) + 1)}
    for partition in family:
        spectrum[str(max(partition) + 1)] += 1
    if spectrum != case["expected_spectrum"]:
        raise AssertionError(f"{cell}: exact spectrum differs from preregistered expectation")
    if not family or spectrum[str(case["expected_k_max"])] == 0:
        raise AssertionError(f"{cell}: no partition at expected kmax")

    pair_rows = []
    for i, left in enumerate(alphabet):
        for j in range(i + 1, len(alphabet)):
            right = alphabet[j]
            same = next((part for part in family if part[i] == part[j]), None)
            different = next((part for part in family if part[i] != part[j]), None)
            pair_rows.append({
                "symbols": [left, right],
                "relation": "forced_same" if different is None else "ambiguous",
                "same_partition_count": sum(part[i] == part[j] for part in family),
                "different_partition_count": sum(part[i] != part[j] for part in family),
                "same_witness_rgs": same,
                "different_witness_rgs": different,
            })

    if cell in ("m14_seven_pair_atoms", "m64_eight_connected_groups"):
        atom_map = {symbol: index for index, atom in enumerate(provider_atoms) for symbol in atom}
        if cell == "m14_seven_pair_atoms":
            expected_within, expected_cross = 877, 203
        else:
            expected_within, expected_cross = 4140, 877
        for row in pair_rows:
            same = row["same_partition_count"]
            within = atom_map[row["symbols"][0]] == atom_map[row["symbols"][1]]
            if same != (expected_within if within else expected_cross):
                raise AssertionError(f"{cell}: pair formula mismatch for {row['symbols']}")
    elif cell == "m10_graph_empty_five_semantic_pairs":
        semantic_map = {symbol: index for index, atom in enumerate(case["expected_semantic_atoms"]) for symbol in atom}
        for row in pair_rows:
            within = semantic_map[row["symbols"][0]] == semantic_map[row["symbols"][1]]
            if row["same_partition_count"] != (52 if within else 15):
                raise AssertionError(f"m10: semantic pair formula mismatch for {row['symbols']}")
    else:
        semantic_map = {"a": 0, "b": 0, "c": 1, "d": 2}
        for row in pair_rows:
            within = semantic_map[row["symbols"][0]] == semantic_map[row["symbols"][1]]
            if row["same_partition_count"] != (5 if within else 2):
                raise AssertionError(f"long-word: semantic pair formula mismatch for {row['symbols']}")

    return {
        "case_id": cell,
        "input_sha256": case["input"]["sha256"],
        "canonical_payload_sha256": case["input"]["canonical_payload_sha256"],
        "oracle_status": "accepted_independent_scale_oracle",
        "oracle_domain": domain,
        "symbol_partitions_enumerated": symbol_partitions_enumerated,
        "atom_or_semantic_partitions_enumerated": atom_partitions_enumerated,
        "swap_edges": edges,
        "provider_atoms": provider_atoms,
        "atom_partition_feasible": feasible(data, provider_atoms),
        "compatible_partition_count": len(family),
        "compatible_partition_count_by_k": spectrum,
        "k_max_compatible": max(k for k in range(1, len(alphabet) + 1) if spectrum[str(k)]),
        "compatible_rgs": family,
        "pair_relations": pair_rows,
        "pair_count": len(pair_rows),
    }


manifest_raw = (SCALE / "manifest.json").read_bytes()
manifest = json.loads(manifest_raw.decode("utf-8"))
output = []
for case in manifest["cells"]:
    input_path = SCALE / case["input"]["path"]
    raw = input_path.read_bytes()
    if sha(raw) != case["input"]["sha256"] or len(raw) != case["input"]["bytes"]:
        raise AssertionError(f"frozen scale input hash mismatch: {case['case_id']}")
    data = json.loads(raw.decode("utf-8"))
    alphabet = sorted(data["alphabet"])
    edges = adjacent_swap_edges(data)
    atoms = components(alphabet, edges)
    row = expected_family(case, data, atoms, edges)
    output.append(row)

print(json.dumps({
    "schema_version": 1,
    "status": "accepted_four_cell_independent_scale_oracle",
    "scale_manifest_sha256": sha(manifest_raw),
    "cells": output,
}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

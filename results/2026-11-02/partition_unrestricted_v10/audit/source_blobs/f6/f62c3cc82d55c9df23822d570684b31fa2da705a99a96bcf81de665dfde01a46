#!/usr/bin/env python3
"""Freeze the four preregistered C010 no-K correctness scale inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "scale_v1"
INPUTS = OUT / "inputs"
OUT.mkdir(parents=True, exist_ok=False)
INPUTS.mkdir()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canon(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def write_input(name: str, data: dict) -> dict:
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path = INPUTS / name
    with path.open("xb") as handle:
        handle.write(raw)
    return {"path": f"inputs/{name}", "bytes": len(raw),
            "sha256": sha(raw), "canonical_payload_sha256": sha(canon(data)),
            "alphabet_size": len(data["alphabet"]),
            "positive_count": len(data["positive"]),
            "negative_count": len(data["negative"]),
            "max_word_length": max(map(len, data["positive"] + data["negative"]), default=0)}


def stirling_row(n: int) -> dict[str, int]:
    row = [1] + [0] * n
    for size in range(1, n + 1):
        next_row = [0] * (n + 1)
        for k in range(1, size + 1):
            next_row[k] = row[k - 1] + k * row[k]
        row = next_row
    return {str(k): row[k] for k in range(1, n + 1)}


safe_ascii = [chr(code) for code in range(33, 127) if code not in (34, 92)]
assert len(safe_ascii) >= 64

# Seven disjoint adjacent-swap positive/negative pairs certify seven atoms.
symbols14 = list("ABCDEFGHIJKLMN")
p14 = [symbols14[i] + symbols14[i + 1] for i in range(0, 14, 2)]
n14 = [word[1] + word[0] for word in p14]
data14 = {"alphabet": symbols14, "positive": p14, "negative": n14}

# Eight paths of eight symbols each; each path edge has a replayable swap pair.
symbols64 = safe_ascii[:64]
groups64 = [symbols64[i:i + 8] for i in range(0, 64, 8)]
p64, n64 = [], []
for group in groups64:
    for left, right in zip(group, group[1:]):
        p64.append(left + right)
        n64.append(right + left)
data64 = {"alphabet": symbols64, "positive": p64, "negative": n64}

# Five graph-empty doubled-pair gadgets; each pair is a semantic must-link.
symbols10 = list("abcdefghij")
p10 = ["", "aabb", "ccdd", "eeff", "gghh", "iijj"]
n10 = ["bbaa", "ddcc", "ffee", "hhgg", "jjii"]
data10 = {"alphabet": symbols10, "positive": p10, "negative": n10}

# Long-word split-obstruction control; c,d remain independently mergeable.
data_long = {"alphabet": list("abcd"),
             "positive": ["a" * 2048 + "b" * 2048],
             "negative": ["b" * 2048 + "a" * 2048]}

cases = [
    {
        "case_id": "m14_seven_pair_atoms",
        "input": write_input("m14_seven_pair_atoms.json", data14),
        "oracle_mode": "quotient-enumerate-Bell-7-and-lift; replay 7 swap edges and atom feasibility",
        "expected_atoms": [[symbols14[i], symbols14[i + 1]] for i in range(0, 14, 2)],
        "expected_edge_count": 7,
        "expected_atom_partition_feasible": True,
        "expected_count": 877,
        "expected_spectrum": {**stirling_row(7), **{str(k): 0 for k in range(8, 15)}},
        "expected_k_max": 7,
        "pair_counts": {"within_atom_same": 877, "cross_atom_same": 203},
        "provider_mode": "default counts and witnesses; no full-list output required"
    },
    {
        "case_id": "m64_eight_connected_groups",
        "input": write_input("m64_eight_connected_groups.json", data64),
        "oracle_mode": "quotient-enumerate-Bell-8=4140 atom partitions and lift; never enumerate Bell(64)",
        "expected_atoms": groups64,
        "expected_edge_count": 56,
        "expected_atom_partition_feasible": True,
        "expected_count": 4140,
        "expected_spectrum": {**stirling_row(8), **{str(k): 0 for k in range(9, 65)}},
        "expected_k_max": 8,
        "pair_counts": {"within_atom_same": 4140, "cross_atom_same": 877},
        "provider_mode": "default counts and witnesses; no full-list output required"
    },
    {
        "case_id": "m10_graph_empty_five_semantic_pairs",
        "input": write_input("m10_graph_empty_five_semantic_pairs.json", data10),
        "oracle_mode": "directly enumerate Bell(10)=115975 symbol partitions and replay every feasibility check",
        "expected_semantic_atoms": [[symbols10[i], symbols10[i + 1]] for i in range(0, 10, 2)],
        "expected_provider_atoms": [[symbol] for symbol in symbols10],
        "expected_edge_count": 0,
        "expected_atom_partition_feasible": False,
        "expected_count": 52,
        "expected_spectrum": {**stirling_row(5), **{str(k): 0 for k in range(6, 11)}},
        "expected_k_max": 5,
        "pair_counts": {"within_semantic_atom_same": 52, "cross_semantic_atom_same": 15},
        "provider_mode": "default counts and witnesses; no full-list output required"
    },
    {
        "case_id": "long_word_length_4096_forced_pair",
        "input": write_input("long_word_length_4096_forced_pair.json", data_long),
        "oracle_mode": "directly enumerate Bell(4)=15 symbol partitions and replay every feasibility check",
        "expected_semantic_atoms": [["a", "b"], ["c"], ["d"]],
        "expected_provider_atoms": [["a"], ["b"], ["c"], ["d"]],
        "expected_edge_count": 0,
        "expected_atom_partition_feasible": False,
        "expected_count": 5,
        "expected_spectrum": {**stirling_row(3), "4": 0},
        "expected_k_max": 3,
        "pair_counts": {"within_ab_same": 5, "all_other_pair_same": 2},
        "provider_mode": "default counts and witnesses; no full-list output required"
    }
]

manifest = {
    "schema_version": 1,
    "cycle": "C010",
    "status": "four_scale_inputs_frozen_before_oracle_and_provider_scale_runs",
    "generator": "generate_scale_corpus_v2.py",
    "seed": None,
    "purpose": "correctness-only bounded scale cells; no timing comparison",
    "cells": cases
}
manifest_raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
with (OUT / "manifest.json").open("xb") as handle:
    handle.write(manifest_raw)
print(json.dumps({"status": manifest["status"], "cells": len(cases),
                  "manifest_sha256": sha(manifest_raw),
                  "input_hashes": [row["input"]["sha256"] for row in cases]},
                 ensure_ascii=False, sort_keys=True))

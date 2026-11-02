#!/usr/bin/env python3
"""Freeze five adaptive-only structured scale correctness inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "scale_v1"
PROTOCOL = HERE / "PROTOCOL_SCALE_V1.md"
LONG_LENGTH = 65536


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_case(case_id, sizes, context_repeat=1):
    total = sum(sizes)
    alphabet = [chr(0xE000 + i) for i in range(total)]
    groups = []
    cursor = 0
    for size in sizes:
        groups.append(alphabet[cursor:cursor + size])
        cursor += size
    base = "".join(alphabet) * context_repeat
    edges = []
    negatives = []
    for start, size in zip((sum(sizes[:i]) for i in range(len(sizes))), sizes):
        for offset in range(size - 1):
            position = start + offset
            word = base[:position] + base[position + 1] + base[position] + base[position + 2:]
            edges.append({"symbols": [alphabet[position], alphabet[position + 1]],
                          "negative_index": len(negatives), "position": position})
            negatives.append(word)
    if len(set(negatives)) != len(negatives) or base in negatives:
        raise AssertionError("constructed labels are not distinct")
    if context_repeat > 1 and len(base) != LONG_LENGTH:
        raise AssertionError("long-context length mismatch")
    visible = {"alphabet": alphabet, "positive": [base], "negative": negatives}
    row = {"case_id": case_id, "input": visible}
    hidden = {"case_id": case_id,
              "payload_sha256": hashlib.sha256(json.dumps(visible, ensure_ascii=False,
                  sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
              "expected_finest_partition": groups,
              "base_positive_word": base,
              "swap_edges": edges,
              "generator_kind": "one_positive_with_all_internal_path_adjacent_swap_negatives",
              "intended_block_count": len(groups),
              "context_length": len(base),
              "note": "audit sidecar only; not included in solver input"}
    return row, hidden


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f"refusing to overwrite frozen scale inputs: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [
        ("scale_m64_equal8", [8] * 8, 1),
        ("scale_m64_unequal8", [2, 3, 4, 5, 6, 7, 8, 29], 1),
        ("scale_m128_equal16", [8] * 16, 1),
        ("scale_m256_unequal16", list(range(1, 16)) + [136], 1),
        ("scale_m16_len65536", [4] * 4, LONG_LENGTH // 16),
    ]
    rows, sidecars = [], []
    for case_id, sizes, repeat in specs:
        row, sidecar = make_case(case_id, sizes, repeat)
        rows.append(row)
        sidecars.append(sidecar)
    input_path = OUT / "inputs.jsonl"
    sidecar_path = OUT / "truth_sidecars.jsonl"
    input_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                                     for row in rows), encoding="utf-8", newline="\n")
    sidecar_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                                       for row in sidecars), encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": 1,
        "corpus": "C007_ADAPTIVE_SCALE_CORRECTNESS_V1",
        "cells": [{"case_id": row["case_id"], "alphabet_size": len(row["input"]["alphabet"]),
                   "negative_count": len(row["input"]["negative"]),
                   "context_length": len(row["input"]["positive"][0]),
                   "intended_blocks": len(sidecar["expected_finest_partition"]),
                   "block_sizes": [len(block) for block in sidecar["expected_finest_partition"]]}
                  for row, sidecar in zip(rows, sidecars)],
        "solver_fields": ["alphabet", "positive", "negative"],
        "sidecar_fields_excluded_from_solver": ["expected_finest_partition", "base_positive_word", "swap_edges"],
        "protocol_sha256": sha256(PROTOCOL),
        "generator_sha256": sha256(Path(__file__)),
        "files": {"inputs.jsonl": {"bytes": input_path.stat().st_size, "sha256": sha256(input_path)},
                  "truth_sidecars.jsonl": {"bytes": sidecar_path.stat().st_size,
                                           "sha256": sha256(sidecar_path)}},
        "execution_policy": {"mode": "adaptive", "cooperative_seconds": 28,
                             "capture_hard_seconds": 30, "fresh_serial_processes": True,
                             "reference_at_16_atoms": "excluded"},
        "timing_status": "held_pending_master_go",
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    print(json.dumps({"cell_count": len(rows), "manifest_sha256": sha256(manifest_path),
                      "input_sha256": sha256(input_path), "sidecar_sha256": sha256(sidecar_path),
                      "input_bytes": input_path.stat().st_size}, sort_keys=True))


if __name__ == "__main__":
    main()

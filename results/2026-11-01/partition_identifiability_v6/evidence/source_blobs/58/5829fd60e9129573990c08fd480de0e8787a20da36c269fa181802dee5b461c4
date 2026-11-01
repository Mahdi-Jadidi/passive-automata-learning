"""Freeze the two primary C006 performance proposal inputs and truth checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "benchmark_v1"


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def accepts(grammar, word):
    kind = grammar["kind"]
    if kind == "fixed_prefix_center_leaf_pairs_star":
        prefix, center, leaves = grammar["prefix"], grammar["center"], set(grammar["leaves"])
        if not word.startswith(prefix):
            return False
        tail = word[len(prefix):]
        return len(tail) % 2 == 0 and all(
            tail[i] == center and tail[i + 1] in leaves for i in range(0, len(tail), 2))
    if kind == "finite_words_union_unary_tail":
        return word in set(grammar["finite_words"]) or (
            len(word) >= grammar["tail_min_length"] and
            all(symbol == grammar["tail_symbol"] for symbol in word))
    if kind == "unary_star":
        return all(symbol == grammar["symbol"] for symbol in word)
    raise ValueError(kind)


def projection(word, block):
    block = set(block)
    return "".join(symbol for symbol in word if symbol in block)


def expected_full_cover(data):
    alphabet = sorted(data["alphabet"])
    positives, negatives = sorted(set(data["positive"])), sorted(set(data["negative"]))
    count = (1 << (len(alphabet) - 1)) - 1
    rows = []
    for tail in range(count):
        mask = (tail << 1) | 1
        left = [symbol for i, symbol in enumerate(alphabet) if (mask >> i) & 1]
        right = [symbol for i, symbol in enumerate(alphabet) if not ((mask >> i) & 1)]
        blocks = [left, right]
        collision = None
        for negative in negatives:
            matches = []
            for block in blocks:
                target = projection(negative, block)
                match = next((p for p in positives if projection(p, block) == target), None)
                if match is None:
                    break
                matches.append(match)
            if len(matches) == 2:
                collision = {"negative": negative, "matching_positive_by_side": matches}
                break
        if collision is None:
            raise AssertionError(f"small target has a compatible cut at mask {mask}")
        rows.append({"canonical_left_atom_mask": mask, "collision": collision})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir()

    manager = json.loads((ROOT / "implementation" / "example_manager_candidate_v1.json")
                        .read_text(encoding="utf-8"))
    small_data = {"alphabet": sorted(manager["alphabet"]),
                  "positive": sorted(set(manager["positive"])),
                  "negative": sorted(set(manager["negative"]))}
    assert small_data == {"alphabet": list("abcd"),
                          "positive": ["acdb", "bcda", "cabd", "dabc"],
                          "negative": ["abcd"]}

    alphabet = [chr(0x4E00 + i) for i in range(64)]
    center, leaves = alphabet[0], alphabet[1:]
    prefix = center * 128
    large_data = {"alphabet": alphabet,
                  "positive": sorted([prefix] + [prefix + center + leaf for leaf in leaves]),
                  "negative": [prefix + center]}

    optional_data = {"alphabet": alphabet, "positive": [center], "negative": []}
    cells = [
        ("large_connected_m64", large_data,
         {"factor_count": 1, "blocks": [alphabet],
          "grammar": {"kind": "fixed_prefix_center_leaf_pairs_star", "prefix": prefix,
                      "center": center, "leaves": leaves, "infinite": True,
                      "notation": "c^128 (cY)*"}},
         {"expected_status": "not_decomposable", "obstruction": "connected_must_link_graph",
          "expected_edge_pairs": [sorted([center, leaf]) for leaf in leaves],
          "expected_edge_count": 63, "expected_component_count": 1,
          "expected_cut_record_count": 0}),
        ("small_full_cover_m4", small_data,
         {"factor_count": 1, "blocks": [small_data["alphabet"]],
          "grammar": {"kind": "finite_words_union_unary_tail",
                      "finite_words": small_data["positive"], "tail_symbol": "a",
                      "tail_min_length": 5, "infinite": True,
                      "notation": "{acdb,bcda,cabd,dabc} union a^5 a*"}},
         {"expected_status": "not_decomposable", "obstruction": "complete_cut_collision_cover",
          "expected_graph_edge_count": 0,
          "expected_cut_rejections": expected_full_cover(small_data)}),
        ("optional_decomposable_m64", optional_data,
         {"factor_count": 1, "blocks": [alphabet],
          "grammar": {"kind": "unary_star", "symbol": center, "infinite": True,
                      "notation": "c*"}},
         {"expected_status": "found", "complete": False, "decision_complete": True,
          "mode": "decision; one witness only"}),
    ]

    visible_rows, truth_rows, expected_rows, cell_manifest = [], [], [], []
    for case_id, data, truth, expected in cells:
        assert set(data) == {"alphabet", "positive", "negative"}
        assert len(data["alphabet"]) == len(set(data["alphabet"]))
        assert all(isinstance(symbol, str) and len(symbol) == 1 for symbol in data["alphabet"])
        assert not (set(data["positive"]) & set(data["negative"]))
        assert all(set(word) <= set(data["alphabet"])
                   for word in data["positive"] + data["negative"])
        grammar = truth["grammar"]
        assert all(accepts(grammar, word) for word in data["positive"]), case_id
        assert all(not accepts(grammar, word) for word in data["negative"]), case_id
        input_raw = canonical_bytes(data)
        input_path = inputs_dir / f"{case_id}.json"
        input_path.write_bytes(input_raw)
        visible_rows.append({"case_id": case_id, "input": data})
        truth_rows.append({"case_id": case_id, **truth})
        expected_rows.append({"case_id": case_id, **expected})
        cell_manifest.append({
            "case_id": case_id,
            "optional": case_id.startswith("optional_"),
            "input_path": str(input_path.relative_to(AUDIT)),
            "input_sha256": digest(input_raw),
            "alphabet_size": len(data["alphabet"]),
            "positive_count": len(data["positive"]),
            "negative_count": len(data["negative"]),
            "max_word_length": max(map(len, data["positive"] + data["negative"]), default=0),
            "expected_status": expected["expected_status"],
            "expected_obstruction": expected.get("obstruction")
        })

    visible_raw = b"".join(canonical_bytes(row) for row in visible_rows)
    truth_raw = b"".join(canonical_bytes(row) for row in truth_rows)
    expected_raw = b"".join(canonical_bytes(row) for row in expected_rows)
    (OUT / "inputs.jsonl").write_bytes(visible_raw)
    (OUT / "truth_sidecars.jsonl").write_bytes(truth_raw)
    (OUT / "expected_obstructions.jsonl").write_bytes(expected_raw)

    protocol_path = AUDIT / "PROTOCOL_BENCHMARK_V2.md"
    manifest = {
        "schema": "C006_benchmark_freeze_v1",
        "freeze_status": "frozen_inputs_and_targets; provider_runs_not_authorized_here",
        "generator": "audit/freeze_benchmark_v1.py",
        "generator_sha256": digest(Path(__file__).read_bytes()),
        "protocol": str(protocol_path.relative_to(ROOT)),
        "protocol_sha256": digest(protocol_path.read_bytes()),
        "provider_sha256": digest((ROOT / "implementation" / "solver_v5.py").read_bytes()),
        "cli_sha256": digest((ROOT / "implementation" / "cli_v4.py").read_bytes()),
        "root_wrapper_sha256": digest((ROOT / "solver.py").read_bytes()),
        "parent_helper_sha256": digest((ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5"
                                       / "general" / "known_k_qexact_v2.py").read_bytes()),
        "primary_jobs": 6,
        "primary_repetitions": 3,
        "optional_jobs": 3,
        "optional_authorized": False,
        "inputs_sha256": digest(visible_raw),
        "truth_sidecars_sha256": digest(truth_raw),
        "expected_obstructions_sha256": digest(expected_raw),
        "records": len(visible_rows),
        "cells": cell_manifest,
        "provider_input_policy": "only nested alphabet/positive/negative records are supplied to solver; no k or q"
    }
    manifest_raw = canonical_bytes(manifest)
    (OUT / "manifest.json").write_bytes(manifest_raw)
    print(json.dumps({"scientific_status": "passed_pre-freeze_grammar_membership",
                      "execution_status": "success", "manifest": manifest,
                      "manifest_sha256": digest(manifest_raw)},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

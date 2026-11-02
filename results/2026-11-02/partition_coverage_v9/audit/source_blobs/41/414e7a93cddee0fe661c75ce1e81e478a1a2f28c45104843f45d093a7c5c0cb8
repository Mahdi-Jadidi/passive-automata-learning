#!/usr/bin/env python3
"""Independent exact scale oracle: quotient partitions for pair atoms, direct partitions for long word."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCALE_DIR = ROOT / "scale_v1"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def set_insert_partitions(items: list[object]) -> list[list[list[object]]]:
    if not items:
        return [[]]
    head, *tail = items
    output = []
    for partition in set_insert_partitions(tail):
        for index in range(len(partition)):
            candidate = [block.copy() for block in partition]
            candidate[index].append(head)
            output.append(candidate)
        output.append([[head], *[block.copy() for block in partition]])
    return output


def blocks_to_rgs(blocks: list[list[str]], alphabet: list[str]) -> tuple[int, ...]:
    owner = {symbol: block_index for block_index, block in enumerate(blocks) for symbol in block}
    names: dict[int, int] = {}
    result = []
    for symbol in alphabet:
        raw = owner[symbol]
        names.setdefault(raw, len(names))
        result.append(names[raw])
    return tuple(result)


def rgs_to_blocks(rgs: tuple[int, ...], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(blocks) <= label:
            blocks.append([])
        blocks[label].append(symbol)
    return blocks


def project(word: str, block: set[str]) -> str:
    return "".join(letter for letter in word if letter in block)


def feasible(data: dict, blocks: list[list[str]]) -> bool:
    allowed = set(data.get("allowed_k", range(1, len(data["alphabet"]) + 1)))
    if len(blocks) not in allowed:
        return False
    local_positive = [{project(p, set(block)) for p in data["positive"]} for block in blocks]
    return all(any(project(n, set(block)) not in language
                   for block, language in zip(blocks, local_positive))
               for n in data["negative"])


def stirling_second(n: int, k: int) -> int:
    table = [[0] * (k + 1) for _ in range(n + 1)]
    table[0][0] = 1
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            table[i][j] = table[i - 1][j - 1] + j * table[i - 1][j]
    return table[n][k]


def all_expected(data: dict, kind: str) -> set[tuple[int, ...]]:
    alphabet = sorted(data["alphabet"])
    allowed = set(data.get("allowed_k", range(1, len(alphabet) + 1)))
    if kind == "proved_pair_atom_coarsening_family":
        atoms = [alphabet[i:i + 2] for i in range(0, len(alphabet), 2)]
        found = set()
        for atom_partition in set_insert_partitions(list(range(len(atoms)))):
            if len(atom_partition) not in allowed:
                continue
            expanded = [[symbol for atom_index in atom_block for symbol in atoms[atom_index]]
                        for atom_block in atom_partition]
            if feasible(data, expanded):
                found.add(blocks_to_rgs(expanded, alphabet))
        return found
    if kind == "proved_adjacent_swap_long_word":
        found = set()
        for blocks in set_insert_partitions(alphabet):
            if feasible(data, blocks):
                found.add(blocks_to_rgs(blocks, alphabet))
        return found
    raise ValueError(f"unknown scale case family: {kind}")


def make_result(case: dict, data: dict) -> dict:
    alphabet = sorted(data["alphabet"])
    rgs_set = all_expected(data, case["origin"])
    rgs_rows = sorted(rgs_set)
    k_hist: dict[str, int] = {}
    for rgs in rgs_rows:
        k = max(rgs) + 1
        k_hist[str(k)] = k_hist.get(str(k), 0) + 1
    pairs = []
    for i in range(len(alphabet)):
        for j in range(i + 1, len(alphabet)):
            same = [rgs for rgs in rgs_rows if rgs[i] == rgs[j]]
            different = [rgs for rgs in rgs_rows if rgs[i] != rgs[j]]
            if not rgs_rows:
                relation = "model_inconsistent"
            elif len(same) == len(rgs_rows):
                relation = "forced_same"
            elif not same:
                relation = "forced_different"
            else:
                relation = "ambiguous"
            pairs.append({
                "symbols": [alphabet[i], alphabet[j]],
                "relation": relation,
                "coown_count": len(same),
                "different_count": len(different),
                "same_witness_rgs": list(same[0]) if same else None,
                "same_witness_blocks": rgs_to_blocks(same[0], alphabet) if same else None,
                "different_witness_rgs": list(different[0]) if different else None,
                "different_witness_blocks": rgs_to_blocks(different[0], alphabet) if different else None,
            })
    raw = (SCALE_DIR / case["path"]).read_bytes()
    return {
        "case_id": case["case_id"],
        "input_sha256": sha(raw),
        "alphabet": alphabet,
        "allowed_k": data.get("allowed_k", list(range(1, len(alphabet) + 1))),
        "origin": case["origin"],
        "complete": True,
        "status": "model_inconsistent" if not rgs_rows else ("unique_partition" if len(rgs_rows) == 1 else "multiple_partitions"),
        "partition_count": len(rgs_rows),
        "k_histogram": k_hist,
        "compatible_rgs": [list(rgs) for rgs in rgs_rows],
        "compatible_partitions": [rgs_to_blocks(rgs, alphabet) for rgs in rgs_rows],
        "pair_relations": pairs,
        "independent_method": "set insertion on quotient atoms plus direct projection test; long-word control enumerates all symbol set partitions",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=SCALE_DIR / "manifest.json")
    parser.add_argument("--output", type=Path, default=SCALE_DIR / "oracle_v1.jsonl")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = []
    for case in manifest["cases"]:
        raw = (args.manifest.parent / case["path"]).read_bytes()
        if sha(raw) != case["input_sha256"]:
            raise SystemExit(f"input hash mismatch: {case['case_id']}")
        data = json.loads(raw.decode("utf-8"))
        result = make_result(case, data)
        if result["partition_count"] != case["expected_partition_count"]:
            raise AssertionError(f"analytic expected count mismatch: {case['case_id']}")
        if case["origin"] == "proved_pair_atom_coarsening_family":
            r = case["atom_count"]
            allowed = case["allowed_k"]
            expected_total = sum(stirling_second(r, k) for k in allowed)
            expected_cross = sum(stirling_second(r - 1, k) for k in allowed)
            if result["partition_count"] != expected_total:
                raise AssertionError(f"Stirling total mismatch: {case['case_id']}")
            for pair in result["pair_relations"]:
                ia = data["alphabet"].index(pair["symbols"][0]) // 2
                ja = data["alphabet"].index(pair["symbols"][1]) // 2
                if ia == ja:
                    expected_coown = expected_total
                else:
                    expected_coown = expected_cross
                if pair["coown_count"] != expected_coown:
                    raise AssertionError(f"Stirling pair count mismatch: {case['case_id']} {pair['symbols']}")
        results.append(result)
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite scale oracle: {args.output}")
    raw_output = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in results).encode("utf-8")
    args.output.write_bytes(raw_output)
    print(json.dumps({"status": "accepted_exact_scale_oracle", "cases": len(results),
                      "partition_counts": {row["case_id"]: row["partition_count"] for row in results},
                      "oracle_sha256": sha(raw_output), "oracle_bytes": len(raw_output)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

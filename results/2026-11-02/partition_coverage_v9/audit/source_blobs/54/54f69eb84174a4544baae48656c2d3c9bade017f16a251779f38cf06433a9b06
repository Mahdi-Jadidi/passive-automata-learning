#!/usr/bin/env python3
"""Direct RGS enumeration and projection-feasibility oracle for C009; no provider DP."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def enumerate_rgs(m: int):
    if m < 1:
        return
    def rec(prefix: list[int], max_label: int):
        if len(prefix) == m:
            yield tuple(prefix)
            return
        for label in range(max_label + 2):
            prefix.append(label)
            yield from rec(prefix, max(max_label, label))
            prefix.pop()
    yield from rec([0], 0)


def blocks_from_rgs(rgs: tuple[int, ...] | list[int], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(blocks) <= label:
            blocks.append([])
        blocks[label].append(symbol)
    return blocks


def project(word: str, block: set[str]) -> str:
    return "".join(symbol for symbol in word if symbol in block)


def valid_partition(data: dict, rgs: tuple[int, ...]) -> bool:
    alphabet = data["alphabet"]
    blocks = blocks_from_rgs(rgs, alphabet)
    allowed_k = data.get("allowed_k", list(range(1, len(alphabet) + 1)))
    if len(blocks) not in allowed_k:
        return False
    positive = data["positive"]
    negative = data["negative"]
    projection_sets = [
        {project(word, set(block)) for word in positive}
        for block in blocks
    ]
    for word in negative:
        if not any(project(word, set(block)) not in seen for block, seen in zip(blocks, projection_sets)):
            return False
    return True


def validate_input(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError("input_not_object")
    alphabet = data.get("alphabet")
    if not isinstance(alphabet, list) or not alphabet:
        raise ValueError("empty_or_missing_alphabet")
    if any(not isinstance(x, str) or not x for x in alphabet) or len(set(alphabet)) != len(alphabet):
        raise ValueError("invalid_or_duplicate_alphabet_symbol")
    for key in ("positive", "negative"):
        words = data.get(key)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(f"invalid_{key}_list")
        if len(set(words)) != len(words):
            raise ValueError(f"duplicate_{key}_word")
        if any(any(symbol not in alphabet for symbol in word) for word in words):
            raise ValueError(f"{key}_word_outside_alphabet")
    if set(data["positive"]) & set(data["negative"]):
        raise ValueError("conflicting_labels")
    if "allowed_k" in data:
        allowed = data["allowed_k"]
        if not isinstance(allowed, list) or not allowed:
            raise ValueError("allowed_k_must_be_nonempty_list")
        if any(type(k) is not int or k < 1 or k > len(alphabet) for k in allowed):
            raise ValueError("allowed_k_out_of_range")
        if len(set(allowed)) != len(allowed):
            raise ValueError("duplicate_allowed_k")


def output_case(case_id: str, data: dict) -> dict:
    validate_input(data)
    alphabet = data["alphabet"]
    allowed_k = data.get("allowed_k", list(range(1, len(alphabet) + 1)))
    compatible: list[tuple[int, ...]] = []
    for rgs in enumerate_rgs(len(alphabet)):
        if valid_partition(data, rgs):
            compatible.append(rgs)

    k_histogram: dict[str, int] = {}
    for rgs in compatible:
        k = max(rgs) + 1
        k_histogram[str(k)] = k_histogram.get(str(k), 0) + 1
    pair_rows = []
    for i in range(len(alphabet)):
        for j in range(i + 1, len(alphabet)):
            same_witness = next((r for r in compatible if r[i] == r[j]), None)
            different_witness = next((r for r in compatible if r[i] != r[j]), None)
            same_count = sum(r[i] == r[j] for r in compatible)
            if not compatible:
                relation = "model_inconsistent"
            elif same_count == len(compatible):
                relation = "forced_same"
            elif same_count == 0:
                relation = "forced_different"
            else:
                relation = "ambiguous"
            pair_rows.append({
                "symbols": [alphabet[i], alphabet[j]],
                "relation": relation,
                "compatible_partition_count": len(compatible),
                "coown_count": same_count,
                "different_count": len(compatible) - same_count,
                "same_witness_rgs": list(same_witness) if same_witness is not None else None,
                "same_witness_blocks": blocks_from_rgs(same_witness, alphabet) if same_witness is not None else None,
                "different_witness_rgs": list(different_witness) if different_witness is not None else None,
                "different_witness_blocks": blocks_from_rgs(different_witness, alphabet) if different_witness is not None else None,
            })

    # Separate witness replay: do not trust the relation/counts just constructed.
    for row in pair_rows:
        for key in ("same", "different"):
            witness = row[f"{key}_witness_rgs"]
            if witness is None:
                continue
            if not valid_partition(data, tuple(witness)):
                raise AssertionError(f"invalid {key} pair witness {case_id} {row['symbols']}")
            i = alphabet.index(row["symbols"][0])
            j = alphabet.index(row["symbols"][1])
            condition = witness[i] == witness[j]
            if condition != (key == "same"):
                raise AssertionError(f"wrong {key} pair witness {case_id} {row['symbols']}")
    replayed_count = sum(valid_partition(data, tuple(rgs)) for rgs in compatible)
    if replayed_count != len(compatible):
        raise AssertionError(f"full-set replay mismatch {case_id}")

    return {
        "case_id": case_id,
        "input_sha256": sha(canonical_bytes(data)),
        "alphabet": alphabet,
        "allowed_k": allowed_k,
        "positive_count": len(data["positive"]),
        "negative_count": len(data["negative"]),
        "status": "model_inconsistent" if not compatible else ("unique_partition" if len(compatible) == 1 else "multiple_partitions"),
        "complete": True,
        "partition_count": len(compatible),
        "k_histogram": k_histogram,
        "compatible_rgs": [list(rgs) for rgs in compatible],
        "compatible_partitions": [blocks_from_rgs(rgs, alphabet) for rgs in compatible],
        "pair_relations": pair_rows,
        "pair_witnesses_replayed": True,
        "full_set_witness_replay_count": len(compatible),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = []
    for row in manifest["valid_cases"]:
        input_path = args.manifest.parent / row["path"]
        raw = input_path.read_bytes()
        if sha(raw) != row["input_sha256"]:
            raise SystemExit(f"input hash mismatch: {row['case_id']}")
        data = json.loads(raw.decode("utf-8"))
        results.append(output_case(row["case_id"], data))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite oracle output: {args.output}")
    text = "".join(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n" for result in results)
    args.output.write_text(text, encoding="utf-8", newline="\n")
    raw_out = args.output.read_bytes()
    summary = {
        "status": "accepted_independent_exact_oracle",
        "method": "direct canonical RGS enumeration + projection feasibility; no provider DP",
        "valid_cases": len(results),
        "cases_with_zero_partitions": sum(row["partition_count"] == 0 for row in results),
        "cases_with_unique_partition": sum(row["partition_count"] == 1 for row in results),
        "cases_with_multiple_partitions": sum(row["partition_count"] > 1 for row in results),
        "all_pair_witnesses_replayed": all(row["pair_witnesses_replayed"] for row in results),
        "total_partition_rows": sum(row["partition_count"] for row in results),
        "output_path": str(args.output),
        "output_sha256": sha(raw_out),
        "output_bytes": len(raw_out),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Direct unrestricted RGS enumerator and projection-feasibility oracle for C010."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def enumerate_rgs(m: int):
    if m < 1:
        return
    def rec(prefix: list[int], maximum: int):
        if len(prefix) == m:
            yield tuple(prefix)
            return
        for label in range(maximum + 2):
            prefix.append(label)
            yield from rec(prefix, max(maximum, label))
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


def validate_input(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError("input_not_object")
    if set(data) - {"alphabet", "positive", "negative"}:
        raise ValueError("no_K_or_other_extra_fields_allowed")
    alphabet = data.get("alphabet")
    if not isinstance(alphabet, list) or not alphabet:
        raise ValueError("empty_or_missing_alphabet")
    if any(not isinstance(x, str) or len(x) != 1 for x in alphabet) or len(set(alphabet)) != len(alphabet):
        raise ValueError("invalid_or_duplicate_alphabet_symbol")
    for key in ("positive", "negative"):
        words = data.get(key)
        if not isinstance(words, list) or any(not isinstance(word, str) for word in words):
            raise ValueError(f"invalid_{key}_list")
        if len(set(words)) != len(words):
            raise ValueError(f"duplicate_{key}_word")
        if any(any(symbol not in alphabet for symbol in word) for word in words):
            raise ValueError(f"{key}_word_outside_alphabet")
    if set(data["positive"]) & set(data["negative"]):
        raise ValueError("conflicting_labels")


def feasible(data: dict, blocks: list[list[str]]) -> bool:
    local_positive = [{project(word, set(block)) for word in data["positive"]} for block in blocks]
    return all(any(project(word, set(block)) not in accepted
                   for block, accepted in zip(blocks, local_positive))
               for word in data["negative"])


def make_result(case: dict, data: dict) -> dict:
    validate_input(data)
    alphabet = data["alphabet"]
    compatible = [rgs for rgs in enumerate_rgs(len(alphabet)) if feasible(data, blocks_from_rgs(rgs, alphabet))]
    if not compatible:
        raise AssertionError(f"valid unrestricted input unexpectedly has empty model: {case['case_id']}")
    histogram = {str(k): sum(max(rgs) + 1 == k for rgs in compatible) for k in range(1, len(alphabet) + 1)}
    pair_rows = []
    for i in range(len(alphabet)):
        for j in range(i + 1, len(alphabet)):
            same = [rgs for rgs in compatible if rgs[i] == rgs[j]]
            different = [rgs for rgs in compatible if rgs[i] != rgs[j]]
            if not same:
                raise AssertionError(f"unrestricted coarsening theorem violated: {case['case_id']} {alphabet[i]}{alphabet[j]}")
            relation = "forced_same" if len(same) == len(compatible) else "ambiguous"
            if relation == "forced_different":
                raise AssertionError("forced_different is impossible for unrestricted consistent inputs")
            pair_rows.append({
                "symbols": [alphabet[i], alphabet[j]],
                "relation": relation,
                "compatible_partition_count": len(compatible),
                "coown_count": len(same),
                "different_count": len(different),
                "same_witness_rgs": list(same[0]),
                "same_witness_blocks": blocks_from_rgs(same[0], alphabet),
                "different_witness_rgs": list(different[0]) if different else None,
                "different_witness_blocks": blocks_from_rgs(different[0], alphabet) if different else None,
            })
    # Independently replay each displayed pair witness using projection feasibility.
    for row in pair_rows:
        i, j = (alphabet.index(symbol) for symbol in row["symbols"])
        for side, equals in (("same", True), ("different", False)):
            witness = row[f"{side}_witness_rgs"]
            if witness is None:
                if side == "same" or row["relation"] != "forced_same":
                    raise AssertionError(f"missing required {side} witness {case['case_id']}")
                continue
            if tuple(witness) not in compatible or not feasible(data, blocks_from_rgs(witness, alphabet)):
                raise AssertionError(f"invalid {side} witness {case['case_id']}")
            if (witness[i] == witness[j]) is not equals:
                raise AssertionError(f"wrong {side} witness relation {case['case_id']}")
    status = "one_block_only" if len(compatible) == 1 else "multiple_compatible_partitions"
    if len(compatible) == 1 and compatible[0] != tuple(0 for _ in alphabet):
        raise AssertionError("unrestricted singleton must be the one-block partition")
    return {
        "case_id": case["case_id"],
        "input_sha256": sha(canonical(data)),
        "alphabet": alphabet,
        "positive_count": len(data["positive"]),
        "negative_count": len(data["negative"]),
        "complete": True,
        "status": status,
        "partition_count": len(compatible),
        "kmax": max(max(rgs) + 1 for rgs in compatible),
        "partition_count_by_k": histogram,
        "compatible_rgs": [list(rgs) for rgs in compatible],
        "compatible_partitions": [blocks_from_rgs(rgs, alphabet) for rgs in compatible],
        "pair_relations": pair_rows,
        "pair_witnesses_replayed": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = []
    for case in manifest["valid_cases"]:
        path = args.manifest.parent / case["path"]
        raw = path.read_bytes()
        if sha(raw) != case["input_sha256"]:
            raise SystemExit(f"input hash mismatch: {case['case_id']}")
        data = json.loads(raw.decode("utf-8"))
        results.append(make_result(case, data))
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite unrestricted oracle: {args.output}")
    raw_out = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in results).encode("utf-8")
    with args.output.open("xb") as handle:
        handle.write(raw_out)
    print(json.dumps({
        "status": "accepted_unrestricted_direct_rgs_oracle",
        "method": "complete canonical-RGS enumeration plus direct projection feasibility; no provider DP or K",
        "valid_cases": len(results),
        "total_compatible_partition_rows": sum(row["partition_count"] for row in results),
        "one_block_only_cases": sum(row["status"] == "one_block_only" for row in results),
        "all_pair_witnesses_replayed": all(row["pair_witnesses_replayed"] for row in results),
        "output_sha256": sha(raw_out),
        "output_bytes": len(raw_out),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

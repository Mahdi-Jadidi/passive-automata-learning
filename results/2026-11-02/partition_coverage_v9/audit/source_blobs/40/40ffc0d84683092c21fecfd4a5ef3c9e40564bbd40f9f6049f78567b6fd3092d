#!/usr/bin/env python3
"""Independent Stage-A audit: set-insertion enumeration, corpus and witness checks."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus_v1"
MANIFEST_PATH = CORPUS / "manifest.json"
ORACLE_PATH = ROOT / "oracle_v1.jsonl"
REPORT_PATH = ROOT / "stage_a_validation_v1.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canon(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def set_insert_partitions(symbols: list[str]) -> list[list[list[str]]]:
    """Generate set partitions by inserting each symbol into existing/new blocks."""
    if not symbols:
        return [[]]
    head, *tail = symbols
    result: list[list[list[str]]] = []
    for partition in set_insert_partitions(tail):
        for index in range(len(partition)):
            candidate = [block.copy() for block in partition]
            candidate[index].append(head)
            result.append(candidate)
        result.append([[head], *[block.copy() for block in partition]])
    return result


def canonical_rgs(partition: list[list[str]], alphabet: list[str]) -> tuple[int, ...]:
    owner = {symbol: index for index, block in enumerate(partition) for symbol in block}
    labels: dict[int, int] = {}
    next_label = 0
    result = []
    for symbol in alphabet:
        raw = owner[symbol]
        if raw not in labels:
            labels[raw] = next_label
            next_label += 1
        result.append(labels[raw])
    return tuple(result)


def project(word: str, block: set[str]) -> str:
    return "".join(letter for letter in word if letter in block)


def feasible(data: dict, blocks: list[list[str]]) -> bool:
    allowed = data.get("allowed_k", list(range(1, len(data["alphabet"]) + 1)))
    if len(blocks) not in allowed:
        return False
    positives = data["positive"]
    local_positive = [
        {project(word, set(block)) for word in positives}
        for block in blocks
    ]
    return all(
        any(project(word, set(block)) not in accepted
            for block, accepted in zip(blocks, local_positive))
        for word in data["negative"]
    )


def expected_rgs(data: dict) -> set[tuple[int, ...]]:
    alphabet = data["alphabet"]
    rows = set_insert_partitions(alphabet)
    if len(rows) != bell(len(alphabet)):
        raise AssertionError(f"set-insertion enumerator count mismatch m={len(alphabet)}")
    canonical = [canonical_rgs(blocks, alphabet) for blocks in rows]
    if len(set(canonical)) != len(rows):
        raise AssertionError(f"set-insertion enumerator produced duplicate partitions m={len(alphabet)}")
    return {
        canonical_rgs(blocks, alphabet)
        for blocks in rows
        if feasible(data, blocks)
    }


def bell(n: int) -> int:
    triangle = [[0] * (n + 1) for _ in range(n + 1)]
    triangle[0][0] = 1
    for row in range(1, n + 1):
        triangle[row][0] = triangle[row - 1][row - 1]
        for col in range(1, row + 1):
            triangle[row][col] = triangle[row][col - 1] + triangle[row - 1][col - 1]
    return triangle[n][0]


def rgs_blocks(rgs: tuple[int, ...] | list[int], alphabet: list[str]) -> list[list[str]]:
    labels: list[list[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(labels) <= label:
            labels.append([])
        labels[label].append(symbol)
    return labels


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest_raw = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    checked_files = 0
    for row in manifest["files"]:
        raw = (CORPUS / row["path"]).read_bytes()
        require(sha(raw) == row["sha256"], f"frozen corpus hash mismatch: {row['path']}")
        require(len(raw) == row["bytes"], f"frozen corpus byte-count mismatch: {row['path']}")
        checked_files += 1

    random_rows = [row for row in manifest["valid_cases"] if row["origin"] == "seeded_random_no_hidden_partition"]
    require(len(random_rows) == 120, "must have 120 random cases")
    require(len({row["payload_sha256"] for row in random_rows}) == 120, "random payloads are not unique")
    require({int(m): n for m, n in manifest["random_alphabet_sizes"].items()} == {m: 20 for m in range(2, 8)}, "wrong random m distribution")
    for row in random_rows:
        require(2 <= row["alphabet_size"] <= 7, f"random m out of range: {row['case_id']}")
        data = json.loads((CORPUS / row["path"]).read_text(encoding="utf-8"))
        require(sha(canon(data)) == row["payload_sha256"], f"payload hash mismatch: {row['case_id']}")
        alphabet = data["alphabet"]
        require(all(len(word) <= 5 and all(letter in alphabet for letter in word)
                    for word in data["positive"] + data["negative"]), f"word bound/alphabet failure: {row['case_id']}")
        require(not set(data["positive"]) & set(data["negative"]), f"conflicting labels: {row['case_id']}")
        if "allowed_k" in data:
            require(data["allowed_k"] and len(set(data["allowed_k"])) == len(data["allowed_k"]), f"bad K: {row['case_id']}")
            require(all(type(k) is int and 1 <= k <= len(alphabet) for k in data["allowed_k"]), f"K out of range: {row['case_id']}")

    oracle_rows = [json.loads(line) for line in ORACLE_PATH.read_text(encoding="utf-8").splitlines()]
    require(len(oracle_rows) == len(manifest["valid_cases"]) == 129, "oracle/corpus row count mismatch")
    by_id = {row["case_id"]: row for row in oracle_rows}
    require(len(by_id) == len(oracle_rows), "duplicate oracle case id")
    matched = 0
    witness_count = 0
    total_feasible = 0
    for case in manifest["valid_cases"]:
        result = by_id[case["case_id"]]
        raw = (CORPUS / case["path"]).read_bytes()
        data = json.loads(raw.decode("utf-8"))
        require(result["input_sha256"] == sha(canon(data)), f"oracle input hash mismatch: {case['case_id']}")
        wanted = expected_rgs(data)
        actual = {tuple(rgs) for rgs in result["compatible_rgs"]}
        require(len(actual) == len(result["compatible_rgs"]), f"duplicate partition row: {case['case_id']}")
        require(actual == wanted, f"complete feasible set mismatch: {case['case_id']}")
        actual_blocks = result["compatible_partitions"]
        require(len(actual_blocks) == len(result["compatible_rgs"]), f"partition/block row count mismatch: {case['case_id']}")
        for rgs, blocks in zip(result["compatible_rgs"], actual_blocks):
            require(blocks == rgs_blocks(rgs, data["alphabet"]), f"partition block rendering mismatch: {case['case_id']}")
        require(result["partition_count"] == len(wanted), f"partition count mismatch: {case['case_id']}")
        require(result["complete"] is True, f"oracle not complete: {case['case_id']}")
        expected_status = "model_inconsistent" if not wanted else ("unique_partition" if len(wanted) == 1 else "multiple_partitions")
        require(result["status"] == expected_status, f"status mismatch: {case['case_id']}")
        total_feasible += len(wanted)
        alphabet = data["alphabet"]
        require(len(result["pair_relations"]) == len(alphabet) * (len(alphabet) - 1) // 2,
                f"pair relation row count mismatch: {case['case_id']}")
        seen_pairs: set[tuple[str, str]] = set()
        for pair in result["pair_relations"]:
            pair_key = tuple(pair["symbols"])
            require(pair_key not in seen_pairs and pair_key[0] in alphabet and pair_key[1] in alphabet and pair_key[0] != pair_key[1],
                    f"invalid/duplicate pair relation: {case['case_id']} {pair_key}")
            seen_pairs.add(pair_key)
            i, j = (alphabet.index(symbol) for symbol in pair["symbols"])
            same_count = sum(rgs[i] == rgs[j] for rgs in wanted)
            require(pair["coown_count"] == same_count, f"pair count mismatch {case['case_id']} {pair['symbols']}")
            require(pair["different_count"] == len(wanted) - same_count, f"pair diff count mismatch {case['case_id']} {pair['symbols']}")
            if not wanted:
                relation = "model_inconsistent"
            elif same_count == len(wanted):
                relation = "forced_same"
            elif same_count == 0:
                relation = "forced_different"
            else:
                relation = "ambiguous"
            require(pair["relation"] == relation, f"pair relation mismatch {case['case_id']} {pair['symbols']}")
            for side, same in (("same", True), ("different", False)):
                witness = pair[f"{side}_witness_rgs"]
                if witness is None:
                    absent_side_count = same_count if same else len(wanted) - same_count
                    require(not wanted or absent_side_count == 0, f"missing pair witness {case['case_id']} {pair['symbols']} {side}")
                    continue
                witness_tuple = tuple(witness)
                require(witness_tuple in wanted, f"pair witness not in full feasible set {case['case_id']} {pair['symbols']} {side}")
                require((witness_tuple[i] == witness_tuple[j]) is same, f"pair witness relation wrong {case['case_id']} {pair['symbols']} {side}")
                # Replay feasibility with set partitions, not the oracle's RGS helper.
                blocks = rgs_blocks(witness_tuple, alphabet)
                require(feasible(data, blocks), f"pair witness projection replay failed {case['case_id']} {pair['symbols']} {side}")
                witness_count += 1
        matched += 1

    expected_controls = {
        "doubled_pairs_default": (5, "multiple_partitions"),
        "doubled_pairs_k_3_4": (1, "unique_partition"),
        "doubled_pairs_k_3": (1, "unique_partition"),
        "forced_ab_other_pairs_ambiguous": (2, "multiple_partitions"),
        "known_k_forces_different": (1, "unique_partition"),
        "zero_answers_under_k": (0, "model_inconsistent"),
        "positive_only_all_partitions": (5, "multiple_partitions"),
        "epsilon_and_unused_symbols": (15, "multiple_partitions"),
        "no_positive_boundary": (5, "multiple_partitions"),
    }
    for case_id, (count, status) in expected_controls.items():
        row = by_id[case_id]
        require((row["partition_count"], row["status"]) == (count, status), f"named control mismatch: {case_id}")
    forced_ab = by_id["forced_ab_other_pairs_ambiguous"]["pair_relations"]
    rel = {"".join(row["symbols"]): row["relation"] for row in forced_ab}
    require(rel == {"ab": "forced_same", "ac": "ambiguous", "bc": "ambiguous"}, "forced/ambiguous pair control mismatch")
    invalid_rows = [json.loads(line) for line in (CORPUS / "invalid_cases.jsonl").read_text(encoding="utf-8").splitlines()]
    require(len(invalid_rows) == 7, "invalid control count mismatch")

    report = {
        "schema_version": 1,
        "status": "accepted_independent_stage_a",
        "method": "independent set-insertion partition enumeration and projection feasibility, cross-checked against direct-RGS oracle output",
        "corpus_manifest_sha256": sha(manifest_raw),
        "oracle_output_sha256": sha(ORACLE_PATH.read_bytes()),
        "random_cases": len(random_rows),
        "valid_cases": matched,
        "invalid_controls": len(invalid_rows),
        "manifest_files_checked": checked_files,
        "complete_partition_sets_cross_checked": matched,
        "total_feasible_partitions": total_feasible,
        "pair_witnesses_independently_replayed": witness_count,
        "named_controls_checked": len(expected_controls),
        "oracle_rows": len(oracle_rows),
    }
    raw_report = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with REPORT_PATH.open("xb") as handle:
        handle.write(raw_report)
    report["report_sha256"] = sha(raw_report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

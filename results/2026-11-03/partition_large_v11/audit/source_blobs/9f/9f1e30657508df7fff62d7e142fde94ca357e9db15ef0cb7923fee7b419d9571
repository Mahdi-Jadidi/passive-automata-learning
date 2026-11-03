#!/usr/bin/env python3
"""Cross-check C010's direct-RGS oracle with independent set-insertion enumeration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus_v1"
MANIFEST_PATH = CORPUS / "manifest.json"
ORACLE_PATH = CORPUS / "oracle_v1.jsonl"
REPORT_PATH = ROOT / "oracle_validation_v1.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def set_insert_partitions(items: list[str]) -> list[list[list[str]]]:
    if not items:
        return [[]]
    head, *tail = items
    out = []
    for partition in set_insert_partitions(tail):
        for index in range(len(partition)):
            candidate = [block.copy() for block in partition]
            candidate[index].append(head)
            out.append(candidate)
        out.append([[head], *[block.copy() for block in partition]])
    return out


def blocks_to_rgs(partition: list[list[str]], alphabet: list[str]) -> tuple[int, ...]:
    owner = {symbol: block_index for block_index, block in enumerate(partition) for symbol in block}
    rename: dict[int, int] = {}
    result = []
    for symbol in alphabet:
        raw = owner[symbol]
        rename.setdefault(raw, len(rename))
        result.append(rename[raw])
    return tuple(result)


def rgs_to_blocks(rgs: tuple[int, ...] | list[int], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(blocks) <= label:
            blocks.append([])
        blocks[label].append(symbol)
    return blocks


def project(word: str, block: set[str]) -> str:
    return "".join(symbol for symbol in word if symbol in block)


def feasible(data: dict, partition: list[list[str]]) -> bool:
    positive_languages = [{project(word, set(block)) for word in data["positive"]} for block in partition]
    return all(any(project(word, set(block)) not in language
                   for block, language in zip(partition, positive_languages))
               for word in data["negative"])


def bell_partition_set(data: dict) -> set[tuple[int, ...]]:
    alphabet = data["alphabet"]
    partitions = set_insert_partitions(alphabet)
    result = set()
    for partition in partitions:
        if feasible(data, partition):
            result.add(blocks_to_rgs(partition, alphabet))
    if len({blocks_to_rgs(partition, alphabet) for partition in partitions}) != len(partitions):
        raise AssertionError("set-insertion generator repeated a partition")
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest_raw = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    oracle_rows = [json.loads(line) for line in ORACLE_PATH.read_text(encoding="utf-8").splitlines()]
    require(len(oracle_rows) == len(manifest["valid_cases"]) >= 100, "valid corpus/oracle count mismatch")
    require(len({case["canonical_payload_sha256"] for case in manifest["valid_cases"]}) == len(manifest["valid_cases"]),
            "valid payloads are not unique")
    random_count = sum(case["origin"] == "C009_no_K_derived_random" for case in manifest["valid_cases"])
    require(random_count >= 100, f"not enough retained C009 random payloads: {random_count}")

    files_checked = 0
    for file_row in manifest["files"]:
        raw = (CORPUS / file_row["path"]).read_bytes()
        require(sha(raw) == file_row["sha256"] and len(raw) == file_row["bytes"], f"corpus file hash mismatch: {file_row['path']}")
        files_checked += 1
    invalid_rows = [json.loads(line) for line in (CORPUS / "invalid_cases.jsonl").read_text(encoding="utf-8").splitlines()]
    require(len(invalid_rows) == 6, "stale K/malformed fixture count mismatch")
    require({row["case_id"] for row in invalid_rows} >= {"stale_allowed_k", "stale_legacy_k"}, "stale-K rejection controls missing")
    dedup_rows = [json.loads(line) for line in (CORPUS / "deduplication.jsonl").read_text(encoding="utf-8").splitlines()]
    require(len(dedup_rows) == manifest["candidate_count"] == 131, "dedup ledger candidate count mismatch")
    retained_ids = {row["case_id"] for row in manifest["valid_cases"]}
    payload_hash_to_id = {row["canonical_payload_sha256"]: row["case_id"] for row in manifest["valid_cases"]}
    for decision in dedup_rows:
        require(decision["retained_as"] in retained_ids, f"dedup target absent: {decision['candidate_id']}")
        if decision["decision"] == "deduplicated":
            require(decision["canonical_payload_sha256"] in payload_hash_to_id, f"duplicate canonical payload absent: {decision['candidate_id']}")

    by_id = {row["case_id"]: row for row in oracle_rows}
    require(len(by_id) == len(oracle_rows), "duplicate oracle case IDs")
    total = 0
    witness_replays = 0
    for case in manifest["valid_cases"]:
        case_id = case["case_id"]
        raw = (CORPUS / case["path"]).read_bytes()
        data = json.loads(raw.decode("utf-8"))
        require(set(data) == {"alphabet", "positive", "negative"}, f"K/extra field found in valid C010 input: {case_id}")
        require(sha(canonical(data)) == case["canonical_payload_sha256"], f"canonical payload hash mismatch: {case_id}")
        result = by_id[case_id]
        expected = bell_partition_set(data)
        observed = {tuple(rgs) for rgs in result["compatible_rgs"]}
        require(len(observed) == len(result["compatible_rgs"]), f"duplicate oracle partitions: {case_id}")
        require(expected == observed, f"complete unrestricted partition-set mismatch: {case_id}")
        require(result["input_sha256"] == sha(canonical(data)), f"oracle input hash mismatch: {case_id}")
        require(result["partition_count"] == len(expected) >= 1, f"empty/incorrect unrestricted model count: {case_id}")
        require(sum(result["partition_count_by_k"].values()) == len(expected), f"k-spectrum count mismatch: {case_id}")
        require(all(str(k) in result["partition_count_by_k"] for k in range(1, len(data["alphabet"]) + 1)),
                f"k-spectrum missing zero counts: {case_id}")
        require(result["kmax"] == max(int(k) for k, value in result["partition_count_by_k"].items() if value),
                f"kmax mismatch: {case_id}")
        require(result["status"] == ("one_block_only" if len(expected) == 1 else "multiple_compatible_partitions"),
                f"status mismatch: {case_id}")
        alphabet = data["alphabet"]
        pair_map = {tuple(row["symbols"]): row for row in result["pair_relations"]}
        require(len(pair_map) == len(alphabet) * (len(alphabet) - 1) // 2, f"pair rows incomplete: {case_id}")
        for i in range(len(alphabet)):
            for j in range(i + 1, len(alphabet)):
                symbols = (alphabet[i], alphabet[j])
                row = pair_map[symbols]
                same = [rgs for rgs in expected if rgs[i] == rgs[j]]
                diff = [rgs for rgs in expected if rgs[i] != rgs[j]]
                relation = "forced_same" if len(same) == len(expected) else "ambiguous"
                require(row["relation"] == relation, f"pair relation mismatch: {case_id} {symbols}")
                require(row["coown_count"] == len(same) and row["different_count"] == len(diff),
                        f"pair count mismatch: {case_id} {symbols}")
                require(row["relation"] != "forced_different" and len(same) >= 1,
                        f"unrestricted impossibility theorem violated: {case_id} {symbols}")
                for side, want_same in (("same", True), ("different", False)):
                    witness = row[f"{side}_witness_rgs"]
                    exists = len(same) > 0 if want_same else len(diff) > 0
                    require((witness is not None) == exists, f"pair witness existence mismatch: {case_id} {symbols} {side}")
                    if witness is not None:
                        value = tuple(witness)
                        require(value in expected and feasible(data, rgs_to_blocks(value, alphabet)),
                                f"pair witness projection replay failed: {case_id} {symbols} {side}")
                        require((value[i] == value[j]) is want_same, f"pair witness relation mismatch: {case_id} {symbols} {side}")
                        witness_replays += 1
        total += len(expected)

    controls = {
        "one_block_only_unrestricted": 1,
        "no_labels_all_partitions": 5,
        "doubled_pairs_default": 5,
        "positive_only_all_partitions": 5,
        "forced_ab_other_pairs_ambiguous": 2,
        "known_k_forces_different": 2,
        "no_positive_boundary": 5,
    }
    for case_id, count in controls.items():
        require(by_id[case_id]["partition_count"] == count, f"named control count mismatch: {case_id}")
    graph_empty = by_id["doubled_pairs_default"]
    require(graph_empty["partition_count_by_k"] == {"1": 1, "2": 3, "3": 1, "4": 0, "5": 0, "6": 0},
            "graph-empty doubled-pairs spectrum mismatch")
    graph_pairs = {"".join(row["symbols"]): row for row in graph_empty["pair_relations"]}
    require(all(graph_pairs[pair]["relation"] == "forced_same" for pair in ("ab", "cd", "ef")),
            "doubled-pairs internal atoms not forced")
    require(all(graph_pairs[pair]["relation"] == "ambiguous" and graph_pairs[pair]["coown_count"] == 2
                and graph_pairs[pair]["different_count"] == 3 for pair in ("ac", "ad", "ae", "af", "bc", "bd", "be", "bf", "ce", "cf", "de", "df")),
            "doubled-pairs cross-atom counts mismatch")
    one_block = by_id["one_block_only_unrestricted"]
    require(one_block["compatible_partitions"] == [[list("ab")]], "one-block-only control partition mismatch")
    former_known_k = by_id["known_k_forces_different"]
    require(former_known_k["pair_relations"][0]["relation"] == "ambiguous", "removing K failed to remove forced-different result")
    require(all(row["partition_count_by_k"] == {"1": 1, "2": 3, "3": 1} for row in (by_id["no_labels_all_partitions"], by_id["positive_only_all_partitions"], by_id["no_positive_boundary"])),
            "unrestricted Bell(3) boundary spectrum mismatch")

    report = {
        "schema_version": 1,
        "status": "accepted_independent_unrestricted_oracle",
        "valid_cases": len(manifest["valid_cases"]),
        "retained_random_derived_cases": random_count,
        "invalid_controls": len(invalid_rows),
        "dedup_candidates_recorded": len(dedup_rows),
        "dedup_duplicate_rows": sum(row["decision"] == "deduplicated" for row in dedup_rows),
        "corpus_files_hash_checked": files_checked,
        "complete_partition_sets_cross_checked": len(manifest["valid_cases"]),
        "total_compatible_partition_rows": total,
        "pair_witnesses_independently_replayed": witness_replays,
        "no_valid_empty_model": True,
        "no_forced_different_relations": True,
        "corpus_manifest_sha256": sha(manifest_raw),
        "oracle_output_sha256": sha(ORACLE_PATH.read_bytes()),
    }
    with REPORT_PATH.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

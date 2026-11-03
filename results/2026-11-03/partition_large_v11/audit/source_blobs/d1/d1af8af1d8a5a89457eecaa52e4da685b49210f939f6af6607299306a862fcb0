#!/usr/bin/env python3
"""Independent direct-RGS oracle for new C011 regressions plus structural family certificates."""
from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

AUDIT = Path(__file__).resolve().parent


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def write_once(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)


def normalize(data: dict) -> tuple[list[str], list[str], list[str]]:
    alphabet = sorted(data["alphabet"])
    if not alphabet or len(set(alphabet)) != len(alphabet) or any(len(x) != 1 for x in alphabet):
        raise ValueError("invalid alphabet")
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    if set(positives) & set(negatives):
        raise ValueError("contradictory labels")
    if any(set(w) - set(alphabet) for w in positives + negatives):
        raise ValueError("out-of-alphabet word")
    return alphabet, positives, negatives


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
    return "".join(ch for ch in word if ch in block)


def feasible(alphabet: list[str], positives: list[str], negatives: list[str],
             rgs: tuple[int, ...]) -> bool:
    blocks = blocks_from_rgs(rgs, alphabet)
    block_sets = [set(block) for block in blocks]
    languages = [{project(p, block) for p in positives} for block in block_sets]
    for negative in negatives:
        if not any(project(negative, block) not in language
                   for block, language in zip(block_sets, languages)):
            return False
    return True


def make_rgs_result(case: dict, raw: bytes, data: dict) -> dict:
    alphabet, positives, negatives = normalize(data)
    if len(alphabet) > 8:
        raise ValueError("direct RGS oracle restricted to m<=8")
    compatible = [rgs for rgs in enumerate_rgs(len(alphabet))
                  if feasible(alphabet, positives, negatives, rgs)]
    if not compatible:
        raise AssertionError(f"valid finite labels unexpectedly have no model: {case['case_id']}")
    by_k = {str(k): sum(max(rgs) + 1 == k for rgs in compatible)
            for k in range(1, len(alphabet) + 1)}
    pairs = []
    for i, j in combinations(range(len(alphabet)), 2):
        same = [rgs for rgs in compatible if rgs[i] == rgs[j]]
        different = [rgs for rgs in compatible if rgs[i] != rgs[j]]
        if not same:
            raise AssertionError("one-block coarsening witness missing")
        pairs.append({
            "symbols": [alphabet[i], alphabet[j]],
            "relation": "forced_same" if len(same) == len(compatible) else "ambiguous",
            "same_count": len(same),
            "different_count": len(different),
            "same_witness_rgs": list(same[0]),
            "different_witness_rgs": list(different[0]) if different else None,
        })
    # Replay every advertised relation witness with direct projection feasibility.
    for pair in pairs:
        i, j = (alphabet.index(ch) for ch in pair["symbols"])
        for key, equal in (("same_witness_rgs", True), ("different_witness_rgs", False)):
            witness = pair[key]
            if witness is None:
                if key == "same_witness_rgs" or pair["relation"] != "forced_same":
                    raise AssertionError(f"required witness missing: {case['case_id']} {pair['symbols']} {key}")
                continue
            wrgs = tuple(witness)
            if wrgs not in compatible or not feasible(alphabet, positives, negatives, wrgs):
                raise AssertionError(f"invalid pair witness: {case['case_id']} {pair['symbols']} {key}")
            if (wrgs[i] == wrgs[j]) is not equal:
                raise AssertionError(f"wrong pair witness: {case['case_id']} {pair['symbols']} {key}")
    return {
        "case_id": case["case_id"],
        "raw_input_sha256": sha(raw),
        "canonical_payload_sha256": sha(canonical(data)),
        "normalized_positive_count": len(positives),
        "normalized_negative_count": len(negatives),
        "alphabet": alphabet,
        "complete": True,
        "method": "canonical RGS enumeration + direct block projection feasibility; no provider imports",
        "compatible_rgs": [list(rgs) for rgs in compatible],
        "partition_count": len(compatible),
        "partition_count_by_k": by_k,
        "kmax": max(max(rgs) + 1 for rgs in compatible),
        "pair_relations": pairs,
        "pair_witnesses_replayed": True,
    }


def adjacent_swap(p: str, n: str) -> tuple[int, str, str] | None:
    if len(p) != len(n):
        return None
    differences = [i for i, (a, b) in enumerate(zip(p, n)) if a != b]
    if len(differences) != 2 or differences[1] != differences[0] + 1:
        return None
    i, j = differences
    if p[i] == n[j] and p[j] == n[i] and p[i] != p[j]:
        return i, p[i], p[j]
    return None


def bell_stirling(n: int) -> tuple[int, list[int]]:
    row = [1] + [0] * n
    for size in range(1, n + 1):
        nxt = [0] * (n + 1)
        for k in range(1, size + 1):
            nxt[k] = row[k - 1] + k * row[k]
        row = nxt
    return sum(row), row


def certify_family(case: dict, data: dict) -> dict:
    alphabet, positives, negatives = normalize(data)
    groups = case["expected_atom_groups"]
    if not groups:
        raise ValueError("family certificate requires explicit atom groups")
    flattened = [ch for group in groups for ch in group]
    if sorted(flattened) != alphabet or len(flattened) != len(set(flattened)):
        raise AssertionError(f"groups do not partition alphabet: {case['case_id']}")
    expected_edges = {tuple(sorted((group[i], group[i + 1])))
                      for group in groups for i in range(len(group) - 1)}
    actual_edge_witnesses: dict[tuple[str, str], tuple[str, str, int]] = {}
    unexpected = []
    for p in positives:
        for n in negatives:
            edge = adjacent_swap(p, n)
            if edge is None:
                continue
            position, x, y = edge
            key = tuple(sorted((x, y)))
            if key not in expected_edges:
                unexpected.append({"positive": p, "negative": n,
                                   "position": position, "symbols": list(key)})
            else:
                actual_edge_witnesses.setdefault(key, (p, n, position))
    missing_edges = sorted(expected_edges - set(actual_edge_witnesses))
    if unexpected or missing_edges:
        raise AssertionError(f"swap-edge family mismatch {case['case_id']}: unexpected={len(unexpected)} missing={len(missing_edges)}")

    positive_languages = [{project(p, set(group)) for p in positives} for group in groups]
    rejection_witnesses = []
    for ni, negative in enumerate(negatives):
        rejected = None
        for gi, group in enumerate(groups):
            value = project(negative, set(group))
            if value not in positive_languages[gi]:
                rejected = {"negative_index": ni, "group_index": gi,
                            "projection": value}
                break
        if rejected is None:
            raise AssertionError(f"atom partition infeasible: {case['case_id']} negative#{ni}")
        rejection_witnesses.append(rejected)

    r = len(groups)
    bell, stirling = bell_stirling(r)
    pair_same = bell_stirling(r - 1)[0] if r > 1 else 1
    return {
        "case_id": case["case_id"],
        "input_sha256": case["input_sha256"],
        "proof_method": "replay all positive-negative adjacent swaps; exact union components; direct atom feasibility; coarsening theorem T1 + sound-swap theorem T2",
        "alphabet_size": len(alphabet),
        "atom_count": r,
        "atoms": groups,
        "expected_swap_edge_pair_count": len(expected_edges),
        "observed_swap_edge_pair_count": len(actual_edge_witnesses),
        "swap_edge_witnesses": [
            {"symbols": list(key), "positive": actual_edge_witnesses[key][0],
             "negative": actual_edge_witnesses[key][1],
             "positions": [actual_edge_witnesses[key][2], actual_edge_witnesses[key][2] + 1]}
            for key in sorted(actual_edge_witnesses)],
        "unexpected_swap_edge_count": len(unexpected),
        "missing_swap_edge_count": len(missing_edges),
        "atom_partition_feasible": True,
        "negative_rejection_witness_count": len(rejection_witnesses),
        "negative_rejection_witnesses": rejection_witnesses,
        "expected_partition_count": bell,
        "expected_partition_count_by_k": {str(k): (stirling[k] if k <= r else 0) for k in range(1, len(alphabet) + 1)},
        "same_count_within_atom": bell,
        "same_count_across_atoms": pair_same,
        "different_count_across_atoms": bell - pair_same,
        "enumerated_bell_of_alphabet": False,
        "enumerated_bell_of_atoms": False,
    }


def main() -> int:
    correctness = json.loads((AUDIT / "CORRECTNESS_MANIFEST_V2.json").read_text(encoding="utf-8"))
    base = [row for row in correctness["cases"] if row["expected_source"] == "c010_direct_rgs_v1"]
    base_oracle_path = AUDIT / "c010_oracle_v1.jsonl"
    base_oracle = [json.loads(line) for line in base_oracle_path.read_text(encoding="utf-8").splitlines()]
    if len(base_oracle) != len(base) or {r["case_id"] for r in base_oracle} != {r["case_id"] for r in base}:
        raise AssertionError("copied C010 oracle rows do not match the 125 frozen input IDs")
    for row in base:
        oracle_row = next(value for value in base_oracle if value["case_id"] == row["case_id"])
        data = json.loads((AUDIT / row["path"]).read_text(encoding="utf-8"))
        if sha(canonical(data)) != oracle_row["input_sha256"]:
            raise AssertionError(f"C010 oracle/input canonical hash mismatch: {row['case_id']}")

    new_rows = [row for row in correctness["cases"] if row["expected_source"] in {"c011_direct_rgs_v1", "c011_direct_rgs_v2"}]
    rgs_outputs = []
    for row in new_rows:
        path = AUDIT / row["path"]
        raw = path.read_bytes()
        if sha(raw) != row["input_sha256"]:
            raise AssertionError(f"new input hash mismatch: {row['case_id']}")
        data = json.loads(raw.decode("utf-8"))
        rgs_outputs.append(make_rgs_result(row, raw, data))
    rgs_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                      for row in rgs_outputs).encode("utf-8")
    write_once(AUDIT / "C011_RGS_ORACLE_V2.jsonl", rgs_raw)
    combined_raw = base_oracle_path.read_bytes() + rgs_raw
    write_once(AUDIT / "FULL_CORRECTNESS_ORACLE_V2.jsonl", combined_raw)

    performance = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
    certs = []
    for case in performance["cells"]:
        if case["family_kind"] == "direct_rgs_fallback":
            output = next(row for row in rgs_outputs if row["case_id"] == case["case_id"])
            data = json.loads((AUDIT / case["path"]).read_text(encoding="utf-8"))
            alphabet, positives, negatives = normalize(data)
            if any(adjacent_swap(p, n) is not None for p in positives for n in negatives):
                raise AssertionError("fallback control unexpectedly has adjacent-swap edges")
            if feasible(alphabet, positives, negatives, tuple(range(len(alphabet)))):
                raise AssertionError("fallback singleton atoms unexpectedly feasible")
            certs.append({"case_id": case["case_id"], "proof_method": "full direct RGS oracle, m<=8; exact empty swap graph and singleton infeasibility replayed",
                          "input_sha256": case["input_sha256"],
                          "partition_count": output["partition_count"],
                          "partition_count_by_k": output["partition_count_by_k"],
                          "compatible_rgs": output["compatible_rgs"],
                          "graph_empty_expected": True,
                          "atom_partition_feasible_expected": False})
        else:
            path = AUDIT / case["path"]
            data = json.loads(path.read_text(encoding="utf-8"))
            certs.append(certify_family(case, data))
    cert_raw = (json.dumps({"schema_version": 1,
                            "method": "independent structural proof certificates; no Bell(alphabet-size) enumeration",
                            "certificates": certs}, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    write_once(AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V2.json", cert_raw)
    receipt = {
        "schema_version": 1,
        "status": "oracle_and_family_certificates_frozen",
        "rgs_new_case_count": len(rgs_outputs),
        "rgs_new_case_ids": [row["case_id"] for row in rgs_outputs],
        "base_c010_oracle_case_count": len(base_oracle),
        "full_correctness_oracle_case_count": len(base_oracle) + len(rgs_outputs),
        "full_oracle_sha256": sha(combined_raw),
        "rgs_extension_sha256": sha(rgs_raw),
        "family_certificate_count": len(certs),
        "family_certificate_sha256": sha(cert_raw),
        "direct_rgs_method": "canonical restricted-growth strings plus direct projection feasibility; duplicate labels normalized as set-valued finite samples",
        "provider_imports": False,
        "bell_large_m_enumeration": False,
    }
    receipt_raw = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    write_once(AUDIT / "ORACLE_FREEZE_RECEIPT_V2.json", receipt_raw)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Independently validate scale oracle with canonical-RGS enumeration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCALE = ROOT / "audit" / "scale_v1"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def rgs_strings(n: int):
    if n == 0:
        yield ()
        return
    values = [0] * n

    def visit(position: int, largest: int):
        if position == n:
            yield tuple(values)
            return
        for label in range(largest + 2):
            values[position] = label
            yield from visit(position + 1, max(largest, label))

    yield from visit(1, 0)


def rgs_blocks(labels: tuple[int, ...] | list[int], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, label in zip(alphabet, labels):
        while len(blocks) <= label:
            blocks.append([])
        blocks[label].append(symbol)
    return blocks


def blocks_rgs(blocks: list[list[str]], alphabet: list[str]) -> tuple[int, ...]:
    owner = {symbol: i for i, block in enumerate(blocks) for symbol in block}
    renaming: dict[int, int] = {}
    result = []
    for symbol in alphabet:
        original = owner[symbol]
        renaming.setdefault(original, len(renaming))
        result.append(renaming[original])
    return tuple(result)


def project(word: str, block: set[str]) -> str:
    return "".join(symbol for symbol in word if symbol in block)


def feasible(data: dict, partition: list[list[str]]) -> bool:
    languages = [{project(word, set(block)) for word in data["positive"]}
                 for block in partition]
    return all(any(project(word, set(block)) not in language
                   for block, language in zip(partition, languages))
               for word in data["negative"])


def replay_edges(data: dict) -> list[dict]:
    output = []
    for positive in data["positive"]:
        for negative in data["negative"]:
            if len(positive) != len(negative):
                continue
            differing = [i for i, (left, right) in enumerate(zip(positive, negative)) if left != right]
            if len(differing) != 2 or differing[1] != differing[0] + 1:
                continue
            i, j = differing
            if positive[i] != positive[j] and positive[i] == negative[j] and positive[j] == negative[i]:
                output.append({"positive": positive, "negative": negative,
                "positions": [i, j], "symbols": [positive[i], positive[j]]})
    return output


def components(alphabet: list[str], edges: list[dict]) -> list[list[str]]:
    parent = {symbol: symbol for symbol in alphabet}

    def find(symbol):
        if parent[symbol] != symbol:
            parent[symbol] = find(parent[symbol])
        return parent[symbol]

    for edge in edges:
        left, right = edge["symbols"]
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)
    groups: dict[str, list[str]] = {}
    for symbol in alphabet:
        groups.setdefault(find(symbol), []).append(symbol)
    return sorted((sorted(group) for group in groups.values()), key=lambda g: g[0])


def lift(labels: tuple[int, ...], atoms: list[list[str]], alphabet: list[str]) -> list[list[str]]:
    owner = {symbol: atom_index for atom_index, atom in enumerate(atoms) for symbol in atom}
    grouped: dict[int, list[str]] = {}
    for symbol in alphabet:
        grouped.setdefault(labels[owner[symbol]], []).append(symbol)
    return [grouped[key] for key in sorted(grouped)]


def expected_set_by_rgs(data: dict) -> tuple[set[tuple[int, ...]], int]:
    alphabet = sorted(data["alphabet"])
    family = set()
    visited = 0
    for candidate in rgs_strings(len(alphabet)):
        visited += 1
        if feasible(data, rgs_blocks(candidate, alphabet)):
            family.add(candidate)
    return family, visited


def expected_set_by_quotient(data: dict, atoms: list[list[str]]) -> tuple[set[tuple[int, ...]], int]:
    alphabet = sorted(data["alphabet"])
    family = set()
    visited = 0
    for atom_labels in rgs_strings(len(atoms)):
        visited += 1
        part = lift(atom_labels, atoms, alphabet)
        if not feasible(data, part):
            raise AssertionError("claimed feasible atom partition has an infeasible coarsening")
        family.add(blocks_rgs(part, alphabet))
    return family, visited


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("oracle_stdout", type=Path)
    parser.add_argument("capture_result", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    capture = json.loads(args.capture_result.read_text(encoding="utf-8"))
    raw = args.oracle_stdout.read_bytes()
    errors: list[str] = []
    if capture.get("execution_status") != "success" or capture.get("exit_code") != 0 or capture.get("child_reaped") is not True:
        errors.append("scale oracle capture status/exit/reap invalid")
    if capture.get("stdout_sha256") != sha(raw) or capture.get("stdout_bytes") != len(raw):
        errors.append("scale oracle stdout hash/size mismatch")
    manifest_raw = (SCALE / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    try:
        oracle = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        oracle = {}
        errors.append(f"scale oracle stdout is not one JSON document: {exc!r}")
    if oracle.get("status") != "accepted_four_cell_independent_scale_oracle" or oracle.get("scale_manifest_sha256") != sha(manifest_raw):
        errors.append("oracle status or scale manifest hash mismatch")
    if len(oracle.get("cells", [])) != 4:
        errors.append("oracle did not produce exactly four cells")
    oracle_by_id = {row.get("case_id"): row for row in oracle.get("cells", [])}

    symbol_domains = 0
    quotient_domains = 0
    direct_feasibility_checks = 0
    pair_witnesses_replayed = 0
    for case in manifest["cells"]:
        case_id = case["case_id"]
        row = oracle_by_id.get(case_id)
        if row is None:
            errors.append(f"oracle row missing: {case_id}")
            continue
        path = SCALE / case["input"]["path"]
        input_raw = path.read_bytes()
        data = json.loads(input_raw.decode("utf-8"))
        if sha(input_raw) != case["input"]["sha256"] or len(input_raw) != case["input"]["bytes"]:
            errors.append(f"frozen input hash mismatch: {case_id}")
            continue
        if sha(canonical(data)) != case["input"]["canonical_payload_sha256"]:
            errors.append(f"frozen canonical input hash mismatch: {case_id}")
            continue
        alphabet = sorted(data["alphabet"])
        edges = replay_edges(data)
        atoms = components(alphabet, edges)
        if row.get("input_sha256") != sha(input_raw) or row.get("swap_edges") != edges or row.get("provider_atoms") != atoms:
            errors.append(f"oracle input/edge/atom evidence mismatch: {case_id}")
            continue
        if row.get("canonical_payload_sha256") != case["input"]["canonical_payload_sha256"]:
            errors.append(f"oracle canonical input hash mismatch: {case_id}")
        if len(edges) != case["expected_edge_count"] or row.get("atom_partition_feasible") is not case["expected_atom_partition_feasible"]:
            errors.append(f"oracle structural expectation mismatch: {case_id}")
        if row.get("atom_partition_feasible") is not feasible(data, atoms):
            errors.append(f"oracle atom-feasibility mismatch: {case_id}")

        if case_id in ("m14_seven_pair_atoms", "m64_eight_connected_groups"):
            expected, visited = expected_set_by_quotient(data, atoms)
            quotient_domains += visited
            if row.get("symbol_partitions_enumerated") != 0:
                errors.append(f"quotient oracle unexpectedly claims symbol enumeration: {case_id}")
            if row.get("atom_or_semantic_partitions_enumerated") != visited:
                errors.append(f"quotient domain count mismatch: {case_id}")
        else:
            expected, visited = expected_set_by_rgs(data)
            symbol_domains += visited
            if row.get("symbol_partitions_enumerated") != visited:
                errors.append(f"direct RGS domain count mismatch: {case_id}")
            semantic_atoms = case["expected_semantic_atoms"]
            quotient = set()
            for atom_labels in rgs_strings(len(semantic_atoms)):
                quotient.add(blocks_rgs(lift(atom_labels, semantic_atoms, alphabet), alphabet))
            quotient_domains += len(quotient)
            if row.get("atom_or_semantic_partitions_enumerated") != len(quotient):
                errors.append(f"semantic quotient domain count mismatch: {case_id}")
            if quotient != expected:
                errors.append(f"direct symbol oracle does not equal semantic coarsenings: {case_id}")

        observed_rows = row.get("compatible_rgs", [])
        observed = {tuple(value) for value in observed_rows}
        if len(observed) != len(observed_rows) or observed != expected:
            errors.append(f"complete compatible RGS set mismatch: {case_id}")
        if len(expected) != case["expected_count"] or row.get("compatible_partition_count") != len(expected):
            errors.append(f"compatible count mismatch: {case_id}")
        spectrum = {str(k): sum(1 for labels in expected if max(labels) + 1 == k)
                    for k in range(1, len(alphabet) + 1)}
        if spectrum != case["expected_spectrum"] or row.get("compatible_partition_count_by_k") != spectrum:
            errors.append(f"per-k spectrum mismatch: {case_id}")
        kmax = max(k for k in range(1, len(alphabet) + 1) if spectrum[str(k)])
        if kmax != case["expected_k_max"] or row.get("k_max_compatible") != kmax:
            errors.append(f"exact kmax mismatch: {case_id}")
        for labels in expected:
            if not feasible(data, rgs_blocks(labels, alphabet)):
                errors.append(f"infeasible expected RGS: {case_id}")
                break
            direct_feasibility_checks += 1

        pair_rows = row.get("pair_relations", [])
        pair_map = {tuple(pair.get("symbols", [])): pair for pair in pair_rows}
        if len(pair_map) != len(alphabet) * (len(alphabet) - 1) // 2 or row.get("pair_count") != len(pair_map):
            errors.append(f"pair relation table incomplete: {case_id}")
            continue
        for i, left in enumerate(alphabet):
            for j in range(i + 1, len(alphabet)):
                right = alphabet[j]
                same_labels = [labels for labels in expected if labels[i] == labels[j]]
                diff_labels = [labels for labels in expected if labels[i] != labels[j]]
                pair = pair_map[(left, right)]
                if pair.get("same_partition_count") != len(same_labels) or pair.get("different_partition_count") != len(diff_labels):
                    errors.append(f"pair counts mismatch: {case_id} {left,right}")
                relation = "forced_same" if not diff_labels else "ambiguous"
                if pair.get("relation") != relation:
                    errors.append(f"pair relation mismatch: {case_id} {left,right}")
                for key, source in (("same_witness_rgs", same_labels), ("different_witness_rgs", diff_labels)):
                    witness = pair.get(key)
                    if (witness is not None) != bool(source):
                        errors.append(f"pair witness presence mismatch: {case_id} {left,right} {key}")
                    elif witness is not None:
                        labels = tuple(witness)
                        if labels not in expected or (labels[i] == labels[j]) != (key == "same_witness_rgs"):
                            errors.append(f"pair witness invalid: {case_id} {left,right} {key}")
                        elif not feasible(data, rgs_blocks(labels, alphabet)):
                            errors.append(f"pair witness infeasible: {case_id} {left,right} {key}")
                        pair_witnesses_replayed += 1

    status = "accepted_independent_scale_oracle" if not errors and len(oracle_by_id) == 4 else "rejected_scale_oracle"
    report = {
        "schema_version": 1,
        "status": status,
        "capture_attempt_id": capture.get("attempt_id"),
        "scale_manifest_sha256": sha(manifest_raw),
        "oracle_stdout_sha256": sha(raw),
        "cells_checked": len(oracle_by_id),
        "symbol_partition_domains_enumerated": symbol_domains,
        "quotient_partition_domains_enumerated": quotient_domains,
        "direct_compatible_partition_feasibility_replays": direct_feasibility_checks,
        "pair_witnesses_replayed": pair_witnesses_replayed,
        "errors": errors,
    }
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if status == "accepted_independent_scale_oracle" else 1


if __name__ == "__main__":
    raise SystemExit(main())

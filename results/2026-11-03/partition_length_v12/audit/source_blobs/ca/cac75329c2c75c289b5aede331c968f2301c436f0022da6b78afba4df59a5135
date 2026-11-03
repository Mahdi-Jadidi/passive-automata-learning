#!/usr/bin/env python3
"""Independent full-set/certificate validator for captured C010 v2 output."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CORPUS = AUDIT / "corpus_v1"
REPORT = AUDIT / "provider_validation_v2.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def project(word: str, block: set[str]) -> str:
    return "".join(ch for ch in word if ch in block)


def feasible(data: dict, partition: list[list[str]]) -> bool:
    languages = [{project(word, set(block)) for word in data["positive"]}
                 for block in partition]
    return all(any(project(word, set(block)) not in language
                   for block, language in zip(partition, languages))
               for word in data["negative"])


def set_insert_partitions(items: list[str]) -> list[list[list[str]]]:
    if not items:
        return [[]]
    head, *tail = items
    out = []
    for part in set_insert_partitions(tail):
        for index in range(len(part)):
            candidate = [block.copy() for block in part]
            candidate[index].append(head)
            out.append(candidate)
        out.append([[head], *[block.copy() for block in part]])
    return out


def direct_expected(data: dict) -> set[tuple[int, ...]]:
    alphabet = data["alphabet"]
    result = set()
    for partition in set_insert_partitions(alphabet):
        if feasible(data, partition):
            owner = {ch: i for i, block in enumerate(partition) for ch in block}
            rename = {}
            rgs = []
            for ch in alphabet:
                rename.setdefault(owner[ch], len(rename))
                rgs.append(rename[owner[ch]])
            result.add(tuple(rgs))
    return result


def partition_rgs(partition: object, alphabet: list[str]) -> tuple[int, ...]:
    if not isinstance(partition, list) or not partition:
        raise ValueError("partition must be a nonempty list of nonempty blocks")
    owner: dict[str, int] = {}
    for block_index, block in enumerate(partition):
        if not isinstance(block, list) or not block:
            raise ValueError("partition contains an empty/non-list block")
        for symbol in block:
            if symbol in owner:
                raise ValueError("partition repeats a symbol")
            owner[symbol] = block_index
    if set(owner) != set(alphabet):
        raise ValueError("partition symbols differ from alphabet")
    rename: dict[int, int] = {}
    result = []
    for symbol in alphabet:
        raw = owner[symbol]
        rename.setdefault(raw, len(rename))
        result.append(rename[raw])
    return tuple(result)


def rgs_blocks(rgs: tuple[int, ...], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, index in zip(alphabet, rgs):
        while len(blocks) <= index:
            blocks.append([])
        blocks[index].append(symbol)
    return blocks


def check_witness(data: dict, witness: object) -> None:
    if not isinstance(witness, dict):
        raise ValueError("projection witness is not an object")
    alphabet = data["alphabet"]
    partition = witness.get("partition")
    partition_rgs(partition, alphabet)
    if not feasible(data, partition):
        raise ValueError("witness partition fails direct negative-cover feasibility")
    blocks = [set(block) for block in partition]
    positive_languages = [{project(p, block) for p in data["positive"]}
                          for block in blocks]
    expected_languages = [sorted(language) for language in positive_languages]
    if witness.get("positive_projection_languages") != expected_languages:
        raise ValueError("positive projection languages do not replay")
    negative_rows = witness.get("negative_witnesses")
    if not isinstance(negative_rows, list) or len(negative_rows) != len(data["negative"]):
        raise ValueError("negative witness list has wrong length")
    for word, row in zip(sorted(set(data["negative"])), negative_rows):
        projections = [project(word, block) for block in blocks]
        rejected = [i for i, value in enumerate(projections)
                    if value not in positive_languages[i]]
        if row.get("word") != word or row.get("projections") != projections:
            raise ValueError("negative projection witness does not replay")
        if row.get("rejected_by_blocks") != rejected or not rejected:
            raise ValueError("negative is not rejected by the listed blocks")


def validate_edges_and_atoms(data: dict, result: dict) -> list[list[str]]:
    alphabet = data["alphabet"]
    positives, negatives = set(data["positive"]), set(data["negative"])
    parent = {ch: ch for ch in alphabet}

    def find(ch: str) -> str:
        while parent[ch] != ch:
            parent[ch] = parent[parent[ch]]
            ch = parent[ch]
        return ch

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    edges = result.get("swap_edge_witnesses")
    if not isinstance(edges, list):
        raise ValueError("swap edge witness list is missing")
    for edge in edges:
        p, n = edge.get("positive"), edge.get("negative")
        pos, symbols = edge.get("positions"), edge.get("symbols")
        if p not in positives or n not in negatives:
            raise ValueError("swap edge is not sourced from frozen labels")
        if not isinstance(pos, list) or len(pos) != 2 or not isinstance(symbols, list) or len(symbols) != 2:
            raise ValueError("malformed swap edge witness")
        i, j = pos
        if not isinstance(i, int) or j != i + 1 or i < 0 or j >= len(p) or len(p) != len(n):
            raise ValueError("invalid adjacent swap positions")
        expected = list(p)
        expected[i], expected[j] = expected[j], expected[i]
        if p[i] == p[j] or "".join(expected) != n or symbols != [p[i], p[j]]:
            raise ValueError("swap edge does not replay")
        union(p[i], p[j])
    groups: dict[str, list[str]] = {}
    for ch in alphabet:
        groups.setdefault(find(ch), []).append(ch)
    expected_atoms = sorted((sorted(block) for block in groups.values()), key=lambda b: b[0])
    observed_atoms = result.get("atom_partition")
    if observed_atoms != expected_atoms:
        raise ValueError("reported atom partition differs from replayed edge components")
    return expected_atoms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider_stdout", type=Path)
    parser.add_argument("capture_result", type=Path)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()

    errors: list[str] = []
    cap = json.loads(args.capture_result.read_text(encoding="utf-8"))
    stdout_raw = args.provider_stdout.read_bytes()
    if cap.get("execution_status") != "success" or cap.get("exit_code") != 0 or cap.get("child_reaped") is not True:
        errors.append("provider capture was not successful, exit-zero and reaped")
    if sha(stdout_raw) != cap.get("stdout_sha256") or len(stdout_raw) != cap.get("stdout_bytes"):
        errors.append("provider stdout differs from immutable capture metadata")

    manifest_raw = (CORPUS / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    oracle_raw = (CORPUS / "oracle_v1.jsonl").read_bytes()
    oracle_rows = [json.loads(line) for line in oracle_raw.decode("utf-8").splitlines()]
    oracle_validation = json.loads((AUDIT / "oracle_validation_v1.json").read_text(encoding="utf-8"))
    if oracle_validation.get("status") != "accepted_independent_unrestricted_oracle":
        errors.append("prerequisite independent oracle validation is not accepted")
    if oracle_validation.get("oracle_output_sha256") != sha(oracle_raw):
        errors.append("validated oracle hash differs from frozen oracle bytes")

    oracle_by_payload = {row["input_sha256"]: row for row in oracle_rows}
    corpus_by_id = {row["case_id"]: row for row in manifest["valid_cases"]}
    expected_specs: list[tuple[str, str, Path, dict]] = []
    for case in manifest["valid_cases"]:
        path = CORPUS / case["path"]
        expected_specs.append((case["case_id"], "frozen_corpus", path,
                               json.loads(path.read_text(encoding="utf-8"))))
    preflight = json.loads((ROOT / "implementation" / "PREFLIGHT_CASES_V1.json").read_text(encoding="utf-8"))
    for case in preflight["cases"]:
        path = ROOT / "implementation" / case["input"]
        expected_specs.append((case["id"], "analytic_preflight", path,
                               json.loads(path.read_text(encoding="utf-8"))))

    try:
        provider_rows = [json.loads(line) for line in stdout_raw.decode("utf-8").splitlines()]
    except Exception as exc:
        provider_rows = []
        errors.append(f"provider stdout is not valid UTF-8 JSONL: {exc!r}")
    by_id = {row.get("case_id"): row for row in provider_rows}
    if len(by_id) != len(provider_rows):
        errors.append("duplicate or missing provider case IDs")
    expected_ids = {spec[0] for spec in expected_specs}
    if set(by_id) != expected_ids:
        errors.append("provider case ID set differs from frozen corpus/preflight ID set")

    full_set_matches = 0
    total_partitions = 0
    witness_replays = 0
    edge_rows = 0
    per_case_errors: dict[str, list[str]] = {}

    for case_id, kind, input_path, data in expected_specs:
        case_errors: list[str] = []
        row = by_id.get(case_id)
        if row is None:
            per_case_errors[case_id] = ["provider result missing"]
            continue
        raw = input_path.read_bytes()
        canonical_sha = sha(canonical(data))
        if row.get("kind") != kind or row.get("input_sha256") != sha(raw):
            case_errors.append("kind/input-byte hash mismatch")
        if row.get("canonical_payload_sha256") != canonical_sha:
            case_errors.append("canonical input hash mismatch")

        oracle = oracle_by_payload.get(canonical_sha)
        if oracle is not None:
            expected = {tuple(rgs) for rgs in oracle["compatible_rgs"]}
        else:
            expected = direct_expected(data)
        m = len(data["alphabet"])
        expected_by_k = {str(k): sum(1 for rgs in expected if max(rgs) + 1 == k)
                         for k in range(1, m + 1)}
        result = row.get("result")
        if not isinstance(result, dict):
            per_case_errors[case_id] = [*case_errors, "result is not an object"]
            continue
        try:
            if result.get("complete") is not True:
                raise ValueError("valid bounded case is not complete")
            wanted_status = "identified_unique_partition" if len(expected) == 1 else "partial_ownership_identification"
            if result.get("status") != wanted_status:
                raise ValueError(f"status mismatch: {result.get('status')!r}")
            if result.get("partition_count") != len(expected) or result.get("partition_count_by_k") != expected_by_k:
                raise ValueError("total or exact-k spectrum mismatch")
            if result.get("k_max_compatible") != max(k for k in range(1, m + 1) if expected_by_k[str(k)]):
                raise ValueError("exact k_max_compatible mismatch")

            atoms = validate_edges_and_atoms(data, result)
            edge_rows += len(result["swap_edge_witnesses"])
            if result.get("k_max_upper_bound") != len(atoms):
                raise ValueError("atom-count upper bound mismatch")
            atom_ok = feasible(data, atoms)
            if result.get("atom_projection_feasible") is not atom_ok:
                raise ValueError("atom feasibility flag does not replay")

            family = result.get("enumerated_partitions")
            if not isinstance(family, list):
                raise ValueError("full enumeration is missing")
            observed: set[tuple[int, ...]] = set()
            for witness in family:
                check_witness(data, witness)
                observed.add(partition_rgs(witness["partition"], data["alphabet"]))
                witness_replays += 1
            if len(observed) != len(family):
                raise ValueError("provider repeats an enumerated partition")
            if observed != expected:
                raise ValueError(f"full compatible set differs (missing={len(expected-observed)}, extra={len(observed-expected)})")
            if result.get("metrics", {}).get("enumerated_partitions") != len(expected):
                raise ValueError("enumeration metric differs from full set size")

            representative = result.get("representative")
            check_witness(data, representative)
            rep_rgs = partition_rgs(representative["partition"], data["alphabet"])
            if rep_rgs not in expected:
                raise ValueError("representative is outside the compatible family")
            witness_replays += 1

            pair_rows = result.get("pair_relations")
            if not isinstance(pair_rows, list):
                raise ValueError("pair relation rows missing")
            pair_map = {tuple(item.get("symbols", [])): item for item in pair_rows}
            pair_count = m * (m - 1) // 2
            if len(pair_map) != pair_count:
                raise ValueError("pair relation table is incomplete")
            alphabet = data["alphabet"]
            for i, a in enumerate(alphabet):
                for j in range(i + 1, m):
                    b = alphabet[j]
                    same = [part for part in expected if part[i] == part[j]]
                    diff = len(expected) - len(same)
                    pair = pair_map[(a, b)]
                    relation = "forced_same" if len(same) == len(expected) else "ambiguous"
                    if pair.get("relation") != relation or pair.get("same_partition_count") != len(same) or pair.get("different_partition_count") != diff:
                        raise ValueError(f"pair counts/relation mismatch for {a,b}")
                    for field, wanted_same in (("same_partition_witness", True), ("different_partition_witness", False)):
                        part = pair.get(field)
                        exists = bool(same) if wanted_same else diff > 0
                        if (part is not None) != exists:
                            raise ValueError(f"pair witness presence mismatch for {a,b} {field}")
                        if part is not None:
                            if not feasible(data, part):
                                raise ValueError(f"pair witness is infeasible for {a,b} {field}")
                            rgs = partition_rgs(part, alphabet)
                            if rgs not in expected or ((rgs[i] == rgs[j]) is not wanted_same):
                                raise ValueError(f"pair witness is outside/contradicts relation for {a,b} {field}")
            if any(item.get("relation") == "forced_different" for item in pair_rows):
                raise ValueError("unrestricted result claims forced_different")
            if not expected:
                raise ValueError("valid consistent no-K input unexpectedly has empty family")
            full_set_matches += 1
            total_partitions += len(expected)
        except Exception as exc:
            case_errors.append(str(exc))
        if case_errors:
            per_case_errors[case_id] = case_errors

    status = "accepted_exact_full_set_gate" if not errors and not per_case_errors and full_set_matches == len(expected_specs) else "rejected_or_incomplete"
    report = {
        "schema_version": 1,
        "status": status,
        "provider_method": "unrestricted_solver_v2.solve; enumerate_partitions=True",
        "capture_attempt_id": cap.get("attempt_id"),
        "capture_execution_status": cap.get("execution_status"),
        "provider_rows": len(provider_rows),
        "expected_rows": len(expected_specs),
        "exact_full_sets_matched": full_set_matches,
        "total_compatible_partition_rows": total_partitions,
        "enumerated_partition_witnesses_replayed": witness_replays,
        "swap_edge_witnesses_replayed": edge_rows,
        "oracle_cases_used": sum(1 for spec in expected_specs if sha(canonical(spec[3])) in oracle_by_payload),
        "preflight_cases_directly_enumerated": sum(1 for spec in expected_specs if sha(canonical(spec[3])) not in oracle_by_payload),
        "errors": errors,
        "per_case_errors": per_case_errors,
        "provider_stdout_sha256": sha(stdout_raw),
        "oracle_sha256": sha(oracle_raw),
        "corpus_manifest_sha256": sha(manifest_raw),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if status == "accepted_exact_full_set_gate" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independently validate frozen C009 provider outputs against set partitions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import run_provider_gate_v2 as run


ROOT = run.ROOT
MANIFEST_PATH = ROOT / "corpus_v1" / "manifest.json"
ORACLE_PATH = ROOT / "oracle_v1.jsonl"
LEDGER_PATH = ROOT / "provider_gate_ledger_v2.jsonl"
RUN_SUMMARY_PATH = ROOT / "provider_gate_run_v2.json"
REPORT_PATH = ROOT / "provider_gate_validation_v1.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def set_insert_partitions(symbols: list[str]) -> list[list[list[str]]]:
    if not symbols:
        return [[]]
    head, *tail = symbols
    parts: list[list[list[str]]] = []
    for rest in set_insert_partitions(tail):
        for i in range(len(rest)):
            candidate = [block.copy() for block in rest]
            candidate[i].append(head)
            parts.append(candidate)
        parts.append([[head], *[block.copy() for block in rest]])
    return parts


def blocks_to_rgs(blocks: list[list[str]], alphabet: list[str]) -> tuple[int, ...]:
    owner = {symbol: block_id for block_id, block in enumerate(blocks) for symbol in block}
    canonical: dict[int, int] = {}
    labels: list[int] = []
    for symbol in alphabet:
        raw = owner[symbol]
        canonical.setdefault(raw, len(canonical))
        labels.append(canonical[raw])
    return tuple(labels)


def rgs_to_blocks(rgs: tuple[int, ...] | list[int], alphabet: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(blocks) <= label:
            blocks.append([])
        blocks[label].append(symbol)
    return blocks


def canonical_blocks(blocks: object, alphabet: list[str]) -> tuple[tuple[str, ...], ...]:
    if not isinstance(blocks, list) or any(not isinstance(block, list) or not block for block in blocks):
        raise ValueError("partition must be a list of nonempty blocks")
    if any(not isinstance(symbol, str) for block in blocks for symbol in block):
        raise ValueError("partition symbols must be strings")
    flattened = [symbol for block in blocks for symbol in block]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(alphabet):
        raise ValueError("partition blocks must cover each alphabet symbol exactly once")
    position = {symbol: i for i, symbol in enumerate(alphabet)}
    normalized = [tuple(sorted(block, key=position.__getitem__)) for block in blocks]
    normalized.sort(key=lambda block: position[block[0]])
    return tuple(normalized)


def project(word: str, block: set[str]) -> str:
    return "".join(symbol for symbol in word if symbol in block)


def feasible(data: dict, blocks: list[list[str]]) -> bool:
    allowed = set(data.get("allowed_k", range(1, len(data["alphabet"]) + 1)))
    if len(blocks) not in allowed:
        return False
    local_positive = [{project(word, set(block)) for word in data["positive"]} for block in blocks]
    return all(any(project(word, set(block)) not in language
                   for block, language in zip(blocks, local_positive))
               for word in data["negative"])


def compatible_set(data: dict) -> set[tuple[int, ...]]:
    alphabet = sorted(data["alphabet"])
    found = set()
    for blocks in set_insert_partitions(alphabet):
        if feasible(data, blocks):
            found.add(blocks_to_rgs(blocks, alphabet))
    return found


def replay_projection_witness(witness: object, data: dict) -> tuple[tuple[str, ...], ...]:
    if not isinstance(witness, dict):
        raise ValueError("projection witness must be an object")
    alphabet = sorted(data["alphabet"])
    blocks = [list(block) for block in canonical_blocks(witness.get("partition"), alphabet)]
    if not feasible(data, blocks):
        raise ValueError("witness partition is incompatible with sample")
    languages = [{project(word, set(block)) for word in data["positive"]} for block in blocks]
    listed_languages = witness.get("positive_projection_languages")
    expected_languages = [sorted(language) for language in languages]
    if listed_languages != expected_languages:
        raise ValueError("positive projection-language witness mismatch")
    positive_rows = witness.get("positive_witnesses")
    if not isinstance(positive_rows, list) or len(positive_rows) != len(data["positive"]):
        raise ValueError("positive projection witness list incomplete")
    seen_positive = set()
    for row in positive_rows:
        word = row.get("word")
        if word not in data["positive"] or word in seen_positive:
            raise ValueError("positive projection witness has wrong/duplicate word")
        seen_positive.add(word)
        expected = [project(word, set(block)) for block in blocks]
        if row.get("projections") != expected:
            raise ValueError("positive word projection mismatch")
    if seen_positive != set(data["positive"]):
        raise ValueError("positive projection witness words omitted")
    negative_rows = witness.get("negative_witnesses")
    if not isinstance(negative_rows, list) or len(negative_rows) != len(data["negative"]):
        raise ValueError("negative projection witness list incomplete")
    seen_negative = set()
    for row in negative_rows:
        word = row.get("word")
        if word not in data["negative"] or word in seen_negative:
            raise ValueError("negative projection witness has wrong/duplicate word")
        seen_negative.add(word)
        projections = [project(word, set(block)) for block in blocks]
        if row.get("projections") != projections:
            raise ValueError("negative word projection mismatch")
        rejected_by = [i for i, projection in enumerate(projections) if projection not in languages[i]]
        if not rejected_by or row.get("rejected_by_blocks") != rejected_by:
            raise ValueError("negative rejection witness is incorrect")
    if seen_negative != set(data["negative"]):
        raise ValueError("negative projection witness words omitted")
    return canonical_blocks(witness["partition"], alphabet)


def main() -> int:
    mismatches: list[dict[str, str]] = []
    def check(condition: bool, case_id: str, detail: str) -> None:
        if not condition:
            mismatches.append({"case_id": case_id, "detail": detail})

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    oracle_rows = [json.loads(line) for line in ORACLE_PATH.read_text(encoding="utf-8").splitlines()]
    oracle_by_id = {row["case_id"]: row for row in oracle_rows}
    ledger_rows = [json.loads(line) for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines()]
    run_summary = json.loads(RUN_SUMMARY_PATH.read_text(encoding="utf-8"))
    check(len(ledger_rows) == 129, "provider_batch", f"ledger rows={len(ledger_rows)}, expected=129")
    check(run_summary.get("captured_cases") == 129 and run_summary.get("status") == "accepted_capture_batch",
          "provider_batch", "runner summary not complete")
    check(sha_path(LEDGER_PATH) == run_summary.get("ledger_sha256"), "provider_batch", "ledger hash mismatch")
    check(len({row["case_id"] for row in ledger_rows}) == 129, "provider_batch", "duplicate/missing case IDs")
    check(len({row["attempt_id"] for row in ledger_rows}) == 129, "provider_batch", "duplicate attempt IDs")
    check(ledger_rows[0].get("recovered_from_orchestration_failure") is True,
          ledger_rows[0].get("case_id", "provider_batch"), "first output not marked as recovered")
    witness_replays = 0

    expected_source_hashes = dict(run.EXPECTED)
    expected_source_hashes.update({
        ROOT / "capture.py": sha_path(ROOT / "capture.py"),
        ROOT / "run_provider_gate_v2.py": run.sha(Path(run.__file__)),
    })
    for index, (case, ledger) in enumerate(zip(manifest["valid_cases"], ledger_rows)):
        case_id = case["case_id"]
        attempt_dir = ROOT / ledger["attempt_dir"]
        cap_manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
        cap_result = json.loads((attempt_dir / "result.json").read_text(encoding="utf-8"))
        stdout = (attempt_dir / "stdout.bin").read_bytes()
        stderr = (attempt_dir / "stderr.bin").read_bytes()
        check(ledger["case_id"] == case_id, case_id, "provider ledger order mismatch")
        check(ledger["input_sha256"] == case["input_sha256"], case_id, "provider ledger input hash mismatch")
        check(ledger["execution_status"] == "success" and ledger["exit_code"] == 0 and ledger["child_reaped"] is True,
              case_id, "provider capture was not clean success/reaped")
        check(cap_manifest.get("label") == f"provider-full-enumeration-{case_id}", case_id, "capture label mismatch")
        check(cap_result.get("stdout_sha256") == sha_bytes(stdout) == ledger.get("stdout_sha256"), case_id, "stdout hash mismatch")
        check(cap_result.get("stderr_sha256") == sha_bytes(stderr) == ledger.get("stderr_sha256"), case_id, "stderr hash mismatch")
        check(not stderr, case_id, "provider stderr nonempty")
        source_hashes = {str(Path(item["path"]).resolve()): item["sha256"] for item in cap_manifest["sources"]}
        per_case = dict(expected_source_hashes)
        per_case[ROOT / "corpus_v1" / case["path"]] = case["input_sha256"]
        if index == 0:
            per_case.pop(ROOT / "run_provider_gate_v2.py")
            per_case[ROOT / "run_provider_gate_v1.py"] = run.PREVIOUS_RUNNER_SHA
        check(all(source_hashes.get(str(path.resolve())) == digest for path, digest in per_case.items()),
              case_id, "capture source snapshot mismatch")
        check(ledger.get("source_snapshot_match") is True, case_id, "runner source snapshot flag false")
        try:
            provider = json.loads(stdout)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            mismatches.append({"case_id": case_id, "detail": f"malformed provider JSON: {exc!r}"})
            continue
        input_path = ROOT / "corpus_v1" / case["path"]
        data = json.loads(input_path.read_text(encoding="utf-8"))
        oracle = oracle_by_id[case_id]
        direct = compatible_set(data)
        oracle_set = {tuple(rgs) for rgs in oracle["compatible_rgs"]}
        check(direct == oracle_set, case_id, "independent set-insertion oracle no longer matches frozen RGS oracle")
        check(provider.get("complete") is True, case_id, "provider result incomplete")

        if not direct:
            check(provider.get("status") == "model_inconsistent", case_id, "zero-answer status mismatch")
            expected_zero_by_k = {str(k): 0 for k in sorted(data.get("allowed_k", range(1, len(data["alphabet"]) + 1)))}
            check(provider.get("partition_count") == 0 and provider.get("partition_count_by_k") == expected_zero_by_k,
                  case_id, "zero-answer count payload incorrect")
            check(provider.get("pair_relations") is None and provider.get("representative") is None
                  and provider.get("enumerated_partitions") is None, case_id, "zero-answer emitted vacuous witnesses")
            continue

        alphabet = sorted(data["alphabet"])
        expected_status = "identified_unique_partition" if len(direct) == 1 else "partial_ownership_identification"
        check(provider.get("status") == expected_status, case_id, "provider status mismatch")
        check(provider.get("alphabet") == alphabet, case_id, "provider alphabet mismatch")
        check(provider.get("partition_count") == len(direct) == oracle["partition_count"], case_id, "total partition count mismatch")
        by_k: dict[str, int] = {}
        for rgs in direct:
            key = str(max(rgs) + 1)
            by_k[key] = by_k.get(key, 0) + 1
        expected_by_k = {str(k): by_k.get(str(k), 0) for k in sorted(data.get("allowed_k", range(1, len(alphabet) + 1)))}
        check(provider.get("partition_count_by_k") == expected_by_k, case_id, "per-k exact count mismatch")
        check(provider.get("enumerated_partitions") is not None, case_id, "full enumeration missing")

        provider_set = set()
        try:
            for witness in provider["enumerated_partitions"]:
                normalized = replay_projection_witness(witness, data)
                witness_replays += 1
                rgs = blocks_to_rgs([list(block) for block in normalized], alphabet)
                provider_set.add(rgs)
        except (KeyError, TypeError, ValueError, AssertionError) as exc:
            mismatches.append({"case_id": case_id, "detail": f"enumerated projection witness invalid: {exc!r}"})
        check(len(provider["enumerated_partitions"]) == len(direct), case_id, "enumerated partition count mismatch")
        check(len(provider_set) == len(provider.get("enumerated_partitions", [])), case_id, "duplicate provider partitions")
        check(provider_set == direct, case_id, "complete provider partition set mismatch")

        try:
            replay_projection_witness(provider.get("representative"), data)
            witness_replays += 1
        except (KeyError, TypeError, ValueError, AssertionError) as exc:
            mismatches.append({"case_id": case_id, "detail": f"representative projection witness invalid: {exc!r}"})
        expected_pairs = {(alphabet[i], alphabet[j]) for i in range(len(alphabet)) for j in range(i + 1, len(alphabet))}
        pair_rows = provider.get("pair_relations")
        check(isinstance(pair_rows, list), case_id, "pair relation list missing")
        observed_pairs = set()
        oracle_pairs = {tuple(row["symbols"]): row for row in oracle["pair_relations"]}
        for pair in pair_rows or []:
            symbols = tuple(pair.get("symbols", []))
            observed_pairs.add(symbols)
            if symbols not in expected_pairs or len(symbols) != 2:
                mismatches.append({"case_id": case_id, "detail": f"invalid pair key {symbols!r}"})
                continue
            i, j = alphabet.index(symbols[0]), alphabet.index(symbols[1])
            same_count = sum(rgs[i] == rgs[j] for rgs in direct)
            different_count = len(direct) - same_count
            relation = "forced_same" if same_count == len(direct) else "forced_different" if same_count == 0 else "ambiguous"
            check(pair.get("same_partition_count") == same_count, case_id, f"same-pair count mismatch {symbols}")
            check(pair.get("different_partition_count") == different_count, case_id, f"different-pair count mismatch {symbols}")
            check(pair.get("relation") == relation, case_id, f"pair relation mismatch {symbols}")
            oracle_pair = oracle_pairs.get(symbols)
            check(oracle_pair is not None and oracle_pair["coown_count"] == same_count, case_id, f"oracle pair count mismatch {symbols}")
            for side, should_same in (("same", True), ("different", False)):
                key = f"{side}_partition_witness"
                witness = pair.get(key)
                exists = same_count > 0 if should_same else different_count > 0
                check((witness is not None) == exists, case_id, f"pair witness existence mismatch {symbols} {side}")
                if witness is not None:
                    try:
                        normalized = replay_projection_witness({
                            "partition": witness,
                            "positive_projection_languages": [sorted({project(p, set(b)) for p in data["positive"]}) for b in witness],
                            "positive_witnesses": [{"word": p, "projections": [project(p, set(b)) for b in witness]} for p in data["positive"]],
                            "negative_witnesses": [{
                                "word": n,
                                "projections": [project(n, set(b)) for b in witness],
                                "rejected_by_blocks": [bi for bi, b in enumerate(witness) if project(n, set(b)) not in {project(p, set(b)) for p in data["positive"]}],
                            } for n in data["negative"]],
                        }, data)
                        witness_replays += 1
                        rgs = blocks_to_rgs([list(block) for block in normalized], alphabet)
                        check(rgs in direct and ((rgs[i] == rgs[j]) is should_same), case_id,
                              f"pair witness projection/ownership mismatch {symbols} {side}")
                    except (KeyError, TypeError, ValueError, AssertionError) as exc:
                        mismatches.append({"case_id": case_id, "detail": f"pair witness invalid {symbols} {side}: {exc!r}"})
        check(observed_pairs == expected_pairs and len(observed_pairs) == len(pair_rows or []), case_id, "pair relation set incomplete or duplicated")

    report = {
        "schema_version": 1,
        "status": "accepted_independent_provider_gate" if not mismatches else "rejected_provider_gate_with_mismatches",
        "cases_planned": 129,
        "provider_calls": len(ledger_rows),
        "unique_case_ids": len({row["case_id"] for row in ledger_rows}),
        "complete_partition_sets_cross_checked": sum(1 for case in manifest["valid_cases"] if oracle_by_id[case["case_id"]]["complete"]),
        "direct_set_insert_partition_checks": 129,
        "provider_projection_witnesses_replayed": witness_replays,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "ledger_sha256": sha_path(LEDGER_PATH),
        "oracle_sha256": sha_path(ORACLE_PATH),
        "provider_batch_summary_sha256": sha_path(RUN_SUMMARY_PATH),
        "provider_solver_sha256": sha_path(run.SOLVER_PATH),
        "provider_cli_sha256": sha_path(run.CLI_PATH),
    }
    with REPORT_PATH.open("xb") as handle:
        handle.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if not mismatches and len(ledger_rows) == 129 else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze three preselected C007 v4 timing inputs from the validated corpus."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "timing_v1"
CASE_IDS = ("c007_gen_m04_013", "c007_gen_m06_000", "c007_gen_m08_000")
INPUT_SHA = "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b"
RGS_SHA = "a4216c69d0328419086096ff7b28f7efc39f98fb85ff904d798c5a6f54421281"
ADAPTIVE_ATTEMPT = "20261102T064415.454215Z_56c9af5e1d"
ADAPTIVE_STDOUT_SHA = "0e4a38c50bd95a8d9e9955aad059885abe038ae2620a34644f7b036a19ba080d"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    input_path = AUDIT / "corpus_v1" / "all_valid_inputs.jsonl"
    rgs_path = AUDIT / "oracle_v1" / "all_k_rgs.jsonl"
    adaptive_stdout_path = ROOT / "evidence" / "attempts" / ADAPTIVE_ATTEMPT / "stdout.bin"
    if digest(input_path.read_bytes()) != INPUT_SHA or digest(rgs_path.read_bytes()) != RGS_SHA:
        raise RuntimeError("frozen corpus or all-k oracle changed")
    if digest(adaptive_stdout_path.read_bytes()) != ADAPTIVE_STDOUT_SHA:
        raise RuntimeError("accepted v4 adaptive gate output changed")

    corpus = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line]
    oracle = {row["case_id"]: row for row in
              (json.loads(line) for line in rgs_path.read_text(encoding="utf-8").splitlines() if line)}
    adaptive = {}
    for line in adaptive_stdout_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("record_type") == "case_result":
            adaptive[row["case_id"]] = row["result"]

    computed_selection = []
    for alphabet_size, desired_fallback, desired_status in (
        (4, True, "multiple_maximal_exist"),
        (6, False, "finest_unique"),
        (8, False, "finest_unique"),
    ):
        candidates = []
        for source in corpus:
            case_id = source["case_id"]
            raw = source["input"]
            result = adaptive.get(case_id, {})
            if (len(raw["alphabet"]) != alphabet_size
                    or result.get("status") != desired_status
                    or result.get("staged_preprocessing", {}).get("fallback_used") is not desired_fallback):
                continue
            max_length = max((len(word) for group in (raw["positive"], raw["negative"])
                              for word in group), default=0)
            candidates.append((len(oracle[case_id]["compatible_binary_partitions"]),
                               max_length, case_id))
        if not candidates:
            raise RuntimeError(f"no candidate for preregistered class m={alphabet_size}")
        computed_selection.append(sorted(candidates, key=lambda item: (-item[0], -item[1], item[2]))[0][2])
    if tuple(computed_selection) != CASE_IDS:
        raise RuntimeError(f"deterministic candidate selection drifted: {computed_selection}")

    OUT.mkdir(parents=True, exist_ok=True)
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    cases = {}
    for case_id in CASE_IDS:
        source = next(row for row in corpus if row["case_id"] == case_id)
        raw = source["input"]
        cli_data = {"alphabet": list(raw["alphabet"]),
                    "positive": ["".join(word) for word in raw["positive"]],
                    "negative": ["".join(word) for word in raw["negative"]]}
        target = inputs_dir / f"{case_id}.json"
        encoded = (json.dumps(cli_data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        target.write_bytes(encoded)
        result = adaptive[case_id]
        o = oracle[case_id]
        cases[case_id] = {
            "path": f"inputs/{case_id}.json",
            "sha256": digest(encoded),
            "bytes": len(encoded),
            "payload_sha256": digest(canonical(raw)),
            "alphabet_size": len(raw["alphabet"]),
            "max_word_length": max((len(word) for group in (raw["positive"], raw["negative"])
                                    for word in group), default=0),
            "positive_count": len(raw["positive"]),
            "negative_count": len(raw["negative"]),
            "all_k_compatible_bipartitions": len(o["compatible_binary_partitions"]),
            "all_k_expected_status": ("finest_unique" if o["meet_compatible"] and len(o["meet"]) > 1
                                      else "one_block_only" if o["meet_compatible"]
                                      else "multiple_maximal_exist"),
            "all_k_expected_meet": o["meet"],
            "validated_v4_adaptive_path": result.get("metrics", {}).get("preprocessing_path"),
            "validated_v4_adaptive_fallback": result.get("staged_preprocessing", {}).get("fallback_used"),
            "validated_v4_adaptive_status": result.get("status"),
        }

    manifest = {
        "schema_version": 1,
        "status": "frozen_inputs_prepared_no_timing_run",
        "selection_rule": "one registered corpus row per m in {4,6,8}; choose an m=4 fallback/multiple-maximal case, then m=6 and m=8 swap-only unique-finest cases; within the class, maximize compatible binary cuts, then max word length, then lexicographic case_id; no timing observations used",
        "source_inputs_sha256": INPUT_SHA,
        "all_k_rgs_sha256": RGS_SHA,
        "selection_correctness_capture": ADAPTIVE_ATTEMPT,
        "selection_correctness_stdout_sha256": ADAPTIVE_STDOUT_SHA,
        "cases": cases,
    }
    manifest_path = OUT / "input_manifest_v1.json"
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    print(json.dumps({"status": manifest["status"], "manifest_path": str(manifest_path),
                      "manifest_sha256": digest(manifest_bytes), "cases": cases},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

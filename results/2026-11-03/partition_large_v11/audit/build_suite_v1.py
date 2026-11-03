#!/usr/bin/env python3
"""Build the immutable C011 audit corpus once; standard library only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
RESULTS = ROOT.parent.parent
C010 = RESULTS / "2026-11-02" / "partition_unrestricted_v10"
C010_AUDIT = C010 / "audit"
BASE = C010_AUDIT / "corpus_v1"
EXPECTED = {
    "c010_manifest": "82fbc29c1b960cd4b7ca3b177bba586cfdfb8b7cedad55fbade06334d3e13e4c",
    "c010_oracle": "f14d31d8c1dc2b69e742478b80407bf6ba1efc51e70a10ceb395b6f221206cb9",
    "c010_rgs_source": "392add401ccee213ace963203cef7aebde28fc0c19c9e1d030fdc0fd64f68273",
    "c010_solver": "4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502",
    "c010_cli": "3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa",
    "c010_capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def write_json_once(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2) + "\n").encode("utf-8")
    write_once(path, raw)
    return raw


def case_row(case_id: str, path: Path, raw: bytes, data: dict,
             category: str, expected_source: str) -> dict:
    return {
        "case_id": case_id,
        "category": category,
        "path": path.relative_to(AUDIT).as_posix(),
        "input_sha256": sha(raw),
        "canonical_payload_sha256": sha(canonical(data)),
        "alphabet_size": len(data["alphabet"]),
        "positive_count_raw": len(data["positive"]),
        "negative_count_raw": len(data["negative"]),
        "positive_count_unique": len(set(data["positive"])),
        "negative_count_unique": len(set(data["negative"])),
        "max_word_length": max((len(w) for w in data["positive"] + data["negative"]), default=0),
        "expected_source": expected_source,
    }


# Reuse, byte-for-byte, the accepted C010 125-case no-K corpus and direct-RGS oracle.
source_manifest_raw = (BASE / "manifest.json").read_bytes()
source_oracle_raw = (BASE / "oracle_v1.jsonl").read_bytes()
if sha(source_manifest_raw) != EXPECTED["c010_manifest"]:
    raise SystemExit("C010 manifest hash drift")
if sha(source_oracle_raw) != EXPECTED["c010_oracle"]:
    raise SystemExit("C010 direct-RGS oracle hash drift")
for rel, expected_key in (("oracle_independent_v1.py", "c010_rgs_source"),):
    if sha((C010_AUDIT / rel).read_bytes()) != EXPECTED[expected_key]:
        raise SystemExit(f"C010 oracle source drift: {rel}")
for rel, expected_key in (("implementation/unrestricted_solver_v2.py", "c010_solver"),
                          ("implementation/unrestricted_cli_v2.py", "c010_cli"),
                          ("audit/capture.py", "c010_capture")):
    if sha((C010 / rel).read_bytes()) != EXPECTED[expected_key]:
        raise SystemExit(f"C010 source drift: {rel}")

source_manifest = json.loads(source_manifest_raw.decode("utf-8"))
base_rows = []
for item in source_manifest["valid_cases"]:
    raw = (BASE / item["path"]).read_bytes()
    if sha(raw) != item["input_sha256"]:
        raise SystemExit(f"C010 case hash drift: {item['case_id']}")
    data = json.loads(raw.decode("utf-8"))
    dst = AUDIT / "cases" / "base_c010" / f"{item['case_id']}.json"
    write_once(dst, raw)
    row = case_row(item["case_id"], dst, raw, data, "reused_c010", "c010_direct_rgs_v1")
    row["source_input_path"] = f"C010/audit/corpus_v1/{item['path']}"
    row["source_input_sha256"] = item["input_sha256"]
    base_rows.append(row)
write_once(AUDIT / "c010_oracle_v1.jsonl", source_oracle_raw)

# Targeted full-set regressions. Duplicate labels are intentional in exactly one case.
targets = [
    ("interval_two_symbol_nonadjacent", {"alphabet": list("ab"), "positive": ["aab"], "negative": ["baa"]}),
    ("interval_binary_with_context", {"alphabet": list("abcde"), "positive": ["caabd"], "negative": ["cbaad"]}),
    ("interval_full_anagram_repeated", {"alphabet": list("ab"), "positive": ["aabb"], "negative": ["bbaa"]}),
    ("unsafe_three_symbol_acb_bca", {"alphabet": list("abc"), "positive": ["acb"], "negative": ["bca"]}),
    ("duplicate_label_idempotence", {"alphabet": list("abcd"), "positive": ["abac", "abac", "cd", "cd"], "negative": ["baac", "baac"]}),
    ("unary_boundary", {"alphabet": ["a"], "positive": ["aa"], "negative": ["a"]}),
    ("no_negative_epsilon_boundary", {"alphabet": list("abcde"), "positive": ["", "abc", "cba"], "negative": []}),
    ("graph_empty_no_label_boundary", {"alphabet": list("abcd"), "positive": [], "negative": []}),
    ("graph_empty_anagram_fallback", {"alphabet": list("abcd"), "positive": ["abcd"], "negative": ["dcba"]}),
    ("adjacent_swap_repeated_symbol_boundary", {"alphabet": list("ab"), "positive": ["aab"], "negative": ["aba"]}),
]
target_rows = []
for case_id, data in targets:
    path = AUDIT / "cases" / "targeted" / f"{case_id}.json"
    raw = canonical(data) + b"\n"
    write_once(path, raw)
    target_rows.append(case_row(case_id, path, raw, data, "targeted_regression", "c011_direct_rgs_v1"))

# One deliberately graph-empty fallback scale control, also included in full-set correctness.
fallback_data = {"alphabet": list("abcdefgh"), "positive": ["abcdefgh"], "negative": ["hgfedcba"]}
fallback_path = AUDIT / "cases" / "performance" / "unstructured_graph_empty_m8.json"
fallback_raw = canonical(fallback_data) + b"\n"
write_once(fallback_path, fallback_raw)
fallback_row = case_row("unstructured_graph_empty_m8", fallback_path, fallback_raw,
                        fallback_data, "performance_fallback_correctness", "c011_direct_rgs_v1")

# Performance inputs: three smaller profiles, then five scale cells.
def pair_context_data(contexts: int) -> dict:
    alphabet = list("abcdefgh")
    pairs = [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")]
    positives, negatives = [], []
    width = 18
    for x, y in pairs:
        for number in range(contexts):
            digits = []
            value = number
            for _ in range(width):
                digits.append(alphabet[value % len(alphabet)])
                value //= len(alphabet)
            context = "".join(digits)
            positives.append(x + y + context)
            negatives.append(y + x + context)
    return {"alphabet": alphabet, "positive": positives, "negative": negatives}


def long_pair_data(length: int) -> dict:
    alphabet = list("abcdefgh")
    pairs = [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")]
    context = "a" * (length - 2)
    return {"alphabet": alphabet,
            "positive": [x + y + context for x, y in pairs],
            "negative": [y + x + context for x, y in pairs]}


def structured_data(m: int, group_width: int = 8, variants: int = 4) -> tuple[dict, list[list[str]]]:
    alphabet = [chr(0xE000 + i) for i in range(m)]
    groups = [alphabet[i:i + group_width] for i in range(0, m, group_width)]
    positives, negatives = [], []
    for group in groups:
        for edge in range(group_width - 1):
            x, y = group[edge], group[edge + 1]
            for variant in range(variants):
                value = edge * variants + variant
                digits = []
                for _ in range(4):
                    digits.append(group[value % group_width])
                    value //= group_width
                context = "".join(digits)
                positives.append(x + y + context)
                negatives.append(y + x + context)
    return {"alphabet": alphabet, "positive": positives, "negative": negatives}, groups

performance_cases = []
perf_specs = [
    ("small_volume_128_each_m8", pair_context_data(32), "pair_context", [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
    ("small_volume_512_each_m8", pair_context_data(128), "pair_context", [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
    ("scale_volume_1000_each_m8", pair_context_data(250), "pair_context", [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
    ("small_long_word_10000_m8", long_pair_data(10_000), "pair_context", [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
    ("scale_long_word_100000_m8", long_pair_data(100_000), "pair_context", [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
]
for m in (64, 128):
    data, groups = structured_data(m)
    perf_specs.append((f"scale_structured_m{m}_groups8", data, "verified_group_chain", groups))
perf_specs.append(("scale_unstructured_fallback_m8", fallback_data, "direct_rgs_fallback", None))

for case_id, data, family_kind, groups in perf_specs:
    path = fallback_path if case_id == "scale_unstructured_fallback_m8" else AUDIT / "cases" / "performance" / f"{case_id}.json"
    if case_id != "scale_unstructured_fallback_m8":
        raw = canonical(data) + b"\n"
        write_once(path, raw)
    else:
        raw = fallback_raw
    row = case_row(case_id, path, raw, data, "performance", "c011_family_certificate_v1" if family_kind != "direct_rgs_fallback" else "c011_direct_rgs_v1")
    row.update({"family_kind": family_kind,
                "expected_atom_groups": groups,
                "expected_compatible_partition_count": None if groups is None else "Bell(%d)" % len(groups),
                "expected_sample_family": "all coarsenings of verified compatible atom groups" if groups else "full direct-RGS oracle"})
    performance_cases.append(row)

# Reused invalid and execution-control inputs for candidate controls, byte-for-byte.
controls_dir = AUDIT / "controls"
controls_dir.mkdir(parents=True, exist_ok=True)
for filename in ("invalid_cases.jsonl", "execution_controls_v1.json"):
    raw = (C010_AUDIT / "corpus_v1" / filename).read_bytes()
    write_once(controls_dir / filename, raw)

correctness_rows = base_rows + target_rows + [fallback_row]
correctness = {
    "schema_version": 1,
    "status": "frozen_inputs_before_any_timing",
    "source_cycle": "C010",
    "base_case_count": len(base_rows),
    "targeted_case_count": len(target_rows),
    "fallback_performance_case_added_to_exact_gate": fallback_row["case_id"],
    "valid_case_count": len(correctness_rows),
    "max_alphabet_size": max(row["alphabet_size"] for row in correctness_rows),
    "cases": correctness_rows,
    "source_anchors": EXPECTED,
    "source_manifest_sha256": sha(source_manifest_raw),
    "source_oracle_sha256": sha(source_oracle_raw),
}
write_json_once(AUDIT / "CORRECTNESS_MANIFEST_V1.json", correctness)

performance = {
    "schema_version": 1,
    "status": "frozen_inputs_before_any_timing",
    "runs_per_method_cell": 3,
    "fresh_process_per_run": True,
    "cli_default_mode": "expanded exact result; partition enumeration disabled",
    "cells": performance_cases,
    "time_budget_seconds_per_process": 30,
    "time_budget_seconds_per_method_all_in": 900,
    "memory_probe": {"separate_process_per_cell_and_method": True,
                     "tracemalloc_only": True,
                     "timeout_seconds_per_probe": 12,
                     "total_method_time_includes_probes": True},
    "fairness": {
        "compare_all_semantic_result_fields_and_witnesses": True,
        "candidate_only_allowed_addition": "mustlink_interval_certificates",
        "baseline_legacy_adjacent_swap_certificates_remain_separate": True,
        "record_raw_stdout_bytes_and_serialized_json_bytes": True,
        "no_output_reduction_claim_without_same_required_fields_and_witnesses": True,
    },
}
write_json_once(AUDIT / "PERFORMANCE_MANIFEST_V1.json", performance)

combined = {
    "schema_version": 1,
    "correctness_manifest": "audit/CORRECTNESS_MANIFEST_V1.json",
    "performance_manifest": "audit/PERFORMANCE_MANIFEST_V1.json",
    "correctness_case_count": len(correctness_rows),
    "performance_cell_count": len(performance_cases),
    "targeted_case_ids": [row["case_id"] for row in target_rows],
    "performance_cell_ids": [row["case_id"] for row in performance_cases],
    "generator_sha256": sha(Path(__file__).read_bytes()),
    "c010_commit": "0e0c52cc33825b9e820e083b8a90db2a9ab120d0",
}
write_json_once(AUDIT / "CORPUS_BUILD_RECEIPT_V1.json", combined)
print(json.dumps({"status": "built_once", "correctness_cases": len(correctness_rows),
                  "base_cases": len(base_rows), "targeted_cases": len(target_rows),
                  "performance_cells": len(performance_cases),
                  "generator_sha256": combined["generator_sha256"]}, sort_keys=True))
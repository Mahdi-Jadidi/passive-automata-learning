#!/usr/bin/env python3
"""Versioned correction of performance contexts after C011 oracle v1 assumption failure."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def pair_context_data(contexts: int) -> dict:
    alphabet = list("abcdefgh")
    pairs = [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")]
    positives, negatives = [], []
    context_width = 18  # 2**18 distinct pair-local contexts per pair.
    for x, y in pairs:
        for number in range(contexts):
            context = "".join((x, y)[(number >> bit) & 1] for bit in range(context_width))
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


prior_path = AUDIT / "PERFORMANCE_MANIFEST_V1.json"
prior_raw = prior_path.read_bytes()
prior = json.loads(prior_raw.decode("utf-8"))
if prior["status"] != "frozen_inputs_before_any_timing" or len(prior["cells"]) != 8:
    raise SystemExit("C011 performance v1 is not the expected frozen 8-cell manifest")
prior_by_id = {row["case_id"]: row for row in prior["cells"]}
new_cases = []

for case_id in prior["cell_ids"] if "cell_ids" in prior else [row["case_id"] for row in prior["cells"]]:
    prior_row = prior_by_id[case_id]
    if case_id == "small_volume_128_each_m8":
        data = pair_context_data(32)
    elif case_id == "small_volume_512_each_m8":
        data = pair_context_data(128)
    elif case_id == "scale_volume_1000_each_m8":
        data = pair_context_data(250)
    elif case_id in ("small_long_word_10000_m8", "scale_long_word_100000_m8"):
        data = json.loads((AUDIT / prior_row["path"]).read_text(encoding="utf-8"))
    else:
        data = json.loads((AUDIT / prior_row["path"]).read_text(encoding="utf-8"))
    raw = canonical(data) + b"\n"
    path = AUDIT / "cases" / "performance_v2" / f"{case_id}.json"
    write_once(path, raw)
    new_row = {key: value for key, value in prior_row.items()
               if key not in ("path", "input_sha256", "canonical_payload_sha256",
                              "positive_count_raw", "negative_count_raw",
                              "positive_count_unique", "negative_count_unique", "max_word_length")}
    new_row.update({
        "path": path.relative_to(AUDIT).as_posix(),
        "input_sha256": sha(raw),
        "canonical_payload_sha256": sha(canonical(data)),
        "positive_count_raw": len(data["positive"]),
        "negative_count_raw": len(data["negative"]),
        "positive_count_unique": len(set(data["positive"])),
        "negative_count_unique": len(set(data["negative"])),
        "max_word_length": max((len(w) for w in data["positive"] + data["negative"]), default=0),
    })
    if len(data["positive"]) != len(set(data["positive"])) or len(data["negative"]) != len(set(data["negative"])):
        raise AssertionError(f"duplicate words in performance case: {case_id}")
    if set(data["positive"]) & set(data["negative"]):
        raise AssertionError(f"conflicting labels in performance case: {case_id}")
    if len(data["alphabet"]) != len(set(data["alphabet"])) or any(len(ch) != 1 for ch in data["alphabet"]):
        raise AssertionError(f"invalid alphabet in performance case: {case_id}")
    new_cases.append(new_row)

manifest = {
    "schema_version": 1,
    "status": "revised_frozen_inputs_before_timing",
    "supersedes": "audit/PERFORMANCE_MANIFEST_V1.json",
    "superseded_manifest_sha256": sha(prior_raw),
    "revision_reason": "v1 family auditor assumed the atom partition was feasible for unrestricted pair-local contexts; v2 contexts are restricted to each intended pair so atom feasibility has a direct local proof.",
    "generator_sha256": sha(Path(__file__).read_bytes()),
    "runs_per_method_cell": prior["runs_per_method_cell"],
    "fresh_process_per_run": prior["fresh_process_per_run"],
    "cli_default_mode": prior["cli_default_mode"],
    "time_budget_seconds_per_process": prior["time_budget_seconds_per_process"],
    "time_budget_seconds_per_method_all_in": prior["time_budget_seconds_per_method_all_in"],
    "memory_probe": prior["memory_probe"],
    "fairness": prior["fairness"],
    "cell_order": [row["case_id"] for row in new_cases],
    "cells": new_cases,
}
manifest_raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
write_once(AUDIT / "PERFORMANCE_MANIFEST_V2.json", manifest_raw)
receipt = {
    "schema_version": 1,
    "status": "built_once_under_captured_attempt",
    "cell_count": len(new_cases),
    "cell_ids": [row["case_id"] for row in new_cases],
    "manifest_sha256": sha(manifest_raw),
    "generator_sha256": manifest["generator_sha256"],
    "v1_manifest_sha256": sha(prior_raw),
}
receipt_raw = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
write_once(AUDIT / "PERFORMANCE_BUILD_RECEIPT_V2.json", receipt_raw)
print(json.dumps(receipt, sort_keys=True))
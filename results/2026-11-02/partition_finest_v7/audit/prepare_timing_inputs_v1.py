#!/usr/bin/env python3
"""Prepare three provider-only JSON cells for a future timing proposal."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "timing_proposal_v1" / "inputs"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def convert(data):
    alphabet = data["alphabet"]
    if any(not isinstance(symbol, str) or len(symbol) != 1 for symbol in alphabet):
        raise ValueError("provider CLI v1 accepts one-character symbols")
    return {"alphabet": list(alphabet),
            "positive": ["".join(word) for word in data["positive"]],
            "negative": ["".join(word) for word in data["negative"]]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    corpus_rows = [json.loads(line) for line in (HERE / "corpus_v1" / "all_valid_inputs.jsonl")
                   .read_text(encoding="utf-8").splitlines() if line]
    selected_ids = ("ctrl_partial_meet_ambiguity", "ctrl_unique_finest_3plus")
    selected = {row["case_id"]: row for row in corpus_rows if row["case_id"] in selected_ids}
    extra = json.loads((HERE / "targeted_empty_graph_v1.jsonl").read_text(encoding="utf-8").splitlines()[0])
    selected[extra["case_id"]] = extra
    if set(selected) != set(selected_ids) | {"ctrl_empty_must_link_unique_3"}:
        raise AssertionError("timing input selection is incomplete")

    truth = {}
    all_oracle = {row["case_id"]: row for row in (HERE / "oracle_v1" / "all_k_rgs.jsonl")
                  .read_text(encoding="utf-8").splitlines() if row}
    extra_oracle = json.loads((HERE / "targeted_empty_graph" / "oracle_rgs_v1.jsonl")
                              .read_text(encoding="utf-8").splitlines()[0])
    all_oracle[extra_oracle["case_id"]] = extra_oracle
    files = {}
    for case_id, row in selected.items():
        data = convert(row["input"])
        encoded = (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        path = OUT / (case_id + ".json")
        if path.exists():
            raise FileExistsError(f"refusing to overwrite prepared timing input {path}")
        path.write_bytes(encoded)
        oracle = all_oracle[case_id]
        truth[case_id] = {"input_payload_sha256": sha(canonical(row["input"]).encode("utf-8")),
                          "sample_finest": oracle["meet"],
                          "unique_finest": oracle["meet_compatible"],
                          "maximal_frontier_count": len(oracle["maximal_refinement_frontier"]),
                          "compatible_binary_count": len(oracle["compatible_binary_partitions"])}
        files[case_id] = {"path": path.name, "bytes": len(encoded), "sha256": sha(encoded)}
    manifest = {
        "schema_version": 1,
        "source_corpus_sha256": sha((HERE / "corpus_v1" / "all_valid_inputs.jsonl").read_bytes()),
        "extra_addendum_sha256": sha((HERE / "targeted_empty_graph_v1.jsonl").read_bytes()),
        "oracle_all_k_sha256": sha((HERE / "oracle_v1" / "all_k_rgs.jsonl").read_bytes()),
        "extra_oracle_sha256": sha((HERE / "targeted_empty_graph" / "oracle_rgs_v1.jsonl").read_bytes()),
        "input_files": files,
        "oracle_targets": truth,
        "provider_input_fields": ["alphabet", "positive", "negative"],
        "timing_status": "prepared_only; master_GO_required",
    }
    manifest_path = OUT.parent / "input_manifest_v1.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite timing input manifest {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    print(json.dumps({"inputs": len(files), "manifest_sha256": sha(manifest_path.read_bytes()),
                      "manifest": str(manifest_path)}, sort_keys=True))


if __name__ == "__main__":
    main()

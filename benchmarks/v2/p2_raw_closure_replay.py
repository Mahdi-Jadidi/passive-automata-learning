"""Reproduce the producer raw-closure phase only; no ledger/journal replay.

This intentionally does not import the bounded-deletion verifier or RegisteredLedger.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

CORE_SOURCE_COMMIT = "796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33"
HARDENED_PROOF_COMMIT_NOT_IMPORTED = "cf5a007571853b6cdf6259fa2a9a95f5c1e351f8"
CORE_BLOBS = {
    "core.py": "997304c3adce9d3148d454b079639575f419ba0e",
    "component_closure.py": "97844bc266556cc04cd54a75c0d57dc00d6709ea",
    "sparse_analysis.py": "f773cc1c6b1a852193ba2afb75aa2fce4941a5c2",
    "schema.py": "65a7522a8442a184c14f7a0fa74fc307ce60229f",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def unique_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError(f"duplicate JSON key: {k}")
        obj[k] = v
    return obj


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--expected-input-sha256", required=True)
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=30.0)
    p.add_argument("--memory-mib", type=int, default=1536)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    process_started = time.perf_counter()
    result = {"schema": "p2-raw-closure-observation/1", "status": "INCOMPLETE",
              "core_source_commit": CORE_SOURCE_COMMIT,
              "hardened_proof_commit_not_imported": HARDENED_PROOF_COMMIT_NOT_IMPORTED,
              "phase": "RAW_CLOSURE_ONLY", "ledger_ingestion": "NOT RUN",
              "independent_journal_replay": "NOT RUN", "bounded_deletion_verifier_imported": False}
    try:
        cap = a.memory_mib * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        result["resource_limit_applied_before_input"] = True
        input_bytes = a.input.read_bytes()
        result["input_sha256"] = sha256(input_bytes)
        result["input_bytes"] = len(input_bytes)
        if result["input_sha256"] != a.expected_input_sha256:
            raise ValueError("input SHA-256 mismatch")
        data = json.loads(input_bytes, object_pairs_hook=unique_object)
        if type(data) is not dict or set(data) != {"alphabet", "positive", "negative"}:
            raise ValueError("raw input must contain exactly alphabet, positive, negative")
        core_dir = a.repo_root / "implementation/partition_feedback_final/selector_v2"
        actual_blobs = {}
        for name, expected in CORE_BLOBS.items():
            actual = git_blob_sha1((core_dir / name).read_bytes())
            actual_blobs[name] = actual
            if actual != expected:
                raise ValueError(f"source blob mismatch for {name}: {actual}")
        result["core_source_blobs"] = actual_blobs
        sys.path.insert(0, str(a.repo_root / "implementation/partition_feedback_final"))
        from selector_v2.core import Budget, PartitionRef, Sample
        from selector_v2 import component_closure, sparse_analysis, schema
        sample = Sample.from_input(data)
        result["sample_digest"] = sample.sample_digest
        result["input_dimensions"] = {
            "alphabet": len(sample.alphabet), "positives": len(sample.positive),
            "negatives": len(sample.negative),
            "occurrences": sum(map(len, sample.positive + sample.negative)),
            "max_word_length": max(map(len, sample.positive + sample.negative), default=0),
        }
        exact_checks = 0
        original_equal = sparse_analysis._equal
        def counted_equal(x, y, owner, group):
            nonlocal exact_checks
            exact_checks += 1
            return original_equal(x, y, owner, group)
        sparse_analysis._equal = counted_equal
        budget = Budget(seconds=a.seconds)
        started = time.perf_counter()
        closure = component_closure.component_closure(sample, budget)
        closure_elapsed = time.perf_counter() - started
        records = list(closure["records"])
        structural = None
        raw_check_elapsed = 0.0
        if closure["state"] != "LABEL_CONFLICT":
            raw_check_started = time.perf_counter()
            structural = component_closure.structural_record(
                sample, PartitionRef(tuple(closure["owner"]))
            )
            raw_check_elapsed = time.perf_counter() - raw_check_started
            records.append(structural)
        epoch_records = [r for r in closure["records"] if r["kind"] == "COMPONENT_EPOCH"]
        facts = sum(len(r["payload"]["facts"]) for r in epoch_records)
        edges = sum(len(r["payload"]["edges"]) for r in epoch_records)
        result.update({
            "raw_closure_state": closure["state"],
            "epochs": len(epoch_records),
            "deletion_facts": facts,
            "forced_edges": edges,
            "work_units": budget.used,
            "deletion_exact_checks": exact_checks,
            "quotient_blocks": len(set(closure["owner"])),
            "producer_raw_check": None if structural is None else structural["payload"]["compatible"],
            "closure_elapsed_seconds": closure_elapsed,
            "raw_check_elapsed_seconds": raw_check_elapsed,
            "python_optimize": sys.flags.optimize,
            "address_space_cap_mib": a.memory_mib,
            "peak_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        })
        (a.output / "scope.json").write_bytes(schema.canonical(schema.scope(sample)) + b"\n")
        record_bytes = schema.canonical(records) + b"\n"
        (a.output / "raw-records.json").write_bytes(record_bytes)
        result["scope_sha256"] = sha256((a.output / "scope.json").read_bytes())
        result["raw_records_sha256"] = sha256(record_bytes)
        result["raw_records_bytes"] = len(record_bytes)
        result["elapsed_seconds"] = time.perf_counter() - process_started
        if closure["state"] == "FIXPOINT":
            result["status"] = "RAW_CLOSURE_COMPLETE"
        elif closure["state"] == "LABEL_CONFLICT":
            result["status"] = "RAW_LABEL_CONFLICT"
        else:
            result["status"] = "INCOMPLETE"
    except MemoryError:
        result["elapsed_seconds"] = time.perf_counter() - process_started
        result["status"] = "MEMORY_ERROR"
        result["error"] = "MemoryError during raw closure phase"
    except Exception as exc:
        result["elapsed_seconds"] = time.perf_counter() - process_started
        result["status"] = "INVALID"
        result["error"] = f"{type(exc).__name__}: {exc}"
    result["peak_rss_kib"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    result["operational_status"] = "INCOMPLETE"
    (a.output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in ("RAW_CLOSURE_COMPLETE", "RAW_LABEL_CONFLICT", "INCOMPLETE", "MEMORY_ERROR") else 1


if __name__ == "__main__":
    raise SystemExit(main())

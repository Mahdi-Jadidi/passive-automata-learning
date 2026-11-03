#!/usr/bin/env python3
"""Independent full-family, witness, interval and control replay for C011."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
C010 = ROOT.parent.parent / "2026-11-02" / "partition_unrestricted_v10"
CHECKER = C010 / "audit" / "validate_provider_v2.py"
spec = importlib.util.spec_from_file_location("accepted_c010_checker", CHECKER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalize(data):
    return {"alphabet": sorted(data["alphabet"]), "positive": sorted(set(data["positive"])),
            "negative": sorted(set(data["negative"]))}


def check_edges(data, result, expected):
    alphabet = data["alphabet"]
    parent = {x: x for x in alphabet}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def join(x, y):
        a, b = find(x), find(y)
        parent[max(a, b)] = min(a, b)
    legacy = result.get("swap_edge_witnesses")
    intervals = result.get("binary_interval_must_link_certificates")
    if not isinstance(legacy, list) or not isinstance(intervals, list):
        raise ValueError("certificate list absent")
    for row in legacy:
        p, n = row.get("positive"), row.get("negative")
        ij, pair = row.get("positions"), row.get("symbols")
        if p not in data["positive"] or n not in data["negative"]:
            raise ValueError("legacy edge polarity/source mismatch")
        if not isinstance(ij, list) or len(ij) != 2:
            raise ValueError("legacy positions malformed")
        i, j = ij
        if type(i) is not int or type(j) is not int or j != i + 1 or i < 0 or j >= len(p) or len(p) != len(n):
            raise ValueError("legacy positions invalid")
        chars = list(p)
        chars[i], chars[j] = chars[j], chars[i]
        if p[i] == p[j] or "".join(chars) != n or pair != [p[i], p[j]]:
            raise ValueError("legacy swap replay failed")
        join(*pair)
    observed_pairs = set()
    for row in intervals:
        p, n = row.get("positive"), row.get("negative")
        bounds, pair = row.get("interval"), row.get("symbols")
        if p not in data["positive"] or n not in data["negative"] or p == n or len(p) != len(n):
            raise ValueError("interval polarity/source/length mismatch")
        if not isinstance(bounds, list) or len(bounds) != 2 or not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("interval record malformed")
        lo, hi = bounds
        if type(lo) is not int or type(hi) is not int or not 0 <= lo < hi <= len(p):
            raise ValueError("interval bounds invalid")
        if len(set(pair)) != 2 or any(x not in alphabet for x in pair):
            raise ValueError("interval pair invalid")
        if p[:lo] != n[:lo] or p[hi:] != n[hi:] or row.get("left") != p[:lo] or row.get("right") != p[hi:]:
            raise ValueError("exact interval contexts do not replay")
        if set(p[lo:hi]) != set(pair) or set(n[lo:hi]) != set(pair):
            raise ValueError("interval is not exactly binary")
        counts = {x: p[lo:hi].count(x) for x in pair}
        if counts != {x: n[lo:hi].count(x) for x in pair} or row.get("counts") != counts:
            raise ValueError("binary interval counts do not replay")
        if row.get("type") != "binary_anagram_interval":
            raise ValueError("interval certificate type mismatch")
        observed_pairs.add(tuple(sorted(pair)))
        join(*pair)
    # Independent exhaustive short-word coverage; all frozen gate words have
    # length <=8. Legacy certificates cannot hide a missing interval edge.
    required_pairs = set()
    for p in data["positive"]:
        for n in data["negative"]:
            if len(p) != len(n):
                continue
            for lo in range(len(p)):
                for hi in range(lo + 1, len(p) + 1):
                    pair = set(p[lo:hi])
                    if (len(pair) == 2 and p[:lo] == n[:lo] and p[hi:] == n[hi:]
                            and set(n[lo:hi]) == pair
                            and all(p[lo:hi].count(x) == n[lo:hi].count(x) for x in pair)):
                        required_pairs.add(tuple(sorted(pair)))
    if observed_pairs != required_pairs:
        raise ValueError(f"binary extractor pair coverage differs: missing={required_pairs-observed_pairs}, extra={observed_pairs-required_pairs}")
    groups = {}
    for symbol in alphabet:
        groups.setdefault(find(symbol), []).append(symbol)
    atoms = sorted(groups.values())
    if old.partition_rgs(result.get("atom_partition"), alphabet) != old.partition_rgs(atoms, alphabet):
        raise ValueError("atom partition differs from replayed certificate components")
    for pair in observed_pairs:
        i, j = map(alphabet.index, pair)
        if any(rgs[i] != rgs[j] for rgs in expected):
            raise ValueError("certificate edge contradicts exact family")
    return atoms, len(legacy), len(intervals), len(required_pairs)


def check_complete(data, result, expected, case_id):
    alphabet = data["alphabet"]
    m = len(alphabet)
    by_k = {str(k): sum(max(rgs) + 1 == k for rgs in expected) for k in range(1, m + 1)}
    if result.get("complete") is not True or result.get("alphabet") != alphabet:
        raise ValueError("complete/alphabet mismatch")
    wanted = "identified_unique_partition" if len(expected) == 1 else "partial_ownership_identification"
    if result.get("status") != wanted or result.get("partition_count") != len(expected) or result.get("partition_count_by_k") != by_k:
        raise ValueError("status/count/spectrum mismatch")
    kmax = max(k for k in range(1, m + 1) if by_k[str(k)])
    if result.get("k_max_compatible") != kmax:
        raise ValueError("exact k_max_compatible mismatch")
    atoms, legacy, intervals, coverage = check_edges(data, result, expected)
    upper = result.get("k_max_upper_bound")
    if type(upper) is not int or not kmax <= upper <= len(atoms):
        raise ValueError("k upper bound internally invalid")
    if result.get("atom_projection_feasible") is not old.feasible(data, atoms):
        raise ValueError("atom feasibility mismatch")
    family = result.get("enumerated_partitions")
    if not isinstance(family, list):
        raise ValueError("full family enumeration absent")
    seen = set()
    projections = 0
    for witness in family:
        old.check_witness(data, witness)
        seen.add(old.partition_rgs(witness["partition"], alphabet))
        projections += 1
    if len(seen) != len(family) or seen != expected:
        raise ValueError(f"exact family differs: missing={len(expected-seen)}, extra={len(seen-expected)}")
    old.check_witness(data, result.get("representative"))
    if old.partition_rgs(result["representative"]["partition"], alphabet) not in expected:
        raise ValueError("representative outside family")
    rows = result.get("pair_relations")
    if not isinstance(rows, list) or len(rows) != m * (m-1) // 2:
        raise ValueError("pair table row count mismatch")
    pair_map = {tuple(row.get("symbols", [])): row for row in rows}
    if len(pair_map) != len(rows):
        raise ValueError("duplicate pair rows")
    cache = {}
    references = 0
    for i, j in itertools.combinations(range(m), 2):
        key = (alphabet[i], alphabet[j])
        row = pair_map[key]
        same = sum(rgs[i] == rgs[j] for rgs in expected)
        diff = len(expected) - same
        relation = "forced_same" if diff == 0 else "ambiguous"
        if row.get("relation") != relation or row.get("same_partition_count") != same or row.get("different_partition_count") != diff:
            raise ValueError(f"pair count/relation mismatch: {key}")
        for field, together, exists in (("same_partition_witness", True, same > 0), ("different_partition_witness", False, diff > 0)):
            part = row.get(field)
            if (part is not None) != exists:
                raise ValueError(f"pair witness presence mismatch: {key}, {field}")
            if part is not None:
                references += 1
                rgs = old.partition_rgs(part, alphabet)
                if rgs not in cache:
                    cache[rgs] = old.feasible(data, part)
                if not cache[rgs] or rgs not in expected or (rgs[i] == rgs[j]) is not together:
                    raise ValueError(f"pair witness fails replay/relation: {key}, {field}")
    certs = result["binary_interval_must_link_certificates"]
    if case_id == "hash_collision_keep_all_contexts" and not any(c.get("positive") == "dabd" and c.get("negative") == "dbad" and set(c.get("symbols", [])) == {"a", "b"} and c.get("interval") == [1, 3] for c in certs):
        raise ValueError("required second collision-class interval certificate absent")
    if case_id == "hash_collision_exact_context_guard":
        if any(set(c.get("symbols", [])) == {"a", "b"} for c in certs):
            raise ValueError("unequal-context collision produced ab interval")
    return {"projection_witnesses": projections + 1, "pair_witness_references": references,
            "distinct_pair_feasibility_evaluations": len(cache), "legacy_certificates": legacy,
            "interval_certificates": intervals, "binary_pair_coverage": coverage}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    plan = json.loads((args.run / "run_manifest.json").read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in (args.run / "ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    oracle = {x["case_id"]: x for x in (json.loads(line) for line in (AUDIT / "FULL_CORRECTNESS_ORACLE_V3.jsonl").read_text(encoding="utf-8").splitlines())}
    expected_specs = plan["specs"]
    errors, censored, completed = {}, [], []
    totals = {key: 0 for key in ("projection_witnesses", "pair_witness_references", "distinct_pair_feasibility_evaluations", "legacy_certificates", "interval_certificates", "binary_pair_coverage")}
    if len(rows) != len(expected_specs) or [r["case_id"] for r in rows] != [r["case_id"] for r in expected_specs]:
        errors["job_set"] = "ledger does not equal frozen run plan"
    for row, item in zip(rows, expected_specs):
        key = item["case_id"]
        try:
            attempt = AUDIT / "attempts" / row["attempt_id"]
            cap = json.loads((attempt / "result.json").read_text(encoding="utf-8"))
            manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
            raw = (attempt / "stdout.bin").read_bytes()
            err = (attempt / "stderr.bin").read_bytes()
            if cap["stdout_sha256"] != sha(raw) or cap["stderr_sha256"] != sha(err):
                raise ValueError("captured stream hash mismatch")
            if cap.get("child_reaped") is not True or cap.get("cleanup_error"):
                raise ValueError("child cleanup failure")
            source_map = {r["path"]: r["sha256"] for r in manifest["sources"]}
            for path, digest in plan["source_hashes"].items():
                if source_map.get(path) != digest:
                    raise ValueError(f"capture source hash mismatch: {path}")
            input_path = Path(item["input"])
            if sha(input_path.read_bytes()) != item["input_sha256"] or source_map.get(str(input_path)) != item["input_sha256"]:
                raise ValueError("input snapshot/current hash mismatch")
            if cap["execution_status"] in {"timed_out", "interrupted"}:
                censored.append(key)
                continue
            result = json.loads(raw.decode("utf-8"))
            if item["kind"] == "invalid":
                if cap.get("exit_code") != 2 or result.get("status") != "invalid_input":
                    raise ValueError("invalid input not rejected")
            elif item["kind"] in {"expired", "interrupt"}:
                if cap.get("exit_code") != 3 or result.get("status") != "incomplete" or result.get("complete") is not False:
                    raise ValueError("incomplete control did not return nonfinal status")
                if any(result.get(f) is not None for f in ("partition_count", "partition_count_by_k", "pair_relations", "representative", "enumerated_partitions")):
                    raise ValueError("incomplete control made final claim")
                if item["kind"] == "interrupt":
                    progress = result.get("audit_injection", {})
                    if progress.get("injected") is not True or progress.get("positive_interval_records", 0) < 1 or result.get("metrics", {}).get("positive_interval_records", 0) < 1:
                        raise ValueError("interruption lacked observable extraction progress")
            elif result.get("complete") is not True:
                if result.get("status") != "incomplete" or any(result.get(f) is not None for f in ("partition_count", "partition_count_by_k", "pair_relations", "representative", "enumerated_partitions")):
                    raise ValueError("censored result made final claim")
                censored.append(key)
                continue
            else:
                if cap.get("execution_status") != "success" or cap.get("exit_code") != 0:
                    raise ValueError("complete output process failed")
                data = normalize(json.loads(input_path.read_text(encoding="utf-8-sig")))
                source_id = item.get("oracle_case_id", key)
                expected = ({tuple(x) for x in oracle[source_id]["compatible_rgs"]}
                            if source_id in oracle else old.direct_expected(data))
                counts = check_complete(data, result, expected, source_id)
                for field, value in counts.items():
                    totals[field] += value
            completed.append(key)
        except Exception as exc:
            errors[key] = str(exc)
    accepted = not errors and not censored and len(completed) == len(expected_specs)
    report = {"schema_version": 1, "status": "accepted_exact_correctness_and_controls" if accepted else "rejected_or_incomplete",
              "planned_jobs": len(expected_specs), "ledger_jobs": len(rows), "validated_jobs": len(completed),
              "full_corpus_cases": 138, "censored": censored, "errors": errors, **totals,
              "provider_timing_claim": False, "benchmark_authorized": False}
    raw_report = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with (args.run / "validation_report.json").open("xb") as stream:
        stream.write(raw_report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())

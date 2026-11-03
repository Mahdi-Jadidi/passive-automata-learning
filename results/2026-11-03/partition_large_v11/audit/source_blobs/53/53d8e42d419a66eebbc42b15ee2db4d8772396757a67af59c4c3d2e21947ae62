#!/usr/bin/env python3
"""Independent read-only validation of the C011 V3 oracle artifacts."""
from __future__ import annotations

from itertools import combinations
import hashlib
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canon(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def rgs_words(m: int):
    if m < 1:
        return
    def visit(prefix: list[int], maximum: int):
        if len(prefix) == m:
            yield tuple(prefix)
            return
        for label in range(maximum + 2):
            prefix.append(label)
            yield from visit(prefix, max(maximum, label))
            prefix.pop()
    yield from visit([0], 0)


def blocks(rgs: tuple[int, ...], alphabet: list[str]) -> list[set[str]]:
    out: list[set[str]] = []
    for symbol, label in zip(alphabet, rgs):
        while len(out) <= label:
            out.append(set())
        out[label].add(symbol)
    return out


def feasible(alphabet: list[str], positives: list[str], negatives: list[str],
             rgs: tuple[int, ...]) -> bool:
    parts = blocks(rgs, alphabet)
    languages = [{"".join(ch for ch in word if ch in part) for word in positives}
                 for part in parts]
    for word in negatives:
        if not any("".join(ch for ch in word if ch in part) not in language
                   for part, language in zip(parts, languages)):
            return False
    return True


def direct_family(data: dict) -> tuple[list[str], list[str], list[str], list[tuple[int, ...]]]:
    alphabet = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    if set(positives) & set(negatives):
        raise AssertionError("contradictory labels in frozen corpus")
    family = [rgs for rgs in rgs_words(len(alphabet))
              if feasible(alphabet, positives, negatives, rgs)]
    return alphabet, positives, negatives, family


def adjacent_swap(p: str, n: str):
    if len(p) != len(n):
        return None
    diff = [i for i, (x, y) in enumerate(zip(p, n)) if x != y]
    if len(diff) != 2 or diff[1] != diff[0] + 1:
        return None
    i, j = diff
    if p[i] == n[j] and p[j] == n[i] and p[i] != p[j]:
        return tuple(sorted((p[i], p[j])))
    return None


def bell_rows(n: int):
    row = [1] + [0] * n
    bell = [1]
    for size in range(1, n + 1):
        nxt = [0] * (n + 1)
        for k in range(1, size + 1):
            nxt[k] = row[k - 1] + k * row[k]
        row = nxt
        bell.append(sum(row))
    return bell, row


def main() -> int:
    correctness = json.loads((AUDIT / "CORRECTNESS_MANIFEST_V2.json").read_text(encoding="utf-8"))
    perf = json.loads((AUDIT / "PERFORMANCE_MANIFEST_V2.json").read_text(encoding="utf-8"))
    receipt = json.loads((AUDIT / "ORACLE_FREEZE_RECEIPT_V3.json").read_text(encoding="utf-8"))
    full_path = AUDIT / "FULL_CORRECTNESS_ORACLE_V3.jsonl"
    extension_path = AUDIT / "C011_RGS_ORACLE_V3.jsonl"
    cert_path = AUDIT / "PERFORMANCE_FAMILY_CERTIFICATES_V3.json"
    full_raw = full_path.read_bytes()
    ext_raw = extension_path.read_bytes()
    cert_raw = cert_path.read_bytes()
    if sha(full_raw) != receipt["full_oracle_sha256"] or sha(ext_raw) != receipt["rgs_extension_sha256"]:
        raise AssertionError("oracle output hash mismatch")
    if sha(cert_raw) != receipt["family_certificate_sha256"]:
        raise AssertionError("family certificate hash mismatch")
    full_rows = [json.loads(line) for line in full_raw.decode("utf-8").splitlines()]
    new_rows = [json.loads(line) for line in ext_raw.decode("utf-8").splitlines()]
    expected_ids = {row["case_id"] for row in correctness["cases"]}
    by_id = {row["case_id"]: row for row in full_rows}
    if len(full_rows) != 138 or len(by_id) != 138 or set(by_id) != expected_ids:
        raise AssertionError("full oracle IDs/count do not match 138 frozen correctness rows")
    if len(new_rows) != 13 or len({row["case_id"] for row in new_rows}) != 13:
        raise AssertionError("new direct-RGS extension must contain exactly 13 unique cases")

    direct_checked = []
    for case in correctness["cases"]:
        row = by_id[case["case_id"]]
        raw = (AUDIT / case["path"]).read_bytes()
        data = json.loads(raw.decode("utf-8"))
        alphabet, positives, negatives, family = direct_family(data)
        if len(alphabet) > 8:
            raise AssertionError("full direct RGS validation unexpectedly exceeds m=8")
        if case["expected_source"] != "c010_direct_rgs_v1":
            if row["raw_input_sha256"] != sha(raw):
                raise AssertionError(f"new oracle input hash mismatch: {case['case_id']}")
            actual = {tuple(value) for value in row["compatible_rgs"]}
            if actual != set(family) or len(actual) != len(row["compatible_rgs"]):
                raise AssertionError(f"full family mismatch: {case['case_id']}")
            expected_by_k = {str(k): sum(max(rgs) + 1 == k for rgs in family)
                             for k in range(1, len(alphabet) + 1)}
            if row["partition_count"] != len(family) or row["partition_count_by_k"] != expected_by_k:
                raise AssertionError(f"family spectrum mismatch: {case['case_id']}")
            direct_checked.append(case["case_id"])
        else:
            # C010 rows were already independently accepted; preserve their exact
            # source hash relation and recheck their advertised families here.
            if row["input_sha256"] != sha(canon(data)):
                raise AssertionError(f"reused C010 input hash mismatch: {case['case_id']}")
            if len(family) != row["partition_count"]:
                raise AssertionError(f"reused C010 family count drift: {case['case_id']}")
            if {tuple(value) for value in row["compatible_rgs"]} != set(family):
                raise AssertionError(f"reused C010 full family drift: {case['case_id']}")

    cert_bundle = json.loads(cert_raw.decode("utf-8"))
    certs = cert_bundle["certificates"]
    if len(certs) != 8 or {c["case_id"] for c in certs} != {c["case_id"] for c in perf["cells"]}:
        raise AssertionError("performance certificate IDs/count mismatch")
    cert_by_id = {c["case_id"]: c for c in certs}
    family_checked = []
    for case in perf["cells"]:
        cert = cert_by_id[case["case_id"]]
        raw = (AUDIT / case["path"]).read_bytes()
        data = json.loads(raw.decode("utf-8"))
        if sha(raw) != case["input_sha256"] or cert["input_sha256"] != sha(raw):
            raise AssertionError(f"performance case input hash mismatch: {case['case_id']}")
        alphabet = sorted(data["alphabet"])
        positives = sorted(set(data["positive"]))
        negatives = sorted(set(data["negative"]))
        if case["family_kind"] == "direct_rgs_fallback":
            _, _, _, family = direct_family(data)
            claimed = {tuple(value) for value in cert["compatible_rgs"]}
            if claimed != set(family) or cert["partition_count"] != len(family):
                raise AssertionError("fallback exact family mismatch")
            if any(adjacent_swap(p, n) is not None for p in positives for n in negatives):
                raise AssertionError("fallback is not graph-empty")
            if cert["graph_empty_expected"] is not True or cert["atom_partition_feasible_expected"] is not False:
                raise AssertionError("fallback certificate controls mismatch")
            family_checked.append(case["case_id"])
            continue

        groups = cert["atoms"]
        flattened = [ch for group in groups for ch in group]
        if sorted(flattened) != alphabet or len(set(flattened)) != len(alphabet):
            raise AssertionError(f"atom groups do not partition alphabet: {case['case_id']}")
        expected_edges = {tuple(sorted((group[i], group[i + 1])))
                          for group in groups for i in range(len(group) - 1)}
        observed_edges = {edge for p in positives for n in negatives
                          if (edge := adjacent_swap(p, n)) is not None}
        if observed_edges != expected_edges:
            raise AssertionError(f"exact adjacent-swap component edge mismatch: {case['case_id']}")
        if cert["missing_swap_edge_count"] or cert["unexpected_swap_edge_count"]:
            raise AssertionError("certificate reports nonzero edge mismatch")
        atom_sets = [set(group) for group in groups]
        rejection_count = 0
        for word in negatives:
            if any("".join(ch for ch in word if ch in group) not in
                   {"".join(ch for ch in p if ch in group) for p in positives}
                   for group in atom_sets):
                rejection_count += 1
            else:
                raise AssertionError(f"atom partition accepts a negative: {case['case_id']}")
        if rejection_count != len(negatives):
            raise AssertionError("negative rejection witness coverage mismatch")
        bell, stirling = bell_rows(len(groups))
        if cert["expected_partition_count"] != bell[-1]:
            raise AssertionError(f"Bell count mismatch: {case['case_id']}")
        expected_spectrum = {str(k): (stirling[k] if k <= len(groups) else 0)
                             for k in range(1, len(alphabet) + 1)}
        if cert["expected_partition_count_by_k"] != expected_spectrum:
            raise AssertionError(f"Stirling spectrum mismatch: {case['case_id']}")
        across = bell_rows(len(groups) - 1)[0][-1] if len(groups) > 1 else 1
        if cert["same_count_within_atom"] != bell[-1] or cert["same_count_across_atoms"] != across:
            raise AssertionError(f"pair count mismatch: {case['case_id']}")
        if len(alphabet) in {64, 128} and (cert["enumerated_bell_of_alphabet"] or cert["enumerated_bell_of_atoms"]):
            raise AssertionError("large structured case claims Bell enumeration")
        family_checked.append(case["case_id"])

    bells, _ = bell_rows(16)
    bell15, _ = bell_rows(15)
    summary = {
        "schema_version": 1,
        "status": "independent_oracle_validation_passed",
        "correctness_cases": len(full_rows),
        "new_rgs_cases_recomputed": len(direct_checked),
        "all_138_families_rechecked": True,
        "performance_family_certificates_replayed": len(family_checked),
        "fallback_direct_rgs_family_replayed": True,
        "bell16": bells[16],
        "bell15": bell15[15],
        "large_alphabet_bell_enumeration": False,
        "oracle_sha256": sha(full_raw),
        "family_certificates_sha256": sha(cert_raw),
        "oracle_capture_attempt_id": "20261102T211140.345666Z_c0ff4fe4f5",
    }
    report = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path = AUDIT / "ORACLE_VALIDATION_REPORT_V4.json"
    with path.open("xb") as stream:
        stream.write(report)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

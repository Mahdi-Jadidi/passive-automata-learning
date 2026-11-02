#!/usr/bin/env python3
"""Derive and deduplicate a no-K C010 corpus from frozen C009 cases."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "corpus_v1"
PROTOCOL = ROOT / "PROTOCOL_AUDIT_V1.md"
CONTRACT = ROOT.parent / "coordination" / "CONTRACT.md"
C009_AUDIT = ROOT.parents[1] / "partition_coverage_v9" / "audit"
C009_CORPUS = C009_AUDIT / "corpus_v1"
C009_MANIFEST = C009_CORPUS / "manifest.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
    return raw


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite C010 corpus: {OUT}")
    source_manifest_raw = C009_MANIFEST.read_bytes()
    source_manifest = json.loads(source_manifest_raw.decode("utf-8"))
    source_cases = source_manifest["valid_cases"]
    controls = [row for row in source_cases if row["origin"] == "named_mathematical_control"]
    randoms = [row for row in source_cases if row["origin"] == "seeded_random_no_hidden_partition"]

    custom = [
        ("one_block_only_unrestricted", {"alphabet": list("ab"), "positive": ["ab"], "negative": ["ba"]},
         "named_one_block_only_control", "only one-block compatible; also witnesses no forced-different relation"),
        ("no_labels_all_partitions", {"alphabet": list("abc"), "positive": [], "negative": []},
         "named_no_label_control", "unrestricted empty-label boundary; all Bell(3)=5 partitions"),
    ]
    candidates: list[dict[str, object]] = []
    for case_id, payload, origin, note in custom:
        candidates.append({"candidate_id": case_id, "source_case_id": case_id, "origin": origin,
                           "note": note, "payload": payload})
    # Preserve named controls ahead of random rows so a duplicate retains its mathematical-control name.
    for source_row in controls + randoms:
        input_path = C009_CORPUS / source_row["path"]
        raw = input_path.read_bytes()
        if sha(raw) != source_row["input_sha256"]:
            raise SystemExit(f"C009 frozen input hash mismatch: {source_row['case_id']}")
        payload = json.loads(raw.decode("utf-8"))
        removed = {key: payload.pop(key) for key in ("allowed_k", "k") if key in payload}
        candidates.append({
            "candidate_id": source_row["case_id"],
            "source_case_id": source_row["case_id"],
            "origin": "C009_no_K_derived_control" if source_row["origin"] == "named_mathematical_control" else "C009_no_K_derived_random",
            "source_input_sha256": source_row["input_sha256"],
            "removed_count_fields": removed,
            "payload": payload,
        })

    (OUT / "inputs").mkdir(parents=True)
    seen: dict[str, str] = {}
    cases = []
    decisions = []
    for candidate in candidates:
        payload = candidate["payload"]
        canonical_sha = sha(canonical(payload))
        if canonical_sha in seen:
            decisions.append({"candidate_id": candidate["candidate_id"], "source_case_id": candidate["source_case_id"],
                              "decision": "deduplicated", "canonical_payload_sha256": canonical_sha,
                              "retained_as": seen[canonical_sha], "removed_count_fields": candidate.get("removed_count_fields", {})})
            continue
        seen[canonical_sha] = candidate["candidate_id"]
        case_id = candidate["candidate_id"]
        path = OUT / "inputs" / f"{case_id}.json"
        raw = write_json(path, payload)
        alphabet = payload["alphabet"]
        cases.append({
            "case_id": case_id,
            "origin": candidate["origin"],
            "source_case_id": candidate["source_case_id"],
            "path": f"inputs/{path.name}",
            "input_sha256": sha(raw),
            "canonical_payload_sha256": canonical_sha,
            "alphabet_size": len(alphabet),
            "positive_count": len(payload["positive"]),
            "negative_count": len(payload["negative"]),
            "max_word_length": max((len(word) for word in payload["positive"] + payload["negative"]), default=0),
            "removed_count_fields": candidate.get("removed_count_fields", {}),
            "note": candidate.get("note"),
        })
        decisions.append({"candidate_id": candidate["candidate_id"], "source_case_id": candidate["source_case_id"],
                          "decision": "retained", "canonical_payload_sha256": canonical_sha,
                          "retained_as": case_id, "removed_count_fields": candidate.get("removed_count_fields", {})})

    invalids = [
        ("stale_allowed_k", {"alphabet": list("ab"), "positive": ["ab"], "negative": ["ba"], "allowed_k": [2]}, "stale_count_constraint"),
        ("stale_legacy_k", {"alphabet": list("ab"), "positive": ["ab"], "negative": ["ba"], "k": 2}, "stale_count_constraint"),
        ("empty_alphabet", {"alphabet": [], "positive": [""], "negative": []}, "empty_alphabet"),
        ("duplicate_alphabet_symbol", {"alphabet": ["a", "a"], "positive": ["a"], "negative": []}, "duplicate_alphabet_symbol"),
        ("conflicting_labels", {"alphabet": ["a"], "positive": ["a"], "negative": ["a"]}, "conflicting_labels"),
        ("word_outside_alphabet", {"alphabet": ["a"], "positive": ["b"], "negative": []}, "word_outside_alphabet"),
    ]
    invalid_rows = []
    for case_id, payload, expected in invalids:
        path = OUT / "invalid" / f"{case_id}.json"
        raw = write_json(path, payload)
        invalid_rows.append({"case_id": case_id, "path": f"invalid/{path.name}",
                             "input_sha256": sha(raw), "expected_rejection": expected})

    decisions_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in decisions).encode("utf-8")
    with (OUT / "deduplication.jsonl").open("xb") as handle:
        handle.write(decisions_raw)
    cases_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in cases).encode("utf-8")
    with (OUT / "cases.jsonl").open("xb") as handle:
        handle.write(cases_raw)
    invalid_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in invalid_rows).encode("utf-8")
    with (OUT / "invalid_cases.jsonl").open("xb") as handle:
        handle.write(invalid_raw)
    execution_controls = {
        "schema_version": 1,
        "status": "pending_frozen_provider_api",
        "controls": [
            {"case_id": "expired_deadline", "expected": "unknown/incomplete; no final exact count or ownership claim; child reaped; raw streams retained"},
            {"case_id": "interruption_after_partial_work", "expected": "unknown/incomplete; no final exact count or ownership claim; partial progress/streams retained; child reaped"},
        ],
        "provider_invocation": None,
        "note": "No C010 provider/API is present at preregistration; no outcomes or command syntax are fabricated.",
    }
    write_json(OUT / "execution_controls_v1.json", execution_controls)
    files = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "manifest.json"):
        raw = path.read_bytes()
        files.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha(raw), "bytes": len(raw)})
    manifest = {
        "schema_version": 1,
        "status": "generated_pending_independent_oracle",
        "deduplication_rule": "remove allowed_k and k, then deduplicate by canonical sorted-key JSON; named controls take priority over random aliases",
        "source_cycle": "C009",
        "source_manifest_sha256": sha(source_manifest_raw),
        "protocol_sha256": sha(PROTOCOL.read_bytes()),
        "contract_sha256": sha(CONTRACT.read_bytes()),
        "source_case_count": len(source_cases),
        "candidate_count": len(candidates),
        "retained_valid_case_count": len(cases),
        "unique_valid_payload_count": len(seen),
        "duplicate_candidate_count": len(candidates) - len(cases),
        "valid_cases": cases,
        "invalid_control_count": len(invalid_rows),
        "invalid_controls": invalid_rows,
        "deduplication_ledger": "deduplication.jsonl",
        "files": files,
    }
    write_json(OUT / "manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "source_case_count": len(source_cases),
                      "candidate_count": len(candidates), "retained": len(cases),
                      "unique_payloads": len(seen), "duplicates": len(candidates) - len(cases),
                      "invalid_controls": len(invalid_rows), "manifest_sha256": sha((OUT / "manifest.json").read_bytes())},
                     ensure_ascii=False, sort_keys=True))
    return 0 if len(cases) >= 100 and len(seen) == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministically generate the preregistered C009 audit corpus; no target planted."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "corpus_v1"
SEED = 20261102


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    return data


def words_up_to(alphabet: list[str], max_length: int = 5) -> list[str]:
    result = [""]
    for length in range(1, max_length + 1):
        result.extend("".join(chars) for chars in itertools.product(alphabet, repeat=length))
    return result


def choose_k(rng: random.Random, m: int, mode: str) -> list[int] | None:
    values = list(range(1, m + 1))
    if mode == "default":
        return None
    if mode == "exact":
        return [rng.choice(values)]
    if mode == "range":
        if m == 1:
            return [1]
        lo = rng.randint(1, m - 1)
        hi = rng.randint(lo + 1, m)
        return list(range(lo, hi + 1))
    if mode == "noncontiguous":
        candidates = []
        for mask in range(1, 1 << m):
            subset = [k for bit, k in enumerate(values) if mask & (1 << bit)]
            if len(subset) >= 2 and any(subset[i + 1] - subset[i] > 1 for i in range(len(subset) - 1)):
                candidates.append(subset)
        if not candidates:
            raise ValueError("noncontiguous allowed_k is impossible for this alphabet size")
        return rng.choice(candidates)
    raise ValueError(mode)


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite frozen/generated corpus directory: {OUT}")
    (OUT / "inputs").mkdir(parents=True)
    (OUT / "invalid").mkdir()
    rng = random.Random(SEED)
    cases: list[dict[str, object]] = []
    seen_payloads: set[str] = set()

    for m in range(2, 8):
        alphabet = [chr(ord("a") + i) for i in range(m)]
        pool = words_up_to(alphabet, 5)
        modes = ["default", "exact", "range"] + (["noncontiguous"] if m >= 3 else [])
        for index in range(1, 21):
            mode = modes[(index - 1) % len(modes)]
            for attempt in range(1, 10001):
                words = rng.sample(pool, rng.randint(1, min(9, len(pool))))
                positive_count = rng.randint(0, min(5, len(words)))
                positive = sorted(words[:positive_count], key=lambda w: (len(w), w))
                remaining = words[positive_count:]
                negative_count = rng.randint(0, min(5, len(remaining)))
                negative = sorted(remaining[:negative_count], key=lambda w: (len(w), w))
                allowed_k = choose_k(rng, m, mode)
                payload: dict[str, object] = {
                    "alphabet": alphabet,
                    "positive": positive,
                    "negative": negative,
                }
                if allowed_k is not None:
                    payload["allowed_k"] = allowed_k
                payload_sha = digest(canonical_bytes(payload))
                if payload_sha not in seen_payloads:
                    seen_payloads.add(payload_sha)
                    break
            else:
                raise RuntimeError(f"could not create a unique random payload m={m} i={index}")

            case_id = f"rand_m{m}_{index:02d}"
            path = OUT / "inputs" / f"{case_id}.json"
            raw = write_json(path, payload)
            cases.append({
                "case_id": case_id,
                "origin": "seeded_random_no_hidden_partition",
                "constraint_kind": mode,
                "path": f"inputs/{path.name}",
                "input_sha256": digest(raw),
                "payload_sha256": payload_sha,
                "alphabet_size": m,
                "positive_count": len(positive),
                "negative_count": len(negative),
            })

    doubled_pairs = {
        "alphabet": list("abcdef"),
        "positive": ["", "aabb", "ccdd", "eeff"],
        "negative": ["bbaa", "ddcc", "ffee"],
    }
    controls: list[tuple[str, dict[str, object], str, str]] = [
        ("doubled_pairs_default", doubled_pairs, "default_all_k", "old graph-empty unique-three-block sample"),
        ("doubled_pairs_k_3_4", {**doubled_pairs, "allowed_k": [3, 4]}, "noncontiguous", "known allowed-k list; k=4 has no compatible partition"),
        ("doubled_pairs_k_3", {**doubled_pairs, "allowed_k": [3]}, "exact", "trusted exact k=3 control"),
        ("forced_ab_other_pairs_ambiguous", {"alphabet": list("abc"), "positive": ["ab"], "negative": ["ba"]}, "default_all_k", "ab forced same; ac and bc ambiguous"),
        ("known_k_forces_different", {"alphabet": list("ab"), "positive": ["ab"], "negative": [], "allowed_k": [2]}, "exact", "positive-only data; trusted k=2 forces a and b apart"),
        ("zero_answers_under_k", {"alphabet": list("ab"), "positive": ["ab"], "negative": ["ba"], "allowed_k": [2]}, "exact", "swap witness forces same but K permits only two singleton blocks"),
        ("positive_only_all_partitions", {"alphabet": list("abc"), "positive": ["ab"], "negative": []}, "default_all_k", "positive-only boundary; all five partitions compatible"),
        ("epsilon_and_unused_symbols", {"alphabet": list("abcd"), "positive": [""], "negative": ["a"]}, "default_all_k", "epsilon and unused b,c,d"),
        ("no_positive_boundary", {"alphabet": list("abc"), "positive": [], "negative": ["a"]}, "default_all_k", "no-positive boundary"),
    ]
    for case_id, payload, constraint_kind, note in controls:
        payload_sha = digest(canonical_bytes(payload))
        if payload_sha in seen_payloads:
            raise RuntimeError(f"named control duplicates earlier payload: {case_id}")
        seen_payloads.add(payload_sha)
        path = OUT / "inputs" / f"{case_id}.json"
        raw = write_json(path, payload)
        cases.append({
            "case_id": case_id,
            "origin": "named_mathematical_control",
            "constraint_kind": constraint_kind,
            "note": note,
            "path": f"inputs/{path.name}",
            "input_sha256": digest(raw),
            "payload_sha256": payload_sha,
            "alphabet_size": len(payload["alphabet"]),
            "positive_count": len(payload["positive"]),
            "negative_count": len(payload["negative"]),
        })

    invalids = [
        ("empty_alphabet", {"alphabet": [], "positive": [""], "negative": []}, "empty_alphabet"),
        ("duplicate_alphabet_symbol", {"alphabet": ["a", "a"], "positive": ["a"], "negative": []}, "duplicate_alphabet_symbol"),
        ("conflicting_labels", {"alphabet": ["a"], "positive": ["a"], "negative": ["a"]}, "conflicting_labels"),
        ("word_outside_alphabet", {"alphabet": ["a"], "positive": ["b"], "negative": []}, "word_outside_alphabet"),
        ("empty_allowed_k", {"alphabet": ["a"], "positive": [""], "negative": [], "allowed_k": []}, "empty_allowed_k"),
        ("allowed_k_zero", {"alphabet": ["a"], "positive": [""], "negative": [], "allowed_k": [0]}, "allowed_k_out_of_range"),
        ("allowed_k_too_large", {"alphabet": ["a"], "positive": [""], "negative": [], "allowed_k": [2]}, "allowed_k_out_of_range"),
    ]
    invalid_rows = []
    for case_id, payload, expected_rejection in invalids:
        path = OUT / "invalid" / f"{case_id}.json"
        raw = write_json(path, payload)
        invalid_rows.append({
            "case_id": case_id,
            "path": f"invalid/{path.name}",
            "expected_input_classification": expected_rejection,
            "input_sha256": digest(raw),
        })

    (OUT / "cases.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in cases), encoding="utf-8", newline="\n")
    (OUT / "invalid_cases.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in invalid_rows), encoding="utf-8", newline="\n")
    execution_controls = {
        "schema_version": 1,
        "status": "pending_provider_api_readiness",
        "controls": [
            {"case_id": "expired_deadline", "required_semantics": "complete=false; no final universal ownership/count claim; child reaped; stdout/stderr preserved"},
            {"case_id": "interruption_after_partial_work", "required_semantics": "complete=false; no final universal ownership/count claim; partial work preserved; child reaped; stdout/stderr preserved"},
        ],
        "api_specific_invocation": None,
        "note": "No provider/API is present in the initial C009 workspace; commands and provider outcomes are intentionally not fabricated.",
    }
    write_json(OUT / "execution_controls_v1.json", execution_controls)

    files = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "manifest.json"):
        files.append({"path": path.relative_to(OUT).as_posix(), "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size})
    manifest = {
        "schema_version": 1,
        "status": "generated_pending_frozen_capture",
        "seed": SEED,
        "generation_rule": "random.Random(20261102); 20 unique seeded payloads for each m=2..7; labels sampled directly, no planted partition or hidden target",
        "random_unique_payload_count": 120,
        "random_alphabet_sizes": {str(m): 20 for m in range(2, 8)},
        "valid_case_count": len(cases),
        "unique_valid_payload_count": len(seen_payloads),
        "valid_cases": cases,
        "invalid_control_count": len(invalid_rows),
        "invalid_controls": invalid_rows,
        "files": files,
    }
    write_json(OUT / "manifest.json", manifest)
    print(json.dumps({
        "status": manifest["status"],
        "seed": SEED,
        "random_unique_payload_count": manifest["random_unique_payload_count"],
        "valid_case_count": len(cases),
        "unique_valid_payload_count": len(seen_payloads),
        "invalid_control_count": len(invalid_rows),
        "manifest_sha256": digest((OUT / "manifest.json").read_bytes()),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

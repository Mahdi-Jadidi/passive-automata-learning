"""Build and freeze deterministic, auditor-owned Stage-2 inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
CORPUS = HERE / "corpora" / "stage2_v1"
SMALL_STAGE1 = HERE / "corpora" / "stage1_v4"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def alphabet(n: int) -> list[str]:
    if n <= 26:
        return [chr(ord("a") + i) for i in range(n)]
    return [chr(0x0400 + i) for i in range(n)]


def q2_constructive(m: int, k: int):
    symbols = alphabet(m)
    if m % k:
        raise ValueError("constructive q2 cells require equal block sizes")
    width = m // k
    blocks = [symbols[i * width:(i + 1) * width] for i in range(k)]
    local = ["".join(block) * 2 for block in blocks]
    second = [word + block[0] for word, block in zip(local, blocks)]
    lockstep = "".join(local[b][i] for i in range(len(local[0])) for b in range(k))
    positive = ["".join(local), "".join(reversed(local)), lockstep, "".join(second)]
    return {"alphabet": symbols, "k": k, "positive": positive, "negative": []}, blocks


def main() -> None:
    if CORPUS.exists():
        raise FileExistsError(f"refusing to overwrite frozen corpus: {CORPUS}")
    inputs = CORPUS / "inputs"
    truths = CORPUS / "hidden_truth"
    inputs.mkdir(parents=True)
    truths.mkdir(parents=True)
    records = []

    def add(case_id, family, data, target=None, notes=None):
        ip = inputs / f"{case_id}.json"
        write_json(ip, data)
        truth_rel = None
        if target is not None:
            truth_rel = f"hidden_truth/{case_id}.json"
            write_json(truths / f"{case_id}.json", target)
        records.append({"id": case_id, "family": family,
                        "input": f"inputs/{case_id}.json", "truth": truth_rel,
                        "alphabet_size": len(data["alphabet"]),
                        "k_input": data.get("k"), "k_hidden": (target or {}).get("k"),
                        "positive_count": len(data["positive"]), "negative_count": len(data["negative"]),
                        "positive_lengths": sorted({len(w) for w in data["positive"]}),
                        "negative_lengths": sorted({len(w) for w in data["negative"]}),
                        "notes": notes or ""})

    # Import the earlier frozen small tier by copying only public solver inputs.
    old_manifest_path = SMALL_STAGE1 / "manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    old_cases = [row for row in old_manifest["cases"]
                 if row["family"] in {"small_general", "small_singleton", "random_dfa_small", "boundary"}
                 and isinstance(row.get("k"), int) and 2 <= row["k"] <= row["alphabet_size"]]
    if len(old_cases) != 80:
        raise AssertionError(f"expected 80 small valid stage1 inputs, got {len(old_cases)}")
    old_provenance = []
    for old in old_cases:
        original = SMALL_STAGE1 / old["input"]
        data = json.loads(original.read_text(encoding="utf-8"))
        case_id = f"small_{old['id']}"
        add(case_id, "small_fullset_import", data,
            notes=f"Copied public input from stage1_v4 case {old['id']}; no truth sidecar passed to solver.")
        old_provenance.append({"source_id": old["id"], "source_input": str(original),
                               "source_input_sha256": sha(original), "stage2_id": case_id})

    add("sparse_k3_ambiguous", "sparse_singleton_known_k",
        {"alphabet": list("abcd"), "k": 3,
         "positive": ["abcd", "bacd", "acbd", "abdc"], "negative": []},
        {"k": 3, "target_blocks": [["a"], ["b"], ["c", "d"]]},
        "Connected opposition path; all unordered exact singleton solutions are independently enumerated.")
    add("sparse_k3_disambiguated", "sparse_singleton_known_k",
        {"alphabet": list("abcd"), "k": 3,
         "positive": ["abcd", "bacd", "acbd", "abdc"], "negative": ["bdac"]},
        {"k": 3, "target_blocks": [["a", "d"], ["b"], ["c"]]},
        "Same sparse opposition path plus one negative; verify the exact full set.")

    # Q=2 controls separate bounded finite languages from singleton and
    # unrestricted regular-factor semantics.
    add("q2_one_projection_control", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": ["ab", "ab"], "negative": ["aa"]},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "Duplicate positive samples collapse to one projection per singleton block.")
    add("q2_two_projection_control", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": ["a", "b"], "negative": ["aa"]},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "At most two words fits; exactly-one local words do not.")
    add("q2_three_projection_violation", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": ["", "a", "aa"], "negative": []},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "Unrestricted finite factors fit; q=2 is impossible because one block has three projections.")
    add("q2_empty_positive_boundary", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": [], "negative": ["a"]},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "At-most-q empty observed languages are distinct from exactly-one singleton recovery.")
    add("q2_repeated_projection_control", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": ["a", "ba", "aba", "a"], "negative": ["aa"]},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "Repeated positive words and repeated local projections exercise deduplication.")
    add("q2_negative_witness_control", "q2_small_control",
        {"alphabet": ["a", "b"], "k": 2, "positive": ["ab", "ba"], "negative": ["aa"]},
        {"k": 2, "target_blocks": [["a"], ["b"]]}, "Both factors have two observed projections; every negative needs a direct unseen projection witness.")
    add("q2_naive_threshold_counterexample", "q2_small_control",
        {"alphabet": list("abc"), "k": 2, "positive": ["abc", "bac"], "negative": []},
        {"k": 2, "target_blocks": [["a", "b"], ["c"]]}, "The pair ab has exactly two projections and must not be marked opposed at q=2.")
    add("q2_pairwise_full_block_cap_failure", "q2_small_control",
        {"alphabet": list("abcd"), "k": 2,
         "positive": ["abcabcdd", "ddabcabc", "abcdabcd", "acbacbdd", "bacbacdd"],
         "negative": []},
        {"k": 2, "target_blocks": [["a", "b", "c"], ["d"]]},
        "Pair q=2 opposition forces abc|d, but the full abc block has four projections; cap check must reject.")

    q2_targets = []
    for m, k in ((8, 2), (16, 4), (32, 4), (128, 8)):
        data, blocks = q2_constructive(m, k)
        case_id = f"q2_positive_only_m{m}_k{k}"
        add(case_id, "q2_positive_only_constructive", data,
            {"k": k, "target_blocks": blocks, "local_word_cap": 2},
            "Four positive constructions: forward, reverse, lockstep, and each repeated local word plus its first symbol; no negatives.")
        q2_targets.append(case_id)

    add("unknown_k_singleton_unique", "singleton_unknown_k",
        {"alphabet": list("abcd"), "positive": ["abcd", "cdab"], "negative": ["bacd", "abdc"]},
        {"k": 2, "target_blocks": [["a", "b"], ["c", "d"]]},
        "No k field in public input; hidden target k remains only in this sidecar.")
    add("unknown_k_ambiguous_control", "singleton_unknown_k",
        {"alphabet": list("abc"), "positive": ["ab", "ba"], "negative": []},
        None, "No target k; singleton certificate should abstain without a quotient-clique proof.")
    add("unknown_k_empty_positive_boundary", "singleton_unknown_k",
        {"alphabet": list("abc"), "positive": [], "negative": [""]},
        None, "No target k and no positive coverage; must remain unresolved.")

    # Long contextual pair-star families. A common C contains every symbol;
    # one negative C+a and one positive C+ab are added per tree edge.
    contextual = []
    for n, k, target_length in ((32, 4, 128), (32, 4, 1024),
                                (32, 8, 4096), (128, 8, 1024)):
        symbols = alphabet(n)
        width = n // k
        blocks = [symbols[i * width:(i + 1) * width] for i in range(k)]
        base_length = target_length - 2
        base = "".join(symbols[i % n] for i in range(base_length))
        positives = [base]
        negatives = []
        edges = []
        for block in blocks:
            center = block[0]
            for leaf in block[1:]:
                edges.append([center, leaf])
                positives.append(base + center + leaf)
                negatives.append(base + center)
        case_id = f"context_pair_star_a{n}_k{k}_L{target_length}"
        add(case_id, "contextual_tree_pair_star", {
            "alphabet": symbols, "k": k, "positive": positives, "negative": negatives},
            {"k": k, "target_blocks": blocks, "base": base, "tree_edges": edges,
             "max_word_length": target_length},
            "Every observed word is long and nonempty. The target is forced by one positive insertion-rescue and one negative per tree edge.")
        contextual.append(case_id)

    # Copy the five public root CLI examples, retaining their exact file data.
    cli_cases = []
    for source in sorted((PROJECT / "examples").glob("*.json")):
        data = json.loads(source.read_text(encoding="utf-8-sig"))
        case_id = f"cli_{source.stem}"
        if source.stem == "infer_singleton_k":
            add(case_id, "root_cli_unknown_k", data,
                {"k": 2, "target_blocks": [["a", "b"], ["c", "d"]]},
                "Public inference CLI input has no k; hidden target is sidecar-only.")
        else:
            add(case_id, "root_cli_example", data, None,
                f"Public CLI example copied from {source.name}; no target is passed to the solver.")
        cli_cases.append(case_id)

    cases = []
    for row in records:
        input_path = CORPUS / row["input"]
        truth_path = CORPUS / row["truth"] if row["truth"] else None
        row["input_sha256"] = sha(input_path)
        row["input_bytes"] = input_path.stat().st_size
        if truth_path:
            row["truth_sha256"] = sha(truth_path)
            row["truth_bytes"] = truth_path.stat().st_size
        cases.append(row)
    manifest = {"schema": "C004-stage2-corpus-manifest-v1", "case_count": len(cases),
                "generator": "audit/generate_stage2_corpus_v1.py", "cases": cases,
                "borrowed_stage1_inputs": old_provenance,
                "q2_constructive_case_ids": q2_targets,
                "contextual_case_ids": contextual, "root_cli_case_ids": cli_cases}
    write_json(CORPUS / "manifest.json", manifest)
    freeze = {"schema": "C004-stage2-corpus-freeze-v1", "manifest_sha256": sha(CORPUS / "manifest.json"),
              "generator_sha256": sha(Path(__file__)),
              "stage1_manifest_sha256": sha(SMALL_STAGE1 / "manifest.json"),
              "case_count": len(cases),
              "input_file_count": len(cases),
              "truth_file_count": sum(row["truth"] is not None for row in cases),
              "positive_only_q2_constructive_cases": q2_targets,
              "long_contextual_cases": contextual,
              "root_cli_cases": cli_cases}
    write_json(CORPUS / "freeze_v1.json", freeze)
    print(json.dumps({"case_count": len(cases), "truth_count": freeze["truth_file_count"],
                      "manifest_sha256": freeze["manifest_sha256"],
                      "freeze_sha256": sha(CORPUS / "freeze_v1.json"),
                      "q2_cases": q2_targets, "contextual_cases": contextual,
                      "cli_cases": cli_cases}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()

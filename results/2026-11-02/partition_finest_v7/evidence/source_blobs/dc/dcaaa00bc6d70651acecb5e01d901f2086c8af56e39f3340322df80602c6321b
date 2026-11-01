#!/usr/bin/env python3
"""Generate and freeze C007's seed-20261102 audit corpus and hidden sidecars."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL_CORPUS_V1.md"
OUT = HERE / "corpus_v1"
SEED = 20261102


def dump_jsonl(path: Path, rows: list[object]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                              for row in rows), encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_key(word):
    return (len(word), tuple(word))


def random_partition(alphabet: list[str], rng: random.Random, k: int):
    shuffled = list(alphabet)
    rng.shuffle(shuffled)
    blocks = [[symbol] for symbol in shuffled[:k]]
    for symbol in shuffled[k:]:
        blocks[rng.randrange(k)].append(symbol)
    return [sorted(block, key=alphabet.index) for block in blocks]


def make_component(block: list[str], rng: random.Random):
    template = rng.choice(("ends_with", "contains", "even_marker", "odd_marker"))
    marker = rng.choice(block)
    states = [0, 1]
    if template == "ends_with":
        transitions = {str(q): {s: (1 if s == marker else 0) for s in block}
                       for q in states}
        accepting = [1]
        witness, reject = [marker], []
    elif template == "contains":
        transitions = {"0": {s: (1 if s == marker else 0) for s in block},
                       "1": {s: 1 for s in block}}
        accepting = [1]
        witness, reject = [marker], []
    elif template in ("even_marker", "odd_marker"):
        transitions = {"0": {s: (1 if s == marker else 0) for s in block},
                       "1": {s: (0 if s == marker else 1) for s in block}}
        accepting = [0] if template == "even_marker" else [1]
        witness = [] if template == "even_marker" else [marker]
        reject = [marker] if template == "even_marker" else []
    else:
        raise AssertionError(template)
    return {
        "alphabet": block,
        "states": states,
        "start": 0,
        "accepting": accepting,
        "transitions": transitions,
        "language_template": template,
        "marker": marker,
        "infinite_language_proof": {
            "cycle_word": marker,
            "cycle_state": 1 if template in ("ends_with", "contains") else 0,
            "accepted_cycle_family": "template-specific ultimately periodic family; see generator source",
        },
        "accepted_witness": witness,
        "rejected_witness": reject,
    }


def component_accepts(component, word):
    state = component["start"]
    transitions = component["transitions"]
    for symbol in word:
        state = transitions[str(state)][symbol]
    return state in component["accepting"]


def product_accepts(components, word):
    return all(component_accepts(component,
                                 [symbol for symbol in word if symbol in component["alphabet"]])
               for component in components)


def build_generated_case(case_index: int, m: int, rng: random.Random):
    alphabet = list("abcdefgh"[:m])
    max_k = min(6, m)
    k = rng.randint(1, max_k)
    blocks = random_partition(alphabet, rng, k)
    components = [make_component(block, rng) for block in blocks]
    positive_witness = [s for component in components for s in component["accepted_witness"]]
    negative_witnesses = []
    for index, rejected_component in enumerate(components):
        word = [s for j, component in enumerate(components)
                for s in (rejected_component["rejected_witness"] if j == index
                          else component["accepted_witness"])]
        if not product_accepts(components, word):
            negative_witnesses.append(word)
    if not product_accepts(components, positive_witness):
        raise AssertionError("bad positive generator witness")
    if not negative_witnesses:
        raise AssertionError("every generated product needs a negative witness")

    sampled = {tuple(positive_witness), *(tuple(word) for word in negative_witnesses)}
    target_count = rng.randint(15, 24)
    for _ in range(target_count * 4):
        length = rng.randint(0, min(12, m + 4))
        sampled.add(tuple(rng.choice(alphabet) for _ in range(length)))
        if len(sampled) >= target_count:
            break
    positives, negatives = [], []
    for word in sampled:
        (positives if product_accepts(components, list(word)) else negatives).append(list(word))
    positives.sort(key=word_key)
    negatives.sort(key=word_key)
    if not positives or not negatives:
        raise AssertionError("witnesses must force both labels")

    case_id = f"c007_gen_m{m:02d}_{case_index:03d}"
    visible = {"alphabet": alphabet, "positive": positives, "negative": negatives}
    visible_bytes = json.dumps(visible, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
    hidden = {
        "case_id": case_id,
        "payload_sha256": hashlib.sha256(visible_bytes).hexdigest(),
        "generator_kind": "product_of_infinite_total_dfas",
        "seed": SEED,
        "planted_partition": blocks,
        "components": components,
        "sample_counts": {"positive": len(positives), "negative": len(negatives)},
        "note": "hidden generator metadata; not part of the solver-visible record",
    }
    return {"case_id": case_id, "input": visible}, hidden


def control(case_id, alphabet, positive, negative, note):
    return {"case_id": case_id,
            "input": {"alphabet": alphabet, "positive": positive, "negative": negative},
            "audit_note": note}


def random_control_payload(rng, m):
    alphabet = list("abcdefgh"[:m])
    universe = [[]]
    for length in range(1, 4):
        universe.extend([[rng.choice(alphabet) for _ in range(length)] for _ in range(3 * m)])
    universe = list({tuple(word) for word in universe})
    rng.shuffle(universe)
    split = rng.randint(1, len(universe) - 1)
    positive = [list(w) for w in universe[:split]]
    negative = [list(w) for w in universe[split:]]
    positive.sort(key=word_key)
    negative.sort(key=word_key)
    return {"alphabet": alphabet, "positive": positive, "negative": negative}


def select_target_controls(rng):
    from oracle_direct_v1 import analyze

    wanted = {"unique_finest_3plus": None, "multiple_maximal_refinements": None}
    attempts = 0
    while any(value is None for value in wanted.values()) and attempts < 50000:
        attempts += 1
        data = random_control_payload(rng, rng.choice((3, 4, 5)))
        result = analyze({"case_id": f"search{attempts}", "input": data})
        frontier = result["maximal_refinement_frontier"]
        if (wanted["unique_finest_3plus"] is None and result["unique_finest"]
                and len(result["meet"]) >= 3):
            wanted["unique_finest_3plus"] = data
        if (wanted["multiple_maximal_refinements"] is None and len(frontier) >= 2):
            wanted["multiple_maximal_refinements"] = data
    if any(value is None for value in wanted.values()):
        missing = [key for key, value in wanted.items() if value is None]
        raise RuntimeError(f"target search exhausted after {attempts}: {missing}")
    return wanted, attempts


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty frozen corpus: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    inputs, sidecars = [], []
    seen = set()
    counts = {m: 0 for m in range(2, 9)}
    retries = 0
    while any(counts[m] < 30 for m in counts):
        m = next(size for size in range(2, 9) if counts[size] < 30)
        trial = 0
        while True:
            trial += 1
            retries += int(trial > 1)
            row, hidden = build_generated_case(counts[m], m, rng)
            digest = hashlib.sha256(json.dumps(row["input"], ensure_ascii=False, sort_keys=True,
                separators=(",", ":")).encode("utf-8")).hexdigest()
            if digest not in seen:
                seen.add(digest)
                inputs.append(row)
                sidecars.append(hidden)
                counts[m] += 1
                break

    targeted, target_attempts = select_target_controls(random.Random(SEED ^ 0x5A5A))
    controls = [
        control("ctrl_unique_finest_3plus", targeted["unique_finest_3plus"]["alphabet"],
                targeted["unique_finest_3plus"]["positive"], targeted["unique_finest_3plus"]["negative"],
                "search-selected: unique sample finest with at least three blocks"),
        control("ctrl_multiple_maximal_refinements",
                targeted["multiple_maximal_refinements"]["alphabet"],
                targeted["multiple_maximal_refinements"]["positive"],
                targeted["multiple_maximal_refinements"]["negative"],
                "search-selected: at least two incomparable maximal refinements"),
        control("ctrl_partial_meet_ambiguity", ["a", "b", "c"], [[], ["a", "b", "c"]], [["a"]],
                "partial meet of two compatible cuts can certify multiple maxima; exact meet/frontier is separate"),
        control("ctrl_one_block_only", ["a", "b"], [["a", "b"]], [["b", "a"]],
                "only one-block partition is compatible"),
        control("ctrl_no_positives", ["a", "b", "c"], [], [["a"], ["b", "c"]],
                "valid empty-positive sample"),
        control("ctrl_no_negatives", ["a", "b", "c"], [[], ["a"]], [],
                "valid empty-negative sample and epsilon positive"),
        control("ctrl_unused_symbol", ["a", "b", "c"], [["a"]], [["b", "a"]],
                "symbol c is unused in every sample word"),
        control("ctrl_epsilon_positive", ["a", "b"], [[], ["a", "b"]], [["a"]],
                "epsilon is a positive trace"),
    ]
    invalid = [
        {"case_id": "invalid_duplicate_alphabet", "input": {"alphabet": ["a", "a"],
         "positive": [["a"]], "negative": []}},
        {"case_id": "invalid_unknown_symbol", "input": {"alphabet": ["a", "b"],
         "positive": [["c"]], "negative": []}},
        {"case_id": "invalid_label_conflict", "input": {"alphabet": ["a"],
         "positive": [["a"]], "negative": [["a"]]}},
    ]
    execution_controls = {
        "schema_version": 1,
        "controls": [
            {"id": "deadline_during_search", "expected": "incomplete; no finality claim"},
            {"id": "interrupt_after_partial_answers", "expected": "incomplete; preserve prior answers"},
            {"id": "omit_one_cut_from_no_separator_certificate", "expected": "reject finality"},
            {"id": "forge_one_cut_collision_witness", "expected": "reject certificate"},
            {"id": "return_partial_meet_as_exact_final_meet", "expected": "reject exact-meet completeness; ambiguity decision may remain valid if partial meet is infeasible"},
            {"id": "remove_one_branch_from_separator_search_proof", "expected": "reject coverage"},
        ],
        "note": "pre-registered controls; apply only after production proof schema is frozen",
    }

    dump_jsonl(OUT / "inputs.jsonl", inputs)
    dump_jsonl(OUT / "truth_sidecars.jsonl", sidecars)
    dump_jsonl(OUT / "targeted_controls.jsonl", controls)
    valid_control_inputs = [{"case_id": row["case_id"], "input": row["input"]} for row in controls]
    dump_jsonl(OUT / "all_valid_inputs.jsonl", inputs + valid_control_inputs)
    dump_jsonl(OUT / "invalid_controls.jsonl", invalid)
    (OUT / "execution_controls.json").write_text(json.dumps(execution_controls, ensure_ascii=False,
        sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")

    payload_hashes = [hashlib.sha256(json.dumps(row["input"], ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest() for row in inputs]
    if len(set(payload_hashes)) != len(inputs):
        raise AssertionError("duplicate visible inputs survived deduplication")
    all_valid_hashes = [hashlib.sha256(json.dumps(row["input"], ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest() for row in inputs + valid_control_inputs]
    if len(set(all_valid_hashes)) != len(all_valid_hashes):
        raise AssertionError("targeted controls duplicate another frozen valid payload")
    files = ["inputs.jsonl", "truth_sidecars.jsonl", "targeted_controls.jsonl",
             "all_valid_inputs.jsonl",
             "invalid_controls.jsonl", "execution_controls.json"]
    manifest = {
        "schema_version": 1,
        "corpus": "C007_AUDIT_CORPUS_V1",
        "seed": SEED,
        "generated_rows": len(inputs),
        "distinct_generated_payloads": len(set(payload_hashes)),
        "all_valid_rows_including_controls": len(inputs) + len(controls),
        "distinct_all_valid_payloads": len(set(all_valid_hashes)),
        "rows_per_alphabet_size": {str(m): counts[m] for m in counts},
        "alphabet_sizes": list(range(2, 9)),
        "infinite_regular_product_rows": len(sidecars),
        "targeted_control_rows": len(controls),
        "invalid_control_rows": len(invalid),
        "duplicate_retry_count": retries,
        "target_control_search_attempts": target_attempts,
        "solver_input_fields": ["alphabet", "positive", "negative"],
        "generator_and_partition_data_in_solver_inputs": False,
        "files": {name: {"bytes": (OUT / name).stat().st_size, "sha256": sha256(OUT / name)}
                  for name in files},
        "protocol_sha256": sha256(PROTOCOL),
        "generator_sha256": sha256(Path(__file__)),
        "oracle_source_sha256": sha256(HERE / "oracle_direct_v1.py"),
        "scientific_status": "frozen_before_candidate_comparison",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False,
        sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"rows": len(inputs), "distinct": len(set(payload_hashes)),
                      "all_valid_rows": len(inputs) + len(controls),
                      "rows_per_size": manifest["rows_per_alphabet_size"],
                      "controls": len(controls), "invalid_controls": len(invalid),
                      "target_search_attempts": target_attempts,
                      "manifest_sha256": sha256(OUT / "manifest.json")}, sort_keys=True))


if __name__ == "__main__":
    main()

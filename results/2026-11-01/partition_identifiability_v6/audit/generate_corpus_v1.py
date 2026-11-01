"""Generate the frozen C006 small consistent corpus and audit-only truth sidecars."""
import argparse
import hashlib
import json
import random
from pathlib import Path

SEED = 20261101
SIZES = tuple(range(2, 8))


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def accepts(grammar, word):
    kind = grammar["kind"]
    if kind == "equal_pair_token_star":
        return len(word) % 2 == 0 and all(word[i] == word[i + 1]
                                          for i in range(0, len(word), 2))
    if kind == "finite_words_plus_unary_tail":
        if word in set(grammar["finite_words"]):
            return True
        symbol = grammar["tail_symbol"]
        return (len(word) >= grammar["tail_min_length"] and
                all(a == symbol for a in word))
    raise ValueError("unknown grammar kind")


def product_case(m, ordinal, retry=0):
    seed = SEED + m * 10000 + ordinal * 100 + retry
    rng = random.Random(seed)
    alphabet = [chr(ord("a") + i) for i in range(m)]
    k = 2 + rng.randrange(m - 1)
    shuffled = alphabet[:]
    rng.shuffle(shuffled)
    blocks = [[] for _ in range(k)]
    for i, symbol in enumerate(shuffled):
        blocks[i % k].append(symbol)
    rng.shuffle(blocks)
    positives = set()
    if rng.random() < 0.5:
        positives.add("")
    for _ in range(rng.randint(3, 8)):
        tokens = [rng.choice(alphabet) for _ in range(rng.randint(1, 8))]
        rng.shuffle(tokens)
        positives.add("".join(a + a for a in tokens))
    negatives = set()
    while len(negatives) < rng.randint(4, 10):
        length = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
        word = "".join(rng.choice(alphabet) for _ in range(length))
        # A word is in the token-star product iff every symbol occurs evenly.
        if any(word.count(a) % 2 for a in alphabet) and word not in positives:
            negatives.add(word)
    grammars = [dict(kind="equal_pair_token_star", tokens=[a + a for a in sorted(block)])
                for block in blocks]
    data = dict(alphabet=alphabet, positive=sorted(positives), negative=sorted(negatives))
    truth = dict(seed=seed, generator_kind="planted_product", blocks=blocks,
                 grammars=grammars)
    for word in data["positive"]:
        assert all(accepts(g, "".join(a for a in word if a in block))
                   for block, g in zip(blocks, grammars))
    for word in data["negative"]:
        assert not all(accepts(g, "".join(a for a in word if a in block))
                       for block, g in zip(blocks, grammars))
    return data, truth


def single_factor_case(m, ordinal, retry=0):
    seed = SEED + 900000 + m * 10000 + ordinal * 100 + retry
    rng = random.Random(seed)
    alphabet = [chr(ord("a") + i) for i in range(m)]
    words = ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, 5)))
             for _ in range(25)]
    positives = set(words[:rng.randint(1, 7)])
    negatives = set()
    while len(negatives) < rng.randint(4, 8):
        word = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 6)))
        if word not in positives:
            negatives.add(word)
    tail_symbol = alphabet[rng.randrange(m)]
    grammar = dict(kind="finite_words_plus_unary_tail",
                   finite_words=sorted(positives), tail_symbol=tail_symbol,
                   tail_min_length=8)
    data = dict(alphabet=alphabet, positive=sorted(positives), negative=sorted(negatives))
    truth = dict(seed=seed, generator_kind="one_factor_infinite_regular_control",
                 blocks=[alphabet], grammars=[grammar])
    assert all(accepts(grammar, word) for word in data["positive"])
    assert not any(accepts(grammar, word) for word in data["negative"])
    return data, truth


def fixed_control(case_id, alphabet, positive, negative, blocks, grammars, kind):
    return dict(case_id=case_id,
                input=dict(alphabet=alphabet, positive=positive, negative=negative)), \
        dict(case_id=case_id, generator_kind=kind, blocks=blocks, grammars=grammars)


def controls():
    # No nontrivial partition is compatible, although the exact sound
    # must-link graph is disconnected: each negative ab/ba collides with the
    # positive projections a and b under {a}|{b}.
    yield fixed_control(
        "mustlink_not_necessary_nondecomposable", ["a", "b"], ["a", "b"], ["ab", "ba"],
        [["a", "b"]],
        [dict(kind="finite_words_plus_unary_tail", finite_words=["a", "b"],
              tail_symbol="a", tail_min_length=5)],
        "one_factor_infinite_regular_nondecomposable")
    yield fixed_control(
        "all_partitions_ambiguous_epsilon", ["a", "b", "c"], [""], [],
        [["a", "c"], ["b"]],
        [dict(kind="equal_pair_token_star", tokens=["aa", "cc"]),
         dict(kind="equal_pair_token_star", tokens=["bb"])],
        "infinite_regular_product_ambiguity")
    yield fixed_control(
        "empty_positive_empty_negative", ["a", "b", "c"], [], [],
        [["a", "b", "c"]],
        [dict(kind="finite_words_plus_unary_tail", finite_words=[],
              tail_symbol="a", tail_min_length=5)],
        "one_factor_infinite_regular_empty_sample")
    yield fixed_control(
        "unused_symbol_and_unequal_blocks", ["a", "b", "c"], ["aa"], ["b"],
        [["a", "b"], ["c"]],
        [dict(kind="equal_pair_token_star", tokens=["aa", "bb"]),
         dict(kind="equal_pair_token_star", tokens=["cc"])],
        "infinite_regular_product_unused_symbol")
    yield fixed_control(
        "epsilon_positive_negative_unary", ["a", "b"], [""], ["a", "b"],
        [["a"], ["b"]],
        [dict(kind="equal_pair_token_star", tokens=["aa"]),
         dict(kind="equal_pair_token_star", tokens=["bb"])],
        "infinite_regular_product_epsilon")
    yield fixed_control(
        "no_positive_epsilon_negative", ["a", "b"], [], [""],
        [["a", "b"]],
        [dict(kind="finite_words_plus_unary_tail", finite_words=[],
              tail_symbol="a", tail_min_length=5)],
        "one_factor_infinite_regular_negative_epsilon")
    yield fixed_control(
        "m1_no_nontrivial_partition", ["a"], [""], [],
        [["a"]],
        [dict(kind="finite_words_plus_unary_tail", finite_words=[""],
              tail_symbol="a", tail_min_length=5)],
        "one_factor_infinite_regular_single_symbol_structural_control")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    records, truths, seen = [], [], set()
    for m in SIZES:
        for ordinal in range(20):
            constructor = single_factor_case if ordinal >= 16 else product_case
            attempt = 0
            while True:
                data, hidden = constructor(m, ordinal, attempt)
                payload = canonical(data)
                digest = hashlib.sha256(payload).hexdigest()
                if digest not in seen:
                    seen.add(digest)
                    break
                attempt += 1
                if attempt > 1000:
                    raise RuntimeError("failed to create a distinct visible input")
            case_id = f"c006_m{m:02d}_{ordinal:02d}"
            records.append(dict(case_id=case_id, input=data))
            truths.append(dict(case_id=case_id, **hidden))
    control_records, control_truths = [], []
    for visible, hidden in controls():
        digest = hashlib.sha256(canonical(visible["input"])).hexdigest()
        if digest in seen:
            raise ValueError("control duplicates a corpus payload")
        seen.add(digest)
        control_records.append(visible)
        control_truths.append(hidden)
    invalid = [
        dict(case_id="contradictory_label_control",
             input=dict(alphabet=["a", "b"], positive=["a"], negative=["a"])),
    ]
    files = {
        "inputs.jsonl": b"".join(canonical(row) for row in records),
        "truth_sidecars.jsonl": b"".join(canonical(row) for row in truths),
        "controls.jsonl": b"".join(canonical(row) for row in control_records),
        "control_truth_sidecars.jsonl": b"".join(canonical(row) for row in control_truths),
        "invalid_controls.jsonl": b"".join(canonical(row) for row in invalid),
    }
    file_manifest = {}
    for name, raw in files.items():
        (args.output / name).write_bytes(raw)
        file_manifest[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    manifest = dict(corpus="C006_UNKNOWN_K_REGULAR_V1", seed=SEED,
                    base_cases=120, cases_per_size=20, sizes=list(SIZES),
                    distinct_base_payloads=len(records), valid_controls=len(control_records),
                    invalid_controls=len(invalid), files=file_manifest,
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    protocol="PROTOCOL_V1.md",
                    input_policy="No k, q, partition, DFA, or grammar in solver-visible rows.",
                    scientific_status="frozen_before_candidate_comparison")
    raw = canonical(manifest)
    (args.output / "manifest.json").write_bytes(raw)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

"""Deterministic C004 stage-1 corpus builder (standard library only)."""
from __future__ import annotations
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "corpora" / "stage1_v4"
INPUTS = ROOT / "inputs"
HIDDEN = ROOT / "hidden_truth"


def alphabet_chars(n):
    return [chr(0x0400 + i) for i in range(n)]


def rgs_partitions(n, k):
    if n < 1 or k < 1 or k > n:
        return
    owner = [0] * n
    def visit(pos, max_owner):
        if pos == n:
            if max_owner + 1 == k:
                yield tuple(owner)
            return
        upper = min(max_owner + 1, k - 1)
        for side in range(upper + 1):
            owner[pos] = side
            yield from visit(pos + 1, max(max_owner, side))
    yield from visit(1, 0)


def blocks_from_owner(alphabet, owner):
    return [ [a for a, s in zip(alphabet, owner) if s == side]
             for side in range(max(owner) + 1) ]


def shuffle_words(words, rng):
    cursors = [0] * len(words)
    out = []
    remaining = sum(map(len, words))
    while remaining:
        available = [i for i, w in enumerate(words) if cursors[i] < len(w)]
        factor = rng.choice(available)
        out.append(words[factor][cursors[factor]])
        cursors[factor] += 1
        remaining -= 1
    return "".join(out)


def projections(word, blocks):
    return ["".join(ch for ch in word if ch in set(block)) for block in blocks]


def canonical_truth(blocks, local_languages):
    pairs = sorted(zip([sorted(b) for b in blocks], local_languages), key=lambda item: item[0])
    return {"blocks": [x[0] for x in pairs],
            "local_languages": [sorted(set(x[1])) for x in pairs]}


def write_case(records, case_id, family, data, truth=None, **meta):
    data = dict(data)
    INPUTS.mkdir(parents=True, exist_ok=True)
    HIDDEN.mkdir(parents=True, exist_ok=True)
    ipath = INPUTS / f"{case_id}.json"
    ipath.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    tpath = None
    if truth is not None:
        tpath = HIDDEN / f"{case_id}.json"
        tpath.write_text(json.dumps(truth, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    records.append({"id": case_id, "family": family,
                    "input": str(ipath.relative_to(ROOT)).replace("\\", "/"),
                    "truth": str(tpath.relative_to(ROOT)).replace("\\", "/") if tpath else None,
                    "alphabet_size": len(data.get("alphabet", [])),
                    "k": data.get("k"),
                    "positive_count": len(data.get("positive", [])),
                    "negative_count": len(data.get("negative", [])),
                    "positive_lengths": sorted(set(len(x) for x in data.get("positive", []) if isinstance(x, str))),
                    "negative_lengths": sorted(set(len(x) for x in data.get("negative", []) if isinstance(x, str))), **meta})


def rand_word(rng, symbols, maximum=5, allow_empty=True):
    size = rng.randint(0 if allow_empty else 1, maximum)
    return "".join(rng.choice(symbols) for _ in range(size))


def make_general_small(records, n, k, seed):
    rng = random.Random(seed)
    alpha = alphabet_chars(n)
    owner = next(iter(rgs_partitions(n, k)))
    allp = list(rgs_partitions(n, k))
    owner = allp[rng.randrange(len(allp))]
    blocks = blocks_from_owner(alpha, owner)
    langs = []
    for block in blocks:
        lang = {rand_word(rng, block, 4, allow_empty=True) for _ in range(rng.randint(1, 3))}
        langs.append(sorted(lang))
    positives = set()
    for _ in range(rng.randint(3, 5)):
        selected = [rng.choice(lang) for lang in langs]
        positives.add(shuffle_words(selected, rng))
    negatives = set()
    attempts = 0
    while len(negatives) < 2 and attempts < 1000:
        attempts += 1
        word = rand_word(rng, alpha, 9, allow_empty=True)
        if word in positives:
            continue
        imgs = projections(word, blocks)
        if any(img not in lang for img, lang in zip(imgs, langs)):
            negatives.add(word)
    truth = canonical_truth(blocks, langs)
    write_case(records, f"small_general_n{n}_k{k}_s{seed}", "small_general",
               {"alphabet": alpha, "k": k, "positive": sorted(positives), "negative": sorted(negatives)},
               truth, seed=seed)


def make_singleton_small(records, n, k, seed):
    rng = random.Random(seed)
    alpha = alphabet_chars(n)
    allp = list(rgs_partitions(n, k))
    owner = allp[rng.randrange(len(allp))]
    blocks = blocks_from_owner(alpha, owner)
    local = [rand_word(rng, block, 6, allow_empty=False) for block in blocks]
    positives = set()
    for j in range(4):
        order = list(range(k))
        if j == 0:
            rng.shuffle(order)
        elif j == 1:
            order.reverse()
        elif j == 2:
            order = order[1:] + order[:1]
        else:
            rng.shuffle(order)
        words = [local[i] for i in order]
        positives.add("".join(words))
    negatives = set()
    # A local substitution keeps length fixed and breaks the known singleton projection.
    base = list("".join(local))
    pos_set = set(positives)
    for side in (0, min(1, k - 1)):
        block = blocks[side]
        index = next((i for i, ch in enumerate(base) if ch in set(block)), None)
        if index is None:
            continue
        replacement = next(ch for ch in alpha if ch not in set(block))
        candidate = base.copy()
        candidate[index] = replacement
        word = "".join(candidate)
        if word not in pos_set:
            negatives.add(word)
    truth = canonical_truth(blocks, [[w] for w in local])
    write_case(records, f"small_singleton_n{n}_k{k}_s{seed}", "small_singleton",
               {"alphabet": alpha, "k": k, "positive": sorted(positives), "negative": sorted(negatives)},
               truth, seed=seed)


def make_long_singleton(records, n, k, length, stress=False):
    alpha = alphabet_chars(n)
    owner = tuple(min(k - 1, i * k // n) for i in range(n))
    blocks = blocks_from_owner(alpha, owner)
    base, rem = divmod(length, k)
    local = []
    for i, block in enumerate(blocks):
        target = base + (1 if i < rem else 0)
        local.append("".join(block[j % len(block)] for j in range(target)))
    forward = "".join(local)
    reverse = "".join(reversed(local))
    if length > 1:
        rr = [0] * k
        roundrobin = []
        while sum(rr) < length:
            for i in range(k):
                if rr[i] < len(local[i]):
                    roundrobin.append(local[i][rr[i]])
                    rr[i] += 1
        # Forward/reverse are the proof witnesses; round-robin exercises another long shuffle.
        positives = sorted({forward, reverse, "".join(roundrobin)})
    else:
        positives = sorted({forward, reverse})
    # Two same-length counterexamples. Substitute a symbol across hidden blocks.
    negatives = []
    for src_side, dst_side in ((0, 1), (k - 1, 0)):
        candidate = list(forward)
        source = blocks[src_side][0]
        dst = blocks[dst_side][0]
        idx = candidate.index(source)
        candidate[idx] = dst
        neg = "".join(candidate)
        if neg not in positives and neg not in negatives:
            negatives.append(neg)
    truth = canonical_truth(blocks, [[w] for w in local])
    case_id = f"{'stress' if stress else 'long_singleton'}_a{n}_k{k}_l{length}"
    write_case(records, case_id, "stress_16384" if stress else "long_singleton",
               {"alphabet": alpha, "k": k, "positive": positives, "negative": sorted(negatives)},
               truth, length=length)


def random_dfa(block, seed, states=4):
    rng = random.Random(seed)
    symbols = sorted(block)
    trans = {str(q): {a: rng.randrange(states) for a in symbols} for q in range(states)}
    return {"states": list(range(states)), "alphabet": symbols, "start": 0,
            "transitions": trans, "accepting": [], "seed": seed}


def dfa_step(dfa, word):
    state = dfa["start"]
    for ch in word:
        state = dfa["transitions"][str(state)][ch]
    return state


def accepted_word_for_length(block, dfa, length, rng, mode="random"):
    if mode == "pattern":
        x, y = block[0], block[1]
        singles = block[2:]
        out = []
        i = 0
        while i < length:
            if i + 1 < length and rng.random() < 0.45:
                out.extend((x, y))
                i += 2
            else:
                out.append(rng.choice(singles))
                i += 1
        word = "".join(out)
        # By construction all token strings are accepted by the pattern DFA.
        return word
    return "".join(rng.choice(block) for _ in range(length))


def pattern_dfa(block):
    # Boundary state 0 accepts; x starts a required xy token; all other
    # letters except y are single-letter tokens. State 2 is a rejecting sink.
    x, y = block[0], block[1]
    trans = {"0": {}, "1": {}, "2": {}}
    for ch in block:
        trans["0"][ch] = 1 if ch == x else (2 if ch == y else 0)
        trans["1"][ch] = 0 if ch == y else 2
        trans["2"][ch] = 2
    return {"states": [0, 1, 2], "alphabet": sorted(block), "start": 0,
            "transitions": trans, "accepting": [0]}


def assemble_product(locals_, rng):
    return shuffle_words(locals_, rng)


def make_product_case(records, n, k, length, seed, contextual=False):
    rng = random.Random(seed)
    alpha = alphabet_chars(n)
    owner = tuple(min(k - 1, i * k // n) for i in range(n))
    blocks = blocks_from_owner(alpha, owner)
    if contextual and min(map(len, blocks)) < 3:
        raise ValueError("contextual tier needs at least three letters in each factor")
    dfas = [pattern_dfa(b) if contextual else random_dfa(b, seed + 131 * i)
            for i, b in enumerate(blocks)]
    lengths = [length // k + (1 if i < length % k else 0) for i in range(k)]
    positive_words = set()
    positive_locals = []
    for sample_index in range(3):
        local_words = []
        for i, block in enumerate(blocks):
            local = accepted_word_for_length(block, dfas[i], lengths[i], rng,
                                              "pattern" if contextual else "random")
            local_words.append(local)
        positive_locals.append(local_words)
        if not contextual:
            for i, local in enumerate(local_words):
                dfa = dfas[i]
                dfa["accepting"].append(dfa_step(dfa, local))
                dfa["accepting"] = sorted(set(dfa["accepting"]))
        positive_words.add(assemble_product(local_words, rng))
    negatives = set()
    for attempt in range(1000):
        word = "".join(rng.choice(alpha) for _ in range(length))
        if word in positive_words:
            continue
        bad = False
        for block, dfa in zip(blocks, dfas):
            local = "".join(ch for ch in word if ch in set(block))
            if dfa_step(dfa, local) not in dfa["accepting"]:
                bad = True
                break
        if bad:
            negatives.add(word)
        if len(negatives) >= 2:
            break
    labels = {"blocks": [sorted(b) for b in blocks], "dfas": dfas,
              "positive_local_words_by_sample": positive_locals,
              "generation": "deterministic random DFA product" if not contextual else "contextual token-cycle regular product"}
    prefix = "context_regular" if contextual else ("random_dfa_small" if n <= 7 else "random_dfa")
    case_id = f"{prefix}_a{n}_k{k}_l{length}_s{seed}"
    write_case(records, case_id, prefix,
               {"alphabet": alpha, "k": k, "positive": sorted(positive_words),
                "negative": sorted(negatives)}, labels, length=length, seed=seed)


def make_boundaries(records):
    a = alphabet_chars(4)
    boundary = [
        ("edge_rescue_counterexample", {"alphabet": a[:2], "k": 2, "positive": ["", a[1]], "negative": [a[0]]}, None),
        ("edge_rescue_true_control", {"alphabet": a[:2], "k": 2, "positive": ["", a[1], a[0]+a[1]], "negative": [a[0]]}, None),
        ("three_color_connected_nonunique", {"alphabet": a, "k": 3,
         "positive": ["".join(a[i] for i in order) for order in
                      ((0, 1, 2, 3), (1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))],
         "negative": []}, None),
        ("empty_both", {"alphabet": a[:3], "k": 2, "positive": [], "negative": []}, None),
        ("empty_positive_negative", {"alphabet": a[:3], "k": 2, "positive": [], "negative": [a[0], a[1] * 2]}, None),
        ("empty_negative", {"alphabet": a[:3], "k": 2, "positive": [a[0] + a[1], a[1] + a[0]], "negative": []}, None),
        ("absent_symbols", {"alphabet": a, "k": 2, "positive": [a[0] + a[0], a[0] * 3], "negative": [a[1] + a[1]]}, None),
        ("epsilon_positive", {"alphabet": a[:2], "k": 2, "positive": [""], "negative": [a[0]]}, None),
        ("repeated_symbols", {"alphabet": a[:4], "k": 3, "positive": [a[0]*2+a[1]+a[2]*2, a[2]*2+a[0]*2+a[1]], "negative": [a[0]*2+a[3]+a[2]*2]}, None),
        ("duplicate_samples", {"alphabet": a[:3], "k": 2, "positive": [a[0]+a[1], a[0]+a[1], a[1]+a[0]], "negative": [a[2], a[2]]}, None),
    ]
    for case_id, data, truth in boundary:
        # No planted truth is supplied for hand-constructed controls.
        write_case(records, case_id, "boundary", data, truth)
    invalid = [
        ("invalid_k_zero", {"alphabet": a[:2], "k": 0, "positive": [a[0]], "negative": []}),
        ("invalid_k_one", {"alphabet": a[:2], "k": 1, "positive": [a[0]], "negative": []}),
        ("invalid_k_too_large", {"alphabet": a[:2], "k": 3, "positive": [a[0]], "negative": []}),
        ("invalid_k_bool", {"alphabet": a[:2], "k": True, "positive": [a[0]], "negative": []}),
        ("invalid_k_float", {"alphabet": a[:2], "k": 2.0, "positive": [a[0]], "negative": []}),
        ("invalid_alphabet_duplicate", {"alphabet": [a[0], a[0]], "k": 2, "positive": [], "negative": []}),
        ("invalid_unknown_symbol", {"alphabet": a[:2], "k": 2, "positive": [a[0] + "Z"], "negative": []}),
        ("invalid_contradictory_label", {"alphabet": a[:2], "k": 2, "positive": [a[0]], "negative": [a[0]]}),
        ("invalid_positive_type", {"alphabet": a[:2], "k": 2, "positive": [17], "negative": []}),
    ]
    for case_id, data in invalid:
        write_case(records, case_id, "invalid", data, None)


def main():
    if ROOT.exists():
        raise FileExistsError(f"refusing to replace frozen corpus directory: {ROOT}")
    records = []
    make_boundaries(records)
    small_seed_base = 44110
    for n in range(3, 8):
        for k in range(2, min(n, 4) + 1):
            pair_idx = n * 19 + k * 7
            for rep in range(2):
                seed = small_seed_base + pair_idx * 11 + rep
                make_general_small(records, n, k, seed)
                make_singleton_small(records, n, k, seed + 500)
                if rep == 0:
                    make_product_case(records, n, k, 24, 64000 + n * 1000 + k * 100 + rep, contextual=False)
    for n in (8, 32, 128):
        for k in (2, 3, 4, 6, 8):
            if k <= n:
                for length in (128, 1024, 4096):
                    make_long_singleton(records, n, k, length)
    for n in (8, 32, 128):
        for k in (2, 3, 4, 6, 8):
            for length in (128, 1024, 4096):
                # For n=8,k=8 factor alphabets are unary; random-DFA works,
                # but token-context tier requires at least 3 letters per factor.
                make_product_case(records, n, k, length, 76000 + n * 1000 + k * 100 + length,
                                  contextual=False)
                if n >= 32:
                    make_product_case(records, n, k, length, 91000 + n * 1000 + k * 100 + length,
                                      contextual=True)
    for k in (2, 4, 8):
        make_long_singleton(records, 128, k, 16384, stress=True)
    manifest = {"schema": "c004-stage1-corpus-v1", "seed_policy": "all seeds embedded in case metadata and deterministic generator source",
                "solver_input_excludes_truth": True, "case_count": len(records), "cases": records}
    ROOT.mkdir(parents=True, exist_ok=True)
    path = ROOT / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"corpus_root": str(ROOT), "case_count": len(records),
                      "families": {family: sum(r["family"] == family for r in records)
                                   for family in sorted({r["family"] for r in records})},
                      "manifest": str(path)}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()




"""Deterministically freeze C005 audit-owned solver inputs and hidden sidecars."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "frozen_corpus_v2"
INPUTS = ROOT / "small" / "inputs"
HIDDEN = ROOT / "small" / "hidden"
STRESS_INPUTS = ROOT / "stage2" / "inputs"
STRESS_HIDDEN = ROOT / "stage2" / "hidden"
SEED = 20261031


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alphabet_of(m: int) -> list[str]:
    if m <= 26:
        return [chr(ord("a") + i) for i in range(m)]
    return [chr(0x100 + i) for i in range(m)]


def rgs_partitions(symbols: list[str], k: int):
    """Independent restricted-growth enumeration, in deterministic order."""
    n = len(symbols)
    owners = [0] * n

    def visit(pos: int, high: int):
        if pos == n:
            if high + 1 == k:
                blocks = [tuple(symbols[i] for i, side in enumerate(owners) if side == j)
                          for j in range(k)]
                yield tuple(sorted(tuple(sorted(block)) for block in blocks))
            return
        for side in range(min(high + 1, k - 1) + 1):
            owners[pos] = side
            yield from visit(pos + 1, max(high, side))

    if n:
        yield from visit(1, 0)


def project(word: str, block: tuple[str, ...] | list[str] | set[str]) -> str:
    chosen = set(block)
    return "".join(ch for ch in word if ch in chosen)


def oracle(data: dict, cap: int | None) -> list[list[list[str]]]:
    symbols = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    feasible = []
    for partition in rgs_partitions(symbols, data["k"]):
        languages = [{project(word, block) for word in positives} for block in partition]
        if cap is not None and any(len(language) > cap for language in languages):
            continue
        if any(all(project(word, block) in languages[i]
                  for i, block in enumerate(partition)) for word in negatives):
            continue
        feasible.append([list(block) for block in partition])
    return feasible


def shuffled_join(parts: list[str], rng: random.Random) -> str:
    # Insert deterministic interleaving while preserving each factor projection.
    queues = [list(part) for part in parts]
    out = []
    while any(queues):
        live = [i for i, queue in enumerate(queues) if queue]
        rng.shuffle(live)
        for i in live[:rng.randint(1, min(3, len(live)))]:
            out.append(queues[i].pop(0))
    return "".join(out)


def random_word(rng: random.Random, alphabet: list[str], lo: int, hi: int) -> str:
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(lo, hi)))


def unequal_partition(alphabet: list[str], k: int, shift: int = 0) -> list[list[str]]:
    # Positive, surjective, strongly nonuniform when the sizes permit it.
    sizes = [1] * k
    for _ in range(len(alphabet) - k):
        sizes[(shift + len(alphabet) - k - _) % k] += 1
    blocks = []
    cursor = 0
    for size in sizes:
        blocks.append(alphabet[cursor:cursor + size])
        cursor += size
    return blocks


def make_planted(rng: random.Random, alphabet: list[str], k: int,
                 blocks: list[list[str]], q: int, *, missing: bool = False,
                 repeats: bool = False) -> tuple[dict, dict]:
    effective = [list(b) for b in blocks]
    if missing and len(alphabet) > k:
        # A source symbol remains in Sigma but is excluded from all traces.
        effective[-1] = effective[-1][:-1] or effective[-1]
    block_words: list[list[str]] = []
    for bi, block in enumerate(effective):
        if not block:
            block = [blocks[bi][0]]
        count = max(1, min(q, 4))
        variants = []
        for variant in range(count):
            seq = list(block)
            if len(seq) > 1:
                seq = seq[variant % len(seq):] + seq[:variant % len(seq)]
                if variant % 2:
                    seq.reverse()
            if variant % 3 == 2:
                seq = seq + seq[:1]
            variants.append("".join(seq))
        # Remove accidental equalities for singleton / repeated-size cases.
        block_words.append(list(dict.fromkeys(variants)))
    nrows = max(len(row) for row in block_words)
    positives = []
    for row in range(nrows):
        components = [words[row % len(words)] for words in block_words]
        positives.append(shuffled_join(components, rng))
    positives = sorted(set(positives))
    source_langs = [set(words) for words in block_words]
    negatives = []
    # Keep only negatives guaranteed rejected by the planted finite product.
    for attempt in range(300):
        candidate = random_word(rng, alphabet, 1, max(2, 2 * len(alphabet)))
        projections = [project(candidate, block) for block in effective]
        if any(projections[i] not in source_langs[i] for i in range(k)):
            negatives.append(candidate)
        if len(negatives) == 2:
            break
    if repeats and positives:
        positives = positives + [positives[0], positives[0]]
    data = {"alphabet": alphabet, "k": k, "positive": positives, "negative": sorted(set(negatives))}
    hidden = {
        "family": "planted_finite_language",
        "source_blocks": [sorted(b) for b in blocks],
        "effective_trace_blocks": [sorted(b) for b in effective],
        "source_local_languages": [sorted(x) for x in source_langs],
        "planted_cap": q,
        "missing_symbols": sorted(set(alphabet) - set("".join(positives + negatives))),
        "repeat_injection": repeats,
    }
    return data, hidden


def case_id(m: int, k: int, family: str, index: int) -> str:
    return f"small_m{m}_k{k}_{family}_{index:02d}"


def write_case(directory: Path, case: str, data: dict, sidecar: dict,
               records: list[dict], expected_modes: list[int | None] | None = None):
    ipath = directory / "inputs" / f"{case}.json"
    hpath = directory / "hidden" / f"{case}.json"
    ipath.parent.mkdir(parents=True, exist_ok=True)
    hpath.parent.mkdir(parents=True, exist_ok=True)
    ipath.write_bytes(canonical_json(data))
    hpath.write_bytes(canonical_json(sidecar))
    records.append({
        "id": case,
        "input": ipath.relative_to(ROOT).as_posix(),
        "input_sha256": digest(ipath),
        "input_bytes": ipath.stat().st_size,
        "hidden": hpath.relative_to(ROOT).as_posix(),
        "hidden_sha256": digest(hpath),
        "hidden_bytes": hpath.stat().st_size,
        "m": len(data["alphabet"]),
        "k": data["k"],
        "positive_count_raw": len(data["positive"]),
        "positive_count_distinct": len(set(data["positive"])),
        "negative_count_raw": len(data["negative"]),
        "negative_count_distinct": len(set(data["negative"])),
        "positive_lengths": sorted(set(map(len, data["positive"]))),
        "negative_lengths": sorted(set(map(len, data["negative"]))),
        "q_modes": expected_modes or [1, 2, 3, 4, None],
        "family": sidecar.get("family", "control"),
    })


def generate_small() -> list[dict]:
    records: list[dict] = []
    for m in range(2, 8):
        alphabet = alphabet_of(m)
        for k in range(2, m + 1):
            pairseed = SEED + m * 101 + k * 17
            rng = random.Random(pairseed)
            blocks = unequal_partition(alphabet, k, (m + k) % k)
            specs = [
                ("planted", "planted_finite_language"),
                ("unequal", "planted_unequal_blocks"),
                ("missing", "planted_missing_event_symbols"),
                ("random_labels", "random_exact_label_assignments"),
                ("sparse", "sparse_random_finite_language"),
                ("repeats", "repeated_events_and_duplicate_examples"),
                ("empty", "ambiguous_empty_sample"),
                ("qstress", "q_opposition_stress"),
            ]
            for i, (tag, family) in enumerate(specs):
                local = random.Random(pairseed * 37 + i * 997)
                if tag in ("planted", "unequal", "missing", "repeats", "qstress"):
                    partition = blocks if tag != "planted" else [[x] for x in alphabet[:k - 1]] + [alphabet[k - 1:]]
                    partition = [b for b in partition if b]
                    # The planted default above can yield fewer than k blocks only
                    # when m==k; there it is exactly k singleton blocks.
                    q = 2 if tag == "qstress" else (1 + i % 4)
                    data, hidden = make_planted(local, alphabet, k, partition, q,
                                               missing=(tag == "missing"), repeats=(tag == "repeats"))
                    hidden["family"] = family
                elif tag in ("random_labels", "sparse"):
                    positive, negative = set(), set()
                    # De-duplicate before assigning labels; repeated random draws
                    # must not put one exact word in both classes.
                    pool = list({random_word(local, alphabet, 0, max(1, m + 1))
                                 for _ in range(24 if tag == "random_labels" else 8)})
                    local.shuffle(pool)
                    for word in pool:
                        (positive if local.random() < (0.5 if tag == "random_labels" else 0.28) else negative).add(word)
                    if not positive and tag == "random_labels":
                        positive.add(random_word(local, alphabet, 0, m))
                    data = {"alphabet": alphabet, "k": k, "positive": sorted(positive), "negative": sorted(negative)}
                    hidden = {"family": family, "assignment_seed": pairseed * 37 + i * 997,
                              "planted_partition": None, "interpretation": "No generating decomposition is claimed."}
                else:
                    data = {"alphabet": alphabet, "k": k, "positive": [], "negative": []}
                    hidden = {"family": family, "planted_partition": None,
                              "interpretation": "All nonempty k-partitions are feasible under empty observations."}
                # Ensure every payload is a canonical exact-label instance.
                data["positive"] = list(data["positive"])
                data["negative"] = list(data["negative"])
                write_case(ROOT / "small", case_id(m, k, family, i), data, hidden, records)

    # Required historical counterexample, retained as an independent regression.
    p4 = {"alphabet": list("abcd"), "k": 3,
          "positive": ["abcd", "bacd", "acbd", "abdc"], "negative": []}
    write_case(ROOT / "small", "control_connected_p4_k3",
               p4, {"family": "connected_p4_control", "planted_partition": None}, records)

    # Pairwise q-opposition has no edges, but the whole abc projection set has 4 > q.
    fullblock = {"alphabet": list("abc"), "k": 2,
                 "positive": ["abc", "bca", "cab", "acb"], "negative": []}
    write_case(ROOT / "small", "control_q2_full_block_cap_failure",
               fullblock, {"family": "full_block_cap_control", "target_blocks": [["a", "b", "c"]]}, records)

    write_case(ROOT / "small", "control_negative_distinguishing",
               {"alphabet": list("ab"), "k": 2, "positive": ["ab"], "negative": ["aa"]},
               {"family": "negative_distinguishing_control", "target_blocks": [["a"], ["b"]]}, records)
    write_case(ROOT / "small", "control_negative_accepted",
               {"alphabet": list("ab"), "k": 2, "positive": ["ab"], "negative": ["ba"]},
               {"family": "negative_accepted_control", "target_blocks": None}, records)
    write_case(ROOT / "small", "control_empty_word_positive",
               {"alphabet": list("ab"), "k": 2, "positive": [""], "negative": []},
               {"family": "empty_word_control", "interpretation": "Nonempty positive sample containing epsilon."}, records)
    write_case(ROOT / "small", "control_empty_positive_negative",
               {"alphabet": list("ab"), "k": 2, "positive": [], "negative": ["ab"]},
               {"family": "empty_positive_control", "interpretation": "No positive samples."}, records)

    # Deliberately invalid controls remain outside the canonical valid case count.
    invalid = [
        ("control_invalid_contradictory_labels", {"alphabet": list("ab"), "k": 2, "positive": ["ab"], "negative": ["ab"]}, "contradictory_labels"),
        ("control_invalid_unknown_symbol", {"alphabet": list("ab"), "k": 2, "positive": ["ac"], "negative": []}, "unknown_symbol"),
        ("control_invalid_k", {"alphabet": list("ab"), "k": 3, "positive": [], "negative": []}, "invalid_k"),
    ]
    for case, data, error in invalid:
        write_case(ROOT / "small", case, data, {"family": "invalid_input_control", "expected_error": error}, records)
    return records


def large_word(rng: random.Random, symbols: list[str], length: int) -> str:
    return "".join(symbols[rng.randrange(len(symbols))] for _ in range(length))


def make_stress_case(m: int, k: int, length: int, q: int, family: str, serial: int):
    alphabet = alphabet_of(m)
    rng = random.Random(SEED + 1_000_003 * m + 10_007 * k + 101 * length + q + serial)
    case = f"stage2_m{m}_k{k}_L{length}_q{q}_{family}_{serial:02d}"
    if family == "planted_unequal_blocks":
        blocks = unequal_partition(alphabet, k, serial % k)
        # Promote sizes to at least two where possible so each factor admits
        # distinct local projection variants, while retaining unequal sizes.
        local_words = []
        for bi, block in enumerate(blocks):
            variants = []
            base = block[:]
            chunk_size = max(1, length // k)
            for v in range(q):
                seq = base[v % len(base):] + base[:v % len(base)] if base else []
                if v & 1:
                    seq.reverse()
                if not seq:
                    seq = [alphabet[bi]]
                repeats = max(1, (chunk_size + len(seq) - 1) // len(seq))
                variants.append(("".join(seq) * repeats)[:chunk_size])
            local_words.append(list(dict.fromkeys(variants)))
        row_count = max(max(map(len, local_words)), 1)
        positives = []
        for j in range(row_count):
            selected = [words[j % len(words)] for words in local_words]
            # Fixed-order concatenation yields an exact deterministic long trace.
            word = "".join(selected)
            if len(word) < length:
                word += ("".join(alphabet) * (length // m + 1))[:length - len(word)]
            positives.append(word[:length])
        effective_words = [set(words) for words in local_words]
        negatives = []
        for attempt in range(500):
            # A short random trace almost surely has at least one unseen factor projection.
            word = large_word(rng, alphabet, length)
            if any(project(word, b) not in effective_words[i] for i, b in enumerate(blocks)):
                negatives.append(word)
            if len(negatives) == 2:
                break
        data = {"alphabet": alphabet, "k": k, "positive": sorted(set(positives)), "negative": sorted(set(negatives))}
        hidden = {"family": family, "source_blocks": [sorted(b) for b in blocks],
                  "planted_q": q, "source_local_languages": [sorted(x) for x in effective_words]}
    else:
        # Sparse random traces deliberately do not carry a generating partition.
        positives = [large_word(rng, alphabet, length) for _ in range(3)]
        negatives = [large_word(rng, alphabet, length) for _ in range(2)]
        # Avoid contradictory exact labels while keeping the intended sparse trace mix.
        negative_set = set(negatives) - set(positives)
        data = {"alphabet": alphabet, "k": k, "positive": sorted(set(positives)), "negative": sorted(negative_set)}
        hidden = {"family": "sparse_random_traces", "assignment_seed": SEED + 1_000_003 * m + 10_007 * k + 101 * length + q + serial,
                  "planted_partition": None, "ambiguity": "expected; no uniqueness label is preassigned"}
    ipath = STRESS_INPUTS / f"{case}.json"
    hpath = STRESS_HIDDEN / f"{case}.json"
    ipath.parent.mkdir(parents=True, exist_ok=True)
    hpath.parent.mkdir(parents=True, exist_ok=True)
    ipath.write_bytes(canonical_json(data))
    hpath.write_bytes(canonical_json(hidden))
    return {"id": case, "input": ipath.relative_to(ROOT).as_posix(), "input_sha256": digest(ipath),
            "input_bytes": ipath.stat().st_size, "hidden": hpath.relative_to(ROOT).as_posix(),
            "hidden_sha256": digest(hpath), "hidden_bytes": hpath.stat().st_size,
            "m": m, "k": k, "length_target": length, "positive_lengths": sorted(set(map(len, data["positive"]))),
            "negative_lengths": sorted(set(map(len, data["negative"]))), "q_mode": q,
            "family": hidden["family"], "truth_available": hidden.get("source_blocks") is not None}


def generate_stage2() -> list[dict]:
    records = []
    configs = [
        (16, 2, 4096), (32, 4, 4096), (64, 8, 4096), (128, 8, 4096),
        (256, 16, 4096), (32, 2, 32768), (64, 4, 32768), (128, 8, 32768),
        (256, 16, 32768), (16, 16, 32768),
    ]
    for i, (m, k, length) in enumerate(configs):
        for q in (3, 4):
            records.append(make_stress_case(m, k, length, q, "planted_unequal_blocks", i * 2 + q))
    for serial, (m, k, length) in enumerate([(16, 4, 4096), (64, 8, 4096), (256, 16, 4096),
                                               (128, 8, 32768), (256, 16, 32768)]):
        for q in (3, 4):
            records.append(make_stress_case(m, k, length, q, "sparse_random_traces", serial * 2 + q))
    return records


def main() -> None:
    for path in (INPUTS, HIDDEN, STRESS_INPUTS, STRESS_HIDDEN):
        if path.exists() and any(path.rglob("*")):
            raise SystemExit(f"refusing to overwrite nonempty corpus path: {path}")
    small = generate_small()
    stage2 = generate_stage2()
    canonical_payloads = set()
    valid_payloads = set()
    for row in small:
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        payload = (data["k"], tuple(data["alphabet"]), tuple(data["positive"]), tuple(data["negative"]))
        canonical_payloads.add(payload)
        if row["family"] != "invalid_input_control":
            valid_payloads.add(payload)
    if len(valid_payloads) < 120:
        raise SystemExit(f"small valid canonical payload count below target: {len(valid_payloads)}")
    manifest = {
        "schema": "C005-independent-frozen-corpus-v1",
        "seed": SEED,
        "generator": "audit/generate_corpus_v1.py",
        "protocol": "audit/corpus_protocol_v1.json",
        "small": {"case_count": len(small), "canonical_payload_count": len(canonical_payloads),
                  "valid_canonical_payload_count": len(valid_payloads), "cases": small},
        "stage2": {"case_count": len(stage2), "cases": stage2},
        "corpus_policy": "Inputs and hidden sidecars are frozen together. Provider receives inputs only. This manifest and the freeze record reveal no planted sidecar content.",
    }
    mpath = ROOT / "manifest_v1.json"
    mpath.write_bytes(canonical_json(manifest))
    freeze = {
        "schema": "C005-independent-corpus-freeze-v1",
        "seed": SEED,
        "manifest_sha256": digest(mpath),
        "manifest_bytes": mpath.stat().st_size,
        "small_case_count": len(small),
        "small_canonical_payload_count": len(canonical_payloads),
        "small_valid_canonical_payload_count": len(valid_payloads),
        "stage2_case_count": len(stage2),
        "input_files": sum(1 for _ in INPUTS.glob("*.json")) + sum(1 for _ in STRESS_INPUTS.glob("*.json")),
        "hidden_sidecars": sum(1 for _ in HIDDEN.glob("*.json")) + sum(1 for _ in STRESS_HIDDEN.glob("*.json")),
        "execution_policy": "No provider execution occurs during corpus generation. Solver runs require capture.py and the frozen manifest, all relevant inputs, drivers, protocols, and provider source files in the source snapshot.",
    }
    fpath = ROOT / "freeze_record_v1.json"
    fpath.write_bytes(canonical_json(freeze))
    print(json.dumps({"manifest_sha256": freeze["manifest_sha256"],
                      "small_case_count": len(small),
                      "small_canonical_payload_count": len(canonical_payloads),
                      "stage2_case_count": len(stage2),
                      "input_files": freeze["input_files"],
                      "hidden_sidecars": freeze["hidden_sidecars"]}, sort_keys=True))


if __name__ == "__main__":
    main()

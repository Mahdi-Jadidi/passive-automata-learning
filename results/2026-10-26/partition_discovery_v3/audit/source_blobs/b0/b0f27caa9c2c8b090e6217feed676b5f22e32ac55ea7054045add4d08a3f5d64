"""Deterministically generate and freeze C003 audit corpora and job list.

Run from the workspace root with the configured Python 3.12 runtime. The
generator writes solver inputs separately from truth sidecars. It never imports
or executes a candidate provider.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
C003 = ROOT / "results/2026-10-26/partition_discovery_v3"
AUDIT = C003 / "audit"
OUT = AUDIT / "corpus/frozen_c003_v1"
C002 = ROOT / "results/2026-10-26/partition_constraints_v2"
FROZEN = C002 / "audit/corpus/frozen_v1"
CORRECTNESS = C002 / "audit/correctness_runs/20261026T125503.860658Z_805e5494"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical(row) for row in rows))


def shuffle_merge(left: str, right: str, rng: random.Random) -> str:
    out = []
    i = j = 0
    while i < len(left) or j < len(right):
        if i == len(left):
            take_left = False
        elif j == len(right):
            take_left = True
        else:
            take_left = bool(rng.getrandbits(1))
        if take_left:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return "".join(out)


def dfa_make(rng: random.Random, alphabet: list[str]) -> dict:
    n = rng.randint(2, 5)
    accepting_count = rng.randint(1, n - 1)
    return {"states": n, "start": rng.randrange(n),
            "accepting": sorted(rng.sample(range(n), accepting_count)),
            "transitions": [[rng.randrange(n) for _ in alphabet] for _ in range(n)]}


def dfa_accepts(dfa: dict, word: str, alphabet: list[str]) -> bool:
    index = {a: i for i, a in enumerate(alphabet)}
    state = dfa["start"]
    for symbol in word:
        state = dfa["transitions"][state][index[symbol]]
    return state in dfa["accepting"]


def random_dfa_cases() -> tuple[list[dict], list[dict]]:
    rng = random.Random(20261026)
    inputs, truths = [], []
    for m in (4, 6, 8, 10, 12, 16):
        alphabet = [chr(ord("a") + i) for i in range(m)]
        blocks = [alphabet[:m//2], alphabet[m//2:]]
        for k in range(20):
            sample_rng = random.Random(rng.getrandbits(128))
            attempts = pair_attempts = 0
            while True:
                pair_attempts += 1
                left, right = dfa_make(rng, blocks[0]), dfa_make(rng, blocks[1])
                positives, negatives = set(), set()
                local_attempts = 0
                while (len(positives) < 12 or len(negatives) < 12) and local_attempts < 50000:
                    local_attempts += 1
                    length = sample_rng.randint(1, 24)
                    word = "".join(sample_rng.choice(alphabet) for _ in range(length))
                    accepted = (dfa_accepts(left, "".join(a for a in word if a in set(blocks[0])), blocks[0]) and
                                dfa_accepts(right, "".join(a for a in word if a in set(blocks[1])), blocks[1]))
                    (positives if accepted else negatives).add(word)
                attempts += local_attempts
                if len(positives) >= 12 and len(negatives) >= 12:
                    break
                if pair_attempts >= 100:
                    raise RuntimeError(f"could not fill balanced sample: m={m}, k={k}")
            pos = sorted(positives)[:12]
            neg = sorted(negatives)[:12]
            case_id = f"random_dfa_m{m}_{k:03d}"
            inputs.append({"case_id": case_id,
                           "input": {"alphabet": alphabet,
                                     "positive": pos, "negative": neg}})
            truths.append({"case_id": case_id, "blocks": blocks,
                           "dfa_left": left, "dfa_right": right,
                           "sampling_attempts": attempts, "dfa_pair_attempts": pair_attempts,
                           "generator_seed": "20261026"})
    return inputs, truths


def fixed_word_cases() -> tuple[list[dict], list[dict]]:
    root_rng = random.Random(20261027)
    inputs, truths = [], []
    for m in (2, 8, 16, 32, 64, 128):
        alphabet = [chr(0x100 + i) for i in range(m)]
        for k in range(20):
            rng = random.Random(root_rng.getrandbits(128))
            order = alphabet[:]
            rng.shuffle(order)
            cut = 1 if m == 2 else rng.randint(1, m - 1)
            left_symbols, right_symbols = order[:cut], order[cut:]
            # Two copies ensure deliberate repeats while every block symbol is covered.
            left = "".join(s * rng.randint(1, 3) for s in left_symbols)
            right = "".join(s * rng.randint(1, 3) for s in right_symbols)
            pset = [left + right, right + left]
            pset.extend(shuffle_merge(left, right, rng) for _ in range(4))
            positives = sorted(set(pset))
            def valid(word: str) -> bool:
                return ("".join(s for s in word if s in set(left_symbols)) == left and
                        "".join(s for s in word if s in set(right_symbols)) == right)
            negatives = set()
            attempts = 0
            while len(negatives) < 12 and attempts < 100000:
                attempts += 1
                length = rng.randint(1, len(left) + len(right) + 3)
                word = "".join(rng.choice(alphabet) for _ in range(length))
                if not valid(word):
                    negatives.add(word)
            if len(negatives) < 12:
                raise RuntimeError(f"could not construct negative sample: m={m}, k={k}")
            case_id = f"fixed_word_m{m}_{k:03d}"
            inputs.append({"case_id": case_id,
                           "input": {"alphabet": alphabet,
                                     "positive": positives,
                                     "negative": sorted(negatives)[:12]}})
            truths.append({"case_id": case_id, "blocks": [left_symbols, right_symbols],
                           "local_words": [left, right], "sampling_attempts": attempts,
                           "generator_seed": "20261027"})
    return inputs, truths


def load_c002_regressions() -> tuple[list[dict], list[dict]]:
    manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
    baseline_rows = {}
    with gzip.open(CORRECTNESS / "baseline.jsonl.gz", "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            baseline_rows[row["case_id"]] = row
    sampled = []
    rng = random.Random(20261028)
    for dataset, spec in manifest["datasets"].items():
        case_ids = [item["case_id"] for item in spec["case_input_hashes"]]
        if dataset == "random_ternary_5000":
            chosen = sorted(rng.sample(range(len(case_ids)), 60))
        else:
            chosen = sorted({0, (len(case_ids) - 1) // 2, len(case_ids) - 1})
        for index in chosen:
            case_id = case_ids[index]
            row = baseline_rows.get(case_id)
            if row is None or not row["result"].get("complete"):
                continue
            sampled.append((dataset, index, row))
    inputs, refs = [], []
    for dataset, index, row in sampled:
        case_id = row["case_id"]
        inputs.append({"case_id": case_id, "dataset": dataset, "input": row["input"],
                       "input_sha256": row["input_sha256"]})
        refs.append({"case_id": case_id, "dataset": dataset, "selected_index": index,
                     "baseline_f2": row["result"]})
    return inputs, refs


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dfa_in, dfa_truth = random_dfa_cases()
    fixed_in, fixed_truth = fixed_word_cases()
    regression_in, regression_ref = load_c002_regressions()
    files: dict[str, bytes] = {}
    for name, rows in (("random_dfa_inputs.jsonl", dfa_in),
                       ("random_dfa_truth.jsonl", dfa_truth),
                       ("fixed_word_inputs.jsonl", fixed_in),
                       ("fixed_word_truth.jsonl", fixed_truth),
                       ("c002_regression_inputs.jsonl", regression_in),
                       ("c002_regression_f2.jsonl", regression_ref)):
        dump_jsonl(OUT / name, rows)
        files[name] = (OUT / name).read_bytes()
    jobs = []
    for method, rows in (("general", regression_in), ("fair-reference", regression_in),
                         ("fixed-word", regression_in), ("general", dfa_in),
                         ("fair-reference", dfa_in), ("fixed-word", fixed_in)):
        if method == "fixed-word" and rows in (regression_in, dfa_in):
            continue
        for row in rows:
            jobs.append({"job_id": f"{method}__{row['case_id']}", "method": method,
                         "case_id": row["case_id"], "dataset": row.get("dataset", "generated"),
                         "input_file": ("c002_regression_inputs.jsonl" if rows is regression_in else
                                        "random_dfa_inputs.jsonl" if rows is dfa_in else
                                        "fixed_word_inputs.jsonl")})
    jobs.extend({"job_id": f"fixed-word__{row['case_id']}", "method": "fixed-word",
                 "case_id": row["case_id"], "dataset": "fixed_word_constructive",
                 "input_file": "fixed_word_inputs.jsonl"} for row in fixed_in)
    dump_jsonl(OUT / "job_list.jsonl", jobs)
    files["job_list.jsonl"] = (OUT / "job_list.jsonl").read_bytes()
    manifest = {"corpus_id": "C003-frozen-v1", "seed_policy": {
                    "random_dfa": 20261026, "fixed_word": 20261027,
                    "random_ternary_regression_sample": 20261028},
                "counts": {"random_dfa": len(dfa_in), "fixed_word": len(fixed_in),
                           "c002_regression": len(regression_in), "jobs": len(jobs)},
                "files": {name: {"bytes": len(raw), "sha256": sha(raw)}
                          for name, raw in sorted(files.items())},
                "c002_frozen_manifest_sha256": sha((FROZEN / "manifest.json").read_bytes()),
                "c002_baseline_f2_sha256": sha((CORRECTNESS / "baseline.jsonl.gz").read_bytes()),
                "generator_sha256": sha(Path(__file__).read_bytes()),
                "truth_policy": "truth sidecars are audit-only and are never passed to solvers",
                "generated_utc_policy": "omitted for byte-identical deterministic regeneration"}
    raw_manifest = canonical(manifest)
    (OUT / "freeze_manifest.json").write_bytes(raw_manifest)
    print(json.dumps({"manifest": str(OUT / "freeze_manifest.json"),
                      "sha256": sha(raw_manifest), "counts": manifest["counts"],
                      "files": manifest["files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

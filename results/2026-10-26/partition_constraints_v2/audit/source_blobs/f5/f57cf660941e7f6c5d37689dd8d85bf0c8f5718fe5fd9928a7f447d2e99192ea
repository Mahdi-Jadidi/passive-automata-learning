"""Build the immutable C002 sample-only corpus and separate generator truth."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent
BASELINE = CYCLE / "baseline"
CORPUS = AUDIT / "corpus" / "frozen_v1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def words(alphabet: list[str], max_len: int) -> list[str]:
    return ["".join(chars)
            for length in range(max_len + 1)
            for chars in itertools.product(alphabet, repeat=length)]


def input_data(alphabet: list[str], positive: list[str], negative: list[str]) -> dict:
    return {"alphabet": sorted(alphabet), "positive": sorted(positive),
            "negative": sorted(negative)}


def record(dataset: str, case_id: str, data: dict) -> dict:
    return {"case_id": case_id, "dataset": dataset, "input": data,
            "input_sha256": sha(canonical_json(data))}


def write_jsonl(path: Path, records: list[dict]) -> tuple[str, int]:
    raw = b"".join(canonical_json(item) + b"\n" for item in records)
    path.write_bytes(raw)
    return sha(raw), len(raw)


def label_strata(records: list[dict]) -> dict:
    presence = Counter()
    positive_counts = Counter()
    negative_counts = Counter()
    for item in records:
        data = item["input"]
        p, n = len(data["positive"]), len(data["negative"])
        key = "both" if p and n else "positive_only" if p else "negative_only" if n else "no_labels"
        presence[key] += 1
        positive_counts[str(p)] += 1
        negative_counts[str(n)] += 1
    return {"class_presence": dict(sorted(presence.items())),
            "positive_count_histogram": dict(sorted(positive_counts.items(), key=lambda x: int(x[0]))),
            "negative_count_histogram": dict(sorted(negative_counts.items(), key=lambda x: int(x[0])))}


def prior_exhaustive(dataset: str, alphabet: list[str], max_len: int) -> list[dict]:
    universe = words(alphabet, max_len)
    records = []
    for index, statuses in enumerate(itertools.product((0, 1, 2), repeat=len(universe))):
        positive = [word for word, status in zip(universe, statuses) if status == 1]
        negative = [word for word, status in zip(universe, statuses) if status == 2]
        records.append(record(dataset, f"{dataset}_{index:04d}",
                              input_data(alphabet, positive, negative)))
    return records


def targeted_controls() -> list[dict]:
    cases = [
        ("swap_forward", "abc", ["cab"], ["cba"]),
        ("swap_reverse", "abc", ["cba"], ["cab"]),
        ("rescue_parent_minimal", "abc", ["", "c", "cab"], ["ca"]),
        ("rescue_forward_contextual", "abc", ["cabb", "cb"], ["cab"]),
        ("rescue_reverse_contextual", "abc", ["cb", "cbab"], ["cab"]),
        ("no_feasible_two_block_partition", "abc", ["ab", "ac", "bc"], ["abc"]),
        ("empty_both_classes", "ab", [], []),
        ("empty_positive_class", "ab", [], ["ab"]),
        ("empty_negative_class", "ab", ["ab"], []),
    ]
    return [record("targeted_controls", name,
                   input_data(list(alpha), positive, negative))
            for name, alpha, positive, negative in cases]


def random_ternary_5000() -> tuple[list[dict], dict]:
    alphabet = list("abc")
    universe = words(alphabet, 2)
    rng = random.Random(20261026)
    seen: set[tuple[int, ...]] = set()
    records = []
    per_word = {word: Counter() for word in universe}
    while len(records) < 5000:
        statuses = tuple(rng.randrange(3) for _ in universe)
        if statuses in seen:
            continue
        seen.add(statuses)
        for word, status in zip(universe, statuses):
            per_word[word][("absent", "positive", "negative")[status]] += 1
        positive = [word for word, status in zip(universe, statuses) if status == 1]
        negative = [word for word, status in zip(universe, statuses) if status == 2]
        records.append(record("random_ternary_5000", f"ternary_{len(records):04d}",
                              input_data(alphabet, positive, negative)))
    label_statuses = {word: dict(sorted(counts.items()))
                      for word, counts in per_word.items()}
    return records, {"seed": 20261026, "universe_size": len(universe),
                     "unique_samples": len(records),
                     "per_word_label_status_counts": label_statuses,
                     "sample_strata": label_strata(records)}


def canonical_partition(alphabet: list[str], rng: random.Random) -> list[list[str]]:
    # The first alphabet symbol is fixed on side zero to remove block symmetry.
    mask = rng.randrange(1, 1 << (len(alphabet) - 1))
    left = [alphabet[0]]
    right = []
    for offset, symbol in enumerate(alphabet[1:]):
        (right if (mask >> offset) & 1 else left).append(symbol)
    return [sorted(left), sorted(right)]


def local_words(block: list[str]) -> list[str]:
    return words(block, 2)


def random_nonempty_language(block: list[str], rng: random.Random) -> list[str]:
    universe = local_words(block)
    while True:
        language = [word for word in universe if rng.random() < 0.5]
        if language:
            return language


def projection(word: str, block: list[str]) -> str:
    allowed = set(block)
    return "".join(symbol for symbol in word if symbol in allowed)


def draw_product_case(alphabet: list[str], rng: random.Random,
                      dataset: str, case_id: str) -> tuple[dict, dict, tuple]:
    partition = canonical_partition(alphabet, rng)
    languages = [random_nonempty_language(block, rng) for block in partition]
    accepted = [set(language) for language in languages]
    positives = []
    negatives = []
    for word in words(alphabet, 4):
        if not (any(symbol in partition[0] for symbol in word)
                and any(symbol in partition[1] for symbol in word)):
            continue
        label = (projection(word, partition[0]) in accepted[0]
                 and projection(word, partition[1]) in accepted[1])
        (positives if label else negatives).append(word)
    picked_positive = sorted(rng.sample(positives, min(32, len(positives))))
    picked_negative = sorted(rng.sample(negatives, min(32, len(negatives))))
    data = input_data(alphabet, picked_positive, picked_negative)
    truth = {"case_id": case_id, "true_partition": partition,
             "local_languages": [{"block": block, "language": language}
                                 for block, language in zip(partition, languages)],
             "word_length_bound": 4,
             "positive_pool_size": len(positives),
             "negative_pool_size": len(negatives),
             "selected_positive_count": len(picked_positive),
             "selected_negative_count": len(picked_negative),
             "generator_seed": None}
    # The hidden-model key ensures genuinely distinct finite generators per set.
    model_key = (tuple(tuple(block) for block in partition),
                 tuple(tuple(language) for language in languages))
    return record(dataset, case_id, data), truth, model_key


def build_finite_set(dataset: str, seed: int,
                     sizes_and_counts: list[tuple[int, int]]) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    cases: list[dict] = []
    truths: list[dict] = []
    for alphabet_size, count in sizes_and_counts:
        alphabet = [chr(ord("a") + i) for i in range(alphabet_size)]
        seen_models: set[tuple] = set()
        seen_inputs: set[str] = set()
        accepted = 0
        attempts = 0
        while accepted < count:
            attempts += 1
            if attempts > count * 10000:
                raise RuntimeError(f"unable to produce distinct cases for {dataset}, m={alphabet_size}")
            case_id = f"{dataset}_m{alphabet_size}_{accepted:03d}"
            item, truth, model_key = draw_product_case(alphabet, rng, dataset, case_id)
            input_hash = item["input_sha256"]
            if model_key in seen_models or input_hash in seen_inputs:
                continue
            seen_models.add(model_key)
            seen_inputs.add(input_hash)
            truth["generator_seed"] = seed
            truth["generation_attempt"] = attempts
            cases.append(item)
            truths.append(truth)
            accepted += 1
    return cases, truths


def source_hash(path: Path) -> str:
    return sha(path.read_bytes())


def main() -> int:
    if CORPUS.exists():
        raise FileExistsError(f"refusing to overwrite frozen corpus: {CORPUS}")

    datasets: dict[str, list[dict]] = {}
    datasets["prior_binary_2187"] = prior_exhaustive("prior_binary_2187", list("ab"), 2)
    datasets["prior_abc_81"] = prior_exhaustive("prior_abc_81", list("abc"), 1)
    theory_records = []
    for path in sorted(BASELINE.glob("theory_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        theory_records.append(record("prior_theory_4", path.stem, input_data(
            data["alphabet"], data["positive"], data["negative"])))
    if len(theory_records) != 4:
        raise AssertionError(f"expected four frozen theory examples, got {len(theory_records)}")
    datasets["prior_theory_4"] = theory_records
    datasets["targeted_controls"] = targeted_controls()

    random_records, ternary_info = random_ternary_5000()
    datasets["random_ternary_5000"] = random_records
    finite_records, finite_truth = build_finite_set(
        "finite_generator_140", 20261027,
        [(size, 20) for size in range(4, 11)])
    datasets["finite_generator_140"] = finite_records
    scale_records, scale_truth = build_finite_set(
        "performance_100", 20261028,
        [(size, 25) for size in (4, 6, 8, 10)])
    datasets["performance_100"] = scale_records

    CORPUS.mkdir(parents=True, exist_ok=False)
    input_dir = CORPUS / "solver_inputs"
    truth_dir = CORPUS / "truth_sidecars"
    input_dir.mkdir()
    truth_dir.mkdir()

    manifest: dict[str, object] = {
        "schema_version": 1,
        "corpus_id": "C002-frozen-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "frozen_before_solver_runs": True,
        "solver_input_contract": "Only each record's input object may be passed to a solver.",
        "word_order": "length then lexicographic over sorted alphabet",
        "random_ternary_design": ternary_info,
        "finite_generator_design": {
            "local_word_bound": 2,
            "global_sample_word_bound": 4,
            "touches_both_blocks": True,
            "local_language_sampling": "independent Bernoulli(1/2) per local word, resampled if empty",
            "per_class_sample_cap": 32,
            "generator_truth_in_solver_input": False,
            "finite_generator_seed": 20261027,
            "performance_seed": 20261028,
        },
        "provenance": {
            str(path.relative_to(CYCLE)): source_hash(path)
            for path in [BASELINE / "partition_solver.py",
                         BASELINE / "audit_partition.py",
                         BASELINE / "audit_results.json",
                         BASELINE / "audit_examples.json",
                         *sorted(BASELINE.glob("theory_*.json")),
                         Path(__file__)]
        },
        "datasets": {},
    }
    for name, records in datasets.items():
        path = input_dir / f"{name}.jsonl"
        digest, byte_count = write_jsonl(path, records)
        item = {"path": str(path.relative_to(CORPUS)).replace("\\", "/"),
                "sha256": digest, "bytes": byte_count, "count": len(records),
                "case_input_hashes": [{"case_id": r["case_id"],
                                       "sha256": r["input_sha256"]} for r in records],
                "label_strata": label_strata(records)}
        if name == "random_ternary_5000":
            item["sampling"] = ternary_info
        manifest["datasets"][name] = item

    for name, truths in (("finite_generator_140", finite_truth),
                         ("performance_100", scale_truth)):
        path = truth_dir / f"{name}_truth.jsonl"
        digest, byte_count = write_jsonl(path, truths)
        manifest.setdefault("truth_sidecars", {})[name] = {
            "path": str(path.relative_to(CORPUS)).replace("\\", "/"),
            "sha256": digest, "bytes": byte_count, "count": len(truths),
            "forbidden_to_solver": True,
        }

    manifest_path = CORPUS / "manifest.json"
    manifest_path.write_bytes(canonical_json(manifest) + b"\n")
    summary = {name: {"count": spec["count"], "sha256": spec["sha256"]}
               for name, spec in manifest["datasets"].items()}
    summary["manifest_sha256"] = sha(manifest_path.read_bytes())
    print(json.dumps({"corpus": str(CORPUS), "datasets": summary,
                      "truth_sidecars": manifest["truth_sidecars"]},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

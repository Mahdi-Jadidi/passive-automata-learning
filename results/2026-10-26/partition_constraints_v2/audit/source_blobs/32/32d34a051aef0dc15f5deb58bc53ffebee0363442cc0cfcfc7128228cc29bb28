"""Recreate and freeze the prior 3,072 finite-generator sample-only inputs."""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent
BASELINE = CYCLE / "baseline"
OUT = AUDIT / "corpus" / "legacy_generator_extension_v1"
ALPHABET = "abc"


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def words(alphabet: str, max_len: int) -> list[str]:
    return ["".join(items) for length in range(max_len + 1)
            for items in itertools.product(alphabet, repeat=length)]


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def partitions_k(alphabet: str, k: int):
    result = set()

    def rec(index, blocks):
        if index == len(alphabet):
            if len(blocks) == k:
                result.add(canonical_partition(blocks))
            return
        symbol = alphabet[index]
        for j in range(len(blocks)):
            blocks[j].append(symbol)
            rec(index + 1, blocks)
            blocks[j].pop()
        if len(blocks) < k:
            blocks.append([symbol])
            rec(index + 1, blocks)
            blocks.pop()

    rec(0, [])
    return sorted(result)


def local_words(block):
    return words("".join(sorted(block)), 2)


def project(word, block):
    members = set(block)
    return "".join(symbol for symbol in word if symbol in members)


def accepts(word, partition, languages):
    return all(project(word, block) in languages[index]
               for index, block in enumerate(partition))


def main() -> int:
    if OUT.exists():
        raise FileExistsError(f"refusing to overwrite legacy extension: {OUT}")
    if not (BASELINE / "audit_partition.py").is_file():
        raise FileNotFoundError("frozen prior audit source missing")

    partition_counts = Counter()
    empty_factor_counts = Counter()
    duplicate_inputs = 0
    seen_input_hashes = set()
    input_count = 0
    input_hasher = hashlib.sha256()
    truth_hasher = hashlib.sha256()
    OUT.mkdir(parents=True, exist_ok=False)
    input_path = OUT / "solver_inputs.jsonl"
    truth_path = OUT / "truth_sidecars.jsonl"
    sample_universe = words(ALPHABET, 4)

    with input_path.open("xb") as input_file, truth_path.open("xb") as truth_file:
        for partition_index, partition in enumerate(partitions_k(ALPHABET, 2)):
            candidates_per_block = [local_words(block) for block in partition]
            local_options = [
                [tuple(word for index, word in enumerate(candidates)
                       if (mask >> index) & 1)
                 for mask in range(1 << len(candidates))]
                for candidates in candidates_per_block
            ]
            sample_words = [word for word in sample_universe
                            if all(any(symbol in word for symbol in block)
                                   for block in partition)]
            for option_indices, local_languages in enumerate(itertools.product(*local_options)):
                case_id = f"legacy_generator_{input_count:04d}"
                language_sets = [set(language) for language in local_languages]
                positives = [word for word in sample_words
                             if accepts(word, partition, language_sets)]
                positive_set = set(positives)
                negatives = [word for word in sample_words if word not in positive_set]
                data = {"alphabet": list(ALPHABET), "positive": sorted(positives),
                        "negative": sorted(negatives)}
                input_digest = sha(canonical_json(data))
                if input_digest in seen_input_hashes:
                    duplicate_inputs += 1
                seen_input_hashes.add(input_digest)
                record = {"case_id": case_id,
                          "dataset": "legacy_generator_extension_v1",
                          "input": data, "input_sha256": input_digest}
                input_line = canonical_json(record) + b"\n"
                input_file.write(input_line)
                input_hasher.update(input_line)

                truth = {"case_id": case_id,
                         "true_partition": [list(block) for block in partition],
                         "local_languages": [
                             {"block": list(block), "language": list(language)}
                             for block, language in zip(partition, local_languages)],
                         "positive_pool_size": len(positives),
                         "negative_pool_size": len(negatives),
                         "sample_word_count": len(sample_words),
                         "partition_index": partition_index,
                         "factor_option_indices": list(option_indices) if isinstance(option_indices, tuple) else option_indices}
                # product() has no exposed index; record exact factor masks
                # from the selected finite local languages for reproducibility.
                truth["factor_option_masks"] = [
                    sum(1 << i for i, word in enumerate(candidates) if word in language)
                    for candidates, language in zip(candidates_per_block, local_languages)]
                truth.pop("factor_option_indices", None)
                truth_line = canonical_json(truth) + b"\n"
                truth_file.write(truth_line)
                truth_hasher.update(truth_line)

                partition_key = "|".join("".join(block) for block in partition)
                partition_counts[partition_key] += 1
                for block_index, language in enumerate(local_languages):
                    if not language:
                        empty_factor_counts[str(block_index)] += 1
                input_count += 1

    if input_count != 3072:
        raise AssertionError(f"expected 3072 generator pairs, got {input_count}")
    baseline_path = BASELINE / "audit_partition.py"
    manifest = {
        "schema_version": 1,
        "extension_id": "C002-legacy-generator-extension-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "provenance": {
            "source": "baseline/audit_partition.py::run_generator_exhaustion",
            "source_sha256": sha(baseline_path.read_bytes()),
            "generator_script_sha256": sha(Path(__file__).read_bytes()),
        },
        "generation_protocol": {
            "alphabet": ALPHABET,
            "known_k": 2,
            "generator_pairs": "all k=2 partitions times all subsets of local words of length at most 2",
            "local_words_order": "length then lexicographic",
            "global_input_words": "all words of length at most 4 touching both true blocks",
            "labels": "complete finite-product generator labels on those words only",
            "witness_context_labels": "excluded; never supplied to a solver",
            "deduplicate": False,
        },
        "count": input_count,
        "partition_group_counts": dict(sorted(partition_counts.items())),
        "empty_factor_occurrences_by_block_index": dict(sorted(empty_factor_counts.items())),
        "duplicate_solver_inputs": duplicate_inputs,
        "unique_solver_inputs": len(seen_input_hashes),
        "files": {
            "solver_inputs.jsonl": {"sha256": input_hasher.hexdigest(),
                                     "bytes": input_path.stat().st_size,
                                     "count": input_count,
                                     "truth_not_in_input": True},
            "truth_sidecars.jsonl": {"sha256": truth_hasher.hexdigest(),
                                     "bytes": truth_path.stat().st_size,
                                     "count": input_count,
                                     "forbidden_to_solver": True},
        },
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_bytes(canonical_json(manifest) + b"\n")
    manifest["manifest_sha256"] = sha(manifest_path.read_bytes())
    print(json.dumps({"extension": str(OUT), "count": input_count,
                      "partition_group_counts": manifest["partition_group_counts"],
                      "duplicate_solver_inputs": duplicate_inputs,
                      "unique_solver_inputs": len(seen_input_hashes),
                      "files": manifest["files"],
                      "manifest_sha256": manifest["manifest_sha256"]},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

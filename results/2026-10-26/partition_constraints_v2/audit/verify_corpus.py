"""Independently verify the C002 frozen corpus and hidden-truth separation."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
CORPUS = AUDIT / "corpus" / "frozen_v1"
EXPECTED = {
    "prior_binary_2187": 2187,
    "prior_abc_81": 81,
    "prior_theory_4": 4,
    "targeted_controls": 9,
    "random_ternary_5000": 5000,
    "finite_generator_140": 140,
    "performance_100": 100,
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path: Path) -> tuple[bytes, list[dict]]:
    raw = path.read_bytes()
    records = [json.loads(line) for line in raw.splitlines() if line]
    return raw, records


def project(word: str, block: list[str]) -> str:
    allowed = set(block)
    return "".join(symbol for symbol in word if symbol in allowed)


def verify() -> dict:
    manifest_path = CORPUS / "manifest.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    assert manifest["corpus_id"] == "C002-frozen-v1"
    assert manifest["frozen_before_solver_runs"] is True
    assert manifest["solver_input_contract"].startswith("Only each record's input object")
    assert set(manifest["datasets"]) == set(EXPECTED)

    loaded: dict[str, list[dict]] = {}
    summaries = {}
    for name, expected_count in EXPECTED.items():
        spec = manifest["datasets"][name]
        path = CORPUS / spec["path"]
        raw, records = read_jsonl(path)
        assert sha(raw) == spec["sha256"], (name, "file hash")
        assert len(records) == expected_count == spec["count"], (name, "count")
        assert len({record["case_id"] for record in records}) == expected_count, (name, "case IDs")
        assert [r["case_id"] for r in records] == [x["case_id"] for x in spec["case_input_hashes"]]
        case_hashes = []
        for record in records:
            assert set(record) == {"case_id", "dataset", "input", "input_sha256"}
            data = record["input"]
            assert record["dataset"] == name
            assert set(data) == {"alphabet", "positive", "negative"}, (name, "solver schema")
            assert data["alphabet"] == sorted(set(data["alphabet"]))
            assert 2 <= len(data["alphabet"]) <= 10
            assert all(isinstance(symbol, str) and len(symbol) == 1 for symbol in data["alphabet"])
            assert data["positive"] == sorted(set(data["positive"]))
            assert data["negative"] == sorted(set(data["negative"]))
            assert not (set(data["positive"]) & set(data["negative"]))
            for word in data["positive"] + data["negative"]:
                assert set(word) <= set(data["alphabet"])
            digest = sha(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8"))
            assert digest == record["input_sha256"]
            case_hashes.append(digest)
        assert case_hashes == [x["sha256"] for x in spec["case_input_hashes"]]
        if name in ("random_ternary_5000", "finite_generator_140", "performance_100"):
            assert len(set(case_hashes)) == expected_count, (name, "unique inputs")
        loaded[name] = records
        summaries[name] = {"count": len(records), "sha256": spec["sha256"],
                            "unique_input_hashes": len(set(case_hashes))}

    ternary_info = manifest["random_ternary_design"]
    assert ternary_info["seed"] == 20261026
    assert ternary_info["universe_size"] == 13 and ternary_info["unique_samples"] == 5000
    for word, counts in ternary_info["per_word_label_status_counts"].items():
        assert sum(counts.values()) == 5000, word
        assert set(counts) == {"absent", "positive", "negative"}
    assert sum(ternary_info["sample_strata"]["class_presence"].values()) == 5000

    expected_sizes = {
        "finite_generator_140": {size: 20 for size in range(4, 11)},
        "performance_100": {size: 25 for size in (4, 6, 8, 10)},
    }
    truth_summary = {}
    for name in ("finite_generator_140", "performance_100"):
        truth_spec = manifest["truth_sidecars"][name]
        assert truth_spec["forbidden_to_solver"] is True
        truth_path = CORPUS / truth_spec["path"]
        raw, truths = read_jsonl(truth_path)
        assert sha(raw) == truth_spec["sha256"]
        assert len(truths) == truth_spec["count"] == EXPECTED[name]
        records = loaded[name]
        assert [t["case_id"] for t in truths] == [r["case_id"] for r in records]
        size_counts = Counter()
        seen_models = set()
        for record, truth in zip(records, truths):
            data = record["input"]
            blocks = truth["true_partition"]
            assert len(blocks) == 2 and all(blocks)
            assert blocks[0][0] == data["alphabet"][0]
            assert set(blocks[0]).isdisjoint(blocks[1])
            assert sorted(blocks[0] + blocks[1]) == data["alphabet"]
            size_counts[len(data["alphabet"])] += 1
            local = truth["local_languages"]
            assert len(local) == 2
            language_sets = []
            model = [tuple(tuple(block) for block in blocks)]
            for item, block in zip(local, blocks):
                assert item["block"] == block and item["language"]
                assert item["language"] == sorted(set(item["language"]),
                                                   key=lambda word: (len(word), word))
                for word in item["language"]:
                    assert len(word) <= 2 and set(word) <= set(block)
                language_sets.append(set(item["language"]))
                model.append(tuple(item["language"]))
            model_key = tuple(model)
            assert model_key not in seen_models, (name, "duplicate hidden generator")
            seen_models.add(model_key)
            for word in data["positive"]:
                assert 0 < len(word) <= 4
                assert any(symbol in blocks[0] for symbol in word)
                assert any(symbol in blocks[1] for symbol in word)
                assert project(word, blocks[0]) in language_sets[0]
                assert project(word, blocks[1]) in language_sets[1]
            for word in data["negative"]:
                assert 0 < len(word) <= 4
                assert any(symbol in blocks[0] for symbol in word)
                assert any(symbol in blocks[1] for symbol in word)
                assert not (project(word, blocks[0]) in language_sets[0]
                            and project(word, blocks[1]) in language_sets[1])
            assert len(data["positive"]) == min(32, truth["positive_pool_size"])
            assert len(data["negative"]) == min(32, truth["negative_pool_size"])
            assert len(data["positive"]) + len(data["negative"]) <= 64
            assert truth["generator_seed"] == (20261027 if name == "finite_generator_140" else 20261028)
        assert dict(size_counts) == expected_sizes[name]
        truth_summary[name] = {"count": len(truths), "size_counts": dict(sorted(size_counts.items())),
                               "sha256": truth_spec["sha256"]}

    return {"corpus_id": manifest["corpus_id"],
            "manifest_sha256": sha(manifest_raw),
            "datasets": summaries, "truth_sidecars": truth_summary,
            "checks": ["file and per-input SHA256", "expected counts and unique samples",
                       "input schema and disjoint labels", "separate target truth sidecars",
                       "finite product labels match their generators", "sample caps and word bounds"]}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True))

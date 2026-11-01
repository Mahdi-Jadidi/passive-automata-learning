"""Independent validation of the frozen C006 benchmark inputs and targets."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
BENCH = AUDIT / "benchmark_v1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def project(word, block):
    chosen = set(block)
    return "".join(symbol for symbol in word if symbol in chosen)


def target_accepts(grammar, word):
    kind = grammar.get("kind")
    if kind == "fixed_prefix_center_leaf_pairs_star":
        prefix, center, leaves = grammar["prefix"], grammar["center"], set(grammar["leaves"])
        if not word.startswith(prefix):
            return False
        tail = word[len(prefix):]
        if len(tail) % 2:
            return False
        return all(tail[i] == center and tail[i + 1] in leaves for i in range(0, len(tail), 2))
    if kind == "finite_words_union_unary_tail":
        return word in set(grammar["finite_words"]) or (
            len(word) >= grammar["tail_min_length"] and
            all(symbol == grammar["tail_symbol"] for symbol in word))
    if kind == "unary_star":
        return all(symbol == grammar["symbol"] for symbol in word)
    raise AssertionError(f"unknown grammar: {kind}")


def canonical_cut_rows(data):
    alphabet = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    expected = []
    for tail in range((1 << (len(alphabet) - 1)) - 1):
        mask = (tail << 1) | 1
        blocks = [[a for i, a in enumerate(alphabet) if (mask >> i) & 1],
                  [a for i, a in enumerate(alphabet) if not ((mask >> i) & 1)]]
        collision = None
        for negative in negatives:
            matched = []
            for block in blocks:
                projected = project(negative, block)
                positive = next((p for p in positives if project(p, block) == projected), None)
                if positive is None:
                    break
                matched.append(positive)
            if len(matched) == 2:
                collision = {"negative": negative, "matching_positive_by_side": matched}
                break
        expected.append({"canonical_left_atom_mask": mask, "collision": collision})
    return expected


def main():
    manifest_path = BENCH / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    visible_raw = (BENCH / "inputs.jsonl").read_bytes()
    truth_raw = (BENCH / "truth_sidecars.jsonl").read_bytes()
    expected_raw = (BENCH / "expected_obstructions.jsonl").read_bytes()
    assert sha(visible_raw) == manifest["inputs_sha256"]
    assert sha(truth_raw) == manifest["truth_sidecars_sha256"]
    assert sha(expected_raw) == manifest["expected_obstructions_sha256"]
    visible, truths, expected = (read_jsonl(BENCH / "inputs.jsonl"),
                                 read_jsonl(BENCH / "truth_sidecars.jsonl"),
                                 read_jsonl(BENCH / "expected_obstructions.jsonl"))
    assert len(visible) == len(truths) == len(expected) == 3
    truth_by_id = {row["case_id"]: row for row in truths}
    expected_by_id = {row["case_id"]: row for row in expected}
    assert len(truth_by_id) == len(expected_by_id) == 3

    validated = []
    for row in visible:
        case_id, data = row["case_id"], row["input"]
        truth, obstruction = truth_by_id[case_id], expected_by_id[case_id]
        assert set(data) == {"alphabet", "positive", "negative"}
        assert len(data["alphabet"]) == len(set(data["alphabet"]))
        assert all(isinstance(a, str) and len(a) == 1 for a in data["alphabet"])
        assert not (set(data["positive"]) & set(data["negative"]))
        assert all(set(word) <= set(data["alphabet"])
                   for word in data["positive"] + data["negative"])
        assert truth["factor_count"] == 1 and truth["blocks"] == [data["alphabet"]]
        grammar = truth["grammar"]
        assert all(target_accepts(grammar, word) for word in data["positive"])
        assert all(not target_accepts(grammar, word) for word in data["negative"])
        input_path = BENCH / "inputs" / f"{case_id}.json"
        assert json.loads(input_path.read_text(encoding="utf-8")) == data
        assert sha(input_path.read_bytes()) == next(c["input_sha256"] for c in manifest["cells"]
                                                    if c["case_id"] == case_id)
        if case_id == "large_connected_m64":
            assert len(data["alphabet"]) == 64 and len(grammar["prefix"]) == 128
            center, leaves = grammar["center"], grammar["leaves"]
            base, negative = grammar["prefix"], data["negative"][0]
            assert negative == base + center and base in data["positive"]
            pair_edges = []
            for leaf in leaves:
                rescued = base + center + leaf
                assert rescued in data["positive"]
                assert negative[:-1] == base
                assert negative + leaf == rescued
                pair_edges.append(sorted([center, leaf]))
            assert pair_edges == obstruction["expected_edge_pairs"]
            assert len(pair_edges) == 63 and len(set(tuple(x) for x in pair_edges)) == 63
            assert len({x for edge in pair_edges for x in edge}) == 64
            assert obstruction["obstruction"] == "connected_must_link_graph"
        elif case_id == "small_full_cover_m4":
            assert obstruction["obstruction"] == "complete_cut_collision_cover"
            derived = canonical_cut_rows(data)
            assert derived == obstruction["expected_cut_rejections"]
            assert len(derived) == 7 and all(row["collision"] for row in derived)
            assert obstruction["expected_graph_edge_count"] == 0
        elif case_id == "optional_decomposable_m64":
            assert truth["grammar"] == {"kind": "unary_star", "symbol": data["alphabet"][0],
                                         "infinite": True, "notation": "c*"}
            assert obstruction["expected_status"] == "found"

        validated.append({"case_id": case_id, "alphabet_size": len(data["alphabet"]),
                          "positive_count": len(data["positive"]),
                          "negative_count": len(data["negative"]),
                          "target_membership": "passed",
                          "obstruction_shape": obstruction.get("obstruction"),
                          "expected_edge_count": obstruction.get("expected_edge_count"),
                          "expected_cut_count": len(obstruction.get("expected_cut_rejections", []))})

    report = {
        "scientific_status": "passed_independent_frozen_input_and_truth_validation",
        "execution_status": "success",
        "cases": validated,
        "primary_case_count": 2,
        "optional_case_count": 1,
        "primary_provider_jobs": 6,
        "provider_invocations_performed": 0,
        "large_cell": {
            "infinite_regular_target": "c^128 (cY)*",
            "independent_insertion_rescue_edges": 63,
            "graph_connected": True,
            "positive_words_accept": True,
            "negative_word_rejects": True
        },
        "small_cell": {
            "infinite_regular_target": "{four listed positive words} union a^5a*",
            "canonical_cuts": 7,
            "all_cut_collision_witnesses_independently_derived": True
        },
        "input_sha256": sha(visible_raw),
        "truth_sidecars_sha256": sha(truth_raw),
        "expected_obstructions_sha256": sha(expected_raw),
        "manifest_sha256": sha(manifest_path.read_bytes())
    }
    output = AUDIT / "benchmark_v1" / "freeze_validation.json"
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

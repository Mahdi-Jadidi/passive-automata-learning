"""Independently replay the already-captured 4-symbol obstruction output."""
import argparse
import hashlib
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def project(word, block):
    return "".join(a for a in word if a in set(block))


def enhanced_edges(data):
    pos, neg, alphabet = set(data["positive"]), set(data["negative"]), data["alphabet"]
    edges = set()
    # Existing adjacent-swap rule.
    for p in pos:
        for i in range(len(p) - 1):
            a, b = p[i], p[i + 1]
            if a != b and p[:i] + b + a + p[i + 2:] in neg:
                edges.add(tuple(sorted((a, b))))
    # Existing insertion-rescue rule.
    for n in neg:
        for i, a in enumerate(n):
            base = n[:i] + n[i + 1:]
            if base not in pos:
                continue
            for b in alphabet:
                if a == b:
                    continue
                if any(n[:j] + b + n[j:] in pos for j in (i, i + 1)):
                    edges.add(tuple(sorted((a, b))))
    # Enhanced A: alternatives inserted into the same gap of one negative.
    for n in neg:
        for t in range(len(n) + 1):
            x, y = n[:t], n[t:]
            for i, a in enumerate(alphabet):
                for b in alphabet[i + 1:]:
                    if x + a + y in pos and x + b + y in pos:
                        edges.add((a, b))
    # Enhanced B: positive words each delete one distinct symbol occurrence.
    for n in neg:
        for i, a in enumerate(n):
            pa = n[:i] + n[i + 1:]
            if pa not in pos:
                continue
            for j, b in enumerate(n):
                if a == b:
                    continue
                pb = n[:j] + n[j + 1:]
                if pb in pos:
                    edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--captured-output", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    visible = json.loads(args.input.read_text(encoding="utf-8").splitlines()[0])
    actual = json.loads(args.captured_output.read_text(encoding="utf-8"))
    oracle = {r["case_id"]: r for r in read_jsonl(args.oracle)}[visible["case_id"]]
    data = visible["input"]
    assert oracle["nondecomposable_nontrivial"] is True
    assert not oracle["compatible_by_k"]["2"]
    assert enhanced_edges(data) == []
    cert = actual["certificate"]
    assert actual["status"] == "not_decomposable" and actual["complete"] is True
    assert actual["enumeration_complete"] is True and actual["decision_complete"] is True
    assert cert["kind"] == "no_nontrivial_bipartition"
    assert cert["obstruction"] == "complete_cut_collision_cover"
    assert cert["must_link_edges"] == []
    components = cert["components"]
    assert components == [["a"], ["b"], ["c"], ["d"]]
    expected_masks = list(range(1, (1 << len(components)) - 1, 2))
    expected_masks.remove((1 << len(components)) - 1)
    records = cert["cut_rejections"]
    by_mask = {row["canonical_left_atom_mask"]: row for row in records}
    assert len(records) == len(by_mask) == 7
    assert set(by_mask) == set(expected_masks)
    for mask in expected_masks:
        left = [symbol for i, block in enumerate(components) if mask & (1 << i) for symbol in block]
        right = [symbol for i, block in enumerate(components) if not mask & (1 << i) for symbol in block]
        collision = by_mask[mask]["collision"]
        n = collision["negative"]
        assert n in data["negative"]
        assert collision["projections"] == [project(n, left), project(n, right)]
        matches = collision["matching_positive_by_side"]
        assert len(matches) == 2
        for side, p in enumerate(matches):
            block = (left, right)[side]
            assert p in data["positive"] and project(p, block) == project(n, block)
    report = dict(status="independently_replayed", case_id=visible["case_id"],
                  true_nontrivial_partitions=0, must_link_edges_by_old_plus_enhanced_rules=0,
                  canonical_bipartitions_covered=len(expected_masks),
                  collisions_validated=2 * len(expected_masks),
                  manager_candidate_hypothesis="confirmed: non-decomposable despite disconnected empty sound graph",
                  candidate_output_sha256=hashlib.sha256(args.captured_output.read_bytes()).hexdigest(),
                  oracle_sha256=hashlib.sha256(args.oracle.read_bytes()).hexdigest())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

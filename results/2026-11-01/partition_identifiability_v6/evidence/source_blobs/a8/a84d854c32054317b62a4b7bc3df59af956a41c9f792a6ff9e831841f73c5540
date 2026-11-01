"""RGS all-k oracle; no imports from C005/C006 solver code."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def rgs_labels(n):
    if n < 1:
        return
    labels = [0] * n

    def visit(pos, current_max):
        if pos == n:
            yield tuple(labels)
            return
        for label in range(current_max + 2):
            labels[pos] = label
            yield from visit(pos + 1, max(current_max, label))

    yield from visit(1, 0)


def blocks_from_labels(symbols, labels):
    count = max(labels) + 1
    return [tuple(symbols[i] for i, label in enumerate(labels) if label == side)
            for side in range(count)]


def partitions(symbols):
    for labels in rgs_labels(len(symbols)):
        yield blocks_from_labels(symbols, labels)


def project(word, block):
    block = set(block)
    return "".join(a for a in word if a in block)


def partition_test(data, blocks):
    positive = data["positive"]
    local_positive = [{project(word, block) for word in positive} for block in blocks]
    witnesses = []
    for negative in data["negative"]:
        for side, block in enumerate(blocks):
            projection = project(negative, block)
            if projection not in local_positive[side]:
                witnesses.append(dict(negative=negative, block_index=side,
                                      projection=projection))
                break
        else:
            collisions = []
            for side, block in enumerate(blocks):
                projection = project(negative, block)
                positives = [p for p in positive if project(p, block) == projection]
                collisions.append(dict(block_index=side, projection=projection,
                                       matching_positive_words=positives))
            return dict(compatible=False,
                        conflict=dict(negative=negative,
                                      positive_projection_collisions=collisions))
    return dict(compatible=True, witnesses=witnesses)


def grammar_accepts(grammar, word):
    kind = grammar["kind"]
    if kind == "equal_pair_token_star":
        return len(word) % 2 == 0 and all(word[i] == word[i + 1]
                                          and word[i] + word[i + 1] in grammar["tokens"]
                                          for i in range(0, len(word), 2))
    if kind == "finite_words_plus_unary_tail":
        return (word in grammar["finite_words"] or
                (len(word) >= grammar["tail_min_length"] and
                 bool(word) and all(a == grammar["tail_symbol"] for a in word)))
    raise ValueError(f"unknown grammar: {kind}")


def validate_truth(visible, truth):
    data = visible["input"]
    assert visible["case_id"] == truth["case_id"]
    alphabet = data["alphabet"]
    assert len(alphabet) == len(set(alphabet))
    sigma = set(alphabet)
    assert all(set(w) <= sigma for w in data["positive"] + data["negative"])
    assert not (set(data["positive"]) & set(data["negative"]))
    blocks = truth["blocks"]
    assert blocks and set().union(*(set(b) for b in blocks)) == sigma
    assert sum(len(b) for b in blocks) == len(sigma)
    assert len(truth["grammars"]) == len(blocks)
    for label, words in ((True, data["positive"]), (False, data["negative"])):
        for word in words:
            accepted = all(grammar_accepts(grammar, project(word, block))
                           for block, grammar in zip(blocks, truth["grammars"]))
            assert accepted == label, (visible["case_id"], word, label)


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def coarsenings(blocks):
    for labels in rgs_labels(len(blocks)):
        groups = [[] for _ in range(max(labels) + 1)]
        for i, label in enumerate(labels):
            groups[label].extend(blocks[i])
        yield [tuple(sorted(group)) for group in groups]


def audit_case(visible, truth):
    validate_truth(visible, truth)
    data = visible["input"]
    symbols = sorted(data["alphabet"])
    compatible = {k: [] for k in range(1, len(symbols) + 1)}
    bipartitions = []
    all_partition_count = 0
    for blocks in partitions(symbols):
        all_partition_count += 1
        tested = partition_test(data, blocks)
        k = len(blocks)
        canonical_blocks = canonical_partition(blocks)
        if tested["compatible"]:
            compatible[k].append(dict(blocks=[list(b) for b in canonical_blocks],
                                      witnesses=tested["witnesses"]))
        if k == 2:
            bipartitions.append(dict(blocks=[list(b) for b in canonical_blocks], **tested))
    for k in compatible:
        compatible[k].sort(key=lambda item: canonical_partition(item["blocks"]))
    feasible_nontrivial = [k for k in compatible if k >= 2 and compatible[k]]
    kmax = max(feasible_nontrivial, default=1)
    assert feasible_nontrivial == list(range(2, kmax + 1))
    has_bipartition = bool(compatible[2]) if len(symbols) >= 2 else False
    assert bool(feasible_nontrivial) == has_bipartition
    feasible_sets = {k: {canonical_partition(item["blocks"]) for item in values}
                     for k, values in compatible.items()}
    coarsening_checks = 0
    for k, values in compatible.items():
        for item in values:
            old = item["blocks"]
            for coarse in coarsenings(old):
                coarsening_checks += 1
                assert canonical_partition(coarse) in feasible_sets[len(coarse)]
    nondecomp = not has_bipartition and len(symbols) >= 2
    if nondecomp:
        assert bipartitions and all(not row["compatible"] for row in bipartitions)
    return dict(case_id=visible["case_id"], alphabet_size=len(symbols),
                consistent=True, all_k_partition_count=all_partition_count,
                compatible_by_k={str(k): values for k, values in compatible.items()},
                feasible_nontrivial_k=feasible_nontrivial, kmax=kmax,
                bipartitions=bipartitions,
                nondecomposable_nontrivial=nondecomp,
                nondecomposition_certificate=bipartitions if nondecomp else None,
                coarsening_checks=coarsening_checks)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--truths", type=Path, required=True)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--control-truths", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    visible = read_jsonl(args.inputs) + read_jsonl(args.controls)
    hidden_rows = read_jsonl(args.truths) + read_jsonl(args.control_truths)
    hidden = {row["case_id"]: row for row in hidden_rows}
    assert len(hidden) == len(hidden_rows) == len(visible)
    assert len({row["case_id"] for row in visible}) == len(visible)
    results = [audit_case(row, hidden[row["case_id"]]) for row in visible]
    raw = b"".join(canonical(row) for row in results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    sizes = {}
    for result in results:
        sizes[result["alphabet_size"]] = sizes.get(result["alphabet_size"], 0) + 1
    summary = dict(cases=len(results), sizes=sizes,
                   nondecomposable_count=sum(r["nondecomposable_nontrivial"] for r in results),
                   ambiguous_count=sum(sum(len(v) > 1 for k, v in r["compatible_by_k"].items()
                                             if int(k) >= 2) for r in results),
                   coarsening_checks=sum(r["coarsening_checks"] for r in results),
                   expected_sha256=hashlib.sha256(raw).hexdigest(),
                   input_sha256=hashlib.sha256(args.inputs.read_bytes()).hexdigest(),
                   truth_sha256=hashlib.sha256(args.truths.read_bytes()).hexdigest(),
                   controls_sha256=hashlib.sha256(args.controls.read_bytes()).hexdigest(),
                   control_truths_sha256=hashlib.sha256(args.control_truths.read_bytes()).hexdigest(),
                   oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   scientific_status="independent_exact_projection_oracle_completed")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

"""Second, independent set-partition oracle/checker and graph-gap audit."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def canonical(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def generated_set_partitions(symbols):
    """Enumerate partitions by recursive block insertion, independent of RGS code."""
    if not symbols:
        yield []
        return
    first, rest = symbols[0], symbols[1:]
    for partition in generated_set_partitions(rest):
        yield [(first,), *partition]
        for i in range(len(partition)):
            expanded = [tuple(block) for block in partition]
            expanded[i] = (first,) + expanded[i]
            yield expanded


def project(word, block):
    block = set(block)
    return "".join(a for a in word if a in block)


def exact_test(data, blocks):
    local = [{project(p, b) for p in data["positive"]} for b in blocks]
    witnesses = []
    for n in data["negative"]:
        rejecting = [i for i, b in enumerate(blocks) if project(n, b) not in local[i]]
        if rejecting:
            witnesses.append((n, rejecting[0], project(n, blocks[rejecting[0]])))
        else:
            return False, None
    return True, witnesses


def derive_swap_rescue_graph(data):
    """Reimplement precisely adjacent-swap and insertion-rescue witness rules."""
    pos, neg = set(data["positive"]), set(data["negative"])
    edges = set()
    for p in pos:
        for i in range(len(p) - 1):
            a, b = p[i], p[i + 1]
            swapped = p[:i] + b + a + p[i + 2:]
            if a != b and swapped in neg:
                edges.add(tuple(sorted((a, b))))
    for n in neg:
        for i, a in enumerate(n):
            base = n[:i] + n[i + 1:]
            if base not in pos:
                continue
            for b in data["alphabet"]:
                if b == a:
                    continue
                for j in (i, i + 1):
                    rescued = n[:j] + b + n[j:]
                    if rescued in pos:
                        edges.add(tuple(sorted((a, b))))
    components, unseen = [], set(data["alphabet"])
    adjacency = {a: set() for a in data["alphabet"]}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    while unseen:
        todo = [min(unseen)]
        comp = set()
        while todo:
            a = todo.pop()
            if a in comp:
                continue
            comp.add(a)
            todo.extend(adjacency[a] - comp)
        components.append(tuple(sorted(comp)))
        unseen -= comp
    return sorted(edges), sorted(components)


def verify_case(visible, oracle):
    data = visible["input"]
    assert visible["case_id"] == oracle["case_id"]
    symbols = sorted(data["alphabet"])
    partitions = list(generated_set_partitions(symbols))
    assert len(partitions) == oracle["all_k_partition_count"]
    expected_by_k = {}
    bipartition_rows = {}
    for blocks in partitions:
        compatible, _ = exact_test(data, blocks)
        if compatible:
            expected_by_k.setdefault(len(blocks), set()).add(canonical(blocks))
        if len(blocks) == 2:
            bipartition_rows[canonical(blocks)] = compatible
    stored_by_k = {int(k): {canonical(row["blocks"]) for row in rows}
                   for k, rows in oracle["compatible_by_k"].items()}
    for k in range(1, len(symbols) + 1):
        assert stored_by_k.get(k, set()) == expected_by_k.get(k, set()), (visible["case_id"], k)
    listed_bis = {canonical(row["blocks"]): row for row in oracle["bipartitions"]}
    assert set(listed_bis) == set(bipartition_rows)
    for blocks, compatible in bipartition_rows.items():
        row = listed_bis[blocks]
        assert row["compatible"] is compatible
        if compatible:
            assert len(row["witnesses"]) == len(data["negative"])
            for w in row["witnesses"]:
                assert w["projection"] == project(w["negative"], blocks[w["block_index"]])
                assert w["projection"] not in {project(p, blocks[w["block_index"]])
                                                for p in data["positive"]}
        else:
            conflict = row["conflict"]
            n = conflict["negative"]
            assert n in data["negative"]
            collisions = conflict["positive_projection_collisions"]
            assert len(collisions) == 2
            for side, col in enumerate(collisions):
                proj = project(n, blocks[side])
                assert col["projection"] == proj
                assert col["matching_positive_words"]
                for p in col["matching_positive_words"]:
                    assert p in data["positive"] and project(p, blocks[side]) == proj
    expected_nontrivial = bool(expected_by_k.get(2))
    assert oracle["nondecomposable_nontrivial"] is (not expected_nontrivial and len(symbols) >= 2)
    edges, components = derive_swap_rescue_graph(data)
    if oracle["nondecomposable_nontrivial"]:
        assert all(not value for value in bipartition_rows.values())
        assert len(oracle["nondecomposition_certificate"]) == (2 ** (len(symbols) - 1) - 1)
    return dict(case_id=visible["case_id"], m=len(symbols),
                compatible_partition_counts={str(k): len(v) for k, v in expected_by_k.items()},
                nondecomposable_nontrivial=oracle["nondecomposable_nontrivial"],
                must_link_edges=[list(e) for e in edges],
                must_link_components=[list(c) for c in components],
                must_link_connected=(len(components) == 1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--controls", type=Path, required=True)
    p.add_argument("--extra-inputs", type=Path, required=True)
    p.add_argument("--theory-inputs", type=Path, required=True)
    p.add_argument("--oracle", type=Path, required=True)
    p.add_argument("--invalid", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    visible = read(args.inputs) + read(args.controls) + read(args.extra_inputs) + read(args.theory_inputs)
    oracles = read(args.oracle)
    assert len(visible) == len(oracles) == 135
    assert len({r["case_id"] for r in visible}) == 135
    by_id = {r["case_id"]: r for r in oracles}
    reports = [verify_case(row, by_id[row["case_id"]]) for row in visible]
    invalid = read(args.invalid)
    assert len(invalid) == 1 and invalid[0]["case_id"] == "contradictory_label_control"
    data = invalid[0]["input"]
    assert set(data["positive"]) & set(data["negative"])
    gaps = [r["case_id"] for r in reports
            if r["nondecomposable_nontrivial"] and not r["must_link_connected"]]
    named = {"mustlink_not_necessary_nondecomposable",
             "manager_candidate_four_symbol_cycles",
             "theory_examples_v1_original_graph_gap",
             "theory_examples_v1_reduced_graph_gap",
             "manager_examples_v1_manager_graph_gap"}
    assert named <= set(gaps), (named, gaps)
    assert "theory_examples_v1_infinite_irreducible_target_sample" not in gaps
    result = dict(status="accepted_independent_replay", cases=len(reports),
                  all_k_partition_sets_rechecked=135,
                  bipartition_coverage_and_collision_certificates_rechecked=sum(
                      r["m"] >= 2 for r in reports),
                  nondecomposable_count=sum(r["nondecomposable_nontrivial"] for r in reports),
                  nondecomposable_with_disconnected_swap_rescue_graph=gaps,
                  contradictory_label_control_rejected_outside_oracle=True,
                  oracle_sha256=hashlib.sha256(args.oracle.read_bytes()).hexdigest(),
                  source_hashes={name: hashlib.sha256(Path(value).read_bytes()).hexdigest()
                                 for name, value in vars(args).items()
                                 if name in ("inputs", "controls", "extra_inputs", "theory_inputs", "invalid")})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

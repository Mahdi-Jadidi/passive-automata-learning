"""Independent replay of sparse scaling cells and proof-boundary controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V5 = HERE.parent
STRUCTURAL = V5 / "structural"
FIXTURE = STRUCTURAL / "sparse_scaling_fixtures_v1.json"
COUNTEREXAMPLE = STRUCTURAL / "minimization_result_v1.json"
PROVIDER = STRUCTURAL / "sparse_certificate_v2.py"
EXPECTED_PROVIDER_SHA256 = "1ff16263322f2009d68cd2b4ecc3b6587fa9ef80695fa9489fb199c9e13d6705"
EXPECTED_FIXTURE_SHA256 = "d6b8398e9a8c85d8f3c2f65cb87a9518ea7ffefade56a9e42c0d46ae6e8c084c"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load provider {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def project(word: str, block) -> str:
    members = set(block)
    return "".join(symbol for symbol in word if symbol in members)


def opposition_edges(data, q: int):
    alphabet = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    edges = set()
    pair_values = {}
    for i, a in enumerate(alphabet):
        for b in alphabet[i + 1:]:
            pair = (a, b)
            values = {project(word, pair) for word in positives}
            pair_values[pair] = values
            if len(values) > q:
                edges.add(pair)
    return edges, pair_values


def build_scale_case(m: int, k: int, event_repeat: int, q: int):
    alphabet = [chr(0x400 + i) for i in range(m)]
    anchors = alphabet[-(k - 3):] if k > 3 else []
    pool = alphabet[:m - len(anchors)]
    groups = {}
    at = 0
    for i, name in enumerate("abcde"):
        size = len(pool) // 5 + (i < len(pool) % 5)
        groups[name] = pool[at:at + size]
        at += size
    bases = [
        "".join(anchors) + "".join("".join(groups[x]) for x in "acbde"),
        "".join("".join(groups[x]) for x in "ebadc") + "".join(reversed(anchors)),
    ]
    data = {
        "alphabet": alphabet,
        "positive": ["".join(symbol * (event_repeat * r) for symbol in word)
                     for word in bases for r in range(1, q + 1)],
        "negative": [""],
        "k": k,
    }
    blocks = sorted([
        sorted(groups["a"] + groups["c"]),
        sorted(groups["b"] + groups["d"]),
        sorted(groups["e"]),
        *[[symbol] for symbol in anchors],
    ])
    return data, groups, anchors, blocks


def replay_certificate(graph, certificate, expected_edges, expected_blocks, k):
    errors = []
    vertices = sorted(graph.get("symbols", []))
    if not isinstance(certificate, dict) or not certificate.get("unique_q_opposition_coloring"):
        return ["missing_unique_coloring_claim"]
    anchor = certificate.get("anchor")
    if not isinstance(anchor, list) or len(anchor) != k or len(set(anchor)) != k:
        return ["bad_anchor"]
    colors = {symbol: color for color, symbol in enumerate(anchor)}
    for i, a in enumerate(anchor):
        for b in anchor[i + 1:]:
            if tuple(sorted((a, b))) not in expected_edges:
                errors.append("anchor_not_a_clique")
    for step in certificate.get("steps", []):
        vertex = step.get("vertex")
        color = step.get("color")
        witnesses = step.get("neighbor_by_excluded_color", {})
        if vertex in colors or not isinstance(color, int) or isinstance(color, bool) or color not in range(k):
            errors.append("invalid_forced_step")
            continue
        expected_colors = {str(c) for c in range(k) if c != color}
        if set(witnesses) != expected_colors:
            errors.append("incomplete_excluded_color_witnesses")
            continue
        for color_key, neighbor in witnesses.items():
            edge = tuple(sorted((vertex, neighbor)))
            if edge not in expected_edges or colors.get(neighbor) != int(color_key):
                errors.append("invalid_excluded_color_witness")
        colors[vertex] = color
    if set(colors) != set(vertices):
        errors.append("certificate_did_not_force_all_vertices")
        return errors
    if any(colors[a] == colors[b] for a, b in expected_edges):
        errors.append("certificate_coloring_not_proper")
    replayed = canonical_partition([[v for v in vertices if colors[v] == c] for c in range(k)])
    if replayed != canonical_partition(expected_blocks):
        errors.append("replayed_partition_mismatch")
    if canonical_partition(certificate.get("blocks", [])) != replayed:
        errors.append("certificate_block_record_mismatch")
    return errors


def check_result(data, q, expected_blocks, expected_edges, result):
    errors = []
    if result.get("status") != "found" or result.get("uniqueness") != "unique":
        errors.append("provider_did_not_return_unique_found")
    if (not result.get("search_exhausted") or not result.get("decision_complete")
            or not result.get("complete")):
        errors.append("completion_fields_inconsistent")
    actual_blocks = result.get("solutions", [{}])[0].get("blocks", [])
    if canonical_partition(actual_blocks) != canonical_partition(expected_blocks):
        errors.append("partition_mismatch")
    graph = result.get("graph", {})
    actual_edges = {tuple(sorted(edge)) for edge in graph.get("edges", [])}
    if actual_edges != expected_edges or len(graph.get("edges", [])) != len(actual_edges):
        errors.append("opposition_edge_set_mismatch")
    if not graph.get("construction_complete"):
        errors.append("graph_construction_not_complete")
    if len(result.get("solutions", [])) != 1:
        errors.append("solution_count_not_one")
        return errors
    solution = result["solutions"][0]
    positives = sorted(set(data["positive"]))
    languages = [{project(word, block) for word in positives} for block in actual_blocks]
    if solution.get("positive_projection_languages") != [sorted(language) for language in languages]:
        errors.append("full_block_projection_languages_mismatch")
    if any(len(language) > q for language in languages):
        errors.append("full_block_cap_violation")
    negative = sorted(set(data["negative"]))
    witnesses = {w.get("negative"): w for w in solution.get("negative_witnesses", [])}
    if set(witnesses) != set(negative):
        errors.append("negative_witness_coverage_mismatch")
    for word in negative:
        images = [project(word, block) for block in actual_blocks]
        unseen = [i for i, image in enumerate(images) if image not in languages[i]]
        witness = witnesses.get(word)
        if not unseen:
            errors.append("negative_accepted")
        elif (witness is None or witness.get("block_index") != unseen[0]
              or witness.get("projection") != images[unseen[0]]
              or sorted(witness.get("all_unseen_block_indices", [])) != unseen):
            errors.append("negative_witness_invalid")
    witness_rows = graph.get("edge_witnesses", [])
    witness_map = {tuple(sorted(row.get("symbols", []))): row for row in witness_rows}
    if set(witness_map) != expected_edges or len(witness_rows) != len(witness_map):
        errors.append("edge_witness_coverage_mismatch")
    for edge in expected_edges:
        row = witness_map.get(edge)
        if row is None:
            continue
        indices = row.get("positive_indices", [])
        values = row.get("pair_projections", [])
        if len(indices) != len(values) or len(set(values)) <= q:
            errors.append("edge_witness_threshold_failure")
            continue
        for index, value in zip(indices, values):
            if (not isinstance(index, int) or index < 0 or index >= len(positives)
                    or project(positives[index], edge) != value):
                errors.append("edge_witness_projection_mismatch")
    errors.extend(replay_certificate(graph, result.get("certificate"), expected_edges,
                                     expected_blocks, data["k"]))
    return errors


def audit_scale_cells(sparse):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if len(fixture.get("cases", [])) != 8:
        raise AssertionError("expected exactly eight frozen scaling cells")
    records = []
    errors = []
    for row in fixture["cases"]:
        m, k, event_repeat = row["cell"]["m"], row["cell"]["k"], row["cell"]["event_repeat"]
        data, groups, anchors, expected_blocks = build_scale_case(m, k, event_repeat, row["q"])
        if data != row["data"]:
            errors.append({"id": row["id"], "check": "frozen_input_does_not_match_independent_recipe"})
        if canonical_partition(row["expected_blocks"]) != canonical_partition(expected_blocks):
            errors.append({"id": row["id"], "check": "frozen_target_does_not_match_independent_recipe"})
        q = row["q"]
        edges, pair_values = opposition_edges(data, q)
        block_sets = [set(block) for block in expected_blocks]
        complete = {tuple(sorted((a, b))) for i, left in enumerate(block_sets)
                    for right in block_sets[i + 1:] for a in left for b in right}
        missing = complete - edges
        expected_missing = {tuple(sorted((a, d))) for a in groups["a"] for d in groups["d"]}
        if missing != expected_missing:
            errors.append({"id": row["id"], "check": "missing_edges_not_exactly_A_times_D"})
        if edges - complete:
            errors.append({"id": row["id"], "check": "within_target_block_opposition_edge"})
        if len(edges) != row["expected_edges"]:
            errors.append({"id": row["id"], "check": "opposition_edge_count_mismatch"})
        if len(complete) - len(expected_missing) != row["expected_edges"]:
            errors.append({"id": row["id"], "check": "complete_graph_density_formula_mismatch"})
        if max(map(len, data["positive"])) != m * event_repeat * q:
            errors.append({"id": row["id"], "check": "length_ceiling_mismatch"})
        for block in expected_blocks:
            if len({project(word, block) for word in data["positive"]}) != q:
                errors.append({"id": row["id"], "check": "target_block_does_not_have_exactly_q_words"})
        result = sparse.solve(data, k=k, local_word_cap=q, deadline=None, max_solutions=1)
        cell_errors = check_result(data, q, expected_blocks, edges, result)
        errors.extend({"id": row["id"], "check": check} for check in cell_errors)
        records.append({
            "id": row["id"], "m": m, "k": k, "event_repeat": event_repeat, "q": q,
            "positive_count": len(data["positive"]),
            "maximum_positive_length": max(map(len, data["positive"])),
            "edge_count": len(edges), "complete_multipartite_edge_count": len(complete),
            "missing_rectangle_edges": len(expected_missing),
            "expected_block_sizes": sorted(map(len, expected_blocks)),
            "status": result.get("status"), "certificate_steps": len(result.get("certificate", {}).get("steps", [])),
            "errors": cell_errors,
        })
    return records, errors


def audit_q_plus_one(sparse):
    symbol_blocks = [list("abc"), list("de"), list("f")]
    block_strings = ["".join(block) for block in symbol_blocks]
    positives_by_q = {}
    records, errors = [], []
    for q in (1, 2, 3, 4):
        positives = ["".join(part * 2 for part in block_strings),
                     "".join(part * 2 for part in reversed(block_strings))]
        positives.extend("".join(part * r for part in block_strings) for r in range(3, q + 2))
        data = {"alphabet": list("abcdef"), "k": 3, "positive": positives, "negative": []}
        positives_by_q[q] = data
        edge_set, pair_values = opposition_edges(data, q)
        target = canonical_partition(symbol_blocks)
        complete = {tuple(sorted((a, b))) for i, left in enumerate(symbol_blocks)
                    for right in symbol_blocks[i + 1:] for a in left for b in right}
        if len(positives) != q + 1:
            errors.append({"q": q, "check": "positive_count_not_q_plus_one"})
        if edge_set != complete:
            errors.append({"q": q, "check": "opposition_not_exactly_complete_multipartite"})
        if any(len({project(word, block) for word in positives}) != q for block in symbol_blocks):
            errors.append({"q": q, "check": "local_projection_count_not_q"})
        if any(len(pair_values[edge]) != q + 1 for edge in complete):
            errors.append({"q": q, "check": "cross_pair_projection_count_not_q_plus_one"})
        result = sparse.solve(data, k=3, local_word_cap=q, deadline=None, max_solutions=1)
        cell_errors = check_result(data, q, [list(block) for block in target], edge_set, result)
        errors.extend({"q": q, "check": check} for check in cell_errors)
        records.append({"q": q, "positive_count": len(positives),
                        "local_words_per_block": q, "cross_pair_projections": q + 1,
                        "edge_count": len(edge_set), "status": result.get("status"),
                        "errors": cell_errors})
    return records, errors


def audit_unequal_counterexample(sparse):
    source = json.loads(COUNTEREXAMPLE.read_text(encoding="utf-8"))
    case = source["minimized_unequal_failures"][0]
    data = case["input"]
    q = 2
    pair = ("b", "f")
    positives = sorted(set(data["positive"]))
    values = {project(word, pair) for word in positives}
    edges, _ = opposition_edges(data, q)
    expected_blocks = [["a", "b"], ["c", "d", "e", "f"]]
    errors = []
    if values != {"bbff", "ffbb"}:
        errors.append("b_f_projection_set_mismatch")
    if pair in edges:
        errors.append("expected_complete_multipartite_edge_was_present")
    if len(edges) != 7 or len(expected_blocks[0]) * len(expected_blocks[1]) != 8:
        errors.append("one_edge_shortfall_mismatch")
    for block in expected_blocks:
        if len({project(word, block) for word in positives}) > q:
            errors.append("counterexample_target_violates_full_block_cap")
    result = sparse.solve(data, k=2, local_word_cap=q, deadline=None, max_solutions=1)
    errors.extend(check_result(data, q, expected_blocks, edges, result))
    return {
        "q": q, "block_sizes": [2, 4], "positive_count": len(positives),
        "b_f_projections": sorted(values), "observed_edge_count": len(edges),
        "complete_bipartite_edge_count": 8, "status": result.get("status"),
        "errors": errors,
    }, errors


def main():
    if digest(PROVIDER) != EXPECTED_PROVIDER_SHA256:
        raise AssertionError("sparse provider hash differs from frozen readiness hash")
    if digest(FIXTURE) != EXPECTED_FIXTURE_SHA256:
        raise AssertionError("scaling fixture hash differs from preserved source hash")
    sparse = load_module("audit_scaling_sparse_v2", PROVIDER)
    scale_rows, scale_errors = audit_scale_cells(sparse)
    qplus_rows, qplus_errors = audit_q_plus_one(sparse)
    counterexample, counterexample_errors = audit_unequal_counterexample(sparse)
    errors = scale_errors + qplus_errors + counterexample_errors
    output = {
        "schema": "C005-independent-sparse-scaling-audit-v1",
        "provider_sha256": digest(PROVIDER),
        "fixture_sha256": digest(FIXTURE),
        "counts": {"scaling_cells": len(scale_rows), "q_plus_one_cases": len(qplus_rows),
                   "unequal_counterexample_cases": 1, "errors": len(errors)},
        "scaling_cells": scale_rows,
        "q_plus_one_construction": qplus_rows,
        "unequal_counterexample": counterexample,
        "errors": errors,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

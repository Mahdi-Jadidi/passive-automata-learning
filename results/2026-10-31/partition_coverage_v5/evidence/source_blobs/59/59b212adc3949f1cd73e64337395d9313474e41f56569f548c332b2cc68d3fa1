"""Independent full-set oracle gate for C005, using no provider internals."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "frozen_corpus_v2"
MANIFEST = ROOT / "manifest_v1.json"
FREEZE = ROOT / "freeze_record_v1.json"
EXACT_PATH = HERE.parent / "general" / "known_k_qexact_v2.py"
SPARSE_PATH = HERE.parent / "structural" / "sparse_certificate_v2.py"
GRAPH_UNITS = HERE / "graph_unit_controls_v1.json"
TRACE_FIXTURE = HERE.parent / "structural" / "sparse_trace_fixtures_v1.json"
EXPECTED_EXACT_SHA256 = "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d"
EXPECTED_SPARSE_SHA256 = "1ff16263322f2009d68cd2b4ecc3b6587fa9ef80695fa9489fb199c9e13d6705"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def project(word: str, block) -> str:
    symbols = set(block)
    return "".join(symbol for symbol in word if symbol in symbols)


def restricted_growth_partitions(alphabet, k):
    """Enumerate each unordered exactly-k nonempty partition once."""
    symbols = sorted(alphabet)
    owners = [0] * len(symbols)

    def visit(pos: int, maximum: int):
        if pos == len(symbols):
            if maximum + 1 == k:
                yield canonical_partition([
                    [symbol for symbol, owner in zip(symbols, owners) if owner == color]
                    for color in range(k)
                ])
            return
        for color in range(min(maximum + 1, k - 1) + 1):
            owners[pos] = color
            yield from visit(pos + 1, max(maximum, color))

    if symbols:
        yield from visit(1, 0)


def oracle(data, cap):
    alphabet = sorted(data["alphabet"])
    positive = sorted(set(data["positive"]))
    negative = sorted(set(data["negative"]))
    feasible = set()
    for blocks in restricted_growth_partitions(alphabet, data["k"]):
        languages = [{project(word, block) for word in positive} for block in blocks]
        if cap is not None and any(len(language) > cap for language in languages):
            continue
        if any(all(project(word, block) in languages[i]
                   for i, block in enumerate(blocks)) for word in negative):
            continue
        feasible.add(blocks)
    return feasible


def partition_set(result):
    return {canonical_partition(solution["blocks"]) for solution in result.get("solutions", [])}


def verify_partition_and_witnesses(data, solution, cap):
    errors = []
    alphabet = set(data["alphabet"])
    blocks = solution.get("blocks")
    if not isinstance(blocks, list) or any(not isinstance(block, list) for block in blocks):
        return ["malformed_blocks"]
    normalized = [set(block) for block in blocks]
    if len(normalized) != data["k"] or any(not block for block in normalized):
        errors.append("wrong_block_count_or_empty_block")
    if set().union(*normalized) != alphabet or sum(map(len, normalized)) != len(alphabet):
        errors.append("blocks_do_not_partition_alphabet")
    positive = sorted(set(data["positive"]))
    negative = sorted(set(data["negative"]))
    languages = [{project(word, block) for word in positive} for block in normalized]
    reported = solution.get("positive_projection_languages")
    if reported != [sorted(lang) for lang in languages]:
        errors.append("positive_projection_language_mismatch")
    if cap is not None and any(len(lang) > cap for lang in languages):
        errors.append("full_block_cap_violation")
    witness_map = {}
    for witness in solution.get("negative_witnesses", []):
        word = witness.get("negative")
        if word in witness_map:
            errors.append("duplicate_negative_witness")
        witness_map[word] = witness
    if set(witness_map) != set(negative):
        errors.append("negative_witness_coverage_mismatch")
    for word in negative:
        images = [project(word, block) for block in normalized]
        unseen = [i for i, image in enumerate(images) if image not in languages[i]]
        if not unseen:
            errors.append("negative_is_accepted")
            continue
        witness = witness_map.get(word)
        if witness is None:
            errors.append("missing_negative_witness")
        elif (witness.get("block_index") != unseen[0]
              or witness.get("projection") != images[unseen[0]]
              or sorted(witness.get("all_unseen_block_indices", [])) != unseen):
            errors.append("negative_witness_mismatch")
    return errors


def opposition_edges(data, q):
    positive = sorted(set(data["positive"]))
    alphabet = sorted(data["alphabet"])
    expected = set()
    for i, a in enumerate(alphabet):
        for b in alphabet[i + 1:]:
            values = {project(word, (a, b)) for word in positive}
            if len(values) > q:
                expected.add((a, b))
    return expected


def graph_partition_oracle(vertices, edges, k):
    edge_set = {tuple(sorted(edge)) for edge in edges}
    return {partition for partition in restricted_growth_partitions(vertices, k)
            if all(not (a in block and b in block)
                   for block in partition for a, b in edge_set)}


def verify_graph_certificate(graph, cert, expected_edges, k):
    errors = []
    if not isinstance(cert, dict) or not cert.get("unique_q_opposition_coloring"):
        return ["missing_unique_coloring_claim"]
    vertices = sorted(graph.get("symbols", []))
    anchor = cert.get("anchor")
    if not isinstance(anchor, list) or len(anchor) != k or len(set(anchor)) != k:
        errors.append("bad_anchor")
        return errors
    if any(tuple(sorted((a, b))) not in expected_edges
           for i, a in enumerate(anchor) for b in anchor[i + 1:]):
        errors.append("anchor_not_clique")
    color = {symbol: i for i, symbol in enumerate(anchor)}
    for step in cert.get("steps", []):
        symbol = step.get("vertex")
        side = step.get("color")
        neighbor_map = step.get("neighbor_by_excluded_color", {})
        if symbol in color or side not in range(k):
            errors.append("bad_forced_step_target")
            continue
        if set(neighbor_map) != {str(i) for i in range(k) if i != side}:
            errors.append("forced_step_missing_excluded_color_witness")
            continue
        for color_key, neighbor in neighbor_map.items():
            edge = tuple(sorted((symbol, neighbor)))
            if edge not in expected_edges or color.get(neighbor) != int(color_key):
                errors.append("forced_step_witness_invalid")
        color[symbol] = side
    if set(color) != set(vertices):
        errors.append("certificate_did_not_color_all_vertices")
        return errors
    blocks = canonical_partition([[v for v, c in color.items() if c == i] for i in range(k)])
    if blocks != canonical_partition(cert.get("blocks", [])):
        errors.append("certificate_blocks_do_not_match_replay")
    if any(color[a] == color[b] for a, b in expected_edges):
        errors.append("certificate_coloring_not_proper")
    colorings = graph_partition_oracle(vertices, expected_edges, k)
    if colorings != {blocks}:
        errors.append("certificate_graph_coloring_not_unique")
    return errors


def verify_sparse_graph(data, q, result):
    errors = []
    graph = result.get("graph", {})
    expected = opposition_edges(data, q)
    actual_list = graph.get("edges", [])
    actual = {tuple(sorted(edge)) for edge in actual_list if isinstance(edge, list) and len(edge) == 2}
    unary_shortcut = (result.get("status") == "infeasible"
                      and result.get("reason") == "more_than_q_positive_unary_counts")
    empty_positive_shortcut = (result.get("status") == "insufficient_coverage"
                               and result.get("reason") == "no_positive_q_opposition_evidence")
    if not graph.get("construction_complete") and not unary_shortcut and not empty_positive_shortcut:
        errors.append("graph_construction_incomplete_without_timeout")
    if not unary_shortcut and not empty_positive_shortcut and (actual != expected or len(actual_list) != len(actual)):
        errors.append("opposition_edge_set_mismatch")
    witness_rows = graph.get("edge_witnesses", [])
    witness_map = {tuple(sorted(item.get("symbols", []))): item for item in witness_rows
                   if isinstance(item, dict)}
    if not unary_shortcut and not empty_positive_shortcut and set(witness_map) != expected:
        errors.append("edge_witness_coverage_mismatch")
    positive = sorted(set(data["positive"]))
    for edge in (() if unary_shortcut or empty_positive_shortcut else expected):
        witness = witness_map.get(edge)
        if witness is None:
            continue
        indices = witness.get("positive_indices", [])
        values = witness.get("pair_projections", [])
        if len(indices) != len(values) or len(set(values)) <= q:
            errors.append("edge_witness_threshold_failure")
            continue
        for index, value in zip(indices, values):
            if not isinstance(index, int) or index < 0 or index >= len(positive):
                errors.append("edge_witness_index_out_of_range")
                continue
            if project(positive[index], edge) != value:
                errors.append("edge_witness_projection_mismatch")
    certificate = result.get("certificate")
    if isinstance(certificate, dict) and "anchor" in certificate:
        errors.extend(verify_graph_certificate(graph, certificate, expected, data["k"]))
    if isinstance(certificate, dict) and certificate.get("kind") == "unary_q_violation":
        symbol = certificate.get("symbol")
        positives = sorted(set(data["positive"]))
        observed = {project(word, (symbol,)) for word in positives}
        if symbol not in set(data["alphabet"]) or len(observed) <= q:
            errors.append("unary_q_infeasibility_witness_invalid")
        witness_counts = certificate.get("counts", [])
        witness_indices = certificate.get("positive_indices", [])
        if (len(witness_counts) <= q or any(count not in {len(value) for value in observed}
                                             for count in witness_counts)
                or len(set(witness_counts)) != len(witness_counts)
                or len(witness_indices) != len(witness_counts)):
            errors.append("unary_q_infeasibility_counts_mismatch")
        else:
            for count, index in zip(witness_counts, witness_indices):
                if (not isinstance(index, int) or index < 0 or index >= len(positives)
                        or len(project(positives[index], (symbol,))) != count):
                    errors.append("unary_q_infeasibility_index_mismatch")
    if isinstance(certificate, dict) and certificate.get("offending_block_index") is not None:
        idx = certificate["offending_block_index"]
        blocks = certificate.get("blocks", [])
        if not isinstance(idx, int) or idx not in range(len(blocks)):
            errors.append("full_block_cap_witness_bad_index")
        else:
            actual_values = {project(word, blocks[idx]) for word in set(data["positive"])}
            if len(actual_values) <= q or sorted(actual_values) != certificate.get("distinct_positive_projections"):
                errors.append("full_block_cap_witness_invalid")
    if isinstance(certificate, dict) and "accepted_negative" in certificate:
        blocks = certificate.get("blocks", [])
        negative = certificate.get("accepted_negative")
        languages = [{project(word, block) for word in set(data["positive"])} for block in blocks]
        if negative not in set(data["negative"]) or not all(
                project(negative, block) in languages[i] for i, block in enumerate(blocks)):
            errors.append("accepted_negative_infeasibility_witness_invalid")
    return errors


def validate_freeze():
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    manifest_bytes = MANIFEST.read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != freeze["manifest_sha256"]:
        raise AssertionError("frozen manifest hash mismatch")
    manifest = json.loads(manifest_bytes)
    bad = []
    for row in manifest["small"]["cases"] + manifest["stage2"]["cases"]:
        for key, hash_key in (("input", "input_sha256"), ("hidden", "hidden_sha256")):
            path = ROOT / row[key]
            if not path.is_file() or sha(path) != row[hash_key]:
                bad.append({"id": row["id"], "file": key, "hash_mismatch": True})
    if bad:
        raise AssertionError(f"corpus input/sidecar hash mismatch: {bad[:3]}")
    return manifest, freeze


def run_invalid(exact, sparse, manifest):
    cases = [row for row in manifest["small"]["cases"] if row["family"] == "invalid_input_control"]
    outcomes = []
    errors = []
    for row in cases:
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        result = {"id": row["id"], "exact": {}, "sparse": {}}
        for name, fn, q in (("exact", exact.solve, 2), ("sparse", sparse.solve, 2)):
            try:
                fn(data, k=data["k"], local_word_cap=q, deadline=None, max_solutions=None)
                status = "accepted_invalid"
            except ValueError as exc:
                status = "rejected_value_error"
                result[name]["error"] = str(exc)
            except Exception as exc:  # preserve non-validation failures as a discrepancy
                status = "raised_wrong_exception"
                result[name]["error"] = repr(exc)
            result[name]["status"] = status
            if status != "rejected_value_error":
                errors.append({"id": row["id"], "provider": name, "status": status})
        outcomes.append(result)
    return outcomes, errors


def run_deadline_controls(exact, sparse):
    data = {"alphabet": list("abcde"), "k": 3,
            "positive": ["acbde", "ebadc"], "negative": ["", "aa"]}
    outcomes, errors = [], []
    for name, fn, cap in (("exact", exact.solve, 2), ("sparse", sparse.solve, 2)):
        for label, deadline in (("expired", time.perf_counter() - 1.0),
                                ("near_expired", time.perf_counter() + 1e-12)):
            try:
                result = fn(data, k=3, local_word_cap=cap, deadline=deadline,
                            max_solutions=None if name == "exact" else 1)
                row = {"provider": name, "control": label, "status": result.get("status"),
                       "search_exhausted": result.get("search_exhausted"),
                       "decision_complete": result.get("decision_complete"),
                       "complete": result.get("complete"),
                       "uniqueness": result.get("uniqueness"),
                       "well_formed": isinstance(result.get("solutions"), list)}
                if result.get("status") != "incomplete" or not row["well_formed"]:
                    errors.append({"provider": name, "control": label, "reason": "did_not_return_well_formed_incomplete"})
            except Exception as exc:
                row = {"provider": name, "control": label, "raised": repr(exc)}
                errors.append({"provider": name, "control": label, "reason": "exception"})
            outcomes.append(row)
        for label, deadline in (("nan_deadline", float("nan")),
                                ("infinite_deadline", float("inf"))):
            try:
                fn(data, k=3, local_word_cap=cap, deadline=deadline,
                   max_solutions=None if name == "exact" else 1)
                errors.append({"provider": name, "control": label, "reason": "accepted_nonfinite_deadline"})
                outcomes.append({"provider": name, "control": label, "status": "accepted"})
            except ValueError as exc:
                outcomes.append({"provider": name, "control": label, "status": "rejected_value_error", "error": str(exc)})
            except Exception as exc:
                errors.append({"provider": name, "control": label, "reason": "wrong_exception", "detail": repr(exc)})
    return outcomes, errors


def run_graph_units(sparse):
    controls = json.loads(GRAPH_UNITS.read_text(encoding="utf-8"))["cases"]
    records, errors = [], []
    for row in controls:
        adjacency = {vertex: set() for vertex in row["vertices"]}
        for a, b in row["edges"]:
            adjacency[a].add(b)
            adjacency[b].add(a)
        actual = sparse.graph_certificate(adjacency, row["k"], deadline=None)
        oracle_set = graph_partition_oracle(row["vertices"], row["edges"], row["k"])
        expected = row["expected_unique_partition"]
        oracle_expected = ({canonical_partition(expected)} if expected is not None else None)
        if expected is None:
            if len(oracle_set) == 1:
                errors.append({"id": row["id"], "check": "unit_oracle_expected_nonunique_graph"})
            if actual is not None:
                errors.append({"id": row["id"], "check": "spurious_graph_certificate_for_nonunique_graph"})
        elif expected is not None:
            if oracle_set != oracle_expected:
                errors.append({"id": row["id"], "check": "unit_oracle_expected_partition_mismatch"})
            if actual is None or canonical_partition(actual["blocks"]) != canonical_partition(expected):
                errors.append({"id": row["id"], "check": "certificate_missing_or_wrong"})
            elif not actual.get("unique_q_opposition_coloring"):
                errors.append({"id": row["id"], "check": "missing_uniqueness_claim"})
            elif verify_graph_certificate({"symbols": row["vertices"]}, actual,
                                          {tuple(sorted(edge)) for edge in row["edges"]}, row["k"]):
                errors.append({"id": row["id"], "check": "certificate_replay_failure"})
        records.append({"id": row["id"], "oracle_proper_colorings": len(oracle_set),
                        "certificate": actual})
    return records, errors


def run_trace_sparse_control(sparse):
    fixture = json.loads(TRACE_FIXTURE.read_text(encoding="utf-8"))
    records, errors = [], []
    for row in fixture["cases"]:
        data = row["data"]
        q = row["q"]
        expected_edges = {tuple(edge) for edge in row["expected_edges"]}
        computed = opposition_edges(data, q)
        if computed != expected_edges:
            errors.append({"id": row["id"], "check": "independent_trace_edge_set_mismatch"})
        result = sparse.solve(data, k=data["k"], local_word_cap=q, deadline=None, max_solutions=1)
        errors.extend({"id": row["id"], "check": err} for err in verify_sparse_graph(data, q, result))
        if result.get("status") != "found" or partition_set(result) != {canonical_partition(row["expected_blocks"])}:
            errors.append({"id": row["id"], "check": "trace_sparse_target_not_certified"})
        for solution in result.get("solutions", []):
            errors.extend({"id": row["id"], "check": err}
                          for err in verify_partition_and_witnesses(data, solution, q))
        records.append({"id": row["id"], "q": q, "expected_edges": sorted(expected_edges),
                        "result": result})
    return records, errors


def main():
    manifest, freeze = validate_freeze()
    if sha(EXACT_PATH) != EXPECTED_EXACT_SHA256:
        raise AssertionError("exact provider source differs from frozen readiness hash")
    if sha(SPARSE_PATH) != EXPECTED_SPARSE_SHA256:
        raise AssertionError("sparse provider source differs from frozen readiness hash")
    exact = load_module("audit_exact_v2", EXACT_PATH)
    sparse = load_module("audit_sparse_v2", SPARSE_PATH)
    exact_rows = []
    sparse_rows = []
    errors = []
    valid_rows = [row for row in manifest["small"]["cases"]
                  if row["family"] != "invalid_input_control"]
    for row in valid_rows:
        data = json.loads((ROOT / row["input"]).read_text(encoding="utf-8"))
        if len(data["alphabet"]) > 7:
            continue
        expected_by_q = {}
        for q in (1, 2, 3, 4, None):
            expected = oracle(data, q)
            expected_by_q[q] = expected
            try:
                result = exact.solve(data, k=data["k"], local_word_cap=q,
                                     deadline=None, max_solutions=None)
                actual = partition_set(result)
                witness_errors = [err for sol in result.get("solutions", [])
                                  for err in verify_partition_and_witnesses(data, sol, q)]
                exhausted = bool(result.get("search_exhausted"))
                complete = bool(result.get("decision_complete"))
                equal = actual == expected
                if not equal or not exhausted or not complete or witness_errors:
                    errors.append({"id": row["id"], "provider": "exact", "q": q,
                                   "check": "full_set_or_witness_mismatch",
                                   "expected": sorted(expected), "actual": sorted(actual),
                                   "search_exhausted": exhausted, "decision_complete": complete,
                                   "witness_errors": witness_errors})
                exact_rows.append({"id": row["id"], "q": q, "expected": sorted(expected),
                                   "actual": sorted(actual), "status": result.get("status"),
                                   "search_exhausted": exhausted, "decision_complete": complete,
                                   "witness_errors": witness_errors, "result": result})
            except Exception as exc:
                errors.append({"id": row["id"], "provider": "exact", "q": q,
                               "check": "provider_exception", "exception": repr(exc)})
        sets = [expected_by_q[q] for q in (1, 2, 3, 4, None)]
        if any(not sets[i] <= sets[i + 1] for i in range(len(sets) - 1)):
            errors.append({"id": row["id"], "provider": "oracle", "check": "q_feasible_sets_not_nested"})

        for q in (1, 2, 3, 4):
            try:
                result = sparse.solve(data, k=data["k"], local_word_cap=q,
                                      deadline=None, max_solutions=1)
                graph_errors = verify_sparse_graph(data, q, result)
                actual = partition_set(result)
                status = result.get("status")
                if status == "found":
                    if len(expected_by_q[q]) != 1 or actual != expected_by_q[q]:
                        errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                       "check": "unsound_or_nonunique_found",
                                       "expected": sorted(expected_by_q[q]), "actual": sorted(actual)})
                    for sol in result.get("solutions", []):
                        graph_errors.extend(verify_partition_and_witnesses(data, sol, q))
                    if (not result.get("search_exhausted") or not result.get("decision_complete")
                            or not result.get("complete") or result.get("uniqueness") != "unique"):
                        errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                       "check": "found_status_completion_fields_inconsistent"})
                elif status == "infeasible":
                    if expected_by_q[q]:
                        errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                       "check": "false_infeasible", "expected": sorted(expected_by_q[q])})
                    if result.get("uniqueness") != "none":
                        errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                       "check": "infeasible_uniqueness_not_none"})
                elif status in ("insufficient_coverage", "incomplete"):
                    if actual:
                        errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                       "check": "abstention_returned_solutions"})
                    # Abstention is preserved as abstention regardless of oracle feasibility.
                else:
                    errors.append({"id": row["id"], "provider": "sparse", "q": q,
                                   "check": "unknown_status", "status": status})
                errors.extend({"id": row["id"], "provider": "sparse", "q": q, "check": e}
                              for e in graph_errors)
                sparse_rows.append({"id": row["id"], "q": q, "status": status,
                                    "expected_count": len(expected_by_q[q]),
                                    "actual": sorted(actual), "search_exhausted": result.get("search_exhausted"),
                                    "decision_complete": result.get("decision_complete"),
                                    "graph_errors": graph_errors, "result": result})
            except Exception as exc:
                errors.append({"id": row["id"], "provider": "sparse", "q": q,
                               "check": "provider_exception", "exception": repr(exc)})

    invalid, invalid_errors = run_invalid(exact, sparse, manifest)
    errors.extend(invalid_errors)
    deadlines, deadline_errors = run_deadline_controls(exact, sparse)
    errors.extend(deadline_errors)
    graph_units, graph_errors = run_graph_units(sparse)
    errors.extend(graph_errors)
    trace_sparse, trace_errors = run_trace_sparse_control(sparse)
    errors.extend(trace_errors)
    status_counts = {}
    for row in sparse_rows:
        key = row["status"]
        status_counts[key] = status_counts.get(key, 0) + 1
    output = {
        "schema": "C005-independent-small-gate-results-v2",
        "seed": freeze["seed"],
        "freeze_manifest_sha256": freeze["manifest_sha256"],
        "provider_sha256": {"exact": sha(EXACT_PATH), "sparse": sha(SPARSE_PATH)},
        "counts": {"valid_small_payloads": len(valid_rows), "exact_full_set_comparisons": len(exact_rows),
                   "sparse_q_comparisons": len(sparse_rows), "invalid_controls": len(invalid),
                   "synthetic_graph_unit_controls": len(graph_units),
                   "trace_realizable_sparse_controls": len(trace_sparse), "errors": len(errors),
                   "sparse_status_counts": status_counts},
        "errors": errors,
        "invalid_controls": invalid,
        "deadline_controls": deadlines,
        "graph_unit_controls": graph_units,
        "trace_realizable_sparse_controls": trace_sparse,
        "exact_full_set_rows": exact_rows,
        "sparse_rows": sparse_rows,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

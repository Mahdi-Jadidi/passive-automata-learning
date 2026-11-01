"""Independent correctness gate for the frozen C006 solver_v5 provider."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
IMPL = ROOT / "implementation"
DATA_FILES = [
    AUDIT / "corpus_v1" / "inputs.jsonl",
    AUDIT / "corpus_v1" / "controls.jsonl",
    AUDIT / "targeted_nondec_v1" / "input.jsonl",
    AUDIT / "theory_examples_v1" / "inputs.jsonl",
]
EXPECTED_PATH = AUDIT / "oracle_v4" / "expected.jsonl"


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_blocks(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def project(word, block):
    members = set(block)
    return "".join(symbol for symbol in word if symbol in members)


def load_provider():
    path = IMPL / "solver_v5.py"
    spec = importlib.util.spec_from_file_location("c006_audited_solver_v5", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_partition_set(row):
    return {canonical_blocks(item["blocks"])
            for item in row["compatible_by_k"].get("2", [])}


def check_solution_independently(data, solution):
    if not isinstance(solution, dict):
        return False, "solution_not_object"
    blocks = solution.get("blocks")
    if not isinstance(blocks, list) or len(blocks) != 2:
        return False, "not_two_blocks"
    if any(not isinstance(block, list) or not block for block in blocks):
        return False, "empty_or_malformed_block"
    flattened = [symbol for block in blocks for symbol in block]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(data["alphabet"]):
        return False, "blocks_do_not_partition_alphabet"
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    languages = [{project(word, block) for word in positives} for block in blocks]
    expected_languages = [sorted(language) for language in languages]
    if solution.get("positive_projection_languages") != expected_languages:
        return False, "incorrect_positive_projection_languages"
    p_witnesses = solution.get("positive_witnesses")
    if not isinstance(p_witnesses, list) or len(p_witnesses) != len(positives):
        return False, "positive_witness_count"
    for word, witness in zip(positives, p_witnesses):
        if witness != {"word": word, "projections": [project(word, b) for b in blocks]}:
            return False, "incorrect_positive_witness"
    n_witnesses = solution.get("negative_witnesses")
    if not isinstance(n_witnesses, list) or len(n_witnesses) != len(negatives):
        return False, "negative_witness_count"
    for word, witness in zip(negatives, n_witnesses):
        projections = [project(word, block) for block in blocks]
        rejecting = [i for i, projection in enumerate(projections)
                     if projection not in languages[i]]
        if not rejecting:
            return False, "negative_is_accepted"
        if witness != {"word": word, "projections": projections,
                       "rejected_by_side": rejecting[0]}:
            return False, "incorrect_negative_witness"
    return True, "ok"


def replay_edge(edge, positive, negative, alphabet):
    if not isinstance(edge, dict):
        return False
    pair, witness = edge.get("symbols"), edge.get("witness")
    if (not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]
            or any(not isinstance(x, str) or x not in alphabet for x in pair)
            or not isinstance(witness, dict) or witness.get("negative") not in negative):
        return False
    a, b = pair
    n = witness["negative"]
    if witness.get("rule") == "adjacent_swap":
        p, i = witness.get("positive"), witness.get("position")
        return (p in positive and isinstance(i, int) and not isinstance(i, bool)
                and 0 <= i < len(p) - 1 and p[i:i + 2] in (a + b, b + a)
                and p[:i] + p[i + 1] + p[i] + p[i + 2:] == n)
    if witness.get("rule") == "insertion_rescue":
        ps, i = witness.get("positive"), witness.get("position")
        if (not isinstance(ps, list) or len(ps) != 2 or any(p not in positive for p in ps)
                or isinstance(i, bool) or not isinstance(i, int)):
            return False
        base, rescued = ps
        for j, deleted in enumerate(n):
            if j != i or deleted not in pair or n[:j] + n[j + 1:] != base:
                continue
            inserted = pair[1] if deleted == pair[0] else pair[0]
            if rescued in (n[:j] + inserted + n[j:], n[:j + 1] + inserted + n[j + 1:]):
                return True
        return False
    return False


def graph_components(alphabet, edges):
    parent = {a: a for a in alphabet}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for edge in edges:
        a, b = edge["symbols"]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups = {}
    for symbol in alphabet:
        groups.setdefault(find(symbol), []).append(symbol)
    return sorted((sorted(group) for group in groups.values()), key=lambda group: group[0])


def blocks_from_mask(components, mask):
    left, right = [], []
    for index, component in enumerate(components):
        (left if (mask >> index) & 1 else right).extend(component)
    return [sorted(left), sorted(right)]


def replay_certificate_independently(data, certificate):
    alphabet = sorted(data["alphabet"])
    positive, negative = set(data["positive"]), set(data["negative"])
    if not isinstance(certificate, dict) or certificate.get("kind") != "no_nontrivial_bipartition":
        return False, "wrong_certificate_kind", 0
    if len(alphabet) == 1:
        okay = (certificate.get("obstruction") == "singleton_alphabet"
                and certificate.get("alphabet") == alphabet
                and certificate.get("components") == [alphabet]
                and certificate.get("must_link_edges") == [])
        return okay, "singleton" if okay else "bad_singleton", 0
    edges = certificate.get("must_link_edges")
    if not isinstance(edges, list) or any(not replay_edge(e, positive, negative, set(alphabet)) for e in edges):
        return False, "invalid_edge_witness", 0
    components = graph_components(alphabet, edges)
    if certificate.get("alphabet") != alphabet or certificate.get("components") != components:
        return False, "component_mismatch", 0
    if len(components) == 1:
        okay = certificate.get("obstruction") == "connected_must_link_graph"
        return okay, "connected_graph" if okay else "wrong_connected_claim", 0
    if certificate.get("obstruction") != "complete_cut_collision_cover":
        return False, "wrong_cut_claim", 0
    records = certificate.get("cut_rejections")
    if not isinstance(records, list):
        return False, "missing_cut_rejections", 0
    expected_masks = [(tail << 1) | 1 for tail in range((1 << (len(components) - 1)) - 1)]
    by_mask = {}
    for record in records:
        if not isinstance(record, dict):
            return False, "malformed_cut_record", len(expected_masks)
        mask = record.get("canonical_left_atom_mask")
        if isinstance(mask, bool) or not isinstance(mask, int) or mask in by_mask:
            return False, "duplicate_or_invalid_mask", len(expected_masks)
        by_mask[mask] = record
    if set(by_mask) != set(expected_masks):
        return False, "incomplete_or_extra_cut_cover", len(expected_masks)
    for mask in expected_masks:
        blocks = blocks_from_mask(components, mask)
        collision = by_mask[mask].get("collision")
        if not isinstance(collision, dict) or collision.get("negative") not in negative:
            return False, "missing_negative_collision", len(expected_masks)
        matching = collision.get("matching_positive_by_side")
        if not isinstance(matching, list) or len(matching) != 2:
            return False, "missing_side_collision", len(expected_masks)
        n = collision["negative"]
        for side, p in enumerate(matching):
            if p not in positive or project(p, blocks[side]) != project(n, blocks[side]):
                return False, "invalid_side_collision", len(expected_masks)
        # Also independently establish that this cut really is infeasible.
        languages = [{project(p, block) for p in positive} for block in blocks]
        if any(any(project(n2, block) not in languages[i]
                   for i, block in enumerate(blocks)) for n2 in negative):
            return False, "covered_cut_is_compatible", len(expected_masks)
    return True, "complete_cut_collision_cover", len(expected_masks)


def check_invalid_controls(solver):
    cases = {
        "contradictory_labels": {"alphabet": ["a", "b"], "positive": ["a"], "negative": ["a"]},
        "unknown_symbol": {"alphabet": ["a", "b"], "positive": ["c"], "negative": []},
        "forbidden_k": {"alphabet": ["a", "b"], "positive": [], "negative": [], "k": 2},
        "forbidden_q": {"alphabet": ["a", "b"], "positive": [], "negative": [], "q": 3},
        "forbidden_local_word_cap": {"alphabet": ["a", "b"], "positive": [], "negative": [], "local_word_cap": 9},
    }
    outcomes = {}
    for name, data in cases.items():
        outcomes[name] = solver.solve(data, max_solutions=None)["status"]
        assert outcomes[name] == "invalid_input", (name, outcomes[name])
    return outcomes


def main():
    solver = load_provider()
    visible = []
    for path in DATA_FILES:
        visible.extend(read_jsonl(path))
    expected_rows = read_jsonl(EXPECTED_PATH)
    expected = {row["case_id"]: row for row in expected_rows}
    ids = [row["case_id"] for row in visible]
    assert len(visible) == len(expected_rows) == 135
    assert len(ids) == len(set(ids)) == len(expected)
    assert set(ids) == set(expected)

    rows = []
    total_solutions = total_witnesses = total_edges = total_cuts = 0
    by_kind = {}
    for visible_row in visible:
        case_id, data = visible_row["case_id"], visible_row["input"]
        oracle_row = expected[case_id]
        wanted = expected_partition_set(oracle_row)
        result = solver.solve(data, max_solutions=None)
        actual = {canonical_blocks(solution["blocks"]) for solution in result.get("solutions", [])}
        assert actual == wanted, (case_id, "full k=2 partition set mismatch", actual, wanted)
        assert result.get("complete") is True and result.get("enumeration_complete") is True, (case_id, result)
        assert result.get("decision_complete") is True, (case_id, result)
        assert (result.get("status") == "found") == bool(wanted), (case_id, result.get("status"), wanted)
        assert bool(oracle_row["feasible_nontrivial_k"]) == bool(wanted), (case_id, "coarsening/existence mismatch")
        for solution in result.get("solutions", []):
            ok, why = check_solution_independently(data, solution)
            assert ok, (case_id, "independent witness failure", why)
            assert solver.verify_solution(data, solution).get("valid") is True, (case_id, "provider verifier")
            total_witnesses += len(solution["positive_witnesses"]) + len(solution["negative_witnesses"])
        cert_info = None
        if not wanted:
            cert = result.get("certificate")
            ok, why, cuts = replay_certificate_independently(data, cert)
            assert ok, (case_id, "independent certificate failure", why)
            assert solver.verify_certificate(data, cert).get("valid") is True, (case_id, "provider certificate verifier")
            edge_count = len(cert.get("must_link_edges", []))
            total_edges += edge_count
            total_cuts += cuts
            cert_kind = cert.get("obstruction")
            by_kind[cert_kind] = by_kind.get(cert_kind, 0) + 1
            cert_info = {"kind": cert_kind, "edges": edge_count, "cuts": cuts}
        total_solutions += len(actual)
        rows.append({"case_id": case_id, "status": result["status"],
                     "compatible_bipartitions": len(actual), "certificate": cert_info,
                     "expected_feasible_k": oracle_row["feasible_nontrivial_k"],
                     "independent_witnesses_valid": True})

    # Explicit final target from the implementation owner; identical may also occur in the corpus.
    final_data = json.loads((IMPL / "FINAL_TARGET_V1.json").read_text(encoding="utf-8"))
    final_result = solver.solve(final_data, max_solutions=None)
    ok, why, final_cuts = replay_certificate_independently(final_data, final_result.get("certificate"))
    assert final_result["status"] == "not_decomposable" and ok, ("final target", why, final_result)
    assert solver.verify_certificate(final_data, final_result["certificate"]).get("valid") is True

    # Targeted verifier tampering: full cover, collision, edge shape/roles, and large empty cover.
    target = final_data
    target_cert = final_result["certificate"]
    tamper_results = {}
    cases = []
    missing = json.loads(json.dumps(target_cert)); missing["cut_rejections"].pop()
    cases.append(("missing_cut", target, missing))
    duplicate = json.loads(json.dumps(target_cert)); duplicate["cut_rejections"].append(json.loads(json.dumps(duplicate["cut_rejections"][0])))
    cases.append(("duplicate_cut", target, duplicate))
    bad_collision = json.loads(json.dumps(target_cert)); bad_collision["cut_rejections"][0]["collision"]["matching_positive_by_side"][0] = "not-a-positive"
    cases.append(("bad_collision", target, bad_collision))
    swap_data = {"alphabet": ["a", "b"], "positive": ["ab"], "negative": ["ba"]}
    swap_cert = solver.solve(swap_data, max_solutions=None)["certificate"]
    malformed_edge = json.loads(json.dumps(swap_cert)); malformed_edge["must_link_edges"][0]["symbols"][0] = "z"
    cases.append(("unknown_edge_symbol", swap_data, malformed_edge))
    malformed_rule = json.loads(json.dumps(swap_cert)); malformed_rule["must_link_edges"][0]["witness"].pop("rule")
    cases.append(("malformed_edge_rule", swap_data, malformed_rule))
    large_alpha = [chr(0x100 + i) for i in range(40)]
    large_data = {"alphabet": large_alpha, "positive": [], "negative": []}
    large_cert = {"kind": "no_nontrivial_bipartition", "obstruction": "complete_cut_collision_cover",
                  "alphabet": sorted(large_alpha), "components": [[x] for x in sorted(large_alpha)],
                  "must_link_edges": [], "cut_rejections": []}
    cases.append(("large_empty_cover", large_data, large_cert))
    for name, data, cert in cases:
        provider_check = solver.verify_certificate(data, cert)
        independent_check = replay_certificate_independently(data, cert)
        assert provider_check.get("valid") is False, (name, provider_check)
        assert independent_check[0] is False, (name, independent_check)
        tamper_results[name] = {"provider_rejected": True, "independent_rejected": True,
                                "provider_reason": provider_check.get("reason"),
                                "independent_reason": independent_check[1]}

    # Positive witness mutation must not validate.
    positive_case = next(row for row in visible if expected_partition_set(expected[row["case_id"]]))
    positive_data = positive_case["input"]
    positive_result = solver.solve(positive_data, max_solutions=None)
    forged_solution = json.loads(json.dumps(positive_result["solutions"][0]))
    if forged_solution["positive_witnesses"]:
        forged_solution["positive_witnesses"][0]["projections"][0] += "x"
    else:
        forged_solution["negative_witnesses"].append({"word": "forged"})
    assert solver.verify_solution(positive_data, forged_solution).get("valid") is False
    assert check_solution_independently(positive_data, forged_solution)[0] is False
    tamper_results["positive_witness"] = {"provider_rejected": True, "independent_rejected": True}

    # Timeout, max-solution truncation, and interruption after an answer keep non-final statuses.
    free_data = {"alphabet": ["a", "b", "c"], "positive": ["abc"], "negative": []}
    deadline_result = solver.solve(free_data, deadline=time.perf_counter() - 1, max_solutions=None)
    assert deadline_result["status"] == "incomplete" and deadline_result["complete"] is False
    truncated = solver.solve(free_data, max_solutions=1)
    assert truncated["status"] == "found" and truncated["complete"] is False
    original_compatibility = solver._compatibility
    calls = 0

    def interrupt_on_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        return original_compatibility(*args, **kwargs)

    solver._compatibility = interrupt_on_second
    interrupted = solver.solve(free_data, max_solutions=None)
    solver._compatibility = original_compatibility
    assert calls == 2 and interrupted["status"] == "incomplete" and not interrupted["complete"]
    assert interrupted["decision_complete"] is True and len(interrupted["solutions"]) == 1

    invalid_statuses = check_invalid_controls(solver)
    singleton = solver.solve({"alphabet": ["a"], "positive": [], "negative": []}, max_solutions=None)
    assert singleton["status"] == "not_decomposable"
    assert replay_certificate_independently({"alphabet": ["a"], "positive": [], "negative": []},
                                             singleton["certificate"])[0]

    report = {
        "gate": "C006_solver_v5_independent_correctness_gate_v1",
        "scientific_status": "passed" if len(rows) == 135 else "failed",
        "execution_status": "success",
        "cases": len(rows), "exact_full_bipartition_sets_matched": len(rows),
        "expected_all_k_existence_matched": len(rows),
        "provider_witnesses_independently_checked": total_witnesses,
        "independently_replayed_no_decomposition_certificates": sum(1 for r in rows if r["certificate"]),
        "certificate_cut_records_independently_checked": total_cuts + final_cuts,
        "must_link_edges_independently_replayed": total_edges,
        "certificate_kinds": by_kind,
        "extra_final_target": {"status": final_result["status"], "cut_count": final_cuts},
        "tampering_controls": tamper_results,
        "deadline": {"status": deadline_result["status"], "complete": deadline_result["complete"]},
        "truncation": {"status": truncated["status"], "complete": truncated["complete"],
                        "decision_complete": truncated["decision_complete"]},
        "interruption_after_answer": {"calls": calls, "status": interrupted["status"],
                                       "complete": interrupted["complete"],
                                       "decision_complete": interrupted["decision_complete"],
                                       "retained_solutions": len(interrupted["solutions"])},
        "invalid_input_controls": invalid_statuses,
        "singleton_control": singleton["status"],
        "inputs_sha256": {path.name: sha(path.read_bytes()) for path in DATA_FILES},
        "oracle_expected_sha256": sha(EXPECTED_PATH.read_bytes()),
        "rows": rows,
    }
    output = AUDIT / "validation_v2" / "solver_v5_gate.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

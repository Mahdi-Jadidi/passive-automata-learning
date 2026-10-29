"""Independent exhaustive stage-1 audit for alpha<=7; emits raw solver results."""
from __future__ import annotations
import importlib.util
import json
import sys
import time
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
CASE_IDS = set(sys.argv[2:]) if len(sys.argv) > 2 else None
CORPUS = MANIFEST.parent
HERE = Path(__file__).resolve().parent
V3_GENERAL = HERE.parent / "general" / "known_k_v3.py"
S001 = HERE.parent / "structural" / "singleton_solver_v1.py"
C003_GENERAL = HERE.parents[2] / "2026-10-26" / "partition_discovery_v3" / "general" / "general_solver.py"
C003_FIXED = HERE.parents[2] / "2026-10-26" / "partition_discovery_v3" / "structural" / "fixed_word_solver.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compositions(n, k):
    owner = [0] * n
    def visit(pos, hi):
        if pos == n:
            if hi + 1 == k:
                yield tuple(owner)
            return
        for side in range(min(hi + 1, k - 1) + 1):
            owner[pos] = side
            yield from visit(pos + 1, max(hi, side))
    if n:
        yield from visit(1, 0)


def project(word, block):
    return "".join(ch for ch in word if ch in block)


def partition_key(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def oracle(data, k, cap=None, exact_singleton=False):
    alphabet = sorted(data["alphabet"])
    positives = sorted(set(data["positive"]))
    negatives = sorted(set(data["negative"]))
    feasible = set()
    for owner in compositions(len(alphabet), k):
        blocks = [set() for _ in range(k)]
        for ch, side in zip(alphabet, owner):
            blocks[side].add(ch)
        langs = [{project(word, block) for word in positives} for block in blocks]
        if exact_singleton:
            if positives and any(len(lang) != 1 for lang in langs):
                continue
            # If no positive is observed, arbitrary longer singleton local words
            # exist: choose length 1+max negative length in each nonempty block.
        elif cap is not None and any(len(lang) > cap for lang in langs):
            continue
        if any(all(project(word, blocks[s]) in langs[s] for s in range(k))
               for word in negatives):
            continue
        feasible.add(partition_key(blocks))
    return feasible


def verify_solution(data, solution):
    alphabet = set(data["alphabet"])
    blocks = solution.get("blocks")
    if not isinstance(blocks, list) or any(not isinstance(b, list) for b in blocks):
        return ["solution_blocks_missing_or_malformed"]
    block_sets = [set(b) for b in blocks]
    errors = []
    if len(block_sets) != data["k"] or any(not b for b in block_sets):
        errors.append("wrong_block_count_or_empty_block")
    if set().union(*block_sets) != alphabet or sum(map(len, block_sets)) != len(alphabet):
        errors.append("blocks_do_not_partition_alphabet")
    positive = sorted(set(data["positive"]))
    negative = sorted(set(data["negative"]))
    expected_langs = [{project(w, b) for w in positive} for b in block_sets]
    reported = solution.get("positive_projection_languages")
    if reported is None and "local_words" in solution:
        reported = [[w] for w in solution["local_words"]]
    if reported is not None:
        actual = [sorted(set(x)) for x in reported]
        expected = [sorted(x) for x in expected_langs]
        if actual != expected:
            errors.append("reported_positive_projection_languages_mismatch")
    witness_map = {}
    for witness in solution.get("negative_witnesses", []):
        word = witness.get("negative")
        if word in witness_map:
            errors.append("duplicate_negative_witness")
        witness_map[word] = witness
    if set(witness_map) != set(negative):
        errors.append("negative_witness_coverage_mismatch")
    for word in negative:
        unseen = [i for i, block in enumerate(block_sets)
                  if project(word, block) not in expected_langs[i]]
        if not unseen:
            errors.append("negative_accepted_by_reported_partition")
            continue
        witness = witness_map.get(word)
        if witness is not None:
            i = witness.get("block_index")
            if not isinstance(i, int) or i not in range(len(block_sets)):
                errors.append("negative_witness_bad_block_index")
            elif witness.get("projection") != project(word, block_sets[i]):
                errors.append("negative_witness_projection_mismatch")
            elif witness.get("projection") in expected_langs[i]:
                errors.append("negative_witness_projection_was_seen")
            if sorted(witness.get("all_unseen_block_indices", [])) != unseen:
                errors.append("negative_witness_unseen_set_mismatch")
    return errors


def verify_edges(data, edges):
    positive, negative = set(data["positive"]), set(data["negative"])
    errors, seen = [], set()
    for edge in edges:
        pair = edge.get("symbols")
        witness = edge.get("witness")
        if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]:
            errors.append({"kind": "malformed_edge", "edge": edge})
            continue
        pair_key = tuple(sorted(pair))
        if pair_key in seen:
            errors.append({"kind": "duplicate_edge", "pair": pair_key})
        seen.add(pair_key)
        if not isinstance(witness, dict):
            errors.append({"kind": "edge_missing_witness", "pair": pair_key})
            continue
        rule = witness.get("rule")
        i = witness.get("position")
        if rule == "adjacent_swap":
            p, n = witness.get("positive"), witness.get("negative")
            valid = (isinstance(p, str) and isinstance(n, str) and
                     p in positive and n in negative and isinstance(i, int) and
                     0 <= i < len(p) - 1 and len(p) == len(n) and
                     p[:i] == n[:i] and p[i] != p[i+1] and
                     n[i:i+2] == p[i+1] + p[i] and p[i+2:] == n[i+2:] and
                     tuple(sorted((p[i], p[i+1]))) == pair_key)
            if not valid:
                errors.append({"kind": "invalid_adjacent_swap_witness", "pair": pair_key,
                               "witness": witness})
        elif rule == "insertion_rescue":
            ps, n = witness.get("positive"), witness.get("negative")
            valid = False
            if isinstance(ps, list) and len(ps) == 2 and isinstance(n, str) and n in negative and isinstance(i, int) and 0 <= i < len(n):
                base, rescued = ps
                a = n[i]
                valid_base = isinstance(base, str) and base in positive and base == n[:i] + n[i+1:]
                valid_rescue = False
                b = None
                if isinstance(rescued, str) and rescued in positive:
                    for j in (i, i + 1):
                        if 0 <= j <= len(n):
                            candidate = rescued[j] if j < len(rescued) else None
                            if candidate is not None and candidate != a and rescued == n[:j] + candidate + n[j:]:
                                b = candidate
                                valid_rescue = True
                                break
                valid = valid_base and valid_rescue and tuple(sorted((a, b))) == pair_key
            if not valid:
                errors.append({"kind": "invalid_insertion_rescue_witness", "pair": pair_key,
                               "witness": witness})
        else:
            errors.append({"kind": "unknown_edge_witness_rule", "pair": pair_key,
                           "witness": witness})
    return errors


def run():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    general = load_module("audit_general_v3", V3_GENERAL)
    structural = load_module("audit_s001", S001)
    c003_general = load_module("audit_c003_general", C003_GENERAL)
    c003_fixed = load_module("audit_c003_fixed", C003_FIXED)
    raw, mismatches, small = [], [], []
    for row in manifest["cases"]:
        if row["alphabet_size"] > 7 or row["family"] == "invalid":
            continue
        if CASE_IDS is not None and row["id"] not in CASE_IDS:
            continue
        data = json.loads((CORPUS / row["input"]).read_text(encoding="utf-8"))
        k = data["k"]
        if isinstance(k, bool) or not isinstance(k, int) or not 2 <= k <= len(data["alphabet"]):
            continue
        expected = oracle(data, k)
        expected_q1 = oracle(data, k, cap=1)
        expected_singleton = oracle(data, k, exact_singleton=True)
        started = time.perf_counter()
        gen = general.solve(data, k=k, deadline=time.perf_counter()+20,
                            max_solutions=None, local_word_cap=None)
        q1 = general.solve(data, k=k, deadline=time.perf_counter()+20,
                           max_solutions=None, local_word_cap=1)
        st = structural.solve(data, k=k, deadline=time.perf_counter()+20, max_solutions=None)
        sys.stdout.write(json.dumps({"type": "raw_candidate_results", "id": row["id"],
                                     "general": gen, "q1": q1, "structural": st},
                                    ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        result_row = {"id": row["id"], "expected_general_count": len(expected),
                      "expected_q1_count": len(expected_q1),
                      "expected_singleton_exact_count": len(expected_singleton),
                      "general": gen, "q1": q1, "structural": st}
        gen_set = {partition_key(x["blocks"]) for x in gen["solutions"]}
        q1_set = {partition_key(x["blocks"]) for x in q1["solutions"]}
        if gen_set != expected or not gen.get("search_exhausted") or not gen.get("decision_complete"):
            mismatches.append({"id": row["id"], "check": "general_full_set",
                               "expected": sorted(expected), "actual": sorted(gen_set),
                               "status": gen.get("status"), "exhausted": gen.get("search_exhausted")})
        if q1_set != expected_q1 or not q1.get("search_exhausted"):
            mismatches.append({"id": row["id"], "check": "general_q1_full_set",
                               "expected": sorted(expected_q1), "actual": sorted(q1_set),
                               "status": q1.get("status"), "exhausted": q1.get("search_exhausted")})
        edge_errors = verify_edges(data, gen.get("graph", {}).get("edges", []))
        if edge_errors:
            mismatches.append({"id": row["id"], "check": "general_graph_witnesses", "errors": edge_errors})
        for solution in gen["solutions"]:
            errs = verify_solution(data, solution)
            if errs:
                mismatches.append({"id": row["id"], "check": "general_solution_witness", "errors": errs})
        st_status = st.get("status")
        st_set = {partition_key(x["blocks"]) for x in st.get("solutions", [])}
        if st_status == "found":
            if st_set != expected_singleton or len(expected_singleton) != 1:
                mismatches.append({"id": row["id"], "check": "structural_unsound_certificate",
                                   "expected_singleton": sorted(expected_singleton), "actual": sorted(st_set)})
        elif st_status == "infeasible":
            if expected_singleton:
                mismatches.append({"id": row["id"], "check": "structural_false_infeasible",
                                   "expected_singleton": sorted(expected_singleton)})
        elif st_status not in ("insufficient_coverage", "incomplete"):
            mismatches.append({"id": row["id"], "check": "structural_unexpected_status", "status": st_status})
        for solution in st.get("solutions", []):
            errs = verify_solution(data, solution)
            if errs:
                mismatches.append({"id": row["id"], "check": "structural_solution_witness", "errors": errs})
        c3 = None
        if k == 2:
            c3 = c003_general.solve(data, deadline=time.perf_counter()+20, max_solutions=None)
            sys.stdout.write(json.dumps({"type": "raw_c003_general", "id": row["id"],
                                         "result": c3}, ensure_ascii=False,
                                        separators=(",", ":")) + "\n")
            sys.stdout.flush()
            c3_set = {partition_key(x["blocks"]) for x in c3["solutions"]}
            if c3_set != expected or not c3.get("search_exhausted"):
                mismatches.append({"id": row["id"], "check": "c003_k2_bridge_full_set",
                                   "expected": sorted(expected), "actual": sorted(c3_set),
                                   "status": c3.get("status"), "exhausted": c3.get("search_exhausted")})
            for solution in c3["solutions"]:
                errs = verify_solution(data, solution)
                if errs:
                    mismatches.append({"id": row["id"], "check": "c003_witness", "errors": errs})
            c3f = c003_fixed.solve(data, deadline=time.perf_counter()+20, max_solutions=None)
            sys.stdout.write(json.dumps({"type": "raw_c003_fixed", "id": row["id"],
                                         "result": c3f}, ensure_ascii=False,
                                        separators=(",", ":")) + "\n")
            sys.stdout.flush()
            c3f_set = {partition_key(x["blocks"]) for x in c3f.get("solutions", [])}
            if c3f.get("status") == "found" and (c3f_set != expected_singleton or len(expected_singleton) != 1):
                mismatches.append({"id": row["id"], "check": "c003_fixed_word_unsound", "expected": sorted(expected_singleton), "actual": sorted(c3f_set)})
            if c3f.get("status") == "assumption_violation" and expected_singleton:
                mismatches.append({"id": row["id"], "check": "c003_fixed_word_false_rejection",
                                   "expected_singleton": sorted(expected_singleton)})
            for solution in c3f.get("solutions", []):
                errs = verify_solution(data, solution)
                if errs:
                    mismatches.append({"id": row["id"], "check": "c003_fixed_witness", "errors": errs})
        else:
            c3f = None
        result_row["c003_general"] = c3
        result_row["c003_fixed"] = c3f
        result_row["audit_elapsed_nonbenchmark_seconds"] = time.perf_counter() - started
        raw.append({"id": row["id"], "general_status": gen.get("status"),
                    "q1_status": q1.get("status"), "structural_status": st_status,
                    "c003_general_status": c3.get("status") if c3 else None,
                    "c003_fixed_status": c3f.get("status") if c3f else None})
        small.append({"id": row["id"], "k": k, "alphabet_size": len(data["alphabet"]),
                      "general_solution_count": len(expected), "q1_solution_count": len(expected_q1),
                      "singleton_exact_count": len(expected_singleton),
                      "structural_status": st_status,
                      "c003_k2": k == 2})
    report = {"audit": "C004 independent small exhaustive full-set audit v1",
              "manifest": str(MANIFEST), "candidate_general_source": str(V3_GENERAL),
              "candidate_structural_source": str(S001), "cases_audited": len(raw),
              "mismatch_count": len(mismatches), "mismatches": mismatches,
              "case_summaries": small, "result_summaries": raw}
    sys.stdout.write(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.flush()
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(run())

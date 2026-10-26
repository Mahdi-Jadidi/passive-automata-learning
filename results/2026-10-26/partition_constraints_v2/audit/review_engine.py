"""Independent bounded review of A's proposed shared engine and helpers."""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import time
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
CYCLE = AUDIT.parent
EAGER = CYCLE / "approaches" / "eager"
CORPUS = AUDIT / "corpus" / "frozen_v1"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(EAGER / "engine_candidate.py", "c002_audit_engine_candidate")
HELPERS = load_module(EAGER / "common_helpers_candidate.py", "c002_audit_helper_candidate")


def words(alphabet: str, max_len: int) -> list[str]:
    return ["".join(items) for length in range(max_len + 1)
            for items in itertools.product(alphabet, repeat=length)]


def all_blocks(alphabet: str) -> list[set[str]]:
    return [set(alphabet[i] for i in range(len(alphabet)) if (mask >> i) & 1)
            for mask in range(1, 1 << len(alphabet))]


def canonical_ownership_models(size: int):
    for suffix in itertools.product((0, 1), repeat=size - 1):
        assignment = (0,) + suffix
        if 1 in assignment:
            yield assignment


def reference_eval(expr, assignment):
    kind = expr[0]
    if kind == "const":
        return bool(expr[1])
    if kind == "lit":
        value = assignment[expr[1]]
        return None if value == -1 else value == expr[2]
    values = [reference_eval(child, assignment) for child in expr[1]]
    if kind == "and":
        return False if False in values else None if None in values else True
    if kind == "or":
        return True if True in values else None if None in values else False
    raise AssertionError(kind)


def expression_family(size: int):
    atoms = [("const", False), ("const", True)]
    atoms += [("lit", i, side) for i in range(size) for side in (0, 1)]
    expressions = list(atoms) + [("and", ()), ("or", ())]
    for op in ("and", "or"):
        for left in atoms:
            for right in atoms:
                expressions.append((op, (left, right)))
        for triple in itertools.combinations(atoms, 3):
            expressions.append((op, tuple(triple)))
        for left in atoms:
            for right in atoms:
                expressions.append((op, (("and", (left, right)),
                                         ("or", (right, left)))))
    return expressions


def check_engine() -> dict:
    eval_cases = 0
    model_cases = 0
    formula_counts = {}
    for size in range(2, 4):
        formulas = expression_family(size)
        formula_counts[str(size)] = len(formulas)
        partials = list(itertools.product((-1, 0, 1), repeat=size))
        for expr in formulas:
            for partial in partials:
                actual = ENGINE.eval_expr(expr, partial)
                expected = reference_eval(expr, partial)
                assert actual is expected, (expr, partial, actual, expected)
                eval_cases += 1
                if actual is False:
                    for completion in itertools.product((0, 1),
                                                        repeat=partial.count(-1)):
                        iterator = iter(completion)
                        full = tuple(next(iterator) if value == -1 else value
                                     for value in partial)
                        assert reference_eval(expr, full) is False, (expr, partial, full)

        constraints = [[], [("const", True)], [("const", False)]]
        constraints.extend([(expr,) for expr in formulas])
        # Pair interactions detect accidental per-constraint/last-constraint logic.
        for i in range(0, min(32, len(formulas) - 1), 2):
            constraints.append([formulas[i], formulas[i + 1]])
        for constraint_list in constraints:
            got = list(ENGINE.iter_models(size, constraint_list))
            expected = [assignment for assignment in canonical_ownership_models(size)
                        if all(reference_eval(expr, assignment) is True
                               for expr in constraint_list)]
            assert got == expected, (size, constraint_list, got, expected)
            assert len(got) == len(set(got))
            assert all(model[0] == 0 and 1 in model for model in got)
            first = ENGINE.find_model(size, constraint_list)
            assert first == (expected[0] if expected else None)
            model_cases += 1

    try:
        list(ENGINE.iter_models(3, [], deadline=time.perf_counter() - 1))
    except ENGINE.SearchInterrupted:
        expired_deadline_raised = True
    else:
        raise AssertionError("expired deadline did not raise SearchInterrupted")

    stats = {}
    assert list(ENGINE.iter_models(3, [], stats=stats))
    before = stats.copy()
    assert list(ENGINE.iter_models(3, [("const", False)], stats=stats)) == []
    assert stats["nodes_visited"] > before["nodes_visited"]
    assert stats["complete_assignments"] >= before["complete_assignments"]
    for bad in (True, 1, 0, -1, 1.5):
        try:
            list(ENGINE.iter_models(bad, []))
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid num_vars accepted: {bad!r}")
    return {"formula_count_by_size": formula_counts,
            "three_valued_expression_cases": eval_cases,
            "pruning_completions_checked": True,
            "enumeration_constraint_sets": model_cases,
            "find_model_matches_first_lex_model": True,
            "models_unique_canonical_nonempty": True,
            "deadline_expiration_raises": expired_deadline_raised,
            "cumulative_stats": stats}


def check_helpers() -> dict:
    legacy = HELPERS.load_baseline()
    theory_path = CYCLE / "baseline" / "theory_ambiguous.json"
    data_files = [CORPUS / "solver_inputs" / "targeted_controls.jsonl",
                  CORPUS / "solver_inputs" / "prior_theory_4.jsonl"]
    data_records = [json.loads(line) for path in data_files
                    for line in path.read_text(encoding="utf-8").splitlines()]
    for item in data_records:
        data = item["input"]
        alphabet, positive, negative = HELPERS.validate(data)
        old_alpha, old_positive, old_negative = legacy.validate(data)
        assert (alphabet, positive, negative) == (old_alpha, old_positive, old_negative)
        old_graph = legacy.witness_graph(alphabet, positive, negative)
        new_graph = HELPERS.witness_graph(alphabet, positive, negative)
        assert new_graph == old_graph

    alphabet = "abc"
    universe = words(alphabet, 3)
    distinguisher_cases = 0
    checked_blocks = 0
    for negative in universe:
        for positive in universe:
            family = HELPERS.distinguishers(list(alphabet), negative, positive)
            assert family == tuple(sorted(family, key=lambda subset: (len(subset), subset)))
            for subset in family:
                assert len(subset) in (1, 2)
                projected_n = HELPERS.project(negative, {alphabet[i] for i in subset})
                projected_p = HELPERS.project(positive, {alphabet[i] for i in subset})
                assert projected_n != projected_p
            for block in all_blocks(alphabet):
                differs = HELPERS.project(negative, block) != HELPERS.project(positive, block)
                represented = any(set(subset) <= {alphabet.index(symbol) for symbol in block}
                                  for subset in family)
                assert differs == represented, (negative, positive, block, family)
                checked_blocks += 1
            distinguisher_cases += 1

    for a, b in itertools.combinations(range(4), 2):
        expr = HELPERS.graph_constraints(list("abcd"), [{"symbols": ["abcd"[a], "abcd"[b]]}])[0]
        for assignment in canonical_ownership_models(4):
            assert ENGINE.eval_expr(expr, assignment) is (assignment[a] == assignment[b])

    record_cases = 0
    for item in data_records:
        data = item["input"]
        alphabet, positive, negative = HELPERS.validate(data)
        baseline = legacy.solve(data, prune=False)
        expected = {tuple(tuple(block) for block in record["blocks"])
                    for record in baseline["feasible_partitions"]}
        actual = set()
        for ownership in canonical_ownership_models(len(alphabet)):
            blocks = [{symbol for symbol, side in zip(alphabet, ownership) if side == s}
                      for s in (0, 1)]
            candidate = HELPERS.partition_record(alphabet, positive, negative, ownership)
            key = tuple(tuple(sorted(block)) for block in blocks)
            if candidate is None:
                assert key not in expected
                continue
            assert key in expected
            for witness in candidate["negative_witnesses"]:
                side = witness["block_index"]
                assert witness["projection"] == HELPERS.project(witness["negative"], blocks[side])
                positive_projections = {HELPERS.project(word, blocks[side]) for word in positive}
                assert witness["projection"] not in positive_projections
            actual.add(key)
        assert actual == expected, (item["case_id"], actual, expected)
        record_cases += 1

    # The loader must work after changing away from the workspace/cycle CWD.
    old_cwd = Path.cwd()
    try:
        os.chdir(Path(os.environ.get("WINDIR", r"C:\Windows")))
        assert HELPERS.load_baseline().validate(json.loads(theory_path.read_text(encoding="utf-8")))
    finally:
        os.chdir(old_cwd)

    incomplete = HELPERS.result_from_records(
        ["a", "b"], [], [], [], method="audit", components=[["a"], ["b"]],
        edges=[], complete=False)
    assert incomplete["complete"] is False
    assert incomplete["status"] == "incomplete"
    assert incomplete["feasible_partition_count"] is None
    assert incomplete["found_partition_count"] == 0
    return {"baseline_validation_graph_delegation_cases": len(data_records),
            "word_pair_distinguisher_cases": distinguisher_cases,
            "block_equivalence_cases": checked_blocks,
            "graph_constraint_equalities": 6,
            "direct_record_vs_unpruned_baseline_cases": record_cases,
            "witness_projections_independently_validated": True,
            "baseline_loader_cwd_independent": True,
            "incomplete_result_contract": True}


def main() -> int:
    report = {
        "engine": check_engine(),
        "helpers": check_helpers(),
        "note": "Bounded independent audit of shared candidate primitives; this is not yet the end-to-end 5000-sample or benchmark audit.",
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Independent exhaustive partition oracle and q-cap sweep for small inputs."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("known_k_v3_qcap_sweep", HERE / "known_k_v3.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)
INPUT = HERE / "fixtures" / "qcap_sweep_inputs.json"
TRUTH = HERE / "fixtures" / "qcap_sweep_truth.json"
cases = json.loads(INPUT.read_text(encoding="utf-8"))["cases"]
truth = json.loads(TRUTH.read_text(encoding="utf-8"))
CAPS = (1, 2, 3, None)


def independent_project(word, block):
    return "".join(symbol for symbol in word if symbol in block)


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def all_partitions(alphabet, k):
    symbols = sorted(alphabet)

    def visit(prefix):
        if len(prefix) == len(symbols):
            if max(prefix) + 1 == k:
                blocks = [{s for s, owner in zip(symbols, prefix) if owner == side}
                          for side in range(k)]
                yield blocks
            return
        used = max(prefix) + 1 if prefix else 0
        for side in range(min(used, k - 1) + 1):
            yield from visit(prefix + (side,))

    yield from visit(())


def oracle(data, cap):
    positive = sorted(set(data["positive"]))
    negative = sorted(set(data["negative"]))
    feasible = set()
    for blocks in all_partitions(data["alphabet"], data["k"]):
        languages = [{independent_project(word, block) for word in positive}
                     for block in blocks]
        if cap is not None and any(len(language) > cap for language in languages):
            continue
        if any(all(independent_project(word, block) in languages[side]
                   for side, block in enumerate(blocks)) for word in negative):
            continue
        feasible.add(canonical_partition(blocks))
    return feasible


def provider_partition_set(result):
    return {canonical_partition(solution["blocks"]) for solution in result["solutions"]}


def verify_witnesses(data, result, cap):
    errors = []
    for solution in result["solutions"]:
        blocks = solution["blocks"]
        languages = [{independent_project(word, block) for word in data["positive"]}
                     for block in blocks]
        reported = [set(language) for language in solution["positive_projection_languages"]]
        if reported != languages:
            errors.append("projection_languages")
        if cap is not None:
            if not all(len(language) <= cap for language in languages):
                errors.append("cap_violation")
        witness_map = {w["negative"]: w for w in solution["negative_witnesses"]}
        if set(witness_map) != set(data["negative"]):
            errors.append("negative_coverage")
        for word in data["negative"]:
            projections = [independent_project(word, block) for block in blocks]
            unseen = [i for i, value in enumerate(projections) if value not in languages[i]]
            witness = witness_map.get(word)
            if witness is None:
                errors.append("missing_witness:" + word)
                continue
            if (not unseen or witness["block_index"] != unseen[0]
                    or witness["projection"] != projections[unseen[0]]
                    or witness["all_unseen_block_indices"] != unseen):
                errors.append("negative_witness:" + word)
    return errors


records = {}
results_by_case = {}
errors = []
for name, data in cases.items():
    records[name] = {}
    results_by_case[name] = {}
    for cap in CAPS:
        expected = oracle(data, cap)
        result = provider.solve(data, k=data["k"], deadline=None,
                                max_solutions=None, local_word_cap=cap)
        actual = provider_partition_set(result)
        witness_errors = verify_witnesses(data, result, cap)
        partition_equal = expected == actual
        complete = result["search_exhausted"] and result["decision_complete"]
        if not partition_equal:
            errors.append("partition_set:" + name + ":" + str(cap))
        if not complete:
            errors.append("incomplete_search:" + name + ":" + str(cap))
        if witness_errors:
            errors.extend(name + ":" + str(cap) + ":" + error for error in witness_errors)
        results_by_case[name][cap] = actual
        records[name]["infinity" if cap is None else str(cap)] = {
            "status": result["status"],
            "expected_partitions": sorted([[list(block) for block in part] for part in expected]),
            "actual_partitions": sorted([[list(block) for block in part] for part in actual]),
            "partition_equal": partition_equal,
            "witness_errors": witness_errors,
            "nodes": result["metrics"]["nodes"],
            "leaves": result["metrics"]["leaves"],
            "cap_pruned_nodes": result["metrics"]["cap_pruned_nodes"],
            "search_exhausted": result["search_exhausted"],
            "decision_complete": result["decision_complete"]
        }
    nested = (results_by_case[name][1] <= results_by_case[name][2]
              <= results_by_case[name][3] <= results_by_case[name][None])
    records[name]["nested_feasible_sets"] = nested
    if not nested:
        errors.append("nesting:" + name)

# The planted partition is audit-only and never enters provider.solve.
planted = canonical_partition(truth["actual_true_q2"]["planted_partition"])
planted_membership = {"1": planted in results_by_case["actual_true_q2"][1],
                      "2": planted in results_by_case["actual_true_q2"][2],
                      "3": planted in results_by_case["actual_true_q2"][3],
                      "infinity": planted in results_by_case["actual_true_q2"][None]}
if planted_membership != {"1": False, "2": True, "3": True, "infinity": True}:
    errors.append("planted_partition_membership")
target_q2 = provider.solve(cases["actual_true_q2"], k=2, max_solutions=None,
                          local_word_cap=2)
target_languages = sorted([sorted(x) for x in target_q2["solutions"][0]["positive_projection_languages"]]) if target_q2["solutions"] else []
expected_target_languages = sorted([sorted(x) for x in truth["actual_true_q2"]["planted_local_languages"]])
target_languages_match = target_languages == expected_target_languages
if not target_languages_match:
    errors.append("planted_local_languages")

# Empty positive samples mean every bounded local projection language is empty;
# this differs from the nonempty positive sample containing the empty word.
empty_result = provider.solve(cases["empty_positive_semantics"], k=2,
                              max_solutions=None, local_word_cap=2)
empty_positive_ok = (len(empty_result["solutions"]) == 3 and
                     all(solution["positive_projection_languages"] == [[], []]
                         for solution in empty_result["solutions"]))
if not empty_positive_ok:
    errors.append("empty_positive_semantics")

# A q=1 cap violation prunes before reaching a complete partition.
pruned = provider.solve(cases["actual_true_q2"], k=2, max_solutions=None,
                        local_word_cap=1)
cap_pruning_ok = pruned["metrics"]["cap_pruned_nodes"] > 0
if not cap_pruning_ok:
    errors.append("cap_pruning")

# Emit the complete raw comparison record before any final assertions.
print(json.dumps({"schema":"qcap_sweep_raw_v1", "cases":records,
                  "errors_before_final_assertions":errors,
                  "true_q2_planted_partition": [list(block) for block in planted],
                  "true_q2_planted_membership": planted_membership,
                  "true_q2_local_languages_match_sidecar":target_languages_match,
                  "empty_positive_partition_count":len(empty_result["solutions"]),
                  "empty_positive_semantics_ok":empty_positive_ok,
                  "q1_cap_pruned_nodes":pruned["metrics"]["cap_pruned_nodes"],
                  "cap_pruning_ok":cap_pruning_ok},
                 ensure_ascii=False, sort_keys=True))

assert not errors, errors
assert all(records["actual_true_q2"][str(q)]["actual_partitions"] ==
           records["actual_true_q2"][str(q)]["expected_partitions"] for q in (2, 3))
assert records["actual_true_q2"]["1"]["actual_partitions"] == []
assert records["actual_true_q2"]["2"]["actual_partitions"] == [[["a"], ["b"]]]
assert records["three_projection_cap_violation"]["2"]["actual_partitions"] == []
assert records["three_projection_cap_violation"]["3"]["actual_partitions"] == [[["a"], ["b"]]]

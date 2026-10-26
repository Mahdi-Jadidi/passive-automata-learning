#!/usr/bin/env python3
"""Bounded adversarial audit for passive alphabet-partition claims.

Run from any directory with:
    python audit_partition.py

The audit is deterministic and exhaustive within the finite bounds recorded in
audit_results.json. It is a research check, not a production learner.
"""

from __future__ import annotations

import itertools
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Iterable


OUT = Path(__file__).resolve().parent
ALPHABET = "abc"


def words(alphabet: str, max_len: int) -> list[str]:
    return [
        "".join(chars)
        for n in range(max_len + 1)
        for chars in itertools.product(alphabet, repeat=n)
    ]


def canonical_partition(blocks: Iterable[Iterable[str]]) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted((tuple(sorted(block)) for block in blocks)))


def partitions_k(alphabet: str, k: int) -> list[tuple[tuple[str, ...], ...]]:
    """Enumerate unlabeled set partitions with exactly k nonempty blocks."""
    result: set[tuple[tuple[str, ...], ...]] = set()

    def rec(i: int, blocks: list[list[str]]) -> None:
        if i == len(alphabet):
            if len(blocks) == k:
                result.add(canonical_partition(blocks))
            return
        sym = alphabet[i]
        for j in range(len(blocks)):
            blocks[j].append(sym)
            rec(i + 1, blocks)
            blocks[j].pop()
        if len(blocks) < k:
            blocks.append([sym])
            rec(i + 1, blocks)
            blocks.pop()

    rec(0, [])
    return sorted(result)


def project(word: str, block: Iterable[str]) -> str:
    members = set(block)
    return "".join(ch for ch in word if ch in members)


def criterion_feasible(
    partition: tuple[tuple[str, ...], ...], positives: set[str], negatives: set[str]
) -> bool:
    """Finite feasibility criterion: each negative has a missing positive projection."""
    pos_projections = [
        {project(word, block) for word in positives} for block in partition
    ]
    return all(
        any(project(negative, block) not in pos_projections[i]
            for i, block in enumerate(partition))
        for negative in negatives
    )


def brute_boolean_feasible(
    partition: tuple[tuple[str, ...], ...], positives: set[str], negatives: set[str]
) -> tuple[bool, int, int]:
    """Independently enumerate local Boolean membership assignments.

    A variable is a local language decision for one observed projected word.
    Positive examples constrain every corresponding variable to True; each
    negative constrains at least one corresponding variable to False.
    """
    observed = sorted({
        (i, project(word, block))
        for i, block in enumerate(partition)
        for word in positives | negatives
    })
    index = {var: i for i, var in enumerate(observed)}
    pos_constraints = [
        [index[(i, project(word, block))] for i, block in enumerate(partition)]
        for word in positives
    ]
    neg_constraints = [
        [index[(i, project(word, block))] for i, block in enumerate(partition)]
        for word in negatives
    ]
    satisfying = 0
    for mask in range(1 << len(observed)):
        if any(any(((mask >> j) & 1) == 0 for j in row) for row in pos_constraints):
            continue
        if any(all(((mask >> j) & 1) == 1 for j in row) for row in neg_constraints):
            continue
        satisfying += 1
    return satisfying > 0, len(observed), satisfying


def local_words(block: Iterable[str], max_len: int) -> list[str]:
    return words("".join(sorted(block)), max_len)


def generator_accepts(
    word: str,
    partition: tuple[tuple[str, ...], ...],
    local_languages: tuple[frozenset[str], ...],
) -> bool:
    return all(project(word, block) in local_languages[i]
               for i, block in enumerate(partition))


def touching_both(word: str, partition: tuple[tuple[str, ...], ...]) -> bool:
    return all(any(ch in word for ch in block) for block in partition)


def spans_interleave(word: str, partition: tuple[tuple[str, ...], ...]) -> bool:
    spans = []
    for block in partition:
        positions = [i for i, ch in enumerate(word) if ch in block]
        if not positions:
            return False
        spans.append((min(positions), max(positions)))
    return max(lo for lo, _ in spans) < min(hi for _, hi in spans)


def graph_edges_from_complete_generator(
    alphabet: str,
    accepts,
    context_words: list[str],
) -> set[tuple[str, str]]:
    """Build just the two proposed families of sound must-link witnesses."""
    edges: set[tuple[str, str]] = set()
    ordered_pairs = [(a, b) for a in alphabet for b in alphabet if a != b]
    for a, b in ordered_pairs:
        for x in context_words:
            for y in context_words:
                # Commutation witness: xaby is positive, xbay is negative.
                if accepts(x + a + b + y) and not accepts(x + b + a + y):
                    edges.add(tuple(sorted((a, b))))
                # Rescue witness: xy+, xay-, and either xaby+ or xbay+.
                if accepts(x + y) and not accepts(x + a + y):
                    if accepts(x + a + b + y) or accepts(x + b + a + y):
                        edges.add(tuple(sorted((a, b))))
    return edges


def graph_components(alphabet: str, edges: set[tuple[str, str]]) -> tuple[tuple[str, ...], ...]:
    parent = {ch: ch for ch in alphabet}

    def find(ch: str) -> str:
        while parent[ch] != ch:
            parent[ch] = parent[parent[ch]]
            ch = parent[ch]
        return ch

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups: dict[str, list[str]] = {}
    for ch in alphabet:
        groups.setdefault(find(ch), []).append(ch)
    return canonical_partition(groups.values())


def refines(partition_a: tuple[tuple[str, ...], ...], partition_b: tuple[tuple[str, ...], ...]) -> bool:
    """True iff every block of A is contained in a block of B."""
    b_sets = [set(b) for b in partition_b]
    return all(any(set(a) <= b for b in b_sets) for a in partition_a)


def run_boolean_exhaustion() -> dict:
    alphabet = "ab"
    universe = words(alphabet, 2)
    partition = canonical_partition(({"a"}, {"b"}))
    count = 0
    variable_assignments = 0
    for statuses in itertools.product((0, 1, 2), repeat=len(universe)):
        positives = {w for w, s in zip(universe, statuses) if s == 1}
        negatives = {w for w, s in zip(universe, statuses) if s == 2}
        via_projection = criterion_feasible(partition, positives, negatives)
        via_boolean, nvars, nassignments = brute_boolean_feasible(partition, positives, negatives)
        assert via_projection == via_boolean
        count += 1
        variable_assignments += 1 << nvars
    return {
        "alphabet": alphabet,
        "words_length_at_most": 2,
        "universe_words": len(universe),
        "candidate_partition": [["a"], ["b"]],
        "labeled_samples_exhausted": count,
        "boolean_assignments_checked_total": variable_assignments,
        "result": "projection criterion agrees with independent Boolean assignment enumeration",
    }


def run_generator_exhaustion() -> dict:
    alphabet = ALPHABET
    candidate_partitions = partitions_k(alphabet, 2)
    all_words_to_6 = words(alphabet, 6)
    all_witness_contexts = words(alphabet, 2)
    sample_universe = [w for w in words(alphabet, 4)]
    model_count = 0
    edge_count = 0
    no_edge_models = 0
    exact_graph_models = 0
    full_sample_unique_models = 0
    unique_with_graph_incomplete = 0
    checked_context_pairs = len(all_witness_contexts) ** 2

    # Every block language ranges over all words up to length 2. Since these
    # are finite languages, each is regular and is supplied as a full generator.
    for true_partition in candidate_partitions:
        local_options = [
            [frozenset(s) for bits in range(1 << len(candidates))
             for s in [tuple(w for i, w in enumerate(candidates) if (bits >> i) & 1)]]
            for candidates in [local_words(block, 2) for block in true_partition]
        ]
        sample_words = [w for w in sample_universe if touching_both(w, true_partition)]
        for local_languages in itertools.product(*local_options):
            model_count += 1
            cache: dict[str, bool] = {}

            def accepts(word: str) -> bool:
                if word not in cache:
                    cache[word] = generator_accepts(word, true_partition, local_languages)
                return cache[word]

            positives = {w for w in sample_words if accepts(w)}
            negatives = set(sample_words) - positives
            assert criterion_feasible(true_partition, positives, negatives)

            feasible = [p for p in candidate_partitions
                        if criterion_feasible(p, positives, negatives)]
            # The sample is generated from the true partition, so it cannot
            # exclude its own partition.
            assert true_partition in feasible
            if len(feasible) == 1:
                full_sample_unique_models += 1

            # Explicitly populate the complete known generator labels through
            # all witness word lengths; no partial sample labels are used here.
            for word in all_words_to_6:
                accepts(word)
            edges = graph_edges_from_complete_generator(alphabet, accepts, all_witness_contexts)
            edge_count += len(edges)
            components = graph_components(alphabet, edges)
            assert refines(components, true_partition), (true_partition, edges, components)
            assert len(components) >= 2
            if len(edges) == 0:
                no_edge_models += 1
            if len(components) == 2:
                assert components == true_partition
                exact_graph_models += 1
            if len(feasible) == 1 and len(components) > 2:
                unique_with_graph_incomplete += 1

    return {
        "alphabet": alphabet,
        "known_k": 2,
        "true_partitions": len(candidate_partitions),
        "local_language_domain": "all subsets of block words of length at most 2 (finite regular languages)",
        "generator_pairs_exhausted": model_count,
        "sample_words": "all words of length at most 4 touching both true blocks; labels from complete generator",
        "witness_contexts": "all x,y over abc of length at most 2 each; labels queried from complete generator",
        "context_pairs_per_symbol_pair": checked_context_pairs,
        "witness_word_max_length": 6,
        "must_link_edges_found_total": edge_count,
        "models_with_no_witness_edges": no_edge_models,
        "models_with_r_equal_k_and_exact_graph_recovery": exact_graph_models,
        "models_where_full_bounded_sample_uniquely_feasible": full_sample_unique_models,
        "models_where_sample_is_unique_but_graph_has_r_greater_than_k": unique_with_graph_incomplete,
        "assertions": [
            "every inferred edge lies inside the true generator block",
            "graph components refine the true partition",
            "r >= k for every enumerated generator",
            "if r == k, graph components equal the true partition",
            "the true partition is feasible for every generated finite sample",
        ],
    }


def run_solver_crosscheck() -> dict:
    """Compare the theory solver to all local Boolean assignments on 81 samples."""
    if str(OUT) not in sys.path:
        sys.path.insert(0, str(OUT))
    import partition_solver  # type: ignore[import-not-found]

    alphabet = "abc"
    universe = words(alphabet, 1)
    all_partitions = partitions_k(alphabet, 2)
    samples = 0
    solver_calls = 0
    boolean_assignments = 0
    for statuses in itertools.product((0, 1, 2), repeat=len(universe)):
        positives = {w for w, s in zip(universe, statuses) if s == 1}
        negatives = {w for w, s in zip(universe, statuses) if s == 2}
        oracle = set()
        for p in all_partitions:
            feasible, nvars, _ = brute_boolean_feasible(p, positives, negatives)
            boolean_assignments += 1 << nvars
            if feasible:
                oracle.add(p)
        data = {"alphabet": list(alphabet),
                "positive": sorted(positives), "negative": sorted(negatives)}
        for prune in (True, False):
            result = partition_solver.solve(data, prune=prune)
            found = {
                canonical_partition(candidate["blocks"])
                for candidate in result["feasible_partitions"]
            }
            assert found == oracle, (data, prune, found, oracle)
            solver_calls += 1
        samples += 1

    example_checks = {}
    for path in sorted(OUT.glob("theory_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        pruned = partition_solver.solve(data, prune=True)
        exhaustive = partition_solver.solve(data, prune=False)
        pruned_set = {canonical_partition(x["blocks"]) for x in pruned["feasible_partitions"]}
        exhaustive_set = {canonical_partition(x["blocks"]) for x in exhaustive["feasible_partitions"]}
        assert pruned_set == exhaustive_set
        expected = {
            "theory_ambiguous.json": "ambiguous",
            "theory_empty_graph_unique.json": "unique",
            "theory_graph_recovered.json": "unique",
            "theory_structural_graph_gap.json": "unique",
        }.get(path.name)
        if expected is not None:
            assert pruned["status"] == expected, (path.name, pruned["status"])
        if path.name == "theory_structural_graph_gap.json":
            assert pruned["graph"]["edges"] == []
            assert pruned["graph"]["component_count"] == 3
            assert pruned_set == {canonical_partition(({"a"}, {"b", "c"}))}
        example_checks[path.name] = {
            "status": pruned["status"],
            "feasible_partition_count": len(pruned_set),
            "pruned_equals_unpruned": True,
            "graph_edges": len(pruned["graph"]["edges"]),
            "graph_components": pruned["graph"]["component_count"],
        }
    return {
        "alphabet": alphabet,
        "word_universe": universe,
        "labeled_samples_exhausted": samples,
        "candidate_partitions_per_sample": len(all_partitions),
        "solver_calls_pruned_and_unpruned": solver_calls,
        "independent_boolean_assignments_checked_total": boolean_assignments,
        "result": "partition_solver matches the independent Boolean assignment oracle, with and without graph pruning",
        "theory_json_example_checks": example_checks,
    }


def run_targeted_solver_cases() -> dict:
    """Exercise swap/rescue extraction, payloads, and an infeasible k=2 set."""
    if str(OUT) not in sys.path:
        sys.path.insert(0, str(OUT))
    import partition_solver  # type: ignore[import-not-found]

    cases = [
        {
            "name": "swap_forward",
            "alphabet": "abc",
            "partition": canonical_partition(({"a", "b"}, {"c"})),
            "languages": (frozenset({"ab"}), frozenset({"c"})),
            "positive": {"cab"}, "negative": {"cba"},
            "expected_rule": "swap",
        },
        {
            "name": "swap_reverse",
            "alphabet": "abc",
            "partition": canonical_partition(({"a", "b"}, {"c"})),
            "languages": (frozenset({"ba"}), frozenset({"c"})),
            "positive": {"cba"}, "negative": {"cab"},
            "expected_rule": "swap",
        },
        {
            "name": "rescue_parent_minimal",
            "alphabet": "abc",
            "partition": canonical_partition(({"a", "b"}, {"c"})),
            "languages": (frozenset({"", "ab"}), frozenset({"c"})),
            "positive": {"c", "cab"}, "negative": {"ca"},
            "expected_rule": "insertion_rescue",
        },
        {
            "name": "rescue_forward_contextual",
            "alphabet": "abc",
            "partition": canonical_partition(({"a", "b"}, {"c"})),
            "languages": (frozenset({"b", "abb"}), frozenset({"c"})),
            "positive": {"cb", "cabb"}, "negative": {"cab"},
            "expected_rule": "insertion_rescue",
        },
        {
            "name": "rescue_reverse_contextual",
            "alphabet": "abc",
            "partition": canonical_partition(({"a", "b"}, {"c"})),
            "languages": (frozenset({"b", "bab"}), frozenset({"c"})),
            "positive": {"cb", "cbab"}, "negative": {"cab"},
            "expected_rule": "insertion_rescue",
        },
    ]
    tested = {}
    boolean_assignments = 0
    for case in cases:
        alpha = case["alphabet"]
        partition = case["partition"]
        positives, negatives = case["positive"], case["negative"]
        assert all(generator_accepts(w, partition, case["languages"]) for w in positives)
        assert all(not generator_accepts(w, partition, case["languages"]) for w in negatives)
        assert all(touching_both(w, partition) for w in positives | negatives) or case["name"] == "rescue_parent_minimal"
        oracle = set()
        for candidate in partitions_k(alpha, 2):
            feasible, nvars, _ = brute_boolean_feasible(candidate, positives, negatives)
            boolean_assignments += 1 << nvars
            if feasible:
                oracle.add(candidate)
        input_data = {"alphabet": list(alpha), "positive": sorted(positives),
                      "negative": sorted(negatives)}
        pruned = partition_solver.solve(input_data, prune=True)
        exhaustive = partition_solver.solve(input_data, prune=False)
        found = {canonical_partition(x["blocks"]) for x in pruned["feasible_partitions"]}
        full = {canonical_partition(x["blocks"]) for x in exhaustive["feasible_partitions"]}
        assert found == full == oracle
        edge = next(e for e in pruned["graph"]["edges"]
                    if e["symbols"] == ["a", "b"])
        witness = edge["witness"]
        assert witness["rule"] == case["expected_rule"]
        if witness["rule"] == "swap":
            positive_word = witness["positive"][0]
            negative_word = witness["negative"]
            position = witness["position"]
            assert positive_word in positives and negative_word in negatives
            pair = positive_word[position:position + 2]
            swapped = positive_word[:position] + pair[1] + pair[0] + positive_word[position + 2:]
            assert set(pair) == {"a", "b"} and swapped == negative_word
        else:
            base, rescued = witness["positive"]
            negative_word = witness["negative"]
            position = witness["position"]
            assert base in positives and rescued in positives and negative_word in negatives
            assert base == negative_word[:position] + negative_word[position + 1:]
            other = "b" if negative_word[position] == "a" else "a"
            possible = {
                negative_word[:position] + other + negative_word[position:],
                negative_word[:position + 1] + other + negative_word[position + 1:],
            }
            assert rescued in possible
        tested[case["name"]] = {
            "rule": witness["rule"],
            "edge": edge["symbols"],
            "payload_verified": True,
            "feasible_partitions": len(found),
            "oracle_agrees_with_pruned_and_unpruned": True,
        }

    infeasible_data = {"alphabet": list("abc"),
                       "positive": ["ab", "ac", "bc"],
                       "negative": ["abc"]}
    infeasible_oracle = [
        p for p in partitions_k("abc", 2)
        if brute_boolean_feasible(p, set(infeasible_data["positive"]),
                                  set(infeasible_data["negative"]))[0]
    ]
    infeasible_result = partition_solver.solve(infeasible_data, prune=True)
    infeasible_full = partition_solver.solve(infeasible_data, prune=False)
    assert not infeasible_oracle
    assert infeasible_result["status"] == infeasible_full["status"] == "infeasible"
    assert not infeasible_result["feasible_partitions"]
    tested["no_feasible_two_block_partition"] = {
        "status": infeasible_result["status"],
        "independent_oracle_feasible_count": len(infeasible_oracle),
        "pruned_equals_unpruned": True,
    }
    return {
        "case_count": len(tested),
        "independent_boolean_assignments_checked": boolean_assignments,
        "cases": tested,
        "result": "forward/reverse swap and insertion-rescue witnesses are extracted with valid payloads; infeasible case agrees with oracle",
    }


def examples() -> dict:
    # (a) A genuine k=2 generator: parity couples a and b inside one block.
    parity_partition = canonical_partition(({"a", "b"}, {"c"}))

    def parity_accepts(word: str) -> bool:
        return (len(project(word, {"a", "b"})) % 2 == 0
                and project(word, {"c"}) == "c")

    parity_sample = {"abc": True, "bac": True, "ac": False}
    assert all(parity_accepts(w) == y for w, y in parity_sample.items())

    # (b,e) Same positive-only sample under two incomparable k=2 generators.
    sample_word = "adbc"
    p1 = canonical_partition(({"a", "b"}, {"c", "d"}))
    l1 = (frozenset({"ab"}), frozenset({"dc"}))
    p2 = canonical_partition(({"a", "c"}, {"b", "d"}))
    l2 = (frozenset({"ac"}), frozenset({"db"}))
    assert generator_accepts(sample_word, p1, l1)
    assert generator_accepts(sample_word, p2, l2)
    assert spans_interleave(sample_word, p1) and spans_interleave(sample_word, p2)
    distinguishers = {"P1_only": "abdc", "P2_only": "acdb"}
    assert generator_accepts(distinguishers["P1_only"], p1, l1)
    assert not generator_accepts(distinguishers["P1_only"], p2, l2)
    assert generator_accepts(distinguishers["P2_only"], p2, l2)
    assert not generator_accepts(distinguishers["P2_only"], p1, l1)

    # (c) Two incomparable maximally fine feasible partitions under k=2.
    p3_alphabet = "abc"
    p3_pos = {"", "abc"}
    p3_neg = {"a"}
    p3_all = partitions_k(p3_alphabet, 2)
    p3_feasible = [p for p in p3_all if criterion_feasible(p, p3_pos, p3_neg)]
    p3_boolean = {"|".join("".join(b) for b in p): brute_boolean_feasible(p, p3_pos, p3_neg)[0]
                  for p in p3_all}
    assert len(p3_feasible) == 2
    assert all(brute_boolean_feasible(p, p3_pos, p3_neg)[0] for p in p3_feasible)

    # (d) Pairwise merges do not help, but merging all three letters does.
    p4_pos = {"ab", "ac", "bc"}
    p4_neg = {"abc"}
    singleton = canonical_partition(({"a"}, {"b"}, {"c"}))
    pair_merges = {pair: canonical_partition((set(pair), set("abc") - set(pair)))
                   for pair in ("ab", "ac", "bc")}
    pair_merge_feasible = {pair: criterion_feasible(p, p4_pos, p4_neg)
                           for pair, p in pair_merges.items()}
    one_block = canonical_partition(({"a", "b", "c"},))
    assert not criterion_feasible(singleton, p4_pos, p4_neg)
    assert not any(pair_merge_feasible.values())
    assert criterion_feasible(one_block, p4_pos, p4_neg)

    # (g) Complete-generator graph can be incomplete while finite data is unique.
    incomplete_partition = canonical_partition(({"a"}, {"b", "c"}))
    incomplete_langs = (frozenset({"a"}), frozenset({"b", "c"}))
    incomplete_pos = {"ab", "ba", "ac", "ca"}
    incomplete_neg = {"abc"}
    assert all(generator_accepts(w, incomplete_partition, incomplete_langs)
               for w in incomplete_pos)
    assert all(not generator_accepts(w, incomplete_partition, incomplete_langs)
               for w in incomplete_neg)
    assert {w for w in words("abc", 6)
            if generator_accepts(w, incomplete_partition, incomplete_langs)} == incomplete_pos
    complete_accepts = lambda w: generator_accepts(w, incomplete_partition, incomplete_langs)
    complete_edges = graph_edges_from_complete_generator(
        "abc", complete_accepts, words("abc", 2))
    assert complete_edges == set()
    incomplete_feasible = [p for p in partitions_k("abc", 2)
                           if criterion_feasible(p, incomplete_pos, incomplete_neg)]
    assert incomplete_feasible == [incomplete_partition]
    incomplete_components = graph_components("abc", complete_edges)
    assert len(incomplete_components) == 3

    # (f) Same partition, but a sample-consistent negative allocation changes target.
    alloc_partition = canonical_partition(({"a"}, {"b"}))
    true_alloc_langs = (frozenset({"a"}), frozenset({"b", "bb"}))
    learned_alloc_langs = (frozenset({"a"}), frozenset({"b"}))
    alloc_pos, alloc_neg = {"ab"}, {"abab"}
    assert generator_accepts("ab", alloc_partition, true_alloc_langs)
    assert not generator_accepts("abab", alloc_partition, true_alloc_langs)
    assert generator_accepts("ab", alloc_partition, learned_alloc_langs)
    assert not generator_accepts("abab", alloc_partition, learned_alloc_langs)
    assert generator_accepts("abb", alloc_partition, true_alloc_langs)
    assert not generator_accepts("abb", alloc_partition, learned_alloc_langs)

    return {
        "scope_note": "Examples are split into finite-constraint illustrations and explicit generated-model counterexamples.",
        "a_same_label_swap_does_not_prove_independence": {
            "kind": "generated-model counterexample",
            "alphabet": "abc",
            "k": 2,
            "true_partition": [["a", "b"], ["c"]],
            "local_languages": {"ab": "all even-length words", "c": ["c"]},
            "sample_labels": parity_sample,
            "observation": "abc and bac are both positive after swapping a,b, yet parity couples a and b in one true block; ac is negative.",
        },
        "b_positive_only_nonidentifiability": {
            "kind": "two explicit generated models with positive-only data",
            "sample_positive_only": [sample_word],
            "known_k": 2,
            "model_1": {"partition": [list(x) for x in p1], "local_languages": {"ab": ["ab"], "cd": ["dc"]}},
            "model_2": {"partition": [list(x) for x in p2], "local_languages": {"ac": ["ac"], "bd": ["db"]}},
            "sample_word_interleaves_both_blocks_under_both_models": True,
        },
        "c_incomparable_maximally_fine_feasible_partitions": {
            "kind": "finite constraint example; not claimed generated by one known true partition",
            "alphabet": p3_alphabet,
            "known_k": 2,
            "positives": ["ε", "abc"],
            "negatives": ["a"],
            "feasible_partitions": [[list(block) for block in p] for p in p3_feasible],
            "all_two_block_partitions_boolean_feasibility": p3_boolean,
            "observation": "The two feasible partitions are incomparable and both are maximally fine among feasible k=2 partitions.",
        },
        "d_pairwise_merge_blind_spot": {
            "kind": "finite constraint example only; not claimed generated by a known-k=2 target",
            "base": {
                "alphabet": "abc",
                "positives": ["ab", "ac", "bc"],
                "negatives": ["abc"],
                "singleton_partition_feasible": False,
                "pair_merge_feasibility": pair_merge_feasible,
                "all_three_merged_feasible": criterion_feasible(one_block, p4_pos, p4_neg),
                "note": "Under fixed k=2 on abc no partition is feasible; the one-block merge is only a finite-constraint illustration.",
            },
        },
        "e_sample_consistency_not_target_or_partition_recovery": {
            "kind": "same generated models as the positive-only example",
            "sample_positive_only": [sample_word],
            "distinguishing_words": {
                "abdc": {"model_1": True, "model_2": False},
                "acdb": {"model_1": False, "model_2": True},
            },
            "observation": "The sample is consistent with both partitions and both global regular targets, which disagree off-sample.",
        },
        "f_negative_allocation_can_change_true_target": {
            "kind": "generated-model counterexample plus sample-consistent alternate local assignment",
            "alphabet": "ab",
            "true_partition": [["a"], ["b"]],
            "true_local_languages": {"a": ["a"], "b": ["b", "bb"]},
            "sample_positives": sorted(alloc_pos),
            "sample_negatives": sorted(alloc_neg),
            "alternate_local_languages": {"a": ["a"], "b": ["b"]},
            "distinguishing_word": {"word": "abb", "true_target": True, "alternate_target": False},
            "observation": "The negative abab is rejected by the true a-component via projection aa, but a learner can also reject it through b by excluding unseen projection bb; both hypotheses fit the sample.",
        },
        "g_unique_sample_with_incomplete_complete_generator_graph": {
            "kind": "generated-model counterexample; labels and graph witnesses use the complete target",
            "alphabet": "abc",
            "known_k": 2,
            "true_partition": [["a"], ["b", "c"]],
            "local_languages": {"a": ["a"], "bc": ["b", "c"]},
            "complete_target_positive_language": sorted(incomplete_pos),
            "sample_positives": sorted(incomplete_pos),
            "sample_negatives": sorted(incomplete_neg),
            "every_sample_word_touches_both_true_blocks": True,
            "complete_generator_graph_edges": [list(e) for e in sorted(complete_edges)],
            "graph_components": [list(block) for block in incomplete_components],
            "r": len(incomplete_components),
            "unique_feasible_k2_partition": [list(block) for block in incomplete_feasible[0]],
            "why_graph_is_empty": "The only positive words have length 2 and every adjacent swap partner is also positive. Rescue requires xy=epsilon to be positive, but epsilon is rejected; any longer rescued positive is outside the finite target.",
            "observation": "The complete-generator graph has r=3>k, while the labeled sample uniquely identifies the true k=2 partition.",
        },
    }


def main() -> None:
    started = time.perf_counter()
    boolean = run_boolean_exhaustion()
    solver_check = run_solver_crosscheck()
    targeted_solver = run_targeted_solver_cases()
    generators = run_generator_exhaustion()
    example_data = examples()
    elapsed_seconds = time.perf_counter() - started
    solver_path = OUT / "partition_solver.py"
    audit_path = Path(__file__).resolve()
    results = {
        "audit_name": "bounded_adversarial_alphabet_partition_audit",
        "date": "2026-10-26",
        "seed": None,
        "seed_note": "No randomness; every reported finite range is exhaustively enumerated.",
        "command": "python audit_partition.py",
        "executed_command": f'"{sys.executable}" audit_partition.py',
        "python_version": sys.version.split()[0],
        "elapsed_seconds": round(elapsed_seconds, 3),
        "sha256": {
            "audit_partition.py": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
            "partition_solver.py": hashlib.sha256(solver_path.read_bytes()).hexdigest(),
        },
        "scope": {
            "finite_feasibility": "all 3^7 labeled subsets of the 7 words over {a,b} of length at most 2; candidate partition {{a},{b}}",
            "generated_languages": "all 2-block partitions of {a,b,c}; for each block, all finite languages that are subsets of block words of length at most 2",
            "generated_sample": "all words over {a,b,c} of length at most 4 that touch both true blocks, labeled by the complete generator",
            "witness_check": "complete generator labels on words through length 6; all context words x,y over {a,b,c} each of length at most 2",
        },
        "finite_feasibility_boolean_exhaustion": boolean,
        "theory_solver_independent_crosscheck": solver_check,
        "targeted_solver_witness_cases": targeted_solver,
        "known_generator_exhaustion": generators,
        "claim_limitations": [
            "A finite sample can be feasible under multiple incomparable partitions and multiple different target languages.",
            "Pairwise projection/merge checks can miss a constraint that appears only when three letters form one block.",
            "Graph soundness follows from the witness theorem; this bounded enumeration is corroboration, not the general proof.",
            "r=k exact recovery is conditional on a true noise-free k-block target in the model class and correctly labeled witnesses for every graph edge used; complete-generator labels are used only in the generator audit, not required by the solver theorem.",
        ],
    }
    (OUT / "audit_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "audit_examples.json").write_text(json.dumps(example_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "finite_feasibility": boolean,
        "targeted_solver_witness_cases": targeted_solver,
        "known_generator_exhaustion": generators,
        "examples": sorted(example_data),
        "output_dir": str(OUT),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

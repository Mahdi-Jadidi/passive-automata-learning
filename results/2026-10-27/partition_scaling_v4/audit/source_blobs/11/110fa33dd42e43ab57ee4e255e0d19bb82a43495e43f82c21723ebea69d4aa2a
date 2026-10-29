"""Recover a class-conditional partition from connected positive opposition.

No alphabet cap, no target/oracle queries and no general-regular uniqueness claim.
Disconnected evidence is deliberately not enumerated: insufficient_coverage.
Malformed input/unsupported parameter values raise ValueError for the root CLI.
"""
from __future__ import annotations

from collections import deque
import math
import time


class _Interrupted(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Interrupted


def _project(word, block, deadline):
    out = []
    for i, symbol in enumerate(word):
        if i & 1023 == 0:
            _check(deadline)
        if symbol in block:
            out.append(symbol)
    return "".join(out)


def _validate(data, deadline):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    raw = data.get("alphabet")
    if (not isinstance(raw, list) or len(raw) < 2
            or any(not isinstance(a, str) or len(a) != 1 for a in raw)
            or len(set(raw)) != len(raw)):
        raise ValueError("alphabet must list at least two distinct one-character strings")
    _check(deadline)
    alphabet = sorted(raw)
    allowed = set(alphabet)
    classes = []
    for key in ("positive", "negative"):
        values = data.get(key)
        if not isinstance(values, list):
            raise ValueError(f"{key} must be a list of strings")
        for word in values:
            _check(deadline)
            if not isinstance(word, str):
                raise ValueError(f"{key} must be a list of strings")
            for i, symbol in enumerate(word):
                if i & 1023 == 0:
                    _check(deadline)
                if symbol not in allowed:
                    raise ValueError(f"{key} contains a symbol outside alphabet")
        classes.append(sorted(set(values)))
    if set(classes[0]).intersection(classes[1]):
        raise ValueError("a word cannot have both labels")
    return alphabet, classes[0], classes[1]


def _counts(word, deadline):
    counts = {}
    for i, symbol in enumerate(word):
        if i & 1023 == 0:
            _check(deadline)
        counts[symbol] = counts.get(symbol, 0) + 1
    return counts


def _odd_cycle(a, b, parent):
    path_a, path_b = [], []
    while a != -1:
        path_a.append(a)
        a = parent[a]
    while b != -1:
        path_b.append(b)
        b = parent[b]
    positions = {node: i for i, node in enumerate(path_a)}
    for j, node in enumerate(path_b):
        if node in positions:
            # Tree path a--LCA--b followed by the conflicting edge b--a.
            path = path_a[:positions[node] + 1] + list(reversed(path_b[:j]))
            return path + [path[0]]
    raise AssertionError("conflict endpoints must share a BFS root")


def solve(data, *, deadline=None, max_solutions=1):
    """Return a unique fixed-word partition certificate, or an explicit limitation.

    max_solutions accepts a positive int or None. Since this route only emits a
    structurally certified unique answer, every accepted limit is respected;
    disconnected cases are not enumerated, even when None requests all answers.
    """
    if (max_solutions is not None
            and (isinstance(max_solutions, bool) or not isinstance(max_solutions, int)
                 or max_solutions < 1)):
        raise ValueError("max_solutions must be a positive integer or None")
    if deadline is not None:
        if isinstance(deadline, bool) or not isinstance(deadline, (int, float)):
            raise ValueError("deadline must be an absolute finite perf_counter value or None")
        try:
            finite = math.isfinite(deadline)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError("deadline must be finite")
    started = time.perf_counter()
    solutions = []
    graph = {"symbols": [], "edges": [], "edge_positive_indices": [],
             "components": [], "colors": [], "construction_complete": False}
    metrics = {"pair_tests": 0, "pair_projection_calls": 0,
               "positive_count_checks": 0, "positive_projection_checks": 0,
               "negative_checks": 0, "candidate_checks": 0}
    assumptions = ["exactly_two_nonempty_disjoint_alphabet_blocks",
                   "each_local_language_is_a_singleton_word_language",
                   "positives_are_complete_traces_not_prefixes",
                   "fixed_noise_free_labels",
                   "connected_positive_opposition_is_a_sufficient_coverage_condition"]

    def result(status, *, reason, exhausted=False, decision=False,
               uniqueness="unknown", certificate=None):
        if status != "incomplete":
            _check(deadline)
        return {"method": "fixed-word", "model_class": "fixed_word_product",
                "status": status, "solutions": solutions,
                "search_exhausted": exhausted, "decision_complete": decision,
                "uniqueness": uniqueness,
                "uniqueness_scope": "unordered_two_nonempty_block_partitions_within_fixed_word_product_class",
                "assumptions": assumptions, "reason": reason,
                "metrics": {**metrics, "provider_seconds": time.perf_counter() - started},
                "graph": graph, "certificate": certificate,
                "limitations": ["No uniqueness claim for unrestricted regular factors.",
                                "Disconnected opposition returns insufficient_coverage, not general infeasibility.",
                                "Accepted max_solutions modes certify at most one answer; no disconnected enumeration."]}

    try:
        _check(deadline)
        alphabet, positive, negative = _validate(data, deadline)
        metrics.update(alphabet_size=len(alphabet), positive_count=len(positive),
                       negative_count=len(negative))
        graph["symbols"] = alphabet
        if not positive:
            return result("insufficient_coverage", reason="no_positive_word_to_determine_local_factors")
        reference = positive[0]
        expected = _counts(reference, deadline)
        for index, word in enumerate(positive):
            _check(deadline)
            actual = _counts(word, deadline)
            metrics["positive_count_checks"] += 1
            if actual != expected:
                symbol = next(a for a in alphabet if actual.get(a, 0) != expected.get(a, 0))
                return result("assumption_violation", reason="positive_symbol_count_inconsistency",
                              exhausted=True, decision=True,
                              certificate={"kind": "count_inconsistency", "symbol": symbol,
                                           "positive_indices": [0, index],
                                           "counts": [expected.get(symbol, 0), actual.get(symbol, 0)]})
        graph["absent_symbols"] = [a for a in alphabet if a not in expected]
        size = len(alphabet)
        adjacency = [[] for _ in alphabet]
        for i in range(size):
            for j in range(i + 1, size):
                _check(deadline)
                metrics["pair_tests"] += 1
                pair = {alphabet[i], alphabet[j]}
                projected = _project(reference, pair, deadline)
                metrics["pair_projection_calls"] += 1
                for index in range(1, len(positive)):
                    _check(deadline)
                    variation = _project(positive[index], pair, deadline)
                    metrics["pair_projection_calls"] += 1
                    if variation != projected:
                        graph["edges"].append([alphabet[i], alphabet[j]])
                        graph["edge_positive_indices"].append(index)
                        adjacency[i].append(j)
                        adjacency[j].append(i)
                        break
        graph["construction_complete"] = True
        graph["reference_positive_index"] = 0
        graph["positive_order"] = "sorted unique input words"
        colors = [-1] * size
        parent = [-1] * size
        graph["colors"] = colors
        for root in range(size):
            _check(deadline)
            if colors[root] != -1:
                continue
            colors[root] = 0
            component = []
            graph["components"].append(component)
            queue = deque([root])
            while queue:
                _check(deadline)
                current = queue.popleft()
                component.append(alphabet[current])
                for other in adjacency[current]:
                    _check(deadline)
                    if colors[other] == -1:
                        colors[other] = 1 - colors[current]
                        parent[other] = current
                        queue.append(other)
                    elif colors[other] == colors[current]:
                        cycle = _odd_cycle(current, other, parent)
                        return result("assumption_violation", reason="opposition_graph_has_odd_cycle",
                                      exhausted=True, decision=True,
                                      certificate={"kind": "odd_opposition_cycle",
                                                   "symbols": [alphabet[k] for k in cycle]})
            component.sort()
        metrics["opposition_edges"] = len(graph["edges"])
        metrics["opposition_components"] = len(graph["components"])
        graph["coloring_complete"] = True
        if len(graph["components"]) != 1:
            return result("insufficient_coverage", reason="opposition_graph_is_disconnected",
                          certificate={"kind": "unmet_sufficient_condition",
                                       "component_count": len(graph["components"]),
                                       "does_not_assert_multiple_solutions": True})
        blocks = [{a for a, c in zip(alphabet, colors) if c == side} for side in (0, 1)]
        if not all(blocks):
            raise AssertionError("a connected graph on at least two vertices has both colors")
        factors = [_project(reference, block, deadline) for block in blocks]
        metrics["candidate_checks"] += 1
        positive_conflicts = []
        for index, word in enumerate(positive):
            _check(deadline)
            images = [_project(word, block, deadline) for block in blocks]
            metrics["positive_projection_checks"] += 1
            if images != factors:
                positive_conflicts.append(index)
        witnesses, negative_conflicts = [], []
        for word in negative:
            _check(deadline)
            images = [_project(word, block, deadline) for block in blocks]
            unseen = [s for s in (0, 1) if images[s] != factors[s]]
            metrics["negative_checks"] += 1
            if not unseen:
                negative_conflicts.append(word)
            else:
                side = unseen[0]
                witnesses.append({"negative": word, "block_index": side,
                                  "projection": images[side], "all_unseen_block_indices": unseen})
        _check(deadline)
        certificate = {"kind": "connected_bipartite_opposition",
                       "unique_positive_partition_up_to_swapping_sides": True,
                       "local_words": factors,
                       "all_positive_projections_checked": True,
                       "all_negative_projections_checked": True}
        if positive_conflicts or negative_conflicts:
            certificate.update(positive_conflict_indices=positive_conflicts,
                               accepted_negative_conflicts=negative_conflicts)
            return result("assumption_violation", reason="unique_structural_candidate_violates_labels",
                          exhausted=True, decision=True, certificate=certificate)
        solutions.append({"blocks": [sorted(block) for block in blocks],
                          "positive_projection_languages": [[word] for word in factors],
                          "negative_witnesses": witnesses, "local_words": factors})
        _check(deadline)
        return result("found", reason="unique_partition_certified_within_fixed_word_class",
                      exhausted=True, decision=True, uniqueness="unique", certificate=certificate)
    except (_Interrupted, KeyboardInterrupt):
        return result("incomplete", reason="deadline_or_interruption",
                      decision=bool(solutions))

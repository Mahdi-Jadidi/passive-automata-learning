"""Exact lazy enumeration for the fixed C002 two-block model."""
from __future__ import annotations

import time

from common.engine import SearchInterrupted, check_deadline, find_model
from common.helpers import (distinguishers, graph_constraints, partition_record,
                            project, result_from_records, validate, witness_graph)


def side_distinguishes(family, side):
    return ("or", tuple(("and", tuple(("lit", i, side) for i in subset))
                        for subset in family))


def offending_matches(alphabet, positive, negative, assignment, *, deadline=None):
    """Lex-first offending negative and lex-first positive match on each side."""
    blocks = [{a for a, owner in zip(alphabet, assignment) if owner == side}
              for side in (0, 1)]
    matches = [{}, {}]
    for side in (0, 1):
        for p in positive:
            check_deadline(deadline)
            matches[side].setdefault(project(p, blocks[side]), p)
    for n in negative:
        check_deadline(deadline)
        projected = [project(n, block) for block in blocks]
        if all(projected[s] in matches[s] for s in (0, 1)):
            return n, matches[0][projected[0]], matches[1][projected[1]]
    return None


def solve(data, *, deadline=None):
    started = time.perf_counter()
    alphabet, positive, negative = validate(data)
    records, constraints = [], []
    components, edges = [[a] for a in alphabet], []
    stats = {name: 0 for name in ("nodes_visited", "complete_assignments",
                                  "pruned_nodes", "constraint_evaluations")}
    metrics = {"search_calls": 0, "lazy_cuts": 0, "answer_blockers": 0,
               "distinguisher_calls": 0, "distinguisher_cache_hits": 0,
               "distinguisher_terms": 0, "direct_record_checks": 0,
               "preprocessing_seconds": 0.0, "separation_seconds": 0.0,
               "cut_generation_seconds": 0.0}
    families, cuts = {}, set()
    complete = True
    try:
        check_deadline(deadline)
        components, edges = witness_graph(alphabet, positive, negative)
        check_deadline(deadline)
        constraints.extend(graph_constraints(alphabet, edges))
        metrics["preprocessing_seconds"] = time.perf_counter() - started
        while True:
            check_deadline(deadline)
            metrics["search_calls"] += 1
            assignment = find_model(len(alphabet), constraints,
                                    deadline=deadline, stats=stats)
            if assignment is None:
                break
            separation_start = time.perf_counter()
            check_deadline(deadline)
            record = partition_record(alphabet, positive, negative, assignment)
            metrics["direct_record_checks"] += 1
            if record is not None:
                records.append(record)
                constraints.append(("or", tuple(("lit", i, 1 - side)
                                                for i, side in enumerate(assignment))))
                metrics["answer_blockers"] += 1
                metrics["separation_seconds"] += time.perf_counter() - separation_start
                continue
            offending = offending_matches(alphabet, positive, negative, assignment,
                                          deadline=deadline)
            if offending is None:
                raise AssertionError("direct criterion and separator disagree")
            metrics["separation_seconds"] += time.perf_counter() - separation_start
            cut_start = time.perf_counter()
            n, p0, p1 = offending
            terms = []
            for side, p in enumerate((p0, p1)):
                check_deadline(deadline)
                key = (n, p)
                if key not in families:
                    families[key] = distinguishers(alphabet, n, p)
                    metrics["distinguisher_calls"] += 1
                    metrics["distinguisher_terms"] += len(families[key])
                else:
                    metrics["distinguisher_cache_hits"] += 1
                terms.append(side_distinguishes(families[key], side))
            cut = ("or", tuple(terms))
            if cut in cuts:
                raise AssertionError("an existing cut failed to exclude its violating model")
            cuts.add(cut)
            constraints.append(cut)
            metrics["lazy_cuts"] += 1
            metrics["cut_generation_seconds"] += time.perf_counter() - cut_start
    except (SearchInterrupted, KeyboardInterrupt):
        complete = False
    if not metrics["preprocessing_seconds"]:
        metrics["preprocessing_seconds"] = time.perf_counter() - started
    metrics["constraints_stored"] = len(constraints)
    metrics["provider_seconds"] = time.perf_counter() - started
    metrics["search_restarts"] = max(0, metrics["search_calls"] - 1)
    return result_from_records(alphabet, positive, negative, records,
                               method="lazy", components=components, edges=edges,
                               stats=stats, complete=complete, metrics=metrics)

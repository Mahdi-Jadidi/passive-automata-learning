"""Exact eager constraints for C002. Requires the reviewed shared candidates."""
from __future__ import annotations

import time

from common.engine import SearchInterrupted, check_deadline, iter_models
from common.helpers import (distinguishers, graph_constraints, partition_record,
                            result_from_records, validate, witness_graph)


def side_distinguishes(family, side):
    return ("or", tuple(("and", tuple(("lit", i, side) for i in subset))
                         for subset in family))


def solve(data, *, deadline=None):
    started = time.perf_counter()
    alphabet, positive, negative = validate(data)
    records, constraints = [], []
    components, edges = [[a] for a in alphabet], []
    stats = {"nodes_visited": 0, "complete_assignments": 0,
             "pruned_nodes": 0, "constraint_evaluations": 0}
    metrics = {"negative_constraints": 0, "distinguisher_calls": 0,
               "distinguisher_terms": 0, "direct_record_checks": 0,
               "preprocessing_seconds": 0.0}
    complete = True
    try:
        check_deadline(deadline)
        components, edges = witness_graph(alphabet, positive, negative)
        check_deadline(deadline)
        constraints.extend(graph_constraints(alphabet, edges))
        for n in negative:
            side_terms = [[], []]
            for p in positive:
                check_deadline(deadline)
                family = distinguishers(alphabet, n, p)
                metrics["distinguisher_calls"] += 1
                metrics["distinguisher_terms"] += len(family)
                for side in (0, 1):
                    side_terms[side].append(side_distinguishes(family, side))
            constraints.append(("or", tuple(("and", tuple(terms))
                                              for terms in side_terms)))
            metrics["negative_constraints"] += 1
        metrics["preprocessing_seconds"] = time.perf_counter() - started
        for assignment in iter_models(len(alphabet), constraints,
                                      deadline=deadline, stats=stats):
            check_deadline(deadline)
            record = partition_record(alphabet, positive, negative, assignment)
            metrics["direct_record_checks"] += 1
            if record is None:
                raise AssertionError("eager formula emitted an infeasible partition")
            records.append(record)
    except (SearchInterrupted, KeyboardInterrupt):
        complete = False
    if not metrics["preprocessing_seconds"]:
        metrics["preprocessing_seconds"] = time.perf_counter() - started
    metrics["constraints_stored"] = len(constraints)
    metrics["provider_seconds"] = time.perf_counter() - started
    return result_from_records(alphabet, positive, negative, records,
                               method="eager", components=components, edges=edges,
                               stats=stats, complete=complete, metrics=metrics)

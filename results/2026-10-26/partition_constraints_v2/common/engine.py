"""C002 shared ownership-search candidate. Standard library only.

Expressions: ('const', bool), ('lit', index, side),
('and', tuple(children)), ('or', tuple(children)).
"""
from __future__ import annotations

import time


class SearchInterrupted(Exception):
    """The declared cooperative deadline has expired."""


def check_deadline(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchInterrupted("search deadline expired")


def eval_expr(expr, assignment):
    """Return True, False, or None for a partial -1/0/1 assignment."""
    kind = expr[0]
    if kind == "const":
        return bool(expr[1])
    if kind == "lit":
        value = assignment[expr[1]]
        return None if value == -1 else value == expr[2]
    if kind not in ("and", "or"):
        raise ValueError(f"unknown expression kind: {kind!r}")
    unknown = False
    for child in expr[1]:
        value = eval_expr(child, assignment)
        if kind == "and" and value is False:
            return False
        if kind == "or" and value is True:
            return True
        unknown = unknown or value is None
    if unknown:
        return None
    return kind == "and"


def iter_models(num_vars, constraints, *, deadline=None, stats=None):
    """Enumerate canonical nonempty bipartitions in lexicographic order.

    Constraints are snapshotted when iteration starts. Call find_model again
    after adding lazy cuts. Counter dictionaries accumulate across calls.
    complete_assignments counts nonempty full assignments, including rejected
    ones; the forbidden all-zero ownership is excluded from that counter.
    """
    if not isinstance(num_vars, int) or isinstance(num_vars, bool) or num_vars < 2:
        raise ValueError("num_vars must be an integer >= 2")
    if stats is None:
        stats = {}
    for name in ("nodes_visited", "complete_assignments", "pruned_nodes",
                 "constraint_evaluations"):
        stats.setdefault(name, 0)
    fixed_constraints = tuple(constraints)
    assignment = [0] + [-1] * (num_vars - 1)

    def visit(index):
        check_deadline(deadline)
        stats["nodes_visited"] += 1
        full = index == num_vars
        if full and 1 not in assignment:
            stats["pruned_nodes"] += 1
            return
        if full:
            stats["complete_assignments"] += 1
        for constraint in fixed_constraints:
            check_deadline(deadline)
            stats["constraint_evaluations"] += 1
            if eval_expr(constraint, assignment) is False:
                stats["pruned_nodes"] += 1
                return
        if full:
            yield tuple(assignment)
            return
        for side in (0, 1):
            assignment[index] = side
            yield from visit(index + 1)
        assignment[index] = -1

    yield from visit(1)


def find_model(num_vars, constraints, *, deadline=None, stats=None):
    iterator = iter_models(num_vars, constraints, deadline=deadline, stats=stats)
    try:
        return next(iterator, None)
    finally:
        iterator.close()

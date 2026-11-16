"""Exhaustively compare SAT cuts with a direct set-of-classes predicate."""
import itertools
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '2026-11-14' / 'sat_candidate_v37' / 'vendor'))
from pysat.solvers import Solver
from master import Master


def blocks(q, pairs, bits):
    # Independent graph components; validity also checks every pair agrees.
    edges = {p for p, bit in zip(pairs, bits) if bit}
    groups = []
    unseen = set(range(q))
    while unseen:
        component = {min(unseen)}
        while True:
            grown = component | {v for a, b in edges for v in (a, b)
                                 if a in component or b in component}
            if grown == component:
                break
            component = grown
        groups.append(component)
        unseen -= component
    valid = all(any(a in g and b in g for g in groups) == bit
                for (a, b), bit in zip(pairs, bits))
    return valid, groups


def main():
    for q in range(5):
        base = Master(q)
        pairs = list(base.pairs)
        assignments = []
        for bits in itertools.product((False, True), repeat=len(pairs)):
            valid, groups = blocks(q, pairs, bits)
            assumptions = [base.pairs[p] if bit else -base.pairs[p] for p, bit in zip(pairs, bits)]
            assignments.append((assumptions, valid, groups))
            for t in range(q + 2):
                with Solver(bootstrap_with=base.threshold(t)) as solver:
                    actual = solver.solve(assumptions=assumptions)
                    assert actual == (valid and len(groups) >= t), (q, bits, t)
                    if actual:
                        assert base.decode(solver.get_model()) == [sorted(g) for g in groups]
        masks = list(range(1, (1 << q) - 1))
        for selection in range(1 << len(masks)):
            cover = [u for i, u in enumerate(masks) if selection & (1 << i)]
            master = Master(q)
            before = len(master.clauses)
            added = master.add_cover(cover)
            assert added == master.clauses[before:]
            with Solver(bootstrap_with=master.clauses) as solver:
                for assumptions, valid, groups in assignments:
                    expected = valid and any(all(any(not (u & (1 << a)) for a in g)
                                                 for u in cover) for g in groups)
                    assert solver.solve(assumptions=assumptions) == expected, (q, cover, assumptions)
        print(f'q={q}: {len(assignments)} pair assignments, {1 << len(masks)} covers passed', flush=True)
    # Input validation and normalization are deterministic.
    for bad in (0, 7, -1, True):
        try:
            Master(3).add_cover([bad])
        except ValueError:
            pass
        else:
            raise AssertionError(bad)
    a, b = Master(3), Master(3)
    assert a.add_cover([3, 1, 3]) == b.add_cover([1, 3])
    print('All master tests passed.')


if __name__ == '__main__':
    main()


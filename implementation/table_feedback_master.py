"""Exact outer search for the unbounded, complete coverage-table contract.

The injected teacher is bound to D. It receives (blocks, tick) and returns
{'status': 'ACCEPT' | 'REJECT' | 'INCOMPLETE'}. On REJECT it must also return
'tables', keyed by tuples of symbols in the proposed block order. Every row
has one bit per entry of D['negative'], in its original order.
"""

from pathlib import Path
import sys
from threading import Timer


_V45 = Path(__file__).resolve().parents[1] / 'results/2026-11-16/interactive_teacher_v45'
sys.path.append(str(_V45))
from master import Master
from spec import Exhausted, Invalid, budget, direct_reject, normalize, partition_masks, response
from verify import check_drup


def _query(solver, threshold, tick):
    if threshold is False:
        return False
    tick()
    seconds = tick.remaining()
    timer = None if seconds is None else Timer(seconds, solver.interrupt)
    if timer is not None:
        timer.daemon = True
        timer.start()
    try:
        answer = solver.solve_limited(
            assumptions=[] if threshold is True else [threshold], expect_interrupt=True
        )
        tick()
        if answer is None:
            raise Exhausted()
        return answer
    finally:
        if timer is not None:
            timer.cancel()
            timer.join()


def _maximal_regions(regions, tick):
    maximal = []
    for region in sorted(regions, key=int.bit_count, reverse=True):
        tick()
        if not any(region & other == region for other in maximal):
            maximal.append(region)
    return sorted(maximal)


def _learn_zero_regions(regions, blocks, masks, tables, tick):
    if set(tables) != {tuple(block) for block in blocks}:
        raise ValueError('teacher must return one complete table per proposed block')
    width = len(regions)
    covered = [False] * width
    for block, mask in zip(blocks, masks):
        rows = tables[tuple(block)]
        if not rows:
            raise ValueError('teacher table is empty')
        columns = [False] * width
        for row in rows:
            tick()
            if len(row) != width or any(type(bit) not in (int, bool) or bit not in (0, 1) for bit in row):
                raise ValueError('teacher row must contain one bit per negative trace')
            columns = [old or bit for old, bit in zip(columns, row)]
        if columns not in rows and tuple(columns) not in rows:
            raise ValueError('teacher table lacks the simultaneous coverage row')
        for i, can_cover in enumerate(columns):
            if can_cover:
                covered[i] = True
            else:
                regions[i].add(mask)
    if all(covered):
        raise ValueError('teacher rejection contradicts its coverage tables')


def _encode(q, regions, tick):
    master = Master(q, tick)
    full = (1 << q) - 1
    for row in regions:
        tick()
        if not q or full in row:
            master.clauses.append([])
        elif row:
            master.add_cover(row)
    return master


def solve_optimal(D, teacher, limits=None):
    """Return one optimum and a DRUP upper-bound certificate, or INCOMPLETE."""
    from pysolvers import error as SatError
    from pysat.solvers import Solver

    try:
        tick = budget(limits)
        Sigma, _, _ = normalize(D)
        tick()
        q = len(Sigma)
        learned = [set() for _ in D['negative']]
        blocks = [[symbol] for symbol in Sigma]
        upper = q
        while True:
            tick()
            verdict = teacher(blocks, tick)
            tick()
            if verdict['status'] == 'INCOMPLETE':
                return response('INCOMPLETE')
            if verdict['status'] == 'ACCEPT':
                status, threshold = 'OPTIMAL', len(blocks) + 1
                break
            if verdict['status'] != 'REJECT':
                raise ValueError('unknown teacher status')
            _learn_zero_regions(
                learned, blocks, partition_masks(Sigma, blocks), verdict['tables'], tick
            )
            regions = [_maximal_regions(row, tick) for row in learned]
            master = _encode(q, regions, tick)
            with Solver(name='g3', bootstrap_with=master.clauses) as solver:
                lo, hi = 0, upper
                model = None
                while lo <= hi:
                    mid = (lo + hi + 1) // 2
                    if _query(solver, master.thresholds[mid], tick):
                        model = master.decode(solver.get_model())
                        lo = len(model) + 1
                    else:
                        hi = mid - 1
            if model is None:
                status, threshold, blocks = 'INFEASIBLE', 0, None
                break
            upper = len(model)
            blocks = [[Sigma[j] for j in block] for block in model]

        regions = [_maximal_regions(row, tick) for row in learned]
        master = _encode(q, regions, tick)
        proof = []
        if not check_drup(master, threshold, proof, tick):
            with Solver(name='g3', with_proof=True) as solver:
                # Enable proof tracing before adding the refutation target.
                for clause in master.threshold(threshold):
                    tick()
                    solver.add_clause(clause)
                if _query(solver, True, tick):
                    raise RuntimeError('master failed to prove the upper bound')
                proof = solver.get_proof()
        certificate = {'type': 'table_feedback_drup', 'zero_regions': regions, 'proof': proof}
        result = response(status, blocks, None if blocks is None else len(blocks), certificate)
        if not _verify(D, Sigma, result, tick):
            raise ValueError('teacher feedback failed certificate verification')
        return result
    except Invalid:
        return response('INVALID_INPUT')
    except (Exhausted, MemoryError, RecursionError, KeyboardInterrupt, SatError):
        return response('INCOMPLETE')


def _verify(D, Sigma, result, tick):
    S_plus, S_minus = D['positive'], D['negative']
    q = len(Sigma)
    status = result['status']
    size = result['max_devices']
    if status == 'OPTIMAL':
        masks = partition_masks(Sigma, result['blocks'])
        if type(size) is not int or size != len(masks):
            return False
        covered = 0
        for mask in masks:
            tick()
            covered |= direct_reject(Sigma, S_plus, S_minus, mask)
        if covered != (1 << len(S_minus)) - 1:
            return False
        threshold = size + 1
    elif status == 'INFEASIBLE' and size is None and result['blocks'] is None:
        threshold = 0
    else:
        return False
    cert = result['certificate']
    if (type(cert) is not dict or set(cert) != {'type', 'zero_regions', 'proof'}
            or cert['type'] != 'table_feedback_drup'):
        return False
    regions = cert['zero_regions']
    if type(regions) is not list or len(regions) != len(S_minus):
        return False
    for i, row in enumerate(regions):
        if type(row) is not list or row != sorted(set(row)):
            return False
        for region in row:
            tick()
            if type(region) is not int or not 0 < region < 1 << q:
                return False
            if direct_reject(Sigma, S_plus, [S_minus[i]], region):
                return False
    return check_drup(_encode(q, regions, tick), threshold, cert['proof'], tick)


def verify_optimal(D, result, limits=None):
    """Check certificate against D without a teacher or native SAT solver."""
    try:
        tick = budget(limits)
        Sigma, _, _ = normalize(D)
        tick()
        valid = type(result) is dict and set(result) == {'status', 'blocks', 'max_devices', 'certificate'}
        return {'status': 'ACCEPT' if valid and _verify(D, Sigma, result, tick) else 'REJECT'}
    except (Invalid, ValueError, TypeError, KeyError, IndexError):
        return {'status': 'REJECT'}
    except (Exhausted, MemoryError, RecursionError, KeyboardInterrupt):
        return {'status': 'INCOMPLETE'}

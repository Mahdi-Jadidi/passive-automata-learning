"""Experimental full-contract forced-pair graph candidate; see PROOF.md."""
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location("v33_baseline_contract", Path(__file__).with_name("baseline_contract.py"))
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)


def _components(alphabet, positives, negatives):
    m = len(alphabet)
    parent = list(range(m))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = root(a), root(b)
        if a != b:
            parent[b] = a

    # Each negative's must-link vertices form a clique; a star has the same components.
    mandatory = [[] for _ in negatives]
    for i, omitted in enumerate(alphabet):
        group = set(alphabet)
        group.remove(omitted)
        projected_positives = {_ref._projection(p, group) for p in positives}
        for j, n in enumerate(negatives):
            if _ref._projection(n, group) in projected_positives:
                mandatory[j].append(i)
    for vertices in mandatory:
        for v in vertices[1:]:
            union(vertices[0], v)
    component_by_root = {}
    owners = []
    for i in range(m):
        r = root(i)
        if r not in component_by_root:
            component_by_root[r] = len(component_by_root)
        owners.append(component_by_root[r])
    return tuple(owners), len(component_by_root)


def _bell(n):
    values = [1]
    for i in range(n):
        values.append(sum(math.comb(i, j) * values[j] for j in range(i + 1)))
    return values[n]


def _expand(owners, labels):
    return tuple(labels[owner] for owner in owners)


def _finish(alphabet, positives, negatives, count, best, best_count, all_rgs, best_rgs):
    if count == 0:
        result = _ref._blank('INCOMPATIBLE')
        result.update(compatible_count=0, optimal_count=0,
                      compatible_witnesses=[], optimal_witnesses=[])
        return result
    all_witnesses = [_ref._witness(alphabet, positives, negatives, rgs) for rgs in all_rgs]
    best_witnesses = [_ref._witness(alphabet, positives, negatives, rgs) for rgs in best_rgs]
    if any(w is None or not _ref._verify_witness(w, alphabet, positives, negatives)
           for w in all_witnesses + best_witnesses):
        return _ref._blank('ERROR', 'witness replay failed')
    return {'status': 'UNIQUE_COMPATIBLE' if count == 1 else 'AMBIGUOUS',
            'compatible_count': count, 'optimal_count': best_count,
            'max_blocks': best, 'recommendation': best_witnesses[0],
            'optimal_unique': best_count == 1,
            'compatible_witnesses': all_witnesses, 'optimal_witnesses': best_witnesses}


def solve(data, *, max_candidates=None):
    if max_candidates is not None:
        return _ref.solve(data, max_candidates=max_candidates)
    try:
        try:
            alphabet, positives, negatives = _ref._normalize(data)
        except _ref.InvalidInput as exc:
            return _ref._blank('INVALID_INPUT', str(exc))
        if set(positives) & set(negatives):
            return _finish(alphabet, positives, negatives, 0, None, 0, [], [])
        owners, q = _components(alphabet, positives, negatives)
        finest = _expand(owners, tuple(range(q)))
        if _ref._candidate(alphabet, positives, negatives, finest) is not None:
            all_rgs = [_expand(owners, (0,) * q)]
            if q > 1:
                all_rgs.append(_expand(owners, (0,) * (q - 1) + (1,)))
            return _finish(alphabet, positives, negatives, _bell(q), q, 1, all_rgs, [finest])
        count, best, best_count = 0, None, 0
        all_rgs, best_rgs = [], []
        for labels in _ref._rgs(q):
            rgs = _expand(owners, labels)
            if _ref._candidate(alphabet, positives, negatives, rgs) is None:
                continue
            count += 1
            if len(all_rgs) < 2:
                all_rgs.append(rgs)
            k = max(labels) + 1 if labels else 0
            if best is None or k > best:
                best, best_count, best_rgs = k, 1, [rgs]
            elif k == best:
                best_count += 1
                if len(best_rgs) < 2:
                    best_rgs.append(rgs)
        return _finish(alphabet, positives, negatives, count, best, best_count, all_rgs, best_rgs)
    except (KeyboardInterrupt, MemoryError):
        return _ref._blank('INCOMPLETE', 'execution interrupted or resources exhausted')

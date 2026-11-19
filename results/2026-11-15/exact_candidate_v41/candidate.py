"""V33 exact coverage-state subset DP; explicit budgets use frozen C028.

API: solve(record, *, max_candidates=None). See PROOF.md for output and costs.
"""
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_REFERENCE_SHA256 = '5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94'
_REFERENCE_PATH = (Path(__file__).resolve().parents[2] / '2026-11-11' /
                   'exact_foundations_v28' / 'implementation' / 'reference.py')
if sha256(_REFERENCE_PATH.read_bytes()).hexdigest() != _REFERENCE_SHA256:
    raise ImportError('frozen C028 reference hash mismatch')
_spec = spec_from_file_location('_v33_frozen_c028', _REFERENCE_PATH)
_ref = module_from_spec(_spec)
_spec.loader.exec_module(_ref)


def _incompatible():
    result = _ref._blank('INCOMPATIBLE')
    result.update(compatible_count=0, optimal_count=0,
                  compatible_witnesses=[], optimal_witnesses=[])
    return result


def _add_into(total, coefficients, shift=0):
    needed = len(coefficients) + shift
    if len(total) < needed:
        total.extend([0] * (needed - len(total)))
    for index, value in enumerate(coefficients):
        total[index + shift] += value


def solve(data, *, max_candidates=None):
    if max_candidates is not None:
        return _ref.solve(data, max_candidates=max_candidates)
    try:
        try:
            alphabet, positives, negatives = _ref._normalize(data)
        except _ref.InvalidInput as exc:
            return _ref._blank('INVALID_INPUT', str(exc))
        if set(positives) & set(negatives):
            return _incompatible()
        m = len(alphabet)
        all_symbols = (1 << m) - 1
        all_negatives = (1 << len(negatives)) - 1

        @lru_cache(maxsize=None)
        def rejection(mask):
            group = {alphabet[i] for i in range(m) if mask & (1 << i)}
            language = {_ref._projection(word, group) for word in positives}
            result = 0
            for j, word in enumerate(negatives):
                if _ref._projection(word, group) not in language:
                    result |= 1 << j
            return result

        @lru_cache(maxsize=None)
        def unconstrained(size, opened):
            # Coefficient k: extensions using k NEW blocks and `opened`
            # already distinguished nonempty blocks. Insert the last new ID
            # into one of opened+k blocks, or make its singleton new block.
            if size == 0:
                return (1,)
            previous = unconstrained(size - 1, opened)
            result = [0] * (size + 1)
            for k in range(size + 1):
                if k < len(previous): result[k] += (opened + k) * previous[k]
                if k: result[k] += previous[k - 1]
            return tuple(result)

        @lru_cache(maxsize=None)
        def counts(remaining, uncovered):
            if not remaining:
                return (int(uncovered == 0),)
            if not uncovered:
                return unconstrained(remaining.bit_count(), 0)
            if uncovered & ~rejection(remaining):
                return (0,)
            anchor = remaining & -remaining
            tail = remaining ^ anchor
            subset = tail
            total = [0]
            while True:
                block = subset | anchor
                child = counts(remaining ^ block, uncovered & ~rejection(block))
                _add_into(total, child, 1)
                if not subset:
                    break
                subset = (subset - 1) & tail
            return tuple(total)

        polynomial = counts(all_symbols, all_negatives)
        all_count = sum(polynomial)
        if not all_count:
            return _incompatible()
        best = max(k for k, coefficient in enumerate(polynomial) if coefficient)
        best_count = polynomial[best]

        def feasible(prefix, optimum_only):
            q = max(prefix) + 1 if prefix else 0
            fixed = [0] * q
            for i, label in enumerate(prefix):
                fixed[label] |= 1 << i
            remaining = all_symbols & ~((1 << len(prefix)) - 1)

            @lru_cache(maxsize=None)
            def extend(j, available, uncovered):
                if not uncovered:
                    return unconstrained(available.bit_count(), q - j)
                if j == q:
                    return counts(available, uncovered)
                total = [0]
                subset = available
                while True:
                    child = extend(j + 1, available ^ subset,
                                   uncovered & ~rejection(fixed[j] | subset))
                    _add_into(total, child)
                    if not subset:
                        break
                    subset = (subset - 1) & available
                return tuple(total)

            ways = extend(0, remaining, all_negatives)
            if optimum_only:
                needed = best - q
                return 0 <= needed < len(ways) and ways[needed] > 0
            return any(ways)

        def first_two(optimum_only):
            found = []

            def visit(prefix, labels):
                if len(found) >= 2:
                    return
                if len(prefix) == m:
                    found.append(tuple(prefix))
                    return
                for label in range(labels + 1):
                    new_prefix = prefix + (label,)
                    if feasible(new_prefix, optimum_only):
                        visit(new_prefix, max(labels, label + 1))
                    if len(found) >= 2:
                        return

            if m == 0:
                return [()]
            visit((), 0)
            return found

        all_rgs = first_two(False)
        best_rgs = first_two(True)
        if len(all_rgs) != min(2, all_count) or len(best_rgs) != min(2, best_count):
            return _ref._blank('ERROR', 'witness reconstruction failed')
        all_witnesses = [_ref._witness(alphabet, positives, negatives, rgs) for rgs in all_rgs]
        best_witnesses = [_ref._witness(alphabet, positives, negatives, rgs) for rgs in best_rgs]
        if any(w is None or not _ref._verify_witness(w, alphabet, positives, negatives)
               for w in all_witnesses + best_witnesses):
            return _ref._blank('ERROR', 'witness replay failed')
        return {'status': 'UNIQUE_COMPATIBLE' if all_count == 1 else 'AMBIGUOUS',
                'compatible_count': all_count, 'optimal_count': best_count,
                'max_blocks': best, 'recommendation': best_witnesses[0],
                'optimal_unique': best_count == 1,
                'compatible_witnesses': all_witnesses, 'optimal_witnesses': best_witnesses}
    except (KeyboardInterrupt, MemoryError, RecursionError):
        return _ref._blank('INCOMPLETE', 'execution interrupted or resources exhausted')

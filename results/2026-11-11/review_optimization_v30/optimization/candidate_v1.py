"""C028 exhaustive reference. Atomic string IDs; full-word samples; no hidden K.

solve(record, max_candidates=None): optional nonnegative budget limits inspected
partitions and returns INCOMPLETE without mathematical claims when exhausted.
An unlimited invocation performs the finite exhaustive search, subject to the
host's resources and external interruption.
"""


class InvalidInput(ValueError):
    pass


def _blank(status, reason=None):
    result = {
        'status': status, 'compatible_count': None, 'optimal_count': None,
        'max_blocks': None, 'recommendation': None, 'optimal_unique': None,
        'compatible_witnesses': None, 'optimal_witnesses': None,
    }
    if reason is not None:
        result['reason'] = reason
    return result


def _normalize(data):
    if not isinstance(data, dict) or set(data) != {'alphabet', 'positive', 'negative'}:
        raise InvalidInput('expected exactly alphabet, positive, negative')
    alphabet = data['alphabet']
    if not isinstance(alphabet, list):
        raise InvalidInput('alphabet must be an array')
    if any(not isinstance(x, str) or not x for x in alphabet):
        raise InvalidInput('alphabet IDs must be nonempty strings')
    if len(set(alphabet)) != len(alphabet):
        raise InvalidInput('alphabet IDs must be distinct')
    allowed = set(alphabet)
    normalized = []
    for key in ('positive', 'negative'):
        words = data[key]
        if not isinstance(words, list):
            raise InvalidInput(key + ' must be an array')
        seen = set()
        dedup = []
        for word in words:
            if not isinstance(word, list):
                raise InvalidInput('each word must be an array')
            if any(not isinstance(x, str) or x not in allowed for x in word):
                raise InvalidInput('word contains invalid or unknown symbol')
            value = tuple(word)
            if value not in seen:
                seen.add(value)
                dedup.append(value)
        normalized.append(dedup)
    return tuple(alphabet), normalized[0], normalized[1]


def _rgs(m):
    """Iterative lexicographic restricted-growth strings; includes m=0."""
    if m == 0:
        yield ()
        return
    values = [0] * m
    while True:
        yield tuple(values)
        i = m - 1
        while i > 0:
            maximum = max(values[:i]) + 1
            if values[i] < maximum:
                values[i] += 1
                values[i + 1:] = [0] * (m - i - 1)
                break
            i -= 1
        if i == 0:
            return


def _blocks(alphabet, rgs):
    count = max(rgs) + 1 if rgs else 0
    result = [[] for _ in range(count)]
    for symbol, label in zip(alphabet, rgs):
        result[label].append(symbol)
    return result


def _projection(word, symbols):
    return tuple(x for x in word if x in symbols)


def _candidate(alphabet, positives, negatives, rgs):
    blocks = _blocks(alphabet, rgs)
    groups = [set(block) for block in blocks]
    languages = [{_projection(word, group) for word in positives} for group in groups]
    rejected_by = []
    for word in negatives:
        found = next((i for i, group in enumerate(groups)
                      if _projection(word, group) not in languages[i]), None)
        if found is None:
            return None
        rejected_by.append(found)
    return blocks, languages, rejected_by


def _witness(alphabet, positives, negatives, rgs):
    evaluated = _candidate(alphabet, positives, negatives, rgs)
    if evaluated is None:
        return None
    blocks, _, rejected_by = evaluated
    # Preserve positive input order, eliminate duplicate local projections.
    factors = []
    for block in blocks:
        group = set(block)
        local = []
        seen = set()
        for word in positives:
            value = _projection(word, group)
            if value not in seen:
                seen.add(value)
                local.append(list(value))
        factors.append(local)
    return {'rgs': list(rgs), 'blocks': blocks, 'factors': factors,
            'negative_rejected_by': rejected_by}


def _verify_witness(witness, alphabet, positives, negatives):
    """Replay the returned factor languages, block cover, and every label."""
    blocks = witness['blocks']
    flat = [x for block in blocks for x in block]
    if any(not block for block in blocks) or len(flat) != len(alphabet) or set(flat) != set(alphabet):
        return False
    if tuple(witness['rgs']) not in _single_rgs_for_blocks(alphabet, blocks):
        return False
    factors = [set(tuple(word) for word in factor) for factor in witness['factors']]
    if len(factors) != len(blocks) or len(witness['negative_rejected_by']) != len(negatives):
        return False
    groups = [set(block) for block in blocks]
    for i, group in enumerate(groups):
        if factors[i] != {_projection(p, group) for p in positives}:
            return False
    for p in positives:
        if any(_projection(p, group) not in factors[i] for i, group in enumerate(groups)):
            return False
    for n, block_id in zip(negatives, witness['negative_rejected_by']):
        if not isinstance(block_id, int) or not 0 <= block_id < len(blocks):
            return False
        if _projection(n, groups[block_id]) in factors[block_id]:
            return False
    return True


def _single_rgs_for_blocks(alphabet, blocks):
    """Return singleton if blocks are canonically numbered, else empty."""
    owner = {symbol: i for i, block in enumerate(blocks) for symbol in block}
    labels = tuple(owner[x] for x in alphabet)
    highest = -1
    for label in labels:
        if label > highest + 1:
            return ()
        highest = max(highest, label)
    return (labels,)


def solve(data, *, max_candidates=None):
    try:
        if max_candidates is not None and (type(max_candidates) is not int or max_candidates < 0):
            return _blank('INVALID_INPUT', 'max_candidates must be a nonnegative integer or None')
        try:
            alphabet, positives, negatives = _normalize(data)
        except InvalidInput as exc:
            return _blank('INVALID_INPUT', str(exc))
        if set(positives) & set(negatives):
            result = _blank('INCOMPATIBLE')
            result.update(compatible_count=0, optimal_count=0,
                          compatible_witnesses=[], optimal_witnesses=[])
            return result
        all_count = 0
        best_count = 0
        best = None
        all_rgs, best_rgs = [], []
        inspected = 0
        for rgs in _rgs(len(alphabet)):
            if max_candidates is not None and inspected >= max_candidates:
                return _blank('INCOMPLETE', 'candidate budget exhausted')
            inspected += 1
            if _candidate(alphabet, positives, negatives, rgs) is None:
                continue
            all_count += 1
            if len(all_rgs) < 2:
                all_rgs.append(rgs)
            k = max(rgs) + 1 if rgs else 0
            if best is None or k > best:
                best, best_count, best_rgs = k, 1, [rgs]
            elif k == best:
                best_count += 1
                if len(best_rgs) < 2:
                    best_rgs.append(rgs)
        if all_count == 0:
            result = _blank('INCOMPATIBLE')
            result.update(compatible_count=0, optimal_count=0,
                          compatible_witnesses=[], optimal_witnesses=[])
            return result
        all_witnesses = [_witness(alphabet, positives, negatives, rgs) for rgs in all_rgs]
        best_witnesses = [_witness(alphabet, positives, negatives, rgs) for rgs in best_rgs]
        if any(w is None or not _verify_witness(w, alphabet, positives, negatives)
               for w in all_witnesses + best_witnesses):
            return _blank('ERROR', 'witness replay failed')
        return {'status': 'UNIQUE_COMPATIBLE' if all_count == 1 else 'AMBIGUOUS',
                'compatible_count': all_count, 'optimal_count': best_count,
                'max_blocks': best, 'recommendation': best_witnesses[0],
                'optimal_unique': best_count == 1,
                'compatible_witnesses': all_witnesses, 'optimal_witnesses': best_witnesses}
    except (KeyboardInterrupt, MemoryError):
        return _blank('INCOMPLETE', 'execution interrupted or resources exhausted')

# C030: proof-approved A/B candidates; baseline helpers above remain unchanged.
from collections import OrderedDict


def _bell(m):
    """Exact Bell number using one Stirling-number row."""
    row = [1]
    for n in range(1, m + 1):
        old = row
        row = [0] * (n + 1)
        for k in range(1, n + 1):
            row[k] = old[k - 1] + (k * old[k] if k < len(old) else 0)
    return sum(row)


def _certified_all(alphabet, positives, negatives):
    """Return full-family exact result when singleton partition is compatible."""
    m = len(alphabet)
    singleton = tuple(range(m))
    if _candidate(alphabet, positives, negatives, singleton) is None:
        return None
    count = _bell(m)
    first = (0,) * m
    all_rgs = [first]
    if m >= 2:
        all_rgs.append((0,) * (m - 1) + (1,))
    all_witnesses = [_witness(alphabet, positives, negatives, rgs) for rgs in all_rgs]
    best_witnesses = [_witness(alphabet, positives, negatives, singleton)]
    if any(w is None or not _verify_witness(w, alphabet, positives, negatives)
           for w in all_witnesses + best_witnesses):
        return _blank('ERROR', 'witness replay failed')
    return {'status': 'UNIQUE_COMPATIBLE' if count == 1 else 'AMBIGUOUS',
            'compatible_count': count, 'optimal_count': 1,
            'max_blocks': m, 'recommendation': best_witnesses[0],
            'optimal_unique': True, 'compatible_witnesses': all_witnesses,
            'optimal_witnesses': best_witnesses}


def _cached_candidate(alphabet, positives, negatives, rgs, cache):
    """Boolean compatibility via bounded local memo of block rejection vectors."""
    vectors = []
    for block in _blocks(alphabet, rgs):
        key = tuple(block)
        vector = cache.get(key)
        if vector is None:
            group = set(block)
            language = {_projection(p, group) for p in positives}
            vector = tuple(_projection(n, group) not in language for n in negatives)
            cache[key] = vector
            if len(cache) > 256:
                cache.popitem(last=False)
        else:
            cache.move_to_end(key)
        vectors.append(vector)
    return all(any(vector[j] for vector in vectors) for j in range(len(negatives)))


def _run_c030(data, *, max_candidates=None, use_a=True, use_b=True):
    try:
        if max_candidates is not None and (type(max_candidates) is not int or max_candidates < 0):
            return _blank('INVALID_INPUT', 'max_candidates must be a nonnegative integer or None')
        try:
            alphabet, positives, negatives = _normalize(data)
        except InvalidInput as exc:
            return _blank('INVALID_INPUT', str(exc))
        if set(positives) & set(negatives):
            result = _blank('INCOMPATIBLE')
            result.update(compatible_count=0, optimal_count=0,
                          compatible_witnesses=[], optimal_witnesses=[])
            return result
        if use_a and max_candidates is None:
            certified = _certified_all(alphabet, positives, negatives)
            if certified is not None:
                return certified
        cache = OrderedDict()
        all_count = 0
        best_count = 0
        best = None
        all_rgs, best_rgs = [], []
        inspected = 0
        for rgs in _rgs(len(alphabet)):
            if max_candidates is not None and inspected >= max_candidates:
                return _blank('INCOMPLETE', 'candidate budget exhausted')
            inspected += 1
            compatible = (_cached_candidate(alphabet, positives, negatives, rgs, cache)
                          if use_b else _candidate(alphabet, positives, negatives, rgs) is not None)
            if not compatible:
                continue
            all_count += 1
            if len(all_rgs) < 2:
                all_rgs.append(rgs)
            k = max(rgs) + 1 if rgs else 0
            if best is None or k > best:
                best, best_count, best_rgs = k, 1, [rgs]
            elif k == best:
                best_count += 1
                if len(best_rgs) < 2:
                    best_rgs.append(rgs)
        if all_count == 0:
            result = _blank('INCOMPATIBLE')
            result.update(compatible_count=0, optimal_count=0,
                          compatible_witnesses=[], optimal_witnesses=[])
            return result
        all_witnesses = [_witness(alphabet, positives, negatives, rgs) for rgs in all_rgs]
        best_witnesses = [_witness(alphabet, positives, negatives, rgs) for rgs in best_rgs]
        if any(w is None or not _verify_witness(w, alphabet, positives, negatives)
               for w in all_witnesses + best_witnesses):
            return _blank('ERROR', 'witness replay failed')
        return {'status': 'UNIQUE_COMPATIBLE' if all_count == 1 else 'AMBIGUOUS',
                'compatible_count': all_count, 'optimal_count': best_count,
                'max_blocks': best, 'recommendation': best_witnesses[0],
                'optimal_unique': best_count == 1,
                'compatible_witnesses': all_witnesses, 'optimal_witnesses': best_witnesses}
    except (KeyboardInterrupt, MemoryError):
        return _blank('INCOMPLETE', 'execution interrupted or resources exhausted')


def solve_a(data, *, max_candidates=None):
    return _run_c030(data, max_candidates=max_candidates, use_a=True, use_b=False)


def solve_b(data, *, max_candidates=None):
    return _run_c030(data, max_candidates=max_candidates, use_a=False, use_b=True)


def solve_combined(data, *, max_candidates=None):
    return _run_c030(data, max_candidates=max_candidates, use_a=True, use_b=True)

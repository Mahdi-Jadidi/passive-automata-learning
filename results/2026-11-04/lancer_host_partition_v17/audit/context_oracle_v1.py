"""Independent small-alphabet local-output oracle. Pure stdlib; no provider import.

Input traces are lists of {'symbol': opaque_string, 'label': True/False/None}.
No metadata or outcomes may be encoded into symbol. No I/O on import.
"""
from itertools import combinations


def partitions(symbols):
    """Canonical set partitions, including the unique empty partition."""
    symbols = tuple(symbols)
    if len(set(symbols)) != len(symbols):
        raise ValueError('duplicate alphabet symbol')
    blocks = []

    def visit(i):
        if i == len(symbols):
            yield tuple(tuple(b) for b in blocks)
            return
        for b in blocks:
            b.append(symbols[i])
            yield from visit(i + 1)
            b.pop()
        blocks.append([symbols[i]])
        yield from visit(i + 1)
        blocks.pop()

    yield from visit(0)


def block_conflicts(traces, block, depth):
    """Replay entire stream, then project onto this block, suffix after projection.

    Returns contradictory keys with both witness IDs. Dataset split is caller's
    responsibility; tables pool traces but histories reset at each trace.
    """
    if depth != 'full' and (type(depth) is not int or depth < 0):
        raise ValueError('invalid depth')
    block = frozenset(block)
    table = {}
    for ti, trace in enumerate(traces):
        prior = []
        for ei, event in enumerate(trace):
            symbol, label = event['symbol'], event['label']
            if label is not None and type(label) is not bool:
                raise ValueError('label must be bool or None')
            if symbol not in block:
                continue
            context = tuple(prior if depth == 'full' else prior[-depth:] if depth else ())
            if label is not None:
                key = (symbol, context)
                row = table.setdefault(key, {False: [], True: []})
                row[label].append((ti, ei))
            # Unlabeled/failed actions update history as well.
            prior.append(symbol)
    return {key: row for key, row in table.items() if row[False] and row[True]}


def direct_family(traces, symbols, depth):
    """Full Bell enumeration; no pruning, no monotonicity assumptions."""
    return tuple(p for p in partitions(symbols)
                 if all(not block_conflicts(traces, b, depth) for b in p))


def subset_family(traces, symbols, depth):
    """Equivalent exhaustive enumeration with block-alone memoization."""
    symbols = tuple(symbols)
    good = {}
    for size in range(1, len(symbols) + 1):
        for block in combinations(symbols, size):
            good[frozenset(block)] = not block_conflicts(traces, block, depth)
    return tuple(p for p in partitions(symbols)
                 if all(good[frozenset(b)] for b in p))


def strict_next_status(next_actor_observation):
    """Reference scalar policy, NOT a YAML parser or upstream converter."""
    status = next_actor_observation.get('prev_action_status')
    if type(status) is int and status in (1, 3):
        return status == 1
    return None


def training_symbols(traces, limit=8):
    """Only opaque identity and training frequency, including unlabeled events."""
    counts = {}
    for trace in traces:
        for event in trace:
            a = event['symbol']
            if not isinstance(a, str):
                raise ValueError('opaque symbol must be string')
            counts[a] = counts.get(a, 0) + 1
    return tuple(sorted(counts, key=lambda a: (-counts[a], a))[:limit])


def synthetic_gate():
    """Prepared but not run before explicit readiness authorization."""
    assert [sum(1 for _ in partitions(tuple(map(str, range(n))))))
            for n in range(9)] == [1, 1, 2, 5, 15, 52, 203, 877, 4140]
    for value in [2, None, True, False, '1', 1.0, 0, 4]:
        assert strict_next_status({'prev_action_status': value}) is None
    assert strict_next_status({}) is None
    assert strict_next_status({'prev_action_status': 1}) is True
    assert strict_next_status({'prev_action_status': 3}) is False
    # Adding b repairs a's empty-history collision for positive depth.
    traces = [[{'symbol': 'a', 'label': False}],
              [{'symbol': 'b', 'label': None}, {'symbol': 'a', 'label': True}]]
    assert block_conflicts(traces, ('a',), 1)
    assert not block_conflicts(traces, ('a', 'b'), 1)
    assert block_conflicts(traces, ('a', 'b'), 0)
    for depth in [0, 1, 2, 4, 8, 'full']:
        assert direct_family(traces, ('a', 'b'), depth) == subset_family(traces, ('a', 'b'), depth)
    assert training_symbols(traces) == ('a', 'b')
    return {'status': 'passed', 'scope': 'synthetic oracle self-check only'}

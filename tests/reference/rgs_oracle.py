"""Independent small-alphabet structural reference; no producer imports."""
from itertools import product
from time import monotonic


class Limit(Exception):
    pass


def rgs(n):
    if type(n) is not int or not 0 <= n <= 8:
        raise Limit('oracle alphabet cap: 8')
    def visit(prefix, k):
        if len(prefix) == n:
            yield prefix
        else:
            for g in range(k + 1):
                yield from visit(prefix + (g,), max(k, g + 1))
    yield from visit((), 0)


def validate(raw):
    if type(raw) is not dict or set(raw) != {'alphabet', 'positive', 'negative'}:
        raise ValueError('raw fields')
    a = raw['alphabet']
    if type(a) is not list or any(type(x) is not str or not x for x in a) or len(set(a)) != len(a):
        raise ValueError('alphabet')
    if len(a) > 8:
        raise Limit('oracle alphabet cap: 8')
    ids = dict(zip(a, range(len(a))))
    def words(key):
        ws = raw[key]
        if type(ws) is not list or any(type(w) is not list for w in ws):
            raise ValueError('traces')
        if any(type(x) is not str or x not in ids for w in ws for x in w):
            raise ValueError('token')
        return tuple(tuple(ids[x] for x in w) for w in ws)
    return len(a), words('positive'), words('negative')


def compatible(p, X, Y):
    # Ordered ORIGINAL symbol IDs, never block-label substitution.
    def project(w, g):
        return tuple(x for x in w if p[x] == g)
    groups = set(p)
    positives = {g: {project(x, g) for x in X} for g in groups}
    return all(any(project(y, g) not in positives[g] for g in groups) for y in Y)


def pairs_checked(pairs, n):
    if type(pairs) not in (tuple, list):
        raise ValueError("pairs container")
    for pair in pairs:
        if (type(pair) not in (tuple, list) or len(pair) != 2 or
                any(type(x) is not int or not 0 <= x < n for x in pair) or pair[0] == pair[1]):
            raise ValueError('pair')
    return tuple(tuple(pair) for pair in pairs)


def region(p, E, D):
    return all(p[a] == p[b] for a, b in E) and all(p[a] != p[b] for a, b in D)


def oracle(raw, E=(), D=(), *, max_partitions=4140, seconds=10):
    """Complete region optimum only; limits discard all claims. Small trusted inputs."""
    try:
        if type(max_partitions) is not int or max_partitions < 0 or type(seconds) not in (int, float) or not 0 <= seconds <= 60:
            raise ValueError('budget')
        deadline = monotonic() + seconds
        n, X, Y = validate(raw)
        E, D = pairs_checked(E, n), pairs_checked(D, n)
        best, winners, visited = None, [], 0
        for p in rgs(n):
            if visited >= max_partitions or monotonic() >= deadline:
                raise Limit('enumeration budget')
            visited += 1
            if region(p, E, D) and compatible(p, X, Y):
                c = n - len(set(p))
                if best is None or c < best:
                    best, winners = c, [p]
                elif c == best:
                    winners.append(p)
        if monotonic() >= deadline:
            raise Limit('deadline')
        return dict(status='VERIFIED', result=dict(optimum=best, optima=winners, visited=visited), operational_status='INCOMPLETE')
    except (Limit, MemoryError):
        return dict(status='INCOMPLETE', operational_status='INCOMPLETE')
    except (ValueError, TypeError):
        return dict(status='INVALID', operational_status='INCOMPLETE')


def split(E, D, alternatives):
    """Reference first-true partition of the region, including residual."""
    E, D = tuple(E), tuple(D)
    A = tuple(alternatives)
    return [(E + (a,), D + A[:i]) for i, a in enumerate(A)], (E, D + A)


def self_test():
    def check(condition):
        if not condition:
            raise RuntimeError('oracle self-test failed')
    bells = [1, 1, 2, 5, 15, 52, 203, 877, 4140]
    for n, b in enumerate(bells):
        ps = list(rgs(n))
        check(len(ps) == len(set(ps)) == b)
        check(all(all(0 <= g <= (max(p[:i], default=-1) + 1) for i, g in enumerate(p)) for p in ps))
        if n <= 5:
            def canonical(w):
                d = {}
                return tuple(d.setdefault(x, len(d)) for x in w)
            check(set(ps) == {canonical(w) for w in product(range(n), repeat=n)})
    raw = {'alphabet': ['a', 'b', 'unused'], 'positive': [['a'], ['b']], 'negative': [['a', 'b']]}
    check(oracle(raw)['result']['optimum'] == 1)
    check(oracle(raw, D=((0, 1),))['result']['optimum'] is None)
    check(oracle(raw, max_partitions=0)['status'] == 'INCOMPLETE')
    check('result' not in oracle(raw, max_partitions=4))
    check(oracle(raw, seconds=0)['status'] == 'INCOMPLETE')
    check(oracle(dict(raw, negative=[['a']]))['result']['optimum'] is None)
    check(oracle(dict(raw, positive=[['a'], ['a'], ['b']]))['result'] == oracle(raw)['result'])
    check(oracle({'alphabet': [], 'positive': [], 'negative': []})['result']['optimum'] == 0)
    check(oracle({'alphabet': [], 'positive': [], 'negative': [[]]})['result']['optimum'] is None)
    check(oracle(dict(raw, negative=[['unknown']]))['status'] == 'INVALID')
    # All ordered nonrepeating alternative sequences on 4 symbols, with and without local constraints.
    from itertools import combinations, permutations
    A = tuple(combinations(range(4), 2))
    checks = 0
    for k in range(4):
        for order in permutations(A, k):
            for E, D in [((), ()), (((0, 1),), ((2, 3),)), ((), ((0, 1),))]:
                children, residual = split(E, D, order)
                for p in rgs(4):
                    hits = sum(region(p, e, d) for e, d in children + [residual])
                    check(hits == int(region(p, E, D)))
                    check(sum(region(p, e, d) for e, d in children) == int(region(p, E, D) and any(p[a] == p[b] for a, b in order)))
                    checks += 1
    print('Bell counts 0..8; independent label enumeration 0..5; region membership checks:', checks)
    print('Structural examples, duplicate/empty/unused symbols, malformed token and caps: PASS')


if __name__ == '__main__':
    self_test()

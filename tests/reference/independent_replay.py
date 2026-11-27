"""Independent raw proof kernel, selector-v2/1 proposal; standard library only.

Wire layout is provisional until the core schema is frozen. No external verdicts
or search/frontier completion can be certified by this kernel.
"""
import hashlib
import json

VERSION = 'selector-v2/1'


class InvalidProof(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidProof(message)


def fields(obj, names):
    require(type(obj) is dict and set(obj) == set(names.split()), 'record fields')


def array(obj):
    require(type(obj) is list, 'expected JSON array')
    return obj


def index(value, size):
    require(type(value) is int and 0 <= value < size, 'invalid index')
    return value


def hex_digest(value):
    require(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'digest syntax')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(',', ':'), sort_keys=True).encode('utf-8')).hexdigest()


def load_json(text):
    def pairs(items):
        result = {}
        for key, val in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = val
        return result
    def reject(_):
        raise InvalidProof('nonfinite JSON number')
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    except (ValueError, TypeError, RecursionError) as exc:
        raise InvalidProof('invalid JSON: ' + str(exc)) from exc


def sample_data(raw):
    fields(raw, 'alphabet positive negative')
    alphabet = array(raw['alphabet'])
    require(all(type(a) is str and a for a in alphabet), 'invalid symbol')
    ids = {a: i for i, a in enumerate(alphabet)}
    require(len(ids) == len(alphabet), 'duplicate symbol')
    def encode(words):
        out = []
        for w in array(words):
            require(all(type(a) is str and a in ids for a in array(w)), 'undeclared token')
            out.append(tuple(ids[a] for a in w))
        return tuple(out)
    X, Y = encode(raw['positive']), encode(raw['negative'])
    return len(alphabet), X, Y, digest(['sample-v2', alphabet, X, Y])


def owner_map(value, n):
    p = array(value)
    require(len(p) == n, 'partition coverage')
    for a, g in enumerate(p):
        index(g, n)
        require(g <= a and type(p[g]) is int and p[g] == g, 'noncanonical owner')
    return tuple(p)


def scope_check(scope, sample_digest):
    fields(scope, 'sample_digest regime family capacity_digest')
    require(hex_digest(scope['sample_digest']) == sample_digest, 'wrong sample digest')
    require(scope['family'] == 'ALL_PARTITIONS', 'unsupported admissible family')
    require(scope['regime'] in ('UNRESTRICTED', 'BOUNDED'), 'unknown regime')
    if scope['regime'] == 'UNRESTRICTED':
        require(scope['capacity_digest'] is None, 'unexpected capacity digest')
    else:
        hex_digest(scope['capacity_digest'])


def projection(word, group, owner, retain=True):
    return tuple(a for a in word if (owner[a] == group) == retain)


def deletion(X, Y, p, negative, group, positive):
    i, j, g = index(negative, len(Y)), index(positive, len(X)), index(group, len(p))
    require(p[g] == g, 'not a component representative')
    require(projection(X[j], g, p, False) == projection(Y[i], g, p, False), 'false deletion equality')


def structural(X, Y, p, record):
    ok = record['compatible']
    require(type(ok) is bool, 'invalid structural verdict')
    witnesses = array(record['separating_groups'])
    failed = record['failed_negative']
    groups = set(p)
    if ok:
        require(failed is None and len(witnesses) == len(Y), 'missing structural witness')
        # Independent index includes epsilon explicitly, only for requested groups.
        positives = {}
        for i, g in enumerate(witnesses):
            index(g, len(p))
            require(g in groups, 'nonrepresentative witness')
            if g not in positives:
                positives[g] = {projection(x, g, p) for x in X}
            require(projection(Y[i], g, p) not in positives[g], 'false separating witness')
    else:
        require(not witnesses, 'unexpected separating witnesses')
        y = Y[index(failed, len(Y))]
        require(all(any(projection(x, g, p) == projection(y, g, p) for x in X) for g in groups), 'false failed negative')
    return ok


def replay(raw, certificate, expected_scope=None):
    """Verify a batch atomically; return only raw conclusions, never ACCEPT.

    Epoch = count of preceding successful component edges. A frozen epoch may
    be reused after a merge in the same pass; its owner must match that prefix.
    Standalone deletion at arbitrary owner is a raw equality only, not a merge.
    """
    n, X, Y, sd = sample_data(raw)
    fields(certificate, 'version scope records')
    require(certificate['version'] == VERSION, 'unsupported version')
    scope = certificate['scope']
    scope_check(scope, sd)
    if expected_scope is not None:
        scope_check(expected_scope, sd)
        require(scope == expected_scope, 'wrong expected scope')
    # Independent graph replay; no producer DSU or checker imports.
    current = tuple(range(n))
    epochs = [current]
    checks, conflict, deletions = [], False, 0
    for r in array(certificate['records']):
        require(type(r) is dict and r.get('origin') == 'RAW', 'untrusted origin')
        kind = r.get('kind')
        if kind == 'DELETE_EQUAL':
            fields(r, 'kind origin owner negative group positive')
            p = owner_map(r['owner'], n)
            deletion(X, Y, p, r['negative'], r['group'], r['positive'])
            deletions += 1
        elif kind == 'COMPONENT_EDGE':
            fields(r, 'kind origin epoch owner negative a positive_a b positive_b')
            p = owner_map(r['owner'], n)
            require(p == epochs[index(r['epoch'], len(epochs))], 'unproved frozen epoch')
            a, b = r['a'], r['b']
            deletion(X, Y, p, r['negative'], a, r['positive_a'])
            deletion(X, Y, p, r['negative'], b, r['positive_b'])
            require(a != b and current[a] != current[b], 'redundant or self edge')
            lo, hi = sorted((current[a], current[b]))
            current = tuple(lo if g == hi else g for g in current)
            epochs.append(current)
        elif kind == 'LABEL_CONFLICT':
            fields(r, 'kind origin negative positive')
            require(Y[index(r['negative'], len(Y))] == X[index(r['positive'], len(X))], 'false label conflict')
            conflict = True
        elif kind == 'STRUCTURAL_CHECK':
            fields(r, 'kind origin owner compatible separating_groups failed_negative')
            p = owner_map(r['owner'], n)
            checks.append((p, structural(X, Y, p, r)))
        else:
            raise InvalidProof('unsupported record kind')
    floor = n - len(set(current))
    root_compatible = (current, True) in checks
    optimum = floor if root_compatible and scope['regime'] == 'UNRESTRICTED' and not conflict else None
    return {'sample_digest': sd, 'mandatory_owner': current, 'mandatory_floor': floor,
            'deletion_count': deletions, 'structural_checks': tuple(checks),
            'label_conflict': conflict, 'structural_optimum': optimum,
            'operational_status': 'INCOMPLETE'}


def replay_json(raw_text, certificate_text, expected_scope=None):
    return replay(load_json(raw_text), load_json(certificate_text), expected_scope)

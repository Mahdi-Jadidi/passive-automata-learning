"""Independent replay of core schema cd627dcdf2a9b73cb79d313f3b864c8284b55082.
No imports from selector_v2. Structural facts only; never evaluator acceptance.
"""
from collections import defaultdict
from independent_replay import (VERSION, InvalidProof, require, fields, array, index,
                                digest, sample_data, owner_map, scope_check, deletion,
                                load_json)


def scope_v1(sc, sd):
    fields(sc, 'version sample_digest regime family capacity_digest')
    require(sc['version'] == VERSION, 'scope version')
    scope_check({k: v for k, v in sc.items() if k != 'version'}, sd)


def verify_request(raw, request):
    n, X, Y, sd = sample_data(raw)
    fields(request, 'version scope owner request_id attempt_id negative_ids')
    require(request['version'] == VERSION and n > 0, 'invalid request version or empty alphabet')
    scope_v1(request['scope'], sd)
    owner_map(request['owner'], n)
    for key in ('request_id', 'attempt_id'):
        require(type(request[key]) is str and request[key], 'invalid request identity')
    ids = array(request['negative_ids'])
    require(all(type(i) is int for i in ids) and ids == list(range(len(Y))), 'negative column order')
    return digest(request)


class Forest:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.low = list(range(n))
        self.rank = 0

    def root(self, a):
        while self.parent[a] != a:
            a = self.parent[a]
        return a

    def join(self, a, b):
        a, b = self.root(a), self.root(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        self.low[a] = min(self.low[a], self.low[b])
        self.rank += 1
        return True

    def owner(self):
        return tuple(self.low[self.root(a)] for a in range(len(self.parent)))


def expected_deletions(X, Y, p):
    """Exact literal join, independent of producer fingerprints; touched groups only.
    Space can be quadratic in length of a single highly diverse trace.
    """
    require(not set(X).intersection(Y), 'duplicate conflict precludes exhausted pass')
    full = set(X)
    by_group, inverse = set(), defaultdict(set)
    for x in full:
        for g in {p[a] for a in x}:
            remainder = tuple(a for a in x if p[a] != g)
            by_group.add((g, remainder))
            inverse[remainder].add(g)
    for i, y in enumerate(Y):
        touched = {p[a] for a in y}
        for g in touched:
            remainder = tuple(a for a in y if p[a] != g)
            if remainder in full or (g, remainder) in by_group:
                yield i, g
        for g in inverse.get(y, ()) - touched if y in inverse else ():
            yield i, g


def check_structural(X, Y, p, r):
    fields(r, 'owner compatible separating_groups failed_negative')
    ok = r['compatible']
    require(type(ok) is bool, 'structural type')
    witness = array(r['separating_groups'])
    groups = set(p)
    def group_word(w):
        out = defaultdict(list)
        for a in w:
            out[p[a]].append(a)
        return {g: tuple(v) for g, v in out.items()}
    seen, count = defaultdict(set), defaultdict(int)
    for x in X:
        for g, w in group_word(x).items():
            seen[g].add(w)
            count[g] += 1
    universal = {g for g, c in count.items() if c == len(X)}
    def separates(local, g):
        if not X:
            return True
        return local[g] not in seen.get(g, ()) if g in local else g in universal
    if ok:
        require(r['failed_negative'] is None and len(witness) == len(Y), 'missing structural witness')
        for y, g in zip(Y, witness):
            index(g, len(p))
            require(g in groups and separates(group_word(y), g), 'false structural witness')
    else:
        require(not witness, 'unexpected structural witnesses')
        local = group_word(Y[index(r['failed_negative'], len(Y))])
        if not X:
            require(not groups, 'false failed negative without positives')
        else:
            require(not (universal - local.keys()) and all(not separates(local,g) for g in local), 'false failed negative')
    return ok


def unwrap(record, sd):
    fields(record, 'version origin sample_digest kind payload')
    require(record['version'] == VERSION and record['sample_digest'] == sd, 'record binding')
    require(record['origin'] == 'RAW', 'nonraw observation is not a proof')
    require(type(record['kind']) is str, 'record kind')
    return record['kind'], record['payload']


def check_cursor(cursor, X, Y, facts):
    c = array(cursor)
    require(len(c) == 2 and c[0] in ('positive','conflict','negative'), 'invalid cursor')
    stage, at = c
    index(at, len(X) if stage == 'positive' else len(Y))
    require(not facts or (stage == 'negative' and all(i <= at for i, _, _ in facts)), 'cursor before emitted facts')


def replay_closure(raw, scope, closure, structural_records=()):
    """Verify exact serialized closure and optional structural records.
    Scope must be supplied independently. PARTIAL remains partial; no frontier,
    external receipt, bounded feasibility or operational optimality is certified.
    """
    n, X, Y, sd = sample_data(raw)
    scope_v1(scope, sd)
    fields(closure, 'state owner records')
    claimed_owner = owner_map(closure['owner'], n)
    records = array(closure['records'])
    require(bool(records), 'missing closure evidence')
    forest = Forest(n)
    terminal = None
    epoch = 0
    fact_count = 0
    for record in records:
        require(terminal is None, 'record after terminal closure')
        kind, r = unwrap(record, sd)
        if kind == 'LABEL_CONFLICT':
            fields(r, 'negative positive')
            require(Y[index(r['negative'], len(Y))] == X[index(r['positive'], len(X))], 'false label conflict')
            terminal = 'LABEL_CONFLICT'
            continue
        require(kind == 'COMPONENT_EPOCH', 'unsupported closure record')
        fields(r, 'epoch owner facts edges result_owner state cursor')
        require(type(r['epoch']) is int and r['epoch'] == epoch, 'epoch sequence')
        p = owner_map(r['owner'], n)
        require(p == forest.owner(), 'unproved frozen component scope')
        facts, keys = set(), set()
        by_negative = defaultdict(list)
        for f in array(r['facts']):
            fields(f, 'negative group positive')
            i,g,j = f['negative'],f['group'],f['positive']
            deletion(X,Y,p,i,g,j)
            require((i,g) not in keys, 'duplicate deletion group')
            keys.add((i,g)); facts.add((i,g,j)); by_negative[i].append(g)
        fact_count += len(facts)
        state = r['state']
        if state == 'EXHAUSTED':
            require(r['cursor'] is None, 'exhausted with cursor')
            require(keys == set(expected_deletions(X,Y,p)), 'missing or extra exhausted deletion facts')
        elif state == 'PARTIAL':
            check_cursor(r['cursor'], X, Y, facts)
        else:
            raise InvalidProof('invalid epoch state')
        # Replay only edges licensed by two emitted facts for the same negative.
        for e in array(r['edges']):
            fields(e, 'negative a positive_a b positive_b')
            i,a,j,b,k = e['negative'],e['a'],e['positive_a'],e['b'],e['positive_b']
            deletion(X,Y,p,i,a,j); deletion(X,Y,p,i,b,k)
            require((i,a,j) in facts and (i,b,k) in facts, 'edge cites missing fact')
            require(forest.join(a,b), 'redundant edge')
        # All emitted same-negative obligations must be joined (even on PARTIAL).
        for gs in by_negative.values():
            require(all(forest.root(g) == forest.root(gs[0]) for g in gs), 'missing required contraction')
        require(owner_map(r['result_owner'], n) == forest.owner(), 'wrong epoch result')
        if state == 'PARTIAL': terminal = 'PARTIAL'
        elif not r['edges']: terminal = 'FIXPOINT'
        epoch += 1
    require(terminal is not None and closure['state'] == terminal, 'missing or false terminal state')
    final = forest.owner()
    require(final == claimed_owner, 'wrong final owner')
    checks = []
    for record in structural_records:
        kind, r = unwrap(record, sd)
        require(kind == 'STRUCTURAL_CHECK', 'unsupported structural record')
        fields(r, 'owner compatible separating_groups failed_negative')
        p = owner_map(r['owner'], n)
        checks.append((p, check_structural(X,Y,p,r)))
    root_optimum = forest.rank if (final, True) in checks and terminal != 'LABEL_CONFLICT' and scope['regime'] == 'UNRESTRICTED' else None
    return dict(sample_digest=sd, state=terminal, mandatory_owner=final, mandatory_floor=forest.rank,
                facts=fact_count, epochs=epoch, structural_checks=tuple(checks),
                structural_optimum=root_optimum, label_conflict=terminal=='LABEL_CONFLICT',
                operational_status='INCOMPLETE')


def replay_serialized(raw_text, scope_text, closure_text, structural_text='[]'):
    return replay_closure(load_json(raw_text), load_json(scope_text), load_json(closure_text), array(load_json(structural_text)))

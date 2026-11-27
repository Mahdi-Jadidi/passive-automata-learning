"""P2 selector-only reference. No transport, learner, or deployment authority."""
import hashlib
import json
from threading import Lock

SCHEMA = 'selector-v2/1'


def canonical(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False).encode('utf-8')


def json_check(value):
    """Reject non-JSON types before serializing untrusted inputs."""
    if type(value) is dict:
        need(all(type(k) is str for k in value), 'nonstring key')
        for v in value.values():
            json_check(v)
    elif type(value) is list:
        for v in value:
            json_check(v)
    else:
        need(type(value) in (str, int, bool, type(None)), 'non-JSON value')


def snapshot(value):
    json_check(value)
    return json.loads(canonical(value))


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def fields(obj, keys):
    need(type(obj) is dict and set(obj) == set(keys.split()), 'unexpected/missing fields')


def integer(x, n):
    return type(x) is int and 0 <= x < n


def text_id(x):
    return type(x) is str and bool(x)


def sequence(x):
    need(type(x) is list, 'expected list')
    return x


def encode_sample(raw):
    fields(raw, 'alphabet positive negative')
    alphabet = sequence(raw['alphabet'])
    need(all(map(text_id, alphabet)) and len(set(alphabet)) == len(alphabet), 'invalid symbols')
    ids = {a: i for i, a in enumerate(alphabet)}
    def encode(words):
        out = []
        for word in sequence(words):
            need(all(type(a) is str and a in ids for a in sequence(word)), 'invalid token')
            out.append([ids[a] for a in word])
        return out
    return ['sample-v2', list(alphabet), encode(raw['positive']), encode(raw['negative'])]


def id_map(pairs, count):
    """Explicit per-label wire ID mapping in original column order; no dedup."""
    need(type(pairs) is list and len(pairs) == count, 'ID map length')
    out = {}
    for i, pair in enumerate(pairs):
        need(type(pair) is list and len(pair) == 2 and text_id(pair[0]) and type(pair[1]) is int and pair[1] == i and pair[0] not in out, 'ID map not ordered bijection')
        out[pair[0]] = i
    return out


def request(raw, owner, request_id, attempt_id, capacities=None):
    sample = encode_sample(raw)
    n = len(sample[1])
    need(n > 0, 'empty alphabet unsupported externally')
    need(type(owner) is list and len(owner) == n and all(integer(g, n) and g <= a and type(owner[g]) is int and owner[g] == g for a, g in enumerate(owner)), 'noncanonical/incomplete owner')
    need(text_id(request_id) and text_id(attempt_id), 'request/attempt ID')
    roots = [a for a, g in enumerate(owner) if a == g]
    if capacities is not None:
        need(type(capacities) is list and len(capacities) == len(roots) and all(type(v) is int and v > 0 for v in capacities), 'capacity vector')
    scope = {'version': SCHEMA, 'sample_digest': digest(sample), 'regime': 'UNRESTRICTED' if capacities is None else 'BOUNDED', 'family': 'ALL_PARTITIONS', 'capacity_digest': None if capacities is None else digest(['capacity-v2', list(zip(roots, capacities))])}
    return {'version': SCHEMA, 'scope': scope, 'owner': list(owner), 'request_id': request_id, 'attempt_id': attempt_id, 'negative_ids': list(range(len(sample[3])))}


def projection(word, block):
    return tuple(a for a in word if a in block)


def table_check(t, root, block, pos, neg, failed):
    fields(t, 'block kind complete zeros free')
    need(type(t['block']) is int and t['block'] == root and t['kind'] == 'UNRESTRICTED_BASE' and t['complete'] is True, 'table scope')
    pp = [projection(w, block) for w in pos]
    nn = [projection(w, block) for w in neg]
    pset = set(pp)
    seen, groups = set(), set()
    named = False
    def take(i):
        need(integer(i, len(nn)) and i not in seen, 'bad/duplicate negative ID')
        seen.add(i)
        return nn[i]
    for z in sequence(t['zeros']):
        fields(z, 'negative positive')
        i, j = z['negative'], z['positive']
        w = take(i)
        need(w in pset, 'false fixed zero')
        if j is not None:
            need(integer(j, len(pp)) and pp[j] == w, 'false named witness')
            named |= i == failed
    for group in sequence(t['free']):
        need(bool(sequence(group)), 'empty free group')
        words = {take(i) for i in group}
        need(len(words) == 1, 'merged distinct groups')
        w = next(iter(words))
        need(w not in pset and w not in groups, 'false free/split group')
        groups.add(w)
    need(len(seen) == len(nn) and named, 'incomplete table or missing failed witness')


def dfa_check(d, root, block, pos, neg, capacity):
    fields(d, 'block states initial accepting transitions')
    n = d['states']
    need(type(d['block']) is int and d['block'] == root and type(n) is int and n > 0 and (capacity is None or n <= capacity), 'DFA block/state bound')
    need(integer(d['initial'], n), 'initial state')
    accept = sequence(d['accepting'])
    need(all(integer(s, n) for s in accept) and len(set(accept)) == len(accept), 'accepting states')
    delta = {}
    for row in sequence(d['transitions']):
        need(type(row) is list and len(row) == 3, 'transition shape')
        s, a, t = row
        need(integer(s, n) and type(a) is int and a in block and integer(t, n) and (s, a) not in delta, 'invalid/nondeterministic transition')
        delta[s, a] = t
    need(len(delta) == n * len(block), 'incomplete DFA')
    def accepts(word):
        s = d['initial']
        for a in projection(word, block):
            s = delta[s, a]
        return s in accept
    need(all(map(accepts, pos)), 'positive rejected')
    return [int(not accepts(w)) for w in neg]


def validate(raw, expected, payload, capacities=None, authenticate=None):
    """Validate all-or-nothing; transport authenticates exact canonical bytes.

    This review-only adapter never grants operational acceptance, even with a
    supplied test authenticator. Real transport/owner approval is a future gate.
    """
    json_check(expected)
    json_check(payload)
    sample = encode_sample(raw)
    fields(expected, 'version scope owner request_id attempt_id negative_ids')
    actual = request(raw, expected['owner'], expected['request_id'], expected['attempt_id'], capacities)
    need(canonical(actual) == canonical(expected), 'stale digest/scope/request')
    need(type(payload) is dict, 'missing response')
    status = payload.get('status')
    base = 'version request origin status complete receipt'
    extra = {'PROJECTION_NO': ' failed tables', 'ACCEPT': ' dfas', 'BOUNDED_NO': ' exact'}
    need(type(status) is str and status in extra, 'unknown/ambiguous status')
    if status == 'ACCEPT' and 'joint_row' in payload:
        extra['ACCEPT'] += ' joint_row'
    fields(payload, base + extra[status])
    need(payload['version'] == SCHEMA and canonical(payload['request']) == canonical(actual) and payload['complete'] is True, 'response binding/completeness')
    origin = payload['origin']
    need(origin in ('SIMULATOR', 'EXTERNAL') and text_id(payload['receipt']), 'origin/receipt')
    if origin == 'EXTERNAL':
        need(authenticate is not None and authenticate(canonical(actual), canonical(payload)) is True, 'untrusted external receipt')
    groups = {}
    for a, g in enumerate(actual['owner']):
        groups.setdefault(g, set()).add(a)
    pos, neg = sample[2:]
    if status == 'PROJECTION_NO':
        failed = payload['failed']
        need(integer(failed, len(neg)), 'failed ID')
        tables = sequence(payload['tables'])
        need(len(tables) == len(groups), 'missing table')
        for (g, block), t in zip(groups.items(), tables):
            table_check(t, g, block, pos, neg, failed)
    elif status == 'BOUNDED_NO':
        need(capacities is not None and payload['exact'] is True, 'not exact bounded NO')
    else:
        dfas = sequence(payload['dfas'])
        need(len(dfas) == len(groups), 'missing DFA')
        bits = [dfa_check(d, g, block, pos, neg, None if capacities is None else capacities[i]) for i, ((g, block), d) in enumerate(zip(groups.items(), dfas))]
        need(all(any(row[i] for row in bits) for i in range(len(neg))), 'negative accepted')
        if 'joint_row' in payload:
            need(canonical(bits) == canonical(payload['joint_row']), 'joint row mismatch')
    return {'version': SCHEMA, 'request': actual, 'origin': origin, 'status': status, 'operational': False, 'scope': 'NONE', 'payload': payload}


class Ledger:
    """In-memory atomic append; immutable canonical records, separate quarantine.

    No record authorizes pruning/incumbency in this mock/review ledger.
    """
    def __init__(self, raw):
        self._raw = canonical(snapshot(raw))
        encode_sample(json.loads(self._raw))
        self._records = ()
        self._quarantine = ()
        self._attempts = frozenset()
        self._lock = Lock()

    @property
    def records(self):
        return self._records

    @property
    def quarantine(self):
        return self._quarantine

    def ingest(self, expected, payload, capacities=None, authenticate=None):
        with self._lock:
            try:
                # Snapshot before validation; caller mutation cannot change committed facts.
                expected = snapshot(expected)
                payload = snapshot(payload)
                capacities = snapshot(capacities)
                key = (expected['request_id'], expected['attempt_id'])
                need(key not in self._attempts, 'duplicate attempt')
                record = validate(json.loads(self._raw), expected, payload, capacities, authenticate)
                encoded = canonical(record)
                records = self._records + (encoded,)
                attempts = self._attempts | {key}
                self._records, self._attempts = records, attempts
                return record['status']
            except Exception as exc:
                self._quarantine += (str(exc),)
                return 'UNKNOWN'

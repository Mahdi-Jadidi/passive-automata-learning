"""Append-only in-memory selector ledger. Validation is not independent certification."""
import json
from collections import defaultdict
from enum import Enum
from .core import PartitionRef, SymbolDSU
from .schema import (VERSION, canonical, fields, hex_digest, identity, integer,
                     owner_ref, require, sample_id, token, validate_request)
from .sparse_analysis import raw_check


class Origin(str, Enum):
    RAW = 'RAW'
    SIMULATOR = 'SIMULATOR'
    EXTERNAL = 'EXTERNAL'


class Verdict(str, Enum):
    ACCEPT = 'ACCEPT'
    PROJECTION_NO = 'PROJECTION_NO'
    BOUNDED_NO = 'BOUNDED_NO'
    UNKNOWN = 'UNKNOWN'


def _fact(sample, owner, fact):
    fields(fact, 'negative', 'group', 'positive')
    i = integer(fact['negative'], len(sample.negative))
    j = integer(fact['positive'], len(sample.positive))
    g = integer(fact['group'], len(owner))
    require(owner[g] == g, 'noncanonical group')
    require(tuple(a for a in sample.negative[i] if owner[a] != g) ==
            tuple(a for a in sample.positive[j] if owner[a] != g), 'false deletion equality')
    return i, g, j


def _projection_index(words, owner):
    possible, presence = defaultdict(set), defaultdict(int)
    for word in words:
        local = defaultdict(list)
        for a in word:
            local[owner[a]].append(a)
        for g, seq in local.items():
            possible[g].add(tuple(seq)); presence[g] += 1
    return possible, presence


def _structural(sample, p):
    fields(p, 'owner', 'compatible', 'separating_groups', 'failed_negative')
    part = owner_ref(sample, p['owner']); owner = part.owner
    require(type(p['compatible']) is bool and type(p['separating_groups']) is list, 'invalid structural result')
    if not p['compatible']:
        i = integer(p['failed_negative'], len(sample.negative))
        require(not p['separating_groups'], 'unexpected witnesses')
        from .core import Sample
        one = Sample(sample.alphabet, sample.positive, (sample.negative[i],))
        require(not raw_check(one, part).compatible, 'false failed negative')
        return
    require(p['failed_negative'] is None and len(p['separating_groups']) == len(sample.negative), 'witness coverage')
    possible, presence = _projection_index(sample.positive, owner)
    for y, g in zip(sample.negative, p['separating_groups']):
        integer(g, len(owner)); require(owner[g] == g, 'noncanonical group')
        seq = tuple(a for a in y if owner[a] == g)
        require(seq not in possible[g] if seq else presence[g] == len(sample.positive), 'false separation')


def _epoch(sample, p, owner, epoch):
    fields(p, 'epoch', 'owner', 'facts', 'edges', 'result_owner', 'state', 'cursor')
    require(type(p['epoch']) is int and p['epoch'] == epoch, 'epoch order')
    require(owner_ref(sample,p['owner']).owner == owner, 'unproved component snapshot')
    result = owner_ref(sample,p['result_owner']).owner
    require(p['state'] in ('PARTIAL','EXHAUSTED'), 'epoch state')
    if p['state'] == 'PARTIAL':
        c = p['cursor']
        require(type(c) is list and len(c) == 2 and c[0] in ('positive','conflict','negative'), 'cursor shape')
        integer(c[1], len(sample.positive) if c[0] == 'positive' else len(sample.negative))
    else:
        require(p['cursor'] is None, 'unexpected cursor')
    require(type(p['facts']) is list and type(p['edges']) is list, 'epoch arrays')
    facts = {_fact(sample,owner,f) for f in p['facts']}
    require(len(facts) == len(p['facts']) and len({(i,g) for i,g,j in facts}) == len(facts), 'duplicate facts')
    dsu = SymbolDSU(len(owner))
    for a,g in enumerate(owner):
        dsu.union(a,g)
    for e in p['edges']:
        fields(e, 'negative', 'a', 'positive_a', 'b', 'positive_b')
        i = integer(e['negative'], len(sample.negative))
        a = integer(e['a'],len(owner)); b = integer(e['b'],len(owner))
        j = integer(e['positive_a'],len(sample.positive)); k = integer(e['positive_b'],len(sample.positive))
        require((i,a,j) in facts and (i,b,k) in facts and dsu.union(a,b), 'invalid forced edge')
    require(dsu.snapshot().owner == result, 'incorrect result owner')
    # Check that all emitted obligations for one negative were joined; no assertion of join exhaustion.
    first = {}
    for i,g,j in facts:
        require(result[g] == result[first.setdefault(i,g)], 'missing contraction')
    return result


def _table(sample, owner, table, failed):
    fields(table, 'group', 'named_zeros', 'anonymous_zeros', 'free_groups')
    g = integer(table['group'], len(owner)); require(owner[g] == g, 'noncanonical table group')
    require(all(type(table[k]) is list for k in ('named_zeros','anonymous_zeros','free_groups')), 'table arrays')
    def projection(w):
        return tuple(a for a in w if owner[a] == g)
    positives = {projection(w) for w in sample.positive}
    negatives = [projection(w) for w in sample.negative]
    seen, named, free = set(), set(), set()
    def column(i):
        integer(i,len(negatives)); require(i not in seen,'duplicate column'); seen.add(i)
        return negatives[i]
    for z in table['named_zeros']:
        fields(z,'negative','positive')
        i = z['negative']; seq = column(i); j = integer(z['positive'],len(sample.positive))
        require(seq == projection(sample.positive[j]), 'false named zero'); named.add(i)
    for i in table['anonymous_zeros']:
        require(column(i) in positives,'false anonymous zero')
    for group in table['free_groups']:
        require(type(group) is list and bool(group),'empty free group')
        seqs = {column(i) for i in group}
        require(len(seqs) == 1, 'unequal free group')
        seq = next(iter(seqs))
        require(seq not in positives and seq not in free,'false or split free group'); free.add(seq)
    require(len(seen) == len(negatives) and failed in named, 'incomplete table or failed witness')
    return g


def _observation(sample, origin, p, requests):
    fields(p,'request_digest','status','response_digest','receipt_digest','feedback')
    key = hex_digest(p['request_digest']); require(key in requests,'unknown request')
    req = requests[key]; status = p['status']; require(status in tuple(v.value for v in Verdict),'invalid verdict')
    hex_digest(p['response_digest'])
    if origin == Origin.EXTERNAL.value and status != Verdict.UNKNOWN.value:
        hex_digest(p['receipt_digest'])
    elif p['receipt_digest'] is not None:
        require(origin == Origin.EXTERNAL.value,'simulator receipt forbidden'); hex_digest(p['receipt_digest'])
    feedback = p['feedback']
    if status == Verdict.PROJECTION_NO.value:
        fields(feedback,'kind','failed_negative','tables')
        require(feedback['kind'] == 'UNRESTRICTED_COMPLETE' and type(feedback['tables']) is list,'unrestricted tables required')
        i = integer(feedback['failed_negative'],len(sample.negative)); owner = req['owner']
        groups = [_table(sample,owner,t,i) for t in feedback['tables']]
        require(groups == sorted(set(owner)), 'table group coverage/order')
    elif status == Verdict.BOUNDED_NO.value:
        require(req['scope']['regime'] == 'BOUNDED', 'bounded scope required')
        if feedback is not None:
            fields(feedback,'kind','artifact_digest')
            require(feedback['kind'] in ('BOUNDED_OPAQUE','CONDITIONED_OPAQUE'),'invalid opaque feedback')
            hex_digest(feedback['artifact_digest'])
    else:
        require(feedback is None,'unexpected feedback')
    # Receipt digests are references, not authentication or verified DFA witnesses.


class EvidenceLedger:
    """Immutable snapshots on read; atomic batches; quarantined batches never update evidence.

    In-memory only. No operational incumbent, no inference from observation status.
    """
    def __init__(self, sample):
        self._sample = sample
        self._digest = sample_id(sample)
        self._entries = []
        self._quarantine = []
        self._owner = tuple(range(len(sample.alphabet)))
        self._epoch = 0
        self._closed = False
        self._requests = {}
        self._attempts = set()
        self._request_ids = {}
        self._observed = set()
        self._receipts = set()

    @property
    def records(self):
        return tuple(json.loads(b) for b in self._entries)

    @property
    def quarantine(self):
        return tuple(self._quarantine)

    @property
    def owner(self):
        return self._owner

    def append(self, records):
        """Return bool; preserve prior state on malformed or conflicting input."""
        try:
            require(type(records) is list and bool(records), 'nonempty record batch required')
            owner, epoch, closed = self._owner,self._epoch,self._closed
            requests, attempts, request_ids = self._requests.copy(),self._attempts.copy(),self._request_ids.copy()
            observed, receipts = self._observed.copy(),self._receipts.copy()
            pending = []
            for record in records:
                fields(record,'version','origin','sample_digest','kind','payload')
                require(record['version'] == VERSION and record['sample_digest'] == self._digest == sample_id(self._sample),'record scope')
                origin, kind, p = record['origin'],record['kind'],record['payload']
                if origin == Origin.RAW.value:
                    if kind == 'COMPONENT_EPOCH':
                        require(not closed,'epoch stream terminated')
                        owner = _epoch(self._sample,p,owner,epoch); epoch += 1
                        closed = p['state'] == 'PARTIAL' or not p['edges']
                    elif kind == 'LABEL_CONFLICT':
                        fields(p,'negative','positive')
                        i = integer(p['negative'],len(self._sample.negative)); j = integer(p['positive'],len(self._sample.positive))
                        require(self._sample.negative[i] == self._sample.positive[j],'false label conflict'); closed = True
                    elif kind == 'STRUCTURAL_CHECK':
                        _structural(self._sample,p)
                    elif kind == 'DELETE_EQUAL':
                        fields(p,'owner','fact'); _fact(self._sample,owner_ref(self._sample,p['owner']).owner,p['fact'])
                    elif kind == 'REQUEST':
                        validate_request(self._sample,p); key = identity(p)
                        aid, rid = p['attempt_id'],p['request_id']
                        binding = identity({k:v for k,v in p.items() if k != 'attempt_id'})
                        require(aid not in attempts and request_ids.get(rid,binding) == binding,'request or attempt reuse')
                        attempts.add(aid); request_ids[rid] = binding; requests[key] = json.loads(canonical(p))
                    else:
                        raise ValueError('invalid raw kind')
                else:
                    require(origin in (Origin.SIMULATOR.value,Origin.EXTERNAL.value) and kind == 'OBSERVATION','invalid provenance')
                    _observation(self._sample,origin,p,requests)
                    key, receipt = p['request_digest'],p['receipt_digest']
                    require(key not in observed, 'attempt already observed')
                    require(receipt is None or receipt not in receipts, 'receipt reuse')
                    observed.add(key)
                    if receipt is not None:
                        receipts.add(receipt)
                pending.append(canonical(record))
        except (ValueError,TypeError,KeyError,IndexError) as exc:
            try:
                raw = canonical(records)
                bad = identity(records)
            except (ValueError,TypeError):
                raw, bad = None, None
            self._quarantine.append((bad,str(exc),raw))
            return False
        self._entries.extend(pending)
        self._owner,self._epoch,self._closed = owner,epoch,closed
        self._requests,self._attempts,self._request_ids = requests,attempts,request_ids
        self._observed,self._receipts = observed,receipts
        return True

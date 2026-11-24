"""P2.1 single-authority journal; adapter and core validators have no separate live state."""
import json
from contextlib import contextmanager
from hashlib import sha256
from threading import RLock
from .core import Sample
from .schema import VERSION, canonical, identity, raw_record, require
from .evidence_store import EvidenceLedger

JOURNAL_VERSION = 'selector-v2-journal/1'


def _sha(data):
    return sha256(data).hexdigest()


def _convert(sample, entry, observation):
    p = observation['payload']
    status = observation['status']
    feedback = None
    if status == 'PROJECTION_NO':
        feedback = dict(kind='UNRESTRICTED_COMPLETE', failed_negative=p['failed'], tables=[
            dict(group=t['block'], named_zeros=[z for z in t['zeros'] if z['positive'] is not None],
                 anonymous_zeros=[z['negative'] for z in t['zeros'] if z['positive'] is None],
                 free_groups=t['free']) for t in p['tables']])
    encoded = canonical(observation)
    receipt = identity(p['receipt']) if entry['origin'] == 'EXTERNAL' else None
    return dict(version=VERSION, origin=entry['origin'], sample_digest=sample.sample_digest,
                kind='OBSERVATION', payload=dict(request_digest=identity(entry['request']),
                status=status, response_digest=_sha(encoded), receipt_digest=receipt, feedback=feedback))


class RegisteredLedger:
    """Single sample/session journal, globally unique attempt IDs within it.

    The pinned interface adapter supplies pure request/map/response validation and
    strict parsing; its legacy stateful ledgers must not be used on this path.
    Core EvidenceLedger is a disposable batch validator, not a second authority.
    In memory only; complete replay on each transaction favors correctness over speed.
    """
    def __init__(self, raw, *, adapter, parse, authenticate=None):
        self._raw = canonical(adapter.snapshot(raw))
        self._sample = Sample.from_input(json.loads(self._raw))
        self._adapter, self._parse, self._authenticate = adapter, parse, authenticate
        self._journal = ()
        self._lock = RLock()
        self._writing = False

    @contextmanager
    def _transaction(self):
        with self._lock:
            require(not self._writing, 'reentrant write')
            self._writing = True
            try:
                yield
            finally:
                self._writing = False

    def _events(self):
        return [json.loads(b) for b in self._journal]

    @property
    def journal(self):
        with self._lock:
            return self._journal

    @property
    def records(self):
        with self._lock:
            return tuple(r for e in self._events() for r in e['records'])

    @property
    def quarantine(self):
        with self._lock:
            return tuple(e for e in self._events() if e['event'] == 'QUARANTINE')

    def export(self):
        with self._lock:
            return canonical(dict(version=JOURNAL_VERSION, sample_digest=self._sample.sample_digest,
                                  events=self._events()))

    def export_records(self):
        return canonical(list(self.records))

    def _index(self):
        entries, statuses, receipts = {}, {}, set()
        for e in self._events():
            if e['event'] == 'REGISTER':
                q = e['registered']['request']; aid = q['attempt_id']
                entries[aid] = e['registered']; statuses[aid] = 'PENDING'
            elif e['event'] == 'OBSERVE':
                statuses[e['attempt_id']] = e['status']; receipts.add(e['receipt_ref'])
            elif e['event'] == 'QUARANTINE' and e['records']:
                statuses[e['attempt_id']] = 'UNKNOWN'
        return entries, statuses, receipts

    def _commit(self, event):
        # Caller holds the one transaction lock. Commit exactly one immutable event
        # after validation. No mutable interface or core ledger survives this call.
        encoded = canonical(event)
        validator = EvidenceLedger(self._sample)
        records = list(self.records) + json.loads(encoded)['records']
        if records and not validator.append(records):
            raise ValueError('core rejected transaction: ' + str(validator.quarantine[0][1]))
        self._journal = self._journal + (encoded,)

    def append_raw(self, records):
        with self._transaction():
            batch = self._adapter.snapshot(records)
            require(type(batch) is list and bool(batch), 'empty raw batch')
            require(all(type(r) is dict and r.get('origin') == 'RAW' and r.get('kind') in
                        ('COMPONENT_EPOCH','LABEL_CONFLICT','STRUCTURAL_CHECK','DELETE_EQUAL') for r in batch),
                    'registration/observation bypass forbidden')
            self._commit(dict(event='RAW', records=batch))

    def register(self, owner, request_id, attempt_id, *, capacities=None, origin='SIMULATOR',
                 positive_map=None, negative_map=None):
        with self._transaction():
            a = self._adapter
            require(origin in ('SIMULATOR','EXTERNAL'), 'origin')
            capacities = a.snapshot(capacities)
            q = a.request(json.loads(self._raw), a.snapshot(owner), request_id, attempt_id, capacities)
            maps = {label: None if pairs is None else a.id_map(a.snapshot(pairs), len(words))
                    for label,pairs,words in [('positive',positive_map,self._sample.positive),
                                             ('negative',negative_map,self._sample.negative)]}
            entry = dict(request=q, capacities=capacities, origin=origin, maps=maps)
            entries, _, _ = self._index()
            require(attempt_id not in entries, 'global attempt ID reuse')
            for old in entries.values():
                if old['request']['request_id'] == request_id:
                    old['request']['attempt_id'] = attempt_id
                    require(canonical(old) == canonical(entry), 'request provenance rebound')
            self._commit(dict(event='REGISTER', registered=entry,
                              records=[raw_record(self._sample,'REQUEST',q)]))
            return json.loads(canonical(q))

    def _lookup(self, entries, request_id, attempt_id):
        require(type(request_id) is str and type(attempt_id) is str, 'invalid attempt identity')
        e = entries.get(attempt_id)
        require(e is not None and e['request']['request_id'] == request_id, 'unregistered attempt')
        return e

    def original_id(self, request_id, attempt_id, label, wire_id):
        with self._lock:
            entry = self._lookup(self._index()[0],request_id,attempt_id)
            require(label in ('positive','negative'), 'invalid label')
            m = entry['maps'][label]
            require(m is not None and type(wire_id) is str and wire_id in m, 'unknown wire ID')
            return m[wire_id]

    def attempt_status(self, request_id, attempt_id):
        with self._lock:
            entries,statuses,_ = self._index()
            self._lookup(entries,request_id,attempt_id)
            return statuses[attempt_id]

    @property
    def pending_candidates(self):
        # No search/closure authority in this layer; even validated mock ACCEPT and
        # opaque NO remain unresolved candidates. Raw evidence is separately usable.
        with self._lock:
            return tuple(sorted({e['request']['request_id'] for e in self._index()[0].values()}))

    def ingest(self, request_id, attempt_id, raw):
        with self._transaction():
            entries,statuses,receipts = self._index()
            entry = None
            wire = dict(wire_hex=raw.hex() if type(raw) is bytes else None,
                        wire_sha256=_sha(raw) if type(raw) is bytes else None)
            try:
                entry = self._lookup(entries,request_id,attempt_id)
                require(statuses[attempt_id] == 'PENDING', 'closed attempt')
                payload = self._parse(raw)
                require(type(payload) is dict and payload.get('origin') == entry['origin'], 'origin mismatch')
                obs = self._adapter.validate(json.loads(self._raw),entry['request'],payload,
                                             entry['capacities'],self._authenticate)
                receipt_ref = identity(payload['receipt'])
                require(receipt_ref not in receipts, 'receipt reuse')
                record = _convert(self._sample,entry,obs)
                encoded = canonical(obs)
                self._commit(dict(event='OBSERVE', request_id=request_id, attempt_id=attempt_id,
                                  status=obs['status'], receipt_ref=receipt_ref, normalized_hex=encoded.hex(),
                                  normalized_sha256=_sha(encoded), records=[record], **wire))
                return obs['status']
            except Exception as exc:
                records = []
                if entry is not None and statuses[attempt_id] == 'PENDING':
                    p = dict(request_digest=identity(entry['request']),status='UNKNOWN',
                             response_digest=wire['wire_sha256'] or _sha(b''),receipt_digest=None,feedback=None)
                    records.append(dict(version=VERSION,origin=entry['origin'],sample_digest=self._sample.sample_digest,
                                        kind='OBSERVATION',payload=p))
                self._commit(dict(event='QUARANTINE',request_id=request_id if type(request_id) is str else None,
                                  attempt_id=attempt_id if type(attempt_id) is str else None,
                                  reason=str(exc),records=records,**wire))
                return 'UNKNOWN'

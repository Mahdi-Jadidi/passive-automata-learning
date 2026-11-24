"""P2.1 gateway: actual core EvidenceLedger is the only observation journal.

Requires a pinned selector_v2 package. No production transport or authority.
"""
import json
from hashlib import sha256
from threading import RLock
from dataclasses import dataclass

from adapter import canonical, id_map, need, request, snapshot, validate
from strict_ledger import parse
from selector_v2.core import Sample
from selector_v2.schema import VERSION, identity, raw_record
from selector_v2.evidence_store import EvidenceLedger


@dataclass(frozen=True)
class Outcome:
    status: str
    committed: bool
    operational: bool = False
    scope: str = 'NONE'
    candidate_pending: bool = True


def sha(data):
    return sha256(data).hexdigest()


def feedback(payload):
    """Only call after complete strict validation; preserve named/anonymous IDs."""
    if payload['status'] != 'PROJECTION_NO':
        return None
    return {'kind': 'UNRESTRICTED_COMPLETE', 'failed_negative': payload['failed'],
            'tables': [{'group': t['block'],
                        'named_zeros': [z for z in t['zeros'] if z['positive'] is not None],
                        'anonymous_zeros': [z['negative'] for z in t['zeros'] if z['positive'] is None],
                        'free_groups': t['free']} for t in payload['tables']]}


class SharedGateway:
    """Single-writer facade over core journal, with immutable artifact sidecar.

    Do not hand out the mutable core ledger. All writes/read snapshots use the
    same lock. No parallel RegisteredLedger state; attempts/status are derived
    from the core records. Sidecar is staged before append and published only
    if the core transaction succeeds. Memory-only; no crash atomicity claim.
    """
    def __init__(self, raw, authenticate=None):
        self._raw = canonical(snapshot(raw))
        self.sample = Sample.from_input(json.loads(self._raw))
        self._ledger = EvidenceLedger(self.sample)
        self._auth = authenticate
        self._lock = RLock()
        self._registrations = {}  # request_digest -> immutable registration bytes
        self._artifacts = {}      # SHA256 -> exact bytes (incl. rejected input)
        self._quarantine = ()     # diagnostic only; not a verdict or observation

    def _attempt(self, aid):
        for r in self._ledger.records:
            if r['kind'] == 'REQUEST' and r['payload']['attempt_id'] == aid:
                q = r['payload']; key = identity(q)
                return q, key
        return None, None

    def _observed(self, key):
        return next((r['payload'] for r in self._ledger.records
                     if r['kind'] == 'OBSERVATION' and r['payload']['request_digest'] == key), None)

    def status(self, aid):
        with self._lock:
            _, key = self._attempt(aid)
            if key is None:
                return 'UNREGISTERED'
            obs = self._observed(key)
            return 'PENDING' if obs is None else obs['status']

    def export(self):
        """Single coherent snapshot. V1 journal plus audit artifacts (not v1 fields)."""
        with self._lock:
            return {'records': list(self._ledger.records), 'owner': list(self._ledger.owner),
                    'registrations': {k: v.hex() for k, v in self._registrations.items()},
                    'artifacts': {k: v.hex() for k, v in self._artifacts.items()},
                    'quarantine': [json.loads(v) for v in self._quarantine]}

    def append_raw(self, records):
        """Do not permit REQUEST/OBSERVATION bypass through this entry point."""
        with self._lock:
            records = snapshot(records)
            need(type(records) is list and all(r['origin'] == 'RAW' and r['kind'] != 'REQUEST' for r in records), 'not raw evidence')
            return self._ledger.append(records)

    def register(self, owner, request_id, attempt_id, *, origin='SIMULATOR', capacities=None,
                 positive_map=None, negative_map=None):
        with self._lock:
            need(origin in ('SIMULATOR', 'EXTERNAL'), 'origin')
            q = request(json.loads(self._raw), snapshot(owner), request_id, attempt_id, snapshot(capacities))
            need(self._attempt(attempt_id)[0] is None, 'global attempt reuse')
            maps = {label: None if pairs is None else id_map(snapshot(pairs), len(words))
                    for label, pairs, words in [('positive', positive_map, self.sample.positive),
                                                 ('negative', negative_map, self.sample.negative)]}
            entry = {'request': q, 'origin': origin, 'capacities': snapshot(capacities), 'maps': maps}
            for old in self._registrations.values():
                prev = json.loads(old)
                if prev['request']['request_id'] == request_id:
                    prev['request']['attempt_id'] = attempt_id
                    need(canonical(prev) == canonical(entry), 'request metadata rebound')
            key = identity(q); encoded = canonical(entry)
            registrations = {**self._registrations, key: encoded}
            need(self._ledger.append([raw_record(self.sample, 'REQUEST', q)]), 'core registration rejected')
            self._registrations = registrations
            return snapshot(q)

    def original_id(self, aid, label, wire_id):
        with self._lock:
            _, key = self._attempt(aid)
            need(key is not None and label in ('positive', 'negative'), 'attempt/label')
            mapping = json.loads(self._registrations[key])['maps'][label]
            need(mapping is not None and type(wire_id) is str and wire_id in mapping, 'unknown wire ID')
            return mapping[wire_id]

    def _observation(self, entry, status, raw, receipt=None, fb=None):
        return {'version': VERSION, 'origin': entry['origin'], 'sample_digest': self.sample.sample_digest,
                'kind': 'OBSERVATION', 'payload': {'request_digest': identity(entry['request']),
                    'status': status, 'response_digest': sha(raw), 'receipt_digest': receipt,
                    'feedback': fb}}

    def ingest(self, aid, raw):
        with self._lock:
            need(type(aid) is str and bool(aid), 'attempt ID')
            q, key = self._attempt(aid)
            # Only bytes from normalized response parser are journaled. Timeout is
            # an explicit diagnostic byte artifact, not an invented response.
            body = raw if type(raw) is bytes else canonical({'local_event': 'NO_RESPONSE'})
            artifacts = {**self._artifacts, sha(body): body}
            entry = None
            try:
                need(q is not None and self._observed(key) is None, 'unsolicited or closed attempt')
                entry = json.loads(self._registrations[key])
                need(type(raw) is bytes, 'no response bytes')
                payload = parse(raw)
                need(type(payload) is dict and payload.get('origin') == entry['origin'], 'origin mismatch')
                def authenticate(qbytes, pbytes):
                    # Strict adapter verifies request/body, then caller-supplied
                    # verifier binds exact bytes AND registration metadata.
                    return self._auth is not None and self._auth(qbytes, raw, canonical(entry)) is True
                result = validate(json.loads(self._raw), q, payload, entry['capacities'], authenticate)
                receipt = None
                if entry['origin'] == 'EXTERNAL':
                    receipt_bytes = payload['receipt'].encode('utf-8')
                    receipt = sha(receipt_bytes)
                    artifacts[receipt] = receipt_bytes
                obs = self._observation(entry, result['status'], body, receipt, feedback(payload))
                need(self._ledger.append([obs]), 'core observation rejected (including receipt reuse)')
                self._artifacts = artifacts
                return Outcome(result['status'], True)
            except Exception as exc:
                # Preserve original evidence; only a previously pending registered
                # attempt can get one UNKNOWN control observation, with no feedback.
                event = canonical({'attempt_id': aid, 'response_digest': sha(body), 'reason': str(exc)})
                quarantine = self._quarantine + (event,)
                committed = False
                if entry is not None and self._observed(key) is None:
                    committed = self._ledger.append([self._observation(entry, 'UNKNOWN', body)])
                self._artifacts, self._quarantine = artifacts, quarantine
                return Outcome('UNKNOWN', committed)

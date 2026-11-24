"""Registered-attempt boundary for the P2 normalized adapter (review only)."""
from dataclasses import dataclass
from hashlib import sha256
import json
from threading import Lock

from adapter import canonical, encode_sample, id_map, need, request, snapshot, validate


def parse(raw):
    need(type(raw) is bytes, 'response must be UTF-8 bytes')
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    def noninteger(_):
        raise ValueError('noninteger JSON number')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_float=noninteger, parse_constant=noninteger)


@dataclass(frozen=True)
class Outcome:
    status: str
    operational: bool = False
    scope: str = 'NONE'
    record: bytes | None = None


class RegisteredLedger:
    """Atomic, memory-only observation ledger. Caller owns request scheduling.

    UNKNOWN closes an attempt, not its candidate: retry with a new attempt ID.
    No operational ACCEPT/prune authority, even with a test authenticator.
    """
    def __init__(self, raw, authenticate=None):
        self._raw = canonical(snapshot(raw))
        self._sample = encode_sample(json.loads(self._raw))
        self._authenticate = authenticate
        self._lock = Lock()
        self._state = ({}, (), ())  # attempts, observation records, quarantine

    @property
    def records(self):
        return self._state[1]

    @property
    def quarantine(self):
        return self._state[2]

    def register(self, owner, request_id, attempt_id, *, capacities=None,
                 origin='SIMULATOR', positive_map=None, negative_map=None):
        need(origin in ('SIMULATOR', 'EXTERNAL'), 'origin')
        q = request(json.loads(self._raw), snapshot(owner), request_id, attempt_id,
                    snapshot(capacities))
        maps = {}
        for label, pairs, words in [('positive', positive_map, self._sample[2]),
                                    ('negative', negative_map, self._sample[3])]:
            maps[label] = None if pairs is None else id_map(snapshot(pairs), len(words))
        entry = {'request': q, 'capacities': capacities, 'origin': origin, 'maps': maps}
        entry = snapshot(entry)
        key = (request_id, attempt_id)
        with self._lock:
            attempts, records, quarantine = self._state
            need(key not in attempts, 'attempt already registered')
            # A request ID has one immutable target; only attempt ID may change.
            for (rid, _), (old, _) in attempts.items():
                if rid == request_id:
                    old_entry = json.loads(old)
                    old_entry['request']['attempt_id'] = attempt_id
                    need(canonical(old_entry) == canonical(entry), 'request ID rebound')
            self._state = ({**attempts, key: (canonical(entry), 'PENDING')}, records, quarantine)
        return snapshot(q)

    def original_id(self, request_id, attempt_id, label, wire_id):
        """Translate only using the registered per-label map, never guessed IDs."""
        need(label in ('positive', 'negative'), 'label')
        entry, _ = self._state[0][request_id, attempt_id]
        mapping = json.loads(entry)['maps'][label]
        need(mapping is not None and type(wire_id) is str and wire_id in mapping, 'unknown wire ID')
        return mapping[wire_id]

    def attempt_status(self, request_id, attempt_id):
        return self._state[0][request_id, attempt_id][1]

    def ingest(self, request_id, attempt_id, raw):
        key = (request_id, attempt_id)
        with self._lock:
            attempts, records, quarantine = self._state
            found = attempts.get(key)
            try:
                need(found is not None and found[1] == 'PENDING', 'unregistered or closed attempt')
                entry = json.loads(found[0])
                payload = parse(raw)
                need(type(payload) is dict and payload.get('origin') == entry['origin'], 'origin mismatch')
                observation = validate(json.loads(self._raw), entry['request'], payload,
                                       entry['capacities'], self._authenticate)
                # One immutable envelope binds original bytes and trusted ID maps.
                encoded = canonical({'observation': observation, 'registered': entry,
                                     'wire_hex': raw.hex(), 'wire_sha256': sha256(raw).hexdigest()})
                new = ({**attempts, key: (found[0], observation['status'])},
                       records + (encoded,), quarantine)
                self._state = new
                return Outcome(observation['status'], record=encoded)
            except Exception as exc:
                # Close only the registered pending attempt; never alter prior evidence.
                if found is not None and found[1] == 'PENDING':
                    attempts = {**attempts, key: (found[0], 'UNKNOWN')}
                event = canonical({'request_id': request_id, 'attempt_id': attempt_id,
                                   'reason': str(exc), 'wire_hex': raw.hex() if type(raw) is bytes else None,
                                   'wire_sha256': sha256(raw).hexdigest() if type(raw) is bytes else None})
                self._state = (attempts, records, quarantine + (event,))
                return Outcome('UNKNOWN')

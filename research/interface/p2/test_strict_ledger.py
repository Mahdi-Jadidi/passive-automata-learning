import copy
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import unittest
from adapter import canonical
from strict_ledger import RegisteredLedger
from test_adapter import RAW, NO, YES


class RegisteredTests(unittest.TestCase):
    def register(self, ledger, attempt='a1', **kw):
        return ledger.register([0, 1, 2], 'q', attempt, **kw)

    def payload(self, q):
        p = copy.deepcopy(NO)
        p['request'] = q
        return p

    def test_unsolicited_replay_and_retry(self):
        l = RegisteredLedger(RAW)
        self.assertEqual(l.ingest('q', 'a1', canonical(NO)).status, 'UNKNOWN')
        self.assertEqual(l.records, ())
        q = self.register(l)
        raw = canonical(self.payload(q))
        bad = raw[:-1]
        self.assertEqual(l.ingest('q', 'a1', bad).status, 'UNKNOWN')
        self.assertEqual(l.attempt_status('q', 'a1'), 'UNKNOWN')
        self.assertEqual(l.records, ())
        self.assertEqual(l.ingest('q', 'a1', raw).status, 'UNKNOWN')
        with self.assertRaises(ValueError): self.register(l)
        with self.assertRaises(ValueError): l.register([0, 0, 2], 'q', 'a2')
        q2 = self.register(l, 'a2')
        out = l.ingest('q', 'a2', canonical(self.payload(q2)))
        self.assertEqual(out.status, 'PROJECTION_NO')
        self.assertFalse(out.operational)
        self.assertEqual(out.scope, 'NONE')
        self.assertEqual(len(l.records), 1)
        self.assertEqual(l.ingest('q', 'a2', canonical(self.payload(q2))).status, 'UNKNOWN')
        self.assertEqual(len(l.records), 1)
        event = json.loads(l.quarantine[1])
        self.assertEqual(event['wire_sha256'], sha256(bad).hexdigest())
        self.assertEqual(bytes.fromhex(event['wire_hex']), bad)

    def test_duplicate_keys_and_origin(self):
        for raw in [b'{"status":"ACCEPT","status":"NO"}', b'{"nested":{"a":1,"a":2}}', b'{"number":1.0}', b'{"number":NaN}', b'\xff']:
            with self.subTest(raw=raw):
                l = RegisteredLedger(RAW); self.register(l)
                self.assertEqual(l.ingest('q', 'a1', raw).status, 'UNKNOWN')
                self.assertEqual(l.records, ())
        l = RegisteredLedger(RAW, authenticate=lambda *_: True)
        q = self.register(l); p = self.payload(q); p['origin'] = 'EXTERNAL'
        self.assertEqual(l.ingest('q', 'a1', canonical(p)).status, 'UNKNOWN')
        self.assertEqual(l.records, ())

    def test_registered_map_and_snapshot(self):
        l = RegisteredLedger(RAW)
        nm = [['same', 0], ['duplicate-word', 1], ['third', 2]]
        pm = [['same', 0], ['empty', 1]]
        q = self.register(l, positive_map=pm, negative_map=nm)
        self.assertEqual(l.original_id('q', 'a1', 'positive', 'same'), 0)
        self.assertEqual(l.original_id('q', 'a1', 'negative', 'duplicate-word'), 1)
        nm[1][0] = 'mutated'
        with self.assertRaises(ValueError): l.original_id('q', 'a1', 'negative', 'mutated')
        raw = canonical(self.payload(q)); out = l.ingest('q', 'a1', raw)
        event = json.loads(out.record)
        self.assertEqual(event['registered']['maps']['negative']['duplicate-word'], 1)
        self.assertEqual(event['wire_sha256'], sha256(raw).hexdigest())
        self.assertEqual(bytes.fromhex(event['wire_hex']), raw)

    def test_atomic_concurrent_delivery(self):
        l = RegisteredLedger(RAW); q = self.register(l)
        raw = canonical(self.payload(q))
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(lambda _: l.ingest('q', 'a1', raw).status, range(16)))
        self.assertEqual(statuses.count('PROJECTION_NO'), 1)
        self.assertEqual(statuses.count('UNKNOWN'), 15)
        self.assertEqual(len(l.records), 1)
        self.assertEqual(len(l.quarantine), 15)

    def test_no_operational_accept(self):
        for origin, auth in [('SIMULATOR', None), ('EXTERNAL', lambda *_: True)]:
            with self.subTest(origin=origin):
                l = RegisteredLedger(RAW, authenticate=auth)
                q = l.register([0, 0, 2], 'q2', 'a2', origin=origin)
                p = copy.deepcopy(YES); p['request'] = q; p['origin'] = origin
                out = l.ingest('q2', 'a2', canonical(p))
                self.assertEqual(out.status, 'ACCEPT')
                self.assertFalse(out.operational)
                self.assertEqual(out.scope, 'NONE')
                self.assertFalse(json.loads(out.record)['observation']['operational'])

if __name__ == '__main__': unittest.main(verbosity=2)

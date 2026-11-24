import copy
import hashlib
import hmac
import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from adapter import canonical
from shared_gateway import SharedGateway, sha
from test_adapter import RAW, NO, YES
from selector_v2.core import PartitionRef
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.evidence_store import EvidenceLedger
from selector_v2.schema import identity


class Integration(unittest.TestCase):
    def reg(self, g, aid='a1', rid='q', owner=None, **kw):
        return g.register([0, 1, 2] if owner is None else owner, rid, aid, **kw)

    def payload(self, q, template=NO, **kw):
        p = copy.deepcopy(template); p['request'] = q; p.update(kw)
        return p

    def replay(self, g):
        e = g.export(); core = EvidenceLedger(g.sample)
        self.assertTrue(core.append(e['records']), core.quarantine)
        self.assertEqual(list(core.owner), e['owner'])
        for r in e['records']:
            if r['kind'] == 'OBSERVATION':
                p = r['payload']
                for field in ('response_digest', 'receipt_digest'):
                    if p[field] is not None:
                        self.assertEqual(sha(bytes.fromhex(e['artifacts'][p[field]])), p[field])
        return e

    def test_actual_roundtrip(self):
        g = SharedGateway(RAW)
        result = component_closure(g.sample)
        self.assertTrue(g.append_raw(result['records'] + [structural_record(g.sample, PartitionRef(tuple(result['owner'])))]))
        q = self.reg(g, positive_map=[['p', 0], ['empty', 1]], negative_map=[['n', 0], ['dup', 1], ['long', 2]])
        self.assertEqual(g.original_id('a1', 'negative', 'dup'), 1)
        raw = canonical(self.payload(q)); out = g.ingest('a1', raw)
        self.assertEqual(out.status, 'PROJECTION_NO'); self.assertFalse(out.operational)
        e = self.replay(g); p = e['records'][-1]['payload']
        self.assertEqual(p['feedback']['tables'][0], {'group': 0, 'named_zeros': [{'negative': 0, 'positive': 0}], 'anonymous_zeros': [1], 'free_groups': [[2]]})
        self.assertEqual(p['response_digest'], sha(raw))
        self.assertEqual(e['owner'], result['owner'])
        self.assertEqual(json.loads(bytes.fromhex(e['registrations'][identity(q)]))['maps']['negative']['dup'], 1)

    def test_global_attempt_and_retry(self):
        g = SharedGateway(RAW); q = self.reg(g)
        with self.assertRaises(ValueError): self.reg(g, rid='different')
        self.assertEqual(g.ingest('a1', None).status, 'UNKNOWN')
        self.assertEqual(g.status('a1'), 'UNKNOWN')
        self.assertEqual(g.ingest('a1', canonical(self.payload(q))).status, 'UNKNOWN')
        with self.assertRaises(ValueError): self.reg(g, aid='a2', origin='EXTERNAL')
        q2 = self.reg(g, aid='a2'); out = g.ingest('a2', canonical(self.payload(q2)))
        self.assertTrue(out.candidate_pending); self.assertEqual(out.status, 'PROJECTION_NO')
        e = self.replay(g); self.assertEqual([r['payload']['status'] for r in e['records'] if r['kind']=='OBSERVATION'], ['UNKNOWN', 'PROJECTION_NO'])

    def test_corrupt_payload_no_partial_feedback(self):
        for mutation in [lambda p:p['tables'][-1]['zeros'].pop(), lambda p:p.update(origin='EXTERNAL'), lambda p:p['request'].update(attempt_id='old'), lambda p:p['request']['scope'].update(sample_digest='0'*64), lambda p:p['tables'][0]['zeros'][0].update(positive=None)]:
            g = SharedGateway(RAW); q = self.reg(g); p = self.payload(q); mutation(p)
            out = g.ingest('a1', canonical(p)); self.assertEqual(out.status, 'UNKNOWN'); self.assertTrue(out.candidate_pending)
            e = self.replay(g); self.assertEqual(len(e['records']), 2)
            self.assertIsNone(e['records'][-1]['payload']['feedback']); self.assertEqual(e['owner'], [0,1,2])
        g = SharedGateway(RAW); self.reg(g)
        self.assertEqual(g.ingest('a1', b'{"status":"ACCEPT","status":"NO"}').status, 'UNKNOWN')
        self.replay(g)

    def test_bounded_vs_projection(self):
        g = SharedGateway(RAW); q = self.reg(g, capacities=[1,1,1]); self.assertEqual(g.ingest('a1', canonical(self.payload(q))).status, 'PROJECTION_NO')
        q = self.reg(g, 'a2', 'b', [0,0,2], capacities=[1,1]); p = {k:v for k,v in self.payload(q).items() if k not in ('failed','tables')}; p.update(status='BOUNDED_NO', exact=True)
        out = g.ingest('a2', canonical(p)); self.assertEqual(out.status, 'BOUNDED_NO'); self.assertEqual(out.scope,'NONE'); self.assertTrue(out.candidate_pending)
        e = self.replay(g); self.assertIsNone(e['records'][-1]['payload']['feedback'])

    def test_external_receipt_binding_and_reuse(self):
        key = b'test-only-key'; signed = set()
        def auth(q, raw, reg):
            return hmac.digest(key, q+b'\0'+raw+b'\0'+reg, 'sha256') in signed
        g = SharedGateway(RAW, authenticate=auth)
        def sign(q, p):
            raw = canonical(p); reg = bytes.fromhex(g.export()['registrations'][identity(q)])
            signed.add(hmac.digest(key, canonical(q)+b'\0'+raw+b'\0'+reg, 'sha256')); return raw
        q = self.reg(g, owner=[0,0,2], origin='EXTERNAL'); p = self.payload(q, YES, origin='EXTERNAL', receipt='r1')
        raw = sign(q,p); out = g.ingest('a1',raw); self.assertEqual(out.status,'ACCEPT'); self.assertFalse(out.operational); self.assertTrue(out.candidate_pending)
        q2 = self.reg(g, 'a2', owner=[0,0,2], origin='EXTERNAL'); p2 = self.payload(q2,YES,origin='EXTERNAL',receipt='r1')
        self.assertEqual(g.ingest('a2',sign(q2,p2)).status,'UNKNOWN')  # same receipt rejected by actual core
        q3 = self.reg(g, 'a3', owner=[0,0,2], origin='EXTERNAL'); p3 = self.payload(q3,YES,origin='EXTERNAL',receipt='r3')
        sign(q3,p3); p3['receipt']='tampered'; self.assertEqual(g.ingest('a3',canonical(p3)).status,'UNKNOWN')
        e=self.replay(g); obs=[r['payload'] for r in e['records'] if r['kind']=='OBSERVATION']; self.assertEqual([r['status'] for r in obs],['ACCEPT','UNKNOWN','UNKNOWN']); self.assertEqual(obs[0]['receipt_digest'],sha(b'r1')); self.assertIsNone(obs[1]['receipt_digest'])

    def test_single_writer_concurrent(self):
        g=SharedGateway(RAW); q=self.reg(g); raw=canonical(self.payload(q))
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes=list(pool.map(lambda _:g.ingest('a1',raw),range(16)))
        self.assertEqual(sum(o.committed for o in outcomes),1); self.assertEqual(sum(o.status=='UNKNOWN' for o in outcomes),15); self.assertEqual(len(self.replay(g)['records']),2)

if __name__ == '__main__': unittest.main(verbosity=2)

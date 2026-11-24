import copy
import hashlib
import hmac
import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import adapter
from adapter import canonical, request
from gateway import open_gateway
from selector_v2.core import Sample, PartitionRef, Budget
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.registered_ledger import RegisteredLedger, NO_RESPONSE_DIGEST
from selector_v2.schema import identity, raw_record, scope
from test_adapter import RAW, NO, YES


def sha(data):
    return hashlib.sha256(data).hexdigest()


def response(q, template=NO, **kw):
    p = copy.deepcopy(template); p['request'] = q; p.update(kw); return p


def events(g):
    return json.loads(g.export())['events']


def reg(g, aid, rid='r', owner=None, **kw):
    return g.register([0,1,2] if owner is None else owner, rid, aid, **kw)


class SignedFixture:
    def __init__(self):
        self.tags = set()

    def tag(self, q, raw, entry):
        return hmac.digest(b'fixture-only', q+b'\0'+raw+b'\0'+entry, 'sha256')

    def auth(self, q, raw, entry):
        return self.tag(q, raw, entry) in self.tags

    def sign(self, g, q, p, *, wrong_entry=False):
        entry = next(e['registered'] for e in events(g) if e['event']=='REGISTER' and e['registered']['request']==q)
        if wrong_entry:
            entry['maps']['negative'] = None
        raw = canonical(p)
        self.tags.add(self.tag(canonical(q), raw, canonical(entry)))
        return raw


class DelegationTests(unittest.TestCase):
    def test_exact_core_authority_and_version(self):
        g = open_gateway(RAW)
        self.assertIs(type(g), RegisteredLedger)
        self.assertEqual(json.loads(g.export())['version'], 'selector-v2-journal/2')
        self.assertFalse(any(k in vars(g) for k in ('_ledger','_records','_registrations','_artifacts','_attempts')))
        with patch('gateway.JOURNAL_VERSION','selector-v2-journal/1'):
            with self.assertRaises(ValueError): open_gateway(RAW)

    def test_raw_and_table_conversion(self):
        g = open_gateway(RAW); s = Sample.from_input(RAW)
        c = component_closure(s)
        g.append_raw(c['records']+[structural_record(s,PartitionRef(tuple(c['owner'])))])
        q = reg(g,'a',positive_map=[['p',0],['empty',1]],negative_map=[['n',0],['duplicate',1],['long',2]])
        self.assertEqual(g.original_id('r','a','negative','duplicate'),1)
        raw = json.dumps(response(q),ensure_ascii=False,indent=2).encode()
        self.assertEqual(g.ingest('r','a',raw),'PROJECTION_NO')
        e = events(g)[-1]; p = e['records'][0]['payload']
        self.assertEqual(bytes.fromhex(e['wire_hex']),raw)
        self.assertEqual(p['response_digest'],sha(raw))
        self.assertEqual(e['normalized_sha256'],sha(bytes.fromhex(e['normalized_hex'])))
        self.assertEqual(p['feedback']['tables'][0],dict(group=0,named_zeros=[dict(negative=0,positive=0)],anonymous_zeros=[1],free_groups=[[2]]))
        self.assertEqual(g.pending_candidates,('r',))
        old = g.export(); records = g.records; records[0]['payload'].clear()
        self.assertEqual(g.export(),old)
        with self.assertRaises(ValueError): g.append_raw([raw_record(s,'REQUEST',q)])
        self.assertEqual(g.export(),old)

    def test_retry_and_global_ids(self):
        g = open_gateway(RAW); q = reg(g,'a'); before = g.export()
        with self.assertRaises(ValueError): reg(g,'a','other')
        with self.assertRaises(ValueError): reg(g,'b',origin='EXTERNAL')
        with self.assertRaises(ValueError): reg(g,'b',capacities=[1,1,1])
        self.assertEqual(g.export(),before)
        self.assertEqual(g.ingest('wrong','a',b'bad'),'UNKNOWN')
        self.assertEqual(g.attempt_status('r','a'),'PENDING')
        self.assertEqual(events(g)[-1]['records'],[])
        self.assertEqual(g.ingest('r','a',None),'UNKNOWN')
        self.assertEqual(g.records[-1]['payload']['response_digest'],NO_RESPONSE_DIGEST)
        self.assertEqual(g.attempt_status('r','a'),'UNKNOWN')
        self.assertEqual(g.ingest('r','a',canonical(response(q))),'UNKNOWN')
        self.assertEqual(events(g)[-1]['records'],[])
        q = reg(g,'b'); self.assertEqual(g.ingest('r','b',canonical(response(q))),'PROJECTION_NO')
        self.assertEqual(g.pending_candidates,('r',))

    def test_strict_rejections(self):
        for name, mutate in [('origin',lambda p:p.update(origin='EXTERNAL')),('receipt',lambda p:p.update(receipt=False)),('binding',lambda p:p['request'].update(attempt_id='old')),('table',lambda p:p['tables'].pop()),('witness',lambda p:p['tables'][0]['zeros'][0].update(positive=None)),('stale',lambda p:p['request']['scope'].update(sample_digest='0'*64))]:
            with self.subTest(name=name):
                g=open_gateway(RAW); q=reg(g,'a'); p=response(q); mutate(p)
                self.assertEqual(g.ingest('r','a',canonical(p)),'UNKNOWN')
                self.assertIsNone(g.records[-1]['payload']['feedback'])
                self.assertEqual(len(g.records),2)
        for raw in [b'{"a":1,"a":2}',b'{"n":1.0}',b'{"n":NaN}',b'\xff']:
            g=open_gateway(RAW); reg(g,'a'); self.assertEqual(g.ingest('r','a',raw),'UNKNOWN')
            self.assertEqual(events(g)[-1]['wire_sha256'],sha(raw))

    def test_receipt_exact_bytes_and_metadata(self):
        f=SignedFixture(); g=open_gateway(RAW,authenticate=f.auth)
        maps=dict(negative_map=[['n',0],['dup',1],['long',2]])
        for i, mode in enumerate(('valid','reuse','whitespace','wrong_map','unsigned')):
            aid=str(i); q=reg(g,aid,owner=[0,0,2],origin='EXTERNAL',**maps)
            p=response(q,YES,origin='EXTERNAL',receipt='receipt' if i<2 else 'receipt-'+aid)
            raw=canonical(p) if mode=='unsigned' else f.sign(g,q,p,wrong_entry=mode=='wrong_map')
            if mode=='whitespace': raw=json.dumps(p,indent=2).encode()
            self.assertEqual(g.ingest('r',aid,raw),'ACCEPT' if i==0 else 'UNKNOWN')
        observed=[e for e in events(g) if e['event']=='OBSERVE']
        self.assertEqual(len(observed),1)
        e=observed[0]; self.assertEqual(e['receipt_ref'],sha(b'receipt'))
        self.assertEqual(e['records'][0]['payload']['receipt_digest'],e['receipt_ref'])
        self.assertFalse(json.loads(bytes.fromhex(e['normalized_hex']))['operational'])
        self.assertEqual(g.pending_candidates,('r',))
        g=open_gateway(RAW); q=reg(g,'a',owner=[0,0,2],origin='EXTERNAL')
        self.assertEqual(g.ingest('r','a',canonical(response(q,YES,origin='EXTERNAL'))),'UNKNOWN')

    def test_bounded_and_dfa(self):
        g=open_gateway(RAW); q=reg(g,'a',capacities=[1,1,1])
        self.assertEqual(g.ingest('r','a',canonical(response(q))),'PROJECTION_NO')
        q=reg(g,'b','bounded',[0,0,2],capacities=[1,1]); p=response(q)
        del p['failed'],p['tables']; p.update(status='BOUNDED_NO',exact=True)
        self.assertEqual(g.ingest('bounded','b',canonical(p)),'BOUNDED_NO')
        self.assertIsNone(g.records[-1]['payload']['feedback'])
        q=reg(g,'c','dfa',[0,0,2]); p=response(q,YES); p['dfas'][0]['transitions'].pop()
        self.assertEqual(g.ingest('dfa','c',canonical(p)),'UNKNOWN')
        q=reg(g,'d','dfa',[0,0,2]); self.assertEqual(g.ingest('dfa','d',canonical(response(q,YES))),'ACCEPT')
        self.assertEqual(g.pending_candidates,('bounded','dfa','r'))

    def test_concurrent_and_atomic_raw(self):
        g=open_gateway(RAW)
        def register(i):
            try: reg(g,'same',str(i)); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=8) as pool: self.assertEqual(sum(pool.map(register,range(16))),1)
        self.assertEqual(len(g.records),1)
        q=g.records[0]['payload']; raw=canonical(response(q)); rid=q['request_id']
        with ThreadPoolExecutor(max_workers=8) as pool: out=list(pool.map(lambda _:g.ingest(rid,'same',raw),range(16)))
        self.assertEqual(out.count('PROJECTION_NO'),1); self.assertEqual(len(g.records),2)
        s=Sample.from_input(RAW); c=component_closure(s); bad=copy.deepcopy(c['records']); bad[-1]['sample_digest']='0'*64
        before=g.export()
        with self.assertRaises(ValueError): g.append_raw(bad)
        self.assertEqual(g.export(),before)

    def test_reentrant_auth_rejected(self):
        def auth(*_):
            g.register([0,1,2],'injected','injected'); return True
        g=open_gateway(RAW,authenticate=auth); q=reg(g,'a',owner=[0,0,2],origin='EXTERNAL')
        self.assertEqual(g.ingest('r','a',canonical(response(q,YES,origin='EXTERNAL'))),'UNKNOWN')
        self.assertEqual(len(g.records),2); self.assertEqual(g.pending_candidates,('r',))


if __name__=='__main__': unittest.main()

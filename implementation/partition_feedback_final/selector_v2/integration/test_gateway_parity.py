"""Latest interface gateway is a reference only; compare its v1 record projection."""
import hashlib
import hmac
import json
import unittest

import adapter
from strict_ledger import parse
from shared_gateway import SharedGateway
from selector_v2.core import Sample, PartitionRef
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.registered_ledger import RegisteredLedger
from selector_v2.schema import canonical, scope
from selector_v2.integration.audit_journal import replay_journal
from selector_v2.integration.test_roundtrip import RAW, response, tables, trie_dfa


class GatewayParityTests(unittest.TestCase):
    def test_latest_gateway_projection_and_auth_binding(self):
        signed=set(); key=b'fixture-only-key'
        def tag(q,b,r): return hmac.digest(key,q+b'\0'+b+b'\0'+r,'sha256')
        def auth(q,b,r): return tag(q,b,r) in signed
        actual=RegisteredLedger(RAW,adapter=adapter,parse=parse,authenticate=auth)
        reference=SharedGateway(RAW,authenticate=auth)
        sample=Sample.from_input(RAW); closure=component_closure(sample)
        batch=closure['records']+[structural_record(sample,PartitionRef(tuple(closure['owner']))) ]
        actual.append_raw(batch); self.assertTrue(reference.append_raw(batch))
        def reg(owner,rid,aid,**kw):
            q=actual.register(owner,rid,aid,**kw)
            self.assertEqual(q,reference.register(owner,rid,aid,**kw)); return q
        def observe(rid,aid,raw,expected):
            self.assertEqual(actual.ingest(rid,aid,raw),expected)
            outcome=reference.ingest(aid,raw)
            self.assertEqual(outcome.status,expected)
            self.assertFalse(outcome.operational); self.assertTrue(outcome.candidate_pending)
            self.assertEqual(actual.export_records(),canonical(reference.export()['records']))
        def sign(q,p):
            raw=canonical(p)
            entry=next(e['registered'] for e in json.loads(actual.export())['events']
                       if e['event']=='REGISTER' and e['registered']['request']['attempt_id']==q['attempt_id'])
            signed.add(tag(canonical(q),raw,canonical(entry))); return raw
        owner=[0,1,2,3]; merged=[0,0,0,0]
        q=reg(owner,'sim','a'); observe('sim','a',None,'UNKNOWN')
        q=reg(owner,'sim','b'); observe('sim','b',canonical(response(q,'PROJECTION_NO','sim',failed=0,tables=tables(RAW,q,0))),'PROJECTION_NO')
        q=reg(owner,'bounded','c',capacities=[1,1,1,1]); observe('bounded','c',canonical(response(q,'BOUNDED_NO','sim',exact=True)),'BOUNDED_NO')
        maps=dict(positive_map=[['p'+str(i),i] for i in range(4)],negative_map=[['n'+str(i),i] for i in range(5)])
        q=reg(merged,'ext','d',origin='EXTERNAL',**maps)
        self.assertEqual(actual.original_id('ext','d','negative','n4'),reference.original_id('d','negative','n4'))
        p=response(q,'ACCEPT','receipt',origin='EXTERNAL',dfas=[trie_dfa(RAW)])
        observe('ext','d',sign(q,p),'ACCEPT')
        self.assertEqual(actual.records[-1]['payload']['receipt_digest'],hashlib.sha256(b'receipt').hexdigest())
        q=reg(merged,'ext','e',origin='EXTERNAL',**maps); p=response(q,'ACCEPT','receipt',origin='EXTERNAL',dfas=[trie_dfa(RAW)])
        observe('ext','e',sign(q,p),'UNKNOWN')
        q=reg(merged,'ext','f',origin='EXTERNAL',**maps); p=response(q,'ACCEPT','fresh',origin='EXTERNAL',dfas=[trie_dfa(RAW)])
        sign(q,p); observe('ext','f',json.dumps(p,indent=2).encode(),'UNKNOWN')
        q=reg(merged,'ext','g',origin='EXTERNAL',**maps); p=response(q,'ACCEPT','fresh',origin='EXTERNAL',dfas=[trie_dfa(RAW)])
        wrong_entry={'request':q,'origin':'EXTERNAL','capacities':None,'maps':{'positive':None,'negative':None}}
        raw=canonical(p); signed.add(tag(canonical(q),raw,canonical(wrong_entry)))
        observe('ext','g',raw,'UNKNOWN')
        result=replay_journal(RAW,scope(sample),actual.export())
        self.assertEqual(result['proof']['operational_status'],'INCOMPLETE')
        self.assertEqual(result['proof']['structural_optimum'],2)
        print('latest gateway parity:',len(actual.records),'byte-identical v1 records; exact-byte and registration auth binding PASS')


if __name__=='__main__': unittest.main()

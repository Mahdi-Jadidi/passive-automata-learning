"""Outer journal roundtrip and tampering tests, using real producer/adapter events."""
import copy
import json
import os
from pathlib import Path
import unittest

import adapter
from strict_ledger import parse
from independent_replay import InvalidProof
from selector_v2.core import Sample, PartitionRef
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.registered_ledger import RegisteredLedger
from selector_v2.schema import canonical, scope
from selector_v2.integration.audit_journal import replay_journal, encoded, sha, digest
from selector_v2.integration.test_roundtrip import RAW, response, tables, trie_dfa


def fixture():
    s=Sample.from_input(RAW)
    ledger=RegisteredLedger(RAW,adapter=adapter,parse=parse,authenticate=lambda q,p,r: True)
    closure=component_closure(s)
    ledger.append_raw(closure['records']+[structural_record(s,PartitionRef(tuple(closure['owner'])))])
    owner=[0,1,2,3]; maps=dict(positive_map=[['p'+str(i),i] for i in range(4)],negative_map=[['n'+str(i),i] for i in range(5)])
    q=ledger.register(owner,'r','a',origin='EXTERNAL',**maps)
    ledger.ingest('r','a',b'{"status":1,"status":2}')
    q=ledger.register(owner,'r','b',origin='EXTERNAL',**maps)
    p=response(q,'PROJECTION_NO','r1',origin='EXTERNAL',failed=0,tables=tables(RAW,q,0))
    ledger.ingest('r','b',canonical(p))
    ledger.ingest('r','b',canonical(p))
    q=ledger.register(owner,'bounded','c',capacities=[1,1,1,1])
    ledger.ingest('bounded','c',canonical(response(q,'BOUNDED_NO','r2',exact=True)))
    q=ledger.register([0,0,0,0],'accept','d',origin='EXTERNAL')
    ledger.ingest('accept','d',canonical(response(q,'ACCEPT','r3',origin='EXTERNAL',dfas=[trie_dfa(RAW)])))
    ledger.register(owner,'pending','e')
    ledger.ingest('wrong','e',None)
    return s,ledger


def event(j,kind,aid=None):
    return next(e for e in j['events'] if e['event']==kind and (aid is None or (e.get('attempt_id') or e.get('registered',{}).get('request',{}).get('attempt_id'))==aid))


def rewrite_observation(e, transform, *, wire=False):
    normal=json.loads(bytes.fromhex(e['normalized_hex']))
    transform(normal)
    b=encoded(normal); e['normalized_hex']=b.hex(); e['normalized_sha256']=sha(b)
    if wire:
        b=encoded(normal['payload']); e['wire_hex']=b.hex(); e['wire_sha256']=sha(b)
        e['records'][0]['payload']['response_digest']=sha(b)


class JournalAuditTests(unittest.TestCase):
    def test_full_outer_roundtrip(self):
        s,ledger=fixture(); result=replay_journal(RAW,scope(s),ledger.export())
        self.assertEqual(encoded(result['records']),ledger.export_records())
        self.assertEqual(result['proof']['mandatory_owner'],(0,0,0,3))
        self.assertEqual(result['proof']['structural_optimum'],2)
        self.assertEqual(result['proof']['operational_status'],'INCOMPLETE')
        self.assertEqual(result['attempt_status'],{'a':'UNKNOWN','b':'PROJECTION_NO','c':'BOUNDED_NO','d':'ACCEPT','e':'PENDING'})
        self.assertEqual(result['pending_candidates'],ledger.pending_candidates)
        self.assertEqual(result['quarantine'],3)
        artifact=os.environ.get('P2_ADVERSARIAL_ARTIFACT')
        if artifact:
            Path(artifact).write_bytes(encoded(dict(raw=RAW,scope=scope(s),journal=json.loads(ledger.export()),result=result)))
        print('outer replay:',len(ledger.journal),'events,',len(result['records']),'records,',result['quarantine'],'quarantines')

    def test_corruptions(self):
        s,ledger=fixture(); original=json.loads(ledger.export())
        def duplicate_attempt(j):
            e=event(j,'REGISTER','e'); e['registered']['request']['attempt_id']='a'; e['records'][0]['payload']['attempt_id']='a'
        def receipt_reuse(j):
            e=event(j,'OBSERVE','d'); rewrite_observation(e,lambda o:o['payload'].update(receipt='r1'),wire=True); e['receipt_ref']=sha(b'r1'); e['records'][0]['payload']['receipt_digest']=sha(b'r1')
        def corrupt_dfa(j):
            e=event(j,'OBSERVE','d'); rewrite_observation(e,lambda o:o['payload']['dfas'][0]['transitions'].pop(),wire=True)
        def change_map(j):
            # A valid bijection but inconsistent with the first registered retry target.
            e=event(j,'REGISTER','b'); m=e['registered']['maps']['positive']; m['p0'],m['p1']=m['p1'],m['p0']
        mutations=[
            lambda j:j.update(sample_digest='0'*64),
            lambda j:event(j,'REGISTER','b')['registered'].update(origin='SIMULATOR'),
            lambda j:event(j,'REGISTER','a')['registered']['maps']['positive'].update(p0=True),
            change_map,
            lambda j:event(j,'REGISTER','c')['registered']['capacities'].__setitem__(0,2),
            duplicate_attempt,
            lambda j:event(j,'OBSERVE','b').update(wire_sha256='0'*64),
            lambda j:event(j,'OBSERVE','b').update(normalized_sha256='0'*64),
            lambda j:rewrite_observation(event(j,'OBSERVE','b'),lambda o:o.update(operational=True)),
            lambda j:rewrite_observation(event(j,'OBSERVE','b'),lambda o:o['payload'].update(receipt='changed')),
            lambda j:event(j,'OBSERVE','b')['records'][0]['payload'].update(receipt_digest='0'*64),
            lambda j:event(j,'OBSERVE','b')['records'][0]['payload']['feedback'].update(tables=[]),
            receipt_reuse,
            corrupt_dfa,
            lambda j:event(j,'QUARANTINE','a')['records'].clear(),
            lambda j:event(j,'QUARANTINE','e')['records'].append(event(j,'QUARANTINE','a')['records'][0]),
            lambda j:event(j,'OBSERVE','b').update(request_id='wrong'),
            lambda j:event(j,'RAW')['records'].append(event(j,'REGISTER','a')['records'][0]),
            lambda j:next(r for r in event(j,'RAW')['records'] if r['kind']=='COMPONENT_EPOCH' and not r['payload']['edges'])['payload']['facts'].pop(),
        ]
        for i,mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                bad=copy.deepcopy(original); mutate(bad)
                with self.assertRaises(InvalidProof): replay_journal(RAW,scope(s),encoded(bad))
        with self.assertRaises(InvalidProof): replay_journal(RAW,scope(s),b'{"version":1,"version":2}')
        print('outer provenance corruptions rejected:',len(mutations)+1)

    def test_untrusted_and_reentrant_authentication(self):
        s=Sample.from_input(RAW)
        for callback in (None,lambda q,p,r:False):
            ledger=RegisteredLedger(RAW,adapter=adapter,parse=parse,authenticate=callback)
            q=ledger.register([0,0,0,0],'r','a',origin='EXTERNAL')
            wire=canonical(response(q,'ACCEPT','r1',origin='EXTERNAL',dfas=[trie_dfa(RAW)]))
            self.assertEqual(ledger.ingest('r','a',wire),'UNKNOWN')
            result=replay_journal(RAW,scope(s),ledger.export())
            self.assertEqual(result['attempt_status'],{'a':'UNKNOWN'})
            self.assertEqual(result['pending_candidates'],('r',))
            self.assertEqual(result['proof']['operational_status'],'INCOMPLETE')
        def reenter(q,p,r):
            ledger.register([0,0,0,0],'nested','nested')
            return True
        ledger=RegisteredLedger(RAW,adapter=adapter,parse=parse,authenticate=reenter)
        q=ledger.register([0,0,0,0],'r','a',origin='EXTERNAL')
        wire=canonical(response(q,'ACCEPT','r1',origin='EXTERNAL',dfas=[trie_dfa(RAW)]))
        self.assertEqual(ledger.ingest('r','a',wire),'UNKNOWN')
        self.assertEqual(replay_journal(RAW,scope(s),ledger.export())['attempt_status'],{'a':'UNKNOWN'})
        self.assertEqual(len(ledger.journal),2)

    def test_raw_atomic_rollback(self):
        s=Sample.from_input(RAW); ledger=RegisteredLedger(RAW,adapter=adapter,parse=parse)
        good=component_closure(s)['records']; bad=copy.deepcopy(good); bad[-1]['payload']['result_owner']=[0,1,2,3]
        before=ledger.export()
        with self.assertRaises(ValueError): ledger.append_raw(bad)
        self.assertEqual(ledger.export(),before)
        ledger.append_raw(good)
        self.assertEqual(replay_journal(RAW,scope(s),ledger.export())['proof']['mandatory_owner'],(0,0,0,3))


if __name__=='__main__': unittest.main()

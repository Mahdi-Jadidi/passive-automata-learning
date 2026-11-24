"""Actual cross-stream integration; run through the pinned-source runner."""
import copy
import json
import os
from pathlib import Path
import unittest
from concurrent.futures import ThreadPoolExecutor

import adapter
from strict_ledger import parse
from ledger_replay import replay_ledger_json
from independent_replay import InvalidProof
from selector_v2.core import Budget, PartitionRef, Sample
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.registered_ledger import RegisteredLedger
from selector_v2.schema import canonical, scope, identity, raw_record

RAW = {'alphabet':['β','a','😀','unused'], 'positive':[['β','a'],['😀'],['β','a'],[]],
       'negative':[['a','β'],['β','a','😀'],['β','a','😀'],['β','β'],['β','β']]}


def response(q, status, receipt, origin='SIMULATOR', **kw):
    return dict(version=q['version'], request=q, origin=origin, status=status,
                complete=True, receipt=receipt, **kw)


def tables(raw, q, failed):
    _, alphabet, X, Y = adapter.encode_sample(raw)
    p = q['owner']; out = []
    for g in sorted(set(p)):
        proj = lambda w: tuple(a for a in w if p[a] == g)
        pp = [proj(x) for x in X]; zeros = []; free = {}
        for i,y in enumerate(Y):
            w = proj(y)
            if w in pp:
                zeros.append(dict(negative=i,positive=pp.index(w) if i == failed else None))
            else:
                free.setdefault(w,[]).append(i)
        out.append(dict(block=g,kind='UNRESTRICTED_BASE',complete=True,zeros=zeros,free=list(free.values())))
    return out


def trie_dfa(raw):
    _, alphabet, X, _ = adapter.encode_sample(raw)
    paths = {():0}
    for x in X:
        for k in range(1,len(x)+1):
            prefix = tuple(x[:k]); paths.setdefault(prefix,len(paths))
    sink = len(paths)
    return dict(block=0, states=sink+1, initial=0, accepting=sorted({paths[tuple(x)] for x in X}),
                transitions=[[state,a,paths.get(prefix+(a,),sink)] for prefix,state in paths.items()
                             for a in range(len(alphabet))]+[[sink,a,sink] for a in range(len(alphabet))])


def replay(raw, journal):
    s = Sample.from_input(raw)
    return replay_ledger_json(canonical(raw),canonical(scope(s)),journal.export_records())


class RoundtripTests(unittest.TestCase):
    def make(self, raw=RAW):
        return RegisteredLedger(raw,adapter=adapter,parse=parse,authenticate=lambda q,p,r: True)

    def test_actual_producer_adapter_proof(self):
        s = Sample.from_input(RAW); ledger = self.make()
        closure = component_closure(s)
        self.assertEqual(closure['owner'],[0,0,0,3])
        ledger.append_raw(closure['records']+[structural_record(s,PartitionRef(tuple(closure['owner'])))])
        q = ledger.register([0,1,2,3],'root','a1',positive_map=[['p'+str(i),i] for i in range(4)],
                            negative_map=[['n'+str(i),i] for i in range(5)])
        self.assertEqual(ledger.original_id('root','a1','positive','p2'),2)
        data = response(q,'PROJECTION_NO','sim1',failed=0,tables=tables(RAW,q,0))
        wire = json.dumps(data,ensure_ascii=False,indent=2).encode()
        self.assertEqual(ledger.ingest('root','a1',wire),'PROJECTION_NO')
        converted = ledger.records[-1]['payload']['feedback']
        self.assertTrue(any(t['anonymous_zeros'] for t in converted['tables']))
        self.assertTrue(any(t['free_groups'] for t in converted['tables']))
        q2 = ledger.register([0,1,2,3],'bounded','a2',capacities=[1,1,1,1])
        self.assertEqual(ledger.ingest('bounded','a2',canonical(response(q2,'BOUNDED_NO','sim2',exact=True))),'BOUNDED_NO')
        q3 = ledger.register([0,0,0,0],'accept','a3',origin='EXTERNAL')
        self.assertEqual(ledger.ingest('accept','a3',canonical(response(q3,'ACCEPT','mock-external',origin='EXTERNAL',dfas=[trie_dfa(RAW)]))),'ACCEPT')
        q4 = ledger.register([0,0,0,0],'simaccept','a4')
        self.assertEqual(ledger.ingest('simaccept','a4',canonical(response(q4,'ACCEPT','sim4',dfas=[trie_dfa(RAW)]))),'ACCEPT')
        out = replay(RAW,ledger)
        self.assertEqual(out['mandatory_owner'],(0,0,0,3))
        self.assertEqual(out['structural_optimum'],2)
        self.assertEqual(out['structural_no_request_digests'],(identity(q),))
        self.assertEqual(out['operational_status'],'INCOMPLETE')
        self.assertEqual(ledger.pending_candidates,('accept','bounded','root','simaccept'))
        events = json.loads(ledger.export())['events']
        event = next(e for e in events if e['event']=='OBSERVE')
        self.assertEqual(bytes.fromhex(event['wire_hex']),wire)
        self.assertEqual(identity(json.loads(bytes.fromhex(event['normalized_hex']))),event['normalized_sha256'])
        self.assertEqual(event['records'][0]['payload']['response_digest'],event['wire_sha256'])
        events[0]['records'].clear(); self.assertTrue(ledger.records)
        artifact = os.environ.get('P2_ARTIFACT')
        if artifact:
            Path(artifact).write_bytes(canonical(dict(raw=RAW,scope=scope(s),journal=json.loads(ledger.export()),
                                                      records=json.loads(ledger.export_records()),proof=out)))
        print('actual roundtrip:',len(closure['records']),'epochs,',len(ledger.records),'records,',len(ledger.journal),'events, structural optimum',out['structural_optimum'])

    def test_transaction_rejections_and_retry(self):
        ledger=self.make(); owner=[0,1,2,3]
        q=ledger.register(owner,'r','a',origin='EXTERNAL')
        before=ledger.export()
        with self.assertRaises(ValueError): ledger.register(owner,'other','a')
        with self.assertRaises(ValueError): ledger.register(owner,'r','b',origin='SIMULATOR')
        with self.assertRaises(ValueError): ledger.append_raw([raw_record(Sample.from_input(RAW),'REQUEST',q)])
        self.assertEqual(ledger.export(),before)
        bad=response(q,'PROJECTION_NO','x',failed=0,tables=tables(RAW,q,0))
        self.assertEqual(ledger.ingest('r','a',canonical(bad)),'UNKNOWN')
        self.assertEqual(ledger.attempt_status('r','a'),'UNKNOWN')
        self.assertEqual(ledger.pending_candidates,('r',))
        q2=ledger.register(owner,'r','b',origin='EXTERNAL')
        good=response(q2,'PROJECTION_NO','ext1',origin='EXTERNAL',failed=0,tables=tables(RAW,q2,0))
        self.assertEqual(ledger.ingest('r','b',canonical(good)),'PROJECTION_NO')
        old_records=ledger.export_records()
        self.assertEqual(ledger.ingest('r','b',canonical(good)),'UNKNOWN')
        self.assertEqual(ledger.export_records(),old_records)
        q3=ledger.register(owner,'r','c',origin='EXTERNAL')
        reused=dict(good,request=q3)
        self.assertEqual(ledger.ingest('r','c',canonical(reused)),'UNKNOWN')
        q4=ledger.register(owner,'r','d',origin='EXTERNAL')
        self.assertEqual(ledger.ingest('r','d',b'{"status":1,"status":2}'),'UNKNOWN')
        q5=ledger.register(owner,'r','e',origin='EXTERNAL')
        self.assertEqual(ledger.ingest('wrong','e',b'bad'),'UNKNOWN')
        self.assertEqual(ledger.attempt_status('r','e'),'PENDING')
        q6=ledger.register(owner,'r','f',origin='EXTERNAL')
        bad_receipt=dict(good,request=q6,receipt=False)
        self.assertEqual(ledger.ingest('r','f',canonical(bad_receipt)),'UNKNOWN')
        q7=ledger.register(owner,'r','g',origin='EXTERNAL')
        bad_table=copy.deepcopy(good); bad_table.update(request=q7,receipt='ext7'); bad_table['tables'].pop()
        self.assertEqual(ledger.ingest('r','g',canonical(bad_table)),'UNKNOWN')
        q8=ledger.register(owner,'r','h',origin='EXTERNAL')
        self.assertEqual(ledger.ingest('r','h',None),'UNKNOWN')
        out=replay(RAW,ledger)
        self.assertEqual(len(out['pending_attempt_digests']),7)
        self.assertEqual(len(out['structural_no_request_digests']),1)
        self.assertEqual(out['operational_status'],'INCOMPLETE')
        self.assertEqual(len(ledger.quarantine),8)

    def test_partial_conflict_and_false_exhaustion(self):
        s=Sample.from_input(RAW); ledger=self.make()
        result=component_closure(s,Budget(work=0)); ledger.append_raw(result['records'])
        self.assertEqual(replay(RAW,ledger)['closure_state'],'PARTIAL')
        raw={'alphabet':['β','unused'],'positive':[['β']],'negative':[[]]}
        s=Sample.from_input(raw); result=component_closure(s)
        self.assertEqual(len(result['records'][0]['payload']['facts']),1)
        bad=copy.deepcopy(result['records']); bad[0]['payload']['facts']=[]
        ledger=self.make(raw); ledger.append_raw(bad)
        with self.assertRaises(InvalidProof): replay(raw,ledger)
        good=self.make(raw); good.append_raw(result['records'])
        self.assertEqual(replay(raw,good)['closure_state'],'FIXPOINT')
        raw={'alphabet':['β'],'positive':[[]],'negative':[[]]}
        s=Sample.from_input(raw); ledger=self.make(raw); ledger.append_raw(component_closure(s)['records'])
        self.assertTrue(replay(raw,ledger)['label_conflict'])

    def test_concurrent_attempt_uniqueness_and_mutation(self):
        ledger=self.make(); owner=[0,1,2,3]
        def task(i):
            try: ledger.register(owner,str(i),'one'); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(task,range(16))),1)
        self.assertEqual(len(ledger.records),1)
        owner[0]=3
        self.assertEqual(ledger.records[0]['payload']['owner'],[0,1,2,3])


if __name__=='__main__': unittest.main()

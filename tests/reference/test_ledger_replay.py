"""Independent ledger tests, exact normalized schema; receipts remain untrusted."""
import copy
import json
import unittest
from independent_replay import InvalidProof,digest
from ledger_replay import replay_ledger,replay_ledger_json
from test_production_replay import scope,rec,fixture,structural,fact


def setup():
    raw=dict(alphabet=['a','b','c'],positive=[['a','b']],negative=[['b','a'],['c'],['c'],['a','b','a']]);sc=scope(raw);sd=sc['sample_digest']
    def request(aid='a1',rid='r1',owner=None,sc=sc):
        return rec(sd,'REQUEST',dict(version='selector-v2/1',scope=sc,owner=[0,1,2] if owner is None else owner,request_id=rid,attempt_id=aid,negative_ids=[0,1,2,3]))
    def observation(req,status='PROJECTION_NO',origin='SIMULATOR',receipt=None,feedback=None):
        return dict(version='selector-v2/1',origin=origin,sample_digest=sd,kind='OBSERVATION',payload=dict(request_digest=digest(req['payload']),status=status,response_digest='a'*64,receipt_digest=receipt,feedback=feedback))
    def table(g,anonymous,free): return dict(group=g,named_zeros=[dict(negative=0,positive=0)],anonymous_zeros=anonymous,free_groups=free)
    fb=dict(kind='UNRESTRICTED_COMPLETE',failed_negative=0,tables=[table(0,[],[[1,2],[3]]),table(1,[3],[[1,2]]),table(2,[3],[[1,2]])])
    return raw,sc,request,observation,fb


class LedgerAudit(unittest.TestCase):
    def test_observations_never_accept(self):
        raw,sc,req,obs,fb=setup();a=req();b=req('a2');c=req('a3');d=req('a4');e=req('a5','r2',[0,0,2],dict(sc,regime='BOUNDED',capacity_digest='b'*64))
        records=[a,obs(a,'UNKNOWN'),b,obs(b,feedback=fb),c,obs(c,'ACCEPT','EXTERNAL','c'*64),d,e,obs(e,'BOUNDED_NO','EXTERNAL','d'*64)]
        r=replay_ledger_json(json.dumps(raw),json.dumps(sc),json.dumps(records))
        self.assertEqual(r['pending_attempt_digests'],(digest(a['payload']),digest(d['payload'])))
        self.assertEqual(r['structural_no_request_digests'],(digest(b['payload']),))
        self.assertEqual(r['mandatory_owner'],(0,1,2));self.assertEqual(r['operational_status'],'INCOMPLETE');self.assertIsNone(r['structural_optimum'])

    def test_raw_ledger_prefix(self):
        raw,sc,c=fixture();sd=sc['sample_digest'];d=rec(sd,'DELETE_EQUAL',dict(owner=[0,0,2],fact=fact(1,0,1)))
        r=replay_ledger(raw,sc,[d]);self.assertEqual(r['standalone_deletions'],1);self.assertEqual(r['mandatory_floor'],0)
        r=replay_ledger(raw,sc,[c['records'][0],d]);self.assertEqual(r['closure_state'],'OPEN');self.assertEqual(r['mandatory_floor'],1)
        s=structural(raw,c['owner']);r=replay_ledger(raw,sc,c['records']+[d,s]);self.assertEqual(r['structural_optimum'],2)
        with self.assertRaises(InvalidProof): replay_ledger(raw,sc,[d,c['records'][1]])
        with self.assertRaises(InvalidProof): replay_ledger(raw,sc,c['records']+[c['records'][-1]])
        wrong=copy.deepcopy(d);wrong['payload']['fact']['positive']=0
        with self.assertRaises(InvalidProof): replay_ledger(raw,sc,[wrong])

    def test_ledger_mutations(self):
        raw,sc,req,obs,fb=setup();a=req();o=obs(a,feedback=fb);bad=[]
        bad.extend([[o],[a,a],[a,o,o],[a,req('a2',owner=[0,0,2])],[a,obs(a,'ACCEPT','EXTERNAL')],[a,obs(a,'ACCEPT','SIMULATOR','c'*64)],[a,obs(a,'BOUNDED_NO')],[a,obs(a,'UNKNOWN',feedback=fb)],[a,obs(a,'ACCEPT',feedback=fb)]])
        b=req('a2');bad.append([a,obs(a,'ACCEPT','EXTERNAL','c'*64),b,obs(b,'UNKNOWN','EXTERNAL','c'*64)])
        for path,value in [
            (('payload','request_digest'),'0'*64),(('payload','response_digest'),'z'*64),(('payload','status'),'NO'),(('origin',),'RAW'),(('kind',),'UNKNOWN'),(('sample_digest',),'0'*64),
            (('payload','feedback','kind'),'BOUNDED_OPAQUE'),(('payload','feedback','failed_negative'),1),(('payload','feedback','tables',0,'group'),1),
            (('payload','feedback','tables',0,'named_zeros',0,'negative'),False),(('payload','feedback','tables',0,'named_zeros',0,'positive'),1),
            (('payload','feedback','tables',0,'free_groups'),[[1],[2],[3]]),(('payload','feedback','tables',0,'free_groups'),[[1,2,3]]),
            (('payload','feedback','tables',0,'free_groups'),[[1,2],[]]),(('payload','feedback','tables',0,'free_groups'),[[1,2],[2,3]]),
            (('payload','feedback','tables',0,'free_groups'),[[1,2]]),(('payload','feedback','tables',1,'anonymous_zeros'),[1]),
            (('payload','feedback','tables',0,'named_zeros'),[]),(('payload','feedback','tables'),fb['tables'][:2]),(('payload','feedback','tables'),list(reversed(fb['tables'])))]:
            x=copy.deepcopy(o);d=x
            for key in path[:-1]:d=d[key]
            d[path[-1]]=value;bad.append([a,x])
        for i,records in enumerate(bad):
            with self.subTest(i=i),self.assertRaises(InvalidProof): replay_ledger(raw,sc,records)
        self.assertEqual(replay_ledger(raw,sc,[a,o])['observations'],1)
        print(f'ledger_mutations={len(bad)}')


if __name__=='__main__':unittest.main(verbosity=2)

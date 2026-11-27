"""Exact core wire fixtures and literal exhaustive oracle, no producer imports."""
import copy
import itertools
import json
import unittest
from independent_replay import InvalidProof, sample_data
from production_replay import replay_closure, replay_serialized, verify_request


def rec(sd, kind, payload):
    return dict(version='selector-v2/1', origin='RAW', sample_digest=sd, kind=kind, payload=payload)


def scope(raw):
    return dict(version='selector-v2/1',sample_digest=sample_data(raw)[3],regime='UNRESTRICTED',family='ALL_PARTITIONS',capacity_digest=None)


def epoch(sd,k,p,f,e,q,state='EXHAUSTED',cursor=None):
    return rec(sd,'COMPONENT_EPOCH',dict(epoch=k,owner=p,facts=f,edges=e,result_owner=q,state=state,cursor=cursor))


def fact(i,g,j): return dict(negative=i,group=g,positive=j)
def edge(i,a,j,b,k): return dict(negative=i,a=a,positive_a=j,b=b,positive_b=k)


def build(raw):
    # Literal reference enumeration, deliberately different from the indexed verifier.
    n,X,Y,sd=sample_data(raw); p=list(range(n)); records=[]; k=0
    for i,y in enumerate(Y):
        for j,x in enumerate(X):
            if x==y: return dict(state='LABEL_CONFLICT',owner=p,records=[rec(sd,'LABEL_CONFLICT',dict(negative=i,positive=j))])
    while True:
        f=[]; e=[]; q=p[:]
        for i,y in enumerate(Y):
            hits=[]
            for g in sorted(set(p)):
                for j,x in enumerate(X):
                    if tuple(a for a in x if p[a]!=g)==tuple(a for a in y if p[a]!=g):
                        hits.append((g,j)); f.append(fact(i,g,j)); break
            if hits:
                a,j=hits[0]
                for b,l in hits[1:]:
                    if q[a]!=q[b]:
                        lo,hi=sorted((q[a],q[b])); q=[lo if g==hi else g for g in q]; e.append(edge(i,a,j,b,l))
        records.append(epoch(sd,k,p,f,e,q)); k+=1
        if not e: return dict(state='FIXPOINT',owner=q,records=records)
        p=q


def structural(raw,p):
    _,X,Y,sd=sample_data(raw)
    def proj(w,g): return tuple(a for a in w if p[a]==g)
    choices=[[g for g in sorted(set(p)) if all(proj(x,g)!=proj(y,g) for x in X)] for y in Y]
    ok=all(choices)
    return rec(sd,'STRUCTURAL_CHECK',dict(owner=p,compatible=ok,separating_groups=[v[0] for v in choices] if ok else [],failed_negative=None if ok else choices.index([])))


def fixture():
    raw={'alphabet':['a','b','c'],'positive':[['a','b'],['c']],'negative':[['b','a'],['a','b','c']]}
    return raw,scope(raw),build(raw)


class ProductionAudit(unittest.TestCase):
    def test_golden_core_request(self):
        raw={'alphabet':['β','a','😀'],'positive':[['β','β'],[],['β','β']],'negative':[['a','😀']]}
        sc=scope(raw)
        self.assertEqual(sc['sample_digest'],'7ddb11d457a25ee2b1d273529cf3f3e2064054dc154ebc901acb796b08708bbb')
        req=dict(version='selector-v2/1',scope=sc,owner=[0,1,1],request_id='r1',attempt_id='a1',negative_ids=[0])
        self.assertEqual(verify_request(raw,req),'1f43bbcd2081c20e84469b2220928c7a5f61674ce9a7d4bfec84e7e55285ee72')
        for key,value in [('negative_ids',[False]),('negative_ids',[]),('owner',[0,True,1]),('owner',[0,1]),('version','future'),('request_id',''),('attempt_id',1)]:
            with self.assertRaises(InvalidProof): verify_request(raw,dict(req,**{key:value}))
        stale=copy.deepcopy(raw); stale['positive'][0]=['β']
        with self.assertRaises(InvalidProof): verify_request(stale,req)
        for key,value in [('family','OTHER'),('version','future'),('sample_digest','0'*64),('capacity_digest','0'*64)]:
            with self.assertRaises(InvalidProof): verify_request(raw,dict(req,scope=dict(sc,**{key:value})))
        raw0=dict(alphabet=[],positive=[],negative=[])
        with self.assertRaises(InvalidProof): verify_request(raw0,dict(req,scope=scope(raw0),owner=[],negative_ids=[]))
        print('core_golden_vectors=2 request_mutations=13')

    def test_multi_epoch_and_partial(self):
        raw,sc,c=fixture(); self.assertEqual([r['payload']['owner'] for r in c['records']],[[0,1,2],[0,0,2],[0,0,0]])
        s=structural(raw,c['owner'])
        res=replay_serialized(json.dumps(raw),json.dumps(sc),json.dumps(c),json.dumps([s]))
        self.assertEqual(res['structural_optimum'],2); self.assertEqual(res['operational_status'],'INCOMPLETE')
        part=copy.deepcopy(c); part['records']=part['records'][:1]; part['records'][0]['payload'].update(state='PARTIAL',cursor=['negative',1]); part.update(state='PARTIAL',owner=[0,0,2])
        res=replay_closure(raw,sc,part); self.assertEqual(res['state'],'PARTIAL'); self.assertEqual(res['mandatory_floor'],1); self.assertIsNone(res['structural_optimum'])
        sc2=dict(sc,regime='BOUNDED',capacity_digest='0'*64)
        self.assertIsNone(replay_closure(raw,sc2,c,[s])['structural_optimum'])
        # Partial can still prove a structural optimum if the mandatory root is compatible.
        part=copy.deepcopy(c); part['records']=part['records'][:2]; part['records'][1]['payload'].update(state='PARTIAL',cursor=['negative',1]); part['state']='PARTIAL'
        self.assertEqual(replay_closure(raw,sc,part,[s])['structural_optimum'],2)

    def test_epoch_mutations(self):
        raw,sc,c=fixture(); s=structural(raw,c['owner']); bad=[]
        changes=[(('state',),'FIXPOINTX'),(('owner',),[0,0,2]),(('records',0,'sample_digest'),'0'*64),
                 (('records',0,'version'),'future'),(('records',0,'origin'),'EXTERNAL'),(('records',0,'kind'),'UNKNOWN'),
                 (('records',0,'payload','epoch'),False),(('records',0,'payload','epoch'),1),
                 (('records',0,'payload','owner'),[0,0,2]),(('records',0,'payload','result_owner'),[0,1,2]),
                 (('records',0,'payload','facts',0,'negative'),True),(('records',0,'payload','facts',0,'positive'),1),
                 (('records',0,'payload','facts',0,'group'),3),(('records',0,'payload','edges',0,'positive_b'),1),
                 (('records',0,'payload','edges',0,'b'),0),(('records',0,'payload','cursor'),['negative',0]),
                 (('records',1,'payload','owner'),[0,1,2]),(('records',1,'payload','epoch'),0),
                 (('records',1,'payload','edges',0,'negative'),0),(('records',1,'payload','edges',0,'a'),1)]
        for path,value in changes:
            b=copy.deepcopy(c); d=b
            for key in path[:-1]: d=d[key]
            d[path[-1]]=value; bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload']['facts'].pop(); bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload']['facts'].append(b['records'][0]['payload']['facts'][0]); bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload']['edges']=[]; bad.append(b)
        b=copy.deepcopy(c); b['records'].pop(); bad.append(b)
        b=copy.deepcopy(c); b['records'].append(b['records'][-1]); bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload'].update(state='PARTIAL',cursor=['negative',1]); bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload'].update(state='PARTIAL',cursor=['positive',0]); bad.append(b)
        b=copy.deepcopy(c); b['records'][0]['payload'].update(state='PARTIAL',cursor=['negative',9]); bad.append(b)
        b=copy.deepcopy(c); b['receipt']='ACCEPT'; bad.append(b)
        b=copy.deepcopy(c); b['records'][-1]['payload']['facts']=[]; bad.append(b)
        for i,b in enumerate(bad):
            with self.subTest(i=i),self.assertRaises(InvalidProof): replay_closure(raw,sc,b,[s])
        for key,value in [('compatible',False),('compatible',1),('owner',[0,0,2]),('separating_groups',[0]),('separating_groups',[0,1]),('failed_negative',0)]:
            with self.assertRaises(InvalidProof): replay_closure(raw,sc,c,[dict(s,payload=dict(s['payload'],**{key:value}))])
        for k in ('ACCEPT','BOUNDED_NO','UNKNOWN'):
            with self.assertRaises(InvalidProof): replay_closure(raw,sc,c,[rec(sc['sample_digest'],k,{})])
        print(f'epoch_structural_mutations={len(bad)+9}')

    def test_duplicates_empty_and_scope(self):
        for raw in [dict(alphabet=['a'],positive=[['a']],negative=[['a']]),dict(alphabet=[],positive=[],negative=[[]]),dict(alphabet=[],positive=[[]],negative=[]),dict(alphabet=['a','unused'],positive=[],negative=[[]])]:
            sc=scope(raw); c=build(raw); res=replay_closure(raw,sc,c,[structural(raw,c['owner'])]); self.assertEqual(res['label_conflict'],raw['positive']==raw['negative'] and bool(raw['positive']))
        raw=dict(alphabet=['a'],positive=[['a']],negative=[['a']]);sc=scope(raw);c=build(raw)
        b=copy.deepcopy(c); b['records'][0]['payload']['negative']=1
        with self.assertRaises(InvalidProof): replay_closure(raw,sc,b)
        b=dict(state='FIXPOINT',owner=[0],records=[epoch(sc['sample_digest'],0,[0],[],[],[0])])
        with self.assertRaises(InvalidProof): replay_closure(raw,sc,b)

    def test_exhaustive_closure(self):
        A=['a','b'];W=[[],['a'],['b'],['a','a'],['a','b'],['b','a'],['b','b']]; num=epochs=facts=checks=0
        for labels in itertools.product(range(3),repeat=len(W)):
            raw=dict(alphabet=A,positive=[w for w,l in zip(W,labels) if l==1],negative=[w for w,l in zip(W,labels) if l==2]);sc=scope(raw);c=build(raw)
            ss=[structural(raw,p) for p in ([0,1],[0,0])]; result=replay_closure(raw,sc,c,ss)
            feasible=[p for p,s in zip(([0,1],[0,0]),ss) if s['payload']['compatible']]
            optimum=min(2-len(set(p)) for p in feasible)
            self.assertLessEqual(result['mandatory_floor'],optimum)
            self.assertTrue(all(all(p[a]==p[g] for a,g in enumerate(result['mandatory_owner'])) for p in feasible))
            if result['structural_optimum'] is not None: self.assertEqual(result['structural_optimum'],optimum)
            num+=1;epochs+=result['epochs'];facts+=result['facts'];checks+=len(ss)
        print(f'production_corpora={num} epochs={epochs} deletion_facts={facts} structural_checks={checks}')


if __name__=='__main__': unittest.main(verbosity=2)

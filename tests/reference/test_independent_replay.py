"""Independent wire fixtures, adversarial mutations and exhaustive tiny replays."""
import copy
import itertools
import json
import unittest
from independent_replay import InvalidProof, digest, replay, replay_json, sample_data


def fixture():
    # ab/ba forces a,b. abc/c and abc/ab force {a,b},c at the next epoch.
    raw = {'alphabet': ['a', 'b', 'c', 'unused'],
           'positive': [['a', 'b'], ['c']], 'negative': [['b', 'a'], ['a', 'b', 'c']]}
    scope = {'sample_digest': sample_data(raw)[3], 'regime': 'UNRESTRICTED',
             'family': 'ALL_PARTITIONS', 'capacity_digest': None}
    def record(kind, **kw):
        return dict(kind=kind, origin='RAW', **kw)
    p0, p1, p2 = [0,1,2,3], [0,0,2,3], [0,0,0,3]
    records = [record('DELETE_EQUAL', owner=p0, negative=0, group=0, positive=0),
               record('COMPONENT_EDGE', epoch=0, owner=p0, negative=0, a=0, positive_a=0, b=1, positive_b=0),
               record('COMPONENT_EDGE', epoch=1, owner=p1, negative=1, a=0, positive_a=1, b=2, positive_b=0),
               record('STRUCTURAL_CHECK', owner=p2, compatible=True, separating_groups=[0,0], failed_negative=None)]
    return raw, dict(version='selector-v2/1', scope=scope, records=records)


def partitions(n):
    def rec(prefix):
        if len(prefix) == n:
            yield tuple(prefix)
            return
        for g in sorted(set(prefix) | {len(prefix)}):
            yield from rec(prefix + [g])
    yield from rec([])


def literal(X, Y, p):
    def proj(w, g):
        return tuple(a for a in w if p[a] == g)
    return all(any(all(proj(x,g) != proj(y,g) for x in X) for g in set(p)) for y in Y)


class Audit(unittest.TestCase):
    def test_component_chain_and_scope(self):
        raw, cert = fixture()
        result = replay_json(json.dumps(raw), json.dumps(cert), cert['scope'])
        self.assertEqual(result['mandatory_owner'], (0,0,0,3))
        self.assertEqual(result['structural_optimum'], 2)
        self.assertEqual(result['operational_status'], 'INCOMPLETE')
        bounded = copy.deepcopy(cert)
        bounded['scope'].update(regime='BOUNDED', capacity_digest='a'*64)
        self.assertIsNone(replay(raw, bounded)['structural_optimum'])
        with self.assertRaises(InvalidProof):
            replay(raw, bounded, cert['scope'])

    def test_mutations(self):
        raw, cert = fixture()
        edits = [
            (('version',), 'future'), (('scope','sample_digest'), '0'*64),
            (('scope','capacity_digest'), 'a'*64), (('scope','family'), 'restricted'),
            (('scope','regime'), 'UNKNOWN'), (('records',0,'origin'), 'SIMULATOR'),
            (('records',0,'negative'), True), (('records',0,'positive'), -1),
            (('records',0,'group'), 4), (('records',0,'group'), 2),
            (('records',0,'owner'), [0,1,2]), (('records',0,'owner'), [False,1,2,3]),
            (('records',0,'owner'), [1,1,2,3]), (('records',0,'owner'), [0,0,1,3]),
            (('records',1,'epoch'), 1), (('records',1,'epoch'), False),
            (('records',1,'owner'), [0,0,2,3]), (('records',1,'positive_b'), 1),
            (('records',1,'b'), 0), (('records',2,'epoch'), 0),
            (('records',2,'owner'), [0,0,0,3]), (('records',2,'negative'), 0),
            (('records',2,'a'), 1), (('records',2,'positive_a'), 0),
            (('records',3,'compatible'), 1), (('records',3,'separating_groups'), [0]),
            (('records',3,'separating_groups'), [0,3]), (('records',3,'separating_groups'), [1,0]),
            (('records',3,'failed_negative'), 0), (('records',3,'kind'), 'ACCEPT'),
            (('records',3,'kind'), 'UNKNOWN'), (('records',3,'origin'), 'EXTERNAL'),
        ]
        for path, value in edits:
            broken = copy.deepcopy(cert)
            at = broken
            for key in path[:-1]: at = at[key]
            at[path[-1]] = value
            with self.subTest(path=path, value=value), self.assertRaises(InvalidProof):
                replay(raw, broken)
        extras = []
        for kind in ('receipt', 'frontier', 'status', 'claimed_cost'):
            b=copy.deepcopy(cert); b[kind]='OPTIMAL'; extras.append(b)
        b=copy.deepcopy(cert); del b['records'][1]; extras.append(b)
        b=copy.deepcopy(cert); b['records'].insert(2,b['records'][1]); extras.append(b)
        b=copy.deepcopy(cert); del b['records'][0]['positive']; extras.append(b)
        for b in extras:
            with self.assertRaises(InvalidProof): replay(raw,b)
        stale=copy.deepcopy(raw); stale['positive'][0].reverse()
        with self.assertRaises(InvalidProof): replay(stale,cert)
        for s in ('{"version":1,"version":2}', '{"x":NaN}', '{"x":Infinity}', '{'):
            with self.assertRaises(InvalidProof): replay_json(json.dumps(raw),s)
        print('mutation_rejections=44')

    def test_label_conflict_and_empty(self):
        raw, cert = fixture()
        raw['positive'].append(raw['negative'][0][:])
        cert['scope']['sample_digest'] = sample_data(raw)[3]
        cert['records'] = [dict(kind='LABEL_CONFLICT',origin='RAW',negative=0,positive=2)]
        self.assertTrue(replay(raw,cert)['label_conflict'])
        cert['records'][0]['positive']=0
        with self.assertRaises(InvalidProof): replay(raw,cert)
        for negatives in ([],[[]]):
            raw={'alphabet':[],'positive':[],'negative':negatives}
            cert['scope']['sample_digest']=sample_data(raw)[3]
            cert['records']=[dict(kind='STRUCTURAL_CHECK',origin='RAW',owner=[],compatible=not negatives,
                                  separating_groups=[],failed_negative=0 if negatives else None)]
            self.assertEqual(replay(raw,cert)['structural_optimum'],None if negatives else 0)

    def test_frozen_epoch_reuse_and_arbitrary_deletion(self):
        raw={'alphabet':['a','b','c'],'positive':[['a','b'],['a','c'],['b','c']], 'negative':[['a','b','c']]}
        _,_,_,sd=sample_data(raw)
        scope=dict(sample_digest=sd,regime='UNRESTRICTED',family='ALL_PARTITIONS',capacity_digest=None)
        e=dict(kind='COMPONENT_EDGE',origin='RAW',epoch=0,owner=[0,1,2],negative=0,a=0,positive_a=2,b=1,positive_b=1)
        e2=dict(e,b=2,positive_b=0)
        cert=dict(version='selector-v2/1',scope=scope,records=[e,e2])
        self.assertEqual(replay(raw,cert)['mandatory_floor'],2)
        # Arbitrary owner deletion is true but cannot justify an unproved mandatory quotient.
        raw2={'alphabet':['a','b','c'],'positive':[['c']], 'negative':[['a','b','c']]}
        scope=dict(scope,sample_digest=sample_data(raw2)[3])
        d=dict(kind='DELETE_EQUAL',origin='RAW',owner=[0,0,2],negative=0,group=0,positive=0)
        self.assertEqual(replay(raw2,dict(cert,scope=scope,records=[d]))['mandatory_floor'],0)
        with self.assertRaises(InvalidProof): replay(raw2,dict(cert,scope=scope,records=[dict(e,owner=[0,0,2],b=2,positive_a=0,positive_b=0)]))

    def test_exhaustive_tiny_replay(self):
        W=[(),(0,),(1,),(0,0),(0,1),(1,0),(1,1)]
        A=['a','b']; P=list(partitions(2)); corpus_count=checks=edges=0
        for labels in itertools.product(range(3),repeat=len(W)):
            X=[w for w,l in zip(W,labels) if l==1]; Y=[w for w,l in zip(W,labels) if l==2]
            raw=dict(alphabet=A,positive=[[A[a] for a in w] for w in X],negative=[[A[a] for a in w] for w in Y])
            scope=dict(sample_digest=sample_data(raw)[3],regime='UNRESTRICTED',family='ALL_PARTITIONS',capacity_digest=None)
            rec=[]
            for i,y in enumerate(Y):
                witnesses=[]
                for g in range(2):
                    hits=[j for j,x in enumerate(X) if tuple(a for a in x if a!=g)==tuple(a for a in y if a!=g)]
                    if hits:
                        j=hits[0]; witnesses.append((g,j));rec.append(dict(kind='DELETE_EQUAL',origin='RAW',owner=[0,1],negative=i,group=g,positive=j))
                if len(witnesses)==2 and not any(r['kind']=='COMPONENT_EDGE' for r in rec):
                    rec.append(dict(kind='COMPONENT_EDGE',origin='RAW',epoch=0,owner=[0,1],negative=i,a=0,positive_a=witnesses[0][1],b=1,positive_b=witnesses[1][1])); edges+=1
            for p in P:
                def proj(w,g): return tuple(a for a in w if p[a]==g)
                sep=[[g for g in set(p) if all(proj(x,g)!=proj(y,g) for x in X)] for y in Y]
                ok=all(sep)
                rec.append(dict(kind='STRUCTURAL_CHECK',origin='RAW',owner=list(p),compatible=ok,separating_groups=[v[0] for v in sep] if ok else [],failed_negative=None if ok else sep.index([])))
                checks+=1
            result=replay(raw,dict(version='selector-v2/1',scope=scope,records=rec))
            optimum=min(2-len(set(p)) for p in P if literal(X,Y,p))
            self.assertLessEqual(result['mandatory_floor'],optimum)
            if result['structural_optimum'] is not None: self.assertEqual(result['structural_optimum'],optimum)
            corpus_count+=1
        print(f'exhaustive_corpora={corpus_count} structural_checks={checks} forced_edges={edges}')

    def test_golden_vectors(self):
        vectors=[{'alphabet':['β','a','😀'],'positive':[['β'],[],['β']], 'negative':[['a','😀']]},
                 {'alphabet':['a','β','😀'],'positive':[['β'],[],['β']], 'negative':[['a','😀']]},
                 {'alphabet':[], 'positive':[[]], 'negative':[]}]
        actual=[sample_data(v)[3] for v in vectors]
        print('golden_vectors='+json.dumps(actual))
        self.assertEqual(actual,["b3e6b42446211a76362e92236de37cf631bee2bcaf04c4fff3463d061904fc1c",
                                 "d4d34208a22f662dea22de0c3fa9d983e74c08a9c77984d5be7dafc774806128",
                                 "55860bacb2ab0d7ee214c489b206145a14d1276e4a8fbbb17d547c3f1fdf89c9"])
        self.assertEqual(digest({'z':1,'a':2}),digest({'a':2,'z':1}))


if __name__=='__main__': unittest.main(verbosity=2)

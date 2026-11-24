import itertools
import unittest
from selector_v2.core import Budget, PartitionRef, Sample
from selector_v2.schema import canonical, identity, request, sample_id, scope, validate_request
from selector_v2.component_closure import component_closure, structural_record


def partitions(n):
    def visit(o):
        if len(o) == n:
            yield o
        else:
            for g in sorted(set(o)) + [len(o)]:
                yield from visit(o + [g])
    return visit([])


def compatible(s, o):
    def project(w, g):
        return tuple(a for a in w if o[a] == g)
    return all(any(all(project(y,g) != project(x,g) for x in s.positive)
                   for g in set(o)) for y in s.negative)


class SchemaClosureTests(unittest.TestCase):
    def test_golden(self):
        s = Sample.from_input({'alphabet':['β','a','😀'],'positive':[['β','β'],[],['β','β']],'negative':[['a','😀']]})
        self.assertEqual(sample_id(s), '7ddb11d457a25ee2b1d273529cf3f3e2064054dc154ebc901acb796b08708bbb')
        r = request(s, scope(s), PartitionRef((0,1,1)), 'r1', 'a1')
        self.assertEqual(identity(r), '1f43bbcd2081c20e84469b2220928c7a5f61674ce9a7d4bfec84e7e55285ee72')
        for k, v in [('negative_ids',[False]),('owner',[0,True,1]),('version','future'),('request_id','')]:
            with self.assertRaises(ValueError):
                validate_request(s, dict(r, **{k:v}))
        for k,v in [('family','OTHER'),('sample_digest','0'*64),('capacity_digest','0'*64)]:
            with self.assertRaises(ValueError):
                validate_request(s, dict(r, scope=dict(r['scope'], **{k:v})))
        validate_request(s, request(s, scope(s,'BOUNDED','0'*64), PartitionRef((0,1,1)), 'r2','a2'))
        with self.assertRaises(ValueError):
            request(Sample((),(),()), scope(Sample((),(),())), PartitionRef(()), 'r','a')

    def test_multi_epoch(self):
        s = Sample(('a','b','c'), ((0,1),(2,)), ((1,0),(0,1,2)))
        result = component_closure(s)
        self.assertEqual(result['state'], 'FIXPOINT')
        self.assertEqual(result['owner'], [0,0,0])
        self.assertEqual([r['payload']['owner'] for r in result['records']], [[0,1,2],[0,0,2],[0,0,0]])
        self.assertTrue(structural_record(s,PartitionRef((0,0,0)))['payload']['compatible'])
        for cap in range(100):
            part = component_closure(s, Budget(work=cap))
            self.assertIn(part['state'], ('PARTIAL','FIXPOINT'))
            for o in partitions(3):
                if compatible(s,o):
                    self.assertTrue(all(o[a] == o[g] for a,g in enumerate(part['owner'])))
        self.assertEqual(component_closure(s,Budget(work=0))['state'],'PARTIAL')
        self.assertEqual(component_closure(Sample(('a',),((0,),),((0,),)))['state'],'LABEL_CONFLICT')

    def test_exhaustive_small(self):
        words = [w for n in range(3) for w in itertools.product(range(3),repeat=n)]
        for x,y in itertools.product(words,repeat=2):
            if x == y:
                continue
            s = Sample(('a','b','c'),(x,),(y,))
            result = component_closure(s,hash_bits=0)
            self.assertEqual(result['state'],'FIXPOINT')
            for o in partitions(3):
                if compatible(s,o):
                    self.assertTrue(all(o[a] == o[g] for a,g in enumerate(result['owner'])))
            canonical(result)

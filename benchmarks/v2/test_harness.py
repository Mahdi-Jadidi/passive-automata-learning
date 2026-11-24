import json
from pathlib import Path
import random
import tempfile
import unittest
from itertools import product
from harness import partitions, reference, replay_reference, read_input


def sample(a, p, n):
    return {'alphabet': list(a), 'positive': list(map(list,p)), 'negative': list(map(list,n))}


CASES = {'order': sample('ab', ['aba'], ['aab']), 'triple': sample('abc',['a','b','c'],['']),
         'duplicate_unused': sample('abcd',['ab','ab'],['ba','ba']), 'conflict': sample('ab',['ab'],['ab']),
         'empty_alphabet': sample('',[],['']), 'empty_negatives': sample('abc',[''],[]),
         'choice': sample('abcd',['ab','ac','ad'],['ba','ca','da']),
         'path4': sample('abcdefgh', zip('abcd','efgh'),zip('abc','bcd'))}


class Tests(unittest.TestCase):
    def test_counts(self):
        for n,b in enumerate([1,1,2,5,15,52,203,877,4140]):
            self.assertEqual(sum(1 for _ in partitions(list(range(n)))),b)
    def test_reference(self):
        for d in CASES.values():
            self.assertEqual(replay_reference(d,reference(d))['status'],'VERIFIED')
        r=random.Random(4242)
        words=['','a','b','c','ab','ba','aa','bc','cb']
        for _ in range(250):
            d=sample('abc',r.choices(words,k=r.randrange(5)),r.choices(words,k=r.randrange(5)))
            self.assertEqual(replay_reference(d,reference(d))['status'],'VERIFIED')
    def test_corruption(self):
        d=CASES['order']; result=reference(d); result['blocks']=[['a'],['b']]; result['max_devices']=2
        self.assertEqual(replay_reference(d,result)['status'],'INVALID')
    def test_isolation(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'in.json'; p.write_text(json.dumps({'input':CASES['order'],'result':{}}))
            with self.assertRaises(ValueError): read_input(p)
            p.write_text(json.dumps({**CASES['order'],'planted':[['a','b']]}))
            with self.assertRaises(ValueError): read_input(p)


if __name__=='__main__':
    unittest.main()

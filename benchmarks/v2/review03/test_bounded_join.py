import itertools
import random
import unittest
from bounded_join import expected_deletions


def literal(X,Y,o):
    return {(i,g) for i,y in enumerate(Y) for g in set(o) if any(
        tuple(a for a in x if o[a]!=g)==tuple(a for a in y if o[a]!=g) for x in X)}

class JoinTests(unittest.TestCase):
    def test_exhaustive(self):
        w=[x for l in range(4) for x in itertools.product(range(3),repeat=l)]
        count=0
        for x,y in itertools.product(w,repeat=2):
            if x==y: continue
            for o in ((0,1,2),(0,0,2),(0,0,0)):
                target=literal((x,),(y,),o)
                for bits in (0,1,64):
                    self.assertEqual(set(expected_deletions((x,),(y,),o,hash_bits=bits)),target)
                    count+=1
        print('exhaustive_filter_checks',count)
    def test_random(self):
        r=random.Random(13452);w=[x for l in range(4) for x in itertools.product(range(3),repeat=l)]
        for _ in range(300):
            X=tuple(r.choices(w,k=5));Y=tuple(r.choices([x for x in w if x not in X],k=5))
            for o in ((0,1,2),(0,0,2),(0,0,0)):
                self.assertEqual(set(expected_deletions(X,Y,o,hash_bits=0)),literal(X,Y,o))
        print('random_collision_checks',900)
    def test_conflict(self):
        with self.assertRaises(ValueError): list(expected_deletions(((0,),),((0,),),(0,)))
if __name__=='__main__':unittest.main(verbosity=2)

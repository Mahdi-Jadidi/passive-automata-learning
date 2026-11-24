import itertools,unittest
from bounded_deletion import DeletionBudget, ReplayIncomplete, check_exhaustion
from production_replay import expected_deletions
from independent_replay import InvalidProof

class Bounded(unittest.TestCase):
    def test_exhaustive_filters(self):
        W=[w for l in range(3) for w in itertools.product(range(2),repeat=l)]
        cases=checks=0
        for labels in itertools.product(range(3),repeat=len(W)):
            X=[w for w,l in zip(W,labels) if l==1];Y=[w for w,l in zip(W,labels) if l==2]
            for p in [(0,1),(0,0)]:
                facts=set(expected_deletions(X,Y,p))
                for bits in (0,2,64):
                    check_exhaustion(X,Y,p,facts,DeletionBudget(seconds=None),hash_bits=bits);checks+=1
                if facts:
                    with self.assertRaises(InvalidProof):check_exhaustion(X,Y,p,facts-{next(iter(facts))},DeletionBudget(),hash_bits=0)
                cases+=1
        print('bounded_corpus_owner_cases=',cases,'filter_checks=',checks)
    def test_limits(self):
        X=[(0,1)];Y=[(1,0)];p=(0,1);facts={(0,0),(0,1)}
        for kw in (dict(work=0),dict(entries=0),dict(word_length=1),dict(seconds=0)):
            with self.assertRaises(ReplayIncomplete):check_exhaustion(X,Y,p,facts,DeletionBudget(**kw))
        with self.assertRaises(InvalidProof):check_exhaustion(X,X,p,set(),DeletionBudget())
        with self.assertRaises(InvalidProof):check_exhaustion(X,Y,p,facts|{(1,0)},DeletionBudget())
    def test_long_diverse(self):
        n=20000;p=tuple(range(n));X=[p];Y=[(1,0)+p[2:]];facts={(0,0),(0,1)}
        b=DeletionBudget(seconds=30,entries=n+1);check_exhaustion(X,Y,p,facts,b)
        print('long_diverse_symbols=',n,'index_entries=',b.peak_entries,'exact_checks=',b.exact_checks,'work=',b.used)
if __name__=='__main__':unittest.main()

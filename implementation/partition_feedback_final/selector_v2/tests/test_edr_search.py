"""Producer tests against Agent #3's pinned independent kernel."""
import copy
import itertools
import unittest
from pathlib import Path

from selector_v2.edr_search import canonical, solve, pair_at, load
from selector_v2.edr_bb import SearchCaps
from independent_replay import sample_data
from p3_frontier_verifier import build_trusted_scope, verify_frontier
from rgs_oracle import oracle
from test_production_replay import build as reference_closure


def fixture(raw, nonidentity=False):
    events=[]
    if nonidentity:
        events=[dict(event="RAW",records=reference_closure(raw)["records"])]
    journal=canonical(dict(version="selector-v2-journal/2",sample_digest=sample_data(raw)[3],events=events))
    return journal,build_trusted_scope(raw,journal)


class SearchTests(unittest.TestCase):
    def check_case(self,raw,nonidentity=False):
        journal,scope=fixture(raw,nonidentity)
        ref=oracle(raw)["result"]
        expected=sorted(tuple(p.index(g) for g in p) for p in ref["optima"])
        for mode in ("one","all"):
            cert,metrics=solve(raw,scope,mode)
            self.assertEqual(cert["declared_status"],"EXHAUSTED")
            self.assertEqual(canonical(cert),canonical(solve(raw,scope,mode)[0]))
            result=verify_frontier(raw,journal,scope,canonical(cert))
            self.assertEqual(result["status"],"VERIFIED",result)
            self.assertEqual(result["result"]["optimum"],ref["optimum"])
            if mode=="all":
                self.assertEqual(cert["optima"],[list(p) for p in expected])
            elif expected:
                self.assertIn(tuple(cert["incumbent"]["owner"]),expected)
            else:
                self.assertIsNone(cert["incumbent"])
        return journal,scope

    def test_literal_oracle(self):
        count=0
        for n in range(5):
            a=[str(i) for i in range(n)]
            words=[[]]+[[x] for x in a]+([a[:2],a[:2][::-1]] if n>=2 else [])
            for x in words:
                for y in words:
                    self.check_case(dict(alphabet=a,positive=[x],negative=[y]))
                    count+=1
        print("independent RGS/producer comparisons (both modes):",count)

    def test_ties_duplicates_empty_unused(self):
        for raw in (
            dict(alphabet=["a","b","c","unused"],positive=[["b","c"],["a"],["a"]],negative=[["a","b","c"],["a","b","c"]]),
            dict(alphabet=["a","unused"],positive=[[]],negative=[[]]),
            dict(alphabet=["a","unused"],positive=[],negative=[[]]),
            dict(alphabet=["a","unused"],positive=[[]],negative=[]),
            dict(alphabet=[],positive=[],negative=[]),
            dict(alphabet=[],positive=[],negative=[[]]),
            dict(alphabet=[],positive=[[]],negative=[[]])):
            self.check_case(raw)

    def test_nonidentity_scope(self):
        raw=dict(alphabet=["a","b","unused"],positive=[["a"],["b"]],negative=[["a","b"]])
        j,s=self.check_case(raw,True)
        self.assertEqual(s["root_owner"],[0,0,2])

    def test_direct_pair(self):
        for k in range(64):
            reps=tuple(range(0,2*k,2))
            for j,p in enumerate(itertools.combinations(reps,2)):
                self.assertEqual(pair_at(reps,j),p)
        reps=range(100000)
        self.assertEqual(pair_at(reps,4999949999),(99998,99999))
        with self.assertRaises(ValueError): pair_at(reps,4999950000)

    def test_restart_every_small_entry_boundary(self):
        raw=dict(alphabet=["a","b","c","unused"],positive=[["b","c"],["a"]],negative=[["a","b","c"]])
        j,s=fixture(raw)
        for mode in ("one","all"):
            complete,_=solve(raw,s,mode)
            for cap in range(len(complete["nodes"])+1):
                c,_=solve(raw,s,mode,caps=SearchCaps(entries=cap))
                result=verify_frontier(raw,j,s,canonical(c))
                if c["declared_status"]=="PARTIAL":
                    self.assertEqual(result["status"],"INCOMPLETE",result)
                    self.assertNotIn("result",result)
                    resumed,_=solve(raw,s,mode,checkpoint=copy.deepcopy(c))
                    self.assertEqual(canonical(complete),canonical(resumed))
                else:
                    self.assertEqual(result["status"],"VERIFIED",result)
                    self.assertEqual(canonical(complete),canonical(c))
            c,_=solve(raw,s,mode,caps=SearchCaps(work=0))
            self.assertEqual(verify_frontier(raw,j,s,c)["status"],"INCOMPLETE")
            c,_=solve(raw,s,mode,caps=SearchCaps(seconds=0))
            self.assertEqual(verify_frontier(raw,j,s,c)["status"],"INCOMPLETE")

    def test_large_lazy_suffix(self):
        # n=100k, no feasible identity: cap immediately after explicit residual.
        # The work cap permits root projection but not full alternative emission.
        n=100000
        a=[str(i) for i in range(n)]
        raw=dict(alphabet=a,positive=[["0"],["1"]],negative=[["0","1"]])
        j,s=fixture(raw)
        c,m=solve(raw,s,"one",caps=SearchCaps(entries=1))
        self.assertEqual(c["declared_status"],"PARTIAL")
        root=c["nodes"][0]
        self.assertEqual(root["kind"],"SPLIT")
        self.assertEqual(root["alternative_count"],n*(n-1)//2)
        self.assertEqual(root["cursor"],0)
        self.assertEqual(root["suffix"]["stop"],n*(n-1)//2)
        self.assertEqual(len(c["nodes"]),2)
        self.assertEqual(c["nodes"][1]["edge"],{"kind":"RESIDUAL"})

    def test_strict_scope(self):
        raw=dict(alphabet=["a"],positive=[],negative=[])
        _,s=fixture(raw)
        for bad in (dict(s,root_owner=[True]),dict(s,alphabet=["b"]),dict(s,root_equalities=[])):
            with self.assertRaises(ValueError): solve(raw,bad)


if __name__=="__main__":
    unittest.main()

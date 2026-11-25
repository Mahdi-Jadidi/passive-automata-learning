"""Synthetic certificates only: independent RGS literal reference, never producer."""
import copy
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from independent_replay import sample_data
from p3_frontier_verifier import build_trusted_scope, canonical, pair_at, scope_digest, verify_frontier
from rgs_oracle import oracle, rgs, self_test, compatible

def fixture(raw):
    _, _, _, digest = sample_data(raw)
    j = canonical(dict(version="selector-v2-journal/2", sample_digest=digest, events=[]))
    return j, build_trusted_scope(raw,j)

def minimum_owner(p):
    return tuple(p.index(x) for x in p)

def certificate(raw, scope, mode="all"):
    # Test-only construction using literal membership of every RGS partition.
    n,X,Y,_ = sample_data(raw)
    partitions = [minimum_owner(p) for p in rgs(n)]
    result = oracle(raw)["result"]
    best = result["optimum"]
    optima = sorted(minimum_owner(p) for p in result["optima"])
    nodes = []
    def visit(ident, parent, edge, p, members, residual=False):
        node = dict(id=ident,parent_id=parent,edge=edge,kind="LEAF")
        nodes.append(node)
        if not members:
            reason = "EMPTY"
        elif compatible(p,X,Y):
            reason = "FEASIBLE_MIN"
        elif len(members)==1:
            reason = "EXACT_NO"
        else:
            reps = sorted(set(p))
            pairs = list(itertools.combinations(reps,2))
            node.update(kind="SPLIT",rule="ALL_PAIRS_LEX_V1",alternative_count=len(pairs),
                        cursor=len(pairs),children=[],cursor_log=[],residual_id=ident+"/r",
                        suffix=dict(rule="FIRST_TRUE_SUFFIX_V1",start=len(pairs),stop=len(pairs)))
            remaining = list(members)
            for j,(a,b) in enumerate(pairs):
                child = ident+"/c"+str(j)
                node["children"].append(child)
                node["cursor_log"].append({"from":j,"to":j+1,"child_id":child,"pair":[a,b]})
                selected = [q for q in remaining if q[a]==q[b]]
                remaining = [q for q in remaining if q[a]!=q[b]]
                merged = tuple(a if v==b else v for v in p)
                visit(child,ident,dict(kind="CHILD",index=j,pair=[a,b]),merged,selected)
            visit(ident+"/r",ident,dict(kind="RESIDUAL"),p,remaining,True)
            return
        node["closure"] = dict(reason=reason)
    visit("root",None,dict(kind="ROOT"),tuple(scope["root_owner"]),partitions)
    return dict(format="p3-region-frontier/v1",scope_digest=scope_digest(scope),mode=mode,
                declared_status="EXHAUSTED",root_owner=scope["root_owner"],
                incumbent=None if best is None else dict(owner=list(optima[0]),cost=best),
                optima=[list(q) for q in optima] if mode=="all" else [],
                nodes=sorted(nodes,key=lambda q:q["id"]))

class FrontierTests(unittest.TestCase):
    def setUp(self):
        self.raw=dict(alphabet=["a","b","unused"],positive=[["a"],["b"]],negative=[["a","b"]])
        self.j,self.s=fixture(self.raw)
        self.c=certificate(self.raw,self.s)
    def verify(self,c=None,**kw):
        return verify_frontier(self.raw,self.j,self.s,self.c if c is None else c,**kw)
    def test_reference(self):
        self_test()
        count=0
        for k in range(65):
            reps=list(range(0,2*k,2))
            for j,p in enumerate(itertools.combinations(reps,2)):
                self.assertEqual(pair_at(reps,j),list(p))
                count+=1
        print("pair_at comparisons:",count)
    def test_canonical(self):
        self.assertEqual(canonical({"z":"ä","a":[True,None,0]}),
                         b'{"a":[true,null,0],"z":"\\u00e4"}')
        self.assertNotIn("root_equalities",self.s)
    def test_oracle(self):
        cases=0
        for n in range(6):
            a=[str(i) for i in range(n)]
            words=[[]]+[[x] for x in a]+([a[:2],a[:2][::-1]] if n>=2 else [])
            for x in words:
                for y in words:
                    raw=dict(alphabet=a,positive=[x],negative=[y])
                    j,s=fixture(raw)
                    c=certificate(raw,s)
                    out=verify_frontier(raw,j,s,c)
                    self.assertEqual(out["status"],"VERIFIED",out)
                    ref=oracle(raw)["result"]
                    self.assertEqual(out["result"]["optimum"],ref["optimum"])
                    self.assertEqual(out["result"]["optima"],
                                     [list(q) for q in sorted(minimum_owner(p) for p in ref["optima"])])
                    cases+=1
        print("literal fixture cases:",cases)
    def test_mutations(self):
        mutations=[
            lambda c:c.update(root_owner=[0,0,2]),
            lambda c:c.update(scope_digest="0"*64),
            lambda c:c["nodes"].pop(),
            lambda c:c["nodes"].insert(1,copy.deepcopy(c["nodes"][0])),
            lambda c:c["nodes"][0]["children"].reverse(),
            lambda c:c["nodes"][0]["cursor_log"][0].update(pair=[0,2]),
            lambda c:c["nodes"][0]["suffix"].update(stop=1),
            lambda c:c["nodes"][0].update(alternative_count=True),
            lambda c:c["nodes"][1].update(parent_id="root/r"),
            lambda c:c["nodes"][1]["edge"].update(pair=[1,2]),
            lambda c:c["nodes"][1].update(closure=dict(reason="EMPTY")),
            lambda c:c["nodes"][1].update(closure=dict(reason="COST")),
            lambda c:c["nodes"][1].update(closure=dict(reason="RAW_LABEL_CONFLICT",positive_id="P0",negative_id="N0")),
            lambda c:c.update(incumbent=dict(owner=[0,1,2],cost=0)),
            lambda c:c.update(optima=[]),
            lambda c:c.update(declared_status="PARTIAL"),
            lambda c:c["nodes"][1].update(closure=dict(reason="UNKNOWN")),
        ]
        for i,change in enumerate(mutations):
            with self.subTest(i=i):
                c=copy.deepcopy(self.c); change(c)
                out=self.verify(c)
                self.assertEqual(out["status"],"INVALID",out)
                self.assertNotIn("result",out)
        print("certificate mutations:",len(mutations))
    def test_partial_and_caps(self):
        c=copy.deepcopy(self.c)
        c.update(declared_status="PARTIAL",optima=[])
        c["nodes"]=[dict(id="root",parent_id=None,edge=dict(kind="ROOT"),kind="OPEN",reason="WORK_CAP")]
        self.assertEqual(self.verify(c)["status"],"INCOMPLETE")
        c["declared_status"]="EXHAUSTED"
        self.assertEqual(self.verify(c)["status"],"INVALID")
        for budget in (dict(seconds=0),dict(max_work=0),dict(max_nodes=0),
                       dict(max_proof_bytes=1),dict(max_journal_bytes=1),dict(max_exact_checks=0),
                       dict(max_entries=0)):
            out=self.verify(**budget)
            self.assertEqual(out["status"],"INCOMPLETE",out)
            self.assertNotIn("result",out)
    def test_one_cutoff(self):
        c=certificate(self.raw,self.s,"one")
        q=c["nodes"][1]
        q["closure"]=dict(reason="COST")
        self.assertEqual(self.verify(c)["status"],"VERIFIED")
    def test_large_symbolic_partial(self):
        n=20000
        raw=dict(alphabet=[str(i) for i in range(n)],positive=[],negative=[])
        j,s=fixture(raw)
        t=n*(n-1)//2
        c=dict(format="p3-region-frontier/v1",scope_digest=scope_digest(s),mode="one",
               declared_status="PARTIAL",root_owner=s["root_owner"],incumbent=None,optima=[],
               nodes=[dict(id="root",parent_id=None,edge=dict(kind="ROOT"),kind="SPLIT",
                           rule="ALL_PAIRS_LEX_V1",alternative_count=t,cursor=0,children=[],cursor_log=[],
                           residual_id="root/r",suffix=dict(rule="FIRST_TRUE_SUFFIX_V1",start=0,stop=t)),
                      dict(id="root/r",parent_id="root",edge=dict(kind="RESIDUAL"),kind="OPEN",reason="TIME_CAP")])
        out=verify_frontier(raw,j,s,c)
        self.assertEqual(out["status"],"INCOMPLETE",out)
        self.assertEqual(out["nodes_checked"],2)
        print("symbolic alternatives:",t,"work:",out["work_units"])
    def test_scope_and_cli(self):
        for s in (dict(self.s,root_owner=[0,0,2]),dict(self.s,positive=[dict(id="P0",tokens=[False])])):
            self.assertEqual(verify_frontier(self.raw,self.j,s,self.c)["status"],"INVALID")
        self.assertEqual(verify_frontier(self.raw,self.j+b"\n",self.s,self.c)["status"],"INVALID")
        bad=b'{"format":"x","format":"p3-region-frontier/v1"}'
        self.assertEqual(self.verify(bad)["status"],"INVALID")
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            for name,val in (("raw",canonical(self.raw)),("journal",self.j),
                             ("scope",canonical(self.s)),("proof",bad)):
                (d/name).write_bytes(val)
            args=[sys.executable]
            if not __debug__: args+=["-O"]
            args += [str(Path(__file__).with_name("p3_frontier_verifier.py"))]
            command=args+["--raw",str(d/"raw"),"--journal",str(d/"journal")]
            made=subprocess.run(command+["--make-trusted-scope","--out",str(d/"made")],capture_output=True)
            self.assertEqual(made.returncode,0,made.stderr)
            self.assertEqual((d/"made").read_bytes(),canonical(self.s))
            bad_run=subprocess.run(command+["--scope",str(d/"scope"),"--proof",str(d/"proof")],capture_output=True)
            self.assertEqual(bad_run.returncode,1,bad_run.stderr)
            self.assertEqual(json.loads(bad_run.stdout)["status"],"INVALID")

if __name__=="__main__":
    unittest.main()

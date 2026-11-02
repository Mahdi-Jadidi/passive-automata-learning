"""C007 v4 staged-swap smoke with an independent all-partition RGS oracle."""
import importlib.util
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("c007_finest_v4",ROOT/"finest_solver_v4.py")
solver=importlib.util.module_from_spec(spec); spec.loader.exec_module(solver)

def rgs_partitions(symbols):
    if not symbols: return
    labels=[0]*len(symbols)
    def visit(i,top):
        if i==len(symbols):
            blocks=[]
            for k in range(top+1): blocks.append([symbols[j] for j,x in enumerate(labels) if x==k])
            yield blocks; return
        for k in range(top+2):
            labels[i]=k
            yield from visit(i+1,max(top,k))
    labels[0]=0
    yield from visit(1,0)

def canon(part): return tuple(sorted(tuple(sorted(b)) for b in part))
def direct(part,p,n):
    langs=[{"".join(ch for ch in w if ch in set(b)) for w in p} for b in part]
    return all(any("".join(ch for ch in w if ch in set(b)) not in langs[i]
                   for i,b in enumerate(part)) for w in n)
def meet_parts(parts,alpha):
    if not parts: return [list(alpha)]
    parent={x:x for x in alpha}
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i,a in enumerate(alpha):
        for b in alpha[i+1:]:
            together_everywhere=all(any(a in block and b in block for block in part) for part in parts)
            if together_everywhere: parent[find(a)]=find(b)
    groups={}
    for x in alpha: groups.setdefault(find(x),[]).append(x)
    return sorted((sorted(b) for b in groups.values()),key=lambda b:b[0])
def refines(a,b): return all(any(set(x)<=set(y) for y in b) for x in a)
def oracle(data):
    alpha=sorted(data["alphabet"]); p=sorted(set(data["positive"])); n=sorted(set(data["negative"]))
    feasible=[part for part in rgs_partitions(alpha) if direct(part,p,n)]
    meet=meet_parts(feasible,alpha)
    maxima=[part for part in feasible if not any(canon(part)!=canon(other) and refines(other,part) for other in feasible)]
    return feasible,meet,maxima

CASES={
"three_block_finest":{"alphabet":list("abcdef"),"positive":["","ab","cd","ef"],"negative":["a","b","c","d","e","f"]},
"multiple_maximal":{"alphabet":list("abc"),"positive":["","abc"],"negative":["a"]},
"one_block_only":{"alphabet":list("ab"),"positive":["ab"],"negative":["ba"]},
"empty_binary_family":{"alphabet":list("ab"),"positive":["a","b"],"negative":[""]},
"positive_only":{"alphabet":list("abc"),"positive":["abc"],"negative":[]},
"negative_only":{"alphabet":list("abc"),"positive":[],"negative":[""]},
"epsilon_unused":{"alphabet":list("abcd"),"positive":[""],"negative":["a"]},
"exact_swap_fast_path":{"alphabet":list("abcd"),"positive":["ab","cd"],"negative":["ba","dc"]},
}
rows=[]
for name,data in CASES.items():
    feasible,meet,maxima=oracle(data)
    adapt=solver.solve(data,mode="adaptive")
    reference=solver.solve(data,mode="reference")
    expected=("one_block_only" if len(meet)==1 and len(feasible)==1 else
              "finest_unique" if direct(meet,data["positive"],data["negative"]) else "multiple_maximal_exist")
    assert adapt["status"]==expected,(name,adapt,expected)
    assert reference["status"]==expected,(name,reference,expected)
    assert canon(reference.get("meet_partition",reference.get("finest_witness",{}).get("partition",[])))==canon(meet),(name,reference,meet)
    if expected in ("finest_unique","one_block_only"):
        assert solver.verify_result(data,adapt)["valid"],(name,adapt)
        assert solver.verify_result(data,reference)["valid"],(name,reference)
    else:
        assert len(maxima)>=2,(name,maxima)
        assert solver.verify_result(data,adapt)["valid"],(name,adapt)
        assert solver.verify_result(data,reference)["valid"],(name,reference)
    assert len(reference.get("reference_bipartitions",[]))==sum(len(b)==2 for b in feasible)
    if name=="exact_swap_fast_path": assert adapt["staged_preprocessing"]["fallback_used"] is False
    if name in ("multiple_maximal","empty_binary_family"): assert adapt["staged_preprocessing"]["fallback_used"] is True
    rows.append({"name":name,"feasible_partitions":len(feasible),"compatible_bipartitions":len(reference["reference_bipartitions"]),
                 "oracle_meet":meet,"maximal_refinements":len(maxima),"status":adapt["status"],
                 "adaptive":adapt,"reference":reference,
                 "staged_preprocessing":adapt.get("staged_preprocessing")})

# Only exactly two adjacent reversed mismatches produce a swap edge.
for p,n,expected in [("ab","ba",1),("abc","bac",0),("abcd","badc",0),("abc","cba",0)]:
    got=solver._swap_only_edges(list("abcd"),[p],[n],None,{})
    assert len(got)==expected,(p,n,got)

# Deterministic interruption after one compatible separator; no final claim.
multi=CASES["multiple_maximal"]
orig=solver._canonical_masks
round_id=0
def interrupted_masks(n):
    global round_id
    round_id+=1
    if round_id==1:
        yield 1; yield 3
    else:
        yield 1
        raise KeyboardInterrupt
solver._canonical_masks=interrupted_masks
partial=solver.solve(multi,mode="adaptive")
solver._canonical_masks=orig
assert partial["status"]=="incomplete" and partial["complete"] is False
assert partial["successful_separators"] and partial["partial_meet"]

invalid=solver.solve({"alphabet":["a","b"],"positive":["a"],"negative":["a"]})
assert invalid["status"]=="invalid_input"
badk=solver.solve({"alphabet":["a","b"],"positive":[],"negative":[],"k":2})
assert badk["status"]=="invalid_input"
print(json.dumps({"scientific_status":"passed","cases":rows,
 "additional_checks":["partial_meet_interruption_is_incomplete","swap_edge_exactness","contradictory_labels","k_rejected"]},ensure_ascii=False,sort_keys=True))


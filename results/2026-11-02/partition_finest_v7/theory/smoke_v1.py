import json
from pathlib import Path

def partitions(a):
    def rgs(blocks,i):
        if i==len(a):
            yield tuple(tuple(b) for b in blocks);return
        for j in range(len(blocks)):
            bs=[b[:] for b in blocks];bs[j].append(a[i]);yield from rgs(bs,i+1)
        yield from rgs(blocks+[[a[i]]],i+1)
    return list(rgs([],0))

def projection(w,b):return ''.join(a for a in w if a in b)
def feasible(pi,p,n):
    langs=[{projection(w,b) for w in p} for b in pi]
    return all(any(projection(w,b) not in l for b,l in zip(pi,langs)) for w in n)
def refines(pi,rho):return all(any(set(b)<=set(c) for c in rho) for b in pi)
def meet(a,parts):
    groups={}
    for x in a:
        sig=tuple(next(i for i,b in enumerate(pi) if x in b) for pi in parts)
        groups.setdefault(sig,[]).append(x)
    return tuple(sorted(tuple(b) for b in groups.values()))
def components(a,p,n):
    edges=set();p,n=set(p),set(n)
    for w in p:
        for i in range(len(w)-1):
            x,y=w[i:i+2]
            if x!=y and w[:i]+y+x+w[i+2:] in n:edges.add(tuple(sorted((x,y))))
    for w in n:
        for i,x in enumerate(w):
            if w[:i]+w[i+1:] not in p:continue
            for y in a:
                if x!=y and any(w[:j]+y+w[j:] in p for j in (i,i+1)):
                    edges.add(tuple(sorted((x,y))))
    unseen=set(a);out=[]
    while unseen:
        stack=[min(unseen)];block=set()
        while stack:
            x=stack.pop()
            if x in block:continue
            block.add(x)
            stack.extend(y if x==z else z for z,y in edges if x in (z,y))
        unseen-=block;out.append(tuple(sorted(block)))
    return tuple(sorted(out)),sorted(edges)

examples=json.loads(Path(__file__).with_name('examples_v1.json').read_text(encoding='utf-8'))
for name,s in examples.items():
    a=sorted(s['alphabet']);p,n=s['positive'],s['negative']
    family=[pi for pi in partitions(a) if feasible(pi,p,n)]
    binary=[pi for pi in family if len(pi)==2]
    m=meet(a,binary);mall=meet(a,family)
    frontier=[pi for pi in family if not any(other!=pi and refines(other,pi) for other in family)]
    c,edges=components(a,p,n)
    current=meet(a,[]);history=[]
    while True:
        separator=next((b for b in binary if meet(a,[current,b])!=current),None)
        if separator is None:break
        refined=meet(a,[current,separator]);history.append(dict(before=current,separator=separator,after=refined));current=refined
    raw=dict(case=name,input=s,feasible=family,binary=binary,meet=m,all_k_meet=mall,
             maximal_refinements=frontier,components=c,edges=edges,adaptive_history=history,
             final_adaptive_meet=current,meet_feasible=feasible(m,p,n))
    print(json.dumps(raw),flush=True)
    assert m==mall==current
    assert len(history)<=len(a)-1
    assert feasible(m,p,n)==(len(frontier)==1)
    for h in history:
        assert len(h['after'])>len(h['before']) and h['separator'] in family
        assert refines(m,h['after'])
        if not feasible(h['after'],p,n):assert len(frontier)>1
    if feasible(c,p,n):assert c==m
    if name=='three_blocks_infinite_target':assert len(m)==3 and feasible(m,p,n)
    if name=='multiple_maximal':assert len(frontier)==2 and not feasible(m,p,n)
    if name=='empty_binary_family':assert not binary and len(m)==1
    if not p or not n:assert len(m)==len(a)
print(json.dumps(dict(execution_status='success',scientific_status='branch_proof_smoke_passed_independent_gate_pending',cases=len(examples),performance_job=False)),flush=True)

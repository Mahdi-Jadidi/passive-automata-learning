import json
from pathlib import Path

def partitions(alphabet):
    def visit(blocks, i):
        if i == len(alphabet):
            yield tuple(tuple(b) for b in blocks)
            return
        for j in range(len(blocks)):
            copy = [b[:] for b in blocks]
            copy[j].append(alphabet[i])
            yield from visit(copy, i+1)
        yield from visit(blocks + [[alphabet[i]]], i+1)
    yield from visit([], 0)

def project(w, b):
    return ''.join(a for a in w if a in b)

def feasible(pi, p, n):
    langs = [{project(w,b) for w in p} for b in pi]
    return all(any(project(w,b) not in lang for b,lang in zip(pi,langs)) for w in n)

def edges(data):
    p,n = set(data['positive']),set(data['negative'])
    out = set()
    for w in p:
        for i in range(len(w)-1):
            a,b=w[i:i+2]
            if a!=b and w[:i]+b+a+w[i+2:] in n:
                out.add(tuple(sorted((a,b))))
    for w in n:
        for i,a in enumerate(w):
            if w[:i]+w[i+1:] not in p: continue
            for b in data['alphabet']:
                if a==b: continue
                if any(w[:j]+b+w[j:] in p for j in (i,i+1)):
                    out.add(tuple(sorted((a,b))))
    return sorted(out)

def coarsens(coarse, fine):
    return all(any(set(b)<=set(c) for c in coarse) for b in fine)

data=json.loads(Path(__file__).with_name('enhanced_examples_v1.json').read_text(encoding='utf-8'))
for name,sample in data.items():
    p,n=set(sample['positive']),set(sample['negative'])
    good=[pi for pi in partitions(sample['alphabet']) if feasible(pi,p,n)]
    inferred=[]
    for neg in n:
        insertions={}
        for pos in p:
            if len(pos)!=len(neg)+1: continue
            for i,a in enumerate(pos):
                if pos[:i]+pos[i+1:]==neg:
                    insertions.setdefault(i,[]).append((a,pos))
        for i,items in insertions.items():
            for a,pa in items:
                for b,pb in items:
                    if a<b: inferred.append(dict(rule='A',symbols=[a,b],negative=neg,positive=[pa,pb],offsets=[i,i]))
        deletions=[(i,a,neg[:i]+neg[i+1:]) for i,a in enumerate(neg) if neg[:i]+neg[i+1:] in p]
        for i,a,pa in deletions:
            for j,b,pb in deletions:
                if a<b: inferred.append(dict(rule='B',symbols=[a,b],negative=neg,positive=[pa,pb],offsets=[i,j]))
    old=edges(sample)
    union=set(map(tuple,old))|{tuple(e['symbols']) for e in inferred}
    raw=dict(case=name,input=sample,feasible=good,old_edges=old,new_edge_provenance=inferred,enhanced_edges=sorted(union))
    print(json.dumps(raw),flush=True)
    for e in inferred:
        a,b=e['symbols']
        assert all(any(a in block and b in block for block in pi) for pi in good)
    if name=='manager': assert not union and all(len(pi)==1 for pi in good)
    if name in ('reduced_old_gap','original_old_gap'): assert not old and union
    if name.startswith('feasible_'): assert any(len(pi)>1 for pi in good) and ('a','b') in union
print(json.dumps(dict(execution_status='success',scientific_status='branch_check_passed_independent_audit_pending',performance_job=False)),flush=True)

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

data = json.loads(Path(__file__).with_name('examples_manager_v1.json').read_text(encoding='utf-8'))
for name, sample in data.items():
    all_pi=list(partitions(sorted(sample['alphabet'])))
    p,n=sample['positive'],sample['negative']
    good=[pi for pi in all_pi if feasible(pi,p,n)]
    cover=[]
    for pi in all_pi:
        if len(pi)!=2 or pi in good: continue
        for neg in n:
            matches=[[pos for pos in p if project(pos,b)==project(neg,b)] for b in pi]
            if all(matches):
                cover.append({'blocks':pi,'negative':neg,'positive_matches':[v[0] for v in matches]})
                break
    raw={'case':name,'input':sample,'all_partitions':all_pi,'feasible':good,
         'graph_edges':edges(sample),'collision_cover':cover}
    print(json.dumps(raw),flush=True)
    assert all(coarse in good for fine in good for coarse in all_pi if coarsens(coarse,fine))
    counts=sorted({len(pi) for pi in good})
    assert counts==list(range(1,max(counts)+1))
    assert all(feasible(pi,p,[]) for pi in all_pi)
    assert all(feasible(pi,[],n) for pi in all_pi)
    assert bool([pi for pi in good if len(pi)>1])==bool([pi for pi in good if len(pi)==2])
    if 'graph_gap' in name:
        assert not raw['graph_edges'] and all(len(pi)==1 for pi in good)
        assert len(cover)==sum(len(pi)==2 for pi in all_pi)
    if name=='nonunique_maximal':
        assert counts==[1,2] and sum(len(pi)==2 for pi in good)==2
    if name=='infinite_irreducible_target_sample':
        assert all(len(pi)==1 for pi in good) and raw['graph_edges']==[('a','b')]
reduced=data['reduced_graph_gap']
for removed in reduced['positive']:
    variant={**reduced,'positive':[w for w in reduced['positive'] if w!=removed]}
    found=[pi for pi in partitions(variant['alphabet']) if len(pi)==2 and feasible(pi,variant['positive'],variant['negative'])]
    print(json.dumps({'minimality_remove':removed,'input':variant,'feasible_bipartitions':found}),flush=True)
    assert found
print(json.dumps({'execution_status':'success','scientific_status':'branch_smoke_passed_independent_audit_pending',
                  'examples':len(data),'performance_job':False}),flush=True)

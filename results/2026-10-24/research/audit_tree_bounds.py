"""Adversarial multi-trace tests of unique-edge-label prefix-tree bounds."""
from pathlib import Path
from collections import Counter
import json,random
from static_selector import select
from previous_selector import select as previous
from rpni_work_reference import run,split_run,project
from independent_oracle import oracle_fold,oracle_learner,independent_accept,exact_equivalent

root=Path(__file__).parent;rng=random.Random(20261022)
stats=Counter();decisions=Counter();examples={};candidate_checks=0

def observe(before,r,b,after,ok,neg):
    global candidate_checks
    assert oracle_fold(before,r,b)==after
    assert ok==all(not independent_accept(after,w) for w in neg)
    candidate_checks+=1

def check(P,Q,B,description):
    pred=select(P,Q,B);old=previous(P,Q,B)
    assert pred['selector_work']==old['selector_work']
    g=run(P,Q,observer=observe);model,attempts=oracle_learner(P,Q)
    assert model==g['model'] and attempts==g['A']
    assert g['E']==len(set(''.join(P)))
    assert all(f['unions']==1 and f['passes']==1 and f['work']==3*f['n']+2*f['e'] for f in g['folds'])
    try:s=split_run(P,Q,B)
    except ValueError:
        assert pred['decision']=='INFEASIBLE';stats['infeasible']+=1;return
    if 'global_interval' in pred:
        assert pred['global_interval'][0]<=g['W']<=pred['global_interval'][1],(P,Q,B,pred,g['W'])
        assert pred['split_interval'][0]<=s['W']<=pred['split_interval'][1]
    ps=[{project(w,b) for w in P} for b in B];ns=[set() for b in B]
    for w in Q:
        images=[project(w,b) for b in B];i=max(i for i,v in enumerate(images) if v not in ps[i]);ns[i].add(images[i])
    for p,n,ref in zip(ps,ns,s['runs']):
        r=run(p,n,observer=observe);model,attempts=oracle_learner(p,n)
        assert r['model']==model and r['W']==ref['W'] and r['A']==attempts
        assert r['E']==len(set(''.join(p)))
    d=pred['decision'];h=pred['selector_work'];decisions[d]+=1
    if 'global_exact' in pred:assert pred['global_exact']==g['W']
    if 'split_exact' in pred:assert pred['split_exact']==s['W']
    if d.startswith('NET_GLOBAL'):assert h+g['W']<s['W']
    if d.startswith('NET_SPLIT'):assert h+s['W']<g['W']
    if d=='PIPELINE_GLOBAL':assert g['W']<s['W']
    if d=='PIPELINE_SPLIT':assert s['W']<g['W']
    if d=='TIE':assert g['W']==s['W']
    if pred['same_output_language'] is True:
        assert exact_equivalent(g['model'],[r['model'] for r in s['runs']],B)[0]
    if old['decision']=='UNKNOWN' and d!='UNKNOWN':
        stats['previous_unknown_resolved']+=1
        name='new_split' if 'SPLIT' in d else 'new_global' if 'GLOBAL' in d else 'new_tie'
        if name not in examples or d.startswith('NET_') and not examples[name]['certificate']['decision'].startswith('NET_'):
            examples[name]=dict(positive=sorted(P),negative=sorted(Q),blocks=[sorted(b) for b in B],
                                certificate=pred,WG=g['W'],WS=s['W'],description=description)
    stats['feasible']+=1

for n in (2,3,4,6,8,12):
    letters='abcdefghijkl'[:n]
    for shape in ('chain','star','random'):
        nodes=[''];parents={}
        for a in letters:
            parent=nodes[-1] if shape=='chain' else '' if shape=='star' else rng.choice(nodes)
            child=parent+a;parents[child]=parent;nodes.append(child)
        leaves=set(nodes)-set(parents.values())
        choices=[leaves,set(nodes),leaves|{w for w in nodes if rng.randrange(2)}]
        for P in choices:
            for Q in (set(),{'z'},{'az'},{''},{'aaa'}):
                if P&Q:continue
                for kind in ('round2','halves2','round3'):
                    k=3 if kind=='round3' else 2;B=[set() for _ in range(k)]
                    for i,a in enumerate(letters):
                        index=min(k-1,i*k//n) if kind=='halves2' else i%k
                        B[index].add(a)
                    B[-1].add('z')
                    # For n=2,k=3 the final block is the marker-only factor.
                    assert all(B)
                    check(P,Q,B,dict(n=n,shape=shape,partition=kind))

report=dict(status='passed',case_executions=stats['feasible']+stats['infeasible'],
            counts=dict(stats),decisions=dict(decisions),independent_candidate_checks=candidate_checks,
            examples=examples,note='Targeted tests supplement the infinite-family proofs.')
(root/'tree_audit_results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='examples'},indent=2))

"""Exhaustive verification of a complete finite-domain lookup table."""
from pathlib import Path
from itertools import product
from collections import Counter
import json,ast
from compiled_selector import CompiledSelector
from compile_domain import compile_table
from rpni_work_reference import run,split_run
from independent_oracle import oracle_fold,oracle_learner,independent_accept

root=Path(__file__).parent;selector=CompiledSelector(root/'table_binary_length2.json')
data=selector.data;words=data['vocabulary'];blocks=data['blocks']
counts=Counter();folds=0;g_total=local_total=prep_total=0;best=None

def observe(before,r,b,after,ok,neg):
    global folds
    assert oracle_fold(before,r,b)==after
    assert ok==all(not independent_accept(after,w) for w in neg)
    folds+=1

for labels in product(range(3),repeat=len(words)):
    P={w for w,l in zip(words,labels) if l==1};Q={w for w,l in zip(words,labels) if l==2}
    result=selector.query(P,Q)  # lookup before reference execution
    assert not result['training_started'] and result['method']=='COMPILED_LOOKUP'
    assert result['query_work']==1+len(P)+len(Q)
    g=run(P,Q,observer=observe);model,attempts=oracle_learner(P,Q)
    assert model==g['model'] and attempts==g['A']
    assert result['global_work']==g['W'];g_total+=g['W']
    prep=sum(map(len,P))+sum(map(len,Q))+len(blocks)*(len(P)+2*len(Q));prep_total+=prep
    try:s=split_run(P,Q,blocks)
    except ValueError:
        assert result['status']=='GLOBAL_ONLY';counts['GLOBAL_ONLY']+=1;continue
    assert result['split_work']==s['W']
    expected='GLOBAL' if g['W']<s['W'] else 'SPLIT' if s['W']<g['W'] else 'TIE'
    assert result['status']==expected;counts[expected]+=1
    ps=[{''.join(a for a in w if a in B) for w in P} for B in blocks];ns=[set() for B in blocks]
    for w in Q:
        images=[''.join(a for a in w if a in B) for B in blocks]
        i=max(i for i,v in enumerate(images) if v not in ps[i]);ns[i].add(images[i])
    for p,n,ref in zip(ps,ns,s['runs']):
        r=run(p,n,observer=observe);model,attempts=oracle_learner(p,n)
        assert r['model']==model and r['W']==ref['W'] and r['A']==attempts
        local_total+=r['W']
    chosen=min(g['W'],s['W']);h=result['query_work']
    assert result['chosen_pipeline_work']==chosen
    assert result['per_query_net_excludes_offline_and_setup']==(h+chosen<max(g['W'],s['W']))
    benefit=g['W']-chosen-h
    if best is None or benefit>best['per_query_benefit_vs_global']:
        best=dict(positive=sorted(P),negative=sorted(Q),blocks=blocks,
                  global_work=g['W'],split_work=s['W'],query_work=h,
                  per_query_benefit_vs_global=benefit)

e=data['offline_events'];d=len(words);size=3**d;volume=sum(map(len,words));k=len(blocks)
assert e['label_record']==d*size and e['entry_emit']==size
assert e['preparation']==prep_total==3**(d-1)*(2*volume+3*k*d)
assert e['global_learning']==g_total and e['local_learning']==local_total
assert e['local_dispatch']==k*(size-counts['GLOBAL_ONLY'])
assert data['counts']==dict(counts) and data['offline_work']==sum(e.values())
assert selector.query(['aaa'],[])['status']=='OUT_OF_DOMAIN'
assert selector.query(['a'],['a'])['status']=='INVALID'
try:compile_table(words,blocks,max_entries=1)
except ValueError:pass
else:raise AssertionError('Resource limit not enforced')
tree=ast.parse((root/'compiled_selector.py').read_text(encoding='utf8'))
imports=set()
for n in ast.walk(tree):
    if isinstance(n,ast.Import):imports.update(a.name for a in n.names)
    if isinstance(n,ast.ImportFrom):imports.add(n.module)
assert imports<={'pathlib','json','hashlib','sys'}
assert best['per_query_benefit_vs_global']>0
best['minimum_repeats_for_strict_total_saving_vs_global']=(data['offline_work']+selector.setup_work)//best['per_query_benefit_vs_global']+1
q=best['minimum_repeats_for_strict_total_saving_vs_global'];benefit=best['per_query_benefit_vs_global']
assert (q-1)*benefit<=data['offline_work']+selector.setup_work<q*benefit
report=dict(status='passed',all_domain_inputs_checked=size,counts=dict(counts),
            independent_candidate_checks=folds,offline_work=data['offline_work'],
            setup_work=selector.setup_work,best_amortization_example=best,
            note='Complete only for the declared vocabulary and partition. Compilation executes learners; lookup does not.')
(root/'compiled_audit_results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(root/'compiled_example.json').write_text(json.dumps({key:best[key] for key in ('positive','negative','blocks')},indent=2),encoding='utf8')
print(json.dumps(report,indent=2))

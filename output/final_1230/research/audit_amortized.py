"""Independent attacks on potential-based union charges and inert upper bounds."""
from pathlib import Path
from itertools import product
from collections import Counter
import json,random
from static_selector import select,mandatory_lower,forced_union_lower,inert_bounds,upper,fold_upper
from previous_selector import select as old_select
from rpni_work_reference import run,split_run
from independent_oracle import oracle_fold,independent_accept

root=Path(__file__).parent;counts=Counter();candidate_checks=0;rng=random.Random(1230)

def observe(before,r,b,after,ok,neg):
    global candidate_checks
    assert oracle_fold(before,r,b)==after
    assert ok==all(not independent_accept(after,w) for w in neg)
    candidate_checks+=1

def check(P,Q,category):
    g=run(P,Q,observer=observe);n=g['N'];e=n-1;m=sum(map(len,P));p=len(P)
    support=set(''.join(P));s=len(support)
    pref={''}|{w[:i] for w in P for i in range(1,len(w)+1)}
    t=1
    if n>1:
        x=min(w[0] for w in P if w);t=sum(x+v in pref for v in pref)
    delta=0 if not Q else 1 if '' in Q else 2
    assert mandatory_lower(m,p,n,s,delta,t)<=g['W'],(P,Q,g)
    assert g['W']<=upper(m,p,n,sum(len(w)+1 for w in Q)),(P,Q,g)
    assert g['A']<=n*(n-1)//2 and g['iterations']<=n-1
    assert g['events'].get('red_remap',0)<=n*(n-1)//2
    if n>1:
        union_work=sum(f['n']*f['unions'] for f in g['folds'])
        assert union_work>=forced_union_lower(n,t),(P,Q,union_work,n,t)
    for f in g['folds']:
        assert f['work']==2*f['n']+f['n']*f['unions']+f['e']*(f['passes']+1)
        assert 1<=f['passes']<=f['unions']
        assert f['work']<=fold_upper(f['n'],f['e'])
    inert=all(any(a not in support for a in w) for w in Q)
    if inert:
        d=sum(1+next(i for i,a in enumerate(w,1) if a not in support) for w in Q)
        lo,hi=inert_bounds(m,p,n,s,d,t)
        assert lo<=g['W']<=hi,(P,Q,lo,g['W'],hi)
        assert len(g['model'][0])==1 and g['A']==g['iterations']
        assert sum(f['unions'] for f in g['folds'])==n-1
        assert g['events'].get('red_remap',0)==g['A']
    counts[category]+=1

words=[''.join(w) for n in range(4) for w in product('ab',repeat=n)]
for mask in range(1<<len(words)):
    check({w for i,w in enumerate(words) if mask>>i&1},set(),'all_positive_subsets_length3')
for labels in product(range(3),repeat=7):
    check({w for w,l in zip(words[:7],labels) if l==1},
          {w for w,l in zip(words[:7],labels) if l==2},'all_labeled_samples_length2')

longwords=[''.join(w) for n in range(7) for w in product('ab',repeat=n)]
for _ in range(1500):
    P=set(rng.sample(longwords,rng.randrange(0,12)))
    available=[w for w in longwords if w not in P]
    Q=set(rng.sample(available,rng.randrange(0,12)))
    check(P,Q,'arbitrary_effective_negatives')
for _ in range(250):
    P=set(rng.sample(longwords,rng.randrange(0,12)))
    check(P,{'c','aac','bac','ccab'},'inert_negative_variants')

family=[]
for n in (2,3,4,5,6,8,12,20,30):
    P={'b'+'a'*n+'b'*(n-1),'ba'+'b'*(n-1)+'a'*(n-1)};B=[{'a'},{'b'}]
    cert=select(P,set(),B);prior=old_select(P,set(),B)
    check(P,set(),'two_trace_infinite_family');g=run(P,set());split=split_run(P,set(),B)
    assert cert['selector_work']==20*n+19
    assert split['W']==2*n*n+28*n+26
    assert cert['global_interval'][0]==8*n*n+38*n-6
    assert prior['decision']=='UNKNOWN'
    if n>=4:
        assert cert['decision']=='NET_SPLIT_EQUAL'
        assert 6*n*n-10*n-51>0
    family.append(dict(n=n,WG=g['W'],WS=split['W'],certificate=cert,previous=prior['decision']))
naive=inert_bounds(1,1,2,1,1)[1]
assert run({'a'},{''})['W']==25>naive==24
report=dict(status='passed',case_executions=sum(counts.values()),counts=dict(counts),
            independent_candidate_checks=candidate_checks,family=family,
            negative_premise_counterexample=dict(positive=['a'],negative=[''],actual=25,invalid_upper=24),
            note='Finite audit complements the general potential and amortization proofs.')
(root/'amortized_audit_results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(root/'two_trace_example.json').write_text(json.dumps(dict(positive=['baaaabbb','babbbaaa'],negative=[],blocks=[['a'],['b']]),indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='family'},indent=2))

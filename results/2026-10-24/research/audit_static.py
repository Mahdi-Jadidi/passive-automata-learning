"""Static predictions precede reference execution. Independent quotient oracle.
Finite tests supplement the proofs; they do not prove universal coverage.
"""
from itertools import product
from collections import Counter
from pathlib import Path
import json,random
from total_selector import decide
from static_selector import select
from bounded_policy import choose
from rpni_work_reference import run,split_run,project
from independent_oracle import oracle_fold,independent_accept,oracle_learner

root=Path(__file__).parent
stats=Counter();old=Counter();new=Counter();rules=Counter();examples={};folds=0
import previous_selector as old_module

def observe(before,r,b,after,ok,neg):
    global folds
    assert oracle_fold(before,r,b)==after
    assert ok==all(not independent_accept(after,w) for w in neg)
    folds+=1

def check(pos,neg,blocks,category):
    cert=select(pos,neg,blocks)  # before either learner
    prior=old_module.select(pos,neg,blocks)
    old[prior['decision']]+=1;new[cert['decision']]+=1;rules[cert['rule']]+=1
    g=run(pos,neg,observer=observe)
    oracle,attempts=oracle_learner(pos,neg)
    assert oracle==g['model'] and attempts==g['A']
    images=[{project(w,B) for w in pos} for B in blocks]
    feasible=all(any(project(w,B) not in P for B,P in zip(blocks,images)) for w in neg)
    if not feasible:
        assert cert['decision']=='INFEASIBLE'
        result=decide(pos,neg,blocks)
        assert result['status']=='GLOBAL_ONLY' and not result['training_started']
        stats[category]+=1;return
    s=split_run(pos,neg,blocks)
    ns=[set() for B in blocks]
    for w in neg:
        i=max(i for i,B in enumerate(blocks) if project(w,B) not in images[i])
        ns[i].add(project(w,blocks[i]))
    for P,Q,rr in zip(images,ns,s['runs']):
        r=run(P,Q,observer=observe);model,attempts=oracle_learner(P,Q)
        assert r['W']==rr['W'] and r['model']==model and r['A']==attempts
    d=cert['decision'];h=cert['selector_work']
    policy=choose(pos,neg,blocks)
    chosen=g['W'] if policy['action']=='GLOBAL' else s['W']
    assert chosen-min(g['W'],s['W'])<=policy['excess_pipeline_work_bound']
    assert h+chosen-min(g['W'],s['W'])<=policy['excess_including_selection_bound']
    assert policy['winner_certified']==(d!='UNKNOWN')
    assert prior['decision']=='UNKNOWN' or d!='UNKNOWN', 'Previously decided case lost'
    if 'global_interval' in cert:
        assert cert['global_interval'][0]<=g['W']<=cert['global_interval'][1],(pos,neg,cert,g['W'])
        assert cert['split_interval'][0]<=s['W']<=cert['split_interval'][1]
        for bounds,r in zip(cert['local_factors'],s['runs']):
            assert bounds['lower']<=r['W']<=bounds['upper']
    if 'global_exact' in cert:assert cert['global_exact']==g['W']
    if 'split_exact' in cert:assert cert['split_exact']==s['W']
    if 'split_lower' in cert:assert cert['split_lower']<=s['W']
    if 'split_minus_global_lower' in cert:assert cert['split_minus_global_lower']<=s['W']-g['W']
    if 'split_minus_global' in cert:assert cert['split_minus_global']==s['W']-g['W']
    if d.startswith('NET_GLOBAL'):assert h+g['W']<s['W']
    if d.startswith('NET_SPLIT'):assert h+s['W']<g['W']
    if d=='PIPELINE_GLOBAL':assert g['W']<s['W']
    if d=='PIPELINE_SPLIT':assert s['W']<g['W']
    if d=='TIE':assert g['W']==s['W']
    result=decide(pos,neg,blocks)
    winner='GLOBAL' if g['W']<s['W'] else 'SPLIT' if s['W']<g['W'] else 'TIE'
    assert result['status']==winner and result['status']!='UNKNOWN'
    if result['training_started']:
        assert result['global_work']==g['W'] and result['split_work']==s['W']
        assert result['diagnostic_work']==h+g['W']+s['W']
        assert result['diagnostic_work']>min(g['W'],s['W'])
        assert not result['net_advantage_certified']
    if prior['decision']=='UNKNOWN' and d!='UNKNOWN':stats['unknown_resolved_statically']+=1
    for name,condition in [('fallback',result['training_started']),
                           ('new_unary',prior['decision']=='UNKNOWN' and d!='UNKNOWN' and cert['rule']=='unary_global_inert'),
                           ('tie',winner=='TIE')]:
        if condition and name not in examples:
            examples[name]=dict(positive=sorted(pos),negative=sorted(neg),blocks=[sorted(B) for B in blocks],
                                result=result,actual_global=g['W'],actual_split=s['W'])
    stats[category]+=1

words=['','a','b','aa','ab','ba','bb']
for labels in product(range(3),repeat=len(words)):
    P={w for w,l in zip(words,labels) if l==1};Q={w for w,l in zip(words,labels) if l==2}
    for B in ([{'a'},{'b'}],[{'a','b'}]):check(P,Q,B,'exhaustive_binary')

# Arbitrary unary positive subsets, epsilon included optionally; inert negatives
# may fall into different blocks or the same multi-symbol block as the positive.
unary=['','a','aa','aaa','aaaa'];negatives=['b','ab','aab','ba','c','ac','bc']
for mask in range(1,1<<len(unary)):
    P={w for i,w in enumerate(unary) if mask>>i&1}
    for nmask in range(1<<len(negatives)):
        Q={w for i,w in enumerate(negatives) if nmask>>i&1}
        for B in ([{'a'},{'b'},{'c'}],[{'b'},{'a','c'}]):check(P,Q,B,'unary_inert')

rng=random.Random(20261022)
allwords=[''.join(t) for n in range(4) for t in product('abc',repeat=n)]
for _ in range(300):
    P=set(rng.sample(allwords,rng.randrange(0,8)))
    available=[w for w in allwords if w not in P]
    Q=set(rng.sample(available,rng.randrange(0,8)))
    check(P,Q,[{'a'},{'b'},{'c'}],'random_ternary')

for n in range(1,13):
    for P in ({'a'*n},{'', 'a'*n},{'a'*j for j in range(1,n+1)}):
        Q={'b','ab','a'*7+'c','ba'}
        for B in ([{'a'},{'b','c'}],[{'b'},{'a','c'}],[{'b','c'},{'a'}],[{'a','b'},{'c'}]):
            check(P,Q,B,'long_unary_attacks')

alphabet='abcdefghijklmnop'
for n in range(2,11):
    w=alphabet[:n]
    for k in range(2,6):
        for assignment in ('round_robin','halves','random'):
            B=[set() for _ in range(k)]
            for i,a in enumerate(alphabet[:max(n,k)]):
                j=(i%k if assignment=='round_robin' else min(k-1,i*k//n) if assignment=='halves' else rng.randrange(k))
                B[j].add(a)
            # Complete empty blocks with additional configuration symbols.
            free=iter(alphabet[max(n,k):])
            for block in B:
                if not block:block.add(next(free))
            check({w},set(),B,'distinct_word_partitions')
            if n==4 and k==2 and assignment=='halves':
                examples['distinct_word_split']=dict(positive=[w],negative=[],blocks=[sorted(b) for b in B],
                                                     result=decide({w},set(),B))
B=[set('ab'),set('cde')]+[{a} for a in 'fghijklmnop']
check({'abcde'},set(),B,'nontrivial_tie')
assert decide({'abcde'},set(),B)['status']=='TIE'

for name,x in {
    'unary_informative':json.loads((root/'counterexample_unary_informative.json').read_text(encoding='utf8')),
    'drop_unary':dict(positive=['ba'],negative=[],blocks=[['a'],['b']]),
    'local_informative':dict(positive=['aa'],negative=['ba'],blocks=[['b'],['a']]),
}.items():
    check(set(x['positive']),set(x['negative']),[set(B) for B in x['blocks']],'boundary_counterexamples')
    examples[name]=dict(input=x,result=decide(x['positive'],x['negative'],x['blocks']),
                        WG=run(x['positive'],x['negative'])['W'],
                        WS=split_run(x['positive'],x['negative'],x['blocks'])['W'])

bad=[(['a'],['a'],[['a']]),(['b'],[],[['a']]),([],[],[]),([],[],[['a'],['a']]),([1],[],[['a']])]
for args in bad:assert decide(*args)['status']=='INVALID'
stats['invalid_rejected']=len(bad)
report=dict(status='passed',valid_case_executions=sum(old.values()),counts=dict(stats),old_decisions=dict(old),new_decisions=dict(new),
            rules=dict(rules),independent_candidate_checks=folds,examples=examples,
            note='Totality is proved separately. A fallback executes learners; it is not pre-training prediction.')
(root/'audit_results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='examples'},indent=2))

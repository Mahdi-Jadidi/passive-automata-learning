"""Second adversarial audit of the exact two-region claim. STDlib only.

Uses the independent quotient oracle and exact product equivalence from the
first audit. Domain membership is computed separately from the selector.
Run: python -B audit_boundary.py
"""
from itertools import product,permutations
from math import comb
from pathlib import Path
from collections import Counter
import json
import audit_defense as audit
from defense_selector import select

def domain(pos,neg,blocks):
    p,z=len(pos),len(neg);k=len(blocks)
    alphabet=set().union(*map(set,blocks))
    used=set(''.join(pos|neg))
    if p and k>1 and any(used<=set(b) for b in blocks):
        margin=(k-1)*p+(2*k-1)*z+2*k-4-len(alphabet)
        return 'G' if margin>0 else None
    if k!=3 or any(len(b)!=1 for b in blocks) or not pos:return None
    a,b,c=(next(iter(B)) for B in blocks)
    if neg!={c}:return None
    # Derive n from the common word length; do not call the implementation's
    # histogram recognizer or use the same first-word count expression.
    length=len(next(iter(pos)))
    if not length or length%2:return None
    n=length//2
    if len(pos)!=comb(2*n,n):return None
    if all(len(w)==length and set(w)<=set(a+b) and w.count(a)==n for w in pos):return 'S'
    return None

stats=Counter();examples=[]
def check(pos,neg,blocks,category):
    expected=domain(pos,neg,blocks)
    # Both membership and selection finish BEFORE the learners.
    answer=select(pos,neg,blocks)
    assert answer['certified_region']==expected,(pos,neg,blocks,answer,expected)
    pred,g,s=audit.checked(pos,neg,blocks,category)
    if expected:
        h=pred['selector_work']
        assert audit.exact_equivalent(g['model'],[r['model'] for r in s['runs']],blocks)[0]
        if expected=='G':assert h+g['W']<s['W']
        else:assert h+s['W']<g['W']
    if pred.get('rule')=='single_active_block':
        p,z=len(pos),len(neg);k=len(blocks)
        margin=(k-1)*p+(2*k-1)*z+2*k-4-sum(map(len,blocks))
        assert s['W']-g['W']-pred['selector_work']==margin
        stats['global_margin_positive' if margin>0 else 'global_margin_zero' if margin==0 else 'global_margin_negative']+=1
    stats[category]+=1
    return answer

words=['','a','b','aa','ab','ba','bb']
for j,labels in enumerate(product((-1,0,1),repeat=len(words))):
    pos={w for w,v in zip(words,labels) if v==1}
    if not pos:continue
    neg={w for w,v in zip(words,labels) if v==-1}
    # A multisymbol active block, with deliberately different validation cost
    # from the unused alphabet. Some pass the net guard; others cannot pass it.
    unused=''.join(chr(0x400+t) for t in range((j%13)+1))
    check(pos,neg,['ab',unused],'multisymbol_global_and_unused_alphabet')
print('Expanded Global boundary complete',flush=True)

for abc in permutations('abc'):
    a,b,c=abc
    for order in permutations(abc):
        for n in (1,2,3):
            check(audit.balanced(n,a,b),{c},list(order),'all_block_orders_and_symbol_renamings')

for a,b,c in [('x','y','z'),('α','β','γ'),('0','!','?')]:
    for n in (1,2,3):check(audit.balanced(n,a,b),{c},[a,b,c],'nonstandard_symbol_orders')

for n in (1,2,3):
    pos=audit.balanced(n)
    check(pos,set(),['a','b'],'positive_only_outside_admitted_region')
    for w in sorted(pos):check(pos-{w},{'c'},['a','b','c'],'one_missing_positive')
    check(pos|{''},{'c'},['a','b','c'],'extra_empty_positive')
    check(pos,{'c','' },['a','b','c'],'extra_empty_negative')

# Explicit strict-boundary witnesses. Alphabet size changes H, not either
# learner's active data. These examples test < versus <=.
for inactive,expected in [('x','NET_GLOBAL'),('xy','COST_ONLY'),('xyz','COST_ONLY')]:
    result=check({'a','aa','aaa'},set(),['a',inactive],'strict_net_threshold')
    assert result['status']==expected,(inactive,result)
    examples.append({'inactive_block':inactive,'result':result})

result={'status':'passed','valid_samples':sum(audit.counts.values()),
        'independent_candidate_checks':audit.candidate_checks,'counts':dict(stats),
        'strict_boundary_examples':examples,
        'claim':'Exact membership and sound net decisions for the two admitted regions; finite audit supplements proof.'}
Path(__file__).with_name('boundary_audit_results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='strict_boundary_examples'},indent=2))

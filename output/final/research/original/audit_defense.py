"""Adversarial finite audit. This supplements, and does not replace, proofs.

Run: python -B audit_defense.py
No random sampling, no wall-clock inference. Outputs audit_results.json.
The oracle uses set partitions and transition saturation, not the reference's
flat relabel loop. Every reference candidate is checked against this oracle.
"""
from collections import deque,Counter
from itertools import product,permutations
from pathlib import Path
from math import comb
import json
from certified_selector import predict,initialization,generic_upper,fold_upper
from rpni_work_reference import run,split_run

def key(w):return len(w),w
def independent_accept(model,word):
    states,edges,finals,q=model
    for a in word:
        q=edges.get((q,a),None)
        if q is None:return False
    return q in finals

def oracle_fold(model,r,b):
    states,edges,finals,start=model
    parts=[{r,b}]+[{q} for q in states if q not in (r,b)]
    while True:
        block={q:i for i,C in enumerate(parts) for q in C}
        obligations={}
        for (q,a),t in edges.items():obligations.setdefault((block[q],a),set()).add(block[t])
        conflict=next((targets for targets in obligations.values() if len(targets)>1),None)
        if conflict is None:break
        merged=set().union(*(parts[i] for i in conflict))
        parts=[C for i,C in enumerate(parts) if i not in conflict]+[merged]
    names={q:min(C,key=key) for C in parts for q in C}
    return (set(names.values()),{(names[q],a):names[t] for (q,a),t in edges.items()},
            {names[q] for q in finals},names[start])

candidate_checks=0
def observer(before,r,b,after,ok,neg):
    global candidate_checks
    expected=oracle_fold(before,r,b)
    assert expected==after,('incorrect quotient',before,r,b,expected,after)
    assert ok==all(not independent_accept(expected,w) for w in neg)
    candidate_checks+=1

def oracle_learner(pos,neg):
    states={''}|{w[:j] for w in pos for j in range(1,len(w)+1)}
    model=(states,{(w[:-1],w[-1]):w for w in states if w},set(pos),'')
    red={''};attempts=0
    while True:
        blue={t for (q,a),t in model[1].items() if q in red and t not in red}
        if not blue:return model,attempts
        b=min(blue,key=key)
        for r in sorted(red,key=key):
            attempts+=1;candidate=oracle_fold(model,r,b)
            if all(not independent_accept(candidate,w) for w in neg):
                # A former red state maps to the canonical member of its class.
                # Recover the partition from canonical quotient paths.
                newred=set()
                for old in red:
                    q=candidate[3]
                    for a in old:q=candidate[1][q,a]
                    newred.add(q)
                model,red=candidate,newred
                break
        else:red.add(b)

def exact_equivalent(global_model,local_models,blocks):
    """BFS on completed synchronous product, including implicit rejecting sinks."""
    alphabet=sorted(set().union(*map(set,blocks)))
    initial=(global_model[3],)+tuple(m[3] for m in local_models)
    todo=deque([(initial,'')]);seen={initial}
    while todo:
        qs,w=todo.popleft()
        left=qs[0] in global_model[2]
        right=all(q in m[2] for q,m in zip(qs[1:],local_models))
        if left!=right:return False,w
        for a in alphabet:
            nxt=(global_model[1].get((qs[0],a)),)+tuple(
                m[1].get((q,a)) if a in B else q
                for q,m,B in zip(qs[1:],local_models,blocks))
            if nxt not in seen:seen.add(nxt);todo.append((nxt,w+a))
    return True,None

def local_data(pos,neg,blocks):
    ps=[{''.join(a for a in w if a in B) for w in pos} for B in blocks]
    ns=[set() for B in blocks]
    for w in neg:
        images=[''.join(a for a in w if a in B) for B in blocks]
        witness=[i for i,v in enumerate(images) if v not in ps[i]]
        if not witness:return None
        ns[witness[-1]].add(images[witness[-1]])
    return ps,ns

counts=Counter();decisions=Counter();examples=[]
def checked(pos,neg,blocks,category):
    # Selection must finish before any learner call.
    pred=predict(pos,neg,blocks);decisions[pred['decision']]+=1
    g=run(pos,neg,observer=observer)
    assert all(independent_accept(g['model'],w) for w in pos)
    assert all(not independent_accept(g['model'],w) for w in neg)
    independent,attempts=oracle_learner(pos,neg)
    assert independent==g['model'] and attempts==g['A']
    n=g['N'];I=initialization(sum(map(len,pos)),len(pos),n)
    U=generic_upper(sum(map(len,pos)),len(pos),n,sum(len(w)+1 for w in neg))
    assert I<=g['W']<=U and g['iterations']<=n-1 and g['A']<=n*(n-1)//2
    for f in g['folds']:assert f['work']<=fold_upper(f['n'],f['e'])
    local=local_data(pos,neg,blocks)
    assert (local is None)==(pred['decision']=='INFEASIBLE')
    if local is None:counts[category]+=1;return pred,g,None
    ps,ns=local;locals_=[run(p,z,observer=observer) for p,z in zip(ps,ns)]
    prep=sum(map(len,pos))+sum(map(len,neg))+len(blocks)*(len(pos)+2*len(neg))
    s=split_run(pos,neg,blocks)
    assert s['W']==prep+sum(x['W'] for x in locals_)
    assert [r['model'] for r in s['runs']]==[r['model'] for r in locals_]
    for r,p,z in zip(locals_,ps,ns):
        independent,attempts=oracle_learner(p,z)
        assert independent==r['model'] and attempts==r['A']
        assert all(independent_accept(r['model'],w) for w in p)
        assert all(not independent_accept(r['model'],w) for w in z)
    if pred['decision']=='GLOBAL':assert g['W']<s['W']
    if pred['decision']=='SPLIT':assert s['W']<g['W']
    if pred['rule']=='single_active_block':
        assert s['W']-g['W']==pred['cost_gap_split_minus_global']
        assert pred['beats_split_baseline_including_selector']==(pred['selector_work']+g['W']<s['W'])
    if pred['rule'].startswith('complete_balanced_interleavings'):
        assert pred['global_lower']<=g['W'] and s['W']<=pred['split_upper']
        if pred['beats_global_baseline_including_selector']:assert pred['selector_work']+s['W']<g['W']
    if pred['rule']=='static_intervals':
        assert pred['global_interval'][0]<=g['W']<=pred['global_interval'][1]
        assert pred['split_interval'][0]<=s['W']<=pred['split_interval'][1]
    if pred.get('same_output_language') is True:
        assert exact_equivalent(g['model'],[r['model'] for r in locals_],blocks)[0]
    counts[category]+=1
    return pred,g,s

def balanced(n,a='a',b='b'):
    return {''.join(w) for w in product((a,b),repeat=2*n) if w.count(a)==n}

def main():
    words=['','a','b','aa','ab','ba','bb']
    for labels in product((-1,0,1),repeat=7):
        checked({w for w,v in zip(words,labels) if v==1},{w for w,v in zip(words,labels) if v==-1},['a','b'],'exhaustive_binary_samples')
    print('Binary exhaustive audit complete',flush=True)
    for abc in permutations('abc'):
        a,b,c=abc
        for n in range(1,5):
            pred,g,s=checked(balanced(n,a,b),{c},list(abc),'renamed_full_families')
            assert pred['decision']=='SPLIT' and pred['beats_global_baseline_including_selector']
            if abc==('a','b','c'):examples.append({'n':n,'prediction':pred,'global':g['W'],'split':s['W']})
    pred,g,s=checked(balanced(5),{'c'},['a','b','c'],'family_n5')
    examples.append({'n':5,'prediction':pred,'global':g['W'],'split':s['W']})
    print('Renamed families complete',flush=True)
    family=sorted(balanced(2))
    for mask in range(1<<len(family)):
        checked({w for j,w in enumerate(family) if mask>>j&1},{'c'},['a','b','c'],'all_subsets_n2')
    for w in balanced(3):checked(balanced(3)-{w},{'c'},['a','b','c'],'delete_one_n3')
    for n in (1,2,3):
        for extra in ('a','b','aa','bb','ab','ba','aaa','bbb','ca','ac','bc','cb',''):
            pos=balanced(n)
            if extra not in pos:checked(pos,{'c',extra},['a','b','c'],'extra_negatives')
        checked(balanced(n)|{'a'*(2*n)},{'c'},['a','b','c'],'extra_positive')
    invalid=[({'a'},{'a'},['a','b']),({'a'},set(),[]),({'a'},set(),['a','']),({'a'},set(),['a','ab']),({'z'},set(),['a','b'])]
    for args in invalid:
        try:predict(*args)
        except ValueError:counts['invalid_inputs_rejected']+=1
        else:raise AssertionError(('invalid accepted',args))
    pred,g,s=checked({''},set(),['a','b'],'overhead_counterexample')
    assert (pred['selector_work'],g['W'],s['W'])==(7,4,10)
    assert pred['selector_work']+g['W']>s['W']
    recovery=run({'ab','ba'},{'c'})['model']
    assert independent_accept(recovery,'') and '' not in {'ab','ba'}
    counts['equal_output_not_target_recovery_counterexample']+=1
    for n in (3,4):
        p=comb(2*n,n)
        pred,g,s=checked({'a'*j for j in range(1,p+1)},{'a'*(p+1)},['a','b','c'],'equal_count_global_family')
        assert pred['decision']=='GLOBAL'
    result={'status':'passed','claim':'Finite adversarial checks supplement mathematical proofs. No proof-assistant or wall-clock guarantee.',
            'counts':dict(counts),'decisions':dict(decisions),'independent_candidate_checks':candidate_checks,
            'language_equivalence_method':'Exact reachable-product BFS with implicit rejecting sinks',
            'reference_oracle':'Set-partition saturation and independent learner',
            'overhead_counterexample':{'global':4,'split':10,'selector':7,'selector_plus_global':11},'family_examples':examples}
    Path(__file__).with_name('audit_results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

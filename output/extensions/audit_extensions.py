"""Reproducible deletion experiments and adversarial checks of new theorems.
All predictions are obtained BEFORE reference learners are invoked.
"""
from itertools import product,combinations,permutations
from collections import Counter
from pathlib import Path
from math import comb
import csv,json,random
from extended_selector import select
from rpni_work_reference import run,split_run
from independent_oracle import oracle_fold,oracle_learner,independent_accept,exact_equivalent

root=Path(__file__).parent
counts=Counter();decisions=Counter();rows=[];examples={};candidate_checks=0;quality_example=None
def observe(before,r,b,after,ok,neg):
    global candidate_checks
    assert oracle_fold(before,r,b)==after
    assert ok==all(not independent_accept(after,w) for w in neg)
    candidate_checks+=1

def check(pos,neg,blocks,category,metadata=None):
    global quality_example
    pred=select(pos,neg,blocks) # ALWAYS before learning
    g=run(pos,neg,observer=observe)
    oracle,attempts=oracle_learner(pos,neg)
    assert oracle==g['model'] and attempts==g['A']
    try:s=split_run(pos,neg,blocks)
    except ValueError:
        assert pred['decision']=='INFEASIBLE'
        counts[category]+=1;decisions[pred['decision']]+=1;return pred,g,None
    assert pred['decision']!='INFEASIBLE'
    # Observe local candidates independently of split_run's unobserved call.
    ps=[{''.join(a for a in w if a in B) for w in pos} for B in blocks]
    ns=[set() for B in blocks]
    for w in neg:
        images=[''.join(a for a in w if a in B) for B in blocks]
        witness=max(i for i in range(len(blocks)) if images[i] not in ps[i])
        ns[witness].add(images[witness])
    for p,z,rr in zip(ps,ns,s['runs']):
        local=run(p,z,observer=observe);assert local['model']==rr['model']
        oracle,attempts=oracle_learner(p,z)
        assert oracle==local['model'] and attempts==local['A']
    if 'global_interval' in pred:
        assert pred['global_interval'][0]<=g['W']<=pred['global_interval'][1],(pred,g)
        assert pred['split_interval'][0]<=s['W']<=pred['split_interval'][1],(pred,s)
        for bounds,r in zip(pred['local_factors'],s['runs']):
            assert bounds['lower']<=r['W']<=bounds['upper']
            if bounds['exact']:assert bounds['lower']==r['W']==bounds['upper']
        # The first attempted quotient must pay for at least T class unions,
        # regardless of whether its negative test subsequently rejects it.
        if pred['forced_prefix_pairs']:
            assert g['folds'][0]['unions']>=pred['forced_prefix_pairs']
    if pred['rule']=='one_letter_positive_empty_negative':
        assert g['W']==pred['global_exact']==25 and s['W']==pred['split_exact']
    d=pred['decision'];h=pred['selector_work']
    if d.startswith('NET_SPLIT'):assert h+s['W']<g['W']
    if d.startswith('NET_GLOBAL'):assert h+g['W']<s['W']
    if d=='PIPELINE_SPLIT':assert s['W']<g['W']
    if d=='PIPELINE_GLOBAL':assert g['W']<s['W']
    if pred.get('same_output_language') is True:
        assert exact_equivalent(g['model'],[r['model'] for r in s['runs']],blocks)[0]
    elif d=='NET_SPLIT_COST' and quality_example is None:
        equivalent,witness=exact_equivalent(g['model'],[r['model'] for r in s['runs']],blocks)
        if not equivalent:
            payload=dict(positive=sorted(pos),negative=sorted(neg),blocks=blocks,
                         witness=witness,global_accept=independent_accept(g['model'],witness),
                         split_accept=all(independent_accept(r['model'],''.join(a for a in witness if a in B))
                                          for r,B in zip(s['runs'],blocks)))
            (root/'quality_counterexample.json').write_text(json.dumps(payload,indent=2),encoding='utf8')
            quality_example=payload
    counts[category]+=1;decisions[d]+=1
    row=dict(category=category,positives=len(pos),negatives=len(neg),decision=d,
             rule=pred['rule'],H=h,WG=g['W'],WS=s['W'],net_split_margin=g['W']-s['W']-h,
             first_fold_unions=g['folds'][0]['unions'] if g['folds'] else 0,
             T=pred.get('forced_prefix_pairs'),N=g['N'])
    if metadata:row.update(metadata)
    if category=='all_one_two_deletions_n3':assert d=='NET_SPLIT_EQUAL'
    if category=='deletion_path' and 0<metadata['removed']<metadata['complete_size']:
        n=metadata['n'];p=len(pos);M=2*n*p
        assert h==2*M+6*p+2*g['N']+4*n+32,(row,pred)
        if (n==3 and metadata['removed']<=2) or (n==4 and metadata['removed']<=7):
            assert d=='NET_SPLIT_EQUAL',(row,pred)
    rows.append(row)
    if category=='deletion_path' and d=='NET_SPLIT_EQUAL' and metadata['removed']>0:
        examples.setdefault('incomplete_net_equal',(pos,neg,blocks,pred,row))
    if category=='informative_negatives' and d=='NET_SPLIT_COST':
        examples.setdefault('informative_net_cost',(pos,neg,blocks,pred,row))
    if pred['rule']=='one_letter_positive_empty_negative' and d=='NET_GLOBAL_EQUAL':
        examples.setdefault('informative_global_equal',(pos,neg,blocks,pred,row))
    return pred,g,s

def balanced(n,a='a',b='b'):
    # Choose a positions, rather than generating the entire binary cube.
    ans=set()
    for indexes in combinations(range(2*n),n):
        positions=set(indexes);ans.add(''.join(a if j in positions else b for j in range(2*n)))
    return ans

def main():
    words=['','a','b','aa','ab','ba','bb']
    for labels in product((-1,0,1),repeat=len(words)):
        check({w for w,v in zip(words,labels) if v==1},
              {w for w,v in zip(words,labels) if v==-1},['a','b'],'exhaustive_binary')
    print('Exhaustive binary complete',flush=True)
    fam=sorted(balanced(2))
    for mask in range(1<<len(fam)):
        check({w for j,w in enumerate(fam) if mask>>j&1},{'c'},['a','b','c'],'all_subsets_n2')
    fam=balanced(3)
    for r in (1,2):
        for missing in combinations(sorted(fam),r):
            check(fam-set(missing),{'c'},['a','b','c'],'all_one_two_deletions_n3')
    print('Subset attacks complete',flush=True)
    for n in (1,2,3,4):
        base=sorted(balanced(n))
        orders=[('lex',base),('reverse',list(reversed(base))),
                ('run_count',sorted(base,key=lambda w:(sum(x!=y for x,y in zip(w,w[1:])),w)))]
        shuffled=list(base);random.Random(1729+n).shuffle(shuffled);orders.append(('seeded_shuffle',shuffled))
        for name,order in orders:
            current=set(base)
            for removed in range(len(base)+1):
                check(current,{'c'},['a','b','c'],'deletion_path',
                      dict(n=n,order=name,removed=removed,complete_size=len(base)))
                if removed<len(base):current=current-{order[removed]}
    print('Deletion paths complete',flush=True)
    for n in (1,2,3,4):
        base=balanced(n)
        for positives in (base,base-{min(base)},set(sorted(base)[::2])):
            for extra in ('','a','b','aa','bb','aaa','bbb','ab','ba','a'*n,'b'*n):
                if extra in positives:continue
                check(positives,{'c',extra},['a','b','c'],'informative_negatives',dict(n=n,extra=repr(extra)))
            for negatives in ({'c','cc'},{'ac','bc','ccc'},{'c','a','b'},{'c','', 'a','b'}):
                if positives&negatives:continue
                check(positives,negatives,['a','b','c'],'multiple_negatives',dict(n=n))
    # Arbitrary nonbalanced positives and inert negatives: equality theorem
    # requires no balanced histograms and no complete-family condition.
    for positives in ({'a','b'},{'a','bb','aba'},{'','aab','ba'}, {'aaab','bbaa'}):
        for negatives in ({'c'},{'ac','bc','cc'}):
            check(positives,negatives,['a','b','c'],'unbalanced_positives')
    for abc in permutations('abc'):
        a,b,c=abc
        for blocks in permutations(abc):
            check(balanced(2,a,b)-{a*2+b*2},{c,b},list(blocks),'block_order_attack')
    for blocks in (['a','b'],['b','a'],['ab','c'],['a','bc'],['a','b','c']):
        other=next(a for B in blocks for a in B if a!='a')
        for negatives in ({'',other},{'',other,other*2,'aa'}, {'','aaa',other+'a'}):
            check({'a'},negatives,blocks,'informative_global_family')
    for r in range(1,16):
        # Nonconsecutive unary positive lengths, including epsilon, audit the
        # exact local cost formula independently of the balanced family.
        check({'a'*r,'b',''}, {'c'}, ['a','b','c'],'unary_exact_cost')

    for name,(pos,neg,blocks,pred,row) in examples.items():
        payload=dict(positive=sorted(pos),negative=sorted(neg),blocks=blocks)
        (root/(name+'.json')).write_text(json.dumps(payload,indent=2),encoding='utf8')
        (root/(name+'_certificate.json')).write_text(json.dumps(pred,indent=2),encoding='utf8')
    with (root/'extension_experiments.csv').open('w',newline='',encoding='utf8') as f:
        fields=sorted(set().union(*(r.keys() for r in rows)))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    paths={}
    for n in (1,2,3,4):
        for order in ('lex','reverse','run_count','seeded_shuffle'):
            rr=[r for r in rows if r['category']=='deletion_path' and r['n']==n and r['order']==order]
            paths[f'n{n}_{order}']=dict(total=len(rr),certified=sum(r['decision']=='NET_SPLIT_EQUAL' for r in rr),
                largest_removed_certified=max((r['removed'] for r in rr if r['decision']=='NET_SPLIT_EQUAL'),default=None),
                actual_winner_changes=sum((a['WG']>a['WS'])!=(b['WG']>b['WS']) for a,b in zip(rr,rr[1:])))
    result=dict(status='passed',valid_case_executions=sum(counts.values()),counts=dict(counts),
                decisions=dict(decisions),independent_candidate_checks=candidate_checks,
                deletion_paths=paths,examples={n:r[-1] for n,r in examples.items()},
                unequal_output_counterexample=quality_example,
                guarantee='Finite audit supplements the mathematical proofs; no wall-clock claim.')
    assert 'incomplete_net_equal' in examples and 'informative_net_cost' in examples and 'informative_global_equal' in examples
    assert quality_example is not None
    for x in [([],[],[]),(['a'],[],['a','']),(['a'],[],['a','ab']),(['a'],['a'],['a','b']),(['z'],[],['a','b'])]:
        try:select(*x)
        except ValueError:pass
        else:raise AssertionError(('invalid input accepted',x))
    result['invalid_inputs_rejected']=5
    (root/'extension_audit_results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

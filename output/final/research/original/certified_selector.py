"""Pre-run certificates. This module never imports or invokes a learner.

Use: python certified_selector.py input.json
JSON: {"positive":[...], "negative":[...], "blocks":["ab","xy"]}
Decision is for the declared W loop-event model, not milliseconds.
UNKNOWN means the proved inequalities do not decide that input.
"""
from math import comb
import json,sys

def fold_upper(n,e):return n*e+n*n+3*n+e
def initialization(m,p,n):return m+p+2*n-1
def generic_upper(m,p,n,d):
    e=n-1;b=n*(n-1)//2
    return initialization(m,p,n)+n*(3*n+e)+b*(1+fold_upper(n,e)+d)
def unary_positive_upper(n):return 2*n*n+17*n+12

def predict(pos,neg,blocks):
    pos,neg=set(pos),set(neg);blocks=[set(b) for b in blocks]
    # H uses the same kind of loop-event accounting as W: one event per
    # alphabet block/letter, input word/symbol, active-block test, family-record
    # test, and final family-cardinality test. Native set/hash/arithmetic costs
    # are outside both W and H; H is not a CPython instruction count.
    h=0;owner={}
    if not blocks:raise ValueError('Empty partition')
    for i,B in enumerate(blocks):
        h+=1
        if not B:raise ValueError('Empty partition block')
        for a in B:
            h+=1
            if a in owner:raise ValueError('Overlapping partition blocks')
            owner[a]=i
    used=set();hist={};m=mn=0
    for positive,words in ((True,pos),(False,neg)):
        for w in words:
            h+=1
            if positive and w in neg:raise ValueError('Conflicting labels')
            counts={}
            for a in w:
                h+=1
                if a not in owner:raise ValueError('Unknown input symbol')
                used.add(a);counts[a]=counts.get(a,0)+1
            if positive:hist[w]=counts;m+=len(w)
            else:mn+=len(w)
    k=len(blocks);p=len(pos);z=len(neg);active=[]
    for i,B in enumerate(blocks):
        h+=1
        if used<=B:active.append(i)
    if pos and k>1 and active:
        prep=m+mn+k*(p+2*z)
        gap=prep+4*(k-1)
        return {'decision':'GLOBAL','rule':'single_active_block','cost_gap_split_minus_global':gap,
                'selector_work':h,'beats_split_baseline_including_selector':h<gap,
                'same_output_language':True,'scope':'Specified W event model'}
    # A family recognizer uses lengths, symbol counts and input-set cardinality.
    # No global PTA, local training, merge, or run trace is built here.
    marker_case=k==3 and all(len(B)==1 for B in blocks) and neg=={next(iter(blocks[2]))}
    if ((not neg and k==2) or marker_case) and all(len(B)==1 for B in blocks) and pos:
        a,b=(next(iter(B)) for B in blocks[:2])
        first=next(iter(pos));n=hist[first].get(a,0);balanced=n>=1
        for w,counts in hist.items():
            h+=1
            if len(w)!=2*n or counts.get(a,0)!=n or counts.get(b,0)!=n:balanced=False
        h+=1
        if balanced and p==comb(2*n,n):
            N=comb(2*n+2,n+1)-1
            # The first quotient equates t and a+t for every t with n-1 a's
            # and n b's. These C(2n-1,n-1) pairs have disjoint endpoints.
            forced_unions=comb(2*n-1,n-1)
            lower_g=initialization(m,p,N)+forced_unions*N
            prep=m+mn+k*(p+2*z)
            upper_s=prep+2*unary_positive_upper(n)+(4 if marker_case else 0)
            if marker_case:
                # Mandatory first fringe, map initialization/reconstruction,
                # closure/reconstruction edge scans, attempt, c test, remap.
                # See Sample_Size_Theorems_EN.md for the disjoint event counts.
                lower_g+=7*N+1
                if n==1:
                    # Fixed structural proof: Global folds two candidates of
                    # costs 32 and 21. Unary factors cost exactly 23 each.
                    lower_g=103
                    upper_s=prep+2*23+4
            if upper_s<lower_g:
                return {'decision':'SPLIT','rule':'complete_balanced_interleavings_with_marker' if marker_case else 'complete_balanced_interleavings','n':n,
                        'global_lower':lower_g,'split_upper':upper_s,'selector_work':h,
                        'beats_global_baseline_including_selector':h+upper_s<lower_g,
                        'same_output_language':True,'scope':'Specified W event model'}
    # General static certificate. Feature extraction uses projections/prefixes only.
    def proj(w,B):return ''.join(a for a in w if a in B)
    ps=[{proj(w,B) for w in pos} for B in blocks];ns=[set() for B in blocks]
    for w in neg:
        witnesses=[i for i,B in enumerate(blocks) if proj(w,B) not in ps[i]]
        if not witnesses:return {'decision':'INFEASIBLE','scope':'Conjunctive finite-sample decomposition'}
        i=witnesses[-1];ns[i].add(proj(w,blocks[i]))
    def features(P,Q):
        prefixes={''}|{w[:j] for w in P for j in range(1,len(w)+1)}
        M=sum(map(len,P));D=sum(len(w)+1 for w in Q);N=len(prefixes)
        return initialization(M,len(P),N),generic_upper(M,len(P),N,D)
    lg,ug=features(pos,neg)
    prep=m+mn+k*(p+2*z);pairs=[features(P,Q) for P,Q in zip(ps,ns)]
    ls=prep+sum(x[0] for x in pairs);us=prep+sum(x[1] for x in pairs)
    answer='SPLIT' if us<lg else 'GLOBAL' if ug<ls else 'UNKNOWN'
    # General feature-building work is not charged by the specialized h formula.
    return {'decision':answer,'rule':'static_intervals','global_interval':[lg,ug],
            'split_interval':[ls,us],'selector_work':None,
            'net_gain_including_selector':'not certified','same_output_language':'not claimed',
            'output_requirement':'sample consistency; D-membership not guaranteed for raw global RPNI',
            'scope':'Specified W event model'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python certified_selector.py input.json')
    data=json.load(open(sys.argv[1],encoding='utf8'))
    print(json.dumps(predict(data['positive'],data['negative'],data['blocks']),ensure_ascii=False,indent=2))

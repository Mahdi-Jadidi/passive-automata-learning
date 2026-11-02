"""Static pre-training certificates extending output/defense.

Never imports a learner. Cost = declared W_ref/H loop events, not time.
NET_*_COST does NOT assert equal output languages. NET_*_EQUAL does.
Run: python -B extended_selector.py sample.json
"""
from math import comb
from collections import Counter
import json,sys

def initial(m,p,n):return m+p+2*n-1
def fold_upper(n,e):return n*e+n*n+3*n+e
def upper(m,p,n,d):
    if n==1:return initial(m,p,n)+2
    e=n-1;b=n*(n-1)//2
    return initial(m,p,n)+n*(3*n+e)+b*(1+fold_upper(n,e)+d)

def unary_exact(m,p,r):
    """Nonempty unary positives, maximum exponent r>=1, no negatives."""
    passes=1 if r==1 else 2
    return m+p+r*r+(9+passes)*r+10

def select(positive,negative,partition):
    pos,neg=set(positive),set(negative);blocks=[set(B) for B in partition]
    h=Counter();owner={}
    if not blocks:raise ValueError('Empty partition')
    for i,B in enumerate(blocks):
        h['block']+=1
        if not B:raise ValueError('Empty block')
        for a in B:
            h['alphabet_character']+=1
            if len(a)!=1:raise ValueError('Alphabet symbols must be single characters')
            if a in owner:raise ValueError('Overlapping blocks')
            owner[a]=i
    if pos&neg:raise ValueError('Contradictory labels')
    hist={};used=set();positive_support=set();M=Mn=0
    for positive,words in ((True,pos),(False,neg)):
        for w in words:
            h['input_word']+=1;counts={}
            for a in w:
                h['input_character']+=1
                if a not in owner:raise ValueError('Unknown character')
                used.add(a);counts[a]=counts.get(a,0)+1
                if positive:positive_support.add(a)
            if positive:hist[w]=counts;M+=len(w)
            else:Mn+=len(w)
    k=len(blocks);p=len(pos);z=len(neg);active=[]
    for i,B in enumerate(blocks):
        h['active_test']+=1
        if used<=B:active.append(i)
    prep=M+Mn+k*(p+2*z)
    def result(decision,rule,equal=None,**extra):
        H=sum(h.values())
        return dict(decision=decision,rule=rule,selector_work=H,
                    selector_events=dict(h),same_output_language=equal,
                    metric='W_ref loop events; library internals excluded',**extra)
    if p and k>1 and active:
        gap=prep+4*(k-1)
        return result('NET_GLOBAL_EQUAL' if sum(h.values())<gap else 'PIPELINE_GLOBAL',
                      'single_active_block',True,split_minus_global=gap)

    # Preserve the old fully proved branch before paying new feature costs.
    marker=(k==3 and all(len(B)==1 for B in blocks)
            and neg=={next(iter(blocks[2]))})
    if marker and pos:
        a,b=(next(iter(B)) for B in blocks[:2]);first=next(iter(pos))
        n=hist[first].get(a,0);balanced=n>=1
        for w,counts in hist.items():
            h['balanced_record']+=1
            if len(w)!=2*n or counts.get(a,0)!=n or counts.get(b,0)!=n:balanced=False
        h['balanced_cardinality']+=1
        if balanced and p==comb(2*n,n):
            N=comb(2*n+2,n+1)-1
            lg=initial(M,p,N)+N*(p//2)+7*N+1
            us=M+3*p+4*n*n+34*n+35
            if n==1:lg,us=103,67
            if sum(h.values())+us<lg:
                return result('NET_SPLIT_EQUAL','original_complete_balanced',True,
                              global_lower=lg,split_upper=us,n=n)

    # New informative-negative family: the sole positive is one character;
    # epsilon is negative. Its only possible candidate is rejected by epsilon.
    h['singleton_gate']+=1
    if p==1 and len(next(iter(pos)))==1 and '' in neg and k>1:
        gap=prep+4*(k-1)
        return result('NET_GLOBAL_EQUAL' if sum(h.values())<gap else 'PIPELINE_GLOBAL',
                      'one_letter_positive_empty_negative',True,
                      global_exact=25,split_exact=25+gap,split_minus_global=gap)

    # Build static positive-prefix features and local samples. No edges, fold,
    # red/blue simulation, quotient or hypothesis is constructed.
    prefixes={''};h['global_prefix_create']+=1
    local_pos=[set() for B in blocks];local_neg=[set() for B in blocks]
    pending=[];first_letters=set()
    for positive,words in ((True,pos),(False,neg)):
        for w in words:
            h['projection_word']+=1;buckets={};q=''
            if positive and w:first_letters.add(w[0])
            for a in w:
                h['projection_character']+=1;buckets.setdefault(owner[a],[]).append(a)
                if positive:
                    q+=a
                    if q not in prefixes:h['global_prefix_create']+=1;prefixes.add(q)
            images=[]
            for i in range(k):
                h['projection_slot']+=1;v=''.join(buckets.get(i,[]))
                if positive:local_pos[i].add(v)
                else:images.append(v)
            if not positive:pending.append(images)
    for images in pending:
        witness=None
        for i,v in enumerate(images):
            h['negative_witness_slot']+=1
            if v not in local_pos[i]:witness=i
        if witness is None:return result('INFEASIBLE','negative_witness',None)
        local_neg[witness].add(images[witness])

    N=len(prefixes);lg=initial(M,p,N);ug=upper(M,p,N,Mn+z);T=0;first=None
    if first_letters:
        first=min(first_letters)
        for t in prefixes:
            h['prefix_pair_test']+=1
            if first+t in prefixes:T+=1
        delta=0 if not neg else 1 if '' in neg else 2
        lg+=N*T+4*N+3*(N-1)+1+delta
    lows=[];ups=[];supports=[];local_records=[]
    all_local_negatives_inert=True
    for P,Q in zip(local_pos,local_neg):
        h['local_factor']+=1;pref={''};h['local_prefix_create']+=1
        support=set();m=0;d=0
        for w in P:
            h['local_positive_word']+=1;q=''
            for a in w:
                h['local_positive_character']+=1;m+=1;support.add(a);q+=a
                if q not in pref:h['local_prefix_create']+=1;pref.add(q)
        for w in Q:
            h['local_negative_word']+=1;outside=False;d+=len(w)+1
            for a in w:
                h['local_negative_character']+=1
                if a not in support:outside=True
            if not outside:all_local_negatives_inert=False
        nloc=len(pref);lo=initial(m,len(P),nloc);hi=upper(m,len(P),nloc,d)
        exact=False
        if nloc==1:lo=hi=lo+2;exact=True
        elif len(support)==1 and not Q:
            lo=hi=unary_exact(m,len(P),nloc-1);exact=True
        lows.append(lo);ups.append(hi);supports.append(support)
        local_records.append(dict(positive=sorted(P),negative=sorted(Q),states=nloc,
                                  lower=lo,upper=hi,exact=exact))
    ls=prep+sum(lows);us=prep+sum(ups)
    # Empty global positives give rejecting roots in every factor. Otherwise
    # inert assigned local negatives imply all candidates keep, globally and
    # locally, and every output collapses to the corresponding support star.
    equal=not pos or all_local_negatives_inert
    if first_letters:
        # A distinct terminal fringe always occurs after the first candidate.
        # Every observed positive label survives in at least one edge.
        lg+=2+len(positive_support)
        if all_local_negatives_inert:
            # Here all global negatives contain an unobserved positive label;
            # the first candidate is kept and remaps the singleton red root.
            lg+=1
    quality_reason='all assigned local negatives contain an unseen local symbol' if pos else 'empty positive sample'
    H=sum(h.values())
    if H+us<lg:decision='NET_SPLIT_EQUAL' if equal else 'NET_SPLIT_COST'
    elif H+ug<ls:decision='NET_GLOBAL_EQUAL' if equal else 'NET_GLOBAL_COST'
    elif us<lg:decision='PIPELINE_SPLIT'
    elif ug<ls:decision='PIPELINE_GLOBAL'
    else:decision='UNKNOWN'
    return result(decision,'static_prefix_forest',True if equal else None,
                  quality_reason=quality_reason if equal else 'Equality is not certified; sample consistency is certified.',
                  global_interval=[lg,ug],split_interval=[ls,us],
                  first_symbol=first,forced_prefix_pairs=T,global_prefix_states=N,
                  preparation=prep,local_factors=local_records)

if __name__=='__main__':
    x=json.load(open(sys.argv[1],encoding='utf8'))
    print(json.dumps(select(x['positive'],x['negative'],x['blocks']),ensure_ascii=False,indent=2))

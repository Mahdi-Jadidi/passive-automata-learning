"""Static pre-training certificates extending output/defense.

Never imports a learner. Cost = declared W_ref/H loop events, not time.
NET_*_COST does NOT assert equal output languages. NET_*_EQUAL does.
Run: python -B static_selector.py sample.json
"""
from math import comb
from collections import Counter
import json,sys

def initial(m,p,n):return m+p+2*n-1
def fold_upper(n,e):return n*e+n*n+n
def upper(m,p,n,d):
    if n==1:return initial(m,p,n)+2
    e=n-1;b=n*(n-1)//2
    return initial(m,p,n)+n*(2*n+e)+b*(2+fold_upper(n,e)+d)

def unary_exact(m,p,r):
    """Nonempty unary positives, maximum exponent r>=1, no negatives."""
    passes=1 if r==1 else 2
    return m+p+r*r+(9+passes)*r+10

def distinct_word_exact(r):return (11*r*r+27*r+8)//2

def unique_edge_base(m,p,e):
    """No negatives; positive-prefix trie has one edge per observed label."""
    return m+p+(11*e*e+25*e+6)//2

def potential_union_lower(n):return n*(n+1)//2-1

def forced_union_lower(n,t=1):
    # Charge all iterations via q-|red|, including rejected trials.
    return n*t+potential_union_lower(n-t)

def mandatory_lower(m,p,n,s,delta,t=1):
    if n==1:return initial(m,p,n)+2
    return initial(m,p,n)+forced_union_lower(n,t)+4*n+3*(n-1)+3+s+delta

def inert_bounds(m,p,n,s,d,t=1):
    """Arbitrary positive trie; every negative contains an unseen label.
    d=sum(1+first outside position). Both bounds are pre-training.
    """
    if n==1:return initial(m,p,n)+2,initial(m,p,n)+2
    e=n-1;i=initial(m,p,n)
    lower=i+forced_union_lower(n,t)+4*n+3*e+4+s+d
    upper=unique_edge_base(m,p,e)-e+s+e*d
    return lower,upper

def unique_edge_interval(m,p,e,z,d,inert):
    b=unique_edge_base(m,p,e)
    if e==0:return b,b
    if inert:return b+2*(e-1)*z+d,b+e*d
    return b,None

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
    max_positive_length=0;global_inert=True;global_negative_test_cost=0
    positive_block_volume=Counter();positive_has_repeat=False
    for positive,words in ((True,pos),(False,neg)):
        for w in words:
            h['input_word']+=1;counts={};first_outside=None
            for j,a in enumerate(w,1):
                h['input_character']+=1
                if a not in owner:raise ValueError('Unknown character')
                used.add(a);counts[a]=counts.get(a,0)+1
                if positive:
                    positive_support.add(a);positive_block_volume[owner[a]]+=1
                    if counts[a]>1:positive_has_repeat=True
                elif first_outside is None and a not in positive_support:first_outside=j
            if positive:
                hist[w]=counts;M+=len(w);max_positive_length=max(max_positive_length,len(w))
            else:
                Mn+=len(w)
                if first_outside is None:global_inert=False
                else:global_negative_test_cost+=1+first_outside
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
    # New exact gap rules. Validation above is paid even for these cases.
    if k==1 or not positive_support:
        if k==1:
            gap=prep;rule='one_block_identity'
            extra=dict(split_minus_global=gap)
        else:
            g=3+int('' in pos)
            gap=prep+(k-1)*g;rule='root_only_positives'
            extra=dict(global_exact=g,split_exact=g+gap,split_minus_global=gap)
        decision=('TIE' if gap==0 else
                  'NET_GLOBAL_EQUAL' if sum(h.values())<gap else 'PIPELINE_GLOBAL')
        return result(decision,rule,True,**extra)
    if p and k>1 and active:
        gap=prep+4*(k-1)
        return result('NET_GLOBAL_EQUAL' if sum(h.values())<gap else 'PIPELINE_GLOBAL',
                      'single_active_block',True,split_minus_global=gap)

    # A single repetition-free positive word, with no negatives: every fold
    # has one union and one stable edge pass. All factor words have this form.
    if p==1 and not neg and not positive_has_repeat:
        g=distinct_word_exact(max_positive_length);s=prep
        for i in range(k):
            h['distinct_word_factor']+=1;s+=distinct_word_exact(positive_block_volume[i])
        gap=s-g;H=sum(h.values())
        d=('TIE' if gap==0 else
           'NET_GLOBAL_EQUAL' if gap>H else 'PIPELINE_GLOBAL' if gap>0 else
           'NET_SPLIT_EQUAL' if -gap>H else 'PIPELINE_SPLIT')
        return result(d,'single_distinct_word',True,global_exact=g,split_exact=s,
                      split_minus_global=gap)

    # An infinite family with arbitrary unary positives and globally inert
    # negatives. Informative local negatives are allowed. The outside symbol's
    # block guarantees feasibility; no local allocation need be constructed.
    if len(positive_support)==1 and global_inert:
        v=unary_exact(M,p,max_positive_length)
        g=v+global_negative_test_cost
        ls=prep+v+4*(k-1);gap=ls-g
        assert gap>0
        return result('NET_GLOBAL_COST' if sum(h.values())<gap else 'PIPELINE_GLOBAL',
                      'unary_global_inert',None,global_exact=g,split_lower=ls,
                      split_minus_global_lower=gap,negative_test_cost=global_negative_test_cost,
                      quality_reason='Language equality is a separate question; it is not certified here.')

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
        lg+=forced_union_lower(N,T)+4*N+3*(N-1)+1+delta
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
        inert=True;negative_test_cost=0
        for w in Q:
            h['local_negative_word']+=1;outside=False;d+=len(w)+1
            first_outside=None
            for j,a in enumerate(w,1):
                h['local_negative_character']+=1
                if a not in support:
                    outside=True
                    if first_outside is None:first_outside=j
            if not outside:all_local_negatives_inert=False;inert=False
            else:negative_test_cost+=1+first_outside
        nloc=len(pref);lo=initial(m,len(P),nloc);hi=upper(m,len(P),nloc,d)
        delta_local=0 if not Q else 1 if '' in Q else 2
        lo=max(lo,mandatory_lower(m,len(P),nloc,len(support),delta_local))
        exact=False
        if nloc==1:lo=hi=initial(m,len(P),nloc)+2;exact=True
        elif len(support)==1:
            # The first candidate fold is identical with or without negatives.
            # Kept: red remap + terminal fringe cost 4. Rejected: the next
            # unchanged-trie fringe alone costs at least 5. Hence V is a lower
            # bound even for informative, merge-rejecting local negatives.
            lo=max(lo,unary_exact(m,len(P),nloc-1))
            if inert:
                lo=hi=unary_exact(m,len(P),nloc-1)+negative_test_cost;exact=True
        if nloc-1==len(support):
            lb,ub=unique_edge_interval(m,len(P),nloc-1,len(Q),negative_test_cost,inert)
            lo=max(lo,lb)
            if ub is not None:hi=min(hi,ub)
            exact=lo==hi
        if inert:
            lb,ub=inert_bounds(m,len(P),nloc,len(support),negative_test_cost)
            lo=max(lo,lb);hi=min(hi,ub);exact=lo==hi
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
    # Unary data with informative global negatives still admits the V lower
    # bound proved from the identical first fold and its subsequent fringe.
    if len(positive_support)==1:
        lg=max(lg,unary_exact(M,p,N-1))
    unique_edges=N-1==len(positive_support)
    if unique_edges:
        lb,ub=unique_edge_interval(M,p,N-1,z,global_negative_test_cost,global_inert)
        lg=max(lg,lb)
        if ub is not None:ug=min(ug,ub)
    if global_inert:
        lb,ub=inert_bounds(M,p,N,len(positive_support),global_negative_test_cost,T)
        lg=max(lg,lb);ug=min(ug,ub)
    quality_reason='all assigned local negatives contain an unseen local symbol' if pos else 'empty positive sample'
    H=sum(h.values())
    if lg==ug==ls==us:decision='TIE'
    elif H+us<lg:decision='NET_SPLIT_EQUAL' if equal else 'NET_SPLIT_COST'
    elif H+ug<ls:decision='NET_GLOBAL_EQUAL' if equal else 'NET_GLOBAL_COST'
    elif us<lg:decision='PIPELINE_SPLIT'
    elif ug<ls:decision='PIPELINE_GLOBAL'
    else:decision='UNKNOWN'
    return result(decision,'unique_edge_trie' if unique_edges else 'static_prefix_forest',True if equal else None,
                  quality_reason=quality_reason if equal else 'Equality is not certified; sample consistency is certified.',
                  global_interval=[lg,ug],split_interval=[ls,us],
                  first_symbol=first,forced_prefix_pairs=T,global_prefix_states=N,
                  preparation=prep,local_factors=local_records)

if __name__=='__main__':
    x=json.load(open(sys.argv[1],encoding='utf8'))
    print(json.dumps(select(x['positive'],x['negative'],x['blocks']),ensure_ascii=False,indent=2))

"""Compare Q^3 certificates with independent full-language projection oracle."""
import json,random
from collections import deque
from pathlib import Path
from dfa_oracle_v1 import all_small_dfas,cut_counterexample,accepts
from oracle_v1 import partitions,compatible,rgs,oracle,project

def triple(delta,finals,a,b):
    c=set(a)-set(b);start=(0,0,0);todo=deque([(start,('','',''))]);seen={start}
    while todo:
        (qn,qb,qc),words=todo.popleft()
        if qn not in finals and qb in finals and qc in finals:return words
        for j,x in enumerate(a):
            moves=[]
            if x in b:
                moves=[((delta[qn][j],delta[qb][j],qc),(x,x,'')),((qn,qb,delta[qc][j]),('','',x))]
            else:
                moves=[((delta[qn][j],qb,delta[qc][j]),(x,'',x)),((qn,delta[qb][j],qc),('',x,''))]
            for nxt,added in moves:
                if nxt not in seen:
                    seen.add(nxt);todo.append((nxt,tuple(w+v for w,v in zip(words,added))))
    return None

def run():
    counts=dict(total_small_dfa_choices=324,empty_language_filtered=94,nonempty_small_dfas=0,seeded_larger_dfas=0,cuts=0,invalid_cuts=0,partition_checks=0,epsilon_lift_certificates=0)
    cases=list(all_small_dfas())
    for seed in range(10):
        rng=random.Random(260600+seed);q=3+seed%2;a=list('abc'[:2+seed%2]);d=[tuple(rng.randrange(q) for _ in a) for _ in range(q)];f=frozenset({0}|{i for i in range(q) if rng.choice([0,1])});cases.append((a,d,f))
    for ci,(a,d,f) in enumerate(cases):
        counts['nonempty_small_dfas' if ci<230 else 'seeded_larger_dfas']+=1
        ps=list(partitions(a));cuts=[p for p in ps if len(p)==2];valid_cuts=[];positive=set();negative=set()
        for b,c in cuts:
            counts['cuts']+=1;counter=cut_counterexample(d,f,a,[b,c]);t=triple(d,f,a,set(b))
            assert (counter is None)==(t is None)
            if t is None:valid_cuts.append([b,c]);continue
            counts['invalid_cuts']+=1;n,pb,pc=t
            assert all(len(w)<len(d)**3 for w in t)
            assert not accepts(d,f,n,a) and accepts(d,f,pb,a) and accepts(d,f,pc,a)
            assert project(n,b)==project(pb,b) and project(n,c)==project(pc,c)
            counts['epsilon_lift_certificates']+=int(len(pb)+len(pc)>len(n))
            positive.update([pb,pc]);negative.add(n)
        sample=dict(alphabet=a,positive=sorted(positive),negative=sorted(negative))
        assert not positive&negative and len(positive|negative)<=3*len(cuts)
        # Meet of ALL valid cuts, obtained from independent subset-product oracle.
        groups={}
        for x in a:
            signature=tuple(next(j for j,b in enumerate(cut) if x in b) for cut in valid_cuts)
            groups.setdefault(signature,[]).append(x)
        finest=list(groups.values())
        assert cut_counterexample(d,f,a,finest) is None
        valid=[]
        for p in ps:
            counts['partition_checks']+=1
            language_valid=cut_counterexample(d,f,a,p) is None
            assert language_valid==compatible(sample,p)
            coarsens=all(any(set(b)<=set(c) for c in p) for b in finest)
            assert language_valid==coarsens
            if language_valid:valid.append(p)
        optimum=oracle(sample)
        assert optimum['maximum_blocks']==len(finest) and optimum['optimal_count']==1
        assert rgs(optimum['canonical'],a)==rgs(finest,a)
    return dict(status='passed',**counts)

if __name__=='__main__':
    out=run();path=Path(__file__).with_name('THEOREM_CHECK_V1.json')
    with path.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
    print(json.dumps(out))

"""Independent direct string projection oracle. Never imports provider code."""
from itertools import product
import random

def partitions(alphabet):
    a=sorted(alphabet)
    if not a:
        yield []
        return
    def visit(r):
        if len(r)==len(a):
            yield [[a[i] for i,x in enumerate(r) if x==j] for j in range(max(r)+1)]
            return
        for j in range(max(r)+2):
            yield from visit(r+[j])
    yield from visit([0])

def rgs(blocks, alphabet):
    owner={x:j for j,b in enumerate(blocks) for x in b}
    rename={};out=[]
    for x in sorted(alphabet):
        j=owner[x]
        if j not in rename:rename[j]=len(rename)
        out.append(rename[j])
    return tuple(out)

def project(word, block):
    return ''.join(x for x in word if x in block)

def compatible(data, blocks):
    return all(any(project(n,b) not in {project(p,b) for p in data['positive']} for b in blocks) for n in data['negative'])

def replay(data, blocks):
    flat=[x for b in blocks for x in b]
    assert all(blocks) and sorted(flat)==sorted(data['alphabet']) and len(set(flat))==len(flat)
    assert compatible(data,blocks)
    return True

def oracle(data):
    family=[p for p in partitions(data['alphabet']) if compatible(data,p)]
    best=max(map(len,family),default=0)
    opt=sorted((p for p in family if len(p)==best),key=lambda p:rgs(p,data['alphabet']))
    return dict(status='incompatible' if not family else 'certified_unique' if len(family)==1 else 'ambiguous',
                family_count=len(family),maximum_blocks=best,optimal_count=len(opt),
                canonical=opt[0] if opt else None,optimal_partitions=opt)

def fixtures():
    words=['','a','b','aa','ab','ba','bb']
    for i,labels in enumerate(product(range(3),repeat=7)):
        yield 'ternary_'+str(i),dict(alphabet=list('ab'),positive=[w for w,y in zip(words,labels) if y==1],negative=[w for w,y in zip(words,labels) if y==2])
    for m in range(3,9):
        a=list('abcdefgh'[:m])
        for j in range(10):
            rng=random.Random(260000+m*100+j)
            words=sorted({''.join(rng.choices(a,k=rng.randrange(0,9))) for _ in range(30)})
            labels=[rng.randrange(3) for _ in words]
            yield f'seed_m{m}_{j}',dict(alphabet=a,positive=[w for w,y in zip(words,labels) if y==1],negative=[w for w,y in zip(words,labels) if y==2])

def timing_cells():
    for m in (6,12):
        a=list('abcdefghijkl'[:m])
        yield f'm{m}_no_negative',dict(alphabet=a,positive=[''.join(a)],negative=[])
        yield f'm{m}_swapcert',dict(alphabet=a,positive=[''.join(a)],negative=[''.join(a[:i]+[a[i+1],a[i]]+a[i+2:]) for i in range(m-1)])
        # Same obstruction repeated on disjoint triples; each triple forces a merge
        # without any individual adjacent-swap certificate.
        pos=[''];neg=[]
        for i in range(0,m,3):
            x,y,z=a[i:i+3]
            pos += [x+y,y+z,x+z]
            neg += [x+y+z]
        yield f'm{m}_repeated3symbol',dict(alphabet=a,positive=pos,negative=neg)

def selftest():
    bells=[1,1,2,5,15,52,203,877,4140]
    for m in range(1,9):
        ps=list(partitions(list('abcdefgh'[:m])))
        assert len(ps)==bells[m]
        assert len({rgs(p,list('abcdefgh'[:m])) for p in ps})==len(ps)
    assert oracle(dict(alphabet=list('ab'),positive=['ab'],negative=['ba']))['maximum_blocks']==1
    assert oracle(dict(alphabet=list('ab'),positive=[''],negative=['']))['status']=='incompatible'
    assert len(list(fixtures()))==2247
    return dict(status='passed',bell_counts=bells,fixtures=2247)

if __name__=='__main__':
    import json
    print(json.dumps(selftest()))

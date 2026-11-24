"""Independent small-instance validation for report 02. No solver imports except optional audit baseline.
Run: python no_implication_validation.py
This is a reference experiment, not a production external adapter.
"""
from itertools import combinations, product
from random import Random
import json


def partitions(items):
    if not items:
        yield (); return
    a, *rest = items
    for p in partitions(rest):
        yield (frozenset([a]), *p)
        for i, b in enumerate(p):
            yield (*p[:i], b | {a}, *p[i+1:])


def proj(w, b): return tuple(a for a in w if a in b)
def atoms(b): return [frozenset(c) for k in (1, 2) for c in combinations(sorted(b), k)]
def ok(words, p, P):
    return all(any(all(proj(y,b)!=proj(x,b) for x in words[:p]) for b in P) for y in words[p:])


def history(words,p,queries,named,failures=None):
    eq, ne, anon, zeros = [], [], [], []
    for qi,P in enumerate(queries):
        maps = [{i: [j for j in range(p) if proj(words[i],b)==proj(words[j],b)] for i in range(p,len(words))} for b in P]
        failure=(failures[qi] if failures is not None else next(i for i in range(p,len(words)) if all(m[i] for m in maps)))
        assert all(m[failure] for m in maps)
        for b,m in zip(P,maps):
            for i,js in m.items():
                if js:
                    zeros.append((i,b))
                    if named or i==failure: eq.append((i,js[0],b))
                    else: anon.append((i,b))
                else:
                    ne.extend((i,j,b) for j in range(p))
            free=[i for i in m if not m[i]]
            for i,j in combinations(free,2):
                (eq if proj(words[i],b)==proj(words[j],b) else ne).append((i,j,b))
    return eq,ne,anon,zeros


def least(n,N,eq):
    # class labels; named equalities propagate to every contained atom.
    rel={a:list(range(N)) for a in atoms(range(n))}
    for i,j,b in eq:
        for a in atoms(b):
            v=rel[a]; x,y=v[i],v[j]
            if x!=y: rel[a]=[x if z==y else z for z in v]
    return rel


def equal(rel,i,j,b): return all(rel[a][i]==rel[a][j] for a in atoms(b))
def abstract_ok(rel,p,N,P):
    return all(any(all(not equal(rel,i,j,b) for j in range(p)) for b in P) for i in range(p,N))


def realize(n,N,rel):
    words=[[] for _ in range(N)]
    bits=max(1,(N-1).bit_length())
    for a,b in combinations(range(n),2):
        codes={c:k for k,c in enumerate(sorted(set(rel[frozenset((a,b))])))}
        for i,w in enumerate(words):
            for k in range(bits):
                w.extend((a,b) if not ((codes[rel[frozenset((a,b))][i]]>>k)&1) else (b,a))
    for a in range(n):
        codes={c:k for k,c in enumerate(sorted(set(rel[frozenset((a,))])))}
        for i,w in enumerate(words): w.extend([a]*codes[rel[frozenset((a,))][i]])
    return words


def all_models(n,N,p,eq,ne,anon):
    # Disjoint opposite labels, as in main paper. Same-label duplicates allowed.
    ne=ne+[(i,j,frozenset(range(n))) for i in range(p) for j in range(p,N)]
    anon=list(dict.fromkeys(anon))
    for choice in product(range(p),repeat=len(anon)):
        r=least(n,N,eq+[(i,j,b) for (i,b),j in zip(anon,choice)])
        if not any(equal(r,i,j,b) for i,j,b in ne): yield r


def refines(p,q): return all(any(b<=c for c in q) for b in p)


def test():
    stats={"realization_systems":0,"realization_projection_checks":0,"actual_histories":0,"named_candidate_checks":0,"anonymous_candidate_checks":0,"anonymous_strict_over_named_stitch":0,"named_strict_over_regions":0,"synthesized_models_checked":0}
    labels=[]
    for P in partitions(list(range(3))):
        labels.append(tuple(next(min(b) for b in P if i in b) for i in range(3)))
    AA=atoms(range(3)); blocks=[frozenset(c) for k in range(4) for c in combinations(range(3),k)]
    for vv in product(labels,repeat=len(AA)):
        r=dict(zip(AA,vv))
        if any(r[a][i]==r[a][j] and any(r[frozenset([s])][i]!=r[frozenset([s])][j] for s in a) for a in AA if len(a)==2 for i,j in combinations(range(3),2)): continue
        w=realize(3,3,r); stats['realization_systems']+=1
        for i,j in combinations(range(3),2):
            for b in blocks:
                assert equal(r,i,j,b)==(proj(w[i],b)==proj(w[j],b)); stats['realization_projection_checks']+=1
    rng=Random(20261124); corpora=[]
    ws=[w for k in range(3) for w in product(range(2),repeat=k)]
    for tags in product(range(3),repeat=len(ws)):
        x=[w for w,t in zip(ws,tags) if t==1]; y=[w for w,t in zip(ws,tags) if t==2]
        if x and y: corpora.append((2,x+y,len(x)))
    for _ in range(500):
        n=rng.choice([3,4]); p=rng.choice([1,2,3]); q=rng.choice([1,2,3]); w=[]
        while len(w)<p+q:
            a=tuple(rng.choices(range(n),k=rng.randrange(6)))
            if a not in w: w.append(a)
        corpora.append((n,w,p))
    example=None; namedexample=None
    for n,w,p in corpora:
        PP=list(partitions(list(range(n)))); bad=[P for P in PP if not ok(w,p,P)]
        if not bad: continue
        queries=rng.sample(bad,min(len(bad),rng.choice([1,2,3])))
        stats['actual_histories']+=1
        for named in (True,False):
            eq,ne,anon,z=history(w,p,queries,named)
            if not named and p**len(set(anon))>243: continue
            models=list(all_models(n,len(w),p,eq,ne,anon)); assert models
            base=least(n,len(w),eq)
            for r in models:
                synth=realize(n,len(w),r); stats['synthesized_models_checked']+=1
                assert all(proj(synth[i],b)==proj(synth[j],b) for i,j,b in eq)
                assert all(proj(synth[i],b)!=proj(synth[j],b) for i,j,b in ne)
                assert all(any(proj(synth[i],b)==proj(synth[j],b) for j in range(p)) for i,b in anon)
                assert all(not ok(synth,p,Q) for Q in queries)
            synths=[realize(n,len(w),r) for r in models]
            for P in PP:
                forced=not any(abstract_ok(r,p,len(w),P) for r in models)
                assert not forced or not ok(w,p,P)
                assert forced==all(not ok(s,p,P) for s in synths)
                region=any(all(any(i==ii and b<=u for ii,u in z) for b in P) for i in range(p,len(w)))
                stitch=region or not abstract_ok(base,p,len(w),P)
                stats['named_candidate_checks' if named else 'anonymous_candidate_checks']+=1
                if named and forced and not region:
                    stats['named_strict_over_regions']+=1
                    if namedexample is None: namedexample=(n,w,p,queries,P)
                if not named and forced and not stitch:
                    stats['anonymous_strict_over_named_stitch']+=1
                    if example is None: example=(n,w,p,queries,P)
    def P(*blocks): return tuple(frozenset(ord(a)-97 for a in b) for b in blocks)
    def W(*words): return [tuple(ord(a)-97 for a in w) for w in words]
    w=W('abcd','abdc'); queries=[P('ab','c','d'),P('ac','b','d'),P('bc','a','d')]; target=P('abc','d')
    eq,ne,anon,z=history(w,1,queries,True)
    r=least(4,2,eq); assert not abstract_ok(r,1,2,target)
    assert not any(all(any(i==ii and b<=u for ii,u in z) for b in target) for i in [1])
    stats['targeted_named_stitch']=1
    w=W('abcd','bace','abcde','abced'); queries=[P('acd','b','e'),P('bcd','a','e'),P('ace','b','d'),P('bce','a','d'),P('ab','c','d','e')]; target=P('abc','d','e')
    eq,ne,anon,z=history(w,2,queries,False,[2,2,2,2,3]); r=least(5,4,eq)
    assert abstract_ok(r,2,4,target)
    assert not any(all(any(i==ii and b<=u for ii,u in z) for b in target) for i in [2,3])
    # Branch only on the anonymous (y,ab) fact; all other anonymous facts omitted (safe relaxation).
    models=list(all_models(5,4,2,eq,ne,[(2,frozenset([0,1]))])); assert models
    assert all(not abstract_ok(r,2,4,target) for r in models)
    stats['targeted_anonymous_strict']=1; stats['targeted_anonymous_surviving_branches']=len(models)
    print(json.dumps(stats,indent=2)); print('named example',namedexample); print('anonymous example',example)

if __name__=='__main__': test()

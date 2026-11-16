"""Deterministic trusted instance-to-CNF specification. No SAT dependency."""
from itertools import combinations
import time
class Invalid(ValueError): pass
class Exhausted(Exception): pass
def budget(limits):
    limits={} if limits is None else limits
    if type(limits) is not dict or set(limits)-{'timeout_seconds'}: raise Invalid('limits')
    seconds=limits.get('timeout_seconds')
    if seconds is not None and (type(seconds) not in (int,float) or not 0<=seconds<float('inf')): raise Invalid('timeout')
    end=None if seconds is None else time.monotonic()+seconds
    def tick():
        if end is not None and time.monotonic()>=end: raise Exhausted()
    tick.remaining=lambda:None if end is None else max(0,end-time.monotonic())
    return tick
def normalize(data):
    if type(data) is not dict or set(data)!={'alphabet','positive','negative'}: raise Invalid('schema')
    a=data['alphabet']
    if type(a) is not list or any(type(x) is not str or not x for x in a) or len(set(a))!=len(a): raise Invalid('alphabet')
    out=[]
    for key in ('positive','negative'):
        if type(data[key]) is not list: raise Invalid('words')
        seen=set(); words=[]
        for w in data[key]:
            if type(w) is not list or any(type(x) is not str or x not in a for x in w): raise Invalid('word')
            t=tuple(w)
            if t not in seen: seen.add(t);words.append(t)
        out.append(words)
    return tuple(a),out[0],out[1]
def reject(a,p,n,indices):
    s={a[i] for i in indices}; h={tuple(x for x in w if x in s) for w in p}
    return {j for j,w in enumerate(n) if tuple(x for x in w if x in s) not in h}
def atoms(a,p,n,tick):
    parent=list(range(len(a)))
    def find(i):
        while parent[i]!=i: i=parent[i]
        return i
    forced=[[] for _ in n]
    for i in range(len(a)):
        tick(); r=reject(a,p,n,[j for j in range(len(a)) if j!=i])
        for j in range(len(n)):
            if j not in r: forced[j].append(i)
    for group in forced:
        for i in group[1:]: parent[find(i)]=find(group[0])
    groups={}
    for i in range(len(a)): groups.setdefault(find(i),[]).append(i)
    return sorted(groups.values(),key=lambda x:x[0])
def build(a,p,n,tick):
    groups=atoms(a,p,n,tick); q=len(groups); edges=[[] for _ in n]
    for size in range(1,q+1):
        for subset in combinations(range(q),size):
            tick(); mask=sum(1<<i for i in subset)
            needed=[j for j in range(len(n)) if not any(e&mask==e for e in edges[j])]
            if not needed: continue
            r=reject(a,p,n,[i for g in subset for i in groups[g]])
            for j in needed:
                if j in r: edges[j].append(mask)
    clauses=[]; count=0
    def new():
        nonlocal count
        count+=1;return count
    def gate(op,inputs):
        if not inputs:return op=='and'
        if len(inputs)==1:return inputs[0]
        g=new()
        if op=='and':
            clauses.extend([[-g,x] for x in inputs]);clauses.append([g]+[-x for x in inputs])
        else:
            clauses.extend([[g,-x] for x in inputs]);clauses.append([-g]+inputs)
        return g
    # Fixed constants avoid bool/int literal aliasing.
    true=new();clauses.append([true]); false=-true
    pairs={(i,j):new() for i in range(q) for j in range(i+1,q)}
    for i,j,k in combinations(range(q),3):
        x,y,z=pairs[i,j],pairs[i,k],pairs[j,k]
        clauses.extend([[-x,-y,z],[-x,-z,y],[-y,-z,x]])
    reps=[true]+[gate('and',[-pairs[j,i] for j in range(i)]) for i in range(1,q)] if q else []
    h={}
    for mask in sorted({e for family in edges for e in family}):
        items=[i for i in range(q) if mask>>i&1]
        h[mask]=true if len(items)==1 else gate('and',[pairs[items[0],j] for j in items[1:]])
    for family in edges: clauses.append([h[e] for e in family])
    prev=[true]+[false]*q
    for r in reps:
        prev=[true]+[gate('or',[prev[j],gate('and',[r,prev[j-1]])]) for j in range(1,q+1)]
    return {'groups':groups,'q':q,'pairs':pairs,'clauses':clauses,'thresholds':prev,'variables':count,'edges':edges}
def threshold(enc,t):
    return enc['clauses']+([[]] if t>enc['q'] else [[enc['thresholds'][t]]])
def feasible(a,p,n,blocks):
    if type(blocks) is not list or any(type(b) is not list or not b for b in blocks):return False
    flat=[x for b in blocks for x in b]
    if any(type(x) is not str for x in flat) or len(flat)!=len(a) or set(flat)!=set(a):return False
    return set().union(*(reject(a,p,n,[a.index(x) for x in b]) for b in blocks))==set(range(len(n)))

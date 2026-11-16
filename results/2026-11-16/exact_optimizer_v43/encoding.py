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
class Prepared:
    """Per-call exact rejection oracle, shared by all negative obligations."""
    def __init__(self,Sigma,S_plus,S_minus,tick):
        self.Sigma=Sigma;self.S_plus=S_plus;self.S_minus=S_minus;self.tick=tick
        self.cache={};self.stats={'projection_evaluations':0,'cache_hits':0,'regions':0,'false_regions':0}
        self.full=(1<<len(Sigma))-1
        self.groups=None;self.atom_masks=None

    def prepare_atoms(self):
        if self.groups is not None:return self.groups
        Sigma=self.Sigma;S_minus=self.S_minus
        parent=list(range(len(Sigma)))
        def find(i):
            while parent[i]!=i:
                parent[i]=parent[parent[i]];i=parent[i]
            return i
        forced=[[] for _ in S_minus]
        for i in range(len(Sigma)):
            mask=self.reject_mask(self.full^(1<<i))
            for j in range(len(S_minus)):
                if not (mask>>j&1):forced[j].append(i)
        for group in forced:
            for i in group[1:]:parent[find(i)]=find(group[0])
        groups={}
        for i in range(len(Sigma)):groups.setdefault(find(i),[]).append(i)
        self.groups=sorted(groups.values(),key=lambda group:group[0])
        self.atom_masks=[sum(1<<i for i in group) for group in self.groups]
        return self.groups

    def reject_mask(self,symbol_mask):
        self.tick()
        if symbol_mask in self.cache:
            self.stats['cache_hits']+=1;return self.cache[symbol_mask]
        selected={self.Sigma[i] for i in range(len(self.Sigma)) if symbol_mask>>i&1}
        positive_images={tuple(x for x in w if x in selected) for w in self.S_plus}
        result=sum(1<<j for j,w in enumerate(self.S_minus) if tuple(x for x in w if x in selected) not in positive_images)
        self.cache[symbol_mask]=result;self.stats['projection_evaluations']+=1
        return result

    def atom_rejects(self,atom_mask,negative_index):
        symbol_mask=0
        for i,original in enumerate(self.atom_masks):
            if atom_mask>>i&1:symbol_mask|=original
        return bool(self.reject_mask(symbol_mask)>>negative_index&1)

    def minimal_witnesses(self,negative_index):
        # Maximal unexplored regions form an antichain. False regions eliminate
        # all their subsets. A known witness splits a region into its exclusions.
        full=(1<<len(self.groups))-1;pending={full};processed=set();found=set()
        if not full:return []
        def enqueue(region):
            if not region or region in processed:return
            if any(region&other==region for other in pending):return
            pending.difference_update([other for other in pending if other&region==other])
            pending.add(region)
        while pending:
            self.tick();region=min(pending,key=lambda x:(-x.bit_count(),x));pending.remove(region)
            if region in processed:continue
            processed.add(region);self.stats['regions']+=1
            witness=next((edge for edge in sorted(found) if edge&region==edge),None)
            if witness is None:
                if not self.atom_rejects(region,negative_index):
                    self.stats['false_regions']+=1;continue
                witness=region
                for i in range(len(self.groups)):
                    smaller=witness&~(1<<i)
                    if smaller and smaller!=witness and self.atom_rejects(smaller,negative_index):witness=smaller
                found.add(witness)
            for i in range(len(self.groups)):
                if witness>>i&1:enqueue(region&~(1<<i))
        return sorted(found,key=lambda x:(x.bit_count(),tuple(i for i in range(len(self.groups)) if x>>i&1)))

def atoms(a,p,n,tick):return Prepared(a,p,n,tick).prepare_atoms()

def build(a,p,n,tick,prepared=None):
    prepared=Prepared(a,p,n,tick) if prepared is None else prepared
    groups=prepared.prepare_atoms();q=len(groups)
    edges=[prepared.minimal_witnesses(j) for j in range(len(n))]
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
    upper=min([q]+[q-min(e.bit_count() for e in family)+1 for family in edges if family])
    return {'groups':groups,'q':q,'pairs':pairs,'clauses':clauses,'thresholds':prev,'variables':count,'edges':edges,'upper':upper}
def threshold(enc,t):
    return enc['clauses']+([[]] if t>enc['q'] else [[enc['thresholds'][t]]])
def feasible(a,p,n,blocks):
    if type(blocks) is not list or any(type(b) is not list or not b for b in blocks):return False
    flat=[x for b in blocks for x in b]
    if any(type(x) is not str for x in flat) or len(flat)!=len(a) or set(flat)!=set(a):return False
    return set().union(*(reject(a,p,n,[a.index(x) for x in b]) for b in blocks))==set(range(len(n)))

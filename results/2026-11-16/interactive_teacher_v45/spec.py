"""Wire contract and bounded operations; historical V43 files remain untouched."""
import math
import time

class Invalid(ValueError): pass
class Exhausted(Exception): pass

def budget(limits):
    limits={} if limits is None else limits
    if type(limits) is not dict or set(limits)-{'timeout_seconds'}:raise Invalid('limits')
    seconds=limits.get('timeout_seconds')
    if seconds is not None and (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<0):raise Invalid('timeout')
    end=None if seconds is None else time.monotonic()+seconds
    def tick():
        if end is not None and time.monotonic()>=end:raise Exhausted()
    tick.remaining=lambda:None if end is None else max(0,end-time.monotonic())
    return tick

def normalize(D):
    if type(D) is not dict or set(D)!={'alphabet','positive','negative'}:raise Invalid('schema')
    a=D['alphabet']
    if type(a) is not list or any(type(x) is not str or not x for x in a) or len(set(a))!=len(a):raise Invalid('alphabet')
    labels=[]
    for key in ('positive','negative'):
        if type(D[key]) is not list:raise Invalid('words')
        seen=set();out=[]
        for w in D[key]:
            if type(w) is not list or any(type(x) is not str or x not in a for x in w):raise Invalid('word')
            t=tuple(w)
            if t not in seen:seen.add(t);out.append(t)
        labels.append(out)
    return tuple(a),*labels

def response(status,blocks=None,k=None,certificate=None):
    return dict(status=status,blocks=blocks,max_devices=k,certificate=certificate)

def partition_masks(a,blocks):
    if type(blocks) is not list:raise Invalid('partition')
    seen=set();masks=[]
    for B in blocks:
        if type(B) is not list or not B:raise Invalid('block')
        mask=0
        for x in B:
            if type(x) is not str or x not in a or x in seen:raise Invalid('partition')
            seen.add(x);mask|=1<<a.index(x)
        masks.append(mask)
    if seen!=set(a):raise Invalid('cover')
    return masks

def direct_reject(a,p,n,mask):
    selected={a[j] for j in range(len(a)) if mask>>j&1}
    pos={tuple(x for x in w if x in selected) for w in p}
    return sum(1<<i for i,w in enumerate(n) if tuple(x for x in w if x in selected) not in pos)

def mandatory_groups(a,n,rejection,tick):
    parent=list(range(len(a)));full=(1<<len(a))-1
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    forced=[[] for _ in n]
    for j in range(len(a)):
        tick();bits=rejection(full^(1<<j))
        for i in range(len(n)):
            if not bits>>i&1:forced[i].append(j)
    for group in forced:
        for j in group[1:]:parent[find(j)]=find(group[0])
    out={}
    for j in range(len(a)):out.setdefault(find(j),[]).append(j)
    return sorted(out.values(),key=lambda B:B[0])

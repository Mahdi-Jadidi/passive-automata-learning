"""Benchmark the reviewed P1 singleton forest; not a general solver or P2 replay."""
import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

PIN = '822a45084dcad4f21f09c445802d12c1312e331a'
BLOBS = {'core.py': '997304c3adce9d3148d454b079639575f419ba0e',
         'sparse_analysis.py': 'f773cc1c6b1a852193ba2afb75aa2fce4941a5c2'}


def check_source(root):
    for name, expected in BLOBS.items():
        data = (root / 'selector_v2' / name).read_bytes()
        if hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() != expected:
            raise ValueError('wrong source blob: ' + name)


def load(path):
    d = json.loads(path.read_bytes())
    if type(d) is not dict or set(d) != {'alphabet', 'positive', 'negative'}:
        raise ValueError('input-only schema required')
    a = d['alphabet']
    if type(a) is not list or any(type(s) is not str or not s for s in a) or len(set(a)) != len(a):
        raise ValueError('invalid alphabet')
    allowed = set(a)
    for label in ('positive', 'negative'):
        if type(d[label]) is not list or any(type(w) is not list or any(type(s) is not str or s not in allowed for s in w) for w in d[label]):
            raise ValueError('invalid ordered traces')
    return d


def produce(d, source, seconds):
    from dataclasses import astuple
    check_source(source)
    sys.path.insert(0, str(source))
    from selector_v2.core import Sample, PartitionRef, Budget
    from selector_v2.sparse_analysis import discover_deletions, singleton_forest, raw_check
    t = time.perf_counter()
    s = Sample.from_input(d)
    p = PartitionRef.singletons(len(s.alphabet))
    encode_s = time.perf_counter() - t
    t = time.perf_counter()
    r = discover_deletions(s, p, Budget(seconds=seconds))
    discovery_s = time.perf_counter() - t
    metrics = {'encode_s': encode_s, 'discovery_s': discovery_s, 'facts': len(r.facts), 'exhausted': r.exhausted}
    if r.label_conflict is not None:
        return {'sample_digest': s.sample_digest, 'conflict': r.label_conflict}, metrics
    t = time.perf_counter()
    root, edges = singleton_forest(s, r)
    metrics['forest_s'] = time.perf_counter() - t
    t = time.perf_counter()
    check = raw_check(s, root)
    metrics['raw_check_s'] = time.perf_counter() - t
    metrics['edges'] = len(edges)
    return {'sample_digest': s.sample_digest, 'owner': root.owner,
            'edges': [astuple(e) for e in edges], 'compatible': check.compatible,
            'separating_groups': check.separating_groups}, metrics


def replay(d, proof):
    # Benchmark-only independent verifier for the P1 singleton-edge theorem.
    # No selector imports; reconstruct original IDs and connected components.
    a = d['alphabet']; ids = {s:i for i,s in enumerate(a)}
    xs, ys = [[tuple(ids[s] for s in w) for w in d[k]] for k in ('positive','negative')]
    expected = hashlib.sha256(json.dumps(['sample-v2', a, xs, ys], ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
    if proof['sample_digest'] != expected:
        raise ValueError('sample digest mismatch')
    def index(i, n):
        if type(i) is not int or not 0 <= i < n:
            raise ValueError('invalid ID')
        return i
    if 'conflict' in proof:
        i,j = proof['conflict']
        if ys[index(i,len(ys))] != xs[index(j,len(xs))]:
            raise ValueError('false conflict')
        return {'status':'VERIFIED_INFEASIBLE'}
    n = len(a); graph = [[] for _ in a]
    for i,u,j,v,k in proof['edges']:
        y = ys[index(i,len(ys))]
        index(u,n); index(v,n)
        if u == v:
            raise ValueError('self edge')
        for g,w in ((u,xs[index(j,len(xs))]),(v,xs[index(k,len(xs))])):
            if tuple(s for s in y if s!=g) != tuple(s for s in w if s!=g):
                raise ValueError('false deletion witness')
        graph[u].append(v); graph[v].append(u)
    owner = [-1]*n
    for i in range(n):
        if owner[i]>=0: continue
        owner[i]=i; todo=[i]
        while todo:
            for v in graph[todo.pop()]:
                if owner[v]<0: owner[v]=i; todo.append(v)
    cost=sum(i!=g for i,g in enumerate(owner))
    if proof['owner']!=owner or len(proof['edges'])!=cost:
        raise ValueError('invalid forest/owner')
    if not proof['compatible']:
        return {'status':'VERIFIED_LOWER_BOUND_ONLY','lower':cost,'upper':None}
    witnesses=proof['separating_groups']
    if len(witnesses)!=len(ys): raise ValueError('missing witnesses')
    from collections import defaultdict, Counter
    possible=defaultdict(set); presence=Counter()
    for x in xs:
        local=defaultdict(list)
        for s in x: local[owner[s]].append(s)
        for g,w in local.items(): possible[g].add(tuple(w)); presence[g]+=1
    for y,g in zip(ys,witnesses):
        index(g,n)
        if owner[g]!=g: raise ValueError('non-root witness')
        w=tuple(s for s in y if owner[s]==g)
        if (w and w in possible[g]) or (not w and presence[g]<len(xs)):
            raise ValueError('nonseparating witness')
    return {'status':'VERIFIED_STRUCTURAL_OPTIMUM','lower':cost,'upper':cost}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--seconds',type=float,default=5); p.add_argument('--memory',type=int,default=512)
    p.add_argument('--stage',choices=('produce','replay'))
    a=p.parse_args()
    if not 0<a.seconds<float('inf') or a.memory<=0: p.error('invalid limits')
    if a.stage:
        resource.setrlimit(resource.RLIMIT_AS,(a.memory*2**20,)*2)
        t=time.perf_counter(); d=load(a.input)
        if a.stage=='produce':
            proof,m=produce(d,a.source,a.seconds)
            (a.output/'proof.json').write_text(json.dumps(proof,separators=(',',':')))
        else:
            m=replay(d,json.loads((a.output/'proof.json').read_bytes()))
        print(json.dumps({**m,'compute_s':time.perf_counter()-t,'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})); return
    check_source(a.source); load(a.input)
    a.output.mkdir(parents=True,exist_ok=False)
    snapshot=a.output/'input.json'; snapshot.write_bytes(a.input.read_bytes())
    result={'core_ref':PIN,'input_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'python':sys.version,'host':platform.platform(),'seconds_per_stage':a.seconds,'memory_as_mib':a.memory,'external_attempts':0,'external_response_bytes':0,'operational_status':'INCOMPLETE'}
    for stage in ('produce','replay'):
        if stage=='replay' and result['produce']['process_status']!='OK': break
        cmd=[sys.executable,'-B',str(Path(__file__).resolve()),str(a.source.resolve()),str(snapshot.resolve()),str(a.output.resolve()),'--seconds',str(a.seconds),'--memory',str(a.memory),'--stage',stage]
        t=time.perf_counter()
        try:
            q=subprocess.run(cmd,capture_output=True,timeout=a.seconds+1,env={**os.environ,'PYTHONHASHSEED':'0'})
            (a.output/(stage+'.stderr')).write_bytes(q.stderr); (a.output/(stage+'.stdout')).write_bytes(q.stdout)
            result[stage]={'process_status':'OK',**json.loads(q.stdout)} if q.returncode==0 else {'process_status':'ERROR','returncode':q.returncode}
        except subprocess.TimeoutExpired as exc:
            (a.output/(stage+'.stderr')).write_bytes(exc.stderr or b''); (a.output/(stage+'.stdout')).write_bytes(exc.stdout or b'')
            result[stage]={'process_status':'TIMEOUT'}
        result[stage]['wall_s']=time.perf_counter()-t
    result['artifact_bytes']=(a.output/'proof.json').stat().st_size if (a.output/'proof.json').exists() else None
    (a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result))


if __name__=='__main__': main()

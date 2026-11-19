"""Independent partition and trace audit of the frozen V45 outer algorithm."""
import argparse
from collections import Counter
from functools import lru_cache
import itertools
import json
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'teacher_v46'))
from run import OLD, V45, load, rows, sha

SEED = 461119


@lru_cache(maxsize=None)
def partitions(n):
    """Restricted-growth recursion, with blocks stored as event masks."""
    if n == 0:
        return ((),)
    bit = 1 << (n-1)
    return tuple(p+(bit,) for p in partitions(n-1)) + tuple(
        p[:j]+(p[j]|bit,)+p[j+1:] for p in partitions(n-1) for j in range(len(p))
    )


class Reference:
    def __init__(self, data):
        a = data['alphabet']
        ids = {a:i for i,a in enumerate(a)}
        self.a = a
        self.n = len(a)
        self.full = (1<<len(a))-1
        self.p = tuple(dict.fromkeys(map(tuple,data['positive'])))
        self.y = tuple(dict.fromkeys(map(tuple,data['negative'])))
        self.projections = {}
        self.reject = {}
        for b in range(self.full+1):
            def project(w):
                return tuple(x for x in w if b >> ids[x] & 1)
            pos = tuple(map(project,self.p))
            neg = tuple(map(project,self.y))
            self.projections[b] = (pos,neg)
            self.reject[b] = frozenset(i for i,w in enumerate(neg) if w not in pos)
        self.compatible = [p for p in partitions(self.n) if self.failure(p) is None]
        self.k = max(map(len,self.compatible),default=None)

    def failure(self, p):
        return next((i for i in range(len(self.y)) if all(i not in self.reject[b] for b in p)),None)

    def atoms(self):
        groups = [1<<j for j in range(self.n)]
        for i in range(len(self.y)):
            forced = sum(1<<j for j in range(self.n) if i not in self.reject[self.full^(1<<j)])
            touching = [g for g in groups if g&forced]
            if touching:
                groups = [g for g in groups if not g&forced]+[sum(touching)]
        return sorted(groups,key=lambda g:g&-g)

    def trace(self, trace):
        if not trace:
            return []
        atoms = self.atoms()
        # The two structural queries precede the cut loop. Once an initial cut
        # has been published every subsequent completed query is a master optimum.
        domain = [p for p in partitions(self.n) if all(any(g&b==g for b in p) for g in atoms)]
        assert all(p in domain for p in self.compatible)
        cuts = 0
        checks = []
        for j, step in enumerate(trace):
            p = tuple(sorted(step['partition_masks'], key=lambda m:m&-m))
            assert p in partitions(self.n)
            expected = 'REJECT' if self.failure(p) is not None else 'ACCEPT'
            assert step['teacher_status']==expected
            master_k = max(map(len,domain)) if cuts else None
            if cuts:
                assert p in domain and len(p)==master_k
            cut = step.get('cut')
            if cut:
                i = cut['negative_index']
                assert expected=='REJECT' and all(i not in self.reject[b] for b in p)
                regions = [sum(g for k,g in enumerate(atoms) if u>>k&1) for u in cut['regions']]
                for u,w in zip(regions,cut['positive_indices'],strict=True):
                    pos,neg = self.projections[u]
                    assert pos[w]==neg[i] and u!=self.full
                    assert all(i in self.reject[u|g] for g in atoms if not g&u)
                def satisfies(z):
                    return any(all(b&u!=b for u in regions) for b in z)
                assert not satisfies(p)
                assert all(map(satisfies,self.compatible))
                domain = [z for z in domain if satisfies(z)]
                cuts += 1
            checks.append(dict(candidate=list(p),teacher=expected,master_k=master_k,
                               cut_checked=bool(cut),surviving_relaxation=len(domain)))
        return checks


def cases():
    rng = random.Random(SEED)
    ids = ['event 0','event/1','ژن','αβ','未使用','🧩','s-6']
    for j in range(150):
        n = j % 8
        a = rng.sample(ids,n)
        if j % 5 == 0:
            p = []
        elif j % 5 == 1 or not a:
            p = [[]]
        elif j % 5 == 2:
            p = [[a[0]]]*2
        else:
            p = [[a[0]]*(1+j%3)]
        def word():
            return rng.choices(a,k=rng.choice((0,1,2,3,8,25))) if a else []
        y = [word() for _ in range(1+j%2)]
        if p and j%11==0:
            y.append(p[0][:])
        if j%13==0:
            y = []
        yield f'mixed-{j:03}', dict(alphabet=a,positive=p,negative=y), 10
    targeted = [
        ('order-only',list('ba'), ['ab'], ['ba']),
        ('order-unused',list('bdac'), ['ab'], ['ba','ba']),
        ('epsilon-pair',list('ba'), ['a','b'], ['','ab']),
        ('nonunique-one-cut',list('cba'), ['abc'], ['cba']),
        ('multiple-negatives',list('bca'), ['abc'], ['bca','cab']),
        ('mandatory-suffix-pair',list('cab'), ['abc'], ['acb','cba']),
        ('long-input',list('abc'), [''], ['a'*300+'bc','ba'*100]),
        ('overlapping-binary-regions',list('abcd'), ['', 'abcd'], ['a','b','c','d']),
    ]
    for name,a,p,y in targeted:
        yield name, dict(alphabet=a,positive=list(map(list,p)),negative=list(map(list,y))), 90


def historical():
    base = HERE.parent/'teacher_v46'/'evidence'
    for name in ('corpus','benchmark','fixtures','escalations'):
        data = rows(base/(name+'.jsonl'))
        if name=='benchmark':
            data = [r for r in data if r['method']=='v45']
        counts = Counter(r['profile']['result']['status'] for r in data)
        assert all(r['contract_valid'] for r in data)
        for r in data:
            result = r['profile']['result']
            if result['status']=='INCOMPLETE':
                assert r['checked'] is None and all(result[k] is None for k in ('blocks','max_devices','certificate'))
            else:
                assert r['checked']=={'status':'ACCEPT'} and result['max_devices']==r['expected_k']
        yield dict(suite=name,statuses=dict(counts),rows=len(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out',type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    solve,verify = load('v45')
    counts = Counter()
    with (args.out/'cases.jsonl').open('x',encoding='utf-8') as stream:
        for name,d,limit in cases():
            reference = Reference(d)
            t = time.perf_counter()
            profile = solve(d,{'timeout_seconds':limit})
            elapsed = time.perf_counter()-t
            result = profile['result']
            status = result['status']
            verdict = None
            if status in ('OPTIMAL','INFEASIBLE'):
                verdict = verify(d,result,{'timeout_seconds':30})
                good = verdict=={'status':'ACCEPT'} and result['max_devices']==reference.k
                good &= (status=='INFEASIBLE')==(reference.k is None)
                if status=='OPTIMAL':
                    p = tuple(sorted([sum(1<<reference.a.index(x) for x in b)
                                      for b in result['blocks']],key=lambda b:b&-b))
                    good &= p in reference.compatible and len(p)==reference.k
            else:
                good = status=='INCOMPLETE' and all(result[key] is None
                                                    for key in ('blocks','max_devices','certificate'))
            try:
                trace_checks = reference.trace(profile['trace'])
            except AssertionError:
                trace_checks = None
                good = False
            row = dict(case=name,input=d,expected_k=reference.k,oracle_partitions=len(partitions(reference.n)),
                       oracle_compatible=len(reference.compatible),solve_limit_seconds=limit,
                       consumer_limit_seconds=30,solve_seconds=elapsed,profile=profile,
                       consumer=verdict,trace_checks=trace_checks,match=good)
            stream.write(json.dumps(row)+'\n')
            stream.flush()
            counts[status] += 1
            if not name.startswith('mixed') or not good or sum(counts.values())%25==0:
                print(name,status,reference.k,round(elapsed,3),good,flush=True)
            if not good:
                raise RuntimeError(f'Review evidence for {name}')
    saved = rows(args.out/'cases.jsonl')
    summary = dict(seed=SEED, statuses=dict(counts), run_count=len(saved), historical=list(historical()),
                   oracle_partitions=sum(r['oracle_partitions'] for r in saved),
                   cutoff_phases=dict(Counter(r['profile']['metrics'].get('interrupted_phase')
                                             for r in saved if r['profile']['result']['status']=='INCOMPLETE')),
                   master_candidates=sum(c['master_k'] is not None for r in saved for c in r['trace_checks']),
                   cuts=sum(c['cut_checked'] for r in saved for c in r['trace_checks']),
                   teacher_sha256=sha(V45/'teacher_main.py'), optimizer_sha256=sha(V45/'optimizer.py'),
                   master_sha256=sha(V45/'master.py'))
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()

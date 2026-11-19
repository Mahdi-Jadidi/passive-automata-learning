"""Frozen-reference audits and sequential matched V45/V47 trials."""
import argparse
from collections import Counter
import itertools
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent/'teacher_v46'))
from run import CORPUS, FIXED, ROOT, V45, rows, sha


def api(version):
    if version=='v47':
        from optimizer_v47 import solve_profiled
    else:
        sys.path.insert(0,str(V45))
        from optimizer import solve_profiled
    from verify import verify_optimal
    return solve_profiled, verify_optimal


def measure(case, seconds, checker_seconds, solver):
    solve, verify = solver
    started = time.perf_counter()
    profile = solve(case['input'], {'timeout_seconds':seconds})
    solve_seconds = time.perf_counter()-started
    result = profile['result']
    checked = None
    expected = case['expected_k']
    if result['status'] in ('OPTIMAL','INFEASIBLE'):
        started = time.perf_counter()
        checked = verify(case['input'],result,{'timeout_seconds':checker_seconds})
        consumer_seconds = time.perf_counter()-started
        match = (checked=={'status':'ACCEPT'} and result['max_devices']==expected
                 and (result['status']=='INFEASIBLE')==(expected is None))
    else:
        consumer_seconds = None
        match = result['status']=='INCOMPLETE' and all(result[key] is None
                            for key in ('blocks','max_devices','certificate'))
    return dict(case,profile=profile,checked=checked,contract_valid=match,limit_seconds=seconds,
                checker_limit_seconds=checker_seconds,solve_seconds=solve_seconds,
                consumer_seconds=consumer_seconds)


def emit(stream, row):
    stream.write(json.dumps(row)+'\n')
    stream.flush()
    if not row['contract_valid']:
        raise AssertionError(row)


def graph_cases():
    rng = random.Random(471119)
    all_graphs = []
    for n in (2,3,4):
        pairs = list(itertools.combinations(range(n),2))
        for bits in range(1,1<<len(pairs)):
            all_graphs.append((n,[e for j,e in enumerate(pairs) if bits>>j&1]))
    for n in range(5,9):
        pairs = list(itertools.combinations(range(n),2))
        for _ in range(8):
            all_graphs.append((n,sorted(rng.sample(pairs,rng.randrange(1,len(pairs)+1)))))
    for i,(n,edges) in enumerate(all_graphs):
        tau = min(mask.bit_count() for mask in range(1,1<<n)
                  if all(mask & ((1<<u)|(1<<v)) for u,v in edges))
        a = [f'v{j}' for j in range(n)]
        yield dict(case=f'graph-{i:03}',n=n,edges=edges,vertex_cover=tau,expected_k=n-tau+1,
                   input=dict(alphabet=a,positive=[[a[u],a[v]] for u,v in edges],negative=[[]]))


def replay(path, dataset, seconds, checker_seconds, solver):
    with path.open('x',encoding='utf-8') as stream:
        for case in dataset:
            emit(stream,measure(case,seconds,checker_seconds,solver))
    return dict(Counter(r['profile']['result']['status'] for r in rows(path)))


def worker(case, version, seconds, checker_seconds):
    data = measure(case,seconds,checker_seconds,api(version))
    print(json.dumps(data),flush=True)


def timed(case, version, seconds, checker_seconds, repetition):
    start = time.perf_counter()
    cmd = [sys.executable,'-B',str(__file__),'--worker',version,
           '--seconds',str(seconds),'--checker-seconds',str(checker_seconds)]
    process = subprocess.run(cmd,input=json.dumps(case),capture_output=True,text=True,check=True,
                             timeout=seconds+checker_seconds+30)
    return dict(json.loads(process.stdout),version=version,repetition=repetition,
                fresh_process_seconds=time.perf_counter()-start,worker_stderr=process.stderr)


def benchmarks(out):
    known = {r['case']:r['expected_k'] for r in rows(HERE.parent/'teacher_v46/evidence/benchmark.jsonl')}
    cases = [dict(r,expected_k=known[r['case']]) for r in rows(FIXED)]
    ordinary = json.loads((V45/'interaction_example.json').read_text(encoding='utf-8'))['input']
    with (out/'matched.jsonl').open('x',encoding='utf-8') as stream:
        for case in cases:
            for version in ('v45','v47'):
                result = timed(case,version,2,2,0)
                emit(stream,result)
                print(case['case'],version,result['profile']['result']['status'],
                      round(result['solve_seconds'],5),flush=True)
        for rep,order in enumerate((('v45','v47'),('v47','v45'))):
            for version in order:
                result = timed(dict(case='ordinary_fixture', input=ordinary,expected_k=2),
                               version,60,10,rep)
                emit(stream,result)
                print('ordinary_fixture',version,rep,result['profile']['result']['status'],
                      round(result['solve_seconds'],5),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    parser.add_argument('--worker',choices=('v45','v47'))
    parser.add_argument('--seconds',type=float,default=2)
    parser.add_argument('--checker-seconds',type=float,default=2)
    args = parser.parse_args()
    if args.worker:
        return worker(json.load(sys.stdin),args.worker,args.seconds,args.checker_seconds)
    if args.out is None:
        parser.error('--out is required')
    args.out.mkdir(parents=True,exist_ok=False)
    env = dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
               seed=471119, branch=subprocess.check_output(['git','branch','--show-current'],
                   cwd=ROOT,text=True).strip(), hashes={f.relative_to(ROOT).as_posix():sha(f)
                   for f in (CORPUS,FIXED,V45/'optimizer.py',V45/'teacher_main.py',V45/'verify.py',
                             HERE/'projection_teacher.py',HERE/'optimizer_v47.py',Path(__file__))})
    (args.out/'environment.json').write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8')
    solver = api('v47')
    corpus = [dict(case=r['i'],input=r['input'],expected_k=r['expected_k']) for r in rows(CORPUS)]
    outer = [dict(case=r['case'],input=r['input'],expected_k=r['expected_k']) for r in
             rows(HERE.parent/'teacher_v46_outer_audit/evidence/cases.jsonl')]
    summary = {}
    for name,dataset,solve_seconds in [('corpus',corpus,0.25),('outer',outer,10),
                                        ('vertex_cover',graph_cases(),10)]:
        summary[name] = replay(args.out/(name+'.jsonl'),dataset,solve_seconds,2,solver)
        print(name,summary[name],flush=True)
    with (args.out/'zero_budget.json').open('x',encoding='utf-8') as stream:
        row = measure(dict(case='resource',input=corpus[0]['input'],expected_k=corpus[0]['expected_k']),
                      0,2,solver)
        assert row['profile']['result']['status']=='INCOMPLETE'
        emit(stream,row)
    benchmarks(args.out)
    matched = rows(args.out/'matched.jsonl')
    summary['matched_fixed'] = {v:dict(Counter(r['profile']['result']['status'] for r in matched
                      if r['version']==v and r['case']!='ordinary_fixture')) for v in ('v45','v47')}
    summary['ordinary_fixture'] = {v:[r['solve_seconds'] for r in matched
                      if r['version']==v and r['case']=='ordinary_fixture'] for v in ('v45','v47')}
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()

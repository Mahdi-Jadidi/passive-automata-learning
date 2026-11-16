"""Same optimum + independently replayed proof contract, bounded trials."""
import json,time,sys,subprocess,statistics,importlib.util,hashlib,platform,os
from pathlib import Path
from functools import lru_cache
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
CORPUS=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'

def peak_working_set():
    if os.name!='nt':return None
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ['peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]
    kernel=ctypes.WinDLL('kernel32');api=ctypes.WinDLL('psapi')
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    c=Counters();c.cb=ctypes.sizeof(c)
    return c.peak if api.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(c),c.cb) else None

def child(method,i):
    folder=ROOT/'results/2026-11-15/exact_optimizer_v42' if method=='v42' else HERE
    sys.path.insert(0,str(folder))
    spec=importlib.util.spec_from_file_location('measured_optimizer',folder/'optimizer.py')
    O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)
    import encoding as E
    from verify import verify_optimal
    D=[json.loads(s) for s in CORPUS.read_text().splitlines()][i]['input']
    tick=E.budget({'timeout_seconds':55});metrics={};start=time.perf_counter()
    if method in ('v42','v43'):
        if method=='v43':
            measured=O.solve_profiled(D,{'timeout_seconds':55});result=measured['result'];metrics=measured['metrics']
        else:result=O.solve_optimal(D,{'timeout_seconds':55})
    else:
        Sigma,S_plus,S_minus=E.normalize(D);single=[[x] for x in Sigma]
        if E.feasible(Sigma,S_plus,S_minus,single):partition=single
        elif method=='enumeration':
            def visit(i,blocks):
                tick()
                if i==len(Sigma):yield blocks;return
                for j in range(len(blocks)):
                    nxt=[b[:] for b in blocks];nxt[j].append(Sigma[i]);yield from visit(i+1,nxt)
                yield from visit(i+1,blocks+[[Sigma[i]]])
            partition=None
            for B in visit(0,[]):
                if E.feasible(Sigma,S_plus,S_minus,B) and (partition is None or len(B)>len(partition)):partition=B
        else:
            full=(1<<len(Sigma))-1;missing=(1<<len(S_minus))-1;choices={}
            @lru_cache(None)
            def rejection(B):return sum(1<<j for j in E.reject(Sigma,S_plus,S_minus,[i for i in range(len(Sigma)) if B>>i&1]))
            @lru_cache(None)
            def dp(s,u):
                tick()
                if not s:return 0 if not u else -1000000
                if not u:return s.bit_count()
                if u&~rejection(s):return -1000000
                anchor=s&-s;tail=s^anchor;t=tail;best=-1000000
                while True:
                    B=t|anchor;value=1+dp(s^B,u&~rejection(B))
                    if value>best:best=value;choices[s,u]=B
                    if not t:break
                    t=(t-1)&tail
                return best
            dp(full,missing);partition=[];s=full;u=missing
            while s:
                B=(s&-s) if not u else choices[s,u]
                partition.append([Sigma[i] for i in range(len(Sigma)) if B>>i&1]);s^=B;u&=~rejection(B)
        k=len(partition)
        if k==len(Sigma):cert={'type':'symbol_bound'}
        else:
            enc=E.build(Sigma,S_plus,S_minus,tick)
            if k==enc['q']:cert={'type':'atom_bound'}
            elif k==enc['upper']:cert={'type':'edge_size_bound'}
            else:
                with O.Solver(name='g3',bootstrap_with=E.threshold(enc,k+1),with_proof=True) as solver:
                    if O.query(solver,tick):raise RuntimeError('baseline not optimal')
                    cert={'type':'drup','proof':solver.get_proof()}
        result=O.response('OPTIMAL',partition,k,cert)
    solve_seconds=time.perf_counter()-start
    now=time.perf_counter();checked=verify_optimal(D,result,{'timeout_seconds':tick.remaining()});verify_seconds=time.perf_counter()-now
    print(json.dumps({'result':result,'checked':checked,'solve_seconds':solve_seconds,'verify_seconds':verify_seconds,'total_seconds':time.perf_counter()-start,'peak_working_set_bytes':peak_working_set(),'metrics':metrics}))

def main():
    rows=[json.loads(x) for x in CORPUS.read_text().splitlines()];names=['enumeration','dp','v42','v43']
    with (HERE/'benchmark_raw.jsonl').open('x',encoding='utf8') as stream:
        stream.write(json.dumps({'metadata':{'timeout':60,'repeats':3,'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),'corpus_sha256':hashlib.sha256(CORPUS.read_bytes()).hexdigest(),'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in [HERE,ROOT/'results/2026-11-15/exact_optimizer_v42'] for p in folder.glob('*.py')}}})+'\n');stream.flush()
        for i,row in enumerate(rows):
            for rep in range(3):
                order=names[(i+rep)%4:]+names[:(i+rep)%4]
                for method in order:
                    rec={'case':row['case'],'repeat':rep,'method':method}
                    start=time.perf_counter()
                    try:
                        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',method,str(i)],capture_output=True,text=True,timeout=60)
                        rec.update(stdout=proc.stdout,stderr=proc.stderr,exit=proc.returncode)
                        if proc.returncode:rec['status']='ERROR'
                        else:rec.update(json.loads(proc.stdout));rec['status']=rec['result']['status']
                    except subprocess.TimeoutExpired:rec['status']='TIMEOUT'
                    rec['startup_wall_seconds']=time.perf_counter()-start
                    stream.write(json.dumps(rec)+'\n');stream.flush();print(row['case'],rep,method,rec['status'],flush=True)
if __name__=='__main__':
    if len(sys.argv)>1:child(sys.argv[2],int(sys.argv[3]))
    else:main()

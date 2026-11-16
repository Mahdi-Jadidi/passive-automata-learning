"""Same optimum-only + checked proof contract for all timed methods."""
import json,time,sys,subprocess,statistics,importlib.util,hashlib
from pathlib import Path
from functools import lru_cache
import encoding as E
import optimizer as O
from verify import verify_optimal
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
CORPUS=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
def child(name,i):
 data=[json.loads(s) for s in CORPUS.read_text().splitlines()][i]['input']
 tick=E.budget({'timeout_seconds':55}); a,p,n=E.normalize(data); start=time.perf_counter()
 if name=='constraints':
  result=O.solve_optimal(data,{'timeout_seconds':55})
 else:
  single=[[x] for x in a]
  if E.feasible(a,p,n,single): blocks=single
  elif name=='enumeration':
   def visit(i,blocks):
    tick()
    if i==len(a):
     yield blocks;return
    for j in range(len(blocks)):
     nxt=[b[:] for b in blocks];nxt[j].append(a[i]);yield from visit(i+1,nxt)
    yield from visit(i+1,blocks+[[a[i]]])
   blocks=None
   for b in visit(0,[]):
    if E.feasible(a,p,n,b) and (blocks is None or len(b)>len(blocks)):blocks=b
  else:
   full=(1<<len(a))-1; missing=(1<<len(n))-1; choices={}
   @lru_cache(None)
   def rejection(b):return sum(1<<j for j in E.reject(a,p,n,[i for i in range(len(a)) if b>>i&1]))
   @lru_cache(None)
   def dp(s,u):
    tick()
    if not s:return 0 if not u else -1000000
    if not u:return s.bit_count()
    if u&~rejection(s):return -1000000
    anchor=s&-s; tail=s^anchor; t=tail; best=-1000000
    while True:
     b=t|anchor;value=1+dp(s^b,u&~rejection(b))
     if value>best:best=value;choices[s,u]=b
     if not t:break
     t=(t-1)&tail
    return best
   dp(full,missing);blocks=[];s=full;u=missing
   while s:
    b=(s&-s) if not u else choices[s,u]
    blocks.append([a[i] for i in range(len(a)) if b>>i&1]);s^=b;u&=~rejection(b)
  k=len(blocks)
  if k==len(a):cert={'type':'symbol_bound'}
  else:
   enc=E.build(a,p,n,tick)
   if k==enc['q']:cert={'type':'atom_bound'}
   else:
    model,proof=O.call(E.threshold(enc,k+1),tick,True)
    if model is not None:raise RuntimeError('baseline not optimal')
    cert={'type':'drup','proof':proof}
  result=O.response('OPTIMAL',blocks,k,cert)
  if verify_optimal(data,result,{'timeout_seconds':tick.remaining()})!={'status':'ACCEPT'}:raise RuntimeError('proof rejected')
 elapsed=time.perf_counter()-start
 print(json.dumps({'result':result,'seconds':elapsed}))
def main():
 rows=[json.loads(x) for x in CORPUS.read_text().splitlines()];names=['enumeration','dp','constraints']
 with (HERE/'benchmark_raw.jsonl').open('x',encoding='utf8') as stream:
  stream.write(json.dumps({'metadata':{'timeout':60,'repeats':3,'corpus_sha256':hashlib.sha256(CORPUS.read_bytes()).hexdigest(),'python':sys.version,'sources':{f:hashlib.sha256((HERE/f).read_bytes()).hexdigest() for f in ['encoding.py','optimizer.py','verify.py','benchmark.py']}}})+'\n');stream.flush()
  for i,row in enumerate(rows):
   for rep in range(3):
    order=names[(i+rep)%3:]+names[:(i+rep)%3]
    for name in order:
     rec={'case':row['case'],'repeat':rep,'method':name}
     try:
      proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',name,str(i)],capture_output=True,text=True,timeout=60)
      rec.update(stdout=proc.stdout,stderr=proc.stderr,exit=proc.returncode)
      if proc.returncode:rec['status']='ERROR'
      else:rec.update(json.loads(proc.stdout));rec['status']=rec['result']['status']
     except subprocess.TimeoutExpired:rec['status']='TIMEOUT'
     stream.write(json.dumps(rec)+'\n');stream.flush();print(row['case'],rep,name,rec['status'],flush=True)
if __name__=='__main__':
 if len(sys.argv)>1:child(sys.argv[2],int(sys.argv[3]))
 else:main()

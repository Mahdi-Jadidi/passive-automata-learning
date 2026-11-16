"""Distinct three-symbol cases, independent reference, timeouts retained."""
import hashlib, importlib.util, itertools, json, random, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REF=ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py'
def load(path):
 spec=importlib.util.spec_from_file_location('candidate',path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
def cases():
 rng=random.Random(20261115); a=['a','b','c']; words=[list(x) for k in range(3) for x in itertools.product(a,repeat=k)]
 data=[]; seen=set()
 while len(data)<30:
  pool=words[:]; rng.shuffle(pool); npos=rng.randrange(4); nneg=rng.randrange(4); obj={'alphabet':a,'positive':pool[:npos],'negative':pool[npos:npos+nneg]}; key=json.dumps(obj,sort_keys=True)
  if key not in seen: seen.add(key); data.append(obj)
 return data
def main():
 items=cases()
 if len(sys.argv)>1:
  result=load(HERE/'candidate.py').solve(items[int(sys.argv[1])]); print(json.dumps(result)); return
 out=HERE/'distinct_audit_raw.jsonl'; ref=load(REF)
 if out.exists(): raise RuntimeError('refusing to overwrite audit evidence')
 with out.open('x',encoding='utf8') as f:
  for i,data in enumerate(items):
   expected=ref.solve(data); rec={'index':i,'input':data,'expected':expected}
   try:
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),str(i)],capture_output=True,text=True,timeout=3)
    rec.update(exit=p.returncode,stderr=p.stderr,stdout=p.stdout)
    if p.returncode: rec['status']='ERROR'
    else:
     result=json.loads(p.stdout); rec['result']=result; rec['status']=result['status']; rec['match']=result==expected
   except subprocess.TimeoutExpired: rec['status']='TIMEOUT'
   f.write(json.dumps(rec)+'\n'); f.flush(); print(i,rec['status'],rec.get('match'),flush=True)
if __name__=='__main__': main()

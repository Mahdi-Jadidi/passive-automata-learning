"""Bounded pilot, each case in a separate process; do not overwrite evidence."""
import hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CORPUS=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
REF=ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py'
def load(path):
 s=importlib.util.spec_from_file_location('solver',path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def main():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding='utf8').splitlines()]
 if len(sys.argv)>1:
  row=rows[int(sys.argv[1])]; start=time.perf_counter_ns(); result=load(HERE/'candidate.py').solve(row['input']); print(json.dumps({'result':result,'elapsed_ns':time.perf_counter_ns()-start})); return
 out=HERE/'pilot_raw.jsonl'
 if out.exists(): raise RuntimeError('raw evidence exists')
 ref=load(REF)
 with out.open('x',encoding='utf8') as f:
  for i,row in enumerate(rows):
   expected=ref.solve(row['input']); rec={'case':row['case']}
   try:
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),str(i)],capture_output=True,text=True,timeout=3)
    rec.update(exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
    if p.returncode: rec['status']='ERROR'
    else:
     data=json.loads(p.stdout); rec.update(data); rec['status']=data['result']['status']; rec['matches_reference']=data['result']==expected
   except subprocess.TimeoutExpired: rec['status']='TIMEOUT'
   f.write(json.dumps(rec)+'\n'); f.flush(); print(row['case'],rec['status'],rec.get('matches_reference'),flush=True)
if __name__=='__main__': main()

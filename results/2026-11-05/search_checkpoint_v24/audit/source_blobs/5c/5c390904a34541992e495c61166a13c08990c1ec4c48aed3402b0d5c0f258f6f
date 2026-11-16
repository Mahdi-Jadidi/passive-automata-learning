"""Run supplemental correctness after timing; preserve all attempts."""
import json,sys
from pathlib import Path
import capture
from certificate_replay_c015_v2 import verify
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
 assert (A/'runs/C024-TIMING-01/closure.json').exists(),'Do not add provider load during timing'
 jobs=read(A/'SUPPLEMENT_MANIFEST_V2.json')['jobs'];ors={o['job_id']:o for o in read(A/'SUPPLEMENT_ORACLES_V2.json')['jobs']};out=A/'runs/C024-SUPPLEMENT-02';out.mkdir(exist_ok=False);cp=out/'jobs.json';cp.write_text(json.dumps(jobs));rows=[]
 for p in read(A/'PROVIDERS_V1.json')['providers']:
  cap=capture.capture('C024-SUPPLEMENT-02_'+p['id'],[sys.executable,'-B','-X','utf8',str(A/'provider_batch_v1.py'),p['solver'],str(cp)],cwd=ROOT,timeout_seconds=25,source_paths=[Path(p['solver']),Path(p['cli']),A/'provider_batch_v1.py',Path(__file__),cp,A/'SUPPLEMENT_ORACLES_V2.json'])
  records=[json.loads(l) for l in (Path(cap['attempt_dir'])/'stdout.bin').read_bytes().splitlines()];lookup={j['job_id']:j for j in jobs};seen=set()
  for r in records:
   jid=r['job_id'];seen.add(jid)
   try:assert not r.get('error') and not r.get('unstarted');v=verify(lookup[jid],r['result'],ors[jid]);assert v!='unresolved';rows.append({'provider':p['id'],'job_id':jid,'decision':v,'attempt_id':cap['attempt_id']})
   except Exception as e:rows.append({'provider':p['id'],'job_id':jid,'failure_id':p['id']+'-'+jid,'error':repr(e),'attempt_id':cap['attempt_id']})
  for jid in set(lookup)-seen:rows.append({'provider':p['id'],'job_id':jid,'error':'missing_record'})
 (out/'REPORT_V2.json').write_text(json.dumps({'rows':rows,'errors':sum('error' in r for r in rows)},indent=2));print({'errors':sum('error' in r for r in rows),'calls':len(rows)})
if __name__=='__main__':main()

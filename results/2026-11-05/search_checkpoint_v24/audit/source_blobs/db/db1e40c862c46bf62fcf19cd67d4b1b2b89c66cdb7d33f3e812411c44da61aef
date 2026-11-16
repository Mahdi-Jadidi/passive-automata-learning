"""Integrated CLI smoke after separate A/B timing, no timing claims."""
import hashlib,json,sys
from pathlib import Path
import capture
from oracle_data_v1 import full_family
from certificate_replay_c015_v2 import verify,analytic_obstruction
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
 p=read(A/'PROVIDERS_INTEGRATED_V1.json')['providers'][0];cells={c['cell_id']:c for c in read(A/'TIMING_PLAN_V1.json')['cells']};run=A/'runs/C024-INTEGRATED-CLI-01';run.mkdir(exist_ok=False);rows=[]
 for name,cid,seconds in [('obstruction_noK','obstruction_m8_noK',20),('D_K4','D_K4',20),('expired','obstruction_m12_noK',0),('midsearch','obstruction_m12_noK',0.05)]:
  c=cells[cid];cmd=[sys.executable,'-B','-X','utf8',p['cli'],c['input'],'--seconds',str(seconds)]
  if c['known_k'] is not None:cmd+=['--known-k',str(c['known_k'])]
  cap=capture.capture('C024-INTEGRATED-CLI-'+name,cmd,cwd=ROOT,timeout_seconds=25,source_paths=[Path(p['solver']),Path(p['cli']),Path(__file__),Path(c['input'])]);row={'case':name,'attempt_id':cap['attempt_id'],'execution_status':cap['execution_status']}
  try:
   assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error');d=Path(cap['attempt_dir']);res=json.loads((d/'stdout.bin').read_bytes());row.update(status=res['status'],metrics=res.get('metrics',{}));assert res['input_sha256']==c['input_sha256']
   for stream in ['stdout','stderr']:assert hashlib.sha256((d/(stream+'.bin')).read_bytes()).hexdigest()==cap[stream+'_sha256']
   if name in ['expired','midsearch']:
    assert cap['exit_code']==3 and res['status']=='unresolved' and res['findings']['computation_incomplete'] is True and 'partition' not in res and 'alternatives' not in res
    if name=='midsearch':assert res['metrics']['search_nodes']>0
   else:
    data=read(c['input']);k=c['known_k']
    if name=='obstruction_noK':analytic_obstruction(data);family=[[0]*len(data['alphabet'])]
    else:family=[x for x in full_family(data) if max(x)+1==k]
    assert cap['exit_code']==0;job={'job_id':name,'input':c['input'],'input_sha256':c['input_sha256'],'allowed_k':None if k is None else [k],'expectation':'unique'};verify(job,res,{'compatible_rgs':family})
  except Exception as e:row.update(failure_id='C024-INTEGRATED-CLI-'+name,error=repr(e))
  rows.append(row)
 out={'rows':rows,'errors':sum('error' in r for r in rows),'official_timing_claim':False};(run/'REPORT_V1.json').write_text(json.dumps(out,indent=2)+'\n');print({'errors':out['errors'],'rows':rows})
if __name__=='__main__':main()

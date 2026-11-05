"""Five-cell C022 timing matrix using the existing C020 durable capture."""
import hashlib,json,sys,time
from pathlib import Path
import capture
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    f=read(A/'SOURCE_INPUT_FREEZE_V4.json');plan=read(A/'TIMING_PLAN_V1.json')
    for x in f['frozen_files']+f['audit_tools']:
        assert sha(x['path'])==x['sha256'],x['path']
    for x in f['fixture_artifacts']:
        assert sha(x['path'])==x['sha256'],x['path']
    assert sha(A/'TIMING_PLAN_V1.json')==f['timing_plan_sha256']
    assert sha(A/'run_timing_v3.py')==f['timing_runner_sha256']
    fixtures=read(f['fixture_manifest_path']);inputs={x['case_id']:x for x in fixtures['inputs']}
    providers=f['providers'];spent={p['id']:0.0 for p in providers};run=A/'timing_runs'/f['run_id'];run.mkdir(parents=True,exist_ok=False);ledger=[]
    src=[A/'run_timing_v3.py',A/'validate_timing_v3.py',A/'TIMING_PLAN_V1.json',A/'SOURCE_INPUT_FREEZE_V4.json',A/'capture.py',A/'BINDING_V1.json',A/'SPECIAL_CONTROLS_AND_COUNTEREXAMPLES_V1.json']
    for p in providers:src.extend([A/p['solver'],A/p['cli']])
    for ci,cell in enumerate(plan['cells']):
      fixture=inputs[cell['case_id']];ip=Path(fixture['input']);assert sha(ip)==cell['input_sha256']==fixture['input_sha256']
      for rep in (1,2,3):
        order=providers[(ci+rep-1)%len(providers):]+providers[:(ci+rep-1)%len(providers)]
        for provider in order:
          if spent[provider['id']]+25>300:
            ledger.append({'cell_id':cell['cell_id'],'provider':provider['id'],'rep':rep,'execution_status':'budget_unstarted'});continue
          cmd=[sys.executable,'-B','-X','utf8',str(A/provider['cli']),str(ip),'--seconds','20']
          if cell['known_k'] is not None:cmd.extend(['--known-k',str(cell['known_k'])])
          t=time.perf_counter();cap=capture.capture('c022_'+f['run_id']+'_'+cell['cell_id']+'_'+provider['id']+'_r'+str(rep),cmd,cwd=ROOT,timeout_seconds=25,source_paths=src+[ip]);charge=time.perf_counter()-t;spent[provider['id']]+=charge
          row={'cell_id':cell['cell_id'],'case_id':cell['case_id'],'known_k':cell['known_k'],'provider':provider['id'],'rep':rep,'input_sha256':sha(ip),'attempt_id':cap['attempt_id'],'execution_status':cap['execution_status'],'exit_code':cap['exit_code'],'subprocess_seconds':cap['subprocess_seconds'],'capture_charge_seconds':charge,'provider_charged_seconds':spent[provider['id']]};ledger.append(row)
          print(json.dumps(row,ensure_ascii=False),flush=True)
    (run/'ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger),encoding='utf-8')
    (run/'closure.json').write_text(json.dumps({'status':'captured','provider_charged_seconds':spent,'budgets_seconds':{p:300 for p in spent},'run_id':f['run_id']},indent=2),encoding='utf-8')
    print(json.dumps({'run_id':f['run_id'],'attempts':len([x for x in ledger if 'attempt_id' in x]),'unstarted':len([x for x in ledger if x['execution_status']=='budget_unstarted']),'charged':spent},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())



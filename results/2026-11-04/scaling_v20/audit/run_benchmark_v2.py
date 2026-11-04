"""One frozen bounded C020 suite. Master GO lists reviewed providers only."""
import json,sys,time,os
from pathlib import Path
from datetime import datetime,timezone
import capture
A=Path(__file__).resolve().parent;R=A.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    freeze_path=A/'BENCHMARK_FREEZE_V1.json';go=read(A/'BENCHMARK_GO_V1.json');assert go['status']=='GO' and go['execution_freeze_sha256']==sha(freeze_path);frozen=read(freeze_path);binding=read(A/'BINDING_V1.json');providers=list(binding);assert providers==go['providers'] and providers[0]=='baseline' and len(providers)<=3
    def check():
        for p,h in frozen['sources'].items():assert sha(p)==h
    check();assert read(A/'FIXTURE_AUDIT_V1.json')['status']=='accepted'
    marker=A/'BENCHMARK_STARTED_V1.json'
    with marker.open('x',encoding='utf8') as f:json.dump(dict(started_utc=datetime.now(timezone.utc).isoformat(),freeze_sha256=sha(freeze_path),providers=providers),f)
    run=A/'benchmark_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(parents=True);ledger=(run/'ledger.jsonl').open('x',encoding='utf8');spent={p:0.0 for p in providers};spent['baseline']=read(A/'PROVIDER_PROFILE_CHARGE_V2.json')['charged_seconds'];sources=[Path(p) for p in frozen['sources']]+[freeze_path,A/'BENCHMARK_GO_V1.json',marker]
    def log(x):ledger.write(json.dumps(x)+'\n');ledger.flush();os.fsync(ledger.fileno())
    def call(label,cmd,cap,entry,extra=()):
        provider=entry.get('provider');began=time.perf_counter()
        if provider and spent[provider]+cap+3>600:log({**entry,'execution_status':'budget_unstarted','provider_charged_seconds':spent[provider]});return None
        check();result=capture.capture('c020_'+label,[sys.executable,'-B','-X','utf8',*map(str,cmd)],cwd=R,timeout_seconds=cap,source_paths=sources+list(extra));elapsed=time.perf_counter()-began
        if provider:spent[provider]+=elapsed
        log({**entry,'attempt_id':result['attempt_id'],'execution_status':result['execution_status'],'charged_seconds':elapsed if provider else 0,'provider_charged_seconds':None if provider is None else spent[provider]})
        assert result['child_reaped'] and not result.get('cleanup_error') and not result.get('capture_error')
        if provider and spent[provider]>600:raise RuntimeError('provider budget exceeded; preserve and stop')
        print(json.dumps(dict(label=label,status=result['execution_status'],attempt_id=result['attempt_id'],charged_by_provider=spent)),flush=True);return result
    batches=[]
    for p in providers:
        c=call('small_'+p,[A/'small_batch_v2.py',p],50,dict(kind='small_batch',provider=p));batches.append(c)
    if any(c is None or c['execution_status']!='success' for c in batches):
        ledger.close()
        with (run/'closure.json').open('x') as f:json.dump(dict(status='small_execution_incomplete',charged_by_provider=spent),f,indent=2)
        return 1
    checkpoint=run/'small_ledger_checkpoint.jsonl'
    with checkpoint.open('xb') as f:f.write((run/'ledger.jsonl').read_bytes())
    gate=call('small_verify',[A/'verify_small_v3.py',run],90,dict(kind='small_verify'),extra=[checkpoint])
    if gate['execution_status']!='success' or read(run/'small_report.json')['status']!='accepted':
        ledger.close()
        with (run/'closure.json').open('x') as f:json.dump(dict(status='small_semantics_rejected_or_incomplete',charged_by_provider=spent),f,indent=2)
        return 1
    fixtures=read(A/'FIXTURE_MANIFEST_V1.json');inputs={x['case_id']:x for x in fixtures['inputs']};proof=run/'small_report.json';proof_hash=sha(proof)
    for ci,cell in enumerate(fixtures['cells']):
        item=inputs[cell['case_id']];assert sha(item['input'])==item['input_sha256']
        for rep in [1,2,3]:
            offset=(ci+rep-1)%len(providers);order=providers[offset:]+providers[:offset]
            for p in order:
                assert sha(proof)==proof_hash;cmd=[binding[p]['cli'],item['input'],'--seconds','20']
                if cell['known_k'] is not None:cmd+=['--known-k',str(cell['known_k'])]
                call('timing_'+cell['cell_id']+'_'+p+'_r'+str(rep),cmd,25,dict(kind='timing',provider=p,cell_id=cell['cell_id'],rep=rep),extra=[Path(item['input']),proof])
    for cell_id in ['A_unknown','D_K4']:
        cell=next(c for c in fixtures['cells'] if c['cell_id']==cell_id);item=inputs[cell['case_id']]
        for p in providers:call('memory_'+cell_id+'_'+p,[A/'memory_worker_v1.py',p,item['input'],'unknown' if cell['known_k'] is None else str(cell['known_k'])],25,dict(kind='memory',provider=p,cell_id=cell_id),extra=[Path(item['input']),proof])
    final_checkpoint=run/'final_ledger_checkpoint.jsonl'
    with final_checkpoint.open('xb') as f:f.write((run/'ledger.jsonl').read_bytes())
    result=call('final_validate',[A/'validate_benchmark_v2.py',run],180,dict(kind='final_validation'),extra=[final_checkpoint,proof]);ledger.close()
    with (run/'closure.json').open('x') as f:json.dump(dict(status='validation_success' if result['execution_status']=='success' else 'validation_failed_or_incomplete',charged_by_provider=spent,per_provider_budget_seconds=600,fixture_preparation_excluded=True,profile_included=True),f,indent=2)
    return 0 if result['execution_status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())

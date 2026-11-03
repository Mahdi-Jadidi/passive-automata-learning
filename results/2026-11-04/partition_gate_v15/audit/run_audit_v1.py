"""One frozen C015 launch, bounded to300 active seconds, with no duplicate run."""
import hashlib,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
import capture
from launch_guard_v1 import claim
A=Path(__file__).resolve().parent;R=A.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    start=time.perf_counter();go=A/'MASTER_GO_V1.json';approval=json.loads(go.read_text());freeze=A/'EXECUTION_FREEZE_V1.json'
    assert approval['status']=='GO' and approval['execution_freeze_sha256']==sha(freeze)
    frozen=json.loads(freeze.read_text());sources=[Path(p) for p in frozen['sources']]+[freeze,go]
    def check():
        for p,h in frozen['sources'].items():assert sha(Path(p))==h
    check();marker=claim(A);run=A/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(parents=True);ledger=(run/'ledger.jsonl').open('x',encoding='utf-8')
    def call(label,command,cap,extra=(),entry=None):
        check();assert time.perf_counter()-start+cap+2<=300,'active budget cannot fit next captured stage'
        c=capture.capture('c015_'+label,[sys.executable,'-B','-X','utf8',*map(str,command)],cwd=R,timeout_seconds=cap,source_paths=sources+list(extra)+[marker])
        assert c['child_reaped'] and not c.get('cleanup_error') and not c.get('capture_error')
        if entry:
            ledger.write(json.dumps({**entry,'attempt_id':c['attempt_id']})+'\n');ledger.flush();os.fsync(ledger.fileno())
        print(json.dumps({'label':label,'attempt_id':c['attempt_id'],'status':c['execution_status'],'elapsed_active':time.perf_counter()-start}),flush=True)
        return c
    c=call('independent_data_and_oracles',[A/'oracle_data_v1.py'],45);assert c['execution_status']=='success'
    manifest=json.loads((A/'CASE_MANIFEST_V1.json').read_text());jobs={j['job_id']:j for j in manifest['jobs']};extra=[A/'CASE_MANIFEST_V1.json',A/'ORACLES_V1.json']+list((A/'data').glob('*.json'))+list((A/'invalid').glob('*.json'))
    c=call('api_batch',[A/'gate_batch_v1.py'],190,extra,{'kind':'batch'});assert c['execution_status']=='success','batch capture incomplete; retain raw output and do not retry'
    cli=Path(json.loads((A/'BINDING_V1.json').read_text())['cli']['path'])
    specs=[('graph_failure_unique_K2',None),('swap_covered_noK',None),('invalid_contradictory',None),('invalid_empty_alphabet',None),('empty_both_noK','timeout')]
    for jid,override in specs:
        job=jobs[jid];command=[cli,job['input'],'--seconds','0' if override else '0.5']
        if job['allowed_k'] is not None:command+=['--known-k',str(job['allowed_k'][0])]
        call('cli_'+jid+('_expired' if override else ''),command,2,extra,{'kind':'cli','job_id':jid,'expected_override':override})
    ledger.close();validation_sources=extra+[run/'ledger.jsonl']
    for row in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):validation_sources+=list((A/'attempts'/row['attempt_id']).glob('*'))
    c=call('independent_validation',[A/'validate_gate_v1.py',run],35,validation_sources)
    with (run/'closure.json').open('x') as f:json.dump({'status':'closed' if c['execution_status']=='success' else 'validation_failed_or_incomplete','active_seconds':time.perf_counter()-start,'budget_seconds':300,'validation_capture':c},f,indent=2)
    print(json.dumps({'run':str(run),'validation_capture':c}));return 0 if c['execution_status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())

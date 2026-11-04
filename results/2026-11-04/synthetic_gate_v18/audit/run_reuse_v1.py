"""Reuse all correctness captures; semantic gate then approved timing, no repair."""
import json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
import capture
from large_replay_v2 import sha
A=Path(__file__).resolve().parent;R=A.parent
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def main():
    start=time.perf_counter();plan=load(A/'REUSE_PLAN_V1.json');spent=load(Path(plan['prior_continuation'])/'closure.json')['total_active_seconds'];assert 0<spent<600
    freeze_path=A/'REUSE_FREEZE_V1.json';go=load(A/'REUSE_GO_V1.json');assert go['status']=='GO' and go['execution_freeze_sha256']==sha(freeze_path);frozen=load(freeze_path);binding=load(A/'BINDING_V1.json')
    def check():
        for p,h in frozen['sources'].items():assert sha(p)==h
    check();marker=A/'REUSE_STARTED_V1.json'
    with marker.open('x') as h:json.dump(dict(started_utc=datetime.now(timezone.utc).isoformat(),already_spent_seconds=spent,freeze_sha256=sha(freeze_path)),h)
    runs=A/'reuse_runs';assert not runs.exists() or not list(runs.iterdir());run=runs/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(parents=True)
    ledger=(run/'ledger.jsonl').open('x',encoding='utf8');sources=[Path(p) for p in frozen['sources']]+[freeze_path,A/'REUSE_GO_V1.json',marker]
    def log(e):ledger.write(json.dumps(e)+'\n');ledger.flush();os.fsync(ledger.fileno())
    def call(label,cmd,cap,entry,extra=(),reserve=125):
        check()
        if spent+time.perf_counter()-start+cap+reserve+2>600:log({**entry,'execution_status':'budget_unstarted'});return None
        result=capture.capture('c018_reuse_'+label,[sys.executable,'-B','-X','utf8',*map(str,cmd)],cwd=R,timeout_seconds=cap,source_paths=sources+list(extra));log({**entry,'attempt_id':result['attempt_id'],'execution_status':result['execution_status']})
        assert result['child_reaped'] and not result.get('cleanup_error') and not result.get('capture_error')
        print(json.dumps(dict(label=label,status=result['execution_status'],attempt_id=result['attempt_id'],total_active_seconds=spent+time.perf_counter()-start)),flush=True);return result
    c=call('small_gate',[A/'small_gate_v3.py',run],60,dict(kind='small_gate'))
    if c and c['execution_status']=='success' and load(run/'small_gate_report.json')['status']=='accepted_exact_small_gate':
        for ci,cell in enumerate(load(A/'CASE_MANIFEST_V1.json')['performance']):
            for rep in range(1,4):
                order=['baseline','candidate'] if (ci+rep)%2 else ['candidate','baseline']
                for provider in order:call(cell['case_id']+'_'+provider+'_r'+str(rep),[binding[provider]['cli'],cell['input'],'--seconds','5'],7,dict(kind='timing',provider=provider,case_id=cell['case_id'],rep=rep),extra=[Path(cell['input'])])
    extra=[run/'ledger.jsonl']
    if (run/'small_gate_report.json').exists():extra.append(run/'small_gate_report.json')
    c=call('final_validation',[A/'validate_continuation_v2.py',run],120,dict(kind='final_validation'),extra=extra,reserve=0);ledger.close()
    with (run/'closure.json').open('x') as h:json.dump(dict(prior_active_seconds=spent,reuse_active_seconds=time.perf_counter()-start,total_active_seconds=spent+time.perf_counter()-start,status='validation_success' if c and c['execution_status']=='success' else 'incomplete_or_rejected'),h,indent=2)
    return 0 if c and c['execution_status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())

"""Single authorized C018 launch; captures actual CLI timing, no retry."""
import hashlib,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
import capture
A=Path(__file__).resolve().parent;R=A.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    started=time.perf_counter();go=json.loads((A/'MASTER_GO_V1.json').read_text());f=A/'EXECUTION_FREEZE_V1.json'
    assert go['status']=='GO' and go['execution_freeze_sha256']==sha(f)
    freeze=json.loads(f.read_text());binding=json.loads((A/'BINDING_V1.json').read_text())
    def check():
        for p,h in freeze['sources'].items():assert sha(p)==h
    check()
    marker=A/'RUN_STARTED_V1.json'
    if (A/'runs').exists() and list((A/'runs').iterdir()):raise RuntimeError('existing run: observe; do not repeat')
    with marker.open('x') as handle:json.dump(dict(started_utc=datetime.now(timezone.utc).isoformat(),freeze_sha256=sha(f)),handle)
    run=A/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(parents=True)
    ledger=(run/'ledger.jsonl').open('x',encoding='utf8')
    sources=[Path(p) for p in freeze['sources']]+[f,A/'MASTER_GO_V1.json',marker]
    def log(row):ledger.write(json.dumps(row)+'\n');ledger.flush();os.fsync(ledger.fileno())
    def call(label,argv,cap,extra,entry,reserve=55):
        check()
        if time.perf_counter()-started+cap+reserve+2>600:
            log({**entry,'execution_status':'budget_unstarted'});return None
        result=capture.capture('c018_'+label,[sys.executable,'-B','-X','utf8',*map(str,argv)],cwd=R,timeout_seconds=cap,source_paths=sources+list(extra))
        log({**entry,'attempt_id':result['attempt_id'],'execution_status':result['execution_status']})
        assert result['child_reaped'] and not result.get('cleanup_error') and not result.get('capture_error')
        print(json.dumps(dict(label=label,status=result['execution_status'],attempt_id=result['attempt_id'],active_seconds=time.perf_counter()-started)),flush=True)
        return result
    c=call('prepare',[A/'prepare_v1.py'],20,[],dict(kind='preparation'));assert c and c['execution_status']=='success'
    m=json.loads((A/'CASE_MANIFEST_V1.json').read_text());extra=[A/'CASE_MANIFEST_V1.json',A/'ORACLES_V1.json']
    extra+=list({Path(j['input']) for j in m['jobs']})
    ok=True
    for provider in ['baseline','candidate']:
        c=call('correctness_'+provider,[A/'batch_v1.py',provider],50,extra,dict(kind='batch',provider=provider))
        if c is None or c['execution_status']!='success':ok=False;break
        records=[json.loads(x) for x in (A/'attempts'/c['attempt_id']/'stdout.bin').read_bytes().splitlines()]
        if len(records)!=len(m['jobs']) or any(not x.get('launched') or x.get('execution_error') or x['result']['status']=='unresolved' and not next(j for j in m['jobs'] if j['job_id']==x['job_id']).get('deadline_seconds')==0 for x in records):ok=False;break
    # Semantic acceptance is independently checked after all captures; a batch
    # error/incompleteness stops performance launches, not replays correctness.
    if ok:
        for ci,cell in enumerate(m['performance']):
            for rep in range(1,4):
                order=['baseline','candidate'] if (ci+rep)%2 else ['candidate','baseline']
                for provider in order:
                    cmd=[binding[provider]['cli'],cell['input'],'--seconds','5']
                    call(cell['case_id']+'_'+provider+'_r'+str(rep),cmd,7,[Path(cell['input'])],dict(kind='timing',provider=provider,case_id=cell['case_id'],rep=rep))
    ledger.close()
    # Validation gets reserved wall budget and never launches another provider.
    validation_sources=[run/'ledger.jsonl',A/'CASE_MANIFEST_V1.json',A/'ORACLES_V1.json']
    c=call('validate',[A/'validate_v1.py',run],50,validation_sources,dict(kind='validation'),reserve=0)
    # call() logs through ledger; keep it open until validation is appended.
    with (run/'closure.json').open('x') as out:json.dump(dict(active_seconds=time.perf_counter()-started,status='validation_success' if c and c['execution_status']=='success' else 'incomplete_or_rejected'),out)
    return 0 if c and c['execution_status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())

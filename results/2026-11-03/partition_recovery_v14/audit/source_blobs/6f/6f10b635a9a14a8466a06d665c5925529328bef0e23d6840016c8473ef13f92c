"""One bounded captured C014 audit; refuses execution before master GO/freeze."""
import hashlib,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
import capture
A=Path(__file__).resolve().parent;R=A.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    start=time.perf_counter();go=A/'MASTER_GO_V1.json';approval=json.loads(go.read_text());freeze=A/'EXECUTION_FREEZE_V1.json'
    assert approval['status']=='GO' and approval['execution_freeze_sha256']==sha(freeze)
    frozen=json.loads(freeze.read_text());sources=[Path(p) for p in frozen['sources']]+[freeze,go]
    def check():
        for p,h in frozen['sources'].items():assert sha(Path(p))==h
    check();run=A/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(parents=True);ledger=(run/'ledger.jsonl').open('x',encoding='utf-8')
    def call(label,cmd,cap,extra=(),entry=None):
        check();remaining=600-(time.perf_counter()-start);assert remaining>cap,'audit active budget cannot fit next job'
        result=capture.capture('c014_'+label,[sys.executable,'-B','-X','utf8',*map(str,cmd)],cwd=R,timeout_seconds=cap,source_paths=sources+list(extra))
        assert result['child_reaped'] and not result.get('cleanup_error') and not result.get('capture_error')
        if entry:
            ledger.write(json.dumps({**entry,'attempt_id':result['attempt_id']})+'\n');ledger.flush();os.fsync(ledger.fileno())
        print(json.dumps({'label':label,'attempt_id':result['attempt_id'],'execution_status':result['execution_status'],'elapsed':time.perf_counter()-start}),flush=True)
        return result
    r=call('data',[A/'build_data_v1.py'],45);assert r['execution_status']=='success'
    datafiles=list((A/'data').rglob('*.json'));r=call('oracles',[A/'verify_data_v1.py'],60,datafiles+[A/'DATA_MANIFEST_V1.json']);assert r['execution_status']=='success'
    manifest=json.loads((A/'DATA_MANIFEST_V1.json').read_text());extra=datafiles+[A/'DATA_MANIFEST_V1.json',A/'SMALL_ORACLES_V1.json',A/'HELD_ORACLES_V1.json']
    for method in ['baseline','new']:
        r=call('correctness_'+method,[A/'correctness_batch_v1.py','--method',method],45,extra,{'kind':'batch','method':method});assert r['execution_status']=='success'
    for c in manifest['small_cases']:
        if c['kind']!='calibration':continue
        world=json.loads(Path(c['world']).read_text())
        for k in [None,world['true_devices']]:
            cmd=[A/'recovery_certificate_v2.py',c['path']]+(['--known-k',str(k)] if k is not None else [])
            r=call('recovery_'+c['case_id']+'_'+str(k),cmd,3,extra,{'kind':'recovery','case_id':c['case_id'],'known_k':k});assert r['execution_status']=='success'
    audit_sources=extra+[run/'ledger.jsonl']
    for entry in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):audit_sources+=list((A/'attempts'/entry['attempt_id']).glob('*'))
    r=call('correctness_validation',[A/'check_results_v1.py',run],60,audit_sources);assert r['execution_status']=='success','correctness gate rejected; no timing launched'
    assert json.loads((run/'correctness_report.json').read_text())['status']=='accepted_correctness_and_recovery'
    assert all(c['exact_count_oracle'] for c in json.loads((A/'HELD_ORACLES_V1.json').read_text())['cases']),'fixed held-input oracle not established; do not substitute cells'
    bindings=json.loads((A/'BINDINGS_V1.json').read_text());planned=[]
    for rep in [1,2,3]:
        for c in manifest['timing_cases']:
            for method in (['baseline','new'] if rep!=2 else ['new','baseline']):planned.append((rep,c,method))
    for rep,c,method in planned:
        if time.perf_counter()-start+7+90+2>600:
            ledger.write(json.dumps({'kind':'timing','case_id':c['case_id'],'method':method,'rep':rep,'status':'budget_unstarted'})+'\n');ledger.flush();continue
        cli=bindings[method]['cli'];assert sha(Path(cli['path']))==cli['sha256']
        call(f'timing_{method}_{c["case_id"]}_{rep}',[cli['path'],c['path'],'--seconds','5'],7,extra+[run/'correctness_report.json'],{'kind':'timing','case_id':c['case_id'],'method':method,'rep':rep})
    ledger.close();final_sources=extra+[run/'ledger.jsonl',run/'correctness_report.json']
    for entry in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):
        if 'attempt_id' in entry:final_sources+=list((A/'attempts'/entry['attempt_id']).glob('*'))
    r=call('timing_validation',[A/'check_timing_v1.py',run],min(90,599-(time.perf_counter()-start)),final_sources)
    with (run/'closure.json').open('x') as out:json.dump({'status':'closed' if r['execution_status']=='success' else 'validation_failed_or_censored','active_seconds':time.perf_counter()-start,'last_capture':r,'budget_seconds':600},out,indent=2)
    print(json.dumps({'run':str(run),'validation_status':r['execution_status']}));return 0 if r['execution_status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())

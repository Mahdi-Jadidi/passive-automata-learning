"""Independent semantic gate BEFORE continuation timing; no solver import."""
import hashlib,json,sys,time
from pathlib import Path
from certificate_replay_c015_v2 import verify
A=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    run=Path(sys.argv[1]);began=time.perf_counter();old=load(A/'CONTINUATION_PLAN_V1.json')['original_baseline_attempt'];jobs={j['job_id']:j for j in load(A/'CASE_MANIFEST_V1.json')['jobs']};oracles={o['job_id']:o for o in load(A/'ORACLES_V1.json')['jobs']};errors=[]
    def captured(attempt):
        p=A/'attempts'/attempt;c=load(p/'result.json');assert c['child_reaped'] and c['execution_status']=='success' and c['exit_code']==0 and not c.get('cleanup_error')
        for stream in ['stdout','stderr']:assert sha(p/(stream+'.bin'))==c[stream+'_sha256']
        for s in load(p/'manifest.json')['sources']:assert sha(A/s['snapshot'])==s['sha256'] and sha(s['path'])==s['sha256']
        return [json.loads(x) for x in (p/'stdout.bin').read_bytes().splitlines()]
    baseline=captured(old);assert len(baseline)==len(jobs) and {x['job_id'] for x in baseline}==set(jobs)
    ledger=[json.loads(x) for x in (Path(load(A/'REUSE_PLAN_V1.json')['prior_continuation'])/'small_gate_input_ledger.jsonl').read_text().splitlines()]
    repair=next(x for x in ledger if x['kind']=='repair');candidate=next(x for x in ledger if x['kind']=='candidate_batch')
    replacement=captured(repair['attempt_id']);assert len(replacement)==1 and replacement[0]['job_id']=='c018_unicode_atomic'
    merged=[replacement[0] if x['job_id']=='c018_unicode_atomic' else x for x in baseline]
    new=captured(candidate['attempt_id']);assert len(new)==len(jobs) and {x['job_id'] for x in new}==set(jobs)
    checked=[]
    for provider,records in [('baseline',merged),('candidate',new)]:
        for record in records:
            try:
                assert record.get('launched') and not record.get('execution_error');jid=record['job_id'];job=jobs[jid];status=verify(job,record['result'],oracles.get(jid))
                assert status!='unresolved' or job['expectation']=='timeout'
                checked.append(dict(provider=provider,job_id=jid,status=status))
                if len(checked)%50==0:print(json.dumps(dict(progress='rows_checked',count=len(checked),provider=provider,errors=len(errors))),flush=True)
            except Exception as exc:errors.append(dict(provider=provider,job_id=record.get('job_id'),error=repr(exc)))
        print(json.dumps(dict(progress='small_provider_checked',provider=provider,checked=len(checked),errors=len(errors))),flush=True)
    report=dict(status='accepted_exact_small_gate' if not errors and len(checked)==2*len(jobs) else 'rejected_or_incomplete',checked_rows=len(checked),expected_rows=2*len(jobs),errors=errors,rows=checked,reused_baseline_rows=len(jobs)-1,targeted_replacement='c018_unicode_atomic',targeted_budget_seconds=2,small_gate_seconds=time.perf_counter()-began)
    with (run/'small_gate_report.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','checked_rows','expected_rows','errors','small_gate_seconds']}));return 0 if not errors and len(checked)==2*len(jobs) else 1
if __name__=='__main__':raise SystemExit(main())

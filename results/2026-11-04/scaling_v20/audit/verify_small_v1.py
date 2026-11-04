"""Independent exact small gate, durable progress; no provider imports."""
import json,sys,hashlib
from pathlib import Path
from certificate_replay_c015_v2 import verify
A=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    run=Path(sys.argv[1]);jobs={j['job_id']:j for j in read(A/'SMALL_MANIFEST_V1.json')['jobs']};oracles={o['job_id']:o for o in read(A/'SMALL_ORACLES_V1.json')['jobs']};errors=[];checked=[]
    for entry in map(json.loads,(run/'small_ledger_checkpoint.jsonl').read_text().splitlines()):
        if entry['kind']!='small_batch':continue
        p=A/'attempts'/entry['attempt_id'];cap=read(p/'result.json');assert cap['execution_status']=='success' and cap['exit_code']==0 and cap['child_reaped'] and not cap.get('cleanup_error');assert sha(p/'stdout.bin')==cap['stdout_sha256'];rows=[json.loads(x) for x in (p/'stdout.bin').read_bytes().splitlines()];assert len(rows)==len(jobs) and {r['job_id'] for r in rows}==set(jobs)
        for row in rows:
            try:
                jid=row['job_id'];assert row.get('launched') and not row.get('execution_error');status=verify(jobs[jid],row['result'],oracles.get(jid));assert status!='unresolved' or jobs[jid]['expectation']=='timeout';checked.append(dict(provider=entry['provider'],job_id=jid,status=status))
            except Exception as exc:errors.append(dict(provider=entry['provider'],job_id=row.get('job_id'),error=repr(exc)))
            if len(checked)%50==0:print(json.dumps(dict(progress='small_rows_checked',count=len(checked),errors=len(errors))),flush=True)
    expected=2*len(jobs);report=dict(status='accepted' if not errors and len(checked)==expected else 'rejected_or_incomplete',errors=errors,checked_rows=len(checked),expected_rows=expected,rows=checked)
    with (run/'small_report.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','errors','checked_rows','expected_rows']}));return 0 if report['status']=='accepted' else 1
if __name__=='__main__':raise SystemExit(main())

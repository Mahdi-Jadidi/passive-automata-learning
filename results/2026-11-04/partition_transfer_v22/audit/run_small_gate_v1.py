"""Run and durably verify baseline and C022 on the frozen 1,710-job gate."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import capture
A=Path(__file__).resolve().parent
R=A.parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    freeze=read(A/'SOURCE_INPUT_FREEZE_V1.json')
    for entry in freeze['frozen_files']:
        assert sha(entry['path'])==entry['sha256'],entry['path']
    for entry in freeze['audit_tools']:
        assert sha(entry['path'])==entry['sha256'],entry['path']
    assert sha(A/'small_batch_v1.py')==freeze['small_batch_sha256']
    assert sha(A/'run_small_gate_v1.py')==freeze['runner_sha256']
    run=A/'small_runs'/freeze['run_id'];run.mkdir(parents=True,exist_ok=False)
    ledger=[]
    sources=[A/'small_batch_v1.py',A/'BINDING_V1.json',A/'SMALL_MANIFEST_V2.json',A/'SMALL_ORACLES_V2.json',A/'capture.py',A/'verify_small_v3.py',A/'certificate_replay_c015_v2.py',A/'oracle_data_v1.py',A/'SOURCE_INPUT_FREEZE_V1.json']
    sources += [Path(x['path']) for x in freeze['small_inputs']]
    for provider in ['baseline_c2','transfer']:
        result=capture.capture('c022_'+freeze['run_id']+'_small_'+provider,[sys.executable,'-B','-X','utf8',str(A/'small_batch_v1.py'),provider],cwd=R,timeout_seconds=50,source_paths=sources)
        ledger.append({'kind':'small_batch','provider':provider,'attempt_id':result['attempt_id'],'execution_status':result['execution_status'],'exit_code':result['exit_code']})
        if result['execution_status']!='success' or result['exit_code']!=0:raise SystemExit('small batch process incomplete; raw capture retained')
    (run/'ledger.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ledger),encoding='utf-8')
    (run/'small_ledger_checkpoint.jsonl').write_bytes((run/'ledger.jsonl').read_bytes())
    result=capture.capture('c022_'+freeze['run_id']+'_small_verify',[sys.executable,'-B','-X','utf8',str(A/'verify_small_v3.py'),str(run)],cwd=R,timeout_seconds=90,source_paths=sources+[run/'small_ledger_checkpoint.jsonl'])
    if result['execution_status']!='success' or result['exit_code']!=0:raise SystemExit('independent certificate replay failed; raw capture retained')
    report=read(run/'small_report.json')
    print(json.dumps({'run_id':freeze['run_id'],'attempts':ledger,'verify_attempt_id':result['attempt_id'],'report_status':report['status'],'checked_rows':report['checked_rows'],'expected_rows':report['expected_rows'],'errors':len(report['errors'])},ensure_ascii=False))
    return 0 if report['status']=='accepted' else 1
if __name__=='__main__':raise SystemExit(main())

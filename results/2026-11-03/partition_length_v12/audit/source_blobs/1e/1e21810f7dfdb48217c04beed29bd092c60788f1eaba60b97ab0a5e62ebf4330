"""Frozen serial paired CLI comparison and separate traced-memory probes."""
import hashlib, json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone
import capture
A=Path(__file__).resolve().parent
R=A.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=A/'PERFORMANCE_FREEZE_V1.json'
    frozen=json.loads(freeze.read_text())
    sources=[Path(p) for p in frozen['sources']]+[freeze]
    def check():
        for p,h in frozen['sources'].items():
            if sha(Path(p))!=h: raise RuntimeError('source drift: '+p)
    check()
    go=json.loads((A/'MASTER_GO_V1.json').read_text())
    assert go['status']=='GO' and go['performance_authorized'] and go['baseline_runs_authorized'] and go['candidate_runs_authorized']
    bind=json.loads((A/'CANDIDATE_BINDING_V1.json').read_text())
    assert sha(A/'CANDIDATE_BINDING_V1.json')==go['candidate_binding_sha256']
    for v in bind.values():
        if isinstance(v,dict) and 'sha256' in v: assert sha(R/v['path'])==v['sha256']
    cells=json.loads((A/'PERFORMANCE_MANIFEST_V2.json').read_text())['cells']
    base=R.parent.parent/'2026-11-02/partition_unrestricted_v10/implementation'
    methods={'baseline':(base/'unrestricted_solver_v2.py',base/'unrestricted_cli_v2.py'),'candidate':(R/bind['solver']['path'],R/bind['cli']['path'])}
    run=A/'performance_runs_v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(parents=True)
    jobs=[]
    for rep in range(1,4):
        for c in cells:
            for m in (('baseline','candidate') if rep!=2 else ('candidate','baseline')): jobs.append({'kind':'timing','rep':rep,'case_id':c['case_id'],'method':m})
    for c in cells:
        if not c['memory_probe']: continue
        for m in methods: jobs.append({'kind':'memory','rep':1,'case_id':c['case_id'],'method':m})
    (run/'plan.json').write_text(json.dumps(jobs,indent=2))
    used={m:0.0 for m in methods}
    for p in (A/'attempts').glob('*/result.json'):
        v=json.loads(p.read_text()); label=v.get('label','')
        for m in methods:
            if label.startswith(('c012_'+m+'_cli_','c012_memory_'+m+'_')): used[m]+=v['duration_seconds']
    with (run/'ledger.jsonl').open('x',encoding='utf-8') as ledger:
        for i,j in enumerate(jobs):
            check(); c=next(c for c in cells if c['case_id']==j['case_id']); inp=A/c['path']; m=j['method']; solver,cli=methods[m]
            cap=30 if j['kind']=='timing' else 20
            limit=760 if j['kind']=='timing' else 900
            row=dict(j)
            if used[m]+cap+2>limit: row['status']='budget_censored_before_launch'
            else:
                side=run/f'memory_result_{i}.json'
                cmd=([sys.executable,'-B','-X','utf8',str(cli),str(inp),'--seconds','28'] if j['kind']=='timing' else [sys.executable,'-B','-X','utf8',str(A/'memory_probe_v2.py'),'--input',str(inp),'--solver',str(solver),'--result-output',str(side)])
                label=(f'c012_{m}_cli_' if j['kind']=='timing' else f'c012_memory_{m}_')+c['case_id']+f'_rep{j["rep"]}'
                result=capture.capture(label,cmd,cwd=R,timeout_seconds=cap,source_paths=sources)
                used[m]+=result['duration_seconds']; row.update({'attempt_id':result['attempt_id'],'capture':result})
                if j['kind']=='memory' and side.exists(): row['sidecar']={'path':str(side),'sha256':sha(side)}
                if not result['child_reaped'] or result.get('cleanup_error') or result.get('capture_error') or result['execution_status']=='interrupted': raise RuntimeError('capture supervision failure')
            ledger.write(json.dumps(row)+'\n'); ledger.flush(); os.fsync(ledger.fileno())
            print(json.dumps({'done':i+1,'planned':len(jobs),'used_seconds':used}),flush=True)
    (run/'budget.json').write_text(json.dumps(used,indent=2))
    validation_sources=sources+list(run.glob('*'))
    for row in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):
        if 'attempt_id' in row: validation_sources+=list((A/'attempts'/row['attempt_id']).glob('*'))
    result=capture.capture('c012_performance_validation_v2',[sys.executable,'-B','-X','utf8',str(A/'validate_performance_v2.py'),str(run)],cwd=R,timeout_seconds=180,source_paths=validation_sources)
    (run/'validation_capture.json').write_text(json.dumps(result,indent=2)); print(json.dumps({'run':str(run),'validation':result}),flush=True)
    return 0 if result['execution_status']=='success' else 1
if __name__=='__main__': sys.exit(main())

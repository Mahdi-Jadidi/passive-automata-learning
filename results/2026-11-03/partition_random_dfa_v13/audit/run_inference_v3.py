"""Gated controls or budgeted first-pass-priority 240-cell C010 sweep."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import capture
from active_budget_v2 import Budget
BUDGET=None
A=Path(__file__).resolve().parent;R=A.parent
C=R.parent.parent/'2026-11-02/partition_unrestricted_v10/implementation'
def main():
    global BUDGET
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['controls','grid'],required=True);a=ap.parse_args();BUDGET=Budget('inference',a.phase)
    freeze=json.loads((A/'EXECUTION_FREEZE_V3.json').read_text());sources=[Path(p) for p in freeze['sources']]
    def check():
        for p,h in freeze['sources'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    check();go=A/('STATIC_GATE_GO_V2.json' if a.phase=='controls' else 'MASTER_GRID_GO_V3.json')
    approval=json.loads(go.read_text());assert approval['status']=='GO'
    assert approval['controls_authorized'] if a.phase=='controls' else approval['grid_authorized']
    assert hashlib.sha256((A/'EXECUTION_FREEZE_V3.json').read_bytes()).hexdigest()==approval['execution_freeze_sha256']
    if a.phase=='grid':assert json.loads((A/'SMALL_CONTROL_ACCEPTANCE_V3.json').read_text())['status']=='accepted_exact_full_sets'
    jobs=[]
    if a.phase=='controls':
        for k in range(1,5):
            for L in [8,64]:jobs.append((k,2*k,L,2,1,'control'))
    else:
        basic=[(k,40,L,n) for L in [8,64,512,4096,65536,1000000] for n in [2,8] for k in range(1,21)]
        jobs=[(*x,1,'broad') for x in basic]+[(k,40,1000000,8,1,'confirmation') for k in [1,20]]+ [(*x,rep,'broad') for rep in [2,3] for x in basic]
    # Charge previous captured active work, not time waiting for inter-phase GO.
    ledger=A/f'{a.phase}_inference_ledger_v3.jsonl'
    with ledger.open('x',encoding='utf-8') as f:
        for k,m,L,n,rep,kind in jobs:
            check();directory=A/'data'/a.phase/f'K{k}_M{m}_L{L}';inp=directory/f'input{n}.json';world=directory/'world.json'
            row={'K':k,'m':m,'max_length':L,'samples_per_label':n,'rep':rep,'kind':kind,'input':str(inp),'world':str(world)}
            hard=22 if kind=='confirmation' else 7;seconds=20 if kind=='confirmation' else 5
            if not inp.exists():row['status']='preparation_failed_unstarted'
            elif BUDGET.used()+hard+2+180>2700:row['status']='budget_unstarted'
            else:
                cmd=[sys.executable,'-B','-X','utf8',str(C/'unrestricted_cli_v2.py'),str(inp),'--seconds',str(seconds)]
                if a.phase=='controls':cmd.append('--enumerate')
                result=capture.capture(f'c013_{a.phase}_K{k}_L{L}_n{n}_{kind}_rep{rep}',cmd,cwd=R,timeout_seconds=hard,source_paths=sources+[go,inp,world,directory/'validation.json'])
                row.update({'attempt_id':result['attempt_id'],'status':result['execution_status']})
                if not result['child_reaped'] or result.get('cleanup_error'):raise RuntimeError('capture supervision failure')
            f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno());print(json.dumps(row),flush=True)
    validation_sources=sources+[ledger,go]
    for row in map(json.loads,ledger.read_text().splitlines()):
        if 'attempt_id' in row: validation_sources+=list((A/'attempts'/row['attempt_id']).glob('*'))+[Path(row['input']),Path(row['world'])]
    validation=capture.capture('c013_'+a.phase+'_independent_validation',[sys.executable,'-B','-X','utf8',str(A/'validate_results_v3.py'),str(ledger),a.phase],cwd=R,timeout_seconds=min(180,max(1,2700-BUDGET.used())),source_paths=validation_sources)
    print(json.dumps(validation));return 0 if validation['execution_status']=='success' else 1
if __name__=='__main__':
    try:sys.exit(main())
    finally:
        if BUDGET is not None:BUDGET.close()

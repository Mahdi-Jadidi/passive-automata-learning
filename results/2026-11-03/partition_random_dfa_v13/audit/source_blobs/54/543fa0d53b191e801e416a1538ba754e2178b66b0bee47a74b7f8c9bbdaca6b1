"""Resource-only captured continuation; never regenerate successful V3 cells."""
import hashlib,json,os,sys
from pathlib import Path
import capture
from active_budget_v2 import Budget
A=Path(__file__).resolve().parent;R=A.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(budget):
    go=A/'MASTER_RESOURCE_GO_V4.json';approval=json.loads(go.read_text());assert approval['status']=='GO' and approval['preparation_seconds']==1800 and approval['total_seconds']==4500
    freeze=A/'EXECUTION_FREEZE_V4.json';assert sha(freeze)==approval['execution_freeze_sha256'];frozen=json.loads(freeze.read_text());sources=list(map(Path,frozen['sources']))
    def check():
        for p,h in frozen['sources'].items():assert sha(Path(p))==h
    check();previous=list(map(json.loads,(A/'grid_preparation_ledger_v3.jsonl').read_text().splitlines()))
    assert (A/'grid_preparation_active_budget_v2.json').exists(),'V3 phase must finish naturally before continuation'
    successful={(r['K'],r['max_length']):r for r in previous if r['status']=='success'}
    expected=[(k,L) for L in [8,64,512,4096,65536,1000000] for k in range(1,21)]
    entries={}
    def register(k,L,directory):
        v=json.loads((directory/'validation.json').read_text());assert v['status']=='independent_labels_and_nesting_passed'
        assert sha(directory/'input8.json')==v['input8_sha256'] and sha(directory/'input2.json')==v['input2_sha256']
        entries[f'{k}:{L}']={'directory':str(directory),'input8_sha256':v['input8_sha256'],'input2_sha256':v['input2_sha256'],'world_sha256':sha(directory/'world.json')}
    for (k,L),row in successful.items():register(k,L,Path(row['output']))
    ledger=A/'grid_preparation_resume_ledger_v4.jsonl'
    with ledger.open('x',encoding='utf-8') as out:
        for k,L in expected:
            if (k,L) in successful:continue
            check();directory=A/'data/grid_resume_v4'/f'K{k}_M40_L{L}'
            remaining=min(1800-budget.preparation_used(),4500-budget.used());row={'K':k,'m':40,'max_length':L,'output':str(directory)}
            if remaining<=2:row['status']='preparation_budget_unstarted'
            else:
                result=capture.capture(f'c013_resume_prepare_K{k}_L{L}',[sys.executable,'-B','-X','utf8',str(A/'prepare_case_v1.py'),'--k',str(k),'--m','40','--length',str(L),'--out',str(directory)],cwd=R,timeout_seconds=min(90,remaining),source_paths=sources+[freeze,go,A/'grid_preparation_ledger_v3.jsonl'])
                row.update({'status':result['execution_status'],'attempt_id':result['attempt_id']})
                assert result['child_reaped'] and not result.get('cleanup_error')
            out.write(json.dumps(row)+'\n');out.flush();os.fsync(out.fileno());print(json.dumps(row),flush=True)
            if row['status']!='success':raise RuntimeError('continuation failed; preserved partial files and raw capture')
            register(k,L,directory)
    assert len(entries)==120
    with (A/'GRID_INPUT_MAP_V4.json').open('x') as out:json.dump({'entries':entries,'previous_successes_reused':len(successful),'total_parent_inputs':120,'total_solver_cells':240},out,indent=2)
if __name__=='__main__':
    budget=Budget('preparation','grid_resume_v4')
    try:main(budget)
    finally:budget.close()

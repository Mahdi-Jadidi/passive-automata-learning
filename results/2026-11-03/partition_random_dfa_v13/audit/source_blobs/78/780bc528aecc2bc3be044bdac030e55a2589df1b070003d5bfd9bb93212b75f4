"""Gated captured eight-control or 120-parent/240-input preparation."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
sys.path.insert(0,str(A))
import capture
from active_budget_v2 import Budget
BUDGET=None
def main():
    global BUDGET
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['controls','grid'],required=True);a=ap.parse_args();BUDGET=Budget('preparation',a.phase)
    go=json.loads((A/'STATIC_GATE_GO_V2.json').read_text());assert go['status']=='GO' and go['generation_authorized'] is True
    assert hashlib.sha256((A/'EXECUTION_FREEZE_V2.json').read_bytes()).hexdigest()==go['execution_freeze_sha256']
    freeze=json.loads((A/'EXECUTION_FREEZE_V2.json').read_text());sources=[Path(p) for p in freeze['sources']]
    for p,h in freeze['sources'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    if a.phase=='grid':
        gate=json.loads((A/'SMALL_CONTROL_ACCEPTANCE_V2.json').read_text());assert gate['status']=='accepted_exact_full_sets'
    jobs=[(k,2*k,L) for k in range(1,5) for L in [8,64]] if a.phase=='controls' else [(k,40,L) for L in [8,64,512,4096,65536,1000000] for k in range(1,21)]
    ledger=A/f'{a.phase}_preparation_ledger_v2.jsonl'
    with ledger.open('x',encoding='utf-8') as f:
        for k,m,L in jobs:
            remaining=min(720-BUDGET.preparation_used(),2700-BUDGET.used());out=A/'data'/a.phase/f'K{k}_M{m}_L{L}'
            row={'K':k,'m':m,'max_length':L,'output':str(out)}
            if remaining<=2:row['status']='preparation_budget_unstarted'
            else:
                cmd=[sys.executable,'-B','-X','utf8',str(A/'prepare_case_v1.py'),'--k',str(k),'--m',str(m),'--length',str(L),'--out',str(out)]
                if a.phase=='controls':cmd.append('--small')
                result=capture.capture(f'c013_prepare_{a.phase}_K{k}_L{L}',cmd,cwd=R,timeout_seconds=min(90,remaining),source_paths=sources+[A/'EXECUTION_FREEZE_V2.json',A/'STATIC_GATE_GO_V2.json'])
                row.update({'status':result['execution_status'],'attempt_id':result['attempt_id']})
                if not result['child_reaped'] or result.get('cleanup_error'):raise RuntimeError('capture supervision failure')
            f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
            print(json.dumps(row),flush=True)
            if row['status']!='success':raise RuntimeError('preparation failed; preserved ledger/raw output; report before changing inputs')
if __name__=='__main__':
    try:main()
    finally:
        if BUDGET is not None:BUDGET.close()

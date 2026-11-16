"""Replay the frozen corpus under an explicit budget; incomplete is NOT a pass."""
from pathlib import Path
import hashlib,json,time
from collections import Counter
from optimizer import solve_profiled
from verify import verify_optimal
HERE=Path(__file__).resolve().parent

def main():
    source=HERE.parent/'exact_optimizer_v43/audit_raw.jsonl'
    rows=[json.loads(line) for line in source.read_text().splitlines()]
    counts=Counter();started=time.perf_counter()
    with (HERE/'corpus_audit.jsonl').open('x',encoding='utf-8') as out:
        for row in rows:
            profile=solve_profiled(row['input'],{'timeout_seconds':0.03})
            result=profile['result'];status=result['status'];counts[status]+=1
            checked=None;ok=None
            if status in ('OPTIMAL','INFEASIBLE'):
                checked=verify_optimal(row['input'],result,{'timeout_seconds':2})
                ok=checked=={'status':'ACCEPT'} and result['max_devices']==row['expected_k']
                # The frozen reference uses null for infeasible optima.
                assert ok,(row['i'],result,row['expected_k'],checked)
            else:
                assert status=='INCOMPLETE'
                assert all(result[key] is None for key in ('blocks','max_devices','certificate'))
            out.write(json.dumps({'i':row['i'],'input':row['input'],'reference_k':row['expected_k'],
                                  'profile':profile,'checked':checked,'completed_result_matches_reference':ok})+'\n')
            out.flush()
            if (row['i']+1)%200==0:print(json.dumps({'processed':row['i']+1,'counts':dict(counts)}),flush=True)
    summary={'cases':len(rows),'per_case_seconds':0.03,'statuses':dict(counts),
             'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'wall_seconds':time.perf_counter()-started,'incomplete_is_success':False}
    (HERE/'corpus_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
if __name__=='__main__':main()

"""Explicit theorem family, not field data; sources stay frozen."""
import sys,json,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'results/2026-11-16/exact_optimizer_v43'))
from optimizer import solve_profiled
from verify import verify_optimal
def main():
    with (HERE/'structural_family_raw.jsonl').open('x',encoding='utf8') as f:
        for m in [2,3,4,8,16,32,64,128,256]:
            D={'alphabet':['a','b']+['unused_'+str(i) for i in range(m-2)],'positive':[['a','b']],'negative':[['b','a']]}
            start=time.perf_counter();profile=solve_profiled(D,{'timeout_seconds':60});elapsed=time.perf_counter()-start
            r=profile['result'];checked=verify_optimal(D,r,{'timeout_seconds':60})
            ok=r['status']=='OPTIMAL' and r['max_devices']==m-1 and r['certificate']=={'type':'atom_bound'} and checked=={'status':'ACCEPT'}
            f.write(json.dumps({'m':m,'input':D,'profile':profile,'checked':checked,'seconds':elapsed,'pass':ok})+'\n');f.flush()
            assert ok,(m,r,checked)
            print(m,r['max_devices'],round(elapsed,6),flush=True)
if __name__=='__main__':main()

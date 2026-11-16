"""Fresh-process, same-budget comparison; stores incomplete outcomes verbatim."""
from pathlib import Path
import argparse,json,subprocess,sys,time,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def worker(method,D,seconds):
    folder=HERE if method=='v45' else HERE.parent/'exact_optimizer_v43'
    sys.path.insert(0,str(folder))
    from optimizer import solve_profiled
    from verify import verify_optimal
    start=time.perf_counter();profile=solve_profiled(D,{'timeout_seconds':seconds})
    result=profile['result'];checked=None
    if result['status'] in ('OPTIMAL','INFEASIBLE'):
        checked=verify_optimal(D,result,{'timeout_seconds':seconds})
        assert checked=={'status':'ACCEPT'}
    print(json.dumps({'method':method,'input':D,'profile':profile,'checked':checked,
                      'pipeline_plus_consumer_seconds':time.perf_counter()-start}),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',choices=['v43','v45']);parser.add_argument('--seconds',type=float,default=1);parser.add_argument('--input')
    args=parser.parse_args()
    if args.worker:return worker(args.worker,json.loads(args.input),args.seconds)
    fixed=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
    cases=[json.loads(line) for line in fixed.read_text().splitlines()]
    with (HERE/'benchmark_raw.jsonl').open('x',encoding='utf-8') as out:
        for repeat in range(3):
            for case in cases:
                for method in (['v43','v45'] if repeat%2==0 else ['v45','v43']):
                    command=[sys.executable,str(Path(__file__).resolve()),'--worker',method,'--seconds','1','--input',json.dumps(case['input'])]
                    run=subprocess.run(command,capture_output=True,text=True,timeout=12,check=True)
                    row=json.loads(run.stdout);row.update(case=case.get('name',case.get('case')),repeat=repeat,limit_seconds=1,source_sha256=hashlib.sha256(fixed.read_bytes()).hexdigest())
                    out.write(json.dumps(row)+'\n');out.flush()
                    print(json.dumps({'case':row['case'],'repeat':repeat,'method':method,'status':row['profile']['result']['status']}),flush=True)
    # A longer, explicitly separate interaction example, including the teacher cost.
    D={'alphabet':['a','b','c'],'positive':[['c','b','a']],'negative':[['a','b','c'],['b','a','c']]}
    run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker','v45','--seconds','30','--input',json.dumps(D)],capture_output=True,text=True,timeout=40,check=True)
    row=json.loads(run.stdout)
    (HERE/'interaction_example.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({'interaction_status':row['profile']['result']['status'],'cuts':row['profile']['metrics']['cuts']}),flush=True)
if __name__=='__main__':main()

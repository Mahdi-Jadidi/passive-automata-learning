"""Summarize already-recorded trials; preserve all observations and censoring."""
import collections,hashlib,json,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
raw=H/'timing_raw.jsonl'; data=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines()]
cases=[json.loads(x) for x in (H/'timing_cases.jsonl').read_text(encoding='utf-8').splitlines()]
solvers=['C028','C030','DP','GRAPH']; summary=[]
for case in cases:
    rows=[x for x in data if x['case']==case['case']]
    successful=[x for x in rows if x['status']=='OK' and x['result'].get('status') in ('AMBIGUOUS','UNIQUE_COMPATIBLE','INCOMPATIBLE')]
    distinct={json.dumps(x['result'],sort_keys=True,ensure_ascii=False) for x in successful}
    agreement=len(distinct)==1 and len(successful)>0
    entry={'case':case['case'],'purpose':case['purpose'],'outputs_agree':agreement,'solvers':{}}
    if agreement:
        result=successful[0]['result']; entry['result']={k:result[k] for k in ['status','compatible_count','max_blocks','optimal_count']}
    for solver in solvers:
        rs=[x for x in rows if x['solver']==solver]
        good=[x for x in rs if x in successful]
        values=[x['solve_ns']/1e9 for x in good]
        starts=[x['startup_wall_ns']/1e9 for x in good]
        entry['solvers'][solver]={'statuses':[x['status'] if x not in good else 'COMPLETE' for x in rs],'solve_seconds':values,'startup_seconds':starts,'median_solve_seconds':statistics.median(values) if agreement and len(rs)==len(good)==3 else None,'median_startup_seconds':statistics.median(starts) if agreement and len(rs)==len(good)==3 else None}
    summary.append(entry)
result={'status':'complete' if len(data)==len(cases)*len(solvers)*3 else 'partial','raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'trial_count':len(data),'case_count':len(cases),'output_mismatches':[e['case'] for e in summary if not e['outputs_agree']],'cases':summary}
(H/'timing_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'trial_count':len(data),'case_count':len(cases),'output_mismatches':result['output_mismatches'],'raw_sha256':result['raw_sha256']}))

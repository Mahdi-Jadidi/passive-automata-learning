"""Summarize hybrid trials separately from earlier sequential baseline run."""
import hashlib,json,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
raw=H/'hybrid_timing_raw.jsonl'; data=[json.loads(x) for x in raw.read_text(encoding='utf8').splitlines()]
prior=json.loads((H/'timing_summary.json').read_text(encoding='utf8'))
routes={x['case']:x['route'] for x in json.loads((H/'hybrid_routes_stdout.json').read_text(encoding='utf-8-sig'))['cases']}
assert len(data)==30 and len({(x['case'],x['repeat']) for x in data})==30
out=[]
for c in prior['cases']:
    r=[x for x in data if x['case']==c['case']]
    assert len(r)==3
    good=[x for x in r if x['status']=='OK' and x['matches_prior_c028'] and x['result']['status'] in ('UNIQUE_COMPATIBLE','AMBIGUOUS','INCOMPATIBLE')]
    row={'case':c['case'],'route':routes[c['case']],'statuses':[x['status'] for x in r],'matching_prior':len(good),'solve_seconds':[x['solve_ns']/1e9 for x in good],'startup_seconds':[x['startup_wall_ns']/1e9 for x in good]}
    row['median_solve_seconds']=statistics.median(row['solve_seconds']) if len(good)==3 else None
    row['median_startup_seconds']=statistics.median(row['startup_seconds']) if len(good)==3 else None
    row['earlier_run_medians_solve_seconds']={name:values['median_solve_seconds'] for name,values in c['solvers'].items()}
    out.append(row)
doc={'case_count':len(out),'trial_count':len(data),'complete_matching_trials':sum(x['matching_prior'] for x in out),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'comparison_caveat':'hybrid run followed earlier four-solver run; no contemporaneous randomization','cases':out}
(H/'hybrid_timing_summary.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(doc,ensure_ascii=False))

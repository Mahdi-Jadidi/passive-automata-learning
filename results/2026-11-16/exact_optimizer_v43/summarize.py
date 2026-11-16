"""Read-only integrity, trial identity and median recomputation."""
from pathlib import Path
import json,statistics,hashlib,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    records=[json.loads(line) for line in (HERE/'benchmark_raw.jsonl').read_text().splitlines()]
    metadata=records[0]['metadata'];trials=records[1:]
    for name,expected in metadata['sources'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    corpus=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
    assert hashlib.sha256(corpus.read_bytes()).hexdigest()==metadata['corpus_sha256']
    assert len(trials)==120 and len({(t['case'],t['repeat'],t['method']) for t in trials})==120
    assert all(t['status']=='OPTIMAL' and t['checked']=={'status':'ACCEPT'} for t in trials)
    summary=[]
    for name in dict.fromkeys(t['case'] for t in trials):
        case=[t for t in trials if t['case']==name]
        assert len({t['result']['max_devices'] for t in case})==1
        row={'case':name,'k':case[0]['result']['max_devices'],'methods':{}}
        for method in ['enumeration','dp','v42','v43']:
            items=[t for t in case if t['method']==method]
            assert {t['repeat'] for t in items}=={0,1,2}
            row['methods'][method]={key:statistics.median(t[key] for t in items) for key in ['total_seconds','solve_seconds','verify_seconds','peak_working_set_bytes','startup_wall_seconds']}
        summary.append(row)
    audit=[json.loads(line) for line in (HERE/'audit_raw.jsonl').read_text().splitlines()]
    assert len(audit)==2261 and all(t['pass'] and t['mining_matches_exhaustive'] for t in audit)
    print(json.dumps({'verified_trials':len(trials),'verified_audit_cases':len(audit),'summary':summary},indent=2))
if __name__=='__main__':main()

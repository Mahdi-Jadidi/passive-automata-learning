"""Final continuation audit, cached witness/world replay with durable progress."""
import json,statistics,sys,time
from pathlib import Path
from large_replay_v1 import Replay,sha
A=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def main():
    start=time.perf_counter();run=Path(sys.argv[1]);m=load(A/'CASE_MANIFEST_V1.json');cells={x['case_id']:x for x in m['performance']};ledger=[json.loads(x) for x in (run/'ledger.jsonl').read_text().splitlines()];replay=Replay();rows=[];errors=[];used=set();small=None
    for e in ledger:
        try:
            if e.get('execution_status')=='budget_unstarted':
                if e['kind']=='timing':rows.append({**e,'validated_status':'budget_unstarted'})
                continue
            p=A/'attempts'/e['attempt_id'];cap=load(p/'result.json');assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
            for stream in ['stdout','stderr']:assert sha(p/(stream+'.bin'))==cap[stream+'_sha256']
            for src in load(p/'manifest.json')['sources']:assert sha(A/src['snapshot'])==src['sha256'] and sha(src['path'])==src['sha256']
            if e['kind']=='small_gate':
                assert cap['execution_status']=='success' and cap['exit_code']==0;small=load(run/'small_gate_report.json');assert small['status']=='accepted_exact_small_gate' and small['checked_rows']==2*len(m['jobs']) and not small['errors']
            if e['kind']!='timing':continue
            cell=cells[e['case_id']];used.add(cell['case_id'])
            if cap['execution_status']=='timed_out':rows.append({**e,'validated_status':'hard_timeout'});continue
            result=json.loads((p/'stdout.bin').read_bytes());assert result['input_sha256']==cell['input_sha256'];status=replay.result(cell,result);assert cap['exit_code']==(3 if status=='unresolved' else 0)
            rows.append({**e,'validated_status':status,'subprocess_seconds':cap['subprocess_seconds'],'pipeline_seconds':result['input_and_solver_seconds'],'provider_seconds':result['metrics']['solver_seconds'],'metrics':result['metrics'],'stdout_bytes':cap['stdout_bytes']})
            print(json.dumps(dict(progress='timing_capture_checked',case_id=e['case_id'],provider=e['provider'],rep=e['rep'],status=status,elapsed=time.perf_counter()-start)),flush=True)
        except Exception as exc:errors.append(dict(entry=e,error=repr(exc)))
    truths=[]
    for cid in sorted(used):
        try:
            truths.append(replay.world(cells[cid]));print(json.dumps(dict(progress='world_replayed_once',case_id=cid,elapsed=time.perf_counter()-start)),flush=True)
        except Exception as exc:errors.append(dict(case_id=cid,error=repr(exc)))
    expected={(c,p,r) for c in cells for p in ['baseline','candidate'] for r in [1,2,3]};observed=[(r['case_id'],r['provider'],r['rep']) for r in rows]
    if small is not None and (len(observed)!=len(set(observed)) or set(observed)!=expected):errors.append(dict(error='timing semantic job set missing/duplicate/extra',expected=48,observed=len(observed)))
    timings=[]
    for cid in cells:
        record=dict(case_id=cid,providers={})
        for p in ['baseline','candidate']:
            rr=[r for r in rows if r['case_id']==cid and r['provider']==p];complete=[r for r in rr if r['validated_status'] in ['ambiguous','certified_unique']]
            record['providers'][p]=dict(observed=len(rr),complete=len(complete),statuses=[r['validated_status'] for r in rr],median_subprocess_seconds=statistics.median(r['subprocess_seconds'] for r in complete) if len(complete)==3 else None,median_pipeline_seconds=statistics.median(r['pipeline_seconds'] for r in complete) if len(complete)==3 else None,median_provider_seconds=statistics.median(r['provider_seconds'] for r in complete) if len(complete)==3 else None)
        b,c=[record['providers'][p]['median_subprocess_seconds'] for p in ['baseline','candidate']];record['baseline_over_candidate_subprocess_ratio']=b/c if b is not None and c is not None else None;timings.append(record)
    accepted=small is not None and not errors and len(truths)==len(used)
    report=dict(status='accepted_with_censoring' if accepted else 'rejected_or_incomplete',errors=errors,small_gate_status=None if small is None else small['status'],small_checked_rows=0 if small is None else small['checked_rows'],planned_timing_rows=48,timing_rows=len(rows),timings=timings,truths=truths,rows=rows,validation_seconds=time.perf_counter()-start,limits=['m40 complete ambiguity certified by two exact witnesses, not full-family enumeration','world truth checked after inference, never solver input','original first pass and censoredUnicode preserved; onlythatbaselinecase reexecuted at2s','unattempted cases do not trigger irrelevant world replay'])
    with (run/'validation_report.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','errors','small_checked_rows','timing_rows','validation_seconds']}),flush=True);return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())

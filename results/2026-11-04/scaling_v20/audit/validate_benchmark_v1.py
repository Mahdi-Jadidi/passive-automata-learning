"""C020 independent compact-witness/certificate replay with ordered caches."""
import json,sys,hashlib,statistics,time
from pathlib import Path
from certificate_replay_c015_v2 import witness,canonical,certificate
A=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.perf_counter();run=Path(sys.argv[1]);manifest=read(A/'FIXTURE_MANIFEST_V1.json');fixtures={f['case_id']:f for f in manifest['inputs']};audits={f['case_id']:f for f in read(A/'FIXTURE_AUDIT_V1.json')['fixtures']};cells={c['cell_id']:c for c in manifest['cells']};data={};errors=[];rows=[];gate=read(run/'small_report.json');assert gate['status']=='accepted' and not gate['errors'];providers=list(read(A/'BINDING_V1.json'))
    def check_result(cell,result):
        case=cell['case_id'];f=fixtures[case]
        if case not in data:assert sha(f['input'])==f['input_sha256'];data[case]=read(f['input'])
        d=data[case];expected='certified_unique' if cell['known_k'] is not None else 'ambiguous';status=result['status'];assert result['known_k']==cell['known_k'] and result['physical_truth_read'] is False and ('partition' in result)==(status=='certified_unique')
        if status=='unresolved':assert result['findings']==dict(data_insufficient=None,computation_incomplete=True) and 'alternatives' not in result;return status
        assert status==expected and result['findings']==dict(data_insufficient=status=='ambiguous',computation_incomplete=False)
        ws=result['alternatives'] if status=='ambiguous' else [result['certificate']['witness']];assert len(ws)==(2 if status=='ambiguous' else 1);keys=[]
        for w in ws:
            key=canonical(w['blocks'],sorted(d['alphabet']));keys.append(witness(d,w,None if cell['known_k'] is None else [cell['known_k']],{key}))
        assert len(set(keys))==len(keys)
        cert=result['certificate']
        if case=='D':
            expected_family={tuple(r) for q,family in audits[case]['oracle']['families_by_k'].items() if cell['known_k'] is None or int(q)==cell['known_k'] for r in family};assert all(k in expected_family for k in keys);certificate(d,result,cell['known_k'],expected_family)
        else:
            # Every saved anchor edge is checked in the immutable independent
            # fixture audit; now replay every provider forest edge and ensure
            # its connected atoms equal those forced groups, not guessed truth.
            parent={a:a for a in d['alphabet']}
            def root(a):
                while parent[a]!=a:a=parent[a]
                return a
            for e in cert['swap_forest']:
                pi,ni=e['positive_index'],e['negative_index'];assert type(pi)is int and type(ni)is int and 0<=pi<len(d['positive']) and 0<=ni<len(d['negative']);p,n=d['positive'][pi],d['negative'][ni];i,j=e['positions'];assert type(i)is int and type(j)is int and j==i+1 and 0<=i<j<len(p) and p[i]!=p[j] and e['symbols']==[p[i],p[j]];assert n==p[:i]+p[j]+p[i]+p[j+1:];a,b=root(p[i]),root(p[j]);assert a!=b;parent[b]=a
            groups={}
            for a in sorted(parent):groups.setdefault(root(a),[]).append(a)
            atoms=sorted(groups.values());assert atoms==cert['forced_atoms']==sorted(sorted(g) for g in audits[case]['oracle']['forced_groups']);r=len(atoms)
            for w in ws:
                owner={a:i for i,g in enumerate(w['blocks']) for a in g};assert all(len({owner[a] for a in g})==1 for g in atoms)
            assert cert['route']=='compatible_forced_atoms'
            if status=='certified_unique':assert r==cell['known_k'] and result['partition']==ws[0]['blocks'] and canonical(atoms,sorted(d['alphabet']))==keys[0]
        return status
    for entry in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):
        if entry['kind'] not in ['timing','memory']:continue
        try:
            if entry.get('execution_status')=='budget_unstarted':rows.append({**entry,'validated_status':'budget_unstarted'});continue
            p=A/'attempts'/entry['attempt_id'];cap=read(p/'result.json');assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
            for stream in ['stdout','stderr']:assert sha(p/(stream+'.bin'))==cap[stream+'_sha256']
            for src in read(p/'manifest.json')['sources']:assert sha(A/src['snapshot'])==src['sha256'] and sha(src['path'])==src['sha256']
            if cap['execution_status']=='timed_out':rows.append({**entry,'validated_status':'hard_timeout'});continue
            payload=read(p/'stdout.bin');result=payload if entry['kind']=='timing' else payload['result'];cell=cells[entry['cell_id']];assert payload['input_sha256']==fixtures[cell['case_id']]['input_sha256'];status=check_result(cell,result);assert cap['exit_code']==(3 if status=='unresolved' else 0)
            row={**entry,'validated_status':status,'subprocess_seconds':cap['subprocess_seconds'],'stdout_bytes':cap['stdout_bytes'],'metrics':result['metrics']}
            if entry['kind']=='timing':row.update(pipeline_seconds=payload['input_and_solver_seconds'],provider_seconds=result['metrics']['solver_seconds'])
            else:assert type(payload['peak_python_bytes'])is int and payload['peak_python_bytes']>=0;row.update(peak_python_bytes=payload['peak_python_bytes'],memory_scope=payload['memory_scope'])
            rows.append(row);print(json.dumps(dict(progress='capture_validated',provider=entry['provider'],cell=entry['cell_id'],kind=entry['kind'],status=status,elapsed=time.perf_counter()-start)),flush=True)
        except Exception as exc:errors.append(dict(entry=entry,error=repr(exc)))
    expected={(p,c,r) for p in providers for c in cells for r in [1,2,3]};observed=[(x['provider'],x['cell_id'],x['rep']) for x in rows if x['kind']=='timing'];assert len(observed)==len(set(observed)) and set(observed)==expected
    timings=[]
    for cell in cells:
        result=dict(cell_id=cell,providers={})
        for provider in providers:
            rr=[r for r in rows if r['kind']=='timing' and r['provider']==provider and r['cell_id']==cell];complete=[r for r in rr if r['validated_status'] in ['ambiguous','certified_unique']];result['providers'][provider]=dict(complete=len(complete),statuses=[r['validated_status'] for r in rr],median_subprocess_seconds=statistics.median(r['subprocess_seconds'] for r in complete) if len(complete)==3 else None,median_pipeline_seconds=statistics.median(r['pipeline_seconds'] for r in complete) if len(complete)==3 else None)
        b=result['providers']['baseline']['median_subprocess_seconds'];c=result['providers']['c1']['median_subprocess_seconds'];result['baseline_over_c1']=b/c if b is not None and c is not None else None;timings.append(result)
    paired=[t['baseline_over_c1'] for t in timings if t['baseline_over_c1'] is not None];gain=sum(t['providers']['c1']['complete']==3 and t['providers']['baseline']['complete']<3 for t in timings);report=dict(status='accepted_with_censoring' if not errors else 'rejected',errors=errors,small_gate_rows=gate['checked_rows'],timings=timings,rows=rows,paired_median_ratio=statistics.median(paired) if paired else None,new_completed_cells=gain,material_regression=any(r<.9 for r in paired),no_measurable_median_gain=bool(paired) and statistics.median(paired)<=1.05 and not gain,validation_seconds=time.perf_counter()-start)
    with (run/'validation_report.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','errors','paired_median_ratio','new_completed_cells','no_measurable_median_gain','material_regression','validation_seconds']}));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())

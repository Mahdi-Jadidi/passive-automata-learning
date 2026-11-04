"""Independent small full-family and large witness/world audit; no provider import."""
import hashlib,json,statistics,sys,time
from pathlib import Path
from certificate_replay_c015_v1 import verify as verify_small,canonical
A=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def main():
    started=time.perf_counter();run=Path(sys.argv[1]);manifest=load(A/'CASE_MANIFEST_V1.json');jobs={j['job_id']:j for j in manifest['jobs']};oracles={j['job_id']:j for j in load(A/'ORACLES_V1.json')['jobs']};cells={j['case_id']:j for j in manifest['performance']}
    errors=[];rows=[];data_cache={};witness_cache={};truth_checks=[]
    def data(cell):
        p=cell['input']
        if p not in data_cache:
            assert sha(p)==cell['input_sha256'];data_cache[p]=load(p)
        return data_cache[p]
    def large_witness(d,w):
        alpha=sorted(d['alphabet']);key=canonical(w['blocks'],alpha);cachekey=(id(d),key)
        if cachekey not in witness_cache:
            groups=w['blocks'];owner={ch:i for i,g in enumerate(groups) for ch in g}
            def project(word):
                out=[[] for _ in groups]
                for ch in word:out[owner[ch]].append(ch)
                return [''.join(x) for x in out]
            langs=[set() for _ in groups]
            for p in d['positive']:
                for i,x in enumerate(project(p)):langs[i].add(x)
            rejecting=[]
            for n in d['negative']:rejecting.append(tuple(i for i,x in enumerate(project(n)) if x not in langs[i]))
            assert all(rejecting)
            witness_cache[cachekey]=rejecting
        rejecting=witness_cache[cachekey]
        refs=w['negative_rejections'];assert w['local_language_rule']=='positive_projections_from_input'
        assert len(refs)==len(d['negative']) and {r['negative_index'] for r in refs}==set(range(len(d['negative'])))
        for ref in refs:
            ni,bi=ref['negative_index'],ref['rejected_by_block'];assert type(ni)is int and type(bi)is int and bi in rejecting[ni]
        return key
    def large_verify(cell,result):
        d=data(cell);status=result['status'];assert result['known_k'] is None and result['physical_truth_read'] is False
        if status=='unresolved':
            assert result['findings']['computation_incomplete'] is True and 'partition' not in result and 'alternatives' not in result
            return status
        assert status in ['ambiguous','certified_unique'] and result['findings']['computation_incomplete'] is False
        cert=result['certificate'];route=cert['route']
        if status=='ambiguous':
            assert len(result['alternatives'])==2 and len({large_witness(d,w) for w in result['alternatives']})==2 and 'partition' not in result
        else:
            key=large_witness(d,cert['witness']);assert result['partition']==cert['witness']['blocks']
            # No-K unique proof admitted here only if sound adjacent-swap edges
            # force all symbols together; unknown proof routes fail closed.
            assert max(key)==0
            parent={a:a for a in d['alphabet']}
            def root(a):
                while parent[a]!=a:a=parent[a]
                return a
            for e in cert.get('swap_forest',[]):
                p=d['positive'][e['positive_index']];n=d['negative'][e['negative_index']];i,j=e['positions'];assert type(i)is int and type(j)is int and j==i+1 and 0<=i<j<len(p)
                chars=list(p);chars[i],chars[j]=chars[j],chars[i];assert p[i]!=p[j] and ''.join(chars)==n and e['symbols']==[p[i],p[j]]
                a,b=root(p[i]),root(p[j]);assert a!=b;parent[b]=a
            assert len({root(a) for a in parent})==1,'unsupported large unique proof; not accepted'
        if route=='unary_all_partitions':
            certs=cert['negative_count_certificates'];assert len(certs)==len(d['negative']) and {r['negative_index'] for r in certs}==set(range(len(d['negative'])))
            for r in certs:
                a=r['symbol'];ni=r['negative_index'];assert a in d['alphabet'] and d['negative'][ni].count(a)==r['negative_count'] and r['negative_count'] not in {p.count(a) for p in d['positive']}
        elif status=='ambiguous':
            # Two independently replayed models suffice to certify ambiguity;
            # still verify any advertised swap edges rather than trust them.
            for e in cert.get('swap_forest',[]):
                p=d['positive'][e['positive_index']];n=d['negative'][e['negative_index']];i,j=e['positions'];chars=list(p)
                assert type(i)is int and type(j)is int and j==i+1 and 0<=i<j<len(p)
                chars[i],chars[j]=chars[j],chars[i];assert p[i]!=p[j] and ''.join(chars)==n and e['symbols']==[p[i],p[j]]
        return status
    ledger=[json.loads(x) for x in (run/'ledger.jsonl').read_text().splitlines()]
    for entry in ledger:
        try:
            if entry.get('execution_status')=='budget_unstarted':rows.append({**entry,'validated_status':'budget_unstarted'});continue
            capdir=A/'attempts'/entry['attempt_id'];cap=load(capdir/'result.json');assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
            for stream in ['stdout','stderr']:assert sha(capdir/(stream+'.bin'))==cap[stream+'_sha256']
            for src in load(capdir/'manifest.json')['sources']:
                assert sha(A/src['snapshot'])==src['sha256'] and sha(src['path'])==src['sha256']
            if cap['execution_status']=='timed_out':rows.append({**entry,'validated_status':'hard_timeout'});continue
            if entry['kind']=='preparation':assert cap['exit_code']==0;continue
            payload=(capdir/'stdout.bin').read_bytes()
            if entry['kind']=='batch':
                assert cap['exit_code']==0
                records=[json.loads(x) for x in payload.splitlines()];assert len(records)==len(jobs) and {r['job_id'] for r in records}==set(jobs)
                for record in records:
                    j=jobs[record['job_id']];assert record.get('launched') and not record.get('execution_error')
                    result=record['result'];status=verify_small(j,result,oracles.get(j['job_id']))
                    assert status!='unresolved' or j['expectation']=='timeout'
                    rows.append(dict(kind='batch',provider=entry['provider'],job_id=j['job_id'],validated_status=status))
            elif entry['kind']=='timing':
                result=json.loads(payload);cell=cells[entry['case_id']];assert result['input_sha256']==cell['input_sha256'];status=large_verify(cell,result)
                assert cap['exit_code']==(3 if status=='unresolved' else 0)
                rows.append({**entry,'validated_status':status,'subprocess_seconds':cap['subprocess_seconds'],'pipeline_seconds':result['input_and_solver_seconds'],'provider_seconds':result.get('elapsed_seconds'),'metrics':result['metrics'],'stdout_bytes':len(payload)})
        except Exception as exc:errors.append(dict(entry=entry,error=repr(exc)))
    # Independent replay from saved finite transition tables, after solver work.
    for cid,cell in cells.items():
        try:
            d=data(cell);assert sha(cell['world'])==cell['world_sha256'];world=load(cell['world']);ownership=world['ownership'];devices=world['devices']
            assert len(d['positive'])==len(d['negative'])==cell['samples_per_label']
            assert len(d['alphabet'])==40 and set(ownership)==set(d['alphabet'])
            for label,name in [(True,'positive'),(False,'negative')]:
                for word in d[name]:
                    assert len(word)<=cell['max_length'];states=[v['start'] for v in devices]
                    for ch in word:
                        i=ownership[ch];states[i]=devices[i]['transitions'][states[i]][ch]
                    assert all(q in v['accepting'] for q,v in zip(states,devices))==label
            group=[]
            for device in devices:group.append(device['alphabet'])
            refs=[]
            for ni,n in enumerate(d['negative']):
                found=None
                for bi,g in enumerate(group):
                    allowed=set(g);project=lambda w:''.join(x for x in w if x in allowed)
                    if project(n) not in {project(p) for p in d['positive']}:found=bi;break
                assert found is not None;refs.append(dict(negative_index=ni,rejected_by_block=found))
            assert large_witness(d,dict(blocks=group,negative_rejections=refs,local_language_rule='positive_projections_from_input'))
            truth_checks.append(dict(case_id=cid,status='labels_and_truth_partition_replayed',T=sum(map(len,d['positive']+d['negative'])),actual_lengths=list(map(len,d['positive']+d['negative']))))
        except Exception as exc:errors.append(dict(case_id=cid,error=repr(exc)))
    timings=[]
    for cid in cells:
        by={p:[r for r in rows if r.get('kind')=='timing' and r.get('case_id')==cid and r.get('provider')==p] for p in ['baseline','candidate']}
        record=dict(case_id=cid,providers={})
        for p,rr in by.items():
            complete=[r for r in rr if r['validated_status'] in ['ambiguous','certified_unique']]
            record['providers'][p]=dict(planned=3,observed=len(rr),complete=len(complete),median_subprocess_seconds=statistics.median(r['subprocess_seconds'] for r in complete) if len(complete)==3 else None,median_pipeline_seconds=statistics.median(r['pipeline_seconds'] for r in complete) if len(complete)==3 else None)
        b,c=[record['providers'][p]['median_subprocess_seconds'] for p in ['baseline','candidate']]
        record['baseline_over_candidate_subprocess_ratio']=b/c if b is not None and c is not None else None;timings.append(record)
    expected_batches=2*len(jobs);checked=sum(r['kind']=='batch' for r in rows);timed=sum(r['kind']=='timing' for r in rows)
    accepted=not errors and checked==expected_batches and len(truth_checks)==8
    report=dict(status='accepted_with_censoring' if accepted else 'rejected_or_incomplete',errors=errors,expected_correctness_rows=expected_batches,checked_correctness_rows=checked,timing_rows=timed,planned_timing_rows=48,truth_checks=truth_checks,timings=timings,rows=rows,validation_seconds=time.perf_counter()-started,limits=['large ambiguity checked by two independently replayed witnesses, not full Bell40 family','performance based on same compact CLI; no truth or K passed','three-complete-repetition medians only; unstarted/censored retained'])
    with (run/'validation_report.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ['status','errors','checked_correctness_rows','timing_rows','validation_seconds']}));return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())

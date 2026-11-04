"""Independent full-family decision/witness/certificate replay; no gate imports."""
import hashlib,json,sys
from pathlib import Path
from oracle_data_v1 import feasible,blocks
A=Path(__file__).resolve().parent
def canonical(part,alphabet):
    assert isinstance(part,list) and part and all(isinstance(g,list) and g for g in part)
    owner={x:i for i,g in enumerate(part) for x in g};assert set(owner)==set(alphabet) and len(owner)==sum(map(len,part))
    rename={};out=[]
    for x in alphabet:rename.setdefault(owner[x],len(rename));out.append(rename[owner[x]])
    return tuple(out)
def witness(data,w,allowed,expected):
    alphabet=sorted(data['alphabet']);key=canonical(w['blocks'],alphabet);assert key in expected and feasible(data,key)
    assert allowed is None or max(key)+1 in allowed
    assert w['local_language_rule']=='positive_projections_from_input'
    refs=w['negative_rejections'];assert len(refs)==len(data['negative']) and {r['negative_index'] for r in refs}==set(range(len(data['negative'])))
    for r in refs:
        i,b=r['negative_index'],r['rejected_by_block'];assert type(i)is int and type(b)is int and 0<=b<len(w['blocks'])
        group=set(w['blocks'][b]);project=lambda word:''.join(x for x in word if x in group)
        assert project(data['negative'][i]) not in {project(p) for p in data['positive']}
    return key
def certificate(data,result,k,expected):
    c=result['certificate'];route=c['route'];alphabet=sorted(data['alphabet']);P=data['positive'];N=data['negative']
    if route=='contradictory_labels':assert P[c['positive_index']]==N[c['negative_index']];return
    if route=='known_k_one_consistent_labels':assert k==1 and not set(P)&set(N);return
    if route=='unary_all_partitions':
        certs=c['negative_count_certificates'];assert len(certs)==len(N) and {x['negative_index'] for x in certs}==set(range(len(N)))
        for x in certs:
            a=x['symbol'];assert a in alphabet and N[x['negative_index']].count(a)==x['negative_count'] and x['negative_count'] not in {p.count(a) for p in P}
        assert c['family']==('all_set_partitions' if k is None else 'all_set_partitions_with_exactly_known_k_blocks');return
    parent={a:a for a in alphabet}
    def root(a):
        while parent[a]!=a:a=parent[a]
        return a
    for e in c['swap_forest']:
        p,n=P[e['positive_index']],N[e['negative_index']];i,j=e['positions'];assert type(i)is int and type(j)is int and j==i+1 and 0<=i<j<len(p) and len(p)==len(n)
        chars=list(p);chars[i],chars[j]=chars[j],chars[i];assert p[i]!=p[j] and ''.join(chars)==n and e['symbols']==[p[i],p[j]]
        a,b=root(p[i]),root(p[j]);assert a!=b;parent[max(a,b)]=min(a,b)
    groups={}
    for a in alphabet:groups.setdefault(root(a),[]).append(a)
    atoms=sorted(groups.values());assert atoms==c['forced_atoms'];key=canonical(atoms,alphabet)
    for rgs in expected:assert all(key[i]!=key[j] or rgs[i]==rgs[j] for i in range(len(key)) for j in range(i))
    if route=='forced_atom_count_upper_bound':assert k is not None and k>len(atoms)
    elif route=='only_forced_atom_partition_rejected':assert k==len(atoms) and not feasible(data,key)
    elif route=='compatible_forced_atoms':assert feasible(data,key)
    elif route=='exhausted_all_forced_atom_coarsenings':assert c['search_exhausted'] is True and len(expected)<=1
    else:assert route=='two_exact_search_witnesses' and result['status']=='ambiguous'
def verify(job,result,oracle):
    assert hashlib.sha256(Path(job['input']).read_bytes()).hexdigest()==job['input_sha256']
    expected_status={'unique':'certified_unique','ambiguous':'ambiguous','incompatible':'incompatible','invalid':'invalid_input','timeout':'unresolved'}[job['expectation']]
    status=result['status']
    if status=='unresolved' and job['expectation']!='timeout':return 'unresolved'
    assert status==expected_status
    assert ('partition' in result)==(status=='certified_unique')
    findings=result['findings'];assert findings['computation_incomplete']==(status=='unresolved')
    assert findings['data_insufficient']==(True if status=='ambiguous' else None if status in ['unresolved','invalid_input'] else False)
    if status in ['unresolved','invalid_input']:assert 'alternatives' not in result;return status
    data=json.loads(Path(job['input']).read_text());expected=set(map(tuple,oracle['compatible_rgs']));k=job.get('api_known_k',None if job['allowed_k'] is None else job['allowed_k'][0]);assert result['known_k']==k and result['physical_truth_read'] is False
    certificate(data,result,k,expected)
    if status=='certified_unique':
        key=witness(data,result['certificate']['witness'],job['allowed_k'],expected);assert len(expected)==1 and key==next(iter(expected)) and result['partition']==result['certificate']['witness']['blocks'] and 'alternatives' not in result
    elif status=='ambiguous':
        assert len(result['alternatives'])==2 and len(expected)>=2
        assert len({witness(data,w,job['allowed_k'],expected) for w in result['alternatives']})==2
    else:assert not expected and 'alternatives' not in result
    if job['job_id']=='graph_failure_unique_K2':assert not result['certificate']['swap_forest'] and result['certificate']['route']=='exhausted_all_forced_atom_coarsenings' and result['certificate']['search_exhausted'] is True
    return status
def main():
    run=Path(sys.argv[1]);manifest=json.loads((A/'CASE_MANIFEST_V1.json').read_text());jobs={j['job_id']:j for j in manifest['jobs']};oracles={o['job_id']:o for o in json.loads((A/'ORACLES_V1.json').read_text())['jobs']};errors={};rows=[]
    ledger=list(map(json.loads,(run/'ledger.jsonl').read_text().splitlines()))
    for entry in ledger:
        if entry['kind'] not in ['batch','cli']:continue
        try:
            p=A/'attempts'/entry['attempt_id'];cap=json.loads((p/'result.json').read_text());assert cap['child_reaped'] and not cap.get('cleanup_error')
            for stream in ['stdout','stderr']:assert hashlib.sha256((p/(stream+'.bin')).read_bytes()).hexdigest()==cap[stream+'_sha256']
            for source in json.loads((p/'manifest.json').read_text())['sources']:
                assert hashlib.sha256((A/source['snapshot']).read_bytes()).hexdigest()==source['sha256']
                assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
            if cap['execution_status']=='timed_out':rows.append({'job_id':entry['kind'],'status':'hard_timeout'});continue
            payload=(p/'stdout.bin').read_bytes()
            records=list(map(json.loads,payload.splitlines())) if entry['kind']=='batch' else [{'job_id':entry['job_id'],'result':json.loads(payload),'launched':True}]
            if entry['kind']=='batch':assert len(records)==len(jobs) and {r['job_id'] for r in records}==set(jobs)
            for record in records:
                job=jobs[record['job_id']]
                if entry.get('expected_override'):job={**job,'expectation':entry['expected_override']}
                if not record.get('launched',True):rows.append({'job_id':record['job_id'],'status':'batch_budget_unstarted'});continue
                if record.get('execution_error'):raise AssertionError(record['execution_error'])
                decision=verify(job,record['result'],oracles.get(job['job_id']));rows.append({'job_id':job['job_id'],'kind':entry['kind'],'status':decision,'route':record['result'].get('certificate',{}).get('route')})
                if entry['kind']=='cli':assert cap['exit_code']==(3 if decision=='unresolved' else 2 if decision=='invalid_input' else 0)
        except Exception as e:errors[str(entry)]=repr(e)
    accepted=not errors and len(rows)==len(jobs)+5 and all(r['status'] not in ['unresolved','hard_timeout','batch_budget_unstarted'] or r.get('kind')=='cli' and r['job_id']=='empty_both_noK' for r in rows)
    report={'status':'accepted_exact_decisions_and_witnesses' if accepted else 'rejected_or_incomplete','expected_batch_jobs':len(jobs),'checked_records':len(rows),'errors':errors,'rows':rows}
    with (run/'validation_report.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps({'status':report['status'],'errors':errors,'checked_records':len(rows)}));return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())

"""Independent saved-result replay, exact small-family controls only."""
import hashlib,importlib.util,itertools,json,sys,time
import routing_v2 as routing
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
C=R.parent.parent/'2026-11-02/partition_unrestricted_v10/audit/validate_provider_v2.py'
sp=importlib.util.spec_from_file_location('checker',C);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
def check(directory,result,full):
    data=json.loads((directory/'input2.json').read_text()) if full else None
    # Broad caller supplies the exact observational file, not the world.
    return data
def validate(data,world,result,full=False):
    data={"alphabet":sorted(data["alphabet"]),"positive":sorted(set(data["positive"])),"negative":sorted(set(data["negative"]))}
    alphabet=sorted(data['alphabet']);m=len(alphabet)
    if result.get('complete') is not True:
        assert result['status']=='unknown' and all(result.get(k) is None for k in ['partition_count','partition_count_by_k','pair_relations','representative','enumerated_partitions'])
        return {'status':'cooperative_incomplete'}
    assert result['alphabet']==alphabet and result['status'] in ['identified_unique_partition','partial_ownership_identification']
    spectrum=result['partition_count_by_k'];total=result['partition_count'];assert all(type(v)is int and v>=0 for v in spectrum.values())
    assert set(spectrum)==set(map(str,range(1,m+1))) and sum(spectrum.values())==total and spectrum['1']==1
    kmax=max(int(k) for k,v in spectrum.items() if v);assert result['k_max_compatible']==kmax
    assert world['true_devices']<=kmax<=result['k_max_upper_bound']<=len(result['atom_partition'])<=m
    atoms=old.validate_edges_and_atoms(data,result)
    assert result['atom_projection_feasible'] is routing.evaluate(data,atoms)
    truth=[d['alphabet'] for d in world['devices']];assert routing.evaluate(data,truth)
    routing.evaluate(data,result['representative']['partition'],result['representative'])
    rows=result['pair_relations'];assert len(rows)==m*(m-1)//2
    mapping={tuple(x['symbols']):x for x in rows};assert len(mapping)==len(rows)
    cache={};refs=0
    for i,j in itertools.combinations(range(m),2):
        a,b=alphabet[i],alphabet[j];row=mapping[a,b];same=row['same_partition_count'];diff=row['different_partition_count']
        assert same>=1 and diff>=0 and same+diff==total
        assert row['relation']==('forced_same' if diff==0 else 'ambiguous')
        if diff==0:assert world['ownership'][a]==world['ownership'][b]
        for field,together,exists in [('same_partition_witness',True,same>0),('different_partition_witness',False,diff>0)]:
            part=row[field];assert (part is not None)==exists
            if part is not None:
                key=old.partition_rgs(part,alphabet)
                if key not in cache:cache[key]=routing.evaluate(data,part)
                assert cache[key] and ((key[i]==key[j])==together);refs+=1
    if full:
        expected=old.direct_expected(data);enumerated=result['enumerated_partitions'];assert isinstance(enumerated,list)
        actual=set()
        for w in enumerated:routing.evaluate(data,w['partition'],w);actual.add(old.partition_rgs(w['partition'],alphabet))
        assert actual==expected and len(enumerated)==len(actual)==total
        assert spectrum=={str(k):sum(max(p)+1==k for p in expected) for k in range(1,m+1)}
        for i,j in itertools.combinations(range(m),2):assert mapping[alphabet[i],alphabet[j]]['same_partition_count']==sum(p[i]==p[j] for p in expected)
    return {'status':'unique_recovery' if total==1 else 'completed_ambiguous','truth_compatible':True,'total':total,'spectrum':spectrum,'pair_witness_references':refs,'distinct_partition_checks':len(cache),'full_family_oracle':full,'actual_lengths':[len(w) for w in data['positive']+data['negative']],'total_characters':sum(map(len,data['positive']+data['negative'])),'forced_same':[r['symbols'] for r in rows if r['relation']=='forced_same']}
def main():
    ledger=Path(sys.argv[1]);full=sys.argv[2]=='controls';reports=[];errors={};censored=[]
    routing.deadline=time.perf_counter()+150
    for row in map(json.loads,ledger.read_text().splitlines()):
        if time.perf_counter()>=routing.deadline:censored.append(row);continue
        if 'attempt_id' not in row:reports.append(row);continue
        try:
            p=A/'attempts'/row['attempt_id'];cap=json.loads((p/'result.json').read_text());raw=(p/'stdout.bin').read_bytes()
            assert hashlib.sha256(raw).hexdigest()==cap['stdout_sha256'] and cap['child_reaped'] and not cap.get('cleanup_error')
            assert hashlib.sha256((p/'stderr.bin').read_bytes()).hexdigest()==cap['stderr_sha256']
            manifest=json.loads((p/'manifest.json').read_text())
            for source in manifest['sources']:
                assert hashlib.sha256((A/source['snapshot']).read_bytes()).hexdigest()==source['sha256']
                assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
            if cap['execution_status']=='timed_out':reports.append({**row,'status':'hard_timeout'});continue
            assert cap['execution_status'] in ['success','program_error']
            result=json.loads(raw);data=json.loads(Path(row['input']).read_text());world=json.loads(Path(row['world']).read_text())
            reports.append({**row,**validate(data,world,result,full)})
        except TimeoutError:censored.append(row)
        except Exception as e:errors[str(row)]=repr(e)
    bykey={(x['K'],x['max_length'],x['samples_per_label'],x['rep']):x for x in reports if 'total' in x}
    for (k,L,n,rep),x in bykey.items():
        if n==2 and (k,L,8,rep) in bykey:
            y=bykey[k,L,8,rep]
            small=json.loads(Path(x['input']).read_text());large=json.loads(Path(y['input']).read_text())
            assert all(set(small[label])<=set(large[label]) for label in ['positive','negative'])
            assert y['total']<=x['total'] and all(y['spectrum'][i]<=v for i,v in x['spectrum'].items())
            assert set(map(tuple,x['forced_same']))<=set(map(tuple,y['forced_same']))
    accepted=not errors and not censored and (not full or len(reports)==8 and all(x.get('full_family_oracle') for x in reports))
    report={'status':'accepted_exact_full_sets' if full and accepted else 'accepted_with_evidence_limits' if accepted else 'validation_incomplete' if censored else 'rejected','errors':errors,'rows':reports,'validation_budget_censored':censored,'characters_routed':routing.characters_routed,'soft_validation_seconds':150}
    out=A/('SMALL_CONTROL_ACCEPTANCE_V3.json' if full else 'GRID_VALIDATION_V3.json')
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps({'status':report['status'],'errors':errors}));return 0 if accepted else 1
if __name__=='__main__':sys.exit(main())

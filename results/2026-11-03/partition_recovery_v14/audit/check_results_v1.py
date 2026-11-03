"""Independent compact/expanded semantics and recovery CLI replay."""
import hashlib,importlib.util,itertools,json,sys
import routing_witness_v1 as routing
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
C=R.parent.parent/'2026-11-02/partition_unrestricted_v10/audit/validate_provider_v2.py'
spec=importlib.util.spec_from_file_location('independent_checker',C);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def data_for(c):return json.loads(Path(c['path']).read_text())
def expanded(data,result,oracle,enumerated=False):
    assert result['complete'] is True and result['partition_count']==oracle['partition_count'] and result['partition_count_by_k']==oracle['partition_count_by_k']
    assert result['status']==('identified_unique_partition' if oracle['partition_count']==1 else 'partial_ownership_identification')
    expected=set(map(tuple,oracle['compatible_rgs']));alphabet=sorted(data['alphabet']);normalized={'alphabet':alphabet,'positive':sorted(set(data['positive'])),'negative':sorted(set(data['negative']))}
    assert result['k_max_compatible']==max(max(x)+1 for x in expected)
    atoms=old.validate_edges_and_atoms(normalized,result);assert result['atom_projection_feasible'] is routing.evaluate(normalized,atoms);old.check_witness(normalized,result['representative'])
    assert old.partition_rgs(result['representative']['partition'],alphabet) in expected
    rows=result['pair_relations'];assert len(rows)==len(oracle['pairs']);mapping={tuple(p['symbols']):p for p in rows};assert len(mapping)==len(rows)
    for pair in oracle['pairs']:
        row=mapping[tuple(pair['symbols'])];i,j=map(alphabet.index,pair['symbols']);assert row['same_partition_count']==pair['same'] and row['different_partition_count']==pair['different']
        assert row['relation']==('forced_same' if pair['different']==0 else 'ambiguous')
        for field,want,exists in [('same_partition_witness',True,pair['same']>0),('different_partition_witness',False,pair['different']>0)]:
            part=row[field];assert (part is not None)==exists
            if part is not None:
                key=old.partition_rgs(part,alphabet);assert key in expected and ((key[i]==key[j])==want)
    if enumerated:
        seen=set()
        for witness in result['enumerated_partitions']:old.check_witness(normalized,witness);seen.add(old.partition_rgs(witness['partition'],alphabet))
        assert seen==expected and len(result['enumerated_partitions'])==len(expected)
def compact(data,result,oracle):
    assert result['complete'] is True and result['partition_count']==oracle['partition_count'] and result['partition_count_by_k']==oracle['partition_count_by_k']
    assert result['status']==('identified_unique_partition' if oracle['partition_count']==1 else 'partial_ownership_identification')
    if result['branch']=='frozen_C010':expanded(data,result['baseline_result'],oracle);return
    assert result['branch']=='unary_closed_form' and result['family']['kind']=='all_set_partitions'
    alphabet=sorted(data['alphabet']);m=len(alphabet);assert result['k_max_compatible']==m and result['family']['base_atoms']==[[x] for x in alphabet]
    sets={a:{p.count(a) for p in data['positive']} for a in alphabet}
    assert all(any(n.count(a) not in sets[a] for a in alphabet) for n in data['negative'])
    certificates=result['negative_count_certificates'];assert len(certificates)==len(data['negative']) and {c['negative_index'] for c in certificates}==set(range(len(data['negative'])))
    for c in certificates:
        n=data['negative'][c['negative_index']];a=c['symbol'];assert a in alphabet and n.count(a)==c['negative_count'] and c['negative_count'] not in sets[a]
    pool={w['id']:w for w in result['witness_pool']};assert len(pool)==len(result['witness_pool'])
    for w in pool.values():assert routing.evaluate(data,w['partition'])
    assert result['representative_witness_id'] in pool
    mapping={tuple(p['symbols']):p for p in result['pair_relations']};assert len(mapping)==len(oracle['pairs'])
    for pair in oracle['pairs']:
        row=mapping[tuple(pair['symbols'])];i,j=map(alphabet.index,pair['symbols']);assert row['same_partition_count']==pair['same'] and row['different_partition_count']==pair['different'] and row['relation']=='ambiguous'
        for key,want in [('same_witness_id',True),('different_witness_id',False)]:
            part=pool[row[key]]['partition'];rgs=old.partition_rgs(part,alphabet);assert ((rgs[i]==rgs[j])==want)
def main():
    run=Path(sys.argv[1]);manifest=json.loads((A/'DATA_MANIFEST_V1.json').read_text());cases={c['case_id']:c for c in manifest['small_cases']};oracles={c['case_id']:c for c in json.loads((A/'SMALL_ORACLES_V1.json').read_text())['cases']};errors={};checked=0
    ledger=list(map(json.loads,(run/'ledger.jsonl').read_text().splitlines()))
    for entry in ledger:
        if entry['kind']=='timing':continue
        try:
            p=A/'attempts'/entry['attempt_id'];cap=json.loads((p/'result.json').read_text());raw=(p/'stdout.bin').read_bytes();assert cap['execution_status']=='success' and cap['child_reaped'] and hashlib.sha256(raw).hexdigest()==cap['stdout_sha256']
            assert hashlib.sha256((p/'stderr.bin').read_bytes()).hexdigest()==cap['stderr_sha256']
            for source in json.loads((p/'manifest.json').read_text())['sources']:
                assert hashlib.sha256((A/source['snapshot']).read_bytes()).hexdigest()==source['sha256']
            if entry['kind']=='batch':
                rows=list(map(json.loads,raw.splitlines()));assert len(rows)==217 and {r['case_id'] for r in rows}==set(cases)
                for row in rows:
                    c=cases[row['case_id']];data=data_for(c);o=oracles[c['case_id']]
                    (expanded(data,row['result'],o,True) if entry['method']=='baseline' else compact(data,row['result'],o));checked+=1
            else:
                result=json.loads(raw);o=oracles[entry['case_id']];data=data_for(cases[entry['case_id']]);alphabet=sorted(data['alphabet']);expected=set(map(tuple,o['compatible_rgs']));components=result['forced_same_components']
                assert components==o['components'] and result['component_partition_sample_compatible']==o['component_partition_compatible'] and result['physical_truth_read'] is False
                for edge in result['swap_witnesses']:
                    p,n=edge['positive'],edge['negative'];i,j=edge['positions'];chars=list(p);chars[i],chars[j]=chars[j],chars[i];assert p in data['positive'] and n in data['negative'] and j==i+1 and p[i]!=p[j] and ''.join(chars)==n
                compatible=old.feasible(data,components)
                if compatible:old.check_witness({'alphabet':alphabet,'positive':sorted(set(data['positive'])),'negative':sorted(set(data['negative']))},result['component_projection_witness'])
                if entry['known_k'] is None:
                    assert result['known_k_explicit_argument'] is None and result['known_k_compatible_family'] is None
                    assert result['status']==('certified_finest_compatible_partition' if compatible else 'certificate_not_established')
                    if compatible:
                        owner=old.partition_rgs(components,alphabet)
                        coarsenings={rgs for rgs in old.direct_expected({'alphabet':alphabet,'positive':[],'negative':[]}) if all(owner[i]!=owner[j] or rgs[i]==rgs[j] for i,j in itertools.combinations(range(len(alphabet)),2))};assert coarsenings==expected
                else:
                    assert result['known_k_explicit_argument']==entry['known_k'];established=compatible and len(components)==entry['known_k']
                    assert result['status']==('incompatible_under_trusted_k' if entry['known_k']>len(components) else 'certified_unique_partition_under_trusted_k' if established else 'certificate_not_established')
                    if entry['known_k']>len(components):assert result['incompatible_if_trusted_count'] is True and result['known_k_compatible_family']['kind']=='empty_family'
                    if compatible and entry['known_k']<=len(components):assert result['known_k_compatible_family']['kind']=='coarsenings_of_components_with_exactly_k_blocks' and result['known_k_compatible_family']['k']==entry['known_k']
                    if established:assert len(o['known_k_compatible_rgs'])==1 and old.partition_rgs(result['unique_partition'],alphabet)==tuple(o['known_k_compatible_rgs'][0])
                checked+=1
        except Exception as e:errors[str(entry)]=repr(e)
    report={'status':'accepted_correctness_and_recovery' if not errors and checked==452 else 'rejected_or_incomplete','checked_small_provider_results':checked,'errors':errors,'expected_results':452,'timing_validation_pending':True}
    with (run/'correctness_report.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps(report));return 0 if report['status']=='accepted_correctness_and_recovery' else 1
if __name__=='__main__':raise SystemExit(main())

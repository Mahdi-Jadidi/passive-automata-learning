"""Run ONLY with manager-approved provider SHA passed explicitly."""
import hashlib,importlib.util,json,sys,time,traceback
from pathlib import Path
from oracle_v1 import oracle,fixtures,replay,rgs,project,timing_cells
A=Path(__file__).resolve().parent
SOURCE=A.parent/'implementation/recommend_v1.py'

def check_witness(data,w):
    assert isinstance(w,dict)
    assert w['local_language_rule']=='positive_projections_from_input'
    replay(data,w['blocks'])
    if 'negative_rejections' in w:
        refs=w['negative_rejections']
        assert sorted(x['negative_index'] for x in refs)==list(range(len(data['negative'])))
        for ref in refs:
            b=w['blocks'][ref['rejected_by_block']]
            assert project(data['negative'][ref['negative_index']],b) not in {project(p,b) for p in data['positive']}

def verify(data,result,expected,completed=True):
    assert result['method']=='C026-max-blocks-v1' and result['schema_version']==1
    assert result['physical_truth_read'] is False
    status=result['status'];rec=result['recommendation']
    assert result['findings']['data_insufficient']==(True if status=='ambiguous' else False if status in ('certified_unique','incompatible') else None)
    for w in result.get('alternatives',[]):check_witness(data,w)
    if status=='ambiguous':
        assert result['findings']['computation_incomplete'] is False
        assert len(result['alternatives'])>=2
        assert rgs(result['alternatives'][0]['blocks'],data['alphabet'])!=rgs(result['alternatives'][1]['blocks'],data['alphabet'])
    if rec:
        check_witness(data,rec['witness'])
        assert rec['partition']==rec['witness']['blocks']
        assert rec['block_count']==rec['lower_bound']==len(rec['partition'])
        assert rec['lower_bound']<=expected['maximum_blocks']<=rec['upper_bound']
        for w in rec.get('optimal_witnesses',[]):check_witness(data,w)
    if completed:
        assert status==expected['status'],(status,expected)
        assert result['findings']['computation_incomplete'] is False
        if expected['family_count']:
            assert rec['optimality_proved'] is True
            assert rec['block_count']==rec['upper_bound']==expected['maximum_blocks']
            assert rec['tie_status']==('unique' if expected['optimal_count']==1 else 'multiple')
            assert rgs(rec['partition'],data['alphabet'])==rgs(expected['canonical'],data['alphabet'])
            ws=rec['optimal_witnesses'];assert len(ws)==min(2,expected['optimal_count'])
            assert len({rgs(w['blocks'],data['alphabet']) for w in ws})==len(ws)
        else:assert rec is None

def main():
    approved=sys.argv[1]
    assert len(approved)==64 and hashlib.sha256(SOURCE.read_bytes()).hexdigest()==approved
    spec=importlib.util.spec_from_file_location('approved_provider',SOURCE)
    provider=importlib.util.module_from_spec(spec);spec.loader.exec_module(provider)
    rows=[];failures=[]
    for name,data in fixtures():
        try:
            expected=oracle(data);result=provider.solve(data,deadline=time.perf_counter()+20)
            verify(data,result,expected)
            rows.append({'id':name,'status':result['status'],'maximum':expected['maximum_blocks'],'optimal_count':expected['optimal_count']})
        except Exception:
            failures.append({'id':name,'data':data,'traceback':traceback.format_exc()})
            break
    controls=[]
    data={'alphabet':list('abc'),'positive':['ab','bc','ac'],'negative':['abc']}
    expected=oracle(data)
    for name,kwargs in [('deadline',{'deadline':time.perf_counter()-1}),('memo1',{'memo_limit':1}),('memo2',{'memo_limit':2})]:
        result=provider.solve(data,**kwargs)
        verify(data,result,expected,completed=result['recommendation'] is not None and result['recommendation']['optimality_proved'])
        controls.append({'id':name,'result':result})
    quota_data=dict(timing_cells())['m6_repeated3symbol'];quota_expected=oracle(quota_data)
    interrupted_nontrivial=False
    for limit in range(1,101):
        result=provider.solve(quota_data,memo_limit=limit)
        rec=result['recommendation']
        verify(quota_data,result,quota_expected,completed=bool(rec and rec['optimality_proved']))
        controls.append({'id':'quota_search','memo_limit':limit,'result':result})
        if rec and rec['block_count']>1 and not rec['optimality_proved']:
            interrupted_nontrivial=True;break
    assert interrupted_nontrivial,'No interrupted nontrivial incumbent found in fixed quota sweep1..100'
    invalid=[{}, {'alphabet':[],'positive':[],'negative':[]},{'alphabet':['a','a'],'positive':[],'negative':[]},{'alphabet':['a'],'positive':['z'],'negative':[]},{'alphabet':['a'],'positive':[True],'negative':[]}]
    for d in invalid:
        result=provider.solve(d);assert result['status']=='invalid_input' and result['recommendation'] is None
    for kwargs in [{'memo_limit':0},{'memo_limit':True},{'deadline':float('nan')},{'deadline':True}]:
        result=provider.solve(data,**kwargs);assert result['status']=='invalid_input'
    # Same callable, changing data, then counterexample update; no stale cache allowed.
    before={'alphabet':list('abc'),'positive':['ab'],'negative':[]}
    after={**before,'negative':['ba']}
    for d in [before,after,before,data,after]:verify(d,provider.solve(d),oracle(d))
    rename=dict(zip('abc','zxy'))
    renamed={k:([rename[c] for c in v] if k=='alphabet' else [''.join(rename[c] for c in w) for w in v]) for k,v in data.items()}
    verify(renamed,provider.solve(renamed),oracle(renamed))
    out={'source_sha256':approved,'completed_fixture_count':len(rows),'failures':failures,'rows':rows,'resource_controls':controls,'invalid_controls':len(invalid)+4,'cache_update_renaming_controls':6}
    path=A/'PROVIDER_CORRECTNESS_V1.json'
    with path.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
    print(json.dumps({'completed':len(rows),'failures':len(failures),'path':str(path)}))
    return bool(failures)

if __name__=='__main__':raise SystemExit(main())

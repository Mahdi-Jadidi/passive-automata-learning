import copy,json,importlib.util
from pathlib import Path
from optimizer import solve_optimal
from verify import verify_optimal
ROOT=Path(__file__).resolve().parents[3]
def main():
    spec=importlib.util.spec_from_file_location('reference',ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py')
    reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
    cases=[
      {'alphabet':['a','aa','unused'],'positive':[[],['a','aa'],['a','aa']],'negative':[['aa','a']]},
      {'alphabet':['é','é','unused'],'positive':[['é','é']],'negative':[['é','é']]},
      {'alphabet':['a','b'],'positive':[['a']],'negative':[['a']]},
    ]
    checks=0
    for D in cases:
        result=solve_optimal(D);expected=reference.solve(D)
        assert result['max_devices']==expected['max_blocks'];assert verify_optimal(D,result)=={'status':'ACCEPT'};checks+=1
    invalid=[{}, {'alphabet':['a','a'],'positive':[],'negative':[]}, {'alphabet':['a'],'positive':[['a']],'negative':[['a'],['unknown']]}]
    for D in invalid:
        assert solve_optimal(D)['status']=='INVALID_INPUT';checks+=1
    D={'alphabet':['a','b','c'],'positive':[[],['a','b','c']],'negative':[['a']]}
    result=solve_optimal(D)
    for limits in [{'timeout_seconds':True},{'timeout_seconds':-1},{'unknown':1}]:
        assert solve_optimal(D,limits)['status']=='INVALID_INPUT';checks+=1
    for k in [True,1,3]:
        bad=copy.deepcopy(result);bad['max_devices']=k;assert verify_optimal(D,bad)=={'status':'REJECT'};checks+=1
    bad={'status':'OPTIMAL','blocks':[['a','b','c']],'max_devices':1,'certificate':{'type':'edge_size_bound'}}
    assert verify_optimal(D,bad)=={'status':'REJECT'};checks+=1
    contradictory=copy.deepcopy(D);contradictory['positive'].append(['a'])
    assert verify_optimal(contradictory,result)=={'status':'REJECT'};checks+=1
    print(json.dumps({'boundary_checks':checks}))
if __name__=='__main__':main()

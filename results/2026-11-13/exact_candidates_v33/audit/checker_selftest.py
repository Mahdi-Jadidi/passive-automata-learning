"""Check mutation sensitivity without editing candidate or corpus."""
import copy,json
from check_contract import expected,replay
case={'alphabet':['a','b','c'],'positive':[[],['a','b','c']],'negative':[['a']]}
good=expected(case); replay(case,good); variants={}
for key in ('compatible_count','optimal_count'):
    x=copy.deepcopy(good); x[key]+=1; variants[key]=x
x=copy.deepcopy(good); x['compatible_witnesses'].reverse(); variants['reversed_witnesses']=x
x=copy.deepcopy(good); x['compatible_witnesses'][0]['rgs'][0]=9; variants['rgs']=x
x=copy.deepcopy(good); x['compatible_witnesses'][0]['negative_rejected_by'][0]=99; variants['rejection_index']=x
assert len(good['compatible_witnesses'])==2
assert all(x!=good for x in variants.values())
for name in ['rgs','rejection_index']:
    try: replay(case,variants[name])
    except (AssertionError,IndexError,KeyError,TypeError): pass
    else: raise AssertionError('replay missed '+name)
collision={'alphabet':['a','bc','ab','c'],'positive':[['a','bc']],'negative':[['ab','c']]}
assert expected(collision)['status']!='INCOMPATIBLE'
print(json.dumps({'status':'PASS','exact_comparison_mutations_rejected':list(variants),'replay_mutations_rejected':['rgs','rejection_index'],'opaque_tuple_collision_checked':True}))

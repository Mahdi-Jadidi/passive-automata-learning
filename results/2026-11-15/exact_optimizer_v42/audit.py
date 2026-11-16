import importlib.util,itertools,json,copy,hashlib
from pathlib import Path
from optimizer import solve_optimal
from verify import verify_optimal
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(path):
 s=importlib.util.spec_from_file_location('oracle',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ref=load(ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py')
 words=[[],['a'],['b'],['a','a'],['a','b'],['b','a'],['b','b']]
 cases=[{'alphabet':['a','b'],'positive':[w for w,v in zip(words,labels) if v==1],'negative':[w for w,v in zip(words,labels) if v==2]} for labels in itertools.product(range(3),repeat=7)]
 cases += [{'alphabet':[],'positive':p,'negative':n} for p,n in [([],[]),([],[[]]),([[]],[]),([[]],[[]])]]
 cases += [json.loads(line)['input'] for line in (ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl').read_text().splitlines()]
 path=HERE/'audit_raw.jsonl'
 with path.open('x',encoding='utf8') as stream:
  for i,data in enumerate(cases):
   expected=ref.solve(data); actual=solve_optimal(data,{'timeout_seconds':60});checked=verify_optimal(data,actual,{'timeout_seconds':60})
   ok=checked=={'status':'ACCEPT'} and ((expected['compatible_count']==0 and actual['status']=='INFEASIBLE') or (expected['compatible_count']>0 and actual['status']=='OPTIMAL' and actual['max_devices']==expected['max_blocks']))
   stream.write(json.dumps({'i':i,'input':data,'result':actual,'checked':checked,'expected_k':expected['max_blocks'],'pass':ok})+'\n');stream.flush()
   if not ok:raise AssertionError((i,data,actual,expected,checked))
  data={'alphabet':['a','b','c'],'positive':[[],['a','b','c']],'negative':[['a']]}
  result=solve_optimal(data);assert result['certificate']['type']=='drup'
  for key,value in [('max_devices',3),('blocks',[['a'],['b'],['c']])]:
   bad=copy.deepcopy(result);bad[key]=value;assert verify_optimal(data,bad)=={'status':'REJECT'}
  bad=copy.deepcopy(result);bad['certificate']['proof']=['999999999 0'];assert verify_optimal(data,bad)=={'status':'REJECT'}
  assert solve_optimal(data,{'timeout_seconds':0})['status']=='INCOMPLETE'
  assert verify_optimal(data,result,{'timeout_seconds':0})['status']=='INCOMPLETE'
 print(json.dumps({'pass_cases':len(cases),'tamper_checks':3,'zero_limits':2}))
if __name__=='__main__':main()

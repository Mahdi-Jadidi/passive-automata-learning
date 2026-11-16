import importlib.util,itertools,json,copy,hashlib,random
from pathlib import Path
from optimizer import solve_optimal
from verify import verify_optimal
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(path):
 s=importlib.util.spec_from_file_location('oracle',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ref=load(ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py')
 legacy_encoding=load(ROOT/'results/2026-11-15/exact_optimizer_v42/encoding.py')
 words=[[],['a'],['b'],['a','a'],['a','b'],['b','a'],['b','b']]
 cases=[{'alphabet':['a','b'],'positive':[w for w,v in zip(words,labels) if v==1],'negative':[w for w,v in zip(words,labels) if v==2]} for labels in itertools.product(range(3),repeat=7)]
 cases += [{'alphabet':[],'positive':p,'negative':n} for p,n in [([],[]),([],[[]]),([[]],[]),([[]],[[]])]]
 cases += [json.loads(line)['input'] for line in (ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl').read_text().splitlines()]
 rng=random.Random(20261116)
 for j in range(60):
  Sigma=['s'+str(i) for i in range(3+j%3)]
  words=[list(w) for size in range(3) for w in itertools.product(Sigma,repeat=size)]
  rng.shuffle(words);plus=rng.randrange(4);minus=rng.randrange(1,4)
  cases.append({'alphabet':Sigma,'positive':words[:plus],'negative':words[plus:plus+minus]})
 path=HERE/'audit_raw.jsonl'
 with path.open('x',encoding='utf8') as stream:
  for i,data in enumerate(cases):
   expected=ref.solve(data); actual=solve_optimal(data,{'timeout_seconds':60});checked=verify_optimal(data,actual,{'timeout_seconds':60})
   import encoding as E
   Sigma,S_plus,S_minus=E.normalize(data)
   new=E.build(Sigma,S_plus,S_minus,E.budget(None))
   old=legacy_encoding.build(Sigma,S_plus,S_minus,legacy_encoding.budget(None))
   edges_same=new['groups']==old['groups'] and all(set(x)==set(y) for x,y in zip(new['edges'],old['edges'])) and len(new['edges'])==len(old['edges'])
   ok=checked=={'status':'ACCEPT'} and ((expected['compatible_count']==0 and actual['status']=='INFEASIBLE') or (expected['compatible_count']>0 and actual['status']=='OPTIMAL' and actual['max_devices']==expected['max_blocks']))
   ok=ok and edges_same
   stream.write(json.dumps({'i':i,'input':data,'result':actual,'checked':checked,'expected_k':expected['max_blocks'],'mining_matches_exhaustive':edges_same,'pass':ok})+'\n');stream.flush()
   if not ok:raise AssertionError((i,data,actual,expected,checked))
  data={'alphabet':['a','b','c'],'positive':[[],['a','b','c']],'negative':[['a']]}
  result=solve_optimal(data)
  for key,value in [('max_devices',3),('blocks',[['a'],['b'],['c']])]:
   bad=copy.deepcopy(result);bad[key]=value;assert verify_optimal(data,bad)=={'status':'REJECT'}
  bad=copy.deepcopy(result);bad['certificate']={'type':'drup','proof':['999999999 0']};assert verify_optimal(data,bad)=={'status':'REJECT'}
  assert solve_optimal(data,{'timeout_seconds':0})['status']=='INCOMPLETE'
  assert verify_optimal(data,result,{'timeout_seconds':0})['status']=='INCOMPLETE'
 print(json.dumps({'pass_cases':len(cases),'exhaustive_mining_comparisons':len(cases),'tamper_checks':3,'zero_limits':2}))
if __name__=='__main__':main()

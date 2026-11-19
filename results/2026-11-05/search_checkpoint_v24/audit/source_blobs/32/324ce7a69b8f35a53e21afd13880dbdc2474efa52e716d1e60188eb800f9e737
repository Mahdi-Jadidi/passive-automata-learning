"""Preparation only: no provider imports or executions."""
import hashlib,itertools,json,platform,random,shutil,sys
from pathlib import Path
from oracle_data_v1 import full_family,feasible,rgs
from certificate_replay_c015_v2 import analytic_obstruction
A=Path(__file__).resolve().parent;ROOT=A.parents[3];OLD=ROOT/'results/2026-11-04/scaling_v20/audit'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def put(cid,d):
 p=A/'fixtures'/f'{cid}.json';save(p,d);return {'case_id':cid,'input':str(p),'input_sha256':sha(p)}
def graph_empty(d):
 P=set(d['positive']);N=set(d['negative'])
 return not any(p[:i]+p[i+1]+p[i]+p[i+2:] in N for p in P for i in range(len(p)-1) if p[i]!=p[i+1])
def main():
 jobs=[];oracles=[];screen=[];cells=[];cache={}
 def add(cid,d,ks=(None,1,2),expect=None):
  c=put(cid,d);family=full_family(d) if expect is None else None
  for k in ks:
   f=[x for x in family if k is None or max(x)+1==k] if family is not None else []
   jid=cid+('_noK' if k is None else '_K'+str(k));e=expect or ('unique' if len(f)==1 else 'ambiguous' if f else 'incompatible')
   jobs.append({**c,'job_id':jid,'allowed_k':None if k is None else [k],'expectation':e})
   if expect is None:oracles.append({'job_id':jid,'compatible_rgs':f,'count':len(f),'method':'independent full RGS'})
  return c,family
 # Exhaust all disjoint ternary labels of this four-word binary universe.
 for i,labs in enumerate(itertools.product(range(3),repeat=4)):
  words=['','a','b','ab'];d={'alphabet':['a','b'],'positive':[w for w,l in zip(words,labs) if l==1],'negative':[w for w,l in zip(words,labs) if l==2]};add(f'exhaust2_{i:03}',d)
 for m in range(2,7):
  alpha=list('abcdef'[:m]);rng=random.Random(24000+m);words=['']+[''.join(w) for n in range(1,4) for w in itertools.product(alpha,repeat=n)]
  for i in range(20):
   selected=rng.sample(words,min(16,len(words)));rng.shuffle(selected);add(f'random_m{m}_{i:02}',{'alphabet':alpha,'positive':selected[:8],'negative':selected[8:]},(None,1,2,m))
 # Deterministic screen of deletion subsets; every attempt retained, no provider used.
 alpha=list('abcdef');n=''.join(alpha);deletions=[n[:i]+n[i+1:] for i in range(6)]
 selected=None
 for mask in range(1,64):
  d={'alphabet':alpha,'positive':[p for i,p in enumerate(deletions) if mask>>i&1],'negative':[n]};f=full_family(d)
  ok=graph_empty(d) and not feasible(d,tuple(range(6))) and len(f)>1
  screen.append({'attempt_id':f'C024-SCREEN-{mask:03}','mask':mask,'input':d,'full_family_count':len(f),'graph_empty':graph_empty(d),'atom_incompatible':not feasible(d,tuple(range(6))),'selected':ok and selected is None})
  if ok and selected is None:selected=d
 assert selected
 c,f=add('ambiguous_graph_empty',selected);cells.append({**c,'cell_id':'ambiguous_noK','known_k':None,'oracle_method':'full RGS','compatible_rgs':f})
 for m in [2,3,4,5,6,8,10,12]:
  alpha=list('abcdefghijkl'[:m]);n=''.join(alpha);d={'alphabet':alpha,'positive':[n[:i]+n[i+1:] for i in range(m)],'negative':[n]};assert analytic_obstruction(d)
  if m<=6:add('obstruction_m'+str(m),d,(None,1,2,m))
  else:
   c=put('obstruction_m'+str(m),d);cells.append({**c,'cell_id':'obstruction_m'+str(m)+'_noK','known_k':None,'oracle_method':'analytic deletion obstruction','compatible_rgs':[[0]*m]})
 for tag in ['A','D']:
  src=OLD/'fixtures_v1'/tag/'solver_input.json';c=put('old_'+tag,json.loads(src.read_text(encoding='utf-8-sig')));cells.append({**c,'cell_id':tag+'_K4','known_k':4,'oracle_method':'prior independent structural proof; replay mandatory after launch'})
 base={'alphabet':['a','b','c'],'positive':['','ab','ac'],'negative':['abc']}
 variants={'base':base,'duplicates':{**base,'positive':base['positive']*2,'negative':base['negative']*2},'order':{**base,'alphabet':list(reversed(base['alphabet'])),'positive':list(reversed(base['positive']))},'unicode':{'alphabet':['α','中','🙂'],'positive':['','α中','α🙂'],'negative':['α中🙂']},'empty':{'alphabet':['a','b'],'positive':[],'negative':[]},'contradictory':{'alphabet':['a','b'],'positive':['a'],'negative':['a']}}
 for tag,d in variants.items():add('meta_'+tag,d)
 for tag,d in [('late_unknown',{'alphabet':['a','b'],'positive':['ab']*1000+['abz'],'negative':[]}),('late_nonstring',{'alphabet':['a','b'],'positive':['ab']*1000+[3],'negative':[]}),('duplicate_symbols',{'alphabet':['a','a'],'positive':[],'negative':[]}),('empty_alphabet',{'alphabet':[],'positive':[],'negative':[]})]:add('invalid_'+tag,d,(None,), 'invalid')
 deadline={**jobs[0],'job_id':'deadline_zero','expectation':'timeout','seconds':0};jobs.append(deadline)
 # Independently cross-check canonical masks against full RGS two-block family.
 completeness=[]
 for r in range(2,11):
  masks={tuple(0 if mask>>i&1 else 1 for i in range(r)) for mask in range(1,1<<r,2) if mask!=(1<<r)-1}
  ref={x for x in rgs(r) if max(x)==1};assert masks==ref and len(masks)==2**(r-1)-1
  completeness.append({'r':r,'count':len(masks),'expected':2**(r-1)-1,'matches_full_RGS':True})
 save(A/'CASE_MANIFEST_V1.json',{'jobs':jobs,'unique_input_count':len({j['input_sha256'] for j in jobs}),'call_count':len(jobs),'full_oracle_max_m':6})
 save(A/'ORACLES_V1.json',{'jobs':oracles});save(A/'SCREENING_V1.json',screen);save(A/'BIPARTITION_COMPLETENESS_V1.json',completeness)
 # Fixed target ordering, six cells.
 cells.sort(key=lambda c:['obstruction_m8_noK','obstruction_m10_noK','obstruction_m12_noK','ambiguous_noK','D_K4','A_K4'].index(c['cell_id']))
 save(A/'TIMING_PLAN_V1.json',{'cells':cells,'repeats':5,'cooperative_seconds':20,'outer_seconds':25,'provider_total_process_seconds':600,'rotating_order':True,'official_launch_authorized':False})
 baseline=ROOT/'results/2026-11-04/scaling_v20/implementation/candidate_c2_v1'
 save(A/'PROVIDERS_TEMPLATE_V1.json',{'providers':[{'id':'C020_C2','solver':str(baseline/'gate_v1.py'),'cli':str(baseline/'partition_gate_v1.py')},{'id':'C024_A','solver':'REPLACE_AFTER_SOURCE_REVIEW','cli':'REPLACE_AFTER_SOURCE_REVIEW'}]})
 sources=[OLD/x for x in ['oracle_data_v1.py','certificate_replay_c015_v2.py','capture.py']]+[baseline/'gate_v1.py',baseline/'partition_gate_v1.py']
 save(A/'PREPARATION_FREEZE_V1.json',{'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform()},'historical_sources':[{'path':str(p),'sha256':sha(p)} for p in sources],'prepared_files':[{'path':str(p),'sha256':sha(p)} for p in sorted(A.glob('*.py'))]})
 save(A/'READINESS_V1.json',{'state':'prepared_awaiting_manager_source_review_and_launch','official_timing_run':False,'candidate_executed':False,'unique_inputs':len({j['input_sha256'] for j in jobs}),'correctness_calls':len(jobs),'timing_cells':len(cells),'screening_attempts':len(screen),'bipartition_checks':completeness,'checks':{'full_oracle_generated':True,'analytic_obstruction_m2_to_m12':True,'fixtures_frozen':True,'historical_files_unchanged':True,'provider_binding_pending_review':True},'limitations':['A/D use prior independent structural oracle; final replay must retain that proof','No correctness or timing provider execution in preparation','New route names must match reviewed implementation before launch']})
 print(json.dumps({'prepared':True,'jobs':len(jobs),'unique_inputs':len({j['input_sha256'] for j in jobs}),'cells':len(cells)}))
if __name__=='__main__':main()

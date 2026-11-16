"""C025 independent bounded verification and evaluation. No artifact imports."""
import collections,hashlib,importlib.util,json,random,sys,time
from pathlib import Path
from context_oracle_c017_v3 import partitions,block_conflicts
A=Path(__file__).resolve().parent;R=A.parent;S=R/'implementation/selected_output_v1/solver_v1.py'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def convert(data):return [[{'symbol':e['id'],'label':e['outcome']} for e in t['events']] for t in data['traces']]
def family(data,d,k=None):
 traces=convert(data);alpha=data['alphabet'];good={};out=[]
 for p in partitions(alpha):
  if k is not None and len(p)!=k:continue
  for b in p:
   if b not in good:good[b]=not block_conflicts(traces,b,d)
  if all(good[b] for b in p):out.append(p)
 return out

def replay(data,res,d,fam):
 assert res['status']==('certified_unique' if len(fam)==1 else 'ambiguous' if fam else 'incompatible')
 expected={frozenset(map(frozenset,p)) for p in fam};traces={t['file_id']:t['events'] for t in data['traces']}
 def context(ref,B):
  ev=traces[ref['file_id']];i=ref['event_index'];assert ev[i]['id'] in B;prior=tuple(e['id'] for e in ev[:i] if e['id'] in B);return (prior if d=='full' else prior[-d:] if d else (),ev[i]['id']),ev[i]['outcome']
 for c in res['certificate']['block_checks']:
  if c['conflict']:
   x=c['conflict'];a,y=context(x['first'],c['blocks_symbols']);b,z=context(x['opposite'],c['blocks_symbols']);assert a==b and y!=z and type(y)is bool and type(z)is bool
 ws=res.get('alternatives',[]) if res['status']=='ambiguous' else [res['witness']] if res['status']=='certified_unique' else []
 for w in ws:
  assert frozenset(map(frozenset,w['blocks'])) in expected
  for fn in w['functions']:
   B=fn['block'];table={}
   for t in data['traces']:
    for i,e in enumerate(t['events']):
     if e['id'] in B and e['outcome'] is not None:
      c,y=context({'file_id':t['file_id'],'event_index':i},B);assert c not in table or table[c]==y;table[c]=y
   decoded={0:()}
   for edge in fn['trie']:assert edge['parent'] in decoded;decoded[edge['node']]=decoded[edge['parent']]+(edge['event_id'],)
   rules={}
   for rule in fn['output_rules']:
    c,y=context(rule['reference'],B);assert y==rule['outcome']
    if d=='full':assert decoded[rule['context']]==c[0]+(c[1],)
    else:assert (tuple(rule['context'][0]),rule['context'][1])==c
    rules[c]=y
   assert rules==table
 return ws

def heldout(train,test,w,d,continued=False):
 output=[]
 for fn in w['functions']:
  B=set(fn['block']);table={}
  for t in train['traces']:
   h=[]
   for e in t['events']:
    if e['id'] not in B:continue
    c=(tuple(h if d=='full' else h[-d:] if d else []),e['id'])
    if e['outcome'] is not None:table[c]=e['outcome']
    h.append(e['id'])
  counts=collections.Counter()
  for t in test:
   h=[]
   for i,e in enumerate(t['events']):
    if e['id'] not in B:continue
    c=(tuple(h if d=='full' else h[-d:] if d else []),e['id']);h.append(e['id'])
    if i<t.get('evaluation_start',0) or e['outcome'] is None:continue
    counts['labelled']+=1
    if c not in table:counts['abstention']+=1
    else:counts['known_context']+=1;counts['opposite_conflicts']+=table[c]!=e['outcome']
  output.append({'block':sorted(B),**dict(counts)})
 return output

def main():
 assert hashlib.sha256(S.read_bytes()).hexdigest()=='73ff8ecae70a55525ec6a2d3f1216e721ad2f1298d973d334e6f743080358e4e'
 spec=importlib.util.spec_from_file_location('provider',S);provider=importlib.util.module_from_spec(spec);spec.loader.exec_module(provider)
 mode=sys.argv[1];rows=[]
 if mode=='controls':
  rng=random.Random(25006)
  for j in range(36):
   alpha=list('abc'[:1+j%3]);ts=[]
   for ti in range(3):ts.append({'file_id':ti,'events':[{'id':rng.choice(alpha),'outcome':rng.choice([True,False,None])} for _ in range(rng.randrange(1,9))]})
   data={'alphabet':alpha,'traces':ts}
   for d in [0,1,2,4,8,'full']:
    for k in [None,len(alpha)]:
     f=family(data,d,k);res=provider.solve(data,depth=d,model_version='selected-output-v1',known_k=k,deadline=time.perf_counter()+20);replay(data,res,d,f);rows.append({'case':j,'depth':d,'k':k,'status':res['status']})
  from independent_oracle_v1 import self_check
  self_check()
  valid={'alphabet':['x'],'traces':[]}
  for kwargs in [{'known_k':True},{'depth':3},{'deadline':time.perf_counter()-1}]:
   opts={'depth':0,'model_version':'selected-output-v1',**kwargs};res=provider.solve(valid,**opts);assert res['status']==('unresolved' if 'deadline'in kwargs else 'invalid_input');rows.append({'special':str(kwargs),'status':res['status']})
  save(A/'SMALL_CONTROLS_V1.json',{'errors':0,'calls':len(rows),'rows':rows});print({'controls_pass':True,'calls':len(rows)});return
 arm=sys.argv[2];plan=read(A/'ACTUAL_FREEZE_V3.json');p=next(x for x in plan['arms'] if x['id']==arm);data=read(p['path']);train=data['traces'][:4] if arm!='BGL' else [{'file_id':0,'events':data['traces'][0]['events'][:1400]}];test=data['traces'][4:] if arm!='BGL' else [{**data['traces'][0],'evaluation_start':1400}]
 freq=collections.Counter(e['id'] for t in train for e in t['events']);selected=sorted(freq,key=lambda a:(-freq[a],a))[:8];payload={'alphabet':sorted(selected),'traces':[{'file_id':t['file_id'],'events':[e for e in t['events'] if e['id'] in selected]} for t in train]}
 for d in [0,1,2,4,8,'full']:
  f=family(payload,d);res=provider.solve(payload,depth=d,model_version='selected-output-v1',deadline=time.perf_counter()+20);ws=replay(payload,res,d,f);row={'arm':arm,'depth':d,'status':res['status'],'independent_family_count':len(f),'result':res,'heldout_alternatives':[heldout(payload,test,w,d) for w in ws]};rows.append(row);print(json.dumps({'arm':arm,'depth':d,'status':res['status'],'family_count':len(f)}),flush=True)
 coverage={}
 for name,ts in [('training',train),('heldout',test)]:
  ev=[e for t in ts for i,e in enumerate(t['events']) if i>=t.get('evaluation_start',0)];coverage[name]={'total_events':len(ev),'selected_events':sum(e['id'] in selected for e in ev),'omitted_events':sum(e['id'] not in selected for e in ev),'labelled':sum(e['outcome'] is not None for e in ev),'omitted_labelled':sum(e['outcome'] is not None and e['id'] not in selected for e in ev),'types':len({e['id'] for e in ev})}
 save(A/('ACTUAL_'+arm+'_V1.json'),{'rows':rows,'selected':selected,'coverage':coverage,'whole_host_reference':'undefined unless separately demonstrated functional; no physical recovery claim','errors':0})
if __name__=='__main__':main()

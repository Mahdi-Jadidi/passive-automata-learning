"""Independent artifact inspection. No artifact imports, execution or solver calls."""
import ast,collections,hashlib,json,platform,sys,zipfile
from pathlib import Path
import yaml
A=Path(__file__).resolve().parent;ROOT=A.parents[3];OLD=ROOT/'results/2026-11-04/lancer_case_study_v16/data_audit'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def strict(v):return (v==1) if type(v)is int and v in (1,3) else None
def key(e):
 # Audit-only proposed observable fields. No target/agent/outcome/source identity.
 return json.dumps({k:e.get(k) for k in ['action','exploit_class','exploit_port']},sort_keys=True,ensure_ascii=False,separators=(',',':'))
def inspect_events(episodes):
 seen={};opposites=[];labels=collections.Counter();hosts=collections.defaultdict(set);positions=[];unknown=[];symbols={};prefixes={};contradictions=[]
 for ei,ep in enumerate(episodes):
  history=[]
  for i,e in enumerate(ep):
   k=key(e);symbol='e_'+sha(k.encode());symbols[symbol]=json.loads(k);label=e['label'];host=e.get('hostname');hosts[symbol].add(str(host) if host else '<undefined>');history.append(symbol);labels[str(label)]+=1
   if label is None:unknown.append([ei,i,e.get('unknown_reason','unlabeled')]);continue
   ck=(symbol,);old=seen.setdefault(ck,{False:[],True:[]});old[label].append([ei,i])
   if old[False] and old[True] and len(opposites)<10:opposites.append({'symbol':symbol,'false':old[False][0],'true':old[True][0],'meaning':'same current event at zero history; proposed target-free mapping; not proof against full-history Mealy'})
   pk=tuple(history)
   if pk in prefixes and prefixes[pk][0]!=label:contradictions.append({'first':prefixes[pk][1],'opposite':[ei,i]})
   else:prefixes.setdefault(pk,(label,[ei,i]))
  positions.append({'episode_index':ei,'events':len(ep)})
 return {'episode_boundaries':positions,'labels':dict(labels),'unlabeled_positions':unknown,'symbol_count':len(symbols),'same_current_symbol_opposite_outputs':opposites,'identical_full_prefix_opposite_outputs':contradictions,'host_scope_nonfunctional_symbols':sum(len(v)!=1 or '<undefined>' in v for v in hosts.values()),'proposed_mapping':symbols,'host_recovery_ground_truth_valid':False}
def main():
 out=A/'preparation_v1';out.mkdir(exist_ok=False);access=json.loads((OLD/'archive_access_20261103T211638Z.json').read_text());zp=Path(access['cache_path']);h=hashlib.sha256();md=hashlib.md5()
 with zp.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b);md.update(b)
 assert h.hexdigest()==access['sha256'] and md.hexdigest()==access['md5'] and zp.stat().st_size==access['downloaded_bytes']
 errors=[];verified=[];rows=[];selected=[];omitted=[]
 with zipfile.ZipFile(zp) as z:
  old=json.loads((OLD/'selected_manifest_v1.json').read_text())
  for f in old['files']:
   raw=z.read(f['archive_path']);assert sha(raw)==f['sha256'] and len(raw)==f['bytes'];assert sha((OLD/f['local_path']).read_bytes())==f['sha256'];verified.append({'member':f['archive_path'],'sha256':sha(raw)})
  groups=collections.defaultdict(list)
  for info in z.infolist():
   n=info.filename
   if n.startswith('artifact/data/cage2/cage2_raw_traces/') and n.endswith('.yaml'):groups['CAGE2_raw'].append(n)
   elif n.startswith('artifact/data/one_host_network_validity_only/') and n.endswith('.txt'):groups[n.rsplit('/',1)[0]].append(n)
  for group,names in sorted(groups.items()):
   names.sort();chosen=names[:6];omitted.append({'group':group,'available':len(names),'selected':len(chosen),'omitted':len(names)-len(chosen),'selection':'first six lexicographic original ZIP member names; no outcome filtering','unselected_members_sha256':sha('\n'.join(names[6:]).encode())})
   for n in chosen:
    raw=z.read(n);sid='C025-SOURCE-'+str(len(selected)+1).zfill(3);source={'source_id':sid,'group':group,'member':n,'bytes':len(raw),'sha256':sha(raw),'zip_crc32':z.getinfo(n).CRC};selected.append(source)
    try:
     assert len(raw)<2_000_000
     if group=='CAGE2_raw':
      data=yaml.load(raw,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader));assert isinstance(data,list);ep=[];status=collections.Counter()
      for i,r in enumerate(data):
       for actor in ['Blue','Red']:
        action=r[actor]['action'];assert isinstance(action,dict);v=data[i+1][actor].get('obs',{}).get('prev_action_status') if i+1<len(data) else None;label=strict(v);status[repr(v)]+=1
        ep.append({'action':action['type'],'exploit_class':action.get('exploit_class'),'exploit_port':action.get('exploit_port'),'hostname':action.get('hostname'),'label':label,'unknown_reason':'final_record_no_next_status' if i+1==len(data) else 'unknown_or_invalid_status'})
      episodes=[ep];extra={'raw_records':len(data),'actor_order':'Blue_then_Red','status_from_next_record_same_actor':True,'status_values':dict(status),'final_events_retained_unlabeled':2,'TrueState_excluded':True}
     else:
      data=ast.literal_eval(raw.decode('utf-8'));assert isinstance(data,list);episodes=[];extra={'format':'Python literal parsed by ast.literal_eval; artifact not imported','success_policy':'exact string TRUE/FALSE; everything else unlabeled'}
      for episode in data:
       ep=[]
       for pair in episode:
        assert isinstance(pair,list) and len(pair)==2 and [e['agent'] for e in pair]==['Blue','Red']
        for e in pair:ep.append({**{k:e.get(k) for k in ['action','exploit_class','exploit_port','hostname']},'label':True if e.get('success')=='TRUE' else False if e.get('success')=='FALSE' else None})
       episodes.append(ep)
     row={**source,**extra,**inspect_events(episodes)};rows.append(row)
    except Exception as e:errors.append({'failure_id':'C025-PREP-'+sid,'source':source,'error':repr(e)})
    print(json.dumps({'source_id':sid,'parsed':not errors or errors[-1]['source']['source_id']!=sid}),flush=True)
 save(out/'PROVENANCE_V1.json',{'archive':{'path':str(zp),'bytes':zp.stat().st_size,'sha256':h.hexdigest(),'md5':md.hexdigest()},'selected_C016_members_verified':verified,'source_url':access['url'],'runtime':{'python':sys.version,'platform':platform.platform(),'pyyaml_version':yaml.__version__,'pyyaml_path':yaml.__file__},'artifact_code_executed':False})
 save(out/'SELECTION_MANIFEST_V1.json',{'selection':selected,'groups':omitted,'total_source_files':len(selected),'scope':'audit-independent readiness sample; compare implementation selection before benchmark'})
 save(out/'SCHEMA_AND_LABEL_ASSESSMENT_V1.json',{'files':rows,'errors':errors,'target_free_mapping':'AUDIT-ONLY PROPOSAL; not frozen learner contract','episode_policy':'reset at each source episode; no cross-episode or cross-file flattening','semantic_conclusion':'last-event success labels do not establish whole-word AND acceptance; full-word solver compatibility cannot measure physical-host recovery','production_log_origin_verified':False,'simulator_artifact_origin_verified':True})
 print(json.dumps({'selected':len(selected),'groups':len(groups),'parsed':len(rows),'errors':len(errors)}))
if __name__=='__main__':main()

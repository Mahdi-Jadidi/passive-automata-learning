"""Bounded original-event semantic-obstruction scan; not a solver/model run."""
import hashlib,json,zipfile
from pathlib import Path
import yaml
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def main():
 m=read(A.parent/'inventory/prepared_v1/faithful_records_and_metadata.json');receipt=read(A/'preparation_v1/PROVENANCE_V1.json');scans=[];found=[]
 with zipfile.ZipFile(receipt['archive']['path']) as z:
  for trace in m['traces']:
   events=trace['events'];member=trace['archive_member'];maps={};rawbytes=z.read(member);assert hashlib.sha256(rawbytes).hexdigest()==trace['source_sha256']
   if '/cage2/' in member:
    records=yaml.load(rawbytes,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader))
    for si,r in enumerate(records):
     d={}
     for host,info in r['Blue'].get('obs',{}).items():
      if not isinstance(info,dict):continue
      for interface in info.get('Interface',[]):
       ip=interface.get('IP Address')
       if ip:d.setdefault(ip,set()).add(host)
     maps[si]=d
   def host(e):
    a=e['raw_action'];h=a.get('hostname')
    if h:return h,'explicit_observed_action_hostname'
    ip=a.get('ip_address');hs=maps.get(e['location']['step_index'],{}).get(ip,set())
    if len(hs)==1:return next(iter(hs)),'unique_current_record_Blue_observation_IP_lookup_evaluation_only'
    return None,'unresolved_or_global'
   candidates=0
   for j in range(len(events)-2):
    triple=events[j:j+3]
    if [e['outcome'] for e in triple]!=[True,False,True]:continue
    candidates+=1;ha,ea=host(triple[1]);hb,eb=host(triple[2])
    if not ha or not hb or ha==hb:continue
    # Exact atomic original action identity, protected diagnostic only, no labels.
    word=['d'+hashlib.sha256(canon(e['raw_action']).encode()).hexdigest() for e in events[:j+3]];p,n,q=word[:-2],word[:-1],word;a,b=word[-2:];assert a!=b
    project=lambda w,B:[x for x in w if x in B]
    # Constructed two-block completion witnesses the algebra. General proof uses
    # only a,b assigned distinct blocks; unknown prefix symbols may be anywhere.
    block_a={a};block_other=set(q)-{a};assert b in block_other
    assert project(n,block_a)==project(q,block_a) and project(n,block_other)==project(p,block_other)
    found.append({'witness_id':f'C025-OBSERVED-AND-{len(found)+1:03}','source':member,'source_sha256':trace['source_sha256'],'trace_id':trace['trace_id'],'episode_container_index':trace['episode_container_index'],'three_positions':[{'event_index':j+k,'source_location':e['location'],'raw_outcome':e['raw_outcome'],'outcome':e['outcome'],'raw_action':e['raw_action']} for k,e in enumerate(triple)],'failing_event_observed_target':ha,'following_success_observed_target':hb,'target_evidence':[ea,eb],'prefixes':{'positive_before':p,'negative':n,'positive_after':q},'prefix_sha256':{tag:hashlib.sha256(canon(w).encode()).hexdigest() for tag,w in [('p',p),('n',n),('q',q)]},'independent_projection_check':True,'claim':'actual source-linked True/False/True event pattern with distinct observed targets; conditional AND obstruction for any proposed ownership assigning endpoint a,b to different blocks; not evidence of physical coupling or proof targets are independent factors'})
    break
   scans.append({'source':member,'events':len(events),'True_False_True_patterns':candidates,'source_sha256':trace['source_sha256']})
 report={'scope':'18 original selected complete event streams, including failures/unlabeled events; no top8 filtering','scans':scans,'witnesses':found,'solver_runs':0,'host_map_leaked_to_solver':False,'interpretation':'source-backed semantic mismatch diagnostic conditional on distinct endpoint ownership; not physical-host recovery accuracy'}
 with (A/'OBSERVED_AND_OBSTRUCTION_V1.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps({'sources_scanned':len(scans),'witnesses':len(found),'first_witness':found[0] if found else None},ensure_ascii=False))
if __name__=='__main__':main()

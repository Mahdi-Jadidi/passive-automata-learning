"""Independent reconstruction of implementation ingestion from original ZIP bytes.
No implementation/artifact imports and no solver calls. Audits only the 3 declared pools.
"""
import ast,collections,hashlib,json,sys,zipfile
from pathlib import Path
import yaml
A=Path(__file__).resolve().parent;ROOT=A.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def main():
 prepared=Path(sys.argv[1]);manifest=read(prepared/'manifest.json');assert manifest['status']=='prepared_observations_only';observed=read(prepared/'observations.json');qualified=read(prepared/'observations_target_qualified.json');metadata=read(prepared/'faithful_records_and_metadata.json');vocab=read(prepared/'token_dictionary.json');qdict=read(prepared/'target_qualified_dictionary_metadata.json')['dictionary'];rows=[];errors=[];expected=[];qexpected=[];signatures=[]
 zp=Path(read(A/'preparation_v1/PROVENANCE_V1.json')['archive']['path'])
 for name,digest in manifest['output_hashes'].items():assert sha((prepared/name).read_bytes())==digest
 with zipfile.ZipFile(zp) as z:
  for group in manifest['sources']:
   files=group['files'];prefix=files[0]['archive_member'].rsplit('/',1)[0]+'/';suffix='.yaml' if group['scenario']=='cage2_raw' else '.txt';allnames=sorted(n for n in z.namelist() if n.startswith(prefix) and n.endswith(suffix));assert [f['archive_member'] for f in files]==allnames[:6]
   for f in files:
    try:
     raw=z.read(f['archive_member']);assert sha(raw)==f['sha256'] and len(raw)==f['bytes'];israw=suffix=='.yaml';d=yaml.load(raw,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader)) if israw else ast.literal_eval(raw.decode());episodes=[d] if israw else d
     for ei,episode in enumerate(episodes):
      stream=[];qstream=[];loc=[]
      for si,step in enumerate(episode):
       pair=[step[a] for a in ['Blue','Red']] if israw else step
       assert len(pair)==2
       for ai,e in enumerate(pair):
        actor=['Blue','Red'][ai]
        if not israw:assert e['agent']==actor and pair[0]['step']==pair[1]['step'] and pair[0]['episode']==pair[1]['episode']
        a=e['action'] if israw else {k:v for k,v in e.items() if k not in ['episode','step','agent','success']};desc={'action':a['type'] if israw else a['action']}
        for k in ['exploit_class','exploit_port']:
         if k in a and a[k] is not None:desc[k]=a[k]
        token='e'+sha(canonical(desc).encode());assert vocab[token]==desc
        qdesc={**desc,'observed_target_fields':{k:a[k] for k in ['hostname','ip_address','subnet','subnetname'] if k in a}};qt='q'+sha(canonical(qdesc).encode());assert qdict[qt]==qdesc
        if israw:
         code=episode[si+1][actor]['obs'].get('prev_action_status') if si+1<len(episode) else None;label=code==1 if type(code)is int and code in [1,3] else None
        else:code=e.get('success');label=True if code=='TRUE' else False if code=='FALSE' else None
        stream.append({'id':token,'outcome':label});qstream.append({'id':qt,'outcome':label});loc.append({'actor':actor,'step':si,'code':code})
      ti=len(expected);assert observed['traces'][ti]['events']==stream and qualified['traces'][ti]['events']==qstream;side=metadata['traces'][ti];assert side['archive_member']==f['archive_member'] and side['episode_container_index']==ei and len(side['events'])==len(stream)
      for i,(event,l) in enumerate(zip(side['events'],loc)):
       assert event['location']['actor']==l['actor'] and event['location']['step_index']==l['step'] and event['raw_outcome']==l['code'] and event['token_id']==stream[i]['id'] and event['outcome']==stream[i]['outcome']
       if israw:assert event['location']['outcome_step_index']==(l['step']+1 if l['step']+1<len(episode) else None)
      expected.append(stream);qexpected.append(qstream);signatures.append((f['archive_member'],ei,tuple((v['id'],v['outcome']) for v in stream)))
     rows.append({'source':f['archive_member'],'status':'verified_from_original_bytes','sha256':sha(raw)})
    except Exception as e:errors.append({'failure_id':'C025-INGEST-'+str(len(rows)+len(errors)+1).zfill(3),'source':f['archive_member'],'error':repr(e)})
 assert len(expected)==len(observed['traces'])==len(qualified['traces'])
 overlap=[]
 for i,(a,ea,x) in enumerate(signatures):
  for b,eb,y in signatures[:i]:
   if x[:min(len(x),len(y))]==y[:min(len(x),len(y))]:overlap.append({'left':a,'right':b,'kind':'identical' if len(x)==len(y) else 'prefix_overlap','events':min(len(x),len(y))})
 report={'status':'verified' if not errors else 'rejected','sources_checked':len(rows),'episodes_checked':len(expected),'events_checked':sum(map(len,expected)),'errors':errors,'rows':rows,'selected_source_lineage_overlaps':overlap,'target_free_mapping_matches':not errors,'qualified_mapping_matches':not errors,'solver_executed':False,'known_host_full_alphabet_baseline':'still required before model benchmark; no host interpretation inferred','dataset_independence':'not established by separate file, policy, trial or source family names'}
 with (A/'INGESTION_REPLAY_V1.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:v for k,v in report.items() if k not in ['rows','selected_source_lineage_overlaps']}))
if __name__=='__main__':main()

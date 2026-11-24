"""Compact CSV from complete run summaries; archived references read only after execution."""
import argparse,csv,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('batch',type=Path);p.add_argument('references',type=Path);p.add_argument('csv',type=Path);a=p.parse_args();config=json.loads((a.batch/'config.json').read_text())
fields='case,engine,repeat,producer_status,replay_status,lower,upper,reference_cost,reference_match,producer_compute_s,producer_wall_s,producer_rss_kib,replay_compute_s,replay_wall_s,replay_rss_kib,attempts,responses,response_bytes,artifact_bytes,input_sha256'.split(',')
rows=[]
for f in sorted(a.batch.glob('*/summary.json')):
 d=json.loads(f.read_text()); case,e,rep=f.parent.name.split('--');ref=json.loads((a.references/(case+'.json')).read_text());raw=json.loads((f.parent/'input.json').read_text());n=len(raw['alphabet']);cost=n-len(ref['blocks']);assert d['input_sha256']==hashlib.sha256((f.parent/'input.json').read_bytes()).hexdigest();assert d['operational_status']=='INCOMPLETE' and d['external_attempts']==0
 if e=='p1':
  prod=d['produce'];ver=d.get('replay',{});status=prod['process_status'];vs=ver.get('status',ver.get('process_status','NOT_RUN'));lo=ver.get('lower');hi=ver.get('upper');att=res=wire=0;art=d['artifact_bytes'];pc=prod.get('compute_s');pw=prod.get('wall_s');pr=prod.get('rss_kib');vc=ver.get('compute_s');vw=ver.get('wall_s');vr=ver.get('rss_kib')
 else:
  prod=d['producer'];ver=d['verifier'];status=d.get('producer_status') or prod['process_status'];vs=ver.get('result',{}).get('status',ver.get('process_status'));lo=d['structural_lower_cost'];hi=d['structural_upper_cost'];att=d['local_attempts_observed'];res=d['local_responses_observed'];wire=d['local_response_json_bytes_observed'];art=d['producer_artifact_bytes'];pc=prod.get('compute_seconds');pw=prod.get('wall_seconds');pr=prod.get('peak_rss_kib');vc=ver.get('compute_seconds');vw=ver.get('wall_seconds');vr=ver.get('peak_rss_kib')
 match=(lo==cost and hi==cost) if hi is not None else None
 if hi is not None and not match: raise ValueError('reference mismatch '+case)
 if lo is not None and lo>cost: raise ValueError('lower exceeds reference '+case)
 rows.append([case,e,rep,status,vs,lo,hi,cost,match,pc,pw,pr,vc,vw,vr,att,res,wire,art,d['input_sha256']])
with a.csv.open('w',newline='') as o:
 w=csv.writer(o,lineterminator='\n');w.writerow(fields);w.writerows([[format(v,'.9f') if isinstance(v,float) else v for v in row] for row in rows])
print('records',len(rows),'planned',len(config['cases'])*len(config['engines'])*config['repetitions'])

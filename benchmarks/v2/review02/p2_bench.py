"""Measure exact P2 producer, core ledger and independent proof ledger on raw input.
Three capped workers; structural-only, no authenticated external receipts.
"""
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CORE='539af04bb0b097de5704c28f2b82f23cea5ef783'
PROOF='db8fb33a5726c779e385544219e39db662a6cb5b'
BLOBS={'p2/selector_v2/core.py':'997304c3adce9d3148d454b079639575f419ba0e','p2/selector_v2/sparse_analysis.py':'f773cc1c6b1a852193ba2afb75aa2fce4941a5c2','p2/selector_v2/component_closure.py':'97844bc266556cc04cd54a75c0d57dc00d6709ea','p2/selector_v2/schema.py':'65a7522a8442a184c14f7a0fa74fc307ce60229f','p2/selector_v2/evidence_store.py':'42e38c8ee590267b292ebc0d678e9d4f3a56849b','proof/independent_replay.py':'aa09243fa7ccc941c37609e959aefb419075df32','proof/production_replay.py':'f0bfa1785b49aab010f2af69e0e14c0af46d577c','proof/ledger_replay.py':'c2ae28e42a71aab91f329cf728ab7a95538cbf4e'}
def verify_sources(root):
 for path,expected in BLOBS.items():
  b=(root/path).read_bytes(); actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  if actual!=expected: raise ValueError('source mismatch: '+path)
def worker(a):
 resource.setrlimit(resource.RLIMIT_AS,(a.memory*2**20,)*2)
 t=time.perf_counter(); raw=json.loads(a.input.read_bytes()); parse_s=time.perf_counter()-t
 if set(raw)!={'alphabet','positive','negative'}: raise ValueError('input-only schema')
 out={'input_parse_s':parse_s}
 if a.stage in ('closure','ledger'):
  sys.path.insert(0,str(a.sources/'p2'))
  from selector_v2.core import Sample,PartitionRef,Budget
  from selector_v2.schema import canonical,scope
  from selector_v2.component_closure import component_closure,structural_record
  from selector_v2.evidence_store import EvidenceLedger
  t=time.perf_counter(); s=Sample.from_input(raw); out['encode_s']=time.perf_counter()-t
  if a.stage=='closure':
   t=time.perf_counter(); c=component_closure(s,Budget(seconds=a.seconds));out['closure_s']=time.perf_counter()-t
   out.update(state=c['state'],epochs=sum(r['kind']=='COMPONENT_EPOCH' for r in c['records']),facts=sum(len(r['payload'].get('facts',[])) for r in c['records']),edges=sum(len(r['payload'].get('edges',[])) for r in c['records']))
   records=c['records'];t=time.perf_counter()
   if c['state']!='LABEL_CONFLICT':
    check=structural_record(s,PartitionRef(tuple(c['owner']))); records=records+[check];out['compatible']=check['payload']['compatible']
   out['structural_s']=time.perf_counter()-t;t=time.perf_counter()
   (a.output/'scope.json').write_bytes(canonical(scope(s)));(a.output/'producer-records.json').write_bytes(canonical(records));out['serialize_s']=time.perf_counter()-t
  else:
   t=time.perf_counter(); records=json.loads((a.output/'producer-records.json').read_bytes());out['record_parse_s']=time.perf_counter()-t
   t=time.perf_counter(); l=EvidenceLedger(s); ok=l.append(records);out['ingest_s']=time.perf_counter()-t;out['accepted']=ok
   if not ok: raise ValueError('ledger quarantine: '+str(l.quarantine[0][1]))
   t=time.perf_counter(); payload=canonical(list(l.records));(a.output/'ledger-records.json').write_bytes(payload);out['export_s']=time.perf_counter()-t;out['exact_export_match']=payload==(a.output/'producer-records.json').read_bytes();out['records']=len(records)
   if not out['exact_export_match']: raise ValueError('export mismatch')
 else:
  sys.path.insert(0,str(a.sources/'proof'))
  from ledger_replay import replay_ledger_json
  if 'selector_v2.core' in sys.modules: raise RuntimeError('producer imported in independent replay')
  t=time.perf_counter(); result=replay_ledger_json(a.input.read_text(),(a.output/'scope.json').read_text(),(a.output/'ledger-records.json').read_text());out['replay_s']=time.perf_counter()-t
  out.update({k:result[k] for k in ('mandatory_floor','closure_state','label_conflict','structural_optimum','operational_status','observations')})
  if out['operational_status']!='INCOMPLETE': raise ValueError('invalid operational claim')
 out['rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;print(json.dumps(out))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--sources',type=Path,default=ROOT);p.add_argument('--seconds',type=float,default=5);p.add_argument('--memory',type=int,default=512);p.add_argument('--stage',choices=['closure','ledger','replay']);a=p.parse_args()
 if a.stage: worker(a);return
 verify_sources(a.sources);a.output.mkdir(parents=True,exist_ok=False);b=a.input.read_bytes();snapshot=a.output/'input.json';snapshot.write_bytes(b)
 out={'core_ref':CORE,'proof_ref':PROOF,'input_sha256':hashlib.sha256(b).hexdigest(),'seconds_per_stage':a.seconds,'memory_as_mib':a.memory,'host':platform.platform(),'python':sys.version,'operational_status':'INCOMPLETE','external_attempts':0,'external_response_bytes':0}
 for stage in ('closure','ledger','replay'):
  t=time.perf_counter();cmd=[sys.executable,'-B',str(Path(__file__).resolve()),str(snapshot),str(a.output),'--sources',str(a.sources),'--seconds',str(a.seconds),'--memory',str(a.memory),'--stage',stage]
  try:
   q=subprocess.run(cmd,capture_output=True,timeout=a.seconds+1,env={**os.environ,'PYTHONHASHSEED':'0'});(a.output/(stage+'.stderr')).write_bytes(q.stderr);(a.output/(stage+'.stdout')).write_bytes(q.stdout)
   if q.returncode==0: m={'status':'OK',**json.loads(q.stdout)}
   else: m={'status':'MEMORY_ERROR' if b'MemoryError' in q.stderr else 'ERROR','returncode':q.returncode}
  except subprocess.TimeoutExpired as e:
   (a.output/(stage+'.stderr')).write_bytes(e.stderr or b'');(a.output/(stage+'.stdout')).write_bytes(e.stdout or b'');m={'status':'TIMEOUT'}
  out[stage]={**m,'wall_s':time.perf_counter()-t}
  if m['status']!='OK':break
 out['ledger_bytes']=(a.output/'ledger-records.json').stat().st_size if (a.output/'ledger-records.json').exists() else None
 (a.output/'summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

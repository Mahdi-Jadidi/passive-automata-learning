"""Benchmark-only raw journal/2 replay (not full outer provenance)."""
import argparse, hashlib, json, os, platform, resource, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BLOBS={'core/selector_v2/core.py':'997304c3adce9d3148d454b079639575f419ba0e','core/selector_v2/sparse_analysis.py':'f773cc1c6b1a852193ba2afb75aa2fce4941a5c2','core/selector_v2/component_closure.py':'97844bc266556cc04cd54a75c0d57dc00d6709ea','core/selector_v2/schema.py':'65a7522a8442a184c14f7a0fa74fc307ce60229f','core/selector_v2/evidence_store.py':'42e38c8ee590267b292ebc0d678e9d4f3a56849b','core/selector_v2/registered_ledger.py':'092507fc156e604be242e3100117fedc27b96d04','interface/adapter.py':'c38e441c7327a44adad8a0fe1125d45c93e8ef69','interface/strict_ledger.py':'a66975de137e3ec556b8c7aacd108cf975c46344','proof/independent_replay.py':'aa09243fa7ccc941c37609e959aefb419075df32','proof/production_replay.py':'f0bfa1785b49aab010f2af69e0e14c0af46d577c','proof/ledger_replay.py':'c2ae28e42a71aab91f329cf728ab7a95538cbf4e'}
def worker(a):
    resource.setrlimit(resource.RLIMIT_AS,(a.memory*2**20,)*2)
    t=time.perf_counter(); raw=json.loads(a.input.read_bytes()); m={'parse_s':time.perf_counter()-t}
    if set(raw)!={'alphabet','positive','negative'}: raise ValueError('raw-only sample required')
    if a.stage in ('closure','journal'):
        sys.path[:0]=[str(a.sources/'core'),str(a.sources/'interface')]
        from selector_v2.core import Sample, PartitionRef, Budget
        from selector_v2.schema import canonical,scope
        from selector_v2.component_closure import component_closure,structural_record
        from selector_v2.registered_ledger import RegisteredLedger
        import adapter
        from strict_ledger import parse
        t=time.perf_counter(); s=Sample.from_input(raw); m['encode_s']=time.perf_counter()-t
        if a.stage=='closure':
            t=time.perf_counter(); c=component_closure(s,Budget(seconds=a.seconds)); m['closure_s']=time.perf_counter()-t
            m.update(state=c['state'],epochs=sum(r['kind']=='COMPONENT_EPOCH' for r in c['records']),facts=sum(len(r['payload'].get('facts',[])) for r in c['records']),edges=sum(len(r['payload'].get('edges',[])) for r in c['records']))
            records=c['records']; t=time.perf_counter()
            if c['state']!='LABEL_CONFLICT':
                check=structural_record(s,PartitionRef(tuple(c['owner']))); records=records+[check]; m['compatible']=check['payload']['compatible']
            m['structural_s']=time.perf_counter()-t; t=time.perf_counter()
            (a.output/'scope.json').write_bytes(canonical(scope(s)));(a.output/'records.json').write_bytes(canonical(records));m['serialize_s']=time.perf_counter()-t
        else:
            t=time.perf_counter(); ledger=RegisteredLedger(raw,adapter=adapter,parse=parse);m['journal_init_s']=time.perf_counter()-t
            records=json.loads((a.output/'records.json').read_bytes());t=time.perf_counter();ledger.append_raw(records);m['ingest_s']=time.perf_counter()-t
            t=time.perf_counter(); b=ledger.export();(a.output/'journal.json').write_bytes(b);m['export_s']=time.perf_counter()-t
            if ledger.export_records()!=(a.output/'records.json').read_bytes(): raise ValueError('record projection changed')
            m['journal_bytes']=len(b);m['events']=len(ledger.journal)
    else:
        sys.path.insert(0,str(a.sources/'proof'))
        from independent_replay import load_json, sample_data, require
        import production_replay
        from ledger_replay import replay_ledger
        if any(k.startswith('selector_v2') for k in sys.modules): raise RuntimeError('producer imported')
        if a.replay=='filter':
            from bounded_join import expected_deletions
            production_replay.expected_deletions=expected_deletions
        t=time.perf_counter(); b=(a.output/'journal.json').read_bytes(); j=load_json(b); sc=load_json((a.output/'scope.json').read_bytes())
        require(set(j)=={'version','sample_digest','events'} and j['version']=='selector-v2-journal/2','bad raw journal envelope')
        require(json.dumps(j,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()==b,'noncanonical journal')
        require(j['sample_digest']==sample_data(raw)[3],'sample binding')
        records=[]
        for e in j['events']:
            require(set(e)=={'event','records'} and e['event']=='RAW' and type(e['records']) is list and bool(e['records']),'raw-only envelope required')
            require(all(r['origin']=='RAW' and r['kind'] in ('COMPONENT_EPOCH','STRUCTURAL_CHECK','LABEL_CONFLICT','DELETE_EQUAL') for r in e['records']),'nonraw record')
            records.extend(e['records'])
        result=replay_ledger(raw,sc,records);m['replay_s']=time.perf_counter()-t
        if result['operational_status']!='INCOMPLETE': raise ValueError('operational authority forbidden')
        m.update({k:result[k] for k in ('closure_state','mandatory_floor','structural_optimum','label_conflict','operational_status')})
    m['rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;print(json.dumps(m))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--sources',type=Path,default=ROOT);p.add_argument('--seconds',type=float,default=30);p.add_argument('--memory',type=int,default=1536);p.add_argument('--replay',choices=('literal','filter'),default='filter');p.add_argument('--stage',choices=('closure','journal','replay'));a=p.parse_args()
    if not 0<a.seconds<float('inf') or a.memory<=0: p.error('invalid limits')
    if a.stage: worker(a);return
    for name,expected in BLOBS.items():
        b=(a.sources/name).read_bytes()
        if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=expected: raise ValueError('blob mismatch: '+name)
    a.output.mkdir(parents=True,exist_ok=False);b=a.input.read_bytes();snap=a.output/'input.json';snap.write_bytes(b)
    result=dict(core='4e21dbf0d06c030681e774cb15f1a5cf0c802f0d',proof='ed20d9b12ea9730e07e7d2d1e0581744a266eb02',interface='b27850a667a55927fd3ad127dccce3956d8ead22',host=platform.platform(),python=sys.version,input_sha256=hashlib.sha256(b).hexdigest(),seconds_per_stage=a.seconds,memory_as_mib=a.memory,replay_mode=a.replay,operational_status='INCOMPLETE',external_attempts=0)
    for stage in ('closure','journal','replay'):
        cmd=[sys.executable,'-B',str(Path(__file__).resolve()),str(snap),str(a.output),'--sources',str(a.sources),'--seconds',str(a.seconds),'--memory',str(a.memory),'--replay',a.replay,'--stage',stage];t=time.perf_counter()
        try:
            q=subprocess.run(cmd,capture_output=True,timeout=a.seconds+1,env={**os.environ,'PYTHONHASHSEED':'0'});(a.output/(stage+'.stdout')).write_bytes(q.stdout);(a.output/(stage+'.stderr')).write_bytes(q.stderr)
            m={'status':'OK',**json.loads(q.stdout)} if q.returncode==0 else {'status':'MEMORY_ERROR' if b'MemoryError' in q.stderr else 'ERROR','returncode':q.returncode}
        except subprocess.TimeoutExpired as e:
            (a.output/(stage+'.stdout')).write_bytes(e.stdout or b'');(a.output/(stage+'.stderr')).write_bytes(e.stderr or b'');m={'status':'TIMEOUT'}
        result[stage]={**m,'wall_s':time.perf_counter()-t}
        if m['status']!='OK':break
    result['verification_status']='VERIFIED_RAW_ONLY' if result.get('replay',{}).get('status')=='OK' else 'INCOMPLETE'
    (a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()

"""Hybrid-only extension: preserve original harness/corpus/raw timing bytes."""
import argparse, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
import check_contract as cc
HERE=Path(__file__).resolve().parent
CORPUS='013e2b60dc1d5740d766a9b0f77c458c4fbb92f203ee67977f3fe7104b48215b'
PREVIOUS='65a69bc5cd07a2d897e2171faede6ec9ee9dd50774276bba3970ddce10e480ee'

def child(source,sha,index):
    p=Path(source).resolve()
    if cc.digest(p)!=sha: raise RuntimeError('hybrid source hash changed')
    rows=[json.loads(x) for x in (HERE/'timing_cases.jsonl').read_text(encoding='utf8').splitlines()]
    solve=cc.load(p,'timed_hybrid').solve
    start=time.perf_counter_ns(); result=solve(rows[index]['input']); elapsed=time.perf_counter_ns()-start
    print(json.dumps({'solve_ns':elapsed,'result':result},ensure_ascii=False,separators=(',',':')))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['correctness','timing','child'],required=True); ap.add_argument('--source',required=True); ap.add_argument('--sha',required=True); ap.add_argument('--case',type=int); a=ap.parse_args()
    a.sha=a.sha.lower(); source=Path(a.source).resolve()
    if cc.digest(source)!=a.sha: raise RuntimeError('hybrid source hash mismatch')
    if a.mode=='child': return child(source,a.sha,a.case)
    if a.mode=='correctness':
        cc.SOURCES['HYBRID']=(source,'solve'); sys.argv=[sys.argv[0],'--solver','HYBRID','--sha',a.sha]; return cc.main()
    assert cc.digest(HERE/'timing_cases.jsonl')==CORPUS
    assert cc.digest(HERE/'timing_raw.jsonl')==PREVIOUS
    out=HERE/'hybrid_timing_raw.jsonl'
    if out.exists(): raise RuntimeError('refusing to overwrite hybrid raw results')
    rows=[json.loads(x) for x in (HERE/'timing_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=[json.loads(x) for x in (HERE/'timing_raw.jsonl').read_text(encoding='utf-8').splitlines()]
    metadata={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'processor':platform.processor(),'cpu_count':os.cpu_count(),'timeout_seconds':20,'repeats':3,'timing_corpus_sha256':CORPUS,'previous_raw_sha256':PREVIOUS,'hybrid_source_sha256':a.sha,'start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'comparison':'later sequential run; not interleaved with baseline trials'}
    (HERE/'hybrid_timing_environment.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
    with out.open('x',encoding='utf8',newline='\n') as f:
        for i,row in enumerate(rows):
            for rep in range(3):
                cmd=[sys.executable,str(Path(__file__).resolve()),'--mode','child','--source',str(source),'--sha',a.sha,'--case',str(i)]
                started=time.perf_counter_ns(); status='OK'; stdout=''; stderr=''; rc=None
                try:
                    p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=20); rc=p.returncode; stdout=p.stdout; stderr=p.stderr
                    if rc: status='ERROR'
                except subprocess.TimeoutExpired as e:
                    status='TIMEOUT'; stdout=(e.stdout or b'').decode('utf8','replace') if isinstance(e.stdout,bytes) else (e.stdout or ''); stderr=(e.stderr or b'').decode('utf8','replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
                elapsed=time.perf_counter_ns()-started
                item={'case':row['case'],'case_index':i,'repeat':rep,'solver':'HYBRID','sha256':a.sha,'status':status,'startup_wall_ns':elapsed,'returncode':rc,'stdout':stdout,'stderr':stderr,'command':cmd}
                if status=='OK':
                    try:
                        parsed=json.loads(stdout); item['solve_ns']=parsed['solve_ns']; item['result']=parsed['result']
                        expected=[x['result'] for x in prior if x['case']==row['case'] and x['solver']=='C028' and x['status']=='OK']
                        item['matches_prior_c028']=len(expected)==3 and all(x==parsed['result'] for x in expected)
                    except (ValueError,KeyError,TypeError): item['status']='ERROR_PARSE'
                f.write(json.dumps(item,ensure_ascii=False,separators=(',',':'))+'\n'); f.flush()
                print(f"{row['case']} rep={rep} {item['status']} match={item.get('matches_prior_c028')}",flush=True)
if __name__=='__main__': main()

"""Frozen full-contract timing: parent watchdog, child in-process time."""
import argparse, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
import check_contract as cc
HERE=Path(__file__).resolve().parent
CORPUS='013e2b60dc1d5740d766a9b0f77c458c4fbb92f203ee67977f3fe7104b48215b'
def child(solver,row,expected_sha):
    path,entry=cc.SOURCES[solver]
    if cc.digest(path)!=expected_sha: raise RuntimeError('source hash changed')
    func=getattr(cc.load(path,'timed_'+solver),entry)
    t=time.perf_counter_ns(); result=func(row['input']); elapsed=time.perf_counter_ns()-t
    print(json.dumps({'solve_ns':elapsed,'result':result},ensure_ascii=False,separators=(',',':')))
def parent(shas):
    assert cc.digest(HERE/'timing_cases.jsonl')==CORPUS
    rows=[json.loads(x) for x in (HERE/'timing_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    names=['C028','C030','DP','GRAPH']
    for name in names:
        if cc.digest(cc.SOURCES[name][0])!=shas[name]: raise RuntimeError('source changed: '+name)
    out=HERE/'timing_raw.jsonl';
    if out.exists(): raise RuntimeError('refusing to overwrite raw results')
    meta={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'processor':platform.processor(),'cpu_count':os.cpu_count(),'timeout_seconds':20,'repeats':3,'timing_corpus_sha256':CORPUS,'sources':shas,'clock':'perf_counter_ns','start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (HERE/'timing_environment.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with out.open('x',encoding='utf-8',newline='\n') as f:
        for ci,row in enumerate(rows):
            for rep in range(3):
                rotated=names[(ci+rep)%4:]+names[:(ci+rep)%4]
                for name in rotated:
                    cmd=[sys.executable,str(Path(__file__).resolve()),'--child',name,'--case',str(ci),'--sha',shas[name]]
                    started=time.perf_counter_ns(); status='OK'; stdout=''; stderr=''; returncode=None
                    try:
                        p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=20)
                        returncode=p.returncode; stdout=p.stdout; stderr=p.stderr
                        if p.returncode: status='ERROR'
                    except subprocess.TimeoutExpired as e:
                        status='TIMEOUT'; stdout=(e.stdout or b'').decode('utf-8','replace') if isinstance(e.stdout,bytes) else (e.stdout or ''); stderr=(e.stderr or b'').decode('utf-8','replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
                    elapsed=time.perf_counter_ns()-started
                    item={'case':row['case'],'case_index':ci,'repeat':rep,'solver':name,'sha256':shas[name],'status':status,'startup_wall_ns':elapsed,'returncode':returncode,'stdout':stdout,'stderr':stderr,'command':cmd}
                    if status=='OK':
                        try:
                            parsed=json.loads(stdout); item['solve_ns']=parsed['solve_ns']; item['result']=parsed['result']
                        except (ValueError,KeyError,TypeError): item['status']='ERROR_PARSE'
                    f.write(json.dumps(item,ensure_ascii=False,separators=(',',':'))+'\n'); f.flush()
                    print(f"{ci+1}/{len(rows)} {row['case']} rep={rep} {name} {item['status']}",flush=True)
    # A solve is comparable only if every successful result on its case agrees.
    data=[json.loads(s) for s in out.read_text(encoding='utf-8').splitlines()]
    for row in rows:
        subset=[r for r in data if r['case']==row['case'] and r['status']=='OK']
        outputs={json.dumps(r['result'],sort_keys=True,ensure_ascii=False) for r in subset}
        print('OUTPUT_AGREEMENT',row['case'],len(outputs)==1,'successful',len(subset),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--child',choices=cc.SOURCES); ap.add_argument('--case',type=int); ap.add_argument('--sha'); ap.add_argument('--shas-file'); a=ap.parse_args()
    if a.child:
        rows=[json.loads(x) for x in (HERE/'timing_cases.jsonl').read_text(encoding='utf-8').splitlines()]; child(a.child,rows[a.case],a.sha)
    else: parent(json.loads(Path(a.shas_file).read_text(encoding='utf-8-sig')))

"""Full-output comparison; raw trials, fixed corpus, isolated subprocesses."""
import hashlib, importlib.util, json, os, platform, statistics, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CORPUS=ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'
PATHS={
 'reference':ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py',
 'hybrid':ROOT/'results/2026-11-13/exact_candidates_v33/candidate_dp/hybrid/candidate.py',
 'sat':ROOT/'results/2026-11-14/full_engines_v35/logic/candidate.py',
 'hypergraph':ROOT/'results/2026-11-14/full_engines_v35/hypergraph/candidate.py',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def child(name,index):
    row=[json.loads(s) for s in CORPUS.read_text(encoding='utf-8').splitlines()][index]
    spec=importlib.util.spec_from_file_location('tested',PATHS[name]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    started=time.perf_counter_ns(); result=mod.solve(row['input']); elapsed=time.perf_counter_ns()-started
    print(json.dumps({'result':result,'solve_ns':elapsed},ensure_ascii=True))
def main():
    names=list(PATHS); rows=[json.loads(s) for s in CORPUS.read_text(encoding='utf-8').splitlines()]
    out=HERE/'trials.jsonl'
    if out.exists(): raise RuntimeError('refuse to overwrite trial evidence')
    meta={'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),'sources':{k:sha(v) for k,v in PATHS.items()},'corpus_sha256':sha(CORPUS),'timeout_seconds':3,'repeats':3,'clock':'perf_counter_ns'}
    with out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps({'meta':meta})+'\n'); stream.flush()
        for i,row in enumerate(rows):
            for rep in range(3):
                for name in names[(i+rep)%4:]+names[:(i+rep)%4]:
                    start=time.perf_counter_ns(); rec={'case':row['case'],'solver':name,'repeat':rep}
                    try:
                        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',name,str(i)],capture_output=True,text=True,timeout=3)
                        rec.update(exit_code=p.returncode,stderr=p.stderr,stdout=p.stdout)
                        if p.returncode: rec['status']='ERROR'
                        else:
                            data=json.loads(p.stdout); rec.update(data); rec['status']=data['result']['status'] if data['result']['status'] in ('INCOMPLETE','ERROR','INVALID_INPUT') else 'COMPLETED'
                    except subprocess.TimeoutExpired as exc:
                        rec.update(status='TIMEOUT',stdout=str(exc.stdout or ''),stderr=str(exc.stderr or ''))
                    except Exception as exc: rec.update(status='ERROR',error=repr(exc))
                    rec['startup_wall_ns']=time.perf_counter_ns()-start
                    stream.write(json.dumps(rec,ensure_ascii=True)+'\n'); stream.flush()
                    print(row['case'],rep,name,rec['status'],flush=True)
    print('DONE',flush=True)
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child': child(sys.argv[2],int(sys.argv[3]))
    else: main()

"""Sequential isolated timing with retained bytes and fixed shared query."""
import hashlib,importlib.util,json,subprocess,sys,time,datetime
from pathlib import Path
A=Path(__file__).resolve().parent
ROOT=A.parents[3]
NEW=A.parent/'implementation/recommend_v1.py'
BASE=ROOT/'results/2026-11-05/search_checkpoint_v24/implementation/integrated_c024_v1/gate_v1.py'
PYTHON=Path('C:/Users/Mahdi/AppData/Local/Python/pythoncore-3.14-64/python.exe')

def load(path):
    sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location('timed_provider',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def worker(mode,path):
    from oracle_v1 import replay
    d=json.loads(Path(path).read_text(encoding='utf-8'));provider=load(NEW if mode=='new' else BASE)
    started=time.perf_counter();deadline=started+20
    if mode=='new':
        result=provider.solve(d,deadline=deadline);rec=result.get('recommendation')
        if rec and rec['optimality_proved']:
            out=dict(maximum_blocks=rec['block_count'],optimum_tieclass=rec['tie_status'],witness=rec['witness'],completed=True)
        else:out=dict(completed=False,result=result)
    else:
        out=dict(completed=False)
        for k in range(len(d['alphabet']),0,-1):
            result=provider.solve(d,known_k=k,deadline=deadline)
            if result['status']=='incompatible':continue
            if result['status']=='certified_unique':out=dict(maximum_blocks=k,optimum_tieclass='unique',witness=result['certificate']['witness'],completed=True)
            elif result['status']=='ambiguous':out=dict(maximum_blocks=k,optimum_tieclass='multiple',witness=result['alternatives'][0],completed=True)
            else:out=dict(completed=False,result=result)
            break
    out['solver_seconds']=time.perf_counter()-started
    if out['completed']:replay(d,out['witness']['blocks'])
    print(json.dumps(out))

def orchestrate():
    freeze=json.loads((A/'PREEXECUTION_FREEZE_V1.json').read_text());assert (A/'PROVIDER_CORRECTNESS_V1.json').exists() and (A/'THEOREM_CHECK_V1.json').exists()
    assert hashlib.sha256(NEW.read_bytes()).hexdigest()=='ff633fb352910005d9ccccd61255c20bcd6679e66dc43d5468610521aab05eb4'
    folder=A/'timing_captures_v2';folder.mkdir(exist_ok=False)
    runs=[]
    for cell in freeze['cells']:
        assert hashlib.sha256(Path(cell['input']).read_bytes()).hexdigest()==cell['sha256']
        for rep in range(3):
            for mode in ['new','baseline']:
                argv=[str(PYTHON),'-B',str(Path(__file__).resolve()),'worker',mode,cell['input']]
                runs.append(dict(cell=cell['id'],rep=rep,mode=mode,argv=argv))
    manifest=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [NEW,BASE,Path(__file__).resolve()]},runs=runs,common_query='maximum_blocks,optimum_tieclass,valid_witness',outer_seconds=25,cooperative_seconds=20)
    with (folder/'MANIFEST_V1.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
    rows=[]
    for index,run in enumerate(runs):
        started=time.perf_counter();row={**run,'attempt':index,'timeout':False}
        try:
            cp=subprocess.run(run['argv'],capture_output=True,timeout=25);stdout,stderr=cp.stdout,cp.stderr;row['exit_code']=cp.returncode
        except subprocess.TimeoutExpired as exc:
            stdout,stderr=exc.stdout or b'',exc.stderr or b'';row.update(timeout=True,exit_code=None)
        row['outer_seconds']=time.perf_counter()-started
        for name,raw in [('stdout',stdout),('stderr',stderr)]:
            path=folder/f'{index:02}_{name}.bin';path.write_bytes(raw);row[name+'_path']=str(path);row[name+'_sha256']=hashlib.sha256(raw).hexdigest()
        try:row['output']=json.loads(stdout)
        except Exception:row['output']=None
        rows.append(row)
        with (folder/f'{index:02}_result.json').open('x',encoding='utf-8') as f:json.dump(row,f,indent=2)
        print(json.dumps({k:row[k] for k in ['attempt','cell','rep','mode','exit_code','timeout','outer_seconds']}),flush=True)
    with (A/'TIMING_RESULTS_V2.json').open('x',encoding='utf-8') as f:json.dump({'rows':rows},f,indent=2)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker(sys.argv[2],sys.argv[3])
    else:orchestrate()

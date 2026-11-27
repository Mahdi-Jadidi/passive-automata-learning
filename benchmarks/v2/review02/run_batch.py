import argparse, concurrent.futures, json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--seconds',type=float,default=5);p.add_argument('--memory',type=int,default=512);p.add_argument('--jobs',type=int,default=3);p.add_argument('--engines',nargs='+',default=['legacy','enhanced','p1']);p.add_argument('--cases',nargs='+');p.add_argument('--repetitions',type=int,default=1);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
files=sorted(a.inputs.glob('*.json'));files=[f for f in files if a.cases is None or f.stem in a.cases]; assert files
(a.output/'config.json').write_text(json.dumps({'inputs':str(a.inputs),'seconds':a.seconds,'memory':a.memory,'jobs':a.jobs,'engines':a.engines,'repetitions':a.repetitions,'cases':[f.stem for f in files]},indent=2))
def case(f):
 for r in range(1,a.repetitions+1):
  for engine in a.engines:
   out=a.output/f'{f.stem}--{engine}--{r}'; base=[sys.executable,'-B']; common=['--seconds',str(a.seconds),'--memory',str(a.memory)]
   if engine=='p1': cmd=base+[str(ROOT/'sparse_bench.py'),str(ROOT/'pinned-core'),str(f),str(out)]+common
   else: cmd=base+[str(ROOT/('harness.py' if engine=='legacy' else 'review02/enhanced_runner.py')),str(f),str(out),'--engine','legacy','--repo',str(ROOT/('verified-legacy' if engine=='legacy' else 'review02/enhanced-src')),'--verified-snapshot']+common
   t=time.perf_counter()
   try:
    q=subprocess.run(cmd,capture_output=True,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONPATH':str(ROOT)},timeout=2*(a.seconds+1)+20)
    (a.output/(out.name+'.log')).write_bytes(q.stdout+b'\nSTDERR:\n'+q.stderr)
    code=q.returncode
   except subprocess.TimeoutExpired as e:
    (a.output/(out.name+'.log')).write_bytes((e.stdout or b'')+b'\nWRAPPER TIMEOUT\n'+(e.stderr or b''));code='WRAPPER_TIMEOUT'
   print(json.dumps({'case':f.stem,'engine':engine,'repeat':r,'exit':code,'total_wall_s':time.perf_counter()-t,'summary':str(out/'summary.json')}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex: list(ex.map(case,files))

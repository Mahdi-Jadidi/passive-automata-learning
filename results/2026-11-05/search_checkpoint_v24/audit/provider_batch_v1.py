"""Provider adapter only; independent oracle/replay never imports this module."""
import importlib.util,json,sys,time
from pathlib import Path
p=Path(sys.argv[1]).resolve();sys.path.insert(0,str(p.parent));s=importlib.util.spec_from_file_location('audit_provider',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
jobs=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8-sig'))
end=time.perf_counter()+20
for j in jobs:
 if time.perf_counter()>=end:print(json.dumps({'job_id':j['job_id'],'unstarted':True}),flush=True);continue
 try:
  d=json.loads(Path(j['input']).read_text(encoding='utf-8-sig'));k=j.get('api_known_k',None if j['allowed_k'] is None else j['allowed_k'][0]);r=m.solve(d,known_k=k,deadline=time.perf_counter()+j.get('seconds',0.5));print(json.dumps({'job_id':j['job_id'],'result':r},ensure_ascii=False),flush=True)
 except Exception as e:print(json.dumps({'job_id':j['job_id'],'error':repr(e)}),flush=True)

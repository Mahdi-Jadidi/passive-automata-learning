"""Post-new-GO single baseline repair or full candidate; preserves initial rows."""
import hashlib,importlib.util,json,sys,time
from pathlib import Path
A=Path(__file__).resolve().parent
def main():
    name=sys.argv[1];assert name in ['baseline','candidate']
    binding=json.loads((A/'BINDING_V1.json').read_text())[name];source=Path(binding['solver']);assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['solver_sha256']
    spec=importlib.util.spec_from_file_location('continued_gate',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    jobs=json.loads((A/'CASE_MANIFEST_V1.json').read_text())['jobs']
    if name=='baseline':jobs=[j for j in jobs if j['job_id']=='c018_unicode_atomic'];assert len(jobs)==1
    end=time.perf_counter()+45
    for job in jobs:
        row=dict(job_id=job['job_id'],provider=name)
        if time.perf_counter()>=end:row.update(launched=False,execution_status='batch_budget_unstarted')
        else:
            started=time.perf_counter()
            try:
                raw=Path(job['input']).read_bytes();assert hashlib.sha256(raw).hexdigest()==job['input_sha256']
                seconds=2 if job['job_id']=='c018_unicode_atomic' else job.get('deadline_seconds',0.25)
                k=job.get('api_known_k',None if job['allowed_k'] is None else job['allowed_k'][0])
                row.update(launched=True,result=g.solve(json.loads(raw),known_k=k,deadline=min(end,time.perf_counter()+seconds)),budget_seconds=seconds)
            except Exception as exc:row.update(launched=True,execution_error=repr(exc))
            row['elapsed_seconds']=time.perf_counter()-started
        print(json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=='__main__':main()

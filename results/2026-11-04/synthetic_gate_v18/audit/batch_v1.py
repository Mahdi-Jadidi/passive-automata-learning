"""Stream frozen same-contract correctness jobs for ONE provider; post-GO only."""
import hashlib,importlib.util,json,sys,time
from pathlib import Path
A=Path(__file__).resolve().parent
def main():
    binding=json.loads((A/'BINDING_V1.json').read_text());source=Path(binding[sys.argv[1]]['solver'])
    assert hashlib.sha256(source.read_bytes()).hexdigest()==binding[sys.argv[1]]['solver_sha256']
    spec=importlib.util.spec_from_file_location('gate_under_audit',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    end=time.perf_counter()+45
    for job in json.loads((A/'CASE_MANIFEST_V1.json').read_text())['jobs']:
        row=dict(job_id=job['job_id'],provider=sys.argv[1])
        if time.perf_counter()>=end:row.update(launched=False,execution_status='batch_budget_unstarted')
        else:
            started=time.perf_counter()
            try:
                raw=Path(job['input']).read_bytes();assert hashlib.sha256(raw).hexdigest()==job['input_sha256']
                k=job.get('api_known_k',None if job['allowed_k'] is None else job['allowed_k'][0])
                deadline=min(end,time.perf_counter()+job.get('deadline_seconds',0.25))
                row.update(launched=True,result=module.solve(json.loads(raw),known_k=k,deadline=deadline))
            except Exception as e:row.update(launched=True,execution_error=repr(e))
            row['elapsed_seconds']=time.perf_counter()-started
        print(json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=='__main__':main()

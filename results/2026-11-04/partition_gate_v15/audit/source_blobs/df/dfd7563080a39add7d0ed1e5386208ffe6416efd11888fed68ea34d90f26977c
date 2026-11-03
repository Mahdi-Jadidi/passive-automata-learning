"""Captured bounded API batch. Unstarted work is never fabricated as a gate result."""
import hashlib,importlib.util,json,time
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
def main():
    binding=json.loads((A/'BINDING_V1.json').read_text());source=Path(binding['solver']['path']);assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['solver']['sha256']
    spec=importlib.util.spec_from_file_location('frozen_gate',source);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    end=time.perf_counter()+175
    for job in json.loads((A/'CASE_MANIFEST_V1.json').read_text())['jobs']:
        row={'job_id':job['job_id']}
        if time.perf_counter()>=end:row.update(launched=False,execution_status='batch_budget_unstarted')
        else:
            started=time.perf_counter()
            try:
                raw=Path(job['input']).read_bytes();assert hashlib.sha256(raw).hexdigest()==job['input_sha256']
                k=job.get('api_known_k',None if job['allowed_k'] is None else job['allowed_k'][0])
                row.update(launched=True,result=gate.solve(json.loads(raw),known_k=k,deadline=min(end,time.perf_counter()+0.5)))
            except Exception as e:row.update(launched=True,execution_error=repr(e))
            row['elapsed_seconds']=time.perf_counter()-started
        print(json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=='__main__':main()

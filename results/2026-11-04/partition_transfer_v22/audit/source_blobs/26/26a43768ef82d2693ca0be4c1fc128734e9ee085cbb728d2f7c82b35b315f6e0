"""Small batch using C020 frozen jobs and exact solver API."""
import hashlib,importlib.util,json,sys,time
from pathlib import Path
A=Path(__file__).resolve().parent

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def main():
    provider=sys.argv[1];binding=read(A/'BINDING_V1.json')[provider];source=A/binding['solver'];assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['solver_sha256'];spec=importlib.util.spec_from_file_location('audit_provider_gate',source);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate);end=time.perf_counter()+45
    for job in read(A/'SMALL_MANIFEST_V2.json')['jobs']:
        row={'provider':provider,'job_id':job['job_id']}
        if time.perf_counter()>=end:row.update(launched=False,execution_status='batch_budget_unstarted')
        else:
            began=time.perf_counter()
            try:
                raw=Path(job['input']).read_bytes();assert hashlib.sha256(raw).hexdigest()==job['input_sha256'];seconds=job.get('deadline_seconds',2 if job['job_id']=='c018_unicode_atomic' or 'many_short_parity' in job['job_id'] else .5);k=job.get('api_known_k',None if job['allowed_k'] is None else job['allowed_k'][0]);row.update(launched=True,result=gate.solve(json.loads(raw.decode('utf-8-sig')),known_k=k,deadline=min(end,time.perf_counter()+seconds)))
            except Exception as exc:row.update(launched=True,execution_error=repr(exc))
            row['elapsed_seconds']=time.perf_counter()-began
        print(json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=='__main__':main()

"""Bounded one-provider API correctness; new source/input hashes verified."""
import importlib.util,json,hashlib,sys,time
from pathlib import Path
A=Path(__file__).resolve().parent
def main():
    provider=sys.argv[1];binding=json.loads((A/'BINDING_V1.json').read_text())[provider];source=Path(binding['solver']);assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['solver_sha256'];spec=importlib.util.spec_from_file_location('provider_gate',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);end=time.perf_counter()+45
    for j in json.loads((A/'SMALL_MANIFEST_V1.json').read_text())['jobs']:
        row=dict(provider=provider,job_id=j['job_id'])
        if time.perf_counter()>=end:row.update(launched=False,execution_status='batch_budget_unstarted')
        else:
            began=time.perf_counter()
            try:
                raw=Path(j['input']).read_bytes();assert hashlib.sha256(raw).hexdigest()==j['input_sha256'];seconds=j.get('deadline_seconds',2 if j['job_id']=='c018_unicode_atomic' or 'many_short_parity' in j['job_id'] else .5);k=j.get('api_known_k',None if j['allowed_k'] is None else j['allowed_k'][0]);row.update(launched=True,result=g.solve(json.loads(raw),known_k=k,deadline=min(end,time.perf_counter()+seconds)))
            except Exception as exc:row.update(launched=True,execution_error=repr(exc))
            row['elapsed_seconds']=time.perf_counter()-began
        print(json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=='__main__':main()

"""One captured bounded correctness batch; no timing claims."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--method',choices=['baseline','new'],required=True);args=ap.parse_args()
    binding=json.loads((A/'BINDINGS_V1.json').read_text())[args.method]['solver'];p=Path(binding['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['sha256']
    spec=importlib.util.spec_from_file_location('frozen_provider',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    deadline=time.perf_counter()+40
    for c in json.loads((A/'DATA_MANIFEST_V1.json').read_text())['small_cases']:
        try:
            data=json.loads(Path(c['path']).read_text());kwargs={'deadline':deadline}
            if args.method=='baseline':kwargs['enumerate_partitions']=True
            result=module.solve(data,**kwargs)
            print(json.dumps({'case_id':c['case_id'],'result':result},ensure_ascii=False),flush=True)
        except Exception as e:print(json.dumps({'case_id':c['case_id'],'execution_error':repr(e)}),flush=True)
if __name__=='__main__':main()

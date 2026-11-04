"""Separate Python-tracked memory measurement, not benchmark timing."""
import sys,time,tracemalloc,json,hashlib,importlib.util
from pathlib import Path
A=Path(__file__).resolve().parent
def main():
    provider,input_path,mode=sys.argv[1:4];start=time.perf_counter();tracemalloc.start();binding=json.loads((A/'BINDING_V1.json').read_text())[provider];source=Path(binding['solver']);assert hashlib.sha256(source.read_bytes()).hexdigest()==binding['solver_sha256'];raw=Path(input_path).read_bytes();data=json.loads(raw);spec=importlib.util.spec_from_file_location('memory_gate',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);result=g.solve(data,known_k=None if mode=='unknown' else int(mode),deadline=start+20);current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    print(json.dumps(dict(result=result,input_sha256=hashlib.sha256(raw).hexdigest(),peak_python_bytes=peak,current_python_bytes=current,tracing_scope='before binding/source import and input read through solver return; Python traced allocations, not RSS',memory_scope='completed' if result['status']!='unresolved' else 'partial_incomplete',elapsed_seconds=time.perf_counter()-start),ensure_ascii=False,sort_keys=True));return 3 if result['status']=='unresolved' else 2 if result['status']=='invalid_input' else 0
if __name__=='__main__':raise SystemExit(main())

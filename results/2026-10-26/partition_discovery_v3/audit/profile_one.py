"""One isolated tracemalloc run for the C003 performance suite."""
import argparse, importlib.util, json, time, tracemalloc
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
C003=ROOT/"results/2026-10-26/partition_discovery_v3"
def main():
    p=argparse.ArgumentParser(); p.add_argument("input",type=Path); p.add_argument("--method",required=True)
    p.add_argument("--max-solutions",type=int,required=True); a=p.parse_args()
    data=json.loads(a.input.read_text(encoding="utf-8"))
    spec=importlib.util.spec_from_file_location("c003_root_cli",C003/"solver.py")
    cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
    provider=cli.provider(a.method)
    tracemalloc.start(); start=time.perf_counter()
    result=provider.solve(data,deadline=start+30,max_solutions=a.max_solutions)
    elapsed=time.perf_counter()-start
    current,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    print(json.dumps({"method":a.method,"max_solutions":a.max_solutions,
                      "result":result,"profile_seconds":elapsed,
                      "tracemalloc_current_bytes":current,"tracemalloc_peak_bytes":peak},
                     ensure_ascii=False,separators=(",",":")),flush=True)
if __name__=="__main__":main()

import argparse,json,math,time
from pathlib import Path
import solver_v1
def main():
    ap=argparse.ArgumentParser(description='Experimental selected-output model, at most eight caller-selected atomic IDs')
    ap.add_argument('input',type=Path);ap.add_argument('--model-version',required=True,choices=['selected-output-v1'])
    ap.add_argument('--depth',required=True,choices=['0','1','2','4','8','full']);ap.add_argument('--known-k',type=int)
    ap.add_argument('--seconds',type=float,default=20)
    args=ap.parse_args()
    if not math.isfinite(args.seconds) or args.seconds<0:ap.error('seconds must be finite and nonnegative')
    started=time.perf_counter()
    try:
        raw=args.input.read_bytes();data=json.loads(raw.decode('utf-8-sig'))
        out=solver_v1.solve(data,depth='full' if args.depth=='full' else int(args.depth),model_version=args.model_version,
                            known_k=args.known_k,deadline=started+args.seconds)
    except (OSError,ValueError) as exc:out=dict(status='invalid_input',complete=False,error=str(exc))
    except (MemoryError,RecursionError,KeyboardInterrupt) as exc:out=dict(status='unresolved',complete=False,reason=type(exc).__name__)
    out['input_and_solver_seconds']=time.perf_counter()-started
    print(json.dumps(out,sort_keys=True))
    return {'invalid_input':2,'unresolved':3}.get(out['status'],0)
if __name__=='__main__':raise SystemExit(main())

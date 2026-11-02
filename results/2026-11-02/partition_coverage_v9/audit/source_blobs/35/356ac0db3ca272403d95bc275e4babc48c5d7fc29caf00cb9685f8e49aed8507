"""JSON CLI for exact C009 partial symbol-ownership identification."""
import argparse
import json
import math
import time
from pathlib import Path
import ownership_solver_v1


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path,help="JSON with alphabet, positive, negative, and optional allowed_k")
    parser.add_argument("--seconds",type=float,default=None,help="cooperative wall-time limit")
    parser.add_argument("--enumerate",action="store_true",help="export every compatible partition; no truncation")
    args=parser.parse_args(argv)
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds<0):
        print(json.dumps({"status":"invalid_input","error":"seconds must be finite and nonnegative"})); return 2
    try:
        with args.input.open("r",encoding="utf-8-sig") as stream: data=json.load(stream)
    except (OSError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"invalid_input","error":str(exc)},ensure_ascii=False)); return 2
    deadline=None if args.seconds is None else time.perf_counter()+args.seconds
    result=ownership_solver_v1.solve(data,deadline=deadline,enumerate_partitions=args.enumerate)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return {"invalid_input":2,"unknown":3,"model_inconsistent":0,
            "identified_unique_partition":0,"partial_ownership_identification":0}.get(result["status"],4)


if __name__=="__main__": raise SystemExit(main())

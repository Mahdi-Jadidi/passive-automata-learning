"""JSON CLI for C007 finest_solver_v3."""
import argparse
import json
import math
import time
from pathlib import Path

import finest_solver_v3


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path,help="JSON containing alphabet, positive and negative")
    parser.add_argument("--mode",choices=("adaptive","reference"),default="adaptive")
    parser.add_argument("--seconds",type=float,default=None,help="cooperative duration from provider start")
    parser.add_argument("--max-solutions",type=int,default=None,
                        help="reference mode only; truncation returns incomplete")
    args=parser.parse_args(argv)
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds<0):
        print(json.dumps({"status":"invalid_input","error":"seconds must be finite and nonnegative"}))
        return 2
    if args.mode!="reference" and args.max_solutions is not None:
        print(json.dumps({"status":"invalid_input","error":"--max-solutions is only valid in reference mode"}))
        return 2
    try:
        with args.input.open("r",encoding="utf-8-sig") as stream: data=json.load(stream)
    except (OSError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"invalid_input","error":str(exc)},ensure_ascii=False)); return 2
    deadline=None if args.seconds is None else time.perf_counter()+args.seconds
    try:
        result=finest_solver_v3.solve(data,deadline=deadline,mode=args.mode,max_solutions=args.max_solutions)
    except ValueError as exc:
        print(json.dumps({"status":"invalid_input","error":str(exc)},ensure_ascii=False)); return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return {"finest_unique":0,"one_block_only":0,"multiple_maximal_exist":0,
            "incomplete":3,"invalid_input":2,"runtime_error":4}.get(result["status"],4)


if __name__=="__main__": raise SystemExit(main())

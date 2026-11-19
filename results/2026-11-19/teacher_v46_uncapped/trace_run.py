"""Observe an uncapped V45 run, preserving its implementation and results."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'teacher_v46'))
from run import FIXED, V45, load, rows, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('case')
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    source = V45/'benchmark_raw.jsonl'
    case = next(row for row in rows(FIXED) if row['case']==args.case)
    expected = next(row['profile']['result']['max_devices'] for row in rows(source)
                    if row['case']==args.case and row['method']=='v43')
    solve, verify = load('v45')
    import optimizer
    from teacher_main import MainTeacher

    args.out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    stop = threading.Event()
    lock = threading.Lock()
    state = {}
    totals = dict(teacher_seconds=0.0, projection_and_teacher_seconds=0.0,
                  local_seconds=0.0, named_dfas=0, cache_hits=0, calls=0)

    with (args.out/'events.jsonl').open('x',encoding='utf-8') as stream:
        def record(event, **fields):
            row = dict(event=event, elapsed_seconds=time.perf_counter()-start, **fields)
            with lock:
                stream.write(json.dumps(row,ensure_ascii=True)+'\n')
                stream.flush()
                print(json.dumps(row,ensure_ascii=True),flush=True)

        class ObservedTeacher(MainTeacher):
            def check(self, blocks, images):
                totals['calls'] += 1
                number = totals['calls']
                t = time.perf_counter()
                record('teacher_start',call=number,blocks=blocks)
                verdict = super().check(blocks,images)
                elapsed = time.perf_counter()-t
                totals['teacher_seconds'] += elapsed
                record('teacher_end',call=number,status=verdict['status'],seconds=elapsed,
                       metrics=dict(self.stats))
                return verdict

            def _local(self, block, pos, neg, bound, metrics):
                call = totals['calls']
                planned = sum(2**h*h**(len(block)*h) for h in range(1,bound+1))
                before = metrics['dfa_representations']
                cached = (block,pos,neg,bound) in self.cache
                t = time.perf_counter()
                state['local'] = (call,block,bound,planned,before,metrics,t)
                record('local_start',call=call,block=block,bound=bound,
                       named_dfas_if_uncached=planned,cached=cached)
                try:
                    table = super()._local(block,pos,neg,bound,metrics)
                    return table
                finally:
                    state.pop('local',None)
                    elapsed = time.perf_counter()-t
                    count = metrics['dfa_representations']-before
                    totals['local_seconds'] += elapsed
                    totals['named_dfas'] += count
                    totals['cache_hits'] += int(cached)
                    record('local_end',call=call,block=block,bound=bound,cached=cached,
                           seconds=elapsed, named_dfas=count)

        def observe():
            while not stop.wait(15):
                current = state.get('local')
                if current:
                    call,block,bound,planned,before,metrics,t = current
                    count = metrics['dfa_representations']-before
                    record('progress',call=call,block=block,bound=bound,named_dfas=count,
                           named_dfas_if_uncached=planned,local_seconds=time.perf_counter()-t)

        observer = threading.Thread(target=observe,daemon=True)
        original = optimizer.MainTeacher
        optimizer.MainTeacher = ObservedTeacher
        record('start', case=args.case, solver_limit_seconds=None, consumer_limit_seconds=None,
               input=case['input'], expected_k=expected, python=sys.version, platform=platform.platform(),
               source_sha256=sha(FIXED),teacher_sha256=sha(V45/'teacher_main.py'))
        observer.start()
        try:
            profile = solve(case['input'], None)
            solved = time.perf_counter()
        finally:
            stop.set()
            observer.join()
            optimizer.MainTeacher = original
        result = profile['result']
        checked = verify(case['input'],result,None) if result['status'] in ('OPTIMAL','INFEASIBLE') else None
        totals['projection_and_teacher_seconds'] = profile['metrics'].get('teacher_seconds',0.0)
        accepted = checked=={'status':'ACCEPT'} and result['max_devices']==expected
        report = dict(case=args.case, profile=profile, checked=checked, expected_k=expected,
                      verified_reference_match=accepted, totals=totals,
                      solve_seconds=solved-start, consumer_seconds=time.perf_counter()-solved)
        with (args.out/'result.json').open('x',encoding='utf-8') as output:
            json.dump(report,output,indent=2)
        record('finish',status=result['status'],checked=checked,verified_reference_match=accepted,
               totals=totals,solve_seconds=report['solve_seconds'])
    if not accepted:
        raise SystemExit(1)


if __name__=='__main__':
    main()

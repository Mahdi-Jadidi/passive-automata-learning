"""Run read-only upstream kernel tests plus independent V46 boundary checks."""
import argparse
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import V45, load, oracle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output', type=Path)
    ap.add_argument('--oracle-seconds', type=float, default=60)
    args = ap.parse_args()
    with args.output.open('x', encoding='utf-8') as stream:
        records = []
        for file in ('teacher_tests.py', 'projection_tests.py', 'master_tests.py',
                     'cut_certificate_tests.py'):
            start = time.perf_counter()
            result = subprocess.run([sys.executable, '-B', str(V45/file)], capture_output=True,
                                    encoding='utf-8', timeout=60)
            records.append(dict(script=file, returncode=result.returncode, stdout=result.stdout,
                                stderr=result.stderr, wall_seconds=time.perf_counter()-start))
        solve, verify = load('v45')
        from teacher_main import MainTeacher
        from spec import Exhausted
        checks = []
        sigma = ['opaque log α', 'b', 'unused 🧩']
        words = [[], [sigma[0]], [sigma[1]], [sigma[0], sigma[1]], [sigma[1], sigma[0]]]
        for labels in itertools.product(range(3), repeat=3):
            # ε, one event, and its unused peers; small enough for bounded exhaustive replay.
            d = dict(alphabet=sigma, positive=[w for w,t in zip(words,labels) if t==1],
                     negative=[w for w,t in zip(words,labels) if t==2])
            expected = oracle(d)
            result = solve(d, {'timeout_seconds':args.oracle_seconds})['result']
            checked = (verify(d, result, {'timeout_seconds':2})
                       if result['status'] in ('OPTIMAL','INFEASIBLE') else None)
            checks.append(dict(input=d, expected_k=expected, result=result, checked=checked,
                               solve_limit_seconds=args.oracle_seconds, consumer_limit_seconds=2,
                               ok=result['max_devices']==expected and checked=={'status':'ACCEPT'}))
        # A deterministic interruption during a real teacher local-table build.
        # It must not add a producer cut or publish the partial teacher table.
        d = dict(alphabet=sigma[:2], positive=[[sigma[0],sigma[1]]],
                 negative=[[sigma[1],sigma[0]]])
        import optimizer
        original_budget = optimizer.budget
        teacher_ref = []
        original_check = MainTeacher.check

        def capture(self, blocks, images):
            teacher_ref.append(self)
            return original_check(self, blocks, images)

        def step_budget(limits):
            def tick():
                if teacher_ref and teacher_ref[-1].stats['dfa_representations'] >= 3:
                    raise Exhausted()
            tick.remaining = lambda: None
            return tick

        try:
            optimizer.budget = step_budget
            MainTeacher.check = capture
            interrupted = solve(d)
        finally:
            optimizer.budget = original_budget
            MainTeacher.check = original_check
        status = interrupted['result']
        timeout_ok = (status['status']=='INCOMPLETE' and
                      all(status[key] is None for key in ('blocks','max_devices','certificate')) and
                      not interrupted['trace'] and interrupted['metrics']['cuts']==0 and
                      not teacher_ref[-1].cache and teacher_ref[-1].completed_checks==0)
        data = dict(kernel_replay=records, opaque_oracle_cases=checks,
                    teacher_timeout=dict(profile=interrupted, cache_size=len(teacher_ref[-1].cache),
                                         passed=timeout_ok))
        json.dump(data, stream, indent=2)
    if not all(r['returncode']==0 for r in records) or not all(c['ok'] for c in checks) or not timeout_ok:
        raise SystemExit(1)
    print('Four kernel scripts, 27 opaque-ID oracle comparisons, and injected interruption passed')


if __name__ == '__main__':
    main()

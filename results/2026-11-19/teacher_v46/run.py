"""Sequential runners for frozen V43/V45. Every output directory is new."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'results/2026-11-16'
V45 = OLD / 'interactive_teacher_v45'
V43 = OLD / 'exact_optimizer_v43'
VENDOR = ROOT / 'results/2026-11-14/sat_candidate_v37/vendor'
CORPUS = V43 / 'audit_raw.jsonl'
FIXED = ROOT / 'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def append(stream, row):
    stream.write(json.dumps(row, ensure_ascii=True) + '\n')
    stream.flush()


def load(method):
    sys.path.insert(0, str(V45 if method == 'v45' else V43))
    from optimizer import solve_profiled
    from verify import verify_optimal
    return solve_profiled, verify_optimal


def execute(case, solve_seconds, verify_seconds, api):
    solve, verify = api
    start = time.perf_counter()
    profile = solve(case['input'], {'timeout_seconds': solve_seconds})
    solved = time.perf_counter()
    result = profile['result']
    status = result['status']
    checked = None
    if status in ('OPTIMAL', 'INFEASIBLE'):
        checked = verify(case['input'], result, {'timeout_seconds': verify_seconds})
        valid = checked == {'status': 'ACCEPT'} and result['max_devices'] == case['expected_k']
        valid &= (status == 'INFEASIBLE') == (case['expected_k'] is None)
    else:
        valid = status == 'INCOMPLETE' and all(
            result[key] is None for key in ('blocks', 'max_devices', 'certificate'))
    proof = (result['certificate'] or {}).get('proof') or []
    return dict(case, profile=profile, checked=checked, contract_valid=valid,
                limit_seconds=solve_seconds, consumer_limit_seconds=verify_seconds,
                solve_seconds=solved-start, consumer_seconds=time.perf_counter()-solved if checked else None,
                proof_lines=len(proof), proof_bytes=sum(len(line.encode())+1 for line in proof))


def worker(args):
    request = json.load(sys.stdin)
    start = time.perf_counter()
    api = load(request['method'])
    sys.path.append(str(V45))
    from memory_measurements import peak
    print(json.dumps({'import_seconds': time.perf_counter()-start}), flush=True)
    row = execute(request, args.solve, args.verify, api)
    row['peak_working_set_bytes'] = peak() if os.name == 'nt' else None
    print(json.dumps(row), flush=True)


def call(case, method, repeat, limits, out):
    request = dict(case, method=method, repeat=repeat)
    solve, verify = limits
    cmd = [sys.executable, '-B', str(__file__), 'worker', '--solve', str(solve),
           '--verify', str(verify)]
    start = time.perf_counter()
    with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, encoding='utf-8') as proc:
        proc.stdin.write(json.dumps(request))
        proc.stdin.close()
        proc.stdin = None
        # The ready message is flushed before solve; its receipt includes spawn/import.
        ready = proc.stdout.readline()
        startup = time.perf_counter()-start
        try:
            stdout, stderr = proc.communicate(timeout=solve+verify+15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
    try:
        row = json.loads(stdout)
        row.update(json.loads(ready))
    except (ValueError, TypeError):
        row = dict(request, contract_valid=False, limit_seconds=solve,
                   consumer_limit_seconds=verify, worker_error={'ready': ready, 'stdout': stdout})
    row.update(worker_returncode=proc.returncode, worker_stderr=stderr,
               startup_seconds=startup, fresh_process_seconds=time.perf_counter()-start)
    append(out, row)
    print(method, case['case'], repeat, row.get('profile', {}).get('result', {}).get('status', 'WORKER_ERROR'),
          round(row.get('solve_seconds', 0), 4), flush=True)
    return row


def oracle(data):
    def partitions(items):
        if not items:
            yield []
            return
        a, *rest = items
        for p in partitions(rest):
            yield [{a}, *p]
            for i, b in enumerate(p):
                yield p[:i] + [b | {a}] + p[i+1:]

    def accepts(p):
        def project(w, b):
            return tuple(a for a in w if a in b)
        return all(any(all(project(y, b) != project(x, b) for x in data['positive'])
                       for b in p) for y in data['negative'])
    return max((len(p) for p in partitions(data['alphabet']) if accepts(p)), default=None)


def integrity(out):
    hashes = {
        'encoding.py': '38da943c28419cb02c7b2aecff56c9ce189ed57ec51e39d2e19b74afab50727e',
        'optimizer.py': 'a4dcb3f1dfa6a84d5743276a9d8d584ab6e17d79fda1da95d3aa0ba976d8da63',
        'verify.py': 'e42c85a2cddb61797856114292f3577a2356c6bebcdf6bb7933ba6ca71af0dad',
    }
    expected = read(V45 / 'manifest.json')
    expected.update({(V43/f).relative_to(ROOT).as_posix(): {'sha256': h} for f, h in hashes.items()})
    checks = {}
    for path, record in expected.items():
        f = ROOT/path
        actual = {'sha256': sha(f), 'bytes': f.stat().st_size} if f.is_file() else {}
        checks[path] = {'expected': record, 'actual': actual,
                        'match': all(actual.get(k) == v for k, v in record.items())}
    env = dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
               machine=platform.machine(), cpu=os.environ.get('PROCESSOR_IDENTIFIER'),
               logical_cpus=os.cpu_count(), solver='Glucose3 (g3)',
               dependencies={d.metadata['Name']:d.version
                             for d in importlib.metadata.distributions(path=[str(VENDOR)])},
               native={f.name:sha(f) for f in sorted(VENDOR.glob('*'))
                       if f.suffix.lower() in ('.dll', '.pyd')},
               commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               sources={str(f.relative_to(ROOT)):sha(f) for f in [CORPUS, FIXED, V45/'manifest.json',
                        V45/'benchmark_raw.jsonl', V45/'interaction_example.json', V45/'two_cut_example.json']},
               checks=checks)
    with (out/'environment.json').open('x', encoding='utf-8') as stream:
        json.dump(env, stream, indent=2)
    if not all(check['match'] for check in checks.values()):
        print('FROZEN HASH MISMATCH: see environment.json', flush=True)
        raise SystemExit(2)


def corpus(out, limits):
    api = load('v45')
    counts = Counter()
    with (out/'corpus.jsonl').open('x', encoding='utf-8') as stream:
        for case in rows(CORPUS):
            row = execute({'i':case['i'], 'input':case['input'], 'expected_k':case['expected_k']},
                          *limits, api)
            append(stream, row)
            counts[row['profile']['result']['status']] += 1
            if not row['contract_valid'] or sum(counts.values()) % 200 == 0:
                print('corpus', sum(counts.values()), dict(counts), row['contract_valid'], flush=True)
    print('corpus complete', dict(counts), flush=True)


def benchmark(out, limits, escalation):
    reference = {r['case']:r['profile']['result']['max_devices']
                 for r in rows(V45/'benchmark_raw.jsonl') if r['method']=='v43'}
    cases = [dict(c, expected_k=reference[c['case']]) for c in rows(FIXED)]
    finished = set()
    censored = []
    with (out/'benchmark.jsonl').open('x', encoding='utf-8') as stream:
        for case in cases:
            for method in ('v43','v45'):
                row = call(case, method, 0, limits, stream)
                status = row.get('profile', {}).get('result', {}).get('status')
                if row['contract_valid'] and status in ('OPTIMAL','INFEASIBLE'):
                    finished.add((case['case'], method))
                if method == 'v45' and status == 'INCOMPLETE':
                    censored.append(case)
        for rep, order in ((1,('v45','v43')), (2,('v43','v45'))):
            for case in cases:
                for method in order:
                    if (case['case'],method) in finished:
                        call(case, method, rep, limits, stream)
    fixtures = {
        'ordinary': read(V45/'interaction_example.json')['input'],
        'two_cut': read(V45/'two_cut_example.json')['input'],
        'ab_ba': {'alphabet':['a','b'], 'positive':[['a','b']], 'negative':[['b','a']]},
    }
    with (out/'fixtures.jsonl').open('x', encoding='utf-8') as stream:
        for name, data in fixtures.items():
            call(dict(case=name,input=data,expected_k=oracle(data)), 'v45', 0, limits, stream)
    if escalation and censored:
        with (out/'escalations.jsonl').open('x', encoding='utf-8') as stream:
            case = censored[0]
            call(dict(case, selection='First censored case in preregistered fixed order'),
                 'v45', 0, (escalation,limits[1]), stream)


def projection(out):
    sys.path.insert(0, str(V45))
    import projection_benchmark as p
    p.OUTPUT = out/'projection.jsonl'
    p.main()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['all', 'worker', 'integrity', 'corpus', 'benchmark', 'projection'])
    ap.add_argument('--out', type=Path)
    ap.add_argument('--solve', type=float, default=60)
    ap.add_argument('--verify', type=float, default=60)
    ap.add_argument('--corpus-solve', type=float, default=0.25)
    ap.add_argument('--corpus-verify', type=float, default=2)
    ap.add_argument('--escalation', type=float, default=300)
    args = ap.parse_args()
    if args.mode == 'worker':
        return worker(args)
    if not args.out:
        ap.error('--out is required')
    args.out.mkdir(parents=True, exist_ok=False)
    integrity(args.out)
    with (args.out/'config.json').open('x', encoding='utf-8') as stream:
        json.dump(vars(args), stream, indent=2, default=str)
    if args.mode in ('all', 'benchmark'):
        benchmark(args.out, (args.solve,args.verify), args.escalation)
    if args.mode in ('all', 'corpus'):
        corpus(args.out, (args.corpus_solve,args.corpus_verify))
    if args.mode in ('all', 'projection'):
        projection(args.out)


if __name__ == '__main__':
    main()

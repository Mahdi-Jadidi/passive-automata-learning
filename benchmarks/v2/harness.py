"""Isolated structural benchmark harness (Linux, Python 3.10+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time

PIN = '7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6'
MODULE = 'implementation/partition_feedback_final'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def read_input(path):
    raw = path.read_bytes()
    d = json.loads(raw)
    if type(d) is not dict or set(d) != {'alphabet', 'positive', 'negative'}:
        raise ValueError('input-only schema required; extract bundles separately')
    a = d['alphabet']
    if type(a) is not list or any(type(s) is not str or not s for s in a) or len(set(a)) != len(a):
        raise ValueError('invalid alphabet')
    allowed = set(a)
    for label in ('positive', 'negative'):
        if type(d[label]) is not list or any(type(w) is not list or any(type(s) is not str or s not in allowed for s in w) for w in d[label]):
            raise ValueError('invalid ordered traces')
    return d, digest(raw)


def partitions(symbols):
    # Pinned audit.py enumeration, unchanged algorithm.
    if not symbols:
        yield ()
        return
    a, *rest = symbols
    for base in partitions(rest):
        yield (frozenset({a}), *base)
        for j, block in enumerate(base):
            yield (*base[:j], block | {a}, *base[j + 1:])


def compatible(D, P):
    def project(word, block):
        return tuple(a for a in word if a in block)
    return all(any(project(y, b) not in {project(x, b) for x in D['positive']} for b in P)
               for y in D['negative'])


def reference(d):
    best, count = None, 0
    for p in partitions(d['alphabet']):
        count += 1
        if (best is None or len(p) > len(best)) and compatible(d, p):
            best = p
    if best is None:
        return {'status': 'INFEASIBLE', 'partitions_enumerated': count}
    return {'status': 'OPTIMAL', 'max_devices': len(best), 'blocks': [sorted(b) for b in best], 'partitions_enumerated': count}


def replay_reference(d, result):
    # Independent restricted growth string enumeration and block-index projection.
    a = d['alphabet']
    def rgs(prefix, k):
        if len(prefix) == len(a):
            yield prefix
        else:
            for i in range(k + 1):
                yield from rgs(prefix + [i], max(k, i + 1))
    def check(labels):
        owner = dict(zip(a, labels))
        k = max(labels, default=-1) + 1
        def projections(w):
            out = [[] for _ in range(k)]
            for s in w:
                out[owner[s]].append(s)
            return list(map(tuple, out))
        pos = [set() for _ in range(k)]
        for x in d['positive']:
            for j, p in enumerate(projections(x)):
                pos[j].add(p)
        return all(any(p not in pos[j] for j, p in enumerate(projections(y))) for y in d['negative'])
    optimum = max((max(p, default=-1) + 1 for p in rgs([], 0) if check(p)), default=None)
    if result['status'] == 'INFEASIBLE':
        ok = optimum is None
    else:
        blocks = result['blocks']
        flat = [s for b in blocks for s in b]
        owner = {s: j for j, b in enumerate(blocks) for s in b}
        ok = (result['status'] == 'OPTIMAL' and all(blocks) and len(flat) == len(a) and set(flat) == set(a)
              and len(blocks) == result['max_devices'] == optimum and check([owner[s] for s in a]))
    return {'status': 'VERIFIED' if ok else 'INVALID'}


def pinned_source(repo):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != PIN or git('status', '--porcelain', '--untracked-files=all', '--', MODULE):
        raise ValueError('legacy requires clean checkout at pinned commit')
    return repo / MODULE


def worker(args):
    resource.setrlimit(resource.RLIMIT_AS, (args.memory * 2**20,) * 2)
    d, _ = read_input(args.input)
    started = time.perf_counter()
    if args.engine == 'reference':
        if len(d['alphabet']) > 9:
            raise ValueError('reference cap: 9 symbols')
        result = reference(d) if args.stage == 'solve' else replay_reference(d, json.loads(args.proof.read_bytes()))
    else:
        sys.path.insert(0, str(pinned_source(args.repo)))
        if args.stage == 'solve':
            import model
            import staged
            old = model.ProjectionOracle.__call__
            def observed(self, partition, purpose):
                with args.events.open('a') as f:
                    f.write(json.dumps({'attempt': list(partition)}) + '\n')
                response = old(self, partition, purpose)
                with args.events.open('a') as f:
                    f.write(json.dumps({'response_bytes': len(encode(response)), 'status': response['status']}) + '\n')
                return response
            model.ProjectionOracle.__call__ = observed
            result = staged.solve(d, seconds=args.seconds, transcript=True)
        else:
            from verify import verify
            result = verify(d, json.loads(args.proof.read_bytes()), seconds=args.seconds)
    print(json.dumps({'result': result, 'compute_seconds': time.perf_counter()-started,
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))


def run(args):
    d, checksum = read_input(args.input)
    if args.engine == 'legacy':
        pinned_source(args.repo)
    args.output.mkdir(parents=True, exist_ok=False)
    snapshot = args.output / 'input.json'
    raw = args.input.read_bytes()
    if digest(raw) != checksum:
        raise ValueError('input changed during snapshot')
    snapshot.write_bytes(raw)
    proof = args.output / 'producer.json'
    events = args.output / 'events.jsonl'
    events.touch()
    def stage(name):
        cmd = [sys.executable, '-B', str(Path(__file__).resolve()), str(snapshot), str(args.output),
               '--engine', args.engine, '--repo', str(args.repo.resolve()), '--seconds', str(args.seconds),
               '--memory', str(args.memory), '--stage', name, '--proof', str(proof), '--events', str(events)]
        start = time.perf_counter()
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=args.seconds + 1, check=False,
                               env={**os.environ, 'PYTHONHASHSEED': '0'})
            (args.output / (name + '.stderr')).write_bytes(p.stderr)
            (args.output / (name + '.stdout')).write_bytes(p.stdout)
            if p.returncode:
                return {'process_status': 'MEMORY_ERROR' if b'MemoryError' in p.stderr else 'PROCESS_ERROR', 'returncode': p.returncode, 'wall_seconds': time.perf_counter()-start}
            return {'process_status': 'OK', 'wall_seconds': time.perf_counter()-start, **json.loads(p.stdout)}
        except subprocess.TimeoutExpired as e:
            (args.output / (name + '.stderr')).write_bytes(e.stderr or b'')
            (args.output / (name + '.stdout')).write_bytes(e.stdout or b'')
            return {'process_status': 'TIMEOUT', 'wall_seconds': time.perf_counter()-start}
    producer = stage('solve')
    result = producer.pop('result', {})
    proof.write_bytes(encode(result))
    verdict = stage('verify') if result.get('status') in ('OPTIMAL', 'INFEASIBLE') else {'process_status': 'NOT_RUN'}
    observed = []
    log_valid = True
    for line in events.read_text().splitlines():
        try:
            observed.append(json.loads(line))
        except json.JSONDecodeError:
            log_valid = False
    attempts = [tuple(sorted(e['attempt'])) for e in observed if 'attempt' in e]
    responses = [e for e in observed if 'response_bytes' in e]
    verified = verdict.get('result', {}).get('status') == 'VERIFIED'
    cost = len(d['alphabet'])-result['max_devices'] if verified and result.get('status') == 'OPTIMAL' else None
    summary = {'schema': 1, 'engine': args.engine, 'legacy_pin': PIN if args.engine == 'legacy' else None,
               'input_sha256': checksum, 'alphabet': len(d['alphabet']), 'positives': len(d['positive']), 'negatives': len(d['negative']),
               'host': platform.platform(), 'python': sys.version, 'hash_seed': 0, 'memory_limit_as_mib': args.memory,
               'seconds_per_stage': args.seconds, 'hard_wall_seconds_per_stage': args.seconds+1,
               'producer': producer, 'producer_status': result.get('status'), 'producer_stats': result.get('stats'),
               'verifier': verdict, 'producer_artifact_bytes': proof.stat().st_size, 'structural_lower_cost': cost,
               'structural_upper_cost': cost, 'structural_gap': 0 if cost is not None else None,
               'operational_status': 'INCOMPLETE', 'external_attempts': 0, 'external_response_bytes': 0,
               'local_attempts_observed': len(attempts), 'distinct_local_candidates_observed': len(set(attempts)),
               'local_responses_observed': len(responses), 'local_response_json_bytes_observed': sum(e['response_bytes'] for e in responses),
               'local_metrics_complete': log_valid and producer['process_status'] == 'OK' and len(attempts) == len(responses)}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--engine', choices=('reference', 'legacy'), default='reference')
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--seconds', type=float, default=5)
    p.add_argument('--memory', type=int, default=512)
    p.add_argument('--stage', choices=('solve', 'verify'))
    p.add_argument('--proof', type=Path)
    p.add_argument('--events', type=Path)
    args = p.parse_args()
    if not 0 < args.seconds < float('inf') or args.memory <= 0:
        p.error('positive finite budgets required')
    worker(args) if args.stage else run(args)

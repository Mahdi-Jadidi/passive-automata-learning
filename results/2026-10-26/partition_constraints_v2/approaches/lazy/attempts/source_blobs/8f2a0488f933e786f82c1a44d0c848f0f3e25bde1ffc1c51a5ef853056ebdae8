"""Owned immutable smoke capture; candidate imports are only for this smoke."""
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
import types
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def worker():
    common = types.ModuleType('common')
    common.__path__ = []
    sys.modules['common'] = common
    for name, file in [('engine', 'engine_candidate.py'),
                       ('helpers', 'common_helpers_candidate.py')]:
        load('common.' + name, ROOT / 'approaches/eager' / file)
    lazy = load('lazy_smoke', HERE / 'lazy_solver.py')
    baseline = load('baseline_smoke', ROOT / 'baseline/partition_solver.py')
    cases = []
    words = ['', 'a', 'b', 'aa', 'ab', 'ba', 'bb']
    for labels in itertools.product(range(3), repeat=len(words)):
        cases.append(dict(alphabet=list('ab'),
                          positive=[w for w, x in zip(words, labels) if x == 1],
                          negative=[w for w, x in zip(words, labels) if x == 2]))
    rng = random.Random(20261026)
    words = [''] + list('abc') + [''.join(w) for w in itertools.product('abc', repeat=2)]
    for _ in range(100):
        labels = [rng.randrange(3) for w in words]
        cases.append(dict(alphabet=list('abc'),
                          positive=[w for w, x in zip(words, labels) if x == 1],
                          negative=[w for w, x in zip(words, labels) if x == 2]))
    for path in sorted((ROOT / 'baseline').glob('theory_*.json')):
        cases.append(json.loads(path.read_text(encoding='utf-8-sig')))
    key = lambda r: {tuple(tuple(b) for b in p['blocks']) for p in r['feasible_partitions']}
    for i, data in enumerate(cases):
        expected = baseline.solve(data)
        actual = lazy.solve(data)
        print(json.dumps(dict(case=i, input=data, baseline=expected, lazy=actual)))
        assert actual['complete'] and key(actual) == key(expected), i
        assert len(actual['feasible_partitions']) == len(key(actual)), i
    partial = lazy.solve(cases[-1], deadline=time.perf_counter()-1)
    print(json.dumps(dict(expired_deadline=partial)))
    assert not partial['complete'] and partial['status'] == 'incomplete'
    assert partial['feasible_partition_count'] is None
    print(json.dumps(dict(passed=len(cases), shared_candidates_only=True)))


def capture():
    attempt = HERE / 'attempts' / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+uuid.uuid4().hex[:8])
    attempt.mkdir(parents=True)
    blobs = HERE / 'attempts/source_blobs'
    blobs.mkdir(exist_ok=True)
    files = list(HERE.glob('*.py')) + list((ROOT/'approaches/eager').glob('*candidate.py')) + list((ROOT/'baseline').glob('*.py')) + list((ROOT/'baseline').glob('theory_*.json'))
    manifest = []
    for path in files:
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        dest = blobs / digest
        if not dest.exists():
            dest.write_bytes(content)
        manifest.append(dict(path=str(path.relative_to(ROOT)), sha256=digest))
    command = [sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--worker']
    (attempt/'started.json').write_text(json.dumps(dict(command=command, cwd=str(ROOT), sources=manifest, python=sys.version, platform=platform.platform(), seed=20261026),indent=2),encoding='utf-8')
    start = time.perf_counter()
    with (attempt/'stdout.txt').open('wb') as out, (attempt/'stderr.txt').open('wb') as err:
        completed = subprocess.run(command,cwd=ROOT,stdout=out,stderr=err)
    result = dict(exit_code=completed.returncode, elapsed_seconds=time.perf_counter()-start,
                  execution_status='success' if completed.returncode == 0 else 'program_error',
                  scientific_status='initial_check_passed_independent_audit_pending' if completed.returncode == 0 else 'undetermined')
    (attempt/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(attempt=str(attempt),**result)))
    return completed.returncode


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker()
    else:
        sys.exit(capture())

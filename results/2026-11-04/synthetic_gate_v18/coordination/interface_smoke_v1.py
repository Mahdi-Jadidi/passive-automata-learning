"""Check the public root entry point after benchmark timing has ended."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    root = Path(__file__).resolve().parents[4]
    cycle = Path(__file__).resolve().parent.parent
    jobs = json.loads((cycle / 'audit/CASE_MANIFEST_V1.json').read_text())['jobs']
    source = Path(next(j['input'] for j in jobs if j['job_id'] == 'graph_failure_unique_K2'))
    sample = json.loads(source.read_text())
    out = cycle / 'coordination/interface_smoke_v1'
    out.mkdir(exist_ok=False)
    records = []
    for name, flags, expected in [('known_k', ['--known-k', '2'], 'certified_unique'),
                                  ('no_k', [], 'ambiguous')]:
        command = [sys.executable, '-B', '-X', 'utf8', str(root / 'partition.py'), str(source), *flags]
        started = time.perf_counter()
        child = subprocess.run(command, capture_output=True, timeout=10)
        (out / (name + '.stdout.bin')).write_bytes(child.stdout)
        (out / (name + '.stderr.bin')).write_bytes(child.stderr)
        result = json.loads(child.stdout)
        assert child.returncode == 0 and result['status'] == expected
        assert result['method'] == 'C018-exact-chunked-count-gate-v1'
        witnesses = ([result['certificate']['witness']] if expected == 'certified_unique'
                     else result['alternatives'])
        keys = []
        for witness in witnesses:
            groups = witness['blocks']
            assert sorted(a for group in groups for a in group) == sorted(sample['alphabet'])
            languages = [{''.join(a for a in word if a in group) for word in sample['positive']}
                         for group in groups]
            assert all(any(''.join(a for a in word if a in group) not in language
                           for group, language in zip(groups, languages)) for word in sample['negative'])
            keys.append(tuple(sorted(tuple(sorted(group)) for group in groups)))
        assert len(set(keys)) == len(keys)
        if expected == 'certified_unique':
            assert keys == [(('a', 'b'), ('c', 'd'))]
        else:
            assert 'partition' not in result and len(keys) == 2
        records.append({'command': command, 'exit_code': child.returncode,
                        'status': result['status'], 'wall_seconds': time.perf_counter() - started,
                        'stdout_sha256': hashlib.sha256(child.stdout).hexdigest(),
                        'stderr_sha256': hashlib.sha256(child.stderr).hexdigest()})
    (out / 'result.json').write_text(json.dumps({'status': 'passed', 'not_part_of_benchmark': True,
                                               'records': records}, indent=2))
    print('public entry point: both interface checks passed')


if __name__ == '__main__':
    main()

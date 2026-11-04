"""Master integrity closure; does not rerun scientific benchmarks."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
A = R / 'audit'
cache = {}


def digest(path):
    path = Path(path)
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    if key not in cache:
        cache[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return cache[key]


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    attempts = []
    snapshots = 0
    for folder in sorted((A / 'attempts').iterdir()):
        if not folder.is_dir():
            continue
        meta = read(folder / 'manifest.json')
        result = read(folder / 'result.json')
        assert result['child_reaped'] and not result.get('cleanup_error')
        assert not result.get('capture_error')
        for name in ('stdout', 'stderr'):
            stream = folder / (name + '.bin')
            assert digest(stream) == result[name + '_sha256']
            assert stream.stat().st_size == result[name + '_bytes']
        for source in meta['sources']:
            assert digest(A / source['snapshot']) == source['sha256']
            assert digest(source['path']) == source['sha256']
            snapshots += 1
        attempts.append({k: result[k] for k in
                         ('attempt_id', 'label', 'execution_status', 'exit_code')})
    freeze = read(A / 'BENCHMARK_FREEZE_V1.json')
    for path, expected in freeze['sources'].items():
        assert digest(path) == expected
    run = A / 'benchmark_runs/20261104T120316.506188Z'
    validation = read(run / 'validation_report.json')
    assert validation['status'] == 'accepted_with_censoring'
    assert not validation['errors'] and validation['small_gate_rows'] == 5130
    assert read(run / 'closure.json')['status'] == 'validation_success'
    assert read(R / 'coordination/k20_functional_control_v1/result.json')['status'] == 'accepted'
    assert read(R / 'coordination/public_smoke_v1/result.json')['status'] == 'accepted'
    report = {'status': 'accepted', 'attempt_count': len(attempts),
              'stream_count': 2 * len(attempts), 'source_references': snapshots,
              'distinct_hashed_files': len(cache), 'attempts': attempts,
              'benchmark_freeze_sha256': digest(A / 'BENCHMARK_FREEZE_V1.json'),
              'scope': 'raw captures, content-addressed source blobs, current frozen sources and completed semantic reports'}
    target = R / 'coordination/INTEGRITY_V1.json'
    with target.open('x', encoding='utf8') as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k != 'attempts'}))


if __name__ == '__main__':
    main()

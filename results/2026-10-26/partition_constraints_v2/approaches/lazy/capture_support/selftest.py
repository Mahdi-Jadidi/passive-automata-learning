"""Isolated candidate checks; all effects stay in owned attempts/source_blobs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
from uuid import uuid4

import capture_candidate as candidate

HERE = Path(__file__).resolve().parent


def main():
    inputs = HERE / 'attempts' / ('selftest_inputs_' + uuid4().hex)
    inputs.mkdir(parents=True, exist_ok=False)
    fixture = inputs / 'child.py'
    fixture.write_text('''import pathlib, sys, time
mode = sys.argv[1]
print("OUT-READY", flush=True)
print("ERR-READY", file=sys.stderr, flush=True)
if len(sys.argv) > 2:
    pathlib.Path(sys.argv[2]).write_text("ready", encoding="utf-8")
if mode == "nonzero":
    sys.exit(7)
if mode == "sleep":
    time.sleep(10)
''', encoding='utf-8')
    results = []

    def run(label, mode, expected, *, timeout=3.0, extra=None, command=None):
        cmd = command or [sys.executable, '-B', '-X', 'utf8', str(fixture), mode, *(extra or [])]
        result = candidate.capture(label, cmd, cwd=HERE, timeout_seconds=timeout,
                                   source_paths=[fixture, Path(__file__)])
        # Preserve the result before making any assertion about it.
        (inputs / (label + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(dict(label=label, result=result)), flush=True)
        results.append(result)
        assert result['execution_status'] == expected, result
        assert result['scientific_status'] == 'not_assessed'
        assert result['duration_seconds'] >= result['subprocess_seconds'] >= 0
        run_dir = Path(result['attempt_dir'])
        for stream in ('stdout', 'stderr'):
            raw = (run_dir / (stream + '.bin')).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == result[stream + '_sha256']
            assert len(raw) == result[stream + '_bytes']
        manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
        for source in manifest['sources']:
            blob = HERE / source['snapshot']
            assert hashlib.sha256(blob.read_bytes()).hexdigest() == source['sha256']
        if result['child_pid'] is not None:
            assert result['child_reaped'] is True
        return result

    success = run('success', 'success', 'success')
    assert success['exit_code'] == 0
    nonzero = run('nonzero', 'nonzero', 'program_error')
    assert nonzero['exit_code'] == 7
    timeout = run('timeout_partial', 'sleep', 'timed_out', timeout=1.0)
    assert b'OUT-READY' in (Path(timeout['attempt_dir']) / 'stdout.bin').read_bytes()
    assert b'ERR-READY' in (Path(timeout['attempt_dir']) / 'stderr.bin').read_bytes()
    environment = run('missing_executable', '', 'environment_error',
                      command=[str(inputs / 'definitely_missing_executable')])
    assert environment['exit_code'] is None and environment['child_pid'] is None

    # Inject one KeyboardInterrupt into wait only after THIS child's flush marker.
    # No OS signal, foreground process interruption or unrelated process control.
    ready = inputs / 'ready.txt'
    real_wait = subprocess.Popen.wait
    fired = False

    def interrupt_once(process, *args, **kwargs):
        nonlocal fired
        if not fired:
            fired = True
            limit = time.perf_counter() + 3
            while not ready.exists() and time.perf_counter() < limit:
                time.sleep(.01)
            assert ready.exists(), 'child did not become ready'
            raise KeyboardInterrupt('isolated simulated interruption')
        return real_wait(process, *args, **kwargs)

    with patch.object(subprocess.Popen, 'wait', interrupt_once):
        interrupted = run('interrupt_partial', 'sleep', 'interrupted', extra=[str(ready)])
    assert fired and interrupted['child_reaped']
    assert b'OUT-READY' in (Path(interrupted['attempt_dir']) / 'stdout.bin').read_bytes()
    assert b'ERR-READY' in (Path(interrupted['attempt_dir']) / 'stderr.bin').read_bytes()

    real_sources = candidate._source_manifest

    def slow_sources(paths):
        time.sleep(.25)
        return real_sources(paths)

    with patch.object(candidate, '_source_manifest', slow_sources):
        timed = run('clock_separation', 'success', 'success')
    assert timed['duration_seconds'] - timed['subprocess_seconds'] >= .25
    with patch.object(candidate, '_source_manifest', side_effect=KeyboardInterrupt):
        prelaunch = run('interrupt_prelaunch', 'success', 'interrupted')
    assert prelaunch['child_pid'] is None and prelaunch['subprocess_seconds'] == 0
    assert len({r['attempt_dir'] for r in results}) == len(results)
    summary = dict(passed_scenarios=len(results), result_attempts=[r['attempt_dir'] for r in results],
                   simulation='single mocked wait interruption, no foreground OS signal',
                   performance_claim=False)
    (inputs / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

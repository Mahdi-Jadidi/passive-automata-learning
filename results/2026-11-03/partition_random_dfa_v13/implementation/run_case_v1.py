"""Generate observations and capture the frozen C010 exact CLI in fresh processes."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parents[2] / '2026-11-02' / 'partition_unrestricted_v10' / 'implementation'
FROZEN = {
    HERE / 'generate_v1.py': '0b649344035f449b0a17cd6410dd41db67c6b1e06025b78262807740b93ba410',
    BASELINE / 'unrestricted_solver_v2.py': '4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502',
    BASELINE / 'unrestricted_cli_v2.py': '3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa',
}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def capture(command, folder, name, timeout):
    started = time.perf_counter()
    entry = {'command': command, 'timeout_seconds': timeout}
    with (folder / f'{name}.stdout.bin').open('wb') as out, (folder / f'{name}.stderr.bin').open('wb') as err:
        try:
            process = subprocess.run(command, stdout=out, stderr=err, timeout=timeout, check=False)
            entry.update(exit_code=process.returncode, execution_status='exited')
        except subprocess.TimeoutExpired:
            entry.update(exit_code=None, execution_status='hard_timeout')
        except OSError as exc:
            entry.update(exit_code=None, execution_status='environment_error', error=str(exc))
    entry['wall_seconds'] = time.perf_counter() - started
    for suffix in ('stdout.bin', 'stderr.bin'):
        path = folder / f'{name}.{suffix}'
        entry[suffix] = {'path': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size}
    return entry


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--devices', type=int)
    group.add_argument('--allowed-devices', type=int, nargs='+')
    parser.add_argument('--max-length', type=int, required=True)
    parser.add_argument('--samples-per-label', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--alphabet-size', type=int)
    parser.add_argument('--length-mode', choices=['near-max', 'uniform'], default='near-max')
    parser.add_argument('--event-profile', choices=['uniform', 'skewed'], default='uniform')
    parser.add_argument('--max-attempts-per-label', type=int)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--hard-seconds', type=float, default=7)
    parser.add_argument('--generation-seconds', type=float, default=120)
    parser.add_argument('--enumerate', action='store_true')
    parser.add_argument('--reuse-input', action='store_true', help='reuse out/data; generation arguments are metadata only')
    args = parser.parse_args(argv)
    if any(not math.isfinite(x) or x <= 0 for x in (args.seconds, args.hard_seconds, args.generation_seconds)):
        parser.error('time limits must be finite and positive')
    if args.hard_seconds <= args.seconds:
        parser.error('hard-seconds must exceed cooperative seconds')
    actual_hashes = {str(path): digest(path) for path in FROZEN}
    if any(actual_hashes[str(path)] != expected for path, expected in FROZEN.items()):
        parser.error('frozen source integrity mismatch; preserve versions and review a new binding')
    actual_hashes[str(Path(__file__).resolve())] = digest(Path(__file__).resolve())
    data = args.out.resolve() / 'data'
    if args.reuse_input:
        if not (data / 'world.json').is_file() or not (data / 'solver_input.json').is_file():
            parser.error('reuse requires existing out/data/world.json and solver_input.json')
    elif data.exists():
        parser.error('out/data already exists; use --reuse-input or a new out')
    run = args.out.resolve() / 'runs' / uuid.uuid4().hex
    run.mkdir(parents=True)
    record = {'schema_version': 1, 'python': sys.executable, 'python_version': sys.version,
              'source_hashes': actual_hashes, 'run': str(run), 'reuse_input': args.reuse_input,
              'complete': False, 'full_partition_listing': False,
              'requested_parameters': {key: str(value) if isinstance(value, Path) else value
                                       for key, value in vars(args).items()},
              'enumeration_requested': args.enumerate}
    try:
        if args.reuse_input:
            record['generation'] = {'execution_status': 'reused', 'wall_seconds': None}
            record['generation_shortfall'] = None
        else:
            command = [sys.executable, '-B', '-X', 'utf8', str(HERE / 'generate_v1.py'),
                       '--max-length', str(args.max_length), '--samples-per-label', str(args.samples_per_label),
                       '--seed', str(args.seed), '--out', str(data), '--length-mode', args.length_mode,
                       '--event-profile', args.event_profile]
            command += ['--devices', str(args.devices)] if args.devices is not None else ['--allowed-devices', *map(str, args.allowed_devices)]
            for key in ('alphabet_size', 'max_attempts_per_label'):
                if getattr(args, key) is not None:
                    command += ['--' + key.replace('_', '-'), str(getattr(args, key))]
            record['generation'] = capture(command, run, 'generation', args.generation_seconds)
            record['generation_shortfall'] = record['generation'].get('exit_code') == 3
            if record['generation'].get('exit_code') not in (0, 3):
                record['status'] = 'generation_failed'
                return 1
        observational = data / 'solver_input.json'
        record['solver_input'] = {'path': str(observational), 'sha256': digest(observational)}
        # Never open world.json. Validate the observational boundary before
        # passing the input path alone to a fresh baseline subprocess.
        with observational.open(encoding='utf-8') as stream:
            sample = json.load(stream)
        if not isinstance(sample, dict) or set(sample) != {'alphabet', 'positive', 'negative'}:
            raise ValueError('solver input has forbidden or missing fields')
        if any(not isinstance(sample[key], list) for key in sample):
            raise ValueError('observational fields must be lists')
        record['actual_sample_counts'] = {label: len(sample[label]) for label in ('positive', 'negative')}
        del sample
        command = [sys.executable, '-B', '-X', 'utf8', str(BASELINE / 'unrestricted_cli_v2.py'),
                   str(observational), '--seconds', str(args.seconds)]
        if args.enumerate:
            command.append('--enumerate')
        record['inference'] = capture(command, run, 'inference', args.hard_seconds)
        record['complete'] = False
        try:
            with (run / 'inference.stdout.bin').open(encoding='utf-8') as stream:
                result = json.load(stream)
            if not isinstance(result, dict):
                raise ValueError('solver output must be a JSON object')
            shutil.copyfile(run / 'inference.stdout.bin', run / 'result.json')
            record['solver_status'] = result.get('status')
            record['complete'] = (record['inference'].get('exit_code') == 0 and result.get('complete') is True)
            record['full_partition_listing'] = (record['complete'] and args.enumerate and
                                                 isinstance(result.get('enumerated_partitions'), list))
            record['status'] = 'complete' if record['complete'] else 'incomplete_or_failed'
        except (ValueError, OSError) as exc:
            record.update(status='incomplete_or_failed', result_parse_error=str(exc), full_partition_listing=False)
        return 0 if record['complete'] else 3
    except (OSError, ValueError) as exc:
        record.update(status='environment_or_input_error', error=str(exc), complete=False)
        return 1
    finally:
        (run / 'manifest.json').write_text(json.dumps(record, indent=2, sort_keys=True), encoding='utf-8')
        print(json.dumps({'run': str(run), 'status': record.get('status'), 'complete': record.get('complete', False)}))


if __name__ == '__main__':
    raise SystemExit(main())

"""One authorized integration smoke, with durable capture and independent small oracle."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / 'audit'
OUT = HERE / 'smoke_case_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(partition):
    return tuple(sorted(tuple(sorted(block)) for block in partition))


def oracle(data):
    found = set()
    def walk(i, blocks):
        if i == len(data['alphabet']):
            langs = [{''.join(c for c in p if c in b) for p in data['positive']} for b in blocks]
            if all(any(''.join(c for c in n if c in b) not in lang
                       for b, lang in zip(blocks, langs)) for n in data['negative']):
                found.add(canonical(blocks))
            return
        symbol = sorted(data['alphabet'])[i]
        for block in blocks:
            block.append(symbol)
            walk(i + 1, blocks)
            block.pop()
        blocks.append([symbol])
        walk(i + 1, blocks)
        blocks.pop()
    walk(0, [])
    return found


def family(result):
    if result.get('complete') is not True or not isinstance(result.get('enumerated_partitions'), list):
        raise ValueError('missing complete enumeration')
    rows = result['enumerated_partitions']
    found = {canonical(row['partition']) for row in rows}
    if len(found) != len(rows) or len(found) != result['partition_count']:
        raise ValueError('duplicate/missing partition or count mismatch')
    spectrum = {str(k): sum(len(p) == k for p in found) for k in range(1, len(result['alphabet']) + 1)}
    if spectrum != result['partition_count_by_k']:
        raise ValueError('spectrum mismatch')
    for row in result['pair_relations']:
        a, b = row['symbols']
        same = sum(any(a in block and b in block for block in p) for p in found)
        if same != row['same_partition_count'] or len(found) - same != row['different_partition_count']:
            raise ValueError('pair count mismatch against full family')
        for field, together in [('same_partition_witness', True), ('different_partition_witness', False)]:
            witness = row[field]
            if witness is not None:
                part = canonical(witness)
                if part not in found or any(a in block and b in block for block in part) != together:
                    raise ValueError('invalid pair witness')
    return found


def main():
    OUT.mkdir(exist_ok=False)
    command = [sys.executable, '-B', '-X', 'utf8', str(HERE / 'run_case_v1.py'),
               '--devices', '2', '--alphabet-size', '4', '--max-length', '64',
               '--samples-per-label', '2', '--seed', '20261103', '--length-mode',
               'near-max', '--event-profile', 'uniform', '--enumerate', '--out', str(OUT)]
    record = {'command': command, 'cwd': str(HERE.parents[3]), 'python': sys.version,
              'script_sha256': sha(Path(__file__)), 'pipeline_sha256': sha(HERE / 'run_case_v1.py'),
              'grid_timing_included': False, 'execution_status': 'started'}
    (OUT / 'outer_started.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    started = time.perf_counter()
    with (OUT / 'outer.stdout.bin').open('wb') as stdout, (OUT / 'outer.stderr.bin').open('wb') as stderr:
        try:
            process = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=150, check=False)
            record.update(exit_code=process.returncode, execution_status='exited')
        except subprocess.TimeoutExpired:
            record.update(exit_code=None, execution_status='hard_timeout')
        except OSError as exc:
            record.update(exit_code=None, execution_status='environment_error', error=str(exc))
    record['wall_seconds'] = time.perf_counter() - started
    record['stdout_sha256'] = sha(OUT / 'outer.stdout.bin')
    record['stderr_sha256'] = sha(OUT / 'outer.stderr.bin')
    (OUT / 'outer_result.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    evidence = {'status': 'not_compared', 'no_additional_provider_execution': True}
    try:
        if record.get('exit_code') != 0:
            raise ValueError('outer pipeline did not complete successfully; retained without retry')
        message = json.loads((OUT / 'outer.stdout.bin').read_bytes())
        run = Path(message['run'])
        acceptance_path = AUDIT / 'SMALL_CONTROL_ACCEPTANCE_V3.json'
        accepted = json.loads(acceptance_path.read_bytes())
        target = next(r for r in accepted['rows'] if r['K'] == 2 and r['max_length'] == 64)
        reference_input = Path(target['input'])
        reference_stdout = AUDIT / 'attempts' / target['attempt_id'] / 'stdout.bin'
        data = json.loads((OUT / 'data' / 'solver_input.json').read_bytes())
        saved = json.loads(reference_input.read_bytes())
        actual = json.loads((run / 'result.json').read_bytes())
        reference = json.loads(reference_stdout.read_bytes())
        actual_family, reference_family, independent = family(actual), family(reference), oracle(data)
        if data != saved or actual_family != reference_family or actual_family != independent:
            raise ValueError('parsed input or full canonical family differs')
        world = json.loads((OUT / 'data' / 'world.json').read_bytes())
        reference_world = json.loads(Path(target['world']).read_bytes())
        if any(world[field] != reference_world[field] for field in ('devices', 'ownership', 'alphabet', 'seed')):
            raise ValueError('generated complete devices differ from saved control')
        for label in ('positive', 'negative'):
            for word in data[label]:
                states = [d['start'] for d in world['devices']]
                for event in word:
                    owner = world['ownership'][event]
                    states[owner] = world['devices'][owner]['transitions'][states[owner]][event]
                accepts = all(s in d['accepting'] for s, d in zip(states, world['devices']))
                if accepts != (label == 'positive'):
                    raise ValueError('independent device replay disagrees with label')
        evidence.update(status='passed_exact_input_world_and_full_family',
                        parsed_input_identical=True, complete_devices_identical=True,
                        independent_label_replay=True, canonical_family=sorted(actual_family),
                        partition_count=len(actual_family), spectrum=actual['partition_count_by_k'],
                        independent_full_set_oracle=True, pair_counts_and_witnesses_checked=True,
                        pipeline_run=str(run), reference_attempt_id=target['attempt_id'],
                        hashes={str(p): sha(p) for p in (acceptance_path, reference_input, reference_stdout,
                                Path(target['world']), OUT / 'data' / 'solver_input.json',
                                OUT / 'data' / 'world.json', run / 'result.json')})
    except Exception as exc:
        evidence.update(status='failed_preserved_no_retry', error=repr(exc))
    (OUT / 'equivalence_evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'outer_exit': record.get('exit_code'), 'comparison': evidence['status']}))
    return 0 if evidence['status'] == 'passed_exact_input_world_and_full_family' else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Small reproducible advisor demo. Standard-library Python only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--large', action='store_true',
                        help='also replay the saved C020 input with trusted K20')
    args = parser.parse_args()
    run = HERE / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(parents=True, exist_ok=False)
    alpha = list('abcd')
    unique = dict(alphabet=alpha, positive=['abcd'], negative=['bacd', 'abdc'])
    cases = [
        ('unique_K2', unique, 2, 5, 'certified_unique'),
        ('ambiguous_unknown_K', unique, None, 5, 'ambiguous'),
        ('ambiguous_same_summary_K2', dict(alphabet=alpha, positive=['abcd'],
                                         negative=['bacd', 'badc']), 2, 5, 'ambiguous'),
        ('incompatible_K2', dict(alphabet=alpha, positive=['bacd', 'abdc'],
                                 negative=['abcd']), 2, 5, 'incompatible'),
        ('unresolved_zero_budget', unique, 2, 0, 'unresolved'),
    ]
    if args.large:
        data = json.loads((ROOT / 'results/2026-11-04/scaling_v20/audit/fixtures_v1/C/solver_input.json').read_bytes())
        cases.append(('large_C_trusted_K20', data, 20, 20, 'certified_unique'))
    records = []
    for name, data, known_k, seconds, expected in cases:
        target = run / (name + '.input.json')
        target.write_text(json.dumps(data, ensure_ascii=False), encoding='utf8')
        command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'partition.py'),
                   str(target), '--seconds', str(seconds)]
        if known_k is not None:
            command += ['--known-k', str(known_k)]
        child = subprocess.run(command, capture_output=True, timeout=seconds + 5)
        (run / (name + '.stdout.bin')).write_bytes(child.stdout)
        (run / (name + '.stderr.bin')).write_bytes(child.stderr)
        result = json.loads(child.stdout)
        assert result['status'] == expected, (name, result['status'])
        assert child.returncode == (3 if expected == 'unresolved' else 0)
        print(name + ': ' + result['status'])
        if 'partition' in result:
            print('  partition = ' + json.dumps(result['partition']))
        elif 'alternatives' in result:
            print('  alternatives = ' + json.dumps([w['blocks'] for w in result['alternatives']]))
        records.append(dict(name=name, command=command, expected=expected,
                            actual=result['status'], exit_code=child.returncode,
                            input_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                            stdout_sha256=hashlib.sha256(child.stdout).hexdigest(),
                            stderr_sha256=hashlib.sha256(child.stderr).hexdigest()))
    receipt = dict(status='passed', presentation_demo_not_benchmark=True,
                   python=sys.version, records=records,
                   source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   entry_sha256=hashlib.sha256((ROOT / 'partition.py').read_bytes()).hexdigest())
    (run / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')
    print('Saved to ' + str(run))


if __name__ == '__main__':
    main()

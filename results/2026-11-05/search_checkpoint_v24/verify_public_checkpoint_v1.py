"""Manager verification of composition, frozen sources and the public CLI."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMPL = HERE / 'implementation'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

expected = {
    'baseline_c020_v1': '5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680',
    'candidate_c024a_v1': '9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4',
    'candidate_c024b_v1': '4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3',
    'integrated_c024_v1': '0aded302c5f9b0a364e3428a8319eab15b1d96be67fd98a64d117faa1b3a1d61',
}
checks = []
for directory, digest in expected.items():
    path = IMPL / directory / 'gate_v1.py'
    assert sha(path) == digest
    checks.append({'path': str(path), 'sha256': digest})
historical = ROOT / 'results/2026-11-04/scaling_v20/implementation/candidate_c2_v1/gate_v1.py'
assert sha(historical) == expected['baseline_c020_v1']
a = (IMPL / 'candidate_c024a_v1/gate_v1.py').read_text(encoding='utf-8')
b = (IMPL / 'candidate_c024b_v1/gate_v1.py').read_text(encoding='utf-8')
combined = a[:a.index('        solutions = []\n')] + b[b.index('        solutions = []\n'):]
combined = combined.replace("METHOD = 'C024-A-forced-atom-bipartition-gate-v1'", "METHOD = 'C024-integrated-exact-search'")
assert combined == (IMPL / 'integrated_c024_v1/gate_v1.py').read_text(encoding='utf-8')
summary = json.loads((HERE / 'audit/FINAL_SUMMARY_V2.json').read_text(encoding='utf-8'))
assert summary['A']['automatic_promotion_criteria_pass']
assert summary['B']['automatic_promotion_criteria_pass']
assert summary['integrated']['errors'] == summary['integrated']['CLI_smoke_errors'] == 0
assert summary['correctness']['capture_integrity']['errors'] == []

cases = [
    ('unknown_K', HERE / 'audit/fixtures/obstruction_m10.json', ['--seconds', '20'], 0, 'certified_unique'),
    ('known_K', ROOT / 'results/2026-11-04/scaling_v20/audit/fixtures_v1/D/solver_input.json', ['--known-k', '4', '--seconds', '20'], 0, 'certified_unique'),
    ('expired', HERE / 'audit/fixtures/obstruction_m10.json', ['--seconds', '0'], 3, 'unresolved'),
]
rows = []
for name, input_path, args, code, status in cases:
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'partition.py'), str(input_path), *args]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=8)
    elapsed = time.perf_counter() - started
    output = json.loads(result.stdout.decode('utf-8'))
    row = {'name': name, 'command': command, 'exit_code': result.returncode,
           'process_seconds': elapsed, 'stdout': output, 'stderr': result.stderr.decode('utf-8'),
           'input_sha256': sha(input_path), 'public_entry_sha256': sha(ROOT / 'partition.py')}
    rows.append(row)
    assert result.returncode == code and output['status'] == status
    assert output['method'] == 'C024-integrated-exact-search'
    assert not result.stderr
    if status == 'unresolved':
        assert 'partition' not in output and 'alternatives' not in output

report = {'passed': True, 'frozen_sources': checks, 'composition_matches': True,
          'historical_baseline_unchanged': True, 'public_CLI_checks': rows,
          'environment': {'executable': sys.executable, 'python': sys.version, 'platform': platform.platform()},
          'performance_claim': 'none; these are functional post-promotion checks'}
(HERE / 'PUBLIC_VERIFICATION_V1.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'public_CLI_checks': len(rows), 'composition_matches': True}))

"""Accept immutable C007 v4 independent evidence; preserve v3 acceptance."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def read(p): return json.loads((ROOT / p).read_text(encoding='utf-8'))
def ref(p): return {'path': p, 'sha256': sha256((ROOT / p).read_bytes()).hexdigest()}

provider = ref('implementation/finest_solver_v4.py')
assert provider['sha256'] == 'c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff'
cli = ref('implementation/finest_cli_v2.py')
assert cli['sha256'] == '46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879'
gate_path = 'audit/validation_v2/provider_gate_v4.json'
gate = read(gate_path)
assert gate['status'] == 'accepted' and not gate['failures']
assert gate['adaptive_rows'] == gate['reference_rows'] == gate['valid_rows'] == 218
assert gate['independent_certificate_replays'] == 436
assert all(gate['mutations_rejected'].values())
assert all(not x['source_failures'] for x in gate['capture_integrity'].values())
long_path = 'audit/scale_v1/long_v4_replay_v1.json'
long = read(long_path)
assert long['status'] == 'accepted' and not long['failures']
assert long['context_length'] == 65536 and long['blocks'] == 4
scale_path = 'audit/scale_v1/scale_validation_v4.json'
scale = read(scale_path)
assert scale['status'] == 'accepted_with_censoring'
assert scale['accepted_cells'] == 4 and scale['censored_cells'] == 1
event = dict(cycle='C007', event='master_accepts_v4_correctness_and_scale',
    at_utc=datetime.now(timezone.utc).isoformat(), user_date='2026-11-02',
    provider=provider, cli=cli, gate=ref(gate_path), long_case=ref(long_path),
    historical_v3_scale=ref(scale_path), unique_main_inputs=218, mode_outputs=436,
    scientific_status='confirmed_under_declared_sample_target',
    target='Unique finest sample-compatible partition; not hidden architecture recovery',
    scope_note='Large cells are structured cases; no arbitrary-data capacity guarantee',
    timing_note='Long v4 versus censored v3 is exploratory, not a repeated benchmark',
    performance='pending_frozen_GO', historical_v3_acceptance='CORRECTNESS_ACCEPTANCE.json')
with (ROOT/'coordination/CORRECTNESS_ACCEPTANCE_V4.json').open('x', encoding='utf-8') as f:
    json.dump(event, f, ensure_ascii=False, indent=2)
with (ROOT/'coordination/journal.jsonl').open('a', encoding='utf-8') as f:
    f.write(json.dumps(event, ensure_ascii=False)+'\n')
print(json.dumps(dict(status='accepted', unique_inputs=218, mode_outputs=436,
    historical_v3_scale_successes=4, historical_v3_censored=1, long_v4_accepted=True)))

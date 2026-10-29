"""Accept the existing independent Stage-2 gate; authorize 15 serial jobs."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
gatepath=ROOT/'audit/stage2_gate_report_v1.json'
raw=gatepath.read_bytes()
assert sha256(raw).hexdigest()=='f1ab159020e3b16d8e6ce80e9989b68e3ec646d898e45cb323a1ed436883adcf'
gate=json.loads(raw)
assert gate['acceptance']=='accepted'
assert not gate['source_integrity_errors'] and not gate['capture_reconciliation_errors']
for name,wanted in gate['source_bindings'].items():
    assert sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
stamp=datetime.now(timezone.utc).isoformat()
record=dict(at_utc=stamp,client_acceptance_date='2026-10-29',
    gate='audit/stage2_gate_report_v1.json',gate_sha256=sha256(raw).hexdigest(),
    scientific_status='verified_under_declared_assumptions',
    case_records=107,canonical_normalized_payloads=104,duplicate_payload_groups=3,
    active_entrypoint='solver_v2.py',
    serial_timing_authorization=dict(worker='/root/auditor_v4',
        class_name='known-k finite local languages of at most two words',
        methods=['general V3 with local_word_cap=2','QOP001 bounded certificate'],
        max_solutions=2,cells=[dict(alphabet=16,k=4),dict(alphabet=128,k=8)],
        repetitions=3,wall_jobs=12,allocation_jobs_at_most=3,total_jobs_at_most=15,
        output_scope='full API result serialized in child; independent validation after raw capture',
        hard_seconds_per_job=30,per_provider_budget_seconds=900,
        allocation_scope='separate runs; state exact tracemalloc scope, not RSS',
        censor_incomplete=True,other_worker_provider_runs='not permitted during timing window'),
    next='Close measured subset, final report, one byte-integrity scan and scoped local Git commit.')
with (ROOT/'coordination/STAGE2_ACCEPTANCE.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage2_gate_accepted_and_serial_measurement_authorized',**record),ensure_ascii=False)+'\n')
print(json.dumps(dict(stage2='accepted',records=107,normalized_payloads=104,wall_jobs=12,memory_jobs_at_most=3)))

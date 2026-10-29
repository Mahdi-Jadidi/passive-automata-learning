"""Close the Stage-1 timing window and authorize separate Stage-2 attempts."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
accepted = json.loads((ROOT/'coordination/STAGE1_ACCEPTANCE.json').read_text(encoding='utf-8'))
assert accepted['scientific_status'] == 'verified_under_declared_assumptions'
old = json.loads((ROOT/'coordination/runtime_stage1.json').read_text(encoding='utf-8'))
for item in old['files']:
    assert sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256']
files = []
for name in ['solver.py','general/known_k_v3.py','structural/singleton_solver_v1.py',
             'structural/singleton_solver_v2.py','structural/singleton_solver_v3.py',
             'structural/bounded_certificate_v1.py','audit/capture.py']:
    raw = (ROOT/name).read_bytes()
    files.append(dict(path=name,sha256=sha256(raw).hexdigest(),bytes=len(raw)))
stamp = datetime.now(timezone.utc).isoformat()
record = dict(at_utc=stamp, version='C004-stage2-R1', stage2_provider_execution='authorized',
    stage1_correctness_accepted='coordination/STAGE1_ACCEPTANCE.json',
    stage1_timing_window='closed_after_auditor_reported_63_of_63_schedule_rows_complete',
    stage1_performance_aggregate='reconciliation_pending_not_yet_final_acceptance',
    files=files, scientific_status='new_candidates_pending_independent_audit',
    scopes=['sparse known-k singleton exact search','unknown-k singleton sufficient certificate',
            'at-most-q local languages and q-opposition certificate',
            'long contextual witness coverage for unrestricted known-k regular factors'],
    public_inference_input_must_omit_k=True,
    new_source_versions_required_for_bug_fixes=True,
    official_phase2_timings='held_until_source_and_corpus_correctness_gate',
    script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
with (ROOT/'coordination/STAGE2_GO.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage2_authorized_after_stage1_timing',**record),ensure_ascii=False)+'\n')
print(json.dumps(dict(version=record['version'],files=len(files),stage2='authorized',stage1_aggregate='pending')))

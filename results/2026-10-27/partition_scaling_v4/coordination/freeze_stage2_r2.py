"""Preserve R1 and freeze the interruption-safe Stage-2 candidates."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
old=json.loads((ROOT/'coordination/STAGE2_GO.json').read_text(encoding='utf-8'))
for item in old['files']:
    assert sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
paths=[x['path'] for x in old['files']]
paths=[{'solver.py':'solver_v2.py','structural/singleton_solver_v3.py':'structural/singleton_solver_v4.py'}.get(x,x) for x in paths]
files=[]
for name in paths:
    raw=(ROOT/name).read_bytes()
    files.append(dict(path=name,sha256=sha256(raw).hexdigest(),bytes=len(raw)))
perfpath=ROOT/'audit/stage1_performance_report_v2.json'
perf=json.loads(perfpath.read_text(encoding='utf-8-sig'))
assert perf['acceptance']=='accepted'
assert perf['gates']['bridge_answer_comparison_count']==6
assert perf['gates']['ledger_rows']==63
stamp=datetime.now(timezone.utc).isoformat()
record=dict(at_utc=stamp,version='C004-stage2-R2',files=files,
    supersedes='C004-stage2-R1 for public CLI and unknown-k singleton provider only',
    rejected_provider='structural/singleton_solver_v3.py',
    defect='structural/DEFECT_S003_INTERRUPT_001.md',
    historical_entrypoint='solver.py',active_entrypoint='solver_v2.py',
    scientific_status='proof_scope_unchanged_new_implementation_pending_independent_audit',
    official_phase2_timings='not_yet_authorized')
with (ROOT/'coordination/runtime_stage2_r2.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage1_performance_accepted',at_utc=stamp,
        report='audit/stage1_performance_report_v2.json',sha256=sha256(perfpath.read_bytes()).hexdigest(),
        rows=63,passed=59,censored=4,
        timing_output_scope='normalized first-answer summary; full correctness evidence separate',
        superseded_aggregate_preserved='audit/stage1_performance_report_v1.json'),ensure_ascii=False)+'\n')
    handle.write(json.dumps(dict(event='stage2_interruption_bug_preserved_and_candidates_refrozen',**record),ensure_ascii=False)+'\n')
print(json.dumps(dict(version=record['version'],files=len(files),entrypoint=record['active_entrypoint'])))

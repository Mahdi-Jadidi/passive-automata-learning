"""Accept the frozen independent correctness gate and open serial timing."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT/'audit/stage1_gate_report_v1.json'
raw = GATE.read_bytes()
assert sha256(raw).hexdigest() == 'd73f6f7175bb1948c9529a8c22284f84d8c21b98b2e554a6cc7622f6614b9fcb'
gate = json.loads(raw)
assert gate['gate'] == 'accepted' and gate['stage1_correctness_complete']
runtime = json.loads((ROOT/'coordination/runtime_stage1.json').read_text(encoding='utf-8'))
for item in runtime['files']:
    assert sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256']
stamp = datetime.now(timezone.utc).isoformat()
record = dict(at_utc=stamp, gate='audit/stage1_gate_report_v1.json',
    gate_sha256=sha256(raw).hexdigest(), decision='stage1_correctness_accepted_under_declared_scope',
    full_set_cases=80, small_k2_parent_bridge_cases=33, long_certificates_checked=6,
    scientific_status='verified_under_declared_assumptions',
    serial_performance_window='authorized_for_auditor_v4_only',
    other_workers='no provider experiments during timing window',
    stage2_provider_execution='held_until_stage1_performance_finished',
    per_job_hard_seconds=30, per_provider_measured_budget_seconds=900,
    censored_parent_long_case_retained=True,
    metadata_path_erratum='coordination/AUDIT_PATH_ERRATA_01.json')
with (ROOT/'coordination/STAGE1_ACCEPTANCE.json').open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
errata = dict(original='audit/stage1_gate_report_v1.json', original_preserved=True,
    issue='old-source metadata paths have one extra ../; recorded hashes and actual captured source bindings are unchanged',
    resolution_base='C004 root',
    correct_paths_from_c004_root={
      'old_c003_fixed_word':'../../2026-10-26/partition_discovery_v3/structural/fixed_word_solver.py',
      'old_c003_general':'../../2026-10-26/partition_discovery_v3/general/general_solver.py',
      'old_c003_support':'../../2026-10-26/partition_discovery_v3/general/support.py',
      'c002_graph_dependency':'../../2026-10-26/partition_constraints_v2/baseline/partition_solver.py'},
    scientific_effect='metadata-only; no reexecution needed')
for key, name in errata['correct_paths_from_c004_root'].items():
    assert sha256((ROOT/name).read_bytes()).hexdigest() == gate['source_freeze'][key]['sha256']
with (ROOT/'coordination/AUDIT_PATH_ERRATA_01.json').open('x', encoding='utf-8') as handle:
    json.dump(errata, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage1_gate_accepted_serial_timing_authorized', **record),ensure_ascii=False)+'\n')
print(json.dumps(record, ensure_ascii=False))

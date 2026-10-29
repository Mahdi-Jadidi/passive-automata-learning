"""Accept completed measurements and freeze the final C004 runtime/evidence."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))


gate_name='audit/stage2_timing_gate_v1.json'
gate=read(gate_name)
assert digest(ROOT/gate_name)=='89bd39d109d3751e00951bcd5570294e6d2f69d84d22629555074bd4654a8d1e'
assert gate['acceptance']=='accepted' and not gate['validation_errors']
assert gate['job_counts']['actual_wall']==12 and gate['job_counts']['actual_memory']==3
assert gate['job_counts']['fresh_child_processes']==15
for name,wanted in gate['source_bindings'].items():
    assert digest(ROOT/name)==wanted,name
assert digest(ROOT/'audit/stage2_timing_protocol_v1.json')==gate['protocol_sha256']
assert digest(ROOT/'audit/stage2_timing_protocol_freeze_v1.json')==gate['protocol_freeze_record_sha256']
for item in gate['inputs'].values():
    assert digest(ROOT/'audit'/Path(item['input_path'].replace('\\','/')))==item['sha256']
runtime=read('coordination/runtime_stage2_r2.json')
for item in runtime['files']:
    assert digest(ROOT/item['path'])==item['sha256']
accepted_reports=[]
for name in ['audit/stage1_gate_report_v1.json','audit/stage1_performance_report_v2.json',
             'audit/stage2_gate_report_v1.json',gate_name]:
    report=read(name)
    assert report.get('acceptance',report.get('gate'))=='accepted'
    accepted_reports.append(dict(path=name,sha256=digest(ROOT/name)))
stamp=datetime.now(timezone.utc).isoformat()
record=dict(version='C004-final-R2',at_utc=stamp,client_delivery_date='2026-10-29',
    files=runtime['files'],active_entrypoint='solver_v2.py',accepted_reports=accepted_reports,
    scientific_status='verified_under_declared_assumptions',
    measured_invocation_archive_complete=True,historical_pre_execution_archive_complete=False,
    archival_gap='audit/stage2_timing_preservation_inventory_v1.json',
    archival_gap_sha256=digest(ROOT/'audit/stage2_timing_preservation_inventory_v1.json'),
    no_fabricated_reconstruction=True,previous_cycle_replaced=False,
    source_script_sha256=digest(Path(__file__)))
with (ROOT/'coordination/runtime_final.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage2_matched_measurements_accepted',at_utc=stamp,
        report=gate_name,sha256=digest(ROOT/gate_name),wall_jobs=12,memory_jobs=3,
        validation_errors=0,output_scope='full API',historical_archive_gap=record['archival_gap']),ensure_ascii=False)+'\n')
    handle.write(json.dumps(dict(event='idea_outcome',at_utc=stamp,idea_id='C004-QOP001',
        scientific_status='verified_under_declared_assumptions',novelty_claim=False,
        evidence='audit/stage2_gate_report_v1.json'),ensure_ascii=False)+'\n')
    handle.write(json.dumps(dict(event='final_runtime_frozen',at_utc=stamp,
        manifest='coordination/runtime_final.json',sha256=digest(ROOT/'coordination/runtime_final.json'),
        active_entrypoint='solver_v2.py',remaining='final report promotion and delivery byte-integrity/local Git closure'),ensure_ascii=False)+'\n')
print(json.dumps(dict(runtime='C004-final-R2',accepted_reports=len(accepted_reports),source_files=len(runtime['files']))))

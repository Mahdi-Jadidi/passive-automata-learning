"""Record the final C004 delivery from existing reports; run no providers."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
OUT=ROOT/'coordination/CYCLE_OUTCOME.json'
assert not OUT.exists(),'Do not overwrite a cycle outcome'


def evidence(name):
    path=ROOT/name
    return dict(path=name,sha256=sha256(path.read_bytes()).hexdigest())


runtime=json.loads((ROOT/'coordination/runtime_final.json').read_text(encoding='utf-8'))
for item in runtime['files']:
    assert sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
for item in runtime['accepted_reports']:
    assert sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
integrity='coordination/integrity_runs/20261029T090333.672199Z_8f85e63e/result.json'
byte_review=json.loads((ROOT/integrity).read_text(encoding='utf-8'))
assert byte_review['all_match'] and byte_review['check_count']==1534
checked_links=0
for path in [ROOT/'README_FA.md',ROOT/'RESEARCH_REPORT_FA.md',ROOT/'MASTER_DECISION_FA.md',
             ROOT/'RESUME_FA.md',WORKSPACE/'START_HERE_FA.md']:
    for url in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)',path.read_text(encoding='utf-8-sig')):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',url) or url.startswith('#'):
            continue
        target=(path.parent/url.split('#',1)[0]).resolve()
        target.relative_to(WORKSPACE)
        assert target.exists(),(str(path),url)
        checked_links+=1

execution_counts=Counter()
unfinished=[]
attempts=list((ROOT/'audit/attempts').iterdir())
for path in attempts:
    if not path.is_dir():
        continue
    result=path/'result.json'
    if result.exists():
        record=json.loads(result.read_text(encoding='utf-8-sig'))
        execution_counts[record.get('execution_status','not_classified')]+=1
    else:
        unfinished.append(dict(attempt_id=path.name,execution_status='final_record_unavailable',
                               files=sorted(x.name for x in path.iterdir() if x.is_file())))
stamp=datetime.now(timezone.utc).isoformat()
record=dict(cycle='C004',at_utc=stamp,client_delivery_date='2026-10-29',
    research_round_complete=True,scientific_status='verified_under_declared_assumptions',
    execution_status='required_accepted_studies_complete',
    active_entrypoint='solver_v2.py',runtime=evidence('coordination/runtime_final.json'),
    accepted_reports=runtime['accepted_reports'],
    delivery_artifacts=[evidence(name) for name in ['RESEARCH_REPORT_FA.md','README_FA.md',
        'MASTER_DECISION_FA.md','coordination/report_promotion.json','coordination/AUDIT_REPORTING_ERRATA.md']],
    byte_integrity=evidence(integrity),byte_comparisons=1534,delivery_links_checked=checked_links,
    scope_counts=dict(stage1_frozen_case_records=212,stage1_small_full_sets=80,
        stage1_parent_k2_bridges=33,stage1_measured_rows=63,
        stage1_validation_pass=59,stage1_censored=4,
        stage2_case_records=107,stage2_canonical_payloads=104,stage2_duplicate_payload_groups=3,
        stage2_s002_full_sets=82,stage2_general_q2_full_sets=88,
        stage2_qop_scale_certificates=4,stage2_long_context_unique_cases=4,
        stage2_cli_command_checks=12,stage2_matched_wall_jobs=12,stage2_allocation_jobs=3,
        stage2_incomplete_large_exact_wall_jobs=3,counts_are_not_additive_independent_observations=True),
    captured_attempt_statuses=dict(execution_counts),unfinished_capture_records=unfinished,
    all_measured_provider_invocations_have_captures=True,
    historical_pre_execution_archive_complete=False,
    explicit_archival_gap=evidence('audit/stage2_timing_preservation_inventory_v1.json'),
    historical_bytes_reconstructed=False,previous_cycles_unchanged=True,
    future_unexecuted_ideas='coordination/NEXT_IDEAS.json',
    automatic_new_cycle=False,
    limits=['class-conditional identification, not arbitrary passive DFA recovery',
            'selected synthetic coverage families; exponential search remains possible',
            'RPNI and empirical state-explosion reduction not tested',
            'historical zero-job protocol/freeze/executor bytes missing, explicitly recorded'],
    script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
with OUT.open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    for event in [dict(event='final_report_promoted',source='structural/C004_FINAL_REPORT_CANDIDATE_FA_REV3_FINAL.md',
                       promotion='coordination/report_promotion.json',target='RESEARCH_REPORT_FA.md'),
                  dict(event='final_byte_integrity_and_links_checked',checks=1534,failures=0,
                       report=integrity,links=checked_links,scientific_proof_inferred_from_hashes=False),
                  dict(event='cycle_completed',outcome='coordination/CYCLE_OUTCOME.json',
                       scientific_status=record['scientific_status'],archival_gap_disclosed=True,
                       new_cycle_started=False)]:
        handle.write(json.dumps(dict(at_utc=stamp,**event),ensure_ascii=False)+'\n')
print(json.dumps(dict(outcome=str(OUT),links_checked=checked_links,
                     capture_statuses=dict(execution_counts),unfinished_capture_records=len(unfinished))))

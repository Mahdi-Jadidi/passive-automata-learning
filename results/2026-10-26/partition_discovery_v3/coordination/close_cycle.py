"""Record the master's acceptance of existing evidence; run no solvers."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
OUT = ROOT / 'coordination/CYCLE_OUTCOME.json'
assert not OUT.exists(), 'A closure record must never be overwritten'
STAMP = datetime.now(timezone.utc).isoformat()


def evidence(relative):
    path = ROOT / relative
    return dict(path=relative, sha256=sha256(path.read_bytes()).hexdigest())


accepted = []
for name in [
    'audit/validation/c002_full_v1/report.json',
    'audit/validation/generated_v1/report.json',
    'audit/validation/performance_v4/report.json',
    'audit/validation/coverage_family_infinite_v1/report_v2.json',
    'audit/validation/boundary_controls_v1/report.json',
    'general/structural_boundary_audit/run_001/report.json',
]:
    value = json.loads((ROOT / name).read_text(encoding='utf-8-sig'))
    assert value.get('accepted') is True or value.get('status') == 'accepted', name
    accepted.append(evidence(name))

integrity = 'coordination/integrity_runs/20261027T074859.860658Z_024a383b/result.json'
verified = json.loads((ROOT / integrity).read_text(encoding='utf-8'))
assert verified['all_match'] and verified['check_count'] == 5595

checked_links = 0
for path in [ROOT/'RESEARCH_REPORT_FA.md', ROOT/'README_FA.md',
             ROOT/'MASTER_DECISION_FA.md', ROOT/'RESUME_FA.md',
             ROOT/'coordination/AUDIT_ERRATA_FA.md', WORKSPACE/'START_HERE_FA.md']:
    for url in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', path.read_text(encoding='utf-8-sig')):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', url) or url.startswith('#'):
            continue
        local = (path.parent / url.split('#', 1)[0]).resolve()
        local.relative_to(WORKSPACE)
        assert local.exists(), (path, url)
        checked_links += 1

artifacts = [evidence(name) for name in [
    'RESEARCH_REPORT_FA.md', 'MASTER_DECISION_FA.md', 'README_FA.md',
    'coordination/report_promotion.json', 'coordination/MASTER_THEORY_REVIEW.md',
    'coordination/AUDIT_ERRATA_FA.md', 'coordination/runtime_manifest.json',
    'coordination/parent_manifest.json',
]]
record = dict(cycle='C003', at_utc=STAMP, client_delivery_date='2026-10-27',
    scientific_status='verified_under_declared_assumptions', execution_status='successful',
    research_round_complete=True, previous_cycle_replaced=False,
    accepted_reports=accepted, delivery_artifacts=artifacts,
    integrity=evidence(integrity), integrity_checks=5595,
    checked_delivery_links=checked_links,
    independent_checks=dict(full_partition_set_cases_per_general_method=7281,
        selected_regression_cases=78, generated_regular_product_cases=120,
        generated_regular_exact_full_set_cases=80,
        generated_regular_constructive_feasible_only_cases=40,
        fixed_word_recovered_true_partitions=120, infinite_regular_coverage_cases=24,
        infinite_regular_provider_results=96, general_boundary_cases=9,
        independent_fixed_word_boundary_cases=9, validated_performance_processes=1744,
        counts_not_additive_unique_input_totals=True),
    conclusions=[
        'Sound must-link graph with exactly two components plus feasibility certifies the partition in the unrestricted declared two-factor class.',
        'A connected bipartite opposition graph plus sample checks certifies recovery under the fixed-word factor assumption.',
        'True-partition interpretation requires a realizable target in the declared model.',
        'Generic compatible-first-answer construction does not alone identify the true partition.',
        'No overall speed advantage over fair-reference is established.',
        'No RPNI experiment or empirical passive-learning speedup is claimed.',
    ],
    failed_paths_preserved=True,
    historical_records_not_reconstructed=True,
    next_research='Relax the coverage or singleton-language assumptions in a separately specified cycle.',
    automatically_start_next_cycle=False,
    script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
with OUT.open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')

events = [
    dict(event='independent_scientific_gates_accepted', accepted_reports=accepted,
         counts=record['independent_checks'], scientific_status='verified_under_declared_assumptions'),
    dict(event='idea_outcome', idea_id='C003-GC001',
         initial_record_preserved='coordination/IDEA_C003_GC001.json',
         scientific_status='verified_under_declared_assumptions',
         evidence='audit/validation/coverage_family_infinite_v1/report_v2.json',
         novelty_claim=False),
    dict(event='negative_performance_result_retained',
         evidence='general/performance_analysis/SUMMARY_FA.md',
         conclusion='No overall speed advantage established; per-case medians and limits reported.'),
    dict(event='report_promoted_and_master_decision_recorded',
         source='structural/C003_RESEARCH_REPORT_CANDIDATE_FA_REV5_FINAL.md',
         promotion='coordination/report_promotion.json',
         decision='MASTER_DECISION_FA.md', earlier_drafts_preserved=True),
    dict(event='general_recovery_delivery_example_reviewed',
         input='examples/general_coverage.json',
         run='audit/attempts/20261026T201050.297812Z_993c8777d4',
         outcome='unique partition {a,b}|{c,d}; search exhausted in general_regular_product'),
    dict(event='master_byte_integrity_review_completed', checks=5595, failed=0,
         report=integrity, scientific_proof_inferred_from_hashes=False,
         duplicate_earlier_auditor_integrity_runs_preserved=True,
         errata='coordination/AUDIT_ERRATA_FA.md'),
    dict(event='cycle_completed', outcome='coordination/CYCLE_OUTCOME.json',
         scientific_status=record['scientific_status'], execution_status='successful',
         runtime='C003-R1', parent_cycle_files_unchanged=True,
         unapproved_new_experiments_started=False),
]
with (ROOT / 'coordination/journal.jsonl').open('a', encoding='utf-8', newline='\n') as handle:
    for event in events:
        handle.write(json.dumps(dict(at_utc=STAMP, **event), ensure_ascii=False) + '\n')
print(json.dumps(dict(outcome=str(OUT), events=len(events), checked_links=checked_links)))

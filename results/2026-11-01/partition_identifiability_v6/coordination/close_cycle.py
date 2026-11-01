"""Master closes C006 from existing accepted evidence; no experiments rerun."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return sha256(path.read_bytes()).hexdigest()
integrity_path=ROOT/'coordination/FINAL_INTEGRITY_R3_2026-11-01.json'
integrity=read(integrity_path)
assert integrity['status']=='pass' and integrity['error_count']==0
runtime=read(ROOT/'coordination/runtime_final.json')
for item in runtime['files']:
    path=ROOT/item['path']
    if not path.is_file():path=WORKSPACE/item['path']
    assert digest(path)==item['sha256'],item['path']
gate=read(ROOT/'audit/validation_v2/solver_v5_gate_v6.json')
bench=read(ROOT/'audit/benchmark_v1/benchmark_results_v2.json')
assert gate['scientific_status']=='passed'
assert gate['exact_full_bipartition_sets_matched']==135
assert gate['expected_all_k_existence_matched']==135
assert bench['scientific_status']=='passed' and not bench['errors']
assert bench['actual_captured_provider_processes']==6
assert bench['independently_validated_provider_processes']==6
assert all(j['capture_status']=='success' and j['independent_validation']=='passed' for j in bench['jobs'])
attempt_statuses={}
for directory in (ROOT/'evidence/attempts').iterdir():
    if not directory.is_dir():continue
    result=read(directory/'result.json')
    key=result['execution_status']
    attempt_statuses[key]=attempt_statuses.get(key,0)+1
assert sum(attempt_statuses.values())==integrity['counts']['attempts']
refs=['coordination/runtime_final.json','coordination/CORRECTNESS_ACCEPTANCE.json',
 'coordination/PERFORMANCE_ACCEPTANCE.json','audit/AUDIT_GATE_V1.json',
 'audit/validation_v2/solver_v5_gate_v6.json','audit/validation_v1/oracle_crosscheck.json',
 'audit/benchmark_v1/benchmark_results_v2.json','README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md']
outcome=dict(cycle='C006',status='complete',user_completion_date='2026-11-02',
 started_date='2026-11-01',at_utc=datetime.now(timezone.utc).isoformat(),
 scientific_status='confirmed_under_retained_assumptions',parent_commit='eb521fdd',
 removed_assumptions=['known factor count for existential nontrivial decomposition decision','finite local-language word-cardinality cap'],
 retained_assumptions=['known disjoint alphabet','independent factors preserving local order','exact whole-word labels','complete words'],
 output_scope='Compatible bipartition, replayable proof of no compatible k>=2 partition, or incomplete; not hidden-k/architecture recovery',
 independent_case_records=135,unique_canonical_payloads=133,
 projection_witness_checks=gate['provider_witnesses_independently_checked'],
 obstruction_replays=gate['independently_replayed_no_decomposition_certificates'],
 replay_caveat='11 certificate checks include an extra duplicate manager sample; they are not 11 independent inputs',
 benchmark_processes=6,benchmark_cells=['large_connected_m64','small_full_cover_m4'],
 benchmark_scope='Three fresh serial processes per cell, full JSON; no old-method comparison or memory measurement',
 unused_data='Frozen optional_decomposable_m64 was not executed',
 attempt_statuses=attempt_statuses,unfinished_attempts=0,
 integrity=dict(path=str(integrity_path.relative_to(ROOT)),sha256=digest(integrity_path),counts=integrity['counts'],errors=0),
 preserved_failures='All provider versions, oracle/gate/postprocessing failures and both failed integrity reports retained; metadata path fixes did not change tested provider/data/output bytes',
 dormant_features=['A/B rules: theory approved but inactive in solver_v5','meet proposal: independent audit pending, no runtime implementation'],
 limitations=['Exponential worst-case search and obstruction size','Positive-only data cannot establish non-decomposability without further restrictions','True architecture generally indistinguishable from coarsenings','No RPNI or state-explosion experiment'],
 evidence=[dict(path=p,sha256=digest(ROOT/p)) for p in refs])
with (ROOT/'coordination/CYCLE_OUTCOME.json').open('x',encoding='utf-8') as f:json.dump(outcome,f,ensure_ascii=False,indent=2)
links=[]
for name in ['README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md']:
    path=ROOT/name
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):continue
        file=(path.parent/target.split('#')[0]).resolve()
        assert file.exists(),(name,target)
        links.append(dict(document=name,target=target))
with (ROOT/'coordination/DELIVERY_LINKS.json').open('x',encoding='utf-8') as f:json.dump(dict(count=len(links),links=links),f,ensure_ascii=False,indent=2)
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps(dict(event='cycle_completed',user_date='2026-11-02',at_utc=outcome['at_utc'],outcome='coordination/CYCLE_OUTCOME.json',links=len(links)),ensure_ascii=False)+'\n')
print(json.dumps(dict(status='complete',case_records=135,unique_payloads=133,processes=6,attempt_statuses=attempt_statuses,links=len(links))))

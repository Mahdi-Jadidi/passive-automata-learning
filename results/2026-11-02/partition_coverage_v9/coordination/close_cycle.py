"""Master final closure after the read-only archive check; no research reruns."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,re
ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def write_new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
integrity_path=ROOT/'coordination/FINAL_INTEGRITY.json'
integrity=read(integrity_path)
assert integrity['status']=='pass' and integrity['error_count']==0
for item in read(ROOT/'coordination/runtime_final.json')['files']:
    assert digest(WORKSPACE/item['path'])==item['sha256'],item['path']
assert (WORKSPACE/'START_HERE_FA.md').read_bytes()==(ROOT/'coordination/START_HERE_C009_SNAPSHOT.md').read_bytes()
links=[]
for doc in ['README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(ROOT/doc).read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):continue
        assert (ROOT/target.split('#')[0]).is_file(),(doc,target)
        links.append(dict(document=doc,target=target))
acceptance=read(ROOT/'coordination/FINAL_ACCEPTANCE.json')
outcome=dict(cycle='C009',status='complete',user_date='2026-11-02',at_utc=datetime.now(timezone.utc).isoformat(),
    scientific_status='confirmed_under_explicit_model_with_one_censored_scale_case',
    main_unique_inputs=129,full_sets_matched=129,projection_witness_replays=15394,
    additional_partial_control=1,input_stop_controls=9,completed_scale_cells=3,censored_scale_cells=1,
    universal_physical_recovery=False,real_dataset_evaluated=False,
    new_coverage=['trusted arbitrary allowed component counts','exact complete ownership family counting','forced same/different/ambiguous pair ownership','unique ownership beyond empty simple graph'],
    model_assumptions=['known disjoint alphabet','independent regular local languages','exact whole-word labels','actual component count belongs to trusted K'],
    future_prune='proved but not implemented or measured in this version',
    limitations=['exponential worst-case','m14 censored; oracle413 is not provider result','cooperative protected-region stop','uninstrumented witness counter','no prime/state/noise/shared-symbol enforcement'],
    acceptance=acceptance,integrity=dict(path='coordination/FINAL_INTEGRITY.json',sha256=digest(integrity_path),counts=integrity.get('counts',{})),
    references=[dict(path=n,sha256=digest(ROOT/n)) for n in ['README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md','coordination/runtime_final.json']])
write_new(ROOT/'coordination/CYCLE_OUTCOME.json',outcome)
write_new(ROOT/'coordination/DELIVERY_CHECKS.json',dict(status='pass',links=links,runtime_hashes='pass',shared_index_snapshot='pass',parent_scope='C008 immutable',research_reruns=0))
print(json.dumps(dict(status='complete',links_checked=len(links))))

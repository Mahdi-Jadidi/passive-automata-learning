import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent
def record(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
a=here.parent/'candidate_c024a_v1/gate_v1.py'
assert record(a)['sha256']=='9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4'
assert json.loads((here/'smoke_results_v1.json').read_text())['passed']
payload=dict(candidate='C024-B-v1',ready_for_source_review=True,ready_for_independent_audit=True,official_benchmarks_run=False,
 baseline=record(here.parent/'baseline_c020_v1/gate_v1.py'),frozen_a=record(a),
 files={p.name:record(p) for p in here.iterdir() if p.is_file() and p.name!='READINESS_v1.json'},
 smoke_command='py -3.14 results/2026-11-05/search_checkpoint_v24/implementation/candidate_c024b_v1/smoke_v1.py',smoke_exit_code=0,
 rule='include reject(U) iff len(masks) < known_k; only nonterminal known-K DFS after count bounds',
 limits=['Independent full audit pending','No official benchmarks','No public promotion'])
(here/'READINESS_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(ready=True,gate=record(here/'gate_v1.py'))))

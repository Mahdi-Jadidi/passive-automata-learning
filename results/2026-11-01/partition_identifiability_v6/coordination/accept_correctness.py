"""Master records acceptance of the independent fixed-source correctness gate."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
paths=['audit/validation_v1/oracle_crosscheck.json','audit/validation_v2/solver_v5_gate_v6.json','audit/validation_v2/root_cli_v1.json','audit/PROOF_REVIEW_V1.md']
gate=json.loads((ROOT/paths[1]).read_text(encoding='utf-8'))
cli=json.loads((ROOT/paths[2]).read_text(encoding='utf-8'))
assert gate['scientific_status']=='passed' and cli['scientific_status']=='passed'
assert gate['exact_full_bipartition_sets_matched']==135
assert gate['expected_all_k_existence_matched']==135
record=dict(cycle='C006',event='master_accepts_correctness',
 at_utc=datetime.now(timezone.utc).isoformat(),scientific_status='confirmed_under_retained_assumptions',
 case_records=135,unique_payloads=133,proof_scope='Unknown-k existence and unrestricted regular factors; not hidden-k recovery',
 sources=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
 dormant_features=['enhanced A/B rules','meet proposal'],performance='not_yet_accepted')
with (ROOT/'coordination/CORRECTNESS_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
print('Correctness accepted')

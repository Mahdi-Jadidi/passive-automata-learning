"""Record master's acceptance of independently reviewed C005 correctness gates."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
names=['SMALL_GATE_REPORT_V2.json','EXACT_TOGGLE_GATE_REPORT_V1.json',
       'SPARSE_SCALING_AUDIT_REPORT_V1.json','ROOT_CLI_AUDIT_REPORT_V1.json']
reports=[]
for name in names:
    path=ROOT/'audit'/name
    data=json.loads(path.read_text(encoding='utf-8'))
    assert data['scientific_status']=='passed', name
    reports.append(dict(path='audit/'+name,sha256=sha256(path.read_bytes()).hexdigest()))
record=dict(cycle='C005',event='master_accepts_correctness',
    at_utc=datetime.now(timezone.utc).isoformat(),scientific_status='confirmed_under_assumptions',
    reports=reports,performance_status='separate_pending_schedule')
with (ROOT/'coordination/CORRECTNESS_ACCEPTANCE.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as handle:
    handle.write(json.dumps(record,ensure_ascii=False)+'\n')
print(json.dumps(dict(accepted=len(reports))))

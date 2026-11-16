import json,sys
from pathlib import Path
import capture
A=Path(__file__).resolve().parent;ROOT=A.parents[3];plan=json.loads((A/'ACTUAL_FREEZE_V3.json').read_text());ledger=[]
for arm in plan['arms']:
 cap=capture.capture('C025-ACTUAL-'+arm['id'],[sys.executable,'-B','-X','utf8',str(A/'evaluate_v3.py'),'actual',arm['id']],cwd=ROOT,timeout_seconds=120,source_paths=[A/'evaluate_v3.py',A/'context_oracle_c017_v3.py',A/'ACTUAL_FREEZE_V3.json',A/'PROTOCOL_V3.md',A.parent/'implementation/selected_output_v1/solver_v1.py',Path(arm['path'])]);ledger.append({'arm':arm['id'],**cap});print(json.dumps({'arm':arm['id'],'execution_status':cap['execution_status']}),flush=True)
 with (A/'ACTUAL_LEDGER_V1.json').open('w') as f:json.dump(ledger,f,indent=2)

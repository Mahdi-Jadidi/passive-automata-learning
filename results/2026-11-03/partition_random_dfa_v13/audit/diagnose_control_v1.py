import json
from pathlib import Path
import validate_results_v2 as audit
A=Path(__file__).resolve().parent
row=json.loads((A/'controls_inference_ledger_v2.jsonl').read_text().splitlines()[0])
data=json.loads(Path(row['input']).read_text());world=json.loads(Path(row['world']).read_text());result=json.loads((A/'attempts'/row['attempt_id']/'stdout.bin').read_bytes())
audit.validate(data,world,result,True)

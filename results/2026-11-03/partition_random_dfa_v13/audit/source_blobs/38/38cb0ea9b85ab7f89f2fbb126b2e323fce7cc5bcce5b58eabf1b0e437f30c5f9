import json
from pathlib import Path
import validate_results_v2 as audit
A=Path(__file__).resolve().parent
row=json.loads((A/'controls_inference_ledger_v2.jsonl').read_text().splitlines()[0])
data=json.loads(Path(row['input']).read_text());world=json.loads(Path(row['world']).read_text());result=json.loads((A/'attempts'/row['attempt_id']/'stdout.bin').read_bytes())
raw_order=[w['word'] for w in result['representative']['negative_witnesses']]
print(json.dumps({'input_negative_order':data['negative'],'witness_negative_order':raw_order,'witness_order_is_sorted_input':raw_order==sorted(set(data['negative']))}),flush=True)
normalized={'alphabet':sorted(data['alphabet']),'positive':sorted(set(data['positive'])),'negative':sorted(set(data['negative']))}
print(json.dumps(audit.validate(normalized,world,result,True)),flush=True)

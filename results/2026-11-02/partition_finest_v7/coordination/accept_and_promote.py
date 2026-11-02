"""Master accepts existing independent small-case gate and promotes root README."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def digest(p):return sha256(p.read_bytes()).hexdigest()
gatepath=ROOT/'audit/validation_v1/provider_gate_v2.json'
gate=json.loads(gatepath.read_text(encoding='utf-8'))
assert gate['status']=='accepted' and not gate['failures']
assert gate['adaptive_rows']==218 and gate['reference_rows']==218
assert gate['independent_certificate_replays']==436
provider=ROOT/'implementation/finest_solver_v3.py'
assert digest(provider)=='c783929cc75b0979cab679f82c0e43e3aceab014db0b2d063628d0302b33477a'
record=dict(cycle='C007',event='master_accepts_small_correctness',
 at_utc=datetime.now(timezone.utc).isoformat(),unique_inputs=218,mode_outputs=436,
 gate=dict(path=str(gatepath.relative_to(ROOT)),sha256=digest(gatepath)),
 provider=dict(path=str(provider.relative_to(ROOT)),sha256=digest(provider)),
 counts=gate['adaptive_status_counts'],scientific_status='confirmed_under_declared_sample_target',
 scope='Unique finest sample-compatible partition, not hidden architecture recovery',large_scale='pending',performance='pending')
with (ROOT/'coordination/CORRECTNESS_ACCEPTANCE.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
source=ROOT/'implementation/ROOT_README_CANDIDATE_FA_v1.md'
content=source.read_text(encoding='utf-8').replace('برای مثال دو ریزترینِ بیشینهٔ ناسازگار:','برای مثال چند پالایشِ بیشینهٔ رقیب:')
with (ROOT/'README_FA.md').open('x',encoding='utf-8',newline='\n') as f:f.write(content)
with (ROOT/'coordination/readme_promotion.json').open('x',encoding='utf-8') as f:
 json.dump(dict(source=str(source.relative_to(ROOT)),source_sha256=digest(source),target='README_FA.md',target_sha256=digest(ROOT/'README_FA.md'),amendment='Correct terminology: competing maximal refinements, not multiple finest partitions'),f,indent=2)
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
print(json.dumps(dict(accepted_outputs=436,unique_inputs=218,readme='README_FA.md')))

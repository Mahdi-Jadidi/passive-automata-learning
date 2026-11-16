"""Preserve first readiness and fix console-log hashes after command completion."""
import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent
p=here/'READINESS_v1.json';before=here/'READINESS_before_log_finalize_v1.json'
if before.exists():raise FileExistsError(before)
before.write_bytes(p.read_bytes())
payload=json.loads(p.read_text())
def record(path):return dict(path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
payload['implementation']={name:record(Path(item['path'])) for name,item in payload['implementation'].items()}
payload['manifest_correction']='The first readiness captured finalize.stdout.txt while its command was still writing. Original manifest preserved as READINESS_before_log_finalize_v1.json. Implementation hashes refreshed after completion; input/adapter/prepared data unchanged.'
p.write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(base_readiness=record(p),original_preserved=record(before))))

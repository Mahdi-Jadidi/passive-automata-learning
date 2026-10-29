"""Freeze C004 Stage-1 runtime candidates; not a scientific acceptance."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
files = []
expected = {'structural/singleton_solver_v1.py':
    '16065fdfabf52d4280e3c0f5a7f427faff8990583579bd97b4ea64f70c5a023e'}
ready = json.loads((ROOT/'general/SOURCE_READY_V3.json').read_text(encoding='utf-8-sig'))
expected['general/known_k_v3.py'] = ready['source']['sha256']
assert expected['general/known_k_v3.py'].startswith('15191898')
parent = json.loads((ROOT/'coordination/parent_manifest.json').read_text(encoding='utf-8'))
expected['audit/capture.py'] = parent['capture_sha256']
for name, wanted in expected.items():
    raw = (ROOT/name).read_bytes()
    found = sha256(raw).hexdigest()
    assert found == wanted, (name, found)
    files.append(dict(path=name, sha256=found, bytes=len(raw)))
stamp = datetime.now(timezone.utc).isoformat()
record = dict(version='C004-stage1-R1', at_utc=stamp, files=files,
              common_k_range='2 through alphabet size',
              provider_specific_extension='structural v1 additionally accepts k=1; not part of common interface',
              scientific_status='candidate_frozen_pending_independent_audit',
              script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
with (ROOT/'coordination/runtime_stage1.json').open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='stage1_candidates_frozen', at_utc=stamp,
        manifest='coordination/runtime_stage1.json', files=files,
        scientific_status=record['scientific_status']), ensure_ascii=False)+'\n')
print(json.dumps(record, ensure_ascii=False))

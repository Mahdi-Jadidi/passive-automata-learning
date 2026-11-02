"""Route the public entry to the new separately versioned provider; preserve R1."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
expected={'implementation/finest_solver_v4.py':'c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff','implementation/finest_cli_v2.py':'46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879'}
for name,wanted in expected.items():assert sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
path=ROOT/'solver.py';raw=path.read_bytes()
assert raw.count(b'finest_cli_v1.py')==1
with (ROOT/'coordination/public_wrapper_R1.py').open('xb') as f:f.write(raw)
path.write_bytes(raw.replace(b'finest_cli_v1.py',b'finest_cli_v2.py'))
with (ROOT/'coordination/WRAPPER_R2.json').open('x',encoding='utf-8') as f:json.dump(dict(reason='New staged-provider version after recorded preprocessing timeout',old_sha256=sha256(raw).hexdigest(),new_sha256=sha256(path.read_bytes()).hexdigest(),targets=expected),f,indent=2)
print('Public wrapper now selects CLI v2/provider v4; old wrapper retained')

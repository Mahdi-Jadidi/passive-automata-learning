from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
PARENT=WORKSPACE/'results/2026-10-31/partition_coverage_v5'
for name in ['theory','implementation','audit','evidence']:
    (ROOT/name).mkdir(exist_ok=False)
paths=subprocess.check_output(['git','ls-files','-z','--',str(PARENT)],cwd=WORKSPACE).decode().split('\0')
files=[dict(path=p,sha256=sha256((WORKSPACE/p).read_bytes()).hexdigest()) for p in paths if p]
with (ROOT/'coordination/parent_manifest.json').open('x',encoding='utf-8') as f:
    json.dump(dict(parent_commit='eb521fdd',files=files),f,indent=2)
shutil.copyfile(PARENT/'evidence/capture.py',ROOT/'evidence/capture.py')
with (ROOT/'coordination/journal.jsonl').open('x',encoding='utf-8') as f:
    f.write(json.dumps(dict(event='cycle_started',cycle='C006',at_utc=datetime.now(timezone.utc).isoformat(),parent_commit='eb521fdd'))+'\n')
print(json.dumps(dict(parent_files=len(files),root=str(ROOT))))

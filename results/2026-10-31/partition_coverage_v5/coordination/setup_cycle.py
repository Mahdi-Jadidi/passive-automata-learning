"""Exclusive C005 setup; preserves the committed C004 parent by hashes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
PARENT = WORKSPACE / 'results/2026-10-27/partition_scaling_v4'

def write(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

for name in ['structural', 'general', 'audit', 'evidence', 'examples']:
    (ROOT / name).mkdir(exist_ok=False)
files = subprocess.check_output(['git', 'ls-files', '-z', '--', str(PARENT)], cwd=WORKSPACE).decode().split('\0')
items = []
for name in filter(None, files):
    path = WORKSPACE / name
    raw = path.read_bytes()
    items.append(dict(path=name, sha256=sha256(raw).hexdigest(), bytes=len(raw)))
write(ROOT/'coordination/parent_manifest.json', dict(parent_commit='0ab2d9eb', files=items))
shutil.copyfile(PARENT/'audit/capture.py', ROOT/'evidence/capture.py')
write(ROOT/'coordination/environment.json', dict(
    created_utc=datetime.now(timezone.utc).isoformat(), user_date='2026-10-31',
    timezone='Asia/Tehran', python='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
    parent_files=len(items), capture_sha256=sha256((ROOT/'evidence/capture.py').read_bytes()).hexdigest()))
with (ROOT/'coordination/journal.jsonl').open('x',encoding='utf-8',newline='\n') as handle:
    handle.write(json.dumps(dict(event='cycle_started', cycle='C005', parent_commit='0ab2d9eb',
        at_utc=datetime.now(timezone.utc).isoformat(), contract='coordination/CONTRACT.md'))+'\n')
print(json.dumps(dict(root=str(ROOT), parent_files=len(items))))

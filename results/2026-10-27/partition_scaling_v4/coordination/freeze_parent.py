"""Create an immutable hash manifest of the C003 references used by C004."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
PARENT = WORKSPACE / 'results/2026-10-26/partition_discovery_v3'
names = ['solver.py', 'general/general_solver.py', 'general/fair_reference.py',
         'general/support.py', 'general/PROOFS.md', 'general/coverage_family/PROOFS.md',
         'structural/fixed_word_solver.py', 'structural/PROOFS.md', 'structural/SOURCES.md',
         'audit/capture.py', 'coordination/runtime_manifest.json',
         'coordination/CYCLE_OUTCOME.json', 'MASTER_DECISION_FA.md', 'RESEARCH_REPORT_FA.md']
files = []
for name in names:
    path = PARENT / name
    data = path.read_bytes()
    files.append(dict(path=str(path.relative_to(WORKSPACE)).replace('\\', '/'),
                      sha256=sha256(data).hexdigest(), bytes=len(data)))
capture = (ROOT / 'audit/capture.py').read_bytes()
assert capture == (PARENT / 'audit/capture.py').read_bytes()
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=WORKSPACE, text=True).strip()
assert head.startswith('f7ae918a'), head
record = dict(cycle='C004', created_utc=datetime.now(timezone.utc).isoformat(),
              parent_commit=head, files=files,
              capture_sha256=sha256(capture).hexdigest(),
              script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
with (ROOT/'coordination/parent_manifest.json').open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
with (ROOT/'coordination/journal.jsonl').open('x', encoding='utf-8') as handle:
    handle.write(json.dumps(dict(event='cycle_started', at_utc=record['created_utc'],
        parent_commit=head, contract='coordination/CONTRACT.md', workers='coordination/workers.json',
        ordered_stages=['known-k scaling', 'separate assumption relaxations'],
        scientific_status='under_investigation', execution_status='setup_successful'), ensure_ascii=False)+'\n')
print(json.dumps(dict(parent_commit=head, frozen_files=len(files), capture_sha256=record['capture_sha256'])))

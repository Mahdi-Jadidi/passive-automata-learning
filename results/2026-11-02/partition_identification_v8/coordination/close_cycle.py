"""Close bounded C008 research from existing proofs/evidence, no model reruns."""
from pathlib import Path
from hashlib import sha256
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p): return sha256(p.read_bytes()).hexdigest()
def write_new(p, d):
    with p.open('x', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=2)

errors = []
def check(p, h, label, size=None):
    if not p.is_file() or digest(p) != h:
        errors.append(f'{label}: missing or changed {p}')
    elif size is not None and p.stat().st_size != int(size):
        errors.append(f'{label}: byte count {p}')

parent = read(ROOT/'coordination/parent_manifest.json')
for item in parent['files']:
    check(WORKSPACE/item['path'], item['sha256'], 'parent')
evidence = ROOT/'audit/evidence'
attempts = []
source_refs = 0
for directory in sorted((evidence/'attempts').iterdir()):
    m, r = read(directory/'manifest.json'), read(directory/'result.json')
    if m['attempt_id'] != directory.name or r['attempt_id'] != directory.name:
        errors.append(f'attempt ID {directory.name}')
    if r['execution_status'] != 'success' or r['exit_code'] != 0 or r['child_reaped'] is not True:
        errors.append(f'execution {directory.name}')
    if not m['sources'] or m['source_snapshot_error'] is not None:
        errors.append(f'capture sources {directory.name}')
    for item in m['sources']:
        source_refs += 1
        check(evidence/item['snapshot'], item['sha256'], 'snapshot', item['bytes'])
        check(Path(item['path']), item['sha256'], 'immutable tested source', item['bytes'])
    for stream in ['stdout', 'stderr']:
        check(directory/(stream+'.bin'), r[stream+'_sha256'], stream, r[stream+'_bytes'])
    output = read(directory/'stdout.bin')
    attempts.append(dict(attempt_id=directory.name, execution_status=r['execution_status'],
                         scientific_status=output['scientific_status']))
if len(attempts) != 2: errors.append('expected exactly two scientific attempts')
for blob in (evidence/'source_blobs').glob('*/*'):
    if blob.is_file(): check(blob, blob.name, 'content-addressed source')

links = []
for target in re.findall(r'\]\(([^)]+)\)', (ROOT/'RESULT_FA.md').read_text(encoding='utf-8')):
    if '://' in target or target.startswith('#'): continue
    if not (ROOT/target.split('#')[0]).is_file(): errors.append(f'broken link {target}')
    links.append(target)
for rel in ['theory/PROOFS_v1.md','theory/OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1.md',
            'theory/ADDENDUM_PREFIX_CLOSED_v1.md','literature/INDEPENDENT_CRITIQUE_V2.md',
            'audit/COUNTEREXAMPLE_AUDIT_REPORT_V1.md']:
    if not (ROOT/rel).is_file(): errors.append(f'missing proof/review {rel}')

files = [{'path':p.relative_to(ROOT).as_posix(), 'sha256':digest(p), 'bytes':p.stat().st_size}
         for p in sorted(ROOT.rglob('*')) if p.is_file()]
write_new(ROOT/'coordination/FINAL_FILES.json', dict(files=files,
    note='Snapshot before closure outputs; includes all research sources and evidence, not a new experiment.'))
integrity = dict(status='pass' if not errors else 'fail', error_count=len(errors), errors=errors,
    parent_files=len(parent['files']), scientific_attempts=len(attempts), source_references=source_refs,
    root_links=len(links), checker_sha256=digest(Path(__file__)),
    scope='Artifact and byte checks only; mathematical acceptance is separately scoped in CYCLE_OUTCOME.')
write_new(ROOT/'coordination/FINAL_INTEGRITY.json', integrity)
assert not errors, errors
outcome = dict(cycle='C008', user_date='2026-11-02', at_utc=datetime.now(timezone.utc).isoformat(),
    status='research_complete', requested_universal_guarantee='mathematically_impossible_in_declared_class',
    accepted_claims=['T1','T2','T3','T4','T5','T8','T9','T10'],
    separately_reviewed_claims=dict(T6_T7='Accepted by master after independent L1/meet review in critique V2; historical pending ledger retained',
                                  prefix_closed_addendum='Direct constructive proof checked by master; no runtime experiment claimed'),
    exact_identifier_runtime_implemented=False,
    attainable='Conditional certified ownership when admissible ownership version space is singleton; trusted k plus k sound graph components is one sufficient finite certificate',
    scientific_attempts=attempts,
    preserved_corrections=['Literature V1 overstates need for state bound; V2 corrects it',
                           'Parity local minimal DFAs are decomposable, so prime finite-data construction is separate',
                           'Theory failed-candidate ledger and deliberate mutant are preserved'],
    limitations=['No supplied real dataset evaluated','No universal 100% physical ownership learner exists under present assumptions',
                 'No proof-assistant verification of entire implementation','No novelty or general speed claim'],
    final_files_sha256=digest(ROOT/'coordination/FINAL_FILES.json'),
    integrity_sha256=digest(ROOT/'coordination/FINAL_INTEGRITY.json'))
write_new(ROOT/'coordination/CYCLE_OUTCOME.json', outcome)
print(json.dumps(dict(status='complete', integrity=integrity, attempts=attempts), ensure_ascii=False))

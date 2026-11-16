import hashlib, json
from pathlib import Path
here=Path(__file__).resolve().parent
def record(p):
    return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
smoke=json.loads((here/'smoke_results_v1.json').read_text())
profiles=here.parent/'profile/current_c020_v1'
payload=dict(candidate='C024-A-v1',ready_for_independent_audit=True,public_promotion=False,
    files={p.relative_to(here).as_posix():record(p) for p in here.glob('*/*.py')},
    minimal_diff=record(here/'candidate_c024a_v1/minimal.diff'),
    baseline_hashes=record(here/'baseline_hashes.json'),
    smoke=dict(passed=smoke['passed'],results=record(here/'smoke_results_v1.json'),command='py -3.14 results/2026-11-05/search_checkpoint_v24/implementation/smoke_v1.py',exit_code=0),
    profiles=[dict(metadata=record(profiles/f'{case}.metadata.json'),exit_code=0,completed=True) for case in ['obstruction_m8','D']],
    profile_summary=record(profiles/'PROFILE_NOTES_v1.md'),method_and_review_concerns=record(here/'candidate_c024a_v1/METHOD_v1.md'),
    limits=['No full correctness audit or ordinary benchmark','Inline validation/graph and initial atom-check wall time not separately isolated','No C024-B','No public files or Git modified'])
(here/'READINESS_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(ready=True,gate=payload['files']['candidate_c024a_v1/gate_v1.py'])))

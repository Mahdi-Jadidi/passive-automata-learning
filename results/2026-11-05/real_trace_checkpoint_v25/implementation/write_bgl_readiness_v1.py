import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent;out=here.parent/'inventory/bgl_v1'
def record(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
m=json.loads((out/'manifest.json').read_text())
assert m['status']=='prepared_observations_only' and m['raw_csv_alignment_checks']==2000
for name,sha in m['output_hashes'].items():assert record(out/name)['sha256']==sha
payload=dict(status='prepared_for_independent_replay',solver_runs=0,command=m['command'],exit_code=0,
 files={p.name:record(p) for p in out.iterdir() if p.is_file()},adapter=record(here/'prepare_bgl_v1.py'),notes=record(here/'BGL_ADAPTER_v1.md'),
 caveats=['current-message alert output, not success or AND acceptance','one observed sample stream, no proven contiguity or reset','existing EventId may be shared across nodes','top8 diagnostic is transductive, not training split'])
(here/'READINESS_BGL_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(payload['files']['observations.json']))

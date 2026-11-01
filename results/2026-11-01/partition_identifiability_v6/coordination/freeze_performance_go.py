"""Master authorizes exactly the six-job preregistered C006 characterization."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
refs=['audit/BENCHMARK_PROPOSAL_V2.md','audit/PROTOCOL_BENCHMARK_V2.md','audit/benchmark_v1/manifest.json','audit/benchmark_v1/freeze_validation.json','implementation/solver_v5.py','implementation/cli_v4.py','solver.py']
data=json.loads((ROOT/'audit/benchmark_v1/freeze_validation.json').read_text(encoding='utf-8'))
assert data['scientific_status']=='passed_independent_frozen_input_and_truth_validation'
assert data['provider_invocations_performed']==0
record=dict(cycle='C006',decision='GO',primary_provider_jobs=6,
 source_records=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in refs],
 allowed_cells=['large_connected_m64','small_full_cover_m4'],repetitions=3,
 mode='--all --seconds 28',hard_timeout_seconds=30,
 requirements=['Freeze all new drivers before launch','Serial fresh process per job','Full JSON and raw streams captured','Independent replay after timing','No rerun of successful or censored jobs'],
 excluded='optional_decomposable_m64 and all additional datasets',
 scope='Standalone characterization, no old-method comparison or speedup claim')
with (ROOT/'coordination/PERFORMANCE_GO.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print('GO: six jobs, two frozen cells')

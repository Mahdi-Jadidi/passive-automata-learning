import hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[4]
def record(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
smoke=json.loads((here/'smoke_results_v1.json').read_text());assert smoke['passed']
copy=here.parent/'contexts_c017_copy_v1.py';original=root/'results/2026-11-04/lancer_host_partition_v17/implementation/contexts_v1.py'
assert record(copy)['sha256']==record(original)['sha256']
payload=dict(status='ready_for_independent_source_and_small_family_audit',candidate='C025-selected-output-v1',real_data_solver_runs=0,
             public_solver_modified=False,files={p.name:record(p) for p in here.iterdir() if p.is_file() and p.name!='READINESS_SOLVER_v1.json'},
             c017_copy=record(copy),c017_original=record(original),contract=record(root/'results/2026-11-05/real_trace_checkpoint_v25/theory/MODEL_CONTRACT_V1.md'),
             smoke_command='py -3.14 results/2026-11-05/real_trace_checkpoint_v25/implementation/selected_output_v1/smoke_v1.py',smoke_exit_code=0,
             oracle_controls=len(smoke['oracle_controls']),delta='new bounded solver reusing C017 block semantics; adds validation, polling, exact final-block cover, lazy cache and replayable output function witnesses',
             review_concerns=['No independent audit yet','Exhaustion metadata requires separate independent enumeration','Output rules can be large; deadline/resource interruption remains unresolved','No physical ownership or prediction claims','No data selection inside core'])
(here/'READINESS_SOLVER_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(status=payload['status'],solver=payload['files']['solver_v1.py'],oracle_controls=payload['oracle_controls'])))

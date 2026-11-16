import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=HERE.parent/'inventory/prepared_v1'
def record(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
manifest=read('manifest.json');faithful=read('faithful_records_and_metadata.json')['traces']
for view in ['observations','observations_target_qualified']:
    data=read(view+'.json')
    for source in manifest['sources']:
        scenario=source['scenario'];ids={x['trace_id'] for x in faithful if x['scenario']==scenario}
        traces=[t for t in data['traces'] if t['file_id'] in ids]
        payload=dict(alphabet=sorted({e['id'] for t in traces for e in t['events']}),traces=traces)
        p=OUT/f'{scenario}_{view}.json'
        if p.exists():raise FileExistsError(p)
        p.write_text(json.dumps(payload,indent=2),encoding='utf-8')
prior=ROOT/'results/2026-11-04/lancer_case_study_v16'
c017=ROOT/'results/2026-11-04/lancer_host_partition_v17'
sources=[prior/'data_audit/DATA_AUDIT_FA_V1.md',prior/'data_audit/selected_manifest_v1.json',prior/'data_audit/archive_inventory_v1.json',
 prior/'implementation/inventory_selected_v1.py',prior/'implementation/INGESTION_REPRODUCIBILITY_PLAN_V1.md',
 prior/'data_audit/selected_v1/artifact/data/cage2/convert_traces.py',
 c017/'implementation/prepare_v1.py',c017/'implementation/contexts_v1.py',c017/'theory/SELECTED_OUTPUT_PROOFS_v1.md']
assert record(HERE/'contexts_c017_copy_v1.py')['sha256']==record(c017/'implementation/contexts_v1.py')['sha256']
payload=dict(status='ready_for_independent_ingestion_replay_and_model_review',solver_runs=0,and_inputs_created=False,
             archive_sha256=manifest['archive_sha256'],selection='six lexicographically sorted files each CAGE2 raw/Baby random15/Baby heuristic15',
             source_evidence=[record(p) for p in sources],
             prepared_outputs={p.name:record(p) for p in OUT.iterdir() if p.is_file()},
             implementation={p.name:record(p) for p in HERE.iterdir() if p.is_file() and p.name!='READINESS_v1.json'},
             commands=[dict(command=manifest['command'],exit_code=0),dict(command='py -3.14 results/2026-11-05/real_trace_checkpoint_v25/implementation/check_preparation_v1.py',exit_code=0)],
             limitations=['simulator-generated benchmark, not production logs','current-event success differs from full-word AND acceptance','per-file/episode independent initialization is a modeling choice','target-qualified tokens deliberately use observable target metadata','no inference or real-data consistency checks yet','independent audit pending'])
(HERE/'READINESS_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(status=payload['status'],observations=record(OUT/'observations.json'),qualified=record(OUT/'observations_target_qualified.json'))))

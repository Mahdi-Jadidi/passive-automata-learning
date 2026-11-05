"""Independent projection/certificate replay for C022 timing captures."""
import hashlib,json,statistics,sys
from pathlib import Path
from certificate_replay_c015_v2 import canonical,certificate,witness
from oracle_data_v1 import feasible,full_family
A=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compatible_family(data,k):
 family=full_family(data)
 return [x for x in family if k is None or max(x)+1==k]
def main(runpath):
 f=read(A/'SOURCE_INPUT_FREEZE_V5.json');plan=read(A/'TIMING_PLAN_V1.json');run=Path(runpath);rows=list(map(json.loads,(run/'ledger.jsonl').read_text().splitlines()));fixtures=read(f['fixture_manifest_path']);inputs={x['case_id']:x for x in fixtures['inputs']};validated=[];errors=[]
 for row in rows:
  if 'attempt_id' not in row:validated.append({**row,'validated_status':'budget_unstarted'});continue
  capdir=A/'attempts'/row['attempt_id'];cap=read(capdir/'result.json')
  try:
   assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
   assert sha(capdir/'stdout.bin')==cap['stdout_sha256'] and sha(capdir/'stderr.bin')==cap['stderr_sha256']
   for source in read(capdir/'manifest.json')['sources']:
    assert sha(A/source['snapshot'])==source['sha256'];assert sha(source['path'])==source['sha256']
   cell=next(x for x in plan['cells'] if x['cell_id']==row['cell_id']);ip=Path(inputs[cell['case_id']]['input']);assert sha(ip)==cell['input_sha256']==row['input_sha256']
   if cap['execution_status']=='timed_out':validated.append({**row,'validated_status':'hard_timeout'});continue
   result=json.loads((capdir/'stdout.bin').read_bytes());assert result['input_sha256']==cell['input_sha256'] and result['known_k']==cell['known_k'] and result['physical_truth_read'] is False
   status=result['status'];assert status in {'certified_unique','ambiguous','incompatible','unresolved'}
   data=read(ip);forced=result.get('certificate',{}).get('forced_atoms',[])
   parts=[result['certificate']['witness']['blocks']] if status=='certified_unique' else [w['blocks'] for w in result.get('alternatives',[])]
   keys={canonical(part,sorted(data['alphabet'])) for part in parts}
   if status in {'certified_unique','ambiguous'}:
    assert len(parts)==(1 if status=='certified_unique' else 2)
    certificate(data,result,cell['known_k'],keys)
    for part in parts:witness(data,{'blocks':part,'negative_rejections':(result['certificate'].get('witness',{}).get('negative_rejections') if status=='certified_unique' else next(w['negative_rejections'] for w in result['alternatives'] if w['blocks']==part)),'local_language_rule':'positive_projections_from_input'},None if cell['known_k'] is None else [cell['known_k']],keys)
    if status=='ambiguous':assert len(keys)==2
    if status=='certified_unique':
     route=result['certificate']['route']
     if route=='compatible_forced_atoms':assert len(forced)==(cell['known_k'] if cell['known_k'] is not None else 1)
     elif route=='known_k_one_consistent_labels':assert cell['known_k']==1
     elif route=='unary_all_partitions':assert cell['known_k'] in (None,1,len(data['alphabet']))
     elif route=='exhausted_all_forced_atom_coarsenings':
      assert len(data['alphabet'])<=8 and len(compatible_family(data,cell['known_k']))==1
     else:raise AssertionError('unique status lacks an independently checked uniqueness route: '+route)
   elif status=='incompatible':
    route=result['certificate']['route'];k=cell['known_k']
    if route=='forced_atom_count_upper_bound':assert k is not None and k>len(forced)
    elif route=='only_forced_atom_partition_rejected':assert k==len(forced) and not feasible(data,canonical(forced,sorted(data['alphabet'])))
    elif route=='exhausted_all_forced_atom_coarsenings':assert len(data['alphabet'])<=8 and len(compatible_family(data,cell['known_k']))==0
    elif route=='contradictory_labels':assert set(data['positive'])&set(data['negative'])
    else:raise AssertionError('incompatible status lacks independent proof route: '+route)
   validated.append({**row,'validated_status':status,'route':result.get('certificate',{}).get('route'),'metrics':result.get('metrics',{}),'result':result})
  except Exception as exc:errors.append({'cell_id':row['cell_id'],'provider':row['provider'],'rep':row['rep'],'attempt_id':row['attempt_id'],'error':repr(exc)})
 # Compare completed provider decisions per repetition; censored rows remain explicit.
 pairs=[]
 for cell in plan['cells']:
  for rep in (1,2,3):
   group=[x for x in validated if x.get('cell_id')==cell['cell_id'] and x.get('rep')==rep and x.get('provider') in ('baseline_c2','transfer')]
   if len(group)==2 and all(x.get('validated_status') not in ('unresolved','hard_timeout','budget_unstarted') for x in group):
    same=group[0]['validated_status']==group[1]['validated_status'];pairs.append({'cell_id':cell['cell_id'],'rep':rep,'same_status':same,'baseline':group[0]['validated_status'],'transfer':group[1]['validated_status']})
    if not same:errors.append({'cell_id':cell['cell_id'],'rep':rep,'error':'complete exact statuses differ'})
 summaries=[]
 for cell in plan['cells']:
  for p in ('baseline_c2','transfer'):
   g=[x for x in validated if x.get('cell_id')==cell['cell_id'] and x.get('provider')==p];done=[x for x in g if x.get('validated_status') not in ('unresolved','hard_timeout','budget_unstarted')]
   summary={'cell_id':cell['cell_id'],'provider':p,'completed':len(done),'statuses':[x.get('validated_status') for x in g]}
   if len(done)==3:summary.update(median_subprocess_seconds=statistics.median(x['subprocess_seconds'] for x in done),median_input_solver_seconds=statistics.median(x['result']['input_and_solver_seconds'] for x in done),median_projection_characters=statistics.median(x['metrics'].get('projection_characters',0) for x in done),median_projection_chunks=statistics.median(x['metrics'].get('projection_chunks',0) for x in done))
   summaries.append(summary)
 report={'status':'accepted' if not errors and len(validated)==30 else 'rejected_or_incomplete','run_id':f['run_id'],'attempts':len(validated),'errors':errors,'paired_status_checks':pairs,'medians':summaries,'rows':[{k:v for k,v in x.items() if k!='result'} for x in validated]}
 (run/'validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':report['status'],'attempts':len(validated),'errors':len(errors),'medians':summaries},ensure_ascii=False));return 0 if report['status']=='accepted' else 1
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))



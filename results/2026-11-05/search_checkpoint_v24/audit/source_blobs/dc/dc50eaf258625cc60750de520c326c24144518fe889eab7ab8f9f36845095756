"""Independent status-aware post-timing verification; replay excluded from timing."""
import hashlib,json,statistics,sys
from pathlib import Path
from oracle_data_v1 import full_family
from certificate_replay_c015_v2 import verify,certificate,witness,canonical,analytic_obstruction
A=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 run=Path(sys.argv[1]);plan=read(A/'TIMING_PLAN_V1.json');cells={c['cell_id']:c for c in plan['cells']};ledger=[json.loads(l) for l in (run/'ledger.jsonl').read_text().splitlines()];expected={};rows=[];errors=[]
 for cid,c in cells.items():
  d=read(c['input']);k=c['known_k']
  if cid.startswith('obstruction'):analytic_obstruction(d);expected[cid]=[[0]*len(d['alphabet'])]
  elif cid in ['ambiguous_noK','D_K4']:expected[cid]=[x for x in full_family(d) if k is None or max(x)+1==k]
 for r in ledger:
  row={k:r[k] for k in ['provider','cell_id','rep','execution_status']};row['process_seconds']=r.get('subprocess_seconds')
  try:
   if r['execution_status']=='budget_unstarted':row['decision']='budget_unstarted';rows.append(row);continue
   p=Path(r['attempt_dir']);cap=read(p/'result.json');assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
   for stream in ['stdout','stderr']:assert sha(p/(stream+'.bin'))==cap[stream+'_sha256']
   for s in read(p/'manifest.json')['sources']:assert sha(A/s['snapshot'])==s['sha256'] and sha(s['path'])==s['sha256']
   if cap['execution_status']=='timed_out':row['decision']='hard_timeout';rows.append(row);continue
   c=cells[r['cell_id']];assert sha(c['input'])==c['input_sha256']==r['input_sha256'];res=json.loads((p/'stdout.bin').read_bytes());assert res['input_sha256']==c['input_sha256'];status=res['status'];assert cap['exit_code']==(3 if status=='unresolved' else 2 if status=='invalid_input' else 0)
   row.update(decision=status,route=res.get('certificate',{}).get('route'),metrics=res.get('metrics',{}))
   if status=='unresolved':assert res['findings']['computation_incomplete'] is True
   elif c['cell_id']=='A_K4':
    d=read(c['input']);cert=res['certificate'];assert status=='certified_unique' and cert['route']=='compatible_forced_atoms' and len(cert['forced_atoms'])==4 and res['known_k']==4 and res['physical_truth_read'] is False
    key=canonical(cert['forced_atoms'],sorted(d['alphabet']));certificate(d,res,4,{key});assert witness(d,cert['witness'],[4],{key})==key;assert res['partition']==cert['witness']['blocks']
   else:
    fam=expected[c['cell_id']];expect='unique' if len(fam)==1 else 'ambiguous' if fam else 'incompatible';job={'input':c['input'],'input_sha256':c['input_sha256'],'job_id':c['cell_id'],'allowed_k':None if c['known_k'] is None else [c['known_k']],'expectation':expect};verify(job,res,{'compatible_rgs':fam})
   assert status in ['certified_unique','ambiguous','incompatible','unresolved']
  except Exception as e:row['error']=repr(e);errors.append({**row,'attempt_id':r.get('attempt_id'),'failure_id':f"C024-TIMING-{r['provider']}-{r['cell_id']}-r{r['rep']}"})
  rows.append(row)
 summaries=[];comparisons=[]
 for cid in cells:
  group={}
  for provider in ['C020_C2','C024_A']:
   rr=[r for r in rows if r['cell_id']==cid and r['provider']==provider];done=[r for r in rr if r.get('decision') in ['certified_unique','ambiguous','incompatible'] and 'error' not in r];med=statistics.median(r['process_seconds'] for r in done) if len(done)==5 else None
   item={'cell_id':cid,'provider':provider,'completed':len(done),'statuses':[r.get('decision') for r in rr],'raw_seconds':[r.get('process_seconds') for r in rr],'median_completed_seconds':med,'complete_candidates':[r.get('metrics',{}).get('complete_candidates') for r in rr],'search_nodes':[r.get('metrics',{}).get('search_nodes') for r in rr]};summaries.append(item);group[provider]=item
  b,a=group['C020_C2'],group['C024_A'];ratio=a['median_completed_seconds']/b['median_completed_seconds'] if a['median_completed_seconds'] is not None and b['median_completed_seconds'] is not None else None
  comparisons.append({'cell_id':cid,'candidate_over_baseline_median':ratio,'material_benefit':a['completed']==5 and (b['completed']<5 or ratio<=0.8),'guardrail_block':cid in ['A_K4','D_K4'] and (ratio is None or ratio>1.15),'candidate_count_reduced':all(x is not None and y is not None and x<y for x,y in zip(a['complete_candidates'],b['complete_candidates']))})
 semantic_pass=not errors and len(rows)==60;benefit=any(c['material_benefit'] for c in comparisons);counts=all(c['candidate_count_reduced'] for c in comparisons if c['cell_id'].startswith('obstruction'));guard=not any(c['guardrail_block'] for c in comparisons)
 report={'semantic_certificate_pass':semantic_pass,'errors':errors,'material_benefit':benefit,'unique_stress_candidate_reduction':counts,'known_k_guardrails_pass':guard,'automatic_promotion_criteria_pass':semantic_pass and benefit and counts and guard,'summaries':summaries,'comparisons':comparisons,'rows':rows,'warning':'distributions.json is raw capture summary; only this validated status-aware summary supports comparisons'};out=run/'VALIDATED_SUMMARY_V1.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','summaries']},ensure_ascii=False))
if __name__=='__main__':main()

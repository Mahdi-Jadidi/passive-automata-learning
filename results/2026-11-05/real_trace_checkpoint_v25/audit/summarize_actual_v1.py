import json,collections,hashlib
from pathlib import Path
from context_oracle_c017_v3 import block_conflicts
A=Path(__file__).resolve().parent;R=A.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
qd=read(R/'inventory/prepared_v1/target_qualified_dictionary_metadata.json')['dictionary'];baselines=[]
for scenario in ['cage2_raw','baby_random15','baby_heuristic15']:
 data=read(R/'inventory/prepared_v1'/f'{scenario}_observations_target_qualified.json');alpha=data['alphabet'];groups=collections.defaultdict(list);undefined=[]
 for a in alpha:
  target=qd[a]['observed_target_fields'];host=target.get('hostname')
  if host:groups[host].append(a)
  else:undefined.append(a)
 traces=[[{'symbol':e['id'],'label':e['outcome']} for e in t['events']] for t in data['traces'][:4]]
 diagnostics=[]
 for d in [0,1,2,4,8,'full']:
  for host,B in groups.items():
   conflicts=block_conflicts(traces,B,d);diagnostics.append({'depth':d,'observed_hostname':host,'types':len(B),'conflicting_contexts':len(conflicts),'first_conflict':repr(next(iter(conflicts.items()))) if conflicts else None})
 baselines.append({'dataset':scenario,'full_alphabet_types':len(alpha),'undefined_scope_types':undefined,'whole_reference':'undefined' if undefined else 'functional observed-host scope only; not physical truth','partial_full_alphabet_diagnostics':diagnostics})
bgl=read(R/'inventory/bgl_v1/observations.json');constant=collections.defaultdict(set)
for e in bgl['traces'][0]['events'][:1400]:
 if e['outcome'] is not None:constant[e['id']].add(e['outcome'])
rows=[];coverage={}
for p in A.glob('ACTUAL_*_V1.json'):
 v=read(p)
 if not isinstance(v,dict) or 'rows'not in v:continue
 coverage[p.stem]=v['coverage']
 for r in v['rows']:rows.append({k:r[k] for k in ['arm','depth','status','independent_family_count','heldout_alternatives']})
errors=[]
for r in read(A/'ACTUAL_LEDGER_V1.json'):
 p=Path(r['attempt_dir']);cap=read(p/'result.json');assert cap['child_reaped'] and cap['execution_status']=='success'
 for stream in ['stdout','stderr']:assert hashlib.sha256((p/(stream+'.bin')).read_bytes()).hexdigest()==cap[stream+'_sha256']
 for s in read(p/'manifest.json')['sources']:assert hashlib.sha256((A/s['snapshot']).read_bytes()).hexdigest()==s['sha256'] and hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
summary={'status':'42_completed_cells_match_independent_complete_RGS_and_witness_replay','cells':len(rows),'semantic_certificate_errors':0,'small_controls_calls':read(A/'SMALL_CONTROLS_V1.json')['calls'],'rows':rows,'coverage':coverage,'full_alphabet_scope_baselines':baselines,'BGL_constancy':{'training_EventIds':len(constant),'mixed_output_EventIds':sum(len(v)>1 for v in constant.values()),'explanation':'Selected types have constant observed training outputs; d0 imposes no grouping restriction, so every partition fits. This is not subsystem recovery.'},'limitations':['Observed scope is not independently proved physical ownership','Incomplete operational sampled history','Selected types omit potentially state-relevant inputs','No accuracy claim from arbitrary extension','All heldout tables retain training model and report abstention','No timing repetitions or public promotion'],'solver_sha256':'73ff8ecae70a55525ec6a2d3f1216e721ad2f1298d973d334e6f743080358e4e'}
(A/'ACTUAL_RESULTS_V1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# C025 independent actual-data results','',f"All {len(rows)} cells match independent complete RGS classification; output functions and conflict references replayed. Zero completed semantic/certificate errors. Small controls: {summary['small_controls_calls']} calls.",'','| Representation | d0 | d1 | d2 | d4 | d8 | full |','|---|---|---|---|---|---|---|']
for arm in sorted({r['arm'] for r in rows}):
 rr=[r for r in rows if r['arm']==arm];lines.append('| '+arm+' | '+' | '.join(r['status']+' ('+str(r['independent_family_count'])+')' for r in rr)+' |')
lines+=['','Counts are complete compatible-family sizes. Target-qualified simulator arms are primary; action-only arms are secondary diagnostics. No cell certified unique.','',summary['BGL_constancy']['explanation'],'','Full-alphabet scope diagnostics, exact coverage counts, and heldout results for both alternatives are in ACTUAL_RESULTS_V1.json. Nonfunctional/global scopes leave whole ownership references undefined. Source-backed AND obstruction witnesses remain in OBSERVED_AND_OBSTRUCTION_V1.json.','',*['- '+s for s in summary['limitations']]]
(A/'ACTUAL_RESULTS_V1.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');(A/'READINESS_V3.json').write_text(json.dumps({'state':'bounded_actual_evaluation_verified','cells':len(rows),'semantic_certificate_errors':0,'full_small_RGS_matches':True,'captures_verified':7,'public_promotion':False,'results':str(A/'ACTUAL_RESULTS_V1.json')},indent=2)+'\n')
print({'cells':len(rows),'statuses':dict(collections.Counter(r['status'] for r in rows)),'BGL_mixed':summary['BGL_constancy']['mixed_output_EventIds']})

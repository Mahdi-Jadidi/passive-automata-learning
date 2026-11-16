"""Posthoc integrity/coverage only. No solver or oracle imports or executions."""
import collections,hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 freeze=read(A/'ACTUAL_FREEZE_V3.json');checks=[];coverage=[];errors=[];files=[A/'ACTUAL_FREEZE_V3.json',A/'evaluate_v3.py',A/'PROTOCOL_V3.md',A/'ACTUAL_RESULTS_V1.json']
 qdict=read(R/'inventory/prepared_v1/target_qualified_dictionary_metadata.json')['dictionary'];adict=read(R/'inventory/prepared_v1/token_dictionary.json');bmeta=read(R/'inventory/bgl_v1/eventid_dictionary_metadata.json')
 for arm in freeze['arms']:
  ip=Path(arm['path']);assert digest(ip)==arm['sha256'];data=read(ip);rp=A/('ACTUAL_'+arm['id']+'_V1.json');result=read(rp);files.extend([ip,rp]);selected=set(result['selected']);train=data['traces'][:4] if arm['id']!='BGL' else [{'file_id':0,'events':data['traces'][0]['events'][:1400]}];test=data['traces'][4:] if arm['id']!='BGL' else [{**data['traces'][0],'events':data['traces'][0]['events'][1400:]}];refs={t['file_id']:[e for e in t['events'] if e['id'] in selected] for t in train}
  for row in result['rows']:
   cid=arm['id']+'-d'+str(row['depth'])
   try:
    res=row['result'];assert res['complete'] is True;status=res['status'];assert res['certificate']['search_exhausted'] is (status!='ambiguous')
    ws=res.get('alternatives',[]) if status=='ambiguous' else [res['witness']] if status=='certified_unique' else []
    if status=='ambiguous':assert len(ws)==2
    keys=[]
    for w in ws:
     blocks=w['blocks'];assert isinstance(blocks,list) and blocks and all(isinstance(b,list) and b for b in blocks)
     flat=[x for b in blocks for x in b];assert len(flat)==len(set(flat)) and set(flat)==selected
     key=tuple(sorted(tuple(sorted(b)) for b in blocks));keys.append(key)
     funcs=w['functions'];assert len(funcs)==len(blocks);fkeys=[]
     for fn in funcs:
      b=fn['block'];assert b and len(b)==len(set(b));fkeys.append(tuple(sorted(b)))
     assert len(set(fkeys))==len(fkeys) and sorted(fkeys)==list(key)
    assert len(keys)==len(set(keys))
    for c in res['certificate']['block_checks']:
     conflict=c.get('conflict')
     if conflict:
      a=conflict['first'];b=conflict['opposite'];x=refs[a['file_id']][a['event_index']];y=refs[b['file_id']][b['event_index']]
      assert x['outcome'] is conflict['first_outcome'] and y['outcome'] is conflict['opposite_outcome']
      assert type(x['outcome']) is bool and type(y['outcome']) is bool and x['outcome']!=y['outcome']
      assert x['id']==y['id']==conflict['current_id'] and x['id'] in c['blocks_symbols']
    checks.append({'cell_id':cid,'status':'passed','alternatives_checked':len(ws),'heldout_alternatives_recorded':len(row['heldout_alternatives'])});assert len(row['heldout_alternatives'])==len(ws)
   except Exception as e:errors.append({'failure_id':'C025-POSTHOC-'+cid,'error':repr(e)})
  for split,ts in [('training',train),('heldout',test)]:
   ev=[e for t in ts for e in t['events']];entry={'arm':arm['id'],'split':split}
   for kind,keep in [('retained',True),('omitted',False)]:
    subset=[e for e in ev if (e['id'] in selected)==keep];counts=collections.Counter('None' if e['outcome'] is None else str(e['outcome']) for e in subset);types=sorted({e['id'] for e in subset});actions={};scopes={}
    for token in types:
     if arm['id']=='BGL':actions[token]='EventId template';scopes[token]='node ownership nonfunctional/unverified'
     else:
      desc=(qdict if arm['primary'] else adict)[token];actions[token]=desc.get('action');target=desc.get('observed_target_fields')
      scopes[token]=('observed_hostname' if target.get('hostname') else 'ip_only_unresolved' if target.get('ip_address') else 'subnet_scope' if target.get('subnet') or target.get('subnetname') else 'no_target_or_global') if target is not None else 'action_only_aliasing_scope_not_identifiable'
    entry[kind]={'events':len(subset),'label_counts':{v:counts[v] for v in ['True','False','None']},'types':types,'type_count':len(types),'action_by_type':actions,'scope_by_type':scopes}
   coverage.append(entry)
 # Include authenticated original artifacts/receipts and all used input/result/harness bytes.
 for p in [R/'external/loghub_bgl_v1/ACQUISITION_V1.json',R/'inventory/prepared_v1/manifest.json',R/'inventory/prepared_v1/faithful_records_and_metadata.json',R/'inventory/prepared_v1/aliasing_diagnostics.json',R/'inventory/prepared_v1/target_qualified_dictionary_metadata.json',R/'inventory/bgl_v1/manifest.json',A/'preparation_v1/PROVENANCE_V1.json',Path(__file__)]:files.append(p)
 receipt=read(A/'preparation_v1/PROVENANCE_V1.json');zp=Path(receipt['archive']['path']);assert digest(zp)==receipt['archive']['sha256'];files.append(zp)
 for f in read(R/'external/loghub_bgl_v1/ACQUISITION_V1.json')['files']:
  p=R/'external/loghub_bgl_v1'/f['local'];assert digest(p)==f['sha256'];files.append(p)
 report={'status':'passed' if not errors and len(checks)==42 else 'rejected','cells_checked':len(checks),'errors':errors,'checks':checks,'coverage_supplement':coverage,'solver_oracle_reruns':0,'original_results_modified':False}
 out=A/'POSTHOC_INTEGRITY_COVERAGE_V1.json'
 with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 files.append(out)
 with (A/'POSTHOC_FREEZE_V1.json').open('x',encoding='utf-8') as f:json.dump([{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':digest(p)} for p in dict.fromkeys(files)],f,indent=2)
 print(json.dumps({'status':report['status'],'cells':len(checks),'errors':errors,'coverage_records':len(coverage)}))
if __name__=='__main__':main()

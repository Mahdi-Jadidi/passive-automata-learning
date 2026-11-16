"""Independent operational BGL sample assessment; no solver or model run."""
import collections,csv,hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent;SRC=A.parent/'external/loghub_bgl_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=json.loads((SRC/'ACQUISITION_V1.json').read_text());verified=[]
 for f in receipt['files']:
  p=SRC/f['local'];assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'];verified.append({'file':str(p),'sha256':sha(p),'url':f['url']})
 lines=(SRC/'BGL_2k.log').read_text(encoding='utf-8').splitlines()
 with (SRC/'BGL_2k.log_structured.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
 assert len(rows)==len(lines)==2000
 errors=[];nodes=collections.defaultdict(set);templates=collections.defaultdict(set);template_ids=collections.defaultdict(set);outputs=collections.defaultdict(collections.Counter);labels=collections.Counter();references=collections.defaultdict(dict)
 fields=['Label','Timestamp','Date','Node','Time','NodeRepeat','Type','Component','Level','Content']
 for i,(line,r) in enumerate(zip(lines,rows),1):
  try:
   parts=line.split(None,9);assert len(parts)==10 and int(r['LineId'])==i
   for key,value in zip(fields,parts):assert r[key]==value,(key,r[key],value)
   assert r['EventId'] and r['EventTemplate'];nodes[r['EventId']].add(r['Node']);templates[r['EventId']].add(r['EventTemplate']);template_ids[r['EventTemplate']].add(r['EventId']);label=r['Label']=='-';outputs[r['EventId']][label]+=1;labels[label]+=1;references[r['EventId']].setdefault(label,i)
  except Exception as e:errors.append({'failure_id':f'C025-BGL-ROW-{i:04}','row':i,'error':repr(e)})
 shared={event:sorted(ns) for event,ns in nodes.items() if len(ns)>1};mixed={event:{'nonalert':c[True],'alert':c[False],'opposite_row_witnesses':references[event]} for event,c in outputs.items() if c[True] and c[False]}
 report={'status':'verified' if not errors else 'rejected','commit':receipt['commit'],'verified_sources':verified,'raw_rows':len(lines),'csv_rows':len(rows),'ordered_raw_csv_fields_verified':fields,'errors':errors,'distinct_EventId':len(nodes),'distinct_nodes':len(set().union(*nodes.values())),'labels':{'nonalert_true':labels[True],'alert_false':labels[False]},'event_template_nonfunctional':{k:list(v) for k,v in templates.items() if len(v)>1},'template_EventId_nonfunctional':{k:list(v) for k,v in template_ids.items() if len(v)>1},'EventId_shared_across_nodes':shared,'shared_EventId_count':len(shared),'constant_current_EventId_output_conflicts':mixed,'known_node_partition_status':'undefined: EventId templates shared across nodes; not a functional symbol-owner map' if shared else 'not independently validated physical ownership','input_symbol':'original EventId only; no Node, Label, Content, timestamp or source row encoded','output_semantics':'True iff original alert tag equals - (nonalert), False for alert tag; not action success or whole-word language rejection','boundary':'one stream in observed sample row order; no invented reset','completeness':'2k sample may omit intervening events; ordered rows do not establish complete physical history or common initial system state','provenance':'operational BlueGene/L log sample hosted by Loghub; source provenance distinct from CAGE2/Baby simulator artifact','original_code_executed':False,'solver_executed':False}
 with (A/'BGL_ASSESSMENT_V1.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:report[k] for k in ['status','raw_rows','csv_rows','distinct_EventId','distinct_nodes','labels','shared_EventId_count','known_node_partition_status']}))
if __name__=='__main__':main()

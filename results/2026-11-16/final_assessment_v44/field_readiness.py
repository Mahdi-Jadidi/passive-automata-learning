"""Audit real-log schema without inventing AND-acceptance labels."""
import csv,json,hashlib,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    path=ROOT/'results/2026-11-05/real_trace_checkpoint_v25/external/loghub_bgl_v1/BGL_2k.log_structured.csv'
    rows=list(csv.DictReader(path.open(encoding='utf8')));labels=collections.Counter(r['Label'] for r in rows);by_event={}
    for r in rows:by_event.setdefault(r['EventId'],set()).add(r['Label']=='-')
    report={'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(rows),'event_types':len(by_event),'label_counts':dict(labels),'event_types_with_both_alert_and_nonalert':sum(len(v)>1 for v in by_event.values()),'and_model_field_tests':0,'status':'NOT_SEMANTICALLY_AUTHORIZED','reason':'Per-message alert labels do not establish whole-trace conjunctive acceptance. Prior adapter used selected last-event outputs. No relabeling or hidden partition ground truth is injected.'}
    with (HERE/'field_readiness.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

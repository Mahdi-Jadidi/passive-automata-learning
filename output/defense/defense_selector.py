"""Presentation-facing certificate status, computed entirely before training.

NET_* means a proved net advantage against the opposite fixed pipeline in the
declared event model, with equal output languages. COST_ONLY makes no such net
or quality guarantee. Evidence is retained to keep these distinctions explicit.
"""
import json,sys
from certified_selector import predict

def select(positive,negative,blocks):
    evidence=predict(positive,negative,blocks)
    decision=evidence['decision']
    if decision=='INFEASIBLE':status='INFEASIBLE'
    elif decision=='UNKNOWN':status='UNKNOWN'
    elif (decision=='SPLIT' and evidence.get('rule')=='complete_balanced_interleavings_with_marker'
          and evidence.get('same_output_language') is True
          and evidence.get('beats_global_baseline_including_selector') is True):status='NET_SPLIT'
    elif (decision=='GLOBAL' and evidence.get('rule')=='single_active_block'
          and evidence.get('same_output_language') is True
          and evidence.get('beats_split_baseline_including_selector') is True):status='NET_GLOBAL'
    else:status='COST_ONLY'
    return {'status':status,'certified_region':{'NET_GLOBAL':'G','NET_SPLIT':'S'}.get(status),
            'pipeline_winner':decision if decision in ('SPLIT','GLOBAL') else None,
            'metric':'W_ref loop events, not elapsed time','evidence':evidence}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python defense_selector.py input.json')
    x=json.load(open(sys.argv[1],encoding='utf8'))
    print(json.dumps(select(x['positive'],x['negative'],x['blocks']),ensure_ascii=False,indent=2))

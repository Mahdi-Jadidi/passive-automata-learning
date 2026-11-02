"""Total comparison baseline, explicitly NOT a universal pre-training selector.

Static certificates run first. On UNKNOWN only, the optional exact fallback
executes both reference pipelines. This is diagnostic work, not free prediction.
CLI: python -B total_selector.py sample.json [--static-only]
"""
import json,sys
from static_selector import select as static_select
from rpni_work_reference import run,split_run


def decide(positive,negative,blocks,exact_fallback=True):
    # Parsing/type validation and set construction follow the reference's
    # unmetered library convention. H counts the static selector's loop events.
    try:
        if isinstance(positive,str) or isinstance(negative,str):
            raise ValueError('Samples must be collections of words')
        pos,neg=set(positive),set(negative)
        if any(not isinstance(w,str) for w in pos|neg):
            raise ValueError('Words must be strings')
        blocks=[set(B) for B in blocks]
        if any(not isinstance(a,str) for B in blocks for a in B):
            raise ValueError('Alphabet symbols must be strings')
        cert=static_select(pos,neg,blocks)
    except (TypeError,ValueError) as exc:
        return dict(status='INVALID',reason=str(exc),training_started=False)
    d=cert['decision'];h=cert['selector_work']
    base=dict(static_certificate=cert,training_started=False,
              scope='fixed W_ref; known partition; highest-index negative witness')
    if d=='INFEASIBLE':
        return dict(base,status='GLOBAL_ONLY',reason='No sample-consistent AND decomposition exists')
    if d!='UNKNOWN':
        winner='TIE' if d=='TIE' else 'SPLIT' if 'SPLIT' in d else 'GLOBAL'
        return dict(base,status=winner,method='STATIC_CERTIFICATE',
                    net_advantage_certified=d.startswith('NET_'))
    if not exact_fallback:
        return dict(base,status='UNKNOWN',method='STATIC_ONLY',net_advantage_certified=False)
    g=run(pos,neg);s=split_run(pos,neg,blocks)
    winner='GLOBAL' if g['W']<s['W'] else 'SPLIT' if s['W']<g['W'] else 'TIE'
    base['training_started']=True
    return dict(base,status=winner,method='EXACT_EXECUTION_FALLBACK',
                global_work=g['W'],split_work=s['W'],
                diagnostic_work=h+g['W']+s['W'],
                net_advantage_certified=False,
                global_events=g['events'],
                split_preparation=s['projection_work'],
                local_events=[r['events'] for r in s['runs']])


if __name__=='__main__':
    with open(sys.argv[1],encoding='utf8') as stream:x=json.load(stream)
    print(json.dumps(decide(x['positive'],x['negative'],x['blocks'],
                           exact_fallback='--static-only' not in sys.argv),
                     indent=2,ensure_ascii=False))

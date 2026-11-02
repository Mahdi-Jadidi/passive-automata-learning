"""Pre-training action on every valid feasible input, with a regret bound.
An action is NOT necessarily a certified winner. UNKNOWN remains explicit.
"""
from static_selector import select


def choose(positive,negative,blocks):
    cert=select(positive,negative,blocks)
    d=cert['decision'];h=cert['selector_work']
    if d=='INFEASIBLE':
        return dict(action='GLOBAL_ONLY',winner_certified=None,certificate=cert)
    if d!='UNKNOWN':
        action='GLOBAL' if d=='TIE' or 'GLOBAL' in d else 'SPLIT'
        return dict(action=action,winner_certified=True,excess_pipeline_work_bound=0,
                    excess_including_selection_bound=h,certificate=cert)
    lg,ug=cert['global_interval'];ls,us=cert['split_interval']
    rg=max(0,ug-ls);rs=max(0,us-lg)
    action='GLOBAL' if rg<=rs else 'SPLIT';regret=min(rg,rs)
    return dict(action=action,winner_certified=False,
                excess_pipeline_work_bound=regret,
                excess_including_selection_bound=h+regret,
                guarantee='Chosen work minus min(WG,WS) is at most the bound; winner is not certified.',
                certificate=cert)

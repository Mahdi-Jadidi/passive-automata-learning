"""Independent SCHEMA_V1.md ledger replay, core commit 539af04.
Checks raw mathematical evidence and normalized observation consistency only.
No producer code, authentication, persistent resume or operational incumbent.
"""
from independent_replay import (VERSION, InvalidProof, require, fields, array, index,
                                digest, hex_digest, sample_data, owner_map, deletion, load_json)
from production_replay import scope_v1, verify_request, replay_closure, check_structural


def verify_table(X,Y,p,t,failed):
    fields(t,'group named_zeros anonymous_zeros free_groups')
    g=index(t['group'],len(p)); require(p[g]==g,'noncanonical table group')
    def project(w): return tuple(a for a in w if p[a]==g)
    positive={project(x) for x in X}; negative=[project(y) for y in Y]
    used=set(); named=set(); free=set()
    def col(i):
        index(i,len(Y)); require(i not in used,'duplicate negative column'); used.add(i); return negative[i]
    for z in array(t['named_zeros']):
        fields(z,'negative positive'); i=z['negative']; j=index(z['positive'],len(X))
        require(col(i)==project(X[j]),'false named zero'); named.add(i)
    for i in array(t['anonymous_zeros']): require(col(i) in positive,'false anonymous zero')
    for group in array(t['free_groups']):
        values={col(i) for i in array(group)}
        require(len(values)==1,'empty or unequal free group')
        v=next(iter(values)); require(v not in positive and v not in free,'false or split free group'); free.add(v)
    require(len(used)==len(Y) and failed in named,'missing column or named failed witness')
    return g


def verify_observation(X,Y,origin,p,requests):
    fields(p,'request_digest status response_digest receipt_digest feedback')
    key=hex_digest(p['request_digest']); require(key in requests,'unregistered request')
    req=requests[key]; status=p['status']; receipt=p['receipt_digest']; feedback=p['feedback']
    require(status in ('ACCEPT','PROJECTION_NO','BOUNDED_NO','UNKNOWN'),'invalid verdict')
    hex_digest(p['response_digest'])
    if origin=='SIMULATOR': require(receipt is None,'simulator receipt')
    elif status!='UNKNOWN' or receipt is not None: hex_digest(receipt)
    if status=='PROJECTION_NO':
        fields(feedback,'kind failed_negative tables'); require(feedback['kind']=='UNRESTRICTED_COMPLETE','untyped feedback')
        failed=index(feedback['failed_negative'],len(Y)); owner=req['owner']
        groups=[verify_table(X,Y,owner,t,failed) for t in array(feedback['tables'])]
        require(groups==sorted(set(owner)),'table group coverage/order')
    elif status=='BOUNDED_NO':
        require(req['scope']['regime']=='BOUNDED','bounded scope required')
        if feedback is not None:
            fields(feedback,'kind artifact_digest'); require(feedback['kind'] in ('BOUNDED_OPAQUE','CONDITIONED_OPAQUE'),'opaque feedback kind')
            hex_digest(feedback['artifact_digest'])
    else: require(feedback is None,'unexpected feedback')
    return key,receipt,status


def replay_ledger(raw, scope, records, *, deletion_budget=None):
    """Pure batch replay; errors expose no verified prefix or mutable state.
    OPEN/PARTIAL are not exhaustion. An observation cannot establish external ACCEPT.
    """
    n,X,Y,sd=sample_data(raw); scope_v1(scope,sd)
    closure=[]; terminal='OPEN'; owner=list(range(n)); conflict=False
    requests={}; attempts=set(); request_ids={}; observed={}; receipts=set(); checks=[]; zeros=[]; standalone=0
    for r in array(records):
        fields(r,'version origin sample_digest kind payload')
        require(r['version']==VERSION and r['sample_digest']==sd,'record binding')
        kind,origin,p=r['kind'],r['origin'],r['payload']
        if origin=='RAW':
            if kind=='COMPONENT_EPOCH':
                require(terminal=='OPEN' and not conflict,'epoch after terminal or conflict')
                fields(p,'epoch owner facts edges result_owner state cursor')
                closure.append(r); owner=p['result_owner']
                terminal='PARTIAL' if p['state']=='PARTIAL' else 'FIXPOINT' if p['state']=='EXHAUSTED' and not p['edges'] else 'OPEN'
            elif kind=='LABEL_CONFLICT':
                fields(p,'negative positive'); require(Y[index(p['negative'],len(Y))]==X[index(p['positive'],len(X))],'false label conflict')
                conflict=True
            elif kind=='DELETE_EQUAL':
                fields(p,'owner fact'); q=owner_map(p['owner'],n); f=p['fact']; fields(f,'negative group positive')
                deletion(X,Y,q,f['negative'],f['group'],f['positive']); standalone+=1
            elif kind=='STRUCTURAL_CHECK':
                fields(p,'owner compatible separating_groups failed_negative'); q=owner_map(p['owner'],n)
                checks.append((q,check_structural(X,Y,q,p)))
            elif kind=='REQUEST':
                key=verify_request(raw,p); aid=p['attempt_id']; rid=p['request_id']; binding=digest({k:v for k,v in p.items() if k!='attempt_id'})
                require(aid not in attempts and request_ids.get(rid,binding)==binding,'request or attempt reuse')
                attempts.add(aid); request_ids[rid]=binding; requests[key]=p
            else: raise InvalidProof('unsupported raw kind')
        else:
            require(origin in ('SIMULATOR','EXTERNAL') and kind=='OBSERVATION','invalid observation provenance')
            key,receipt,status=verify_observation(X,Y,origin,p,requests)
            require(key not in observed,'duplicate attempt observation')
            require(receipt is None or receipt not in receipts,'duplicate receipt reference')
            observed[key]=status
            if receipt is not None: receipts.add(receipt)
            if status=='PROJECTION_NO': zeros.append(key) # literal structural NO only
    if closure:
        result=replay_closure(raw,scope,dict(state=terminal,owner=owner,records=closure),allow_prefix=True,deletion_budget=deletion_budget)
        owner=result['mandatory_owner']; floor=result['mandatory_floor']
    else: owner=tuple(owner); floor=0
    # Absence of a response and UNKNOWN both remain unresolved attempt records.
    pending=tuple(k for k in requests if observed.get(k) in (None,'UNKNOWN'))
    optimum=floor if (owner,True) in checks and not conflict and scope['regime']=='UNRESTRICTED' else None
    return dict(mandatory_owner=owner,mandatory_floor=floor,closure_state='LABEL_CONFLICT' if conflict else terminal,
                label_conflict=conflict,standalone_deletions=standalone,structural_checks=tuple(checks),
                structural_no_request_digests=tuple(zeros),pending_attempt_digests=pending,
                observations=len(observed),structural_optimum=optimum,operational_status='INCOMPLETE')


def replay_ledger_json(raw_text,scope_text,records_text):
    return replay_ledger(load_json(raw_text),load_json(scope_text),load_json(records_text))

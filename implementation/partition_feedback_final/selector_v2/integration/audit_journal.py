"""P2.1 test-side provenance audit, independent of producer and adapter code.

Uses the pinned proof stream for the v1 projection; this outer-format checker
is core-authored integration evidence, not independent proof-stream approval.
It checks consistency, not cryptographic authenticity or durable history.
"""
import hashlib
import json
from independent_replay import VERSION, InvalidProof, require, fields, array, index, sample_data
from production_replay import verify_request
from ledger_replay import replay_ledger


JOURNAL_VERSION = 'selector-v2-journal/2'


def encoded(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(encoded(value))


def parse(data):
    require(type(data) is bytes,'expected bytes')
    def pairs(seq):
        out = {}
        for k,v in seq:
            require(k not in out,'duplicate JSON key'); out[k] = v
        return out
    def reject(_):
        raise InvalidProof('noninteger JSON number')
    return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_float=reject,parse_constant=reject)


def unhex(value, checksum):
    require(type(value) is str and len(value)%2 == 0 and all(c in '0123456789abcdef' for c in value),'invalid artifact hex')
    b = bytes.fromhex(value)
    require(sha(b) == checksum,'artifact digest mismatch')
    return b


def text_id(value):
    return type(value) is str and bool(value)


def validate_registration(raw, entry, X, Y):
    fields(entry,'request capacities origin maps')
    q = entry['request']; verify_request(raw,q)
    require(entry['origin'] in ('SIMULATOR','EXTERNAL'),'invalid registration origin')
    caps = entry['capacities']; groups = sorted(set(q['owner']))
    if caps is None:
        require(q['scope']['regime']=='UNRESTRICTED' and q['scope']['capacity_digest'] is None,'capacity scope')
    else:
        require(len(array(caps))==len(groups) and all(type(c) is int and c>0 for c in caps),'invalid capacities')
        require(q['scope']['regime']=='BOUNDED' and q['scope']['capacity_digest']==digest(['capacity-v2',list(zip(groups,caps))]),'capacity digest mismatch')
    fields(entry['maps'],'positive negative')
    for label,count in [('positive',len(X)),('negative',len(Y))]:
        mapping = entry['maps'][label]
        if mapping is not None:
            require(type(mapping) is dict and all(text_id(k) for k in mapping),'invalid ID map')
            require(all(type(v) is int for v in mapping.values()) and sorted(mapping.values())==list(range(count)),'nonbijective map')
    return q


def check_dfas(payload, q, caps, X, Y):
    owner=q['owner']; groups=sorted(set(owner)); dfas=array(payload['dfas'])
    require(len(dfas)==len(groups),'DFA coverage')
    rows=[]
    for k,(g,d) in enumerate(zip(groups,dfas)):
        fields(d,'block states initial accepting transitions')
        n=d['states']; require(type(d['block']) is int and d['block']==g and type(n) is int and n>0,'DFA block/states')
        require(caps is None or n<=caps[k],'DFA capacity')
        index(d['initial'],n); accepting=array(d['accepting'])
        for a in accepting: index(a,n)
        require(len(set(accepting))==len(accepting),'duplicate accepting state')
        block={a for a,b in enumerate(owner) if b==g}; transitions={}
        for row in array(d['transitions']):
            require(len(array(row))==3,'DFA transition shape')
            u,a,v=row; index(u,n); index(v,n); index(a,len(owner))
            require(a in block and (u,a) not in transitions,'DFA transition scope/duplicate')
            transitions[u,a]=v
        require(len(transitions)==n*len(block),'incomplete DFA')
        def accepts(w):
            state=d['initial']
            for a in w:
                if a in block: state=transitions[state,a]
            return state in accepting
        require(all(accepts(x) for x in X),'DFA positive rejected')
        rows.append([int(not accepts(y)) for y in Y])
    require(all(any(row[i] for row in rows) for i in range(len(Y))),'DFA negative accepted')
    if 'joint_row' in payload:
        require(encoded(payload['joint_row'])==encoded(rows),'DFA joint row mismatch')


def normalize_feedback(payload, q, caps, X, Y):
    base='version request origin status complete receipt'; status=payload.get('status')
    require(status in ('PROJECTION_NO','ACCEPT','BOUNDED_NO'),'invalid normalized status')
    extra={'PROJECTION_NO':' failed tables','ACCEPT':' dfas','BOUNDED_NO':' exact'}[status]
    if status=='ACCEPT' and 'joint_row' in payload: extra+=' joint_row'
    fields(payload,base+extra)
    require(payload['version']==VERSION and payload['complete'] is True and text_id(payload['receipt']),'invalid response envelope')
    require(encoded(payload['request'])==encoded(q),'response request mismatch')
    if status=='BOUNDED_NO':
        require(caps is not None and payload['exact'] is True,'invalid bounded failure'); return None
    if status=='ACCEPT':
        check_dfas(payload,q,caps,X,Y); return None
    failed=index(payload['failed'],len(Y)); tables=[]
    groups=sorted(set(q['owner'])); source=array(payload['tables'])
    require(len(source)==len(groups),'normalized table coverage')
    for g,t in zip(groups,source):
        fields(t,'block kind complete zeros free')
        require(type(t['block']) is int and t['block']==g and t['kind']=='UNRESTRICTED_BASE' and t['complete'] is True,'normalized table scope')
        named=[]; anonymous=[]
        for z in array(t['zeros']):
            fields(z,'negative positive')
            if z['positive'] is None: anonymous.append(z['negative'])
            else: named.append(z)
        tables.append(dict(group=g,named_zeros=named,anonymous_zeros=anonymous,free_groups=array(t['free'])))
    return dict(kind='UNRESTRICTED_COMPLETE',failed_negative=failed,tables=tables)


def observation_record(sd, entry, status, response_digest, receipt_digest, feedback):
    return dict(version=VERSION,origin=entry['origin'],sample_digest=sd,kind='OBSERVATION',
                payload=dict(request_digest=digest(entry['request']),status=status,response_digest=response_digest,
                             receipt_digest=receipt_digest,feedback=feedback))


def _replay(raw, scope, journal_bytes):
    journal=parse(journal_bytes); require(encoded(journal)==journal_bytes,'noncanonical journal')
    fields(journal,'version sample_digest events')
    _,X,Y,sd=sample_data(raw)
    require(journal['version']==JOURNAL_VERSION and journal['sample_digest']==sd,'journal sample/version mismatch')
    entries={}; status={}; targets={}; receipts=set(); records=[]; quarantine=0
    for e in array(journal['events']):
        require(type(e) is dict,'event object'); kind=e.get('event'); batch=array(e.get('records'))
        if kind=='RAW':
            fields(e,'event records')
            require(bool(batch) and all(type(r) is dict and r.get('origin')=='RAW' and r.get('kind') in ('COMPONENT_EPOCH','LABEL_CONFLICT','STRUCTURAL_CHECK','DELETE_EQUAL') for r in batch),'raw event bypass')
        elif kind=='REGISTER':
            fields(e,'event registered records'); entry=e['registered']; q=validate_registration(raw,entry,X,Y)
            aid,rid=q['attempt_id'],q['request_id']
            require(aid not in entries,'global attempt ID reuse')
            target=encoded(dict(entry,request={k:v for k,v in q.items() if k!='attempt_id'}))
            require(rid not in targets or targets[rid]==target,'request provenance rebound')
            require(encoded(batch)==encoded([dict(version=VERSION,origin='RAW',sample_digest=sd,kind='REQUEST',payload=q)]),'registration projection mismatch')
            entries[aid]=entry; status[aid]='PENDING'; targets[rid]=target
        elif kind in ('OBSERVE','QUARANTINE'):
            fields(e,'event request_id attempt_id wire_hex wire_sha256 records '+('status receipt_ref normalized_hex normalized_sha256' if kind=='OBSERVE' else 'reason'))
            aid,rid=e['attempt_id'],e['request_id']
            require((aid is None or type(aid) is str) and (rid is None or type(rid) is str),'invalid event IDs')
            entry=entries.get(aid)
            matched=entry is not None and entry['request']['request_id']==rid and status[aid]=='PENDING'
            if e['wire_hex'] is None:
                require(e['wire_sha256'] is None,'absent wire digest'); wire=None
            else:
                wire=unhex(e['wire_hex'],e['wire_sha256'])
            if kind=='QUARANTINE':
                quarantine+=1; require(type(e['reason']) is str,'invalid quarantine reason')
                expected=[observation_record(sd,entry,'UNKNOWN',sha(wire) if wire is not None else digest({'local_event':'NO_RESPONSE'}),None,None)] if matched else []
                require(encoded(batch)==encoded(expected),'quarantine projection mismatch')
                if matched: status[aid]='UNKNOWN'
            else:
                require(matched and wire is not None,'observation without matched pending registration')
                normal=unhex(e['normalized_hex'],e['normalized_sha256']); obs=parse(normal); payload=parse(wire)
                require(encoded(obs)==normal and type(payload) is dict,'noncanonical normalized observation')
                require(e['status']==payload.get('status') and payload.get('origin')==entry['origin'],'origin/status mismatch')
                q=entry['request']; feedback=normalize_feedback(payload,q,entry['capacities'],X,Y)
                expected=dict(version=VERSION,request=q,origin=entry['origin'],status=e['status'],operational=False,scope='NONE',payload=payload)
                require(encoded(obs)==encoded(expected),'normalized wrapper or wire mismatch')
                receipt=sha(payload['receipt'].encode('utf-8')) if entry['origin']=='EXTERNAL' else None
                require(e['receipt_ref']==receipt and (receipt is None or receipt not in receipts),'receipt reference mismatch/reuse')
                expected=[observation_record(sd,entry,e['status'],sha(wire),receipt,feedback)]
                require(encoded(batch)==encoded(expected),'normalized projection mismatch')
                if receipt is not None: receipts.add(receipt)
                status[aid]=e['status']
        else:
            raise InvalidProof('unknown journal event')
        records.extend(batch)
    proof=replay_ledger(raw,scope,records)
    require(proof['operational_status']=='INCOMPLETE','unexpected operational conclusion')
    return dict(records=records,proof=proof,attempt_status=status,pending_candidates=tuple(sorted(targets)),quarantine=quarantine)


def replay_journal(raw, scope, journal_bytes):
    """Reject inconsistent provenance; no result on invalid or resource-censored replay."""
    try:
        return _replay(raw,scope,journal_bytes)
    except InvalidProof:
        raise
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,AttributeError) as exc:
        raise InvalidProof('invalid journal: '+str(exc)) from exc

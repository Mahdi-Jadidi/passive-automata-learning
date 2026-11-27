"""Independent selector-v2-journal/2 proof kernel, pinned core 4e21dbf.
No producer, adapter, or audit_journal imports. Byte consistency is not auth.
"""
from independent_replay import (VERSION, InvalidProof, require, fields, array,
                                digest, sample_data, hex_digest)
from production_replay import verify_request, scope_v1
from ledger_replay import replay_ledger
from interface_artifact_replay import canonical, sha, strict_bytes, replay_bundle
from bounded_deletion import DeletionBudget, ReplayIncomplete

JOURNAL_VERSION='selector-v2-journal/2'
NO_RESPONSE_DIGEST=sha(canonical({'local_event':'NO_RESPONSE'}))


def unhex(h,d):
    require(type(h) is str,'missing bytes')
    b=bytes.fromhex(h)
    require(b.hex()==h and sha(b)==hex_digest(d),'byte digest mismatch')
    return b


def registration(raw,e):
    n,X,Y,sd=sample_data(raw)
    fields(e,'request capacities origin maps');q=e['request'];key=verify_request(raw,q)
    require(e['origin'] in ('SIMULATOR','EXTERNAL'),'registration origin')
    caps=e['capacities'];roots=sorted(set(q['owner']))
    if caps is None: require(q['scope']['regime']=='UNRESTRICTED','capacity regime')
    else:
        require(type(caps) is list and len(caps)==len(roots) and all(type(c) is int and c>0 for c in caps),'capacity vector')
        require(q['scope']['regime']=='BOUNDED' and q['scope']['capacity_digest']==digest(['capacity-v2',list(zip(roots,caps))]),'capacity digest')
    fields(e['maps'],'positive negative')
    for label,size in [('positive',len(X)),('negative',len(Y))]:
        m=e['maps'][label]
        if m is not None:
            require(type(m) is dict and len(m)==size and all(type(k) is str and k for k in m) and all(type(v) is int for v in m.values()) and set(m.values())==set(range(size)),'ID map')
    return q,key


def replay_journal(raw,scope,journal_bytes,*,expected_records=None,deletion_budget=None):
    """Exact canonical journal replay; raises on malformed or resource failure.
    The optional expected projection must match, never supplies missing evidence.
    Returned proof is structural only. All registered candidates remain pending.
    """
    if deletion_budget is None:deletion_budget=DeletionBudget()
    _,_,_,sd=sample_data(raw);scope_v1(scope,sd)
    j=strict_bytes(journal_bytes);fields(j,'version sample_digest events')
    require(j['version']==JOURNAL_VERSION and j['sample_digest']==sd,'journal binding')
    require(canonical(j)==journal_bytes,'noncanonical journal')
    records=[];entries={};states={};bindings={};receipts=set();quarantine=0
    for e in array(j['events']):
        require(type(e) is dict,'event object'); kind=e.get('event')
        if kind=='RAW':
            fields(e,'event records');rs=array(e['records'])
            require(bool(rs) and all(type(r) is dict and r.get('origin')=='RAW' and r.get('kind') in ('DELETE_EQUAL','COMPONENT_EPOCH','STRUCTURAL_CHECK','LABEL_CONFLICT') for r in rs),'raw event bypass')
        elif kind=='REGISTER':
            fields(e,'event registered records');entry=e['registered'];q,key=registration(raw,entry)
            aid=q['attempt_id'];rid=q['request_id']
            binding=digest(dict(entry,request={k:v for k,v in q.items() if k!='attempt_id'}))
            require(aid not in entries and bindings.get(rid,binding)==binding,'attempt reuse or retry rebound')
            expected=dict(version=VERSION,origin='RAW',sample_digest=sd,kind='REQUEST',payload=q)
            rs=array(e['records']);require(canonical(rs)==canonical([expected]),'register projection')
            entries[aid]=entry;states[aid]='PENDING';bindings[rid]=binding
        elif kind=='OBSERVE':
            fields(e,'event request_id attempt_id status receipt_ref normalized_hex normalized_sha256 wire_hex wire_sha256 records')
            aid=e['attempt_id'];rid=e['request_id'];require(type(aid) is str and type(rid) is str and aid in entries and states[aid]=='PENDING','unregistered or closed observation')
            entry=entries[aid];q=entry['request'];require(q['request_id']==rid,'observation request mismatch')
            norm=unhex(e['normalized_hex'],e['normalized_sha256']);wire=unhex(e['wire_hex'],e['wire_sha256'])
            normal=strict_bytes(norm);require(canonical(normal)==norm,'noncanonical normalized wrapper')
            # Use the separately authored wire/DFAs/tables checker. Its ephemeral
            # envelope is constructed from the actual event's original bytes.
            wrapper=dict(observation=normal,registered=entry,wire_hex=wire.hex(),wire_sha256=sha(wire))
            expected=replay_bundle(raw,canonical(wrapper),entry)
            status=expected['payload']['status'];receipt=expected['payload']['receipt_digest']
            require(e['status']==status and e['receipt_ref']==receipt,'event status or receipt binding')
            require(receipt is None or receipt not in receipts,'receipt reuse')
            rs=array(e['records']);require(canonical(rs)==canonical([expected]),'observation projection mismatch')
            states[aid]=status
            if receipt is not None:receipts.add(receipt)
        elif kind=='QUARANTINE':
            fields(e,'event request_id attempt_id reason wire_hex wire_sha256 records')
            rid,aid=e['request_id'],e['attempt_id'];require(rid is None or type(rid) is str,'quarantine request type');require(aid is None or type(aid) is str,'quarantine attempt type')
            require(type(e['reason']) is str,'quarantine reason type')
            if e['wire_hex'] is None:require(e['wire_sha256'] is None,'no-response digest fields');h=NO_RESPONSE_DIGEST
            else:h=sha(unhex(e['wire_hex'],e['wire_sha256']))
            matched=aid in entries and entries[aid]['request']['request_id']==rid and states[aid]=='PENDING'
            expected=[]
            if matched:
                entry=entries[aid];expected=[dict(version=VERSION,origin=entry['origin'],sample_digest=sd,kind='OBSERVATION',payload=dict(request_digest=digest(entry['request']),status='UNKNOWN',response_digest=h,receipt_digest=None,feedback=None))]
            rs=array(e['records']);require(canonical(rs)==canonical(expected),'quarantine changed wrong attempt or invented evidence')
            if matched:states[aid]='UNKNOWN'
            quarantine+=1
        else:raise InvalidProof('unknown journal event')
        records.extend(rs)
    if expected_records is not None:require(canonical(records)==canonical(expected_records),'outer/inner record projection mismatch')
    proof=replay_ledger(raw,scope,records,deletion_budget=deletion_budget)
    return dict(records=records,proof=proof,attempt_status=states,pending_candidates=tuple(sorted(bindings)),quarantine=quarantine)


def verify_journal(raw,scope,journal_bytes,*,expected_records=None,deletion_budget=None,max_journal_bytes=64*1024*1024):
    """Fail-closed public boundary. VERIFIED means consistency/structural evidence,
    never external authentication. INVALID/INCOMPLETE expose no proof.
    Limits are cooperative deletion caps + journal byte cap, not hard RSS/time.
    """
    try:
        if type(journal_bytes) is bytes and len(journal_bytes)>max_journal_bytes:raise ReplayIncomplete('journal byte cap')
        if deletion_budget is None:deletion_budget=DeletionBudget()
        result=replay_journal(raw,scope,journal_bytes,expected_records=expected_records,deletion_budget=deletion_budget)
        return dict(status='VERIFIED',result=result,operational_status='INCOMPLETE')
    except (ReplayIncomplete,MemoryError,RecursionError,TimeoutError,InterruptedError) as exc:
        return dict(status='INCOMPLETE',reason=str(exc) or type(exc).__name__,operational_status='INCOMPLETE')
    except (ValueError,TypeError,KeyError,IndexError,OverflowError,AttributeError) as exc:
        cause=exc.__cause__ or exc.__context__
        if isinstance(cause,(ReplayIncomplete,MemoryError,RecursionError,TimeoutError,InterruptedError)):
            return dict(status='INCOMPLETE',reason=type(cause).__name__,operational_status='INCOMPLETE')
        return dict(status='INVALID',reason=str(exc),operational_status='INCOMPLETE')

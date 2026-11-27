"""Independent replay of RegisteredLedger artifacts (interface c6487af).
No adapter/core imports. The registration must be supplied by the caller's
trusted journal; matching self-reported fields is not authentication.
"""
import hashlib
import json
from independent_replay import VERSION, InvalidProof, require, fields, array, index, digest, sample_data, load_json
from production_replay import verify_request
from ledger_replay import verify_table


def canonical(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_bytes(raw):
    require(type(raw) is bytes, 'expected bytes')
    obj = load_json(raw.decode('utf-8'))
    def walk(v):
        if type(v) is dict:
            for x in v.values(): walk(x)
        elif type(v) is list:
            for x in v: walk(x)
        else: require(type(v) in (str,int,bool,type(None)), 'noninteger JSON value')
    walk(obj)
    return obj


def independent_dfa(d,g,p,X,Y,cap):
    fields(d,'block states initial accepting transitions')
    n=d['states']; require(type(n) is int and n>0 and (cap is None or n<=cap), 'state count/capacity')
    require(type(d['block']) is int and d['block']==g,'DFA block')
    initial=index(d['initial'],n); accept=set()
    for a in array(d['accepting']):
        index(a,n); require(a not in accept,'duplicate final state'); accept.add(a)
    B={a for a,v in enumerate(p) if v==g}; delta={}
    for row in array(d['transitions']):
        require(type(row) is list and len(row)==3,'transition shape')
        s,a,t=row; index(s,n); index(t,n); index(a,len(p))
        require(a in B and (s,a) not in delta,'transition domain'); delta[s,a]=t
    require(len(delta)==n*len(B),'incomplete DFA')
    def run(w):
        s=initial
        for a in w:
            if a in B: s=delta[s,a]
        return s in accept
    require(all(run(x) for x in X),'positive rejected')
    return [int(not run(y)) for y in Y]


def replay_bundle(raw, encoded, registration):
    """Verify actual immutable adapter bytes against external expected registration.
    Return test-only core translation; receipt reference is not authentication.
    """
    n,X,Y,sd=sample_data(raw)
    b=strict_bytes(encoded); fields(b,'observation registered wire_hex wire_sha256')
    require(canonical(b)==encoded,'noncanonical committed bundle')
    reg=b['registered']; fields(reg,'request capacities origin maps')
    require(canonical(reg)==canonical(registration),'wrong registered attempt/origin/maps')
    q=reg['request']; key=verify_request(raw,q); p=q['owner']; roots=sorted(set(p))
    caps=reg['capacities']; origin=reg['origin']; require(origin in ('SIMULATOR','EXTERNAL'),'origin')
    if caps is None: require(q['scope']['regime']=='UNRESTRICTED','capacity scope')
    else:
        require(type(caps) is list and len(caps)==len(roots) and all(type(c) is int and c>0 for c in caps),'capacity vector')
        require(q['scope']['regime']=='BOUNDED' and q['scope']['capacity_digest']==digest(['capacity-v2',list(zip(roots,caps))]),'capacity digest')
    fields(reg['maps'],'positive negative')
    for label,size in [('positive',len(X)),('negative',len(Y))]:
        m=reg['maps'][label]
        if m is not None:
            require(type(m) is dict and len(m)==size and all(type(k) is str and k for k in m) and all(type(v) is int for v in m.values()) and set(m.values())==set(range(size)),'ID map')
    try: wire=bytes.fromhex(b['wire_hex'])
    except (ValueError,TypeError) as exc: raise InvalidProof('wire hex') from exc
    require(wire.hex()==b['wire_hex'] and sha(wire)==b['wire_sha256'],'wire digest mismatch')
    w=strict_bytes(wire); o=b['observation']; fields(o,'version request origin status operational scope payload')
    require(o['version']==VERSION and o['origin']==origin and o['operational'] is False and o['scope']=='NONE','untrusted observation authority')
    require(canonical(o['request'])==canonical(q) and canonical(o['payload'])==canonical(w),'observation binding')
    status=o['status']; require(status in ('PROJECTION_NO','ACCEPT','BOUNDED_NO'),'unknown committed status')
    base='version request origin status complete receipt'
    extra={'PROJECTION_NO':' failed tables','ACCEPT':' dfas','BOUNDED_NO':' exact'}[status]
    if status=='ACCEPT' and 'joint_row' in w: extra+=' joint_row'
    fields(w,base+extra)
    require(w['version']==VERSION and canonical(w['request'])==canonical(q) and w['origin']==origin and w['status']==status and w['complete'] is True,'wire binding')
    require(type(w['receipt']) is str and bool(w['receipt']),'receipt reference')
    feedback=None
    if status=='PROJECTION_NO':
        failed=index(w['failed'],len(Y)); tables=[]
        for t in array(w['tables']):
            fields(t,'block kind complete zeros free'); require(t['kind']=='UNRESTRICTED_BASE' and t['complete'] is True,'table scope')
            named=[]; anon=[]
            for z in array(t['zeros']):
                fields(z,'negative positive')
                if z['positive'] is None: anon.append(z['negative'])
                else: named.append(z)
            table=dict(group=t['block'],named_zeros=named,anonymous_zeros=anon,free_groups=t['free'])
            verify_table(X,Y,p,table,failed); tables.append(table)
        require([t['group'] for t in tables]==roots,'table coverage/order')
        feedback=dict(kind='UNRESTRICTED_COMPLETE',failed_negative=failed,tables=tables)
    elif status=='ACCEPT':
        ds=array(w['dfas']); require(len(ds)==len(roots),'DFA coverage')
        rows=[independent_dfa(d,g,p,X,Y,None if caps is None else caps[i]) for i,(g,d) in enumerate(zip(roots,ds))]
        require(all(any(r[i] for r in rows) for i in range(len(Y))),'negative accepted')
        if 'joint_row' in w: require(canonical(w['joint_row'])==canonical(rows),'joint row')
    else: require(caps is not None and w['exact'] is True,'opaque bounded NO')
    # Test-only conversion: external receipt token hash is a reference, NOT authenticated.
    return dict(version=VERSION,origin=origin,sample_digest=sd,kind='OBSERVATION',payload=dict(request_digest=key,status=status,response_digest=sha(wire),receipt_digest=None if origin=='SIMULATOR' else sha(w['receipt'].encode()),feedback=feedback))

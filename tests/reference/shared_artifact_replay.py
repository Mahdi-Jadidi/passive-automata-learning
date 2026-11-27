"""Independent replay of SharedGateway export; no producer imports.
Registration sidecars are checked for internal consistency, not authenticated.
An EXTERNAL-shaped artifact cannot establish operational acceptance here.
"""
from independent_replay import require, fields, array, digest, sample_data, hex_digest, owner_map, load_json
from production_replay import verify_request
from ledger_replay import replay_ledger
from interface_artifact_replay import canonical, sha, strict_bytes, replay_bundle


def unhex(value):
    require(type(value) is str, 'hex type')
    b=bytes.fromhex(value);require(b.hex()==value,'noncanonical hex');return b


def replay_shared(raw,scope,bundle):
    fields(bundle,'records owner registrations artifacts quarantine')
    n,X,Y,sd=sample_data(raw)
    result=replay_ledger(raw,scope,bundle['records'])
    require(owner_map(bundle['owner'],n)==result['mandatory_owner'],'outer owner')
    require(type(bundle['registrations']) is dict and type(bundle['artifacts']) is dict,'sidecar maps')
    artifacts={}
    for k,v in bundle['artifacts'].items():
        b=unhex(v);require(hex_digest(k)==sha(b),'artifact hash');artifacts[k]=b
    requests={}; reg={}; bindings={}; observed=set(); counts={}; quarantine=[]
    for r in bundle['records']:
        if r['kind']=='REQUEST':
            q=r['payload']; key=verify_request(raw,q);requests[key]=q
            require(key in bundle['registrations'],'missing registration')
            b=unhex(bundle['registrations'][key]);e=strict_bytes(b);require(canonical(e)==b,'noncanonical registration')
            fields(e,'request origin capacities maps');require(canonical(e['request'])==canonical(q),'registration request')
            require(e['origin'] in ('SIMULATOR','EXTERNAL'),'registration origin')
            cap=e['capacities'];roots=sorted(set(q['owner']))
            if cap is None:require(q['scope']['regime']=='UNRESTRICTED','registration regime')
            else:
                require(type(cap) is list and len(cap)==len(roots) and all(type(c) is int and c>0 for c in cap),'registration capacities')
                require(q['scope']['regime']=='BOUNDED' and q['scope']['capacity_digest']==digest(['capacity-v2',list(zip(roots,cap))]),'registration capacity digest')
            fields(e['maps'],'positive negative')
            for label,size in [('positive',len(X)),('negative',len(Y))]:
                m=e['maps'][label]
                if m is not None:require(type(m) is dict and len(m)==size and all(type(k) is str and k for k in m) and all(type(v) is int for v in m.values()) and set(m.values())==set(range(size)),'registration ID map')
            same=dict(e,request={k:v for k,v in q.items() if k!='attempt_id'});rid=q['request_id'];key2=digest(same)
            require(bindings.get(rid,key2)==key2,'registration retry metadata rebound');bindings[rid]=key2;reg[key]=e
        elif r['kind']=='OBSERVATION':
            p=r['payload'];key=p['request_digest'];e=reg[key];q=requests[key];status=p['status'];observed.add(key)
            require(r['origin']==e['origin'],'observation registration origin')
            h=p['response_digest'];require(h in artifacts,'missing response bytes');wire=artifacts[h]
            counts[status]=counts.get(status,0)+1
            if status=='UNKNOWN':
                require(p['feedback'] is None and p['receipt_digest'] is None,'UNKNOWN authority')
                quarantine.append((q['attempt_id'],h));continue
            # Reuse the independent wire semantics checker with an ephemeral envelope
            # derived solely from the actual gateway registration and actual wire bytes.
            w=strict_bytes(wire)
            envelope=dict(observation=dict(version=q['version'],request=q,origin=r['origin'],status=status,operational=False,scope='NONE',payload=w),registered=e,wire_hex=wire.hex(),wire_sha256=h)
            converted=replay_bundle(raw,canonical(envelope),e)
            require(canonical(converted)==canonical(r),'journal differs from wire-derived facts')
            if p['receipt_digest'] is not None:
                h2=p['receipt_digest'];require(h2 in artifacts and artifacts[h2]==w['receipt'].encode(),'receipt bytes missing/mismatch')
    require(set(reg)==set(bundle['registrations']),'orphan registration')
    diagnostics=[]
    for event in array(bundle['quarantine']):
        fields(event,'attempt_id response_digest reason');require(type(event['attempt_id']) is str and event['attempt_id'] and type(event['reason']) is str and event['reason'],'quarantine shape')
        require(event['response_digest'] in artifacts,'quarantine artifact missing');diagnostics.append((event['attempt_id'],event['response_digest']))
    require(all(x in diagnostics for x in quarantine),'UNKNOWN diagnostic missing')
    return dict(result,registration_count=len(reg),artifact_count=len(artifacts),observation_counts=counts,quarantine_count=len(diagnostics),unanswered_attempts=tuple(q['attempt_id'] for k,q in requests.items() if k not in observed),operational_status='INCOMPLETE')

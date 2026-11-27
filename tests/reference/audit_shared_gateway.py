"""Audit latest actual SharedGateway exports and live in-memory fixture behavior.
Usage: python audit_shared_gateway.py CORE_DIR INTERFACE_DIR EXPORT_DIR
First run actual interface export_roundtrip.py at b27850a with pinned core.
No external learner calls. Independent kernel separate from driver imports.
"""
import copy
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from independent_replay import digest, InvalidProof
from interface_artifact_replay import canonical,sha
from shared_artifact_replay import replay_shared
from roundtrip_p21 import check,check_blobs,reject,CORE_BLOBS,INTERFACE_BLOBS


def main(core,interface,exports):
    check_blobs(core/'selector_v2',CORE_BLOBS)
    check_blobs(interface,{**INTERFACE_BLOBS,'shared_gateway.py':'33ef122814c409cc7c0d201b0cb4c3127b078862','export_roundtrip.py':'ddd211111322ff1bae9c7e2a0c0f4eaef40c9d75','test_adapter.py':'bfa7dee3373da7d267c373e238b95d271a8a2669'})
    sys.path[:0]=[str(core),str(interface)]
    from shared_gateway import SharedGateway
    from test_adapter import RAW,NO,YES
    from selector_v2.component_closure import component_closure
    from selector_v2.core import Budget
    from selector_v2.schema import scope
    b=(exports/'roundtrip_bundle.json').read_bytes();j=(exports/'roundtrip_journal.json').read_bytes()
    check(sha(b)=='1ec8d4c2d13910c0803339e1d21737716855b929511b1c56b299672b48d7ba35' and sha(j)=='425c3f4da1908592e64c9b0f94ed039ba7ebb18bf3ca5815a10f843d892aa392','published artifact mismatch')
    cases=json.loads(b);journal=json.loads(j)
    for i,(case,jc) in enumerate(zip(cases,journal)):
        raw,sc,bundle=case['raw'],case['scope'],case['bundle']
        check(canonical(jc)==canonical(dict(raw=raw,scope=sc,records=bundle['records'])),'journal mismatch')
        r=replay_shared(raw,sc,bundle);check(r['structural_optimum']==i+1 and r['operational_status']=='INCOMPLETE','optimum')
        print(f'published_case={i} records={len(bundle["records"])} optimum={r["structural_optimum"]} registrations={r["registration_count"]} artifacts={r["artifact_count"]} observations={r["observation_counts"]} pending_attempts={len(r["pending_attempt_digests"])} operational=INCOMPLETE')
    c=cases[0];raw,sc,bundle=c['raw'],c['scope'],c['bundle'];mutations=0
    def mutate(fn):
        nonlocal mutations
        z=copy.deepcopy(bundle);fn(z);reject(lambda:replay_shared(raw,sc,z));mutations+=1
    # Actual export mutations: no synthetic replacement certificates.
    for fn in [lambda z:z['records'][0]['payload']['facts'].clear(),lambda z:z['records'][0]['payload']['edges'].clear(),lambda z:z['records'][0]['payload'].update(epoch=1),lambda z:z.update(owner=[0,1,2]),lambda z:z['registrations'].pop(next(iter(z['registrations']))),lambda z:z['artifacts'].pop(next(iter(z['artifacts']))),lambda z:z['artifacts'].__setitem__(next(iter(z['artifacts'])),'00'),lambda z:z['quarantine'].clear(),lambda z:z['records'][4]['payload'].update(feedback={'bad':True}),lambda z:z['records'][6]['payload']['feedback']['tables'].pop(),lambda z:z['records'][6].update(origin='EXTERNAL'),lambda z:z['records'][6]['payload'].update(receipt_digest='0'*64),lambda z:z['records'][6]['payload'].update(response_digest='0'*64),lambda z:z['records'][7]['payload'].update(attempt_id='attempt-1')]:mutate(fn)
    def reg_origin(z):
        k=z['records'][6]['payload']['request_digest'];e=json.loads(bytes.fromhex(z['registrations'][k]));e['origin']='EXTERNAL';z['registrations'][k]=canonical(e).hex()
    mutate(reg_origin)
    # Replace actual wire DFA, update hash and journal to defeat superficial hash-only check.
    def corrupt_dfa(z):
        p=z['records'][8]['payload'];old=p['response_digest'];wire=json.loads(bytes.fromhex(z['artifacts'].pop(old)));wire['dfas'][0]['transitions'].pop();new=canonical(wire);p['response_digest']=sha(new);z['artifacts'][sha(new)]=new.hex()
    mutate(corrupt_dfa)
    print('actual_published_export_mutations_rejected='+str(mutations))
    def verify(g):return replay_shared(RAW,scope(g.sample),g.export())
    def payload(q,template=NO,**kw):p=copy.deepcopy(template);p['request']=q;p.update(kw);return canonical(p)
    g=SharedGateway(RAW);q=g.register([0,1,2],'r','a');before=g.export();reject(lambda:g.register([0,1,2],'other','a'));check(g.export()==before,'reuse rollback')
    check(g.ingest('a',None).status=='UNKNOWN','timeout');check(g.status('a')=='UNKNOWN','timeout state');check(not g.ingest('a',payload(q)).committed,'late delivery')
    before=g.export();reject(lambda:g.register([0,1,2],'r','b',origin='EXTERNAL'));check(g.export()==before,'rebound registration rollback')
    q=g.register([0,1,2],'r','b');o=g.ingest('b',payload(q));check(o.status=='PROJECTION_NO' and o.candidate_pending and not o.operational,'retry');verify(g)
    # Actual malformed table, wrong provenance, duplicate JSON: UNKNOWN control only.
    for i,kind in enumerate(('table','origin','duplicate-key','missing-receipt')):
        aid=f'bad{i}';q=g.register([0,1,2],aid,aid);before=g.export();p=copy.deepcopy(NO);p['request']=q
        if kind=='table':p['tables'].pop()
        elif kind=='origin':p['origin']='EXTERNAL'
        elif kind=='missing-receipt':p['receipt']=''
        body=b'{"status":"ACCEPT","status":"NO"}' if kind=='duplicate-key' else canonical(p)
        o=g.ingest(aid,body);after=g.export();check(o.status=='UNKNOWN' and o.candidate_pending and o.committed and after['records'][:-1]==before['records'] and after['records'][-1]['payload']['feedback'] is None,'invalid atomic rollback');verify(g)
    # Actual gateway external-shaped test callback; repeat receipt under new attempt.
    h=SharedGateway(RAW,authenticate=lambda q,w,e:True);q=h.register([0,0,2],'x','x1',origin='EXTERNAL');o=h.ingest('x1',payload(q,YES,origin='EXTERNAL',receipt='same'));check(o.status=='ACCEPT' and not o.operational and o.candidate_pending,'mock authority')
    q=h.register([0,0,2],'x','x2',origin='EXTERNAL');before=h.export();o=h.ingest('x2',payload(q,YES,origin='EXTERNAL',receipt='same'));after=h.export();check(o.status=='UNKNOWN' and after['records'][:-1]==before['records'] and after['records'][-1]['payload']['receipt_digest'] is None,'receipt reuse rollback');verify(h)
    # Actual raw rollback and false EXHAUSTED metadata still producer-accepted.
    k=SharedGateway(RAW);c=component_closure(k.sample);bad=copy.deepcopy(c['records'][1]);bad['payload']['epoch']=99;before=k.export();check(not k.append_raw([c['records'][0],bad]) and k.export()==before,'raw atomic rollback');check(k.append_raw(c['records']),'valid raw replay');verify(k)
    k=SharedGateway(RAW);c=component_closure(k.sample,Budget(work=0));c['records'][0]['payload'].update(state='EXHAUSTED',cursor=None);check(k.append_raw(c['records']),'false exhaustion behavior changed');reject(lambda:verify(k))
    # Shared lock serializes actual duplicate deliveries.
    k=SharedGateway(RAW);q=k.register([0,1,2],'concurrent','same');wire=payload(q)
    with ThreadPoolExecutor(max_workers=8) as pool:outcomes=list(pool.map(lambda _:k.ingest('same',wire),range(16)))
    check(sum(o.committed for o in outcomes)==1 and sum(o.status=='UNKNOWN' for o in outcomes)==15,'concurrent replay');verify(k)
    print('latest_gateway_global_reuse=REJECTED origin_rebind=REJECTED duplicate_receipt=UNKNOWN_ONLY raw_atomic_rollback=PASS invalid_response_rollback=4 unknown_retry=PASS concurrent_deliveries=16 committed=1')
    print('latest_gateway_false_exhaustion=CORE_ACCEPTED_INDEPENDENT_REJECTED sidecar_authentication=NOT_ESTABLISHED operational_status=INCOMPLETE')


if __name__=='__main__':main(*(Path(x).resolve() for x in sys.argv[1:]))

"""Independent audit of actual delegated journal/2 gateway outputs.
Usage: python audit_interface_j2.py CORE_DIR INTERFACE_DIR OUTPUT_DIR
"""
import copy,hmac,json,sys
from pathlib import Path
from audit_journal_v2 import event
from roundtrip_p21 import check,check_blobs,CORE_BLOBS,INTERFACE_BLOBS
from interface_artifact_replay import canonical,sha
from journal_v2_replay import verify_journal


def main(core,interface,out):
    check_blobs(core/'selector_v2',{**CORE_BLOBS,'registered_ledger.py':'092507fc156e604be242e3100117fedc27b96d04'})
    check_blobs(interface,{**INTERFACE_BLOBS,'gateway.py':'8b314e11c0d935122779365b08666c482697621f','test_adapter.py':'bfa7dee3373da7d267c373e238b95d271a8a2669'})
    sys.path[:0]=[str(core),str(interface)]
    from gateway import open_gateway
    from selector_v2.registered_ledger import RegisteredLedger
    from selector_v2.core import Sample,PartitionRef
    from selector_v2.component_closure import component_closure,structural_record
    from selector_v2.schema import scope
    from test_adapter import RAW,NO,YES
    out.mkdir(parents=True,exist_ok=True);s=Sample.from_input(RAW);sc=scope(s)
    tags=set()
    def tag(q,w,e):return hmac.digest(b'audit-fixture-only',q+b'\0'+w+b'\0'+e,'sha256')
    def auth(q,w,e):return tag(q,w,e) in tags
    g=open_gateway(RAW,authenticate=auth);check(type(g) is RegisteredLedger,'not exact authoritative ledger')
    c=component_closure(s);g.append_raw(c['records']+[structural_record(s,PartitionRef(tuple(c['owner'])))])
    def reg(aid,rid='r',owner=None,**kw):return g.register([0,1,2] if owner is None else owner,rid,aid,**kw)
    def response(q,template=NO,**kw):p=copy.deepcopy(template);p.update(request=q,**kw);return p
    def verify(g):
        a=verify_journal(RAW,sc,g.export(),expected_records=json.loads(g.export_records()));check(a['status']=='VERIFIED',a);r=a['result'];check(r['pending_candidates']==g.pending_candidates,'candidate state');return r
    def obs(rid,aid,w,expected):check(g.ingest(rid,aid,w)==expected,(aid,expected));verify(g)
    q=reg('unknown');obs('wrong','unknown',b'bad','UNKNOWN');check(g.attempt_status('r','unknown')=='PENDING','wrong request closed')
    obs('r','unknown',None,'UNKNOWN');obs('r','unknown',canonical(response(q)),'UNKNOWN')
    q=reg('retry');obs('r','retry',json.dumps(response(q),ensure_ascii=False,indent=2).encode(),'PROJECTION_NO')
    q=reg('bounded','b',[0,0,2],capacities=[1,1]);p=response(q);del p['failed'],p['tables'];p.update(status='BOUNDED_NO',exact=True);obs('b','bounded',canonical(p),'BOUNDED_NO')
    q=reg('sim','sim',[0,0,2]);obs('sim','sim',canonical(response(q,YES)),'ACCEPT')
    maps=dict(positive_map=[['p',0],['epsilon',1]],negative_map=[['n',0],['dup',1],['long',2]])
    for i,mode in enumerate(('valid','reuse','whitespace','wrong-map','unsigned')):
        aid='ext-'+str(i);q=reg(aid,'external',[0,0,2],origin='EXTERNAL',**maps);p=response(q,YES,origin='EXTERNAL',receipt='receipt' if i<2 else 'receipt-'+aid)
        entry=event(json.loads(g.export()),'REGISTER',aid)['registered'];wire=canonical(p)
        if mode=='wrong-map':entry['maps']['negative']=None
        if mode!='unsigned':tags.add(tag(canonical(q),wire,canonical(entry)))
        if mode=='whitespace':wire=json.dumps(p,indent=2).encode()
        obs('external',aid,wire,'ACCEPT' if mode=='valid' else 'UNKNOWN')
        check(g.original_id('external',aid,'negative','dup')==1,'original map')
    q=reg('unanswered','pending');r=verify(g)
    check(r['proof']['structural_optimum']==1 and r['proof']['operational_status']=='INCOMPLETE','structural status')
    check(r['attempt_status']['unanswered']=='PENDING' and len(r['proof']['structural_no_request_digests'])==1,'pending/no')
    data=dict(raw=RAW,scope=sc,journal=json.loads(g.export()),records=json.loads(g.export_records()))
    b=canonical(data);(out/'delegated-journal-v2.json').write_bytes(b)
    print('actual_delegated_export events=',len(g.journal),'records=',len(g.records),'quarantines=',r['quarantine'],'attempts=',len(r['attempt_status']),'optimum=',r['proof']['structural_optimum'],'operational=',r['proof']['operational_status'])
    print('delegated-journal-v2.json',len(b),sha(b))
    print('attempt_status=',r['attempt_status'],'pending_candidates=',r['pending_candidates'])
    print('exact_authority=PASS mock_auth_binding=PASS reuse=UNKNOWN whitespace=UNKNOWN wrong_map=UNKNOWN unsigned=UNKNOWN')

if __name__=='__main__':main(*(Path(p).resolve() for p in sys.argv[1:]))

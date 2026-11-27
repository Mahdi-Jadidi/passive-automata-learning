"""Generate the actual pinned /2 producer exports and independently replay them.
Usage: python audit_journal_v2.py CORE_DIR INTERFACE_DIR OUT_DIR
No import of producer audit_journal.py or validation internals in proof kernel.
Synthetic service inputs reproduce the published producer test call sequences.
"""
import copy,json,sys
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
from journal_v2_replay import verify_journal,replay_journal,NO_RESPONSE_DIGEST
from interface_artifact_replay import canonical,sha
from bounded_deletion import DeletionBudget
from roundtrip_p21 import check,check_blobs,CORE_BLOBS,INTERFACE_BLOBS

CORE_HASHES={'roundtrip-v2.json':'14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8','adversarial-v2.json':'1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c'}
RAW={'alphabet':['β','a','😀','unused'],'positive':[['β','a'],['😀'],['β','a'],[]],'negative':[['a','β'],['β','a','😀'],['β','a','😀'],['β','β'],['β','β']]}


def response(q,status,receipt,origin='SIMULATOR',**kw):
    return dict(version=q['version'],request=q,origin=origin,status=status,complete=True,receipt=receipt,**kw)


def tables(raw,q,failed):
    ids={a:i for i,a in enumerate(raw['alphabet'])}; X=[[ids[a] for a in w] for w in raw['positive']]; Y=[[ids[a] for a in w] for w in raw['negative']]
    p=q['owner'];out=[]
    for g in sorted(set(p)):
        proj=lambda w:tuple(a for a in w if p[a]==g)
        pp=[proj(x) for x in X];zeros=[];free={}
        for i,y in enumerate(Y):
            w=proj(y)
            if w in pp:zeros.append(dict(negative=i,positive=pp.index(w) if i==failed else None))
            else:free.setdefault(w,[]).append(i)
        out.append(dict(block=g,kind='UNRESTRICTED_BASE',complete=True,zeros=zeros,free=list(free.values())))
    return out


def trie_dfa(raw):
    alphabet=raw['alphabet'];ids={a:i for i,a in enumerate(alphabet)};X=[[ids[a] for a in w] for w in raw['positive']];paths={():0}
    for x in X:
        for k in range(1,len(x)+1):
            prefix=tuple(x[:k]);paths.setdefault(prefix,len(paths))
    sink=len(paths)
    return dict(block=0,states=sink+1,initial=0,accepting=sorted({paths[tuple(x)] for x in X}),transitions=[[state,a,paths.get(prefix+(a,),sink)] for prefix,state in paths.items() for a in range(len(alphabet))]+[[sink,a,sink] for a in range(len(alphabet))])


def event(j,kind,aid=None):
    return next(e for e in j['events'] if e['event']==kind and (aid is None or (e.get('attempt_id') or e.get('registered',{}).get('request',{}).get('attempt_id'))==aid))


def main(core,interface,out):
    check_blobs(core/'selector_v2',{**CORE_BLOBS,'registered_ledger.py':'092507fc156e604be242e3100117fedc27b96d04'});check_blobs(interface,INTERFACE_BLOBS)
    sys.path[:0]=[str(core),str(interface)]
    import adapter
    from strict_ledger import parse
    from selector_v2.core import Sample,PartitionRef,Budget
    from selector_v2.schema import scope,raw_record
    from selector_v2.component_closure import component_closure,structural_record
    from selector_v2.registered_ledger import RegisteredLedger
    out.mkdir(parents=True,exist_ok=True);s=Sample.from_input(RAW);sc=scope(s);owner=[0,1,2,3];merged=[0,0,0,0]
    maps=dict(positive_map=[['p'+str(i),i] for i in range(4)],negative_map=[['n'+str(i),i] for i in range(5)])
    def make(auth=lambda q,p,r:True):
        l=RegisteredLedger(RAW,adapter=adapter,parse=parse,authenticate=auth)
        c=component_closure(s);l.append_raw(c['records']+[structural_record(s,PartitionRef(tuple(c['owner'])))])
        return l
    def replay(l):
        r=verify_journal(RAW,sc,l.export(),expected_records=json.loads(l.export_records()));check(r['status']=='VERIFIED',r);check(r['result']['pending_candidates']==l.pending_candidates,'pending candidate mismatch');return r['result']
    l=make();q=l.register(owner,'root','a1',**maps);data=response(q,'PROJECTION_NO','sim1',failed=0,tables=tables(RAW,q,0));check(l.ingest('root','a1',json.dumps(data,ensure_ascii=False,indent=2).encode())=='PROJECTION_NO','projection')
    q=l.register(owner,'bounded','a2',capacities=[1,1,1,1]);check(l.ingest('bounded','a2',canonical(response(q,'BOUNDED_NO','sim2',exact=True)))=='BOUNDED_NO','bounded')
    q=l.register(merged,'accept','a3',origin='EXTERNAL');check(l.ingest('accept','a3',canonical(response(q,'ACCEPT','mock-external',origin='EXTERNAL',dfas=[trie_dfa(RAW)])))=='ACCEPT','mock ext')
    q=l.register(merged,'simaccept','a4');check(l.ingest('simaccept','a4',canonical(response(q,'ACCEPT','sim4',dfas=[trie_dfa(RAW)])))=='ACCEPT','sim accept')
    r=replay(l);roundtrip=dict(raw=RAW,scope=sc,journal=json.loads(l.export()),records=json.loads(l.export_records()),proof=r['proof']);check(r['proof']['structural_optimum']==2,'optimum')
    print('roundtrip events=',len(l.journal),'records=',len(r['records']),'optimum=',r['proof']['structural_optimum'],'operational=',r['proof']['operational_status'])
    l=make();q=l.register(owner,'r','a',origin='EXTERNAL',**maps);l.ingest('r','a',b'{"status":1,"status":2}')
    q=l.register(owner,'r','b',origin='EXTERNAL',**maps);p=response(q,'PROJECTION_NO','r1',origin='EXTERNAL',failed=0,tables=tables(RAW,q,0));l.ingest('r','b',canonical(p));l.ingest('r','b',canonical(p))
    q=l.register(owner,'bounded','c',capacities=[1,1,1,1]);l.ingest('bounded','c',canonical(response(q,'BOUNDED_NO','r2',exact=True)))
    q=l.register(merged,'accept','d',origin='EXTERNAL');l.ingest('accept','d',canonical(response(q,'ACCEPT','r3',origin='EXTERNAL',dfas=[trie_dfa(RAW)])))
    l.register(owner,'pending','e');l.ingest('wrong','e',None);r=replay(l);adversarial=dict(raw=RAW,scope=sc,journal=json.loads(l.export()),result=r)
    check(r['attempt_status']=={'a':'UNKNOWN','b':'PROJECTION_NO','c':'BOUNDED_NO','d':'ACCEPT','e':'PENDING'},'attempt lifecycle')
    print('adversarial events=',len(l.journal),'records=',len(r['records']),'quarantine=',r['quarantine'],'states=',r['attempt_status'],'operational=',r['proof']['operational_status'])
    for name,data in [('roundtrip-v2.json',roundtrip),('adversarial-v2.json',adversarial)]:
        body=canonical(data);(out/name).write_bytes(body);h=sha(body);print(name,len(body),h,'published_digest_match=',h==CORE_HASHES[name])
    # Actual artifacts, including coherent byte rehash attacks.
    original=adversarial['journal'];mutants=[]
    def mutation(fn):
        z=copy.deepcopy(original);fn(z);mutants.append(z)
    def rewrite(e,fn,wire=True):
        obj=json.loads(bytes.fromhex(e['normalized_hex']));fn(obj);b=canonical(obj);e.update(normalized_hex=b.hex(),normalized_sha256=sha(b))
        if wire:
            b=canonical(obj['payload']);e.update(wire_hex=b.hex(),wire_sha256=sha(b));e['records'][0]['payload']['response_digest']=sha(b)
    def receipt_reuse(z):
        e=event(z,'OBSERVE','d');rewrite(e,lambda o:o['payload'].update(receipt='r1'));e['receipt_ref']=sha(b'r1');e['records'][0]['payload']['receipt_digest']=sha(b'r1')
    def attempt_reuse(z):
        e=event(z,'REGISTER','e');e['registered']['request']['attempt_id']='a';e['records'][0]['payload']['attempt_id']='a'
    def remap(z):
        m=event(z,'REGISTER','b')['registered']['maps']['positive'];m['p0'],m['p1']=m['p1'],m['p0']
    for fn in [lambda z:z.update(version='selector-v2-journal/1'),lambda z:z.update(sample_digest='0'*64),lambda z:event(z,'REGISTER','b')['registered'].update(origin='SIMULATOR'),lambda z:event(z,'REGISTER','a')['registered']['maps']['positive'].update(p0=True),remap,lambda z:event(z,'REGISTER','c')['registered']['capacities'].__setitem__(0,2),attempt_reuse,lambda z:event(z,'OBSERVE','b').update(wire_sha256='0'*64),lambda z:event(z,'OBSERVE','b').update(normalized_sha256='0'*64),lambda z:rewrite(event(z,'OBSERVE','b'),lambda o:o.update(operational=True)),lambda z:rewrite(event(z,'OBSERVE','b'),lambda o:o['payload'].update(receipt='changed'),False),lambda z:event(z,'OBSERVE','b')['records'][0]['payload'].update(receipt_digest='0'*64),lambda z:event(z,'OBSERVE','b')['records'][0]['payload']['feedback'].update(tables=[]),receipt_reuse,lambda z:rewrite(event(z,'OBSERVE','d'),lambda o:o['payload']['dfas'][0]['transitions'].pop()),lambda z:event(z,'QUARANTINE','a')['records'].clear(),lambda z:event(z,'QUARANTINE','e')['records'].append(event(z,'QUARANTINE','a')['records'][0]),lambda z:event(z,'OBSERVE','b').update(request_id='wrong'),lambda z:event(z,'RAW')['records'].append(event(z,'REGISTER','a')['records'][0]),lambda z:next(r for r in event(z,'RAW')['records'] if r['kind']=='COMPONENT_EPOCH' and not r['payload']['edges'])['payload']['facts'].pop(),lambda z:event(z,'OBSERVE','b').update(status='ACCEPT'),lambda z:z['events'].append(event(z,'OBSERVE','b'))]:mutation(fn)
    for i,z in enumerate(mutants):
        a=verify_journal(RAW,sc,canonical(z));check(a['status']=='INVALID' and 'result' not in a,(i,a))
    check(verify_journal(RAW,sc,b'{"version":1,"version":2}')['status']=='INVALID','duplicate key')
    check(verify_journal(RAW,sc,canonical(original),expected_records=[])['status']=='INVALID','projection mismatch')
    for b in (DeletionBudget(work=0),DeletionBudget(entries=0),DeletionBudget(word_length=0),DeletionBudget(seconds=0)):
        a=verify_journal(RAW,sc,canonical(original),deletion_budget=b);check(a['status']=='INCOMPLETE' and 'result' not in a,'resource boundary')
    print('outer_mutants_rejected=',len(mutants)+2,'resource_censored=',4)
    # Atomic transaction, pending candidate and reentrant callback on actual core.
    l=make();q=l.register(owner,'r','x',origin='EXTERNAL',**maps);before=l.export()
    for fn in [lambda:l.register(owner,'other','x'),lambda:l.register(owner,'r','y',origin='SIMULATOR',**maps),lambda:l.append_raw([raw_record(s,'REQUEST',q)])]:
        try:fn()
        except ValueError:pass
        else:raise RuntimeError('invalid registration accepted')
        check(l.export()==before,'registration rollback')
    check(l.ingest('wrong','x',None)=='UNKNOWN' and l.attempt_status('r','x')=='PENDING','wrong attempt closed')
    check(l.ingest('r','x',None)=='UNKNOWN' and l.attempt_status('r','x')=='UNKNOWN','timeout')
    q=l.register(owner,'r','y',origin='EXTERNAL',**maps);p=response(q,'PROJECTION_NO','ext',origin='EXTERNAL',failed=0,tables=tables(RAW,q,0));check(l.ingest('r','y',canonical(p))=='PROJECTION_NO','retry')
    q=l.register(owner,'r','z',origin='EXTERNAL',**maps);p['request']=q;check(l.ingest('r','z',canonical(p))=='UNKNOWN','receipt reuse');replay(l)
    l=RegisteredLedger(RAW,adapter=adapter,parse=parse);good=component_closure(s)['records'];bad=copy.deepcopy(good);bad[-1]['payload']['result_owner']=owner;before=l.export()
    try:l.append_raw(bad)
    except ValueError:pass
    else:raise RuntimeError('invalid batch accepted')
    check(l.export()==before,'raw rollback');l.append_raw(good);replay(l)
    l=RegisteredLedger(RAW,adapter=adapter,parse=parse);bad=component_closure(s,Budget(work=0))['records'];bad[0]['payload'].update(state='EXHAUSTED',cursor=None);l.append_raw(bad);check(verify_journal(RAW,sc,l.export())['status']=='INVALID','false exhaustion')
    l=RegisteredLedger(RAW,adapter=adapter,parse=parse)
    def task(i):
        try:l.register(owner,str(i),'single');return 1
        except ValueError:return 0
    with ThreadPoolExecutor(max_workers=8) as pool:check(sum(pool.map(task,range(16)))==1,'concurrent attempt reuse')
    replay(l)
    print('actual_atomic_rollback=PASS global_reuse=REJECTED wrong_attempt=PENDING unknown_retry=PASS receipt_reuse=UNKNOWN false_exhaustion=INVALID concurrent_registrations=1/16')

if __name__=='__main__':main(*(Path(p).resolve() for p in sys.argv[1:]))

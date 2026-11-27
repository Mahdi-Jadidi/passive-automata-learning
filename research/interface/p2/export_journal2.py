"""Generate actual journal/2 interchange through the delegated interface."""
import gzip
import json
import sys
from pathlib import Path
from adapter import canonical, need
from gateway import open_gateway
from test_gateway_v2 import SignedFixture, response, reg, events, sha
from test_adapter import RAW, YES
from selector_v2.core import Sample, PartitionRef
from selector_v2.component_closure import component_closure, structural_record
from selector_v2.schema import scope


def produce(raw, exercise):
    f = SignedFixture(); g = open_gateway(raw, authenticate=f.auth)
    s = Sample.from_input(raw); c = component_closure(s)
    g.append_raw(c['records']+[structural_record(s,PartitionRef(tuple(c['owner'])))])
    if exercise:
        q=reg(g,'a'); need(g.ingest('r','a',None)=='UNKNOWN','timeout')
        q=reg(g,'b'); need(g.ingest('r','b',json.dumps(response(q),indent=2).encode())=='PROJECTION_NO','table')
        q=reg(g,'c','bounded',[0,0,2],capacities=[1,1]); p=response(q)
        del p['failed'],p['tables']; p.update(status='BOUNDED_NO',exact=True)
        need(g.ingest('bounded','c',canonical(p))=='BOUNDED_NO','bounded')
        q=reg(g,'d','sim',[0,0,2]); need(g.ingest('sim','d',canonical(response(q,YES)))=='ACCEPT','simulator')
        maps=dict(positive_map=[['p',0],['epsilon',1]],negative_map=[['n',0],['dup',1],['long',2]])
        for aid, expected in [('e','ACCEPT'),('f','UNKNOWN')]:
            q=reg(g,aid,'ext',[0,0,2],origin='EXTERNAL',**maps)
            p=response(q,YES,origin='EXTERNAL',receipt='mock-receipt')
            need(g.ingest('ext',aid,f.sign(g,q,p))==expected,'receipt reuse')
        q=reg(g,'g','ext',[0,0,2],origin='EXTERNAL',**maps)
        p=response(q,YES,origin='EXTERNAL',receipt='mock-new'); f.sign(g,q,p)
        need(g.ingest('ext','g',json.dumps(p,indent=2).encode())=='UNKNOWN','exact bytes')
        q=reg(g,'h','pending',[0,0,2]); need(g.ingest('wrong','h',b'bad')=='UNKNOWN','wrong request')
        need(g.attempt_status('pending','h')=='PENDING','wrong attempt closed')
        need(g.ingest('r','b',b'late')=='UNKNOWN','late response')
    journal=json.loads(g.export()); records=json.loads(g.export_records())
    need(journal['version']=='selector-v2-journal/2','version')
    need(records==[r for e in journal['events'] for r in e['records']],'projection')
    return dict(raw=raw,scope=scope(s),journal=journal,records=records)


def main(directory):
    out=Path(directory); out.mkdir(parents=True,exist_ok=True)
    multi={'alphabet':['a','b','c'],'positive':[['a','b'],['c']],'negative':[['b','a'],['a','b','c']]}
    for name,case in [('interface-journal2',produce(RAW,True)),('interface-journal2-epochs',produce(multi,False))]:
        body=canonical(case); (out/(name+'.json')).write_bytes(body)
        compressed=gzip.compress(body,mtime=0); (out/(name+'.json.gz')).write_bytes(compressed)
        es=case['journal']['events']
        print(name, 'bytes',len(body),'sha256',sha(body),'gzip_bytes',len(compressed),'gzip_sha256',sha(compressed),'events',len(es),'records',len(case['records']))
        print('events', [e['event']+(':'+e['status'] if e['event']=='OBSERVE' else '') for e in es])


if __name__=='__main__': main(sys.argv[1])

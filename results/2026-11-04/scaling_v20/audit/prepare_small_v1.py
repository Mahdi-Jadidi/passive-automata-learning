"""Reuse C018 exact references and add tiny C1-specific cases; no solver imports."""
import json,hashlib
from pathlib import Path
from oracle_data_v1 import full_family
A=Path(__file__).resolve().parent;OLD=A.parents[1]/'synthetic_gate_v18/audit'
def save(p,value):
    p.parent.mkdir(exist_ok=True,parents=True)
    with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert json.loads((A/'FIXTURE_AUDIT_V1.json').read_text())['status']=='accepted'
    manifest=json.loads((OLD/'CASE_MANIFEST_V1.json').read_text());jobs=manifest['jobs'];assert len(jobs)==1695;oracles={o['job_id']:o for o in json.loads((OLD/'ORACLES_V1.json').read_text())['jobs']}
    for j in jobs:assert sha(Path(j['input']))==j['input_sha256']
    cases=[('same_parikh_nonedge',list('abc'),['abc'],['cba']),('duplicate_edge',list('ab'),['ab','ab'],['ba','ba']),('full_vector_not_unary',list('ab'),['ab','aabb'],['aab']),('unicode_exact',list('😀é\u0301\x00'),['😀é\u0301\x00'],['é😀\u0301\x00']),('envelope_extension',list('abc'),['aaccbb'],['ccaabb'])]
    for name,alpha,P,N in cases:
        data=dict(alphabet=alpha,positive=P,negative=N);path=A/'small_added'/f'{name}.json';save(path,data);family=full_family(data)
        for k in [None,2,len(alpha)]:
            jid='c020_'+name+('_unknown' if k is None else '_K'+str(k));selected=[r for r in family if k is None or max(r)+1==k];jobs.append(dict(job_id=jid,case_id=name,input=str(path),input_sha256=sha(path),allowed_k=None if k is None else [k],expectation='unique' if len(selected)==1 else 'ambiguous' if selected else 'incompatible'));oracles[jid]=dict(job_id=jid,compatible_rgs=selected,count=len(selected))
    # Remove duplicate K2 job when m2, retaining deterministic order.
    jobs=list({j['job_id']:j for j in jobs}.values())
    fixtures=json.loads((A/'FIXTURE_MANIFEST_V1.json').read_text());audit=json.loads((A/'FIXTURE_AUDIT_V1.json').read_text());D=next(x for x in fixtures['inputs'] if x['case_id']=='D');oracle=next(x for x in audit['fixtures'] if x['case_id']=='D')['oracle']['families_by_k']
    for k in [None,4]:
        family=[r for q,rs in oracle.items() if k is None or int(q)==k for r in rs];jid='c020_D'+('_unknown' if k is None else '_K4');jobs.append(dict(job_id=jid,case_id='D',input=D['input'],input_sha256=D['input_sha256'],allowed_k=None if k is None else [k],expectation='unique' if len(family)==1 else 'ambiguous'));oracles[jid]=dict(job_id=jid,compatible_rgs=family,count=len(family))
    save(A/'SMALL_MANIFEST_V1.json',dict(jobs=jobs,held_jobs=1695,added_jobs=len(jobs)-1695));save(A/'SMALL_ORACLES_V1.json',dict(jobs=list(oracles.values())));print(json.dumps(dict(status='prepared',jobs=len(jobs))))
if __name__=='__main__':main()

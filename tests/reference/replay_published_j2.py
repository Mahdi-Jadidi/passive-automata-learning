"""Independent replay of four exact published gzip journal/2 artifacts.
Usage: python replay_published_j2.py CORE_ARTIFACT_DIR INTERFACE_ARTIFACT_DIR
No producer imports. For reproducible regeneration see audit_journal_v2.py and
interface exporter 18d0fab. This script refuses any digest mismatch.
"""
import copy,gzip,hashlib,json,sys
from pathlib import Path
from interface_artifact_replay import canonical,sha
from journal_v2_replay import verify_journal
from bounded_deletion import DeletionBudget

ARTIFACTS=[
('roundtrip-v2.json.gz','eedb6c2fb7ad29346f91230dfc7db1df46eff716','14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8',2,12),
('adversarial-v2.json.gz','1f1444631ba3e1b12f95ae8ba4e362f93d5b8246','1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c',2,13),
('interface-journal2.json.gz','a61d493991c7464641c6d182929ba8c185f57421','caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94',1,18),
('interface-journal2-epochs.json.gz','6efdc4356b79e4368e17c59b6376d50861762c12','adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491',2,4)]


def need(ok,message):
    if not ok:raise RuntimeError(message)


def main(core,interface):
    for i,(name,blob,digest,cost,count) in enumerate(ARTIFACTS):
        z=((core if i<2 else interface)/name).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(z)).encode()+b'\0'+z).hexdigest();need(actual==blob,'gzip Git blob mismatch '+name)
        b=gzip.decompress(z);need(sha(b)==digest,'JSON digest mismatch '+name)
        a=json.loads(b);expected=a.get('records',a.get('result',{}).get('records'))
        budget=DeletionBudget()
        r=verify_journal(a['raw'],a['scope'],canonical(a['journal']),expected_records=expected,deletion_budget=budget)
        need(r['status']=='VERIFIED',r);p=r['result'];proof=p['proof'];need(len(p['records'])==count and proof['structural_optimum']==cost and proof['closure_state']=='FIXPOINT' and proof['operational_status']=='INCOMPLETE','unexpected structural result')
        if 'proof' in a:need(canonical(a['proof'])==canonical(proof),'reported core proof mismatch')
        if 'result' in a:need(canonical(a['result'])==canonical(p),'reported core result mismatch')
        print(name,'blob',actual,'sha256',digest,'events',len(a['journal']['events']),'records',count,'structural_cost',cost,'attempts',p['attempt_status'],'quarantine',p['quarantine'],'pending_candidates',p['pending_candidates'],'operational',proof['operational_status'],'deletion_work',budget.used,'peak_index_entries',budget.peak_entries,'exact_checks',budget.exact_checks)
        if i==2:
            # Attack the actual interface export, not an invented substitute.
            original=a['journal']
            def at(z,kind,aid):return next(e for e in z['events'] if e['event']==kind and (e.get('attempt_id') or e.get('registered',{}).get('request',{}).get('attempt_id'))==aid)
            def changed(z):
                e=at(z,'OBSERVE','e');normal=json.loads(bytes.fromhex(e['normalized_hex']));normal['payload']['dfas'][0]['initial']=True
                n=canonical(normal);w=canonical(normal['payload']);e.update(normalized_hex=n.hex(),normalized_sha256=sha(n),wire_hex=w.hex(),wire_sha256=sha(w));e['records'][0]['payload']['response_digest']=sha(w)
            mutants=[lambda z:at(z,'REGISTER','e')['registered']['maps']['negative'].update(dup=False),lambda z:at(z,'REGISTER','f')['registered'].update(origin='SIMULATOR'),lambda z:at(z,'OBSERVE','b')['records'][0]['payload']['feedback']['tables'][0]['anonymous_zeros'].clear(),lambda z:at(z,'QUARANTINE','a')['records'].clear(),lambda z:at(z,'QUARANTINE','h')['records'].append(at(z,'QUARANTINE','a')['records'][0]),lambda z:at(z,'OBSERVE','e').update(receipt_ref='0'*64),changed]
            for mutate in mutants:
                z=copy.deepcopy(original);mutate(z);bad=verify_journal(a['raw'],a['scope'],canonical(z));need(bad['status']=='INVALID' and 'result' not in bad,'interface mutation accepted')
            print('published_interface_mutations_rejected='+str(len(mutants)))
    print('published_artifacts_verified=4')

if __name__=='__main__':main(*(Path(p).resolve() for p in sys.argv[1:]))

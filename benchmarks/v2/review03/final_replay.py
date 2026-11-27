"""Replay exact journal/2 artifacts with the independently authored bounded kernel."""
import argparse,hashlib,json,resource,sys,time
from pathlib import Path
BLOBS={'independent_replay.py':'aa09243fa7ccc941c37609e959aefb419075df32','production_replay.py':'4666c3f1aca6189331a83ff2f00de0e376e2a710','ledger_replay.py':'0b615b6c17258e621d73147baa262d791985d8d0','bounded_deletion.py':'64eda7d13b3153175f09b70e41be66e1615846b2','interface_artifact_replay.py':'51f928ee2311ab8995f88f0e9f195ac7c659e469','journal_v2_replay.py':'6c49013e809b5ac4d2b2a37850e6e6cece513072'}
PIN='e8895a344821f7cd463823774e6bc591e064264c'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('artifact',type=Path);p.add_argument('--proof',type=Path,required=True);p.add_argument('--memory',type=int,default=1536);p.add_argument('--seconds',type=float,default=30);p.add_argument('--work',type=int,default=200_000_000);p.add_argument('--entries',type=int,default=2_000_000);p.add_argument('--word-length',type=int,default=2_000_000);a=p.parse_args()
    for name,expected in BLOBS.items():
        b=(a.proof/name).read_bytes()
        if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=expected: raise ValueError('wrong proof blob '+name)
    resource.setrlimit(resource.RLIMIT_AS,(a.memory*2**20,)*2);sys.path.insert(0,str(a.proof.resolve()))
    from journal_v2_replay import verify_journal
    from bounded_deletion import DeletionBudget
    from interface_artifact_replay import canonical
    t=time.perf_counter(); budget=DeletionBudget(work=a.work,entries=a.entries,word_length=a.word_length,seconds=a.seconds)
    try:
        if a.artifact.is_dir():
            raw=json.loads((a.artifact/'input.json').read_bytes());sc=json.loads((a.artifact/'scope.json').read_bytes());journal=(a.artifact/'journal.json').read_bytes();expected=json.loads((a.artifact/'records.json').read_bytes())
        else:
            obj=json.loads(a.artifact.read_bytes());raw=obj['raw'];sc=obj['scope'];journal=canonical(obj['journal']);expected=obj.get('records',obj.get('result',{}).get('records'))
        result=verify_journal(raw,sc,journal,expected_records=expected,deletion_budget=budget)
    except MemoryError:
        result={'status':'INCOMPLETE','reason':'MemoryError before verifier return','operational_status':'INCOMPLETE'}
    if any(k.startswith('selector_v2') or k in ('adapter','audit_journal') for k in sys.modules): raise RuntimeError('producer import')
    if result['operational_status']!='INCOMPLETE': raise RuntimeError('invalid operational status')
    if result['status']!='VERIFIED' and 'result' in result: raise RuntimeError('failed verifier exposed proof')
    out=dict(proof_pin=PIN,artifact=a.artifact.name,memory_as_mib=a.memory,seconds=a.seconds,work_cap=a.work,entry_cap=a.entries,word_length_cap=a.word_length,status=result['status'],reason=result.get('reason'),operational_status='INCOMPLETE',elapsed_s=time.perf_counter()-t,rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,work=budget.used,peak_entries=budget.peak_entries,exact_checks=budget.exact_checks)
    if result['status']=='VERIFIED':
        q=result['result'];pr=q['proof'];out.update({k:pr[k] for k in ('mandatory_floor','structural_optimum','closure_state')});out.update(records=len(q['records']),quarantine=q['quarantine'],attempt_status=q['attempt_status'],pending_candidates=q['pending_candidates'])
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

"""Exact maximum-device optimizer; no partition enumeration or model blocking."""
from pathlib import Path
import sys,threading
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-11-14/sat_candidate_v37/vendor'))
from pysat.solvers import Solver
import encoding as E
from verify import verify_optimal
def response(status,blocks=None,k=None,certificate=None):
    return {'status':status,'blocks':blocks,'max_devices':k,'certificate':certificate}
def call(clauses,tick,proof=False):
    tick()
    with Solver(name='g3',bootstrap_with=clauses,with_proof=proof) as s:
        remaining=tick.remaining(); timer=None
        if remaining is not None:
            timer=threading.Timer(remaining,s.interrupt);timer.daemon=True;timer.start()
        try:
            ok=s.solve_limited(expect_interrupt=True)
            tick()
            if ok is None:raise E.Exhausted()
            return (s.get_model(),None) if ok else (None,s.get_proof() if proof else None)
        finally:
            if timer is not None:timer.cancel();timer.join()
def decode(a,enc,model):
    positive=set(x for x in model if x>0);parent=list(range(enc['q']))
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    for (i,j),v in enc['pairs'].items():
        if v in positive:parent[find(j)]=find(i)
    groups={}
    for i,group in enumerate(enc['groups']):groups.setdefault(find(i),[]).extend(group)
    return [[a[i] for i in sorted(b)] for b in sorted(groups.values(),key=lambda b:min(b))]
def solve_optimal(instance,limits=None):
    try:
        tick=E.budget(limits);a,p,n=E.normalize(instance);tick()
        if set(p)&set(n) or (not a and n):return response('INFEASIBLE',certificate={'type':'direct_infeasible'})
        single=[[x] for x in a]
        if E.feasible(a,p,n,single):return response('OPTIMAL',single,len(a),{'type':'symbol_bound'})
        enc=E.build(a,p,n,tick);q=enc['q']; best=[list(a)];lo=1;hi=q
        while lo<hi:
            t=(lo+hi+1)//2;model,_=call(E.threshold(enc,t),tick)
            if model is None:hi=t-1
            else:
                best=decode(a,enc,model);lo=len(best)
        # Reconstruct if the initial one-block incumbent was retained.
        if len(best)!=lo:
            model,_=call(E.threshold(enc,lo),tick);best=decode(a,enc,model)
        if lo==q: cert={'type':'atom_bound'}
        else:
            model,proof=call(E.threshold(enc,lo+1),tick,True)
            if model is not None:raise RuntimeError('inconsistent upper bound')
            cert={'type':'drup','proof':proof}
        result=response('OPTIMAL',best,lo,cert)
        # No exact claim before completed proof replay. Share remaining budget.
        checked=verify_optimal(instance,result,{'timeout_seconds':tick.remaining()})
        if checked['status']!='ACCEPT':raise E.Exhausted()
        return result
    except E.Invalid:return response('INVALID_INPUT')
    except (E.Exhausted,MemoryError,RecursionError,KeyboardInterrupt):return response('INCOMPLETE')

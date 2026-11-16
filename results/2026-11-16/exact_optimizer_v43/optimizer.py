"""Exact optimizer of |P| for D=(S_plus,S_minus), without state bounds."""
from pathlib import Path
from itertools import combinations
import sys,threading,time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-11-14/sat_candidate_v37/vendor'))
from pysat.solvers import Solver
import encoding as E
from verify import check_drup

def response(status,blocks=None,k=None,certificate=None):
    return {'status':status,'blocks':blocks,'max_devices':k,'certificate':certificate}

def query(solver,tick,assumptions=()):
    tick();timer=None;remaining=tick.remaining()
    if remaining is not None:
        timer=threading.Timer(remaining,solver.interrupt);timer.daemon=True;timer.start()
    try:
        answer=solver.solve_limited(assumptions=list(assumptions),expect_interrupt=True)
        tick()
        if answer is None:raise E.Exhausted()
        return answer
    finally:
        if timer is not None:timer.cancel();timer.join()

def decode(Sigma,enc,model):
    positive=set(x for x in model if x>0);parent=list(range(enc['q']))
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    for (i,j),v in enc['pairs'].items():
        if v in positive:parent[find(j)]=find(i)
    groups={}
    for i,group in enumerate(enc['groups']):groups.setdefault(find(i),[]).extend(group)
    return [[Sigma[i] for i in sorted(B)] for B in sorted(groups.values(),key=min)]

def _solve(D,limits,metrics):
    started=time.perf_counter();prepared=None
    phases={'preprocess':0.,'encoding':0.,'optimization':0.,'proof':0.,'self_check':0.}
    try:
        tick=E.budget(limits);Sigma,S_plus,S_minus=E.normalize(D);tick()
        if set(S_plus)&set(S_minus) or (not Sigma and S_minus):
            return response('INFEASIBLE',certificate={'type':'direct_infeasible'})
        prepared=E.Prepared(Sigma,S_plus,S_minus,tick)
        needed=(1<<len(S_minus))-1;covered=0
        for i in range(len(Sigma)):covered|=prepared.reject_mask(1<<i)
        if covered==needed:return response('OPTIMAL',[[x] for x in Sigma],len(Sigma),{'type':'symbol_bound'})
        groups=prepared.prepare_atoms();covered=0
        for mask in prepared.atom_masks:covered|=prepared.reject_mask(mask)
        if covered==needed:
            return response('OPTIMAL',[[Sigma[i] for i in B] for B in groups],len(groups),{'type':'atom_bound'})
        phases['preprocess']=time.perf_counter()-started
        if len(S_minus)==1:
            # Exact one-obligation theorem: minimum rejecting size d implies
            # optimum q-d+1. No all-witness construction or SAT instance needed.
            now=time.perf_counter();q=len(groups);metrics['route']='single_negative';metrics['atoms']=q
            for size in range(2,q+1):
                for subset in combinations(range(q),size):
                    symbol_mask=0
                    for i in subset:symbol_mask|=prepared.atom_masks[i]
                    if prepared.reject_mask(symbol_mask)&1:
                        merged=sorted(i for atom in subset for i in groups[atom])
                        blocks=[merged]+[B for j,B in enumerate(groups) if j not in subset]
                        partition=[[Sigma[i] for i in B] for B in sorted(blocks,key=min)]
                        phases['optimization']=time.perf_counter()-now
                        tick();return response('OPTIMAL',partition,q-size+1,{'type':'single_negative_bound'})
            raise RuntimeError('no rejecting block for disjoint sample')
        now=time.perf_counter();enc=E.build(Sigma,S_plus,S_minus,tick,prepared)
        phases['encoding']=time.perf_counter()-now
        metrics.update(atoms=enc['q'],minimal_sets=sum(map(len,enc['edges'])),variables=enc['variables'],clauses=len(enc['clauses']),sat_queries=0,proof_queries=0)
        lo=1;hi=enc['upper'];partition=[list(Sigma)]
        now=time.perf_counter()
        if lo<hi:
            # Same base formula and learned clauses survive all threshold calls.
            with Solver(name='g3',bootstrap_with=enc['clauses']) as solver:
                while lo<hi:
                    t=(lo+hi+1)//2;metrics['sat_queries']+=1
                    if query(solver,tick,[enc['thresholds'][t]]):
                        partition=decode(Sigma,enc,solver.get_model());lo=len(partition)
                    else:hi=t-1
        phases['optimization']=time.perf_counter()-now
        if len(partition)!=lo:raise RuntimeError('incumbent mismatch')
        if lo==enc['upper']:certificate={'type':'edge_size_bound'}
        else:
            now=time.perf_counter();metrics['proof_queries']+=1
            # A fresh, assumption-free instance is used for a portable proof.
            with Solver(name='g3',bootstrap_with=E.threshold(enc,lo+1),with_proof=True) as solver:
                if query(solver,tick):raise RuntimeError('inconsistent upper bound')
                proof=solver.get_proof()
            phases['proof']=time.perf_counter()-now
            certificate={'type':'drup','proof':proof}
        now=time.perf_counter()
        if not E.feasible(Sigma,S_plus,S_minus,partition):raise RuntimeError('invalid incumbent')
        if certificate['type']=='drup' and not check_drup(enc,lo,certificate['proof'],tick):
            raise RuntimeError('proof replay failed')
        phases['self_check']=time.perf_counter()-now
        tick();return response('OPTIMAL',partition,lo,certificate)
    except E.Invalid:return response('INVALID_INPUT')
    except (E.Exhausted,MemoryError,RecursionError,KeyboardInterrupt):return response('INCOMPLETE')
    finally:
        metrics['phases_seconds']=phases;metrics['total_seconds']=time.perf_counter()-started
        if not any(phases.values()):phases['preprocess']=metrics['total_seconds']
        if prepared is not None:metrics.update(prepared.stats)

def solve_optimal(D,limits=None):return _solve(D,limits,{})
def solve_profiled(D,limits=None):
    metrics={};result=_solve(D,limits,metrics)
    return {'result':result,'metrics':metrics}

"""V47 outer search with the proved fixed-partition projection teacher."""
from pathlib import Path
import sys
import threading
import time

# Reuse the frozen V45 encoder, projections, normalization and consumer.
V45 = Path(__file__).resolve().parents[2] / '2026-11-16/interactive_teacher_v45'
sys.path.append(str(V45))
from spec import Invalid,Exhausted,budget,normalize,response,mandatory_groups
from projections import ProjectionStore
from projection_teacher import ProjectionTeacher
from master import Master

VENDOR=Path(__file__).resolve().parents[2]/'2026-11-14/sat_candidate_v37/vendor'
sys.path.insert(0,str(VENDOR))
from pysat.solvers import Solver

def query(solver,tick,assumptions=()):
    if any(x is False for x in assumptions):return False
    assumptions=[x for x in assumptions if x is not True]
    tick();timer=None;remaining=tick.remaining()
    if remaining is not None:
        timer=threading.Timer(remaining,solver.interrupt);timer.daemon=True;timer.start()
    try:
        answer=solver.solve_limited(assumptions=list(assumptions),expect_interrupt=True)
        tick()
        if answer is None:raise Exhausted()
        return answer
    finally:
        if timer is not None:timer.cancel();timer.join()

def solve_profiled(D,limits=None):
    metrics={'teacher_calls':0,'cuts':0,'sat_queries':0,'teacher_totals':{},'phase':'validation'}
    start=time.perf_counter();store=None;teacher=None;log=[]
    try:
        tick=budget(limits);a,p,n=normalize(D);tick()
        if set(p)&set(n) or (not a and n):
            return {'result':response('INFEASIBLE',certificate={'type':'direct_infeasible'}),'metrics':metrics,'trace':log}
        if not a:
            return {'result':response('OPTIMAL',[],0,{'type':'symbol_bound'}),'metrics':metrics,'trace':log}
        store=ProjectionStore(a,p,n,tick);teacher=ProjectionTeacher(tick)
        def ask(masks):
            metrics['phase']='projection_teacher';metrics['teacher_calls']+=1;now=time.perf_counter()
            blocks=[tuple(a[j] for j in range(len(a)) if mask>>j&1) for mask in masks]
            images={B:store.entry(mask) for B,mask in zip(blocks,masks)}
            check_started=time.perf_counter()
            try:verdict=teacher.check(blocks,images)
            finally:
                elapsed=time.perf_counter()-now
                metrics['teacher_seconds']=metrics.get('teacher_seconds',0)+elapsed
                metrics['teacher_decision_seconds']=metrics.get('teacher_decision_seconds',0)+time.perf_counter()-check_started
                for key,value in teacher.stats.items():
                    metrics['teacher_totals'][key]=metrics['teacher_totals'].get(key,0)+value
            if verdict['status'] not in ('ACCEPT','REJECT'):raise Exhausted()
            covered=0
            for mask in masks:covered|=store.entry(mask)['rejection_mask']
            actual=covered==(1<<len(n))-1
            if actual!=(verdict['status']=='ACCEPT'):raise RuntimeError('Projection teacher/store coverage disagreement')
            log.append({'partition_masks':masks,'teacher_status':verdict['status'],'seconds':elapsed})
            return actual,covered
        singleton=[1<<j for j in range(len(a))]
        accepted,_=ask(singleton)
        if accepted:
            return {'result':response('OPTIMAL',[[x] for x in a],len(a),{'type':'symbol_bound'}),'metrics':metrics,'trace':log}
        metrics['phase']='mandatory_atoms'
        groups=mandatory_groups(a,n,lambda mask:store.entry(mask)['rejection_mask'],tick)
        atoms=[sum(1<<j for j in B) for B in groups];q=len(atoms);metrics['atoms']=q
        if atoms==singleton:accepted,covered=False,0
        else:accepted,covered=ask(atoms)
        if accepted:
            return {'result':response('OPTIMAL',[[a[j] for j in B] for B in groups],q,{'type':'atom_bound'}),'metrics':metrics,'trace':log}
        metrics['phase']='master';master=Master(q,tick);cuts=[]
        def symbols(atom_mask):
            value=0
            for j,B in enumerate(atoms):
                if atom_mask>>j&1:value|=B
            return value
        def learn(block_masks):
            metrics['phase']='explain_failure'
            covered=0
            for B in block_masks:covered|=store.entry(symbols(B))['rejection_mask']
            i=next(j for j in range(len(n)) if not covered>>j&1)
            regions=[]
            for B in block_masks:
                U=B
                for j in range(q):
                    tick();larger=U|1<<j
                    if not store.entry(symbols(larger))['rejection_mask']>>i&1:U=larger
                regions.append(U)
            regions=sorted(set(regions))
            witnesses=[]
            for U in regions:
                image=store.entry(symbols(U));witnesses.append(image['positive_witness'][image['negative'][i]])
            record={'negative_index':i,'regions':regions,'positive_indices':witnesses}
            if record in cuts:raise RuntimeError('duplicate cut failed to eliminate candidate')
            cuts.append(record);metrics['cuts']=len(cuts)
            log[-1]['cut']=record
            return master.add_cover(regions)
        # The rejected atom partition supplies the first generalized cut.
        initial=learn([1<<j for j in range(q)])
        upper=q
        with Solver(name='g3',bootstrap_with=master.clauses) as solver:
            while True:
                metrics['phase']='master';metrics['sat_queries']+=1
                if query(solver,tick,[master.thresholds[upper]]):
                    candidate=master.decode(solver.get_model());k=len(candidate)
                else:
                    lo=1;hi=upper-1;candidate=[list(range(q))]
                    while lo<hi:
                        t=(lo+hi+1)//2;metrics['sat_queries']+=1
                        if query(solver,tick,[master.thresholds[t]]):
                            candidate=master.decode(solver.get_model());lo=len(candidate)
                        else:hi=t-1
                    k=lo
                upper=k
                amasks=[sum(1<<j for j in B) for B in candidate]
                smasks=[symbols(B) for B in amasks]
                accepted,_=ask(smasks)
                if accepted:break
                clauses=learn(amasks)
                for clause in clauses:solver.add_clause(clause)
        metrics['phase']='proof'
        with Solver(name='g3',bootstrap_with=master.threshold(k+1),with_proof=True) as solver:
            if query(solver,tick):raise RuntimeError('relaxation optimum refutation failed')
            proof=solver.get_proof()
        blocks=[[a[j] for j in range(len(a)) if mask>>j&1] for mask in sorted(smasks,key=lambda m:(m&-m).bit_length())]
        result=response('OPTIMAL',blocks,k,{'type':'teacher_cut_drup','cuts':cuts,'proof':proof})
        metrics['phase']='consumer_self_check'
        from verify import verify_optimal
        checked=verify_optimal(D,result,{'timeout_seconds':tick.remaining()} if tick.remaining() is not None else None)
        if checked['status']=='INCOMPLETE':raise Exhausted()
        if checked['status']!='ACCEPT':raise RuntimeError('consumer self-check failed')
        return {'result':result,'metrics':metrics,'trace':log}
    except Invalid:
        return {'result':response('INVALID_INPUT'),'metrics':metrics,'trace':log}
    except (Exhausted,MemoryError,RecursionError,KeyboardInterrupt):
        metrics['interrupted_phase']=metrics['phase']
        return {'result':response('INCOMPLETE'),'metrics':metrics,'trace':log}
    finally:
        metrics['total_seconds']=time.perf_counter()-start
        if store is not None:metrics['projections']=dict(store.stats)
        if teacher is not None:metrics['projection_teacher']=dict(getattr(teacher,'stats',{}))

def solve_optimal(D,limits=None):return solve_profiled(D,limits)['result']

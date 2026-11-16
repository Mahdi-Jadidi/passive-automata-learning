"""Build a diagnostic fixture requiring at least two outer rejection cuts.

The generator inspects the deterministic master's first proposal; production
still calls the unchanged teacher for every proposal. Not a performance test.
"""
import itertools,json
from pathlib import Path
from optimizer import solve_profiled,Solver
from master import Master
from verify import verify_optimal

def main():
    a=('a','b','c','d');p=a[::-1];y=a
    master=Master(4);master.add_cover([1,2,4,8])
    with Solver(name='g3',bootstrap_with=master.clauses) as solver:
        assert not solver.solve(assumptions=[master.thresholds[4]])
        lo,hi=1,3
        while lo<hi:
            t=(lo+hi+1)//2
            if solver.solve(assumptions=[master.thresholds[t]]):
                blocks=master.decode(solver.get_model());lo=len(blocks)
            else:hi=t-1
    def image(w,B):return tuple(x for x in w if x in B)
    for candidate in itertools.permutations(a):
        if any(image(candidate,{a[j] for j in B})!=image(p,{a[j] for j in B}) for B in blocks):continue
        forced=[j for j in range(4) if image(candidate,set(a)-{a[j]})==image(p,set(a)-{a[j]})]
        if len(forced)<2 and candidate!=p:
            z=candidate;break
    else:raise RuntimeError('no fixture')
    D={'alphabet':list(a),'positive':[list(p)],'negative':[list(y),list(z)]}
    profile=solve_profiled(D,{'timeout_seconds':30})
    assert profile['result']['status']=='OPTIMAL',profile
    assert profile['metrics']['cuts']>=2,profile
    checked=verify_optimal(D,profile['result'],{'timeout_seconds':5});assert checked=={'status':'ACCEPT'}
    row={'input':D,'generator':'model-dependent diagnostic, NOT unbiased benchmark','profile':profile,'checked':checked}
    with (Path(__file__).resolve().parent/'two_cut_example.json').open('x',encoding='utf-8') as f:json.dump(row,f,indent=2)
    print(json.dumps({'cuts':profile['metrics']['cuts'],'k':profile['result']['max_devices'],'checked':checked}),flush=True)
if __name__=='__main__':main()

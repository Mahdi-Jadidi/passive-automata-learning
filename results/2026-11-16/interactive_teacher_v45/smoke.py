import json
from optimizer import solve_profiled
from verify import verify_optimal

def main():
    cases=[
        {'alphabet':[],'positive':[[]],'negative':[]},
        {'alphabet':['a','b'],'positive':[],'negative':[['a']]},
        {'alphabet':['a','b'],'positive':[['a','b']],'negative':[['b','a']]},
        {'alphabet':['a','b','c'],'positive':[['c','b','a']],'negative':[['a','b','c'],['a','c','b']]},
        {'alphabet':['a','b'],'positive':[[]],'negative':[['a'],['b']]},
    ]
    for D in cases:
        profile=solve_profiled(D,{'timeout_seconds':2})
        checked=verify_optimal(D,profile['result'],{'timeout_seconds':2}) if profile['result']['status'] in ('OPTIMAL','INFEASIBLE') else None
        print(json.dumps({'input':D,'profile':profile,'checked':checked}),flush=True)
if __name__=='__main__':main()

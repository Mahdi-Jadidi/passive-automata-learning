"""Sufficient worst-case deletion budgets; no learner or enumeration of subsets."""
from math import comb
from pathlib import Path
import json

def bound(n,r):
    P=comb(2*n,n);N0=comb(2*n+2,n+1)-1;T0=comb(2*n+1,n)-1
    if not (n>=1 and 1<=r<P):raise ValueError('Use a proper nonempty deletion: 1 <= r < P')
    p=P-r;M=2*n*p
    nl=max(2*n+1,N0-2*n*r);tl=max(1,T0-4*n*r);nu=N0-r
    lg=M+p+2*nl-1+nl*tl+7*nl+5
    hu=2*M+6*p+2*nu+4*n+32
    v=23 if n==1 else n*n+12*n+11
    ws=M+3*p+11+2*v
    return dict(n=n,removed=r,remaining=p,N_lower=nl,T_lower=tl,N_upper=nu,
                global_lower=lg,selector_upper=hu,split_exact=ws,
                guaranteed_net_split=hu+ws<lg,margin=lg-hu-ws)

def main():
    rows=[]
    for n in range(1,11):
        P=comb(2*n,n);R=0;last=None
        for r in range(1,P):
            b=bound(n,r)
            if not b['guaranteed_net_split']:break
            R=r;last=b
        if R:
            N0=comb(2*n+2,n+1)-1;T0=comb(2*n+1,n)-1
            assert last['N_lower']==N0-2*n*R and last['T_lower']==T0-4*n*R
            assert 4*n*R<=T0
            derivative=16*n*n*R-4*n*N0-2*n*T0-14*n+10
            assert derivative<0 and last['margin']>0
        rows.append(dict(n=n,complete_positives=P,any_deletions_up_to=R,
                         minimum_remaining_for_this_budget=P-R,last_bound=last))
    Path(__file__).with_name('deletion_budgets.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(rows,indent=2))

if __name__=='__main__':main()

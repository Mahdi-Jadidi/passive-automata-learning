"""Synthetic input-only scale fixture, independently constructed certificate.
Run with /usr/bin/time -f 'process_seconds=%e max_rss_kib=%M' python scale_replay.py.
"""
from production_replay import replay_closure
from test_production_replay import scope,epoch,fact,edge,rec
from time import perf_counter

n=100000; k=10000
A=[str(i) for i in range(n)]
raw=dict(alphabet=A,positive=[[A[2*i],A[2*i+1]] for i in range(k)],negative=[[A[2*i+1],A[2*i]] for i in range(k)])
s=scope(raw);sd=s['sample_digest'];p=list(range(n));q=p[:]
for i in range(k):q[2*i+1]=2*i
f=[fact(i,g,i) for i in range(k) for g in (2*i,2*i+1)];e=[edge(i,2*i,i,2*i+1,i) for i in range(k)]
c=dict(state='FIXPOINT',owner=q,records=[epoch(sd,0,p,f,e,q),epoch(sd,1,q,[fact(i,2*i,i) for i in range(k)],[],q)])
w=rec(sd,'STRUCTURAL_CHECK',dict(owner=q,compatible=True,separating_groups=[2*i for i in range(k)],failed_negative=None))
t=perf_counter();r=replay_closure(raw,s,c,[w])
if r['structural_optimum']!=k or r['mandatory_floor']!=k or r['operational_status']!='INCOMPLETE': raise RuntimeError('incorrect replay')
print('synthetic_symbols=',n,'traces=',2*k,'facts=',r['facts'],'mandatory_floor=',r['mandatory_floor'],'structural_optimum=',r['structural_optimum'],'operational_status=',r['operational_status'],'replay_seconds=',round(perf_counter()-t,4))

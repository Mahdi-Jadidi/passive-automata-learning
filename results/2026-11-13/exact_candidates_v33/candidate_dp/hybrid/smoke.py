import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('hybrid',Path(__file__).with_name('candidate.py'))
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
cases=[
 ('singleton', {'alphabet':['a','b'],'positive':[], 'negative':[]}),
 ('graph', {'alphabet':['a','b','c'],'positive':[['a','b','c']], 'negative':[['b','a','c'],['a','c','b']]}),
 ('dp', {'alphabet':['a','b','c'],'positive':[[],['a','b','c']], 'negative':[['a']]}),
 ('empty-ok', {'alphabet':[], 'positive':[], 'negative':[]}),
 ('empty-negative', {'alphabet':[], 'positive':[], 'negative':[[]]}),
 ('contradiction', {'alphabet':['a'], 'positive':[[]], 'negative':[[]]}),
 ('invalid', {'alphabet':['a'], 'positive':[['bad']], 'negative':[]}),
]
for name,data in cases:
 for budget in (None,0,1,10,-1,True):
  got=h.solve(data,max_candidates=budget); want=h._ref.solve(data,max_candidates=budget)
  assert got==want,(name,budget,got,want)
for name,data in cases[:3]:
 a,p,n=h._ref._normalize(data)
 singleton=h._c030._certified_all(a,p,n) is not None
 owners,q=h._graph._components(a,p,n)
 graph=h._ref._candidate(a,p,n,h._graph._expand(owners,tuple(range(q)))) is not None
 assert (singleton,graph)=={'singleton':(True,True),'graph':(False,True),'dp':(False,False)}[name]
print('PASS: 7 records x 6 budgets; singleton, graph and DP routes exercised; full C028 output equality')

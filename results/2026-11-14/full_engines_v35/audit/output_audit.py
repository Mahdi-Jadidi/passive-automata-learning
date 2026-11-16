import importlib.util,itertools,json,random,sys,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1]
repo=root.parents[2]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path); x=importlib.util.module_from_spec(s); s.loader.exec_module(x); return x
reference=load('reference',repo/'results/2026-11-11/exact_foundations_v28/implementation/reference.py')
engine=load('candidate',root/sys.argv[1]/'candidate.py')
def insert_parts(m):
    parts=[()]
    for i in range(m):
        nxt=[]
        for old in parts:
            for j in range(len(old)):
                b=list(old); b[j]=b[j]+(i,); nxt.append(tuple(b))
            nxt.append(old+((i,),))
        parts=nxt
    return parts
def independent(data):
    a=data['alphabet']; p=list(dict.fromkeys(map(tuple,data['positive']))); n=list(dict.fromkeys(map(tuple,data['negative'])))
    sols=[]
    for blocks in insert_parts(len(a)):
        groups=[{a[i] for i in b} for b in blocks]
        fac=[[tuple(x for x in w if x in b) for w in p] for b in groups]
        def proj(w,b): return tuple(x for x in w if x in b)
        rej=[next((i for i,b in enumerate(groups) if proj(w,b) not in fac[i]),None) for w in n]
        if None in rej: continue
        r=tuple(next(j for j,b in enumerate(blocks) if i in b) for i in range(len(a)))
        f=[[list(w) for w in dict.fromkeys(g)] for g in fac]
        witness={'rgs':list(r),'blocks':[[a[i] for i in b] for b in blocks],'factors':f,'negative_rejected_by':rej}
        sols.append((r,witness))
    sols.sort(key=lambda x:x[0])
    if not sols:
        return {'status':'INCOMPATIBLE','compatible_count':0,'optimal_count':0,'max_blocks':None,'recommendation':None,'optimal_unique':None,'compatible_witnesses':[],'optimal_witnesses':[]}
    k=max(len(w['blocks']) for _,w in sols); opts=[w for _,w in sols if len(w['blocks'])==k]
    return {'status':'UNIQUE_COMPATIBLE' if len(sols)==1 else 'AMBIGUOUS','compatible_count':len(sols),'optimal_count':len(opts),'max_blocks':k,'recommendation':opts[0],'optimal_unique':len(opts)==1,'compatible_witnesses':[w for _,w in sols[:2]],'optimal_witnesses':opts[:2]}
records=[]; count=0
quick='--quick' in sys.argv
words=[[],['a'],['b']] if quick else [[],['a'],['b'],['a','a'],['a','b'],['b','a'],['b','b']]
cases=[]
for labels in itertools.product(range(3),repeat=7):
    cases.append({'alphabet':['a','b'],'positive':[w for w,v in zip(words,labels) if v==1],'negative':[w for w,v in zip(words,labels) if v==2]})
cases += [{'alphabet':[], 'positive':p,'negative':n} for p,n in [([],[]),([],[[]]),([[]],[]),([[]],[[]])]]
cases += [{'alphabet':['long','b','unused'],'positive':[[],['long','b'],['long','b']], 'negative':[['long']]}, {'alphabet':['a','b','c'],'positive':[[],['a','b','c']],'negative':[['a']]}]
random.seed(418)
for _ in range(0 if quick else 50):
    a=['a','b','c']; pool=[list(t) for l in range(3) for t in itertools.product(a,repeat=l)]; random.shuffle(pool)
    cases.append({'alphabet':a,'positive':pool[:random.randrange(4)],'negative':pool[5:5+random.randrange(3)]})
if quick:
    cases=[case for case in cases if len(case['alphabet']) <= 2]
try:
    for i,data in enumerate(cases):
        actual=engine.solve(data); expected=reference.solve(data); independent_result=independent(data)
        if actual!=expected or expected!=independent_result: raise AssertionError((i,data,actual,expected,independent_result))
        count+=1
    for data in cases[::211]+cases[-56:]:
        m=len(data['alphabet']); bells=[1,1,2,5,15,52]; B=bells[m]
        for budget in (0,max(0,B-1),B,B+1,None,-1,True,1.0):
            expected=reference.solve(data,max_candidates=budget); actual=engine.solve(data,max_candidates=budget)
            if actual!=expected: raise AssertionError((data,budget,actual,expected))
            records.append('budget')
    invalid=[None,{}, {'alphabet':[],'positive':[],'negative':[],'x':0}, {'alphabet':'a','positive':[],'negative':[]}, {'alphabet':['','a'],'positive':[],'negative':[]}, {'alphabet':['a','a'],'positive':[],'negative':[]}, {'alphabet':['a'],'positive':[[]],'negative':[['b']]}, {'alphabet':[],'positive':'x','negative':[]}, {'alphabet':[],'positive':[None],'negative':[]}]
    for data in invalid:
        for budget in (None,0,True):
            assert engine.solve(data,max_candidates=budget)==reference.solve(data,max_candidates=budget), (data,budget)
            records.append('invalid')
    print(json.dumps({'engine':sys.argv[1],'status':'PASS','cases':count,'budget_checks':records.count('budget'),'invalid_checks':records.count('invalid')}))
except BaseException:
    traceback.print_exc(); print(json.dumps({'engine':sys.argv[1],'status':'FAIL','completed_cases':count})); raise

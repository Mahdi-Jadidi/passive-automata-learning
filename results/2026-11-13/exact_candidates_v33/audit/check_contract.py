"""Independent full-contract comparison after source/proof freeze."""
import argparse, copy, hashlib, importlib.util, json, platform, sys, traceback
from pathlib import Path
import insertion_oracle as ref

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'results/2026-11-11/exact_foundations_v28/implementation/reference.py'
OLD=ROOT/'results/2026-11-11/review_optimization_v30/optimization/candidate_v1.py'
DP=HERE.parent/'candidate_dp/candidate.py'
GRAPH=HERE.parent/'candidate_graph/candidate.py'
SOURCES={'C028':(BASE,'solve'),'C030':(OLD,'solve_combined'),'DP':(DP,'solve'),'GRAPH':(GRAPH,'solve')}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
def expected(data):
    sigma,ps,ns=ref.normalize(data); raw=ref.oracle(data)
    def conv(w):
        factors=[]
        for b in w['blocks']:
            unique=[]
            for p in ps:
                projected=list(ref.projection(p,set(b)))
                if projected not in unique: unique.append(projected)
            factors.append(unique)
        return {'rgs':w['rgs'],'blocks':w['blocks'],'factors':factors,'negative_rejected_by':w['rejecting_block_by_negative']}
    if raw['max_blocks'] is None:
        return {'status':'INCOMPATIBLE','compatible_count':0,'optimal_count':0,'max_blocks':None,'recommendation':None,'optimal_unique':None,'compatible_witnesses':[],'optimal_witnesses':[]}
    a=[conv(w) for w in raw['compatible']]; o=[conv(w) for w in raw['optimal']]
    return {'status':raw['status'],'compatible_count':raw['compatible_count'],'optimal_count':raw['optimal_count'],'max_blocks':raw['max_blocks'],'recommendation':o[0],'optimal_unique':raw['optimal_unique'],'compatible_witnesses':a,'optimal_witnesses':o}
def replay(data,result):
    sigma,ps,ns=ref.normalize(data)
    for w in result['compatible_witnesses']+result['optimal_witnesses']:
        blocks=w['blocks']; flat=[x for b in blocks for x in b]
        assert len(flat)==len(sigma) and set(flat)==set(sigma) and all(blocks)
        assert list(ref.canonical_rgs(tuple(frozenset(b) for b in blocks),sigma))==w['rgs']
        for i,b in enumerate(blocks):
            projections=[]
            for p in ps:
                value=list(ref.projection(p,set(b)))
                if value not in projections: projections.append(value)
            assert w['factors'][i]==projections
        assert len(w['negative_rejected_by'])==len(ns)
        for n,i in zip(ns,w['negative_rejected_by']):
            assert type(i) is int and 0<=i<len(blocks)
            assert all(ref.projection(n,set(b)) in {ref.projection(p,set(b)) for p in ps} for b in blocks[:i])
            assert ref.projection(n,set(blocks[i])) not in {ref.projection(p,set(blocks[i])) for p in ps}

def budget_cases():
    d={'alphabet':['a','b','c','d'],'positive':[],'negative':[]}
    for b in [0,1,14,15]: yield 'bell4_'+str(b),d,b
    yield 'empty0',{'alphabet':[],'positive':[],'negative':[]},0
    yield 'one0',{'alphabet':['a'],'positive':[],'negative':[]},0
    yield 'one1',{'alphabet':['a'],'positive':[],'negative':[]},1
    yield 'contradict0',{'alphabet':['a'],'positive':[['a']],'negative':[['a']]},0
    for tag,bad,b in [('extra',{**d,'extra':1},None),('missing',{'alphabet':['a'],'positive':[]},None),('empty_id',{'alphabet':[''],'positive':[],'negative':[]},None),('duplicate',{'alphabet':['a','a'],'positive':[],'negative':[]},None),('unknown',{'alphabet':['a'],'positive':[['b']],'negative':[]},None),('bad_word',{'alphabet':['a'],'positive':['a'],'negative':[]},None),('negative_budget',d,-1),('bool_budget',d,True),('float_budget',d,1.0)]: yield tag,bad,b

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--solver',choices=SOURCES,required=True); ap.add_argument('--sha',required=True); args=ap.parse_args()
    path,entry=SOURCES[args.solver]; actual_sha=digest(path)
    if actual_sha.lower()!=args.sha.lower(): raise SystemExit('source hash mismatch')
    assert digest(HERE/'correctness_cases.jsonl').lower()=='294b48b80df5a15aa95debbbd14677fb26211ddb86e81ef0ee44aa29f5282927'
    mod=load(path,'audited_'+args.solver); solve=getattr(mod,entry); baseline=load(BASE,'audit_baseline')
    assert ref.selftest()['status']=='passed'
    count=0; results={}
    for line in (HERE/'correctness_cases.jsonl').read_text(encoding='utf-8').splitlines():
        row=json.loads(line); data=row['input']; want=expected(data); got=solve(copy.deepcopy(data))
        if got!=want: raise AssertionError(json.dumps({'case':row['case'],'expected':want,'actual':got},ensure_ascii=False))
        replay(data,got); count+=1
        if row['case'].startswith('meta_'): results[row['case']]=got
    for field in ['status','compatible_count','optimal_count','max_blocks','optimal_unique']:
        assert results['meta_original'][field]==results['meta_duplicate'][field]==results['meta_renamed'][field]
    for field in ['compatible_witnesses','optimal_witnesses']:
        assert [w['rgs'] for w in results['meta_original'][field]]==[w['rgs'] for w in results['meta_duplicate'][field]]==[w['rgs'] for w in results['meta_renamed'][field]]
    for case,data,b in budget_cases():
        got=solve(copy.deepcopy(data),max_candidates=b); want=baseline.solve(copy.deepcopy(data),max_candidates=b)
        if got!=want: raise AssertionError(json.dumps({'case':case,'expected':want,'actual':got},ensure_ascii=False))
    print(json.dumps({'status':'PASS','solver':args.solver,'source_sha256':actual_sha,'cases':count,'budget_and_invalid_cases':17,'oracle':ref.selftest(),'python':sys.version,'platform':platform.platform()},ensure_ascii=False))

if __name__=='__main__':
    try: main()
    except BaseException: traceback.print_exc(); sys.exit(1)

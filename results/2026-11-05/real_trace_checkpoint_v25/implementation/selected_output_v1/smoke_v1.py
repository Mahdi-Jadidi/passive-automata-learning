"""Small developer controls and direct oracle, not independent audit or data runs."""
import copy,hashlib,importlib.util,itertools,json,py_compile,sys,time
from pathlib import Path
import solver_v1 as solver
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('c017',HERE.parent/'contexts_c017_copy_v1.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def data(alphabet,traces):return dict(alphabet=list(alphabet),traces=[dict(file_id=i+1,events=[dict(id=a,outcome=y) for a,y in trace]) for i,trace in enumerate(traces)])
def parts(alphabet):
    if not alphabet:yield [];return
    first,*rest=alphabet
    for p in parts(rest):
        yield [[first]]+p
        for i in range(len(p)):yield p[:i]+[[first]+p[i]]+p[i+1:]
def consistent(d,block,depth):
    records={}
    for trace in d['traces']:
        history=[]
        for e in trace['events']:
            if e['id'] not in block:continue
            prior=history if depth=='full' else history[-depth:] if depth else []
            key=(tuple(prior),e['id']);y=e['outcome']
            if y is not None:
                if key in records and records[key]!=y:return False
                records[key]=y
            history.append(e['id'])
    return True
def replay(d,w,depth):
    assert sorted(a for b in w['blocks'] for a in b)==sorted(d['alphabet'])
    assert len(w['functions'])==len(w['blocks'])
    for block,function in zip(w['blocks'],w['functions']):
        assert function['block']==block and consistent(d,block,depth)
        if depth=='full':
            transitions={(x['parent'],x['event_id']):x['node'] for x in function['trie']}
            rules={x['context']:x['outcome'] for x in function['output_rules']}
        else:rules={(tuple(x['context'][0]),x['context'][1]):x['outcome'] for x in function['output_rules']}
        for trace in d['traces']:
            history=[];prefix=0
            for e in trace['events']:
                if e['id'] not in block:continue
                if depth=='full':prefix=transitions[(prefix,e['id'])];key=prefix
                else:key=(tuple(history[-depth:] if depth else []),e['id'])
                if e['outcome'] is not None:assert rules[key]==e['outcome']
                history.append(e['id'])
def main():
    for p in HERE.glob('*.py'):py_compile.compile(str(p),doraise=True)
    fixtures=[data('x',[[('x',True)],[('x',False)]]),data('abc',[[('a',True),('b',None),('a',False)]]),
              data('abc',[[]]),data('ab',[[('a',True),('b',False)],[('b',True),('a',False)]]),
              data('abc',[[('b',None),('a',True)],[('c',None),('a',False)]]),
              data('xy',[[('y',False),('x',False)],[('x',False),('y',False),('x',True)]]),
              data('x',[[('x',False)],[('x',None),('x',True)]]),
              data('xy',[[('x',None),('y',True)],[('y',None),('x',False)]]),
              data('xy',[[('y',True)],[('y',None),('x',False)],[('y',None),('x',None),('y',True)]])]
    rows=[]
    for fi,d in enumerate(fixtures):
        for depth in solver.DEPTHS:
            for k in [None,1,len(d['alphabet'])]:
                family=[p for p in parts(d['alphabet']) if k is None or len(p)==k]
                feasible=[p for p in family if all(consistent(d,b,depth) for b in p)]
                expected='incompatible' if not feasible else 'certified_unique' if len(feasible)==1 else 'ambiguous'
                out=solver.solve(d,depth=depth,model_version=solver.MODEL_VERSION,known_k=k)
                assert out['status']==expected,(fi,depth,k,out)
                # JSON-roundtrip verifies witness key serialization.
                out=json.loads(json.dumps(out))
                for w in out.get('alternatives',[])+([out['witness']] if out['status']=='certified_unique' else []):replay(d,w,depth)
                for check in out['certificate']['block_checks']:
                    block=check['blocks_symbols']
                    assert check['consistent']==consistent(d,block,depth)
                    assert old.evaluate_block(d,block,depth)['consistent']==check['consistent']
                    if check['conflict']:
                        c=check['conflict'];keys=[]
                        for ref in [c['first'],c['opposite']]:
                            trace=next(t for t in d['traces'] if t['file_id']==ref['file_id'])
                            prior=[e['id'] for e in trace['events'][:ref['event_index']] if e['id'] in block]
                            current=trace['events'][ref['event_index']]
                            keys.append((tuple(prior if depth=='full' else prior[-depth:] if depth else []),current['id']))
                        assert keys[0]==keys[1] and c['first_outcome']!=c['opposite_outcome']
                rows.append(dict(fixture=fi,depth=depth,k=k,status=out['status'],oracle_compatible_partitions=len(feasible)))
    invalid=[]
    for field,value in [('depth',True),('depth',3),('model_version','wrong'),('known_k',True),('known_k',0),('deadline',float('nan')),('deadline',True)]:
        kwargs=dict(depth='full',model_version=solver.MODEL_VERSION);kwargs[field]=value
        assert solver.solve(fixtures[0],**kwargs)['status']=='invalid_input';invalid.append(field+':'+str(value))
    for bad in [dict(alphabet=list('abcdefghi'),traces=[]),dict(alphabet=['a'],traces=[dict(file_id=1,events=[dict(id='a',outcome=1)])]),
                dict(alphabet=['a'],traces=[dict(file_id=1,events=[dict(id='z',outcome=None)])]),dict(alphabet=['a'],traces=[],host='leak')]:
        assert solver.solve(bad,depth=0,model_version=solver.MODEL_VERSION)['status']=='invalid_input'
    # Validate late malformed records before any result on easy early data.
    late=copy.deepcopy(fixtures[1]);late['traces'][0]['events'].append(dict(id='a',outcome='TRUE'))
    assert solver.solve(late,depth=0,model_version=solver.MODEL_VERSION)['status']=='invalid_input'
    expired=solver.solve(fixtures[0],depth='full',model_version=solver.MODEL_VERSION,deadline=time.perf_counter()-1)
    assert expired['status']=='unresolved' and not expired['complete'] and 'certificate' not in expired and 'partition' not in expired
    report=dict(passed=True,python=sys.version,oracle_controls=rows,invalid_controls=invalid,expired_deadline=expired,
                real_data_solver_runs=0,solver_sha256=hashlib.sha256((HERE/'solver_v1.py').read_bytes()).hexdigest())
    (HERE/'smoke_results_v1.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(passed=True,oracle_cases=len(rows),real_data_solver_runs=0)))
if __name__=='__main__':main()

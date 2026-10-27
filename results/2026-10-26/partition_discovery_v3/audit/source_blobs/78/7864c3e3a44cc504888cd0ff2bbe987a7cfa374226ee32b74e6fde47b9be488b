import importlib.util
import itertools
import json
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


general = load('smoke_general', HERE/'general_solver.py')
fair = load('smoke_fair', HERE/'fair_reference.py')
old = load('smoke_old', HERE.parents[1]/'partition_constraints_v2/baseline/partition_solver.py')
key = lambda r: tuple(tuple(b) for b in r['blocks'])
rng = random.Random(2026102603)
words = [''] + list('abc') + [''.join(t) for t in itertools.product('abc', repeat=2)]
for ordinal in range(60):
    labels = [rng.randrange(3) for w in words]
    data = dict(alphabet=list('abc'), positive=[w for w,x in zip(words,labels) if x==1],
                negative=[w for w,x in zip(words,labels) if x==2])
    expected = old.solve(data)
    full = general.solve(data, max_solutions=None)
    fairfull = fair.solve(data, max_solutions=None)
    print(json.dumps(dict(case=ordinal, input=data, old=expected, general=full, fair=fairfull)), flush=True)
    assert {key(r) for r in full['solutions']} == {key(r) for r in expected['feasible_partitions']}
    assert full['solutions'] == fairfull['solutions']
    assert full['search_exhausted'] and full['decision_complete']
    for limit in (1,2):
        a, b = general.solve(data,max_solutions=limit), fair.solve(data,max_solutions=limit)
        print(json.dumps(dict(case=ordinal, limit=limit, general=a, fair=b)), flush=True)
        assert a['solutions'] == b['solutions'] == full['solutions'][:limit]
        assert a['decision_complete'] and b['decision_complete']
        if len(a['solutions']) >= 2:
            assert a['uniqueness'] == 'ambiguous'

data = dict(alphabet=list('lkjihgfedcba'),positive=['ab','ab'],negative=['ba','ba'])
for provider in (general,fair):
    r = provider.solve(data,max_solutions=2)
    expired = provider.solve(data,deadline=time.perf_counter()-1)
    print(json.dumps(dict(boundary_input=data,result=r,expired=expired)),flush=True)
    assert len(r['solutions']) == 2 and r['uniqueness']=='ambiguous'
    assert len(r['alphabet'])==12 and r['metrics']['graph_components']==11
    assert expired['status']=='incomplete' and not expired['search_exhausted']
    assert not expired['decision_complete'] and expired['uniqueness']=='unknown'
    permuted = dict(alphabet=sorted(data['alphabet']),positive=['ab'],negative=['ba'])
    norm = provider.solve(permuted,max_solutions=2)
    print(json.dumps(dict(normalized_input=permuted,result=norm)),flush=True)
    assert norm['solutions']==r['solutions']
    for bad in (dict(alphabet=['a','b'],positive=['a'],negative=['a']),
                dict(alphabet=['a','b'],positive=['c'],negative=[])):
        try:
            result=provider.solve(bad)
        except ValueError as error:
            print(json.dumps(dict(invalid_input=bad,error=str(error))),flush=True)
        else:
            print(json.dumps(dict(invalid_input=bad,unexpected_result=result)),flush=True)
            raise AssertionError('invalid input accepted')
print(json.dumps(dict(passed=True,seed=2026102603,cases=60,independent_audit_pending=True)),flush=True)

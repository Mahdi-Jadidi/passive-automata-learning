import difflib, hashlib, importlib.util, json, py_compile, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
basepath=HERE.parent/'baseline_c020_v1/gate_v1.py'
base=load('base',basepath);new=load('candidate',HERE/'gate_v1.py')
for p in HERE.glob('*.py'): py_compile.compile(str(p),doraise=True)
n='abcdefgh'
ob=dict(alphabet=list(n),positive=[n[:i]+n[i+1:] for i in range(8)],negative=[n])
cases=[('D_K4',json.loads((ROOT/'results/2026-11-04/scaling_v20/audit/fixtures_v1/D/solver_input.json').read_text()),4),
       ('obstruction_K4',ob,4),('unsafe_current_coverage',dict(alphabet=list('abc'),positive=['aaccbb'],negative=['ccaabb']),2),
       ('quantifier',dict(alphabet=list('ab'),positive=['a','b'],negative=['ab']),2),
       ('quantifier_saved_epsilon',dict(alphabet=list('ab'),positive=['a','b'],negative=['']),2),('no_k_unchanged',ob,None)]
records=[]
for name,data,k in cases:
    a=base.solve(data,known_k=k);b=new.solve(data,known_k=k)
    assert a['status']==b['status'],(name,a,b)
    for w in b.get('alternatives',[])+([b['certificate']['witness']] if b['status']=='certified_unique' else []):
        assert sorted(c for block in w['blocks'] for c in block)==sorted(data['alphabet'])
        for neg in data['negative']:
            assert any(''.join(c for c in neg if c in block) not in {''.join(c for c in p if c in block) for p in data['positive']} for block in w['blocks'])
    if k is None:
        a.pop('method');b.pop('method');a['metrics'].pop('solver_seconds');b['metrics'].pop('solver_seconds');assert a==b
    records.append(dict(name=name,status=b['status'],certificate=b.get('certificate'),metrics=b['metrics']))
assert records[1]['metrics']['envelope_prunes']>0
assert records[2]['status']=='certified_unique'
assert records[3]['status']=='incompatible'
expired=new.solve(ob,known_k=4,deadline=time.perf_counter()-1)
assert expired['status']=='unresolved' and 'partition' not in expired
(HERE/'minimal.diff').write_text(''.join(difflib.unified_diff(basepath.read_text().splitlines(True),(HERE/'gate_v1.py').read_text().splitlines(True),fromfile='C020/gate_v1.py',tofile='C024-B/gate_v1.py')),encoding='utf-8')
(HERE/'smoke_results_v1.json').write_text(json.dumps(dict(passed=True,python=sys.version,cases=records,expired_deadline=expired),indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,cases=[dict(name=r['name'],status=r['status']) for r in records])))

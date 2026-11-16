"""Small targeted controls only; independent audit remains required."""
import difflib, hashlib, importlib.util, json, platform, py_compile, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
def load(name, folder):
    spec = importlib.util.spec_from_file_location(name, HERE / folder / 'gate_v1.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod
base = load('base', 'baseline_c020_v1')
new = load('candidate', 'candidate_c024a_v1')
for path in HERE.glob('*/*.py'):
    py_compile.compile(str(path), doraise=True)
def replay(data, w):
    blocks = w['blocks']
    assert sorted(a for b in blocks for a in b) == sorted(data['alphabet'])
    for n in data['negative']:
        assert any(''.join(c for c in n if c in b) not in {''.join(c for c in p if c in b) for p in data['positive']} for b in blocks)
n = 'abcdefgh'
obstruction = dict(alphabet=list(n), positive=[n[:i]+n[i+1:] for i in range(8)], negative=[n])
# Atomic partition fails, yet {a,b}|{c} rejects ab against ba.
amb = dict(alphabet=list('abc'), positive=['ba'], negative=['ab'])
# Swap forces ab, which is compatible; exercises unchanged fast route.
cases = [('obstruction', obstruction, None), ('swap_fast', amb, None),
         ('known_k_obstruction', obstruction, 4), ('unary', dict(alphabet=list('ab'),positive=['a'],negative=['bb']),None),
         ('contradiction', dict(alphabet=['a'],positive=['a'],negative=['a']),None),
         ('invalid', dict(alphabet=['a'],positive=['x'],negative=[]),None)]
# No adjacent swap edge; unary projections collide, but ab distinguishes order.
cases.append(('fallback_ambiguous', dict(alphabet=list('abc'),positive=['bac'],negative=['acb']),None))
records=[]
for name, data, k in cases:
    a=base.solve(data,known_k=k); b=new.solve(data,known_k=k)
    assert a['status']==b['status'], (name,a,b)
    for w in b.get('alternatives',[]): replay(data,w)
    if b['status']=='certified_unique': replay(data,b['certificate']['witness'])
    records.append(dict(name=name,status=b['status'],route=b.get('certificate',{}).get('route'),metrics=b['metrics']))
assert records[0]['route']=='exhausted_forced_atom_bipartitions'
assert records[0]['metrics']['complete_candidates']==128
assert records[-1]['route']=='two_block_search_witness'
expired=new.solve(obstruction,deadline=time.perf_counter()-1)
assert expired['status']=='unresolved' and 'partition' not in expired and 'alternatives' not in expired
for r in range(2,9):
    splits=[(1|(tail<<1), ((1<<r)-1)^(1|(tail<<1))) for tail in range((1<<(r-1))-1)]
    assert len(splits)==2**(r-1)-1 and len(set(splits))==len(splits)
    assert all(a&1 and a and b and not a&b and a|b==(1<<r)-1 for a,b in splits)
old=(HERE/'baseline_c020_v1/gate_v1.py').read_text()
candidate=(HERE/'candidate_c024a_v1/gate_v1.py').read_text()
(HERE/'candidate_c024a_v1/minimal.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),candidate.splitlines(True),fromfile='C020/gate_v1.py',tofile='C024-A/gate_v1.py')),encoding='utf-8')
(HERE/'smoke_results_v1.json').write_text(json.dumps(dict(passed=True,python=sys.version,platform=platform.platform(),cases=records,expired_deadline=expired,canonical_enumeration_r=list(range(2,9))),indent=2),encoding='utf-8')
print(json.dumps(records,indent=2))

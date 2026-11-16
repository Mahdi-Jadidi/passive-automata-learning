import copy,difflib,hashlib,importlib.util,json,py_compile,sys,time
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[4]
def record(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
a=load('a',here.parent/'candidate_c024a_v1/gate_v1.py');b=load('b',here.parent/'candidate_c024b_v1/gate_v1.py');new=load('integrated',here/'gate_v1.py')
for p in here.glob('*.py'):py_compile.compile(str(p),doraise=True)
def normalized(result):
    out=copy.deepcopy(result);out.pop('method');out['metrics'].pop('solver_seconds');return out
n='abcdefgh';ob=dict(alphabet=list(n),positive=[n[:i]+n[i+1:] for i in range(8)],negative=[n])
cases=[('obstruction_noK',ob,None),('fallback_ambiguous',dict(alphabet=list('abc'),positive=['bac'],negative=['acb']),None),
 ('obstruction_K4',ob,4),('D_K4',json.loads((root/'results/2026-11-04/scaling_v20/audit/fixtures_v1/D/solver_input.json').read_text()),4),
 ('unsafe_current_coverage',dict(alphabet=list('abc'),positive=['aaccbb'],negative=['ccaabb']),2),
 ('quantifier',dict(alphabet=list('ab'),positive=['a','b'],negative=['']),2),
 ('unary',dict(alphabet=list('ab'),positive=['a'],negative=['bb']),None),
 ('invalid',dict(alphabet=['a'],positive=['x'],negative=[]),None),
 ('contradiction',dict(alphabet=['a'],positive=['a'],negative=['a']),None)]
rows=[]
for name,data,k in cases:
    expected=(a if k is None else b).solve(data,known_k=k);actual=new.solve(data,known_k=k)
    assert normalized(expected)==normalized(actual),name
    rows.append(dict(name=name,reference='A' if k is None else 'B',result=actual))
for k in [None,4]:
    out=new.solve(ob,known_k=k,deadline=time.perf_counter()-1)
    assert out['status']=='unresolved' and 'partition' not in out and 'alternatives' not in out
base=here.parent/'baseline_c020_v1/gate_v1.py'
(here/'minimal_combined.diff').write_text(''.join(difflib.unified_diff(base.read_text().splitlines(True),(here/'gate_v1.py').read_text().splitlines(True),fromfile='C020/gate_v1.py',tofile='C024-integrated/gate_v1.py')),encoding='utf-8')
(here/'smoke_results_v1.json').write_text(json.dumps(dict(passed=True,python=sys.version,cases=rows,expired_deadlines_passed=True),indent=2),encoding='utf-8')
payload=dict(candidate='C024-integrated-v1',ready_for_independent_audit=True,public_promotion=False,full_benchmark_run=False,
 gate=record(here/'gate_v1.py'),cli=record(here/'partition_gate_v1.py'),baseline=record(base),
 frozen_a=record(here.parent/'candidate_c024a_v1/gate_v1.py'),frozen_b=record(here.parent/'candidate_c024b_v1/gate_v1.py'),
 diff=record(here/'minimal_combined.diff'),smoke=record(here/'smoke_results_v1.json'),method=record(here/'METHOD_v1.md'),
 command='py -3.14 results/2026-11-05/search_checkpoint_v24/implementation/integrated_c024_v1/verify_integration_v1.py',exit_code=0,
 composition='A returns on every unknown-K fallback before DFS; B modifies only known-K DFS. Shared validation/fast paths/cache/reject/witness unchanged. No combined extra optimization.',
 limits=['Independent integrated audit pending','No full benchmark','No public files or Git modified'])
assert payload['frozen_a']['sha256']=='9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4'
assert payload['frozen_b']['sha256']=='4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3'
(here/'READINESS_v1.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,cases=len(rows),gate=payload['gate'])))

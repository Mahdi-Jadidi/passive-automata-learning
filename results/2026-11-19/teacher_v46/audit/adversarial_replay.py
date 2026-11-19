import copy, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
V45 = ROOT / 'results/2026-11-16/interactive_teacher_v45'
VENDOR = ROOT / 'results/2026-11-14/sat_candidate_v37/vendor'
sys.path[:0] = [str(V45), str(VENDOR)]
from master import Master
from verify import verify_optimal, check_drup
from spec import budget
from pysat.solvers import Solver
D = {'alphabet': list('abcd'), 'positive': [list(x) for x in ('abcd','dcba','bdca','cabd')], 'negative': [list(x) for x in ('dbac','cdab')]}
cuts = [{'negative_index': 0, 'regions': [5,6,11,12], 'positive_indices': [0,0,1,1]}, {'negative_index': 1, 'regions': [7,9,10,12], 'positive_indices': [3,1,1,0]}]
m = Master(4)
for cut in cuts: m.add_cover(cut['regions'])
with Solver(name='g3', bootstrap_with=m.threshold(3), with_proof=True) as solver:
    assert not solver.solve()
    proof = solver.get_proof()
r = {'status':'OPTIMAL','blocks':[['a','c','d'],['b']], 'max_devices':2, 'certificate':{'type':'teacher_cut_drup','cuts':cuts,'proof':proof}}
checks = []
def test(name, data, result, expected, limits=None):
    actual = verify_optimal(data, result, limits)['status']; checks.append({'case':name,'expected':expected,'actual':actual}); assert actual == expected, checks[-1]
def mutate(name, fn):
    x=copy.deepcopy(r); fn(x); test(name,D,x,'REJECT')
test('original',D,r,'ACCEPT')
mutate('negative_index_minus_one',lambda x:x['certificate']['cuts'][0].__setitem__('negative_index',-1))
mutate('positive_index_minus_one',lambda x:x['certificate']['cuts'][0]['positive_indices'].__setitem__(0,-1))
mutate('negative_index_boolean',lambda x:x['certificate']['cuts'][0].__setitem__('negative_index',False))
mutate('region_zero',lambda x:x['certificate']['cuts'][0]['regions'].__setitem__(0,0))
mutate('region_all',lambda x:x['certificate']['cuts'][0]['regions'].__setitem__(-1,15))
mutate('duplicate_region',lambda x:x['certificate']['cuts'][0]['regions'].__setitem__(1,5))
mutate('invalid_witness',lambda x:x['certificate']['cuts'][0]['positive_indices'].__setitem__(0,2))
mutate('empty_proof',lambda x:x['certificate'].__setitem__('proof',[]))
mutate('out_of_range_proof',lambda x:x['certificate'].__setitem__('proof',['999999 0']))
mutate('malformed_proof',lambda x:x['certificate'].__setitem__('proof',['xyz 0']))
mutate('missing_terminator',lambda x:x['certificate'].__setitem__('proof',['1']))
mutate('suboptimal_feasible_claim',lambda x:(x.__setitem__('blocks',[list('abcd')]),x.__setitem__('max_devices',1)))
d=copy.deepcopy(D); d['negative'].reverse(); test('negative_order_rebound',d,r,'REJECT')
test('zero_budget',D,r,'INCOMPLETE',{'timeout_seconds':0})
class Fixture:
    variables=1
    def __init__(self, clauses): self.clauses=clauses
    def threshold(self,t): return self.clauses
for name, clauses, lines, expected in [('duplicate_units',[[1,1],[-1,-1]],[],True),('tautology_not_unit',[[1,-1]],[],False),('satisfiable_false_empty',[[1]],['0'],False),('tautological_addition',[[1]],['1 -1 0'],False),('ignored_deletion',[[1],[-1]],['d 1 0'],True)]:
    actual=check_drup(Fixture(clauses),1,lines,budget(None)); checks.append({'case':name,'expected':expected,'actual':actual}); assert actual==expected,checks[-1]
print(json.dumps({'checks':checks,'proof_lines':len(proof)},indent=2))

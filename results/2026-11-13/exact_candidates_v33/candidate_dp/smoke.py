import importlib.util
from pathlib import Path
p = Path(__file__).with_name('candidate.py')
spec = importlib.util.spec_from_file_location('candidate', p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ref = module._ref
cases = [
 {'alphabet': [], 'positive': [], 'negative': []},
 {'alphabet': [], 'positive': [], 'negative': [[]]},
 {'alphabet': ['a','b'], 'positive': [['a','b']], 'negative': [['b','a']]},
 {'alphabet': ['a','b','c'], 'positive': [[],['a','b','c']], 'negative': [['a']]},
 {'alphabet': ['a','b'], 'positive': [], 'negative': [[]]},
 {'alphabet': ['a','b'], 'positive': [[]], 'negative': [[]]},
 {'alphabet': ['id space','字','unused'], 'positive': [['字'],['字']], 'negative': [[]]},
 {'alphabet': ['a'], 'positive': [['x']], 'negative': []},
]
for i, case in enumerate(cases):
    for budget in (None, 0, 1, 10, -1, True):
        got = module.solve(case, max_candidates=budget)
        expected = ref.solve(case, max_candidates=budget)
        assert got == expected, (i, budget, got, expected)
print('PASS: 8 records x 6 budgets, full serialized equality to frozen C028')

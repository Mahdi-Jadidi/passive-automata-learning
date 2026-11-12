"""Pre-freeze developer differential check; independent official audit is separate."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = ROOT / 'results/2026-11-11/exact_foundations_v28/audit'
sys.path.insert(0, str(AUDIT))
from run_independent_audit_v1 import compare_one

spec = importlib.util.spec_from_file_location('candidate', HERE / 'candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

checked = 0
for filename in ('edge_cases_v1.jsonl', 'binary_ternary_length2_v1.jsonl', 'seeded_m3_to_m8_v1.jsonl'):
    with (AUDIT / filename).open(encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            compare_one(candidate, record)
            checked += 1
# Specific component-first occurrence order and graph shortcut; duplicate words and IDs.
for record in [
    {'alphabet':['a','b','c','d'], 'positive':[['a','c']], 'negative':[['c','a']]},
    {'alphabet':['a','b','c','d'], 'positive':[['a','c'],['a','c']], 'negative':[['c','a'],['c','a']]},
    {'alphabet':['α','multi-token','x'], 'positive':[], 'negative':[[]]},
]:
    compare_one(candidate, record)
    checked += 1
# Budgets and invalids must be exact baseline equality, including reasons.
with (AUDIT / 'invalid_cases_v1.jsonl').open(encoding='utf-8') as f:
    records = [json.loads(line) for line in f]
records += [{'alphabet':['a','b','c'], 'positive':[['a','b']], 'negative':[['b','a']]},
            {'alphabet':[], 'positive':[], 'negative':[[]]}]
for record in records:
    for budget in (0,1,2,5,100,-1,True,'bad'):
        assert candidate.solve(record, max_candidates=budget) == candidate._ref.solve(record, max_candidates=budget)
print(json.dumps({'oracle_cases': checked, 'budget_comparisons': len(records)*8, 'result':'PASS'}))


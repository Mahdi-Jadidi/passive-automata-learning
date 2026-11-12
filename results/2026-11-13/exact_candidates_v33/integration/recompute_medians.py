"""Read-only recomputation of the frozen timing matrix; does not run solvers."""
import collections, hashlib, json, statistics
from pathlib import Path
HERE = Path(__file__).resolve().parent
V33 = HERE.parent
RESULTS = HERE.parents[2]
A = V33 / 'audit'
expected = {
    RESULTS / '2026-11-11/exact_foundations_v28/implementation/reference.py': '5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94',
    RESULTS / '2026-11-11/review_optimization_v30/optimization/candidate_v1.py': '7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b',
    V33 / 'candidate_dp/candidate.py': '8ec5b68a08d9ec430c0bf5f10d86024408c3bb9408a4045f7efb41eed6e5f86f',
    V33 / 'candidate_graph/candidate.py': '71204f44840353ad5bd1f1bbfbb6365f6aabda5fff788f335ae788928f7cc242',
    V33 / 'candidate_graph/baseline_contract.py': '5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94',
    A / 'timing_cases.jsonl': '013e2b60dc1d5740d766a9b0f77c458c4fbb92f203ee67977f3fe7104b48215b',
    A / 'correctness_cases.jsonl': '294b48b80df5a15aa95debbbd14677fb26211ddb86e81ef0ee44aa29f5282927',
    A / 'timing_raw.jsonl': '65a69bc5cd07a2d897e2171faede6ec9ee9dd50774276bba3970ddce10e480ee',
    A / 'timing_summary.json': '4729bb0e024ae793d5d00e821f52092bef42701985ebf97e724317e60bcd66a1',
}
for path, digest in expected.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest: raise ValueError(f'hash mismatch: {path}: {actual}')
rows = [json.loads(line) for line in (A / 'timing_raw.jsonl').read_text(encoding='utf-8').splitlines()]
cases = [json.loads(line) for line in (A / 'timing_cases.jsonl').read_text(encoding='utf-8').splitlines()]
summary = json.loads((A / 'timing_summary.json').read_text(encoding='utf-8'))
solvers = ('C028', 'C030', 'DP', 'GRAPH')
assert len(rows) == 120 and len(cases) == 10
indexes = {(r['case'], r['solver'], r['repeat']) for r in rows}
assert len(indexes) == 120 and indexes == {(c['case'],s,i) for c in cases for s in solvers for i in range(3)}
by_case = {entry['case']:entry for entry in summary['cases']}
print('All frozen hashes, 120 distinct trials, complete statuses, full outputs and 80 medians match.')
for metric, summary_key in [('solve_ns','median_solve_seconds'),('startup_wall_ns','median_startup_seconds')]:
    print('\n'+metric+' (seconds; median of three)')
    print('| Case | C028 | C030 | DP | Graph |')
    print('|---|---:|---:|---:|---:|')
    for c in cases:
        name = c['case']; subset = [r for r in rows if r['case']==name]
        assert all(r['status']=='OK' and r['result']['status'] in ('UNIQUE_COMPATIBLE','AMBIGUOUS','INCOMPATIBLE') for r in subset)
        assert len({json.dumps(r['result'],sort_keys=True,ensure_ascii=False) for r in subset})==1
        medians=[]
        for solver in solvers:
            med = statistics.median([r[metric] for r in subset if r['solver']==solver])/1e9
            assert med == by_case[name]['solvers'][solver][summary_key]
            medians.append(med)
        print('| '+name+' | '+' | '.join(f'{v:.6f}' for v in medians)+' |')

# Separately recorded hybrid round, compared only after the original matrix.
hybrid_expected = {
    V33 / 'candidate_dp/hybrid/candidate.py': '6377ccd75281567be11af5820ae52668612a069240c31d2a5aee0cf4f1022063',
    A / 'HYBRID_REVIEW.md': '2fde71267c68cb7044dc7ef6d47b8bd7f945e01f74241a65dceb9c42a3b1ba27',
    A / 'hybrid_timing_raw.jsonl': '6c369e0380eca99c4d68f0917a395b5f2d07abcee3182d5866065fcd3d4c4dd2',
    A / 'hybrid_timing_summary.json': 'ee54c41d572ce14b26ccb0de5b6cf48d10da54d6fc25419e2b7d8e5535903694',
}
for path, digest in hybrid_expected.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest: raise ValueError(f'hybrid hash mismatch: {path}: {actual}')
hr = [json.loads(line) for line in (A/'hybrid_timing_raw.jsonl').read_text(encoding='utf-8').splitlines()]
hs = json.loads((A/'hybrid_timing_summary.json').read_text(encoding='utf-8'))
hby = {x['case']:x for x in hs['cases']}
assert len(hr)==30 and {(x['case'],x['repeat']) for x in hr} == {(c['case'],i) for c in cases for i in range(3)}
assert all(x['status']=='OK' and x['result']['status'] in ('UNIQUE_COMPATIBLE','AMBIGUOUS','INCOMPATIBLE') and x['matches_prior_c028'] for x in hr)
print('\nHybrid later round (seconds; median of three; cross-round comparisons descriptive only)')
print('| Case | Route | solve | startup-inclusive |')
print('|---|---|---:|---:|')
for c in cases:
    name=c['case']; group=[x for x in hr if x['case']==name]
    old=[x for x in rows if x['case']==name]
    assert all(x['result']==old[0]['result'] for x in group)
    solve=statistics.median(x['solve_ns'] for x in group)/1e9
    startup=statistics.median(x['startup_wall_ns'] for x in group)/1e9
    assert solve==hby[name]['median_solve_seconds'] and startup==hby[name]['median_startup_seconds']
    print(f"| {name} | {hby[name]['route']} | {solve:.6f} | {startup:.6f} |")
print('Hybrid frozen hashes, 30 distinct complete trials, full-output equality and 20 medians match.')

"""Validate saved evidence and regenerate summaries, without rerunning solvers."""
from pathlib import Path
from collections import Counter
import hashlib,json,platform,statistics,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(name):return [json.loads(x) for x in (HERE/name).read_text().splitlines() if x]
def main():
    trials=read('benchmark_raw.jsonl');assert len(trials)==60
    cases=[]
    for case in dict.fromkeys(r['case'] for r in trials):
        item={'case':case}
        for method in ['v43','v45']:
            records=[r for r in trials if r['case']==case and r['method']==method]
            assert {r['repeat'] for r in records}=={0,1,2}
            completed=[r for r in records if r['profile']['result']['status']=='OPTIMAL']
            assert all(r['checked']=={'status':'ACCEPT'} for r in completed)
            item[method]={'statuses':dict(Counter(r['profile']['result']['status'] for r in records)),
                          'median_pipeline_seconds':statistics.median(r['pipeline_plus_consumer_seconds'] for r in completed) if len(completed)==3 else None}
        cases.append(item)
    audit=read('corpus_audit.jsonl');assert len(audit)==2261
    assert all(r['completed_result_matches_reference'] is True for r in audit if r['profile']['result']['status'] in ('OPTIMAL','INFEASIBLE'))
    assert all(r['completed_result_matches_reference'] is None for r in audit if r['profile']['result']['status']=='INCOMPLETE')
    tests=read('test_runs.jsonl');assert len(tests)==4 and all(r['exit_code']==0 for r in tests)
    memory=read('memory_raw.jsonl');assert len(memory)==20 and all(r['peak_working_set_bytes']>0 for r in memory)
    projection=read('projection_benchmark.jsonl');assert len(projection)==24
    projection_summary=[]
    for size in [4,8]:
        for work in ['distinct','repeated']:
            records=[r for r in projection if r['alphabet_size']==size and r['workload']==work]
            assert len(records)==6
            for repeat in range(3):
                pair=[r for r in records if r['repeat']==repeat]
                assert len({r['result_sha256'] for r in pair})==1 and len({r['rejection_sha256'] for r in pair})==1
            projection_summary.append({'alphabet_size':size,'workload':work,
                **{m:statistics.median(r['total_seconds'] for r in records if r['method']==m) for m in ['naive_cached','projection_store']}})
    examples={name:json.loads((HERE/name).read_text()) for name in ['interaction_example.json','two_cut_example.json']}
    assert all(r['checked']=={'status':'ACCEPT'} for r in examples.values())
    summary={'version':'V45','python':sys.version,'platform':platform.platform(),
             'benchmark_trials':60,'benchmark':cases,'corpus_cases':2261,
             'corpus_statuses':dict(Counter(r['profile']['result']['status'] for r in audit)),
             'corpus_seconds_per_case':0.03,'corpus_incomplete_is_pass':False,
             'test_scripts_passed':4,'projection_summary':projection_summary,
             'memory_single_trial_bytes':memory,
             'examples':{name:{'cuts':r['profile']['metrics']['cuts'],'max_devices':r['profile']['result']['max_devices'],
                                'seconds':r['profile']['metrics']['total_seconds']} for name,r in examples.items()},
             'teacher_modified':False,'and_model_field_trials':0,
             'notes':['First benchmark batch overlapped corpus audit; preserved as benchmark_contended.jsonl and excluded from timing table.',
                      'Clean benchmark ran without concurrent audit or agent benchmarks; OS background load uncontrolled.',
                      'Projection microbenchmark is a separate bounded workload, not an end-to-end speedup.',
                      'Consumer normalizes duplicate literals after review; no teacher logic was changed.']}
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['## 7. Measured evaluation','',
           'All timings below are seconds. The main comparison uses ten fixed synthetic inputs, three fresh processes per method/case, a one-second solve budget and a separate one-second consumer budget. Imports and process startup are excluded. Incomplete results are censored outcomes, not slow successful solves. V43 and V45 are not equal-work internal implementations: V45 deliberately calls the exhaustive manuscript teacher.','',
           '| Case | V43 completed / 3 | V43 median | V45 completed / 3 | V45 median |',
           '|---|---:|---:|---:|---:|']
    for r in cases:
        a,b=r['v43'],r['v45']
        def sec(v):return '-' if v is None else f'{v:.6f}'
        lines.append(f"| {r['case']} | {a['statuses'].get('OPTIMAL',0)} | {sec(a['median_pipeline_seconds'])} | {b['statuses'].get('OPTIMAL',0)} | {sec(b['median_pipeline_seconds'])} |")
    lines+=['','The original concurrently run timing batch is retained but excluded from this table. Single-trial process peak working sets were measured separately for all twenty case/method pairs using Windows GetProcessMemoryInfo. They include Python/native imports and are not algorithm-only allocations; incomplete and completed runs do different work, so no memory superiority is claimed.','',
            'On the 2,261-case frozen-reference corpus, the new solver had a 0.03-second per-instance budget: '+', '.join(f'{v} {k}' for k,v in summary['corpus_statuses'].items())+'. Every completed optimum/infeasibility result agreed with its reference and passed the consumer. The incomplete instances are not counted as correctness successes. This corpus run overlapped an initial benchmark batch and is not a clean timing experiment.','',
            'Four saved test-script runs passed: projection tests (three tests including all masks and 5,000-symbol words), teacher tests (six tests including thirty seeded Cartesian-join comparisons), exhaustive master tests through four atoms (16,384 covers and 64 pair assignments at four atoms), and certificate/cut tests (167 monotone families, 758 cuts, 5,218 preservation checks, an accepted fourteen-line DRUP trace, and tamper/boundary checks).','',
            'Two production interaction examples completed with accepted optimum certificates. The ordinary three-symbol example learned one cut; a separate model-dependent four-symbol diagnostic deliberately required two cuts and returned three blocks. The latter fixture is not an unbiased benchmark. Its initial generator incorrectly assumed identical SAT tie-breaking under different query sequences; that diagnostic issue and correction are preserved in history.','',
            '| Projection workload | Cached scanner median | Shared store median |',
            '|---|---:|---:|']
    for r in projection_summary:lines.append(f"| {r['alphabet_size']} symbols, {r['workload']} | {r['naive_cached']:.6f} | {r['projection_store']:.6f} |")
    lines+=['','These twenty-four microbenchmark records include initialization and three repetitions per workload/method. Both methods cache masks; full-result and rejection checksums match. The prefix store shares representation and transformations, but Python DAG traversal and tuple materialization may cost more than direct scanning. No universal projection speedup is claimed.','']
    (HERE/'EVALUATION.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'benchmark_trials':60,'corpus_statuses':summary['corpus_statuses'],'projection_summary':projection_summary,'examples':summary['examples']}))
if __name__=='__main__':main()

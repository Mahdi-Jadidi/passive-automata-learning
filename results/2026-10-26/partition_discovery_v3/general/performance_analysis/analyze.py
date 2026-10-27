"""Saved-output postprocessing only: no provider/solver execution."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def median(values):
    return statistics.median(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', required=True, type=Path)
    parser.add_argument('--validator', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    raw_ledger, raw_report = args.ledger.read_bytes(), args.validator.read_bytes()
    report = json.loads(raw_report)
    provenance = dict(ledger=str(args.ledger), ledger_sha256=sha(raw_ledger),
                      validator=str(args.validator), validator_sha256=sha(raw_report),
                      analysis_sha256=sha(Path(__file__).read_bytes()))
    (args.output/'started.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    require(report['accepted'] is True and not report['errors'], 'v4 not accepted')
    require(report['planned_jobs'] == 1744 and report['status_counts'] == {'found': 1744}, 'v4 coverage mismatch')
    require(report['budget_skipped'] == 0 and report['ledger_sha256'] == sha(raw_ledger), 'ledger binding mismatch')
    rows = [json.loads(line) for line in raw_ledger.splitlines() if line]
    require(len(rows) == 1744 and len({r['job_id'] for r in rows}) == 1744, 'ledger coverage/duplicates')
    groups = defaultdict(list)
    for row in rows:
        require(row['execution_status'] == 'success' and row['exit_code'] == 0 and row['child_reaped'], 'raw execution not successful/reaped')
        groups[row['method'], row['case_id'], row['max_solutions']].append(row)
    per_case = []
    with (args.output/'per_case.jsonl').open('x', encoding='utf-8') as stream:
        for (method, cid, limit), records in sorted(groups.items()):
            timing = sorted((r for r in records if r['mode']=='timing'), key=lambda r:r['replicate'])
            memory = [r for r in records if r['mode']=='memory']
            require(len(records)==4 and [r['replicate'] for r in timing]==[1,2,3]
                    and len(memory)==1 and memory[0]['replicate']==1, 'expected 3 timing and 1 memory')
            timings, metrics, dependencies, alphabets = [], [], [], []
            peak = None
            for row in [*timing, *memory]:
                path = Path(row['attempt_dir'])/'stdout.bin'
                raw = path.read_bytes()
                require(sha(raw)==row['stdout_sha256'], 'stdout hash mismatch')
                payload = json.loads(raw)
                result = payload['result'] if row['mode']=='memory' else payload
                require(result['status']=='found' and result['method']==method, 'validated result shape drift')
                alpha = result.get('alphabet', result.get('graph',{}).get('symbols'))
                require(isinstance(alpha,list), 'missing alphabet')
                alphabets.append(alpha)
                dependencies.append(dict(attempt_id=row['attempt_id'], mode=row['mode'],
                                         stdout_sha256=sha(raw), path=str(path)))
                if row['mode']=='timing':
                    value = row['subprocess_seconds']
                    require(isinstance(value,(int,float)) and math.isfinite(value) and value>0, 'invalid process time')
                    timings.append(value)
                    metrics.append(result.get('metrics',{}))
                else:
                    peak = payload['tracemalloc_peak_bytes']
                    require(isinstance(peak,int) and peak>=0, 'invalid provider-call peak')
            require(all(a==alphabets[0] for a in alphabets), 'alphabet changed across repetitions')
            fields = ('graph_components','nodes','leaves','cuts','preprocessing_seconds',
                      'separation_seconds','cut_generation_seconds','opposition_components',
                      'opposition_edges','pair_tests','candidate_checks','provider_seconds')
            metric_medians = {}
            for field in fields:
                values = [m.get(field) for m in metrics]
                if all(isinstance(v,(int,float)) and math.isfinite(v) for v in values):
                    metric_medians[field] = median(values)
            record = dict(method=method, case_id=cid, max_solutions=limit,
                          alphabet_size=len(alphabets[0]), timing_repetitions=3,
                          raw_timing_seconds=timings, case_median_seconds=median(timings),
                          provider_call_peak_bytes=peak, timing_metrics_by_repetition=metrics,
                          metric_case_medians=metric_medians, saved_output_dependencies=dependencies)
            # Full derived per-case record saved before aggregate assertions.
            stream.write(json.dumps(record, ensure_ascii=False,sort_keys=True)+'\n')
            stream.flush()
            per_case.append(record)
    by_key = {(r['method'],r['case_id'],r['max_solutions']):r for r in per_case}
    general_summary, size_summary, fixed_summary = [], [], []
    for limit in (1,2):
        g = {r['case_id']:r for r in per_case if r['method']=='general' and r['max_solutions']==limit}
        f = {r['case_id']:r for r in per_case if r['method']=='fair-reference' and r['max_solutions']==limit}
        require(set(g)==set(f) and len(g)==100, 'expected 100 paired cases per limit')
        pairs = [dict(case_id=cid, alphabet_size=g[cid]['alphabet_size'],
                      general_seconds=g[cid]['case_median_seconds'],fair_seconds=f[cid]['case_median_seconds'],
                      general_over_fair=g[cid]['case_median_seconds']/f[cid]['case_median_seconds'],
                      general_peak=g[cid]['provider_call_peak_bytes'],fair_peak=f[cid]['provider_call_peak_bytes'])
                 for cid in sorted(g)]
        def summarize(subset):
            return dict(max_solutions=limit, paired_cases=len(subset), timing_reps_per_case=3,
                        general_faster_cases=sum(p['general_over_fair']<1 for p in subset),
                        fair_faster_cases=sum(p['general_over_fair']>1 for p in subset),
                        tied_cases=sum(p['general_over_fair']==1 for p in subset),
                        median_general_over_fair_case_ratio=median([p['general_over_fair'] for p in subset]),
                        general_median_of_case_medians_seconds=median([p['general_seconds'] for p in subset]),
                        fair_median_of_case_medians_seconds=median([p['fair_seconds'] for p in subset]),
                        general_provider_peak_median_bytes=median([p['general_peak'] for p in subset]),
                        fair_provider_peak_median_bytes=median([p['fair_peak'] for p in subset]),
                        pairs=subset)
        general_summary.append(summarize(pairs))
        for m in (4,6,8,10):
            subset=[p for p in pairs if p['alphabet_size']==m]
            require(len(subset)==25,'expected 25 pairs per alphabet')
            size_summary.append(dict(alphabet_size=m,**summarize(subset)))
        fixed=[r for r in per_case if r['method']=='fixed-word' and r['max_solutions']==limit]
        require(len(fixed)==18,'expected 18 structural cases per limit')
        for m in (2,8,16,32,64,128):
            subset=[r for r in fixed if r['alphabet_size']==m]
            require(len(subset)==3,'expected 3 structural cases per size/limit')
            fixed_summary.append(dict(max_solutions=limit,alphabet_size=m,cases=3,
                timing_reps_per_case=3,group_median_of_case_medians_seconds=median([r['case_median_seconds'] for r in subset]),
                max_case_median_seconds=max(r['case_median_seconds'] for r in subset),
                observed_max_individual_timing_seconds=max(t for r in subset for t in r['raw_timing_seconds']),
                provider_call_peak_median_bytes=median([r['provider_call_peak_bytes'] for r in subset]),
                case_ids=[r['case_id'] for r in subset]))
    output=dict(provenance=provenance,accepted_input_rows=1744,postprocessing_only=True,
                case_aggregation='median of 3 timing repetitions BEFORE pairing ratios',
                ratio_direction='general/fair; below 1 means general faster',
                timing_scope='capture subprocess wall including startup and serialization',
                memory_scope='provider.solve traced allocations only, excludes parsing/imports/serialization and RSS',
                limitation='Temporal method-block ordering; descriptive saved-corpus comparison, no universal causal speedup claim.',
                general_vs_fair=general_summary,general_vs_fair_by_size=size_summary,
                fixed_word_scaling=fixed_summary,
                per_case_file='per_case.jsonl',per_case_sha256=sha((args.output/'per_case.jsonl').read_bytes()))
    (args.output/'analysis.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    brief={k:output[k] for k in ('accepted_input_rows','case_aggregation','ratio_direction','limitation')}
    brief['general_vs_fair']=[{k:v for k,v in s.items() if k!='pairs'} for s in general_summary]
    brief['fixed_word_scaling']=fixed_summary
    print(json.dumps(brief,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()

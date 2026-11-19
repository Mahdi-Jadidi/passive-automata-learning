"""Replay historical V45 certificates and separately classify censored rows."""
import argparse
from collections import Counter
import json
from pathlib import Path

from audit import HERE, OLD, V45, load, rows


def entries():
    old_corpus = rows(V45/'corpus_audit.jsonl')
    for row in old_corpus:
        yield 'v45-corpus-0.03s', row['i'], row['input'], row['reference_k'], row['profile']
    base = HERE.parent/'teacher_v46'/'evidence'
    fixed = {r['case']:r['expected_k'] for r in rows(base/'benchmark.jsonl')}
    for row in rows(V45/'benchmark_raw.jsonl'):
        if row['method']=='v45':
            yield 'v45-fixed-1s', row['case'], row['input'], fixed[row['case']], row['profile']
    for name in ('corpus','benchmark','fixtures','escalations'):
        for row in rows(base/(name+'.jsonl')):
            if row.get('method','v45')=='v45':
                yield 'v46-'+name, row.get('i',row.get('case')), row['input'], row['expected_k'], row['profile']
    uncapped = HERE.parent/'teacher_v46_uncapped'/'overlap_8'
    old_result = json.loads((uncapped/'result.json').read_text(encoding='utf-8'))
    details = rows(uncapped/'events.jsonl')[0]
    yield 'uncapped', 'overlap_8', details['input'], old_result['expected_k'], old_result['profile']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    _, verify = load('v45')
    counts = Counter()
    with args.output.open('x',encoding='utf-8') as stream:
        for suite,index,d,k,profile in entries():
            r = profile['result']
            status = r['status']
            if status in ('OPTIMAL','INFEASIBLE'):
                verdict = verify(d,r,{'timeout_seconds':30})
                valid = verdict=={'status':'ACCEPT'} and r['max_devices']==k
                valid &= (status=='INFEASIBLE')==(k is None)
            else:
                verdict = None
                valid = status=='INCOMPLETE' and all(r[key] is None
                                                    for key in ('blocks','max_devices','certificate'))
            record = dict(suite=suite,case=index,expected_k=k,status=status,checker=verdict,
                          checker_limit_seconds=30,valid=valid,
                          interrupted_phase=profile['metrics'].get('interrupted_phase'))
            stream.write(json.dumps(record)+'\n')
            counts[suite,status] += 1
            if not valid:
                raise RuntimeError(record)
    print(json.dumps({f'{s}/{v}':n for (s,v),n in counts.items()}),flush=True)


if __name__=='__main__':
    main()

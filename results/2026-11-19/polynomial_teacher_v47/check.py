"""Independent exhaustive teacher decisions and bounded known-optimum stress."""
import argparse
import itertools
import json
from pathlib import Path
import sys

from evaluate import HERE, api, emit, measure, rows
from projection_teacher import ProjectionTeacher


def direct_teaching_cases():
    alphabet = ('a','b')
    words = [tuple(w) for length in range(3) for w in itertools.product(alphabet,repeat=length)]
    teacher = ProjectionTeacher(lambda:None)
    for labels in itertools.product(range(3),repeat=len(words)):
        pos = [word for word,label in zip(words,labels) if label==1]
        neg = [word for word,label in zip(words,labels) if label==2]
        for blocks in ((alphabet,), (('a',),('b',))):
            def project(word, block):
                return tuple(event for event in word if event in block)
            images = {b:dict(positive=[project(w,b) for w in pos],
                             negative=[project(w,b) for w in neg]) for b in blocks}
            # Compare pairs directly, without the decision teacher's hash sets or
            # the producer projection cache.
            expected = all(any(all(project(y,b)!=project(x,b) for x in pos)
                               for b in blocks) for y in neg)
            actual = teacher.check(blocks,images)['status']=='ACCEPT'
            yield dict(labels=labels,blocks=blocks,expected=expected,actual=actual,
                       contract_valid=(expected==actual))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out',type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    with (args.out/'teacher_cases.jsonl').open('x',encoding='utf-8') as stream:
        for row in direct_teaching_cases():
            emit(stream,row)
    # Interrupt during the teacher's first positive insertion. Propagation,
    # rather than a returned decision, is part of the caller's contract.
    class InjectedInterruption(Exception):
        pass

    ticks = 0
    def tick():
        nonlocal ticks
        ticks += 1
        if ticks==2:
            raise InjectedInterruption

    teacher = ProjectionTeacher(tick)
    try:
        teacher.check((('a',),),{('a',):{'positive':[('a',)],'negative':[()]}})
    except InjectedInterruption:
        interrupt_propagated = True
    else:
        raise AssertionError('teacher returned a decision after interruption')

    sys.path.insert(0,str(HERE.parent/'teacher_v46_outer_audit'))
    from audit import Reference
    with (args.out/'outer_trace.jsonl').open('x',encoding='utf-8') as stream:
        for row in rows(HERE/'evidence/outer.jsonl'):
            checks = Reference(row['input']).trace(row['profile']['trace'])
            emit(stream,dict(case=row['case'],checks=checks,contract_valid=True))

    # A complete graph on n>=2 has minimum vertex cover n−1, hence
    # optimum two blocks by the proved reduction. Censor slow exact replays.
    solve = api('v47')
    with (args.out/'clique_scale.jsonl').open('x',encoding='utf-8') as stream:
        for n in (10,12,16,20):
            a = [f'v{i}' for i in range(n)]
            d = dict(alphabet=a,positive=list(map(list,itertools.combinations(a,2))),negative=[[]])
            row = measure(dict(case=f'K{n}',input=d,expected_k=2),2,2,solve)
            emit(stream,row)
    traces = [c for r in rows(args.out/'outer_trace.jsonl') for c in r['checks']]
    result = dict(teacher_cases=len(rows(args.out/'teacher_cases.jsonl')),
                  teacher_interruption_propagated=interrupt_propagated,
                  outer_candidates_checked=sum(c['master_k'] is not None for c in traces),
                  outer_cuts_checked=sum(c['cut_checked'] for c in traces),
                  clique_scale=[dict(case=r['case'], status=r['profile']['result']['status'],
                                     interrupted_phase=r['profile']['metrics'].get('interrupted_phase'))
                                for r in rows(args.out/'clique_scale.jsonl')])
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
